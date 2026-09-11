"""Transformation layer mapping raw extracted data to the canonical spreadsheet schema.

Ensures separation of concerns between raw extraction models and downstream output structures.
"""
from __future__ import annotations
from ecourts_scraper.models import RawCaseDetail, CaseSummary, CanonicalCaseRow

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

def parse_date_str(date_str: str) -> Optional[datetime]:
    """Helper to parse eCourts dates in 'DD-MM-YYYY' or 'DDth Month YYYY' formats."""
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = date_str.strip()
    
    # 1. Format: DD-MM-YYYY
    if re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', date_str):
        try:
            return datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            pass
            
    # 2. Format: DDth Month YYYY (e.g. '05th February 2011', '17th March 2021')
    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    for fmt in ("%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            pass
            
    return None

def normalize_case_number(case_number: str) -> str:
    """Normalizes case number for canonical comparison."""
    if not case_number:
        return ""
    cleaned = re.sub(r'[^a-zA-Z0-9/]', '', case_number).upper()
    return cleaned

def clean_and_format_date(date_str: str) -> str:
    """Standardizes date strings to DD-MM-YYYY format, returning empty string if invalid."""
    dt = parse_date_str(date_str)
    if dt:
        return dt.strftime("%d-%m-%Y")
    return ""

def raw_to_canonical(
    raw: RawCaseDetail,
    summary: CaseSummary,
    scraped_at: str,
    source_file_name: str
) -> dict[str, Any]:
    """Translates RawCaseDetail and metadata into a flattened dictionary matching Sample Fields.xlsx."""
    
    # Standardize dates to DD-MM-YYYY without hallucinating fallbacks
    decision_date_str = raw.decision_date or ""
    filing_date_std = clean_and_format_date(raw.filing_date) or raw.filing_date or ""
    first_hearing_date_std = clean_and_format_date(raw.first_hearing_date) or raw.first_hearing_date or ""
    decision_date_std = clean_and_format_date(decision_date_str) or decision_date_str or ""
    
    # 2. Get last hearing info and clean dates
    last_hearing_date = ""
    next_hearing_date = ""
    if raw.history:
        last_hearing_date = raw.history[-1].business_date or ""
        next_hearing_date = raw.history[-1].hearing_date or ""
        
    last_hearing_date_std = clean_and_format_date(last_hearing_date) or last_hearing_date or ""
    next_hearing_date_std = clean_and_format_date(next_hearing_date) or next_hearing_date or ""

    # 3. Calculate duration days
    filing_dt = parse_date_str(filing_date_std)
    decision_dt = parse_date_str(decision_date_std)
    first_hearing_dt = parse_date_str(first_hearing_date_std)
    
    case_duration_days = ""
    if filing_dt and decision_dt:
        case_duration_days = str((decision_dt - filing_dt).days)
        
    filing_to_first_hearing_days = ""
    if filing_dt and first_hearing_dt:
        filing_to_first_hearing_days = str((first_hearing_dt - filing_dt).days)

    # 4. Format list fields as semicolon-separated strings (no raw python lists or JSON strings)
    appellant_list = [p[0] for p in raw.petitioners] if raw.petitioners else []
    respondent_list = [r[0] for r in raw.respondents] if raw.respondents else []
    
    petitioner_advs = list(set([p[1] for p in raw.petitioners if p[1]]))
    respondent_advs = list(set([r[1] for r in raw.respondents if r[1]]))
    
    appellant_str = "; ".join(appellant_list) if appellant_list else ""
    respondent_str = "; ".join(respondent_list) if respondent_list else ""
    petitioner_advs_str = "; ".join(petitioner_advs) if petitioner_advs else ""
    respondent_advs_str = "; ".join(respondent_advs) if respondent_advs else ""
    
    # Format sections
    sec_parts = []
    for a in raw.acts:
        act = a.act_name.strip()
        sec = a.sections.strip()
        if act and sec:
            sec_parts.append(f"{act} Section {sec}")
        elif act:
            sec_parts.append(act)
        elif sec:
            sec_parts.append(f"Section {sec}")
    sections_str = "; ".join(sec_parts) if sec_parts else ""

    # Parse judges - preserve full text with court room code prefixes
    judges_set = set()
    if raw.court_number_and_judge:
        judges_set.add(raw.court_number_and_judge.strip())
        
    for h in raw.history:
        if h.judge:
            judges_set.add(h.judge.strip())
    judges_list = list(judges_set)
    judges_str = "; ".join(judges_list) if judges_list else ""

    # Extract CNR components
    cnr = raw.cnr_number or ""
    cnr_court_code = cnr[:6] if len(cnr) >= 6 else ""
    
    # Year
    cnr_year = ""
    if summary.case_year:
        cnr_year = summary.case_year
    elif filing_dt:
        cnr_year = str(filing_dt.year)
    elif len(cnr) >= 4:
        cnr_year = cnr[-4:]

    # Type Code
    type_code = ""
    if "/" in raw.case_number:
        type_code = raw.case_number.split("/")[0]

    # Resolve Court room name fallback
    court_name_val = raw.court_number_and_judge or ""
    if not court_name_val and judges_list:
        court_name_val = judges_list[0]

    # Resolve Case Status defaults
    case_status_val = raw.case_status or "Disposed"

    # Order details formatting
    order_types_str = "; ".join([o.order_number for o in raw.orders]) if raw.orders else ""
    order_dates_str = "; ".join([clean_and_format_date(o.order_date) or o.order_date for o in raw.orders]) if raw.orders else ""
    order_source_urls_str = "; ".join([o.order_link for o in raw.orders]) if raw.orders else ""
    order_filenames_str = "; ".join([Path(o.order_link).name for o in raw.orders if o.order_link]) if raw.orders else ""

    # Extended Level 9 Order Fields and serializations
    orders_data = []
    business_list = []
    nature_of_disposal_list = []
    disposal_dates_list = []
    order_text_list = []
    all_doc_names = []
    
    # Layer counters (spec §10, §24)
    order_page_count = 0
    order_text_count = 0
    document_link_count = 0
    
    for o in raw.orders:
        docs_list = o.metadata.get("documents", []) if o.metadata else []
        for doc in docs_list:
            if doc.get("filename"):
                all_doc_names.append(doc["filename"])
                
        # Track layer flags
        if getattr(o, 'order_page_found', None) is True:
            order_page_count += 1
        if getattr(o, 'order_text_found', None) is True:
            order_text_count += 1
        if getattr(o, 'document_link_found', None) is True:
            document_link_count += 1
                
        orders_data.append({
            "order_number": o.order_number,
            "order_date": o.order_date,
            "order_link": o.order_link,
            "business": o.business or "",
            "nature_of_disposal": o.nature_of_disposal or "",
            "disposal_date": o.disposal_date or "",
            "judge": o.metadata.get("judge", "") if o.metadata else "",
            "full_order_text": o.order_text or "",
            "documents": docs_list,
            # Layer tracking flags (spec §10)
            "order_page_found": getattr(o, 'order_page_found', None),
            "order_text_found": getattr(o, 'order_text_found', None),
            "document_link_found": getattr(o, 'document_link_found', None),
            "document_url": getattr(o, 'document_url', None),
        })
        if o.business:
            business_list.append(o.business.strip())
        if o.nature_of_disposal:
            nature_of_disposal_list.append(o.nature_of_disposal.strip())
        if o.disposal_date:
            disposal_dates_list.append(o.disposal_date.strip())
        if o.order_text:
            order_text_list.append(o.order_text.strip())
            
    orders_json_str = json.dumps(orders_data)
    business_str = "; ".join(business_list)
    nature_of_disposal_str = "; ".join(nature_of_disposal_list)
    disposal_date_str = "; ".join(disposal_dates_list)
    order_text_combined = "\n\n--- NEXT ORDER ---\n\n".join(order_text_list)
    doc_names_str = "; ".join(all_doc_names)

    # Reconstruct extra_fields dictionary
    extra_fields = dict(raw.extra_fields)
    if raw.history:
        extra_fields["history"] = [
            {
                "judge": h.judge,
                "business_date": h.business_date,
                "hearing_date": h.hearing_date,
                "purpose": h.purpose,
                "purpose_of_hearing": h.purpose,
                "business_date_link": h.business_date_link
            }
            for h in raw.history
        ]
    if raw.processes:
        extra_fields["processes"] = [
            {
                "process_id": p.process_id,
                "process_title": p.process_title,
                "process_date": p.process_date
            }
            for p in raw.processes
        ]
    if raw.transfers:
        extra_fields["transfers"] = [
            {
                "registration_number": t.registration_number,
                "transfer_date": t.transfer_date,
                "from_court": t.from_court,
                "to_court": t.to_court
            }
            for t in raw.transfers
        ]

    # Purpose of Hearing: collect unique purposes from history
    purposes = []
    for h in raw.history:
        if h.purpose and h.purpose not in purposes:
            purposes.append(h.purpose)
    purpose_of_hearing_str = "; ".join(purposes) if purposes else ""

    # Sub Stage
    sub_stage_str = raw.sub_stage or ""

    # Daily Status
    daily_status_str = raw.daily_status_text or ""

    # e-Filing fields
    efiling_number_str = raw.efiling_number or ""
    efiling_date_str = raw.efiling_date or ""

    # Map directly to Sample Fields template
    record = {
        "cnr": cnr,
        "cnr_court_code": cnr_court_code,
        "bench_code": "",
        "type_code": type_code,
        "cnr_case_number": raw.registration_number or "",
        "cnr_year": cnr_year,
        "appeal_type": "",
        "case_type_label": raw.case_type or "",
        "case_number": raw.case_number or "",
        "appeal_number_raw": "",
        "case_title": summary.parties or "",
        "appellant": appellant_str,
        "respondent": respondent_str,
        "bench_name": "",
        "bench_alloted": "",
        "bench_city": "BENGALURU",
        "bench_state": "Karnataka",
        "court_name": court_name_val,
        "assessment_year": "",
        "case_status": case_status_val,
        "case_status_raw": case_status_val,
        "filing_date": filing_date_std,
        "first_hearing_date": first_hearing_date_std,
        "last_hearing_date": last_hearing_date_std,
        "next_hearing_date": next_hearing_date_std,
        "decision_date": decision_date_std,
        "result": raw.nature_of_disposal or "",
        "judges": judges_str,
        "petitioner_advocates": petitioner_advs_str,
        "respondent_advocates": respondent_advs_str,
        "sections": sections_str,
        "case_category": "",
        "case_duration_days": case_duration_days,
        "filing_to_first_hearing_days": filing_to_first_hearing_days,
        "has_orders": "1" if raw.orders else "0",
        "order_count": str(len(raw.orders)) if raw.orders else "0",
        "hearing_count": str(len(raw.history)) if raw.history else "0",
        "order_types": order_types_str,
        "order_dates": order_dates_str,
        "order_results": "",
        "order_source_urls": order_source_urls_str,
        "order_master_filenames": order_filenames_str,
        "scraped_at": scraped_at,
        "source_file": source_file_name,
        
        # New Level 9 fields
        "business": business_str,
        "business_text": order_text_combined,
        "nature_of_disposal": nature_of_disposal_str,
        "disposal_date": disposal_date_str or decision_date_std,
        "order_text": order_text_combined,
        "order_source_urls": order_source_urls_str,
        "order_document_names": doc_names_str,
        "orders_json": orders_json_str,
        
        # Production fields
        "purpose_of_hearing": purpose_of_hearing_str,
        "sub_stage": sub_stage_str,
        "daily_status_text": daily_status_str,
        "efiling_number": efiling_number_str,
        "efiling_date": efiling_date_str,

        "extra_metadata": json.dumps(extra_fields) if extra_fields else "",
        
        # Layer counts (spec §10, §24) — independent metrics
        "order_page_count": str(order_page_count),
        "order_text_count": str(order_text_count),
        "document_link_count": str(document_link_count),
        
        # Explicit counts for one-to-many tables (spec §11, §7)
        "process_count": str(len(raw.processes)) if raw.processes else "0",
        "transfer_count": str(len(raw.transfers)) if raw.transfers else "0",
    }
    
    return record
