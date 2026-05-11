# Blog Content Writing

Create publish-ready Shopify blog article body HTML from an approved blog brief.

## Use When

- The user asks to write final blog copy, article copy, Shopify blog HTML, QA a blog draft, or revise blog content.
- An approved blog brief exists and defines the article structure and allowed HTML policy.
- Triggered by `ld-seo-shopify-blog-writing`.

## Required Inputs

- Approved blog brief JSON or Google Doc text.
- Client sidecar and brief.
- Target article slug or title.
- Primary keyword, secondary keywords, search intent, audience, sources/claims, approved links, CTA guidance, and brand voice.
- Saved collection sitemap export and blog sitemap export for the client site.
- Saved SERP review export for the primary keyword, covering the top 3 ranking relevant blog/article results where available.

## Phase 0 - Access And Input Preflight

Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.

Before drafting, prove the client and data surface are ready. Save any large live responses to local files; do not paste raw exports into chat.

### Client And Destination

- Confirm `<client>` resolves to `docs/agent/clients/<client>.json` and read the matching Markdown brief when present.
- Confirm the client website URL is present and reachable.
- If Google Doc creation or update is requested, confirm the Drive destination before writing:
  - prefer `05 Content / Blogs` or an explicit blog/content folder in the client sidecar
  - use the Google Drive MCP to list/check the folder
  - do not fall back to `03 Audits` for blog content unless the user explicitly approves it
- If Monday task creation or update is requested, read the Monday board schema and confirm the target board/group before writing.

### Brief And Style

- Confirm an approved blog brief exists as JSON or Google Doc text.
- Confirm the brief contains target title/slug, primary keyword, secondary keywords or keyword expansion notes, search intent, audience, required structure, allowed HTML tags, approved links, source/claim constraints, banned phrases, CTA guidance, and word-count guidance.
- Confirm a client writing style guide exists. If not, pause drafting and route to the content-briefing/style-guide step: review recent live posts, derive a client writing style guide, save it, then return here.

### Data Access

- Confirm collection and blog sitemaps can be fetched or that fresh saved exports exist.
- Confirm SE Ranking access works or that fresh keyword/SERP exports are available:
  - tracked/expanded keyword data for the topic
  - top relevant SERP results for the primary keyword
- If the brief expects Search Console opportunity signals, confirm GSC access through the client setup or route to `ld-seo-maintenance` before continuing.

### Missing-input routing

If a preflight check fails, do not improvise around it. Route to the smallest dependency that fixes the blocker:

| Missing or blocked item | Route to |
| --- | --- |
| client sidecar, Drive/Monday/GA4/SE Ranking setup | `ld-seo-client-onboarding` |
| access failures, stale credentials, broken Drive folder, SE Ranking/GSC diagnostics | `ld-seo-maintenance` |
| approved blog brief, keyword strategy, SERP context, internal link plan, or style guide | `ld-seo-content-briefs` |
| final collection copy instead of blog copy | `ld-seo-shopify-collection-writing` |
| client-facing Google Doc creation/update | `google-drive:google-docs` |

Only continue when all required inputs are present, or when the user explicitly approves a documented limitation.

## Phase 1 - Validate Source Brief

When a brief JSON is available, confirm it contains:

- target slug or title
- primary keyword
- brief-defined HTML policy with allowed tags
- required headings or outline
- approved internal links and sources/external links, when links are expected
- banned phrases or claim restrictions
- CTA guidance

If working from a Google Doc brief only, read the Doc and confirm the same fields are present before drafting. Missing HTML policy or required structure is a blocker.

## Phase 2 - Sitemap-Grounded Internal Links

Fetch or export the client's Shopify collection and blog sitemap URLs before drafting. Save them locally, for example:

- `/tmp/<client>-collections-sitemap.json`
- `/tmp/<client>-blogs-sitemap.json`

Run the internal-link candidate helper:

```bash
python scripts/build_blog_internal_link_candidates.py \
  --brief-json /tmp/<client>-blog-briefs.json \
  --slug <slug> \
  --collections-sitemap /tmp/<client>-collections-sitemap.json \
  --blogs-sitemap /tmp/<client>-blogs-sitemap.json \
  --output /tmp/<client>-<slug>-internal-link-candidates.json
```

Use Codex judgement to select the final internal links:

- Choose **1-5 collection links** as the main commercial pathways.
- Add **0-3 blog links** only when they genuinely support the article and do not distract from the CTA.
- Prefer links with topical fit, keyword relevance, useful shopper intent, and natural placement in the article.
- Avoid self-links, utility pages, already-forced exact-match anchors, and links that would feel inserted for SEO only.
- Write a short rationale for every selected link in the brief before drafting.

