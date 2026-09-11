import json
import pandas as pd

with open('test_output/EX_2_2023/case.json', 'r', encoding='utf-8') as f:
    cj = json.load(f)

csv_df = pd.read_csv('Consolidated_Executive_Petitions_2023_FINAL.csv', dtype=str)
ex2_csv = csv_df[csv_df['Case Number'] == 'EX/2/2023']

for i in range(32):
    csv_text = ex2_csv.iloc[i]['Business Text']
    ds = cj['daily_status'][i]
    
    # Let's see what components build up csv_text
    parts = []
    parts.append(f"Back Daily Status {ds.get('establishment', '')}")
    parts.append(f"In the court of :{ds.get('judge', '')}")
    parts.append(f"CNR Number :{ds.get('cnr', '')}")
    parts.append(f"Case Number :{ds.get('case_number', '')}")
    parts.append(f"{ds.get('case_title', '')}")
    parts.append(f"Date : {ds.get('date', '')}")
    parts.append(f"Business : {ds.get('business', '')}")
    
    if ds.get('nature_of_disposal'):
        parts.append(f"Nature of Disposal : {ds.get('nature_of_disposal')}")
    if ds.get('disposal_date'):
        parts.append(f"Disposal Date : {ds.get('disposal_date')}")
    if ds.get('signing_judge') and ds.get('nature_of_disposal'):
        parts.append(f"{ds.get('signing_judge')}")
        
    if ds.get('next_purpose'):
        parts.append(f"Next Purpose : {ds.get('next_purpose')}")
    if ds.get('next_hearing_date'):
        parts.append(f"Next Hearing Date : {ds.get('next_hearing_date')}")
    if ds.get('signing_judge') and not ds.get('nature_of_disposal'):
        parts.append(f"{ds.get('signing_judge')}")
        
    reconstructed = " ".join(p.strip() for p in parts if p.strip())
    match = (csv_text == reconstructed)
    print(f"Row {i+1:2d} match: {match}")
    if not match:
        print(f"  CSV:  {repr(csv_text)}")
        print(f"  RECON:{repr(reconstructed)}")
