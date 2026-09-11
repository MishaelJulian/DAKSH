from playwright.sync_api import sync_playwright
import time

def main():
    print("Launching playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index"
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                print(f"Navigation attempt {attempt}/{max_retries} to {url}...")
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                print("Navigation successful!")
                break
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    print("All attempts failed. Exiting.")
                    browser.close()
                    return
                time.sleep(2)
        
        # Check if viewBusiness is defined
        is_defined = page.evaluate("typeof viewBusiness !== 'undefined'")
        print("Is viewBusiness defined?", is_defined)
        if is_defined:
            func_str = page.evaluate("viewBusiness.toString()")
            print("\n=== viewBusiness source code ===")
            print(func_str)
        else:
            # Let's search in scripts on the page
            print("viewBusiness is not defined yet. Checking scripts...")
            script_srcs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('script')).map(s => s.src).filter(Boolean);
            }""")
            print("Script sources found on page:")
            for src in script_srcs:
                print("-", src)
                
        browser.close()

if __name__ == "__main__":
    main()
