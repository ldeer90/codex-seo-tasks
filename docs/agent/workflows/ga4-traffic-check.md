# GA4 Traffic Check

Quick GA4 organic-landing-page read for a client. No Firecrawl, no Drive output.

## Phase 0 - Access And Input Preflight

- Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.
- Confirm the client sidecar/brief exists and includes GA4 property, website URL, and access subject.
- Confirm whether the user wants a read-only GA4 view, collection prioritisation, or a delivered monthly report.

### Missing-input routing

Route missing client setup, GA4 property, or site-access route to `ld-seo-client-onboarding`; GA4 access/routing failures to `ld-seo-maintenance`; report requests to `monthly-combined-report.md`.

## Collection Priority Check

Use `ga4_collection_opportunities` when the user asks which Shopify collections to prioritise, which collection sidecars to build first, or how to infer high-priority collections from traffic/revenue.

Call it with:

```json
{
  "client_name": "<canonical client>",
  "ga4_property_id": "properties/<id>",
  "website_url": "https://www.example.com",
  "start_date": "<current YYYY-MM-DD>",
  "end_date": "<current YYYY-MM-DD>",
  "comparison_start_date": "<comparison YYYY-MM-DD>",
  "comparison_end_date": "<comparison YYYY-MM-DD>",
  "channel": "Organic Search",
  "path_prefix": "/collections/",
  "limit": 50
}
```

Use the output this way:

- `Protect / Rescue`: existing commercial collection with revenue/conversions and decline. Refresh copy, internal links, metadata, merchandising, and monitoring first.
- `Protect`: high-value collection already earning. Keep it stable, improve cautiously, and add internal links from related pages.
- `Grow`: traffic and commercial signal both exist. Build briefs/copy and link support next.
- `Monetise`: organic traffic exists but revenue/conversions are weak or absent. Review intent, product match, merchandising, and collection copy.
- `Rescue`: traffic has declined without current commercial signal. Investigate before assigning writing budget.
- `Build / Validate`: low signal. Use SE Ranking/GSC/merchandising evidence before prioritising.

The tool merges two GA4 reads per period: top collections by sessions and top collections by revenue. This prevents low-revenue traffic pages and lower-traffic revenue pages from hiding each other.

## General Traffic Check

For a non-collection GA4 traffic look, use `resolve_google_access_subject` to validate access, then either:

- use `ga4_collection_opportunities` with a category-specific `path_prefix` if the request is still path-scoped; or
- add a dedicated `ga4_top_landing_pages` read-only tool before making recurring non-collection traffic checks.

Do not run `create_combined_seo_report` just to answer a GA4-only question. It spends Firecrawl credits and creates Drive files.

## Quality Gate

- Do not spend Firecrawl credits or create Drive files when the user only asked for GA4 numbers.
- Use matching date ranges and say exactly which period is current and which is comparison.
- Treat GA4 revenue and traffic as prioritisation evidence, not final editorial instruction. Sidecar creation still needs product reality, keyword intent, SERP review, and internal-link context.

## Proof Block

Report client, GA4 property, resolved analytics subject, date ranges, channel, path prefix, returned opportunity count, top priority buckets, next recommended workflow, and client timeline update status.
