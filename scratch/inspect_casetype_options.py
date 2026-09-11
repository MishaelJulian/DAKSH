"""Diagnostic script listing all Case Type options for City Civil Court Complex, Bangalore."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Listing Case Types for City Civil Court Complex, Bangalore ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/", wait_until="domcontentloaded")
        time.sleep(2)

        # Select KABC01
        page.select_option("#est_code", value="KABC01")
        time.sleep(2)

        opts = page.eval_on_selector_all("#case_type option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
        print(f"Total Case Types: {len(opts)}")
        for idx, o in enumerate(opts):
            if any(w in o["text"].lower() for w in ["ex", "exec", "petition", "civil"]):
                print(f"  [{idx}] value='{o['value']}' | text='{o['text']}'")

        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
