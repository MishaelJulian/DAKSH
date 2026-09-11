import os
import re
import json
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Paths
json_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010_Final\cases.json"
out_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010_Final"

os.makedirs(out_dir, exist_ok=True)

def clean_text(text):
    """Strips web UI header boilerplate without truncating narrative text."""
    if not isinstance(text, str) or not text:
        return ""
    
    # Replace carriage returns/tabs with spaces, keep newlines
    text = text.replace("\r", " ").replace("\t", " ")
    
    # Strip web interface headers at start of text
    text = re.sub(r'^Back\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Daily Status\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^PRL\.\s+CITY\s+CIVIL\s+AND\s+SESSIONS\s+JUDGE\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^PRL\.\s+CITY\s+CIVIL\s+COURT\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^In the court of\s*:\s*.*?\s*(?=CNR\s+Number)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^CNR\s+Number\s*:\s*[A-Z0-9]+\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Case\s+Number\s*:\s*[A-Z0-9_/]+\b\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^.*?\s+versus\s+.*?\s+Date\s*:\s*\d{1,2}-\d{1,2}-\d{4}\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Business\s*:\s*', '', text, flags=re.IGNORECASE)
    
    # Strip common UI keywords
    text = re.sub(r'\bView QR Code or Cause Title\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(Note the CNR number for future reference\)', '', text, flags=re.IGNORECASE)
    
    return text.strip()

def parse_date(date_str):
    if not isinstance(date_str, str) or not date_str.strip():
        return None
    date_str = date_str.strip()
    for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d'):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
    return pd.to_datetime(date_str, errors='coerce')

def format_date_str(date_val):
    if date_val is None or pd.isna(date_val) or date_val == "":
        return ""
    if isinstance(date_val, str):
        parsed = parse_date(date_val)
        if pd.isna(parsed) or parsed is None:
            return date_val
        return parsed.strftime('%Y-%m-%d')
    return date_val.strftime('%Y-%m-%d')

print("Reading canonical cases.json source...")
with open(json_path, 'r', encoding='utf-8') as f:
    cases = json.load(f)

print(f"Loaded {len(cases)} cases.")

rows = []

# Counters for validation
total_history_count = 0
total_orders_count = 0
total_business_count = 0
total_processes_count = 0
total_transfers_count = 0
total_documents_count = 0

