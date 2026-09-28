"""
scrape_remaining_2023_unified.py
================================
Single-Pass Unified High-Performance Scraper for ALL Remaining 2023 Disposed Execution Petitions.
In a single pass per case:
1. Fetches full case details & parties & acts & processes (viewHistory)
2. Downloads authentic court order PDF and parses operative rulings via PyMuPDF
3. In the SAME session, immediately enriches EVERY hearing with verbatim Business Text (viewBusiness)
4. Saves atomically to master checkpoint after every completed case
5. Auto-exports updated Excel, CSV, and JSON deliverables periodically
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
import scrape_all_2023_disposed as s
import export_checkpoint_preview
from deeper_tool.parser import parse_deeper_case_detail

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("unified_2023")

CHECKPOINT_FILE = BASE_DIR / "pilot_output" / "checkpoint_405_cases.json"
ORDERS_DIR = BASE_DIR / "pilot_output" / "orders"
ORDERS_DIR.mkdir(parents=True, exist_ok=True)


def extract_view_business_map(client: s.EcourtsWorkerClient, html: str, c_tuple: tuple) -> dict:
    """Extracts verbatim business text for all hearings in the case from viewBusiness."""
    soup = BeautifulSoup(html, "html.parser")
    b_map = {}
    case_no = c_tuple[2]

    for a in soup.find_all("a"):
        oc = a.get("onclick", "")
        if "viewBusiness" in oc:
            m = re.search(r"viewBusiness\s*\((.*?)\)", oc)
            if not m:
                continue
            args = [p.strip().strip("'\"") for p in m.group(1).split(",")]
            while len(args) < 11:
                args.append("")

            payload = {
                "ajax_req": "true",
                "app_token": client.app_token,
                "court_code": args[0],
                "dist_code": args[1],
                "nextdate1": args[2],
                "case_number1": args[3],
                "state_code": args[4],
                "disposal_flag": args[5],
                "businessDate": args[6],
                "court_no": args[7],
                "national_court_code": args[8],
                "search_by": args[9],
                "srno": args[10],
                "court_complex_code": "1030135",
            }

            for attempt in range(1, 3):
                try:
                    time.sleep(0.75)
                    r = client.session.post(
                        "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/viewBusiness",
                        data=payload,
                        headers=client.get_api_headers(),
                        timeout=12,
                    )
                    if r.status_code == 200:
                        try:
                            j = r.json()
                            if isinstance(j, dict) and j.get("app_token"):
                                client.app_token = j["app_token"]
                            dl = j.get("data_list", "")
                            sub_soup = BeautifulSoup(dl, "html.parser")
                            b_text, np_text, nhd_text = "", "", ""
                            for tr in sub_soup.find_all("tr"):
                                tds = tr.find_all("td")
                                if len(tds) >= 3:
                                    lbl = tds[0].get_text(strip=True).lower()
                                    val = " ".join(tds[2].get_text(" ", strip=True).split())
                                    if "business" in lbl:
                                        b_text = val
                                    elif "next purpose" in lbl:
                                        np_text = val
                                    elif "next hearing date" in lbl:
                                        m_d = re.search(r"([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})", val)
                                        if m_d:
                                            nhd_text = s.format_date(m_d.group(1))
                                elif len(tds) == 2:
                                    lbl = tds[0].get_text(strip=True).lower()
                                    val = " ".join(tds[1].get_text(" ", strip=True).split())
                                    if "business" in lbl:
                                        b_text = val
                                    elif "next purpose" in lbl:
                                        np_text = val
                                    elif "next hearing date" in lbl:
                                        m_d = re.search(r"([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})", val)
                                        if m_d:
                                            nhd_text = s.format_date(m_d.group(1))

                            if not b_text:
                                txt = sub_soup.get_text("\n")
                                m_b = re.search(
                                    r"Business\s*[:\s]+(.*?)(?=Nature of Disposal|Disposal Date|Next Purpose|Next Hearing Date|CCH|$)",
                                    txt,
                                    re.DOTALL | re.IGNORECASE,
                                )
                                if m_b:
                                    b_text = " ".join(m_b.group(1).split()).strip()

                            d_norm = s.format_date(args[6])
                            b_map[d_norm] = {
                                "text": b_text,
                                "np": np_text,
                                "nhd": nhd_text,
                            }
                            break
                        except Exception:
                            pass

                    if "Search Page not Found" in r.text or "Security Page" in r.text or r.status_code in (405, 403):
                        log.warning("WAF cooldown triggered on %s (hearing %s). Waiting 65s for firewall reset...", case_no, args[6])
                        time.sleep(65)
                        client._init_handshake()
                        payload["app_token"] = client.app_token
                        if not client.app_token:
                            time.sleep(25)
                            client._init_handshake()
                            payload["app_token"] = client.app_token
                except Exception:
                    time.sleep(1.0)

    return b_map


def scrape_unified_case(client: s.EcourtsWorkerClient, c_tuple: tuple) -> tuple:
    """Scrapes a single case completely: metadata + order PDF + verbatim hearing business text."""
    case_no_numeric, cino, case_no = c_tuple
    t0 = time.time()

    # 1. Fetch Case History HTML with auto-retry
    html = client.fetch_view_history(case_no_numeric, cino)
    retry_fetch = 0
    while not html and retry_fetch < 4:
        log.warning("Server cooldown on %s. Pausing 45s for firewall reset (retry %d/4)...", case_no, retry_fetch + 1)
        time.sleep(45)
        client._init_handshake()
        html = client.fetch_view_history(case_no_numeric, cino)
        retry_fetch += 1

    if not html:
        return case_no, None, 0

    # 2. Parse Case Details
    try:
        parsed = parse_deeper_case_detail(html)
    except Exception as e:
        log.warning("Parse warning on %s: %s", case_no, e)
        return case_no, None, 0

    # 3. Download Order PDF & Decompose
    ord0 = parsed.orders[0] if parsed.orders else None
    pdf_url = ""
    order_sec = {"operative": "", "procedural": "", "findings": "", "annexed": ""}
    ord_num = ""
    ord_details = ""
    has_pdf = False
    if ord0 and getattr(ord0, "pdf_params", None):
        ord_num = ord0.order_number or "1"
        ord_details = ord0.order_details or "Orders"
        ord_date = s.format_date(ord0.order_date)
        pdf_url, local_pdf_path = client.fetch_order_pdf(case_no, ord0.pdf_params, ord_num)
        if local_pdf_path and local_pdf_path.is_file():
            has_pdf = True
            order_sec = s.decompose_authentic_pdf(local_pdf_path, ord_date)

    # 4. In the SAME session, fetch verbatim Business Text for all hearings
    b_map = extract_view_business_map(client, html, c_tuple)

    # 5. Build Standard 47-Column Rows
    filing_d = s.format_date(parsed.filing_date)
    reg_d = s.format_date(parsed.registration_date)
    first_hd = s.format_date(parsed.first_hearing_date)
    dec_d = s.format_date(parsed.decision_date)

    dt_f = s.parse_date(filing_d)
    dt_d = s.parse_date(dec_d)
    dt_1 = s.parse_date(first_hd)
    case_dur = str((dt_d - dt_f).days) if dt_f and dt_d else ""
    f2h_dur = str((dt_1 - dt_f).days) if dt_f and dt_1 else ""

    mm0 = parsed.main_matters[0] if parsed.main_matters else None
    main_case_no = mm0.main_case_number if mm0 else ""
    main_cnr = mm0.main_cnr_number if mm0 else ""
    main_filing_no = mm0.main_filing_number if mm0 else ""

    petitioners = [p.name for p in parsed.parties if p.type == "petitioner"]
    pet_advs = [p.advocate for p in parsed.parties if p.type == "petitioner" and p.advocate]
    pet_str = "; ".join(filter(None, petitioners))
    pet_adv_str = "; ".join(filter(None, pet_advs))

    respondents = [p.name for p in parsed.parties if p.type == "respondent"]
    resp_str = "; ".join(filter(None, respondents))
    resp_adv_pairs = []
    for p in parsed.parties:
        if p.type == "respondent":
            if p.advocate:
                resp_adv_pairs.append(f"{p.name} (Advocate: {p.advocate})")
            else:
                resp_adv_pairs.append(p.name)
    resp_and_adv_str = "; ".join(filter(None, resp_adv_pairs)) if resp_adv_pairs else resp_str

    acts_list = [a.act for a in parsed.acts if a.act]
    acts_str = "; ".join(dict.fromkeys(acts_list)) if acts_list else "U/O 21 RULE 11 OF CPC"

    proc0 = parsed.processes[0] if parsed.processes else None
    proc_id = proc0.process_id if proc0 else ""
    proc_title = proc0.process_title if proc0 else ""
    proc_date = s.format_date(proc0.process_date) if proc0 else ""

    raw_reg = parsed.registration_number or case_no.split("/")[-2] + "/2023"
    clean_reg_no = raw_reg.lstrip("'").lstrip("=").strip('"')
    title = f"{pet_str} vs {resp_str}".strip(" vs ")

    base_row = {
        "Case Number": case_no,
        "Case Type": parsed.case_type or "EX - Execution Petition Under Order 21",
        "CNR": cino,
        "Case Title": title,
        "Filing Number": parsed.filing_number or "",
        "Filing Date": filing_d,
        "Registration Number": clean_reg_no,
        "_clean_reg_no": clean_reg_no,
        "Registration Date": reg_d,
        "Main Case Number": main_case_no,
        "Main CNR": main_cnr,
        "Main Filing Number": main_filing_no,
        "First Hearing Date": first_hd,
        "Decision Date": dec_d,
        "Case Status": parsed.case_status or "Case disposed",
        "Nature of Disposal": parsed.nature_of_disposal or "",
        "Case Duration (Days)": case_dur,
        "Filing to First Hearing Duration (Days)": f2h_dur,
        "Court Name": parsed.court_name or "PRL. CITY CIVIL AND SESSIONS JUDGE",
        "Court Room & Judge": parsed.court_number_judge or "CCH53 LII ADDL. CITY CIVIL AND SESSIONS JUDGE",
        "Court Complex": "City Civil Court Complex, Bangalore",
        "State": "Karnataka",
        "District": "BENGALURU",
        "Petitioner": pet_str,
        "Petitioner Advocate": pet_adv_str,
        "Respondent and Advocate": resp_and_adv_str,
        "Acts": acts_str,
        "Order Number": ord_num,
        "Order Details": ord_details,
        "Judgment PDF URL": pdf_url,
        "Order Operative Ruling": order_sec["operative"],
        "Order Procedural History": order_sec["procedural"],
        "Order Judicial Findings": order_sec["findings"],
        "Order Annexed Proceedings": order_sec["annexed"],
        "Process ID": proc_id,
        "Process Title": proc_title,
        "Process Date": proc_date,
        "Establishment Code": "3",
        "Complex Code": "1030135",
        "Scrape Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    rows = []
    enriched_count = 0
    if parsed.hearings:
        for idx, h in enumerate(parsed.hearings, start=1):
            row = dict(base_row)
            row["Hearing Index"] = str(idx)
            b_date = s.format_date(h.business_date)
            row["Business Date"] = b_date
            row["Hearing Judge"] = h.judge or parsed.court_number_judge

            purp = (getattr(h, "purpose", getattr(h, "purpose_of_hearing", "")) or "").strip()
            row["Purpose of Hearing"] = purp

            if purp.lower() == "disposed" or not h.hearing_date:
                row["Hearing Date"] = dec_d or ""
            else:
                row["Hearing Date"] = s.format_date(h.hearing_date)

            if b_date in b_map and b_map[b_date]["text"]:
                row["Business Text"] = b_map[b_date]["text"]
                row["Next Purpose"] = b_map[b_date]["np"]
                row["Next Hearing Date (Hearing)"] = b_map[b_date]["nhd"]
                enriched_count += 1
            else:
                row["Business Text"] = ""
                row["Next Purpose"] = ""
                row["Next Hearing Date (Hearing)"] = ""
            rows.append(row)
    else:
        row = dict(base_row)
        row["Hearing Index"] = "1"
        row["Business Date"] = ""
        row["Hearing Date"] = dec_d or ""
        row["Hearing Judge"] = ""
        row["Purpose of Hearing"] = ""
        row["Business Text"] = ""
        row["Next Purpose"] = ""
        row["Next Hearing Date (Hearing)"] = ""
        rows.append(row)

    j_obj = {
        "case_no": case_no,
        "cino": cino,
        "registration_number": clean_reg_no,
        "filing_number": parsed.filing_number,
        "filing_date": filing_d,
        "registration_date": reg_d,
        "decision_date": dec_d,
        "disposal_nature": parsed.nature_of_disposal,
        "court_name": parsed.court_name,
        "judge": parsed.court_number_judge,
        "petitioner": pet_str,
        "petitioner_advocate": pet_adv_str,
        "respondent": resp_str,
        "acts": acts_str,
        "hearings": [
            {
                "index": r["Hearing Index"],
                "business_date": r["Business Date"],
                "hearing_date": r["Hearing Date"],
                "judge": r["Hearing Judge"],
                "purpose": r["Purpose of Hearing"],
                "business_text": r["Business Text"],
                "next_purpose": r["Next Purpose"],
                "next_hearing_date": r["Next Hearing Date (Hearing)"],
            }
            for r in rows
        ],
        "has_pdf": has_pdf,
    }

    elapsed = round(time.time() - t0, 2)
    case_data = {
        "rows": rows,
        "json": j_obj,
        "has_pdf": has_pdf,
        "elapsed": elapsed,
        "business_text_enriched": True,
    }

    return case_no, case_data, enriched_count


def main():
    if not CHECKPOINT_FILE.exists():
        log.error("Checkpoint not found.")
        return

    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        ckpt = json.load(f)

    roster = s.load_master_case_roster()
    queue = [item for item in roster if item[2] not in ckpt]

    log.info(f"Master Roster: {len(roster)} | Already in Checkpoint: {len(ckpt)} | Remaining Queue: {len(queue)}")
    if not queue:
        log.info("All 2023 cases are already 100% scraped! Regenerating final deliverables...")
        export_checkpoint_preview.export_preview()
        return

    client = s.get_thread_client()
    cases_completed = 0
    total_hearings_enriched = 0
    t_start = time.time()
    interrupted = False

    try:
        for idx, c_tuple in enumerate(queue, start=1):
            time.sleep(1.0)
            case_no, case_data, enriched_count = scrape_unified_case(client, c_tuple)
            if not case_data:
                log.warning("[%d/%d] Skipping %s due to retrieval failure.", idx, len(queue), case_no)
                continue

            ckpt[case_no] = case_data
            s.save_checkpoint(ckpt)
            cases_completed += 1
            total_hearings_enriched += enriched_count

            elapsed = time.time() - t_start
            rate = cases_completed / elapsed if elapsed > 0 else 0.0
            eta_mins = (len(queue) - cases_completed) / (rate * 60) if rate > 0 else 0.0

            log.info(
                f"[{cases_completed:4d}/{len(queue)}] Done: {case_no} | "
                f"Hearings: {len(case_data['rows'])} ({enriched_count} verbatim) | "
                f"PDF: {case_data['has_pdf']} | {case_data['elapsed']}s | "
                f"Overall: {len(ckpt)}/2283 ({len(ckpt)/2283*100:.1f}%) | "
                f"ETA: {eta_mins:.1f}m"
            )

            # Auto-export preview every 25 cases
            if cases_completed % 25 == 0:
                try:
                    export_checkpoint_preview.export_preview()
                except Exception as ex:
                    log.warning("Export preview skipped: %s", ex)

    except KeyboardInterrupt:
        interrupted = True
        log.warning("\n[INTERRUPT DETECTED] Gracefully stopping scraper...")
    finally:
        s.save_checkpoint(ckpt)
        status_str = "SCRAPING PAUSED BY USER" if interrupted else "SCRAPING FINISHED"
        log.info(f"\n{'='*70}\n {status_str}: {cases_completed} cases scraped ({total_hearings_enriched} hearings enriched)\n{'='*70}")
        log.info("Regenerating final updated CSV, Excel, and JSON deliverables...")
        export_checkpoint_preview.export_preview()


if __name__ == "__main__":
    main()
