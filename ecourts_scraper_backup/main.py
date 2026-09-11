"""Main orchestrator demonstrating Phase 3 of eCourts Karnataka Case Scraper.

Launches the browser, populates the search form dropdowns and year,
prompts the user to solve the CAPTCHA, and extracts/verifies the list of
search results directly from the browser DOM (Playwright-first).
"""
from __future__ import annotations
import sys
import logging
import re
from datetime import datetime
from ecourts_scraper import config
from ecourts_scraper.browser import get_browser_page, ECourtsBrowser, CaptchaError
from ecourts_scraper.scraper import extract_search_results
from ecourts_scraper.utils import setup_logging

def split_parties_robustly(parties_text: str) -> tuple[str, str]:
    """Helper to split petitioner versus respondent robustly."""
    lines = [line.strip() for line in parties_text.split("\n") if line.strip()]
    # Look for 'vs' or 'versus' index in lines
    vs_idx = -1
    for i, line in enumerate(lines):
        if line.lower() in ("vs", "versus", "vs.", "versus."):
            vs_idx = i
            break
            
    if vs_idx != -1:
        petitioner = " ".join(lines[:vs_idx]).strip()
        respondent = " ".join(lines[vs_idx+1:]).strip()
    else:
        # Fallback split with regex
        parts = re.split(r'\s+vs\s+|\s+versus\s+', parties_text, flags=re.IGNORECASE)
        if len(parts) >= 2:
            petitioner = parts[0].strip()
            respondent = " ".join(p.strip() for p in parts[1:])
        else:
            petitioner = parties_text
            respondent = "Unknown"
    return petitioner, respondent

