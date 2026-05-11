# LD SEO Skill Architecture Diagrams

These diagrams explain how the repo-local LD SEO skills work across routing, MCPs, external APIs, scripts, cached exports, validation, Codex judgement, and client-facing outputs.

Canonical behaviour still lives in:

- [`docs/agent/skills/_index.md`](skills/_index.md)
- [`docs/agent/skills/_routing-contract.md`](skills/_routing-contract.md)
- [`docs/agent/workflows/_index.md`](workflows/_index.md)
- The individual skill and workflow files linked below

Use these diagrams as an operating map, not as a replacement for the workflow playbooks.

## Legend

```mermaid
flowchart LR
  Human["Human approval / user request"]
  Skill["Repo-local skill<br/>docs/agent/skills"]
  Workflow["Workflow playbook<br/>docs/agent/workflows"]
  Memory["Client memory<br/>brief + sidecar + timeline"]
  MCP["MCP connector<br/>SEO Automation, Drive, Monday"]
  API["External API or platform<br/>GA4, GSC, Firecrawl, SE Ranking"]
  Script["Repo script or validator<br/>scripts/*.py"]
  Cache["Cached export or local evidence"]
  Judgement["Codex judgement layer<br/>SEO, content, business reasoning"]
  Output["Output<br/>Doc, Sheet, Monday update, HTML, proof block"]

  Human --> Skill --> Workflow
  Workflow --> Memory
  Workflow --> MCP --> API
  Workflow --> Script
  Workflow --> Cache
  Cache --> Judgement
  API --> Judgement
  Script --> Judgement
  Judgement --> Output
```

## Whole System

```mermaid
flowchart TB
  User["User request<br/>plain language or /ldseo-*"]
  Menu["ld-seo-command-menu<br/>route to smallest correct skill"]
  Contract["Routing contract<br/>preflight, write gate, output gate"]
  Memory["Client memory preflight<br/>client.md + client.json + timeline.md"]
  Skill["Canonical LD SEO skill"]
  Workflow["Workflow playbook"]

  subgraph MCPs["MCP Layer"]
    SEO_MCP["seo-automation MCP<br/>GA4 + Firecrawl + Google output helpers"]
    Drive_MCP["Google Drive MCP<br/>folder truth, Docs, Sheets"]
    Monday_MCP["Monday MCP<br/>board schema, items, updates"]
    SERanking_MCP["SE Ranking MCP / API tools<br/>keywords, SERPs, volumes"]
  end

  subgraph APIs["External Platforms"]
    GA4["GA4"]
    GSC["Google Search Console"]
    Firecrawl["Firecrawl"]
    Drive["Google Drive, Docs, Sheets"]
    Monday["Monday.com"]
    SERanking["SE Ranking"]
    Shopify["Shopify public site<br/>sitemaps, pages, product context"]
    ScreamingFrog["Screaming Frog CLI"]
  end

  subgraph Local["Repo Intelligence Layer"]
    Scripts["scripts/*.py<br/>discovery, transforms, validators"]
    Caches["Cached exports<br/>keyword, SERP, sitemap, crawl files"]
    Sidecar["Client sidecar<br/>structured operational state"]
    Codex["Codex judgement<br/>SEO priority, fit, caveats, client wording"]
  end

  Output["Client-safe output<br/>Docs, Sheets, Monday drafts/posts, HTML, chat analysis"]
  Proof["Proof block + timeline append<br/>kept out of client-facing Docs"]

  User --> Menu --> Contract --> Skill --> Workflow
  Workflow --> Memory
  Memory --> Sidecar
  Workflow --> MCPs
  SEO_MCP --> GA4
  SEO_MCP --> Firecrawl
  Drive_MCP --> Drive
  Monday_MCP --> Monday
  SERanking_MCP --> SERanking
  Workflow --> Shopify
  Workflow --> ScreamingFrog
  Workflow --> Scripts
  Scripts --> Caches
  GA4 --> Caches
  GSC --> Caches
  Firecrawl --> Caches
  Drive --> Caches
  Monday --> Caches
  SERanking --> Caches
  Shopify --> Caches
  ScreamingFrog --> Caches
  Caches --> Codex
  Sidecar --> Codex
  Codex --> Output
  Output --> Proof
  Proof --> Memory
```

