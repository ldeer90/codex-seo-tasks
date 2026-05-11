# Collection SEO — Full Pipeline (one-shot)

Runs keyword research → competitor SERP → metadata suggestions → Sheet → Monday in a single session, driven by `client.json`.

**Use when:** the user asks "do collection SEO for X" or "generate title suggestions for all collections."
**Skip ahead** to specific phases when only part of the flow needs to run.

---

## Phase 0 — Load sidecar

Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.

```bash
cat docs/agent/clients/<client>.json
cat docs/agent/clients/<client>-timeline.md
```

Confirm: domain, market scope, SE Ranking project + engine IDs, Drive `03_audits` folder ID, Monday board ID, USP, freshness of cached deliverables.

If `client.json` doesn't exist: stop. Bootstrap it first by running discovery (Phase 1) and copying the schema from `melani-the-label.json`.

### Missing-input routing

Route missing client setup, Drive folder, Monday board, or SE Ranking project to `ld-seo-client-onboarding`; access, capacity, duplicate-project, or filing blockers to `ld-seo-maintenance`; stale sidecar or live keyword mismatches to `collection-seo-qa`; content brief requests to `ld-seo-content-briefs`.

## Quality Gate — required before and after live writes

Before adding SE Ranking keywords or creating Drive deliverables:
1. Export live project keywords with `PROJECT_listKeywords(site_id=<project_id>)` and save the raw response to `/tmp/<client>-keywords.json`.
2. Run `scripts/validate_collection_seo_state.py` with the sidecar, keyword export, current page cache, and SERP cache.
3. Stop on validator blockers. Warnings may proceed only if they are called out in the proof block.

After any SE Ranking write:
1. Re-export `PROJECT_listKeywords`.
2. Run `scripts/sync_collection_sidecar_from_exports.py` with AU/US volume exports and current-page cache.
3. Re-run the validator. Deliverables require zero blockers.

---

## Phase 1 — Discovery + classification

```bash
python scripts/discover_collections.py --domain <domain> --output /tmp/<client>-collections.json
```

Merge into `client.json.collections[]`. Show the user:
- `pure_category` count (auto-include)
- `themed_category` count (auto-include)
- `curated_edit` slugs (ask: keep or drop?)
- `style_edit` / `empty` (auto-drop)

Persist user decisions on the curated bucket so subsequent runs skip the prompt.

**Cost:** 0 Firecrawl, 0 SE Ranking.

---

## Phase 2 — Scrape client pages once

```python
from seo_automation_mcp.firecrawl import FirecrawlClient
import asyncio, json, re

cj = json.loads(open('docs/agent/clients/<client>.json').read())
urls = [c['url'] for c in cj['collections'] if c['class'] in ('pure_category','themed_category')]

client = FirecrawlClient()
pages = asyncio.run(client.scrape_urls(urls=urls))

current = {}
for i, page in enumerate(pages):
    slug = urls[i].split('/collections/')[-1]
    inner = page.get('data', {}); meta = inner.get('metadata', {})
    h1s = re.findall(r'^#\s+(.+)$', inner.get('markdown',''), re.MULTILINE)
    current[slug] = {
        'title': meta.get('title','').strip(),
        'h1': h1s[0] if h1s else '',
        'meta_description': meta.get('description','').strip(),
    }
json.dump(current, open(f'/tmp/{client_slug}-current-pages.json','w'))
```

**Cost:** 1 credit per collection. ~22 credits for Melani.

---

## Phase 3 — SE Ranking volumes (parallel)

For every collection's primary keyword, fetch volume. Skip if `client.json.collections[*].au_volume` already populated and < 30 days old.

**Run all batches in parallel** (single message, multiple `PROJECT_getSearchVolume` calls). Up to 10 keywords per call.

Write results back to `client.json.collections[*].au_volume` (and `us_volume` for AU+US clients).

---

## Phase 4 — SERP + competitor scrape (cached)

If `client.json.deliverables.competitor_serp_json.updated` is < 30 days old AND every collection has `competitor_top3_urls` populated → **skip**, reuse cached data.

