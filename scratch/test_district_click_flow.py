"""Diagnostic script testing selection of Bengaluru from Karnataka state page on eCourts SSO."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing eCourts SSO State -> District Flow ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Open eCourts portal
        page.goto("https://ecourts.gov.in/", wait_until="domcontentloaded")
        time.sleep(2)

        # Step 2: District Courts -> Karnataka
        page.locator("a:has-text('District Courts')").first.click()
        time.sleep(2)
        page.locator("a:has-text('Karnataka')").first.click()
        time.sleep(3)

        print(f"State Page URL: {page.url}")

        # Check options in #sateist dropdown or district links
        if page.locator("#sateist").count() > 0:
            print("Found #sateist dropdown on state page!")
            opts = page.eval_on_selector_all("#sateist option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
            print(f"Dropdown options ({len(opts)}): {[o['text'] for o in opts[:10]]}")

            # Select Bengaluru
            b_opt = next((o for o in opts if "bengaluru" in o["text"].lower() or "bangalore" in o["text"].lower()), None)
            if b_opt:
                page.select_option("#sateist", value=b_opt["value"])
                time.sleep(3)
                print(f"Post-District Select URL  : {page.url}")
                print(f"Post-District Select Title: '{page.title()}'")
                body = page.inner_text("body")[:300].replace("\n", " ")
                print(f"Post-District Select Body : '{body}'")

                # Check if #sess_state_code or #casetype-tabMenu or Case Status tab is on page
                has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
                print(f"#sess_state_code visible: {has_state}")

        context.close()
        browser.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
