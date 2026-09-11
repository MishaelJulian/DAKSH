"""Regenerate all exports (Master CSV, Relational CSVs, Nested JSON, Excel) from cases.json.

Usage:
    python regenerate_csv.py

Reads:  data/json/cases.json (or data/cases.json)
Writes: All deliverables directly inside data/
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from ecourts_scraper.exporter import export_dataset


def main() -> None:
    # 1. Load canonical JSON
    json_path = PROJECT_ROOT / "data" / "json" / "cases.json"
    if not json_path.exists():
        json_path = PROJECT_ROOT / "data" / "cases.json"
        
    print(f"Loading canonical JSON from: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    print(f"  Loaded {len(records)} case records")

    # 2. Export dataset (runs cleaning, writes all 10 files under data/)
    print(f"\nRegenerating all formatted outputs to: {PROJECT_ROOT / 'data'}")
    export_dataset(records)
    print("  Done. All files regenerated successfully.")


if __name__ == "__main__":
    main()
