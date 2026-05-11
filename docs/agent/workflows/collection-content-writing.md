# Collection Content Writing

Create publish-ready Shopify collection page HTML from an approved content brief.

## Use When

- The user asks to write final collection copy, produce Shopify HTML, QA writer output, or revise collection content.
- A content brief exists and has zero blockers.
- Triggered by `ld-seo-shopify-collection-writing`.

## Required Inputs

- Approved collection content brief JSON or Google Doc text.
- Client sidecar and brief.
- Collection URL and target slug.
- Approved internal link targets.
- Saved collection sitemap export or equivalent live collection URL list.
- SERP-derived word-count guidance for the collection body copy.

## Phase 0 - Access And Input Preflight

- Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.
- Confirm the client sidecar and Markdown brief exist; otherwise route to `ld-seo-client-onboarding`.
- Confirm the approved collection brief exists and has zero blockers; otherwise route to `ld-seo-content-briefs`.
- Confirm product context, keyword data, SERP context, Search Console signals when expected, brand voice, and approved internal links are present in the brief.
- Confirm the brief defines target length (`min_words` / `max_words` or equivalent) from a top-ranking page review. If absent, run Phase 2 and add SERP-derived length guidance before drafting.
- If Google Doc, Shopify, or Monday output is requested after drafting, confirm destination access first; access or filing blockers route to `ld-seo-maintenance`.

### Missing-input routing

Use `ld-seo-client-onboarding` for missing client setup, `ld-seo-maintenance` for access/destination blockers, `ld-seo-content-briefs` for incomplete briefs, and `ld-seo-shopify-blog-writing` if the target is a blog article rather than a collection page.

## Phase 1 - Validate Source Brief

Run content brief validation first when a brief JSON is available:

```bash
python scripts/validate_collection_content_briefs.py \
  --client-json docs/agent/clients/<client>.json \
  --briefs-json /tmp/<client>-content-briefs.json
```

Stop on blockers. If working from a Google Doc brief only, read the Doc and confirm it contains keyword strategy, product reality, SERP context, internal links, writer prompt, and QA checklist.

## Phase 2 - SERP-Guided Length And Structure

Before drafting, review the top ranking collection pages for the primary keyword. Use SE Ranking SERP results where available; otherwise use a fresh search and clearly record the source.

For the top 5-8 relevant collection pages:

- scrape the page or use a cached scrape from the last 30 days
- estimate descriptive collection copy length after excluding nav, product cards, filter controls, prices, and buttons
- record heading patterns, FAQ/bottom-copy usage, trust/delivery signals, and shopper decision angles
- ignore blocked pages, irrelevant editorial pages, and obvious scrape noise

Save the review locally, then summarise the target range:

```bash
python scripts/analyze_collection_serp_length.py \
  --serp-length-json /tmp/<client>-<slug>-serp-length-review.json \
  --output /tmp/<client>-<slug>-serp-length-guidance.json
```

Use Codex judgement:

- Set `content_requirements.min_words` and `max_words` from the competitor range, not from a fixed default.
- Prefer a range that matches useful shopper depth, usually near the lower-middle of top-ranking pages rather than the longest page.
- If top pages use substantial FAQs or bottom SEO copy and the Shopify page only supports one `<h2>` plus two `<h3>` sections, capture the intent in concise paragraphs instead of forcing an FAQ structure.
- Use **220-320 words only as a fallback** when SERP length review cannot be completed, and document that limitation in the proof block.

## Phase 3 - Sitemap-Grounded Internal Links

Before drafting, fetch or export the client's Shopify collection sitemap and save it locally, for example:

- `/tmp/<client>-collections-sitemap.json`

Then build collection link candidates:

```bash
python scripts/build_collection_internal_link_candidates.py \
  --brief-json /tmp/<client>-content-briefs.json \
  --slug <slug> \
  --collections-sitemap /tmp/<client>-collections-sitemap.json \
  --output /tmp/<client>-<slug>-collection-link-candidates.json
```

Use Codex judgement to select the final internal links:

- Choose **2-4 collection links** when the collection page naturally benefits from comparison paths.
- Prefer sibling recipient, occasion, product-type, and delivery-intent collections that help shoppers narrow choices.
- Avoid self-links, utility pages, forced exact-match anchors, and links that would feel inserted only for SEO.
- Add the selected links to the brief as approved internal links before validation.

If there are no useful collection links, document the reason in the proof block. Do not create an empty-link validation brief simply to pass the validator.

## Phase 4 - Draft With Codex Judgement

Use the writer prompt as the starting point, but apply editorial judgement:

- Codex judgement is required for natural phrasing, useful link placement, and deciding which supplemental keywords genuinely fit.
- Match brand voice and tone direction.
- Write for shoppers and business outcomes, not for crawlers.
- Use real product/category facts from the brief.
- Include the primary keyword near the opening sentence.
- Include supplemental keywords only where natural.
- Add internal links only when they help compare related ranges.
- Write enough useful copy to support shopper decisions. Follow the SERP-derived length range from the brief. Do not pad copy to match unusually long competitors.
- Avoid generic filler and banned phrases.

Output clean HTML only:

- one `<h2>`
- exactly two `<h3>`
- `<p>` tags for body copy
- optional approved `<a href="">anchor</a>` links inside paragraphs
- no `<h1>`, markdown, wrapper elements, scripts, styles, lists, or comments

## Phase 5 - Validate Final HTML

Save the draft to `/tmp/<client>-<slug>-collection-copy.html`, then run:

```bash
python scripts/validate_collection_html_copy.py \
  --briefs-json /tmp/<client>-content-briefs.json \
  --slug <slug> \
  --html /tmp/<client>-<slug>-collection-copy.html \
  --output /tmp/<client>-<slug>-collection-copy-validation.json
```

Fix every blocker before presenting the copy.

Default output is local Shopify collection body HTML. Do not create a Google Doc, Monday task, or Shopify update unless explicitly requested after validation.

## Quality Gate

- HTML structure is valid for Shopify collection content.
- Primary keyword appears naturally near the start.
- Banned phrases are absent.
- Internal links use approved URLs and anchors.
- At least 2 internal links are included when the sitemap provides useful related collection targets, unless the proof block documents why not.
- No unsupported claims appear.
- Word count fits the SERP-informed brief range unless Codex documents why it should differ.

## Proof Block

Report collection, brief source, word count, primary keyword, internal links included, validation blockers, warnings, and any assumptions.

Append the client timeline with the collection URL, output path or destination, validation result, caveats, and next action.