for case in cases:
    cnr = case.get("cnr", "")
    case_number = case.get("case_number", "")
    cnr_court_code = case.get("cnr_court_code", "")
    bench_code = case.get("bench_code", "")
    type_code = case.get("type_code", "")
    cnr_case_number = case.get("cnr_case_number", "")
    cnr_year = case.get("cnr_year", "")
    case_type_label = case.get("case_type_label", "")
    case_title = case.get("case_title", "")
    appellant = case.get("appellant", "")
    respondent = case.get("respondent", "")
    bench_city = case.get("bench_city", "BENGALURU")
    bench_state = case.get("bench_state", "Karnataka")
    court_name = case.get("court_name", "")
    court_complex = "City Civil Court Complex, Bangalore"
    filing_number = case.get("filing_number", "") or cnr_case_number
    filing_date = format_date_str(case.get("filing_date", ""))
    registration_number = cnr_case_number or case.get("registration_number", "")
    registration_date = format_date_str(case.get("registration_date", ""))
    case_status = case.get("case_status", "")
    sub_stage = case.get("sub_stage", "") or case.get("case_sub_stage", "")
    nature_of_disposal = case.get("nature_of_disposal", "") or case.get("result", "")
    disposal_date = format_date_str(case.get("disposal_date", "") or case.get("decision_date", ""))
    decision_date = format_date_str(case.get("decision_date", ""))
    first_hearing_date = format_date_str(case.get("first_hearing_date", ""))
    last_hearing_date = format_date_str(case.get("last_hearing_date", ""))
    next_hearing_date = format_date_str(case.get("next_hearing_date", ""))
    case_duration_days = case.get("case_duration_days", "")
    filing_to_first_hearing_days = case.get("filing_to_first_hearing_days", "")
    petitioner = appellant
    petitioner_advocate = case.get("petitioner_advocates", "")
    respondent_advocate = case.get("respondent_advocates", "")
    acts = case.get("acts", "")
    sections = case.get("sections", "")
    
    # Nested arrays
    history_list = case.get("history", [])
    orders_list = case.get("orders", [])
    business_list = case.get("business_list", [])
    processes_list = case.get("processes", [])
    transfers_list = case.get("transfers", [])
    documents_list = case.get("documents", [])
    
    total_history_count += len(history_list)
    total_orders_count += len(orders_list)
    total_business_count += len(business_list)
    total_processes_count += len(processes_list)
    total_transfers_count += len(transfers_list)
    total_documents_count += len(documents_list)
    
    # Map orders by order_date or index for alignment
    orders_by_idx = {i + 1: o for i, o in enumerate(orders_list)}
    orders_by_date = {o.get("order_date", ""): o for o in orders_list if o.get("order_date")}
    
    business_by_idx = {i + 1: b for i, b in enumerate(business_list)}
    business_by_date = {b.get("business_date", ""): b for b in business_list if b.get("business_date")}
    
    processes_by_date = {}
    for p in processes_list:
        p_dt = p.get("process_date", "")
        processes_by_date.setdefault(p_dt, []).append(p)
        
    transfers_by_date = {}
    for t in transfers_list:
        t_dt = t.get("transfer_date", "")
        transfers_by_date.setdefault(t_dt, []).append(t)
        
    # Determine event count for this case (primary driver is history list)
    num_events = max(len(history_list), len(orders_list), len(business_list), 1)
    
    for idx in range(1, num_events + 1):
        # 1. History record
        h_rec = history_list[idx - 1] if idx <= len(history_list) else {}
        h_date = h_rec.get("hearing_date") or h_rec.get("business_date") or ""
        h_idx = h_rec.get("history_index") or (str(idx) if h_rec else "")
        h_judge = h_rec.get("judge", "")
        h_order_num = h_rec.get("order_number", "")
        h_purpose = h_rec.get("purpose_of_hearing") or h_rec.get("purpose", "")
        h_summary = h_rec.get("business_summary") or h_purpose
        
        # 2. Order record (match by date or index)
        o_rec = orders_by_idx.get(idx) or (orders_by_date.get(h_date) if h_date else {}) or {}
        o_date = o_rec.get("order_date", "")
        o_idx = str(idx) if o_rec else ""
        o_num = o_rec.get("order_number", "")
        o_link = o_rec.get("order_link", "")
        o_nod = o_rec.get("nature_of_disposal", "")
        o_disp_date = format_date_str(o_rec.get("disposal_date", ""))
        o_judge = o_rec.get("judge", "")
        o_text = clean_text(o_rec.get("full_order_text") or o_rec.get("order_text") or "")
        o_doc_count = str(len(o_rec.get("documents", []))) if o_rec else ""
        
        # 3. Business record
        b_rec = business_by_idx.get(idx) or (business_by_date.get(h_date) if h_date else {}) or {}
        b_date = b_rec.get("business_date", "")
        b_idx = str(idx) if b_rec else ""
        b_text = clean_text(b_rec.get("business_text") or o_text)
        
        # 4. Process record (match by date if present)
        p_list = processes_by_date.get(h_date, [])
        p_rec = p_list[0] if p_list else (processes_list[idx - 1] if idx <= len(processes_list) else {})
        p_id = p_rec.get("process_id", "")
        p_title = p_rec.get("process_title", "")
        p_date = format_date_str(p_rec.get("process_date", ""))
        
        # 5. Transfer record (match by date if present)
        t_list = transfers_by_date.get(h_date, [])
        t_rec = t_list[0] if t_list else (transfers_list[idx - 1] if idx <= len(transfers_list) else {})
        t_reg = t_rec.get("registration_number", "")
        t_date = format_date_str(t_rec.get("transfer_date", ""))
        t_from = t_rec.get("from_court", "")
        t_to = t_rec.get("to_court", "")
        
        row_dict = {
            'CNR': cnr,
            'Case Number': case_number,
            'Court Name': court_name,
            'Court Complex': court_complex,
            'State': bench_state,
            'District': bench_city,
            'Case Title': case_title,
            'Case Type': case_type_label,
            'Filing Number': filing_number,
            'Filing Date': filing_date,
            'Registration Number': registration_number,
            'Registration Date': registration_date,
            'Case Status': case_status,
            'Sub Stage': sub_stage,
            'Nature of Disposal': nature_of_disposal,
            'Disposal Date': disposal_date,
            'Decision Date': decision_date,
            'First Hearing Date': first_hearing_date,
            'Last Hearing Date': last_hearing_date,
            'Next Hearing Date': next_hearing_date,
            'Case Duration (Days)': case_duration_days,
            'Filing to First Hearing Duration (Days)': filing_to_first_hearing_days,
            'Petitioner': petitioner,
            'Petitioner Advocate': petitioner_advocate,
            'Respondent': respondent,
            'Respondent Advocate': respondent_advocate,
            'Acts': acts,
            'Sections': sections,
            'Hearing Date': format_date_str(h_date),
            'Hearing Index': h_idx,
            'Hearing Judge': h_judge,
            'Hearing Order Number': h_order_num,
            'Purpose of Hearing': h_purpose,
            'Hearing Business Summary': h_summary,
            'Business Date': format_date_str(b_date or h_date),
            'Business Index': b_idx,
            'Business Text': b_text,
            'Order Date': format_date_str(o_date or h_date),
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
            'Transfer Registration Number': t_reg,
            'Transfer Date': t_date,
            'Transfer From Court': t_from,
            'Transfer To Court': t_to,
            'Documents': ""
        }
        rows.append(row_dict)

