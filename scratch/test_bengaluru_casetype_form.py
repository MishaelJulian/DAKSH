"""Diagnostic script inspecting the form elements on https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/."""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Inspecting Form on https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/ ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page.goto("https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # 1. Establishment Options (#est_code)
        est_opts = []
        if page.locator("#est_code").count() > 0:
            est_opts = page.eval_on_selector(
                "#est_code",
                "el => Array.from(el.options).map(o => ({ text: o.text.trim(), value: o.value }))"
            )
            print(f"\nEstablishment Dropdown (#est_code) — {len(est_opts)} options:")
            for opt in est_opts[:10]:
                print(f"  value: '{opt['value']}' | text: '{opt['text']}'")

        # 2. Select Establishment (PRL. CITY CIVIL AND SESSIONS JUDGE) if available
        est_target = next((o for o in est_opts if "prl" in o["text"].lower() or "city civil" in o["text"].lower()), None)
        if est_target:
            print(f"\nSelecting Establishment: '{est_target['text']}' (val={est_target['value']})...")
            page.select_option("#est_code", value=est_target["value"])
            time.sleep(2)

        # 3. Case Type Options (#case_type)
        if page.locator("#case_type").count() > 0:
            case_type_opts = page.eval_on_selector(
                "#case_type",
                "el => Array.from(el.options).map(o => ({ text: o.text.trim(), value: o.value }))"
            )
            print(f"\nCase Type Dropdown (#case_type) — {len(case_type_opts)} options:")
            ex_opts = [o for o in case_type_opts if "ex" in o["text"].lower() or "execution" in o["text"].lower()]
            for opt in ex_opts:
                print(f"  value: '{opt['value']}' | text: '{opt['text']}'")

        # 4. Inputs (Year, Status Radios, CAPTCHA image)
        print("\nForm Input Elements:")
        year_input = page.locator("#search_year, input[name='search_year'], input[placeholder*='Year']").all()
        print(f"  Year inputs found: {len(year_input)}")
        for y in year_input:
            print(f"    id='{y.get_attribute('id')}' | name='{y.get_attribute('name')}'")

        radios = page.locator("input[type='radio']").all()
        print(f"  Radio buttons found: {len(radios)}")
        for r in radios:
            print(f"    id='{r.get_attribute('id')}' | value='{r.get_attribute('value')}'")

        captcha_img = page.locator("#captcha_image, img[src*='captcha'], img[alt*='captcha']").all()
        print(f"  CAPTCHA images found: {len(captcha_img)}")
        for c in captcha_img:
            print(f"    id='{c.get_attribute('id')}' | src='{c.get_attribute('src')}'")

        go_btn = page.locator("input[type='submit'], button[type='submit'], input[type='button'][value*='Go'], button:has-text('Go')").all()
        print(f"  Go/Submit buttons found: {len(go_btn)}")
        for g in go_btn:
            print(f"    id='{g.get_attribute('id')}' | value='{g.get_attribute('value')}' | text='{g.inner_text()}'")

        context.close()
        browser.close()
    print("\n=== Form Inspection Complete ===")

if __name__ == "__main__":
    main()
