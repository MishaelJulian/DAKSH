"""Diagnostic script inspecting the Karnataka District Court selection page on eCourts 2.0."""
from __future__ import annotations
import time
from playwright.sync_api import sync_playwright

def main() -> None:
    print("=== Inspecting Karnataka Page on eCourts 2.0 ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Step 1: Open main portal -> District Courts -> Karnataka
        page.goto("https://ecourts.gov.in/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        page.locator("a:has-text('District Courts')").first.click()
        time.sleep(2)

        page.locator("a:has-text('Karnataka')").first.click()
        time.sleep(3)

        print(f"Current URL: {page.url}")

        # Check options in #sateist dropdown
        if page.locator("#sateist").count() > 0:
            options = page.eval_on_selector(
                "#sateist",
                "el => Array.from(el.options).map(o => ({ text: o.text.trim(), value: o.value }))"
            )
            print(f"Found {len(options)} options in #sateist dropdown:")
            for opt in options[:15]:
                print(f"  value: '{opt['value']}' | text: '{opt['text']}'")

            # Try selecting BENGALURU or Bengaluru Urban
            bengaluru_opt = next((o for o in options if "bengaluru" in o["text"].lower() or "bangalore" in o["text"].lower()), None)
            if bengaluru_opt:
                print(f"\nSelecting District option: '{bengaluru_opt['text']}' (value={bengaluru_opt['value']})...")
                page.select_option("#sateist", value=bengaluru_opt["value"])
                time.sleep(3)

                print(f"Post-selection URL: {page.url}")
                print(f"Post-selection Title: {page.title()}")

                # Check text/links/iframes/forms on post-selection page
                links = page.locator("a").all()
                link_list = [(a.inner_text().strip(), a.get_attribute("href") or "", a.get_attribute("onclick") or "") for a in links if a.inner_text().strip()]
                print(f"\nLinks after district selection ({len(link_list)}):")
                for txt, href, onclick in link_list[:20]:
                    print(f"  Text: '{txt}' | href: '{href}' | onclick: '{onclick}'")

                # Check if an iframe is embedded
                iframes = page.frames
                print(f"\nTotal frames on page: {len(iframes)}")
                for idx, frame in enumerate(iframes):
                    print(f"  Frame [{idx}]: name='{frame.name}' | url='{frame.url}'")
                    has_state_frame = frame.locator("#sess_state_code").count() > 0 and frame.locator("#sess_state_code").is_visible()
                    print(f"    #sess_state_code visible in frame: {has_state_frame}")

        context.close()
        browser.close()
    print("\n=== Inspection Complete ===")

if __name__ == "__main__":
    main()
