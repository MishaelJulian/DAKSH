import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

cases = pd.read_csv(os.path.join(dir_path, "cases.csv"))
business = pd.read_csv(os.path.join(dir_path, "business(1).csv"))
history = pd.read_csv(os.path.join(dir_path, "case_history(1).csv"))
orders = pd.read_csv(os.path.join(dir_path, "orders(1).csv"))
processes = pd.read_csv(os.path.join(dir_path, "processes(1).csv"))
transfers = pd.read_csv(os.path.join(dir_path, "transfers(1).csv"))

# Standardize dates
history['date_std'] = pd.to_datetime(history['hearing_date'], format='%d-%m-%Y', errors='coerce')
business['date_std'] = pd.to_datetime(business['business_date'], format='%d/%m/%Y', errors='coerce')
orders['date_std'] = pd.to_datetime(orders['order_date'], format='%d-%m-%Y', errors='coerce')
processes['date_std'] = pd.to_datetime(processes['process_date'], format='%d/%m/%Y', errors='coerce')
transfers['date_std'] = pd.to_datetime(transfers['transfer_date'], format='%d/%m/%Y', errors='coerce')

# Merge
merged_hb = pd.merge(history, business, left_on=['cnr', 'case_number', 'history_index'], right_on=['cnr', 'case_number', 'business_index'], how='outer')
merged_hbo = pd.merge(merged_hb, orders, left_on=['cnr', 'case_number', 'history_index'], right_on=['cnr', 'case_number', 'order_index'], how='outer')
merged_hbo_p = pd.merge(merged_hbo, processes, on=['cnr', 'case_number', 'date_std'], how='left')
merged_all = pd.merge(merged_hbo_p, transfers, on=['cnr', 'case_number', 'date_std'], how='left')
final_df = pd.merge(cases, merged_all, on=['cnr', 'case_number'], how='right')

print("All columns in merged df:")
for c in final_df.columns:
    print("  ", c)

print("\nComparing overlapping columns:")
overlap_cols = ['order_number', 'judge']
for col in overlap_cols:
    col_x = col + "_x" # from history
    col_y = col + "_y" # from orders
    if col_x in final_df.columns and col_y in final_df.columns:
        diffs = final_df[final_df[col_x] != final_df[col_y]]
        print(f"Differences in {col}: {len(diffs)} rows out of {len(final_df)}")
        if len(diffs) > 0:
            print(diffs[['cnr', 'history_index', col_x, col_y]].head(5))
