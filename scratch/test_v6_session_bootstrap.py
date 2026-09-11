"""Diagnostic script testing eCourts v6 session bootstrap from home/index -> casestatus."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing eCourts v6 Session Bootstrap ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Open v6 home
        url_home = "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index"
        print(f"\n1. Navigating to {url_home}...")
        resp1 = page.goto(url_home, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"   Status Code: {resp1.status if resp1 else 'N/A'}")
        print(f"   Final URL  : {page.url}")
        print(f"   Title      : '{page.title()}'")
        body1 = page.inner_text("body")[:300].replace("\n", " ")
        print(f"   Body       : '{body1}'")

        # Check links on home
        links = page.locator("a, button").all()
        print(f"   Found {len(links)} interactive elements on home.")
        cs_links = [l for l in links if "case status" in (l.inner_text() + l.get_attribute("href") or "").lower()]
        print(f"   Found {len(cs_links)} Case Status links on home.")

        if cs_links:
            print("2. Clicking Case Status link...")
            cs_links[0].click()
            time.sleep(3)
            print(f"   Post-click URL  : {page.url}")
            print(f"   Post-click Title: {page.title()}")
            body2 = page.inner_text("body")[:300].replace("\n", " ")
            print(f"   Post-click Body : '{body2}'")
            has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
            print(f"   #sess_state_code visible: {has_state}")

        context.close()
        browser.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
