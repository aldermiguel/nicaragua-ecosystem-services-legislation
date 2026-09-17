from pathlib import Path
from bs4 import BeautifulSoup

html_folder = Path("data/legislation/html")
clean_folder = Path("data/legislation/clean_html")

clean_folder.mkdir(parents=True, exist_ok=True)

for input_file in html_folder.glob("*.html"):

    soup = BeautifulSoup(input_file.read_text(encoding="utf-8"), "html.parser")

    section = soup.find(id="view:_id1:section1_contents")

    if section is None:
        print(f"Section not found: {input_file.name}")
        continue

    title = soup.find(id="view:_id1:computedField3")
    title = title.get_text(" ", strip=True) if title else input_file.stem

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 900px;
    margin: 40px auto;
    line-height: 1.5;
}}
</style>
</head>
<body>
{section.decode_contents()}
</body>
</html>
"""

    output_file = clean_folder / input_file.name
    output_file.write_text(html, encoding="utf-8")

    print(f"Created: {output_file}")

# End remarks

print("HTML transformation complete.")