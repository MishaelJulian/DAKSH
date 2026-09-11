"""Controlled test script for testing specific cases:
- EX/81/2023 (known successful case)
- EX/104/2023
- EX/105/2023
- EX/106/2023
"""
import sys
import logging
from ecourts_scraper import config
from ecourts_scraper.browser import get_browser_page, ECourtsBrowser, CaptchaError, ECourtsPortalError
from ecourts_scraper.scraper import extract_search_results

def test_controlled_cases():
    print("==================================================")
    print("CONTROLLED TEST: EX/81/2023, EX/104/2023, EX/105/2023, EX/106/2023")
    print("==================================================")
    
    with get_browser_page(headless=False) as page:
        browser = ECourtsBrowser(page)
        browser.navigate_to_home()
        browser.select_state("Karnataka")
        browser.select_district("BENGALURU")
        browser.select_court_complex("City Civil Court Complex, Bangalore")
        browser.select_establishment("PRL. CITY CIVIL AND SESSIONS JUDGE")
        browser.select_case_type_tab()
        browser.fill_case_type("EX - Execution Petition U")
        browser.fill_year("2023")
        browser.select_disposed()

        print("\n[!] Please solve CAPTCHA in browser and press ENTER...")
        input()

        browser.click_go()
        browser.verify_results_table()
        
        extracted_cases = extract_search_results(page)
        print(f"\nExtracted {len(extracted_cases)} case summaries on page 1.")
        
        target_case_numbers = ["EX/81/2023", "EX/104/2023", "EX/105/2023", "EX/106/2023"]
        cases_to_test = [c for c in extracted_cases if c.case_number in target_case_numbers]
        
        if not cases_to_test:
            print("Target cases not found on Page 1. Found case numbers snippet:", [c.case_number for c in extracted_cases[:10]])
            return

        print(f"Found {len(cases_to_test)} matching cases to test out of {len(target_case_numbers)} requested.")
        
        for case in cases_to_test:
            print("-" * 50)
            print(f"Testing Case: {case.case_number}")
            try:
                browser.click_view(case)
                browser.wait_for_case_detail_page()
                details = browser.get_minimal_case_details()
                print(f"SUCCESS loading details for {case.case_number}:")
                print(f"  CNR: {details.cnr_number}")
                print(f"  Case Number: {details.case_number}")
                print(f"  Status: {details.case_status}")
                browser.return_to_results()
                browser.wait_for_results_table()
            except ECourtsPortalError as e:
                print(f"PORTAL ERROR on {case.case_number}: {e}")
                break
            except Exception as e:
                print(f"ERROR on {case.case_number}: {e}")

if __name__ == "__main__":
    test_controlled_cases()
