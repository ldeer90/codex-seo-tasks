---
description: GA4 organic traffic check — confirms intent first (no read-only GA4 tool yet)
argument-hint: <client> [period]
---

# LD SEO — GA4 Traffic Check

Quick GA4 organic-landing-page read for a client. No Firecrawl, no Drive output.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **GA4 Data API** | `runReport` — only available via `create_combined_seo_report` today (no read-only wrapper exists) |
| **Access router** | `resolve_google_access_subject(validate_ga4_access=True)` — confirms the delegated subject can read the property before any GA4 work |

> **Constraint:** there is no read-only GA4 MCP tool yet. This command confirms intent with the user before running anything that costs Firecrawl credits or writes to Drive.

## How to invoke

```
/ldseo-traffic <client> [period]
```

Examples:

```
/ldseo-traffic melani-the-label
/ldseo-traffic joe-rascal last 30 days
```

## Required reading

`docs/agent/workflows/ga4-traffic-check.md`

## Important constraint

There is no public MCP tool that exposes raw GA4 reads — `create_combined_seo_report` is the only tool that hits GA4. To do a true read-only check you have two paths:

**Option A (not recommended):** run `create_combined_seo_report` with a single dummy crawl. Still spends Firecrawl credits and produces Drive files.

**Option B (preferred):** ask the user whether they actually want the full combined report, or just GA4 numbers — and if just GA4, use `resolve_google_access_subject` to confirm GA4 access is healthy and point them at GA4 Explore directly.

## Hard rules

- Don't auto-run `create_combined_seo_report` for a "quick check" — confirm intent first
- If GA4-only checks become frequent, escalate to add a `ga4_top_landing_pages` tool to `src/seo_automation_mcp/server.py`
