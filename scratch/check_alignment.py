import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

history_df = pd.read_csv(os.path.join(dir_path, "case_history(1).csv"))
business_df = pd.read_csv(os.path.join(dir_path, "business(1).csv"))
orders_df = pd.read_csv(os.path.join(dir_path, "orders(1).csv"))

# Verify lengths are equal
print(f"history: {len(history_df)}, business: {len(business_df)}, orders: {len(orders_df)}")

# Check row-by-row matching
mismatches = 0
for idx in range(len(history_df)):
    h_row = history_df.iloc[idx]
    b_row = business_df.iloc[idx]
    o_row = orders_df.iloc[idx]
    
    # Check if CNR matches
    if h_row['cnr'] != b_row['cnr'] or h_row['cnr'] != o_row['cnr']:
        print(f"Row {idx}: CNR mismatch! H:{h_row['cnr']}, B:{b_row['cnr']}, O:{o_row['cnr']}")
        mismatches += 1
        continue
        
    # Check if indexes match
    if h_row['history_index'] != b_row['business_index'] or h_row['history_index'] != o_row['order_index']:
        print(f"Row {idx}: Index mismatch! H:{h_row['history_index']}, B:{b_row['business_index']}, O:{o_row['order_index']}")
        mismatches += 1
        continue
        
    # Standardize dates
    h_date = pd.to_datetime(h_row['hearing_date'], format='%d-%m-%Y', errors='coerce')
    b_date = pd.to_datetime(b_row['business_date'], format='%d/%m/%Y', errors='coerce')
    o_date = pd.to_datetime(o_row['order_date'], format='%d-%m-%Y', errors='coerce')
    
    if h_date != b_date or h_date != o_date:
        print(f"Row {idx} ({h_row['cnr']}, index {h_row['history_index']}): Date mismatch! H:{h_row['hearing_date']}, B:{b_row['business_date']}, O:{o_row['order_date']}")
        mismatches += 1

print(f"Total mismatches: {mismatches}")
