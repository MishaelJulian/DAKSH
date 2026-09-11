import json
import csv

with open('test_output/EX_2_2023/case.json', 'r', encoding='utf-8') as f:
    cj = json.load(f)

print("Checking daily_status items in case.json:")
for i, ds in enumerate(cj['daily_status']):
    b = ds.get('business', '')
    has_cr = '\r' in b
    has_lf = '\n' in b
    has_comma = ',' in b
    has_quote = '"' in b
    print(f"Row {i+1:2d} | len={len(b):3d} | comma={has_comma} | quote={has_quote} | cr={has_cr} | lf={has_lf}")
    if has_cr or has_lf:
        print(f"  --> RAW: {repr(b)}")
