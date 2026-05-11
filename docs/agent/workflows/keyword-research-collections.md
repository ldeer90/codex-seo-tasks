# Keyword Research — Collection Pages

End-to-end workflow: discover collection pages via sitemap → generate keywords → verify volumes → add to SE Ranking → create Google Sheet → file in Drive → create Monday task.

Can be run as a full flow or any individual phase.

---

## Market scope — confirm before starting

**Default: AU only.** Most clients are Australian businesses targeting Australian search.

Ask the user (or check the client brief) before adding a US engine:
- Does the client sell/ship internationally to the US?
- Is US traffic a stated goal?

Clients confirmed as AU + US: **Melani the Label** (ships to US, dual-market strategy).
All other clients: **AU only** unless explicitly told otherwise.

This affects Phases 3, 4, and 5 — keyword intent, volume columns, and engine selection.

---

## Phase 0 — Pre-flight

Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.

1. **Read `docs/agent/clients/<client>.json`** (sidecar to the .md). This is the single source of truth for: domain, market scope, SE Ranking project + engine IDs, Drive folder IDs, Monday board ID, GA4 property, deliverable links, and per-collection cached state. If the JSON doesn't exist for this client, run `scripts/discover_collections.py --domain <domain> --output /tmp/<client>-collections.json` and seed a sidecar JSON from the schema in `melani-the-label.json`.
2. Check the SE Ranking plan capacity before adding keywords:
   - `PROJECT_listProjects` → sum all `keyword_count` values across all projects
   - Each keyword tracked on 2 engines = 2 pairs. Plan cap = 2,000 pairs (current).
   - Available = cap − current total. If < 50, warn the user before proceeding.
3. Check for duplicate projects (`PROJECT_listProjects` — same domain, multiple IDs). Flag to user. Do not delete without explicit approval.
4. **Skip `PROJECT_getSearchEngines`** — engine IDs are cached in `client.json.se_ranking.engines`. Only call if missing.

### Missing-input routing

Route missing client setup, Drive folder, Monday board, or SE Ranking project to `ld-seo-client-onboarding`; plan capacity, duplicate-project, access, or filing blockers to `ld-seo-maintenance`; stale collection state to `collection-seo-qa`; metadata or content follow-ups to `ld-seo-collection-seo` or `ld-seo-content-briefs`.

## Quality Gate — required

Before adding keywords:
1. Export `PROJECT_listKeywords(site_id=<project_id>)` to `/tmp/<client>-keywords.json`.
2. Run `scripts/validate_collection_seo_state.py` with the sidecar and any current page/SERP caches.
3. Confirm the number of pairs needed fits current SE Ranking capacity. If not, run `se-ranking-hygiene.md`.

After adding keywords:
1. Re-export `PROJECT_listKeywords`.
2. Save AU/US volume maps to `/tmp/<client>-volumes-au.json` and `/tmp/<client>-volumes-us.json`.
3. Run `scripts/sync_collection_sidecar_from_exports.py ... --output docs/agent/clients/<client>.json`.
4. Re-run `scripts/validate_collection_seo_state.py`. Sheets/Docs require zero blockers.

---

## Phase 1 — Collection Discovery + Product-Aware Classification

Use `scripts/discover_collections.py` — it pulls the sitemap, drops promo/utility slugs, then probes Shopify's free `/collections/<slug>/products.json` endpoint in parallel to classify each survivor by product_type concentration. **0 Firecrawl credits, ~25 collections checked in <2s.**

```bash
python scripts/discover_collections.py --domain <site> --output /tmp/<client>-collections.json
```

Output classes:

| Class | Trigger | Action |
|---|---|---|
| `pure_category` | ≥80% one product_type | Auto-include |
| `themed_category` | mixed but ≤3 types, top ≥50% | Auto-include |
| `curated_edit` | mixed, no clear theme (e.g. `tailored`) | **Flag for user review** |
| `style_edit` | colour/season grouping | Auto-drop unless user overrides |
| `empty` | 0 products | Drop |

After discovery, merge results into `client.json.collections[]` and persist any user override decisions on the `curated_edit` bucket so they're not re-asked next session.

**Why this matters:** the previous filter was subtractive only. Melani had 54 collections in the sitemap; the old regex kept 8. The product-aware classifier surfaces 22 SEO-priority pages — a 2.75× coverage lift.

---

## Phase 2 — Page Crawl (Firecrawl, optional)

Only needed if you want H1s, meta descriptions, and on-page content per collection. Skip if you already know the collections well.

```python
result = await client.crawl_site(
    url="https://<site>",
    limit=30,
    include_paths=["/collections/.*"],
)
```

**Credit cost:** 1 credit per page. 30-page crawl = 30 credits.

Alternatively scrape individual missing pages with `scrape_urls` (1 credit each). Note: `scrape_urls` response structure is `page['data']['markdown']`, not `page['markdown']` directly.

---

