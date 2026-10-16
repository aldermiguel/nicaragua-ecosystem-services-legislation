import argparse
import subprocess
import sys
from config import ROOT

# Script jobs
# 1- Run scripts 01-04 in order
# 2- With --offline, skip the web stages (01-02) and reuse the committed HTML documents

parser = argparse.ArgumentParser(description="Run the legislation screening workflow.")
parser.add_argument(
    "--offline",
    action="store_true",
    help="skip discovery and download; reproduce the screening from the committed HTML files"
)
args = parser.parse_args()

web_stages = [
    "01_discover_legislation.py",
    "02_download_legislation.py",
    "build_manifest.py"
]

local_stages = [
    "03_transform_html_files.py",
    "04_screen_legislation.py"
]

stages = local_stages if args.offline else web_stages + local_stages

for script in stages:
    print(f"\n=== Running {script} ===")
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True)

# End remarks

print("\nWorkflow complete.")
