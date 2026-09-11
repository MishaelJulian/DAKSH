import json
import re

with open(r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\cases.json", "r", encoding="utf-8") as f:
    cases = json.load(f)

cases_with_links = 0
total_orders_checked = 0
cases_with_transfers = 0
cases_with_reg_date = 0
cases_with_sub_stage = 0

for case in cases:
    try:
        orders = json.loads(case.get("orders_json", "[]") or "[]")
        total_orders_checked += len(orders)
        non_empty_links = [o for o in orders if o.get("order_link")]
        if non_empty_links:
            cases_with_links += 1
    except:
        pass
        
    extra = {}
    try:
        extra = json.loads(case.get("extra_metadata", "{}") or "{}")
    except:
        pass
        
    if extra.get("transfers"):
        cases_with_transfers += 1
        
    if case.get("registration_date"):
        cases_with_reg_date += 1
        
    sub_stage = case.get("sub_stage") or case.get("case_sub_stage")
    if sub_stage and sub_stage != "Sub Stage":
        cases_with_sub_stage += 1

print(f"Total cases: {len(cases)}")
print(f"Total orders: {total_orders_checked}")
print(f"Cases with order links: {cases_with_links}")
print(f"Cases with transfers: {cases_with_transfers}")
print(f"Cases with registration date: {cases_with_reg_date}")
print(f"Cases with sub stage: {cases_with_sub_stage}")