## Phase 3 — Keyword Collection And Expert Evaluation

The discovery script already provides `primary_keyword` per collection (heuristic from slug + dominant product_type). Use SE Ranking as the raw market source, then apply an SEO-expert selection gate before anything is added to live tracking.

### 3A — Collect candidates from SE Ranking

For each collection primary keyword, fetch candidates from SE Ranking Data API:

- `DATA_getRelatedKeywords`
- `DATA_getSimilarKeywords`
- `DATA_getLongTailKeywords`
- `DATA_getKeywordQuestions` only when the page may support FAQ/content sections; do not add question terms to rank tracking by default.

Save raw candidates to `/tmp/<client>-collection-keyword-candidates.json` in `by_slug` shape. Keep source labels, volume, difficulty, intent, and any SERP/GSC fields returned. Do not paste raw dumps into chat.

### 3B — Add expert context

Pull or reuse:

- AU/US volume maps for all candidates.
- GSC query/page opportunities where available.
- Structured SERP JSON for each primary keyword when the collection decision is ambiguous.
- Product samples and dominant product type from sidecar/discovery.

### 3C — Run the deterministic quality gate

```bash
python scripts/evaluate_collection_keyword_candidates.py \
  --client-json docs/agent/clients/<client>.json \
  --candidates-json /tmp/<client>-collection-keyword-candidates.json \
  --volume-json-au /tmp/<client>-candidate-volumes-au.json \
  --volume-json-us /tmp/<client>-candidate-volumes-us.json \
  --gsc-json /tmp/<client>-gsc-opportunities.json \
  --serp-json docs/<client>-serp-scrape-<date>.json \
  --output /tmp/<client>-keyword-candidate-evaluation.json
```

Every accepted keyword must include: `source`, `target_url`, AU volume, difficulty when available, expert score, score breakdown, and rationale.

### 3D — Codex judgement pass

Codex must review accepted and rejected candidates like an SEO expert before live tracking:

- **Rankability** — will this collection realistically rank, given difficulty, current GSC position, and SERP type?
- **Intent fit** — does the query belong on a collection/category page, not a product page, blog post, homepage, or sibling collection?
- **Cannibalisation** — does another collection already own the head term or closer intent?
- **SERP pattern** — do ranking pages look like collection pages with comparable products, or a different content type?
- **Business usefulness** — would traffic from this query plausibly help the client sell or make a good strategic page?

Only keywords that pass both the script and Codex judgement can be added to SE Ranking.

For each collection, target 1 primary keyword plus 2–5 useful supporting/tracked keywords where justified. Fewer strong keywords are better than padding.

The candidate pool can include:
- **Head terms:** the product category name (e.g. "midi dress", "maxi dress")
- **Modifier + head:** womens, australia, for women, online, buy
- **Intent variants:** going out, party, formal, summer, floral, boho
- **Long-tail:** "midi dress australia", "buy maxi dress online australia"
- **Product-title-derived:** scan `client.json.collections[*].sample_product_titles` for distinctive descriptors (e.g. if titles contain "RUCHED", consider `ruched midi dress`). Cheap signal that competitors miss.

**AU-only clients:** lean into "australia" geo-modifiers and AU buying intent ("buy online australia", "free shipping australia"). Skip US-specific style terms.

**AU + US clients only:** AU keywords use "australia" modifiers; US keywords lean toward style descriptors ("boho maxi dress", "floral maxi dress") with higher absolute volume on broad terms.

Typical target total:
- AU only: 60–80 keywords = 60–80 SE Ranking pairs (1 engine)
- AU + US: 60–80 keywords = 120–160 pairs (2 engines)

---

## Phase 4 — Volume Verification (SE Ranking)

Verify volumes before adding to SE Ranking. Max 10 keywords per call.

Region IDs: **Australia = `10`**, **USA = `182`**

**AU-only clients:** fetch AU volume only. For 70 keywords = 7 calls — **run all 7 in parallel** (single message with 7 MCP calls).
```
PROJECT_getSearchVolume(region_id=10, keywords=[...10 keywords...])
```

**AU + US clients:** fetch both regions, all batches in parallel.
```
PROJECT_getSearchVolume(region_id=10,  keywords=[...10 keywords...])
PROJECT_getSearchVolume(region_id=182, keywords=[...10 keywords...])
```
For 70 keywords = 14 parallel calls (run all in one message). Wall time: ~3s vs 14s sequential.

Keywords returning 0 are silently omitted from the response — treat missing = 0. Drop any keyword with 0 volume in all tracked regions unless it has clear strategic value.

---

## Phase 5 — Add to SE Ranking

**Hard limits:**
- Max 25 keyword-engine pairs per `PROJECT_addKeywords` call
- 12 keywords × 2 engines = 24 pairs = safe batch size
- Plan cap: 2,000 total pairs across all projects (check Phase 0 first)

Get the project's `site_engine_id`(s):
```
PROJECT_getSearchEngines(site_id=<project_id>)
```

