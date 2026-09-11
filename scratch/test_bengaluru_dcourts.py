"""Diagnostic script inspecting Case Status links and iframe targets on bengaluru.dcourts.gov.in."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Inspecting https://bengaluru.dcourts.gov.in/ for Case Status ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        print("1. Loading https://bengaluru.dcourts.gov.in/...")
        page.goto("https://bengaluru.dcourts.gov.in/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        
        # Dump all links with 'case' or 'status' or 'services'
        links = page.eval_on_selector_all(
            "a",
            "els => els.map(e => ({ text: e.innerText.trim(), href: e.href, onclick: e.getAttribute('onclick') || '' }))"
        )
        
        case_links = [l for l in links if any(w in (l["text"] + l["href"] + l["onclick"]).lower() for w in ["case", "status", "services", "search", "ecourt"])]
        print(f"\nFound {len(case_links)} case/status related links:")
        for idx, l in enumerate(case_links):
            print(f"  [{idx}] Text: '{l['text']}' | href: '{l['href']}' | onclick: '{l['onclick']}'")

        # Also search for iframes or embedded objects/forms
        iframes = page.eval_on_selector_all("iframe", "els => els.map(e => ({ src: e.src, id: e.id, name: e.name }))")
        print(f"\nFound {len(iframes)} iframes on page:")
        for idx, f in enumerate(iframes):
            print(f"  Frame [{idx}]: src='{f['src']}' | id='{f['id']}' | name='{f['name']}'")

        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
