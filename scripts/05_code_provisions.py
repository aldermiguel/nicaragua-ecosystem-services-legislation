import re
import pandas as pd
from bs4 import BeautifulSoup
from config import (
    HTML_FOLDER,
    SEARCH_TERMS_FILE,
    CODING_FOLDER
)

# Script jobs
# 1- Load the selected legislation, the coding dictionary and the ES search terms
# 2- Split each selected document into statements (one paragraph or numbered item each)
# 3- Code every statement for conservation logic (command-and-control, market-valuation, participatory-plural)
# 4- Code ES statements with Institutional Grammar components (actor, deontic, aim, or else, deferral, instrument details)
# 5- Apply manual review decisions from manual_review.csv, if present
# 6- Create datasets
#   -> coded_statements.csv: one row per statement in the selected documents
#   -> es_statements.csv: one row per statement that mentions an ES search term, with review columns
#   -> logic_by_document.csv: share of statements carrying each logic, per document
#   -> es_operationality_summary.csv: ES statements by period, logic and operationality

# File locations

coding_folder = CODING_FOLDER

selected_file = coding_folder / "selected_legislation.csv"
dictionary_file = coding_folder / "coding_dictionary.csv"

statements_csv_file = coding_folder / "coded_statements.csv"
es_csv_file = coding_folder / "es_statements.csv"
logic_csv_file = coding_folder / "logic_by_document.csv"
summary_csv_file = coding_folder / "es_operationality_summary.csv"
review_file = coding_folder / "manual_review.csv"

es_excel_file = coding_folder / "es_statements.xlsx"

# Periods used to compare layers over time

period_bins = [1990, 2000, 2007, 2013, 2030]
period_labels = ["1996-2000", "2001-2007", "2008-2013", "2014-2022"]

# Body of a document starts at its first article

body_start = re.compile(r"(?im)^\s*(Art[ií]culo|Arto)\.?\s*1\b")

# Lines that only carry a heading or a number are merged with the next line

heading_only = re.compile(
    r"(?i)^\s*((Art[ií]culo|Arto|Art)\.?\s*\d+[\.\-\s]*|"
    r"\d+[\.\)\-]?|[a-z][\.\)]|cap[ií]tulo\s+\S+|t[ií]tulo\s+\S+|secci[oó]n\s+\S+)\s*$"
)

# Definition statements: "Term: meaning" or "se entiende por"

definition_pattern = re.compile(
    r"(?i)(^\s*(\d+[\.\)\-]?\s*)?[^:;\.]{2,90}:\s*\S)|se entiende(n)? por|se define(n)? como"
)

# Functions

def load_dictionary():
    dictionary = pd.read_csv(dictionary_file)
    compiled = {}

    for (dimension, code), group in dictionary.groupby(["dimension", "code"]):
        pattern = "|".join(f"(?:{p})" for p in group["pattern"])
        compiled[(dimension, code)] = re.compile(pattern, re.IGNORECASE)

    return compiled

def load_es_terms():
    terms = pd.read_csv(SEARCH_TERMS_FILE)["term"].tolist()
    terms = sorted(terms, key=len, reverse=True)
    pattern = "|".join(re.escape(term) for term in terms)

    return re.compile(pattern, re.IGNORECASE)

def document_text(document_id):
    html = (HTML_FOLDER / f"{document_id}.html").read_text(
        encoding="utf-8",
        errors="ignore"
    )
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    text = text.replace("\xa0", " ")

    return text

def split_statements(text):
    start = body_start.search(text)
    body = text[start.start():] if start else text

    lines = [re.sub(r"\s+", " ", line).strip() for line in body.split("\n")]
    lines = [line for line in lines if line]

    statements = []
    carry = ""

    for line in lines:
        short_label = line.endswith(":") and len(line.split()) <= 12

        if heading_only.match(line) or short_label:
            carry = f"{carry} {line}".strip()
            continue

        statements.append(f"{carry} {line}".strip())
        carry = ""

    return statements

def has(compiled, dimension, code, text):
    return bool(compiled[(dimension, code)].search(text))

def code_statement(compiled, es_terms, text):
    row = {
        "command_control": has(compiled, "logic", "command_control", text),
        "market_valuation": has(compiled, "logic", "market_valuation", text),
        "participatory_plural": has(compiled, "logic", "participatory_plural", text)
    }

    es_match = es_terms.findall(text)
    row["es_statement"] = bool(es_match)
    row["es_terms"] = "; ".join(sorted({m.lower() for m in es_match}))

    return row

