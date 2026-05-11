# Session Handover — 2026-05-08 (Monday → Drive filing)

Incoming agent: read this file top-to-bottom before touching anything.
Then read AGENTS.md, docs/agent/system.md, docs/agent/areas.md.

---

## What this session was here to do

1. Fix the Joe Rascal Drive folder ID (one-character typo — lowercase `n` vs uppercase `N`).
2. Set up the Monday MCP server so the next session can scan all boards.
3. Produce a plan to move Monday task attachments/links into the correct Drive folders.

---

## What was completed this session

### Joe Rascal folder ID — fixed

The `CLIENT_FOLDERS` list in `platform_inventory.py` had `14gHf6UZjgZ751CUP6iLz3Sf6WTTQBWSn` (lowercase n). The correct ID confirmed from the Drive URL is `14gHf6UZjgZ751CUP6iLz3Sf6WTTQBWSN` (uppercase N). Fixed at line 978.

`docs/agent/clients/joe-rascal.md` gap notice also updated to reflect that the ID is now correct and a rescan is needed.

### Monday MCP — wired up, needs session restart to activate

Three files created:

**`.claude/monday-mcp.sh`** — wrapper script that:
- Sources `.env` to get `MONDAY_API_KEY`
- Remaps it to `MONDAY_TOKEN` (what `@mondaydotcomorg/monday-api-mcp` expects)
- Execs `npx -y @mondaydotcomorg/monday-api-mcp@latest`

**`.mcp.json`** — registers the `monday` MCP server:
```json
{
  "mcpServers": {
    "monday": {
      "command": "/Users/laurencedeer/Desktop/SEO Automation/.claude/monday-mcp.sh"
    }
  }
}
```

**`.claude/settings.local.json`** — `enableAllProjectMcpServers: true` added so Claude auto-approves on startup.

The MCP is **not yet active in-session** — `.mcp.json` is only read at session start. The next session will have it available.

### Drive subfolder convention — fully documented (from earlier in this session)

All deliverables from the previous handoff (`2026-05-08-drive-folder-mapping.md`) were completed:

- `docs/agent/workflows/report-filing.md` — new convention doc (filing targets, gap registry, GOOGLE_DRIVE_REPORTS_FOLDER_ID recommendation)
- All 11 client briefs updated with `## Drive subfolders` sections
- `docs/client-folder-map.json` written by the scan

---

## Immediate next step — verify Monday MCP is live

At the start of the new session, confirm the server loaded:

```
/mcp
```

You should see `monday` listed with a green status. If it shows an error, check:
1. `.claude/monday-mcp.sh` is executable (`chmod +x` if needed)
2. `npx` path is correct — currently hardcoded to `/Users/laurencedeer/.nvm/versions/node/v22.14.0/bin/npx`. If node version changed, update the script.
3. `.env` is present and contains `MONDAY_API_KEY`

---

## The core task: Monday → Drive filing plan

### What to do

Use the Monday MCP to scan all boards across both workspaces, then produce `docs/monday-drive-filing-plan.md` — a structured plan mapping Monday content to Drive folders.

### Monday workspace context

| Workspace | ID |
|---|---|
| Agency Ops | `2767329` |
| Main workspace | `2556079` |

All 35 boards are documented in `docs/platform-reference.md`. Per-client board IDs are in each `docs/agent/clients/<slug>.md` brief.

### What to extract from Monday

For each task (item) across all boards:

1. **Text updates / comments** — read the full text. Extract any Google Drive links (`drive.google.com/...`). Note what the link points to (doc, sheet, folder) and what the task is about.
2. **File attachments** — collect metadata only: filename, file type, creation date. Do NOT download file content without explicit user permission per file.
3. **Task context** — board name, item name, group name, status column value. This is the signal for which Drive folder the content belongs in.

### Filing logic

Use this decision tree for each piece of content found:

| Content type | Drive destination |
|---|---|
| Monthly SEO report (Doc + Sheet pair) | `07 Reports / SEO Reports` |
| Site audit doc or crawl report | `03 Audits` |
| Keyword research file | `04 Keyword Research` |
| Proposal or pitch deck | `00 Proposals` |
| Onboarding doc | `01 Onboarding` |
| Roadmap or strategy doc | `02 Roadmap` |
| Content brief or copy | `05 Content` |
| Link building plan or outreach | `06 Links` |
| Invoice or payment doc | `08 Invoices` |
| Benchmark / ranking snapshot | `07 Reports / Benchmarks` |
| Unknown / needs review | flag for user |

Resolve the client from the board name. Use the Drive folder IDs in the client briefs (`docs/agent/clients/<slug>.md`).

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

---
```

Group items by client. Within each client, group by board. Flag anything where the recommended folder doesn't have an ID yet (i.e., still shows `pending` in the client brief).

### What the plan does NOT do

- It does not move any files. Moving is a separate step that needs user approval.
- It does not download file content. Only metadata (name, type, size, date).
- It does not create Drive folders. That's still a manual step (see `docs/agent/workflows/report-filing.md`).

---

## State of the Drive subfolder gaps

All 9 scannable active clients are missing `07 Reports / SEO Reports` and `07 Reports / Benchmarks`. These must be created manually in Drive before per-client filing code can be wired up. See `docs/agent/workflows/report-filing.md` for the priority order and step-by-step instructions.

`GOOGLE_DRIVE_REPORTS_FOLDER_ID` is still not set in `.env`. Recommendation: create `_Reports (staging)` inside `Agents Digital / Clients` (`11AdlM1m9kpa3qtJr5RKIyYNUQWUseqb4`) and set that ID as the fallback.

---

## Joe Rascal rescan

Once the filing plan session is done, run the scan again to capture Joe Rascal's subfolders (the typo fix means it will succeed this time):

```bash
cd "/Users/laurencedeer/Desktop/SEO Automation"
.venv/bin/python -m seo_automation_mcp.platform_inventory --client-folders
```

Then update `docs/agent/clients/joe-rascal.md` with the actual subfolder IDs.

---

## Hard constraints (carry forward unchanged)

- Never print, log, or echo `.env`, the service-account JSON, or any API key.
- Never disable robots.txt.
- Never bypass `config/site-access.json`.
- Never modify Drive sharing or permissions. Read and create-in-folder only.
- Never export file contents during scans. Metadata only unless user explicitly approves a specific file download.
- Show diffs to `config/site-access.json` and `.env` before saving.
- Use the smallest tool that satisfies the request.
- Do not run `create_combined_seo_report` or any combined report as a "test".
- Show the full diff to `google_clients.py` and `workflows.py` before shipping the optional per-client filing code change, and wait for explicit approval.
