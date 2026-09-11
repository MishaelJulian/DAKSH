"""Diagnostic script to test initial eCourts session bootstrap navigation."""
from __future__ import annotations
import time
from playwright.sync_api import sync_playwright

LANDING_URL = "https://services.ecourts.gov.in/ecourtindia_v6/"
DIRECT_URL = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index"

def main() -> None:
    print("=== eCourts Session Bootstrap Investigation ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Test 1: Direct URL
        print(f"\n1. Navigating to DIRECT URL: {DIRECT_URL}")
        page.goto(DIRECT_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"   Final URL  : {page.url}")
        print(f"   Page Title : {page.title()}")
        body_text_1 = page.inner_text("body")[:300].replace("\n", " ")
        print(f"   Body Text  : {body_text_1}")
        has_state_1 = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"   #sess_state_code visible: {has_state_1}")

        # Test 2: Landing URL then navigate to Case Status
        print(f"\n2. Navigating to LANDING URL: {LANDING_URL}")
        page.goto(LANDING_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"   Landing URL: {page.url}")
        print(f"   Landing Title: {page.title()}")
        landing_body = page.inner_text("body")[:300].replace("\n", " ")
        print(f"   Landing Body: {landing_body}")

        # Search for Case Status link/button on landing page
        case_status_links = page.locator("a:has-text('Case Status'), button:has-text('Case Status'), [onclick*='casestatus'], a[href*='casestatus']").all()
        print(f"   Found {len(case_status_links)} 'Case Status' elements on landing page.")
        for idx, link in enumerate(case_status_links):
            text = link.inner_text().strip()
            href = link.get_attribute("href") or ""
            onclick = link.get_attribute("onclick") or ""
            print(f"     [{idx}] Text: '{text}' | href: '{href}' | onclick: '{onclick}'")

        # Try clicking Case Status link
        if case_status_links:
            print("   Clicking first 'Case Status' link...")
            case_status_links[0].click()
            time.sleep(3)
            print(f"   Post-click URL  : {page.url}")
            print(f"   Post-click Title: {page.title()}")
            post_body = page.inner_text("body")[:300].replace("\n", " ")
            print(f"   Post-click Body : {post_body}")
            has_state_2 = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
            print(f"   #sess_state_code visible: {has_state_2}")
        else:
            print("   No Case Status links found on landing page!")

        context.close()
        browser.close()
    print("\n=== Investigation Complete ===")

if __name__ == "__main__":
    main()
