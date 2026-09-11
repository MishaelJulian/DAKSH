import json

with open('test_output/EX_2_2023/case.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total Case History rows: {len(data['case_history'])}")
for i, h in enumerate(data['case_history']):
    print(f"{i+1:02d}: Judge={h['judge']} | Business={h['business_date']} | Hearing={h['hearing_date']} | Purpose={h['purpose_of_hearing']}")

print(f"\nTotal Daily Status rows: {len(data['daily_status'])}")
for i, d in enumerate(data['daily_status']):
    print(f"{i+1:02d}: Date={d['date']} | NextPurpose={d['next_purpose']} | NextHearingDate={d['next_hearing_date']} | NatureOfDisposal={d['nature_of_disposal']} | Business={d['business'][:50]}...")
