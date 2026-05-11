---
description: Show the full LD SEO command menu grouped by purpose
---

# LD SEO — Command Menu

When this command is invoked, present the user with the full menu of `/ldseo-*` commands organised by purpose. Reply with the table below verbatim, then ask which one they want to run.

Do not take any other action on `/ldseo` alone. This is a menu, not a workflow.

---

## Reply with this verbatim:

# LD SEO Commands

All commands take a `<client>` argument that maps to `docs/agent/clients/<client>.json`. Add a free-form instruction after the client to scope or override default behaviour.

## 🟢 Start here for a new client

| Command | What it does | MCPs / APIs |
|---|---|---|
| `/ldseo-onboard <slug>` | Full onboarding: gather facts, grant access, create sidecar from template, validate | GA4 Admin · Drive MCP · Monday MCP · SE Ranking Project API · `resolve_google_access_subject` |

## 🔵 Collection SEO pipeline

Run individually, or use `/ldseo-collection-seo` for the one-shot.

| Command | What it does | MCPs / APIs |
|---|---|---|
| `/ldseo-collection-seo <client>` | **One-shot:** discovery → keywords → SERP → metadata → Sheet → Monday | SE Ranking Project + Data APIs · Firecrawl · Drive MCP · Monday MCP · Shopify HTTP |
| `/ldseo-keyword-research <client>` | Discover collections, generate keywords, verify volumes, add to SE Ranking | SE Ranking Project + Data APIs · Drive MCP · Monday MCP · Shopify sitemap |
| `/ldseo-competitors <client>` | Scrape top 3 SERP competitors per primary keyword; 30-day cache | SE Ranking `DATA_getSerpResults` · Firecrawl |
| `/ldseo-metadata <client>` | Generate title + H1 + meta suggestions per collection → Sheet | SE Ranking `PROJECT_listKeywords` · Firecrawl · Drive MCP · Monday MCP |
| `/ldseo-content <client>` | Writer-ready content briefs with brand voice, HTML structure, internal links | SE Ranking Data API (related/similar/long-tail) · `PROJECT_getGoogleSearchConsole` · Drive MCP (Docs) · Monday MCP · Shopify HTTP |

## 🟣 Audits and reporting

| Command | What it does | MCPs / APIs |
|---|---|---|
| `/ldseo-audit-page <url>` | Quick single-page SEO read | Firecrawl · `extract_page_seo` |
| `/ldseo-audit-site <client>` | Firecrawl full-site audit → Sheet + Doc | Firecrawl `crawl_site` · Drive MCP · `create_firecrawl_seo_audit_doc` |
| `/ldseo-monthly-report <client>` | GA4 + Firecrawl combined monthly → Doc + Sheet | GA4 Data API · Firecrawl · Drive MCP · `create_combined_seo_report` · `resolve_google_access_subject` |
| `/ldseo-traffic <client>` | GA4 organic traffic check (confirms intent first) | GA4 Data API (only via combined report — no read-only tool yet) · `resolve_google_access_subject` |

## 🟡 Maintenance and diagnostics

| Command | What it does | MCPs / APIs |
|---|---|---|
| `/ldseo-hygiene [client or "all"]` | Audit SE Ranking projects, find duplicates, check plan cap | SE Ranking Project API (`listProjects`, `listKeywords`, `deleteKeywords`) · `DATA_getCreditBalance` |
| `/ldseo-troubleshoot <client> [error]` | Diagnose Google 401/403/404 before changing anything | `resolve_google_access_subject` · Drive MCP `get_file_permissions` · GA4 Admin (manual) |

## How invocation works

Every command opens with `python scripts/validate_client_json.py` against the client sidecar. **Zero blockers** are required before any deliverable phase runs. Common blockers:

- `brand_voice`, `tone_direction`, or `brand_display_name` missing → writer prompts can't reflect the brand
- `dominant_product_type` null or wrong → internal links target wrong collections
- SE Ranking / Drive / Monday IDs missing → can't write deliverables

Warnings (e.g. `h1_primary_keyword_mismatch`) don't block but should be surfaced to the client alongside the deliverable.

## Reference docs

- Skill specs: [`docs/agent/skills/_index.md`](docs/agent/skills/_index.md)
- Workflow playbooks: [`docs/agent/workflows/_index.md`](docs/agent/workflows/_index.md)
- Client JSON template: [`docs/agent/clients/CLIENT_TEMPLATE.json`](docs/agent/clients/CLIENT_TEMPLATE.json)

---

After printing the table, ask: **Which one would you like to run?**
