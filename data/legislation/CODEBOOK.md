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

## `coding/` — statement-level coding of the selected documents

Produced by `05_code_provisions.py` from the original (first published) text of the 18 documents analysed in the article. The coding combines a dictionary-assisted first pass with a manual review of every statement that mentions an ES search term.

### Inputs

- `selected_legislation.csv`: the 18 documents (one row each) with `document_id`, `no_norma`, `tipo_norma`, `year`, `domain` and `role` (`main`, `regulation` or `reform`) as in Table 3 of the article, and `label_en` (English label used in the article).
- `coding_dictionary.csv`: one row per regular expression (`dimension`, `code`, `pattern`, `note`). Matching is case-insensitive. Dimensions: `logic` (conservation logic), `actor`, `deontic`, `aim`, `or_else`, `instrument` and `deferral`.
- `manual_review.csv`: reviewer decisions that replace dictionary codes for specific ES statements. A row is matched by `label_en` and the first characters of the statement (`text_start`); non-empty `operationality`, `decision_authority` and `es_function` values replace the dictionary codes; `notes` gives the reason.

### Unit of analysis

A **statement** is one paragraph or numbered item of the document body, starting at Article 1 (preambles and *considerandos* are excluded). Lines that only hold a heading or a number, and short labels ending in a colon (such as defined terms), are joined to the following line. Statements shorter than four words are dropped.

### `coded_statements.csv`

One row per statement (6,076 rows).

| Column | Type | Description |
|---|---|---|
| `document_id`, `label_en`, `no_norma`, `tipo_norma`, `year`, `domain`, `role` | text/integer | From `selected_legislation.csv`. |
| `statement_number` | integer | Position of the statement in the document. |
| `words` | integer | Number of words. |
| `text` | text | Statement text (Spanish). |
| `command_control` | boolean | Statement carries command-and-control language (protected areas, prohibitions, permits, sanctions, zoning). |
| `market_valuation` | boolean | Statement carries market-valuation language (valuation, payments, markets, incentives, fees, funds). |
| `participatory_plural` | boolean | Statement carries participatory or plural-knowledge language (participation, consultation, co-management, Indigenous and local communities, traditional knowledge). |
| `es_statement` | boolean | Statement contains at least one term from `search_terms.csv`. |
| `es_terms` | text | ES terms found, separated by `; `. |
| `period` | text | `1996-2000`, `2001-2007`, `2008-2013` or `2014-2022`, from `year`. |

### `es_statements.csv`

One row per statement with `es_statement` true (71 rows). Columns of `coded_statements.csv`, plus:

| Column | Type | Description |
|---|---|---|
| `actor_central`, `actor_subnational`, `actor_community_private` | boolean | Statement names a central-state body; a municipal, regional or territorial government; or communities, owners, users or private actors. |
| `deontic_obligation`, `deontic_prohibition`, `deontic_permission` | boolean | Explicit deontic operator (*deberá*, *se prohíbe*, *podrá* and variants). |
| `aim_operational`, `aim_promotional` | boolean | Aim verb is operational (*establecer*, *crear*, *pagar*, *cobrar*, *reglamentar*...) or promotional (*promover*, *fomentar*, *impulsar*, *incentivar*...). |
| `or_else` | boolean | Statement names a sanction or consequence for non-compliance. |
| `deferral` | boolean | Statement refers its own operationalisation to a future instrument (*reglamentará*, *será regulado por una Ley Especial*, *se establecerán los criterios*...). |
| `instrument_payer`, `instrument_amount_method`, `instrument_fund`, `instrument_procedure` | boolean | Statement specifies who pays, how much or how it is calculated, where the money goes, or an administrative procedure. |
| `statement_type` | text | Institutional Grammar type: `definition`, `strategy` (no deontic), `norm` (deontic, or named actor with operational aim) or `rule` (norm with a sanction). |
| `operationality` | text | `declarative` (definitions, objectives, promotional strategies), `deferring` (operationalisation referred to a future instrument) or `operational` (a named actor is given an action that applies directly). Reviewed value. |
| `instrument_elements` | integer | Number of the four `instrument_*` items present (0-4). |
| `decision_authority` | text | `central_only`, `central_shared` (central and other actors), `non_central_only` or `unspecified`. Actors named only as beneficiaries or interest holders are not decision-makers. Reviewed value. |
| `es_function` | text | Main function of the ES reference: `market_valuation`, `participatory_plural`, `command_control` or `general_es`. Reviewed value. |
| `auto_operationality`, `auto_decision_authority` | text | Dictionary codes before manual review. |
| `review_status` | text | `reviewed_no_change`, or the status recorded in `manual_review.csv` for changed codes. |
| `review_notes` | text | Reason for a changed code. |

### `logic_by_document.csv`

One row per selected document: number of statements and ES statements, share of statements carrying each logic (`*_share`), and `logics_present` (0-3).

### `es_operationality_summary.csv`

ES statements by `period`, `es_function` and `operationality`, with the number that assign decision authority to the central state only (`central_only`), that name no actor (`unspecified_actor`), and that specify who pays or how much (`with_payer_or_amount`).
