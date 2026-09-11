from playwright.sync_api import sync_playwright

def main():
    print("Launching playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index", wait_until="domcontentloaded")
        
        # Print function source code
        js_source = page.evaluate("() => typeof validateStateDistCourt !== 'undefined' ? validateStateDistCourt.toString() : 'undefined'")
        print("\n=== validateStateDistCourt source code ===")
        print(js_source)
        print("==========================================\n")
        
        browser.close()

if __name__ == "__main__":
    main()
