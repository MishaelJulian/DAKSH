"""
fetch_2024_roster.py
====================
Fetches the official eCourts search results roster for 2024 Disposed Execution Cases
(Case Type: EX [23^3], Complex: 1030135, Est: 3 - Prl City Civil & Sessions Judge, Bangalore)
and saves it to disposed_2024.html.
"""

import sys
import os
import time
from pathlib import Path
from bs4 import BeautifulSoup

from deeper_tool.scraper import DeeperScraper
from run_scraper import parse_case_roster_from_html

def main():
    print("[1/4] Initializing session with eCourts portal...")
    scraper = DeeperScraper(pacing=2.0)
    scraper.init_session()

    print("[2/4] Setting court complex (1030135) and establishment (3)...")
    scraper.set_establishment(
        complex_code="1030135",
        state_code="3",
        dist_code="20",
        est_code="3",
    )

    print("[3/4] Solving CAPTCHA and submitting search query for 2024 Disposed Execution Cases...")
    max_retries = 10
    case_data = ""

    for attempt in range(1, max_retries + 1):
        sol = scraper.solve_captcha()
        if not sol or len(sol) < 4:
            print(f"  Attempt {attempt}: CAPTCHA solve returned invalid '{sol}', retrying...")
            time.sleep(1.5)
            continue

        print(f"  Attempt {attempt}: Solved CAPTCHA as '{sol}'. Submitting search...")
        payload = {
            "case_type_1": "23^3",
            "search_year": "2024",
            "case_status": "Disposed",
            "ct_captcha_code": sol,
            "state_code": "3",
            "dist_code": "20",
            "court_complex_code": "1030135",
            "est_code": "3",
        }
        res = scraper._post_api("casestatus/submit_case_type", payload)
        case_data = res.get("case_data", "")

        if "Invalid Captcha" in case_data or "Enter Captcha" in case_data:
            print(f"  Attempt {attempt}: Server rejected CAPTCHA '{sol}'. Retrying...")
            time.sleep(2.0)
            continue

        if not case_data:
            print(f"  Attempt {attempt}: Empty case_data received. Response: {res}")
            time.sleep(2.0)
            continue

        print(f"  [+] Search query accepted by eCourts!")
        break

    if not case_data or "Invalid Captcha" in case_data:
        print("[-] Failed to retrieve 2024 case roster after retries.")
        sys.exit(1)

    print("[4/4] Saving roster to disposed_2024.html...")
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Disposed Cases 2024 - City Civil Court Bangalore</title>
</head>
<body>
    <div id="dispTable">
        {case_data}
    </div>
</body>
</html>
"""
    out_path = Path("disposed_2024.html")
    out_path.write_text(full_html, encoding="utf-8")
    print(f"[+] Saved {out_path.stat().st_size:,} bytes to {out_path.resolve()}")

    # Verify parser compatibility with run_scraper
    roster = parse_case_roster_from_html(out_path)
    print(f"[+] Verification: parse_case_roster_from_html successfully loaded {len(roster)} cases for 2024!")
    if roster:
        print(f"    First case: {roster[0]}")
        print(f"    Last case : {roster[-1]}")

if __name__ == "__main__":
    main()
