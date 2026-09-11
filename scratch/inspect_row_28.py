import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

history_df = pd.read_csv(os.path.join(dir_path, "case_history(1).csv"))
business_df = pd.read_csv(os.path.join(dir_path, "business(1).csv"))
orders_df = pd.read_csv(os.path.join(dir_path, "orders(1).csv"))

cnr = "KABC010069632010"
idx = 28

h_row = history_df[(history_df['cnr'] == cnr) & (history_df['history_index'] == idx)].iloc[0]
b_row = business_df[(business_df['cnr'] == cnr) & (business_df['business_index'] == idx)].iloc[0]
o_row = orders_df[(orders_df['cnr'] == cnr) & (orders_df['order_index'] == idx)].iloc[0]

print("=== HISTORY ROW ===")
for col in history_df.columns:
    print(f"{col}: {h_row[col]}")

print("\n=== BUSINESS ROW ===")
for col in business_df.columns:
    print(f"{col}: {b_row[col]}")

print("\n=== ORDER ROW ===")
for col in orders_df.columns:
    print(f"{col}: {o_row[col]}")
