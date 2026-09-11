from bs4 import BeautifulSoup
import re

html_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\snapshots\case_EX_102_2023.html"

with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

print("--- Case Details Table ---")
details_table = soup.find("table", class_="case_details_table")
if details_table:
    for tr in details_table.find_all("tr"):
        print([td.get_text(strip=True) for td in tr.find_all(["td", "th"])])
else:
    print("Not found")

print("\n--- Case Status Table ---")
status_table = soup.find("table", class_="case_status_table")
if status_table:
    for tr in status_table.find_all("tr"):
        print([td.get_text(strip=True) for td in tr.find_all(["td", "th"])])
else:
    print("Not found")

print("\n--- Searching for 'Transfer' in text ---")
transfers = soup.find_all(text=re.compile(r'transfer', re.IGNORECASE))
print(f"Occurrences of 'transfer': {len(transfers)}")

print("\n--- Searching for 'Order' or links ---")
order_table = soup.find("table", class_="order_table")
if order_table:
    print("Order table found")
    for tr in order_table.find_all("tr")[:5]:
        print([td.get_text(strip=True) for td in tr.find_all(["td", "th"])])
        links = tr.find_all("a")
        if links:
            for l in links:
                print("  Link a tag:", l)
else:
    print("Order table not found")
