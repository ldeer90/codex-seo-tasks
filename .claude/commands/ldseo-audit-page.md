---
description: Single-page SEO audit — quick read of one URL, no Drive output
argument-hint: <url>
---

# LD SEO — Single Page Audit

Quick read of one URL. No Drive output. Returns title, meta, H1, H2s, word count, canonical, internal links, issues, and recommendations.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **Firecrawl** | Single page scrape and content extraction |
| **MCP server tool** | `extract_page_seo` (wraps Firecrawl + heuristic SEO checks) |

## How to invoke

```
/ldseo-audit-page <url>
```

Examples:

```
/ldseo-audit-page https://melanithelabel.com/collections/gowns
/ldseo-audit-page https://example.com/about
```

## Required reading

`docs/agent/workflows/single-page-audit.md`

## Run

Tool: `extract_page_seo`

Input: `{ "url": "<url>" }`

## What you get back

`PageSEOAudit` dict with: `url`, `status`, `title`, `meta_description`, `h1`, `h2s`, `word_count`, `canonical`, `main_content_summary`, `internal_links`, `issues`, `recommendations`.

## Deliver

Reply with: title (verbatim), meta description (verbatim, in quotes), word count, canonical, count of issues, count of internal links, then bullet the `issues` and `recommendations` lists exactly as returned.

Do not embellish. Do not quote more than 15 words from `main_content_summary`.