## Routing And Safety Gates

```mermaid
flowchart TD
  Request["Request arrives"]
  Smallest["Choose smallest matching skill<br/>do not over-run full workflows"]
  ClientScoped{"Client-scoped?"}
  ReadMemory["Read client brief, sidecar if present, timeline"]
  ReadWorkflow["Read canonical skill + workflow"]
  Validate["Validate required state<br/>sidecar, access, destinations, cached exports"]
  Blocker{"Blocker found?"}
  RouteBlocker["Route to smallest dependent skill<br/>onboarding, maintenance, collection SEO, content briefs"]
  WriteIntent{"External write needed?"}
  Confirm["Confirm client + destination + scope<br/>Drive folder, Monday board/group, SE Ranking capacity"]
  Execute["Run workflow"]
  Readback["Read back Docs, Sheets, Monday tasks, or files"]
  Proof["Return proof block<br/>data freshness, outputs, warnings, blockers"]
  Timeline["Append client timeline when client-scoped"]

  Request --> Smallest --> ClientScoped
  ClientScoped -- Yes --> ReadMemory --> ReadWorkflow
  ClientScoped -- No --> ReadWorkflow
  ReadWorkflow --> Validate --> Blocker
  Blocker -- Yes --> RouteBlocker
  Blocker -- No --> WriteIntent
  WriteIntent -- Yes --> Confirm --> Execute
  WriteIntent -- No --> Execute
  Execute --> Readback --> Proof --> Timeline
```

## `ld-seo-command-menu`

Routes a request to the correct canonical skill and workflow. See [`ld-seo-command-menu/SKILL.md`](skills/ld-seo-command-menu/SKILL.md).

```mermaid
flowchart LR
  User["User asks for a task<br/>or types /ldseo-*"]
  Menu["ld-seo-command-menu"]
  Index["Skill index<br/>docs/agent/skills/_index.md"]
  WorkflowIndex["Workflow index<br/>docs/agent/workflows/_index.md"]
  Contract["Routing contract"]

  subgraph Routes["Canonical Routes"]
    Onboard["ld-seo-client-onboarding"]
    Maintain["ld-seo-maintenance"]
    Collection["ld-seo-collection-seo"]
    Briefs["ld-seo-content-briefs"]
    CollectionCopy["ld-seo-shopify-collection-writing"]
    BlogCopy["ld-seo-shopify-blog-writing"]
    Audits["ld-seo-audits-reporting"]
  end

  User --> Menu
  Menu --> Index
  Menu --> WorkflowIndex
  Menu --> Contract
  Contract --> Routes
```

## `ld-seo-client-onboarding`

Sets up valid client state before delivery work. See [`ld-seo-client-onboarding/SKILL.md`](skills/ld-seo-client-onboarding/SKILL.md) and [`add-new-client.md`](workflows/add-new-client.md).

```mermaid
flowchart TD
  Facts["Confirmed client facts<br/>slug, site, access, folders, boards"]
  Existing["Check existing state<br/>clients/*.md, clients/*.json, timeline"]
  DriveCheck["Drive folder checks<br/>Google Drive MCP"]
  MondayCheck["Monday board/schema checks<br/>Monday MCP"]
  AccessRoute["GA4/site route<br/>config/site-access.json"]
  SERanking["SE Ranking project + engines"]
  Sidecar["Create/update client.json"]
  Brief["Create/update client.md"]
  Timeline["Create timeline.md"]
  Validator["scripts/validate_client_json.py"]
  Readback["Read back folders, docs, Monday items"]
  Handoff["Zero-blocker handoff<br/>collection, content, audits, maintenance"]

  Facts --> Existing
  Existing --> DriveCheck
  Existing --> MondayCheck
  Existing --> AccessRoute
  Existing --> SERanking
  DriveCheck --> Sidecar
  MondayCheck --> Sidecar
  AccessRoute --> Sidecar
  SERanking --> Sidecar
  Sidecar --> Brief --> Timeline --> Validator
  Validator --> Readback --> Handoff
```

