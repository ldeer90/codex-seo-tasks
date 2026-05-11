---
name: ld-seo-audits-reporting
description: Audit pages and sites, pull GA4 organic traffic checks, and draft monthly SEO performance comments or report deliverables with readback QA.
---

# LD SEO Audits And Reporting

Use this skill for `/ldseo-audit-page`, `/ldseo-audit-site`, `/ldseo-monthly-report`, `/ldseo-traffic`, monthly SEO performance comments, and equivalent plain-language requests.

`/ldseo-monthly-report <client>` always uses `docs/agent/workflows/monthly-performance-comment.md`.

Do not route `/ldseo-monthly-report` to `monthly-combined-report.md`, `create_combined_seo_report`, or any crawl-based Doc + Sheet workflow. A monthly report is a performance-comment workflow built from GA4, SE Ranking, Search Console, seasonality, and completed Monday work.

## Required Reading

Choose the smallest workflow that fits:
- Single-page audit: `docs/agent/workflows/single-page-audit.md`
- Full-site audit: `docs/agent/workflows/full-site-audit.md`
- `/ldseo-monthly-report`: `docs/agent/workflows/monthly-performance-comment.md`
- Traffic check: `docs/agent/workflows/ga4-traffic-check.md`

Also read the client brief, sidecar when present, and timeline when a client is involved.

## Client Memory

For every client-scoped audit, traffic, report, or ad hoc request, follow `docs/agent/client-memory.md`: read the client brief, sidecar when present, and client timeline before live work, then append the timeline after completion or after discovering a meaningful blocker.

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md` before report or audit writes. Route missing client setup, GA4, Drive, Monday, SE Ranking, or Search Console state to `ld-seo-client-onboarding`; access, Screaming Frog, Drive filing, GA4/GSC, SE Ranking, or Monday routing failures to `ld-seo-maintenance`; strategy follow-up items to `ld-seo-content-briefs`, `ld-seo-collection-seo`, or `seo-roadmap-prioritisation` as appropriate.

## Production Rules

- Confirm client, website, GA4 property, reporting month, comparison windows, SE Ranking project/search engine, Search Console source, Monday board/item, and whether the user wants draft-only or approved posting.
- For monthly performance comments, always present a detailed analysis in chat first, including key metrics, comparisons, seasonality, ranking movement, Search Console availability/results, notable landing pages, relevant caveats, and proposed Monday-ready wording.
- For monthly performance comments, ask the user for additional context at the beginning and require explicit permission after the chat analysis before posting to Monday.
- Treat requests like "do this client next" as permission to research and draft only. Do not create or update Monday in the same step unless the user has already reviewed the detailed chat analysis and approved the exact posting direction.
- For performance commentary, always include YoY context, use only Organic Search and Organic Shopping unless the user asks otherwise, and consider seasonality before concluding.
- For performance commentary, include exact seasonal event dates and comparable event windows where relevant.
- For performance commentary, include SE Ranking visibility/keyword movement and Search Console query/page average position.
- For performance commentary, include completed Monday tasks from the reporting period.
- For Monday comments, use compact HTML formatting that is safe for Monday's renderer: do not wrap the update in `<p>` tags, do not put tables after `</p>`, avoid blank lines inside the HTML body, and use at most one `<br><br>` between sections.
- For keyword movement in Monday report updates, use compact HTML tables when the user asks for tables or there are more than 3 keyword examples. Keep table cells short.
- For keyword tables in Monday report updates, include quantified, client-friendly results such as clicks, impressions, CTR, average position, search volume, start rank, end rank, and movement. Avoid broad qualitative tables like `Keyword group | April result | Why it matters` unless the user specifically requests a strategic summary only.
- Do not include internal source columns such as `Source` in client-facing keyword tables unless the distinction is genuinely useful. When the user asks for SE Ranking keyword changes, use one compact table focused on rank movement rather than adding a separate GSC table.
- For keyword tables in Monday report updates, include 1-3 balanced watch or downward rows when the data supports them. Label them plainly as watch, softening, volatility, or opportunity rather than excluding them.
- Do not duplicate completed-work lists in a Monday report update when the same tasks are already visible on the Monday board or in the linked report, unless the user explicitly asks for that section.
- Validate client state and access before report writes; stop on blockers.
- Prefer no-write traffic checks when the user only wants a read on performance.
- Prefer Screaming Frog for full technical site audits when the local CLI and a project-approved `.seospiderconfig` are available.
- Use `scripts/run_screaming_frog_audit.py` for Screaming Frog crawls and `scripts/analyze_screaming_frog_export.py` for dataset analysis.
- Use Codex judgement to turn raw issues into client-ready priority: business impact, SEO impact, effort, and confidence.
- Read back created Docs/Sheets and verify links before completion.
- Do not call an audit client-ready if it is only a raw scrape; it needs prioritised findings and next actions.

## Proof Block

For monthly performance comments, include client, reporting period, GA4 property and channels used, SE Ranking project/search engine, Search Console property/source, Monday item/update URL if posted, and caveats. For technical audits, include pages audited or exported rows, crawl source/config, export path or URLs, Drive folder, top issues, and residual warnings.
