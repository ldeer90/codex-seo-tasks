# Tool Reference

Nine tools, exposed by `seo-automation` over MCP. All are async unless noted. Source: `src/seo_automation_mcp/server.py`.

---

## `crawl_site`

Crawl a website or section and return Firecrawl page data.

**Inputs**
- `url` (str, required) — start URL.
- `limit` (int, optional) — max pages. Defaults to `FIRECRAWL_DEFAULT_CRAWL_LIMIT` (25). Hard ceiling `FIRECRAWL_MAX_CRAWL_LIMIT` (100).
- `include_paths` (list[str], optional) — regex patterns to include.
- `exclude_paths` (list[str], optional) — regex patterns to exclude. Merged with the default exclusions for admin/cart/checkout/account paths.

**Returns** `{success, id, url, limit, status, total, completed, creditsUsed, data: [page, ...]}`

**Cost** — Firecrawl credits proportional to pages crawled. Polls until complete or 180s timeout.

**Example**
```json
{ "url": "https://www.shoprongrong.com", "limit": 30 }
```

---

## `scrape_url`

Scrape one URL.

**Inputs**
- `url` (str, required)
- `formats` (list[str], optional) — defaults to `["markdown"]`. Common values: `markdown`, `html`, `links`.

**Returns** the raw Firecrawl scrape response.

**Example**
```json
{ "url": "https://www.shoprongrong.com/products", "formats": ["markdown", "html", "links"] }
```

---

## `scrape_urls`

Scrape multiple URLs concurrently (semaphore of 3).

**Inputs**
- `urls` (list[str], required) — max `FIRECRAWL_MAX_SCRAPE_URLS` (50). Always pulls `markdown`, `html`, `links`.

**Returns** `{count, pages: [normalised_page, ...]}`. Per-URL failures are returned in-line with `success: false` rather than aborting the whole call.

**Example**
```json
{ "urls": ["https://example.com/a", "https://example.com/b"] }
```

---

## `extract_page_seo`

Scrape one URL and return parsed SEO fields, issues, and recommendations.

**Inputs**
- `url` (str, required).

**Returns** `PageSEOAudit` as dict: `{url, status, title, meta_description, h1, h2s, word_count, canonical, main_content_summary, internal_links, issues, recommendations}`.

**Example**
```json
{ "url": "https://www.melanithelabel.com/collections/dresses" }
```

---

## `create_site_audit_sheet`

Scrape a list of URLs and write a Google Sheet with one row per URL.

**Inputs**
- `client_name` (str, required) — used for routing and for the Sheet title (`<Client> — Site Audit — YYYY-MM-DD`).
- `urls` (list[str], required).

**Returns** `{client_name, sheet: {id, url, ...}, pages_audited, google_subjects, rows}`.

**Side effects** — creates a Sheet in `GOOGLE_DRIVE_REPORTS_FOLDER_ID`, owned by the output subject (`hello@agents.digital`).

**Example**
```json
{
  "client_name": "Shop Rongrong",
  "urls": [
    "https://www.shoprongrong.com",
    "https://www.shoprongrong.com/about",
    "https://www.shoprongrong.com/products"
  ]
}
```

---

## `create_firecrawl_seo_audit_doc`

Crawl a site, write a crawl Sheet and an SEO audit Doc, return both URLs.

**Inputs**
- `client_name` (str, required).
- `start_url` (str, required).
- `limit` (int, optional) — bounded by `FIRECRAWL_MAX_CRAWL_LIMIT` (100). Defaults to 25.

**Returns** `{client_name, doc, sheet, pages_audited, crawl_id, google_subjects}`.

**Side effects** — creates two Drive files in the reports folder.

**Example**
```json
{
  "client_name": "Avenue Hampers",
  "start_url": "https://www.avenuehampers.com.au",
  "limit": 50
}
```

---

## `resolve_google_access_subject` (sync)

Show which delegated subject will read GA4 and which will own outputs. Use this *before* any combined report.

