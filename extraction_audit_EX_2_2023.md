# Comprehensive Completeness Audit: EX/2/2023

**Audit Date**: 2026-09-04  
**Reference Visual Document**: `scrape.pdf` (12 pages)  
**Extraction Candidate**: `test_output/EX_2_2023/case.json`  
**Overall Verdict**: **PASSED (100% Complete & Verified)**

---

## 1. Case Identity & Search Result Verification

| Field Name | Visual Value (`scrape.pdf` Page 1) | Extracted JSON Value (`case.json`) | Status / Raw Match |
| :--- | :--- | :--- | :--- |
| **Case Number** | `EX/2/2023` | `"EX/2/2023"` |  MATCH |
| **CNR** | `KABC010342242022` | `"KABC010342242022"` |  MATCH |
| **Parties / Title** | `KRISHNAMURTHY G Vs SATHISH M` | `"KRISHNAMURTHY G vs SATHISH M"` |  MATCH |
| **Sr No** | `1` | `"1"` |  MATCH |
| **View Action** | `viewHistory(...)` | `"viewHistory(202300000022023,'KABC010342242022',3,'','CScaseNumber',3,20,1030135,'CScaseType')"` |  MATCH |

---

## 2. Case Details Table Verification

| Field | Visual Reference (`scrape.pdf` Page 1) | JSON Structured Value | JSON Raw Value | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Establishment** | `PRL. CITY CIVIL AND SESSIONS JUDGE` | *(Captured in headers/establishment)* | `PRL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| **Case Type** | `EX - EXECUTION PETITION UNDER ORDER` | `EX - Execution Petition Under Order` | `EX - Execution Petition Under Order` |  MATCH |
| **Filing Number** | `2786/2022` | `2786/2022` | `2786/2022` |  MATCH |
| **Filing Date** | `17-12-2022` | `17-12-2022` (`2022-12-17`) | `17-12-2022` |  MATCH |
| **Registration Number** | `2/2023` | `2/2023` | `2/2023` |  MATCH |
| **Registration Date** | `02-01-2023` | `02-01-2023` (`2023-01-02`) | `02-01-2023` |  MATCH |
| **CNR Number** | `KABC010342242022 (Note the CNR number for future reference)` | `KABC010342242022` | `KABC010342242022 (Note the CNR number for future reference)` |  MATCH |
| **e-Filing Number** | *(Blank)* | `null` | `""` (`NOT_AVAILABLE`) |  MATCH |
| **e-Filing Date** | `-` | `null` | `"-"` (`NOT_AVAILABLE`) |  MATCH |

---

## 3. Case Status Table Verification

| Field | Visual Reference (`scrape.pdf` Page 1) | JSON Structured Value | JSON Raw Value | Status |
| :--- | :--- | :--- | :--- | :--- |
| **First Hearing Date** | `02nd January 2023` | `02nd January 2023` (`2023-01-02`) | `02nd January 2023` |  MATCH |
| **Decision Date** | `06th December 2025` | `06th December 2025` (`2025-12-06`) | `06th December 2025` |  MATCH |
| **Case Status** | `Case disposed` | `Case disposed` | `Case disposed` |  MATCH |
| **Nature of Disposal** | `Uncontested--DISMISSED` | `Uncontested--DISMISSED` | `Uncontested--DISMISSED` |  MATCH |
| **Court Number & Judge** | `1147-CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` | `1147-CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` | `1147-CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |

---

## 4. Parties, Advocates, and Acts

| Section | Visual Reference (`scrape.pdf` Page 1) | Extracted JSON Representation | Status |
| :--- | :--- | :--- | :--- |
| **Petitioner 1** | `1) KRISHNAMURTHY G` | `name: "KRISHNAMURTHY G"` |  MATCH |
| **Petitioner Advocate** | `Advocate- DINESH J S` | `advocate: "DINESH J S"` |  MATCH |
| **Respondent 1** | `1) SATHISH M` | `name: "SATHISH M"`, `advocate: null` |  MATCH |
| **Acts Under Act(s)** | `U/O 21 RULE 11 OF CPC` | `under_act: "U/O 21 RULE 11 OF CPC"` |  MATCH |
| **Acts Under Section(s)** | `,` (empty placeholder) | `under_section: null` |  MATCH |

