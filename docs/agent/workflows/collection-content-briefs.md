# Collection Content Briefs

Creates writer-ready Google Docs for Shopify collection page copy, one Doc and one Monday task per SEO-priority collection.

**Use when:** the user asks for Shopify collection content briefs, collection page copy briefs, internal linking briefs, writer briefs, or LLM-ready content prompts.

---

## Phase 0 - Confirm client and load state

Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.

Read:

```bash
cat docs/agent/clients/<client>.md
cat docs/agent/clients/<client>.json
cat docs/agent/clients/<client>-timeline.md
cat docs/agent/skills/shopify-collection-content-briefs/SKILL.md
```

Run the client JSON validator immediately after reading the sidecar. Zero blockers are required before proceeding to any phase:

```bash
python scripts/validate_client_json.py --client-json docs/agent/clients/<client>.json
```

**Stop on any blocker.** Common blockers and resolutions:

- `missing_required_field` for `brand_voice` / `tone_direction` / `brand_display_name` — these must be filled before the writer prompt will reflect the brand. Ask the user or derive from the client's existing copy and confirm.
- `missing_collection_field` for `dominant_product_type` — check the Shopify admin or the product export and fill with the correct UPPERCASE product type. A wrong value sends internal links to the wrong collections.
- `missing_se_ranking_project_id` or engine IDs — retrieve from the SE Ranking project URL and add to the sidecar.
- `missing_drive_client_folder` — confirm the client folder ID from Drive before any Doc write.

**Warnings do not block** but must be documented in the proof block. The most common warning — `h1_primary_keyword_mismatch` — is a real SEO issue worth surfacing to the client as a recommendation alongside the brief.

If the client JSON does not exist yet, copy `docs/agent/clients/CLIENT_TEMPLATE.json`, rename it, and fill every REQUIRED field before running the validator.

### Missing-input routing

Route missing client setup to `ld-seo-client-onboarding`, access/GSC/Drive/Monday blockers to `ld-seo-maintenance`, stale collection SEO state to `ld-seo-collection-seo` plus `collection-seo-qa`, and final collection copy requests to `ld-seo-shopify-collection-writing`.

## Phase 1 - Collection SEO QA gate

Run the Collection SEO QA workflow first. Content briefs require synced collection state.

Required before brief generation:

1. Export live `PROJECT_listKeywords` to `/tmp/<client>-keywords.json`.
2. Save AU and US volume exports for all primary, tracked, and expansion keywords.
3. Save fresh current page scrape for included collection URLs.
4. Save structured per-slug SERP JSON.
5. **Keyword research and reasoning** — see Phase 1a below.
6. Save Search Console opportunity queries per collection when access is available.
7. Run:

```bash
python scripts/validate_collection_seo_state.py \
  --client-json docs/agent/clients/<client>.json \
  --seranking-keywords-json /tmp/<client>-keywords.json \
  --pages-json /tmp/<client>-pages.json \
  --serp-json docs/<client>-serp-scrape-<date>.json
```

Stop on blockers. Warnings may proceed only when documented in the proof block.

## Phase 1a - Keyword research and reasoning

This is an in-session reasoning step. Do not delegate it to a script. The goal is to produce a curated supplemental keyword list for each collection that a writer can actually use — not a raw dump of whatever SE Ranking returns.

### Fetch

For each included collection, call the SE Ranking Data API for the primary keyword:

- `DATA_getRelatedKeywords` — keywords with overlapping search intent
- `DATA_getSimilarKeywords` — semantically adjacent keywords
- `DATA_getLongTailKeywords` — lower-volume, higher-specificity variants

Batch where possible. Always fetch for the primary keyword, not the slug.

### Reason

For each collection, work through the candidates and decide what to keep. Apply this reasoning in order:

**1. Hard eliminate without further thought**
- Competitor or retailer brand names in the keyword (Kmart, Speedo, Monday Swimwear, Seafolly, Baku, Zimmermann, etc.)
- Product category mismatch — kids, maternity, period, mens, plus-size terms when the catalog doesn't carry those
- Primary keyword of another included collection — hard cannibalization; that keyword already has a home
- Zero AU volume unless Search Console shows a clear live-page opportunity. Low-volume niche terms can stay when they describe the collection exactly and have buyer intent.

**2. Evaluate opportunity**
For each surviving candidate, ask:
- **Volume vs difficulty** — is this achievable? A keyword at KD 65 needs a strong domain authority case. Prefer KD < 50 unless the volume is very high.
- **Intent match** — does the searcher want to browse/buy the product on this specific page? Informational queries (how-to, what-is) rarely convert on collection pages.
- **Collection fit** — does this keyword clearly belong *here* rather than a sibling collection? "Backless formal dress" belongs on Gowns, not All Dresses, even if All Dresses has higher volume.
- **GSC signal** — if the collection already appears at position 8–25 for this query, it's a stronger prioritisation signal than raw volume alone.
- **Writer utility** — can a writer naturally use this keyword in 200 words of copy? If it's awkward to place, it won't add value even if it ranks.

