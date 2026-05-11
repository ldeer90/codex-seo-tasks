# LD SEO Routing Contract

Use this contract for every repo-owned LD SEO skill before live work, client-facing output, or external writes.

## Preflight

- Confirm the request maps to the smallest correct skill and workflow.
- For every client-scoped task, follow `docs/agent/client-memory.md`: read the Markdown brief, sidecar when present, and `docs/agent/clients/<client>-timeline.md` before workflow-specific sources.
- Confirm the client slug resolves to `docs/agent/clients/<client>.md`; use `docs/agent/clients/<client>.json` when the workflow requires structured state.
- Validate required client state before live work. Use deterministic validators where they exist.
- Prefer fresh cached exports before paid API calls. Save large live responses to files instead of chat.
- Confirm the destination before writes: Drive folder via Google Drive MCP, Monday board/group via board schema, and SE Ranking capacity before keyword or prompt writes.

## Missing-Input Routing

Do not work around missing prerequisites. Route to the smallest dependent skill that fixes the blocker:

| Missing or blocked item | Route to |
| --- | --- |
| client sidecar, client brief, `site-access` route, Drive folder, Monday board, GA4, SE Ranking project | `ld-seo-client-onboarding` |
| access errors, stale credentials, Drive filing issues, SE Ranking capacity, duplicate projects, GSC/GA4 routing, platform inventory | `ld-seo-maintenance` |
| collection state, live keyword export, page scrape, SERP cache, sidecar sync, metadata readiness | `ld-seo-collection-seo` plus `collection-seo-qa` |
| collection content brief, product context, keyword reasoning, internal-link plan, GSC enrichment, brand voice | `ld-seo-content-briefs` |
| final collection copy from an approved brief | `ld-seo-shopify-collection-writing` |
| final blog copy from an approved brief | `ld-seo-shopify-blog-writing` |
| Google Doc, Sheet, or Drive editing after LD SEO validation | `google-drive:google-docs` or `google-drive:google-sheets` |

## Write Gate

- No live writes when blockers remain unless the user explicitly approves a documented limitation.
- Never delete SE Ranking keywords/projects, Drive files, or Monday items without explicit user confirmation.
- Do not create client-facing Docs, Sheets, or Monday tasks until validation or readback QA has passed.

## Output Gate

- Client-facing deliverables must be human-readable, polished, and free of internal proof language, raw API dumps, local paths, or validator labels.
- Use Codex judgement for SEO/content/business decisions after facts are gathered.
- Read back Docs, Sheets, and Monday tasks after writes.
- End successful runs with the workflow proof block: data freshness, outputs created/updated, Drive folder, Monday task when relevant, warnings, and validator blockers.
- Append the client timeline after completion or after discovering a meaningful blocker, recording the request/source, evidence checked, outputs, decisions, caveats, next action, and proof summary.
