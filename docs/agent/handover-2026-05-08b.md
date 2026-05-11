# Session Handover — 2026-05-08 (Monday MCP fix → Drive filing plan)

Incoming agent: read this file, then AGENTS.md, docs/agent/system.md, docs/agent/areas.md.

---

## What this session did

Fixed the Monday MCP so it will load on next session start. Previous session wrote the
config files but the MCP was still broken due to a missing peer dependency.

### Root cause

`npx -y @mondaydotcomorg/monday-api-mcp@latest` crashes immediately with:

```
Error: Cannot find module 'exceljs'
```

`npx` doesn't install peer dependencies, so `exceljs` was always missing.

### What was fixed

| File | Change |
|---|---|
| `.claude/monday-mcp-server/package.json` | New — local npm project pinning `monday-api-mcp` + `exceljs` |
| `.claude/monday-mcp-server/node_modules/` | Fully installed — do not delete |
| `.claude/monday-mcp.sh` | Changed from `exec npx …` to `exec node .../index.js` from the local install |
| `.claude/settings.local.json` | Added `"enableAllProjectMcpServers": true` (was never written by previous session) |

### Verified working

A manual MCP handshake (JSON-RPC `initialize`) returned a valid response from the server.
The Monday API key also returned HTTP 200 against `api.monday.com/v2`. Both are good.

---

## Immediate first step

**Restart the session**, then run `/mcp`. You should see `monday` listed with a green status.

If it shows an error:
1. Check `.claude/monday-mcp.sh` is executable: `chmod +x ".claude/monday-mcp.sh"`
2. Confirm node is still at `/Users/laurencedeer/.nvm/versions/node/v22.14.0/bin/node`
   (if the nvm version changed, update the path in both `monday-mcp.sh` and re-run `npm install` in `.claude/monday-mcp-server/`)
3. Confirm `.env` still contains `MONDAY_API_KEY`

---

## The core task: Monday → Drive filing plan

Once the MCP is confirmed live, produce `docs/monday-drive-filing-plan.md`.

### What to do

Use the Monday MCP to scan all 35 boards across both workspaces, then map every item that
contains a Google Drive link or file attachment to the correct Drive subfolder.

### Monday workspace IDs

| Workspace | ID |
|---|---|
| Agency Ops | `2767329` |
| Main workspace | `2556079` |

All 35 boards are in `docs/platform-reference.md`. Per-client board IDs are in each
`docs/agent/clients/<slug>.md`.

### What to extract per item

1. **Text updates / comments** — extract any `drive.google.com/…` links. Note what the link
   points to and what the task is about.
2. **File attachments** — metadata only: filename, type, size, date. Do NOT download content.
3. **Task context** — board name, item name, group name, status column value.

### Filing decision tree

| Content type | Drive subfolder |
|---|---|
| Monthly SEO report (Doc + Sheet pair) | `07 Reports/SEO Reports` |
| Site audit or crawl report | `03 Audits` |
| Keyword research file | `04 Keyword Research` |
| Proposal or pitch deck | `00 Proposals` |
| Onboarding doc | `01 Onboarding` |
| Roadmap or strategy doc | `02 Roadmap` |
| Content brief or copy | `05 Content` |
| Link building plan or outreach | `06 Links` |
| Invoice or payment doc | `08 Invoices` |
| Benchmark / ranking snapshot | `07 Reports/Benchmarks` |
| Unknown | flag for user |

Resolve the client from the board name. Drive folder IDs are in each client brief.

### Output format for `docs/monday-drive-filing-plan.md`

```markdown
# Monday → Drive Filing Plan
Generated: <date>

## Summary
- X boards scanned
- X items with Drive links
- X items with file attachments
- X items flagged for review

---

## <Client Name>

### Board: <Board Name> (<board_id>)

#### Item: <Item Name>
- **Status:** <status>
- **Drive links found in comments:**
  - [Link text](url) — type: Doc/Sheet/Folder — recommended target: `03 Audits` (<folder_id>)
- **File attachments:**
  - `filename.pdf` (PDF, 2.3 MB, created 2026-03-12) — recommended target: `03 Audits` (<folder_id>)
- **Action:** already in correct folder / needs moving / needs review
```

Group by client, then by board. Flag items where the recommended subfolder ID is still
`pending` in the client brief.

### What the plan must NOT do

- Must not move any files. Moving is a separate step requiring user approval.
- Must not download file content. Metadata only.
- Must not create Drive folders.

---

## Drive subfolder gap (carry forward)

All 9 active clients are missing `07 Reports/SEO Reports` and `07 Reports/Benchmarks`.
These must be created manually in Drive before per-client filing code can be wired up.
See `docs/agent/workflows/report-filing.md` for the priority order.

`GOOGLE_DRIVE_REPORTS_FOLDER_ID` is still unset in `.env`. Recommended: create
`_Reports (staging)` inside `Agents Digital/Clients` (`11AdlM1m9kpa3qtJr5RKIyYNUQWUseqb4`)
and set that ID as the fallback.

---

## Joe Rascal rescan (still pending)

The folder ID typo was fixed in a previous session. Run this once the filing plan is done
to capture Joe Rascal's actual subfolders:

```bash
cd "/Users/laurencedeer/Desktop/SEO Automation"
.venv/bin/python -m seo_automation_mcp.platform_inventory --client-folders
```

Then update `docs/agent/clients/joe-rascal.md` with the real subfolder IDs.

---

## Hard constraints (unchanged)

- Never print, log, or echo `.env`, the service-account JSON, or any API key.
- Never disable robots.txt.
- Never bypass `config/site-access.json`.
- Never modify Drive sharing or permissions. Read and create-in-folder only.
- Never export file contents during scans. Metadata only unless user approves a specific file.
- Show diffs to `config/site-access.json` and `.env` before saving.
- Use the smallest tool that satisfies the request.
- Do not run `create_combined_seo_report` as a test.
- Show full diffs to `google_clients.py` and `workflows.py` before shipping any per-client
  filing code change, and wait for explicit approval.
