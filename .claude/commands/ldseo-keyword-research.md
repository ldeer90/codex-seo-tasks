---
description: Collection page keyword research — discover, generate, verify volumes, add to SE Ranking
argument-hint: <client> [scope or phase]
---

# LD SEO — Keyword Research (Collections)

End-to-end keyword research for collection pages: sitemap discovery → keyword generation → volume verification → SE Ranking add → Google Sheet → Drive → Monday task.

Can run as full flow or any individual phase.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **SE Ranking Data API** | `DATA_getSearchVolume`, `DATA_getRelatedKeywords`, `DATA_getSimilarKeywords`, `DATA_getLongTailKeywords`, `DATA_getKeywordQuestions` |
| **SE Ranking Project API** | `PROJECT_listKeywords`, `PROJECT_addKeywords`, `PROJECT_getSearchVolume`, `PROJECT_listProjects` |
| **Google Drive MCP** | Sheets `create_file` (keyword research Sheet) |
| **Monday MCP** | `create_item` (tracking task) |
| **Shopify (HTTP)** | `sitemap.xml` fetch for collection discovery |
| **Local scripts** | `validate_client_json.py`, `validate_collection_seo_state.py` |

## How to invoke

```
/ldseo-keyword-research <client> [scope or phase]
```

Examples:

```
/ldseo-keyword-research melani-the-label
/ldseo-keyword-research joe-rascal discover only
/ldseo-keyword-research ducati-melbourne add to SE Ranking for confirmed list
```

## On invoke — required reading

1. `docs/agent/clients/$CLIENT.json` — sidecar
2. `docs/agent/clients/$CLIENT.md` — client brief
3. `docs/agent/skills/collection-seo-qa/SKILL.md`
4. `docs/agent/workflows/keyword-research-collections.md`

## Market scope — confirm before starting

Default: **AU only**. Most clients target Australian search.

Add US engine only if:
- Client sells/ships to the US
- US traffic is a stated goal
- `client.market_scope` is `AU+US`

Currently confirmed AU+US: Melani the Label.

## Phase 0 — Validate

```bash
python scripts/validate_client_json.py --client-json docs/agent/clients/$CLIENT.json
```

## Hard rules

- Confirm market scope before generating keywords
- Verify volumes from SE Ranking before adding to project
- Run `/ldseo-hygiene` first if SE Ranking project is near plan cap (2,000 pairs)
- Sync sidecar after any keyword add; re-run `validate_collection_seo_state.py`
- Default keyword status: `Active`
