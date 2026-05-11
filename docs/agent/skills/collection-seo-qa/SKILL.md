---
name: collection-seo-qa
description: Use for collection SEO workflows, SE Ranking keyword additions, sidecar repair, metadata suggestions, keyword research deliverables, and any task that reconciles client collection pages with SE Ranking, SERP, Drive, or cached sidecar state.
---

# Collection SEO QA

Use this skill whenever a task touches collection SEO state or deliverables.

Core rule: live writes are not complete until live tool state has been exported, the sidecar has been synced, and validation passes or any remaining warnings are documented.

## Required Flow

1. Read `docs/agent/workflows/collection-seo-full.md` and the relevant client brief.
2. Before adding keywords or creating deliverables, run the workflow's Quality Gate pre-flight.
3. After any SE Ranking write, fetch `PROJECT_listKeywords`, save the raw response, sync the sidecar with `scripts/sync_collection_sidecar_from_exports.py`, then run `scripts/validate_collection_seo_state.py`.
4. Before writing a Sheet or Doc, require zero validator blockers.
5. End with a proof block: live keyword count, live pair count, collection coverage, deliverable rows/sections, Drive folder, and remaining warnings.

## Scripts

- Validate state:
  `python scripts/validate_collection_seo_state.py --client-json docs/agent/clients/<client>.json --seranking-keywords-json /tmp/<client>-keywords.json --pages-json /tmp/<client>-pages.json --serp-json docs/<client>-serp-scrape-<date>.json`
- Sync sidecar:
  `python scripts/sync_collection_sidecar_from_exports.py --client-json docs/agent/clients/<client>.json --seranking-keywords-json /tmp/<client>-keywords.json --volume-json-au /tmp/<client>-volumes-au.json --volume-json-us /tmp/<client>-volumes-us.json --pages-json /tmp/<client>-pages.json --output docs/agent/clients/<client>.json`
- Render keyword research doc body:
  `python scripts/render_keyword_research_doc.py --client-json docs/agent/clients/<client>.json --seranking-keywords-json /tmp/<client>-keywords.json --output /tmp/<client>-keyword-research-doc.txt`

## Do Not

- Do not trust sidecar counts after live SE Ranking writes until re-exported and validated.
- Do not generate metadata suggestions from legacy flat SERP JSON unless this is explicitly a diagnostic draft.
- Do not call a workflow "done" because the external write succeeded; done means the sidecar and docs also reflect it.
