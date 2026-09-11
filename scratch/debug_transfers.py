import pandas as pd
import os

src_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

history = pd.read_csv(os.path.join(src_dir, "case_history(1).csv"))
transfers = pd.read_csv(os.path.join(src_dir, "transfers(1).csv"))

# Parse dates
history['date_std'] = pd.to_datetime(history['hearing_date'], format='%d-%m-%Y', errors='coerce')
transfers['date_std'] = pd.to_datetime(transfers['transfer_date'], format='%d/%m/%Y', errors='coerce')

print("Transfers date_std types and values:")
for idx, r in transfers.iterrows():
    print(f"CNR: {r['cnr']} | Case: {r['case_number']} | Date: {r['transfer_date']} | Parsed: {r['date_std']} | Type: {type(r['date_std'])}")

# Check if there is any exact matching row in history
for idx, r in transfers.iterrows():
    matches = history[(history['cnr'] == r['cnr']) & (history['date_std'] == r['date_std'])]
    print(f"Match for {r['cnr']} on {r['date_std']}: {len(matches)}")
    if len(matches) > 0:
        print("  History match info:")
        print(matches[['cnr', 'case_number', 'date_std']])
