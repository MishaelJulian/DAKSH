import json
import pandas as pd

with open('test_output/EX_2_2023/case.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

hist = d['case_history']
daily = d['daily_status']
print(f'Hist: {len(hist)}, Daily: {len(daily)}')

for i in range(len(hist)):
    h = hist[i]
    b = daily[i]
    print(f"Row {i+1:2d} | Hist b_date: {h.get('business_date')} | Hist h_date: {h.get('hearing_date')} | Daily date: {b.get('date')} | Daily next_date: {b.get('next_hearing_date')}")
