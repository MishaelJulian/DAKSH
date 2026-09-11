"""Diagnostic script inspecting menu links and JS click handlers on https://services.ecourts.gov.in/ecourtindia_v6/."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Inspecting Menu Links on https://services.ecourts.gov.in/ecourtindia_v6/ ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/", wait_until="domcontentloaded")
        time.sleep(3)

        links = page.eval_on_selector_all(
            "a",
            "els => els.map(e => ({ text: e.innerText.trim(), href: e.href, onclick: e.getAttribute('onclick') || '', id: e.id, class: e.className }))"
        )
        print(f"Total links found: {len(links)}")
        for idx, l in enumerate(links):
            if any(w in (l["text"] + l["href"] + l["onclick"] + l["id"]).lower() for w in ["case", "status", "search", "court", "state", "district"]):
                print(f"  [{idx}] text='{l['text']}' | href='{l['href']}' | onclick='{l['onclick']}' | id='{l['id']}' | class='{l['class']}'")

        context.close()
        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
