import re
import csv
from pathlib import Path
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Script jobs
# 1- Open the 'Asamblea Nacional de Nicaragua' website
# 2- Select 'Legislacion por materia'
# 3- Expand the category 'Medio Ambiente y Recursos Naturales'
# 4- Collect every record under the category 'Medio Ambiente y Recursos Naturales'
# 5- Save all discovered legislation as discovered_legislation.csv

# Set session's parameters

session = requests.Session()

url = "http://legislacion.asamblea.gob.ni/Normaweb.nsf/xpMainDIL.xsp"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Function: find legislation records and extract their metadata

def extract_records(soup):

    table = soup.find("table", id="view:_id1:_id163:viewPanel9")

    if table is None:
        return []

    records = []

    for link in table.find_all("a", class_="xspLinkViewColumn"):
        title = link.get_text(" ", strip=True)
        href = link.get("href", "")

        match = re.search(r"documentId=([^&]+)", href)

        if match is None:
            continue

        document_id = match.group(1)

        records.append(
            {
                "document_id": document_id,
                "title": title,
                "href": href
            }
        )

    return records

# Function: find the pagination control

def find_environmental_pager(soup):

    pager = soup.find("div", id="view:_id1:_id163:viewPanel9:pager2")

    return pager

# Load initial page

response = session.get(
    url,
    headers=headers,
    timeout=30
)

print("Request status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

# Submit 'Legislación por Materia'

form = soup.find("form", id="view:_id1")

data = {}

for element in form.find_all("input"):
    name = element.get("name")
    if name:
        data[name] = element.get("value", "")

data["$$xspsubmitid"] = "view:_id1:_id11"

response = session.post(
    url,
    data=data,
    headers=headers,
    timeout=30
)

print("Legislación por Materia:", response.status_code)

# Find the category 'Medio Ambiente y Recursos Naturales'

soup = BeautifulSoup(response.text, "html.parser")

element = None

for tag in soup.find_all("a"):
    if (tag.get_text(strip=True) == "Medio Ambiente y Recursos Naturales"):
        element = tag
        break

if element is None:
    raise RuntimeError("The category 'Medio Ambiente y Recursos Naturales' was not found.")

# Expand the category 'Medio Ambiente y Recursos Naturales'

data["view:_id1:SectionIndMateria_closed"] = "false"

data["$$xspsubmitid"] = (
    "view:_id1:_id163:viewPanel9:17:"
    "viewColumn1__expand:18"
)

data["$$xspexecid"] = (
    "view:_id1:_id163:viewPanel9"
)

response = session.post(
    url,
    params={
        "$$ajaxid":
            "view:_id1:_id163:viewPanel9_OUTER_TABLE"
    },
    data=data,
    headers=headers,
    timeout=30
)

print("Expansion request status:", response.status_code)

# Begin pagination

soup = BeautifulSoup(response.text, "html.parser")

all_records = []

previous_first_id = None

while True:

    records = extract_records(soup)

    if not records:
        break

    # Detect repeated page

    first_id = records[0]["document_id"]

    if first_id == previous_first_id:
        break

    previous_first_id = first_id

    # Add records

    all_records.extend(records)

    # Identify pager

    pager = find_environmental_pager(soup)

    if pager is None:
        break

    # Find Next

    next_control = pager.find("span", class_="xspNext")

    if next_control is None:
        break

    next_id = next_control.get("id")

    if next_id is None:
        break

    # Submit 'Next'

    data["$$xspsubmitid"] = next_id

    data["$$xspexecid"] = pager.get("id")

    data["view:_id1:SectionIndMateria_closed"] = "false"

    response = session.post(
        url,
        params={
            "$$ajaxid":
                "view:_id1:_id163:viewPanel9_OUTER_TABLE"
        },
        data=data,
        headers=headers,
        timeout=30
    )

    print("Next request status:", response.status_code)

    if response.status_code != 200:
        break

    # Prepare next page

    soup = BeautifulSoup(response.text, "html.parser")

# Deduplicate records

unique_records = {}

for record in all_records:
    document_id = record["document_id"]
    unique_records[document_id] = record

all_records = list(unique_records.values())

# Save metadata

output_folder = Path("data/legislation")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "discovered_legislation.csv"
excel_file = output_folder / "discovered_legislation.xlsx"

with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["document_id", "title", "href"])
    writer.writeheader()
    writer.writerows(all_records)

pd.DataFrame(all_records).to_excel(excel_file, index=False)

# End remarks

print("Total records collected:", len(all_records))
print(f"Saved CSV to: {output_file}")
print(f"Saved Excel to: {excel_file}")