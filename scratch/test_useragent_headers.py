"""Diagnostic script testing Chrome headers for services.ecourts.gov.in."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing Chrome Headers for services.ecourts.gov.in ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Chromium";v="128", "Not=A?Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1"
            }
        )
        page = context.new_page()

        print("1. Opening https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index...")
        resp = page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        print(f"Status Code: {resp.status if resp else 'N/A'}")
        print(f"Final URL  : {page.url}")
        print(f"Page Title : '{page.title()}'")
        body_text = page.inner_text("body")[:300].replace("\n", " ")
        print(f"Body Text  : '{body_text}'")

        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"#sess_state_code visible: {has_state}")

        context.close()
        browser.close()
    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
