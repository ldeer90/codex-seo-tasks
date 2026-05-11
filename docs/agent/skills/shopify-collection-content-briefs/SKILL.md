---
name: shopify-collection-content-briefs
description: Use for Shopify ecommerce collection content briefs, collection copy briefs, internal linking plans, writer or LLM draft preparation, and Google Doc handoffs for collection page content.
---

# Shopify Collection Content Briefs

Use this skill when creating writer-ready content briefs for Shopify collection pages.

Core rule: do not create Google Docs or Monday tasks until the collection state, keyword data, current page data, product context, SERP context, supplemental keyword research, Search Console opportunity data, and internal link plan have passed validation.

## Required Flow

1. Read `docs/agent/workflows/collection-content-briefs.md`, `docs/agent/workflows/collection-seo-full.md`, and the relevant client brief/sidecar.
2. Run the Collection SEO QA quality gate first. Collection content briefs depend on synced sidecar state.
3. Save live exports:
   - SE Ranking project keywords and AU/US volumes.
   - Current collection page scrape and structured per-slug SERP JSON.
   - Product samples from Shopify where sidecar samples are thin.
4. **Keyword research and reasoning (Phase 1a)** — fetch SE Ranking related/similar/long-tail per collection, then reason through each candidate in-session. Produce a curated `by_slug` supplemental keywords file with a `reasoning` field on every accepted keyword. See Phase 1a in the workflow doc.
5. Save Google Search Console high-potential queries when access is available.
6. Build offline brief inputs with `scripts/build_collection_content_brief_inputs.py`.
7. Validate with `scripts/validate_collection_content_briefs.py`. Stop on blockers.
8. Render one Doc body per collection with `scripts/render_collection_content_brief_doc.py`.
9. Only after user/client confirmation, create one Google Doc and one Monday task per collection.
10. Update the sidecar with Doc IDs, URLs, updated dates, internal link targets, and batch coverage.
11. End with a proof block: collections covered, Docs created, tasks created, Drive folder, keyword source, and remaining warnings.

## Scripts

- Build brief JSON:
  `python scripts/build_collection_content_brief_inputs.py --client-json docs/agent/clients/<client>.json --seranking-keywords-json /tmp/<client>-keywords.json --volume-json-au /tmp/<client>-volumes-au.json --volume-json-us /tmp/<client>-volumes-us.json --pages-json /tmp/<client>-pages.json --serp-json docs/<client>-serp-scrape-<date>.json --product-json /tmp/<client>-products.json --supplemental-keywords-json /tmp/<client>-supplemental-keywords-scored.json --gsc-json /tmp/<client>-gsc-opportunities.json --output /tmp/<client>-content-briefs.json`
- Validate:
  `python scripts/validate_collection_content_briefs.py --client-json docs/agent/clients/<client>.json --briefs-json /tmp/<client>-content-briefs.json`
- Render Doc bodies:
  `python scripts/render_collection_content_brief_doc.py --briefs-json /tmp/<client>-content-briefs.json --output-dir /tmp/<client>-content-brief-docs`

## Client JSON Requirements

The following fields must be present in the client JSON for full brief quality:

- `brand_display_name` — the typographically correct brand name (e.g. `MÉLANI`) used on first mention in copy
- `brand_voice` — one paragraph describing the brand's register, positioning, and what good copy sounds like vs bad copy
- `tone_direction` — one or two sentences of specific guidance for the writer: what to lead with, what to avoid
- `usp` — the primary customer-facing benefit (e.g. free shipping threshold, made-in detail)

If `brand_voice` or `tone_direction` are absent, the writer prompt falls back to generic guidance and the output will sound like a briefed freelancer, not the brand.

## Do Not

- Do not invent product claims, fabric details, fit notes, shipping promises, or brand USPs.
- Do not use keyword lists without volumes or source labels.
- Do not accept plain text or markdown output from a writer or LLM. All collection copy must be delivered as clean HTML: one `<h2>`, two `<h3>`, and `<p>` tags for body copy. No `<h1>`, no wrapper elements.
- Do not leave heading slots vague. The brief must specify suggested text for the H2 and both H3s — the writer fills them in, not invents the structure.
- Do not skip the keyword reasoning step. Passing raw SE Ranking output straight to the builder produces contaminated briefs (competitor brand names, catalog mismatches, cannibalized terms).
- Do not include a keyword in the supplemental list if you cannot write a one-sentence reason for why it belongs to that specific collection.
- Do not put the same keyword in two collections' supplemental lists. Assign it to the one where it fits best.
- Do not create internal links from memory; score candidates from the included collection set.
- Do not file content briefs in audits. Use `05 Content` or a confirmed content briefs folder.
- Do not create one large Doc unless the user explicitly asks. The default is one Doc and one Monday task per collection.
