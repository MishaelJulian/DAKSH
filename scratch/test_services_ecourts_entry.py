"""Diagnostic script inspecting entry points on https://services.ecourts.gov.in/."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing https://services.ecourts.gov.in/ Entry ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Loading https://services.ecourts.gov.in/...")
        resp = page.goto("https://services.ecourts.gov.in/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        print(f"Status Code: {resp.status if resp else 'N/A'}")
        print(f"Final URL  : {page.url}")
        print(f"Page Title : '{page.title()}'")
        body_text = page.inner_text("body")[:300].replace("\n", " ")
        print(f"Body Text  : '{body_text}'")

        # Inspect select dropdowns
        selects = page.locator("select").all()
        print(f"\nSelect dropdowns found: {len(selects)}")
        for idx, s in enumerate(selects):
            s_id = s.get_attribute("id") or ""
            s_name = s.get_attribute("name") or ""
            s_vis = s.is_visible()
            print(f"  [{idx}] id='{s_id}' | name='{s_name}' | visible={s_vis}")

        # Check forms
        forms = page.locator("form").all()
        print(f"\nForms found: {len(forms)}")
        for idx, f in enumerate(forms):
            f_id = f.get_attribute("id") or ""
            f_action = f.get_attribute("action") or ""
            f_method = f.get_attribute("method") or ""
            print(f"  [{idx}] id='{f_id}' | action='{f_action}' | method='{f_method}'")

        context.close()
        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
