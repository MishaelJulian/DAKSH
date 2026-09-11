"""Diagnostic script testing index.php and POST methods for services.ecourts.gov.in."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing URL Formats & HTTP Methods on eCourts v6 ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        urls_to_test = [
            "https://services.ecourts.gov.in/ecourtindia_v6/index.php?p=casestatus/index",
            "https://services.ecourts.gov.in/ecourtindia_v6/index.php",
            "https://services.ecourts.gov.in/ecourtindia_v6/casestatus",
            "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus",
            "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/state_list",
        ]

        for url in urls_to_test:
            print(f"\nTesting URL: {url}")
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(2)
                status = resp.status if resp else "N/A"
                final_url = page.url
                title = page.title()
                body = page.inner_text("body")[:200].replace("\n", " ")
                has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
                print(f"  Status Code: {status}")
                print(f"  Final URL  : {final_url}")
                print(f"  Title      : '{title}'")
                print(f"  Body       : '{body}'")
                print(f"  #sess_state_code visible: {has_state}")
            except Exception as e:
                print(f"  Error: {e}")

        context.close()
        browser.close()
    print("\n=== URL Test Complete ===")

if __name__ == "__main__":
    main()
