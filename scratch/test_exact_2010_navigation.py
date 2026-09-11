"""Diagnostic script to test exact 2010 eCourts navigation flow."""
from __future__ import annotations
import sys
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Testing Exact 2010 Navigation Flow on services.ecourts.gov.in ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Open base v6 URL
        print("1. Opening https://services.ecourts.gov.in/ecourtindia_v6/...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Step 2: Open ?p=casestatus/index
        print("2. Opening https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index...")
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        print(f"URL: {page.url}")
        print(f"Title: '{page.title()}'")
        body_text = page.inner_text("body")[:300].replace("\n", " ")
        print(f"Body: '{body_text}'")

        has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
        print(f"#sess_state_code visible: {has_state}")

        if has_state:
            print("\n3. Testing dropdown selections...")
            # State: Karnataka (val=3)
            print("   Selecting State: Karnataka...")
            page.select_option("#sess_state_code", value="3")
            time.sleep(2)

            # District: BENGALURU (val=20)
            print("   Selecting District: BENGALURU...")
            page.wait_for_selector("#sess_dist_code option", timeout=5000)
            page.select_option("#sess_dist_code", value="20")
            time.sleep(2)

            # Court Complex: City Civil Court Complex, Bangalore
            print("   Selecting Court Complex...")
            page.wait_for_selector("#court_complex_code option", timeout=5000)
            opts_cc = page.eval_on_selector_all("#court_complex_code option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
            target_cc = next((o for o in opts_cc if "city civil" in o["text"].lower()), None)
            if target_cc:
                page.select_option("#court_complex_code", value=target_cc["value"])
                print(f"   [+] Selected Court Complex: '{target_cc['text']}' (val={target_cc['value']})")
                time.sleep(2)

            # Establishment: PRL. CITY CIVIL AND SESSIONS JUDGE
            print("   Selecting Establishment...")
            opts_est = page.eval_on_selector_all("#court_est_code option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
            target_est = next((o for o in opts_est if "prl" in o["text"].lower() or "city civil" in o["text"].lower()), None)
            if target_est:
                page.select_option("#court_est_code", value=target_est["value"])
                print(f"   [+] Selected Establishment: '{target_est['text']}' (val={target_est['value']})")
                time.sleep(2)

            # Click Case Type Tab
            print("   Clicking Case Type tab (#casetype-tabMenu)...")
            page.locator("#casetype-tabMenu").click()
            time.sleep(2)

            # Select Case Type: EX - Execution Petition Under Order...
            print("   Selecting Case Type...")
            opts_ct = page.eval_on_selector_all("#case_type option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
            ex_ct = next((o for o in opts_ct if "ex - execution petition u" in o["text"].lower()), None)
            if ex_ct:
                page.select_option("#case_type", value=ex_ct["value"])
                print(f"   [+] Selected Case Type: '{ex_ct['text']}' (val={ex_ct['value']})")
                time.sleep(1)

            # Fill Year: 2023
            print("   Filling Year: 2023...")
            page.locator("#search_year").fill("2023")
            print("   [+] Filled Year: 2023 in #search_year")

            # Status: Disposed (#radDCT)
            print("   Selecting Status: Disposed...")
            page.locator("#radDCT").click()
            print("   [+] Clicked #radDCT (Disposed)")

            # Check CAPTCHA
            has_captcha = page.locator("#captcha_image").count() > 0 and page.locator("#captcha_image").is_visible()
            print(f"   [+] CAPTCHA image visible (#captcha_image): {has_captcha}")

        context.close()
        browser.close()
    print("\n=== Navigation Test Complete ===")

if __name__ == "__main__":
    main()
