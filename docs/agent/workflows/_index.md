# Workflow Playbooks

Numbered, step-by-step recipes. When a user request maps to one of these, follow it literally.

Repo-local skill specs live in [`../skills/_index.md`](../skills/_index.md). Read the matching skill before running a workflow that names or implies one.

For client-scoped workflows, read [`../client-memory.md`](../client-memory.md), then read the client brief, sidecar when present, and timeline before workflow-specific sources. Append the timeline after successful completion or after discovering a meaningful blocker.

| Workflow | When to use |
|---|---|
| [monthly-performance-comment.md](monthly-performance-comment.md) | `/ldseo-monthly-report <client>`: client-ready monthly performance comment for Monday from GA4, SE Ranking, GSC, completed work, YoY, and seasonality |
| [monthly-combined-report.md](monthly-combined-report.md) | Legacy explicit Doc + Sheet workflow only. Do not use for `/ldseo-monthly-report`. |
| [single-page-audit.md](single-page-audit.md) | "Audit this URL" |
| [full-site-audit.md](full-site-audit.md) | "Crawl this site and give me a report"; defaults to Screaming Frog technical crawl when local CLI/config are available |
| [ga4-traffic-check.md](ga4-traffic-check.md) | Quick GA4 organic traffic look without writing to Drive |
| [regenerate-platform-reference.md](regenerate-platform-reference.md) | Refresh `docs/platform-reference.md` after a structural change |
| [add-new-client.md](add-new-client.md) | Onboarding a new client end-to-end |
| [troubleshoot-access.md](troubleshoot-access.md) | A tool call returned 401/403 and you need to figure out why |
| [collection-seo-full.md](collection-seo-full.md) | **One-shot:** full collection SEO pipeline (discovery → keywords → competitor SERP → metadata suggestions → Sheet → Monday). Driven by `client.json` sidecar. |
| [keyword-research-collections.md](keyword-research-collections.md) | Collection page keyword research: discover → generate → verify volumes → SE Ranking → Sheet → Drive → Monday |
| [onpage-title-h1-suggestions.md](onpage-title-h1-suggestions.md) | Generate title tag + H1 suggestions per collection page from keyword research data |
| [competitor-keyword-research.md](competitor-keyword-research.md) | Pull competitor organic keywords, find gaps, surface new page and content opportunities |
| [se-ranking-hygiene.md](se-ranking-hygiene.md) | Audit SE Ranking projects, find duplicates, check plan capacity before adding keywords |
| [collection-content-briefs.md](collection-content-briefs.md) | Shopify collection content briefs: keyword grounding, SERP/product context, internal links, Google Docs, Monday tasks |
| [collection-content-writing.md](collection-content-writing.md) | Publish-ready Shopify collection HTML copy from approved collection content briefs |
| [blog-content-writing.md](blog-content-writing.md) | Publish-ready Shopify blog article HTML from approved blog briefs |
| [gsc-opportunity-mining.md](gsc-opportunity-mining.md) | Search Console query/page opportunities for metadata, content, links, and roadmaps |
| [internal-linking-opportunities.md](internal-linking-opportunities.md) | Crawl-grounded internal link recommendations with natural anchor and placement ideas |
| [technical-site-audit-seranking.md](technical-site-audit-seranking.md) | SE Ranking technical audit interpretation and client-ready issue prioritisation |
| [ai-search-tracking.md](ai-search-tracking.md) | SE Ranking AI Result Tracker setup and prompt management |
| [seo-roadmap-prioritisation.md](seo-roadmap-prioritisation.md) | Evidence-led SEO roadmap prioritisation from audits, rankings, GSC, and business context |

Every playbook ends with: confirm the user, deliver URLs from the tool result, read back client-facing outputs where possible, summarise headline issues, append the client timeline when client-scoped, and include the proof block required by the workflow.
