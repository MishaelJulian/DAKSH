import json
from pathlib import Path

cases_json_path = Path("data/cases.json")
if not cases_json_path.exists():
    print("data/cases.json does not exist!")
    exit(1)

with open(cases_json_path, "r", encoding="utf-8") as f:
    cases = json.load(f)

for idx, c in enumerate(cases, 1):
    orders_json_val = c.get("orders_json")
    orders_len = len(c.get("orders", []))
    history_len = len(c.get("history", []))
    processes_len = len(c.get("processes", []))
    transfers_len = len(c.get("transfers", []))
    
    # Print summary
    print(f"Case {idx}: CNR={c.get('cnr')} CaseNumber={c.get('case_number')}")
    print(f"  orders_json = {orders_json_val}")
    print(f"  orders count = {orders_len}, history count = {history_len}, processes count = {processes_len}, transfers count = {transfers_len}")
