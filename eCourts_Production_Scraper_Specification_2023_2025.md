# eCourts Executive Petition Scraper — Production Specification
## 2023–2025 | Zero-Loss / Zero-Defect Requirement

### CRITICAL PRODUCTION RULE

The scraper MUST prioritize data integrity over speed.

The objective is NOT merely to scrape cases.

The objective is:

> For every target case, capture EVERY piece of information that is
> actually exposed by the eCourts portal, preserve it without alteration,
> maintain the correct relationships between tables, and export it
> without losing information.

NEVER fabricate, infer, silently discard, overwrite, truncate, or
normalize away source information.

If information is genuinely unavailable on the portal, preserve the
field as empty/null and explicitly distinguish it from a scraping
failure.

---

# 1. TARGET

Portal:
https://services.ecourts.gov.in/ecourtindia_v6/

Target:

State:
Karnataka

District:
BENGALURU

Court Complex:
City Civil Court Complex, Bangalore

Establishment:
PRL. CITY CIVIL AND SESSIONS JUDGE

Case Type:
EX / Execution Petition

Status:
Disposed

Years:
2023
2024
2025

---

# 2. CURRENT PRODUCTION POSITION

2023 production scraping has already completed and been validated
through:

Serial:
140

Last completed case:
EX/187/2023

Next case:
EX/188/2023

Therefore:

IMPORTANT:
The next production run MUST resume from CASE 141 / EX/188/2023.

DO NOT restart from case 1.

DO NOT modify the already validated 140 completed cases unless a
separate repair/audit operation explicitly requires it.

DO NOT duplicate cases 1–140.

The scraper must identify already completed cases using stable
identifiers such as:

- CNR
- Case Number
- Serial Number

and skip them safely.

---

# 3. COMPLETE DATA REQUIREMENT

For EVERY case, extract all information available from:

1. Search result row
2. Case details page
3. Case status information
4. Party information
5. Advocate information
6. Acts and Sections
7. Processes
8. Case History / Hearing History
9. Purpose of Hearing
10. Business / Daily Status
11. Orders
12. Order metadata
13. Downloadable document/PDF information
14. Transfers
15. Any additional structured information exposed by the case page
16. Any additional linked case-information pages exposed by eCourts

Do not stop extraction after obtaining the basic case metadata.

---

# 4. CASE-LEVEL DATA

Capture, where available:

- Serial Number
- Case Number
- Case Type
- Filing Number
- Filing Date
- Registration Number
- Registration Date
- CNR Number
- e-Filing Number
- e-Filing Date
- First Hearing Date
- Next Hearing Date
- Decision Date
- Case Status
- Sub Stage
- Nature of Disposal
- Disposal Date
- Court Name
- Court Number
- Judge
- Establishment
- Court Complex
- District
- State

Preserve the exact source value.

Do not unnecessarily convert dates into a different representation.

---

# 5. PETITIONERS / RESPONDENTS

Capture EVERY party.

Do not capture only the first petitioner/respondent.

For each party preserve:

- sequence/order
- party name
- party type
- advocate name(s)
- advocate sequence where available
- all additional party information exposed by the portal

Maintain the original ordering.

One-to-many relationships MUST NOT be collapsed into a single value
if doing so would lose information.

---

# 6. ACTS AND SECTIONS

Capture EVERY Act and Section associated with the case.

Preserve:

- Act name
- Section
- sequence/order
- any additional fields exposed

Do not overwrite multiple Acts/Sections with the last value encountered.

---

# 7. PROCESSES

Capture EVERY process row.

For each process preserve all available:

- Process ID
- Process title/type
- Process date
- status
- recipient/party information
- additional fields

If no process exists, record that the case has no process record.

Do not interpret an empty process table as a scraper failure.

---

# 8. CASE HISTORY / HEARINGS

Capture EVERY hearing/history row.

For each row preserve:

- hearing date
- hearing purpose
- Purpose of Hearing
- sub-stage
- business
- summary
- judge
- additional fields exposed by the portal

CRITICAL:

`Purpose of Hearing` MUST remain a dedicated field.

Do NOT merge it into another field if doing so loses its original
meaning.

Do NOT only capture the latest hearing.

---

# 9. BUSINESS / DAILY STATUS

Capture all available daily/business status information.

Preserve:

- date
- business
- purpose
- status
- judge
- stage/sub-stage
- additional information

If multiple rows exist, preserve all rows.

---

# 10. ORDERS — CRITICAL

Orders must be treated as multiple independent layers.

For EVERY order:

### Layer A — Order Record

Capture:

- order date
- order title/type
- order number where available
- business/disposal information
- judge
- metadata
- order page URL/reference

### Layer B — Order Page

Record whether the order page was successfully opened.

