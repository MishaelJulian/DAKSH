import re
from pathlib import Path

html_path = Path("logs/after_view.html")
if not html_path.exists():
    print("logs/after_view.html not found!")
    exit(1)

html = html_path.read_text(encoding="utf-8")

# Let's find caseBusinessDiv_caseType using a simple regex
match = re.search(r'<div[^>]*id=["\']caseBusinessDiv_caseType["\'][^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
if match:
    div_content = match.group(1)
    print("=== DIV CONTENT (First 1500 chars) ===")
    print(div_content[:1500])
    
    # Check for tables inside it
    tables = re.findall(r'<table[^>]*>(.*?)</table>', div_content, re.DOTALL | re.IGNORECASE)
    print(f"\nFound {len(tables)} tables inside the div.")
    for idx, t in enumerate(tables):
        print(f"Table {idx} content (First 300 chars):")
        print(t[:300].strip())
        print("-" * 40)
else:
    # Let's search if the ID is slightly different or if it's there
    print("Div not found by regex. Searching for occurrences of 'caseBusinessDiv' in the file...")
    occurrences = [line.strip() for line in html.splitlines() if "caseBusinessDiv" in line]
    for idx, occ in enumerate(occurrences[:10]):
        print(f"  {idx}: {occ}")
