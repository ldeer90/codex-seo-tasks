---
description: Title + H1 + meta description suggestions per collection page; output Sheet
argument-hint: <client> [scope]
---

# LD SEO — Metadata Suggestions (Title, H1, Meta)

Generates title tag, H1, and meta description suggestions for each collection page using the client's keyword research and competitor SERP scrape data. Output is a Google Sheet ready for client handoff.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **SE Ranking Project API** | `PROJECT_listKeywords` (live volumes for primary keywords) |
| **Firecrawl** | Live current-page scrape per collection URL (current title/H1/meta) |
| **Google Drive MCP** | Sheets `create_file`, file move into client's content/audits folder |
| **Monday MCP** | `create_item` (handoff task) |
| **Local scripts** | `validate_client_json.py`, `validate_collection_seo_state.py` |

Reads cached SERP scrape from `client.json.deliverables.competitor_serp_json.path`.

## How to invoke

```
/ldseo-metadata <client> [scope]
```

Examples:

```
/ldseo-metadata melani-the-label
/ldseo-metadata joe-rascal collections only
/ldseo-metadata ducati-melbourne refresh sheet
```

## Run after

`/ldseo-competitors` (needs SERP scrape JSON in `client.json.deliverables.competitor_serp_json.path`).

## On invoke — required reading

1. `docs/agent/clients/$CLIENT.json` — sidecar (especially `collections[]` and `deliverables.competitor_serp_json`)
2. `docs/agent/skills/collection-seo-qa/SKILL.md`
3. `docs/agent/workflows/onpage-title-h1-suggestions.md`

## Phase 0 — Validate

```bash
python scripts/validate_client_json.py --client-json docs/agent/clients/$CLIENT.json
```

If `competitor_serp_json` is missing or > 30 days old, run `/ldseo-competitors $CLIENT` first.

## Quality Gate

Before generating or uploading suggestions:

```bash
python scripts/validate_collection_seo_state.py \
  --client-json docs/agent/clients/$CLIENT.json \
  --seranking-keywords-json /tmp/$CLIENT-keywords.json \
  --pages-json /tmp/$CLIENT-pages.json \
  --serp-json docs/$CLIENT-serp-scrape-<date>.json
```

The metadata generator fails if more than 10% of included collections are missing volume or current title/H1.

## Hard rules

- Title formula derived from observed SERP patterns, not invented
- Brand suffix uses the casing from `client.brand_display_name`
- Never inflate volumes — use the live SE Ranking export
- Output: one Sheet, one Monday task, sidecar updated with Sheet ID and URL
