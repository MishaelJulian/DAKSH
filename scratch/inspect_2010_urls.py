"""Diagnostic script inspecting form actions and meta tags in 2010 benchmark HTML files."""
from __future__ import annotations
import glob
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Inspecting 2010 HTML Snapshots and Logs ===")
    files = glob.glob("eCourts_Executive_Petitions_2010_Final/snapshots/*.html") + glob.glob("eCourts_Executive_Petitions_2010_Final/logs/*.html") + glob.glob("logs/*.html")
    print(f"Found {len(files)} HTML files.")

    for fpath in files[:10]:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        print(f"\nFile: {fpath}")
        # Find forms and action attributes
        import re
        forms = re.findall(r'<form[^>]*>', content, re.IGNORECASE)
        for form in forms[:5]:
            print(f"  Form: {form}")
        # Find base href or og:url
        meta_urls = re.findall(r'<meta[^>]*og:url[^>]*>', content, re.IGNORECASE)
        for meta in meta_urls:
            print(f"  Meta URL: {meta}")

if __name__ == "__main__":
    main()
