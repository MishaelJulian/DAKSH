import json
import os
import csv

base_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023"
cases_json_path = os.path.join(base_dir, "cases.json")
original_csv_path = os.path.join(base_dir, "Consolidated_Executive_Petitions_2023_before_140_repair_20260819_192325.csv")
target_csv_path = os.path.join(base_dir, "Consolidated_Executive_Petitions_2023.csv")

def update_csv():
    # 1. Load cases to get the mappings
    with open(cases_json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    case_map = {}
    for c in cases:
        cnr = c.get("cnr", "")
        if cnr:
            case_map[cnr] = {
                "registration_date": c.get("registration_date", ""),
                "sub_stage": c.get("sub_stage", "")
            }
            
    print(f"Loaded mappings for {len(case_map)} CNRs.")

    # 2. Read original CSV and write to target
    rows_updated = 0
    updated_rows_list = []
    
    with open(original_csv_path, "r", encoding="utf-8-sig", newline="") as f_in:
        reader = csv.reader(f_in)
        header = next(reader)
        updated_rows_list.append(header)
        
        # Find column indices
        cnr_idx = header.index("CNR")
        reg_date_idx = header.index("Registration Date")
        sub_stage_idx = header.index("Sub Stage")
        
        for row in reader:
            if not row:
                continue
            cnr = row[cnr_idx]
            if cnr in case_map:
                map_data = case_map[cnr]
                # Update only if they are not already set or we want to overwrite empty ones
                if map_data["registration_date"]:
                    row[reg_date_idx] = map_data["registration_date"]
                if map_data["sub_stage"]:
                    row[sub_stage_idx] = map_data["sub_stage"]
                rows_updated += 1
            updated_rows_list.append(row)
            
    # 3. Write back to the target CSV with UTF-8 BOM
    with open(target_csv_path, "w", encoding="utf-8-sig", newline="") as f_out:
        writer = csv.writer(f_out, quoting=csv.QUOTE_ALL)
        writer.writerows(updated_rows_list)
        
    print(f"Successfully updated {rows_updated} rows in-place.")
    print(f"Output CSV written to: {target_csv_path}")

if __name__ == "__main__":
    update_csv()
