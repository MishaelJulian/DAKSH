import json
import pandas as pd

with open('test_output/EX_2_2023/case.json', 'r', encoding='utf-8') as f:
    cj = json.load(f)

csv_df = pd.read_csv('Consolidated_Executive_Petitions_2023_FINAL.csv', dtype=str)
ex2_csv = csv_df[csv_df['Case Number'] == 'EX/2/2023']

print("--- Row 1 Comparison ---")
print("CSV Business Text:")
print(repr(ex2_csv.iloc[0]['Business Text']))
print("\nJSON daily_status[0]:")
print(json.dumps(cj['daily_status'][0], indent=2))

print("\n--- Row 2 Comparison ---")
print("CSV Business Text:")
print(repr(ex2_csv.iloc[1]['Business Text']))
print("\nJSON daily_status[1]:")
print(json.dumps(cj['daily_status'][1], indent=2))