def code_grammar(compiled, text):
    row = {}

    for code in ["central", "subnational", "community_private"]:
        row[f"actor_{code}"] = has(compiled, "actor", code, text)

    for code in ["obligation", "prohibition", "permission"]:
        row[f"deontic_{code}"] = has(compiled, "deontic", code, text)

    row["aim_operational"] = has(compiled, "aim", "operational", text)
    row["aim_promotional"] = has(compiled, "aim", "promotional", text)
    row["or_else"] = has(compiled, "or_else", "sanction", text)
    row["deferral"] = has(compiled, "deferral", "deferral", text)

    for code in ["payer", "amount_method", "fund", "procedure"]:
        row[f"instrument_{code}"] = has(compiled, "instrument", code, text)

    deontic = row["deontic_obligation"] or row["deontic_prohibition"] or row["deontic_permission"]
    actor = row["actor_central"] or row["actor_subnational"] or row["actor_community_private"]

    if definition_pattern.search(text[:120]) and not deontic:
        statement_type = "definition"
    elif (deontic or row["aim_operational"]) and row["or_else"]:
        statement_type = "rule"
    elif deontic or (actor and row["aim_operational"] and not row["aim_promotional"]):
        statement_type = "norm"
    else:
        statement_type = "strategy"

    row["statement_type"] = statement_type
    if statement_type == "definition":
        operationality = "declarative"
    elif row["deferral"]:
        operationality = "deferring"
    elif statement_type in ("norm", "rule") and actor and row["aim_operational"]:
        operationality = "operational"
    else:
        operationality = "declarative"

    row["operationality"] = operationality
    row["instrument_elements"] = sum(
        row[f"instrument_{code}"] for code in ["payer", "amount_method", "fund", "procedure"]
    )

    if row["actor_central"] and not (row["actor_subnational"] or row["actor_community_private"]):
        authority = "central_only"
    elif row["actor_central"]:
        authority = "central_shared"
    elif row["actor_subnational"] or row["actor_community_private"]:
        authority = "non_central_only"
    else:
        authority = "unspecified"

    row["decision_authority"] = authority

    return row

# Process the selected documents

compiled = load_dictionary()
es_terms = load_es_terms()
selected = pd.read_csv(selected_file, dtype=str)
selected["year"] = selected["year"].astype(int)

rows = []

for _, document in selected.iterrows():
    statements = split_statements(document_text(document["document_id"]))

    for number, text in enumerate(statements, start=1):
        row = {
            "document_id": document["document_id"],
            "label_en": document["label_en"],
            "no_norma": document["no_norma"],
            "tipo_norma": document["tipo_norma"],
            "year": document["year"],
            "domain": document["domain"],
            "role": document["role"],
            "statement_number": number,
            "words": len(text.split()),
            "text": text
        }
        row.update(code_statement(compiled, es_terms, text))
        rows.append(row)

statements = pd.DataFrame(rows)
statements["period"] = pd.cut(
    statements["year"],
    bins=period_bins,
    labels=period_labels
).astype(str)

# Statements shorter than four words are headings or residue

statements = statements[statements["words"] >= 4].reset_index(drop=True)

# Institutional Grammar coding of ES statements

es = statements[statements["es_statement"]].copy()
grammar = pd.DataFrame(
    [code_grammar(compiled, text) for text in es["text"]],
    index=es.index
)
es = pd.concat([es, grammar], axis=1)

es["es_function"] = es.apply(
    lambda r: "market_valuation" if r["market_valuation"]
    else ("participatory_plural" if r["participatory_plural"]
          else ("command_control" if r["command_control"] else "general_es")),
    axis=1
)

# Manual review: reviewed codes replace dictionary codes where a reviewer changed them

es["auto_operationality"] = es["operationality"]
es["auto_decision_authority"] = es["decision_authority"]
es["review_status"] = "not_reviewed"
es["review_notes"] = ""

if review_file.exists():
    review = pd.read_csv(review_file, dtype=str).fillna("")
    es["review_status"] = "reviewed_no_change"

    for _, item in review.iterrows():
        mask = (
            (es["label_en"] == item["label_en"])
            & (es["text"].str.startswith(item["text_start"]))
        )

        if mask.sum() != 1:
            print(f"Review row not matched once: {item['label_en']} | {item['text_start']}")
            continue

        for column in ["operationality", "decision_authority", "es_function"]:
            if item.get(column, ""):
                es.loc[mask, column] = item[column]

        es.loc[mask, "review_status"] = item["review_status"]
        es.loc[mask, "review_notes"] = item["notes"]

# Summary: logic shares by document

logic_columns = ["command_control", "market_valuation", "participatory_plural"]

logic = (
    statements
    .groupby(["label_en", "year", "domain", "period"], observed=True)
    .agg(
        statements=("text", "size"),
        es_statements=("es_statement", "sum"),
        **{f"{c}_share": (c, "mean") for c in logic_columns}
    )
    .reset_index()
    .sort_values(["year", "label_en"])
)
logic["logics_present"] = (logic[[f"{c}_share" for c in logic_columns]] > 0).sum(axis=1)

# Summary: ES statements by period, function and operationality

summary = (
    es
    .groupby(["period", "es_function", "operationality"], observed=True)
    .agg(
        es_statements=("text", "size"),
        central_only=("decision_authority", lambda s: (s == "central_only").sum()),
        unspecified_actor=("decision_authority", lambda s: (s == "unspecified").sum()),
        with_payer_or_amount=("instrument_elements", lambda s: 0),
    )
    .reset_index()
)
summary["with_payer_or_amount"] = (
    es
    .assign(spec=es["instrument_payer"] | es["instrument_amount_method"])
    .groupby(["period", "es_function", "operationality"], observed=True)["spec"]
    .sum()
    .values
)

# Save outputs

statements.to_csv(statements_csv_file, index=False, encoding="utf-8-sig")
es.to_csv(es_csv_file, index=False, encoding="utf-8-sig")
es.to_excel(es_excel_file, index=False)
logic.to_csv(logic_csv_file, index=False, encoding="utf-8-sig")
summary.to_csv(summary_csv_file, index=False, encoding="utf-8-sig")

print(f"Statements coded: {len(statements)}")
print(f"ES statements: {len(es)}")
print(f"Saved to: {coding_folder}")
