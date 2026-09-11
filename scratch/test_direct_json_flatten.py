import json
import csv
from pathlib import Path

json_path = Path(r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010_Final\cases.json")

with open(json_path, "r", encoding="utf-8") as f:
    cases = json.load(f)

print(f"Loaded {len(cases)} cases from JSON.")

total_history = sum(len(c.get("history", [])) for c in cases)
total_orders = sum(len(c.get("orders", [])) for c in cases)
total_business = sum(len(c.get("business_list", [])) for c in cases)
total_processes = sum(len(c.get("processes", [])) for c in cases)
total_transfers = sum(len(c.get("transfers", [])) for c in cases)
total_documents = sum(len(c.get("documents", [])) for c in cases)

print(f"Counts in cases.json:")
print(f"  History rows : {total_history}")
print(f"  Orders       : {total_orders}")
print(f"  Business     : {total_business}")
print(f"  Processes    : {total_processes}")
print(f"  Transfers    : {total_transfers}")
print(f"  Documents    : {total_documents}")
