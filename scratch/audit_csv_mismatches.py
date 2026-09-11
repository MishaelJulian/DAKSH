import csv
import os

csv_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\Consolidated_Executive_Petitions_2023.csv"

def audit_csv():
    missing_purpose = []
    missing_business = []
    missing_order_text = []
    
    identical_count = 0
    total_text_rows = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2): # 1-based line number in file (header is line 1)
            cnr = row["CNR"]
            case_num = row["Case Number"]
            purpose = row["Purpose of Hearing"]
            bus_text = row["Business Text"]
            ord_text = row["Order Text"]
            
            if not purpose:
                missing_purpose.append((idx, cnr, case_num, row["Hearing Date"]))
                
            if not bus_text:
                missing_business.append((idx, cnr, case_num, row["Hearing Date"]))
                
            if not ord_text:
                missing_order_text.append((idx, cnr, case_num, row["Hearing Date"]))
                
            if bus_text or ord_text:
                total_text_rows += 1
                if bus_text.strip() == ord_text.strip() and bus_text.strip() != "":
                    identical_count += 1

    print(f"Total CSV Rows: {idx}")
    print(f"1. Empty Purpose of Hearing in CSV: {len(missing_purpose)}")
    for m in missing_purpose:
        print(f"   Line {m[0]}: Case {m[2]} (CNR: {m[1]}), Date: {m[3]}")
        
    print(f"2. Empty Business Text in CSV: {len(missing_business)}")
    for m in missing_business[:10]:
        print(f"   Line {m[0]}: Case {m[2]} (CNR: {m[1]}), Date: {m[3]}")
        
    print(f"3. Empty Order Text in CSV: {len(missing_order_text)}")
    for m in missing_order_text[:10]:
        print(f"   Line {m[0]}: Case {m[2]} (CNR: {m[1]}), Date: {m[3]}")

    print(f"4. Business Text == Order Text count: {identical_count}/{total_text_rows}")

if __name__ == "__main__":
    audit_csv()
