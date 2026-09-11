"""Diagnostic script testing session redirection from ecourts.gov.in to services.ecourts.gov.in."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing Portal Redirection Flow (ecourts.gov.in -> services.ecourts.gov.in) ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Opening https://ecourts.gov.in/...")
        page.goto("https://ecourts.gov.in/", wait_until="domcontentloaded")
        time.sleep(2)
        print(f"   URL: {page.url}")

        print("2. Clicking 'District Courts' menu item...")
        dist_menu = page.locator("a:has-text('District Courts')").first
        if dist_menu.count() > 0:
            dist_menu.click()
            time.sleep(2)
            print(f"   URL: {page.url}")

        print("3. Clicking 'Karnataka' state link...")
        kn_link = page.locator("a:has-text('Karnataka')").first
        if kn_link.count() > 0:
            kn_href = kn_link.get_attribute("href") or ""
            print(f"   Karnataka href: {kn_href}")
            kn_link.click()
            time.sleep(3)
            print(f"   URL post-Karnataka click: {page.url}")
            print(f"   Title                   : '{page.title()}'")
            body_kn = page.inner_text("body")[:300].replace("\n", " ")
            print(f"   Body                    : '{body_kn}'")

        context.close()
        browser.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
