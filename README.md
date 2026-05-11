# SEO Automation MCP

Custom MCP server for SEO reporting workflows that combine:

- GA4 organic landing page data
- Google Drive, Docs, and Sheets report output
- Firecrawl crawling and scraping
- Page-level SEO extraction and recommendations

The v1 approach keeps Firecrawl inside this SEO MCP server so a single tool call can gather analytics, scrape pages, create a supporting Sheet, create a report Doc, and save both in the configured Drive folder.

## Setup

Create a virtual environment and install the package:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Create a local `.env` from `.env.example` and fill in the values:

```bash
cp .env.example .env
```

Required values:

- `FIRECRAWL_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_DELEGATED_SUBJECT` when using Workspace domain-wide delegation
- `GOOGLE_DELEGATED_SUBJECTS` as a comma-separated list when multiple delegated users have different client access
- `GOOGLE_OUTPUT_DELEGATED_SUBJECT` if Docs/Sheets should always be created by a specific delegated user
- `GOOGLE_SITE_ACCESS_MAP` if you want property/client/site routing rules
- `GOOGLE_DRIVE_REPORTS_FOLDER_ID`
- `DEFAULT_GA4_PROPERTY_ID` if you want to omit `ga4_property_id` from tool calls
- `MONDAY_API_KEY` only if regenerating the Monday reference outside an MCP host

Never commit `.env`. If a Firecrawl key has already been shared in chat, rotate it before production use.

## Domain-Wide Delegation

To use the service account as `seo@agents.digital` instead of adding the service account directly to every Analytics property and Drive folder, authorize domain-wide delegation in Google Workspace Admin.

Use this service account OAuth client ID:

```text
115884595613709396832
```

Authorize these OAuth scopes:

```text
https://www.googleapis.com/auth/analytics.readonly,
https://www.googleapis.com/auth/documents,
https://www.googleapis.com/auth/drive,
https://www.googleapis.com/auth/spreadsheets
```

Then set:

```bash
GOOGLE_DELEGATED_SUBJECT=seo@agents.digital
GOOGLE_DELEGATED_SUBJECTS=seo@agents.digital,hello@agents.digital
```

The delegated user still needs access to the GA4 properties and the Drive reports folder.

## Google Access Routing

Some client properties are visible to `seo@agents.digital`, while others are only visible to `hello@agents.digital`. Configure those rules in:

```text
config/site-access.json
```

The combined report workflow chooses the analytics subject in this order:

1. Explicit GA4 property mapping
2. Website host mapping
3. Client name mapping
4. Default delegated subject
5. Live fallback across `GOOGLE_DELEGATED_SUBJECTS` if the mapped user cannot access the GA4 property

Docs and Sheets use `GOOGLE_OUTPUT_DELEGATED_SUBJECT` when set, so report files can be created under the Drive-owning identity while Analytics reads use whichever identity can access the property.

## Run

```bash
seo-automation-mcp
```

Or:

```bash
python -m seo_automation_mcp.server
```

Example MCP client config:

```json
{
  "mcpServers": {
    "seo-automation": {
      "command": "/absolute/path/to/SEO Automation/.venv/bin/python",
      "args": ["-m", "seo_automation_mcp.server"]
    }
  }
}
```

## Tools

- `crawl_site`
- `scrape_url`
- `scrape_urls`
- `extract_page_seo`
- `create_site_audit_sheet`
- `create_firecrawl_seo_audit_doc`
- `create_combined_seo_report`
- `resolve_google_access_subject`

## Platform Reference

Generate a reusable, structure-only reference for future sessions:

```bash
generate-platform-reference
```

This writes:

- `docs/platform-reference.md`
- `docs/platform-inventory.json`
- `docs/monday-mcp-snapshot.json` when Monday inventory is captured through MCP

The generator inventories GA4, Google Drive folder structure, Monday.com workspaces/boards, and remote MCP routing for SE Ranking without exporting Drive file contents, Monday item bodies, private updates, SE Ranking project data, or API keys.

For Monday.com, prefer the hosted monday MCP connector during interactive agent sessions. The local `MONDAY_API_KEY` fallback exists only for non-MCP CLI regeneration. If no token is configured, the generator reuses `docs/monday-mcp-snapshot.json` when present.

For SE Ranking, use the remote MCP server configured in Codex instead of storing an API key in this repo:

```bash
codex mcp add se-ranking --url https://api.seranking.com/mcp
```

The current reference pass records the connector name, URL, status, auth mode, intended SEO use cases, and guardrails. It does not pull project, keyword, competitor, or audit exports unless a future client workflow explicitly asks for that data.

## Guardrails

The server defaults to conservative crawl limits and excludes logged-in or transactional areas such as admin, account, cart, checkout, order, and payment paths. It also keeps `ignoreRobotsTxt` disabled for Firecrawl crawl requests.

The default limits can be adjusted with:

- `FIRECRAWL_DEFAULT_CRAWL_LIMIT`
- `FIRECRAWL_MAX_CRAWL_LIMIT`
- `FIRECRAWL_MAX_SCRAPE_URLS`
- `FIRECRAWL_CRAWL_TIMEOUT_SECONDS`
