# Repo-Local Skills

These skills are project-owned specs for repeatable agent behaviour.

Codex-native skills in this directory are the canonical LD SEO control layer. Workflows in `docs/agent/workflows/` contain the detailed procedures; skills stay short and route tasks to the right workflow with the right guardrails.

`.claude/commands/` is legacy reference only. Do not read those files for normal operation unless you are explicitly migrating or comparing old Claude Code command behaviour.

`scripts/sync_codex_skills.py` installs lightweight installed Codex skill entrypoints into `~/.codex/skills` so future Codex sessions can discover these repo-owned skills natively. The repo-local skills remain the source of truth.

For low-token routing, inspect [`../routing-manifest.json`](../routing-manifest.json) first. It summarises canonical skill routes, required reads, MCP/API dependencies, scripts, validators, write gates, readback requirements, proof fields, and handoff routes. Open the full skill and workflow docs before live work, external writes, or resolving blockers.

Supporting low-token references:

- [`../scripts-index.md`](../scripts-index.md) — compact map of script purpose, inputs, outputs, mutation risk, and when not to run.
- [`../proof-block-templates.md`](../proof-block-templates.md) — reusable proof blocks for agent responses and internal validation, not client-facing Docs.
- [`../skill-architecture-diagrams.md`](../skill-architecture-diagrams.md) — visual architecture companion; useful for understanding, not executable policy.

## Skill Graph

- `ld-seo-client-onboarding` creates valid client state: sidecar, brief, Drive folders, Monday board, GA4 route, and SE Ranking project.
- `ld-seo-maintenance` fixes access, SE Ranking capacity, duplicate projects, Drive filing, routing, and platform-state issues.
- `ld-seo-collection-seo` discovers collections, researches keywords, syncs sidecars, and feeds metadata sheets plus collection content briefs.
- `ld-seo-content-briefs` creates collection briefs from collection SEO state, product context, keyword reasoning, GSC, SERP context, and internal links.
- `ld-seo-shopify-collection-writing` writes final collection HTML from approved collection briefs.
- `ld-seo-shopify-blog-writing` writes final blog HTML from approved blog briefs, writing style guides, keyword data, sitemaps, SERP review, and internal links.
- `ld-seo-audits-reporting` depends on client setup, GA4/GSC/SE Ranking/Monday access for monthly performance comments, Screaming Frog access for full technical audits, Drive access where relevant, and readback QA.

All canonical LD SEO skills follow [`_routing-contract.md`](_routing-contract.md). Missing prerequisites must route to the smallest dependent skill before live writes or client-facing output.

## Codex Invocations

Users may still type `/ldseo-*` because it is convenient, but Codex should route from `docs/agent/routing-manifest.json` and the table below rather than through `.claude/commands/`. Plain-language requests route to the same canonical skills. For example, "create content briefs for Melani" maps to `ld-seo-content-briefs`, while "refresh title and H1 suggestions for Melani" maps to `ld-seo-collection-seo`.

### Task Library

This is the human-facing LD SEO menu. Show it as a table when a user asks what tasks are available, what a task does, or which workflow they should run next.

| Lane | Command or request | Best for | Typical inputs | Output | Canonical skill |
|---|---|---|---|---|---|
| Start | `/ldseo` | Browsing the LD SEO task library before choosing a workflow. | None. | Menu plus routing guidance. | `ld-seo-command-menu` |
| Onboard | `/ldseo-onboard <client-slug>` | Setting up a new SEO client properly before delivery work starts. | Client slug, website, access facts, Drive/Monday targets. | Validated sidecar, client brief, routing, folders, board setup, zero-blocker check. | `ld-seo-client-onboarding` |
| Maintain | `/ldseo-troubleshoot <client> [error]` | Diagnosing GA4, Drive, routing, SE Ranking, or credential problems. | Client slug and error context. | Smallest-fix diagnosis before changing anything. | `ld-seo-maintenance` |
| Maintain | `/ldseo-hygiene [client or "all"]` | Cleaning up SE Ranking projects, duplicates, keyword capacity, and platform reference drift. | Client slug or `all`. | Hygiene findings, capacity notes, cleanup recommendations. | `ld-seo-maintenance` |
| Collection SEO | `/ldseo-collection-seo <client>` | Running the complete Shopify collection SEO pipeline. | Client sidecar, collection URLs, market/search engine access. | Discovery, keyword research, SERP context, metadata, Sheet, Monday handoff. | `ld-seo-collection-seo` |
| Collection SEO | `/ldseo-keyword-research <client>` | Refreshing collection keyword strategy without the full pipeline. | Collection URLs, target market, SE Ranking capacity. | Prioritised keywords, volume checks, mapping notes, Sheet/sidecar updates. | `ld-seo-collection-seo` |
| Collection SEO | `/ldseo-competitors <client>` | Learning what top-ranking competitors are doing for target terms. | Approved primary keywords and market. | Competitor SERP patterns that feed metadata and briefs. | `ld-seo-collection-seo` |
| Collection SEO | `/ldseo-metadata <client>` | Producing title tag, H1, and meta description recommendations. | Valid collection SEO state and keyword decisions. | Metadata suggestions in a QA-ready Sheet. | `ld-seo-collection-seo` |
| Content briefs | `/ldseo-content <client> [instruction]` | Creating writer-ready Shopify collection briefs. | Product context, keywords, voice guidance, internal links. | Google Docs and Monday tasks with structure, SEO notes, and approved links. | `ld-seo-content-briefs` |
| Final copy | Final collection copy or Shopify collection HTML | Turning an approved collection brief into publish-ready Shopify HTML. | Approved collection brief, brand voice, target keywords, approved links. | Validated collection body HTML. | `ld-seo-shopify-collection-writing` |
| Final copy | Final blog copy, article copy, or Shopify blog HTML | Turning an approved blog brief into a polished article. | Approved blog brief, sources, style guide, keywords, internal links. | Validated Shopify blog HTML. | `ld-seo-shopify-blog-writing` |
| Final copy | Generic final content writing from a brief | Routing vague "write the content" requests to the right final-copy workflow. | Brief type. | Collection or blog writing route. | `ld-seo-content-writing` |
| Audit | `/ldseo-audit-page <url>` | Checking one public URL quickly. | URL. | Page-level SEO issues and recommendations in chat; no Drive output. | `ld-seo-audits-reporting` |
| Audit | `/ldseo-audit-site <client> [start_url] [limit]` | Creating a full technical SEO audit from a crawl. | Client slug, start URL, crawl scope. | Screaming Frog export, analysis, issue priorities, proof block. | `ld-seo-audits-reporting` |
| Reporting | `/ldseo-monthly-report <client> [period]` | Drafting a Monday-safe monthly performance comment. | Client slug, period, GA4/GSC/SE Ranking/Monday context. | Client-ready comment draft in chat first; post only after approval. | `ld-seo-audits-reporting` |
| Reporting | `/ldseo-traffic <client>` | Pulling organic traffic numbers without a deliverable. | Client slug, GA4 property/date range if needed. | GA4 organic traffic check in chat. | `ld-seo-audits-reporting` |

