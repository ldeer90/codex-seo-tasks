---
name: ld-seo-content-briefs
description: Create writer-ready Shopify collection content briefs with keyword reasoning, product context, Search Console opportunities, internal links, Google Docs, and Monday tasks.
---

# LD SEO Content Briefs

Use this skill for `/ldseo-content <client>` and plain-language content brief requests,
including Shopify collection briefs, information-page briefs, and blog/article briefs.

This skill creates client-ready content brief/page-copy documents. Use `ld-seo-shopify-collection-writing` when the user asks for final Shopify-ready HTML drafts or QA of written collection copy.

## Required Reading

1. `docs/agent/workflows/collection-content-briefs.md`
2. `docs/agent/skills/shopify-collection-content-briefs/SKILL.md`
3. `docs/agent/skills/collection-seo-qa/SKILL.md`
4. `docs/agent/clients/<client>.json`
5. `docs/agent/clients/<client>.md` when present
6. `docs/agent/clients/<client>-timeline.md`

## Client Memory

For every client-scoped content brief or ad hoc request, follow `docs/agent/client-memory.md`: read the client brief, sidecar when present, and client timeline before live work, then append the timeline after completion or after discovering a meaningful blocker.

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md` before brief generation. Route missing client setup to `ld-seo-client-onboarding`, access/GSC/Drive/Monday issues to `ld-seo-maintenance`, stale collection state to `ld-seo-collection-seo` plus `collection-seo-qa`, final copy requests to `ld-seo-shopify-collection-writing`, and client-facing Doc work to Google Drive skills after validation.

## Production Rules

- Validate collection SEO state before brief generation.
- Use tracked keywords, supplemental SE Ranking keyword research, Search Console opportunities, SERP context, product samples, and current page copy.
- Use the Salad Servers Wedding Catering page-copy format as the current client-facing standard: native Google Docs tables for `Overview`, `Keywords To Work Into The Page`, `Internal Links`, `Recommended Heading Hierarchy`, and `SEO Review`.
- For brief-only blog/article or information-page documents, adapt the same Salad Servers structure but replace final copy with a table-led `Writer Notes`, `FAQs To Cover`, or `Article Requirements` section. Only include `Example Copy` when the user asks for page copy or draft copy.
- In client-facing Google Docs, tables must be real Google Docs table objects that visually look like tables to a human. Do not rely on markdown pipe-table text for final Docs.
- Render briefs/page-copy documents with `scripts/render_collection_content_brief_doc.py` and do not hand-build a different structure unless the user explicitly asks for a one-off variation.
- Include SE Ranking monthly search volume beside every primary and supporting query. Search Console impressions can support prioritisation, but they do not replace keyword volume research.
- Do not pass raw keyword dumps to writers. Codex must reason through keyword fit and remove brand, local, irrelevant, cannibalising, and low-intent terms.
- Consider all included collections as internal-link candidates and select natural links a writer can actually place.
- Do not invent product claims, fabric details, sizing, shipping promises, or brand USPs.
- File Docs in `05 Content` or an explicit content folder, not audits.
- Read back a sample of generated Docs and every Monday task link before completion.
- The `Example Copy` section should be client-presentable page copy in the style of the Salad Servers Wedding Catering page when copy has been requested. It can include page title, meta description, H1, hero subheading, and section copy.
- Final Shopify HTML is still a follow-on step. When the user asks for clean Shopify HTML or publish-ready copy, route to `ld-seo-shopify-collection-writing`.

## Proof Block

Include collections covered, Docs created or updated, Monday tasks, Drive folder, keyword/GSC sources, validator blockers, warnings, and critique status.
