# Google Search Console Opportunity Mining

Find page/query opportunities that can improve content, metadata, internal links, and prioritisation.

## Use When

- The user asks for Search Console opportunities, high-potential queries, striking-distance keywords, content refresh ideas, or query/page analysis.
- A content brief, metadata update, monthly report, or roadmap needs real query grounding.

## Required Inputs

- Client JSON and Markdown brief.
- GSC source: native Search Console export or SE Ranking `PROJECT_getGoogleSearchConsole`.
- Date range, defaulting to the last 90 complete days.
- Target page set, if scoped.

## Phase 0 - Access And Input Preflight

- Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.
- Confirm client sidecar, Markdown brief, website/property route, and target page scope.
- Confirm GSC access via native Search Console export or SE Ranking GSC integration before promising query-level opportunities.
- Confirm Drive/Monday destination only if a deliverable or task is requested.

### Missing-input routing

Route missing client setup or property mapping to `ld-seo-client-onboarding`, Search Console/SE Ranking/access blockers to `ld-seo-maintenance`, content brief enrichment to `ld-seo-content-briefs`, and roadmap prioritisation to `seo-roadmap-prioritisation.md`.

## Process

1. Validate the client sidecar and confirm the website/property route.
2. Export GSC rows by page and query. Save the raw response to `/tmp/<client>-gsc-<date>.json`.
3. Filter obvious brand, typo, navigational, irrelevant, and duplicate queries, but keep a separate brand bucket for reporting.
4. Score opportunities by impressions, clicks, CTR gap, average position, page fit, and business relevance.
5. Use Codex judgement to classify each opportunity:
   - Metadata improvement
   - Content section or FAQ addition
   - New page or collection candidate
   - Internal-link target
   - Not actionable
6. Render a client-ready summary Doc or Sheet only after the scored export is reviewed.

## Quality Gate

- Every recommended query must include source, date range, page URL, impressions, clicks, CTR, position, and rationale.
- Do not recommend targeting a query if the page intent does not match.
- Read back any created Doc/Sheet.

## Proof Block

Report date range, rows exported, opportunities retained, pages covered, Drive folder, deliverable URL, warnings, whether native GSC or SE Ranking supplied the data, and client timeline update status.