For explicit crawl-backed report documents, use `docs/agent/workflows/monthly-combined-report.md` only when the user asks for a Doc + Sheet report. `/ldseo-monthly-report` routes to the monthly performance comment workflow, not that legacy report workflow.

## Skill Docs (read when triggered by workflow or request)

| Skill | When to use |
|---|---|
| [ld-seo-command-menu/SKILL.md](ld-seo-command-menu/SKILL.md) | Any `/ldseo-*` command, LD SEO command menu request, or plain-language SEO automation request that needs routing |
| [ld-seo-client-onboarding/SKILL.md](ld-seo-client-onboarding/SKILL.md) | New client setup: Drive, Monday, GA4 routing, SE Ranking, sidecar and brief creation |
| [ld-seo-collection-seo/SKILL.md](ld-seo-collection-seo/SKILL.md) | Collection discovery, keyword research, SE Ranking additions, competitor SERP, metadata suggestions |
| [ld-seo-content-briefs/SKILL.md](ld-seo-content-briefs/SKILL.md) | Collection content briefs, Search Console opportunities, supplemental keywords, internal links, Docs and Monday tasks |
| [ld-seo-shopify-collection-writing/SKILL.md](ld-seo-shopify-collection-writing/SKILL.md) | Final Shopify collection body HTML from approved collection briefs, with keyword, link, structure, and unsupported-claim QA |
| [ld-seo-shopify-blog-writing/SKILL.md](ld-seo-shopify-blog-writing/SKILL.md) | Final Shopify blog article body HTML from approved blog briefs, with brief-defined structure, links, sources, and unsupported-claim QA |
| [ld-seo-content-writing/SKILL.md](ld-seo-content-writing/SKILL.md) | Backwards-compatible router for final content writing; routes to the collection or blog writing skill |
| [ld-seo-audits-reporting/SKILL.md](ld-seo-audits-reporting/SKILL.md) | Single-page audits, full-site audits, monthly reports, monthly performance comments, and GA4 traffic checks |
| [ld-seo-maintenance/SKILL.md](ld-seo-maintenance/SKILL.md) | SE Ranking hygiene, access troubleshooting, Drive filing, platform refresh, and operational maintenance |
| [collection-seo-qa/SKILL.md](collection-seo-qa/SKILL.md) | Collection SEO, SE Ranking keyword additions, sidecar repair, metadata suggestions, keyword research Docs/Sheets |
| [shopify-collection-content-briefs/SKILL.md](shopify-collection-content-briefs/SKILL.md) | Supporting specialist skill for Shopify collection content briefs. Canonical high-level routing is `ld-seo-content-briefs`. |

## Shared Production Rules

- Follow the shared routing contract before live work or client-facing output.
- For client-scoped work, read and append the client timeline described in `docs/agent/client-memory.md`.
- Validate client sidecars before live work.
- Use cached exports before paid API calls.
- Batch SE Ranking volume checks and prefer bulk exports where possible.
- Save large live responses to files instead of pasting them into chat.
- Use Codex judgement for keyword selection, content strategy, prioritisation, and client-facing recommendations.
- For blog writing, review the top 3 relevant ranking blog/article results for the primary keyword before drafting, then adapt useful strategic patterns without copying wording.
- Read back Google Docs, Sheets, and Monday tasks after writes.
- End every successful deliverable with a proof block: data freshness, outputs created or updated, Drive folder, Monday task, warnings, and validator blockers.
- Keep proof blocks out of client-facing Docs. Client Docs should look human-prepared, with polished tables, headings, hyperlinks, and only the content a client/writer needs to review.
