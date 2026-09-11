"""Diagnostic script investigating eCourts v6 session initialization on services.ecourts.gov.in."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== eCourts v6 Session Investigation on services.ecourts.gov.in ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Open https://services.ecourts.gov.in/ecourtindia_v6/
        print("\n1. Navigating to https://services.ecourts.gov.in/ecourtindia_v6/...")
        resp = page.goto("https://services.ecourts.gov.in/ecourtindia_v6/", wait_until="networkidle", timeout=30000)
        time.sleep(2)
        print(f"   Status Code: {resp.status if resp else 'N/A'}")
        print(f"   Final URL  : {page.url}")
        print(f"   Page Title : '{page.title()}'")
        body_text = page.inner_text("body")[:300].replace("\n", " ")
        print(f"   Body Text  : '{body_text}'")

        # Step 2: Check cookies set
        cookies = context.cookies()
        print(f"\n2. Cookies set ({len(cookies)}): {[c['name'] for c in cookies]}")

        # Step 3: Check selectors on page
        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"\n3. #sess_state_code visible: {has_state}")

        # Step 4: Search for Case Status buttons or links
        links = page.locator("a, button, [onclick]").all()
        print(f"   Interactive elements on page: {len(links)}")
        for idx, l in enumerate(links[:15]):
            try:
                txt = l.inner_text().strip()
                href = l.get_attribute("href") or ""
                onclick = l.get_attribute("onclick") or ""
                print(f"     [{idx}] Text: '{txt}' | href: '{href}' | onclick: '{onclick}'")
            except Exception:
                pass

        context.close()
        browser.close()
    print("\n=== Investigation Complete ===")

if __name__ == "__main__":
    main()
