---
description: Onboard a new client — gather facts, grant access, create sidecar from template, validate
argument-hint: <client-slug>
---

# LD SEO — Onboard New Client

End-to-end onboarding so the MCP server, routing, agent docs, and client JSON sidecar all know about the client.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **GA4 Admin (manual)** | Property Access Management — add delegated subject as Viewer |
| **Google Drive MCP** | `search_files`, `create_file` (folders), `get_file_metadata` |
| **Monday MCP** | `list_workspaces`, `create_board`, `create_item`, `get_board_info` |
| **SE Ranking Project API** | `PROJECT_createProject`, `PROJECT_addSearchEngine` |
| **MCP server tool** | `resolve_google_access_subject(validate_ga4_access=True)` |
| **Local scripts** | `validate_client_json.py` (zero blockers before onboarding is complete) |
| **Files written** | `docs/agent/clients/<slug>.json`, `docs/agent/clients/<slug>.md`, `config/site-access.json` |

## How to invoke

```
/ldseo-onboard <client-slug>
```

Example:

```
/ldseo-onboard new-client-name
```

## Required reading

`docs/agent/workflows/add-new-client.md`

## Pre-flight — gather facts from the user

Ask for:

- **Client name** (canonical form — what you'd write on a report)
- **Brand display name** (typographically correct, e.g. `MÉLANI`, `aje.`)
- **Website URL**
- **Market scope** (`AU`, `US`, `AU+US`)
- **GA4 property ID** (numeric or `properties/<id>` form)
- **Drive folder name** (most often a new folder under `Agents Digital / Clients`)
- **Monday workspace + board** (if SEO work is tracked there)
- **Delegated subject** for Google access (`seo@` or `hello@`)
- **Brand voice paragraph** — register, positioning, what good copy sounds like vs bad
- **Tone direction** — one or two sentences of writer guidance
- **USP** — primary customer-facing benefit, factual

## Steps

1. Grant Google access (GA4 Viewer + Drive Editor for the delegated subject)
2. Update `config/site-access.json` with the new client routing
3. **Create Drive client folder** under `Agents Digital / Clients` (parent ID `11AdlM1m9kpa3qtJr5RKIyYNUQWUseqb4`)
4. **Create the standard subfolder structure** inside the client folder (see "Standard Drive subfolders" below). Record every subfolder ID in the sidecar's `drive.folders` block.
5. **Create Monday board** in the right workspace; record `board_id` and `workspace_id`
6. **Seed the Monday board with the standard first-month kickoff tasks** (see "Standard first-month Monday tasks" below). Record `groups.current_month` after `get_board_info`.
7. Create `docs/agent/clients/<slug>.md` (brief)
8. Create `docs/agent/clients/<slug>.json` from `docs/agent/clients/CLIENT_TEMPLATE.json` — fill every REQUIRED field, including all created Drive folder IDs and the Monday board/workspace IDs from steps 3–6
9. Create SE Ranking project; record `project_id` and `engines.AU` (and `US` if scope includes US) in the sidecar
10. Run validator:

```bash
python3 scripts/validate_client_json.py --client-json docs/agent/clients/<slug>.json
```

11. Re-validate with zero blockers before proceeding to any deliverable workflow

## Standard Drive subfolders

Every new client folder MUST contain these nine subfolders, created in this order. Record each ID in the sidecar's `drive.folders` block.

| # | Folder name | Sidecar key |
|---|---|---|
| 00 | `00 Proposals` | `00_proposals` |
| 01 | `01 Onboarding` | `01_onboarding` |
| 02 | `02 Roadmap` | `02_roadmap` |
| 03 | `03 Audits` | `03_audits` |
| 04 | `04 Keyword Research` | `04_keyword_research` |
| 05 | `05 Content` | `05_content` |
| 06 | `06 Links` | `06_links` |
| 07 | `07 Reports` | `07_reports` |
| 08 | `08 Invoices` | `08_invoices` |

These are created with `mcp__9cfb3b2a-...__create_file` (mimeType `application/vnd.google-apps.folder`, parentId = client folder ID). Do not skip any — downstream workflows file deliverables by exact folder name.

## Standard first-month Monday tasks

Every new board MUST be seeded with these four kickoff items, in this order, against the board's default group. This matches the established AVENUE Hampers template — keep names verbatim. Create via `mcp__monday__create_item`.

| # | Task name | Maps to skill |
|---|---|---|
| 1 | `Audits` | `/ldseo-audit-site` |
| 2 | `Benchmarking` | `/ldseo-monthly-report` (first run = baseline) |
| 3 | `Keyword Research` | `/ldseo-keyword-research` |
| 4 | `Roadmap Creation` | (manual — strategist deliverable) |

Reference: AVENUE Hampers board `5026978865` items `2614130528`, `2614130529`, `2614025540`, `2614025541` (created 2026-03-04). For publisher / non-Shopify clients the names stay the same — only the workflows behind them differ. Note any deviation in the sidecar's `qa.field_sources`.

## Hard rules

- Zero validator blockers before recording the client as onboarded
- Brand voice and tone direction MUST be filled — fall-back to generic guidance produces freelancer-quality copy, not brand copy
- All nine Drive subfolders MUST exist and be recorded in the sidecar before any deliverable workflow runs (`/ldseo-audit-site` files into `03 Audits`, `/ldseo-content` into `05 Content`, etc.)
- All four first-month Monday tasks (Audits, Benchmarking, Keyword Research, Roadmap Creation) MUST be created before the board is considered ready
- Confirm Drive folder ID with a live Drive read, not assumption
- Document the onboarding date and the source of each field in the sidecar's `qa` block
