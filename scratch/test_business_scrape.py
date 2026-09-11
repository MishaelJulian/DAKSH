import logging
import sys
from ecourts_scraper import config
from ecourts_scraper.browser import get_browser_page, ECourtsBrowser
from ecourts_scraper.scraper import extract_search_results
from ecourts_scraper.utils import setup_logging

def main():
    logger = setup_logging(config.LOGS_DIR)
    logger.info("Running test_business_scrape script...")

    with get_browser_page(headless=False) as page:
        browser = ECourtsBrowser(page)
        
        # Navigate and fill form
        browser.navigate_to_home()
        browser.select_state(config.STATE)
        browser.select_district(config.DISTRICT)
        browser.select_court_complex(config.COURT_COMPLEX)
        browser.select_establishment(config.ESTABLISHMENT)
        browser.select_case_type_tab()
        browser.fill_case_type(config.CASE_TYPE)
        browser.fill_year(config.YEAR)
        browser.select_disposed()

        print("\n=======================================================")
        print("Please solve CAPTCHA and press [ENTER] in terminal...")
        print("=======================================================\n")
        input()

        browser.click_go()
        browser.verify_results_table()
        
        extracted_cases = extract_search_results(page)
        if not extracted_cases:
            print("No cases found.")
            return

        case1 = extracted_cases[0]
        print(f"Opening case: {case1.case_number}")
        browser.click_view(case1)
        browser.wait_for_case_detail_page()
        
        # Click the first business date link
        business_link = page.locator("a[onclick*='viewBusiness']").first
        if business_link.count() > 0:
            link_text = business_link.inner_text().strip()
            print(f"Found business date link: {link_text}. Clicking it...")
            business_link.click()
            
            # Wait for caseBusinessDiv_caseType to be visible and have text
            page.wait_for_selector("#caseBusinessDiv_caseType:visible", timeout=10000)
            page.wait_for_timeout(1000) # extra wait for transition
            
            html = page.locator("#caseBusinessDiv_caseType").inner_html()
            print("\n=== BUSINESS DETAILS HTML ===")
            print(html[:2000]) # print first 2000 characters
            print("=============================\n")
            
            # Dump to file
            with open("logs/business_detail_snippet.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            # Return programmatically
            print("Programmatically returning to details...")
            page.evaluate("""() => {
                document.getElementById("caseBusinessDiv_caseType").style.display = "none";
                const pFir = document.getElementById("printDiv_fir");
                if (pFir) pFir.style.display = "none";
                document.getElementById("history").style.display = "block";
                document.getElementById("CScaseType").style.display = "block";
                const mBack = document.getElementById("main_back_caseType");
                if (mBack) mBack.style.display = "block";
            }""")
            page.wait_for_timeout(1000)
            print("Return complete. Check if history is visible:", page.locator("#history").is_visible())
        else:
            print("No business links found.")

if __name__ == '__main__':
    main()
