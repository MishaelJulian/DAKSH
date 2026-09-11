"""Diagnostic script testing fillLangState cookie bootstrap for services.ecourts.gov.in."""
from __future__ import annotations
import sys
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing eCourts v6 Cookie Bootstrap via fillLangState ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Opening https://services.ecourts.gov.in/ecourtindia_v6/?p=home/fillLangState&lang=English&code=english...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=home/fillLangState&lang=English&code=english", wait_until="domcontentloaded")
        time.sleep(2)

        print("2. Opening https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded")
        time.sleep(3)

        body = page.inner_text("body")[:250].replace("\n", " ")
        print(f"Body: '{body}'")

        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"#sess_state_code visible: {has_state}")

        context.close()
        browser.close()
    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
