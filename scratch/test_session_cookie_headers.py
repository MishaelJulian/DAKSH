"""Diagnostic script testing session establishment with Referer headers and portal transitions."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing eCourts Session Initialization & Referer Headers ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        # Scenario A: Set Referer header on context
        print("\n--- Scenario A: Extra HTTP Headers (Referer & User-Agent) ---")
        context_a = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                "Referer": "https://services.ecourts.gov.in/ecourtindia_v6/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        page_a = context_a.new_page()
        
        url_a = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index"
        print(f"Navigating to {url_a} with Referer header...")
        resp_a = page_a.goto(url_a, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        print(f"  Status Code: {resp_a.status if resp_a else 'N/A'}")
        print(f"  Final URL  : {page_a.url}")
        print(f"  Title      : '{page_a.title()}'")
        body_a = page_a.inner_text("body")[:250].replace("\n", " ")
        print(f"  Body       : '{body_a}'")
        has_state_a = page_a.locator("#sess_state_code").count() > 0 and page_a.locator("#sess_state_code").is_visible()
        print(f"  #sess_state_code visible: {has_state_a}")
        context_a.close()

        # Scenario B: Multi-step navigation (Home -> Case Status)
        print("\n--- Scenario B: Stepwise Navigation (Home -> Case Status) ---")
        context_b = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page_b = context_b.new_page()

        # 1. Open base site
        print("1. Opening https://services.ecourts.gov.in/...")
        page_b.goto("https://services.ecourts.gov.in/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"   URL: {page_b.url}")

        # 2. Open home page of v6
        print("2. Navigating to https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index...")
        page_b.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"   URL: {page_b.url}")

        # 3. Click Case Status or navigate to casestatus/index
        print("3. Navigating to https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index...")
        resp_b = page_b.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        print(f"   Status Code: {resp_b.status if resp_b else 'N/A'}")
        print(f"   Final URL  : {page_b.url}")
        body_b = page_b.inner_text("body")[:250].replace("\n", " ")
        print(f"   Body       : '{body_b}'")
        has_state_b = page_b.locator("#sess_state_code").count() > 0 and page_b.locator("#sess_state_code").is_visible()
        print(f"   #sess_state_code visible: {has_state_b}")

        context_b.close()

        # Scenario C: Check cookies or tokens set by eCourts
        print("\n--- Scenario C: Check eCourts Cookies ---")
        context_c = browser.new_context()
        page_c = context_c.new_page()
        page_c.goto("https://ecourts.gov.in/", wait_until="domcontentloaded")
        time.sleep(2)
        cookies = context_c.cookies()
        print(f"Cookies from ecourts.gov.in ({len(cookies)}): {[c['name'] for c in cookies]}")
        context_c.close()

        browser.close()
    print("\n=== Scenario Tests Complete ===")

if __name__ == "__main__":
    main()