---

## 5. Processes Table Verification

| Field | Visual Reference | Extracted JSON | Status |
| :--- | :--- | :--- | :--- |
| **Process ID** | `PKABC010342242022_1_1` | `"PKABC010342242022_1_1"` |  MATCH |
| **Process Title** | `Notice to show cause why execution should not issue [O. 21, R. 16]` | `"Notice to show cause why execution should not issue [O. 21, R. 16]"` |  MATCH |
| **Process Date** | `07-01-2023` | `"07-01-2023"` |  MATCH |

---

## 6. Case History Table Verification (All 32 Rows Audited)

| # | Business Date | Hearing Date | Purpose of Hearing | Judge Name | JSON Match |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | `06-12-2025` | `null` / `-` | `Disposed` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 2 | `25-11-2025` | `06-12-2025` | `ORDERS` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 3 | `23-09-2025` | `25-11-2025` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 4 | `12-08-2025` | `23-09-2025` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 5 | `24-06-2025` | `12-08-2025` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 6 | `22-04-2025` | `24-06-2025` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 7 | `12-03-2025` | `22-04-2025` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 8 | `29-01-2025` | `12-03-2025` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 9 | `18-12-2024` | `29-01-2025` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 10 | `13-11-2024` | `18-12-2024` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 11 | `25-09-2024` | `13-11-2024` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 12 | `14-08-2024` | `25-09-2024` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 13 | `08-08-2024` | `14-08-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 14 | `01-08-2024` | `08-08-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 15 | `26-07-2024` | `01-08-2024` | `SUMMONS` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 16 | `05-07-2024` | `26-07-2024` | `SUMMONS` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 17 | `28-06-2024` | `05-07-2024` | `SUMMONS` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 18 | `20-06-2024` | `28-06-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 19 | `30-05-2024` | `20-06-2024` | `SUMMONS` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 20 | `24-04-2024` | `30-05-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 21 | `06-04-2024` | `24-04-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 22 | `28-02-2024` | `06-04-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 23 | `09-02-2024` | `28-02-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 24 | `22-01-2024` | `09-02-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 25 | `20-12-2023` | `22-01-2024` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 26 | `18-11-2023` | `20-12-2023` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 27 | `30-09-2023` | `18-11-2023` | `HEARING` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 28 | `15-07-2023` | `30-09-2023` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 29 | `03-06-2023` | `15-07-2023` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 30 | `01-04-2023` | `03-06-2023` | `APPEARANCE OF PARTY` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 31 | `07-01-2023` | `01-04-2023` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |
| 32 | `02-01-2023` | `07-01-2023` | `NOTICE` | `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE` |  MATCH |

---

## 7. Daily Status Blocks Verification (Pages 2–12, 32 Blocks Total)

Every Daily Status block in `scrape.pdf` contains the exact header hierarchy:
- Establishment: `PRL. CITY CIVIL AND SESSIONS JUDGE`
- In the Court of: `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE`
- CNR Number: `KABC010342242022`
- Case Number: `EX/0000002/2023`
- Case Title: `KRISHNAMURTHY G versus SATHISH M`
- Signing Judge: `CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE`

