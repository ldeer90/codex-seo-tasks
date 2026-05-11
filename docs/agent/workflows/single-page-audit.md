# Single-Page Audit

Quick read of one URL. No Drive output.

## Phase 0 - Access And Input Preflight

- Memory: for client-scoped page audits, follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.
- Confirm the target URL is explicit and reachable enough to audit.
- If the user wants a client-facing Sheet/Doc or Monday task, confirm the client sidecar and destination first.

### Missing-input routing

Route missing client setup or Drive/Monday destination to `ld-seo-client-onboarding`, access or filing blockers to `ld-seo-maintenance`, and broader site-audit requests to `full-site-audit.md`.

## Run

```json
{ "url": "https://example.com/page" }
```

Tool: `extract_page_seo`.

## What you get back

`PageSEOAudit` dict:

- `url`, `status`, `title`, `meta_description`, `h1`, `h2s`, `word_count`, `canonical`
- `main_content_summary` — short summary, do not quote more than 15 words from it.
- `internal_links`
- `issues` — list of detected problems
- `recommendations` — list of suggested fixes

## Client-Presentable QA

Use Codex judgement before replying:

- Prioritise issues by likely SEO/business impact, not by raw order alone.
- Explain whether the page appears indexable, understandable, and useful for the likely search intent.
- Do not overstate a finding when the scrape is thin or blocked; call out uncertainty.

## Deliver

Reply with: title, meta description, word count, canonical, issue count, internal link count, the highest-priority findings, and practical recommendations. Keep raw tool issue labels when useful, but translate them into client-friendly language.

If the user wants a Sheet for one URL, switch to `create_site_audit_sheet` with `urls: [<the URL>]` and a `client_name`.

## Quality Gate

- Use Codex judgement to prioritise findings by SEO/business impact.
- Do not overstate blocked or thin scrape results.

## Proof Block

Report URL, scrape status, title/H1/meta state, issue count, highest-priority fixes, any crawl limitations, and client timeline update status when client-scoped.
