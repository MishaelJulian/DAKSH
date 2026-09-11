"""Dataclass definitions representing the raw and canonical schemas of extracted case data.

Supports structured validation, field-level extraction provenance, and strict
distinction between AVAILABLE, NOT_AVAILABLE, EXTRACTION_FAILED, and SESSION_ERROR.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Any


class FieldStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    SESSION_ERROR = "SESSION_ERROR"


@dataclass
class FieldResult:
    """Represents a single extracted field with value, status, and provenance."""
    value: Any = None
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    status: str = FieldStatus.AVAILABLE.value
    source: str = ""
    selector: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = {
            "value": self.value,
            "status": self.status
        }
        if self.raw_value is not None:
            d["raw_value"] = self.raw_value
        if self.normalized_value is not None:
            d["normalized_value"] = self.normalized_value
        if self.source:
            d["source"] = self.source
        if self.selector:
            d["selector"] = self.selector
        return d


@dataclass
class CaseSummary:
    """Represents a summary row in the search results list table."""
    serial_number: str
    case_number: str
    parties: str
    view_index: int
    case_type_code: str = ""
    case_seq: str = ""
    case_year: str = ""
    onclick: str = ""
    cnr_from_link: Optional[str] = None


@dataclass
class CaseIdentity:
    """Identity check container for cross-case validation."""
    case_number: str
    cnr: str
    case_title: str
    expected_case_number: Optional[str] = None
    expected_cnr: Optional[str] = None
    expected_case_title: Optional[str] = None
    identity_validated: bool = False


@dataclass
class PartyEntry:
    """Represents a party (petitioner or respondent) with their advocate."""
    name: str
    advocate: Optional[str] = None


@dataclass
class ActEntry:
    """Represents an Act and its associated sections."""
    act_name: str
    sections: Optional[str] = None


@dataclass
class ProcessEntry:
    """Represents a process served/issued in the case."""
    process_id: str
    process_title: str
    process_date: str
    raw_fields: dict[str, str] = field(default_factory=dict)


@dataclass
class HearingRecord:
    """Represents a single entry in the case history."""
    judge: str
    business_date: str
    hearing_date: Optional[str] = None
    purpose: str = ""
    business_date_link: Optional[str] = None


@dataclass
class DailyStatusRecord:
    """Represents an independent Daily Status block for a hearing."""
    cnr: str
    case_number: str
    case_title: Optional[str] = None
    judge: Optional[str] = None
    establishment: Optional[str] = None
    date: Optional[str] = None
    business: Optional[str] = None
    next_purpose: Optional[str] = None
    next_hearing_date: Optional[str] = None
    nature_of_disposal: Optional[str] = None
    disposal_date: Optional[str] = None
    signing_judge: Optional[str] = None
    validation_status: str = "VALIDATED"


@dataclass
class OrderEntry:
    """Represents an order or judgment entry."""
    order_number: str
    order_date: str
    order_details: str = ""
    order_link: str = ""
    local_path: Optional[str] = None
    
    # Granular order concepts (Requirement §22)
    order_listing_present: bool = True
    order_details_present: bool = False
    order_page_url: Optional[str] = None
    order_pdf_available: bool = False
    order_pdf_url: Optional[str] = None
    order_text: Optional[str] = None
    
    # Extended business/order detail fields
    business: Optional[str] = None
    nature_of_disposal: Optional[str] = None
    disposal_date: Optional[str] = None
    metadata: Optional[dict] = None
    
    # Order layer tracking
    order_page_found: Optional[bool] = None
    order_text_found: Optional[bool] = None
    document_link_found: Optional[bool] = None
    document_url: Optional[str] = None


@dataclass
class DocumentEntry:
    """Represents a case document."""
    document_name: str
    document_date: Optional[str] = None
    document_type: Optional[str] = None
    document_url: Optional[str] = None
    document_status: Optional[str] = None


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
    petitioners: list[tuple[str, Optional[str]]] = field(default_factory=list)
    respondents: list[tuple[str, Optional[str]]] = field(default_factory=list)
    
    # Repeatable Subtables
    acts: list[ActEntry] = field(default_factory=list)
    processes: list[ProcessEntry] = field(default_factory=list)
    history: list[HearingRecord] = field(default_factory=list)
    daily_status: list[DailyStatusRecord] = field(default_factory=list)
    orders: list[OrderEntry] = field(default_factory=list)
    documents: list[DocumentEntry] = field(default_factory=list)
    transfers: list[TransferEntry] = field(default_factory=list)
    
    # Field-level status tracking
    field_results: dict[str, FieldResult] = field(default_factory=dict)
    
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
    purpose_of_hearing: str = ""
    sub_stage: str = ""
    daily_status_text: str = ""
    efiling_number: str = ""
    efiling_date: str = ""
    extra_metadata: str = ""
