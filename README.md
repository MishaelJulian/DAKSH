# eCourts High-Performance Unified Scraper Suite

Production-grade, single-pass automated scraping and extraction engine for Indian eCourts (`ecourtindia_v6`), engineered for polite, zero-omission extraction (4–7s per case), resilient anti-WAF session management, and comprehensive legal analysis.

---

## Key Capabilities

1. **High-Fidelity Zero-Loss Throughput (4–7s per case):**
   - Powered by `curl_cffi` with Chrome TLS fingerprint impersonation and persistent HTTP/2 keep-alive.
   - Polite pacing (1.0s–1.5s between requests) ensures zero dropped hearings, zero omitted business text, and zero WAF IP bans.

2. **Single-Pass Comprehensive Extraction:**
   - **Case Metadata:** CNR, Filing/Registration numbers & dates, Case Status, Coram/Judge, Nature of Disposal, Durations.
   - **Litigants & Representation:** Petitioners, Respondents, and individual Advocate assignments.
   - **Statutory Acts & Sections:** Automatic deduplication and normalization.
   - **Process Issuances:** Process ID, Title, and Service Dates.
   - **Parent / Main Matters:** Connected suit numbers and Main CNR links.
   - **Verbatim Hearing History:** Scrapes every hearing's verbatim `Business Text`, `Purpose`, and `Next Hearing Date` via `viewBusiness`.

3. **Authentic Judicial PDF Integration & Decomposition:**
   - Directly downloads authentic court order PDFs from `home/display_pdf`.
   - Utilizes PyMuPDF (`fitz`) to decompose the authentic order text into 4 analytical legal columns:
     - `Order Operative Ruling`
     - `Order Procedural History`
     - `Order Judicial Findings`
     - `Order Annexed Proceedings`

4. **Self-Healing Anti-WAF Session Resilience:**
   - Dynamic session handshake captures `app_token`, versioned `components.js`, server-assigned delimiters, and dynamic security tokens.
   - Automatic 65-second cooldown and reconnection if firewall rate limits are triggered.

5. **Atomic Checkpointing & Multi-Format Deliverables:**
   - Checkpoints state incrementally after every case to prevent data loss.
   - Auto-generates three deliverables simultaneously:
     - **Excel (`.xlsx`):** Formatted with `@` text protection for IDs and clickable hyperlinks that open local authentic court order PDFs.
     - **CSV (`.csv`):** Strict RFC 4180 standard with UTF-8 BOM encoding for Excel/database import.
     - **JSON (`.json`):** Deep nested relational structure for data science pipelines.

---

## Project Structure

```
daksh/
├── run_scraper.py                  # Master unified CLI entrypoint
├── scrape_remaining_2023_unified.py # Single-pass unified pipeline engine
├── scrape_all_2023_disposed.py     # Worker client, TLS session & PDF decomposer
├── export_checkpoint_preview.py    # Triple deliverable exporter (Excel, CSV, JSON)
├── deeper_tool/                    # Local deep HTML parser and dataclass models
│   ├── parser.py                   # BeautifulSoup case history parser
│   ├── models.py                   # Strongly typed dataclasses
│   └── __init__.py
├── ecourts/                        # Core utilities & CAPTCHA preprocessing
├── pilot_output/                   # Output storage
│   ├── checkpoint_405_cases.json   # Master atomic checkpoint
│   └── orders/                     # Downloaded authentic court order PDFs
├── disposed_2311.html              # Search results roster table (input source)
├── requirements.txt                # Python package dependencies
└── README.md                       # Documentation
```

---

## Quick Start: Clone & Run

```bash
# 1. Clone repository
git clone https://github.com/MishaelJulian/DAKSH.git
cd DAKSH

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start scraping with automated audit
python run_scraper.py
```

---

## Working with an AI Agent (Recommended Workflow)

If you are pair-programming with an AI coding assistant (such as **Google Antigravity**, **Cursor**, **Gemini**, **Claude Dev / Cline**, or **GitHub Copilot**):

1. **Clone the repository** and open the `DAKSH` folder in your IDE.
2. In your chat prompt, simply instruct your AI agent:
   > *"Read `MASTER_PROMPT.md` and follow its instructions to begin our scraping run."*
3. **What your AI agent will automatically do:**
   * **Prompt you for the target year:** It will ask whether to scrape **2024** or **2025** (acknowledging 2023 is already 100% finished with all 2,283 cases archived).
   * **Enforce Zero-Omission Pacing:** It will operate at a polite 4–7s pacing to ensure 100% of all hearing business text and authentic court orders are extracted without firewall bans.
   * **Update Deliverables In-Place:** It will update `Consolidated_Executive_Petitions_<YEAR>_FINAL.*` (`.xlsx`, `.csv`, `.json`) directly without creating clutter.
   * **Run the Integrity Audit:** Whenever scraping finishes or is paused, it will automatically run and display a complete mathematical audit (verifying 0 duplicates, 0 omissions, and 100% PDF binary validity).

---

## Detailed Installation & Setup

1. **Prerequisites:** Python 3.10+ installed on Windows, macOS, or Linux.
2. **Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

### 1. Run on Full Case Roster
Scrapes all cases listed in `disposed_2311.html` (skipping already checkpointed cases automatically):
```bash
python run_scraper.py
```

### 2. Test-Run on Specific Number of Cases
To test the pipeline on the first 5 un-scraped cases:
```bash
python run_scraper.py --limit 5
```

### 3. Run on Custom Search Results HTML
To scrape cases from any other year or court complex search results table:
```bash
python run_scraper.py --input path/to/your_cases.html
```

### 4. Re-Export Deliverables Only
To regenerate the final Excel (`.xlsx`), CSV (`.csv`), and JSON (`.json`) files instantly from the existing checkpoint without making network calls:
```bash
python run_scraper.py --export-only
```

---

## Output Columns (47/52-Column Standard Schema)

| Category | Columns |
|---|---|
| **Case Identification** | `Case Number`, `Case Type`, `CNR`, `Case Title`, `Filing Number`, `Filing Date`, `Registration Number`, `Registration Date` |
| **Connected Suits** | `Main Case Number`, `Main CNR`, `Main Filing Number` |
| **Disposal & Durations** | `First Hearing Date`, `Decision Date`, `Case Status`, `Nature of Disposal`, `Case Duration (Days)`, `Filing to First Hearing Duration (Days)` |
| **Court Details** | `Court Name`, `Court Room & Judge`, `Court Complex`, `State`, `District`, `Establishment Code`, `Complex Code` |
| **Parties & Representation** | `Petitioner`, `Petitioner Advocate`, `Respondent and Advocate`, `Acts` |
| **Hearing Business** | `Hearing Index`, `Business Date`, `Hearing Date`, `Hearing Judge`, `Purpose of Hearing`, `Business Text`, `Next Purpose`, `Next Hearing Date (Hearing)` |
| **Judicial Orders & PDF** | `Order Number`, `Order Details`, `Judgment PDF URL` *(Clickable Link)*, `Order Operative Ruling`, `Order Procedural History`, `Order Judicial Findings`, `Order Annexed Proceedings` |
| **Process Tracking** | `Process ID`, `Process Title`, `Process Date`, `Scrape Timestamp` |
