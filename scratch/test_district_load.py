from playwright.sync_api import sync_playwright
import time

def main():
    print("Launching playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Listen to requests/responses
        def on_request(req):
            if "dist" in req.url or "ajax" in req.url or "complex" in req.url or "est" in req.url:
                print(f"Request: {req.method} {req.url}")
                
        def on_response(res):
            if "dist" in res.url or "ajax" in res.url or "complex" in res.url or "est" in res.url:
                print(f"Response: {res.status} {res.url}")
                    
        page.on("request", on_request)
        page.on("response", on_response)
        
        url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded")
        
        # Wait for state dropdown
        page.wait_for_selector("#sess_state_code")
        
        # Print initial state and district options
        states = page.eval_on_selector("#sess_state_code", "el => Array.from(el.options).map(o => o.text.trim())")
        districts = page.eval_on_selector("#sess_dist_code", "el => Array.from(el.options).map(o => o.text.trim())")
        print(f"Initial states count: {len(states)}")
        print(f"Initial districts count: {len(districts)}")
        
        # Select Karnataka (value '3')
        print("Selecting state 'Karnataka' (value: 3)...")
        page.select_option("#sess_state_code", value="3")
        
        # Wait for 10 seconds to see if ajax calls trigger
        print("Waiting 10 seconds...")
        for _ in range(50):
            page.wait_for_timeout(200)
        
        # Check district options again
        districts_after = page.eval_on_selector("#sess_dist_code", "el => Array.from(el.options).map(o => o.text.trim())")
        print(f"Districts after selection count: {len(districts_after)}")
        print(f"Districts options: {districts_after[:10]}")
        
        browser.close()

if __name__ == "__main__":
    main()
