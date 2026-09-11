import os
import re
import json
import pandas as pd

# Paths
json_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023\cases.json"
out_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023"
csv_out_name = "cases.csv"

os.makedirs(out_dir, exist_ok=True)

def clean_text(text):
    """Strips web UI header boilerplate without truncating narrative text."""
    if not isinstance(text, str) or not text:
        return ""
    text = text.replace("\r", " ").replace("\t", " ")
    text = re.sub(r'^Back\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Daily Status\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^PRL\.\s+CITY\s+CIVIL\s+AND\s+SESSIONS\s+JUDGE\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^PRL\.\s+CITY\s+CIVIL\s+COURT\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^In the court of\s*:\s*.*?\s*(?=CNR\s+Number)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^CNR\s+Number\s*:\s*[A-Z0-9]+\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Case\s+Number\s*:\s*[A-Z0-9_/]+\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^.*?\s+versus\s+.*?\s+Date\s*:\s*\d{1,2}-\d{1,2}-\d{4}\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Business\s*:\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bView QR Code or Cause Title\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(Note the CNR number for future reference\)', '', text, flags=re.IGNORECASE)
    return text.strip()

def parse_date(date_str):
    if not isinstance(date_str, str) or not date_str.strip():
        return None
    date_str = date_str.strip()
    if date_str == "-":
        return None
    for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d'):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
    return pd.to_datetime(date_str, errors='coerce')

def format_date_str(date_val):
    if date_val is None or (isinstance(date_val, float) and pd.isna(date_val)) or date_val == "" or date_val == "-":
        return ""
    if isinstance(date_val, str):
        parsed = parse_date(date_val)
        if parsed is None or pd.isna(parsed):
            return date_val
        return parsed.strftime('%d/%m/%Y')
    return date_val.strftime('%d/%m/%Y')

def safe_json_parse(s):
    """Parse a JSON string, returning empty dict/list on failure."""
    if not isinstance(s, str) or not s.strip():
        return {}
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {}

print("Reading cases.json...")
with open(json_path, 'r', encoding='utf-8') as f:
    cases = json.load(f)

print(f"Loaded {len(cases)} cases.")

rows = []

