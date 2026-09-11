"""Configuration settings for the eCourts scraper.

Contains all constants, navigation targets, and behavioral parameters.
Supports per-year output directories and CLI argument parsing.
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# CLI Argument Parsing
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    """Parses command-line arguments for year selection and resume mode."""
    parser = argparse.ArgumentParser(
        description="eCourts Karnataka Executive Petition Scraper (Production)"
    )
    parser.add_argument(
        "--year",
        type=str,
        default=os.getenv("ECOURTS_YEAR", ""),
        help="Filing year to scrape (e.g. 2023, 2024, 2025). Required unless --merge-only is used."
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=False,
        help="Resume from last checkpoint instead of starting fresh."
    )
    parser.add_argument(
        "--merge-only",
        action="store_true",
        default=False,
        help="Skip scraping; only merge existing per-year datasets into combined output."
    )
    # Parse known args to avoid conflicts when running from other entry points
    args, _ = parser.parse_known_args()
    return args

# Only parse CLI args when running as a script (not during imports for tests)
_cli_args = _parse_args()

# ---------------------------------------------------------------------------
# Year and Paths
# ---------------------------------------------------------------------------

YEAR = _cli_args.year
RESUME_MODE = _cli_args.resume
MERGE_ONLY = _cli_args.merge_only

def get_year_data_dir(year: str) -> Path:
    """Returns the output directory for a given year."""
    return BASE_DIR / f"eCourts_Executive_Petitions_{year}"

def get_merged_dir() -> Path:
    """Returns the directory for the merged cross-year dataset."""
    return BASE_DIR / "eCourts_Executive_Petitions_2023_2025_Merged"

# Per-year output paths (set dynamically based on --year)
if YEAR:
    DATA_DIR = get_year_data_dir(YEAR)
else:
    # Fallback for merge-only mode or no year specified
    DATA_DIR = BASE_DIR / "eCourts_Executive_Petitions_output"

JSON_DIR = DATA_DIR
CSV_DIR = DATA_DIR
ORDERS_DIR = DATA_DIR / "orders"
LOGS_DIR = DATA_DIR / "logs"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"

MERGED_DIR = get_merged_dir()

# Ensure directories exist
for directory in [DATA_DIR, ORDERS_DIR, LOGS_DIR, SNAPSHOTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Filenames (year-aware)
# ---------------------------------------------------------------------------

SOURCE_FILE = f"eCourts_Scraper_{YEAR}" if YEAR else "eCourts_Scraper"
JSON_FILENAME = "cases.json"
CSV_FILENAME = "cases.csv"
EXCEL_FILENAME = f"Scraped_Cases_{YEAR}.xlsx" if YEAR else "Scraped_Cases.xlsx"
MASTER_CSV_FILENAME = f"Executive_Petitions_{YEAR}_Master.csv" if YEAR else "Executive_Petitions_Master.csv"
CONSOLIDATED_CSV_FILENAME = f"Consolidated_Executive_Petitions_{YEAR}.csv" if YEAR else "Consolidated_Executive_Petitions.csv"
CONSOLIDATED_XLSX_FILENAME = f"Consolidated_Executive_Petitions_{YEAR}.xlsx" if YEAR else "Consolidated_Executive_Petitions.xlsx"

# Resolve absolute paths
JSON_PATH = JSON_DIR / JSON_FILENAME
CSV_PATH = CSV_DIR / CSV_FILENAME
EXCEL_PATH = DATA_DIR / EXCEL_FILENAME
MASTER_CSV_PATH = DATA_DIR / MASTER_CSV_FILENAME

# ---------------------------------------------------------------------------
# Navigation and Target Parameters (eCourts Karnataka Search Page)
# ---------------------------------------------------------------------------

BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index"


STATE = os.getenv("ECOURTS_STATE", "Karnataka")
DISTRICT = os.getenv("ECOURTS_DISTRICT", "BENGALURU")
COURT_COMPLEX = os.getenv("ECOURTS_COURT_COMPLEX", "City Civil Court Complex, Bangalore")
ESTABLISHMENT = os.getenv("ECOURTS_ESTABLISHMENT", "PRL. CITY CIVIL AND SESSIONS JUDGE")
SEARCH_METHOD = os.getenv("ECOURTS_SEARCH_METHOD", "Case Type")
CASE_TYPE = os.getenv("ECOURTS_CASE_TYPE", "EX - Execution Petition U")  # Matches EX - Execution Petition Under Order...
CASE_STATUS = os.getenv("ECOURTS_CASE_STATUS", "Disposed")  # Pending vs Disposed

# ---------------------------------------------------------------------------
# Browser Configuration
# ---------------------------------------------------------------------------

HEADLESS = os.getenv("ECOURTS_HEADLESS", "False").lower() in ("true", "1", "yes")
DEFAULT_TIMEOUT = int(os.getenv("ECOURTS_DEFAULT_TIMEOUT", "30000"))  # Milliseconds
PAGE_LOAD_TIMEOUT = int(os.getenv("ECOURTS_PAGE_LOAD_TIMEOUT", "60000"))

# ---------------------------------------------------------------------------
# Automation and Retry Configuration
# ---------------------------------------------------------------------------

MAX_CAPTCHA_RETRIES = int(os.getenv("ECOURTS_MAX_CAPTCHA_RETRIES", "5"))
# MAX_CASES = 0 means unlimited — scrape ALL cases until exhausted
MAX_CASES = int(os.getenv("ECOURTS_MAX_CASES", "0"))
RETRY_COUNT = int(os.getenv("ECOURTS_RETRY_COUNT", "3"))
RETRY_DELAY = float(os.getenv("ECOURTS_RETRY_DELAY", "2.0"))
RETRY_BACKOFF = float(os.getenv("ECOURTS_RETRY_BACKOFF", "2.0"))

# ---------------------------------------------------------------------------
# Checkpointing
# ---------------------------------------------------------------------------

CHECKPOINT_INTERVAL = int(os.getenv("ECOURTS_CHECKPOINT_INTERVAL", "5"))

# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

CSV_ENCODING = "utf-8-sig"  # UTF-8 with BOM for Excel compatibility
