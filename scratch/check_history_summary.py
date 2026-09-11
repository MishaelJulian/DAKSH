import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"
history_df = pd.read_csv(os.path.join(dir_path, "case_history(1).csv"))

non_business = history_df[history_df['business_summary'] != 'Business']
print(f"Total rows in history: {len(history_df)}")
print(f"Rows where business_summary != 'Business': {len(non_business)}")

if len(non_business) > 0:
    print(non_business['business_summary'].value_counts())
    print("\nExample rows:")
    for idx, row in non_business.head(3).iterrows():
        print(f"Row {idx} (CNR: {row['cnr']}, index: {row['history_index']}):")
        print(f"  {row['business_summary'][:200]}")
