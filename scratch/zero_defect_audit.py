import json
import os
import re

base_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023"
cases_json_path = os.path.join(base_dir, "cases.json")
snapshots_dir = os.path.join(base_dir, "snapshots")

def run_defect_audit():
    with open(cases_json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"Loaded {len(cases)} cases for zero-defect research.")

    # 1. Find missing Purpose of Hearing
    missing_purpose_cases = []
    # 2. Find missing Business/Order Text rows
    missing_text_cases = []
    # 3. Analyze Business Text vs Order Text alignment
    identical_text_count = 0
    total_text_rows = 0
    # 4. Check for Transfers in snapshots
    transfers_found_snapshots = 0
    
    # Trackers for detailed inspections
    for idx, case in enumerate(cases):
        case_number = case.get("case_number", "")
        cnr = case.get("cnr", "")
        
        safe_num = case_number.replace("/", "_").replace("\\", "_")
        snapshot_path = os.path.join(snapshots_dir, f"case_{safe_num}.html")
        if not os.path.exists(snapshot_path):
            snapshot_path = os.path.join(snapshots_dir, f"EX_{safe_num}.html")
            
        has_snapshot = os.path.exists(snapshot_path)
        html_content = ""
        if has_snapshot:
            with open(snapshot_path, "r", encoding="utf-8") as f_snap:
                html_content = f_snap.read()

        # Check history purposes
        history = []
        try:
            extra = json.loads(case.get("extra_metadata", "{}") or "{}")
            history = extra.get("history", [])
        except:
            pass
            
        for h_idx, h in enumerate(history):
            purpose = h.get("purpose") or h.get("purpose_of_hearing", "")
            if not purpose:
                missing_purpose_cases.append({
                    "case_number": case_number,
                    "cnr": cnr,
                    "hearing_index": h_idx,
                    "date": h.get("hearing_date") or h.get("business_date", "")
                })

        # Check orders/business text
        orders = []
        try:
            orders = json.loads(case.get("orders_json", "[]") or "[]")
        except:
            pass
            
        for o_idx, o in enumerate(orders):
            ord_text = o.get("full_order_text") or o.get("order_text", "")
            bus_text = o.get("business", "")
            
            if not ord_text and not bus_text:
                missing_text_cases.append({
                    "case_number": case_number,
                    "cnr": cnr,
                    "order_index": o_idx,
                    "date": o.get("order_date", "")
                })
                
            if ord_text or bus_text:
                total_text_rows += 1
                if ord_text.strip() == bus_text.strip() and ord_text.strip() != "":
                    identical_text_count += 1

        # Check transfers table in HTML snapshot
        if has_snapshot and "transfer_table" in html_content:
            transfers_found_snapshots += 1

    print("\n--- AUDIT RESEARCH RESULTS ---")
    print(f"1. Missing Purpose Cases: {len(missing_purpose_cases)}")
    for m in missing_purpose_cases[:5]:
        print(f"   Case: {m['case_number']}, Date: {m['date']}")
        
    print(f"2. Missing Business/Order Text Rows: {len(missing_text_cases)}")
    for m in missing_text_cases[:5]:
        print(f"   Case: {m['case_number']}, Date: {m['date']}")

    print(f"3. Identical Text Rows: {identical_text_count}/{total_text_rows}")
    print(f"4. Transfers found in snapshots: {transfers_found_snapshots}")

if __name__ == "__main__":
    run_defect_audit()
