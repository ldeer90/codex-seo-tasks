---
name: ld-seo-shopify-blog-writing
description: Write, revise, or QA publish-ready Shopify blog/article HTML from approved briefs, with keyword, source, internal-link, voice, and claim validation.
---

# LD SEO Shopify Blog Writing

Use this skill when the user asks for final Shopify blog copy, article HTML, blog draft QA, or revisions from an approved blog brief.

## Required Reading

1. `docs/agent/workflows/blog-content-writing.md`
2. Approved blog brief JSON or Google Doc brief.
3. `docs/agent/clients/<client>.json`
4. `docs/agent/clients/<client>.md` when present
5. `docs/agent/clients/<client>-timeline.md`

## Client Memory

For every client-scoped blog writing or ad hoc request, follow `docs/agent/client-memory.md`: read the client brief, sidecar when present, and client timeline before live work, then append the timeline after completion or after discovering a meaningful blocker.

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md`. Route missing client setup to `ld-seo-client-onboarding`, access or destination blockers to `ld-seo-maintenance`, missing brief/style/keyword/SERP/internal-link inputs to `ld-seo-content-briefs`, collection copy requests to `ld-seo-shopify-collection-writing`, and client-facing Doc work to Google Drive skills after validation.

## Production Rules

- Start with the workflow preflight gate. Confirm the client sidecar/brief, website, Drive destination for Docs, Monday board/group for tasks, approved brief, writing style guide, sitemap exports, SE Ranking keyword/SERP data, and optional GSC access before drafting.
- If preflight fails, route to the dependent LD SEO skill instead of working around missing inputs: onboarding for missing client setup, maintenance for access/credential problems, content briefs for missing brief/style/keyword/SERP/internal-link inputs, collection writing for collection copy, and Google Docs for client-facing Doc creation or edits.
- Do not write blog copy from memory. Use the approved brief, keyword strategy, audience, intent, sources, sitemap-grounded internal links, CTA guidance, and brand voice.
- The blog brief defines the HTML policy. If it does not specify allowed HTML tags or required structure, stop and request a complete brief.
- Before drafting, review collection and blog sitemap exports with `scripts/build_blog_internal_link_candidates.py`, then use Codex judgement to choose 1-5 natural collection links plus optional supporting blog links.
- Before drafting, review the top 3 relevant ranking blog/article results for the primary keyword using SE Ranking SERP data where available. Extract useful structure, angles, FAQs, trust signals, and gaps; adapt the best strategic patterns without copying wording or unsupported claims.
- Output Shopify article body HTML only unless the brief explicitly allows a fuller article structure.
- Use the primary keyword naturally near the opening and use secondary keywords only where they fit the article.
- Include only approved internal links and approved sources/external links.
- Do not invent product, shipping, origin, sustainability, pricing, stock, medical/legal, statistical, or competitive claims.
- Validate with `scripts/validate_blog_html_copy.py` before presenting, uploading, or filing the copy.
- If creating a Google Doc, make it client-presentable: use real tables for article details, keyword strategy, and internal links; show one formatted article draft with headings and hyperlinked anchor text; keep raw HTML and validator proof out of the Doc body.
- Read back any Google Doc or Monday output before calling the draft filed or complete.

## Proof Block

Include client, content type, target article title or slug, brief source, local draft path, sitemap sources, SERP sources reviewed, link candidates reviewed, final links selected, validation blockers, warnings, word count, primary keyword, secondary keywords used, and unsupported-claim status.

This proof block is for the agent response, local validation output, or Monday update. It must not appear inside a client-facing Google Doc.
