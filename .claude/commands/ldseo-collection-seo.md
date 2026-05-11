---
description: Full collection SEO pipeline — discovery → keywords → SERP → metadata → Sheet → Monday
argument-hint: <client> [phase or instruction]
---

# LD SEO — Collection SEO (Full Pipeline)

One-shot full collection SEO pipeline: discovery → keywords → competitor SERP → metadata suggestions → Sheet → Monday. Driven by `client.json` sidecar.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **SE Ranking Project API** | `PROJECT_listKeywords`, `PROJECT_addKeywords`, `PROJECT_listProjects`, `PROJECT_getSearchVolume` |
| **SE Ranking Data API** | `DATA_getSerpResults`, `DATA_getRelatedKeywords`, `DATA_getSimilarKeywords` |
| **Firecrawl** | Live page scrape for current title/H1/meta and competitor SERP page extraction |
| **Google Drive MCP** | Sheets and Docs creation for metadata Sheet and reports |
| **Monday MCP** | `get_board_info`, `create_item` (tracking task) |
| **Shopify (HTTP)** | Sitemap fetch, collection JSON discovery |
| **Local scripts** | `validate_client_json.py`, `validate_collection_seo_state.py`, `sync_collection_sidecar_from_exports.py` |

## How to invoke

```
/ldseo-collection-seo <client> [phase or instruction]
```

Examples:

```
/ldseo-collection-seo melani-the-label
/ldseo-collection-seo joe-rascal phase 3 only
/ldseo-collection-seo ducati-melbourne refresh keyword volumes
```

If `<client>` is omitted, ask which client first.

## On invoke — required reading

1. `docs/agent/clients/$CLIENT.json` — sidecar
2. `docs/agent/clients/$CLIENT.md` — client brief
3. `docs/agent/skills/collection-seo-qa/SKILL.md` — skill rules
4. `docs/agent/workflows/collection-seo-full.md` — phase-by-phase workflow

## Phase 0 — Validate and load sidecar

```bash
python scripts/validate_client_json.py --client-json docs/agent/clients/$CLIENT.json
```

Stop on blockers. If `client.json` doesn't exist, run `/ldseo-onboard $CLIENT` first.

## Quality Gate — required before and after live writes

1. Export live keywords: `PROJECT_listKeywords(site_id=<project_id>)` → `/tmp/$CLIENT-keywords.json`
2. Sync sidecar: `python scripts/sync_collection_sidecar_from_exports.py`
3. Validate: `python scripts/validate_collection_seo_state.py`
4. Stop on blockers. Document warnings in proof block.

## Hard rules

- Zero validator blockers before any SE Ranking write or Drive deliverable
- Sidecar must be re-synced after every live SE Ranking write
- AU-only by default unless `client.market_scope` is `AU+US`
- Proof block at end of every run: live keyword count, pair count, collection coverage, deliverable URLs, warnings
