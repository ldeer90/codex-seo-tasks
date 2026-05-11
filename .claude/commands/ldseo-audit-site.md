---
description: Firecrawl full-site SEO audit — Sheet + Doc in client audits folder
argument-hint: <client> [start_url] [limit]
---

# LD SEO — Full Site Audit

Crawl a site (or section), audit each page, write a Sheet of crawl data + a narrative Doc.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **Firecrawl** | `crawl_site` for the full crawl, plus per-page scrape for SEO data |
| **Google Drive MCP** | Doc + Sheet creation, file into `drive.folders.03_audits` |
| **Monday MCP** | Optional task creation if client tracks audits in Monday |
| **MCP server tools** | `create_firecrawl_seo_audit_doc` (orchestrates crawl + audit + Doc + Sheet), `crawl_site` (raw access for `include_paths` filtering) |

## How to invoke

```
/ldseo-audit-site <client> [start_url] [limit]
```

Examples:

```
/ldseo-audit-site melani-the-label
/ldseo-audit-site joe-rascal https://joerascal.com/collections 50
/ldseo-audit-site ducati-melbourne https://ducatimelbourne.com.au 25
```

## On invoke — required reading

1. `docs/agent/clients/$CLIENT.md` — client name, default start_url
2. `docs/agent/workflows/full-site-audit.md`

## Pre-flight

1. Confirm `client_name` and `start_url`
2. Confirm crawl limit. Default 25, hard ceiling 100. SME sites: 50 covers most indexable surface
3. Crawler does NOT follow subdomains and does NOT allow external links
4. For section restriction, use `crawl_site` directly with `include_paths` regex — `create_firecrawl_seo_audit_doc` does not expose `include_paths`

## Run

Tool: `create_firecrawl_seo_audit_doc`

Input: `{ "client_name": "<name>", "start_url": "<url>", "limit": <int> }`

## Hard rules

- Confirm crawl limit before running — Firecrawl credits are billable
- File output Sheet + Doc to client's audits folder (`drive.folders.03_audits`)
- Create Monday task if client tracks audits in Monday
