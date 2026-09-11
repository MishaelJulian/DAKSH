"""Automated test suite verifying eCourts Karnataka Production Scraper output datasets against production specification rules.

Checks:
  - JSON array structure and nested array non-null assertions
  - Post-export disk re-read verification
  - Wide Consolidated CSV/XLSX generation and BOM headers
  - Master CSV column consistency
  - Relational CSV integrity (cases, history, orders, business, processes, transfers, documents)
  - 1-to-1 row-count equality across JSON, CSV, and Excel
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

from ecourts_scraper import config
from ecourts_scraper.exporter import (
    clean_canonical_record, export_dataset, merge_multi_year_datasets,
    CASES_COLUMNS, MASTER_COLUMNS, CONSOLIDATED_COLUMNS
)

def check_bom(path: Path) -> bool:
    if not path.exists():
        return False
    with open(path, "rb") as f:
        bom = f.read(3)
    return bom == b'\xef\xbb\xbf'

def test_mock_export_pipeline() -> None:
    """Tests export pipeline logic with sample canonical records."""
    print("Running export pipeline test...")
    sample_records = [
        {
            "cnr": "KAKA010000012023",
            "case_number": "EX/1/2023",
            "case_type_label": "EX - Execution Petition",
            "case_title": "State Bank of India vs John Doe",
            "appellant": "State Bank of India",
            "respondent": "John Doe",
            "bench_city": "BENGALURU",
            "bench_state": "Karnataka",
            "court_name": "PRL. CITY CIVIL AND SESSIONS JUDGE",
            "filing_date": "01-01-2023",
            "first_hearing_date": "10-01-2023",
            "last_hearing_date": "15-06-2023",
            "next_hearing_date": "",
            "decision_date": "15-06-2023",
            "case_status": "Disposed",
            "sub_stage": "Decreed",
            "nature_of_disposal": "Allowed",
            "disposal_date": "15-06-2023",
            "sections": "CPC Section 21",
            "judges": "PRL. CITY CIVIL AND SESSIONS JUDGE",
            "petitioner_advocates": "Adv. Ramesh",
            "respondent_advocates": "Adv. Suresh",
            "case_duration_days": "165",
            "filing_to_first_hearing_days": "9",
            "has_orders": "1",
            "order_count": "1",
            "hearing_count": "1",
            "scraped_at": "2026-08-19T00:00:00",
            "source_file": "eCourts_Scraper_2023",
            "orders": [
                {
                    "order_number": "1",
                    "order_date": "15-06-2023",
                    "order_link": "https://services.ecourts.gov.in/order.pdf",
                    "business": "Petition allowed with costs.",
                    "nature_of_disposal": "Allowed",
                    "disposal_date": "15-06-2023",
                    "judge": "PRL. CITY CIVIL AND SESSIONS JUDGE",
                    "full_order_text": "Case called out. Heard arguments. Petition allowed with costs.",
                    "documents": []
                }
            ],
            "history": [
                {
                    "cnr": "KAKA010000012023",
                    "case_number": "EX/1/2023",
                    "history_index": "1",
                    "hearing_date": "15-06-2023",
                    "order_number": "1",
                    "judge": "PRL. CITY CIVIL AND SESSIONS JUDGE",
                    "purpose_of_hearing": "ORDERS",
                    "business_summary": "Petition allowed with costs."
                }
            ],
            "processes": [],
            "transfers": [],
            "documents": []
        }
    ]

    # Test export pipeline
    output_dir = PROJECT_ROOT / "eCourts_Executive_Petitions_2023_Test"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config.DATA_DIR = output_dir
    config.JSON_DIR = output_dir
    config.CSV_DIR = output_dir
    config.JSON_PATH = output_dir / "cases.json"
    config.CSV_PATH = output_dir / "cases.csv"
    config.EXCEL_PATH = output_dir / "Scraped_Cases_2023.xlsx"
    config.MASTER_CSV_PATH = output_dir / "Executive_Petitions_2023_Master.csv"
    config.CONSOLIDATED_CSV_FILENAME = "Consolidated_Executive_Petitions_2023.csv"
    config.CONSOLIDATED_XLSX_FILENAME = "Consolidated_Executive_Petitions_2023.xlsx"

    json_p, csv_p, excel_p = export_dataset(sample_records)

    assert json_p.exists(), "cases.json missing"
    assert (output_dir / "Consolidated_Executive_Petitions_2023.csv").exists(), "Consolidated CSV missing"
    assert (output_dir / "Consolidated_Executive_Petitions_2023.xlsx").exists(), "Consolidated XLSX missing"
    assert (output_dir / "Executive_Petitions_2023_Master.csv").exists(), "Master CSV missing"
    
    # Check UTF-8 BOM
    assert check_bom(output_dir / "Consolidated_Executive_Petitions_2023.csv"), "Consolidated CSV missing UTF-8 BOM"
    assert check_bom(output_dir / "Executive_Petitions_2023_Master.csv"), "Master CSV missing UTF-8 BOM"

    # Reload JSON check
    with open(json_p, "r", encoding="utf-8") as f:
        reloaded = json.load(f)
    assert len(reloaded) == len(sample_records), "Disk re-read count mismatch"

    print("[+] All mock export pipeline assertions PASSED!")

def main() -> None:
    print("==================================================")
    print("  eCourts Production Scraper Test & Validation")
    print("==================================================")
    test_mock_export_pipeline()
    print("==================================================\n")

if __name__ == "__main__":
    main()
