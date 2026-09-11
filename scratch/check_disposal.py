import pandas as pd
import os

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

cases = pd.read_csv(os.path.join(dir_path, "cases.csv"))
orders = pd.read_csv(os.path.join(dir_path, "orders(1).csv"))

# Merge on cnr and case_number
merged = pd.merge(cases, orders, on=['cnr', 'case_number'])

print("Total rows:", len(merged))
diff_disposal = merged[merged['nature_of_disposal_x'] != merged['nature_of_disposal_y']]
print("Differences in nature_of_disposal:", len(diff_disposal))
if len(diff_disposal) > 0:
    print(diff_disposal[['cnr', 'nature_of_disposal_x', 'nature_of_disposal_y']].head(5))

diff_date = merged[merged['disposal_date_x'] != merged['disposal_date_y']]
print("Differences in disposal_date:", len(diff_date))
if len(diff_date) > 0:
    print(diff_date[['cnr', 'disposal_date_x', 'disposal_date_y']].head(5))
