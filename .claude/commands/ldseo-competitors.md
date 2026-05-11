---
description: Scrape top SERP competitors per primary keyword; feeds metadata + content briefs
argument-hint: <client> [scope]
---

# LD SEO — Competitor SERP Research

For each collection's primary keyword, fetch the top Google results and scrape the ranking pages to extract title tags, headings, and on-page content. Used to inform metadata strategy and content briefs.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **SE Ranking Data API** | `DATA_getSerpResults` (top 10 organic per keyword, AU/US engines) |
| **Firecrawl** | Page scrape of each top-3 competitor URL — title, H1, H2, meta, word count |
| **Local scripts** | `validate_client_json.py`, `validate_collection_seo_state.py` |

Output saved to `docs/<client>-serp-scrape-<date>.json` and referenced in sidecar `deliverables.competitor_serp_json.path`.

## How to invoke

```
/ldseo-competitors <client> [scope]
```

Examples:

```
/ldseo-competitors melani-the-label
/ldseo-competitors joe-rascal top 5 collections only
/ldseo-competitors ducati-melbourne refresh stale scrape
```

## Run after

`/ldseo-keyword-research` (needs primary keyword per collection).

## Feeds into

`/ldseo-metadata` and `/ldseo-content`.

## On invoke — required reading

1. `docs/agent/clients/$CLIENT.json` — sidecar (`collections[]` with primary keywords)
2. `docs/agent/workflows/competitor-keyword-research.md`

## Freshness check

If `client.json.deliverables.competitor_serp_json.updated` is < 30 days old AND every collection has `competitor_top3_urls` populated → **skip the scrape entirely** and reuse the cache. Tell the user.

## Region

- AU-only clients: scrape AU SERPs only
- AU+US clients: scrape AU SERPs; optionally US SERPs for collections where US is a key market

## Phase 0 — Validate

```bash
python scripts/validate_client_json.py --client-json docs/agent/clients/$CLIENT.json
```

## Hard rules

- Save raw SERP JSON to `docs/$CLIENT-serp-scrape-<date>.json` and reference path in sidecar `deliverables.competitor_serp_json`
- Update `competitor_top3_urls` on each collection in the sidecar
- Don't re-scrape if cached data is < 30 days old unless the user explicitly asks
