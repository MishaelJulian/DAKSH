import pandas as pd
import os
import json

src_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"
json_path = r"C:\Users\misha\OneDrive\Desktop\daksh\data\cases.json"

cases_csv = pd.read_csv(os.path.join(src_dir, "cases.csv"))
master_csv = pd.read_csv(os.path.join(src_dir, "Executive_Petitions_2010_Master.csv"))
history = pd.read_csv(os.path.join(src_dir, "case_history(1).csv"))
business = pd.read_csv(os.path.join(src_dir, "business(1).csv"))
orders = pd.read_csv(os.path.join(src_dir, "orders(1).csv"))
processes = pd.read_csv(os.path.join(src_dir, "processes(1).csv"))
transfers = pd.read_csv(os.path.join(src_dir, "transfers(1).csv"))

with open(json_path, 'r', encoding='utf-8') as f:
    cases_json_data = json.load(f)
cases_json_df = pd.DataFrame(cases_json_data)

# Let's standardize dates for child tables
history['date_std'] = pd.to_datetime(history['hearing_date'], format='%d-%m-%Y', errors='coerce')
business['date_std'] = pd.to_datetime(business['business_date'], format='%d/%m/%Y', errors='coerce')
orders['date_std'] = pd.to_datetime(orders['order_date'], format='%d-%m-%Y', errors='coerce')
processes['date_std'] = pd.to_datetime(processes['process_date'], format='%d/%m/%Y', errors='coerce')
transfers['date_std'] = pd.to_datetime(transfers['transfer_date'], format='%d/%m/%Y', errors='coerce')

# Merge child tables
hb_merged = pd.merge(history, business, left_on=['cnr', 'case_number', 'history_index'], right_on=['cnr', 'case_number', 'business_index'], how='outer')
hbo_merged = pd.merge(hb_merged, orders, left_on=['cnr', 'case_number', 'history_index'], right_on=['cnr', 'case_number', 'order_index'], how='outer')
hbo_p_merged = pd.merge(hbo_merged, processes, on=['cnr', 'case_number', 'date_std'], how='left')
child_records = pd.merge(hbo_p_merged, transfers, on=['cnr', 'case_number', 'date_std'], how='left')

# Merge parent tables
# Select columns properly this time
parent_meta = cases_json_df[['cnr', 'cnr_court_code', 'bench_code', 'type_code', 'cnr_case_number', 'cnr_year', 'bench_city', 'bench_state', 'case_status', 'result', 'judges', 'petitioner_advocates', 'respondent_advocates']].copy()

parent_meta = pd.merge(parent_meta, cases_csv[['cnr', 'court_name', 'case_title', 'filing_date', 'first_hearing_date', 'last_hearing_date', 'next_hearing_date', 'decision_date', 'case_sub_stage', 'nature_of_disposal', 'disposal_date', 'sections', 'case_duration_days', 'filing_to_first_hearing_days', 'scraped_at', 'source_file', 'case_type_label']], on='cnr', how='left')

parent_meta = pd.merge(parent_meta, master_csv[['cnr', 'court_complex', 'registration_number', 'registration_date', 'petitioner', 'petitioner_advocate', 'respondent', 'respondent_advocate', 'acts', 'filing_number']], on='cnr', how='left')

# Final merge
consolidated = pd.merge(parent_meta, child_records, on=['cnr'], how='right')

print("Consolidated columns:")
for c in consolidated.columns:
    print("  ", c)
