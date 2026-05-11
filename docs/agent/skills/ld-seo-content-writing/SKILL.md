---
name: ld-seo-content-writing
description: Route vague final-content requests from approved briefs to the right production workflow: Shopify collection HTML or Shopify blog/article HTML.
---

# LD SEO Content Writing

Use this skill only as a lightweight router for older requests that say "content writing" without naming collection pages or blogs.

## Routing

- Final Shopify collection copy, collection HTML drafts, or collection copy QA: use `ld-seo-shopify-collection-writing` and `docs/agent/workflows/collection-content-writing.md`.
- Final Shopify blog copy, article HTML drafts, or blog copy QA: use `ld-seo-shopify-blog-writing` and `docs/agent/workflows/blog-content-writing.md`.
- If the content type is unclear, infer from the brief title/body where possible; otherwise ask whether the target is a collection page or blog article.

## Preflight And Handoff

Follow `docs/agent/skills/_routing-contract.md` and `docs/agent/client-memory.md` for client-scoped work: read the client brief, sidecar when present, and client timeline before live work, then append the timeline after completion or after discovering a meaningful blocker. Route collection page copy to `ld-seo-shopify-collection-writing`, blog/article copy to `ld-seo-shopify-blog-writing`, missing briefs or style/keyword/link inputs to `ld-seo-content-briefs`, and access or destination blockers to `ld-seo-maintenance`.

## Shared Rules

- Always write from an approved brief, never from memory.
- Default output is a local validated draft first.
- Google Doc, Shopify, or Monday writes are explicit follow-up steps only.
- The dedicated skill's validator must pass with zero blockers before the copy is presented as publish-ready.
- Read back any Google Doc, Shopify, or Monday output through the dedicated skill before calling it complete.

## Proof Block

Use the proof block required by the dedicated collection or blog writing skill.
