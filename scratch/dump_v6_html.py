"""Diagnostic script dumping raw HTML of services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Dumping HTML of services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        html = page.content()
        with open("scratch/v6_dump.html", "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Dumped {len(html)} bytes to scratch/v6_dump.html.")
        print(f"Page Title: '{page.title()}'")
        body_text = page.inner_text("body")[:400].replace("\n", " ")
        print(f"Body Text : '{body_text}'")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
