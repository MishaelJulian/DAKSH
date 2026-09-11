"""Pure text and value parsing functions.

Responsible for string splitting, cleaning, and mapping raw text data into models,
completely independent of external HTML parsing libraries.
"""
from __future__ import annotations
import logging
import re
from ecourts_scraper.models import CaseDetail

logger = logging.getLogger("ecourts_scraper")

def parse_party_lines(lines: list[str]) -> list[tuple[str, Optional[str]]]:
    """Helper to parse party names and advocates sequentially from raw lines."""
    parties = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if it is an advocate line
        adv_match = re.match(r'^(?:Advocate)\b[-:\s]*(.*)$', line, re.IGNORECASE)
        if adv_match:
            adv_name = adv_match.group(1).strip()
            # Clean leading dashes, colons, spaces
            adv_name = re.sub(r'^[-:\s]+', '', adv_name)
            if parties:
                parties[-1] = (parties[-1][0], adv_name)
            continue
            
        # Check if it starts with numbering like "1) " or "1. "
        num_match = re.match(r'^\d+[\)\.]\s*(.*)$', line)
        if num_match:
            party_name = num_match.group(1).strip()
            parties.append((party_name, None))
        else:
            # Treat as party name directly
            parties.append((line, None))
            
    return parties

def parse_case_detail_text(raw_text: str, case_number: str = "") -> CaseDetail:
    """Parses verbatim raw text blocks from DOM extraction into a CaseDetail object.

    Uses state-based transition to cleanly isolate case details and status from 
    dynamic Repeatable Table sections.

    Args:
        raw_text: Verbatim raw text blocks from DOM extraction.
        case_number: Target case identifier fallback.

    Returns:
        CaseDetail structure.
    """
    lines = [line.strip() for line in raw_text.splitlines()]
    
    label_value_map = {}
    petitioners_lines = []
    respondents_lines = []
    
    current_section = None
    
    section_headers = {
        "petitioner and advocate": "PETITIONER",
        "respondent and advocate": "RESPONDENT",
        "acts": "OTHER",
        "case history": "OTHER",
        "processes": "OTHER",
        "history of case hearing": "OTHER",
        "case status": "OTHER",
        "final orders / judgements": "OTHER",
        "transfer details": "OTHER"
    }
    
    for line in lines:
        if not line:
            continue
        
        line_lower = line.lower().strip()
        matched_section = None
        for header, sec in section_headers.items():
            if header in line_lower:
                matched_section = sec
                break
                
        if matched_section:
            current_section = matched_section
            continue
            
        if current_section == "PETITIONER":
            petitioners_lines.append(line)
        elif current_section == "RESPONDENT":
            respondents_lines.append(line)
        elif current_section is None:
            # ONLY parse normal label-value lines BEFORE any sections start
            parts = [p.strip() for p in line.split("\t") if p.strip()]
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    lbl = parts[i].replace(":", "").strip()
                    val = parts[i+1].strip()
                    label_value_map[lbl.lower()] = val

    # Extract raw fields
    case_type = label_value_map.get("case type", "")
    filing_number = label_value_map.get("filing number", "")
    registration_number = label_value_map.get("registration number", "")
    
    # Reconstruct case_number from Case Type and Registration Number
    reconstructed_case_number = ""
    if case_type:
        abbr = re.split(r'\s*-\s*', case_type)[0].strip()
        if abbr and registration_number:
            reconstructed_case_number = f"{abbr}/{registration_number}"
            
    if not reconstructed_case_number:
        reconstructed_case_number = registration_number or filing_number or case_number

    raw_cnr = label_value_map.get("cnr number", "")
    cnr_number = raw_cnr.split()[0] if raw_cnr else ""
    
    petitioners = parse_party_lines(petitioners_lines)
    respondents = parse_party_lines(respondents_lines)
    
    return CaseDetail(
        case_number=reconstructed_case_number,
        cnr_number=cnr_number,
        case_type=case_type,
        filing_number=filing_number,
        filing_date=label_value_map.get("filing date", ""),
        registration_number=registration_number,
        registration_date=label_value_map.get("registration date", ""),
        cnr_link=None,
        efiling_number=label_value_map.get("e-filing number", None),
        efiling_date=label_value_map.get("e-filing date", None),
        first_hearing_date=label_value_map.get("first hearing date", None),
        decision_date=label_value_map.get("decision date", None),
        case_status=label_value_map.get("case status", None),
        nature_of_disposal=label_value_map.get("nature of disposal", None),
        court_number_and_judge=label_value_map.get("court number and judge", None),
        petitioners=petitioners,
        respondents=respondents,
        acts=[],
        processes=[],
        history=[],
        orders=[],
        transfers=[],
        extra_fields={}
    )
