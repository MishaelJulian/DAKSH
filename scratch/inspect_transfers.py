import os
import glob
from bs4 import BeautifulSoup

snapshots = glob.glob(r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\snapshots\case_*.html")
found = 0

for path in snapshots:
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    trans_table = soup.find("table", class_="transfer_table")
    if trans_table:
        found += 1
        print(f"Found transfer table in {os.path.basename(path)}:")
        for tr in trans_table.find_all("tr"):
            print([td.get_text(strip=True) for td in tr.find_all(["td", "th"])])
        if found >= 5:
            break

if found == 0:
    print("No transfer tables found in any HTML snapshots.")
