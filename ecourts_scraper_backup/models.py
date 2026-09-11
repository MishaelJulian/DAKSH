"""Dataclass definitions representing the raw and canonical schemas of extracted case data.

Supports structured validation and clean separation between raw scraping structures
and final normalized canonical row exports.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CaseSummary:
    """Represents a summary row in the search results list table."""
    serial_number: str
    case_number: str
    parties: str
    view_index: int
    case_type_code: str
    case_seq: str
    case_year: str

@dataclass
class ActEntry:
    """Represents an Act and its associated sections."""
    act_name: str
    sections: str

@dataclass
class ProcessEntry:
    """Represents a process served/issued in the case."""
    process_id: str
    process_title: str
    process_date: str

@dataclass
class HearingRecord:
    """Represents a single entry in the case history."""
    judge: str
    business_date: str
    hearing_date: str
    purpose: str
    business_date_link: Optional[str] = None

@dataclass
class OrderEntry:
    """Represents an order or judgment linked in the case details."""
    order_number: str
    order_date: str
    order_link: str
    local_path: Optional[str] = None
    
    # Extended business/order detail fields
    business: Optional[str] = None
    nature_of_disposal: Optional[str] = None
    disposal_date: Optional[str] = None
    order_text: Optional[str] = None
    metadata: Optional[dict] = None
    
    # Order layer tracking (spec §10, §24)
    order_page_found: Optional[bool] = None    # Layer B: was the order/business page opened?
    order_text_found: Optional[bool] = None    # Layer C: was order text successfully extracted?
    document_link_found: Optional[bool] = None # Layer D: was a downloadable PDF link exposed?
    document_url: Optional[str] = None         # Layer D: the actual document URL if found


@dataclass
class TransferEntry:
    """Represents historical transfer details of the case."""
    registration_number: str
    transfer_date: str
    from_court: str
    to_court: str

@dataclass
class RawCaseDetail:
    """Represents the complete raw case detail page exactly as parsed."""
    case_number: str
    cnr_number: str
    case_type: str
    filing_number: str
    filing_date: str
    registration_number: str
    registration_date: str
    
    cnr_link: Optional[str] = None
    efiling_number: Optional[str] = None
    efiling_date: Optional[str] = None
    
    # Case Status Section
    first_hearing_date: Optional[str] = None
    decision_date: Optional[str] = None
    case_status: Optional[str] = None
    nature_of_disposal: Optional[str] = None
    sub_stage: Optional[str] = None
    court_number_and_judge: Optional[str] = None
    daily_status_text: Optional[str] = None
    
    # Party Subsections
    petitioners: list[tuple[str, Optional[str]]] = field(default_factory=list) # List of (Name, Advocate)
    respondents: list[tuple[str, Optional[str]]] = field(default_factory=list) # List of (Name, Advocate)
    
    # Repeatable Subtables
    acts: list[ActEntry] = field(default_factory=list)
    processes: list[ProcessEntry] = field(default_factory=list)
    history: list[HearingRecord] = field(default_factory=list)
    orders: list[OrderEntry] = field(default_factory=list)
    transfers: list[TransferEntry] = field(default_factory=list)
    
    # Fallback container for unmatched values
    extra_fields: dict[str, str] = field(default_factory=dict)

    def __getitem__(self, key: str):
        if key == "petitioner":
            return self.petitioners[0][0] if self.petitioners else ""
        if key == "respondent":
            return self.respondents[0][0] if self.respondents else ""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

# Alias CaseDetail to RawCaseDetail to support parser and exporter imports
CaseDetail = RawCaseDetail

@dataclass
class CanonicalCaseRow:
    """Represents a flat row mapping exactly to Sample_Fields.xlsx schema."""
    cnr: str
    cnr_court_code: str
    bench_code: str
    type_code: str
    cnr_case_number: str
    cnr_year: str
    appeal_type: str
    case_type_label: str
    case_number: str
    appeal_number_raw: str
    case_title: str
    appellant: str
    respondent: str
    bench_name: str
    bench_alloted: str
    bench_city: str
    bench_state: str
    court_name: str
    assessment_year: str
    case_status: str
    case_status_raw: str
    filing_date: str
    first_hearing_date: str
    last_hearing_date: str
    next_hearing_date: str
    decision_date: str
    result: str
    judges: str
    petitioner_advocates: str
    respondent_advocates: str
    sections: str
    case_category: str
    case_duration_days: Optional[int]
    filing_to_first_hearing_days: Optional[int]
    has_orders: int
    order_count: int
    hearing_count: int
    order_types: str
    order_dates: str
    order_results: str
    order_source_urls: str
    order_master_filenames: str
    scraped_at: str
    source_file: str
    # Production fields
    purpose_of_hearing: str = ""
    sub_stage: str = ""
    daily_status_text: str = ""
    efiling_number: str = ""
    efiling_date: str = ""
    extra_metadata: str = ""
