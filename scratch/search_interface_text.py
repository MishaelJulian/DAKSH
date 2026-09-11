import pandas as pd
import os
import re

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

files = {
    "business(1).csv": ["business_text"],
    "orders(1).csv": ["order_text"],
    "processes(1).csv": ["process_title"],
    "case_history(1).csv": ["business_summary"]
}

patterns = [
    r"\bBack\b",
    r"\bDaily Status\b",
    r"\bQR Code\b",
    r"\bNavigation\b",
    r"\bButton\b",
    r"\bCourt Name\b"
]

for filename, cols in files.items():
    path = os.path.join(dir_path, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"\nScanning {filename}...")
        for col in cols:
            if col in df.columns:
                series = df[col].astype(str)
                for pat in patterns:
                    matches = series[series.str.contains(pat, flags=re.IGNORECASE, na=False)]
                    if len(matches) > 0:
                        print(f"  Column '{col}' matches pattern '{pat}' ({len(matches)} times):")
                        for idx, val in matches.head(3).items():
                            print(f"    Row {idx}: {val[:150]}...")
