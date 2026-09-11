import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

history_df = pd.read_csv(os.path.join(dir_path, "case_history(1).csv"))
processes_df = pd.read_csv(os.path.join(dir_path, "processes(1).csv"))
transfers_df = pd.read_csv(os.path.join(dir_path, "transfers(1).csv"))

print("=== CHECKING PROCESS DATES MATCH HEARING DATES ===")
# Note: processes date format is DD/MM/YYYY, history hearing_date is DD-MM-YYYY (let's standardize)
history_df['date_std'] = pd.to_datetime(history_df['hearing_date'], format='%d-%m-%Y', errors='coerce')
processes_df['date_std'] = pd.to_datetime(processes_df['process_date'], format='%d/%m/%Y', errors='coerce')

for idx, p_row in processes_df.iterrows():
    cnr = p_row['cnr']
    p_date = p_row['process_date']
    p_title = p_row['process_title']
    
    # Check if there is a hearing on this date for this cnr
    matches = history_df[(history_df['cnr'] == cnr) & (history_df['date_std'] == p_row['date_std'])]
    print(f"Process: {cnr} on {p_date} ({p_title}) -> Matched hearings: {len(matches)}")
    if len(matches) > 0:
        print(matches[['history_index', 'hearing_date', 'order_number']])

print("\n=== CHECKING TRANSFER DATES MATCH HEARING DATES ===")
transfers_df['date_std'] = pd.to_datetime(transfers_df['transfer_date'], format='%d/%m/%Y', errors='coerce')

for idx, t_row in transfers_df.iterrows():
    cnr = t_row['cnr']
    t_date = t_row['transfer_date']
    t_from = t_row['from_court']
    t_to = t_row['to_court']
    
    matches = history_df[(history_df['cnr'] == cnr) & (history_df['date_std'] == t_row['date_std'])]
    print(f"Transfer: {cnr} on {t_date} ({t_from} -> {t_to}) -> Matched hearings: {len(matches)}")
    if len(matches) > 0:
        print(matches[['history_index', 'hearing_date', 'order_number']])
