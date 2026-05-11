---
name: ld-seo-collection-seo
description: Run Shopify collection SEO workflows: discover collections, research keywords, review SERPs, update SE Ranking state, build metadata Sheets, and pass QA gates.
---

# LD SEO Collection SEO

Use this skill for `/ldseo-collection-seo`, `/ldseo-keyword-research`, `/ldseo-competitors`, `/ldseo-metadata`, and equivalent plain-language requests.

## Required Reading

Choose the smallest workflow that fits:
- Full pipeline: `docs/agent/workflows/collection-seo-full.md`
- Keyword research: `docs/agent/workflows/keyword-research-collections.md`
- Competitor SERP: `docs/agent/workflows/competitor-keyword-research.md`
- Metadata suggestions: `docs/agent/workflows/onpage-title-h1-suggestions.md`

Also read:
- `docs/agent/skills/collection-seo-qa/SKILL.md`
- `docs/agent/clients/<client>.json`
- `docs/agent/clients/<client>.md` when present
- `docs/agent/clients/<client>-timeline.md`

## Client Memory

For every client-scoped collection SEO or ad hoc request, follow `docs/agent/client-memory.md`: read the client brief, sidecar when present, and client timeline before live work, then append the timeline after completion or after discovering a meaningful blocker.

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md` before collection SEO work. Route missing client setup to `ld-seo-client-onboarding`, access/capacity issues to `ld-seo-maintenance`, stale collection state to `collection-seo-qa`, content brief requests to `ld-seo-content-briefs`, and client-facing Doc/Sheet work to the Google Drive skills after validation.

## Production Rules

- Run client JSON validation before live work.
- Run collection SEO validation before Drive deliverables and after any SE Ranking write.
- Use Shopify sitemap/products JSON before Firecrawl crawling.
- Batch SE Ranking volume checks in groups of 10 and run independent batches in parallel.
- Evaluate raw keyword candidates with `scripts/evaluate_collection_keyword_candidates.py` before adding them to live tracking.
- Reuse structured SERP cache when it is less than 30 days old and complete.
- Save large exports to `/tmp` or `docs/` and pass file paths into scripts.
- Use Codex judgement for keyword-to-collection fit, cannibalisation, title formula choice, and client-facing recommendations.
- Read back Sheets/Docs and Monday tasks after writes.

## Proof Block

Include live keyword count, keyword-engine pairs, collections covered, deliverable rows, Drive folder, Monday task, validator blockers, and warnings.