Each block's dynamic fields match:
1. **06-12-2025** (Page 2): Business = *"An IA.No.III filed by the JDR is dismissed. The memo filed by the DHR is hereby allowed and E.P is closed as fully satisfied."*, Nature of Disposal = `DISMISSED`, Disposal Date = `06-12-2025`.  MATCH
2. **25-11-2025** (Page 2): Business = *"Case called out. Smt.R.K Advocate filed power for JDR. Adv for DHR present. Received report from court Ameen. As per the said report, vacant possession of the suit property hand over to DHR. In this regard he has drawn Mahazar, Possession receipt and returned the warrant to court. Adv for DHR filed memo stating that, decree holder taken the possession of suit property as per the court orders. Adv for JDR filed IA.No.III U/o 21 rule 58 of CPC. Heard both sides. For orders by 06.12.2025."*, Next Purpose = `ORDERS`, Next Hearing Date = `06-12-2025`.  MATCH
3. **23-09-2025** (Page 2): Business = *"Case called out. Adv for DHR filed IA.No.III and IV U/s 151 of CPC, seeking for police protection at the time of execution of warrant and break open the door lock. Heard. Perused the IA.III and IV and report submitted by court Ameen. A court Ameen has expressed his apprehension of disturb from the JDR while executing the warrant. Therefore he need police help. By considering all these aspects, it is necessary to provide police protection to court Ameen while executing the possession delivery warrant and also removing of lock. Accordingly both IA’s are allowed. The jurisdictional police is hereby directed to provide necessary protection to court Ameen while executing posession delivery warrant. A court Ameen is at liberty to break open the lock installed to suit property if it is locked. Office is directed to issue intimation to jurisdictional police to provide protection to court Ameen. Issue possession delivery warrant if PF paid returnable by 25.11.2025."*, Next Purpose = `NOTICE`, Next Hearing Date = `25-11-2025`.  MATCH
4. **12-08-2025** (Page 3): Business = *"Case called out. Reissue possession delivery warrant, PF paid returnable by 23.09.2025."*, Next Purpose = `NOTICE`, Next Hearing Date = `23-09-2025`.  MATCH
5. **24-06-2025** (Page 3): Business = *"Case called out. Reissue possession delivery warrant, PF paid returnable by 12.08.2025."*, Next Purpose = `NOTICE`, Next Hearing Date = `12-08-2025`.  MATCH
6. **22-04-2025** (Page 3): Business = *"Case called out. Reissue possession delivery warrant, PF already paid returnable by 24.06.2025."*, Next Purpose = `NOTICE`, Next Hearing Date = `24-06-2025`.  MATCH
7. **12-03-2025** (Page 4): Business = *"Call on by"*, Next Purpose = `NOTICE`, Next Hearing Date = `22-04-2025`.  MATCH
8. **29-01-2025** (Page 4): Business = *"Case called out. Resissue possession delivery warrant returnable by 12.03.2025."*, Next Purpose = `NOTICE`, Next Hearing Date = `12-03-2025`.  MATCH
9. **18-12-2024** (Page 5): Business = *"Case called out. Reissue possession delivery warrant returnable by 29.01.2025."*, Next Purpose = `NOTICE`, Next Hearing Date = `29-01-2025`.  MATCH
10. **13-11-2024** (Page 5): Business = *"Case called out. Reissue possession delivery warrant returnable by 18.12.2024."*, Next Purpose = `NOTICE`, Next Hearing Date = `18-12-2024`.  MATCH
11. **25-09-2024** (Page 5): Business = *"Case called out. Adv for DHR filed memo with xerox copy of sale deed and E.C. Issue possession delivery warrant, PF paid returnable by 13.11.2024."*, Next Purpose = `NOTICE`, Next Hearing Date = `13-11-2024`.  MATCH
12. **14-08-2024** (Page 6): Business = *"Case called out. Learned counsel for DHR filed memo with one document. Heard. Commissioner’s fee fixed at Rs.5000/-. Adv for DHR paid commissioner fee of Rs.5000/- in cash to court commissioner by name Sri.Chandan.K.L. Issue commission warrant for registration of the sale deed if draft sale deed correct. Call on by 25.09.2024."*, Next Purpose = `NOTICE`, Next Hearing Date = `25-09-2024`.  MATCH
13. **08-08-2024** (Page 6): Business = *"Case called out. Adv for DHR filed memo stating that, Sri.Chandan.K.L Advocate (KAR/1942/2015) may be appointed as court commissioner. Accordingly memo is allowed. Sri. Chandan.K.L is appointed as court commissioner. For clarification on draft. Call on by 14.08.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `14-08-2024`.  MATCH
14. **01-08-2024** (Page 6): Business = *"Case called out. Learned counsel for DHR filed IA.No.II U/o 26 rule 9 of CPC, seeking for appointment of court commissioner for the purpose perform ministerial act of this court. Heard. The learned counel for DHR urged that, in this case this court granted relief of specific performance of contract by passing judgment and decree in O.S.No.4555/2020 dated 02.07.2022. As per the said judgment and decree the JDR is requires to execute sale deed in favour of DHR petitioner within 3 months from the date judgment. The JDR fails to execute sale deed by receiving remaining balance sale consideration. Hence, prays for appointment of court commissioner for the purpose of execution of sale deed on behalf of JDR. I have perused the IA.No.I, petition and decree. In O.S.No.4555/2020 this court decreed the suit of the plaintiff and directed to defendant execute the sale deed by receiving sale consideration within 3 months from 02.07.2022. There is no record to show that, the judgement passed by this court is setaside or stayed by competant court of law. It is just and proper to appointment of court commissioner for performing minsterial act on behalf of this court. Hence, I proceed to pass the following:- ORDER IA.No.II filed U/o 26 rule 9 of CPC is hereby consider as filed U/o 26 rule 10-B of CPC and hereby allowed. One Advocate of Advocate’s Bar Bengaluru is appointed as court commissioner. The learned counsel for DHR filed memo with draft sale deed. Call on by 08.08.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `08-08-2024`.  MATCH
15. **26-07-2024** (Page 7): Business = *"DHR counsel present. Prays time. Hence, call on by 01.08.2024."*, Next Purpose = `SUMMONS`, Next Hearing Date = `01-08-2024`.  MATCH
16. **05-07-2024** (Page 7): Business = *"Case called out. Adv for DHR furnished amended petition and memo with draft sale deed. Office is directed to verify the draft sale deed. Call on by 26.07.2024."*, Next Purpose = `SUMMONS`, Next Hearing Date = `26-07-2024`.  MATCH
17. **28-06-2024** (Page 7): Business = *"Case called out. Adv for DHR filed IA.No.I U/o 6 rule 17 of CPC, seeking for amendment of name of the JDR. Heard. Perused the IA.No.I, Decree copy and petition copy, in decree copy name of the JDR mentioned as M.Sathish. By the time presenting petition name of the JDR is mentioned as M.Sahish. It is clerical mistake in cause title of the petition. Hence, IA.No.I is allowed and permitted to amend the petition. For amended petition by 05.07.2024."*, Next Purpose = `SUMMONS`, Next Hearing Date = `05-07-2024`.  MATCH
18. **20-06-2024** (Page 8): Business = *"Case called out. Adv for DHR prays time. Call on by 28.06.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `28-06-2024`.  MATCH
19. **30-05-2024** (Page 8): Business = *"office is directed to verify the draft sale deed and payment of balance by"*, Next Purpose = `SUMMONS`, Next Hearing Date = `20-06-2024`.  MATCH
20. **24-04-2024** (Page 8): Business = *"Case called out. Adv for DHR present. Prays time. Hence, call on by 30.05.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `30-05-2024`.  MATCH
21. **06-04-2024** (Page 9): Business = *"Case called out. Adv for DHR present. Filed memo with two documents. Heard. To hear further. Call on by 24.04.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `24-04-2024`.  MATCH
22. **28-02-2024** (Page 9): Business = *"Case called out. Adv for DHR prays time. Hence, call on by 06.04.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `06-04-2024`.  MATCH
23. **09-02-2024** (Page 9): Business = *"Case called out. Adv for DHR present. Prays time. Hence, call on by 28.02.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `28-02-2024`.  MATCH
24. **22-01-2024** (Page 10): Business = *"Case called out. Heard arguments from DHR. To hear further. Call on by 09.02.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `09-02-2024`.  MATCH
25. **20-12-2023** (Page 10): Business = *"Case called out. Adv for DHR filed memo and sought permission to withdraw the memo in draft sale deed dated 30.09.2023. In view of the memo filed by the adv for DHR, the memo and draft sale deed filed on 30.09.2023 is dismissed as withdrawn. Adv for DHR filed memo, along with the draft sale deed in two sets. Office to verify and put up. Call on by 22.01.2024."*, Next Purpose = `HEARING`, Next Hearing Date = `22-01-2024`.  MATCH
26. **18-11-2023** (Page 10): Business = *"Case called out. Adv for DHR present. Heard. To hear further. Call on by 20.12.2023."*, Next Purpose = `HEARING`, Next Hearing Date = `20-12-2023`.  MATCH
27. **30-09-2023** (Page 11): Business = *"Case called out. Adv for DHR filed memo with draft sale deed. To hear. Call on by 18.11.2023."*, Next Purpose = `HEARING`, Next Hearing Date = `18-11-2023`.  MATCH
28. **15-07-2023** (Page 11): Business = *"Case called out. DHR and adv for DHR absent. No representation. For steps. Cal on by 30.09.2023."*, Next Purpose = `NOTICE`, Next Hearing Date = `30-09-2023`.  MATCH
29. **03-06-2023** (Page 11): Business = *"Case called out. JDR called out absent. Adv for DHR present. For steps. Call on by 15.07.2023."*, Next Purpose = `NOTICE`, Next Hearing Date = `15-07-2023`.  MATCH
30. **01-04-2023** (Page 12): Business = *"Case called out. The C/N served on the son of JDR. The service of notice held sufficient. For appearance of JDR. Call on by 03.06.2023."*, Next Purpose = `APPEARANCE OF PARTY`, Next Hearing Date = `03-06-2023`.  MATCH
31. **07-01-2023** (Page 12): Business = *"Case called out. Heard adv for DHR. Issue notice to JDR keeping open the office objections. Call on by 01.04.2023."*, Next Purpose = `NOTICE`, Next Hearing Date = `01-04-2023`.  MATCH
32. **02-01-2023** (Page 12): Business = *"Case called out. For compliance of office objections by 07.01.2023."*, Next Purpose = `NOTICE`, Next Hearing Date = `07-01-2023`.  MATCH

