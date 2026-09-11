import pandas as pd
import json

df = pd.read_csv('Consolidated_Executive_Petitions_2023_FINAL.csv', dtype=str)
ex2_csv = df[df['Case Number'] == 'EX/2/2023']

print(f"Total rows in EX/2/2023: {len(ex2_csv)}")
for i in range(len(ex2_csv)):
    row = ex2_csv.iloc[i]
    print(f"\n--- Row {i+1} ---")
    for col in df.columns:
        val = row[col]
        if pd.notna(val) and val != "":
            # print if not case-level or if first row
            if i == 0 or col in ['Hearing Date', 'Hearing Index', 'Hearing Judge', 'Purpose of Hearing', 'Hearing Business Summary', 
                                'Business Date', 'Business Index', 'Business Text', 'Order Date', 'Order Index', 'Order Number', 
                                'Order Link', 'Order Nature of Disposal', 'Order Disposal Date', 'Order Judge', 'Order Text', 
                                'Order Document Count', 'Process ID', 'Process Title', 'Process Date', 
                                'Transfer Registration Number', 'Transfer Date', 'Transfer From Court', 'Transfer To Court', 'Documents']:
                val_str = str(val)
                if len(val_str) > 60:
                    val_str = val_str[:57] + '...'
                print(f"  {col}: {val_str}")
