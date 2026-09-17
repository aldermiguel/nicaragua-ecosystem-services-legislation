from pathlib import Path
import re
import unicodedata
import pandas as pd
from bs4 import BeautifulSoup

# Script jobs
# 1- Set directories and output files
# 2- Define search terms
# 3- Process HTML documents
# 4- Create datasets
#   -> screening_documents.csv: one row per document
#   -> screening_matches.csv: one row per individual match

# File locations

html_folder = Path("data/legislation/html")
screening_folder = Path("data/legislation/screening")

screening_folder.mkdir(parents=True, exist_ok=True)

documents_csv_file = screening_folder / "screening_documents.csv"
matches_csv_file = screening_folder / "screening_matches.csv"

documents_excel_file = screening_folder / "screening_documents.xlsx"
matches_excel_file = screening_folder / "screening_matches.xlsx"

# Norm type classification

norm_type_mapping = {
    "Decretos Ejecutivos": "Decreto",
    "Decretos Legislativos": "Decreto",
    "Decreto Presidencial": "Decreto",
    "Decretos - Ley": "Decreto-Ley",
    "Leyes": "Ley",
    "Reglamentos": "Reglamento"
}

allowed_norm_types = {
    "Decreto",
    "Decreto-Ley",
    "Ley",
    "Reglamento"
}

# Search dictionary

def terms(words, category, subcategory, tier):
    return [
        {
            "term": word,
            "category": category,
            "subcategory": subcategory,
            "tier": tier
        }
        for word in words
    ]


search_terms = (
    terms(
        [
            "servicios ecosistémicos",
            "servicios de los ecosistemas",
            "servicios del ecosistema",
            "servicios ambientales",
            "servicios del ambiente",
            "bienes y servicios ambientales",
            "bienes y servicios ecosistémicos"
        ],
        "direct_es",
        "ecosystem_services",
        1
    )
    + terms(
        [
            "funciones ecosistémicas",
            "funciones ecológicas",
            "funciones ambientales"
        ],
        "direct_es",
        "ecosystem_functions",
        1
    )
    + terms(
        [
            "pago por servicios ambientales",
            "pagos por servicios ambientales",
            "pago por servicios ecosistémicos",
            "pagos por servicios ecosistémicos"
        ],
        "economic_instruments",
        "payments",
        2
    )
    + terms(
        [
            "compensación por servicios ambientales",
            "compensación por servicios ecosistémicos"
        ],
        "economic_instruments",
        "compensation",
        2
    )
    + terms(
        [
            "incentivos ambientales",
            "incentivos para la conservación",
            "incentivos económicos para la conservación"
        ],
        "economic_instruments",
        "incentives",
        2
    )
    + terms(
        [
            "mercado de servicios ambientales",
            "mercado de servicios ecosistémicos"
        ],
        "economic_instruments",
        "markets",
        2
    )
)

# Functions

def normalize_text(text):
    if text is None:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def normalize_label(text):
    text = normalize_text(text).lower()

    return "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )

def extract_document_id(file_path):
    return file_path.stem

def extract_url(soup, document_id):
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")

        if "xpNormaJuridica.xsp" in href and "documentId=" in href:
            if href.startswith("http"):
                return href

            if href.startswith("/"):
                return ("http://legislacion.asamblea.nacional.gob.ni" + href)

    return (
        "http://legislacion.asamblea.nacional.gob.ni/"
        "Normaweb.nsf/xpNormaJuridica.xsp"
        f"?documentId={document_id}&action=openDocument"
    )

def extract_metadata(soup):
    metadata = {
        "titulo": "",
        "rango": "",
        "materia": "",
        "no_norma": "",
        "no_gaceta": "",
        "fecha_publicacion": ""
    }

    label_mapping = {
        "titulo": "titulo",
        "rango": "rango",
        "materia": "materia",
        "no norma": "no_norma",
        "no gaceta": "no_gaceta",
        "fecha publicacion": "fecha_publicacion"
    }

    for row in soup.find_all("tr"):
        cells = row.find_all("td", recursive=False)

        if not cells:
            continue

        label = normalize_label(
            cells[0].get_text(" ", strip=True)
        ).rstrip(":").strip()

        if label not in label_mapping:
            continue

        if len(cells) >= 2:
            field = label_mapping[label]
            metadata[field] = normalize_text(
                cells[-1].get_text(" ", strip=True)
            )

    return metadata

def extract_visible_text(soup):
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    return normalize_text(
        soup.get_text(" ", strip=True)
    )

