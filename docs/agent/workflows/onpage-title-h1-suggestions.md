# On-Page Title Tag & H1 Suggestions — Collection Pages

Uses SERP scrape data (from `competitor-keyword-research.md`) plus the client's own keyword research to write suggested title tags, H1s, and meta descriptions for each collection page. Output is a Google Sheet ready for client handoff.

**Run after:** `competitor-keyword-research.md` (needs SERP scrape JSON).

---

## Phase 0 - Access And Input Preflight

Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.

1. **Read `docs/agent/clients/<client>.json`** — provides domain, brand name (exact casing for suffix), market scope, Drive folder IDs, Monday board, USP, and `collections[]` with cached competitor URLs and current-page state.
2. SERP scrape JSON path is at `client.json.deliverables.competitor_serp_json.path`. If missing or > 30 days old, run `competitor-keyword-research.md` first.

### Missing-input routing

Route missing client setup to `ld-seo-client-onboarding`, access/Drive/Monday/SE Ranking blockers to `ld-seo-maintenance`, stale sidecar or missing live keyword/page/SERP data to `ld-seo-collection-seo` plus `collection-seo-qa`, and client-facing Sheet/Doc creation to Google Drive skills after validation.

## Quality Gate

Before generating or uploading suggestions:
1. Export live keywords to `/tmp/<client>-keywords.json`.
2. Run `scripts/validate_collection_seo_state.py` with sidecar, keyword export, current pages, and SERP JSON.
3. Stop on blockers. The metadata generator also fails if more than 10% of included collections are missing volume or current title/H1.

---

## Phase 1 — Scrape Client's Current On-Page Data

Scrape all collection pages to get the current title tag, H1, and meta description.

```python
result = await client.scrape_urls(urls=[
    "https://<site>/collections/maxis",
    "https://<site>/collections/gowns",
    # all target collection URLs
])

for page in result:
    inner = page.get('data', {})
    meta = inner.get('metadata', {})
    content = inner.get('markdown', '')
    title = meta.get('title', '').strip()
    description = meta.get('description', '').strip()
    h1s = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
```

If the collection crawl JSON from the keyword research workflow is recent (< 2 weeks), read from that instead to save credits.

**Credit cost:** 1 per collection page. Skip if recent crawl data exists.

---

## Phase 2 — Generate Suggestions (templated)

Run the suggestion generator. It composes title tag, H1, meta description and assigns a status per collection. Structured SERP patterns and competitor titles are used as conservative inputs: sidecar descriptors win first, then structured SERP descriptors/patterns, then repeated competitor-title modifiers. If the SERP does not expose a clean pattern, the generator leaves the title simple rather than inventing one.

```bash
python scripts/build_metadata_suggestions.py \
    --client-json docs/agent/clients/<client>.json \
    --serp-json docs/<client>-serp-scrape-<date>.json \
    --pages-json /tmp/<client>-current-pages.json \
    --output /tmp/<client>-metadata-suggestions.csv
```

Output columns: `Collection | URL | Primary Keyword | AU Volume | US Volume | Current Title | Suggested Title | Current H1 | Suggested H1 | Suggested Meta Description | Status | Competitor Patterns (Top 3 Titles) | SERP Considerations`

**Status assignment is deterministic:**
| Status | Trigger |
|---|---|
| `Missing H1` | No H1 detected |
| `New` | Primary keyword absent from current title |
| `Tweak` | Keyword present but separator wrong (`–` vs `|`), brand misformatted, or > 60 chars |
| `OK` | Keyword present + correct separator + brand + < 60 chars |

**Spot-check before upload:** scan the CSV for awkward suggestions (e.g. "skirt skirts", duplicated descriptors). Use Codex judgement to fix rows that a client, SEO specialist, or merchandiser would reasonably question.

## Client-Presentable QA

Before creating or overwriting a Sheet:

- Confirm every included row has a real primary keyword, current title/H1 state, and volume data unless explicitly strategic.
- Check titles are natural, under the target length, and use the brand casing from the sidecar.
- Check H1s match page/category intent and do not create cannibalisation with sibling collections.
- Check meta descriptions read like human ecommerce copy, not keyword stuffing.
- Check competitor patterns and SERP considerations were actually reviewed. Codex should adjust rows where the SERP clearly implies a better formula, modifier, or intent angle than the deterministic suggestion.

---

## Phase 4 — Create Google Sheet

**Sheet structure:**

| Collection | URL | Current Title | Suggested Title | Current H1 | Suggested H1 | Suggested Meta Description | Primary Keyword | AU Volume | Status | Competitor Patterns (top 3 titles) | SERP Considerations |
|---|---|---|---|---|---|---|---|---|---|---|---|

The last column (`Competitor Patterns`) gives the client context for why the suggestion is written the way it is — paste the top 3 competitor title tags from the SERP scrape.

**Create and file (one-call, service account):**

```python
from seo_automation_mcp.google_clients import GoogleWorkspaceClient
import csv, json

with open('/tmp/<client>-metadata-suggestions.csv') as f:
    rows = list(csv.reader(f))

cj = json.loads(open('docs/agent/clients/<client>.json').read())
client = GoogleWorkspaceClient(delegated_subject='hello@agents.digital')
result = client.create_sheet(
    title=f"{cj['client']} — On-Page Title & H1 Suggestions",
    values=rows,
    folder_id=cj['drive']['folders']['03_audits'],
)
sheet_url = result['url']
```

After creation, write the sheet ID + URL back to `client.json.deliverables.metadata_suggestions_sheet`.
Read the Sheet back, confirm headers and row count, then re-run the validator and include a proof block in the final response: live keyword count, live pair count, collections covered, Sheet rows, Drive folder, Monday task, validator blockers, remaining warnings, and client timeline update status.

---

## Phase 5 — Monday Task

1. `get_board_info(boardId=<board_id>)` — find current month group
2. Create item: `"On-Page Suggestions — Title Tags & H1s"`
3. Add update comment with:
   - Sheet link
   - Pages covered and how many need changes (`New` count)
   - Top 2–3 highest-priority rewrites (worst current title vs suggested, with AU volume)
   - Note which competitors were used as reference

---

## Suggested sequencing across all three workflows

```
keyword-research-collections.md
        ↓
competitor-keyword-research.md   ← Google top results for each primary keyword, scrape title/H1/copy
        ↓
onpage-title-h1-suggestions.md  ← Use SERP patterns + client keywords to write suggestions
```

All three can be run in a single session. Total Firecrawl credit cost for all three (12 collections):
- Phase 1 of competitor research: ~48 credits (4 competitor pages × 12 collections)
- Phase 1 of this workflow: ~12 credits (client pages, skip if recent crawl exists)
- Total: ~60 credits per client

---

## Common failures

- **Competitor page blocked (403)** — fall back to SERP snippet title from `DATA_getSerpResults`. Still useful for title tag pattern, just no H2/copy data.
- **Client page title includes junk** — e.g. `Maxis – Melani the label` (wrong separator, lowercase brand). The suggested title should fix the separator to ` | ` and match the brand's preferred casing.
- **H1 missing from client page** — flag as `Missing H1` and treat as highest priority (it's a quick developer fix with high SEO impact).
- **Suggestion over 60 chars** — shorten the keyword modifier first, then trim descriptors. Keep the primary keyword and brand intact.
