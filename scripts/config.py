from pathlib import Path

# Shared settings for scripts 01-04

# Repository root, so the scripts can be run from any folder

ROOT = Path(__file__).resolve().parents[1]

# Address of the 'Asamblea Nacional de Nicaragua' legislative repository

BASE_URL = "http://legislacion.asamblea.gob.ni"

# File locations

LEGISLATION_FOLDER = ROOT / "data" / "legislation"

DISCOVERED_FILE = LEGISLATION_FOLDER / "discovered_legislation.csv"
DISCOVERED_EXCEL_FILE = LEGISLATION_FOLDER / "discovered_legislation.xlsx"
SEARCH_TERMS_FILE = LEGISLATION_FOLDER / "search_terms.csv"
MANIFEST_FILE = LEGISLATION_FOLDER / "manifest.csv"

HTML_FOLDER = LEGISLATION_FOLDER / "html"
CLEAN_HTML_FOLDER = LEGISLATION_FOLDER / "clean_html"
SCREENING_FOLDER = LEGISLATION_FOLDER / "screening"
