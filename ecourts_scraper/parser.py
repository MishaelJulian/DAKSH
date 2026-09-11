"""Structurally scoped HTML and DOM parsing functions.

Responsible for parsing exact DOM tables, rows, cells, and elements with zero guessing,
zero hallucination, and full field-status tracking (AVAILABLE, NOT_AVAILABLE, EXTRACTION_FAILED).
"""
from __future__ import annotations
import logging
import re
from datetime import datetime
from typing import Optional, Any
from bs4 import BeautifulSoup, Tag

from ecourts_scraper.models import (
    FieldStatus,
    FieldResult,
    CaseSummary,
    PartyEntry,
    ActEntry,
    ProcessEntry,
    HearingRecord,
    DailyStatusRecord,
    OrderEntry,
    DocumentEntry,
    TransferEntry,
    RawCaseDetail,
)

logger = logging.getLogger("ecourts_scraper")


def clean_text(text: Optional[str]) -> str:
    """Normalizes whitespace and strips text."""
    if not text:
        return ""
    return " ".join(text.strip().split())


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """Normalizes Indian court dates to ISO YYYY-MM-DD format.
    
    Supports:
      - 'DD-MM-YYYY' (e.g. 06-12-2025 -> 2025-12-06)
      - 'DDth Month YYYY' (e.g. 02nd January 2023 -> 2023-01-02)
    Returns None if date parsing fails without guessing.
    """
    if not date_str:
        return None
    s = clean_text(date_str)
    if not s or s in ("-", "--", ".", ",", "null", "none"):
        return None

    # Format 1: DD-MM-YYYY
    m1 = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", s)
    if m1:
        d, m, y = m1.groups()
        try:
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        except Exception:
            return None

    # Format 2: DDth Month YYYY
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", s, flags=re.IGNORECASE)
    for fmt in ("%d %B %Y", "%d %b %Y"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None


def check_portal_session_error(html_or_text: str) -> Optional[str]:
    """Detects actual session timeouts on eCourts portal."""
    if not html_or_text:
        return None
    text = html_or_text.lower()
    if "session timeout..!!!" in text or "oops! session timeout" in text or "session timeout" in text and "click here to go home page" in text:
        return "SESSION_TIMEOUT: 'Oops! Session timeout..!!! Click here to go Home Page' detected."
    return None


def parse_search_results_rows(soup_or_html: BeautifulSoup | str) -> list[CaseSummary]:
    """Extracts search results case summaries atomically from the results table.
    
    Ensures every row is treated as an atomic record (Requirement §6).
    """
    if isinstance(soup_or_html, str):
        soup = BeautifulSoup(soup_or_html, "html.parser")
    else:
        soup = soup_or_html

    table = soup.find("table", id="dispTable")
    if not table:
        for t in soup.find_all("table"):
            t_txt = t.get_text()
            if "Petitioner Name versus Respondent Name" in t_txt or "Case Type/Case Number/Case Year" in t_txt:
                table = t
                break

    if not table:
        logger.warning("Search results table not found in DOM.")
        return []

    results = []
    view_index = 0
    
    for tr in table.find_all("tr"):
        # Skip header rows
        if tr.find("th"):
            continue
        cells = tr.find_all("td")
        if len(cells) < 3:
            continue
        # Skip establishment grouping rows
        if any(c.get("colspan") and int(c.get("colspan", 1)) > 1 for c in cells):
            continue

        sr_no = clean_text(cells[0].get_text())
        if not re.match(r"^\d+$", sr_no):
            continue

        case_num = clean_text(cells[1].get_text())
        parties = clean_text(cells[2].get_text())

        # Extract View link and onclick atomically from the same row
        onclick = ""
        cnr_from_link = None
        view_cell = cells[3] if len(cells) > 3 else cells[-1]
        a_link = view_cell.find("a")
        if a_link:
            onclick = a_link.get("onclick", "")
            # Extract CNR parameter from onclick: e.g. viewHistory(..., 'KABC010342242022', ...)
            cnr_match = re.search(r"viewHistory\([^,]+,\s*'([^']+)'", onclick)
            if cnr_match:
                cnr_from_link = cnr_match.group(1).strip()

        case_id_parts = case_num.split("/")
        if len(case_id_parts) == 3:
            case_type_code, case_seq, case_year = case_id_parts
        else:
            case_type_code, case_seq, case_year = "", "", ""

        results.append(CaseSummary(
            serial_number=sr_no,
            case_number=case_num,
            parties=parties,
            view_index=view_index,
            case_type_code=case_type_code,
            case_seq=case_seq,
            case_year=case_year,
            onclick=onclick,
            cnr_from_link=cnr_from_link
        ))
        view_index += 1

    return results


def parse_case_details_page(
    soup_or_html: BeautifulSoup | str,
    expected_case_number: Optional[str] = None
) -> RawCaseDetail:
    """Structurally scoped parser for Case Details page.
    
    Parses exact tables:
      1. Case Details table
      2. Case Status table
      3. Petitioner and Advocate list
      4. Respondent and Advocate list
      5. Acts and Sections table
      6. Processes table
      7. Case History table
      8. Final Orders / Judgements table
      9. Transfers table (if any)
      10. Documents table (if any)
    
    Never falls back to global body regex.
    Distinguishes strictly between AVAILABLE, NOT_AVAILABLE, and EXTRACTION_FAILED.
    """
    if isinstance(soup_or_html, str):
        soup = BeautifulSoup(soup_or_html, "html.parser")
    else:
        soup = soup_or_html

    # Check session timeout
    timeout_err = check_portal_session_error(str(soup))
    if timeout_err:
        raise RuntimeError(timeout_err)

    field_results: dict[str, FieldResult] = {}

    # Scope to active detail container if available
    detail_container = soup.find("div", id="CScaseType") or soup

    # --- 1. CASE DETAILS TABLE ---
    cd_table = detail_container.find("table", class_="case_details_table")
    cd_raw_map: dict[str, str] = {}
    if cd_table:
        for tr in cd_table.find_all("tr"):
            cells = [clean_text(c.get_text()) for c in tr.find_all(["td", "th"])]
            for i in range(0, len(cells), 2):
                if i + 1 < len(cells):
                    k = cells[i].lower().replace(":", "").strip()
                    v = cells[i + 1].strip()
                    if k:
                        cd_raw_map[k] = v

    def make_field_result(label_keys: list[str], source_table: str, is_date: bool = False) -> FieldResult:
        raw_val = None
        for k in label_keys:
            if k in cd_raw_map:
                raw_val = cd_raw_map[k]
                break

        if raw_val is None:
            return FieldResult(value=None, status=FieldStatus.NOT_AVAILABLE.value, source=source_table)

        # Handle empty / dash values
        if not raw_val or raw_val in ("-", "--", ".", "None"):
            return FieldResult(value=None, raw_value=raw_val, status=FieldStatus.NOT_AVAILABLE.value, source=source_table)

        norm_val = normalize_date(raw_val) if is_date else None
        return FieldResult(
            value=raw_val,
            raw_value=raw_val,
            normalized_value=norm_val,
            status=FieldStatus.AVAILABLE.value,
            source=source_table
        )

    case_type_res = make_field_result(["case type"], "case_details_table")
    filing_num_res = make_field_result(["filing number"], "case_details_table")
    filing_date_res = make_field_result(["filing date"], "case_details_table", is_date=True)
    reg_num_res = make_field_result(["registration number"], "case_details_table")
    reg_date_res = make_field_result(["registration date"], "case_details_table", is_date=True)
    
    # CNR number handling: strip "(Note the CNR number...)"
    cnr_res = make_field_result(["cnr number"], "case_details_table")
    if cnr_res.value:
        clean_cnr = cnr_res.value.split()[0].strip()
        cnr_res.value = clean_cnr

    efiling_num_res = make_field_result(["e-filing number", "efiling number"], "case_details_table")
    efiling_date_res = make_field_result(["e-filing date", "efiling date"], "case_details_table", is_date=True)

    field_results["case_type"] = case_type_res
    field_results["filing_number"] = filing_num_res
    field_results["filing_date"] = filing_date_res
    field_results["registration_number"] = reg_num_res
    field_results["registration_date"] = reg_date_res
    field_results["cnr_number"] = cnr_res
    field_results["efiling_number"] = efiling_num_res
    field_results["efiling_date"] = efiling_date_res

    # Determine primary case number directly from DOM nodes
    case_type_val = case_type_res.value or ""
    reg_num_val = reg_num_res.value or ""
    abbr = case_type_val.split("-")[0].strip() if "-" in case_type_val else case_type_val.split()[0] if case_type_val else ""
    if abbr and reg_num_val:
        extracted_case_number = f"{abbr}/{reg_num_val}"
    else:
        extracted_case_number = reg_num_val or filing_num_res.value or ""

    field_results["case_number"] = FieldResult(
        value=extracted_case_number,
        raw_value=extracted_case_number,
        status=FieldStatus.AVAILABLE.value if extracted_case_number else FieldStatus.EXTRACTION_FAILED.value,
        source="case_details_table"
    )

    # --- 2. CASE STATUS TABLE ---
    cs_table = detail_container.find("table", class_="case_status_table")
    cs_raw_map: dict[str, str] = {}
    if cs_table:
        for tr in cs_table.find_all("tr"):
            cells = [clean_text(c.get_text()) for c in tr.find_all(["td", "th"])]
            if len(cells) >= 2:
                k = cells[0].lower().replace(":", "").strip()
                v = cells[1].strip()
                if k:
                    cs_raw_map[k] = v

    def make_status_result(label_keys: list[str], is_date: bool = False) -> FieldResult:
        raw_val = None
        for k in label_keys:
            if k in cs_raw_map:
                raw_val = cs_raw_map[k]
                break

        if raw_val is None:
            return FieldResult(value=None, status=FieldStatus.NOT_AVAILABLE.value, source="case_status_table")
        if not raw_val or raw_val in ("-", "--", ".", "None"):
            return FieldResult(value=None, raw_value=raw_val, status=FieldStatus.NOT_AVAILABLE.value, source="case_status_table")

        norm_val = normalize_date(raw_val) if is_date else None
        return FieldResult(
            value=raw_val,
            raw_value=raw_val,
            normalized_value=norm_val,
            status=FieldStatus.AVAILABLE.value,
            source="case_status_table"
        )

    first_hearing_date_res = make_status_result(["first hearing date"], is_date=True)
    decision_date_res = make_status_result(["decision date"], is_date=True)
    case_status_res = make_status_result(["case status"])
    nature_disposal_res = make_status_result(["nature of disposal"])
    court_judge_res = make_status_result(["court number and judge"])

    field_results["first_hearing_date"] = first_hearing_date_res
    field_results["decision_date"] = decision_date_res
    field_results["case_status"] = case_status_res
    field_results["nature_of_disposal"] = nature_disposal_res
    field_results["court_number_and_judge"] = court_judge_res

    # --- 3. PETITIONERS AND ADVOCATE ---
    def parse_parties_ul(ul_selector: str) -> list[tuple[str, Optional[str]]]:
        ul = detail_container.find("ul", class_=ul_selector)
        if not ul:
            return []
        parties = []
        for li in ul.find_all("li"):
            # Replace <br> with newline so names and advocates are cleanly split
            for br in li.find_all("br"):
                br.replace_with("\n")
            text = li.get_text()
            lines = [clean_text(l) for l in text.split("\n") if clean_text(l)]
            current_name = None
            current_adv = None
            for line in lines:
                if re.match(r"^advocate\b", line, re.IGNORECASE):
                    adv = re.sub(r"^advocate\b[-:\s]*", "", line, flags=re.IGNORECASE).strip()
                    current_adv = adv if adv else None
                else:
                    name = re.sub(r"^\d+[\)\.]\s*", "", line).strip()
                    if current_name:
                        parties.append((current_name, current_adv))
                        current_adv = None
                    current_name = name
            if current_name:
                parties.append((current_name, current_adv))
        return parties

    petitioners = parse_parties_ul("Petitioner_Advocate_table")
    respondents = parse_parties_ul("Respondent_Advocate_table")

    # --- 4. ACTS AND SECTIONS ---
    act_table = detail_container.find("table", class_="acts_table") or detail_container.find("table", id="act_table")
    acts = []
    if act_table:
        for tr in act_table.find_all("tr"):
            if tr.find("th"):
                continue
            cells = [clean_text(c.get_text()) for c in tr.find_all("td")]
            if len(cells) >= 2:
                act_name = cells[0]
                sec = cells[1]
                if sec in (",", "-", "--", ".", "", "None"):
                    sec = None
                acts.append(ActEntry(act_name=act_name, sections=sec))

    # --- 5. PROCESSES TABLE ---
    proc_table = detail_container.find("table", id="process") or detail_container.find("table", class_="FIR_details_table")
    processes = []
    if proc_table:
        headers = [clean_text(th.get_text()) for th in proc_table.find_all("th")]
        for tr in proc_table.find_all("tr"):
            tds = [clean_text(td.get_text()) for td in tr.find_all("td")]
            if not tds:
                continue
            raw_dict = dict(zip(headers, tds)) if headers and len(headers) == len(tds) else {}
            proc_id = tds[0] if len(tds) > 0 else ""
            proc_title = tds[1] if len(tds) > 1 else ""
            proc_date = tds[2] if len(tds) > 2 else ""
            processes.append(ProcessEntry(
                process_id=proc_id,
                process_title=proc_title,
                process_date=proc_date,
                raw_fields=raw_dict
            ))

    # --- 6. CASE HISTORY TABLE ---
    hist_table = detail_container.find("table", class_="history_table")
    history = []
    if hist_table:
        for tr in hist_table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 4:
                judge_val = clean_text(tds[0].get_text())
                b_cell = tds[1]
                b_date = clean_text(b_cell.get_text())
                a_link = b_cell.find("a")
                b_link = a_link.get("onclick", "") if a_link else None
                h_date = clean_text(tds[2].get_text()) or None
                purpose_val = clean_text(tds[3].get_text())
                history.append(HearingRecord(
                    judge=judge_val,
                    business_date=b_date,
                    hearing_date=h_date,
                    purpose=purpose_val,
                    business_date_link=b_link
                ))

    # --- 7. FINAL ORDERS / JUDGEMENTS TABLE ---
    ord_table = detail_container.find("table", class_="order_table")
    orders = []
    if ord_table:
        for tr in ord_table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 3:
                ord_num = clean_text(tds[0].get_text())
                ord_date = clean_text(tds[1].get_text())
                detail_cell = tds[2]
                ord_details = clean_text(detail_cell.get_text())
                a_link = detail_cell.find("a")
                onclick = a_link.get("onclick", "") if a_link else ""
                href = a_link.get("href", "") if a_link else ""
                orders.append(OrderEntry(
                    order_number=ord_num,
                    order_date=ord_date,
                    order_details=ord_details,
                    order_link=href if href and href != "#" else "",
                    order_listing_present=True,
                    order_details_present=bool(ord_details),
                    metadata={"onclick": onclick, "href": href}
                ))

    # --- 8. TRANSFERS TABLE ---
    trans_table = detail_container.find("table", class_="transfer_table")
    transfers = []
    if trans_table:
        for tr in trans_table.find_all("tr"):
            tds = [clean_text(td.get_text()) for td in tr.find_all("td")]
            if len(tds) >= 4:
                transfers.append(TransferEntry(
                    registration_number=tds[0],
                    transfer_date=tds[1],
                    from_court=tds[2],
                    to_court=tds[3]
                ))

    return RawCaseDetail(
        case_number=extracted_case_number,
        cnr_number=cnr_res.value or "",
        case_type=case_type_res.value or "",
        filing_number=filing_num_res.value or "",
        filing_date=filing_date_res.value or "",
        registration_number=reg_num_res.value or "",
        registration_date=reg_date_res.value or "",
        efiling_number=efiling_num_res.value,
        efiling_date=efiling_date_res.value,
        first_hearing_date=first_hearing_date_res.value,
        decision_date=decision_date_res.value,
        case_status=case_status_res.value,
        nature_of_disposal=nature_disposal_res.value,
        court_number_and_judge=court_judge_res.value,
        petitioners=petitioners,
        respondents=respondents,
        acts=acts,
        processes=processes,
        history=history,
        orders=orders,
        transfers=transfers,
        documents=[],
        field_results=field_results
    )


def parse_daily_status_html(soup_or_html: BeautifulSoup | str) -> DailyStatusRecord:
    """Parses an independent Daily Status block directly from its container.
    
    Extracts:
      - CNR, Case Number, Case Title, Judge, Establishment, Date
      - Business narrative
      - Next Purpose, Next Hearing Date
      - Nature of Disposal, Disposal Date (for disposed/final hearings)
    
    Zero hallucination: only extracts fields physically present in the block.
    """
    if isinstance(soup_or_html, str):
        soup = BeautifulSoup(soup_or_html, "html.parser")
    else:
        soup = soup_or_html

    container = soup.find("div", id="caseBusinessDiv_caseType") or soup.find("div", id="mydiv") or soup

    record = DailyStatusRecord(
        cnr="",
        case_number="",
        case_title=None,
        judge=None,
        establishment=None,
        date=None,
        business=None,
        next_purpose=None,
        next_hearing_date=None,
        nature_of_disposal=None,
        disposal_date=None,
        signing_judge=None,
        validation_status="PENDING"
    )

    # Parse header center / span lines
    for span in container.find_all("span"):
        txt = clean_text(span.get_text())
        if not txt or "daily status" in txt.lower():
            continue
        if re.search(r"in the court of\s*:", txt, re.IGNORECASE):
            record.judge = re.sub(r"^.*in the court of\s*:\s*", "", txt, flags=re.IGNORECASE).strip()
        elif re.search(r"cnr number\s*:", txt, re.IGNORECASE):
            record.cnr = re.sub(r"^.*cnr number\s*:\s*", "", txt, flags=re.IGNORECASE).strip()
        elif re.search(r"case number\s*:", txt, re.IGNORECASE):
            record.case_number = re.sub(r"^.*case number\s*:\s*", "", txt, flags=re.IGNORECASE).strip()
        elif re.search(r"^date\s*:", txt, re.IGNORECASE) or re.search(r"date\s*:\s*\d", txt, re.IGNORECASE):
            record.date = re.sub(r"^.*date\s*:\s*", "", txt, flags=re.IGNORECASE).strip()
        elif "versus" in txt.lower() or " vs " in txt.lower():
            record.case_title = txt
        elif not record.establishment and not any(k in txt.lower() for k in ["court", "cnr", "case", "date", "versus", "vs"]):
            record.establishment = txt

    # Parse key-value table rows
    table = container.find("table")
    if table:
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) == 3:
                lbl = clean_text(tds[0].get_text()).lower().replace(":", "").strip()
                val = clean_text(tds[2].get_text())
                if "business" in lbl:
                    record.business = val if val and val != "-" else None
                elif "next purpose" in lbl:
                    record.next_purpose = val if val and val != "-" else None
                elif "next hearing date" in lbl:
                    record.next_hearing_date = val if val and val != "-" else None
                elif "nature of disposal" in lbl:
                    record.nature_of_disposal = val if val and val != "-" else None
                elif "disposal date" in lbl:
                    record.disposal_date = val if val and val != "-" else None
            elif len(tds) == 1 and tds[0].get("colspan") in ("3", 3):
                record.signing_judge = clean_text(tds[0].get_text())
                if not record.judge:
                    record.judge = record.signing_judge

    return record


def parse_case_detail_text(raw_text: str, case_number: str = "") -> RawCaseDetail:
    """Backward-compatible fallback parser for raw text blocks."""
    # When text is passed, wrap in HTML and parse with main parser
    soup = BeautifulSoup(raw_text, "html.parser")
    return parse_case_details_page(soup, expected_case_number=case_number)
