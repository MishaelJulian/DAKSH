"""Diagnostic script inspecting https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/ ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = "https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/"
        print(f"Navigating to {url}...")
        resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        print(f"Status Code: {resp.status if resp else 'N/A'}")
        print(f"Final URL  : {page.url}")
        print(f"Page Title : '{page.title()}'")
        
        # Check text snippet
        body_text = page.inner_text("body")[:400].replace("\n", " ")
        print(f"Body Text  : '{body_text}'")

        # Check iframes
        frames = page.frames
        print(f"\nTotal frames on page: {len(frames)}")
        for idx, frame in enumerate(frames):
            print(f"  Frame [{idx}]: name='{frame.name}' | url='{frame.url}'")
            has_state = frame.locator("#sess_state_code").count() > 0 and frame.locator("#sess_state_code").is_visible()
            print(f"    #sess_state_code visible in frame: {has_state}")

        # Check main page selectors
        has_state_main = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"Main page #sess_state_code visible: {has_state_main}")

        # Print all select elements across main page and frames
        for f_idx, frame in enumerate(frames):
            selects = frame.locator("select").all()
            if selects:
                print(f"\nSelect dropdowns in Frame [{f_idx}]: {len(selects)}")
                for s_idx, s in enumerate(selects):
                    s_id = s.get_attribute("id") or ""
                    s_name = s.get_attribute("name") or ""
                    s_vis = s.is_visible()
                    print(f"  [{s_idx}] id='{s_id}' | name='{s_name}' | visible={s_vis}")

        context.close()
        browser.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
