"""Diagnostic script testing navigation in browser.py context."""
from __future__ import annotations
import sys
from pathlib import Path
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

def main() -> None:
    print("=== Testing browser navigation with Referer header ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                "Referer": "https://services.ecourts.gov.in/ecourtindia_v6/"
            }
        )
        page = context.new_page()

        print("Step 1: goto https://services.ecourts.gov.in/ecourtindia_v6/")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/", wait_until="domcontentloaded")
        time.sleep(2)

        print("Step 2: goto https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index with referer")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded", referer="https://services.ecourts.gov.in/ecourtindia_v6/")
        time.sleep(3)

        body = page.inner_text("body")[:250].replace("\n", " ")
        print(f"Body: '{body}'")

        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"#sess_state_code visible: {has_state}")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
