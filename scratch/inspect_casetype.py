import re
from pathlib import Path

html_path = Path("logs/fail_dump_EX_18_2010.html")
if not html_path.exists():
    print("logs/fail_dump_EX_18_2010.html not found!")
    exit(1)

html = html_path.read_text(encoding="utf-8")

m = re.search(r'<table[^>]*class=["\'][^"\']*case_status_table[^"\']*["\'][^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
if m:
    print("=== CASE STATUS TABLE ===")
    print(m.group(1).strip())
else:
    print("Table not found!")
