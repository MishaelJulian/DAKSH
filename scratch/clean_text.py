import re

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    # Replace newlines and tabs with spaces to normalize
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove "Back" button text at start (case insensitive, word bounded)
    text = re.sub(r'^Back\b\s*', '', text, flags=re.IGNORECASE)
    
    # Remove "Daily Status" heading at start
    text = re.sub(r'^Daily Status\b\s*', '', text, flags=re.IGNORECASE)
    
    # Remove court complex/establishment header at start
    text = re.sub(r'^PRL\.\s+CITY\s+CIVIL\s+AND\s+SESSIONS\s+JUDGE\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^PRL\.\s+CITY\s+CIVIL\s+COURT\b\s*', '', text, flags=re.IGNORECASE)
    
    # Remove "In the court of : [Judge] CNR Number" pattern
    text = re.sub(r'^In the court of\s*:\s*.*?\s*(?=CNR\s+Number)', '', text, flags=re.IGNORECASE)
    
    # Remove CNR and Case Number labels
    text = re.sub(r'^CNR\s+Number\s*:\s*[A-Z0-9]+\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Case\s+Number\s*:\s*[A-Z0-9_/]+\b\s*', '', text, flags=re.IGNORECASE)
    
    # Remove Petitioner versus Respondent and Date block
    # E.g. "CANARA BANK versus VANITHA Date : 02-04-2011"
    text = re.sub(r'^.*?\s+versus\s+.*?\s+Date\s*:\s*\d{1,2}-\d{1,2}-\d{4}\s*', '', text, flags=re.IGNORECASE)
    
    # Remove table labels: "Business :", "Nature of Disposal :", "Disposal Date :"
    text = re.sub(r'^Business\s*:\s*', '', text, flags=re.IGNORECASE)
    
    # Remove navigation links or UI warnings
    text = re.sub(r'\bBack\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bDaily Status\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bQR Code\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bView QR Code or Cause Title\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(Note the CNR number for future reference\)', '', text, flags=re.IGNORECASE)
    
    return re.sub(r'\s+', ' ', text).strip()

# Test string from Case 20 business div
test_str = (
    "Back Daily Status PRL. CITY CIVIL AND SESSIONS JUDGE In the court of :CCH5 IX ADDL. "
    "CITY CIVIL AND SESSONS JUDGE CNR Number :KABC010005032010 Case Number :EX/0000020/2010 "
    "CANARA BANK versus VANITHA Date : 02-04-2011 Business : Disposed Nature of Disposal : "
    "DISPOSED OTHERWISE Disposal Date : 02-04-2011"
)

cleaned = clean_text(test_str)
print("=== ORIGINAL ===")
print(test_str)
print("\n=== CLEANED ===")
print(cleaned)
