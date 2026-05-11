---
name: ld-seo-client-onboarding
description: Set up a new SEO client end to end: client sidecar, brief, Drive and Monday structure, GA4 routing, SE Ranking project state, and zero-blocker validation.
---

# LD SEO Client Onboarding

Use this skill for `/ldseo-onboard <client>` and plain-language new-client setup.

## Required Reading

1. `docs/agent/workflows/add-new-client.md`
2. `docs/agent/clients/CLIENT_TEMPLATE.json`
3. `docs/agent/system.md`
4. `docs/agent/areas.md`

## Core Flow

Gather or confirm the client facts, create the client operational state, then validate to zero blockers before any deliverable workflow runs.

Required outputs:
- `docs/agent/clients/<client>.json`
- `docs/agent/clients/<client>.md`
- `docs/agent/clients/<client>-timeline.md`
- `config/site-access.json` route
- Drive client folder and standard subfolders
- Monday board and kickoff tasks when tracked
- SE Ranking project and search engines

## Client Memory

Follow `docs/agent/client-memory.md`. Create the client timeline during onboarding, seed it from confirmed setup facts only, and append the client timeline after validation or after discovering a meaningful onboarding blocker.

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md`. This skill is the entrypoint when another skill is missing client setup. After validation passes, hand off to `ld-seo-collection-seo`, `ld-seo-content-briefs`, `ld-seo-audits-reporting`, or `ld-seo-maintenance` based on the original request.

## Production Rules

- Do not guess GA4, Drive, Monday, or SE Ranking IDs. Confirm them through live reads or explicit user input.
- Use the Google Drive MCP for folder checks.
- Read Monday board/schema before creating items.
- Read back created Drive folders, client docs, and Monday items when live writes occur.
- Never print credentials or API keys.
- Run `python3 scripts/validate_client_json.py --client-json docs/agent/clients/<client>.json`.

## Proof Block

Include access, folders, board, SE Ranking project, sidecar path, timeline path, validator blockers, and readback status.