final_df = pd.DataFrame(rows)

column_order = [
    'CNR', 'Case Number', 'Court Name', 'Court Complex', 'State', 'District', 'Case Title', 'Case Type',
    'Filing Number', 'Filing Date', 'Registration Number', 'Registration Date', 'Case Status', 'Sub Stage',
    'Nature of Disposal', 'Disposal Date', 'Decision Date', 'First Hearing Date', 'Last Hearing Date', 'Next Hearing Date',
    'Case Duration (Days)', 'Filing to First Hearing Duration (Days)', 'Petitioner', 'Petitioner Advocate', 'Respondent', 'Respondent Advocate',
    'Acts', 'Sections', 'Hearing Date', 'Hearing Index', 'Hearing Judge', 'Hearing Order Number', 'Purpose of Hearing', 'Hearing Business Summary',
    'Business Date', 'Business Index', 'Business Text', 'Order Date', 'Order Index', 'Order Number',
    'Order Link', 'Order Nature of Disposal', 'Order Disposal Date', 'Order Judge', 'Order Text', 'Order Document Count',
    'Process ID', 'Process Title', 'Process Date', 'Transfer Registration Number', 'Transfer Date', 'Transfer From Court', 'Transfer To Court',
    'Documents'
]

final_df = final_df[column_order]

# Clean label leaks and fill NAs
if 'Sub Stage' in final_df.columns:
    final_df['Sub Stage'] = final_df['Sub Stage'].replace('Sub Stage', '')

for col in final_df.columns:
    if final_df[col].dtype == object:
        final_df[col] = final_df[col].fillna("").astype(str)
        final_df[col] = final_df[col].replace({'nan': '', 'None': '', '<NA>': '', 'NaN': ''})
    else:
        final_df[col] = final_df[col].fillna("")

