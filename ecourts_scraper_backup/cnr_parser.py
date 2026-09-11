"""Parser for India's 16-character National Judicial Data Grid (NJDG) CNR format.

Responsible for decomposing the CNR identifier into state code, court complex code,
case sequence, and case year.
"""
from __future__ import annotations

def parse_cnr(cnr_str: str) -> dict[str, str]:
    """Decomposes a 16-character CNR number into its component parts.

    Format details:
    - Characters 0-1: State Code (e.g. KA)
    - Characters 2-5: Court Complex Code (e.g. BC01)
    - Characters 6-11: Running Sequence (e.g. 006963)
    - Characters 12-15: Case Year (e.g. 2010)

    Args:
        cnr_str: Verbatim CNR string.

    Returns:
        Dictionary containing state_code, court_code, bench_code, sequence, and year.
    """
    # Stub for Phase 7 implementation
    return {}