**Inputs**
- `client_name` (str, optional).
- `website_url` (str, optional).
- `ga4_property_id` (str, optional) — accepts `properties/123` or `123`.
- `validate_ga4_access` (bool, default `True`) — when true, the server actually calls GA4 with each candidate subject and returns the first one that succeeds.

**Returns** `{analytics: {subject, source, key, validated}, output: {subject, source, key}, candidates: [...]}`. `source` is one of `property`, `host`, `client`, `default`.

**Example**
```json
{ "client_name": "Acorn Rentals", "ga4_property_id": "properties/423383715" }
```

---

## `ga4_collection_opportunities` (sync)

Read-only GA4 collection prioritisation. Pulls organic landing pages under a collection path, merges top pages by sessions and revenue, compares against a prior period, and ranks collections for SEO action.

**Inputs**
- `client_name` (str, required).
- `ga4_property_id` (str | null, required) — `null` falls back to `DEFAULT_GA4_PROPERTY_ID`.
- `website_url` (str, required) — used to build absolute collection URLs from GA4 landing-page paths.
- `start_date`, `end_date` (str, required) — ISO `YYYY-MM-DD` for the current period.
- `comparison_start_date`, `comparison_end_date` (str, required) — prior period for decline/rescue scoring.
- `channel` (str, default `Organic Search`).
- `path_prefix` (str, default `/collections/`) — change only for non-Shopify category structures.
- `limit` (int, default `100`) — max ranked opportunities returned. The tool reads at least 250 rows per GA4 ordering internally so both traffic-led and revenue-led collections can surface.

**Returns** `{client_name, ga4_property_id, website_url, date_range, comparison_date_range, channel, source_limit_per_ordering, count, path_prefix, totals, opportunities, google_subjects}`.

Each opportunity includes `{slug, url, priority_bucket, priority_score, current, comparison, delta, notes}`. Priority buckets include `Protect / Rescue`, `Protect`, `Grow`, `Monetise`, `Rescue`, and `Build / Validate`.

**Side effects** — none. No Firecrawl credits, no Drive files.

**Example**
```json
{
  "client_name": "Avenue Hampers",
  "ga4_property_id": "properties/356217618",
  "website_url": "https://www.avenuehampers.com.au",
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "comparison_start_date": "2025-04-01",
  "comparison_end_date": "2025-04-30",
  "limit": 30
}
```

---

## `create_combined_seo_report`

The big one: GA4 organic landing pages (current + comparison ranges) + per-page Firecrawl audit + a narrative Doc that links to the supporting Sheet.

**Inputs**
- `client_name` (str, required).
- `ga4_property_id` (str | null, required) — `null` falls back to `DEFAULT_GA4_PROPERTY_ID`.
- `website_url` (str, required) — used to convert relative landing-page paths from GA4 into absolute URLs to scrape.
- `start_date`, `end_date` (str, required) — ISO `YYYY-MM-DD` for the current period.
- `comparison_start_date`, `comparison_end_date` (str, required) — for the prior period.
- `crawl_limit` (int, optional) — bounded by `min(FIRECRAWL_MAX_CRAWL_LIMIT, FIRECRAWL_MAX_SCRAPE_URLS)` = 50. Defaults to 25.

**Returns** `{client_name, doc: {id, url, ...}, sheet: {id, url, ...}, ga4_property_id, landing_pages_audited, google_subjects: {analytics, output}}`.

**Side effects** — Drive Sheet and Doc, both owned by `hello@agents.digital`.

**Example**
```json
{
  "client_name": "Joe Rascal Harley",
  "ga4_property_id": "properties/513354197",
  "website_url": "https://www.joerascalharley.com.au",
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "comparison_start_date": "2025-04-01",
  "comparison_end_date": "2025-04-30",
  "crawl_limit": 30
}
```

---

## What no tool does

- The local `seo-automation` MCP server does not write to GA4.
- The local `seo-automation` MCP server does not modify Drive sharing.
- The local `seo-automation` MCP server does not write to Monday.com; Codex app sessions may have a separate Monday connector for controlled board/item writes.
- Does not log in or scrape authenticated pages — admin/cart/checkout/account are excluded from crawls.
- Does not bypass `robots.txt`.