print(f"Final consolidated dataset shape: {final_df.shape}")

# Save CSV with UTF-8 BOM
csv_out_path = os.path.join(out_dir, "Consolidated_Executive_Petitions_2010.csv")
try:
    final_df.to_csv(csv_out_path, index=False, encoding='utf-8-sig')
    print(f"Exported CSV: {csv_out_path}")
except PermissionError:
    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    fallback_csv = os.path.join(out_dir, f"Consolidated_Executive_Petitions_2010_{ts}.csv")
    final_df.to_csv(fallback_csv, index=False, encoding='utf-8-sig')
    print(f"  [!] Primary CSV locked — saved fallback '{fallback_csv}'")

# Save XLSX with professional styling
xlsx_out_path = os.path.join(out_dir, "Consolidated_Executive_Petitions_2010.xlsx")
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Consolidated Cases"

ws.append(column_order)

header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
body_font = Font(name="Segoe UI", size=10)
alt_row_fill = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")
border_side = Side(style='thin', color='D9D9D9')
body_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
align_left = Alignment(horizontal='left', vertical='center', wrap_text=True)
align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)

for row_val in final_df.values:
    ws.append(list(row_val))

for col_idx in range(1, len(column_order) + 1):
    cell = ws.cell(row=1, column=col_idx)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

ws.row_dimensions[1].height = 28

for r_idx in range(2, ws.max_row + 1):
    ws.row_dimensions[r_idx].height = 22
    is_alt = (r_idx % 2 == 1)
    for c_idx in range(1, ws.max_column + 1):
        cell = ws.cell(row=r_idx, column=c_idx)
        cell.font = body_font
        cell.border = body_border
        if is_alt:
            cell.fill = alt_row_fill
        col_name = column_order[c_idx - 1]
        if 'Date' in col_name or col_name in ['Hearing Index', 'Business Index', 'Order Index', 'Order Document Count', 'Case Duration (Days)', 'Filing to First Hearing Duration (Days)']:
            cell.alignment = align_center
        else:
            cell.alignment = align_left

ws.freeze_panes = 'A2'
ws.auto_filter.ref = f"A1:{get_column_letter(len(column_order))}{ws.max_row}"

for col in ws.columns:
    max_len = 0
    col_letter = get_column_letter(col[0].column)
    col_name = column_order[col[0].column - 1]
    for cell in col:
        val = str(cell.value or '')
        if len(val) > max_len:
            max_len = len(val)
    if col_name in ['Hearing Business Summary', 'Business Text', 'Order Text']:
        width = 45
    elif col_name in ['Case Title', 'Court Name', 'Court Complex', 'Petitioner', 'Respondent', 'Petitioner Advocate', 'Respondent Advocate', 'Transfer From Court', 'Transfer To Court']:
        width = min(max(max_len + 3, 15), 35)
    else:
        width = max(max_len + 3, 12)
    ws.column_dimensions[col_letter].width = width

try:
    wb.save(xlsx_out_path)
    print(f"Exported XLSX: {xlsx_out_path}")
except PermissionError:
    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    fallback_xlsx = os.path.join(out_dir, f"Consolidated_Executive_Petitions_2010_{ts}.xlsx")
    wb.save(fallback_xlsx)
    print(f"  [!] Primary XLSX locked — saved fallback '{fallback_xlsx}'")

print("\n=== CONSOLIDATION AUDIT REPORT ===")
print(f"Cases Processed    : {len(cases)} / 20")
print(f"Total Rows Exported: {len(final_df)}")
print(f"History Rows       : {total_history_count}")
print(f"Orders             : {total_orders_count}")
print(f"Business Entries   : {total_business_count}")
print(f"Processes          : {total_processes_count}")
print(f"Transfers          : {total_transfers_count}")
print(f"Documents          : {total_documents_count}")
print("===================================\n")
