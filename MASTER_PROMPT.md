# MASTER PROMPT — eCourts Karnataka Scraper Gold Standard Audit & Finalization (2010 Benchmark Dataset)

## Objective

This is the **final verification and productionization phase** of the eCourts Karnataka scraper.

We are **NOT** moving to 2023–2025 yet.

The goal is to create a **100% complete benchmark dataset** consisting of the **first 20 disposed Executive Petition (EX) cases from 2010** from:

* State: Karnataka
* District: BENGALURU
* Court Complex: City Civil Court Complex, Bangalore
* Establishment: PRL. CITY CIVIL AND SESSIONS JUDGE

This benchmark will become the reference implementation before scaling to the larger dataset.

---

## Acceptance Criterion

> **Goal:** Produce a benchmark dataset of the first 20 disposed Executive Petition (EX) cases from 2010 for the Bengaluru City Civil Court. Every field visible on the eCourts website—including case-level information, hearing-level information, processes, transfers, order details, and Daily Status information—must be extracted, preserved, validated, and exported without loss. This benchmark will serve as the validated scraper before scaling to the 2023–2025 dataset.

---

## Target Website

The scraper must operate exclusively on the official Indian eCourts Case Status portal.

Website:
```text
https://services.ecourts.gov.in/ecourtindia_v6/
```

Navigate to:
```text
Case Status
→ Search by Case Type
```

Configure the search exactly as follows:

```text
State:
Karnataka

District:
BENGALURU

Court Complex:
City Civil Court Complex, Bangalore

Establishment:
PRL. CITY CIVIL AND SESSIONS JUDGE

Case Type:
EX – Execution Petition Under Order

Year:
2010

Status:
Disposed
```

After solving the CAPTCHA manually, execute the search and process **only the first 20 Executive Petition cases** from the search results.

---

## Navigation Workflow

```text
Open:
https://services.ecourts.gov.in/ecourtindia_v6/

↓

Select "Case Status"

↓

Select "Case Type"

↓

Choose:
State: Karnataka
District: BENGALURU
Court Complex: City Civil Court Complex, Bangalore
Establishment: PRL. CITY CIVIL AND SESSIONS JUDGE

↓

Select:
EX – Execution Petition Under Order

↓

Year = 2010

↓

Disposed

↓

Pause for manual CAPTCHA entry

↓

Click Go

↓

Verify search results loaded

↓

Scrape first 20 cases

↓

For each case:
    Open View
    Scrape main page
    Scrape Processes
    Scrape Case History
    Scrape Transfers
    Open every Order
    Scrape Daily Status
    Return to case list
```

---

## Search Parameters

Exactly use:

```text
State:
Karnataka

District:
BENGALURU

Court Complex:
City Civil Court Complex, Bangalore

Establishment:
PRL. CITY CIVIL AND SESSIONS JUDGE

Case Type:
EX – Execution Petition Under Order

Year:
2010

Status:
Disposed
```

Only scrape the **first 20 Executive Petition cases**.

---

## PRIMARY GOAL

The scraper must extract **EVERY piece of information visible on every page** associated with each case.

No visible information should remain uncollected.

The scraper should behave like a human manually opening every available section.

---

## COMPLETE SCRAPING WORKFLOW

For every case:

```text
Search Result
↓
Open Case
↓
Scrape Main Page
↓
Open every Order link
↓
Scrape Daily Status
↓
Return
↓
Repeat for every Order
↓
Export
↓
Audit
↓
Validate
↓
Next Case
```

---

## MASTER EXTRACTION CHECKLIST

### 1. Case Details
Extract every field exactly as displayed, including:
* Case Type
* Filing Number
* Filing Date
* Registration Number
* Registration Date
* CNR Number
* e-Filing Number
* e-Filing Date
* QR Code URL (if available)
* First Hearing Date
* Decision Date
* Case Status
* Sub Stage
* Nature of Disposal
* Court Number
* Judge
* Court Name

