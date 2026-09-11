"""Diagnostic script inspecting https://bengaluru.dcourts.gov.in/ for Case Status search integration."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Inspecting https://bengaluru.dcourts.gov.in/ ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Navigating to https://bengaluru.dcourts.gov.in/...")
        page.goto("https://bengaluru.dcourts.gov.in/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        print(f"Current URL: {page.url}")
        print(f"Title      : {page.title()}")

        # List relevant links
        links = page.locator("a, button, [onclick]").all()
        print(f"Found {len(links)} interactive elements.")

        case_status_targets = []
        for a in links:
            try:
                txt = a.inner_text().strip()
                href = a.get_attribute("href") or ""
                onclick = a.get_attribute("onclick") or ""
                combined = (txt + " " + href + " " + onclick).lower()
                if "case status" in combined or "casestatus" in combined or "case-status" in combined:
                    case_status_targets.append((txt, href, onclick, a))
            except Exception:
                pass

        print(f"\nFound {len(case_status_targets)} 'Case Status' target elements:")
        for idx, (txt, href, onclick, el) in enumerate(case_status_targets):
            print(f"  [{idx}] Text: '{txt}' | href: '{href}' | onclick: '{onclick}'")

        if case_status_targets:
            print("\nClicking first Case Status target...")
            target_el = case_status_targets[0][3]
            target_el.click()
            time.sleep(5)

            print(f"Post-click URL  : {page.url}")
            print(f"Post-click Title: {page.title()}")

            # Check frames
            frames = page.frames
            print(f"Total frames: {len(frames)}")
            for idx, frame in enumerate(frames):
                print(f"  Frame [{idx}]: name='{frame.name}' | url='{frame.url}'")
                has_state = frame.locator("#sess_state_code").count() > 0 and frame.locator("#sess_state_code").is_visible()
                print(f"    #sess_state_code visible: {has_state}")

            has_state_main = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
            print(f"Main page #sess_state_code visible: {has_state_main}")

        context.close()
        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
