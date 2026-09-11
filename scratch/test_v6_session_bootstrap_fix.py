"""Diagnostic script testing session initialization options for eCourts v6 (services.ecourts.gov.in)."""
from __future__ import annotations
import sys
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def test_option_1() -> None:
    print("\n--- Test Option 1: Open https://services.ecourts.gov.in/ecourtindia_v6/ then navigate to casestatus ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Open home
        print("1. Opening https://services.ecourts.gov.in/ecourtindia_v6/...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/", wait_until="domcontentloaded")
        time.sleep(2)

        # Step 2: Open casestatus/index
        print("2. Opening https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded")
        time.sleep(3)

        body = page.inner_text("body")[:250].replace("\n", " ")
        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"   Body: '{body}'")
        print(f"   #sess_state_code visible: {has_state}")

        context.close()
        browser.close()

def test_option_2() -> None:
    print("\n--- Test Option 2: Open https://services.ecourts.gov.in/ directly with Referer header ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                "Referer": "https://services.ecourts.gov.in/ecourtindia_v6/"
            }
        )
        page = context.new_page()

        print("1. Opening https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded")
        time.sleep(3)

        body = page.inner_text("body")[:250].replace("\n", " ")
        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"   Body: '{body}'")
        print(f"   #sess_state_code visible: {has_state}")

        context.close()
        browser.close()

def test_option_3() -> None:
    print("\n--- Test Option 3: Navigate via eCourts Portal Link ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Opening https://ecourts.gov.in/...")
        page.goto("https://ecourts.gov.in/", wait_until="domcontentloaded")
        time.sleep(2)

        print("2. Clicking 'District Court Services'...")
        link = page.locator("a:has-text('District Court Services'), a[href*='services.ecourts.gov.in']").first
        if link.count() > 0:
            link.click()
            time.sleep(3)

        print(f"   URL: {page.url}")
        body = page.inner_text("body")[:250].replace("\n", " ")
        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"   Body: '{body}'")
        print(f"   #sess_state_code visible: {has_state}")

        context.close()
        browser.close()

def main() -> None:
    test_option_1()
    test_option_2()
    test_option_3()

if __name__ == "__main__":
    main()
