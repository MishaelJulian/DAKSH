"""Diagnostic script testing various eCourts portal entry points and session URLs."""
from __future__ import annotations
import time
from playwright.sync_api import sync_playwright

TEST_URLS = [
    "https://services.ecourts.gov.in/",
    "https://services.ecourts.gov.in/ecourtindia_v6/",
    "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index",
    "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus",
    "https://ecourts.gov.in/",
]

def main() -> None:
    print("=== Testing eCourts Portal Entry Point URLs ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        page = context.new_page()

        for url in TEST_URLS:
            print(f"\nTesting URL: {url}")
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(2)
                status = response.status if response else "N/A"
                final_url = page.url
                title = page.title()
                body = page.inner_text("body")[:250].replace("\n", " ")
                has_state = page.locator("#sess_state_code").count() > 0 and page.locator("#sess_state_code").is_visible()
                print(f"  Status Code: {status}")
                print(f"  Final URL  : {final_url}")
                print(f"  Page Title : '{title}'")
                print(f"  Body Text  : '{body}'")
                print(f"  #sess_state_code visible: {has_state}")

                # Print links on page if any
                anchors = page.locator("a").all()
                link_texts = []
                for a in anchors[:10]:
                    txt = a.inner_text().strip()
                    if txt:
                        link_texts.append(txt)
                if link_texts:
                    print(f"  Sample Links: {link_texts[:5]}")

            except Exception as e:
                print(f"  Error loading {url}: {e}")

        context.close()
        browser.close()
    print("\n=== Entry Point Test Complete ===")

if __name__ == "__main__":
    main()