## `ld-seo-maintenance`

Diagnoses platform state, access, filing, SE Ranking capacity, and credential problems. See [`ld-seo-maintenance/SKILL.md`](skills/ld-seo-maintenance/SKILL.md), [`troubleshoot-access.md`](workflows/troubleshoot-access.md), and [`se-ranking-hygiene.md`](workflows/se-ranking-hygiene.md).

```mermaid
flowchart TD
  Trigger["Access, capacity, filing, or platform drift issue"]
  Preflight["Read affected client state<br/>or platform reference"]
  DiagnoseType{"Issue type"}

  GA4Route["GA4/GSC routing<br/>site-access + delegated subject"]
  DriveTruth["Drive truth<br/>Google Drive MCP parentId checks"]
  MondayState["Monday state<br/>board/schema/workspace reads"]
  SERankingHygiene["SE Ranking hygiene<br/>projects, keyword-engine pairs, capacity"]
  PlatformRefresh["Platform refresh<br/>seo_automation_mcp.platform_inventory"]

  Scripts["Maintenance scripts<br/>audit_se_ranking_project.py<br/>drive_organise.py<br/>drive_root_cleanup.py"]
  FixPlan["Smallest safe fix<br/>never delete without explicit approval"]
  Validate["Revalidate affected state"]
  Return["Return to originating workflow<br/>rerun preflight before writes"]

  Trigger --> Preflight --> DiagnoseType
  DiagnoseType --> GA4Route
  DiagnoseType --> DriveTruth
  DiagnoseType --> MondayState
  DiagnoseType --> SERankingHygiene
  DiagnoseType --> PlatformRefresh
  SERankingHygiene --> Scripts
  DriveTruth --> Scripts
  PlatformRefresh --> Scripts
  GA4Route --> FixPlan
  MondayState --> FixPlan
  Scripts --> FixPlan --> Validate --> Return
```

## `ld-seo-collection-seo`

Runs collection discovery, keyword research, SERP review, metadata generation, Sheet output, and Monday handoff. See [`ld-seo-collection-seo/SKILL.md`](skills/ld-seo-collection-seo/SKILL.md), [`collection-seo-full.md`](workflows/collection-seo-full.md), [`keyword-research-collections.md`](workflows/keyword-research-collections.md), [`competitor-keyword-research.md`](workflows/competitor-keyword-research.md), and [`onpage-title-h1-suggestions.md`](workflows/onpage-title-h1-suggestions.md).

```mermaid
flowchart TD
  Request["Collection SEO request"]
  Preflight["Client brief + sidecar + timeline<br/>routing contract"]
  ValidateClient["scripts/validate_client_json.py"]
  Discovery["Discover collection URLs<br/>Shopify sitemap first<br/>discover_collections.py"]
  KeywordGen["Generate keyword candidates<br/>Codex judgement + client context"]
  CandidateQA["evaluate_collection_keyword_candidates.py"]
  Volume["SE Ranking volumes<br/>batched by engine/market"]
  AddTrack{"Live keyword writes needed?"}
  SERankingWrite["SE Ranking keyword add<br/>capacity checked first"]
  Export["Live keyword export + cached files"]
  Sync["sync_collection_sidecar_from_exports.py"]
  StateQA["validate_collection_seo_state.py"]
  SERP["SE Ranking SERP data<br/>reuse cache if fresh"]
  Scrape["Firecrawl scrape_urls<br/>top competitor pages when needed"]
  Metadata["build_metadata_suggestions.py"]
  Deliverable["Google Sheet or Doc<br/>Drive MCP / GoogleWorkspaceClient"]
  Monday["Monday task/update<br/>after board schema read"]
  Proof["Proof block + timeline"]

  Request --> Preflight --> ValidateClient --> Discovery --> KeywordGen --> CandidateQA --> Volume --> AddTrack
  AddTrack -- Yes --> SERankingWrite --> Export
  AddTrack -- No --> Export
  Export --> Sync --> StateQA
  StateQA --> SERP --> Scrape --> Metadata --> Deliverable --> Monday --> Proof
```

