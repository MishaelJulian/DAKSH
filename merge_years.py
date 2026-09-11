"""Standalone CLI utility to merge 2023, 2024, and 2025 scraped datasets into combined cross-year deliverables.

Outputs:
  - Executive_Petitions_2023_2025.csv
  - Executive_Petitions_2023_2025.xlsx
"""
from __future__ import annotations
import sys
from pathlib import Path

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from ecourts_scraper.exporter import merge_multi_year_datasets

def main() -> None:
    print("==================================================")
    print("   eCourts Multi-Year Dataset Merger (2023-2025)")
    print("==================================================")
    
    years = ["2023", "2024", "2025"]
    print(f"Merging target years: {', '.join(years)}")
    
    csv_path, xlsx_path = merge_multi_year_datasets(years=years)
    
    print("\n[+] SUCCESS: Multi-year datasets successfully merged!")
    print(f"    Combined CSV : {csv_path}")
    print(f"    Combined XLSX: {xlsx_path}")
    print("==================================================\n")

if __name__ == "__main__":
    main()
