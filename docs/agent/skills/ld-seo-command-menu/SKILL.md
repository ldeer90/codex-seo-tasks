---
name: ld-seo-command-menu
description: Show the LD SEO task library and route requests to the right workflow, with scan-friendly commands, required inputs, expected outputs, and safety notes.
---

# LD SEO Command Menu

This is the Codex-native router for LD SEO. Do not read `.claude/commands/` for normal operation; those files are legacy reference only. Route directly to the repo-local skill and workflow below.

For low-token routing, read `docs/agent/routing-manifest.json` first. It summarises commands, intents, workflow docs, required preflight reads, MCP/API dependencies, scripts, validators, write gates, readback requirements, proof-block fields, and handoff routes. Then open the canonical skill and workflow docs before live work, external writes, or blocker resolution.

Supporting references:

- `docs/agent/scripts-index.md` for script purpose, inputs, outputs, mutation risk, and when not to run.
- `docs/agent/proof-block-templates.md` for reusable proof blocks that stay out of client-facing Docs.
- `docs/agent/skill-architecture-diagrams.md` as a visual companion, not executable policy.

## Task Library

Use this table as the user-facing LD SEO command menu. Prefer the plain-English "Use when" language when presenting options in chat, and keep the command visible for fast invocation.

| Lane | Task | Use when | Needs | Creates or returns | Canonical route |
|---|---|---|---|---|---|
| Start | `/ldseo` | You want the menu of available LD SEO workflows. | Nothing. | A scan-friendly task library and routing suggestions. | `ld-seo-command-menu` -> `docs/agent/skills/_index.md` |
| Onboard | `/ldseo-onboard <client>` | A new SEO client needs the operating system wired up before work starts. | Client slug, website, access facts, target folders and boards. | Client sidecar, brief, access routes, Drive/Monday setup checks, zero-blocker validation. | `ld-seo-client-onboarding` -> `docs/agent/workflows/add-new-client.md` |
| Collection SEO | `/ldseo-collection-seo <client>` | You want the full Shopify collection pipeline in one pass. | Valid client sidecar, sitemap or crawl source, SE Ranking/GSC access where available. | Collection discovery, keyword set, competitor context, metadata sheet, Monday-ready task trail. | `ld-seo-collection-seo` -> `docs/agent/workflows/collection-seo-full.md` |
| Collection SEO | `/ldseo-keyword-research <client>` | You need collection keywords researched or refreshed without running the whole pipeline. | Collection URLs, market/search engine, SE Ranking capacity. | Prioritised keyword candidates, volumes, mapping notes, supporting Sheet/sidecar updates. | `ld-seo-collection-seo` -> `docs/agent/workflows/keyword-research-collections.md` |
| Collection SEO | `/ldseo-competitors <client>` | You need SERP competitors reviewed for priority collection keywords. | Approved primary keywords and market. | Competitor patterns, SERP notes, content/metadata inputs. | `ld-seo-collection-seo` -> `docs/agent/workflows/competitor-keyword-research.md` |
| Collection SEO | `/ldseo-metadata <client>` | Title tags, H1s, and meta descriptions need generation or refresh. | Valid collection SEO state and keyword choices. | Metadata recommendations in a Sheet with QA notes. | `ld-seo-collection-seo` -> `docs/agent/workflows/onpage-title-h1-suggestions.md` |
| Content Planning | `/ldseo-content <client>` | Writers or LLMs need clear Shopify collection content briefs. | Collection URLs, keyword decisions, product context, voice guidance, internal links. | Writer-ready Google Docs and Monday tasks with structure, links, and SEO notes. | `ld-seo-content-briefs` -> `docs/agent/workflows/collection-content-briefs.md` |
| Content Production | Final collection copy or Shopify collection HTML | An approved collection brief needs publish-ready body copy. | Approved brief, brand voice, target keywords, approved internal links. | Shopify-ready HTML plus validation against unsupported claims and brief requirements. | `ld-seo-shopify-collection-writing` -> `docs/agent/workflows/collection-content-writing.md` |
| Content Production | Final blog copy, article copy, or Shopify blog HTML | An approved blog brief needs a polished article draft or QA pass. | Approved blog brief, style guide, sources, keyword data, internal links. | Shopify-ready article HTML with source/link/claim checks. | `ld-seo-shopify-blog-writing` -> `docs/agent/workflows/blog-content-writing.md` |
| Content Production | Generic final content writing from a brief | The request says "content writing" but does not clearly say collection or blog. | The approved brief type. | Routes to the right final-writing workflow. | `ld-seo-content-writing` -> collection or blog writing skill |
| Audits | `/ldseo-audit-page <url>` | One page needs a fast SEO read without Drive output. | Public URL. | Page-level SEO fields, issues, and recommendations in chat. | `ld-seo-audits-reporting` -> `docs/agent/workflows/single-page-audit.md` |
| Audits | `/ldseo-audit-site <client>` | A site needs a technical Screaming Frog audit and client-ready findings. | Client slug, start URL if not in the brief, crawl scope. | Raw crawl export, analysis summary, priority issues, proof block. | `ld-seo-audits-reporting` -> `docs/agent/workflows/full-site-audit.md` |
| Reporting | `/ldseo-monthly-report <client>` | You need the monthly client performance comment for Monday approval. | Client slug, reporting month, GA4/GSC/SE Ranking/Monday access. | Draft client-safe performance comment in chat first; post only after approval. | `ld-seo-audits-reporting` -> `docs/agent/workflows/monthly-performance-comment.md` |
| Reporting | Explicit Doc + Sheet report request | You specifically ask for a crawl-backed report document and support sheet. | Confirmed client, website, GA4 property, dates, crawl limit, output subject. | Google Doc and Sheet report pair. | `ld-seo-audits-reporting` -> `docs/agent/workflows/monthly-combined-report.md` |
| Reporting | `/ldseo-traffic <client>` | You just need organic traffic numbers, not a deliverable. | Client slug, GA4 property/date range if not obvious. | GA4 organic traffic check in chat. | `ld-seo-audits-reporting` -> `docs/agent/workflows/ga4-traffic-check.md` |
| Maintenance | `/ldseo-hygiene [client|all]` | SE Ranking or platform state needs cleanup, capacity checks, or duplicate review. | Client slug or `all`, plus current platform state. | Hygiene findings, cleanup plan, validation notes. | `ld-seo-maintenance` -> `docs/agent/workflows/se-ranking-hygiene.md` |
| Maintenance | `/ldseo-troubleshoot <client>` | Access, routing, Drive, GA4, or credential errors need diagnosis. | Client slug and the error or failing workflow. | Smallest-fix diagnosis and proof of the checked route. | `ld-seo-maintenance` -> `docs/agent/workflows/troubleshoot-access.md` |

