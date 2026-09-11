import pandas as pd
import os
import re

dir_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010"

history_df = pd.read_csv(os.path.join(dir_path, "case_history(1).csv"))
business_df = pd.read_csv(os.path.join(dir_path, "business(1).csv"))

def clean_text(text: str) -> str:
    if not isinstance(text, str) or not text:
        return ""
    
    # Normalise whitespace
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r'\s+', ' ', text).strip()
    
    # We can apply a series of regex replacements to strip the daily status header
    # Let's write a robust version
    
    # 1. Strip starting Back
    text = re.sub(r'^Back\b\s*', '', text, flags=re.IGNORECASE)
    # 2. Strip starting Daily Status
    text = re.sub(r'^Daily Status\b\s*', '', text, flags=re.IGNORECASE)
    # 3. Strip court complex name
    text = re.sub(r'^PRL\.\s+CITY\s+CIVIL\s+AND\s+SESSIONS\s+JUDGE\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^PRL\.\s+CITY\s+CIVIL\s+COURT\b\s*', '', text, flags=re.IGNORECASE)
    # 4. Strip "In the court of : ... CNR Number"
    text = re.sub(r'^In the court of\s*:\s*.*?\s*(?=CNR\s+Number)', '', text, flags=re.IGNORECASE)
    # 5. Strip "CNR Number : ... Case Number : ..."
    text = re.sub(r'^CNR\s+Number\s*:\s*[A-Z0-9]+\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Case\s+Number\s*:\s*[A-Z0-9_/]+\b\s*', '', text, flags=re.IGNORECASE)
    # 6. Strip "Petitioner versus Respondent Date : DD-MM-YYYY"
    text = re.sub(r'^.*?\s+versus\s+.*?\s+Date\s*:\s*\d{1,2}-\d{1,2}-\d{4}\s*', '', text, flags=re.IGNORECASE)
    # 7. Strip starting "Business : "
    text = re.sub(r'^Business\s*:\s*', '', text, flags=re.IGNORECASE)
    
    # General cleanup of UI words inside the text if they appear
    text = re.sub(r'\bBack\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bDaily Status\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bQR Code\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bView QR Code or Cause Title\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(Note the CNR number for future reference\)', '', text, flags=re.IGNORECASE)
    
    return re.sub(r'\s+', ' ', text).strip()

print("=== TESTING CLEANING OF HISTORIES ===")
non_biz_h = history_df[history_df['business_summary'] != 'Business']['business_summary'].unique()
print(f"Found {len(non_biz_h)} unique uncleaned histories.")
for val in non_biz_h[:5]:
    print("Original:", val[:120] + "...")
    print("Cleaned :", clean_text(val))
    print("-" * 50)

print("\n=== TESTING CLEANING OF BUSINESS LABELS ===")
non_biz_b = business_df[business_df['business_label'] != 'Business']['business_label'].unique()
print(f"Found {len(non_biz_b)} unique uncleaned business labels.")
for val in non_biz_b[:5]:
    print("Original:", val[:120] + "...")
    print("Cleaned :", clean_text(val))
    print("-" * 50)
