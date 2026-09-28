import os
import sys
import re
import fitz

repo_root = r"C:\Users\misha\OneDrive\Desktop\LeScrape"
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from deeper_tool.scraper import DeeperScraper

def main():
    print("=== Testing Live PDF Fetch via DeeperScraper curl session ===")
    out_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\test_output\EX_2_2023\orders"
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, "judgment_EX_2_2023_order_1.pdf")

    scraper = DeeperScraper(
        db_path=r"C:\Users\misha\OneDrive\Desktop\LeScrape\deeper_tool\deeper_ecourts.db",
        cookie_file=r"C:\Users\misha\OneDrive\Desktop\LeScrape\deeper_tool\cookies_session.txt"
    )

    print("[1/4] Initializing session handshake...")
    scraper.init_session()

    print("[2/4] Setting active establishment...")
    scraper.set_establishment(complex_code="1030135", state_code="3", dist_code="20", est_code="3")

    print("[3/4] Registering case EX/2/2023 in session via viewHistory...")
    view_params = {
        "case_no": "202300000022023",
        "cino": "KABC010342242022",
        "court_code": "3",
        "hideparty": "",
        "search_flag": "CScaseNumber",
        "state_code": "3",
        "dist_code": "20",
        "court_complex_code": "1030135",
        "search_by": "CScaseType",
    }
    vh_html = scraper.fetch_view_history(view_params)
    print(f"      viewHistory response length: {len(vh_html)} chars")

    onclick = "displayPdf('cl+sGJoSJ58oyVespa8VHg==','wd/evbCOK7tqvcKwXT25tA==','5rHUl/fJ8k9+dheUWTi6OQ==','8NJb071ifDPc/70jxdgMFg+I5ofoKfz4CQ0t934yFW9MCiB9AnJK6BKMDh4ZxKiO','')"
    m = re.search(r"displayPdf\s*\((.*?)\)", onclick)
    args = [a.strip().strip("'\"") for a in m.group(1).split(",")]
    while len(args) < 5:
        args.append("")
    normal_v, case_val, court_code, filename, app_flag = args[:5]

    print("[4/4] Calling home/display_pdf in the same session...")
    payload = {
        "normal_v": normal_v,
        "case_val": case_val,
        "court_code": court_code,
        "filename": filename,
        "appFlag": app_flag,
    }
    res = scraper._post_api("home/display_pdf", payload)
    print("      display_pdf JSON response:", res)

    pdf_rel = res.get("order")
    if pdf_rel and res.get("status"):
        pdf_url = f"https://services.ecourts.gov.in/ecourtindia_v6/{pdf_rel}"
        print(f"      Downloading PDF from {pdf_url}...")
        pdf_bytes = scraper._curl(pdf_url, headers={"Referer": "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index"}, is_binary=True)
        print("      Downloaded bytes length:", len(pdf_bytes))
        if pdf_bytes.startswith(b"%PDF"):
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            print(f"[SUCCESS] Saved valid PDF to {pdf_path} ({len(pdf_bytes)} bytes)!")

            doc = fitz.open(pdf_path)
            print(f"      Pages: {len(doc)}")
            for p_no in range(len(doc)):
                print(f"--- Page {p_no + 1} ---")
                print(doc[p_no].get_text()[:300])
        else:
            print("      Response is not a valid PDF header:", pdf_bytes[:200])
    else:
        print("      Failed to obtain valid order from display_pdf.")

if __name__ == "__main__":
    main()
