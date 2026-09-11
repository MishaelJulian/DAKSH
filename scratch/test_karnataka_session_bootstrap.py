"""Diagnostic script testing the full eCourts session bootstrap flow to Karnataka Case Status form."""
from __future__ import annotations
import time
from playwright.sync_api import sync_playwright

def main() -> None:
    print("=== Testing eCourts Full Session Bootstrap (eCourts 2.0 -> Karnataka) ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Open eCourts portal
        print("\nStep 1: Navigating to https://ecourts.gov.in/...")
        page.goto("https://ecourts.gov.in/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"  URL: {page.url}")

        # Step 2: Navigate to District Courts menu page
        print("\nStep 2: Clicking 'District Courts'...")
        dist_btn = page.locator("a:has-text('District Courts')").first
        if dist_btn.count() > 0:
            dist_btn.click()
            time.sleep(2)
        else:
            page.goto("https://ecourts.gov.in/ecourts2.0//?p=dist_court", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
        print(f"  URL: {page.url}")

        # Step 3: Click 'Karnataka' state link
        print("\nStep 3: Clicking 'Karnataka' state link...")
        kn_link = page.locator("a:has-text('Karnataka')").first
        if kn_link.count() > 0:
            kn_href = kn_link.get_attribute("href")
            print(f"  Karnataka link href: {kn_href}")
            kn_link.click()
            time.sleep(3)
        else:
            print("  Karnataka link NOT found!")

        print(f"  Post-Karnataka URL  : {page.url}")
        print(f"  Post-Karnataka Title: {page.title()}")

        # Inspect page elements post-Karnataka click
        print("\nStep 4: Checking Case Status dropdowns and selectors...")
        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        has_dist = page.locator("#sess_dist_code").count() > 0 and page.locator("#sess_dist_code").is_visible()
        has_case_type_tab = page.locator("#casetype-tabMenu").count() > 0 and page.locator("#casetype-tabMenu").is_visible()

        print(f"  #sess_state_code visible: {has_state}")
        print(f"  #sess_dist_code visible : {has_dist}")
        print(f"  #casetype-tabMenu visible: {has_case_type_tab}")

        # Print all visible select dropdowns or tabs
        selects = page.locator("select").all()
        print(f"  Total select dropdowns: {len(selects)}")
        for idx, sel in enumerate(selects):
            sel_id = sel.get_attribute("id") or ""
            sel_name = sel.get_attribute("name") or ""
            is_vis = sel.is_visible()
            print(f"    [{idx}] id='{sel_id}' | name='{sel_name}' | visible={is_vis}")

        tabs = page.locator("a[data-bs-toggle='tab'], button[data-bs-toggle='tab'], .tabs, #casetype-tabMenu").all()
        print(f"  Total tabs: {len(tabs)}")
        for idx, tab in enumerate(tabs):
            tab_id = tab.get_attribute("id") or ""
            txt = tab.inner_text().strip()
            print(f"    [{idx}] id='{tab_id}' | text='{txt}'")

        context.close()
        browser.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
