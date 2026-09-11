import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

processes_df = pd.read_csv(os.path.join(dir_path, "processes(1).csv"))
transfers_df = pd.read_csv(os.path.join(dir_path, "transfers(1).csv"))

processes_df['date_std'] = pd.to_datetime(processes_df['process_date'], format='%d/%m/%Y', errors='coerce')
transfers_df['date_std'] = pd.to_datetime(transfers_df['transfer_date'], format='%d/%m/%Y', errors='coerce')

overlap = pd.merge(processes_df, transfers_df, on=['cnr', 'date_std'])
print(f"Overlap rows: {len(overlap)}")
if len(overlap) > 0:
    print(overlap)
