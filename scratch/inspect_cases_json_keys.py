import json
from pathlib import Path

cases_json_path = Path("data/cases.json")
if cases_json_path.exists():
    with open(cases_json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
    if cases:
        print("First case keys:")
        for k, v in cases[0].items():
            print(f"  {k}: {type(v)} -> {str(v)[:100]}")