for case_idx, case in enumerate(cases):
    cnr = case.get("cnr", "")
    case_number = case.get("case_number", "")
    case_type_label = case.get("case_type_label", "")
    case_title = (case.get("case_title", "") or "").replace("\n", " ")
    appellant = case.get("appellant", "")
    respondent = case.get("respondent", "")
    bench_city = case.get("bench_city", "BENGALURU")
    bench_state = case.get("bench_state", "Karnataka")
    court_name = case.get("court_name", "")
    court_complex = "City Civil Court Complex, Bangalore"
    cnr_case_number = case.get("cnr_case_number", "")
    filing_number = cnr_case_number
    filing_date = format_date_str(case.get("filing_date", ""))
    registration_number = cnr_case_number
    registration_date = format_date_str(case.get("first_hearing_date", ""))
    first_hearing_date = format_date_str(case.get("first_hearing_date", ""))
    next_hearing_date = format_date_str(case.get("next_hearing_date", ""))
    last_hearing_date = format_date_str(case.get("last_hearing_date", ""))
    decision_date = format_date_str(case.get("decision_date", ""))
    case_status_raw = case.get("case_status", "")
    case_status = "Disposed" if "disposed" in case_status_raw.lower() else case_status_raw
    sub_stage = case.get("sub_stage", "") or case.get("result", "")
    result = case.get("result", "")
    case_duration_days = case.get("case_duration_days", "")
    filing_to_first_hearing_days = case.get("filing_to_first_hearing_days", "")
    petitioner = appellant
    petitioner_advocate = case.get("petitioner_advocates", "")
    respondent_advocate = case.get("respondent_advocates", "")
    sections_raw = case.get("sections", "")
    # Extract Acts from sections (e.g., "U/O 21 RULE 11 OF CPC Section ," -> "CPC")
    acts = ""
    if sections_raw:
        act_match = re.search(r'OF\s+(\w+)', sections_raw)
        if act_match:
            acts = act_match.group(1)
    sections = re.sub(r'\s*Section\s*,?\s*$', '', sections_raw).strip().rstrip(',').strip()

    # Parse extra_metadata for history and processes
    extra_meta = safe_json_parse(case.get("extra_metadata", ""))
    history_list = extra_meta.get("history", []) if isinstance(extra_meta, dict) else []
    processes_list = extra_meta.get("processes", []) if isinstance(extra_meta, dict) else []

    # Parse orders_json
    orders_json_str = case.get("orders_json", "")
    orders_list = safe_json_parse(orders_json_str) if orders_json_str else []
    if not isinstance(orders_list, list):
        orders_list = []

    # Split business_text by "--- NEXT ORDER ---"
    business_text_raw = case.get("business_text", "") or ""
    business_texts = [bt.strip() for bt in business_text_raw.split("--- NEXT ORDER ---") if bt.strip()]

    # Build order lookup by date
    orders_by_date = {}
    for i, o in enumerate(orders_list):
        od = o.get("order_date", "")
        if od:
            orders_by_date[od] = (i, o)

    # Build process lookup by date
    processes_by_date = {}
    for p in processes_list:
        pd_val = p.get("process_date", "")
        if pd_val:
            processes_by_date.setdefault(pd_val, []).append(p)

    # Determine event count (primary driver is history)
    num_events = max(len(history_list), len(orders_list), len(business_texts), 1)

    # Compute disposal date from the first order's disposal_date or decision_date
    first_disp = ""
    if orders_list:
        first_disp = format_date_str(orders_list[0].get("disposal_date", ""))
    if not first_disp:
        first_disp = decision_date

    # Extract nature of disposal from first order text or result
    nature_of_disposal_text = ""
    if orders_list and orders_list[0].get("full_order_text", ""):
        nod_match = re.search(r'Nature of Disposal\s*:\s*(.*?)(?:Disposal Date|$)', 
                              orders_list[0]["full_order_text"], re.IGNORECASE)
        if nod_match:
            nature_of_disposal_text = nod_match.group(1).strip()
    if not nature_of_disposal_text:
        nature_of_disposal_text = result

    for idx in range(1, num_events + 1):
        # History record
        h_rec = history_list[idx - 1] if idx <= len(history_list) else {}
        h_business_date = h_rec.get("business_date", "")
        h_hearing_date = h_rec.get("hearing_date", "")
        h_judge = h_rec.get("judge", "")
        h_purpose = h_rec.get("purpose_of_hearing") or h_rec.get("purpose", "")
        h_summary = h_purpose  # In this format, purpose is the summary

        # Order record (match by index alignment or by date)
        o_rec = orders_list[idx - 1] if idx <= len(orders_list) else {}
        if not o_rec and h_business_date:
            matched = orders_by_date.get(h_business_date)
            if matched:
                o_rec = matched[1]
        o_date = o_rec.get("order_date", "")
        o_idx = str(idx) if o_rec else ""
        o_num = o_rec.get("order_number", "")
        o_link = o_rec.get("order_link", "")
        o_nod = ""
        o_full_text = o_rec.get("full_order_text", "")
        if o_full_text:
            nod_m = re.search(r'Nature of Disposal\s*:\s*(.*?)(?:Disposal Date|$)', o_full_text, re.IGNORECASE)
            if nod_m:
                o_nod = nod_m.group(1).strip()
        o_disp_date = format_date_str(o_rec.get("disposal_date", ""))
        o_judge = o_rec.get("judge", "") or h_judge
        o_text = clean_text(o_full_text)
        o_doc_count = str(len(o_rec.get("documents", []))) if o_rec else ""

        # Business text
        b_text = ""
        if idx <= len(business_texts):
            b_text = clean_text(business_texts[idx - 1])
        elif o_text:
            b_text = o_text

        b_date = format_date_str(h_business_date or o_date)
        b_idx = str(idx) if (b_text or h_business_date) else ""

        # Process record (match by hearing_date = process_date, or by index)
        p_list = processes_by_date.get(h_hearing_date, []) if h_hearing_date else []
        if not p_list:
            p_list = processes_by_date.get(h_business_date, []) if h_business_date else []
        p_rec = p_list[0] if p_list else (processes_list[idx - 1] if idx <= len(processes_list) else {})
        p_id = p_rec.get("process_id", "")
        p_title = p_rec.get("process_title", "")
        p_date = format_date_str(p_rec.get("process_date", ""))

        row_dict = {
            'Case Number': case_number,
            'Case Type': case_type_label,
            'CNR': cnr,
            'Case Title': case_title,
            'Filing Number': filing_number,
            'Filing Date': filing_date,
            'Registration Number': registration_number,
            'Registration Date': registration_date,
            'First Hearing Date': first_hearing_date,
            'Next Hearing Date': next_hearing_date,
            'Last Hearing Date': last_hearing_date,
            'Decision Date': decision_date,
            'Disposal Date': first_disp,
            'Case Status': case_status,
            'Sub Stage': sub_stage,
            'Nature of Disposal': nature_of_disposal_text,
            'Case Duration (Days)': case_duration_days,
            'Filing to First Hearing Duration (Days)': filing_to_first_hearing_days,
            'Court Name': court_name,
            'Court Complex': court_complex,
            'State': bench_state,
            'District': bench_city,
            'Petitioner': petitioner,
            'Petitioner Advocate': petitioner_advocate,
            'Respondent': respondent,
            'Respondent Advocate': respondent_advocate,
            'Acts': acts,
            'Sections': sections,
            'Hearing Date': format_date_str(h_business_date),
            'Hearing Index': str(idx),
            'Hearing Judge': h_judge,
            'Purpose of Hearing': h_purpose,
            'Hearing Business Summary': h_summary,
            'Business Date': b_date,
            'Business Index': b_idx,
            'Business Text': b_text,
            'Order Date': format_date_str(o_date),
            'Order Index': o_idx,
            'Order Number': o_num,
            'Order Link': o_link,
            'Order Nature of Disposal': o_nod,
            'Order Disposal Date': o_disp_date,
            'Order Judge': o_judge,
            'Order Text': o_text,
            'Order Document Count': o_doc_count,
            'Process ID': p_id,
            'Process Title': p_title,
            'Process Date': p_date,
            'Transfer Registration Number': '',
            'Transfer Date': '',
            'Transfer From Court': '',
            'Transfer To Court': '',
            'Documents': ''
        }
        rows.append(row_dict)

    if (case_idx + 1) % 50 == 0:
        print(f"  Processed {case_idx + 1}/{len(cases)} cases...")

