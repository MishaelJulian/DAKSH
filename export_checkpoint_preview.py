"""
export_checkpoint_preview.py
============================
Instantly exports the current checkpoint into:
- RFC 4180 CSV (52 columns, formula-locked Registration Numbers)
- Styled OpenPyXL Excel (with clickable PDF links and Text '@' formatting)
- Structured JSON dataset

Can be run at ANY time (even while the scraper is running) to inspect progress.
"""

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("checkpoint_preview")

BASE_DIR = Path(__file__).resolve().parent
CHECKPOINT_FILE = BASE_DIR / "pilot_output" / "checkpoint_405_cases.json"

COLUMNS_47 = [
    "Case Number",
    "Case Type",
    "CNR",
    "Case Title",
    "Filing Number",
    "Filing Date",
    "Registration Number",
    "Registration Date",
    "Main Case Number",
    "Main CNR",
    "Main Filing Number",
    "First Hearing Date",
    "Decision Date",
    "Case Status",
    "Nature of Disposal",
    "Case Duration (Days)",
    "Filing to First Hearing Duration (Days)",
    "Court Name",
    "Court Room & Judge",
    "Court Complex",
    "State",
    "District",
    "Petitioner",
    "Petitioner Advocate",
    "Respondent and Advocate",
    "Acts",
    "Hearing Index",
    "Business Date",
    "Hearing Date",
    "Hearing Judge",
    "Purpose of Hearing",
    "Business Text",
    "Next Purpose",
    "Next Hearing Date (Hearing)",
    "Order Number",
    "Order Details",
    "Judgment PDF URL",
    "Order Operative Ruling",
    "Order Procedural History",
    "Order Judicial Findings",
    "Order Annexed Proceedings",
    "Process ID",
    "Process Title",
    "Process Date",
    "Establishment Code",
    "Complex Code",
    "Scrape Timestamp",
]


