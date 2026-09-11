"""Audit script: Programmatically compare cases.json vs cases.csv vs Scraped_Cases.xlsx.

Reports row counts, column counts, headers, missing fields, serialization bugs.
"""
import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
FINAL_DIR = BASE / "eCourts_Executive_Petitions_2010_Final"
DATA_DIR  = BASE / "data"

JSON_PATH = FINAL_DIR / "cases.json" if (FINAL_DIR / "cases.json").exists() else DATA_DIR / "cases.json"
CSV_PATH  = FINAL_DIR / "cases.csv"  if (FINAL_DIR / "cases.csv").exists()  else DATA_DIR / "cases.csv"

def load_json():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_csv():
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return reader.fieldnames, rows

def main():
    print("=" * 80)
    print("CSV EXPORT AUDIT REPORT")
    print("=" * 80)

    # ── Load JSON ──
    json_data = load_json()
    json_count = len(json_data)
    json_keys = list(json_data[0].keys()) if json_data else []
    print(f"\n[JSON] Rows: {json_count}")
    print(f"[JSON] Columns: {len(json_keys)}")
    print(f"[JSON] Headers: {json_keys}")

    # ── Load CSV ──
    csv_headers, csv_rows = load_csv()
    csv_count = len(csv_rows)
    print(f"\n[CSV]  Rows: {csv_count}")
    print(f"[CSV]  Columns: {len(csv_headers)}")

    # Check for trailing empty headers
    empty_headers = [h for h in csv_headers if not h or h.strip() == ""]
    if empty_headers:
        print(f"[CSV]  WARNING: {len(empty_headers)} extra empty column headers found!")
    real_headers = [h for h in csv_headers if h and h.strip()]
    print(f"[CSV]  Real headers: {real_headers}")

    # ── Row Count Match ──
    print("\n" + "-" * 80)
    if json_count == csv_count:
        print(f"PASS Row counts match: {json_count}")
    else:
        print(f"FAIL ROW COUNT MISMATCH: JSON={json_count}, CSV={csv_count}")

    # ── Header Comparison ──
    print("\n" + "-" * 80)
    json_set = set(json_keys)
    csv_set = set(real_headers)
    missing_in_csv = json_set - csv_set
    extra_in_csv = csv_set - json_set
    if missing_in_csv:
        print(f"FAIL Missing in CSV: {missing_in_csv}")
    if extra_in_csv:
        print(f"FAIL Extra in CSV: {extra_in_csv}")
    if not missing_in_csv and not extra_in_csv:
        print("PASS Headers match between JSON and CSV")

    # ── Field-by-field comparison (first case) ──
    if csv_count >= 1 and json_count >= 1:
        print("\n" + "-" * 80)
        print("FIELD-BY-FIELD COMPARISON (Case 1)")
        print("-" * 80)
        j = json_data[0]
        c = csv_rows[0] if csv_count >= 1 else {}

        for key in json_keys:
            j_val = j.get(key, "")
            c_val = c.get(key, "<MISSING>")

            # Normalize for comparison
            j_str = str(j_val) if j_val is not None else ""
            c_str = str(c_val) if c_val is not None else ""

            if j_str == c_str:
                status = "MATCH"
            elif j_str[:50] == c_str[:50]:
                status = "PARTIAL (first 50 chars match)"
            else:
                status = "MISMATCH"

            if status != "MATCH":
                print(f"\n  [{status}] {key}")
                print(f"    JSON: {repr(j_str[:120])}")
                print(f"    CSV:  {repr(c_str[:120])}")

    # ── Raw CSV line count ──
    print("\n" + "-" * 80)
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()
    print(f"[RAW] Total lines in CSV file: {len(raw_lines)}")
    print(f"[RAW] Expected: {json_count + 1} (header + {json_count} data rows)")
    if len(raw_lines) != json_count + 1:
        print(f"FAIL LINE COUNT BUG: {len(raw_lines)} raw lines instead of {json_count + 1}")
        print(f"  This means multiline values are NOT properly quoted/escaped!")

    # ── Date format check ──
    print("\n" + "-" * 80)
    print("DATE FORMAT CHECK")
    date_fields = ["filing_date", "first_hearing_date", "last_hearing_date",
                   "next_hearing_date", "decision_date"]
    if csv_count >= 1:
        c = csv_rows[0]
        for df in date_fields:
            val = c.get(df, "")
            if val:
                if "/" in val:
                    print(f"  FAIL {df} = {repr(val)} -- uses SLASHES (should be DD-MM-YYYY)")
                elif "-" in val:
                    print(f"  PASS {df} = {repr(val)} -- correct format")
                else:
                    print(f"  WARN {df} = {repr(val)} -- unknown format")

    # ── cnr_case_number check ──
    print("\n" + "-" * 80)
    print("CNR_CASE_NUMBER CHECK")
    if csv_count >= 1:
        j_val = json_data[0].get("cnr_case_number", "")
        c_val = csv_rows[0].get("cnr_case_number", "")
        print(f"  JSON: {repr(j_val)}")
        print(f"  CSV:  {repr(c_val)}")
        if j_val != c_val:
            print(f"  FAIL VALUE CORRUPTED (likely Excel date auto-interpretation)")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
