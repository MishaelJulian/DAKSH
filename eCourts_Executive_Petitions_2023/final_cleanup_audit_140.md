# 2023 — FINAL 140 CASE DATASET AUDIT

## Source Files

| File | Path |
|------|------|
| **Source** | `Consolidated_Executive_Petitions_2023.csv` |
| **Backup** | `Consolidated_Executive_Petitions_2023_BEFORE_FINAL_CLEANUP.csv` |
| **Final** | `Consolidated_Executive_Petitions_2023_FINAL.csv` |

---

## Dataset Structure

This dataset uses a **relational multi-row structure**: each case spans multiple rows,
with one row per hearing/business/order entry. This is NOT one-row-per-case.

---

## Summary Statistics

| Metric | Before | After |
|--------|--------|-------|
| **Total Rows** | 1858 | 1858 |
| **Total Columns** | 54 | 53 |
| **Unique Case Numbers** | 140 | 140 |
| **Unique CNRs** | 140 | 140 |
| **Duplicate Case Numbers** | 0 | 0 |
| **Duplicate CNRs** | 0 | 0 |
| **Rows Removed** | — | 0 |
| **Columns Removed** | — | 1 |

---

## Columns Removed

| Column | Reason |
|--------|--------|
| `Hearing Order Number` | 0% filled, never populated by scraper, redundant with 'Order Number' |

## Columns Merged

*(No columns were merged. All columns contain distinct information.)*

---

## Phase 1 Repair Verification

| Field | Cases with Data | Expected | Status |
|-------|----------------|----------|--------|
| **Registration Date** | 140/140 | 140 | ✅ PASS |
| **Sub Stage** | 140/140 | 140 | ✅ PASS |

---

## Data Completeness (Per Case)

| Field | Available | Total | Percentage |
|-------|-----------|-------|------------|
| CNR | 140 | 140 | 100.0% |
| Petitioner | 140 | 140 | 100.0% |
| Respondent | 140 | 140 | 100.0% |
| Registration Date | 140 | 140 | 100.0% |
| Sub Stage | 140 | 140 | 100.0% |
| Disposal Date | 140 | 140 | 100.0% |
| Nature of Disposal | 140 | 140 | 100.0% |
| Case Status | 140 | 140 | 100.0% |
| Filing Date | 140 | 140 | 100.0% |
| First Hearing Date | 140 | 140 | 100.0% |
| Decision Date | 140 | 140 | 100.0% |

## Relational Data Availability

| Field | Cases | Rows |
|-------|-------|------|
| Purpose of Hearing | 140/140 | 1856/1858 |
| Business Text | 140/140 | 1849/1858 |
| Order Text | 140/140 | 1849/1858 |
| Process ID | 104/140 | 445/1858 |
| Transfer Registration Number | 0/140 | 0/1858 |
| Order Link | 0/140 | 0/1858 |
| Documents | 0/140 | 0/1858 |

---

## Validation Checks

| Check | Result |
|-------|--------|
| 140_cases | ✅ PASS |
| 140_cnrs | ✅ PASS |
| no_dup_case_numbers | ✅ PASS |
| no_repeated_headers | ✅ PASS |
| no_unnamed_cols | ✅ PASS |
| reg_date_140 | ✅ PASS |
| sub_stage_140 | ✅ PASS |
| utf8_bom | ✅ PASS |
| order_preserved | ✅ PASS |
| history_preserved | ✅ PASS |
| business_preserved | ✅ PASS |
| processes_preserved | ✅ PASS |
| transfer_cols_present | ✅ PASS |
| documents_col_present | ✅ PASS |
| order_link_present | ✅ PASS |
| row_count_preserved | ✅ PASS |

---

## Column Order (Final — 53 columns)