## `ld-seo-content-briefs`

Creates writer-ready Shopify collection briefs from validated collection SEO state. See [`ld-seo-content-briefs/SKILL.md`](skills/ld-seo-content-briefs/SKILL.md), [`shopify-collection-content-briefs/SKILL.md`](skills/shopify-collection-content-briefs/SKILL.md), and [`collection-content-briefs.md`](workflows/collection-content-briefs.md).

```mermaid
flowchart TD
  Request["Content brief request"]
  Preflight["Client memory + routing contract"]
  ClientQA["validate_client_json.py"]
  CollectionQA["validate_collection_seo_state.py"]
  Inputs["Brief input gathering"]

  subgraph Evidence["Evidence Sources"]
    Keywords["Tracked keywords + SE Ranking related terms"]
    GSC["Search Console opportunities"]
    SERP["SERP patterns and competitor context"]
    Products["Current collection pages<br/>product/category context"]
    Links["Sitemap-grounded internal links"]
  end

  SuppResearch["research_supplemental_keywords.py"]
  InputBuilder["build_collection_content_brief_inputs.py"]
  CodexFilter["Codex judgement<br/>remove irrelevant, branded, cannibalising, low-intent terms"]
  BriefQA["validate_collection_content_briefs.py<br/>plus human-quality critique"]
  Render["render_collection_content_brief_doc.py"]
  DriveDocs["Google Docs in content folder<br/>Drive MCP / GoogleWorkspaceClient"]
  MondayTasks["Monday tasks<br/>schema read first"]
  Readback["Read back sample Docs<br/>confirm every Monday URL"]
  Proof["Proof block + timeline"]

  Request --> Preflight --> ClientQA --> CollectionQA --> Inputs
  Keywords --> Inputs
  GSC --> Inputs
  SERP --> Inputs
  Products --> Inputs
  Links --> Inputs
  Inputs --> SuppResearch --> InputBuilder --> CodexFilter --> BriefQA --> Render --> DriveDocs --> MondayTasks --> Readback --> Proof
```

## `ld-seo-shopify-collection-writing`

Turns an approved collection brief into publish-ready Shopify collection body HTML. See [`ld-seo-shopify-collection-writing/SKILL.md`](skills/ld-seo-shopify-collection-writing/SKILL.md) and [`collection-content-writing.md`](workflows/collection-content-writing.md).

```mermaid
flowchart TD
  Request["Final collection copy or QA request"]
  Preflight["Client memory + approved brief gate"]
  Brief["Approved collection brief<br/>Google Doc or JSON"]
  SERPReview["Top-ranking collection review<br/>SE Ranking SERP or saved review"]
  Length["analyze_collection_serp_length.py<br/>when saved review exists"]
  LinkCandidates["build_collection_internal_link_candidates.py<br/>sitemap exports"]
  Judgement["Codex drafting judgement<br/>voice, intent, keyword fit, natural links"]
  Draft["Shopify body HTML only<br/>h2, two h3s, p, approved links"]
  Validator["validate_collection_html_copy.py"]
  OutputChoice{"User requested filing?"}
  Local["Return/local draft path + proof"]
  DriveMonday["Optional Doc or Monday output<br/>after destination confirmed"]
  Readback["Read back filed output"]
  Timeline["Timeline append"]

  Request --> Preflight --> Brief --> SERPReview --> Length --> LinkCandidates --> Judgement --> Draft --> Validator --> OutputChoice
  OutputChoice -- No --> Local --> Timeline
  OutputChoice -- Yes --> DriveMonday --> Readback --> Timeline
```

