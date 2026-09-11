from pathlib import Path
from bs4 import BeautifulSoup

logs_dir = Path(r"c:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\logs")

for dump in logs_dir.glob("fail_dump_*.html"):
    content = dump.read_text(encoding="utf-8", errors="replace")
    if "Invalid Request" in content or "something wrong" in content:
        print(f"Match in {dump.name}: contains 'Invalid Request' / 'something wrong'")
        # Print a snippet around the error
        idx = content.find("Invalid Request")
        if idx != -1:
            print("Snippet:", content[max(0, idx-100):min(len(content), idx+200)])
        else:
            idx = content.find("something wrong")
            print("Snippet:", content[max(0, idx-100):min(len(content), idx+200)])
    else:
        print(f"{dump.name}: NO 'Invalid Request' found in HTML")
