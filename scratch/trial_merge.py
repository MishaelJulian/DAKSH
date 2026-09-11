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

# We know history, business, and orders are 1-to-1 aligned. Let's merge them first by index and CNR.
# Just to be absolutely safe, let's align them by index. We saw that they have exactly the same length and align 1-to-1.
# Let's merge history, business, and orders on 'cnr' and their index.
# In history, index is history_index
# In business, index is business_index
# In orders, index is order_index
merged_hb = pd.merge(history, business, left_on=['cnr', 'case_number', 'history_index'], right_on=['cnr', 'case_number', 'business_index'], how='outer')
merged_hbo = pd.merge(merged_hb, orders, left_on=['cnr', 'case_number', 'history_index'], right_on=['cnr', 'case_number', 'order_index'], how='outer')

print(f"Merged HBO rows: {len(merged_hbo)}")

# Now, let's join processes and transfers. Since processes can have multiple entries per date,
# let's merge processes onto merged_hbo by 'cnr' and 'date_std'.
# Wait, let's look at processes and transfers. If we merge processes by date_std:
# Does 'case_number' also match? Yes.
merged_hbo_p = pd.merge(merged_hbo, processes, on=['cnr', 'case_number', 'date_std'], how='left')
print(f"After processes merge, rows: {len(merged_hbo_p)}")

# Merge transfers by cnr, case_number, and date_std
merged_all = pd.merge(merged_hbo_p, transfers, on=['cnr', 'case_number', 'date_std'], how='left')
print(f"After transfers merge, rows: {len(merged_all)}")

# Let's join the parent case metadata from 'cases'
# cases has columns like: cnr, case_number, ...
# Let's merge cases onto merged_all
final_df = pd.merge(cases, merged_all, on=['cnr', 'case_number'], how='right')
print(f"Final merged rows: {len(final_df)}")

# Let's verify that we didn't lose any source records.
# Unique cases:
print(f"Unique cases in final: {final_df['cnr'].nunique()}")
# History rows: each history row is represented by a unique combination of cnr and history_index.
# Let's verify if all (cnr, history_index) combinations in history exist in final_df.
h_keys = set(zip(history['cnr'], history['history_index']))
final_h_keys = set(zip(final_df['cnr'], final_df['history_index']))
missing_h = h_keys - final_h_keys
print(f"Missing history records: {len(missing_h)}")

# Business rows:
b_keys = set(zip(business['cnr'], business['business_index']))
final_b_keys = set(zip(final_df['cnr'], final_df['business_index']))
missing_b = b_keys - final_b_keys
print(f"Missing business records: {len(missing_b)}")

# Orders rows:
o_keys = set(zip(orders['cnr'], orders['order_index']))
final_o_keys = set(zip(final_df['cnr'], final_df['order_index']))
missing_o = o_keys - final_o_keys
print(f"Missing order records: {len(missing_o)}")

# Processes rows:
p_keys = set(zip(processes['cnr'], processes['process_id']))
final_p_keys = set(zip(final_df['cnr'], final_df['process_id']))
missing_p = {k for k in p_keys if not pd.isna(k[1])} - {k for k in final_p_keys if not pd.isna(k[1])}
print(f"Missing process records: {len(missing_p)}")

# Transfers rows:
# Since transfers don't have a unique ID, let's check by registration_number and transfer_date
t_keys = set(zip(transfers['cnr'], transfers['transfer_date'], transfers['from_court'], transfers['to_court']))
final_t_keys = set(zip(final_df['cnr'], final_df['transfer_date'], final_df['from_court'], final_df['to_court']))
missing_t = t_keys - final_t_keys
print(f"Missing transfer records: {len(missing_t)}")
