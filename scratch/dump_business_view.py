import logging
from ecourts_scraper import config
from ecourts_scraper.browser import get_browser_page, ECourtsBrowser
from ecourts_scraper.scraper import extract_search_results
from ecourts_scraper.utils import setup_logging

def main():
    logger = setup_logging(config.LOGS_DIR)
    logger.info("Starting dump_business_view script...")

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
        
        # Now click the first Business Date link in the case history table
        # We can locate it using selector "a[onclick*='viewBusiness']"
        business_link = page.locator("a[onclick*='viewBusiness']").first
        if business_link.count() > 0:
            print("Clicking business link...")
            business_link.click()
            page.wait_for_timeout(2000) # Wait for AJAX load
            
            # Dump HTML
            html = page.content()
            with open('logs/business_view.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("Successfully dumped business view HTML to logs/business_view.html")
            
            # Capture screenshot
            page.screenshot(path='logs/business_view.png')
            print("Successfully captured business view screenshot to logs/business_view.png")
        else:
            print("No business date links found on this page.")

if __name__ == '__main__':
    main()
