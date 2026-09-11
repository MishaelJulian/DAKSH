"""Diagnostic script testing session bootstrap by opening https://services.ecourts.gov.in/ecourtindia_v6/ then clicking Case Status."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing eCourts v6 Entry via https://services.ecourts.gov.in/ecourtindia_v6/ ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Open landing URL
        print("\nStep 1: Navigating to https://services.ecourts.gov.in/ecourtindia_v6/...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"  URL  : {page.url}")
        print(f"  Title: '{page.title()}'")

        # Step 2: Click 'Case Status' link
        print("\nStep 2: Clicking 'Case Status' link...")
        cs_link = page.locator("a:has-text('Case Status')").first
        if cs_link.count() > 0:
            cs_link.click()
            time.sleep(3)
        else:
            page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded")
            time.sleep(3)

        print(f"  Post-click URL  : {page.url}")
        print(f"  Post-click Title: '{page.title()}'")
        body_text = page.inner_text("body")[:300].replace("\n", " ")
        print(f"  Post-click Body : '{body_text}'")

        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"  #sess_state_code visible: {has_state}")

        if has_state:
            print("\nStep 3: Testing dropdown selections on verified eCourts v6 page...")
            # State
            page.select_option("#sess_state_code", value="3")  # Karnataka = 3
            time.sleep(1)
            print("  Selected State: Karnataka (val=3)")

            # District
            page.wait_for_selector("#sess_dist_code option", timeout=5000)
            page.select_option("#sess_dist_code", value="20")  # BENGALURU = 20
            time.sleep(1)
            print("  Selected District: BENGALURU (val=20)")

            # Court Complex
            page.wait_for_selector("#court_complex_code option", timeout=5000)
            opts = page.eval_on_selector_all("#court_complex_code option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
            target = next((o for o in opts if "city civil" in o["text"].lower()), None)
            if target:
                page.select_option("#court_complex_code", value=target["value"])
                print(f"  Selected Court Complex: '{target['text']}' (val={target['value']})")
                time.sleep(1)

            # Establishment
            opts_est = page.eval_on_selector_all("#court_est_code option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
            target_est = next((o for o in opts_est if "prl" in o["text"].lower() or "city civil" in o["text"].lower()), None)
            if target_est:
                page.select_option("#court_est_code", value=target_est["value"])
                print(f"  Selected Establishment: '{target_est['text']}' (val={target_est['value']})")
                time.sleep(1)

            # Case Type Tab
            page.locator("#casetype-tabMenu").click()
            time.sleep(2)
            print("  Clicked Case Type tab (#casetype-tabMenu)")

            # Case Type dropdown
            opts_ct = page.eval_on_selector_all("#case_type option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
            ex_ct = next((o for o in opts_ct if "ex - execution petition u" in o["text"].lower()), None)
            if ex_ct:
                page.select_option("#case_type", value=ex_ct["value"])
                print(f"  Selected Case Type: '{ex_ct['text']}' (val={ex_ct['value']})")
            else:
                print(f"  Available Case Types sample: {[o['text'] for o in opts_ct[:10]]}")

            # Year
            page.locator("#search_year").fill("2023")
            print("  Entered Year: 2023 in #search_year")

            # Status Disposed
            page.locator("#radDCT").click()
            print("  Selected Status: Disposed (#radDCT)")

            # Check CAPTCHA
            has_captcha = page.locator("#captcha_image").count() > 0 and page.locator("#captcha_image").is_visible()
            print(f"  CAPTCHA image visible (#captcha_image): {has_captcha}")

        context.close()
        browser.close()
    print("\n=== Navigation Test Complete ===")

if __name__ == "__main__":
    main()
