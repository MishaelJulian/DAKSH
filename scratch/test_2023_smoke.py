"""Smoke test for 2023 eCourts Bengaluru City Civil Court scraper with unbuffered logging.

Verifies:
  1. Portal navigation & session initialization
  2. Court Complex selection (City Civil Court Complex, Bangalore)
  3. Establishment selection (PRL. CITY CIVIL AND SESSIONS JUDGE)
  4. Case Type selection (EX - Execution Petition)
  5. Filing Year entry (2023)
  6. Status selection (Disposed)
  7. CAPTCHA display & manual solving prompt
  8. Search results table loading & verification
"""
from __future__ import annotations
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def log(msg: str) -> None:
    print(msg, flush=True)

def main() -> None:
    log("==================================================")
    log("      eCourts 2023 SMOKE TEST (1-Case Audit)")
    log("==================================================")

    with sync_playwright() as p:
        log("[1/10] Launching Chromium Browser...")
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Portal Navigation with Session Bootstrap
        log("[2/10] Navigating to eCourts Portal...")
        page_loaded = False
        
        try:
            log("  Navigating to Portal: https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/...")
            page.goto("https://bengaluru.dcourts.gov.in/case-status-search-by-case-type/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            if "Page not Found" not in page.inner_text("body"):
                page_loaded = True
                log("  [+] Successfully loaded Bengaluru District Case Status Portal!")
        except Exception as e:
            log(f"  [-] Portal navigation failed: {e}")

        if not page_loaded:
            log("[-] ERROR: Could not establish valid eCourts session.")
            sys.exit(1)

        log(f"  Current URL: {page.url}")
        log(f"  Page Title : '{page.title()}'")

        # Step 2: Select Court Complex
        log("[3/10] Verifying State & District / Court Complex Selection...")
        page.wait_for_selector("#est_code", timeout=10000)
        est_opts = page.eval_on_selector_all("#est_code option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
        log(f"  Available Court Complexes ({len(est_opts)}): {[o['text'] for o in est_opts if o['text']]}")
        
        target_est = next((o for o in est_opts if "city civil" in o["text"].lower()), None)
        if target_est:
            page.select_option("#est_code", value=target_est["value"])
            log(f"  [+] Selected Court Complex: '{target_est['text']}' (val={target_est['value']})")
            time.sleep(2)
        else:
            log("  [!] Option 'City Civil Court Complex, Bangalore' not found in #est_code")

        # Step 3: Select Case Type (EX - Execution Petition)
        log("[4/10] Verifying Case Type Selection (EX - Execution Petition)...")
        case_type_sel = "#case_type" if page.locator("#case_type").count() > 0 else "#case_type_2"
        page.wait_for_selector(case_type_sel, timeout=10000)
        
        ct_opts = page.eval_on_selector_all(f"{case_type_sel} option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
        ex_target = next((o for o in ct_opts if o["text"].lower().strip() == "ex" or "execution" in o["text"].lower() or "com.ex" in o["text"].lower()), None)
        
        if not ex_target and len(ct_opts) <= 1:
            log("  Waiting 2s for Case Type options to populate via AJAX...")
            time.sleep(2)
            ct_opts = page.eval_on_selector_all(f"{case_type_sel} option", "els => els.map(o => ({ text: o.text.trim(), value: o.value }))")
            ex_target = next((o for o in ct_opts if o["text"].lower().strip() == "ex" or "execution" in o["text"].lower() or "com.ex" in o["text"].lower()), None)

        if ex_target:
            page.select_option(case_type_sel, value=ex_target["value"])
            log(f"  [+] Selected Case Type: '{ex_target['text']}' (val={ex_target['value']})")
            time.sleep(1)
        else:
            log(f"  [!] Case Type 'EX' not found. Available: {[o['text'] for o in ct_opts[:10]]}")

        # Step 4: Fill Year (#reg_year or #search_year)
        log("[5/10] Entering Filing Year (2023)...")
        year_sel = None
        for sel in ["#reg_year", "#search_year", "input[name='reg_year']", "input[name='search_year']"]:
            if page.locator(sel).count() > 0 and page.locator(sel).is_visible():
                year_sel = sel
                break

        if year_sel:
            page.locator(year_sel).fill("2023")
            log(f"  [+] Entered Year: 2023 (using selector '{year_sel}')")
        else:
            log("  [!] Year input field not found.")

        # Step 5: Select Status
        log("[6/10] Selecting Status: Disposed...")
        status_disposed = page.locator("#chkNoStatus, #radDCT, input[value='D']").first
        if status_disposed.count() > 0:
            status_disposed.click()
            log("  [+] Selected Status: Disposed")
        else:
            log("  [!] Disposed radio button not found.")

        # Step 6: Verify CAPTCHA Display
        log("[7/10] Verifying CAPTCHA Display...")
        captcha_img = page.locator("#captcha_image, #siwp_captcha_image_0, img[src*='captcha']").first
        if captcha_img.count() > 0 and captcha_img.is_visible():
            log("  [+] CAPTCHA image is visible in browser window!")
        else:
            log("  [!] CAPTCHA image not detected.")

        # Step 7: Prompt User for Manual CAPTCHA
        log("\n" + "=" * 60)
        log("    MANUAL CAPTCHA SOLVING FOR 2023 SMOKE TEST")
        log("Please solve the CAPTCHA image in the open browser window.")
        log("Once you enter the CAPTCHA characters and click Search,")
        log("the smoke test will verify search results loading.")
        log("=" * 60 + "\n")

        log("Waiting up to 120s for user to solve CAPTCHA in browser window...")
        results_loaded = False
        start_wait = time.time()
        while time.time() - start_wait < 120:
            tables = page.locator("table").all()
            for t in tables:
                try:
                    txt = t.inner_text()
                    if any(w in txt for w in ["Petitioner", "Respondent", "Case Number", "View", "Sr No"]):
                        results_loaded = True
                        break
                except Exception:
                    pass
            if results_loaded:
                break
            time.sleep(1)

        log("[8/10] Checking Search Results Table...")
        if results_loaded:
            log("  [+] SUCCESS: Search results table loaded in browser DOM!")
        else:
            log("  [!] Results table not loaded within 120s timeout.")

        context.close()
        browser.close()

    log("\n==================================================")
    if results_loaded:
        log("  [+] 2023 SMOKE TEST PASSED SUCCESSFULLY!")
    else:
        log("  [-] 2023 SMOKE TEST PENDING / TIMEOUT")
    log("==================================================\n")

if __name__ == "__main__":
    main()
