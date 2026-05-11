---
name: ld-seo-content-briefs
description: Create writer-ready Shopify collection content briefs with keyword reasoning, product context, Search Console opportunities, internal links, Google Docs, and Monday tasks.
---

# LD SEO Content Briefs

Use this skill for `/ldseo-content <client>` and plain-language collection content brief requests.

This skill creates writer-ready briefs, not final publishable copy. Use `ld-seo-shopify-collection-writing` when the user asks for final Shopify collection HTML drafts or QA of written collection copy.

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
- Do not pass raw keyword dumps to writers. Codex must reason through keyword fit and remove brand, local, irrelevant, cannibalising, and low-intent terms.
- Consider all included collections as internal-link candidates and select natural links a writer can actually place.
- Do not invent product claims, fabric details, sizing, shipping promises, or brand USPs.
- File Docs in `05 Content` or an explicit content folder, not audits.
- Read back a sample of generated Docs and every Monday task link before completion.
- Final collection copy is an optional follow-on step. Do not draft it automatically unless the user asks; when they do, route to `ld-seo-shopify-collection-writing`.

## Proof Block

Include collections covered, Docs created or updated, Monday tasks, Drive folder, keyword/GSC sources, validator blockers, warnings, and critique status.