**3. Reject near-duplicates**
Keep the best form of each concept. "Black formal dress" and "black formal dresses" are the same. Keep the higher-volume singular form unless the plural is clearly dominant in SERP.

**4. Assign and cap**
- Assign each keyword to the one collection where it fits best. Do not put the same keyword in two briefs.
- Target 8–12 good keywords per collection. Fewer is better than padding with marginal terms.

### Produce

Write the reasoning result to `/tmp/<client>-supplemental-keywords.json` in `by_slug` format:

```json
{
  "by_slug": {
    "gowns": [
      {
        "keyword": "backless formal dress",
        "au_volume": 1900,
        "us_volume": 2400,
        "difficulty": 38,
        "intent": "Commercial",
        "source": "SE Ranking AU related",
        "reasoning": "High-relevance to Gowns — backless is a product feature. Good KD for the domain. GSC shows position 14 with 120 impressions, winnable."
      }
    ]
  }
}
```

Include `reasoning` on every keyword. It becomes the brief's signal for why this keyword belongs, and it catches your own mistakes — if you can't write a concise reason, the keyword probably doesn't belong.

If a collection comes back thin (< 5 accepted keywords after reasoning), fetch again with a broader seed — try the collection's H1, a product type, or a synonym of the primary keyword. Document any persistent gaps in the proof block.

### Validation after reasoning

Run `research_supplemental_keywords.py` as a mechanical sanity check after the reasoning step — it will catch anything you missed (brand names, catalog mismatches, cross-collection duplication) and produce the `opportunity_score` breakdown used by the builder:

```bash
python scripts/research_supplemental_keywords.py \
  --client-json docs/agent/clients/<client>.json \
  --raw-keywords-json /tmp/<client>-supplemental-keywords.json \
  --volume-json-au /tmp/<client>-volumes-au.json \
  --volume-json-us /tmp/<client>-volumes-us.json \
  --gsc-json /tmp/<client>-gsc-opportunities.json \
  --output /tmp/<client>-supplemental-keywords-scored.json \
  --diagnostics
```

The `filtered_out` list tells you if your reasoning missed anything obvious.

## Phase 2 - Product and page grounding

For every included Shopify collection:

- scrape the live collection page for title, H1, meta, visible copy, word count, and internal links
- fetch product samples from Shopify collection/product JSON where available
- preserve product titles, product types, and sample counts
- do not invent product facts when a collection has thin or blocked product data

Save product samples to `/tmp/<client>-products.json`.

## Phase 3 - Build and validate brief inputs

Build deterministic brief input JSON:

```bash
python scripts/build_collection_content_brief_inputs.py \
  --client-json docs/agent/clients/<client>.json \
  --seranking-keywords-json /tmp/<client>-keywords.json \
  --volume-json-au /tmp/<client>-volumes-au.json \
  --volume-json-us /tmp/<client>-volumes-us.json \
  --pages-json /tmp/<client>-pages.json \
  --serp-json docs/<client>-serp-scrape-<date>.json \
  --product-json /tmp/<client>-products.json \
  --supplemental-keywords-json /tmp/<client>-supplemental-keywords-scored.json \
  --gsc-json /tmp/<client>-gsc-opportunities.json \
  --output /tmp/<client>-content-briefs.json
```

The builder must fail unless every collection has:

- primary keyword AU volume, plus US volume for AU+US clients
- current title, H1, and copy summary
- product sample context
- structured SERP context
- supplemental SE Ranking keyword opportunities with real volumes
- Search Console opportunities, unless GSC access is unavailable and recorded as a blocker/warning
- five internal link candidates, where five other included collections exist
- writer/LLM prompt and QA checklist

Missing meta descriptions are warnings, not blockers. Preserve the missing state in
the brief so the writer sees the current page reality.

Then validate:

```bash
python scripts/validate_collection_content_briefs.py \
  --client-json docs/agent/clients/<client>.json \
  --briefs-json /tmp/<client>-content-briefs.json
```

Drive and Monday writes require zero blockers.

## Phase 4 - Render one Doc body per collection

```bash
python scripts/render_collection_content_brief_doc.py \
  --briefs-json /tmp/<client>-content-briefs.json \
  --output-dir /tmp/<client>-content-brief-docs
```

Spot-check at least three briefs before writing to Drive:

- one high-volume category
- one long-tail/occasion category
- one collection with warnings or thin data

Check that each brief includes real keyword volume, product facts, SERP patterns, natural keyword instructions, and five internal links.

### Required client-ready structure

