# LD SEO Scripts Index

Compact map of repo scripts used by LD SEO skills. Use this before opening full workflow docs when deciding which script or validator is relevant.

Canonical execution details still live in the workflow docs and script `--help` output. Do not paste secrets or raw API keys into script arguments, logs, or docs.

## Production And Support Scripts

| Script | Type | Used by | Purpose | Inputs | Outputs | Mutates repo files? | Do not run when |
|---|---|---|---|---|---|---:|---|
| `scripts/analyze_collection_serp_length.py` | Analysis | Collection final copy | Summarise saved SERP/page review depth to set copy length. | Saved SERP review/export. | Length guidance. | No | No saved SERP review exists; use documented fallback and note caveat. |
| `scripts/analyze_screaming_frog_export.py` | Analysis/validator | Full-site audit | Convert Screaming Frog CSV exports into compact audit metrics and top issues. | Screaming Frog export directory. | JSON/Markdown summary when output args are used. | Optional output files only | Crawl export is incomplete or from the wrong client/site. |
| `scripts/audit_se_ranking_project.py` | Maintenance | SE Ranking hygiene | Audit project keyword-engine pair usage and cleanup candidates. | SE Ranking project export/metadata. | Hygiene summary. | No unless output path requested | User has not confirmed destructive cleanup; this script should inform, not delete. |
| `scripts/build_blog_internal_link_candidates.py` | Input builder | Blog final copy | Build collection/blog internal-link candidates from sitemap exports. | Collection and blog sitemap exports. | Candidate JSON. | No unless output path requested | Sitemaps are stale or unrelated to the client. |
| `scripts/build_collection_content_brief_inputs.py` | Input builder | Content briefs | Merge collection SEO state, page context, keywords, GSC, and links into brief inputs. | Client sidecar, current-page data, keyword/GSC/link evidence. | Brief input JSON. | No unless output path requested | Collection SEO validation has blockers. |
| `scripts/build_collection_internal_link_candidates.py` | Input builder | Collection final copy | Build related collection link candidates from sitemap exports. | Collection sitemap export and target collection. | Candidate JSON. | No unless output path requested | No sitemap export or link targets are unrelated. |
| `scripts/build_metadata_suggestions.py` | Renderer | Collection SEO metadata | Generate title tag, H1, and meta description suggestions from validated collection state. | Client sidecar and keyword/SERP/current-page evidence. | Metadata rows/JSON. | No unless output path requested | Sidecar or keyword export is stale. |
| `scripts/critique_collection_content_briefs.py` | QA | Content briefs | Score rendered collection briefs against writer/client usefulness. | Rendered brief JSON/text. | Critique summary. | No unless output path requested | Brief generation has validator blockers that should be fixed first. |
| `scripts/discover_collections.py` | Discovery | Collection SEO | Discover Shopify/ecommerce collection URLs and classify them. | Domain or sitemap source. | Collection discovery JSON. | No unless output path requested | Client is not collection-capable or domain is unconfirmed. |
| `scripts/drive_auto_organise.py` | Maintenance | Drive filing | Assist Drive filing/organisation using known folder conventions. | Drive/file metadata and target folder context. | Proposed or executed filing actions depending on args. | No repo mutation | Destination folder has not been verified via Drive MCP. |
| `scripts/drive_organise.py` | Maintenance | Drive filing | Organise Drive files into expected client folders. | Drive/file metadata and folder IDs. | Filing actions/report. | No repo mutation | User has not approved file moves or target folders are uncertain. |
| `scripts/drive_root_cleanup.py` | Maintenance | Drive filing | Find or clean root-level Drive clutter. | Drive/root metadata. | Cleanup report/actions. | No repo mutation | User has not explicitly approved destructive or move actions. |
| `scripts/evaluate_collection_keyword_candidates.py` | QA/validator | Collection SEO keyword research | Score raw keyword candidates for relevance, intent, and cannibalisation risk. | Candidate keyword JSON and client/collection context. | Evaluated keyword JSON/summary. | No unless output path requested | Keywords are already curated and no new candidates are being considered. |
| `scripts/render_collection_content_brief_doc.py` | Renderer | Content briefs | Render writer-ready brief content for Google Docs. | Validated brief input JSON. | Doc-ready text/structure. | No unless output path requested | Brief inputs have blockers or unsupported product claims. |
| `scripts/render_keyword_research_doc.py` | Renderer | Collection SEO | Render keyword research notes into a client/team-readable format. | Client sidecar and keyword export. | Doc-ready text. | No unless output path requested | Keyword export is stale after SE Ranking writes. |
| `scripts/research_supplemental_keywords.py` | Research helper | Content briefs | Pull/score supplemental keyword opportunities for each collection. | Sidecar, seed keywords, SE Ranking/GSC evidence. | Supplemental keyword JSON. | No unless output path requested | SE Ranking access/capacity is blocked or client context is too thin. |
| `scripts/run_screaming_frog_audit.py` | Runner | Full-site audit | Run Screaming Frog CLI with approved config and package exports. | Site URL, config, output dir, optional Drive upload args. | Export folder, summaries, manifest, optional Drive upload. | Writes output artifacts only | Screaming Frog/config is unavailable or crawl scope is unconfirmed. |
| `scripts/sync_collection_sidecar_from_exports.py` | Sync | Collection SEO | Sync client sidecar from live SE Ranking/current-page/volume exports. | Client sidecar, keyword export, volume exports, page cache. | Updated sidecar JSON when output path is set. | Yes, when output is a repo sidecar | Live exports are stale or incomplete after keyword writes. |
| `scripts/validate_blog_html_copy.py` | Validator | Blog final copy | Validate Shopify blog/article HTML against brief, links, and claim rules. | Draft HTML and validation context. | Validation JSON/summary. | No | Brief is incomplete or allowed HTML policy is missing. |
| `scripts/validate_client_json.py` | Validator | Onboarding and all client-scoped workflows | Validate client sidecar shape and blocker/warning state. | Client JSON sidecar. | Validation summary/JSON. | No | Client does not have a sidecar yet; use onboarding path. |
| `scripts/validate_collection_content_briefs.py` | Validator | Content briefs | Validate generated collection content brief inputs/outputs. | Brief input/output JSON. | Validation summary/JSON. | No | Collection SEO state has blockers. |
| `scripts/validate_collection_html_copy.py` | Validator | Collection final copy and brief follow-on drafts | Validate Shopify collection body HTML structure, links, keywords, and claims. | Draft HTML and validation context. | Validation summary/JSON. | No | No approved brief or link context exists. |
| `scripts/validate_collection_seo_state.py` | Validator | Collection SEO and content briefs | Validate sidecar collection coverage, live keywords, current-page state, and SERP evidence. | Client sidecar, keyword export, page cache, SERP cache. | Validation summary/JSON. | No | Live SE Ranking writes have not been re-exported. |

## Support Or Legacy Scripts

| Script | Status | Notes |
|---|---|---|
| `scripts/collection_seo_utils.py` | Support library | Shared helpers imported by collection SEO scripts. Do not run directly. |
| `scripts/melani_collection_keywords.py` | Legacy one-off | Client-specific historical helper. Prefer canonical collection SEO scripts for new work. |
| `scripts/sync_codex_skills.py` | Maintenance support | Syncs installed Codex skill entrypoints from repo-local canonical skills. Used by tests and setup, not normal SEO delivery. |

## Token-Saving Usage

1. Use `docs/agent/routing-manifest.json` to identify the likely scripts and validators.
2. Open only the routed workflow section that explains the selected script.
3. Run script `--help` or inspect the script only when the workflow or manifest does not provide enough detail.
4. Save large script/API responses to files and reference paths in proof blocks instead of pasting raw data into chat.
