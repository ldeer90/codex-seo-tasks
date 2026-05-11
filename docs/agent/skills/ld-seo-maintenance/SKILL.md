---
name: ld-seo-maintenance
description: Diagnose and clean up SEO operations: SE Ranking hygiene, plan capacity, duplicate projects, access issues, Drive filing, routing, credentials, and platform refreshes.
---

# LD SEO Maintenance

Use this skill for `/ldseo-hygiene`, `/ldseo-troubleshoot`, platform refreshes, Drive filing, and operational diagnostics.

## Required Reading

Choose the smallest workflow that fits:
- SE Ranking hygiene: `docs/agent/workflows/se-ranking-hygiene.md`
- Access troubleshooting: `docs/agent/workflows/troubleshoot-access.md`
- Platform refresh: `docs/agent/workflows/regenerate-platform-reference.md`
- Drive filing: `docs/agent/workflows/report-filing.md`

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md` and `docs/agent/client-memory.md` for client-scoped work: read the client brief, sidecar when present, and client timeline before diagnosis, then append the timeline after completion or after discovering a meaningful blocker. This skill is the handoff target for access, capacity, filing, routing, and platform-state blockers. After the blocker is resolved, return to the originating skill and rerun its preflight before writes.

## Production Rules

- Never delete SE Ranking keywords, projects, Drive files, or Monday items without explicit user confirmation.
- Treat SE Ranking `keyword_count` as keyword-engine pairs.
- Use plan capacity and cache checks before adding keywords.
- Use Drive MCP for folder truth; do not trust service-account folder listings.
- Diagnose access in this order: client route, delegated subject, live permission, config mismatch, stale cache.
- Validate the affected client/platform state again before handing back to the originating workflow.
- Document every cleanup in the affected sidecar, client timeline, or proof block.

## Proof Block

Include projects checked, pair usage, actions proposed or taken, sidecars updated, Drive/Monday state verified, and remaining risks.
