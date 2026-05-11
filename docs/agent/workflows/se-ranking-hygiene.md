# SE Ranking Hygiene

Review and clean up SE Ranking projects across all clients. Run before any keyword-addition work to avoid hitting the plan cap, or when the plan cap blocks an add.

## When to run

- Before adding keywords to any project
- When the plan cap error appears (`available limit of adding is 1`)
- Monthly health check

## Plan model

- `keyword_count` from `PROJECT_listProjects` reflects the **count of keyword-engine pairs**, not unique keywords. A keyword tracked on AU + US = 2 pairs.
- Plan cap: **2,000 pairs**. The error `available limit of adding is N` means N pairs free; deleting a tracked pair frees 1.
- Most clients are AU-only (1 engine per keyword). Melani is AU + US (2 engines per keyword).

## Step 1 — Project-level audit

```
PROJECT_listProjects()
```

For each project, note `id`, `title`, `keyword_count`, and flag duplicate domains. Sum across all projects to get current pair usage.

## Step 2 — Identify duplicates (project-level)

Flag any domain that has 2+ project entries. Known duplicates as of 2026-05-09 (deleted):

| Domain | Primary ID | Duplicate ID (deleted) |
|---|---|---|
| shoprongrong.com | `11560829` | `11619515` ✓ |
| avenuehampers.com.au | `11562866` | `11621399` ✓ |
| littleshopofhappiness.com.au | `11562890` | `11660195` ✓ |

Always confirm with the user before deleting a project.
```
PROJECT_deleteProject(site_id=<duplicate_id>)
```

## Step 3 — Keyword-level audit (when slots are tight)

Use this when the plan cap is hit. Target the projects with the highest `keyword_count` first — they have the most low-quality keywords to harvest.

### 3a. Pull keyword list

```
PROJECT_listKeywords(site_id=<project_id>)
```

Save the response `data` array to `/tmp/<client>-keywords.json`. Large lists may exceed token limits — they auto-persist; read from the persisted file.

### 3b. Pull volumes (parallel batches of 10)

For each batch of 10 keywords, call `PROJECT_getSearchVolume(region_id=10, keywords=[...])`. Run all batches **in parallel** (single message, multiple tool calls) — 50 keyword batches return in ~3 seconds. SE Ranking silently omits 0-volume keywords from the response → treat any keyword not in the response as `vol = 0`.

Save all responses merged as `/tmp/<client>-volumes.json` ({keyword: int}).

### 3c. Run audit script

```bash
python scripts/audit_se_ranking_project.py \
    --keywords-json /tmp/<client>-keywords.json \
    --volumes-json /tmp/<client>-volumes.json \
    --brand-terms '<brand>,<alt brand>' \
    --min-volume 50 \
    --output /tmp/<client>-audit.json
```

Logic the script applies:
- **Drop:** any keyword with 0 search volume (no demand)
- **Drop:** any keyword with volume `< min-volume` (default 50; tune up if cleanup needs to be more aggressive)
- **Drop:** exact duplicates (case/punctuation variants — keeps the lowercase first one)
- **Protect:** any keyword containing a brand term (passed via `--brand-terms`). Brand searches don't always register volume but are worth tracking.

Output structure:
```json
{
  "summary": {"total":..., "to_delete":..., "retained_after_cleanup":..., ...},
  "delete_ids": [int, ...],
  "delete_with_reason": [{"id","name","vol"}, ...],
  "kept": [...],
  "brand_protected": [...]
}
```

### 3d. Review and confirm

Always show the user before deleting:
- Total / delete / retain counts
- Top 10 highest-volume keywords being **kept** (sanity check)
- 10–20 sample 0-volume keywords being **deleted**
- Brand-protected list

Wait for explicit approval.

### 3e. Delete in batches of 50

```
PROJECT_deleteKeywords(site_id=<project_id>, keywords_ids=[...up to 50...])
```

Run all delete batches in parallel.

## Real example — Avenue Hampers (2026-05-10)

Plan cap was hit at 1,999/2,000 pairs while adding Melani's 65 new keywords (130 pairs needed).

Audit of Avenue Hampers (Project `11562866`, 365 keywords AU-only):

| Bucket | Count |
|---|---|
| Total | 365 |
| Zero volume | 146 |
| <50 volume | 51 |
| 50+ volume | 168 |
| Duplicates | 2 |
| Brand-protected (`avenue hampers`) | 1 |
| **Deleted** | **198** |
| Retained | 167 |

Slots freed: 198 → enough for Melani's 130 new pairs + 68 buffer.

## Step 4 — Per-project low-volume threshold notes

Most projects can run at `--min-volume 50`. Tune higher (`100`, `200`) only if more cleanup is needed:
- Local-service clients (e.g. Avenue Hampers, hampers/gifts in named cities) — many ultra-niche city+occasion combos return 0; threshold of 50 is right.
- E-commerce category clients (Melani, Shop Rongrong) — long-tail product variants often return real but low volume; threshold of 50 may be too aggressive. Inspect manually.

## Step 5 — Check search engines per project

Each project should have both AU and US engines if the client has international intent.

```
PROJECT_getSearchEngines(site_id=<project_id>)
```

After adding an engine, note the returned `site_engine_id` — this is what `PROJECT_addKeywords` needs, NOT the region_id. Cache engine IDs in `docs/agent/clients/<client>.json` under `se_ranking.engines` so future workflows skip this lookup.

## Reference — all client SE Ranking project IDs

| Client | Project ID | Keywords | Notes |
|---|---|---|---|
| Shop Rongrong | `11560829` | 519 | Audit candidate (next pass) |
| Joe Rascal Harley | `10993304` | 302 | Many near-duplicate brand variants — audit candidate |
| Little Shop of Happiness | `11562890` | 228 | |
| Salad Servers Direct | `11273891` | 198 | |
| Avenue Hampers | `11562866` | **167** | ✓ Audited 2026-05-10 (was 365, dropped 198 zero/low-vol) |
| Melani the Label | `12019802` | 139 | AU + US engines = 278 pairs |
| TravelKon | `11580098` | 113 | |
| Ducati Melbourne | `10993280` | 100 | Titled "joerascalducati.com.au" |
| Acorn Rentals | `11444792` | 26 | |

Last verified: 2026-05-10. Total pair usage after Avenue cleanup + Melani add ≈ 1,931 / 2,000.