final_df = pd.DataFrame(rows)

column_order = [
    'Case Number', 'Case Type', 'CNR', 'Case Title',
    'Filing Number', 'Filing Date', 'Registration Number', 'Registration Date',
    'First Hearing Date', 'Next Hearing Date', 'Last Hearing Date',
    'Decision Date', 'Disposal Date', 'Case Status', 'Sub Stage',
    'Nature of Disposal', 'Case Duration (Days)', 'Filing to First Hearing Duration (Days)',
    'Court Name', 'Court Complex', 'State', 'District',
    'Petitioner', 'Petitioner Advocate', 'Respondent', 'Respondent Advocate',
    'Acts', 'Sections',
    'Hearing Date', 'Hearing Index', 'Hearing Judge',
    'Purpose of Hearing', 'Hearing Business Summary',
    'Business Date', 'Business Index', 'Business Text',
    'Order Date', 'Order Index', 'Order Number', 'Order Link',
    'Order Nature of Disposal', 'Order Disposal Date', 'Order Judge', 'Order Text',
    'Order Document Count',
    'Process ID', 'Process Title', 'Process Date',
    'Transfer Registration Number', 'Transfer Date', 'Transfer From Court', 'Transfer To Court',
    'Documents'
]

final_df = final_df[column_order]

# Clean NAs
for col in final_df.columns:
    if final_df[col].dtype == object:
        final_df[col] = final_df[col].fillna("").astype(str)
        final_df[col] = final_df[col].replace({'nan': '', 'None': '', '<NA>': '', 'NaN': ''})
    else:
        final_df[col] = final_df[col].fillna("")

print(f"\nFinal dataset shape: {final_df.shape}")
print(f"  Unique cases: {final_df['CNR'].nunique()}")
print(f"  Total rows: {len(final_df)}")

# Save CSV with UTF-8 BOM
csv_out_path = os.path.join(out_dir, csv_out_name)
try:
    final_df.to_csv(csv_out_path, index=False, encoding='utf-8-sig')
    print(f"\nExported CSV: {csv_out_path}")
except PermissionError:
    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    fallback = os.path.join(out_dir, f"cases_{ts}.csv")
    final_df.to_csv(fallback, index=False, encoding='utf-8-sig')
    print(f"  [!] Primary CSV locked — saved fallback: {fallback}")

print("Done.")
