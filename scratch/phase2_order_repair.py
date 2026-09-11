import json
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from ecourts_scraper.models import CaseSummary

base_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023"
cases_json_path = os.path.join(base_dir, "cases.json")
checkpoint_path = os.path.join(base_dir, "order_link_repair_checkpoint_140.json")

def load_checkpoint():
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "completed_cnrs": [],
        "completed_cases": [],
        "resolved_order_count": 0,
        "unresolved_order_count": 0,
        "failed_order_count": 0,
        "last_case": "",
        "last_order": "",
        "timestamp": ""
    }

def save_checkpoint(cp):
    cp["timestamp"] = datetime.now().isoformat()
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(cp, f, indent=2, ensure_ascii=False)

def run_phase2_order_repair():
    # 1. Load checkpoint and cases
    cp = load_checkpoint()
    with open(cases_json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    # 2. Build repair queue
    # Filter cases that need order links resolved and are not already completed in checkpoint
    queue = []
    for case in cases:
        cnr = case.get("cnr", "")
        if cnr in cp["completed_cnrs"]:
            continue
        # Check if case has any order requiring resolution
        orders = []
        try:
            orders = json.loads(case.get("orders_json", "[]") or "[]")
        except:
            pass
        has_missing = any(not o.get("order_link") for o in orders)
        if has_missing:
            queue.append(case)

    total_repair_orders = sum(sum(1 for o in json.loads(c.get("orders_json", "[]") or "[]") if not o.get("order_link")) for c in queue)
    
    print("==================================================")
    print("ORDER LINK REPAIR MODE")
    print("==================================================")
    print(f"Existing cases: {len(cases)}")
    print(f"Repair cases: {len(queue)}")
    print(f"Repair orders: {total_repair_orders}")
    print("Next production case: EX/188/2023")
    print("Production scraping: DISABLED")
    print("==================================================")

    if not queue:
        print("All order links already repaired!")
        return

    # 3. Launch Playwright
    from ecourts_scraper import config
    from ecourts_scraper.browser import ECourtsBrowser

    with sync_playwright() as p:
        browser_instance = p.chromium.launch(headless=False)
        context = browser_instance.new_context()
        page = context.new_page()

        browser = ECourtsBrowser(page)
        browser.navigate_to_home()
        browser.select_state(config.STATE)
        browser.select_district(config.DISTRICT)
        browser.select_court_complex(config.COURT_COMPLEX)
        browser.select_establishment(config.ESTABLISHMENT)
        browser.select_case_type_tab()
        browser.fill_case_type(config.CASE_TYPE)
        browser.fill_year(config.YEAR)
        browser.select_disposed()

        print("\n" + "=" * 55)
        print("Please solve the CAPTCHA manually in the browser window.")
        print("Once solved, press [ENTER] in this terminal to continue...")
        print("=" * 55 + "\n")
        input()

        browser.click_go()
        browser.verify_results_table()

        # --- DIAGNOSTIC OUTPUT ---
        print("\n==============================================")
        print("DIAGNOSTICS BEFORE EX/2/2023")
        print("==============================================")
        print(f"Current URL: {page.url}")
        print(f"Page Title: {page.title()}")
        
        # Check table
        table_count = page.locator("table#dispTable, table#showListTable, table:has-text('Petitioner Name versus Respondent Name')").count()
        print(f"Result table selector found: {'YES' if table_count > 0 else 'NO'} (count: {table_count})")
        
        visible_cases = []
        if table_count > 0:
            js_get_visible = """() => {
                const tables = Array.from(document.querySelectorAll("table"));
                let table = null;
                for (const t of tables) {
                    if (t.innerText.includes("Petitioner Name versus Respondent Name") || 
                        t.innerText.includes("Case Type/Case Number/Case Year")) {
                        table = t;
                        break;
                    }
                }
                if (!table) return [];
                return Array.from(table.rows)
                    .filter(r => r.cells.length >= 3 && !r.querySelector("th") && !Array.from(r.cells).some(c => c.colSpan > 1))
                    .map(r => r.cells[1].innerText.trim());
            }"""
            visible_cases = page.evaluate(js_get_visible)
            
        print(f"Total result rows present: {len(visible_cases)}")
        if visible_cases:
            print(f"First 10 visible case numbers: {visible_cases[:10]}")
            print(f"Last 10 visible case numbers: {visible_cases[-10:]}")
        else:
            print("No visible case numbers found in the table.")
            
        # Check pagination
        has_nav = page.locator("a:has-text('Next'), a[onclick*='nextPage']").count() > 0
        print(f"Pagination present: {'YES' if has_nav else 'NO'}")
        
        # Current pagination page number text
        page_num_text = "Unknown"
        try:
            active_page = page.locator("span.current, li.active, a.active").first
            if active_page.count() > 0:
                page_num_text = active_page.inner_text().strip()
        except:
            pass
        print(f"Current pagination/page number: {page_num_text}")
        print("==============================================\n")

        # Iterate over remaining queue
        for idx, case in enumerate(queue, start=1):
            case_number = case.get("case_number", "")
            cnr = case.get("cnr", "")
            print(f"\n[{idx}/{len(queue)}] Resolving links for Case: {case_number} (CNR: {cnr})")

            # Check if "OOPS, SOMETHING HAPPENED" is visible in search results page
            body_text = ""
            try:
                body_text = page.locator("body").inner_text().lower()
            except:
                pass
            if "oops, something happened" in body_text:
                print("Safety Stop: eCourts 'OOPS, SOMETHING HAPPENED' detected on search page. Stopping execution.")
                break

            # Find row and click View using production logic
            clicked = False
            try:
                case_id_parts = case_number.split("/")
                if len(case_id_parts) == 3:
                    case_type_code, case_seq, case_year = case_id_parts
                else:
                    case_type_code, case_seq, case_year = "", "", ""
                
                # We need view_index to locate the row if the case number fails to unique-match.
                # In the search results DOM, we have the list of all cases. We can find the view_index of the case number.
                v_idx = 0
                if case_number in visible_cases:
                    v_idx = visible_cases.index(case_number)
                
                summary = CaseSummary(
                    serial_number="",
                    case_number=case_number,
                    parties="",
                    view_index=v_idx,
                    case_type_code=case_type_code,
                    case_seq=case_seq,
                    case_year=case_year
                )
                browser.click_view(summary)
                clicked = True
            except Exception as click_err:
                print(f"Warning: Failed to find or click row for {case_number}: {click_err}. Stopping to prevent errors.")
                break

            # Wait for detail view or check oops
            try:
                page.locator("div[id^='CS']:has(table.case_details_table)").wait_for(state="visible", timeout=15000)
            except Exception as wait_err:
                # Check if OOPS is visible on page
                body_text = ""
                try:
                    body_text = page.locator("body").inner_text().lower()
                except:
                    pass
                if "oops, something happened" in body_text:
                    print("Safety Stop: eCourts 'OOPS, SOMETHING HAPPENED' detected while loading case details. Stopping execution.")
                    break
                else:
                    print(f"Timeout waiting for details of {case_number}: {wait_err}. Stopping execution.")
                    break

            # Check inside details
            body_text = ""
            try:
                body_text = page.locator("body").inner_text().lower()
            except:
                pass
            if "oops, something happened" in body_text:
                print("Safety Stop: eCourts 'OOPS, SOMETHING HAPPENED' detected inside details. Stopping execution.")
                break

            # Execute AJax resolver
            js_resolve_links = """async () => {
                const resolvePdf = (params) => {
                    return new Promise((resolve) => {
                        if (!params || typeof ajaxCall === 'undefined') {
                            resolve("");
                            return;
                        }
                        const [normal_v, case_val, court_code, filename, appFlag] = params;
                        const postdata = "&normal_v=" + normal_v + "&case_val=" + case_val + "&court_code=" + court_code + "&filename=" + filename + "&appFlag=" + (appFlag || "");
                        ajaxCall({
                            url: 'home/display_pdf',
                            postdata: postdata,
                            callback: (res) => {
                                if (res && res.status && res.order) {
                                    resolve("https://services.ecourts.gov.in/ecourtindia_v6/" + res.order);
                                } else {
                                    resolve("");
                                }
                            }
                        });
                    });
                };

                const ordTable = document.querySelector("table.order_table");
                const resolved = [];
                if (ordTable) {
                    const rows = Array.from(ordTable.querySelectorAll("tr"));
                    for (let r of rows) {
                        if (r.querySelector("th")) continue;
                        const cells = Array.from(r.querySelectorAll("td"));
                        if (cells.length >= 3) {
                            const orderNum = cells[0].innerText.trim();
                            const orderDate = cells[1].innerText.trim();
                            const linkEl = cells[2].querySelector("a");
                            let orderLink = "";
                            if (linkEl) {
                                const onclick = linkEl.getAttribute("onclick") || "";
                                const match = onclick.match(/displayPdf\\s*\\(([^)]+)\\)/);
                                if (match) {
                                    const ajaxParams = match[1].split(",").map(s => s.trim().replace(/^['"]|['"]$/, ""));
                                    try {
                                        orderLink = await resolvePdf(ajaxParams);
                                    } catch (e) {}
                                }
                            }
                            resolved.push({
                                order_number: orderNum,
                                order_date: orderDate,
                                order_link: orderLink
                            });
                        }
                    }
                }
                return resolved;
            }"""

            try:
                resolved_orders = page.evaluate(js_resolve_links)
            except Exception as eval_err:
                print(f"Error evaluating AJAX link resolver for {case_number}: {eval_err}. Stopping execution.")
                break

            # Update orders_json
            orders = []
            try:
                orders = json.loads(case.get("orders_json", "[]") or "[]")
            except:
                pass

            resolved_this_case = 0
            failed_this_case = 0
            
            for ro in resolved_orders:
                for qo in orders:
                    if qo.get("order_number") == ro["order_number"] and qo.get("order_date") == ro["order_date"]:
                        if ro["order_link"]:
                            qo["order_link"] = ro["order_link"]
                            resolved_this_case += 1
                            print(f"  Resolved Order {qo['order_number']}: {ro['order_link']}")
                        else:
                            failed_this_case += 1
                            print(f"  Order {qo['order_number']} has no PDF link on eCourts portal.")

            case["orders_json"] = json.dumps(orders, ensure_ascii=False)

            # Update cases.json
            with open(cases_json_path, "w", encoding="utf-8") as f:
                json.dump(cases, f, indent=4, ensure_ascii=False)

            # Update Checkpoint
            cp["completed_cnrs"].append(cnr)
            cp["completed_cases"].append(case_number)
            cp["resolved_order_count"] += resolved_this_case
            cp["failed_order_count"] += failed_this_case
            cp["last_case"] = case_number
            cp["last_order"] = resolved_orders[-1]["order_number"] if resolved_orders else ""
            save_checkpoint(cp)

            # Go back to search results
            try:
                browser.return_to_results()
                browser.wait_for_results_table()
            except Exception as back_err:
                print(f"Error going back to results: {back_err}. Stopping execution.")
                break

        browser_instance.close()

if __name__ == "__main__":
    run_phase2_order_repair()