## `ld-seo-shopify-blog-writing`

Turns an approved blog brief into publish-ready Shopify article HTML. See [`ld-seo-shopify-blog-writing/SKILL.md`](skills/ld-seo-shopify-blog-writing/SKILL.md) and [`blog-content-writing.md`](workflows/blog-content-writing.md).

```mermaid
flowchart TD
  Request["Final blog/article copy or QA request"]
  Preflight["Client memory + approved blog brief gate"]
  Brief["Approved blog brief<br/>structure, sources, HTML policy"]
  Sources["Approved sources + external links"]
  SERP["Top 3 relevant blog/article SERPs<br/>SE Ranking where available"]
  Sitemaps["Collection + blog sitemap exports"]
  Links["build_blog_internal_link_candidates.py"]
  Judgement["Codex article judgement<br/>angle, structure, trust signals, voice, claims"]
  Draft["Shopify article body HTML<br/>brief-defined tags only"]
  Validator["validate_blog_html_copy.py"]
  OutputChoice{"Doc or Monday requested?"}
  Local["Return/local HTML + proof"]
  DriveDoc["Optional client-presentable Google Doc<br/>raw HTML kept out of body"]
  Monday["Optional Monday update/task"]
  Readback["Read back Doc/Monday output"]
  Timeline["Timeline append"]

  Request --> Preflight --> Brief
  Brief --> Sources --> Judgement
  Brief --> SERP --> Judgement
  Brief --> Sitemaps --> Links --> Judgement
  Judgement --> Draft --> Validator --> OutputChoice
  OutputChoice -- No --> Local --> Timeline
  OutputChoice -- Yes --> DriveDoc --> Monday --> Readback --> Timeline
```

## `ld-seo-audits-reporting`

Handles single-page audits, full technical audits, traffic checks, monthly performance comments, and explicit Doc + Sheet reports. See [`ld-seo-audits-reporting/SKILL.md`](skills/ld-seo-audits-reporting/SKILL.md), [`single-page-audit.md`](workflows/single-page-audit.md), [`full-site-audit.md`](workflows/full-site-audit.md), [`ga4-traffic-check.md`](workflows/ga4-traffic-check.md), [`monthly-performance-comment.md`](workflows/monthly-performance-comment.md), and [`monthly-combined-report.md`](workflows/monthly-combined-report.md).

```mermaid
flowchart TD
  Request["Audit or reporting request"]
  Route{"Smallest workflow"}

  PageAudit["Single-page audit<br/>extract_page_seo via SEO Automation MCP"]
  Traffic["GA4 traffic check<br/>GA4 organic data only"]
  Monthly["Monthly performance comment<br/>GA4 + GSC + SE Ranking + Monday work"]
  FullAudit["Full technical audit<br/>Screaming Frog preferred"]
  Combined["Explicit Doc + Sheet report<br/>GA4 landing pages + Firecrawl audits"]

  Preflight["Client memory + access/destination checks"]
  DraftOnly["Detailed chat analysis first<br/>monthly comments require approval before posting"]
  ScreamingFrog["run_screaming_frog_audit.py"]
  AnalyzeSF["analyze_screaming_frog_export.py"]
  SEO_MCP["seo-automation MCP<br/>resolve_google_access_subject<br/>create_combined_seo_report"]
  Firecrawl["Firecrawl page audits"]
  DriveOutput["Google Doc/Sheet output<br/>when explicitly requested"]
  MondayPost["Monday update<br/>only after explicit approval"]
  Judgement["Codex prioritisation<br/>impact, effort, confidence, seasonality"]
  Proof["Proof block + timeline"]

  Request --> Route
  Route --> PageAudit --> Judgement
  Route --> Traffic --> Judgement
  Route --> Monthly --> Preflight --> DraftOnly --> Judgement
  Route --> FullAudit --> Preflight --> ScreamingFrog --> AnalyzeSF --> Judgement
  Route --> Combined --> Preflight --> SEO_MCP --> Firecrawl --> DriveOutput --> Judgement
  Judgement --> MondayPost --> Proof
  Judgement --> Proof
```

