# Codex CLI setup

This MCP server runs locally over stdio. Codex CLI launches it on demand.

## 1. Install Codex CLI

If not already installed:

```bash
brew install codex          # if available, or
npm i -g @openai/codex      # current cross-platform path
```

Verify:

```bash
codex --version
```

## 2. Add the MCP server to `~/.codex/config.toml`

Open or create `~/.codex/config.toml` and add:

```toml
[mcp_servers.seo-automation]
command = "/Users/laurencedeer/Desktop/SEO Automation/.venv/bin/python"
args = ["-m", "seo_automation_mcp.server"]
# Codex inherits the parent shell env. The .env in the repo is loaded
# automatically by the server because Settings.from_env() calls load_dotenv().
# If Codex is launched from a different cwd, set the cwd explicitly:
cwd = "/Users/laurencedeer/Desktop/SEO Automation"
```

If you have multiple MCP servers, each goes under its own `[mcp_servers.<name>]` table.

## 3. Project-level instructions

Codex auto-loads `AGENTS.md` from the project root. The root `AGENTS.md` in this repo points at `docs/agent/`. No extra wiring needed.

You can also add a global `~/.codex/AGENTS.md` for cross-project rules.

## 4. Smoke test inside Codex

Launch Codex in the repo:

```bash
cd "/Users/laurencedeer/Desktop/SEO Automation"
codex
```

Then ask:

> List the MCP tools you can see from `seo-automation`.

Expected: `crawl_site`, `scrape_url`, `scrape_urls`, `extract_page_seo`, `create_site_audit_sheet`, `create_firecrawl_seo_audit_doc`, `resolve_google_access_subject`, `ga4_collection_opportunities`, `create_combined_seo_report`.

Then:

> Resolve the Google access subject for client "shop rongrong".

Expected: `analytics.subject = seo@agents.digital`, `output.subject = hello@agents.digital`, source `client`.

## 5. Common failure modes

- **`FIRECRAWL_API_KEY is required`** — fill in `.env`. The server only reads it on first crawl/scrape call, so the boot will succeed without it.
- **`GOOGLE_DRIVE_REPORTS_FOLDER_ID is required`** — fill in `.env` before any `create_*` call.
- **`No configured Google delegated subject can access properties/...`** — that property isn't visible to either subject. Add the service account or grant the delegated user access in GA4 Admin.
- **MCP server doesn't appear in Codex** — check `~/.codex/config.toml` syntax (TOML is strict about quoting paths with spaces) and run `codex --debug` to see launch errors.
