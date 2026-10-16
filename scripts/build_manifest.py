import csv
import hashlib
from config import ROOT, HTML_FOLDER, MANIFEST_FILE

# Script jobs
# 1- List every HTML document in the html directory
# 2- Compute its size and SHA-256 checksum
#    (line endings are normalised to LF first, so Windows and Mac/Linux checkouts give the same result)
# 3- Save the list as manifest.csv, so users can verify the corpus is unchanged

rows = []

for file_path in sorted(HTML_FOLDER.glob("*.html")):
    content = file_path.read_bytes().replace(b"\r\n", b"\n")

    rows.append(
        {
            "document_id": file_path.stem,
            "file": file_path.relative_to(ROOT).as_posix(),
            "size_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest()
        }
    )

with open(MANIFEST_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["document_id", "file", "size_bytes", "sha256"])
    writer.writeheader()
    writer.writerows(rows)

# End remarks

print("Documents listed:", len(rows))
print(f"Saved manifest to: {MANIFEST_FILE}")
