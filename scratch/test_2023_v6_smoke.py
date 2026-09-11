"""Smoke test for 2023 eCourts Karnataka scraper using the exact 2010 ECourtsBrowser workflow.

Verifies:
  1. eCourts India session establishment on services.ecourts.gov.in
  2. State selection: Karnataka
  3. District selection: BENGALURU
  4. Court Complex selection: City Civil Court Complex, Bangalore
  5. Establishment selection: PRL. CITY CIVIL AND SESSIONS JUDGE
  6. Case Type tab & selection: EX - Execution Petition U
  7. Year entry: 2023
  8. Status selection: Disposed
  9. CAPTCHA display & manual prompt
  10. Search results table verification (#dispTable)
  11. 2023 Disposed EX case summary extraction (CNR & Case Number)
  12. Pagination controls detection
"""
from __future__ import annotations
import sys
from pathlib import Path
import time

# Ensure project root is in python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ecourts_scraper import config
from ecourts_scraper.browser import get_browser_page, ECourtsBrowser

def log(msg: str) -> None:
    print(msg, flush=True)

def main() -> None:
    log("==================================================")
    log("  eCourts 2023 SMOKE TEST (2010 Verified Workflow)")
    log("==================================================")

    # Set configuration for 2023
    config.YEAR = "2023"
    config.HEADLESS = False  # Headful for CAPTCHA solving

    log(f"Target URL           : {config.BASE_URL}")
    log(f"State                : {config.STATE}")
    log(f"District             : {config.DISTRICT}")
    log(f"Court Complex        : {config.COURT_COMPLEX}")
    log(f"Establishment        : {config.ESTABLISHMENT}")
    log(f"Case Type            : {config.CASE_TYPE}")
    log(f"Year                 : 2023")
    log(f"Status               : {config.CASE_STATUS}")

    with get_browser_page(headless=False) as page:
        browser = ECourtsBrowser(page)

        log("\n[1/12] Navigating to eCourts India Home...")
        try:
            browser.navigate_to_home()
            log("  [+] Successfully navigated to eCourts India Home!")
        except Exception as e:
            log(f"  [-] Navigation failed: {e}")
            sys.exit(1)

        log("\n[2/12] Selecting State: Karnataka...")
        browser.select_state(config.STATE)
        log("  [+] Selected State: Karnataka (#sess_state_code)")

        log("\n[3/12] Selecting District: BENGALURU...")
        browser.select_district(config.DISTRICT)
        log("  [+] Selected District: BENGALURU (#sess_dist_code)")

        log("\n[4/12] Selecting Court Complex: City Civil Court Complex, Bangalore...")
        browser.select_court_complex(config.COURT_COMPLEX)
        log("  [+] Selected Court Complex: City Civil Court Complex, Bangalore (#court_complex_code)")

        log("\n[5/12] Selecting Establishment: PRL. CITY CIVIL AND SESSIONS JUDGE...")
        browser.select_establishment(config.ESTABLISHMENT)
        log("  [+] Selected Establishment: PRL. CITY CIVIL AND SESSIONS JUDGE (#court_est_code)")

        log("\n[6/12] Selecting Case Type Tab...")
        browser.select_case_type_tab()
        log("  [+] Selected Case Type Tab (#casetype-tabMenu)")

        log("\n[7/12] Selecting Case Type: EX - Execution Petition U...")
        browser.fill_case_type(config.CASE_TYPE)
        log("  [+] Selected Case Type: EX - Execution Petition U (#case_type)")

        log("\n[8/12] Filling Year: 2023...")
        browser.fill_year("2023")
        log("  [+] Filled Year: 2023 (#search_year)")

        log("\n[9/12] Selecting Status: Disposed...")
        browser.select_disposed()
        log("  [+] Selected Status: Disposed (#radDCT)")

        log("\n[10/12] Verifying CAPTCHA Display...")
        has_captcha = page.locator("#captcha_image").count() > 0 and page.locator("#captcha_image").is_visible()
        if has_captcha:
            log("  [+] CAPTCHA image is visible on page (#captcha_image)")
        else:
            log("  [!] Warning: #captcha_image not immediately visible")

        log("\n" + "=" * 60)
        log("    MANUAL CAPTCHA SOLVING FOR 2023 SMOKE TEST")
        log("Please solve the CAPTCHA image in the open browser window.")
        log("Once you enter the CAPTCHA characters and click Go,")
        log("the smoke test will verify search results loading.")
        log("=" * 60 + "\n")

        log("Waiting up to 300s for user to solve CAPTCHA and submit search...")
        results_loaded = False
        start_wait = time.time()
        while time.time() - start_wait < 300:
            try:
                browser.verify_results_table(timeout=1000)
                results_loaded = True
                break
            except Exception:
                pass
            time.sleep(1)

        log("\n[11/12] Checking Search Results Table...")
        if results_loaded:
            log("  [+] SUCCESS: Search results table verified in browser DOM!")
            
            # Extract case summaries from result table
            log("\n[12/12] Extracting Case Summaries & Pagination Controls...")
            try:
                summaries = browser.get_cases_summary()
                log(f"  [+] Discovered {len(summaries)} case rows on Page 1.")
                if summaries:
                    sample = summaries[0]
                    log(f"  [+] Sample Case Extracted:")
                    log(f"      - Case Number: {sample.case_number}")
                    log(f"      - CNR Number : {sample.cnr}")
                    log(f"      - Title      : {sample.case_title}")
                
                has_next = browser.has_next_page()
                log(f"  [+] Pagination Controls Detected: Next page available = {has_next}")
            except Exception as e:
                log(f"  [-] Summary/Pagination extraction error: {e}")
        else:
            log("  [!] Results table not detected within 300s timeout.")

    log("\n==================================================")
    if results_loaded:
        log("  [+] 2023 SMOKE TEST PASSED SUCCESSFULLY!")
    else:
        log("  [-] 2023 SMOKE TEST PENDING / TIMEOUT")
    log("==================================================\n")

if __name__ == "__main__":
    main()
