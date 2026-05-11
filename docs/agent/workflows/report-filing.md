# Report Filing Convention

Generated 2026-05-08. Update this file whenever the Drive folder structure changes or a new report type is added.

---

## Canonical client folder structure

Derived from `_ CLIENT TEMPLATE` (`1NSxmr_AUHoweWrFfKotEvBiJ88zdwOPZ`). Every active client folder should contain these subfolders:

```
00 Proposals
01 Onboarding
02 Roadmap
03 Audits
04 Keyword Research
05 Content
06 Links
07 Reports/
    SEO Reports/     ← automated monthly reports land here
    Benchmarks/      ← baseline benchmarks, ranking snapshots
08 Invoices
```

`SEO Reports` and `Benchmarks` are **subfolders inside `07 Reports`**. They are not in the original template and must be created manually in Drive for each client (see gap registry below). Once created, paste the new folder IDs into the relevant `docs/agent/clients/<slug>.md` brief.

---

## Report type → folder mapping

### Decision criteria

| Question | Answer |
|---|---|
| Is it an ongoing periodic deliverable for the client? | → `07 Reports / SEO Reports` |
| Is it a one-off or periodic technical audit? | → `03 Audits` |
| Is it a ranking or traffic baseline snapshot? | → `07 Reports / Benchmarks` |

### Filing targets per tool

| Tool | Target folder | Rationale |
|---|---|---|
| `create_combined_seo_report` | `07 Reports / SEO Reports` | Monthly client deliverable — GA4 + Firecrawl narrative Doc + data Sheet |
| `scripts/run_screaming_frog_audit.py --upload-to-drive` | `03 Audits` | Technical crawl dataset and analysis summary from Screaming Frog |
| `create_firecrawl_seo_audit_doc` | `03 Audits` | Technical audit document, typically one-off or pre-engagement |
| `create_site_audit_sheet` | `03 Audits` | Technical audit spreadsheet, same cadence as above |

The Doc and Sheet from `create_combined_seo_report` always land together in the same folder — both go to `07 Reports / SEO Reports`.

### Filename convention

File date is already embedded by `dated_title()` (e.g. `Shop Rongrong SEO Report — 2026-05`). No year or month subfolder is needed inside `SEO Reports` — the flat layout with dated filenames is sufficient.

---

## Creating missing subfolders (retroactive, manual)

All existing client folders are missing `SEO Reports` and `Benchmarks` inside `07 Reports`. Apply the template retroactively by creating both subfolders in Drive for each client.

**Steps for each client:**

1. Open the client's `07 Reports` folder in Drive (use the ID from the brief).
2. Create a new folder named `SEO Reports` inside it.
3. Create a new folder named `Benchmarks` inside it.
4. Copy the new folder IDs from the Drive URL (`folders/<id>`).
5. Update the `## Drive subfolders` table in the client brief with the new IDs.
6. Update the `client_report_folder_ids` map in `src/seo_automation_mcp/client_config.py` (once that module is created — see code change scope below).

**Priority order** (clients with active monthly reports first):

1. Shop Rongrong
2. AVENUE Hampers
3. Joe Rascal Harley
4. Acorn Rentals
5. Little Shop of Happiness
6. Salad Servers Direct
7. TravelKon
8. Melani the Label
9. Joe Rascal Ducati / Ducati Melbourne
10. Joe Rascal Global (pending parent folder fix — see gap registry)

---

## Per-client filing targets

Scanned 2026-05-08. `SEO Reports` and `Benchmarks` IDs are pending creation.

