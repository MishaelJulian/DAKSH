import json
import os
import shutil
import re
from datetime import datetime

base_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023"
cases_json_path = os.path.join(base_dir, "cases.json")
snapshots_dir = os.path.join(base_dir, "snapshots")
report_path = os.path.join(base_dir, "snapshot_repair_report_140.md")

def run_phase1_repair():
    # 1. Back up cases.json
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(base_dir, f"cases_before_phase1_repair_{ts}.json")
    shutil.copy(cases_json_path, backup_path)
    print(f"Backed up cases.json -> {backup_path}")

    # 2. Load cases
    with open(cases_json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    original_cases_len = len(cases)
    
    # Store deep copy of original data for validation comparison
    original_cases_dump = json.dumps(cases, ensure_ascii=False)
    original_data_map = {c["cnr"]: c for c in json.loads(original_cases_dump)}

    # Trackers
    reg_recovered = 0
    sub_stages_recovered = 0
    cases_modified = 0
    unexpected_failures = 0

    detailed_log = []

    for idx, case in enumerate(cases):
        case_number = case.get("case_number", "")
        cnr = case.get("cnr", "")
        
        safe_num = case_number.replace("/", "_").replace("\\", "_")
        snapshot_path = os.path.join(snapshots_dir, f"case_{safe_num}.html")
        if not os.path.exists(snapshot_path):
            snapshot_path = os.path.join(snapshots_dir, f"EX_{safe_num}.html")
            
        if not os.path.exists(snapshot_path):
            unexpected_failures += 1
            print(f"Unexpected failure: snapshot not found for {case_number}")
            continue
            
        with open(snapshot_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Parse Registration Date
        reg_date = ""
        details_table_match = re.search(r'<table[^>]+class="[^"]*case_details_table[^"]*".*?</table>', html_content, re.DOTALL | re.IGNORECASE)
        if details_table_match:
            reg_match = re.search(r'<th[^>]*>\s*Registration Date\s*</th>\s*<td[^>]*>(.*?)</td>', details_table_match.group(0), re.DOTALL | re.IGNORECASE)
            if reg_match:
                reg_date = re.sub(r'<[^>]+>', '', reg_match.group(1)).strip()
            
        if reg_date:
            for fmt in ('%d-%m-%Y', '%d/%m/%Y'):
                try:
                    dt = datetime.strptime(reg_date, fmt)
                    reg_date = dt.strftime("%d-%m-%Y")
                    break
                except ValueError:
                    pass

        # Parse Sub Stage
        sub_stage = ""
        status_table_match = re.search(r'<table[^>]+class="[^"]*case_status_table[^"]*".*?</table>', html_content, re.DOTALL | re.IGNORECASE)
        if status_table_match:
            status_match = re.search(r'Case Status.*?</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>', status_table_match.group(0), re.DOTALL | re.IGNORECASE)
            if status_match:
                sub_stage = re.sub(r'<[^>]+>', '', status_match.group(2)).strip()

        # Update case
        case_was_modified = False
        old_reg_date = case.get("registration_date", "")
        old_sub_stage = case.get("sub_stage", "")

        # Safe update: Registration Date
        if reg_date and not old_reg_date:
            case["registration_date"] = reg_date
            reg_recovered += 1
            case_was_modified = True
            detailed_log.append((case_number, cnr, "registration_date", "", reg_date))
        
        # Safe update: Sub Stage
        if sub_stage and not old_sub_stage:
            case["sub_stage"] = sub_stage
            
            # Also update in extra_metadata
            extra = {}
            if case.get("extra_metadata"):
                try:
                    extra = json.loads(case["extra_metadata"])
                except:
                    pass
            extra["case_sub_stage"] = sub_stage
            case["extra_metadata"] = json.dumps(extra, ensure_ascii=False)
            
            sub_stages_recovered += 1
            case_was_modified = True
            detailed_log.append((case_number, cnr, "sub_stage", "", sub_stage))

        if case_was_modified:
            cases_modified += 1

    # 3. Write modified cases.json
    with open(cases_json_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)
    print(f"Saved modified cases.json to {cases_json_path}")

    # 4. Phase 1 Validation Checks
    print("\nRunning validations...")
    errors = []
    
    # Check 1: Exactly 140 cases
    if len(cases) != 140:
        errors.append(f"Validation failed: expected exactly 140 cases, got {len(cases)}")
        
    # Check 2: Registration Date missing count is 0
    missing_reg = sum(1 for c in cases if not c.get("registration_date"))
    if missing_reg > 0:
        errors.append(f"Validation failed: {missing_reg} cases are still missing registration_date")
        
    # Check 3: Sub Stage missing count is 0
    missing_sub = sum(1 for c in cases if not c.get("sub_stage"))
    if missing_sub > 0:
        errors.append(f"Validation failed: {missing_sub} cases are still missing sub_stage")

    # Check 4: No other data changed
    for c in cases:
        cnr = c.get("cnr")
        if cnr not in original_data_map:
            errors.append(f"Validation failed: CNR {cnr} was added or modified")
            continue
        orig = original_data_map[cnr]
        
        # Compare key fields to make sure they are unchanged
        fields_to_check = [
            "case_number", "cnr", "appellant", "respondent", "petitioner_advocates", 
            "respondent_advocates", "sections", "history_count", "order_count", "orders_json"
        ]
        for fld in fields_to_check:
            if c.get(fld) != orig.get(fld):
                errors.append(f"Validation failed for case {c.get('case_number')}: Field '{fld}' changed!")

    if errors:
        print("\n".join(errors))
        print("VALIDATION_STATUS: FAILED")
    else:
        print("VALIDATION_STATUS: PASSED")

    # 5. Generate snapshot_repair_report_140.md
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"""# snapshot_repair_report_140.md

## Phase 1 Execution Details
- **Cases audited**: 140
- **Registration Dates recovered**: {reg_recovered}
- **Sub Stages recovered**: {sub_stages_recovered}
- **Cases modified**: {cases_modified}
- **Unexpected failures**: {unexpected_failures}
- **Validation status**: {"PASSED" if not errors else "FAILED"}

## Detailed Log of Modifications
| Case | CNR | Field | Old Value | New Value | Source |
|------|-----|-------|-----------|-----------|--------|
""")
        for log in detailed_log:
            f.write(f"| {log[0]} | {log[1]} | {log[2]} | {log[3]} | {log[4]} | HTML Snapshot |\n")

    print(f"\nGenerated report: {report_path}")

if __name__ == "__main__":
    run_phase1_repair()
