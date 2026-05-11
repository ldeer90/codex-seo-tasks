# Handoff — Map per-client Drive folders for report filing

**Date:** 2026-05-08
**Repo:** `/Users/laurencedeer/Desktop/SEO Automation`
**Author of this handoff:** previous session that built the MCP server and agent docs

Paste this whole file as the first message of a new Codex session, or open it inside Codex with the repo as the working directory.

---

## What you're inheriting

A working SEO Automation MCP server with:

- 8 tools wired up (`crawl_site`, `scrape_url`, `scrape_urls`, `extract_page_seo`, `create_site_audit_sheet`, `create_firecrawl_seo_audit_doc`, `create_combined_seo_report`, `resolve_google_access_subject`).
- Domain-wide delegation across two subjects: `seo@agents.digital` (most clients) and `hello@agents.digital` (Acorn Rentals, Agents Digital, output owner for everything).
- Agent docs under `docs/agent/` — start with `AGENTS.md` at the repo root, then `docs/agent/system.md`, `areas.md`, `tools.md`, `clients/`, `workflows/`.
- A structure-only inventory at `docs/platform-reference.md` (regenerable via `generate-platform-reference`).

`.env` is filled in **except** `GOOGLE_DRIVE_REPORTS_FOLDER_ID`, which is intentionally left empty until this session decides where reports should land.

The server today writes every Doc and Sheet into one Drive folder regardless of client. That's the gap this session is here to close.

## Your job

Walk every per-client folder under `Agents Digital / Clients`, document the subfolder structure, then propose where each report type should be filed. Update agent docs and (optionally) extend the code so future report writes land in the right place.

## Concrete deliverables

1. **Per-client folder map** — for each of the 11 clients in `docs/agent/clients/_index.md`, the immediate subfolders and one level deeper. Folder names + IDs only. No file contents.
2. **Filing convention** — a new `docs/agent/workflows/report-filing.md` describing where each report type should land. Cross-client conventions if they exist; per-client overrides where they don't.
3. **Per-brief updates** — every `docs/agent/clients/<slug>.md` gains a "Drive subfolders" section with the relevant IDs.
4. **Decision on `GOOGLE_DRIVE_REPORTS_FOLDER_ID`** — pick a default folder that's safe even before the per-client filing code lands, and explain the choice. Don't paste secrets into chat.
5. **Optional** — if filing-by-client should be enforced going forward, scope the code change in `src/seo_automation_mcp/workflows.py` and `src/seo_automation_mcp/google_clients.py`. Don't ship it without confirming with the user.

## Folders to scan

Parent `Clients` folder ID: `11AdlM1m9kpa3qtJr5RKIyYNUQWUseqb4` (under `Agents Digital`, `1ZpzgOmzDHmb01ebq_N0lejCI74r3s1jd`).

| Client | Folder ID | Read with |
|---|---|---|
| _ CLIENT TEMPLATE | `1NSxmr_AUHoweWrFfKotEvBiJ88zdwOPZ` | seo@ or hello@ |
| Acorn Rentals | `1M2MXfkRFsAMy5nFoM2m7miNOnjBEkvoj` | hello@ (also seo@) |
| AVENUE Hampers | `1LGXJQosWUROG5s4MVxbNaFgMvXFd90en` | seo@ or hello@ |
| Joe Rascal | `14gHf6UZjgZ751CUP6iLz3Sf6WTTQBWSN` | seo@ or hello@ |
| Joe Rascal Ducati | `157-ddATrb2byi0VMJYKg9JET4RzqIFFr` | seo@ or hello@ |
| Joe Rascal Harley | `1XENbhUku8qau7HM5I7D9ivtIhrKpfU0s` | seo@ or hello@ |
| Little Shop of Happiness | `1wN3HSAcKrkXRLxuFA0OlHyGDqLDo9hx7` | seo@ or hello@ |
| Melani the Label | `1HWLcsHS38P5u_d_vfrWux3LaRVln9iMJ` | seo@ or hello@ |
| New Client Forms | `1eFoEqwgMyuWyMbQuOZZAzK4xtfQTB7Ao` | seo@ or hello@ |
| Salad Servers | `1VTJy6FaSqLkOyRxaf7ZiAQuoIQVXatyf` | seo@ or hello@ |
| Shop Rongrong | `1TTxwqCl5JurXCyva9kGK9rz5v66YzaXU` | seo@ or hello@ |
| TravelKon | `175zcM_g56_jtpU1m9bzAMFvLFahXAqS3` | seo@ or hello@ |