| # | Column Name |
|---|-------------|
| 1 | `Case Number` |
| 2 | `Case Type` |
| 3 | `CNR` |
| 4 | `Case Title` |
| 5 | `Filing Number` |
| 6 | `Filing Date` |
| 7 | `Registration Number` |
| 8 | `Registration Date` |
| 9 | `First Hearing Date` |
| 10 | `Next Hearing Date` |
| 11 | `Last Hearing Date` |
| 12 | `Decision Date` |
| 13 | `Disposal Date` |
| 14 | `Case Status` |
| 15 | `Sub Stage` |
| 16 | `Nature of Disposal` |
| 17 | `Case Duration (Days)` |
| 18 | `Filing to First Hearing Duration (Days)` |
| 19 | `Court Name` |
| 20 | `Court Complex` |
| 21 | `State` |
| 22 | `District` |
| 23 | `Petitioner` |
| 24 | `Petitioner Advocate` |
| 25 | `Respondent` |
| 26 | `Respondent Advocate` |
| 27 | `Acts` |
| 28 | `Sections` |
| 29 | `Hearing Date` |
| 30 | `Hearing Index` |
| 31 | `Hearing Judge` |
| 32 | `Purpose of Hearing` |
| 33 | `Hearing Business Summary` |
| 34 | `Business Date` |
| 35 | `Business Index` |
| 36 | `Business Text` |
| 37 | `Order Date` |
| 38 | `Order Index` |
| 39 | `Order Number` |
| 40 | `Order Link` |
| 41 | `Order Nature of Disposal` |
| 42 | `Order Disposal Date` |
| 43 | `Order Judge` |
| 44 | `Order Text` |
| 45 | `Order Document Count` |
| 46 | `Process ID` |
| 47 | `Process Title` |
| 48 | `Process Date` |
| 49 | `Transfer Registration Number` |
| 50 | `Transfer Date` |
| 51 | `Transfer From Court` |
| 52 | `Transfer To Court` |
| 53 | `Documents` |

---

## Changes Made

1. **Backup created**: `Consolidated_Executive_Petitions_2023_BEFORE_FINAL_CLEANUP.csv`
2. **Removed 1 dead column**: `Hearing Order Number` (0% populated, never used by scraper)
3. **Text normalization**: Stripped leading/trailing whitespace, normalized internal double-spaces in non-text-heavy columns
4. **Column reordering**: Reorganized into logical groups (case info → dates → status → parties → hearing details → business → orders → processes → transfers → documents)
5. **Encoding**: UTF-8 with BOM (`utf-8-sig`) for Excel compatibility
6. **No rows removed**: All 1858 relational rows preserved
7. **No data loss**: All meaningful scraped information retained

### Columns Intentionally KEPT (despite being empty or constant)

| Column | Status | Reason Kept |
|--------|--------|-------------|
| `Order Link` | 0% filled | Placeholder for future order-link repair |
| `Transfer Registration Number` | 0% filled | Legitimate structural field; no cases have transfers |
| `Transfer Date` | 0% filled | Same |
| `Transfer From Court` | 0% filled | Same |
| `Transfer To Court` | 0% filled | Same |
| `Documents` | 0% filled | Legitimate structural field |
| `Respondent Advocate` | 1.6% filled | Sparse but legitimate data (29 rows have value) |
| `Court Complex` | 100% constant | Legitimate case metadata |
| `State` | 100% constant | Legitimate case metadata |
| `District` | 100% constant | Legitimate case metadata |
| `Case Type` | 100% constant | Legitimate case metadata |
| `Case Status` | 100% constant | Legitimate case metadata |
| `Acts` | 100% constant | Legitimate legal information |
| `Order Document Count` | 100% constant (0) | Legitimate order metadata |

---

## Kannada Preservation

No Kannada characters were found in this dataset. — **N/A**

---

## Encoding Verification

- **UTF-8 BOM**: ✅ Present
- **File size**: 3,345,018 bytes

---

## FINAL STATUS

> [!TIP]
> ## ✅ READY FOR BOSS DELIVERY
>
> All validation checks passed. The dataset contains 140 cases across 1858 relational rows with zero data loss.
