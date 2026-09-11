"""Cross-validation test suite checking data quality and consistency across JSON, Excel, Master CSV, and Relational CSVs.

Usage:
    python test_export_consistency.py
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from ecourts_scraper.exporter import (
    CASES_COLUMNS, ORDERS_COLUMNS, BUSINESS_COLUMNS,
    CASE_HISTORY_COLUMNS, PROCESSES_COLUMNS, TRANSFERS_COLUMNS,
    DOCUMENTS_COLUMNS, MASTER_COLUMNS
)

DATA_DIR = PROJECT_ROOT / "data"
JSON_PATH = DATA_DIR / "cases.json"
EXCEL_PATH = DATA_DIR / "Scraped_Cases.xlsx"
MASTER_CSV_PATH = DATA_DIR / "Executive_Petitions_2010_Master.csv"


def check_bom(path: Path) -> bool:
    if not path.exists():
        return False
    with open(path, "rb") as f:
        bom = f.read(3)
    return bom == b'\xef\xbb\xbf'


def load_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        # Try timestamped fallback in same folder
        stem = path.stem
        candidates = sorted(path.parent.glob(f"{stem}_*.csv"), reverse=True)
        if candidates:
            path = candidates[0]
        else:
            return [], []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def main() -> None:
    # 1. Load JSON canonical data
    if not JSON_PATH.exists():
        print(f"Error: JSON file not found at {JSON_PATH}")
        sys.exit(1)
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        json_records = json.load(f)
        
    # JSON Verification
    json_validation = "PASS"
    if len(json_records) != 20:
        json_validation = "FAIL (not 20 cases)"
        
    for r in json_records:
        # Check expected keys and list types
        for k in ["orders", "business_list", "history", "processes", "transfers", "documents"]:
            if k not in r or not isinstance(r[k], list):
                json_validation = f"FAIL (missing or non-array '{k}')"
            # Ensure no nulls inside nested arrays
            if r[k] and any(x is None for x in r[k]):
                json_validation = f"FAIL (null values in array '{k}')"

    # 2. Excel Verification
    excel_validation = "PASS"
    excel_case_count = 0
    if not EXCEL_PATH.exists():
        excel_validation = "FAIL (file missing)"
    else:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
            sheet = wb.active
            
            # Count cases based on header markers
            for row in sheet.iter_rows(min_row=1, max_col=1, values_only=True):
                cell_val = str(row[0]).strip() if row[0] is not None else ""
                if cell_val.startswith("CASE ") and "—" in cell_val:
                    excel_case_count += 1
                    
            if excel_case_count != 20:
                excel_validation = f"FAIL (found {excel_case_count} cases in excel, expected 20)"
                
            # Verify Excel formatting rules
            if sheet.freeze_panes != "A2":
                excel_validation = f"FAIL (sheet freeze_panes is {sheet.freeze_panes}, expected A2)"
            if not sheet.auto_filter.ref:
                excel_validation = "FAIL (auto_filter filter range is missing)"
        except Exception as e:
            excel_validation = f"FAIL ({e})"

    # 3. Master CSV Validation
    master_validation = "PASS"
    master_headers, master_rows = load_csv_rows(MASTER_CSV_PATH)
    
    if len(master_rows) != 20:
        master_validation = f"FAIL (found {len(master_rows)} rows, expected 20)"
    elif len(master_headers) != len(MASTER_COLUMNS) or set(master_headers) != set(MASTER_COLUMNS):
        master_validation = "FAIL (column count or headers mismatch)"
    else:
        # Check summaries are filled and have no nested JSON or multiline values
        for idx, row in enumerate(master_rows):
            for col, val in row.items():
                if val and (val.startswith("[{") or val.startswith('{"')):
                    master_validation = f"FAIL (nested JSON leaked in row {idx+1} col '{col}')"
                if val and "\n" in val:
                    master_validation = f"FAIL (multiline paragraph leaked in row {idx+1} col '{col}')"
            
            # Verify concise summaries
            total_biz = int(row.get("total_business_entries", "0"))
            biz_sum = row.get("business_summary", "")
            hist_sum = row.get("history_summary", "")
            
            if total_biz > 0 and not biz_sum:
                master_validation = f"FAIL (empty business_summary in row {idx+1} despite having business entries)"
            elif total_biz == 0 and biz_sum:
                master_validation = f"FAIL (non-empty business_summary in row {idx+1} despite 0 business entries)"
                
            if "hearings between" not in hist_sum and int(row.get("total_history_rows", "0")) > 0:
                master_validation = f"FAIL (invalid history_summary format in row {idx+1}: '{hist_sum}')"

    # 4. Normalized CSV Validation
    norm_validation = "PASS"
    rel_tables = ["cases", "orders", "business", "case_history", "processes", "transfers", "documents"]
    csv_rows_dict = {}
    csv_headers_dict = {}
    
    for tbl in rel_tables:
        hdrs, rows = load_csv_rows(DATA_DIR / f"{tbl}.csv")
        csv_headers_dict[tbl] = hdrs
        csv_rows_dict[tbl] = rows
        
    # Check cases row count
    cases_rows = csv_rows_dict.get("cases", [])
    if len(cases_rows) != 20:
        norm_validation = f"FAIL (cases.csv has {len(cases_rows)} rows, expected 20)"
        
    # No JSON/multiline in cases
    for idx, r in enumerate(cases_rows):
        for col, val in r.items():
            if val and (val.startswith("[{") or val.startswith('{"')):
                norm_validation = f"FAIL (JSON in cases.csv row {idx+1} col '{col}')"
            if val and "\n" in val:
                norm_validation = f"FAIL (multiline in cases.csv row {idx+1} col '{col}')"

    # 5. Relationships Validation (FK checks)
    relationships = "PASS"
    case_cnrs = {r.get("cnr") for r in cases_rows}
    case_numbers = {r.get("case_number") for r in cases_rows}
    
    for tbl in ["orders", "business", "case_history", "processes", "transfers", "documents"]:
        tbl_rows = csv_rows_dict.get(tbl, [])
        for idx, r in enumerate(tbl_rows):
            cnr = r.get("cnr")
            case_num = r.get("case_number")
            if cnr not in case_cnrs or case_num not in case_numbers:
                relationships = f"FAIL (orphan record in {tbl}.csv row {idx+1})"
                break

    # 6. Encoding and BOM checks
    encoding = "UTF-8"
    all_csvs = [DATA_DIR / "Executive_Petitions_2010_Master.csv"] + [DATA_DIR / f"{tbl}.csv" for tbl in rel_tables]
    for p in all_csvs:
        # Check actual files on disk
        if p.exists() or list(p.parent.glob(f"{p.stem}_*.csv")):
            resolved_p = p if p.exists() else sorted(p.parent.glob(f"{p.stem}_*.csv"))[0]
            if not check_bom(resolved_p):
                encoding = f"FAIL ({resolved_p.name} missing UTF-8 BOM)"
                break

    # 7. Data Quality Metrics
    duplicate_case_numbers = 0
    missing_cnrs = 0
    missing_petitioners = 0
    missing_respondents = 0
    missing_disposal_dates = 0
    missing_nature_of_disposal = 0
    
    # Check across cases.csv
    case_nums_seen = set()
    for r in cases_rows:
        num = r.get("case_number", "")
        if num in case_nums_seen:
            duplicate_case_numbers += 1
        case_nums_seen.add(num)
        
        if not r.get("cnr"):
            missing_cnrs += 1
        if not r.get("appellant"):
            missing_petitioners += 1
        if not r.get("respondent"):
            missing_respondents += 1
        if not r.get("disposal_date"):
            missing_disposal_dates += 1
        if not r.get("nature_of_disposal"):
            missing_nature_of_disposal += 1

    # Counts
    orders_n = len(csv_rows_dict.get("orders", []))
    business_n = len(csv_rows_dict.get("business", []))
    history_n = len(csv_rows_dict.get("case_history", []))
    processes_n = len(csv_rows_dict.get("processes", []))
    transfers_n = len(csv_rows_dict.get("transfers", []))
    documents_n = len(csv_rows_dict.get("documents", []))

    # Overall Status
    overall = "READY FOR DELIVERY"
    all_passes = [
        json_validation == "PASS",
        excel_validation == "PASS",
        master_validation == "PASS",
        norm_validation == "PASS",
        relationships == "PASS",
        "FAIL" not in encoding,
        duplicate_case_numbers == 0,
        missing_cnrs == 0,
        missing_petitioners == 0,
        missing_respondents == 0,
        missing_disposal_dates == 0,
        missing_nature_of_disposal == 0
    ]
    if not all(all_passes):
        overall = "NEEDS ATTENTION"

    # Write final validation report to stdout
    print("\n" + "=" * 36)
    print("      EXPORT VALIDATION REPORT")
    print("=" * 36)
    print(f"Cases                  {len(json_records)} / 20")
    print(f"Orders                 {orders_n}")
    print(f"Business Pages         {business_n}")
    print(f"History Rows           {history_n}")
    print(f"Processes              {processes_n}")
    print(f"Transfers              {transfers_n}")
    print(f"Documents              {documents_n}\n")
    print(f"JSON Validation        {json_validation}")
    print(f"Excel Validation       {excel_validation}")
    print(f"Master CSV Validation  {master_validation}")
    print(f"Normalized CSV Validation {norm_validation}")
    print(f"Relationships          {relationships}")
    print(f"Encoding               {encoding}\n")
    print(f"Duplicate Case Numbers {duplicate_case_numbers}")
    print(f"Missing CNRs           {missing_cnrs}")
    print(f"Missing Petitioners    {missing_petitioners}")
    print(f"Missing Respondents    {missing_respondents}")
    print(f"Missing Disposal Dates {missing_disposal_dates}")
    print(f"Missing Nature of Disposal {missing_nature_of_disposal}\n")
    print(f"Overall Status         {overall}")
    print("=" * 36)

    # Save validation report under logs/ as md
    md_report = f"""# Relational & Master CSV Export Validation Report

- **Cases Validated**: {len(json_records)} / 20
- **Orders**: {orders_n}
- **Business Pages**: {business_n}
- **History Rows**: {history_n}
- **Processes**: {processes_n}
- **Transfers**: {transfers_n}
- **Documents**: {documents_n}

## Validation Summary
* **JSON Validation**: {json_validation}
* **Excel Validation**: {excel_validation}
* **Master CSV Validation**: {master_validation}
* **Normalized CSV Validation**: {norm_validation}
* **Relationships**: {relationships}
* **Encoding**: {encoding}

## Data Quality Checks
* **Duplicate Case Numbers**: {duplicate_case_numbers}
* **Missing CNRs**: {missing_cnrs}
* **Missing Petitioners**: {missing_petitioners}
* **Missing Respondents**: {missing_respondents}
* **Missing Disposal Dates**: {missing_disposal_dates}
* **Missing Nature of Disposal**: {missing_nature_of_disposal}

**Overall Status**: {overall}
"""
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    with open(logs_dir / "export_validation_report.md", "w", encoding="utf-8") as f:
        f.write(md_report)

    if overall == "NEEDS ATTENTION":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