Scan the `_ CLIENT TEMPLATE` folder first — it should reveal the canonical layout new clients are supposed to follow. Use that as the baseline and document drift in the per-client briefs.

## How to do the scan

The MCP server has no `list_drive_folder` tool yet. Pick one path:

**Path A — Extend `platform_inventory.py` (recommended for one-shot mapping).**
That module already walks Drive structure for the top-level inventory. Add a function (or a CLI flag like `generate-platform-reference --client-folders`) that recurses 1–2 levels into each client folder ID and emits structure-only JSON. Reuse `_walk_drive_folder` style logic. Don't pull file contents.

**Path B — Add a `list_drive_folder` MCP tool (recommended if filing should be adaptive long-term).**
Add `GoogleWorkspaceClient.list_folder(folder_id, *, page_size=200)` that returns `[{id, name, mimeType, parents}]` and a thin `@mcp.tool()` wrapper in `server.py`. Then call it from inside Codex 11 times. Add the new tool to `docs/agent/tools.md`.

Either way: read the existing `GoogleWorkspaceClient` in `src/seo_automation_mcp/google_clients.py` to see how the Drive client is built (delegated subject, scopes, error handling) — match those conventions.

For both paths, query as `seo@agents.digital` first; if that returns 404 on a folder, retry as `hello@`. The `Clients` tree is owned by `hello@` and shared with `seo@`, so both should generally work.

## Output format for the map

For each client, produce a section like this. Folder names and IDs only — no document titles.

```
### Shop Rongrong  (1TTxwqCl5JurXCyva9kGK9rz5v66YzaXU)

Subfolders (level 1):
- <Folder Name>  (<id>)
  - <Subfolder Name>  (<id>)
  - ...

Filing recommendation:
- create_combined_seo_report  -> <folder name>  (<id>)
- create_firecrawl_seo_audit_doc -> <folder name>  (<id>)
- create_site_audit_sheet -> <folder name>  (<id>)
```

If a client is missing the expected subfolder, note it as a gap and recommend whether to create the folder, file at the parent, or use a sibling.

## Questions to resolve with the user before writing the convention

1. **Per-client vs central filing.** Should reports live inside each client folder, or stay in one central reports folder with per-client filename prefixes? (Current code = central. Proposal will likely flip this.)
2. **Time bucketing.** By year? Year/quarter? Year/month? Flat with the date in the filename (current behaviour — see `dated_title()` in `src/seo_automation_mcp/google_clients.py`)?
3. **Folder auto-creation.** If the target subfolder doesn't exist, should the MCP create it on the fly or fail loudly? Auto-create can drift; failing loud forces a manual decision.
4. **Template enforcement.** Should the `_ CLIENT TEMPLATE` layout be applied retroactively to existing clients, or only to new ones?

Ask these in chat before changing anything in `config/site-access.json` or shipping code.

## Hard constraints (carry these from the previous session)

- Never print, log, or echo `.env`, the service-account JSON, or any API key.
- Don't disable robots.txt.
- Don't bypass `config/site-access.json` — if the routing doesn't already cover a folder you're touching, ask.
- Don't modify Drive sharing or permissions. Read and create-in-folder only.
- Don't export file contents during the scan. Folder structure only.
- Show diffs to `config/site-access.json` and `.env` before saving.
- Use the smallest tool that satisfies the request. Don't run combined reports as a "test".

## Smoke test before you start

```bash
cd "/Users/laurencedeer/Desktop/SEO Automation"
.venv/bin/pytest -q
.venv/bin/python -c "from seo_automation_mcp.config import Settings; s=Settings.from_env(); print('firecrawl:', bool(s.firecrawl_api_key), 'monday:', bool(s.monday_api_key), 'drive_folder:', bool(s.google_drive_reports_folder_id))"
```

Expected: tests pass, firecrawl=True, monday=True, drive_folder=False (the gap you're closing).

If the user mentions Firecrawl or Monday keys were already in chat history, recommend rotating them before any production run.

## When you're done

End by giving the user:

- A link to the new `docs/agent/workflows/report-filing.md`.
- A summary of which clients matched the template and which drifted.
- The `GOOGLE_DRIVE_REPORTS_FOLDER_ID` value to paste into `.env` (or a recommendation to create a new folder and the steps to do so).
- A short list of follow-ups: any client folders that need cleanup, any code changes needed to make filing-by-client real.