## Data Lineage

This shows where evidence is allowed to come from and where it can land.

```mermaid
flowchart LR
  subgraph Evidence["Evidence In"]
    GA4["GA4<br/>organic sessions, revenue, landing pages"]
    GSC["Search Console<br/>queries, pages, positions"]
    SERanking["SE Ranking<br/>keywords, volumes, SERPs, visibility"]
    Firecrawl["Firecrawl<br/>page content, SEO fields, links"]
    ScreamingFrog["Screaming Frog<br/>technical crawl exports"]
    Shopify["Shopify public data<br/>sitemaps, collections, products"]
    MondayIn["Monday<br/>completed work, board context"]
    DriveIn["Drive<br/>briefs, folders, historical outputs"]
  end

  subgraph Processing["Processing And Intelligence"]
    Caches["Cached raw exports<br/>/tmp or docs"]
    Scripts["Repo scripts<br/>transform, sync, validate, render"]
    Sidecar["client.json<br/>operational state"]
    Codex["Codex judgement<br/>strategy, fit, writing, caveats"]
  end

  subgraph Outputs["Outputs Out"]
    Sheets["Google Sheets<br/>metadata, audits, data tables"]
    Docs["Google Docs<br/>briefs, reports, client drafts"]
    MondayOut["Monday drafts/posts/tasks"]
    HTML["Shopify-ready HTML"]
    Timeline["client timeline<br/>internal memory only"]
    Proof["Proof block<br/>agent response only"]
  end

  GA4 --> Caches
  GSC --> Caches
  SERanking --> Caches
  Firecrawl --> Caches
  ScreamingFrog --> Caches
  Shopify --> Caches
  MondayIn --> Caches
  DriveIn --> Caches
  Caches --> Scripts --> Sidecar --> Codex
  Scripts --> Codex
  Codex --> Sheets
  Codex --> Docs
  Codex --> MondayOut
  Codex --> HTML
  Codex --> Proof
  Proof --> Timeline
```

## Write Approval Boundaries

```mermaid
flowchart TD
  Candidate["Potential write action"]
  Kind{"Write target"}
  Drive["Google Doc, Sheet, or Drive folder"]
  Monday["Monday item, update, or task"]
  SERanking["SE Ranking keyword/project/prompt"]
  Local["Local repo file or cached export"]

  ClientConfirm["Confirm client and destination"]
  FolderTruth["Verify Drive destination via Drive MCP"]
  BoardSchema["Read Monday board schema/group"]
  Capacity["Check SE Ranking project + capacity"]
  Validator["Run relevant validator/readback QA"]
  Execute["Perform write"]
  Readback["Read back created/updated output"]
  Proof["Report URL/path + warnings<br/>append timeline if client-scoped"]

  Candidate --> Kind
  Kind --> Drive --> ClientConfirm --> FolderTruth --> Validator
  Kind --> Monday --> ClientConfirm --> BoardSchema --> Validator
  Kind --> SERanking --> ClientConfirm --> Capacity --> Validator
  Kind --> Local --> Validator
  Validator --> Execute --> Readback --> Proof
```

## Keeping These Diagrams Current

- Update this file when a canonical skill adds or removes a platform dependency, write gate, or validator.
- Do not document secrets, API keys, service-account JSON contents, or raw credentials here.
- Do not copy full workflow steps into diagrams; link to the workflow and show the operational architecture.
- Keep client-facing proof language out of Google Docs and Sheets. Proof blocks belong in agent responses, local validation artifacts, or Monday only when appropriate.
