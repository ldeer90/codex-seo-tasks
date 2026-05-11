# Monthly Combined SEO Report

Produces one Google Doc (narrative) plus one Google Sheet (data) per client. Uses GA4 organic landing pages from a current period and a comparison period, then audits each landing page with Firecrawl.

## Phase 0 - Access And Input Preflight

Follow `docs/agent/client-memory.md` for client memory.

1. Identify the client. Open `docs/agent/clients/<client>.md`, `docs/agent/clients/<client>.json` when present, and `docs/agent/clients/<client>-timeline.md`; read the GA4 property ID, website URL, access subject, and recent timeline caveats before workflow-specific sources.
2. Confirm date ranges with the user. If they say "last month", propose:
   - `start_date` = first day of last calendar month
   - `end_date` = last day of last calendar month
   - `comparison_start_date`, `comparison_end_date` = same length the prior year
3. Confirm crawl limit. Default 25. Maximum 50 (the combined report uses `min(max_crawl_limit, max_scrape_urls)`).
4. Run `resolve_google_access_subject` with the same inputs and `validate_ga4_access=True`. Show the user the resolved `analytics.subject` and `output.subject`. Stop if they don't match expectation.

### Missing-input routing

Route missing client setup, GA4 property, Drive folder, or site-access route to `ld-seo-client-onboarding`; GA4/Drive/access routing blockers to `ld-seo-maintenance`; follow-up content, metadata, or roadmap recommendations to the relevant LD SEO skill after the report is validated.

## Run

Call `create_combined_seo_report` with:

```json
{
  "client_name": "<from brief>",
  "ga4_property_id": "<from brief, e.g. properties/354478921>",
  "website_url": "<from brief, e.g. https://www.shoprongrong.com>",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "comparison_start_date": "YYYY-MM-DD",
  "comparison_end_date": "YYYY-MM-DD",
  "crawl_limit": 25
}
```

The call can take 1–4 minutes (GA4 + Firecrawl scrape of N landing pages). Don't poll or retry — the server's Firecrawl client already retries with backoff and polls the crawl up to 180s per crawl.

## Verify

Inspect the response:

- `landing_pages_audited` should be > 0. If it's 0, GA4 returned pages whose URLs didn't normalise to scrapeable absolute URLs. Re-run with a corrected `website_url` (matching the canonical the site actually serves).
- `google_subjects.analytics.validated` should be `true`.
- `google_subjects.output.subject` should be `hello@agents.digital`.
- Read back or inspect the created Doc/Sheet before telling the user it is client-ready.

## Client-Presentable QA

Use Codex judgement before delivery:

- Explain what changed, why it matters, and what to do next.
- Avoid presenting GA4 numbers without context or comparison.
- Prioritise recommendations by likely SEO/business impact and effort.
- Call out data caveats: date range, crawl sample size, tracking issues, redirects, or pages skipped.
- Confirm the Doc and Sheet links open and are filed in the expected location.

## Deliver

Reply to the user with:

- Doc URL (`response.doc.url`)
- Sheet URL (`response.sheet.url`)
- Pages audited count
- Top 3 issues by frequency (read from the Sheet column "Issues" — or summarise from the audit rows in `response` if returned).
- Short proof block: date range, GA4 subject, output owner, crawl limit, warnings.
- Client timeline updated with reporting period, Doc/Sheet outputs, readback status, caveats, and next action.

Stop. Do not commentate further unless asked.

## Common failures

- **0 pages audited** — fix `website_url` first.
- **`No configured Google delegated subject can access properties/...`** — that property isn't visible to either delegated subject. Confirm the GA4 ID; if correct, ask the user to grant the delegated user access in GA4 Admin.
- **Firecrawl 402 / credit limit** — the user's Firecrawl plan has run out. Surface the message and stop.
- **Firecrawl 429 after retries** — wait, then re-run with a smaller `crawl_limit`.
