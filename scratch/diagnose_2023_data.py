import json
from pathlib import Path

data_dir = Path(r"c:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023")
checkpoint_file = data_dir / "checkpoint_2023.json"
cases_file = data_dir / "cases.json"

if checkpoint_file.exists():
    with open(checkpoint_file, "r", encoding="utf-8") as f:
        cp = json.load(f)
    print(f"Checkpoint last page: {cp.get('last_page')}")
    print(f"Checkpoint cases count: {len(cp.get('cases', []))}")
    print(f"Checkpoint completed CNRs count: {len(cp.get('completed_cnrs', []))}")
    if cp.get('cases'):
        print(f"Last 5 cases in checkpoint: {[c.get('case_number') for c in cp['cases'][-5:]]}")

if cases_file.exists():
    with open(cases_file, "r", encoding="utf-8") as f:
        cases = json.load(f)
    print(f"Cases.json count: {len(cases)}")
    if cases:
        print(f"Last 5 cases in cases.json: {[c.get('case_number') for c in cases[-5:]]}")
