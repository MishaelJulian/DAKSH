from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")
        
        is_defined = page.evaluate("typeof displayPdf !== 'undefined'")
        print("Is displayPdf defined?", is_defined)
        if is_defined:
            func_str = page.evaluate("displayPdf.toString()")
            print("\n=== displayPdf source code ===")
            print(func_str)
            
        browser.close()

if __name__ == "__main__":
    main()
