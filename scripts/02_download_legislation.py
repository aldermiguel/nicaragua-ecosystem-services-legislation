import csv
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Script jobs
# 1- Set directories and output files
# 2- Based on discovered_legislation.csv, download the respective HTML files
# 3- Save all HTML files in the html directory

# File locations

metadata_file = Path("data/legislation/discovered_legislation.csv")

html_folder = Path("data/legislation/html")

html_folder.mkdir(parents=True, exist_ok=True)

# Set session's parameters

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Read metadata

with open(metadata_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    records = list(reader)

# Download HTML pages

for number, record in enumerate(records, start=1):
    document_id = record["document_id"]
    href = record["href"]

    # Construct the URLs
    url = "http://legislacion.asamblea.gob.ni"+ href

    output_file = (html_folder / f"{document_id}.html")

    # Skip files already downloaded
    if output_file.exists():
        continue

    response = session.get(
        url,
        headers=headers,
        timeout=30
    )

    print("Request status:", response.status_code)

    if response.status_code != 200:
        print("Download failed!")
        continue

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(response.text)

    print(f"File saved to :{output_file}")

# End remarks

print("HTML download complete.")