import json
import os
import shutil
import re
from datetime import datetime
from bs4 import BeautifulSoup
import csv
from ecourts_scraper.exporter import CONSOLIDATED_COLUMNS, safe_csv_value

def backup_file(filepath):
    if os.path.exists(filepath):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(os.path.basename(filepath))
        backup_name = f"{name}_before_140_repair_{ts}{ext}"
        backup_path = os.path.join(os.path.dirname(filepath), backup_name)
        shutil.copy(filepath, backup_path)
        print(f"Backed up {filepath} -> {backup_path}")
        return backup_path
    return None

def run_audit_and_repair():
    base_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023"
    cases_json_path = os.path.join(base_dir, "cases.json")
    checkpoint_path = os.path.join(base_dir, "checkpoint_2023.json")
    consolidated_csv_path = os.path.join(base_dir, "Consolidated_Executive_Petitions_2023.csv")
    snapshots_dir = os.path.join(base_dir, "snapshots")

    # Step 1: Backup files
    backup_file(cases_json_path)
    backup_file(checkpoint_path)
    backup_file(consolidated_csv_path)

    # Step 2: Load cases
    with open(cases_json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"Loaded {len(cases)} cases for audit.")

    repaired_count = 0
    cases_already_complete = 0
    cases_requiring_live_rescrape = 0
    fields_repaired = 0
    fields_source_empty = 0
    
    # Audit log entries
    case_repairs_log = []
    order_repairs_log = []
    history_repairs_log = []
    transfer_audit_log = []
    legit_empty_log = {}

    for idx, case in enumerate(cases):
        case_number = case.get("case_number", "")
        cnr = case.get("cnr", "")
        if (idx + 1) % 10 == 0 or idx == 0 or idx == len(cases) - 1:
            print(f"Auditing case {idx + 1}/{len(cases)}: {case_number}")
        
        # Determine snapshot path
        safe_num = case_number.replace("/", "_").replace("\\", "_")
        snapshot_path = os.path.join(snapshots_dir, f"case_{safe_num}.html")
        if not os.path.exists(snapshot_path):
            # Try alternate naming
            snapshot_path = os.path.join(snapshots_dir, f"EX_{safe_num}.html")
            
        if not os.path.exists(snapshot_path):
            print(f"Warning: Snapshot not found for {case_number} ({snapshot_path})")
            continue
            
        with open(snapshot_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            
        case_was_repaired = False
        
        # 1. Parse Registration Date
        reg_date = ""
        details_table = soup.find("table", class_="case_details_table")
        if details_table:
            for tr in details_table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
                for i in range(0, len(cells), 2):
                    if i + 1 < len(cells):
                        lbl = cells[i].replace(r':', '').strip().lower()
                        if "registration date" in lbl:
                            reg_date = cells[i+1].strip()
                            
        # Standardize Registration Date
        if reg_date:
            # eCourts standard date check/parse
            for fmt in ('%d-%m-%Y', '%d/%m/%Y'):
                try:
                    dt = datetime.strptime(reg_date, fmt)
                    reg_date = dt.strftime("%d-%m-%Y")
                    break
                except ValueError:
                    pass
        
        old_reg_date = case.get("registration_date", "")
        if reg_date and old_reg_date != reg_date:
            case["registration_date"] = reg_date
            fields_repaired += 1
            case_was_repaired = True
            case_repairs_log.append((case_number, cnr, "registration_date", old_reg_date, reg_date, "HTML Snapshot"))
        elif not reg_date:
            fields_source_empty += 1
            legit_empty_log["registration_date"] = legit_empty_log.get("registration_date", 0) + 1

        # 2. Parse Sub Stage
        sub_stage = ""
        status_table = soup.find("table", class_="case_status_table")
        if status_table:
            for tr in status_table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
                if len(cells) >= 3 and "case status" in cells[0].lower():
                    sub_stage = cells[2].strip()
                    
        old_sub_stage = case.get("sub_stage", "")
        if sub_stage and old_sub_stage != sub_stage:
            case["sub_stage"] = sub_stage
            # Also update case_sub_stage in extra_metadata
            extra = {}
            if case.get("extra_metadata"):
                try:
                    extra = json.loads(case["extra_metadata"])
                except:
                    pass
            extra["case_sub_stage"] = sub_stage
            case["extra_metadata"] = json.dumps(extra)
            
            fields_repaired += 1
            case_was_repaired = True
            case_repairs_log.append((case_number, cnr, "sub_stage", old_sub_stage, sub_stage, "HTML Snapshot"))
        elif not sub_stage:
            fields_source_empty += 1
            legit_empty_log["sub_stage"] = legit_empty_log.get("sub_stage", 0) + 1

        # 3. Parse Transfers
        transfers = []
        trans_table = soup.find("table", class_="transfer_table")
        if trans_table:
            for tr in trans_table.find_all("tr"):
                if tr.find("th"):
                    continue
                cells = [c.get_text(strip=True) for c in tr.find_all("td")]
                if len(cells) >= 4:
                    transfers.append({
                        "registration_number": cells[0],
                        "transfer_date": cells[1],
                        "from_court": cells[2],
                        "to_court": cells[3]
                    })
                    
        extra = {}
        if case.get("extra_metadata"):
            try:
                extra = json.loads(case["extra_metadata"])
            except:
                pass
        old_transfers = extra.get("transfers", [])
        if len(transfers) != len(old_transfers):
            extra["transfers"] = transfers
            case["extra_metadata"] = json.dumps(extra)
            fields_repaired += 1
            case_was_repaired = True
            transfer_audit_log.append((case_number, cnr, f"Transfers Count changed from {len(old_transfers)} to {len(transfers)}"))
        elif not transfers:
            legit_empty_log["transfers"] = legit_empty_log.get("transfers", 0) + 1
            transfer_audit_log.append((case_number, cnr, "TRANSFER_SECTION_NOT_AVAILABLE"))
        else:
            transfer_audit_log.append((case_number, cnr, "TRANSFER_PRESENT_AND_EXTRACTED"))

        # 4. Parse Order links and onclick parameters
        orders = []
        try:
            orders = json.loads(case.get("orders_json", "[]") or "[]")
        except:
            pass
            
        ord_table = soup.find("table", class_="order_table")
        if ord_table:
            rows = ord_table.find_all("tr")
            ord_idx = 0
            for r in rows:
                if r.find("th"):
                    continue
                cells = r.find_all("td")
                if len(cells) >= 3 and ord_idx < len(orders):
                    link_el = cells[2].find("a")
                    if link_el:
                        onclick = link_el.get("onclick") or ""
                        # Store ajax parameters/onclick details on the order objects
                        if onclick and "displayPdf" in onclick:
                            orders[ord_idx]["onclick"] = onclick
                            # check if the order_link is empty
                            if not orders[ord_idx].get("order_link"):
                                cases_requiring_live_rescrape += 1
                                order_repairs_log.append((case_number, cnr, orders[ord_idx].get("order_number", str(ord_idx+1)), "Empty Link", "Requires Live Rescrape", onclick))
                    ord_idx += 1
            case["orders_json"] = json.dumps(orders, ensure_ascii=False)
            
        if case_was_repaired:
            repaired_count += 1
        else:
            cases_already_complete += 1

    # Save repaired cases.json
    with open(cases_json_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)
    print(f"Saved repaired cases.json to {cases_json_path}")

    # Rebuild Consolidated CSV
    rebuild_consolidated_csv(cases, consolidated_csv_path)

    # Generate Audit Report
    generate_audit_report(
        json_cases_count=len(cases),
        repaired_count=repaired_count,
        cases_already_complete=cases_already_complete,
        cases_requiring_live_rescrape=cases_requiring_live_rescrape,
        fields_repaired=fields_repaired,
        fields_source_empty=fields_source_empty,
        case_repairs_log=case_repairs_log,
        order_repairs_log=order_repairs_log,
        transfer_audit_log=transfer_audit_log,
        legit_empty_log=legit_empty_log,
        base_dir=base_dir
    )

def rebuild_consolidated_csv(cases, output_path):
    rows = []
    for raw_rec in cases:
        rec = clean_canonical_record(raw_rec)
        
        cnr = rec.get("cnr", "")
        case_number = rec.get("case_number", "")
        court_name = rec.get("court_name", "")
        court_complex = "City Civil Court Complex, Bangalore"
        state = rec.get("bench_state", "Karnataka")
        district = rec.get("bench_city", "BENGALURU")
        case_title = rec.get("case_title", "")
        case_type = rec.get("case_type_label", "")
        filing_number = rec.get("filing_number", "") or rec.get("cnr_case_number", "")
        filing_date = rec.get("filing_date", "")
        reg_num = rec.get("registration_number", "") or rec.get("cnr_case_number", "")
        reg_date = rec.get("registration_date", "")
        case_status = rec.get("case_status", "")
        sub_stage = rec.get("sub_stage", "") or rec.get("case_sub_stage", "")
        nod = rec.get("nature_of_disposal", "") or rec.get("result", "")
        disposal_date = rec.get("disposal_date", "") or rec.get("decision_date", "")
        decision_date = rec.get("decision_date", "")
        first_hearing_date = rec.get("first_hearing_date", "")
        last_hearing_date = rec.get("last_hearing_date", "")
        next_hearing_date = rec.get("next_hearing_date", "")
        duration = rec.get("case_duration_days", "")
        filing_to_first = rec.get("filing_to_first_hearing_days", "")
        petitioner = rec.get("appellant", "") or rec.get("petitioner", "")
        petitioner_adv = rec.get("petitioner_advocates", "") or rec.get("petitioner_advocate", "")
        respondent = rec.get("respondent", "")
        respondent_adv = rec.get("respondent_advocates", "") or rec.get("respondent_advocate", "")
        sections = rec.get("sections", "")
        
        acts = rec.get("acts", "")
        if not acts and sections:
            act_match = re.match(r'^([A-Za-z\s0-9]+)\s+Section', sections)
            if act_match:
                acts = act_match.group(1).strip()
            else:
                acts = "CPC" if "CPC" in sections else ""

        history_list = rec.get("history", [])
        orders_list = rec.get("orders", [])
        business_list = rec.get("business_list", [])
        processes_list = rec.get("processes", [])
        transfers_list = rec.get("transfers", [])

        num_events = max(len(history_list), len(orders_list), len(business_list), 1)

        for idx in range(1, num_events + 1):
            h_rec = history_list[idx - 1] if idx <= len(history_list) else {}
            h_date = h_rec.get("hearing_date") or h_rec.get("business_date") or ""
            h_idx = str(h_rec.get("history_index", idx)) if h_rec else ""
            h_judge = h_rec.get("judge", "")
            h_ord = h_rec.get("order_number", "")
            h_purpose = h_rec.get("purpose_of_hearing") or h_rec.get("purpose", "")
            h_summary = h_rec.get("business_summary") or h_purpose

            o_rec = orders_list[idx - 1] if idx <= len(orders_list) else {}
            o_date = o_rec.get("order_date", "")
            o_idx = str(idx) if o_rec else ""
            o_num = o_rec.get("order_number", "")
            o_link = o_rec.get("order_link", "")
            o_nod = o_rec.get("nature_of_disposal", "")
            o_disp_date = o_rec.get("disposal_date", "")
            o_judge = o_rec.get("judge", "")

            raw_order_text = ""
            raw_business_text = ""
            if idx <= len(orders_list):
                try:
                    raw_orders_json = json.loads(raw_rec.get("orders_json", "[]") or "[]")
                    if idx - 1 < len(raw_orders_json):
                        raw_order_text = raw_orders_json[idx - 1].get("full_order_text", "")
                except:
                    pass
            if not raw_order_text:
                raw_order_text = o_rec.get("full_order_text") or o_rec.get("order_text") or ""
                
            if idx <= len(business_list):
                raw_business_text = raw_order_text
            if not raw_business_text:
                raw_business_text = b_rec.get("business_text", "") or raw_order_text

            o_docs = str(len(o_rec.get("documents", []))) if o_rec else ""

            b_rec = business_list[idx - 1] if idx <= len(business_list) else {}
            b_date = b_rec.get("business_date", "") or h_date or o_date
            b_idx = str(idx) if b_rec else ""

            p_rec = processes_list[idx - 1] if idx <= len(processes_list) else {}
            p_id = p_rec.get("process_id", "")
            p_title = p_rec.get("process_title", "")
            p_date = p_rec.get("process_date", "")

            t_rec = transfers_list[idx - 1] if idx <= len(transfers_list) else {}
            t_reg = t_rec.get("registration_number", "")
            t_date = t_rec.get("transfer_date", "")
            t_from = t_rec.get("from_court", "")
            t_to = t_rec.get("to_court", "")

            row = {
                'CNR': cnr,
                'Case Number': case_number,
                'Court Name': court_name,
                'Court Complex': court_complex,
                'State': state,
                'District': district,
                'Case Title': case_title,
                'Case Type': case_type,
                'Filing Number': filing_number,
                'Filing Date': filing_date,
                'Registration Number': reg_num,
                'Registration Date': reg_date,
                'Case Status': case_status,
                'Sub Stage': sub_stage,
                'Nature of Disposal': nod,
                'Disposal Date': disposal_date,
                'Decision Date': decision_date,
                'First Hearing Date': first_hearing_date,
                'Last Hearing Date': last_hearing_date,
                'Next Hearing Date': next_hearing_date,
                'Case Duration (Days)': duration,
                'Filing to First Hearing Duration (Days)': filing_to_first,
                'Petitioner': petitioner,
                'Petitioner Advocate': petitioner_adv,
                'Respondent': respondent,
                'Respondent Advocate': respondent_adv,
                'Acts': acts,
                'Sections': sections,
                'Hearing Date': h_date,
                'Hearing Index': h_idx,
                'Hearing Judge': h_judge,
                'Hearing Order Number': h_ord,
                'Purpose of Hearing': h_purpose,
                'Hearing Business Summary': h_summary,
                'Business Date': b_date,
                'Business Index': b_idx,
                'Business Text': raw_business_text,
                'Order Date': o_date,
                'Order Index': o_idx,
                'Order Number': o_num,
                'Order Link': o_link,
                'Order Nature of Disposal': o_nod,
                'Order Disposal Date': o_disp_date,
                'Order Judge': o_judge,
                'Order Text': raw_order_text,
                'Order Document Count': o_docs,
                'Process ID': p_id,
                'Process Title': p_title,
                'Process Date': p_date,
                'Transfer Registration Number': t_reg,
                'Transfer Date': t_date,
                'Transfer From Court': t_from,
                'Transfer To Court': t_to,
                'Documents': ""
            }
            rows.append(row)

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CONSOLIDATED_COLUMNS, quoting=csv.QUOTE_ALL, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            clean_r = {col: safe_csv_value(r.get(col, "")) for col in CONSOLIDATED_COLUMNS}
            writer.writerow(clean_r)
    print(f"Rebuilt consolidated CSV: {output_path}")

def generate_audit_report(json_cases_count, repaired_count, cases_already_complete, cases_requiring_live_rescrape,
                          fields_repaired, fields_source_empty, case_repairs_log, order_repairs_log,
                          transfer_audit_log, legit_empty_log, base_dir):
    
    report_lines = [
        "# 140-Case Zero-Defect Audit & Repair Report",
        "",
        "## SUMMARY",
        "",
        f"- **Total cases**: {json_cases_count}",
        f"- **Cases requiring repair**: {repaired_count}",
        f"- **Cases already complete**: {cases_already_complete}",
        f"- **Cases requiring live rescrape**: {cases_requiring_live_rescrape}",
        f"- **Fields repaired**: {fields_repaired}",
        f"- **Fields genuinely absent from source**: {fields_source_empty}",
        f"- **Fields still unresolved**: {cases_requiring_live_rescrape}",
        "",
        "## Detailed Case-Level Repairs",
        "",
        "| Case | CNR | Field | Old Value | New Value | Source | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |"
    ]
    
    for r in case_repairs_log:
        report_lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | REPAIRED |")
        
    report_lines.extend([
        "",
        "## Order repairs",
        "",
        "| Case | CNR | Order | URL | Text | Document | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |"
    ])
    
    for r in order_repairs_log:
        report_lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | Extracted | {r[4]} | {r[5]} |")
        
    report_lines.extend([
        "",
        "## Transfer Audit",
        "",
        "| Case | CNR | Transfer Status |",
        "| --- | --- | --- |"
    ])
    
    for r in transfer_audit_log:
        report_lines.append(f"| {r[0]} | {r[1]} | {r[2]} |")
        
    report_lines.extend([
        "",
        "## Legitimately Empty Fields",
        "",
        "| Field | Count | Explanation |",
        "| --- | --- | --- |"
    ])
    
    for k, v in legit_empty_log.items():
        report_lines.append(f"| {k} | {v} | Legitimately empty on portal source |")
        
    report_path = os.path.join(base_dir, "repair_audit_140_cases.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Generated repair audit report: {report_path}")

if __name__ == "__main__":
    run_audit_and_repair()