def make_context(text, start, end, window=1000):
    left_chunk = text[max(0, start - window):start]
    left_match = list(re.finditer(r"[.!?]\s+", left_chunk))
    if left_match:
        left = max(0, start - window) + left_match[-1].end()
    else:
        left = max(0, start - window)

    right_chunk = text[end:min(len(text), end + window)]
    right_match = re.search(r"[.!?](\s+|$)", right_chunk)
    if right_match:
        right = end + right_match.end()
    else:
        right = min(len(text), end + window)

    return normalize_text(text[left:right])

def find_matches(text):
    matches = []
    text_lower = text.lower()

    for item in search_terms:
        term = item["term"]
        term_lower = term.lower()
        start = 0

        while (position := text_lower.find(term_lower, start)) != -1:
            end = position + len(term)

            matches.append({
                **item,
                "matched_text": text[position:end],
                "context": make_context(text, position, end)
            })

            start = end

    return matches

# Main screening

html_files = sorted(html_folder.rglob("*.html"))

if not html_files:
    raise FileNotFoundError(
        f"No HTML files found in {html_folder.resolve()}"
    )

document_results = []
match_results = []

for number, file_path in enumerate(html_files, start=1):

    document_id = extract_document_id(file_path)

    html = file_path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    soup = BeautifulSoup(html, "html.parser")

    metadata = extract_metadata(soup)
    tipo_norma = norm_type_mapping.get(metadata["rango"], "")

    if tipo_norma not in allowed_norm_types:
        print(
            f"[{number}/{len(html_files)}] "
            f"{document_id} | "
            f"Rango: {metadata['rango']} | "
            f"Skipped"
        )
        continue

    url = extract_url(soup, document_id)
    text = extract_visible_text(soup)
    matches = find_matches(text)

    base = {
        "document_id": document_id,
        "url": url,
        "file": str(file_path),
        **metadata,
        "tipo_norma": tipo_norma
    }

    matched_terms = sorted({m["term"] for m in matches})
    matched_categories = sorted({m["category"] for m in matches})
    matched_subcategories = sorted({m["subcategory"] for m in matches})
    matched_tiers = sorted({m["tier"] for m in matches})

    candidate = bool(matches)

    direct_es_matches = sum(
        m["category"] == "direct_es"
        for m in matches
    )

    economic_instruments_matches = sum(
        m["category"] == "economic_instruments"
        for m in matches
    )

    tier_1_matches = sum(
        m["tier"] == 1
        for m in matches
    )

    tier_2_matches = sum(
        m["tier"] == 2
        for m in matches
    )

    document_results.append({
        **base,
        "candidate": candidate,
        "total_matches": len(matches),
        "unique_terms": len(matched_terms),
        "direct_es_matches": direct_es_matches,
        "economic_instruments_matches": economic_instruments_matches,
        "tier_1_matches": tier_1_matches,
        "tier_2_matches": tier_2_matches,
        "matched_terms": "; ".join(matched_terms),
        "matched_categories": "; ".join(matched_categories),
        "matched_subcategories": "; ".join(matched_subcategories),
        "matched_tiers": "; ".join(str(tier) for tier in matched_tiers)
    })

    for match_number, match in enumerate(matches, start=1):
        match_results.append({
            **base,
            "match_number": match_number,
            **match
        })

    print(
        f"[{number}/{len(html_files)}] "
        f"{document_id} | "
        f"Rango: {metadata['rango']} | "
        f"Matches: {len(matches)} | "
        f"Candidate: {candidate}"
    )

# Save results cronologically

documents_df = pd.DataFrame(document_results)
matches_df = pd.DataFrame(match_results)

documents_df["_sort_date"] = pd.to_datetime(
    documents_df["fecha_publicacion"],
    dayfirst=True,
    errors="coerce"
)

matches_df["_sort_date"] = pd.to_datetime(
    matches_df["fecha_publicacion"],
    dayfirst=True,
    errors="coerce"
)

documents_df = documents_df.sort_values(
    "_sort_date"
)

matches_df = matches_df.sort_values(
    ["_sort_date", "document_id", "match_number"]
)

documents_df = documents_df.drop(columns="_sort_date")
matches_df = matches_df.drop(columns="_sort_date")

documents_df.to_csv(
    documents_csv_file,
    index=False,
    encoding="utf-8-sig"
)

matches_df.to_csv(
    matches_csv_file,
    index=False,
    encoding="utf-8-sig"
)

documents_df.to_excel(
    documents_excel_file,
    index=False
)

matches_df.to_excel(
    matches_excel_file,
    index=False
)

# End remarks

print(f"Documents processed: {len(documents_df)}")
print(f"Candidate documents: {documents_df['candidate'].sum()}")
print(f"Total matches: {len(matches_df)}")
print(f"Documents output: {documents_csv_file}")
print(f"Matches output: {matches_csv_file}")