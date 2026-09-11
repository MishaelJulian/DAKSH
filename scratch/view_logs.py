from pathlib import Path
import re

log_path = Path("logs/ecourts_scraper.log")
if not log_path.exists():
    print("Log file not found!")
    exit(1)

print("Reading log...")
with open(log_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Let's search for "Extracted history details" or similar messages
history_matches = re.findall(r"Extracted history details.*", content)
print(f"Found {len(history_matches)} history extraction log lines.")
for m in history_matches[:10]:
    print("  -", m)

# Let's check if there are other log lines showing the content of business/order text
business_matches = re.findall(r"business_text.*", content, re.IGNORECASE)
print(f"Found {len(business_matches)} business_text log lines.")

pdf_matches = re.findall(r"Downloaded PDF successfully.*", content)
print(f"Found {len(pdf_matches)} PDF download log lines.")
for m in pdf_matches[:10]:
    print("  -", m)
