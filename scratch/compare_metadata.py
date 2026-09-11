import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

cases = pd.read_csv(os.path.join(dir_path, "cases.csv"))
master = pd.read_csv(os.path.join(dir_path, "Executive_Petitions_2010_Master.csv"))

print("Cases columns:", list(cases.columns))
print("Master columns:", list(master.columns))

# Compare case list
print(f"Cases in cases.csv: {len(cases)}, in master: {len(master)}")
cases_cnrs = set(cases['cnr'].unique())
master_cnrs = set(master['cnr'].unique())
print(f"Difference (cases - master): {cases_cnrs - master_cnrs}")
print(f"Difference (master - cases): {master_cnrs - cases_cnrs}")

# Compare specific fields like court_complex, registration_number, etc.
merged = pd.merge(cases, master, on='cnr', suffixes=('_cases', '_master'))
print("\nFirst row comparison:")
for col in ['court_complex', 'registration_number', 'filing_date', 'registration_date', 'petitioner', 'respondent']:
    col_cases = col + '_cases' if col + '_cases' in merged.columns else col
    col_master = col + '_master' if col + '_master' in merged.columns else col
    
    val_c = merged.iloc[0][col_cases] if col_cases in merged.columns else "N/A"
    val_m = merged.iloc[0][col_master] if col_master in merged.columns else "N/A"
    print(f"Field: {col}")
    print(f"  cases.csv: {val_c}")
    print(f"  master.csv: {val_m}")
