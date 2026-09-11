import json

with open(r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\cases.json", "r", encoding="utf-8") as f:
    cases = json.load(f)

case = cases[0]
print("Top-level keys in cases.json record:")
print(list(case.keys()))

print("\nValue of 'extra_metadata' (type):", type(case.get("extra_metadata")))
if isinstance(case.get("extra_metadata"), str):
    try:
        meta = json.loads(case["extra_metadata"])
        print("Keys inside extra_metadata string:")
        print(list(meta.keys()))
    except Exception as e:
        print("Error parsing extra_metadata:", e)
elif isinstance(case.get("extra_metadata"), dict):
    print("Keys inside extra_metadata dict:")
    print(list(case["extra_metadata"].keys()))

print("\nValue of 'orders_json' (type):", type(case.get("orders_json")))
if isinstance(case.get("orders_json"), str):
    try:
        orders = json.loads(case["orders_json"])
        print(f"Number of orders inside orders_json: {len(orders)}")
        if orders:
            print("Keys inside first order:")
            print(list(orders[0].keys()))
    except Exception as e:
        print("Error parsing orders_json:", e)
