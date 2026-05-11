# Regenerate Platform Reference

Refreshes `docs/platform-reference.md`, `docs/platform-inventory.json`, and `docs/monday-mcp-snapshot.json` (when Monday MCP is reachable).

## When to run

- A client is added or removed.
- A GA4 property is added, transferred, or its access changes.
- The Drive `Clients` tree is restructured.
- Monday boards are added, archived, or moved between workspaces.

Do **not** run this on every report — it spends GA4 and Drive list quota and is structural metadata, not operational data.

## Run

```bash
cd "/Users/laurencedeer/Desktop/SEO Automation"
.venv/bin/generate-platform-reference
```

Or:

```bash
.venv/bin/python -m seo_automation_mcp.platform_inventory
```

## What it does

- Walks every delegated subject in `GOOGLE_DELEGATED_SUBJECTS` and inventories the GA4 properties + streams it can see.
- Walks each subject's My Drive top-level folders and Shared-With-Me roots, recursing for folder structure (no file contents).
- Pulls Monday workspaces and boards via the hosted Monday MCP if available, falling back to `MONDAY_API_KEY`, falling back to the cached `docs/monday-mcp-snapshot.json`.
- Emits structure-only output. No file contents, no Monday item bodies, no API keys.

## Verify

After the run, check:

- Top of `docs/platform-reference.md` shows the current ISO timestamp.
- The "Cross-Platform Client Map" table at the bottom matches the clients you expect.
- The "Unmatched Structure Names" section is empty (or reflects only known orphans).

## Update agent docs

If the run reveals new or renamed clients, update:

- `config/site-access.json` (add the new client/property/host)
- `docs/agent/clients/<client>.md` (new brief or edit existing)
- `docs/agent/clients/_index.md` (table)