Store null explicitly if blank.

---

### 2. Petitioner Section
Extract:
* Every petitioner
* Every advocate
* Preserve ordering
* Support multiple petitioners & advocates

---

### 3. Respondent Section
* Every respondent
* Every advocate
* Preserve ordering
* Support multiple respondents & advocates

---

### 4. Acts Section
Extract:
* Every Act
* Every Section
* Preserve exact wording

---

### 5. Processes Table
Extract every row:
* Process ID
* Process Title
* Process Date

---

### 6. Case History Table
Extract EVERY row:
* Judge
* Business Date
* Hearing Date
* Purpose of Hearing (NOTICE, ORDERS, SUMMONS, Disposed, Restored, etc.)

---

### 7. Final Orders
Extract every order:
* Order Number
* Order Date
* Order link
* Order URL (if available)

---

### 8. Open EVERY Order
Every order hyperlink must be opened.
Never assume one order. Open them ALL.

---

### 9. Daily Status Page
When an order opens, extract EVERYTHING visible:
* Business
* Nature of Disposal
* Disposal Date
* Judge
* Case Number
* CNR
* Court
* Case Title
* Date
* Daily Status heading
* Every text block, paragraph, and visible sentence

---

### 10. Business Text
Do not summarize or truncate. Store exactly, maintaining paragraphs, punctuation, and Unicode (including Kannada).

---

### 11. Transfers
Extract:
* Registration Number
* Transfer Date
* From Court
* To Court

---

### 12. Metadata
Generate:
* Order Count
* History Count
* Business Count
* Process Count
* Transfer Count
* Document Count
* Duration
* First Hearing
* Last Hearing

---

## AUTOMATIC AUDIT SYSTEM

After every case, run a complete audit ensuring all sections PASS:
- Case Details: PASS
- Petitioners: PASS
- Respondents: PASS
- Acts: PASS
- Processes: PASS
- Case History: PASS
- Orders: PASS
- Daily Status: PASS
- Business: PASS
- Transfers: PASS
- Export: PASS

---

## PAGE COMPARISON AUDIT & ROW COUNT VALIDATION
- Scraped output must match the live webpage 1-to-1.
- Website history length = JSON history length = CSV hearing rows = Excel hearing entries.
- Repeat for Orders, Processes, Transfers, Business entries.

---

## DATA PRESERVATION & ENCODING
- Ensure nested objects (`orders`, `history`, `business_list`, `processes`, `transfers`, `documents`) remain populated before and after export.
- Ensure UTF-8 with BOM for CSVs, UTF-8 for JSON, and native XLSX formatting.
- Preserve Unicode & Kannada characters without corruption.

---

## CONSOLIDATED & SUPPORTING DATASETS
- Produce one consolidated dataset where each row represents one hearing/business/order event.
- Generate supporting relational files:
  * `cases.json`
  * `Scraped_Cases.xlsx`
  * `Executive_Petitions_2010_Master.csv`
  * `Consolidated_Executive_Petitions_2010.csv`
  * `Consolidated_Executive_Petitions_2010.xlsx`
  * `case_history.csv`
  * `orders.csv`
  * `business.csv`
  * `processes.csv`
  * `transfers.csv`
  * `petitioners.csv` / `respondents.csv` / `acts.csv`

---

## Definition of Success
The benchmark dataset is considered complete only when:
1. Every visible field on the eCourts pages has been extracted.
2. Every linked order page has been visited.
3. Every hearing row has been captured.
4. Every "Purpose of Hearing" value has been captured.
5. Every business entry has been preserved.
6. Every process, transfer, petitioner, respondent, and act has been captured.
7. JSON, CSV, and Excel all contain the same information.
8. No nested data is lost during transformation or export.
9. UTF-8 encoding is preserved throughout.
10. The automatic audit reports **zero missing fields** across all 20 cases.