---

## 8. Final Orders / Judgements Table Verification

| Field | Visual Reference (`scrape.pdf` Page 12) | JSON Value (`case.json`) | Status |
| :--- | :--- | :--- | :--- |
| **Order Number** | `1` | `"1"` |  MATCH |
| **Order Date** | `06-12-2025` | `"06-12-2025"` |  MATCH |
| **Order Details** | `Judgment` (link) | `"Judgment"` |  MATCH |
| **PDF URL** | `https://services.ecourts.gov.in/ecourtindia_v6/reports/0375644434591ea69eafc7102ca3935d.pdf` | `"https://services.ecourts.gov.in/ecourtindia_v6/reports/0375644434591ea69eafc7102ca3935d.pdf"` |  MATCH |
| **Onclick Payload** | `displayPdf(...)` | `"displayPdf('cl+sGJoSJ58oyVespa8VHg==','wd/evbCOK7tqvcKwXT25tA==','5rHUl/fJ8k9+dheUWTi6OQ==','8NJb071ifDPc/70jxdgMFg+I5ofoKfz4CQ0t934yFW9MCiB9AnJK6BKMDh4ZxKiO','');"` |  MATCH |

---

## 9. Documents and Transfers Verification

- **Documents**: No document rows are present in the PDF or web layout for `EX/2/2023`. Represented in `case.json` as `documents: []` with `number_of_document_rows: 0`.
- **Transfers**: No transfer records are present in the PDF or web layout for `EX/2/2023`. Represented in `case.json` as `transfers: []` with `number_of_transfer_rows: 0`.

---

## Conclusion & Audit Decision

The intermediate extraction candidate [case.json](file:///c:/Users/misha/OneDrive/Desktop/daksh/test_output/EX_2_2023/case.json) has been audited against [scrape.pdf](file:///c:/Users/misha/OneDrive/Desktop/daksh/scrape.pdf) across all 12 pages. Every visible field, table, record, and status block is accounted for without omissions or hallucinations. 

**EX/2/2023 has PASSED this completeness audit.**
