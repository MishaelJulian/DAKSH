"""Automated ground-truth regression tests for single-case extraction (EX/2/2023).

Tests verify that the parser and pipeline adhere strictly to zero-hallucination,
zero-cross-case-contamination mandates against visual ground-truth reference (scrape.pdf).
"""
import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from ecourts_scraper.parser import (
    parse_search_results_rows,
    parse_case_details_page,
    parse_daily_status_html,
    normalize_date,
    clean_text
)
from ecourts_scraper.models import FieldStatus, RawCaseDetail, CaseSummary
from ecourts_scraper.exporter import export_single_case_test


SNAPSHOTS_DIR = Path("eCourts_Executive_Petitions_2023/snapshots")
SEARCH_HTML_PATH = SNAPSHOTS_DIR / "search_results_page_1.html"
CASE_HTML_PATH = SNAPSHOTS_DIR / "case_EX_2_2023.html"


@pytest.fixture
def search_html():
    if not SEARCH_HTML_PATH.exists():
        pytest.skip(f"Search snapshot not found at {SEARCH_HTML_PATH}")
    return SEARCH_HTML_PATH.read_text(encoding="utf-8")


@pytest.fixture
def case_html():
    if not CASE_HTML_PATH.exists():
        pytest.skip(f"Case snapshot not found at {CASE_HTML_PATH}")
    return CASE_HTML_PATH.read_text(encoding="utf-8")


def test_search_results_first_row(search_html):
    """Requirement §6: First result row must be EX/2/2023."""
    summaries = parse_search_results_rows(search_html)
    assert len(summaries) > 0
    first = summaries[0]
    assert first.serial_number == "1"
    assert first.case_number == "EX/2/2023"
    assert "KRISHNAMURTHY" in first.parties
    assert "SATHISH" in first.parties
    assert first.cnr_from_link == "KABC010342242022"
    assert "viewHistory" in first.onclick


def test_case_details_and_status_parsing(case_html):
    """Requirements §8, §9, §41: Exact extraction of case details and status."""
    details = parse_case_details_page(case_html, expected_case_number="EX/2/2023")
    
    # Case Identity
    assert details.case_number == "EX/2/2023"
    assert details.cnr_number == "KABC010342242022"
    assert details.case_type == "EX - Execution Petition Under Order"
    
    # Filing & Registration
    assert details.filing_number == "2786/2022"
    assert details.filing_date == "17-12-2022"
    assert details.registration_number == "2/2023"
    assert details.registration_date == "02-01-2023"
    
    # e-Filing should be NOT_AVAILABLE
    assert details.efiling_number is None
    assert details.field_results["efiling_number"].status == FieldStatus.NOT_AVAILABLE.value
    
    # Status Table
    assert details.first_hearing_date == "02nd January 2023"
    assert details.decision_date == "06th December 2025"
    assert details.case_status == "Case disposed"
    assert details.nature_of_disposal == "Uncontested--DISMISSED"
    assert "CCH64" in details.court_number_and_judge


def test_parties_zero_contamination(case_html):
    """Requirements §10, §11: No copied advocate for respondent."""
    details = parse_case_details_page(case_html)
    
    assert len(details.petitioners) == 1
    pet_name, pet_adv = details.petitioners[0]
    assert pet_name == "KRISHNAMURTHY G"
    assert pet_adv == "DINESH J S"
    
    assert len(details.respondents) == 1
    resp_name, resp_adv = details.respondents[0]
    assert resp_name == "SATHISH M"
    assert resp_adv is None  # Must NOT hallucinate an advocate


def test_acts_zero_guesswork(case_html):
    """Requirement §12: Act captured without guessing section."""
    details = parse_case_details_page(case_html)
    assert len(details.acts) == 1
    act = details.acts[0]
    assert act.act_name == "U/O 21 RULE 11 OF CPC"
    assert act.sections is None  # Under Section(s) is empty in scrape.pdf


def test_processes_table(case_html):
    """Requirement §13: Process table extracted with exact columns."""
    details = parse_case_details_page(case_html)
    assert len(details.processes) == 1
    proc = details.processes[0]
    assert proc.process_id == "PKABC010342242022_1_1"
    assert "Notice to show cause" in proc.process_title
    assert proc.process_date == "07-01-2023"


def test_case_history_and_orders_table(case_html):
    """Requirements §14, §21: Exact history count (32) and final orders count (1)."""
    details = parse_case_details_page(case_html)
    assert len(details.history) == 32
    assert len(details.orders) == 1
    
    # First history row in reverse chrono
    first_h = details.history[0]
    assert first_h.business_date == "06-12-2025"
    assert first_h.purpose == "Disposed"
    
    # Final order row
    order = details.orders[0]
    assert order.order_number == "1"
    assert order.order_date == "06-12-2025"
    assert order.order_details == "Judgment"


def test_daily_status_parsing():
    """Requirements §16, §17, §18: Daily Status parsing and validation."""
    sample_daily = """<div id="caseBusinessDiv_caseType">
      <div id="mydiv" align="center">
        <span>PRL. CITY CIVIL AND SESSIONS JUDGE</span>
        <span><b>In the court of</b>:CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE</span>
        <span><b>CNR Number</b>:KABC010342242022</span>
        <span><b>Case Number</b>:EX/0000002/2023</span>
        <span>KRISHNAMURTHY G <b>versus</b> SATHISH M</span>
        <span><b>Date</b>: 06-12-2025</span>
        <table border="0" width="87%">
          <tr><td><b>Business</b></td><td>:</td><td>An IA.No.III filed by the JDR is dismissed. The memo filed by the DHR is hereby allowed and E.P is closed as fully satisfied.</td></tr>
          <tr><td><b>Nature of Disposal</b></td><td>:</td><td>DISMISSED</td></tr>
          <tr><td><b>Disposal Date</b></td><td>:</td><td>06-12-2025</td></tr>
        </table>
      </div>
    </div>"""
    rec = parse_daily_status_html(sample_daily)
    assert rec.cnr == "KABC010342242022"
    assert rec.case_number == "EX/0000002/2023"
    assert rec.date == "06-12-2025"
    assert "IA.No.III" in rec.business
    assert rec.nature_of_disposal == "DISMISSED"
    assert rec.disposal_date == "06-12-2025"


def test_date_normalization():
    """Requirement §30: Date normalization."""
    assert normalize_date("06-12-2025") == "2025-12-06"
    assert normalize_date("02nd January 2023") == "2023-01-02"
    assert normalize_date("17-12-2022") == "2022-12-17"
    assert normalize_date("-") is None
    assert normalize_date("invalid") is None
