"""
fetch_roster.py
===============
Universal eCourts Search Roster Fetcher for Disposed Execution Petitions.
(Case Type: EX [23^3], Complex: 1030135, Est: 3 - Prl City Civil & Sessions Judge, Bangalore)

Usage:
  python fetch_roster.py --year 2025
  python fetch_roster.py --year 2024
"""

import argparse
import os
import sys
import time
from pathlib import Path
from bs4 import BeautifulSoup

from deeper_tool.scraper import DeeperScraper
from run_scraper import parse_case_roster_from_html


def fetch_roster_for_year(year: str) -> Path:
    print(f"\n[1/4] Initializing session with eCourts portal for Year {year}...")
    scraper = DeeperScraper(pacing=2.0)
    scraper.init_session()

    print("[2/4] Setting court complex (1030135) and establishment (3)...")
    scraper.set_establishment(
        complex_code="1030135",
        state_code="3",
        dist_code="20",
        est_code="3",
    )

    print(f"[3/4] Solving CAPTCHA and submitting search query for {year} Disposed Execution Cases...")
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
            "search_year": str(year),
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

        print("  [+] Search query accepted by eCourts!")
        break

    if not case_data or "Invalid Captcha" in case_data:
        print(f"[-] Failed to retrieve {year} case roster after retries.")
        sys.exit(1)

    out_file = Path(f"disposed_{year}.html")
    print(f"[4/4] Saving roster to {out_file.name}...")
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Disposed Cases {year} - City Civil Court Bangalore</title>
</head>
<body>
    <div id="dispTable">
        {case_data}
    </div>
</body>
</html>
"""
    out_file.write_text(full_html, encoding="utf-8")
    print(f"[+] Saved {out_file.stat().st_size:,} bytes to {out_file.resolve()}")

    roster = parse_case_roster_from_html(out_file)
    print(f"[+] Verification: parse_case_roster_from_html successfully loaded {len(roster)} cases for {year}!")
    if roster:
        print(f"    First case: {roster[0]}")
        print(f"    Last case : {roster[-1]}")
    else:
        print(f"    Note: No disposed execution cases found for year {year} yet (or empty result).")

    return out_file


def main():
    parser = argparse.ArgumentParser(description="Universal eCourts Search Roster Fetcher")
    parser.add_argument(
        "--year",
        type=str,
        default="2025",
        help="Target year (default: 2025)",
    )
    args = parser.parse_args()
    fetch_roster_for_year(args.year)


if __name__ == "__main__":
    main()
