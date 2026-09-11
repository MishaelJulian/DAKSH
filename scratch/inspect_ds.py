import json

with open('test_output/EX_2_2023/case.json', 'r', encoding='utf-8') as f:
    cj = json.load(f)

for k, v in cj['daily_status'][0].items():
    print(f"{k}: {repr(v)}")
