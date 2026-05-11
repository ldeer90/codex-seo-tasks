---
name: ld-seo-shopify-collection-writing
description: Write, revise, or QA publish-ready Shopify collection page body HTML from approved briefs, with keyword, internal-link, voice, and unsupported-claim validation.
---

# LD SEO Shopify Collection Writing

Use this skill after `ld-seo-content-briefs` when the user wants final Shopify collection copy, HTML drafts, writer/LLM output QA, or collection copy revisions.

## Required Reading

1. `docs/agent/workflows/collection-content-writing.md`
2. Approved collection brief JSON or Google Doc brief for the collection.
3. `docs/agent/clients/<client>.json`
4. `docs/agent/clients/<client>.md` when present
5. `docs/agent/clients/<client>-timeline.md`

## Client Memory

For every client-scoped collection writing or ad hoc request, follow `docs/agent/client-memory.md`: read the client brief, sidecar when present, and client timeline before live work, then append the timeline after completion or after discovering a meaningful blocker.

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md` before drafting. Route missing client setup to `ld-seo-client-onboarding`, access or destination blockers to `ld-seo-maintenance`, missing approved briefs/product/keyword/SERP/link inputs to `ld-seo-content-briefs`, blog/article copy to `ld-seo-shopify-blog-writing`, and client-facing Doc work to Google Drive skills after validation.

## Production Rules

- Do not write final copy from memory. Use approved briefs, product context, keyword data, SERP context, Search Console signals, and brand voice.
- Before drafting, review top-ranking collection pages for the primary keyword and set copy length from their useful descriptive depth; use `scripts/analyze_collection_serp_length.py` when a saved review is available.
- Review collection sitemap exports with `scripts/build_collection_internal_link_candidates.py`, then use Codex judgement to choose 2-4 natural collection links where helpful.
- Output Shopify collection body HTML only: one `<h2>`, exactly two `<h3>`, `<p>` tags, and contextual `<a href="">` links where approved.
- Do not include `<h1>`, markdown, wrapper divs, scripts, styles, lists, comments, or explanatory text around the HTML.
- Use the primary keyword naturally near the start and include supplemental keywords only when they fit the page.
- Include internal links only where they help the shopper compare related ranges; use only approved URLs from the brief.
- Use the SERP-derived length range in the approved brief; use 220-320 words only as a documented fallback when competitor review is unavailable.
- Do not invent product claims, fabric details, sizing, stock, shipping, sustainability, origin, pricing, medical/legal, or competitive claims.
- Validate with `scripts/validate_collection_html_copy.py` before presenting, uploading, or filing the copy.
- Read back any Google Doc or Monday output before calling the draft filed or complete.

## Proof Block

Include client, content type, collection URL, brief source, local draft path, SERP length sources reviewed, recommended length range, sitemap source, link candidates reviewed, final links selected, validation blockers, warnings, word count, primary keyword, internal links included, and unsupported-claim status.