Store a field such as:

`order_page_found = true/false`

### Layer C — Order Text

Record whether actual order text was successfully extracted.

Store:

`order_text_found = true/false`

Preserve the complete available text.

DO NOT truncate order text.

### Layer D — Downloadable Document

Separately determine whether a downloadable document/PDF link is
actually exposed.

Store:

`document_link_found = true/false`

and, where available:

`document_url`

CRITICAL:

An order page existing does NOT mean that a PDF exists.

An order text being extracted does NOT mean that a PDF exists.

A missing PDF URL MUST NOT be represented as an extraction success.

Never fabricate document URLs.

---

# 11. TRANSFERS

Capture EVERY transfer record exposed by the case.

Preserve:

- registration number
- transfer date
- from court
- to court
- additional transfer metadata

If the source page contains no transfer records:

`transfer_count = 0`

This is different from:

`transfer_extraction_failed = true`

Do not confuse "no transfers" with "scraper failed."

---

# 12. RAW HTML SNAPSHOTS

For every successfully processed case, save the raw HTML snapshot.

Required structure:

YEAR_DIR/
    snapshots/
        search_results_page_1.html
        search_results_page_2.html
        ...
        case_<safe_identifier>.html

Where possible, also preserve HTML for linked order/document pages.

Snapshots are the source-of-truth evidence for later auditing.

NEVER delete snapshots during production scraping.

---

# 13. SESSION TIMEOUT HANDLING — CRITICAL

The eCourts portal has previously returned:

"Oops! Session timeout..!!!"

This MUST be detected explicitly.

If detected:

1. Immediately stop scraping the current case.
2. Save the current checkpoint.
3. Record the exact case being processed.
4. Record the last successfully completed case.
5. Record the current page.
6. Record the current result index.
7. Record order progress.
8. DO NOT continue clicking/searching.
9. DO NOT repeatedly retry the expired session.
10. Close the session safely.
11. Require a fresh valid eCourts session before continuing.

The scraper MUST NEVER hammer the portal after a session timeout.

A timeout MUST NOT cause the scraper to mark the current case as
successfully scraped.

---

# 14. CHECKPOINTING

Checkpoint frequently.

At minimum:

- every 5 cases
- immediately before risky navigation
- immediately after successful case completion
- immediately when a session timeout/error occurs

Checkpoint must contain:

- year
- search parameters
- current result page
- current result index
- last completed serial number
- last completed case number
- last completed CNR
- completed case count
- failed case count
- current case
- completed order count
- pending order count
- timestamp

Checkpoint writes MUST be atomic.

Never overwrite a valid checkpoint with corrupted/incomplete data.

---

# 15. RESUME BEHAVIOUR

When using:

`--resume`

the scraper MUST:

1. Load the checkpoint.
2. Load cases.json.
3. Determine the last successfully completed case.
4. Re-establish a fresh eCourts session.
5. Re-run the search.
6. Locate the exact next uncompleted case.
7. Continue from there.

For the current 2023 run:

LAST COMPLETED:
EX/187/2023

NEXT:
EX/188/2023

Therefore the scraper MUST begin production processing at:

CASE 141
EX/188/2023

Do NOT rescrape cases 1–140 during normal production execution.

---

# 16. FAILURE CLASSIFICATION

Every failure must be classified.

Examples:

`SESSION_TIMEOUT`

`NETWORK_ERROR`

`PAGE_LOAD_TIMEOUT`

`CASE_NOT_FOUND`

`ORDER_PAGE_NOT_FOUND`

`DOCUMENT_LINK_NOT_FOUND`

`PARSER_ERROR`

`CAPTCHA_REQUIRED`

`UNKNOWN_PORTAL_ERROR`

A failure must never silently become an empty field.

---

# 17. MISSING DATA AUDIT

After every batch, run an audit.

For each case compare:

RAW HTML
    ↓
PARSED JSON
    ↓
NORMALIZED DATA
    ↓
CSV/XLSX

Flag:

- fields present in HTML but absent in JSON
- fields present in JSON but absent in CSV
- truncated text
- missing party rows
- missing history rows
- missing order rows
- missing process rows
- missing transfer rows
- duplicate rows
- incorrect relationships

Do not automatically "repair" data by guessing.

---

# 18. ZERO-LOSS EXPORT REQUIREMENT

The exported dataset MUST NOT lose information during transformation.

Generate:

cases.csv
case_history.csv
orders.csv
business.csv
processes.csv
transfers.csv
documents.csv

and the consolidated/master dataset.

The normalized relational files are the authoritative representation
for one-to-many information.

The consolidated CSV may contain serialized/list representations,
but it MUST NOT be treated as the only source of truth.

---

# 19. CSV FORMAT

