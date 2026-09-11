import json
import os
import re
from bs4 import BeautifulSoup

def find_next_case():
    base_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023"
    checkpoint_path = os.path.join(base_dir, "checkpoint_2023.json")
    html_path = os.path.join(base_dir, "snapshots", "search_results_page_1.html")
    
    # Load completed keys
    try:
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
            completed_cnrs = set(checkpoint.get("completed_cnrs", []))
    except Exception as e:
        print(f"Error loading checkpoint: {e}")
        return

    # Parse search_results_page_1.html
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
    except Exception as e:
        print(f"Error loading html: {e}")
        return

    tables = soup.find_all("table")
    target_table = None
    for t in tables:
        txt = t.get_text()
        if "Petitioner Name versus Respondent Name" in txt or "Case Type/Case Number/Case Year" in txt:
            target_table = t
            break

    if not target_table:
        print("Results table not found in HTML!")
        return

    rows = target_table.find_all("tr")
    results = []
    view_index = 0
    for row in rows:
        if row.find("th"):
            continue
        cells = row.find_all("td")
        if any(c.get("colspan") and int(c.get("colspan")) > 1 for c in cells):
            continue
        if len(cells) < 3:
            continue
        sr_no = cells[0].get_text(strip=True)
        if not re.match(r'^\d+$', sr_no):
            continue
        case_number = cells[1].get_text(strip=True)
        parties = cells[2].get_text(strip=True)
        results.append({
            "serial_number": sr_no,
            "case_number": case_number,
            "parties": parties,
            "view_index": view_index
        })
        view_index += 1

    print(f"Total cases on page 1 html: {len(results)}")
    
    uncompleted = []
    for r in results:
        norm = re.sub(r'[^a-zA-Z0-9]', '', r["case_number"]).lower()
        if norm in completed_cnrs:
            continue
        uncompleted.append(r)
        
    print(f"Completed cases found on page 1: {len(results) - len(uncompleted)}")
    print(f"Uncompleted cases found on page 1: {len(uncompleted)}")
    if uncompleted:
        print("Next 5 uncompleted cases:")
        for idx, uc in enumerate(uncompleted[:5]):
            print(f"  {idx+1}. Serial: {uc['serial_number']}, Case Number: {uc['case_number']}, View Index: {uc['view_index']}")
    else:
        print("No uncompleted cases found on page 1 snapshot!")

if __name__ == "__main__":
    find_next_case()