Otherwise:
1. `DATA_getSerpResults` for every primary keyword (one call per keyword, all in parallel).
2. Pick top 3 organic URLs per keyword (skip marketplaces, social, the client's own site).
3. Firecrawl `scrape_urls` for all top-3 URLs across all collections in one batch.
4. Save to `docs/<client>-serp-scrape-<date>.json`.
5. Update `client.json.collections[*].competitor_top3_urls` and `deliverables.competitor_serp_json`.

**Cost:** ~12 SE Ranking SERP calls + ~30 Firecrawl credits (when run; 0 on cache hit).

---

## Phase 5 — Generate suggestions

```bash
python scripts/build_metadata_suggestions.py \
    --client-json docs/agent/clients/<client>.json \
    --serp-json docs/<client>-serp-scrape-<date>.json \
    --pages-json /tmp/<client>-current-pages.json \
    --output /tmp/<client>-metadata-suggestions.csv
```

The generator fails if more than 10% of included collections are missing volume or current-page data. Use `--allow-incomplete` only for diagnostic drafts. Spot-check the CSV for awkward suggestions (e.g. duplicated descriptors, weird pluralisations).

---

## Phase 6 — Upload Sheet

```python
from seo_automation_mcp.google_clients import GoogleWorkspaceClient
import csv, json

cj = json.loads(open('docs/agent/clients/<client>.json').read())
rows = list(csv.reader(open('/tmp/<client>-metadata-suggestions.csv')))

g = GoogleWorkspaceClient(delegated_subject='hello@agents.digital')
result = g.create_sheet(
    title=f"{cj['client']} — On-Page Title & H1 Suggestions",
    values=rows,
    folder_id=cj['drive']['folders']['03_audits'],
)
print(result['url'])
```

Update `client.json.deliverables.metadata_suggestions_sheet`.

## Phase 6b — Keyword research Doc

For full keyword research handoff, render a deterministic Doc body:

```bash
python scripts/render_keyword_research_doc.py \
    --client-json docs/agent/clients/<client>.json \
    --seranking-keywords-json /tmp/<client>-keywords.json \
    --output /tmp/<client>-keyword-research-doc.txt
```

Create a new Doc with `GoogleWorkspaceClient.create_doc(..., folder_id=...)`, or overwrite an existing Doc with `GoogleWorkspaceClient.overwrite_doc_text(document_id, text)`.

---

## Phase 7 — Monday task

1. `get_board_info(boardId=<board_id>)` — find current month group from `client.json.monday.groups.current_month`.
2. `create_item` named `"On-Page Suggestions — Title Tags & H1s"` with status `Done` and today's date.
3. `create_update` with: Sheet link, status counts (`New`/`Tweak`/`OK`/`Missing H1`), top 3 highest-priority rewrites by AU volume, competitors referenced.

## Final proof block

End every successful run with:
- Live SE Ranking keyword count and keyword-engine pair count
- Collections covered vs included collections
- Sheet rows and/or Doc sections produced
- Drive folder ID used
- Validator warnings remaining, or "none"
- Client timeline updated with proof summary and next action

---

## Cache hit re-run

A second pass within 30 days (e.g. user reviewed the Sheet, asked to regenerate) skips Phases 1, 3, 4 entirely. Only Phases 2 (re-scrape client pages, optional), 5, 6, 7 fire. Wall time: < 60s.

---

## Common failures

- **`client.json` missing for this client** — bootstrap manually from `melani-the-label.json` schema, then re-run from Phase 1.
- **Discovery surfaces unfamiliar slug pattern** — add to `DROP_PATTERNS` in `scripts/discover_collections.py`.
- **`create_sheet` "User cannot add children"** — service account lacks Editor on the target folder. Check `docs/client-folder-map.json` and grant via Drive UI.
- **Suggestion generator produces awkward H1** — extend `SLUG_TO_KEYWORD` or `singular_to_plural` in `scripts/build_metadata_suggestions.py`.
