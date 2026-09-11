"""Diagnostic script testing session bootstrap by navigating from eCourts SSO / Portal landing page."""
from __future__ import annotations
import time
from playwright.sync_api import sync_playwright

def main() -> None:
    print("=== Testing Navigation from eCourts SSO / Landing Page ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Landing on SSO / Main portal
        print("\nStep 1: Opening https://ecourts.gov.in/...")
        page.goto("https://ecourts.gov.in/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"  URL  : {page.url}")
        print(f"  Title: {page.title()}")

        # Step 2: Click "District Court Services"
        print("\nStep 2: Clicking 'District Court Services'...")
        dist_link = page.locator("a:has-text('District Court Services'), a[href*='services.ecourts.gov.in']")
        if dist_link.count() > 0:
            dist_link.first.click()
            time.sleep(3)
            print(f"  Post-click URL  : {page.url}")
            print(f"  Post-click Title: {page.title()}")
            post_body = page.inner_text("body")[:300].replace("\n", " ")
            print(f"  Post-click Body : '{post_body}'")
            has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
            print(f"  #sess_state_code visible: {has_state}")
        else:
            print("  'District Court Services' link not found!")

        # Step 3: Test clicking "District Courts" if Step 2 didn't load Case Status
        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        if not has_state:
            print("\nStep 3: Trying 'District Courts' link on main page...")
            page.goto("https://ecourts.gov.in/ecourts2.0//?p=dist_court", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            print(f"  URL  : {page.url}")
            print(f"  Title: {page.title()}")
            dist_body = page.inner_text("body")[:300].replace("\n", " ")
            print(f"  Body : '{dist_body}'")

            # Check links on dist_court page
            links = page.locator("a").all()
            link_texts = [(a.inner_text().strip(), a.get_attribute("href") or "") for a in links if a.inner_text().strip()]
            print(f"  Found {len(link_texts)} links on dist_court page. Sample: {link_texts[:10]}")

            # Look for Karnataka / Bengaluru / Case Status links
            kn_links = [l for l in link_texts if any(w in (l[0]+l[1]).lower() for w in ["karnataka", "bengaluru", "bangalore", "case", "status"])]
            print(f"  Matching Karnataka/Status links: {kn_links}")

        context.close()
        browser.close()
    print("\n=== Navigation Test Complete ===")

if __name__ == "__main__":
    main()
