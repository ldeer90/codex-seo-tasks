# SEO Automation Agent

You are running inside Codex CLI with the `seo-automation` MCP server attached. This file is your operating manual. Every other instruction file lives under `docs/agent/`.

## Read order before acting

1. `docs/agent/system.md` — operating rules, identity, guardrails, error handling.
2. `docs/agent/areas.md` — what platforms exist, which subject reads what, where files land.
3. `docs/agent/tools.md` — the MCP tools, their inputs, and example calls.
4. `docs/agent/skills/_index.md` — Codex-native repo-local skill specs for repeatable agent behaviour.
5. `docs/agent/client-memory.md` — client timeline rules for chronological memory, preflight read order, and post-task entries.
6. `docs/agent/clients/<client>.md`, `docs/agent/clients/<client>.json`, and `docs/agent/clients/<client>-timeline.md` — the single source of truth for every client (GA4 ID, website, Drive folder ID, Monday boards, access subject, operational state, chronological memory).
7. `docs/agent/workflows/<task>.md` — step-by-step playbooks for recurring jobs.

If a user request maps to a workflow file, follow that file. Otherwise consult `system.md` and the relevant client brief, then plan from there.

Codex-native skills in `docs/agent/skills/` are canonical. `.claude/commands/` is legacy reference only and should not be used for normal routing unless the user explicitly asks to compare or migrate old Claude Code command behaviour.

## Project at a glance

- Repo: `/Users/laurencedeer/Desktop/SEO Automation`
- Language: Python 3.13, package `seo_automation_mcp`
- Entrypoint: `seo-automation-mcp` (also `python -m seo_automation_mcp.server`)
- Service account: `seo-llm-service-account` in project `seo-agency-work`, OAuth client ID `115884595613709396832`
- Delegated subjects: `seo@agents.digital` (most clients) and `hello@agents.digital` (Acorn Rentals, Agents Digital, plus output ownership)
- Output owner for new Docs/Sheets: `hello@agents.digital`
- Inventory snapshot: `docs/platform-reference.md` (regenerated via `generate-platform-reference`)

## Hard rules

- Never print, log, or echo the contents of `.env`, the service-account JSON, or any API key.
- Never call a write-side tool (`create_*` family) without confirming the client name with the user first.
- Never raise crawl `limit` above `FIRECRAWL_MAX_CRAWL_LIMIT` (default 100). Default to 25 unless the user asks otherwise.
- Never bypass `config/site-access.json`. If a client is missing from that map, stop and ask the user to add it.
- Never edit `docs/platform-reference.md` by hand — regenerate it.
- No workflow is production-ready until it has a passing validator or explicit readback QA, client-presentable output, and a proof block.
- For every client-scoped task, read the client brief, sidecar if present, and client timeline before live work; append a timeline entry after completion or after discovering a meaningful blocker.

## Drive folder checks — always use the Drive MCP

**Never use the service account (`seo@` / `hello@`) to check whether a client Drive folder is empty or to list folder contents.** The service account may return empty results for folders it has access to, producing false "nothing filed" conclusions.

Always check Drive folders via the Google Drive MCP (`mcp__9cfb3b2a-1527-4461-9de2-44d2793f7090__search_files`) using `parentId = '<folder_id>'`. This reads as your personal Google account and returns accurate results.

Example:
```
search_files(query="parentId = '1j_tdnIT0mia1rJz0P2DU4zcs19jpQzS6'")
```

Folder IDs for all clients are in `docs/agent/clients/<client>.md` and in memory (`project_client_folders.md`).

## When in doubt

Ask the user. Routing the wrong subject at a Drive folder produces silent permission errors that look like missing data.
