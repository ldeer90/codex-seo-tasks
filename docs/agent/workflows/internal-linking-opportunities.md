# Internal Linking Opportunities

Create practical internal link recommendations grounded in crawl data, target page value, and natural placement.

## Use When

- The user asks for internal links, collection cross-links, supporting page links, or content update opportunities.
- Content briefs need natural internal-link targets.
- Blog drafts need collection and supporting blog links from sitemap-grounded candidates.

## Required Inputs

- Client sidecar and brief.
- Crawl or page scrape with visible copy and existing internal links.
- Target page list with keyword, URL, business priority, and current performance when available.

## Phase 0 - Access And Input Preflight

- Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.
- Confirm client sidecar/brief, source page scope, target page list, and whether a recent crawl/cache exists.
- Confirm Drive/Monday destination only if a deliverable or task is requested.
- Confirm crawl cost before fetching large page sets.

### Missing-input routing

Route missing client setup to `ld-seo-client-onboarding`, crawl/access/Drive/Monday blockers to `ld-seo-maintenance`, missing target keywords or collection state to `ld-seo-collection-seo`, and missing content briefs to `ld-seo-content-briefs`.

## Process

1. Validate client state and target pages.
2. Reuse a recent crawl/cache when available; otherwise crawl only the needed page set.
3. Build a source-target candidate matrix.
4. Exclude self-links, already-linked targets where no change is needed, noindex pages, utility pages, and intent mismatches.
5. Score by topical similarity, target priority, keyword opportunity, current authority, natural anchor fit, and user usefulness.
6. Use Codex judgement to write human placement recommendations, not just anchor lists.
7. Output a Sheet or Doc with source URL, target URL, anchor text, placement idea, rationale, priority, and confidence.

For Shopify blog writing, use `scripts/build_blog_internal_link_candidates.py` against saved collection and blog sitemap exports, then choose 1-5 collection links plus optional supporting blog links before drafting.

## Quality Gate

- Every recommendation must be naturally placeable in visible page content.
- Do not recommend exact-match anchors when they read unnaturally.
- Read back any created deliverable and surface warnings.

## Proof Block

Report source pages checked, targets considered, links recommended, crawl/cache source, Drive folder, deliverable URL, warnings, next implementation step, and client timeline update status.