**AU-only clients:** use only the AU `site_engine_id`. 12 keywords × 1 engine = 12 pairs per call (well within the 25-pair limit).

**AU + US clients:** use both engine IDs. 12 keywords × 2 engines = 24 pairs per call.

If an engine doesn't exist yet, add it with `PROJECT_addSearchEngine`. Note the returned `site_engine_id` — this is NOT the same as the region_id used for volume checks.

Add keywords in batches with target URL per collection:

```json
{
  "keyword": "maxi dress",
  "target_url": "https://<site>/collections/maxis",
  "site_engine_ids": [<au_engine_id>]
}
```

Run multiple batches in parallel where plan capacity allows.

---

## Phase 6 — Create Google Sheet (one-call, service-account)

Use the service account directly — it has Editor on every client folder. **One Python call, no MCP create-then-move dance.**

```python
from seo_automation_mcp.google_clients import GoogleWorkspaceClient
client = GoogleWorkspaceClient(delegated_subject='hello@agents.digital')
result = client.create_sheet(
    title=f"{client_name} — Keyword Research (Collections)",
    values=rows,                      # list[list[str]] including header row
    folder_id=client_json['drive']['folders']['03_audits'],
)
sheet_url = result['url']
```

**Columns (AU only):** `Keyword | Target Page | Collection | AU Monthly Volume`

**Columns (AU + US):** `Keyword | Target Page | Collection | AU Monthly Volume | US Monthly Volume`

After creation, write the sheet ID + URL back to `client.json.deliverables.keyword_research_sheet`.

For a narrative keyword research handoff, render the Doc body:

```bash
python scripts/render_keyword_research_doc.py \
    --client-json docs/agent/clients/<client>.json \
    --seranking-keywords-json /tmp/<client>-keywords.json \
    --output /tmp/<client>-keyword-research-doc.txt
```

Create into the target folder with `create_doc(..., folder_id=...)` or overwrite an existing Doc with `overwrite_doc_text(document_id, text)`.

---

## Phase 7 — File in Drive

Target: `Agents Digital / Clients / <Client> / 03 Audits`

Folder ID is in the client brief under `## Drive subfolders → 03 Audits`.

If the Drive MCP returns "User cannot add children" → use the service account Python move (see Phase 6).

---

## Phase 8 — Monday Task

1. Get board structure: `get_board_info(boardId=<board_id>)`
2. Identify the current month's group (e.g. "May '26")
3. Create item:

```json
{
  "boardId": <board_id>,
  "groupId": "<current month group id>",
  "name": "Keyword Research — Collections (AU only)",  // or "AU + US" if applicable
  "columnValues": {
    "status": {"label": "Done"},
    "date4": {"date": "YYYY-MM-DD"}
  }
}
```

4. Add update comment with:
   - Sheet link (Google Sheets URL)
   - Drive filing location
   - Collections covered
   - Top 5–6 volume highlights (AU and US)
   - Note that keywords are live in SE Ranking
   - Proof block: live keyword count, live pair count, collections covered, Drive folder, and validator warnings

---

## Running Individual Phases

| Goal | Phases to run |
|---|---|
| Just discover collections | Phase 0 + 1 |
| Build keyword list only (no SE Ranking) | Phase 0 + 1 + 2 (optional) + 3 + 4 |
| Add existing keywords to SE Ranking | Phase 0 (capacity check) + 5 |
| Create and file volume sheet only | Phase 4 + 6 + 7 |
| Log completed work in Monday | Phase 8 only |
| Full flow | All phases in order |

---

## Credit budget (Firecrawl free plan ~500/month)

| Action | Cost |
|---|---|
| Sitemap fetch (Phase 1) | 0 |
| Crawl 30 collection pages | 30 credits |
| Scrape individual missing pages | 1 credit each |
| SE Ranking volume checks | 0 (SE Ranking credits, not Firecrawl) |

**Rule:** always fetch sitemap first (Phase 1) before crawling. This avoids wasting credits on non-collection pages.

---

## Common failures

- **SE Ranking "available limit of adding is 1"** — plan cap hit. Check for duplicate projects wasting slots. Delete duplicates (with user approval), then retry.
- **"User cannot add children" (Drive MCP)** — `hello@` has view-only on that folder. Use service account Python move (Phase 6/7).
- **`scrape_urls` returns empty markdown** — response is nested: read `page['data']['markdown']`, not `page['markdown']`.
- **SE Ranking volume returns fewer keywords than sent** — keywords with 0 volume are silently omitted. Treat missing = 0.
- **Batch size error on `PROJECT_addKeywords`** — max 25 engine-pairs per call. Keep batches to 12 keywords × 2 engines = 24 pairs.

## Proof Block

Report client, market scope, keyword candidates reviewed, keywords added or confirmed, SE Ranking pair usage, Sheet/Doc outputs, cache paths, validator blockers, warnings, next action, and client timeline update status.
