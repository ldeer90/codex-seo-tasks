---
description: Shopify collection content briefs — writer-ready Docs + Monday tasks
argument-hint: <client> [scope or instruction]
---

# LD SEO — Content Briefs

Shopify collection content brief workflow for Laurence Deer clients.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **SE Ranking Data API** | `DATA_getRelatedKeywords`, `DATA_getSimilarKeywords`, `DATA_getLongTailKeywords` (supplemental keyword research) |
| **SE Ranking Project API** | `PROJECT_listKeywords` (live keyword export), `PROJECT_getGoogleSearchConsole` (GSC opportunity queries) |
| **Google Drive MCP** | Docs `create_doc`, `overwrite_doc_text` (one Doc per collection brief) |
| **Monday MCP** | `get_board_info`, `create_item`, `create_update` (one task per collection) |
| **Shopify (HTTP)** | Live collection page scrape, product JSON pull |
| **Local scripts** | `validate_client_json.py`, `build_collection_content_brief_inputs.py`, `validate_collection_content_briefs.py`, `render_collection_content_brief_doc.py`, `research_supplemental_keywords.py` |

## What this skill does

Produces writer-ready Google Docs and Monday tasks for Shopify collection pages — one Doc and one task per SEO-priority collection. Briefs include:

- Proposed title tag and meta description with change flags
- Full keyword strategy: primary, secondary, supplemental (SE Ranking), and GSC opportunity queries
- Required HTML heading structure: H2 + two H3s
- Writer/LLM prompt with brand voice, tone direction, and supplemental keyword placement instructions
- Internal linking plan with scored anchor text and placement rationale
- 10-item QA checklist

## How to invoke

```
/ldseo-content <client> [instruction]
```

Examples:

```
/ldseo-content melani-the-label
/ldseo-content melani-the-label gowns midis sets
/ldseo-content melani-the-label produce content for all collections
/ldseo-content melani-the-label update the brief for swim only
```

If `<client>` is omitted, ask which client before proceeding.

## On invoke — required reading

Before taking any action, read these files in order:

1. `docs/agent/clients/$CLIENT.json` — sidecar state
2. `docs/agent/clients/$CLIENT.md` — client brief and context
3. `docs/agent/skills/shopify-collection-content-briefs/SKILL.md` — full skill rules
4. `docs/agent/workflows/collection-content-briefs.md` — phase-by-phase workflow

## Phase 0 — Client JSON validation (always run first)

```bash
python scripts/validate_client_json.py --client-json docs/agent/clients/$CLIENT.json
```

Stop on any blocker. If `brand_voice`, `tone_direction`, or `brand_display_name` are missing, derive them from the client's existing site copy and confirm with the user before proceeding — the writer prompt quality depends on these fields.

If no client JSON exists, copy `docs/agent/clients/CLIENT_TEMPLATE.json` and fill every REQUIRED field before continuing.

## Phase 1 — Keyword research and reasoning (in-session, per collection)

For each included collection, call SE Ranking:
- `DATA_getRelatedKeywords` — overlapping intent
- `DATA_getSimilarKeywords` — semantically adjacent
- `DATA_getLongTailKeywords` — higher-specificity variants

Reason through every candidate in-session before writing any output. Apply the framework from Phase 1a of the workflow doc. Do not pass raw SE Ranking output to the builder.

## Phase 2 — Build, validate, render

```bash
python scripts/build_collection_content_brief_inputs.py \
  --client-json docs/agent/clients/$CLIENT.json \
  --seranking-keywords-json /tmp/$CLIENT-keywords.json \
  --volume-json-au /tmp/$CLIENT-volumes-au.json \
  --pages-json /tmp/$CLIENT-pages.json \
  --serp-json docs/$CLIENT-serp-scrape-<date>.json \
  --product-json /tmp/$CLIENT-products.json \
  --supplemental-keywords-json /tmp/$CLIENT-supplemental-keywords-reasoned.json \
  --gsc-json /tmp/$CLIENT-gsc-opportunities.json \
  --output /tmp/$CLIENT-content-briefs.json

python scripts/validate_collection_content_briefs.py \
  --client-json docs/agent/clients/$CLIENT.json \
  --briefs-json /tmp/$CLIENT-content-briefs.json

python scripts/render_collection_content_brief_doc.py \
  --briefs-json /tmp/$CLIENT-content-briefs.json \
  --output-dir /tmp/$CLIENT-content-brief-docs
```

## Phase 3 — Write to Drive and Monday

Only after user confirmation. Use `GoogleWorkspaceClient.overwrite_doc_text()` for existing Docs, `create_doc()` for new ones. File to `drive.folders.05_content`. Create one Monday task per collection.

## Proof block (end every run with this)

- Client and market scope
- Collections covered
- Google Docs created or updated (with URLs)
- Monday tasks created or updated
- Drive folder ID
- Keyword source and SE Ranking export date
- Validator blockers: 0
- Remaining warnings, or `none`

## Hard rules

- Zero validator blockers before any Drive or Monday write
- Never invent product claims, fabric details, fit notes, or brand USPs
- Never put the same supplemental keyword in two collections
- Every supplemental keyword must have a one-sentence reason — if you can't write it, the keyword doesn't belong
- Output format is clean HTML: `<h2>`, two `<h3>`, `<p>` tags — no markdown, no `<h1>`
- `brand_display_name` on first mention in every piece of copy, then the full `client` name thereafter
