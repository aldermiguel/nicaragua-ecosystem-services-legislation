# Codebook

This file describes every column of the datasets in `data/legislation/`. Column names in Spanish (`titulo`, `rango`, `materia`, `no_norma`, `no_gaceta`, `fecha_publicacion`) keep the field labels shown on the *Asamblea Nacional de Nicaragua* website; the remaining names were defined for this workflow.

All CSV files are UTF-8 encoded. The screening CSV files include a byte-order mark so that Excel displays accented characters correctly. Each `.xlsx` file is a copy of the CSV file with the same name.

## `discovered_legislation.csv`

One row per legislative record listed under *Medio Ambiente y Recursos Naturales* (746 rows). Produced by `01_discover_legislation.py`.

| Column | Type | Description | Example |
|---|---|---|---|
| `document_id` | text | Unique identifier of the record in the legislative repository. Also the name of the HTML file in `html/` and `clean_html/`. | `864AD46E8D20CFCF06258A78006871BE` |
| `title` | text | Title of the record as displayed in the repository's list view. | `Ley del Digesto Jurídico Nicaragüense de la Materia de Medio Ambiente y Recursos Naturales` |
| `href` | text | Relative URL of the record; prefix it with `http://legislacion.asamblea.gob.ni` to open it. | `/Normaweb.nsf/xpNormaJuridica.xsp?documentId=864AD...&action=openDocument` |

## `search_terms.csv`

The dictionary of Spanish search terms used by `04_screen_legislation.py` (21 rows).

| Column | Type | Description | Example |
|---|---|---|---|
| `term` | text | Search term. Matching is case-insensitive and accent-sensitive, and finds the term anywhere in the document's visible text. | `servicios ambientales` |
| `category` | text | Thematic group: `direct_es` (direct references to ecosystem services or functions) or `economic_instruments` (economic instruments based on ecosystem services). | `direct_es` |
| `subcategory` | text | Category within the group: `ecosystem_services`, `ecosystem_functions`, `payments`, `compensation`, `incentives` or `markets`. | `ecosystem_services` |
| `tier` | integer | `1` for `direct_es` terms, `2` for `economic_instruments` terms. | `1` |

## `manifest.csv`

One row per HTML document in `html/` (746 rows). Produced by `build_manifest.py`; use it to check that the corpus has not changed.

| Column | Type | Description | Example |
|---|---|---|---|
| `document_id` | text | As in `discovered_legislation.csv`. | `00131F646A1707CC062570A100583FC0` |
| `file` | text | Path of the HTML file relative to the repository root. | `data/legislation/html/00131F646A1707CC062570A100583FC0.html` |
| `size_bytes` | integer | File size in bytes, after normalising line endings to LF. | `12902` |
| `sha256` | text | SHA-256 checksum of the file, after normalising line endings to LF. | `686a5218...` |

## `screening/screening_documents.csv`

One row per screened document (492 rows): every record whose `rango` is a law, decree or regulation. Records of other types are not included. Rows are ordered by publication date, then `document_id`. Produced by `04_screen_legislation.py`. The examples come from the *Reglamento de Áreas Protegidas de Nicaragua*.

| Column | Type | Description | Example |
|---|---|---|---|
| `document_id` | text | As in `discovered_legislation.csv`. | `2225795ADAD762DF06257217006632B7` |
| `url` | text | Address of the document in the legislative repository. | `http://legislacion.asamblea.gob.ni/Normaweb.nsf/xpNormaJuridica.xsp?documentId=...&action=openDocument` |
| `file` | text | Path of the screened HTML file relative to the repository root. | `data/legislation/html/2225795ADAD762DF06257217006632B7.html` |
| `titulo` | text | Title (*Título*) from the document's metadata. | `Reglamento de Áreas Protegidas de Nicaragua` |
| `rango` | text | Legal rank (*Rango*) as recorded on the website: `Decretos Ejecutivos`, `Decretos Legislativos`, `Decreto Presidencial`, `Decretos - Ley`, `Leyes` or `Reglamentos`. | `Decretos Ejecutivos` |
| `materia` | text | Subject matter (*Materia*); several subjects are separated by commas. | `Medio Ambiente y Recursos Naturales` |
| `no_norma` | text | Number of the legal instrument (*No. Norma*); `S/N` means unnumbered; empty when not reported. | `14-99` |
| `no_gaceta` | text | Issue(s) of *La Gaceta, Diario Oficial* in which it was published (*No. Gaceta*). | `42 y 43` |
| `fecha_publicacion` | date (DD/MM/YYYY) | Publication date (*Fecha Publicación*). | `03/03/1999` |
| `tipo_norma` | text | Type used in the analysis, grouped from `rango`: `Ley`, `Decreto`, `Decreto-Ley` or `Reglamento`. | `Decreto` |
| `candidate` | logical (`True`/`False`) | `True` if at least one search term was found. | `True` |
| `total_matches` | integer | Number of matches of all search terms. | `4` |
| `unique_terms` | integer | Number of different search terms found. | `1` |
| `direct_es_matches` | integer | Matches of `direct_es` terms. | `4` |
| `economic_instruments_matches` | integer | Matches of `economic_instruments` terms. | `0` |
| `tier_1_matches` | integer | Matches of tier 1 terms. | `4` |
| `tier_2_matches` | integer | Matches of tier 2 terms. | `0` |
| `matched_terms` | text | Different terms found, in alphabetical order, separated by `; `. Empty when none. | `servicios ambientales` |
| `matched_categories` | text | Different categories found, separated by `; `. | `direct_es` |
| `matched_subcategories` | text | Different subcategories found, separated by `; `. | `ecosystem_services` |
| `matched_tiers` | text | Different tiers found, separated by `; `. | `1` |

Note that a longer term contains a shorter one: a match of `pago por servicios ambientales` is also counted as a match of `servicios ambientales`.

## `screening/screening_matches.csv`

One row per individual match of a search term (322 rows). The first ten columns (`document_id` to `tipo_norma`) are the same as in `screening_documents.csv`.

| Column | Type | Description | Example |
|---|---|---|---|
| `match_number` | integer | Running number of the match within its document. Numbering follows the order of `search_terms.csv` and, within a term, the position in the text. | `1` |
| `term` | text | Search term that was matched. | `servicios ambientales` |
| `category` | text | Category of the term (see `search_terms.csv`). | `direct_es` |
| `subcategory` | text | Subcategory of the term. | `ecosystem_services` |
| `tier` | integer | Tier of the term. | `1` |
| `matched_text` | text | The text as it appears in the document, with its original capitalisation. | `SERVICIOS AMBIENTALES` |
| `context` | text | The sentence(s) around the match, cut at the nearest sentence boundary within 1,000 characters on each side. | `SERVICIOS AMBIENTALES: Elementos ambientales y sus Asociaciones ...` |
