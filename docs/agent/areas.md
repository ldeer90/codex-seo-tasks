# Areas Map

Five linked surfaces feed this automation. Treat them as one mental model.

## 1. Identity surface — who is acting

The MCP server uses one Google service account (`seo-llm-service-account` in project `seo-agency-work`, OAuth client ID `115884595613709396832`) with domain-wide delegation. The service account never acts as itself for GA4 or Drive — it impersonates one of two delegated users:

- `seo@agents.digital` — primary identity for most clients. Has access to the bulk of GA4 properties and the shared `Clients` Drive tree.
- `hello@agents.digital` — owner of the central Drive tree, owns Acorn Rentals and Agents Digital data, and is the default output owner for all created Docs/Sheets.

Both are listed in `GOOGLE_DELEGATED_SUBJECTS`. `GOOGLE_OUTPUT_DELEGATED_SUBJECT=hello@agents.digital` means every Doc and Sheet this server creates is owned by `hello@`, regardless of which subject read GA4. That keeps a single owner managing the report archive.

## 2. Routing layer — `config/site-access.json`

The router (`src/seo_automation_mcp/access_routing.py`) picks the analytics subject in this exact order:

1. `properties.<property_id>` — explicit GA4 property mapping.
2. `hosts.<host>` — website host mapping (with parent-domain fallback).
3. `clients.<client_name>` — case- and whitespace-insensitive client mapping.
4. `default_google_subject` from the JSON, then `GOOGLE_DELEGATED_SUBJECT`.
5. Live fallback: if the mapped subject can't actually read the GA4 property, the server tries the rest of `GOOGLE_DELEGATED_SUBJECTS` in order.

Output subject is independent and resolved from `GOOGLE_OUTPUT_DELEGATED_SUBJECT` first.

When you add a new client, edit `config/site-access.json` first. Without an entry the router falls back to defaults, which works most of the time but is fragile.

## 3. Analytics surface — GA4

15 GA4 stream rows across 11 client groupings. The `seo@` subject reads 10 properties; `hello@` reads 7 (with overlap on Avenue Hampers, Ducati Melbourne, and Joe Rascal). Acorn Rentals (`properties/423383715`) and Agents Digital (`properties/516619587`) are `hello@`-only.

Source of truth: `docs/platform-reference.md`. Per-client GA4 IDs are denormalised into `docs/agent/clients/*.md` for fast lookup.

GA4 reads in `create_combined_seo_report` always pull two date ranges (current + comparison) and pull the top organic landing pages, then audit each one with Firecrawl.

## 4. Output surface — Drive, Docs, Sheets

All client folders sit under one tree, owned by `hello@agents.digital` and shared with `seo@agents.digital`:

```
Agents Digital/
  Business Admin/
    Sales/
  Clients/
    _ CLIENT TEMPLATE/
    Acorn Rentals/
    AVENUE Hampers/
    Joe Rascal/
    Joe Rascal Ducati/
    Joe Rascal Harley/
    Little Shop of Happiness/
    Melani the Label/
    New Client Forms/
    Salad Servers/
    Shop Rongrong/
    TravelKon/
```

`GOOGLE_DRIVE_REPORTS_FOLDER_ID` is the parent folder where all generated Docs and Sheets land. Per-client folder IDs are listed in each client brief if a workflow needs to file the report inside a specific subfolder (current code creates everything in the configured reports folder — moving into a per-client folder is a manual step until that's wired up).

## 5. Project-management surface — Monday.com

35 boards across two workspaces (Agency Ops `2767329`, Main workspace `2556079`). The local `seo-automation` MCP server does not write to Monday, but Codex sessions may have the hosted Monday connector available for board reads and controlled writes. Before creating or updating Monday items, read the board schema, confirm the client context, and include task URLs in the proof block.

The local `MONDAY_API_KEY` only matters when regenerating `docs/platform-reference.md` outside of an MCP host.

Per-client Monday board IDs are denormalised into the client briefs.

## Crawl + scrape surface — Firecrawl

Out-of-process from Google entirely. One API key, one base URL (`https://api.firecrawl.dev/v2`). Conservative defaults:

- `FIRECRAWL_DEFAULT_CRAWL_LIMIT=25`
- `FIRECRAWL_MAX_CRAWL_LIMIT=100`
- `FIRECRAWL_MAX_SCRAPE_URLS=50`
- `FIRECRAWL_CRAWL_TIMEOUT_SECONDS=180`

Auto-excluded paths: admin, wp-admin, login, logout, account, my-account, cart, checkout, payment(s), order(s). `ignoreRobotsTxt` is hard-disabled.

## How the surfaces connect in a combined report

```
client_name + website_url + ga4_property_id
        │
        ▼
GoogleAccessRouter (site-access.json)
        │
        ├── analytics_subject ──► GA4 reports (current + comparison range)
        │                             │
        │                             ▼
        │                        organic landing pages
        │                             │
        │                             ▼
        ▼                        Firecrawl scrape_urls
output_subject ──► Drive create Sheet (combined data)
                  ──► Drive create Doc (narrative report linking the Sheet)
```

The Sheet lives next to the Doc in the configured Drive reports folder, and the Doc links to the Sheet.

## Maintaining the map

- Re-run `generate-platform-reference` after onboarding a client, rotating GA4 access, or restructuring Drive. It refreshes `docs/platform-reference.md`, `docs/platform-inventory.json`, and `docs/monday-mcp-snapshot.json` (when Monday MCP is reachable).
- Update the relevant `docs/agent/clients/*.md` brief by hand when a single client changes (new GA4 property, domain change, Drive folder rename).
