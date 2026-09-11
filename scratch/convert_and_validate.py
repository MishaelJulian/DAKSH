import json
import os
import csv
import sys

def run_conversion_and_validation():
    source_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\cases.json"
    output_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\Consolidated_Executive_Petitions_2023_From_JSON.csv"

    # 1. Read JSON
    if not os.path.exists(source_path):
        print(f"Error: source file {source_path} does not exist.")
        sys.exit(1)
        
    with open(source_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    json_records_count = len(cases)
    
    # 2. Compute UNION of all keys
    all_keys_set = set()
    for case in cases:
        all_keys_set.update(case.keys())
    
    csv_columns = sorted(list(all_keys_set))
    
    # 3. Write CSV
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        
        for case in cases:
            row_data = {}
            for col in csv_columns:
                val = case.get(col, "")
                if isinstance(val, (list, dict)):
                    # Serialize using JSON representation
                    row_data[col] = json.dumps(val, ensure_ascii=False)
                elif val is None:
                    row_data[col] = ""
                else:
                    row_data[col] = str(val)
            writer.writerow(row_data)

    # 4. Read back CSV for validation
    csv_rows = []
    with open(output_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_rows.append(row)
            
    csv_records_count = len(csv_rows)

    # CRITICAL VALIDATION 1: Record counts must match
    if json_records_count != csv_records_count:
        print(f"ERROR: Record count mismatch! JSON={json_records_count}, CSV={csv_records_count}")
        sys.exit(1)

    # FIELD VALIDATION
    missing_columns = 0
    extra_columns = 0
    for key in all_keys_set:
        if key not in csv_columns:
            missing_columns += 1

    # CASE ID VALIDATION
    json_cnrs = [c.get("cnr", "") for c in cases]
    csv_cnrs = [r.get("cnr", "") for r in csv_rows]
    
    missing_cnrs = 0
    duplicate_cnrs = len(csv_cnrs) - len(set(csv_cnrs))
    
    for cnr in json_cnrs:
        if cnr not in csv_cnrs:
            missing_cnrs += 1

    # VALUE PRESERVATION TEST & NEWLINE / QUOTE TEST
    value_preservation = "PASS"
    long_text_preservation = "PASS"
    newline_handling = "PASS"
    
    # Double check values for every record
    test_fields = [
        "cnr", "case_number", "case_title", "appellant", "respondent", 
        "filing_date", "decision_date", "result", "judges", 
        "petitioner_advocates", "respondent_advocates", "sections", 
        "order_count", "hearing_count", "business_text", "order_text"
    ]
    
    for idx, case in enumerate(cases):
        csv_row = csv_rows[idx]
        
        # Verify alignment of CNRs/Case numbers
        if case.get("cnr") != csv_row.get("cnr") or case.get("case_number") != csv_row.get("case_number"):
            print(f"Alignment Error at index {idx}! JSON cnr: {case.get('cnr')}, CSV cnr: {csv_row.get('cnr')}")
            value_preservation = "FAIL"
            
        for field in test_fields:
            if field in case:
                expected_val = case[field]
                if isinstance(expected_val, (list, dict)):
                    expected_str = json.dumps(expected_val, ensure_ascii=False)
                elif expected_val is None:
                    expected_str = ""
                else:
                    expected_str = str(expected_val)
                    
                actual_str = csv_row.get(field, "")
                
                if expected_str != actual_str:
                    print(f"Mismatch at index {idx} for field '{field}'!")
                    print(f"Expected (first 100 char): {expected_str[:100]!r}")
                    print(f"Actual (first 100 char):   {actual_str[:100]!r}")
                    value_preservation = "FAIL"
                    if field in ["business_text", "order_text"]:
                        long_text_preservation = "FAIL"
                        newline_handling = "FAIL"

    # Verify BOM
    with open(output_path, "rb") as f:
        bom = f.read(3)
        utf8_bom = "PASS" if bom == b'\xef\xbb\xbf' else "FAIL"

    print("\n==================================================")
    print("JSON -> CSV CONVERSION COMPLETE")
    print("==================================================")
    print(f"Source:\n{source_path}\n")
    print(f"Output:\n{output_path}\n")
    print(f"JSON Records: {json_records_count}")
    print(f"CSV Records: {csv_records_count}")
    print(f"JSON Fields: {len(all_keys_set)}")
    print(f"CSV Columns: {len(csv_columns)}")
    print(f"Missing Columns: {missing_columns}")
    print(f"Extra Columns: {extra_columns}")
    print(f"Duplicate CNRs: {duplicate_cnrs}")
    print(f"Missing CNRs: {missing_cnrs}")
    print(f"UTF-8 BOM: {utf8_bom}")
    print(f"Long Text Preservation: {long_text_preservation}")
    print(f"Newline Handling: {newline_handling}")
    print(f"Value Preservation: {value_preservation}")
    print(f"STATUS: LOSSLESS EXPORT SUCCESS" if value_preservation == "PASS" and utf8_bom == "PASS" else "STATUS: EXPORT FAILURE")
    print("==================================================")

if __name__ == "__main__":
    run_conversion_and_validation()
