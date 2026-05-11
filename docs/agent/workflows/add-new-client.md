# Add a New Client

End-to-end onboarding so the MCP server, routing, and agent docs all know about the client.

## 1. Gather facts

Ask the user for:

- Client name (the canonical form — what you'd write on a report).
- Website URL.
- GA4 property ID (numeric or `properties/<id>` form).
- Drive folder name (most often a new folder under `Agents Digital / Clients`).
- Monday workspace + board (if SEO work will be tracked).
- Which delegated subject should read this property (`seo@` or `hello@`)?

## 2. Grant Google access

Either:

- Add the delegated user to the GA4 property in GA4 Admin → Property Access Management with at least Viewer.
- Add the same user to the Drive folder with at least Editor (so it can create files).

The service account itself does not need direct access — domain-wide delegation handles impersonation.

## 3. Update `config/site-access.json`

Show the user the diff before saving. Add a `clients` entry, and if the property is unambiguous, also a `properties` entry as a safety net:

```json
{
  "clients": {
    "...": "...",
    "new client name": "seo@agents.digital"
  },
  "properties": {
    "...": "...",
    "properties/123456789": "seo@agents.digital"
  }
}
```

## 4. Sanity check the routing

```json
// resolve_google_access_subject
{ "client_name": "New Client Name", "ga4_property_id": "properties/123456789", "validate_ga4_access": true }
```

Confirm `analytics.subject` is what you expect and `analytics.validated` is `true`.

## 5. Add the client brief

Create `docs/agent/clients/<slug>.md` modelled on an existing brief. Include:

- Routing block (subjects + source)
- GA4 block (property ID, account, web stream)
- Web URL
- Drive folder name + ID
- Monday board + subitems board
- Notes

Add a row to `docs/agent/clients/_index.md`.

## 5a. Create the client timeline

Create `docs/agent/clients/<slug>-timeline.md` from `docs/agent/clients/CLIENT_TIMELINE_TEMPLATE.md`.

The first entry must record onboarding request/source, confirmed access facts, created or confirmed Drive folders and Monday board, sidecar and brief paths, validation blockers or warnings, and next action.

Follow `docs/agent/client-memory.md`. Do not backfill anything that was not confirmed during onboarding.

## 6. Regenerate the platform reference

Follow [regenerate-platform-reference.md](regenerate-platform-reference.md). Confirm the new client appears in the cross-platform map.

## 7. Test with the smallest tool first

Before any combined report, run `extract_page_seo` on the homepage to confirm Firecrawl reaches the site and the parser is happy. Then a 5-page `crawl_site`. Then graduate to a full combined report.

Append the client timeline after the smoke test or after any onboarding blocker, with the proof summary and next action.
