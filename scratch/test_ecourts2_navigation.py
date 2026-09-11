"""Diagnostic script to inspect links on https://ecourts.gov.in/ecourts2.0/ and test navigation to Case Status."""
from __future__ import annotations
import time
from playwright.sync_api import sync_playwright

def main() -> None:
    print("=== Inspecting https://ecourts.gov.in/ecourts2.0/ Links ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Navigating to https://ecourts.gov.in/...")
        page.goto("https://ecourts.gov.in/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        print(f"Current URL: {page.url}")
        print(f"Title      : {page.title()}")

        # List all anchors and buttons with text
        items = page.locator("a, button, input[type='button'], input[type='submit']").all()
        print(f"Found {len(items)} interactive elements on page.")

        relevant_items = []
        for item in items:
            try:
                text = item.inner_text().strip()
                href = item.get_attribute("href") or ""
                onclick = item.get_attribute("onclick") or ""
                if any(w in (text + href + onclick).lower() for w in ["case", "status", "district", "services", "karnataka", "bengaluru", "search", "v6"]):
                    relevant_items.append((text, href, onclick))
            except Exception:
                pass

        print(f"\n--- Relevant Links ({len(relevant_items)}) ---")
        for txt, href, onclick in relevant_items[:25]:
            print(f"Text: '{txt}' | href: '{href}' | onclick: '{onclick}'")

        context.close()
        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
