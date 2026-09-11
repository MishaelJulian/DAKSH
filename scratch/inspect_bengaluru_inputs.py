"""Diagnostic script inspecting all input elements on https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Inspecting Inputs on https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/ ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/", wait_until="domcontentloaded")
        time.sleep(3)

        inputs = page.eval_on_selector_all(
            "input",
            "els => els.map(e => ({ id: e.id, name: e.name, type: e.type, placeholder: e.placeholder, class: e.className, value: e.value }))"
        )
        print(f"Total <input> elements found: {len(inputs)}")
        for idx, inp in enumerate(inputs):
            print(f"  [{idx}] id='{inp['id']}' | name='{inp['name']}' | type='{inp['type']}' | placeholder='{inp['placeholder']}' | class='{inp['class']}'")

        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