Use the Salad Servers Wedding Catering page-copy format for every client-facing collection document. This is the current version of the earlier Shop Rongrong table-led structure. The rendered Google Doc must be table-led, clean, and client-ready.

For final Google Docs, use native Google Docs tables. Do not paste markdown pipe tables as the final client-facing table format; markdown tables are acceptable only for local source files or chat previews. Read back the Doc structure and confirm table count/dimensions where possible.

1. `Overview` table with website, page, page type, keyword source, and content approach.
2. `Keywords To Work Into The Page` table with keyword, monthly search volume, and a short natural-use note. These volumes must come from SE Ranking keyword research, not Search Console impressions.
3. `Internal Links` table with anchor text and destination.
4. `Recommended Heading Hierarchy` table with page section, recommended heading, heading level, and SEO role.
5. `SEO Review` table with overall structure, keyword coverage, search intent, page balance, and current-page notes.
6. `Example Copy` section with page title, meta description, H1, optional hero subheading, and section-by-section page copy.

For blog/article or information-page briefs that are not final copy requests, keep the same table-led structure but replace `Example Copy` with `Article Requirements`, `Writer Notes`, or `FAQs To Cover`. Do not publish a plain outline-only Google Doc when the user has asked for a client-facing brief.

Do not include raw research dumps, internal workflow notes, validator labels, proof blocks, or implementation chatter in the client-facing Doc. Final Shopify HTML belongs in the optional writing phase unless the user explicitly asks for clean HTML.

## Client-Presentable QA

Before Drive or Monday writes, critique the rendered briefs with the standard a client, SEO specialist, content writer, and business owner would expect:

- The brief is grounded in real keywords, real product/category context, real SERP patterns, and Search Console where available.
- The writing guidance is specific enough for a writer or LLM to produce useful HTML copy without inventing facts.
- Internal links are natural, varied, and helpful to the customer journey.
- The prompt avoids generic SEO filler and reflects the brand voice.
- Any warnings are useful and honest, not hidden implementation errors.

## Optional Phase 4a - Write final collection copy

Only run this phase when the user explicitly asks for final Shopify collection copy after briefs are approved.

Use `ld-seo-shopify-collection-writing` and `docs/agent/workflows/collection-content-writing.md`.

Default to local drafts first:

```bash
python scripts/validate_collection_html_copy.py \
  --briefs-json /tmp/<client>-content-briefs.json \
  --slug <slug> \
  --html /tmp/<client>-<slug>-collection-copy.html \
  --output /tmp/<client>-<slug>-collection-copy-validation.json
```

Google Doc, Shopify, or Monday writes are follow-up actions only after the local draft validates with zero blockers.

## Phase 5 - Create Google Docs

Use `GoogleWorkspaceClient.create_doc(..., folder_id=<folder_id>)`.

Default folder:

1. `client_json.drive.folders.05_content`, if present
2. `client_json.drive.folders.content_briefs`, if present
3. stop and ask before using another folder

Create one Doc per collection:

```python
from seo_automation_mcp.google_clients import GoogleWorkspaceClient

g = GoogleWorkspaceClient(delegated_subject="hello@agents.digital")
result = g.create_doc(
    title=f"<Client> - Collection Content Brief - <Collection Name>",
    body=<rendered_text>,
    folder_id=<folder_id>,
)
```

After each Doc, update the sidecar collection with:

- `content_brief_doc_id`
- `content_brief_url`
- `content_brief_updated_at`
- `internal_link_targets`
- `brief_status`

Update `deliverables.collection_content_briefs` with coverage, folder ID, updated date, and document count.

## Phase 6 - Create Monday tasks

Read board schema first:

1. `get_board_info(boardId=<board_id>)`
2. Create one task per collection in the configured target group.
3. Task title: `Collection Content Brief - <Collection Name>`
4. Task update includes:
   - Google Doc URL
   - collection URL
   - primary keyword and volumes
   - internal link target count
   - validator result
   - warnings, if any

If the board schema is ambiguous, stop and ask before writing tasks.

After writing, read back a sample of Google Docs and confirm every Monday task URL exists before marking the run complete.

## Final proof block

Every successful run ends with:

- Client and market scope
- Collections covered
- Google Docs created
- Monday tasks created
- Drive folder ID used
- Keyword source and live SE Ranking export date
- Validator blockers: `0`
- Remaining warnings, or `none`
- Client timeline updated with proof summary and next action

## Common failures

- **Sidecar stale after SE Ranking changes** - re-export keywords, sync sidecar, and rerun collection SEO validation.
- **Missing product context** - fetch Shopify collection/product JSON or scrape product cards before generating briefs.
- **SERP JSON is flat or stale** - regenerate structured per-slug SERP JSON.
- **Fewer than five link targets** - only acceptable when the site has fewer than six included collections; document it as a warning.
- **Monday board schema unclear** - read board info and ask before creating items.