All CSV files MUST use:

UTF-8 with BOM

Encoding:

`utf-8-sig`

Requirements:

- preserve Unicode
- preserve Kannada text
- preserve English text
- no mojibake
- no silent character replacement
- no accidental truncation

---

# 20. CONSOLIDATED OUTPUT FORMAT

The final consolidated CSV should contain ONE ROW PER CASE.

It should contain the canonical case-level fields.

Repeated/multi-row information must be represented consistently without
losing information.

Do NOT create duplicate columns such as:

Petitioner
Petitioner_1
Petitioner_2
...

unless explicitly required by the specification.

Do NOT retain redundant columns with the same underlying information.

Column names must be unique.

Column names must be stable across 2023, 2024 and 2025.

---

# 21. DATA QUALITY RULES

Before a case is marked COMPLETE:

- case number must exist
- CNR must exist where the portal provides it
- petitioner information must be captured where present
- respondent information must be captured where present
- disposal information must be captured where present
- registration information must be captured where present
- history must be captured where present
- orders must be inspected where present
- documents must be explicitly checked
- transfers must be explicitly checked
- HTML snapshot must exist

A missing optional record is acceptable.

A failed extraction must NOT be silently treated as an optional blank.

---

# 22. DUPLICATE PREVENTION

Use CNR as the primary stable identifier.

Secondary identifiers:

- Case Number
- Serial Number

No case may appear twice in the authoritative case dataset.

No history/order/process/transfer row may be duplicated because of
pagination, retries, or session recovery.

---

# 23. PORTAL PAGINATION

Automatically process every result page.

Never assume that page 1 contains all cases.

Continue until the portal explicitly indicates that there are no more
results.

Record:

- page number
- number of rows
- first case
- last case

for every search-results page.

---

# 24. IMPORTANT: DO NOT CONFUSE ORDER COUNT WITH PDF COUNT

These are independent metrics:

`order_count`

`order_page_count`

`order_text_count`

`document_link_count`

For example:

order_count = 5
order_page_count = 5
order_text_count = 5
document_link_count = 0

is VALID if the portal exposed five order pages/texts but no
downloadable document links.

---

# 25. FINAL VALIDATION

Before declaring a year COMPLETE:

Verify:

1. Search result count
2. Unique case count
3. JSON count
4. CSV count
5. XLSX count
6. Relational case count
7. History row count
8. Order row count
9. Process row count
10. Transfer row count
11. Document row count
12. Snapshot count
13. Duplicate CNRs
14. Missing CNRs
15. Missing disposal dates
16. Missing petitioners
17. Missing respondents
18. Missing order-page results
19. Missing document links
20. Encoding
21. Column uniqueness
22. JSON → CSV consistency
23. JSON → XLSX consistency

The final validation report MUST distinguish:

- legitimate absence
- extraction failure
- portal-unavailable information
- pending repair

---

# 26. DO NOT CLAIM 100% COMPLETENESS WITHOUT EVIDENCE

The scraper may only declare:

`COMPLETE`

when every target result has been processed and the final audit passes.

If eCourts does not expose a particular field, the correct result is:

`NOT_AVAILABLE_FROM_PORTAL`

not a fabricated value.

If extraction failed, the correct result is:

`EXTRACTION_FAILED`

not blank.

---

# 27. CURRENT EXECUTION

For the next production run:

YEAR:
2023

START CASE:
141

START CASE NUMBER:
EX/188/2023

PREVIOUSLY VALIDATED:
Cases 1–140

PRODUCTION SCRAPING:
ENABLED

ORDER REPAIR:
Do NOT mix targeted historical repair with normal production scraping.

The production run must first continue sequentially from case 141.

If a session timeout occurs, STOP safely and checkpoint.

If an "Oops! Session timeout" message appears:

DO NOT continue.

DO NOT skip forward.

DO NOT mark the case complete.

DO NOT repeatedly retry.

Wait for a fresh session and resume from the exact uncompleted case.

---

# 28. FINAL PRINCIPLE

SPEED IS SECONDARY.

DATA INTEGRITY IS PRIMARY.

The required pipeline is:

eCourts
   ↓
Raw HTML
   ↓
Complete parser
   ↓
Validated JSON
   ↓
Relational datasets
   ↓
Consolidated dataset
   ↓
CSV/XLSX
   ↓
Independent zero-loss audit

The scraper must preserve everything the portal actually exposes,
while clearly distinguishing unavailable information from extraction
failures.

NO SILENT DATA LOSS.
NO DUPLICATES.
NO FABRICATED VALUES.
NO SKIPPED CASES.
NO UNCHECKED EMPTY FIELDS.
NO CONTINUATION AFTER SESSION TIMEOUT.
