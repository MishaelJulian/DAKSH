eCourts Karnataka Scraper
Executive Petition (EX) – 2010

Contents

1. Executive_Petitions_2010_Master.csv
   Summary dataset with one row per case.

2. Scraped_Cases.xlsx
   Human-readable Excel export.

3. cases.json
   Canonical structured dataset.

4. Normalized_CSVs/
   - cases.csv
   - orders.csv
   - business.csv
   - case_history.csv
   - processes.csv
   - transfers.csv

The normalized CSVs separate one-to-many relationships (orders, hearings, business entries, etc.) so that data remains complete and avoids duplication.

Keys:
- case_number
- cnr

These keys can be used to join the datasets if required.