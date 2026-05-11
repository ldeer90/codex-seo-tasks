# SE Ranking Technical Site Audit

Use SE Ranking website audit data to create a client-ready technical SEO issue summary.

## Use When

- The user asks for a SE Ranking technical audit, audit report interpretation, crawl health, or technical issue prioritisation.
- Firecrawl output is too shallow for a technical crawl.

## Required Inputs

- Client sidecar and brief.
- SE Ranking project or domain.
- Existing audit ID when available.

## Phase 0 - Access And Input Preflight

- Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.
- Confirm client sidecar/brief and SE Ranking project/domain.
- Check whether a recent audit exists before creating a new crawl.
- Confirm audit settings, page limits, credit impact, and Drive/Monday destination before writes.

### Missing-input routing

Route missing client setup or SE Ranking project to `ld-seo-client-onboarding`, SE Ranking/access/capacity blockers to `ld-seo-maintenance`, and client roadmap follow-ups to `seo-roadmap-prioritisation.md`.

## Process

1. Validate client state and confirm whether a recent audit exists.
2. Prefer reading an existing recent audit before creating a new crawl.
3. If creating an audit, confirm page limit/settings and credit impact first.
4. Fetch audit report and issue pages for the top issues.
5. Use Codex judgement to collapse raw issues into client-ready priorities by SEO impact, business impact, affected page type, effort, and confidence.
6. Create a Doc/Sheet only when the output includes context, examples, recommended fixes, and next actions.

## Quality Gate

- Do not paste raw audit issue lists as a client deliverable.
- Every priority issue needs example URLs, impact, recommendation, and owner/action.
- Read back any created deliverable.

## Proof Block

Report audit ID/date, pages crawled, health score, issues prioritised, deliverable URL, Drive folder, warnings, any follow-up crawl needed, and client timeline update status.