### Presentation Notes

- Lead with the `Lane`, `Task`, and `Use when` columns when showing the menu to a human.
- Include `Needs` only when the user is deciding what to run next or when a workflow is blocked.
- Keep `Creates or returns` visible so the user knows whether the workflow writes to Drive, Monday, or chat.
- `/ldseo-monthly-report` always means `docs/agent/workflows/monthly-performance-comment.md`; `docs/agent/workflows/monthly-combined-report.md` is legacy and only for explicit Doc + Sheet report requests.

## Skill Graph

Onboarding creates valid client state. Maintenance fixes access, capacity, and filing issues. Collection SEO feeds metadata sheets and collection content briefs. Content briefs feed final collection writing. Blog writing depends on an approved brief, writing style guide, keyword data, sitemaps, SERP review, and internal links. Audits/reporting depend on client setup, GA4/GSC/SE Ranking/Monday access for monthly performance comments, Screaming Frog access for full technical audits, Drive access where relevant, and readback QA.

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md` for all routed work. For client-scoped requests, also follow `docs/agent/client-memory.md`: read the client brief, sidecar when present, and client timeline before live work, then append the timeline after completion or after discovering a meaningful blocker. If prerequisites are missing, route to the smallest dependent skill before continuing instead of improvising around blockers.

## Routing Rules

- If a command has `<client>`, first confirm `docs/agent/clients/<client>.json` exists unless the task is onboarding.
- If no client slug is supplied and it cannot be inferred from the request, ask for the slug.
- Choose the smallest workflow that satisfies the request; use full collection SEO only when the user asks for the full pipeline.
- Read the client brief, sidecar when present, client timeline, canonical skill, and workflow before live writes.
- End with the proof block required by the workflow.

## Production Defaults

- Validate sidecars before live work.
- Use cached exports before paid API calls.
- Save large API responses to files, not chat.
- Use Codex judgement for keyword/content/business decisions after the facts are gathered.
- Read back Drive and Monday outputs before calling client-facing work complete.

## Proof Block

Use the proof block required by the routed workflow.