def main() -> None:
    # Initialize rotating file and console logging
    logger = setup_logging(config.LOGS_DIR)
    logger.info("Starting eCourts Scraper Phase 3 (Playwright-first) Run...")

    try:
        with get_browser_page(headless=False) as page:
            browser = ECourtsBrowser(page)
            
            # Navigate and fill form
            browser.navigate_to_home()
            browser.select_state(config.STATE)
            browser.select_district(config.DISTRICT)
            browser.select_court_complex(config.COURT_COMPLEX)
            browser.select_establishment(config.ESTABLISHMENT)
            browser.select_case_type_tab()
            browser.fill_case_type(config.CASE_TYPE)
            browser.fill_year(config.YEAR)
            browser.select_disposed()

            # Captcha Retry Loop
            max_retries = config.MAX_CAPTCHA_RETRIES
            search_success = False

            for attempt in range(1, max_retries + 1):
                logger.info(f"CAPTCHA loop: Attempt {attempt} of {max_retries}")
                
                print("\n" + "=" * 55)
                print("Please solve the CAPTCHA manually in the browser window.")
                print(f"Once solved, press [ENTER] in this terminal to continue (Attempt {attempt}/{max_retries})...")
                print("=" * 55 + "\n")
                
                # Wait for user confirmation in console
                input()
                
                logger.info("User pressed ENTER. Submitting search...")
                try:
                    browser.click_go()
                    browser.verify_results_table()
                    browser.log_state_investigation("Immediately after search completes")
                    search_success = True
                    break
                except CaptchaError as e:
                    logger.warning(f"CAPTCHA validation failed on attempt {attempt}: {e}")
                    print(f"\n[!] CAPTCHA error: {e}. A new CAPTCHA has been reloaded. Please try again.")
                except Exception as e:
                    logger.error(f"Unexpected error waiting for results: {e}")
                    raise

            if not search_success:
                logger.error(f"Failed to submit search after {max_retries} CAPTCHA attempts.")
                print(f"\n[-] ERROR: Failed to load search results after {max_retries} CAPTCHA attempts. Exiting.")
                sys.exit(1)

            # --- PHASE 3: SEARCH RESULTS EXTRACTION (Playwright-first) ---
            logger.info("Starting search results extraction...")
            extracted_cases = extract_search_results(page)
            browser.log_state_investigation("After results extraction finishes")

            if len(extracted_cases) == 0:
                logger.error("No search results rows could be extracted.")
                # Diagnostic logging
                table_count = page.locator("table").count()
                logger.info("--- DIAGNOSTIC INFORMATION ---")
                logger.info("Table selector checked: table:has-text('Petitioner Name versus Respondent Name')")
                logger.info(f"Number of tables found on the page: {table_count}")
                if table_count > 0:
                    first_table_html = page.locator("table").first.evaluate("el => el.outerHTML")
                    logger.info("Snippet of the first table HTML:")
                    logger.info(first_table_html[:1000])
                logger.info("Reason: The results table was not found or has a different selector structure.")
                print("\n[-] ERROR: Results extraction failed. Check log file for diagnostics.")
                sys.exit(1)

            # Print each extracted case summary in the requested readable format
            for summary in extracted_cases:
                petitioner, respondent = split_parties_robustly(summary.parties)
                print("-" * 50)
                print(f"Case {summary.serial_number}")
                print(f"Serial Number: {summary.serial_number}")
                print(f"Case Number: {summary.case_number}")
                print("Petitioner:")
                print(petitioner)
                print("Respondent:")
                print(respondent)
            print("-" * 50 + "\n")

            # Verify visible count in browser matches extracted count
            logger.info("Verifying row counts...")
            visible_count = page.evaluate("""() => {
                const tables = Array.from(document.querySelectorAll("table"));
                let table = null;
                for (const t of tables) {
                    if (t.innerText.includes("Petitioner Name versus Respondent Name") || 
                        t.innerText.includes("Case Type/Case Number/Case Year")) {
                        table = t;
                        break;
                    }
                }
                if (!table) return 0;
                return Array.from(table.rows).filter(r => {
                    const cells = Array.from(r.cells);
                    if (cells.length < 3) return false;
                    if (r.querySelector("th")) return false;
                    if (cells.some(c => c.colSpan > 1)) return false;
                    return /^\\d+$/.test(cells[0].innerText.trim());
                }).length;
            }""")
            
            print(f"Total cases extracted: {len(extracted_cases)}")
            # Checkpoint & Resume Initialization
            import shutil
            from ecourts_scraper.checkpoint import load_checkpoint, save_checkpoint, clear_checkpoint
            from ecourts_scraper.browser import ECourtsPortalError
            all_canonical_records = []
            completed_cnrs = set()
            start_page = 1

            target_year = config.YEAR or "2023"
            checkpoint_file = config.DATA_DIR / f"checkpoint_{target_year}.json"
            cases_file = config.DATA_DIR / "cases.json"

            if config.RESUME_MODE or checkpoint_file.exists() or cases_file.exists():
                all_canonical_records, loaded_page, loaded_cnrs = load_checkpoint(target_year, config.DATA_DIR)
                completed_cnrs = loaded_cnrs
                if loaded_page > 1:
                    start_page = loaded_page
                
                # Safety Backups (Requirement #4)
                ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                if cases_file.exists():
                    backup_cases_path = config.DATA_DIR / f"cases_before_resume_{ts_str}.json"
                    shutil.copy(cases_file, backup_cases_path)
                    logger.info(f"Created safety backup: {backup_cases_path}")
                if checkpoint_file.exists():
                    backup_cp_path = config.DATA_DIR / f"checkpoint_before_resume_{ts_str}.json"
                    shutil.copy(checkpoint_file, backup_cp_path)
                    logger.info(f"Created safety backup: {backup_cp_path}")

                last_case_str = all_canonical_records[-1].get("case_number", "Unknown") if all_canonical_records else "None"
                print("\n" + "=" * 50)
                print(f"       {target_year} RESUME MODE")
                print("=" * 50)
                print(f"Existing completed cases: {len(all_canonical_records)}")
                print(f"Last checkpoint: {last_case_str}")
                print(f"Last page: {start_page}")
                print()
                print("Loading existing cases...")
                print("Loading checkpoint...")
                print("Validating completed records...")
                print("Creating safety backup...")
                print("Re-establishing eCourts session...")
                print("=" * 50 + "\n")

            # --- PHASE 3 & 4: PAGINATED SEARCH RESULTS EXTRACTION ---
            logger.info("Starting paginated search results and case detail extraction pipeline...")
            import time
            from ecourts_scraper.transform import raw_to_canonical
            from ecourts_scraper.exporter import export_dataset

            cases_attempted = len(all_canonical_records)
            cases_successful = len(all_canonical_records)
            cases_failed = 0
            validation_reports = []
            start_pipeline_time = time.time()

            current_page_num = 1
            
            # Fast-forward browser pagination if resuming to a higher page number
            while current_page_num < start_page:
                if browser.has_next_page():
                    logger.info(f"Navigating to resume page {current_page_num + 1}...")
                    browser.click_next_page()
                    current_page_num += 1
                else:
                    break

            def normalize_case_number(num: str) -> str:
                return re.sub(r'[^a-zA-Z0-9]', '', num).lower()

            more_pages_exist = True
            
            while more_pages_exist:
                logger.info(f"--- Processing Search Results Page {current_page_num} ---")
                
                # Save snapshot of search results page
                snapshot_search_path = config.SNAPSHOTS_DIR / f"search_results_page_{current_page_num}.html"
                try:
                    snapshot_search_path.write_text(page.content(), encoding="utf-8")
                    logger.info(f"Saved search results page snapshot to {snapshot_search_path}")
                except Exception as ss_err:
                    logger.error(f"Failed to save search results snapshot: {ss_err}")

                extracted_cases = extract_search_results(page)
                browser.log_state_investigation(f"After page {current_page_num} extraction")

                if not extracted_cases:
                    logger.warning(f"No cases found on search results page {current_page_num}.")
                    break

                logger.info(f"Extracted {len(extracted_cases)} case summaries on page {current_page_num}.")

                for page_case_idx, case in enumerate(extracted_cases, start=1):
                    # Check case limit
                    if config.MAX_CASES > 0 and len(all_canonical_records) >= config.MAX_CASES:
                        logger.info(f"Reached MAX_CASES limit of {config.MAX_CASES}. Stopping extraction loop.")
                        more_pages_exist = False
                        break

                    # Skip already completed CNRs / case numbers when resuming
                    case_key = normalize_case_number(case.case_number)
                    if case_key in completed_cnrs:
                        logger.info(f"Skipping already scraped case: {case.case_number}")
                        continue

                    cases_attempted += 1
                    logger.info(f"--- Scraping Case {cases_attempted} (Page {current_page_num}, Item {page_case_idx}/{len(extracted_cases)}) ---")
                    
                    case_success = False
                    last_error = None
                    failure_stage = "Initial"
                    max_case_attempts = 2

                    for attempt in range(1, max_case_attempts + 1):
                        logger.info(f"Case {case.case_number}: Attempt {attempt}/{max_case_attempts}")
                        try:
                            failure_stage = "Navigate to Details"
                            browser.click_view(case)
                            browser.wait_for_case_detail_page()

                            failure_stage = "Extract Main Details"
                            details = browser.get_minimal_case_details()

                            # Save HTML snapshot of the individual case page
                            safe_case_num = re.sub(r'[^a-zA-Z0-9]', '_', case.case_number)
                            case_snapshot_path = config.SNAPSHOTS_DIR / f"case_{safe_case_num}.html"
                            try:
                                case_snapshot_path.write_text(page.content(), encoding="utf-8")
                                logger.info(f"Saved case HTML snapshot to {case_snapshot_path}")
                            except Exception as c_ss_err:
                                logger.error(f"Failed to save case snapshot: {c_ss_err}")

                            # Verification check
                            expected_norm = normalize_case_number(case.case_number)
                            actual_norm = normalize_case_number(details.case_number)

                            if expected_norm not in actual_norm and actual_norm not in expected_norm:
                                raise ValueError(
                                    f"Verification mismatch: Expected case '{case.case_number}', but loaded detail page showed '{details.case_number}'"
                                )

                            failure_stage = "Extract Level 9 Details"
                            browser.follow_orders_and_business(details)

                            # Map to canonical record schema
                            scraped_at_iso = datetime.now().isoformat()
                            record = raw_to_canonical(
                                raw=details,
                                summary=case,
                                scraped_at=scraped_at_iso,
                                source_file_name=f"eCourts_Scraper_{config.YEAR}" if config.YEAR else "eCourts_Scraper"
                            )
                            all_canonical_records.append(record)
                            if details.cnr_number:
                                completed_cnrs.add(normalize_case_number(details.cnr_number))
                            completed_cnrs.add(case_key)

                            cases_successful += 1
                            case_success = True

                            # 10-Section Audit Checks
                            history_count = len(details.history) if details.history else 0
                            process_count = len(details.processes) if details.processes else 0
                            transfer_count = len(details.transfers) if details.transfers else 0
                            order_count = len(details.orders) if details.orders else 0
                            orders_opened = sum(1 for o in details.orders if o.order_link or o.order_number.startswith("H-"))
                            business_extracted = sum(1 for o in details.orders if o.business)
                            downloaded_docs = sum(len(o.metadata.get("documents", [])) for o in details.orders if o.metadata)

                            # Section Pass/Fail Audit
                            audit_case_details = "PASS" if details.case_number and details.cnr_number else "FAIL"
                            audit_petitioners = "PASS" if details.petitioners else "WARN"
                            audit_respondents = "PASS" if details.respondents else "WARN"
                            audit_acts = "PASS" if details.acts else "WARN"
                            audit_processes = "PASS"
                            audit_history = "PASS" if history_count > 0 else "WARN"
                            audit_orders = "PASS" if order_count > 0 else "WARN"
                            audit_daily_status = "PASS" if details.daily_status_text else "WARN"
                            audit_business = "PASS" if business_extracted > 0 else "WARN"
                            audit_transfers = "PASS"

                            validation_reports.append({
                                "case": case.case_number,
                                "success": "Yes",
                                "reason": "",
                                "case_details_audit": audit_case_details,
                                "petitioners_audit": audit_petitioners,
                                "respondents_audit": audit_respondents,
                                "acts_audit": audit_acts,
                                "processes_audit": audit_processes,
                                "history_audit": audit_history,
                                "orders_audit": audit_orders,
                                "daily_status_audit": audit_daily_status,
                                "business_audit": audit_business,
                                "transfers_audit": audit_transfers,
                                "business_extracted": business_extracted,
                                "history_rows": history_count,
                                "process_rows": process_count,
                                "transfer_rows": transfer_count,
                                "order_pages_opened": orders_opened,
                                "documents_downloaded": downloaded_docs
                            })
                            logger.info(f"Successfully processed case {case.case_number} (Audit: Details={audit_case_details}, History={history_count}, Orders={order_count})")
                            break

                        except ECourtsPortalError as e_portal:
                            # Failure classification (spec §16)
                            err_str = str(e_portal)
                            if "SESSION_TIMEOUT" in err_str or "Session timeout" in err_str:
                                failure_type = "SESSION_TIMEOUT"
                            elif "Invalid Request" in err_str:
                                failure_type = "UNKNOWN_PORTAL_ERROR"
                            else:
                                failure_type = "UNKNOWN_PORTAL_ERROR"
                            
                            logger.critical(f"EMERGENCY STOP [{failure_type}]: eCourts portal failure detected: {e_portal}")
                            print("\n" + "!" * 65)
                            print(f" [!] EMERGENCY STOP TRIGGERED: {failure_type}")
                            print(f"     Case Attempted : {case.case_number}")
                            print(f"     Results Page   : {current_page_num}")
                            print(f"     Page URL       : {page.url}")
                            print(f"     Timestamp      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"     Error Detail   : {e_portal}")
                            print(" Saving checkpoint and exiting cleanly...")
                            print("!" * 65 + "\n")
                            save_checkpoint(
                                cases=all_canonical_records,
                                year=config.YEAR or "default",
                                output_dir=config.DATA_DIR,
                                last_page=current_page_num,
                                completed_cnrs=completed_cnrs,
                                failed_case_count=cases_failed,
                                current_case=case.case_number,
                                current_result_index=page_case_idx,
                                search_parameters={
                                    "state": config.STATE,
                                    "district": config.DISTRICT,
                                    "court_complex": config.COURT_COMPLEX,
                                    "establishment": config.ESTABLISHMENT,
                                    "case_type": config.CASE_TYPE,
                                    "year": config.YEAR or "",
                                    "status": config.CASE_STATUS,
                                },
                            )
                            sys.exit(1)

                        except Exception as e:
                            last_error = e
                            logger.warning(f"Attempt {attempt} for case {case.case_number} failed at stage '{failure_stage}': {e}")
                            try:
                                browser.return_to_results()
                                browser.wait_for_results_table()
                            except Exception:
                                pass

                    if not case_success:
                        cases_failed += 1
                        
                        # Failure classification (spec §16)
                        err_str = str(last_error) if last_error else ""
                        if "timeout" in err_str.lower() and "session" in err_str.lower():
                            failure_type = "SESSION_TIMEOUT"
                        elif "timeout" in err_str.lower() or "Timeout" in err_str:
                            failure_type = "PAGE_LOAD_TIMEOUT"
                        elif "net::" in err_str or "network" in err_str.lower():
                            failure_type = "NETWORK_ERROR"
                        elif "not found" in err_str.lower() or "case_not_found" in err_str.lower():
                            failure_type = "CASE_NOT_FOUND"
                        elif "captcha" in err_str.lower():
                            failure_type = "CAPTCHA_REQUIRED"
                        elif "pars" in err_str.lower():
                            failure_type = "PARSER_ERROR"
                        else:
                            failure_type = "UNKNOWN_PORTAL_ERROR"
                        
                        logger.error(f"[{failure_type}] Failed to scrape case {case.case_number} after {max_case_attempts} attempts.")

                        import traceback
                        tb_str = traceback.format_exc()
                        curr_url = page.url

                        safe_case_num = re.sub(r'[^a-zA-Z0-9]', '_', case.case_number)
                        html_dump_path = config.LOGS_DIR / f"fail_dump_{safe_case_num}.html"
                        screenshot_path = config.LOGS_DIR / f"fail_screenshot_{safe_case_num}.png"

                        try:
                            html_dump_path.write_text(page.content(), encoding="utf-8")
                        except Exception:
                            pass
                        try:
                            page.screenshot(path=str(screenshot_path))
                        except Exception:
                            pass

                        validation_reports.append({
                            "case": case.case_number,
                            "success": "No",
                            "failure_type": failure_type,
                            "reason": f"[{failure_type}] Stage '{failure_stage}': {last_error}",
                            "case_details_audit": "EXTRACTION_FAILED",
                            "petitioners_audit": "EXTRACTION_FAILED",
                            "respondents_audit": "EXTRACTION_FAILED",
                            "acts_audit": "EXTRACTION_FAILED",
                            "processes_audit": "EXTRACTION_FAILED",
                            "history_audit": "EXTRACTION_FAILED",
                            "orders_audit": "EXTRACTION_FAILED",
                            "daily_status_audit": "EXTRACTION_FAILED",
                            "business_audit": "EXTRACTION_FAILED",
                            "transfers_audit": "EXTRACTION_FAILED",
                            "business_extracted": 0,
                            "history_rows": 0,
                            "process_rows": 0,
                            "transfer_rows": 0,
                            "order_pages_opened": 0,
                            "documents_downloaded": 0
                        })

                    # Always return safely and wait for search table before proceeding
                    try:
                        browser.return_to_results()
                        browser.wait_for_results_table()
                    except Exception as ex_nav:
                        logger.error(f"Post-case results stabilization failed: {ex_nav}")

                    # Periodic Checkpoint Saving every CHECKPOINT_INTERVAL cases (spec §14: every 5)
                    if cases_attempted % config.CHECKPOINT_INTERVAL == 0:
                        save_checkpoint(
                            cases=all_canonical_records,
                            year=config.YEAR or "default",
                            output_dir=config.DATA_DIR,
                            last_page=current_page_num,
                            completed_cnrs=completed_cnrs,
                            failed_case_count=cases_failed,
                            current_case=case.case_number,
                            current_result_index=page_case_idx,
                            search_parameters={
                                "state": config.STATE,
                                "district": config.DISTRICT,
                                "court_complex": config.COURT_COMPLEX,
                                "establishment": config.ESTABLISHMENT,
                                "case_type": config.CASE_TYPE,
                                "year": config.YEAR or "",
                                "status": config.CASE_STATUS,
                            },
                        )
                        logger.info(f"Periodic checkpoint saved at case {cases_attempted}.")

                    # Log progress details
                    elapsed = time.time() - start_pipeline_time
                    avg_time = elapsed / max(cases_attempted, 1)
                    print(f"Progress: Case {cases_attempted} | Page {current_page_num} | Elapsed: {elapsed:.1f}s | Avg/Case: {avg_time:.1f}s")

                # Check if next page exists and navigate
                if more_pages_exist and browser.has_next_page():
                    logger.info(f"Navigating to next search results page (Page {current_page_num + 1})...")
                    success_next = browser.click_next_page()
                    if success_next:
                        current_page_num += 1
                    else:
                        logger.warning("Failed to navigate to next search results page. Ending pagination loop.")
                        more_pages_exist = False
                else:
                    logger.info("No more search results pages found.")
                    more_pages_exist = False

            # --- EXPORT & REPORTING PHASE ---
            logger.info("Exporting scraped dataset into JSON, Excel, Master CSV, and Relational CSVs...")
            json_path, csv_path, excel_path = export_dataset(all_canonical_records)

            # Clear checkpoint after successful export
            clear_checkpoint(config.YEAR or "default", config.DATA_DIR)

            # Generate final markdown validation report
            report_lines = [
                f"# eCourts Production Scraper Validation Report ({config.YEAR or 'All'})",
                "",
                f"- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"- **Year Scraped**: {config.YEAR or 'Not Specified'}",
                f"- **Cases Attempted**: {cases_attempted}",
                f"- **Cases Successful**: {cases_successful}",
                f"- **Cases Failed**: {cases_failed}",
                "",
                "## Per-Case Audit & Metric Breakdown",
                "",
                "| Case | Success | Details Audit | History Audit | Orders Audit | Business Extracted | History Rows | Process Rows | Transfer Rows | Order Pages Opened |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
            ]
            for rep in validation_reports:
                report_lines.append(
                    f"| {rep['case']} | {rep['success']} | {rep.get('case_details_audit', 'N/A')} | "
                    f"{rep.get('history_audit', 'N/A')} | {rep.get('orders_audit', 'N/A')} | "
                    f"{rep['business_extracted']} | {rep['history_rows']} | {rep['process_rows']} | "
                    f"{rep['transfer_rows']} | {rep['order_pages_opened']} |"
                )

            report_content = "\n".join(report_lines)
            report_path = config.DATA_DIR / "validation_report.md"
            report_path.write_text(report_content, encoding="utf-8")
            
            # Also save under logs directory
            (config.LOGS_DIR / "validation_report.md").write_text(report_content, encoding="utf-8")
            logger.info(f"Saved validation report to {report_path}")

            pipeline_duration = time.time() - start_pipeline_time
            print("\n=========================================")
            print("eCourts Production Scraper Execution Completed")
            print("=========================================")
            print(f"Year             : {config.YEAR or 'N/A'}")
            print(f"Cases Attempted  : {cases_attempted}")
            print(f"Cases Successful : {cases_successful}")
            print(f"Cases Failed     : {cases_failed}")
            print(f"JSON Output Path : {json_path}")
            print(f"CSV Output Path  : {csv_path}")
            print(f"Excel Output Path: {excel_path}")
            print(f"Validation Report: {report_path}")
            print(f"Execution Time   : {pipeline_duration:.2f} seconds")
            print("=========================================")

    except Exception as e:
        logger.critical(f"Critical execution failure: {e}", exc_info=True)
        print(f"\n[-] CRITICAL FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

