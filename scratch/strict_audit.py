import csv
import json
import pandas as pd
from pathlib import Path

csv_path = Path(r"C:\Users\misha\OneDrive\Desktop\daksh\test_output\EX_2_2023\Consolidated_Executive_Petitions_2023_EX_2_2023.csv")
json_path = Path(r"C:\Users\misha\OneDrive\Desktop\daksh\test_output\EX_2_2023\case.json")
ref_csv_path = Path(r"C:\Users\misha\OneDrive\Desktop\daksh\Consolidated_Executive_Petitions_2023_FINAL.csv")

# 1. Parse using standard csv reader
with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

print(f"Total columns in header: {len(header)}")
assert len(header) == 53

# Verify every row has exactly 53 fields
for i, r in enumerate(rows):
    assert len(r) == 53, f"Row {i+1} has {len(r)} columns instead of 53"

print("All 32 rows parse with exact 53 columns using csv.reader!")

# 2. Check schema equality with reference CSV
with open(ref_csv_path, "r", encoding="utf-8-sig") as f:
    ref_header = next(csv.reader(f))

assert header == ref_header, "Header mismatch with reference CSV"
print("Schema matches reference CSV 100%!")

# 3. Check Order fields (row 0 has order 1, rows 1..31 have empty order fields)
dict_reader = [dict(zip(header, r)) for r in rows]
for i, r in enumerate(dict_reader):
    if i == 0:
        assert r["Order Number"] == "1"
        assert r["Order Date"] == "06/12/2025"
        assert r["Order Link"] == "https://services.ecourts.gov.in/ecourtindia_v6/reports/0375644434591ea69eafc7102ca3935d.pdf"
        assert r["Order Text"] == ""  # Zero hallucination from daily status!
        assert r["Order Nature of Disposal"] == ""
        assert r["Order Disposal Date"] == ""
        assert r["Order Judge"] == ""
    else:
        assert r["Order Number"] == ""
        assert r["Order Date"] == ""
        assert r["Order Link"] == ""
        assert r["Order Text"] == ""

print("Order fields verified: Exactly 1 order represented, zero bleed from daily status!")

# 4. Check Process fields
for i, r in enumerate(dict_reader):
    if i == 0:
        assert r["Process ID"] == "PKABC010342242022_1_1"
        assert r["Process Title"] == "Notice to show cause why execution should not issue [O. 21, R. 16]"
        assert r["Process Date"] == "07/01/2023"
    else:
        assert r["Process ID"] == ""

print("Process fields verified: Exactly 1 process represented!")

# 5. Check String typing
assert dict_reader[0]["Registration Number"] == "2/2023"
assert dict_reader[0]["Filing Number"] == "2786/2022"
assert dict_reader[0]["Case Number"] == "EX/2/2023"
assert dict_reader[0]["CNR"] == "KABC010342242022"
print("Literal string identifiers verified!")

# 6. Check Daily Status text retention
with open(json_path, "r", encoding="utf-8") as f:
    cj = json.load(f)

for i, ds in enumerate(cj["daily_status"]):
    assert ds["business"] in dict_reader[i]["Business Text"], f"Missing business text in row {i+1}"

print("All 32 Daily Status narratives 100% verified!")