def export_preview():
    if not CHECKPOINT_FILE.exists():
        log.error("No checkpoint file found at %s", CHECKPOINT_FILE)
        return

    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        checkpoint = json.load(f)

    all_rows = []
    all_json = []
    for cname, data in checkpoint.items():
        all_rows.extend(data.get("rows", []))
        j_obj = dict(data.get("json", {}))
        safe_case = str(cname).replace("/", "_")
        local_pdf = BASE_DIR / "pilot_output" / "orders" / f"{safe_case}_order_1.pdf"
        if local_pdf.exists() and "judicial_order" in j_obj:
            jo = dict(j_obj["judicial_order"])
            jo["local_pdf_uri"] = local_pdf.as_uri()
            jo["local_pdf_path"] = str(local_pdf)
            j_obj["judicial_order"] = jo
        all_json.append(j_obj)

    case_count = len(checkpoint)
    log.info("Loaded %d cases (%d hearing rows) from checkpoint.", case_count, len(all_rows))

    # Master canonical file names that are always updated in-place
    canonical_base = "Consolidated_Executive_Petitions_2023_FINAL"
    csv_file = BASE_DIR / f"{canonical_base}.csv"
    xlsx_file = BASE_DIR / f"{canonical_base}.xlsx"
    json_file = BASE_DIR / f"{canonical_base}.json"

    # Prepare normalized clean rows
    clean_rows = []
    for r in all_rows:
        cr = {}
        safe_case = str(r.get("Case Number", "")).replace("/", "_")
        local_pdf = BASE_DIR / "pilot_output" / "orders" / f"{safe_case}_order_1.pdf"
        for k in COLUMNS_47:
            if k == "Registration Number":
                cr[k] = str(r.get("_clean_reg_no") or r.get(k, "")).lstrip("=").strip('"')
            elif k == "Hearing Date" and not r.get(k):
                cr[k] = r.get("Decision Date", "")
            elif k == "Petitioner Advocate":
                cr[k] = r.get(k, "")
            elif k == "Judgment PDF URL":
                if local_pdf.exists():
                    cr[k] = local_pdf.as_uri()
                else:
                    cr[k] = r.get(k, "")
            else:
                cr[k] = r.get(k, "")
        clean_rows.append(cr)

    # 1. JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_json, f, indent=2, ensure_ascii=False)

    # 2. CSV (clean text formatting)
    try:
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS_47, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for cr in clean_rows:
                writer.writerow(cr)
    except PermissionError:
        csv_file = BASE_DIR / f"{base_name}_unlocked.csv"
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS_47, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for cr in clean_rows:
                writer.writerow(cr)
        log.warning("Original CSV was locked by another process. Saved to: %s", csv_file)

    # 3. Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Preview ({case_count} Cases)"

    header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    data_font = Font(name="Segoe UI", size=9)
    border_thin = Border(
        left=Side(style="thin", color="E0E0E0"),
        right=Side(style="thin", color="E0E0E0"),
        top=Side(style="thin", color="E0E0E0"),
        bottom=Side(style="thin", color="E0E0E0"),
    )

    ws.append(COLUMNS_47)
    for c_idx in range(1, len(COLUMNS_47) + 1):
        cell = ws.cell(row=1, column=c_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.row_dimensions[1].height = 28

    for r_idx, r_dict in enumerate(clean_rows, start=2):
        for c_idx, col_name in enumerate(COLUMNS_47, start=1):
            cell = ws.cell(row=r_idx, column=c_idx)
            cell.font = data_font
            cell.border = border_thin

            if col_name in ("Registration Number", "Filing Number", "Main Filing Number", "Process ID", "CNR", "Main CNR"):
                cell.value = str(r_dict.get(col_name, ""))
                cell.number_format = "@"
            elif col_name in ("Business Text", "Order Judicial Findings"):
                cell.value = r_dict.get(col_name, "")
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            elif col_name in ("Order Operative Ruling", "Order Procedural History", "Order Annexed Proceedings"):
                cell.value = r_dict.get(col_name, "")
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            elif col_name == "Judgment PDF URL" and r_dict.get(col_name):
                url_val = r_dict.get(col_name)
                safe_case = str(r_dict.get("Case Number", "")).replace("/", "_")
                local_pdf = BASE_DIR / "pilot_output" / "orders" / f"{safe_case}_order_1.pdf"
                if local_pdf.exists():
                    cell.value = f'=HYPERLINK("{local_pdf.as_posix()}", "Open Authentic Court Order")'
                else:
                    cell.value = f'=HYPERLINK("{url_val}", "Open Court Order PDF")'
                cell.font = Font(name="Segoe UI", size=9, color="0000FF", underline="single")
            else:
                cell.value = r_dict.get(col_name, "")

        ws.row_dimensions[r_idx].height = 45

    col_width_defaults = {
        "Business Text": 65,
        "Order Judicial Findings": 65,
        "Order Operative Ruling": 45,
        "Order Procedural History": 45,
        "Order Annexed Proceedings": 45,
        "Case Title": 35,
        "Court Name": 35,
        "Court Room & Judge": 35,
        "Respondent and Advocate": 35,
        "Petitioner": 30,
        "Petitioner Advocate": 25,
        "Process Title": 30,
        "Process ID": 25,
        "CNR": 20,
        "Main CNR": 20,
        "Judgment PDF URL": 25,
    }
    for col_idx, col_name in enumerate(COLUMNS_47, start=1):
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        if col_name in col_width_defaults:
            ws.column_dimensions[col_letter].width = col_width_defaults[col_name]
        else:
            sample_lens = [len(str(r.get(col_name, ""))) for r in clean_rows[:50]]
            max_len = max(sample_lens + [len(col_name)])
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 30)

    ws.freeze_panes = "A2"
    try:
        wb.save(xlsx_file)
    except PermissionError:
        xlsx_file = BASE_DIR / f"{base_name}_unlocked.xlsx"
        wb.save(xlsx_file)
        log.warning("Original Excel was locked by another process. Saved to: %s", xlsx_file)

    print("\n" + "=" * 80)
    print(f" CHECKPOINT PREVIEW EXPORT COMPLETE ({case_count} Cases)")
    print(f" CSV Deliverable   : {csv_file}")
    print(f" Excel Deliverable : {xlsx_file}")
    print(f" JSON Deliverable  : {json_file}")

    print(f" ALL MASTER AND PRODUCTION DELIVERABLES UPDATED IN-PLACE ({case_count} Cases)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    export_preview()
