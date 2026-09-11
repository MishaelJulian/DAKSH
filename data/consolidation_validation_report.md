# Consolidation Validation Report

This report documents the validation checks performed on the consolidated dataset created from the Karnataka eCourts Executive Petitions 2010 scraped data.

## Verification Summary

| Metric | Source Count | Consolidated Count | Status |
| :--- | :---: | :---: | :---: |
| Unique Cases | 20 | 20 | PASSED |
| History Rows | 333 | 333 | PASSED |
| Business Entries | 333 | 333 | PASSED |
| Orders | 333 | 333 | PASSED |
| Process Rows | 13 | 13 | PASSED |
| Transfer Rows | 6 | 6 | PASSED |
| Document Rows | 0 | 0 | PASSED |

## Detail Audit Checks

- **Unique Cases**: 20 / 20 cases represented.
- **Orphan Records**:
  - Missing histories: 0
  - Missing business entries: 0
  - Missing orders: 0
  - Missing processes: 0
  - Missing transfers: 0
- **Data Integrity**: All child tables (hearings, business, orders, processes, transfers) are 100% joined without data loss or accidental multiplication.
- **Cleaning Quality**: Web UI text block elements (such as "Back", "Daily Status", QR labels, navigation tags) have been completely stripped from the final fields using robust regular expressions.
