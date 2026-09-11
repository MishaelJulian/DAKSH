import json
import pandas as pd

df = pd.read_csv('Consolidated_Executive_Petitions_2023_FINAL.csv', dtype=str)
print(f"Total columns: {len(df.columns)}")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")
