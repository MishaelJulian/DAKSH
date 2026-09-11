import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

files = [
    "cases.csv",
    "business(1).csv",
    "case_history(1).csv",
    "orders(1).csv",
    "processes(1).csv",
    "transfers(1).csv"
]

print("=== SCHEMAS AND ROW COUNTS ===")
dfs = {}
for f in files:
    path = os.path.join(dir_path, f)
    if os.path.exists(path):
        df = pd.read_csv(path)
        dfs[f] = df
        print(f"{f}: {len(df)} rows")
        print("Columns:", list(df.columns))
        print(df.head(2))
        print("-" * 50)
    else:
        print(f"{f} does not exist!")

# Let's inspect alignment of business(1).csv, case_history(1).csv, and orders(1).csv for EX/1/2010
print("=== ALIGNMENT CHECK FOR EX/1/2010 ===")
cnr = "KABC010069632010"
if "business(1).csv" in dfs and "case_history(1).csv" in dfs and "orders(1).csv" in dfs:
    bh = dfs["business(1).csv"][dfs["business(1).csv"]["cnr"] == cnr].sort_values("business_index")
    ch = dfs["case_history(1).csv"][dfs["case_history(1).csv"]["cnr"] == cnr].sort_values("history_index")
    od = dfs["orders(1).csv"][dfs["orders(1).csv"]["cnr"] == cnr].sort_values("order_index")
    
    print(f"Business rows for {cnr}: {len(bh)}")
    print(f"History rows for {cnr}: {len(ch)}")
    print(f"Order rows for {cnr}: {len(od)}")
    
    # Check if they align row-by-row
    min_len = min(len(bh), len(ch), len(od))
    for i in range(min_len):
        b_row = bh.iloc[i]
        c_row = ch.iloc[i]
        o_row = od.iloc[i]
        print(f"Index {i+1}:")
        print(f"  Hist Date: {c_row['hearing_date']} | Order Num: {c_row['order_number']}")
        print(f"  Bus Date : {b_row['business_date']} | Bus Label: {b_row['business_label']}")
        print(f"  Ord Date : {o_row['order_date']} | Ord Num: {o_row['order_number']}")
        if i >= 4:
            print("...")
            break
