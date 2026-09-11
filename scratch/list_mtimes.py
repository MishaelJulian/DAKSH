import os
import datetime
from pathlib import Path

data_dir = Path("data")
for p in sorted(data_dir.rglob("*")):
    if p.is_file():
        mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime)
        size = p.stat().st_size
        print(f"{p}: size={size} bytes, mtime={mtime}")
