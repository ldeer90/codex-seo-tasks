# Competitor Research — SERP Scraping

For each collection's primary keyword, fetch the top Google results and scrape the ranking pages to extract their title tags, headings, and on-page content. Used to inform metadata strategy and collection copy.

**Run after:** `keyword-research-collections.md` (needs primary keyword per collection).
**Feeds into:** `onpage-title-h1-suggestions.md`

---

## Phase 0 - Access And Input Preflight

Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.

1. **Read `docs/agent/clients/<client>.json`** — provides domain, market scope, and `collections[]` with primary keywords.
2. **Check freshness:** if `client.json.deliverables.competitor_serp_json.updated` is < 30 days old AND every collection has `competitor_top3_urls` populated, **skip Phases 1–2 entirely** and reuse the cached scrape. The downstream onpage workflow can still run from cached data.
3. Decide search region:
   - AU-only clients: scrape AU SERPs only
   - AU + US clients: scrape AU SERPs; optionally US SERPs for collections where US is a key market

### Missing-input routing

Route missing client setup or SE Ranking project to `ld-seo-client-onboarding`, SERP/API/access/capacity blockers to `ld-seo-maintenance`, missing collection keywords or stale sidecar state to `ld-seo-collection-seo` plus `collection-seo-qa`, and downstream metadata requests to `onpage-title-h1-suggestions.md` after structured SERP validation.

## Quality Gate

Before reusing cached SERP data, run:

```bash
python scripts/validate_collection_seo_state.py \
    --client-json docs/agent/clients/<client>.json \
    --seranking-keywords-json /tmp/<client>-keywords.json \
    --serp-json docs/<client>-serp-scrape-<date>.json
```

Legacy flat SERP JSON is allowed only as a warning for old caches. New SERP saves must use the structured per-slug shape below and must update `competitor_top3_urls` in the sidecar.

---

## Phase 1 — Get SERP Results per Collection

For each collection's primary keyword, fetch the top 10 organic results.

Use SE Ranking's SERP tool:
```
DATA_getSerpResults(
    keyword=<primary_keyword>,
    region=<region_code>,   # "AU" for Australia
    limit=10
)
```

Run all collections in parallel — one call per collection keyword.

For 12 collections = 12 parallel calls.

Extract from each result:
- `url` — the ranking page URL
- `position` — rank 1–10
- `title` — the title tag as Google shows it
- Ignore: ads, People Also Ask, image packs, maps

Keep only organic results from positions 1–5. Filter out:
- Marketplaces too large to learn from (The Iconic, ASOS) — keep if they're in top 3, they're unavoidable
- Pinterest, Reddit, social media pages
- The client's own site if it appears

---

## Phase 2 — Scrape Ranking Pages (Firecrawl)

Scrape the top 3–5 organic URLs per collection keyword.

```python
result = await client.scrape_urls(urls=[url1, url2, url3, ...])

for page in result:
    inner = page.get('data', {})
    meta = inner.get('metadata', {})
    content = inner.get('markdown', '')

    title = meta.get('title', '').strip()
    description = meta.get('description', '').strip()
    h1s = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
    h2s = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    # First 300 words of body content (collection description copy)
    body = ' '.join(content.split()[:300])
```

**Credit cost:** 1 per page. 12 collections × 4 pages = ~48 credits. Run all scrapes in one batch via `scrape_urls` (accepts a list of URLs).

**Note:** `scrape_urls` response structure is `page['data']['markdown']`, not `page['markdown']` directly.

---

## Phase 3 — Extract Patterns

For each collection, compile what the top-ranking pages are doing:

```
Collection: Maxi Dresses (keyword: "maxi dress")

Rank 1 — showpo.com/maxi-dresses
  Title: Maxi Dresses | Shop Women's Maxi Dresses Online | Showpo AU
  H1: Maxi Dresses
  H2s: Long Maxi Dresses, Floral Maxi Dresses, Formal Maxi Dresses
  Description: Shop the latest maxi dresses at Showpo...
  Copy excerpt: "From flowy florals to sleek evening styles..."

Rank 2 — meshki.com.au/collections/maxi-dresses
  Title: Maxi Dresses | Long Dresses For Women | MESHKI
  H1: Maxi Dresses
  ...
```

Identify patterns across the top 3–5:
- **Title formula:** most common structure (keyword + brand, or keyword + descriptor + brand)
- **H1 pattern:** is it identical to title, shorter, or does it add a descriptor?
- **H2 themes:** what subcategories/facets do they break into?
- **Copy angle:** what benefits or descriptors do they lead with?

---

## Phase 4 — Save Raw Data + Update Sidecar

Save the scraped data as a structured JSON file for use in the title/H1 suggestions workflow:

```
docs/<client>-serp-scrape-<date>.json
```

**Then update `client.json`:**
- `deliverables.competitor_serp_json` → `{path, updated}`
- For each collection, set `competitor_top3_urls` to the URLs of the top 3 ranking pages and `last_scraped` to today's date

This enables the 30-day cache hit on the next run.

Structure:
```json
{
  "collection_slug": {
    "primary_keyword": "...",
    "au_volume": 60500,
    "serp_results": [
      {
        "position": 1,
        "domain": "showpo.com",
        "url": "...",
        "title": "...",
        "h1": "...",
        "h2s": [...],
        "meta_description": "...",
        "copy_excerpt": "..."
      }
    ],
    "patterns": {
      "title_formula": "...",
      "common_h1": "...",
      "common_h2_themes": [...],
      "copy_angles": [...]
    }
  }
}
```

---

## Common failures

- **`DATA_getSerpResults` returns no organic results** — keyword may be too niche or region not supported. Try a broader keyword for that collection.
- **Firecrawl blocked by site (403/429)** — large retailers (Showpo, The Iconic) may block scrapers. Skip and use the SERP title/snippet (already returned by `DATA_getSerpResults`) as a fallback — it contains the title tag and sometimes a meta description snippet.
- **Page has no H1 in markdown** — common on JavaScript-rendered sites. Note as "H1 not detected" — the SERP title is still useful.
- **Credit budget** — 12 collections × 4 pages = 48 credits. On the free plan (~500/month), this is fine but factor it in when planning the month's crawl budget.

## Proof Block

Report collections covered, SERP query count, scrape count, structured SERP JSON path, sidecar update status, cache freshness, validator warnings, any blocked competitor pages, and client timeline update status.
