"""Diagnostic script testing in-DOM menu click navigation on services.ecourts.gov.in."""
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
    print("=== Testing In-DOM Menu Click Navigation on eCourts v6 ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Opening https://services.ecourts.gov.in/ecourtindia_v6/...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/", wait_until="networkidle", timeout=30000)
        time.sleep(3)

        print(f"   Current URL  : {page.url}")
        print(f"   Current Title: '{page.title()}'")

        # Find all Case Status links/buttons/menu items
        cs_elements = page.locator("a:has-text('Case Status'), button:has-text('Case Status'), [onclick*='casestatus'], a[href*='casestatus']").all()
        print(f"   Found {len(cs_elements)} 'Case Status' elements in DOM:")
        for idx, el in enumerate(cs_elements):
            txt = el.inner_text().strip()
            href = el.get_attribute("href") or ""
            onclick = el.get_attribute("onclick") or ""
            print(f"     [{idx}] text='{txt}' | href='{href}' | onclick='{onclick}'")

        if cs_elements:
            print("\n2. Clicking first 'Case Status' element...")
            cs_elements[0].click()
            time.sleep(4)

            print(f"   Post-click URL  : {page.url}")
            print(f"   Post-click Title: '{page.title()}'")
            body_text = page.inner_text("body")[:300].replace("\n", " ")
            print(f"   Post-click Body : '{body_text}'")

            has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
            print(f"   #sess_state_code visible: {has_state}")

        context.close()
        browser.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