If the sitemap has fewer than five relevant collection targets, use the best available links and document the limitation in the proof block.

## Phase 3 - Draft With Codex Judgement

Before drafting, review the top 3 ranking blog/article results for the primary keyword.

Use SE Ranking SERP data first where available. Save the raw response and a compact analysis file, for example:

- `/tmp/<client>-<slug>-primary-keyword-serp.json`
- `/tmp/<client>-<slug>-serp-content-patterns.json`

For each of the top 3 relevant blog/article results, capture:

- URL, title, ranking position, and source.
- Search intent served by the page.
- Heading/section pattern.
- Useful content angles, examples, decision frameworks, FAQs, comparison points, or trust signals.
- Internal/external link patterns when visible.
- Gaps or weaknesses our article can improve on.

Then apply Codex judgement:

- Adopt the best strategic patterns, not the wording.
- Prefer clearer structure, better local/client relevance, stronger product fit, and more useful internal links.
- Do not copy phrasing, paragraph order, examples, or proprietary claims from competitors.
- If fewer than 3 relevant blog/article results are available, document the limitation and use the best available SERP context.

Use the approved brief as the source of truth, then apply editorial judgement:

- Codex judgement is required for structure, flow, claim restraint, and deciding which secondary keywords genuinely fit.
- Match the client voice and article intent.
- Answer the searcher's actual need before adding SEO polish.
- Use primary and secondary keywords naturally; do not force every keyword.
- Use only product, service, statistical, medical/legal, sustainability, pricing, stock, shipping, origin, and competitive claims supported by the brief.
- Include approved internal links and source links only where they help the reader.
- Follow the brief-defined heading outline and HTML policy exactly.
- Avoid generic filler, unsupported superlatives, and banned phrases.

Default output is local Shopify article body HTML. Do not create a Google Doc, Monday task, or Shopify update unless explicitly requested after validation.

## Phase 4 - Validate Final HTML

Save the draft locally, then run:

```bash
python scripts/validate_blog_html_copy.py \
  --brief-json /tmp/<client>-blog-briefs.json \
  --slug <slug> \
  --html /tmp/<client>-<slug>-blog-copy.html \
  --output /tmp/<client>-<slug>-blog-copy-validation.json
```

If the brief is title-keyed instead of slug-keyed, use `--title "<Article Title>"`.

Fix every blocker before presenting the copy as publish-ready.

## Phase 5 - Client-Facing Google Doc Output

When the user asks to create or update a Google Doc, the Doc must be client-presentable rather than an internal QA dump.

Client-facing Docs must include:

- A short document title and client name.
- A concise article details table.
- A keyword strategy table with real volumes and intent/role.
- An internal linking table with anchor text and destination only, unless the client explicitly asks for strategy notes.
- A short SERP insights table when a competitor layer was used, showing the competitor, useful pattern, and how the draft adapts it.
- One final article draft only, formatted as it should read on the site, with actual headings and hyperlinked anchor text.
- Brief publishing notes when useful.

Client-facing Docs must not include:

- Raw validator output.
- Phrases such as `approved links included`, `validation blockers`, `validation warnings`, or `proof block`.
- Duplicate plain-text and raw-HTML versions of the same draft.
- Internal file paths, API notes, or operational scratchpad details.

Keep raw Shopify HTML in the local output file and validation proof in the Monday update or final agent response. The Google Doc is for a client, writer, or business owner to review.

## Quality Gate

- Blog structure follows the approved brief.
- All HTML tags are allowed by the brief.
- Primary keyword appears naturally near the start.
- Secondary keywords are used only when natural.
- Required headings are present.
- Banned phrases are absent.
- Internal links are selected from sitemap-grounded candidates and approved in the brief.
- External/source links are approved by the brief.
- Source/citation requirements are satisfied.
- Unsupported claims are absent.
- Word count fits the brief or the exception is documented.
- Top 3 relevant SERP competitors for the primary keyword were reviewed, with useful patterns adapted and copied language avoided.
- Any missing access or incomplete input was routed to the appropriate dependent skill before drafting.

## Proof Block

Report client, content type, article title or slug, brief source, local draft path, sitemap sources, SERP sources reviewed, collection candidates reviewed, blog candidates reviewed, final links selected, word count, primary keyword, secondary keywords used, validation blockers, warnings, unsupported-claim status, and assumptions.

The proof block belongs in the agent final response, local validation JSON, and/or Monday update. Do not place the proof block inside the client-facing Google Doc.

Append the client timeline with the brief source, outputs, validation result, caveats, and next action.
