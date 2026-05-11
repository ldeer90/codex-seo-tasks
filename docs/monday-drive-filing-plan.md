# Monday → Drive Filing Audit
*Generated: 2026-05-09*

## Summary

Scanned all Monday.com boards and found **55 unique Google files** linked in item comments.
Cross-checked every file against known client Drive folders.

| Status | Count |
|---|---|
| ✅ Correctly filed (link matches a client folder) | 15 |
| ⚠️ Floating – not in any client folder | 36 |
| 🔴 No Drive folder exists for client | 3 |
| 👤 External owner (can't file ourselves) | 4 |

---

## Key Discovery: Two-Copy Problem

Every `.docx` and `.xlsx` file linked in Monday is **a different file ID** from what's been uploaded to Drive. Someone is sharing working originals via Monday comments, then separately uploading copies to the Drive client folders. This means:

- Monday links → originals (floating, no parent folder)
- Drive client folders → uploaded copies (different IDs, never linked from Monday)

**The Monday links are always out of sync with Drive.** The fix is to move workflows to create files *inside* the client folder from the start, then link from Monday — not the other way around.

---

## Files by Client

### Acorn Rentals

| File | Type | Status |
|---|---|---|
| Acorn Car Rental Initial Crawl | Sheet | ✅ 03 Audits |
| On page Sheet of acornrentals.com.au | Sheet | ✅ 03 Audits |
| Audit Report - acornrentals.docx | docx | ⚠️ Floating (copy in 03 Audits, different ID) |
| GSC Report - acornrentals.xlsx | xlsx | ⚠️ Floating (copy in 07 Reports, different ID) |
| Schema code - acornrentals.docx | docx | ⚠️ Floating |
| Content recommendations (March/April) | Doc | ⚠️ Floating (parentId unknown folder `10QndRDmSaE...`) |

**Action:** Move/copy Schema code and Content recommendations into `03 Audits`. GSC originals can be deleted once confirmed the Drive copy is current.

---

### AVENUE Hampers

| File | Type | Status |
|---|---|---|
| Duplicate H1 Tags | Sheet | ✅ 03 Audits |
| On page Sheet of avenuehampers.com.au | Sheet | ✅ 03 Audits |
| AVENUE Hampers (on-page sheet) | Sheet | ✅ 03 Audits |
| Audit Report - avenuehampers.docx | docx | ⚠️ Floating (copy likely in 03 Audits) |
| GSC Report - avenuehampers.xlsx | xlsx | ⚠️ Floating (copy in 07 Reports, different ID) |
| Schema code - avenuehampers.docx | docx | ⚠️ Floating |

**Action:** File Audit Report and Schema code into `03 Audits`.

---

### Joe Rascal Ducati

| File | Type | Status |
|---|---|---|
| Joe Rascal Ducati: Footer Suggestions | Sheet | ✅ 03 Audits |
| Audit Report - joerascalducati.docx | docx | ⚠️ Floating (copy in 07 Reports) |
| Schema code - joerascalducati.docx | docx | ⚠️ Floating (copy in 07 Reports) |

**Note:** 07 Reports has Suggestion Report and Schema Code but **no GSC report** filed yet.

**Action:** File originals in 03 Audits; upload GSC report to 07 Reports.

---

### Joe Rascal Harley

| File | Type | Status |
|---|---|---|
| Joe Rascal Harley: Footer Suggestions | Sheet | ✅ 03 Audits |
| Joe Rascal Harley - Collection | Sheet | ✅ 03 Audits |
| Schema code - joerascalharley.docx | docx | ⚠️ Floating (copy in 07 Reports) |
| Audit Report - joerascalharley.docx | docx | ⚠️ Floating — **owner: iteintegrated@gmail.com** 👤 |
| Keywords Research - joerascalharley.com.au | Sheet | ⚠️ Floating — **owner: iteintegrated@gmail.com** 👤 |
| Suggestion Report - joerascalharley.docx | docx | ⚠️ Floating — **owner: shalu.seodiscovery@gmail.com** 👤 |

**Action:** For external-owned files, request Laurence transfers ownership or re-creates under `seo@agents.digital`. Internal files → file in 03 Audits.

---

### Joe Rascal Global (joerascal.com)

🔴 **No Drive folder exists for this client.**

| File | Type | Status |
|---|---|---|
| Keywords Research - joerascal.com | Sheet | 🔴 No folder |
| Suggestion Meta Tags: Joerascal | Doc | 🔴 No folder |
| Suggested Meta tags and H1 | Doc | 🔴 No folder (sharedWithMe) |

**Action:** Create Drive folder for Joerascal.com. Move/copy these 3 files into it.

---

### Little Shop of Happiness

| File | Type | Status |
|---|---|---|
| On page Sheet of littleshopofhappiness.com.au (v1) | Sheet | ✅ 03 Audits |
| On page Sheet of littleshopofhappiness.com.au (v2) | Sheet | ✅ 03 Audits |
| Audit Report - littleshopofhappiness.docx | docx | ⚠️ Floating (copy likely in 03 Audits) |
| GSC Report - littleshopofhappiness.xlsx | xlsx | ⚠️ Floating (copy in 07 Reports, different ID) |
| Schema code - littleshopofhappiness.docx | docx | ⚠️ Floating |

**Note:** Two "On page Sheet" versions exist in 03 Audits — likely an older and newer version. Should confirm which is current and delete/archive the other.

**Action:** File Audit Report and Schema code in 03 Audits.

---

### Melani the Label

| File | Type | Status |
|---|---|---|
| On-page Status Report: Melani the Label | Sheet | ✅ 03 Audits |
| Detailed Audit Report - melanithelabel.docx (May 8) | docx | ✅ 03 Audits |
| Detailed Audit Report - melanithelabel.docx (May 1) | docx | ✅ 03 Audits (older version) |
| Keywords Research - melanithelabel.com | Sheet | ⚠️ Floating |

**Note:** 03 Audits confirmed populated via Drive MCP (previous session scan was incorrect). 07 Reports is empty — no GSC report or monthly SEO report filed yet. Two audit report versions in 03 Audits — May 8 is current, May 1 can be archived.

**Action:** File Keywords Research sheet into 03 Audits. Archive the May 1 audit report. Create `SEO Reports` subfolder in 07 Reports and file first monthly report when generated.

---

### Salad Servers

| File | Type | Status |
|---|---|---|
| Salad Servers - Screaming Frog Crawl | Sheet | ✅ 03 Audits |
| On page Sheet of saladservers.com.au | Sheet | ✅ 03 Audits |
| Audit Report - saladservers.docx | docx | ⚠️ Floating |
| GSC Report - saladservers.xlsx | xlsx | ⚠️ Floating (copy in 07 Reports, different ID) |
| Schema code - saladservers.docx | docx | ⚠️ Floating |

**Action:** File Audit Report and Schema code in 03 Audits.

---

### Shop Rongrong

| File | Type | Status |
|---|---|---|
| On page Sheet of shoprongrong.com | Sheet | ✅ 03 Audits |
| Client Bench Marking: Shop Rongrong | Sheet | ✅ 03 Audits |
| Audit Report - shoprongrong.docx | docx | ⚠️ Floating (copy likely in 03 Audits) |
| GSC Report - shoprongrong.xlsx | xlsx | ⚠️ Floating (copy in 07 Reports, different ID) |
| Schema code - shoprongrong.docx | docx | ⚠️ Floating |
| Website Suggestion Report: Shoprongrong | Doc | ⚠️ Floating |
| Collection Pages: Shoprongrong | Sheet | ⚠️ Floating |

**Action:** File Audit Report, Schema code, Website Suggestion Report, and Collection Pages in 03 Audits.

---

### TravelKon

| File | Type | Status |
|---|---|---|
| On page Sheet of travelkon.com.au | Sheet | ✅ 03 Audits |
| Audit Report - travelkon.docx | docx | ⚠️ Floating |
| GSC Report - travelkon.xlsx | xlsx | ⚠️ Floating (copy in 07 Reports, different ID) |
| Schema code - travelkon.docx | docx | ⚠️ Floating |

**Action:** File Audit Report and Schema code in 03 Audits.

---

## Cross-Client / Orphan Files

| File | Issue |
|---|---|
| **Keywords Research** (Sheet `1Le51GPh...`) | Used for 5 clients: Shoprongrong, Salad Servers, TravelKon, Acorn, Little Shop of Happiness. Needs to be split into per-client copies and filed in each client's folder. |
| **Analysis of April Month Reports** (Doc) | No parentId — unclear which client this belongs to. Review and file or delete. |
| **Blogs to Unpublish** (Sheet) | No parentId — unclear which client. Review and file or delete. |
| **Client Benchmarking Template** (Sheet) | Filed in a templates area (`1ZpzgOmzDHmb...`), not a client folder. This is probably intentional — confirm it's being used as a reusable template. |

---

## Priority Action List

| Priority | Action |
|---|---|
| 🔴 1 | Create Drive folder for **Joerascal.com** and move/copy 3 floating files |
| 🔴 2 | File all **Melani the Label** files — nothing is filed yet |
| 🟡 3 | Split the **multi-client Keywords Research sheet** into 5 per-client copies |
| 🟡 4 | Resolve **external-owned files** for Joe Rascal Harley (request ownership transfer) |
| 🟢 5 | File all remaining floating **docx/Schema/Suggestion** files in `03 Audits` per client |
| 🟢 6 | Create `SEO Reports` and `Benchmarks` subfolders inside `07 Reports` for all 9 clients |
| 🟢 7 | Establish workflow: create files *inside* client Drive folders, then link from Monday — stops the two-copy problem |

---

## 07 Reports Folder Status

| Client | Contents |
|---|---|
| Acorn Rentals | 1 GSC Report (copy) |
| AVENUE Hampers | 1 GSC Report (copy) |
| Joe Rascal Ducati | Suggestion Report + Schema code (no GSC report) |
| Joe Rascal Harley | Suggestion Report + Schema code (no GSC report) |
| Little Shop of Happiness | 1 GSC Report (copy) |
| Melani the Label | **Empty** |
| Salad Servers | 1 GSC Report (copy) |
| Shop Rongrong | 1 GSC Report (copy) |
| TravelKon | 1 GSC Report (copy) |

All GSC reports in 07 Reports are **uploaded copies** — different file IDs from the originals shared in Monday. No `SEO Reports` or `Benchmarks` subfolders have been created yet for any client.