| Client | 03 Audits ID | 07 Reports ID | SEO Reports ID | Benchmarks ID |
|---|---|---|---|---|
| Acorn Rentals | `1ZGPxHEygUPhes-0twOuoTkDBygIW-tAs` | `1gupoXp_cjGHm3ixSEIs3PFpKTb2ataJ2` | pending | pending |
| AVENUE Hampers | `1zmOww76CYrUhQOB_wcQvUKUbcFsFzYmF` | `1VzFY_bDRX9jDNCeGzC53m5uKYsvOkacG` | pending | pending |
| Joe Rascal Ducati | `1zqzxqVT2aeJ1aahoGW3EM0qEoqomnB5x` | `1dzj65zJm15qNxV0AK0VyefNsr1prGkd2` | pending | pending |
| Joe Rascal Harley | `1zea_22Ldi8q7QU0qkBs53HxZXwA68AIJ` | `1Vutz3IWesdKE21e4mw10P8V9Yw_cE6bD` | pending | pending |
| Little Shop of Happiness | `1MFU9-6X1uJys3IyIod7KFziJz40K5J8C` | `1D6IKdB56uC3uvgT9fOccT28Rl4zPo-qs` | pending | pending |
| Melani the Label | `1j_tdnIT0mia1rJz0P2DU4zcs19jpQzS6` | `1Gfvxg4DuAzv_W5bGBJ62r09ap0woX6Eu` | pending | pending |
| Salad Servers | `1JIyzafg5Q49ExzvJMqCR-Bsu1Hm16N9o` | `1RrX29zwEAiEv-SJFiqfSfkZAqJuKa6Sp` | pending | pending |
| Shop Rongrong | `1ywpJIkNJddGRLdaGTiAnyDksoxP85pWD` | `1K66iztEtBye5mCowq-chwTkMr0E1uati` | pending | pending |
| TravelKon | `1aEbqpVIWbkaz8dkMZGKa14v6b5iJn_Jb` | `1HCuM9DP0xZ9sjms8Y6C1AZhgWap_A5pr` | pending | pending |

Update `pending` to the actual folder ID after creating each subfolder.

---

## Gap registry

Clients with structural problems that need manual attention before filing can proceed.

### Joe Rascal (parent folder) — ID confirmed, rescan needed

- Folder ID confirmed correct (`14gHf6UZjgZ751CUP6iLz3Sf6WTTQBWSN`) from Drive URL on 2026-05-08.
- Previous scan failure was a typo (lowercase `n` vs uppercase `N`) in `CLIENT_FOLDERS` — now fixed.
- **Action:** Re-run `scan-client-folders` to populate Joe Rascal's subfolder data.

### Joe Rascal Global — no dedicated Drive folder

- No Drive folder exists. Reports currently filed under Joe Rascal Harley or the staging fallback.
- **Action:** Create a `Joe Rascal Global` subfolder inside the Joe Rascal parent (once the parent ID is fixed). Once created, update `docs/agent/clients/joe-rascal-global.md`.

### All clients — SEO Reports and Benchmarks subfolders missing

Every active client is missing `07 Reports / SEO Reports` and `07 Reports / Benchmarks`. See "Creating missing subfolders" above.

### New Client Forms — no filing targets

`New Client Forms` (`1eFoEqwgMyuWyMbQuOZZAzK4xtfQTB7Ao`) is an admin intake folder, not a client. No report filing targets apply.

---

## GOOGLE_DRIVE_REPORTS_FOLDER_ID

Until per-client filing code is wired up, this env var is the global fallback. All `create_*` calls land here if the client's `SEO Reports` subfolder ID is not resolved in code.

**Current recommendation:** create a folder named `_Reports (staging)` directly inside `Agents Digital / Clients` (`11AdlM1m9kpa3qtJr5RKIyYNUQWUseqb4`). This keeps staging output isolated from any individual client's tree.

Steps:
1. In Drive, open `Agents Digital / Clients`.
2. Create a new folder: `_Reports (staging)`.
3. Copy the folder ID from the URL.
4. Set `GOOGLE_DRIVE_REPORTS_FOLDER_ID=<new_id>` in `.env`.

**Never use a client-specific folder** (e.g. a client's `07 Reports`) as the global fallback — reports for all other clients would appear inside that client's tree.

---

## Code change scope (per-client filing)

When ready to wire up per-client filing in code, the minimal change is:

1. Add `src/seo_automation_mcp/client_config.py` with a `CLIENT_REPORT_FOLDER_IDS` dict keyed by lowercase client name, value = `SEO Reports` subfolder ID.
2. In each `create_*` workflow in `workflows.py`, resolve `report_folder_id` from `CLIENT_REPORT_FOLDER_IDS` with `GOOGLE_DRIVE_REPORTS_FOLDER_ID` as fallback.
3. Replace the `_move_to_reports_folder` call with `_move_to_folder(file_id, report_folder_id)` in `google_clients.py`.

Full diff must be shown to the user and approved before any code is saved. See handover doc `docs/handoffs/2026-05-08-drive-folder-mapping.md` for the complete code sketch.
