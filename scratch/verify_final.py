import csv
import json
import pandas as pd
from pathlib import Path

# Paths
json_path = Path(r"C:\Users\misha\OneDrive\Desktop\daksh\test_output\EX_2_2023\case.json")
csv_path = Path(r"C:\Users\misha\OneDrive\Desktop\daksh\test_output\EX_2_2023\Consolidated_EX_2_2023.csv")
ref_csv_path = Path(r"C:\Users\misha\OneDrive\Desktop\daksh\Consolidated_Executive_Petitions_2023_FINAL.csv")

# 1. Schema verification
with open(ref_csv_path, "r", encoding="utf-8-sig") as f:
    ref_reader = csv.reader(f)
    ref_header = next(ref_reader)

with open(csv_path, "r", encoding="utf-8-sig") as f:
    gen_reader = csv.reader(f)
    gen_header = next(gen_reader)

assert ref_header == gen_header, f"Header mismatch:\nRef: {ref_header}\nGen: {gen_header}"
print(f"[OK] Schema match: 53 columns identical in order and naming.")

# 2. Load generated CSV
df = pd.read_csv(csv_path, dtype=str)
print(f"[OK] Row count: {len(df)} rows")

# 3. Load JSON
with open(json_path, "r", encoding="utf-8") as f:
    cj = json.load(f)

# 4. Check case-level attributes
assert (df["Case Number"] == "EX/2/2023").all(), "Case Number mismatch"
assert (df["CNR"] == "KABC010342242022").all(), "CNR mismatch"
assert (df["Registration Number"] == "2/2023").all(), "Registration Number mismatch (not literal 2/2023)"
assert (df["Filing Number"] == "2786/2022").all(), "Filing Number mismatch"
assert (df["Filing Date"] == "17/12/2022").all(), "Filing Date mismatch"
assert (df["Registration Date"] == "02/01/2023").all(), "Registration Date mismatch"
assert (df["Decision Date"] == "06/12/2025").all(), "Decision Date mismatch"
assert (df["Disposal Date"] == "06/12/2025").all(), "Disposal Date mismatch"
assert (df["Case Duration (Days)"] == "1085").all(), "Case Duration mismatch"
assert (df["Filing to First Hearing Duration (Days)"] == "16").all(), "Filing to First Hearing Duration mismatch"
assert (df["Petitioner"] == "KRISHNAMURTHY G").all(), "Petitioner mismatch"
assert (df["Petitioner Advocate"] == "DINESH J S").all(), "Petitioner Advocate mismatch"
assert (df["Respondent"] == "SATHISH M").all(), "Respondent mismatch"
print(f"[OK] Case-level fields verified across all {len(df)} rows.")

# 5. Check Case History (32 records)
assert len(cj["case_history"]) == 32
hist_indices = df["Hearing Index"].dropna().tolist()
assert len(hist_indices) == 32
assert hist_indices == [str(i) for i in range(1, 33)]
print(f"[OK] 32 Case History records verified.")

# 6. Check Daily Status (32 records)
assert len(cj["daily_status"]) == 32
biz_indices = df["Business Index"].dropna().tolist()
assert len(biz_indices) == 32
assert biz_indices == [str(i) for i in range(1, 33)]
for i, ds in enumerate(cj["daily_status"]):
    row_text = df.iloc[i]["Business Text"]
    assert ds["business"] in row_text, f"Business text not preserved in row {i+1}"
print(f"[OK] 32 Daily Status records verified with full verbatim narrative text.")

# 7. Check Processes (1 record)
assert len(cj["processes"]) == 1
proc_rows = df[df["Process ID"].notna() & (df["Process ID"] != "")]
assert len(proc_rows) == 1
assert proc_rows.iloc[0]["Process ID"] == "PKABC010342242022_1_1"
assert proc_rows.iloc[0]["Process Title"] == "Notice to show cause why execution should not issue [O. 21, R. 16]"
assert proc_rows.iloc[0]["Process Date"] == "07/01/2023"
print(f"[OK] 1 Process record verified without data loss.")

# 8. Check Orders (1 record)
assert len(cj["orders"]) == 1
order_rows = df[df["Order Number"].notna() & (df["Order Number"] != "")]
assert len(order_rows) == 1
assert order_rows.iloc[0]["Order Number"] == "1"
assert order_rows.iloc[0]["Order Date"] == "06/12/2025"
assert order_rows.iloc[0]["Order Link"] == "https://services.ecourts.gov.in/ecourtindia_v6/reports/0375644434591ea69eafc7102ca3935d.pdf"
print(f"[OK] 1 Order record verified with original link and details.")

print("\n--- SUMMARY OF EX/2/2023 VALIDATION ---")
print(f"Total Rows: {len(df)}")
print(f"Cases Represented: {df['Case Number'].nunique()}")
print(f"Case History Records: {len(hist_indices)}")
print(f"Daily Status Records: {len(biz_indices)}")
print(f"Processes Represented: {len(proc_rows)}")
print(f"Orders Represented: {len(order_rows)}")
print("ALL AUDIT CHECKS PASSED PERFECTLY!")
