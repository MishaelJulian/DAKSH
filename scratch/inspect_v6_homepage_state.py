"""Diagnostic script inspecting state selection on https://services.ecourts.gov.in/ecourtindia_v6/."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Inspecting State Selection on eCourts v6 ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Opening https://services.ecourts.gov.in/ecourtindia_v6/...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/", wait_until="domcontentloaded")
        time.sleep(2)

        # Inspect all selects on homepage
        selects = page.locator("select").all()
        print(f"\nSelect dropdowns on homepage: {len(selects)}")
        for idx, s in enumerate(selects):
            s_id = s.get_attribute("id") or ""
            s_name = s.get_attribute("name") or ""
            s_vis = s.is_visible()
            print(f"  [{idx}] id='{s_id}' | name='{s_name}' | visible={s_vis}")
            if s_vis:
                opts = page.eval_on_selector_all(f"select#{s_id}" if s_id else "select", "els => els[0] ? Array.from(els[0].options).map(o => ({ text: o.text.trim(), value: o.value })) : []")
                print(f"       Sample options ({len(opts)}): {[o['text'] for o in opts[:5]]}")

        # Check links for State or District Courts
        dist_courts_link = page.locator("a:has-text('District Courts')").all()
        print(f"\nFound {len(dist_courts_link)} 'District Courts' links on homepage:")
        for idx, d in enumerate(dist_courts_link):
            txt = d.inner_text().strip()
            href = d.get_attribute("href") or ""
            onclick = d.get_attribute("onclick") or ""
            print(f"  [{idx}] Text: '{txt}' | href: '{href}' | onclick: '{onclick}'")

        context.close()
        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
