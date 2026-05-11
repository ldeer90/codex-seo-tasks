---
description: GA4 + Firecrawl combined monthly SEO report — Doc + Sheet
argument-hint: <client> [period]
---

# LD SEO — Monthly Combined Report

Produces one Google Doc (narrative) + one Google Sheet (data) per client. Uses GA4 organic landing pages from a current period and a comparison period, then audits each landing page with Firecrawl.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **GA4 Data API** | `runReport` (organic landing pages, period vs comparison period) — accessed via `GoogleWorkspaceClient.run_ga4_report` |
| **Firecrawl** | Per-landing-page audit (title, meta, H1, status, redirects) |
| **Google Drive MCP** | Doc + Sheet creation, move into client's reports folder |
| **Monday MCP** | Optional task creation if client tracks reports in Monday |
| **MCP server tool** | `create_combined_seo_report` (orchestrates the GA4 + Firecrawl + Doc + Sheet flow) |
| **Access router** | `resolve_google_access_subject(validate_ga4_access=True)` — checks delegated subject can read the GA4 property |

## How to invoke

```
/ldseo-monthly-report <client> [period]
```

Examples:

```
/ldseo-monthly-report melani-the-label
/ldseo-monthly-report joe-rascal april 2026
/ldseo-monthly-report ducati-melbourne last quarter
```

## On invoke — required reading

1. `docs/agent/clients/$CLIENT.md` — for GA4 property ID, website URL, access subject
2. `docs/agent/clients/$CLIENT.json` — for confirmed Drive folder
3. `docs/agent/workflows/monthly-combined-report.md`

## Pre-flight

1. Confirm date ranges with the user. Default for "last month":
   - `start_date` = first day of last calendar month
   - `end_date` = last day of last calendar month
   - Comparison = same length, prior year
2. Confirm crawl limit. Default 25, max 50.
3. Run `resolve_google_access_subject` with `validate_ga4_access=True`. Stop if subject doesn't match expectation.

## Run

Tool: `create_combined_seo_report`

Required inputs: `client_name`, `ga4_property_id`, `website_url`, `start_date`, `end_date`, `comparison_start_date`, `comparison_end_date`, `max_crawl_limit`.

## Hard rules

- Confirm date ranges and crawl limit with the user before running
- Never skip the access validation step
- File outputs to client's monthly reports folder; update sidecar with Doc + Sheet URLs
- Create a Monday task only if the client uses Monday for report tracking
