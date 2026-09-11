"""Stateful browser-based scraping workflows on the eCourts website.

Coordinates results list extraction directly from the live DOM using Playwright locators.
"""
from __future__ import annotations
import logging
from playwright.sync_api import Page
from ecourts_scraper.models import CaseSummary

logger = logging.getLogger("ecourts_scraper")

def extract_search_results(page: Page) -> list[CaseSummary]:
    """Extracts search results case summaries directly from the browser DOM using Playwright.

    Args:
        page: Playwright Page instance.

    Returns:
        List of CaseSummary models.
    """
    logger.info("Extracting search results case summaries directly from browser DOM...")
    
    # We evaluate JS to locate the table based on text content and parse its rows
    js_extract = """() => {
        const tables = Array.from(document.querySelectorAll("table"));
        let table = null;
        for (const t of tables) {
            if (t.innerText.includes("Petitioner Name versus Respondent Name") || 
                t.innerText.includes("Case Type/Case Number/Case Year")) {
                table = t;
                break;
            }
        }
        if (!table) return null;
        
        const rows = Array.from(table.rows);
        const results = [];
        let viewIndex = 0;
        
        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const cells = Array.from(row.cells);
            
            // Skip header (th) rows
            if (row.querySelector("th")) continue;
            
            // Skip rows with cells that have colspan > 1 (e.g. group establishment headers)
            if (cells.some(c => c.colSpan > 1)) continue;
            
            // Skip rows with insufficient columns
            if (cells.length < 3) continue;
            
            const srNo = cells[0].innerText.trim();
            if (!/^\\d+$/.test(srNo)) continue;
            
            const caseNumber = cells[1].innerText.trim();
            const parties = cells[2].innerText.trim();
            
            results.push({
                serial_number: srNo,
                case_number: caseNumber,
                parties: parties,
                view_index: viewIndex
            });
            viewIndex++;
        }
        return results;
    }"""
    
    logger.info("Table selector checked: table:has-text('Petitioner Name versus Respondent Name')")
    results_data = page.evaluate(js_extract)
    if results_data is None:
        logger.error("Results table containing expected headers not found in browser DOM.")
        return []
        
    summaries = []
    for item in results_data:
        case_number = item["case_number"]
        case_id_parts = case_number.split("/")
        if len(case_id_parts) == 3:
            case_type_code, case_seq, case_year = case_id_parts
        else:
            case_type_code, case_seq, case_year = "", "", ""
            
        summary = CaseSummary(
            serial_number=item["serial_number"],
            case_number=case_number,
            parties=item["parties"],
            view_index=item["view_index"],
            case_type_code=case_type_code,
            case_seq=case_seq,
            case_year=case_year
        )
        summaries.append(summary)
        
    logger.info(f"Number of rows found: {len(summaries)}")
    if summaries:
        logger.info(f"First extracted case: Serial {summaries[0].serial_number}, Case Number {summaries[0].case_number}")
        
    return summaries
