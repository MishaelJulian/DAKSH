import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

cases_df = pd.read_csv(os.path.join(dir_path, "cases.csv"))
business_df = pd.read_csv(os.path.join(dir_path, "business(1).csv"))
history_df = pd.read_csv(os.path.join(dir_path, "case_history(1).csv"))
orders_df = pd.read_csv(os.path.join(dir_path, "orders(1).csv"))
processes_df = pd.read_csv(os.path.join(dir_path, "processes(1).csv"))
transfers_df = pd.read_csv(os.path.join(dir_path, "transfers(1).csv"))

print("=== Case numbers and CNRs in cases.csv ===")
cases_cnrs = set(cases_df['cnr'].unique())
print(f"Total unique cases in cases.csv: {len(cases_cnrs)}")

print("\n=== Row count per case in child tables ===")
records = []
for idx, row in cases_df.iterrows():
    cnr = row['cnr']
    case_num = row['case_number']
    
    b_count = len(business_df[business_df['cnr'] == cnr])
    h_count = len(history_df[history_df['cnr'] == cnr])
    o_count = len(orders_df[orders_df['cnr'] == cnr])
    p_count = len(processes_df[processes_df['cnr'] == cnr])
    t_count = len(transfers_df[transfers_df['cnr'] == cnr])
    
    records.append({
        'cnr': cnr,
        'case_number': case_num,
        'business': b_count,
        'history': h_count,
        'orders': o_count,
        'processes': p_count,
        'transfers': t_count
    })

counts_df = pd.DataFrame(records)
print(counts_df)

print("\n=== Checking CNRs in child tables ===")
for name, df in [('business', business_df), ('history', history_df), ('orders', orders_df), ('processes', processes_df), ('transfers', transfers_df)]:
    df_cnrs = set(df['cnr'].unique())
    orphans = df_cnrs - cases_cnrs
    print(f"Orphans in {name}: {orphans}")
