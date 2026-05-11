# Client Sidecar Map

Generated from the client briefs, `config/site-access.json`, existing JSON sidecars, and lightweight Shopify collection discovery on 2026-05-11.

This map separates two ideas:

- **Operational sidecar**: client routing, Drive, Monday, GA4, SE Ranking, brand voice, and workflow metadata.
- **Collection sidecar**: operational sidecar plus validated Shopify/ecommerce `collections[]` for collection SEO, briefs, and final collection copy.

## Canonical Sidecar Shape

Every real client sidecar should start with:

| Field | Purpose |
|---|---|
| `client` | Canonical client name used in Docs and tasks. |
| `brand_display_name` | Brand typography for copy. |
| `brand_voice` | One paragraph of writing guidance. |
| `tone_direction` | Short instruction for what copy should lead with and avoid. |
| `domain` | Primary domain without protocol. |
| `market_scope` | `AU`, `US`, or `AU+US`. |
| `usp` | Supported factual value proposition. |
| `brand_denylist` | Competitors/retailers to filter from keyword research. |
| `se_ranking.project_id` | SE Ranking project ID. |
| `se_ranking.engines` | Site engine IDs, not volume region IDs. |
| `drive.client_folder_id` | Root Drive folder. |
| `drive.folders` | `03_audits`, `05_content`, `07_reports`, and any known specialty folders. |
| `monday.board_id` | Client board ID. |
| `monday.groups.current_month` | Confirmed board group ID/name before task writes. |
| `ga4_property` | Default GA4 property for SEO work. |
| `deliverables` | Existing Docs/Sheets/cache outputs with dates and coverage. |
| `collections` | Shopify/ecommerce collection state when the collection workflows apply. |

For collection-capable clients, each included collection should contain:

| Field | Purpose |
|---|---|
| `slug`, `url`, `class` | Stable collection identity and classification. |
| `dominant_product_type` | Product/category reality for link and brief logic. |
| `primary_keyword`, `au_volume`, `us_volume` | Target keyword and volume data. |
| `current_title`, `current_h1`, `current_meta_description`, `last_scraped` | Live page state. |
| `competitor_top3_urls` | SERP competitors used for metadata/content strategy. |
| `content_requirements` | SERP-derived copy length and structure guidance. |
| `internal_link_targets` or `internal_links` | Sitemap-grounded link plan. |

## Inferring High-Priority Collections

Use GA4 as the first source of truth for commercial priority, then enrich with keyword/SERP/product evidence before creating briefs.

1. Run `ga4_collection_opportunities` for each Shopify collection-capable client with `channel = Organic Search`, `path_prefix = /collections/`, and a current/comparison period that matches reporting context.
2. Seed or update `collections[]` from the returned opportunities, preserving `priority_bucket`, `priority_score`, current sessions, revenue, conversions, purchases, and deltas.
3. Promote `Protect / Rescue`, `Protect`, `Grow`, and `Monetise` collections into the first sidecar pass. Treat `Build / Validate` as backlog until SE Ranking/GSC/product reality supports it.
4. Cross-check every promoted collection against Shopify collection discovery, SE Ranking keyword volume, SERP length/intent, product availability, and internal-link candidates before briefing or writing copy.
5. Keep GA4 metrics as evidence fields, not copy instructions. The sidecar still needs factual product context and brand voice before content workflows run.

### GA4 Priority Snapshot - 2026-04-01 To 2026-04-30

Comparison period: 2025-04-01 to 2025-04-30. Channel: Organic Search. Path prefix: `/collections/`. Snapshot generated 2026-05-11 with `ga4_collection_opportunities`; refresh before creating a new monthly roadmap.

| Client | Top GA4-priority collection signals |
|---|---|
| Avenue Hampers | `shop-all-1` Protect / Rescue; `easter-hampers` Protect / Rescue; `get-well-soon` Protect / Rescue; `build-your-own-hamper` Protect; `care-packages` Protect; `gifts-for-him` Monetise with revenue decline. |
| Little Shop of Happiness | `care-packages-1` Protect / Rescue; `mothers-day-hampers` Protect; `hampers-brisbane` Protect / Rescue; `confetti-explosion-box` Protect; `hampers-for-kids` Protect; `birthday-hampers` Protect. |
| Melani the Label | `dresses` Protect / Rescue; `all-dresses` Protect / Rescue; `maxis` Monetise with major historic revenue decline; `new-arrivals` Rescue; `sets` Monetise; `bridal` Protect. |
| Salad Servers Direct | `party-salads` Protect / Rescue; `bulk-salads` Protect; `salads-all` Monetise; `curries-and-stews` Monetise; `hot-meals` Monetise. |
| Shop Rongrong | `new-arrivals-1` Protect / Rescue; `sale` Monetise; `sticker-books` Monetise; `stickers` Rescue; `pet-tape` Monetise; `planner-and-sticker-bundles` Monetise. Product JSON discovery still needs investigation before a full collection sidecar. |

## Client Status

| Client | JSON sidecar | Collection discovery | Workflow fit | Priority | Next action |
|---|---:|---:|---|---|---|
| Acorn Rentals | Missing | 0 collections | Operational/reporting only | Low | Create lightweight operational sidecar only if needed for reports; collection SEO not applicable. |
| Agents Digital | Missing | Not run; internal agency site | Operational/reporting only | Low | Create internal operational sidecar only if recurring reports or internal roadmap work need it. |
| Avenue Hampers | Missing | 103 discovered; 65 non-empty candidates | Collection sidecar needed | High | Create `avenue-hampers.json`, then clean collection classes and keyword map. |
| Ducati Melbourne | Missing | 0 collections | Operational/reporting or dealer SEO, not Shopify collection | Medium | Create operational sidecar; use a dealer/category workflow if packaged later. |
| Joe Rascal parent | Missing | Parent only | Routing/rollup only | Medium | Do not create collection sidecar; create parent operational sidecar only after Drive folder scan is repaired. |
| Joe Rascal Harley | Missing | 0 collections | Operational/reporting or dealer SEO, not Shopify collection | Medium | Create operational sidecar if recurring reports need it. |
| Joe Rascal Global | Missing | 0 collections | Operational/reporting; folder setup incomplete | Medium | Add site-access client route and Drive folder before a full sidecar. |
| Little Shop of Happiness | Missing | 215 discovered; 28 non-empty candidates | Collection + blog sidecar needed | High | Create `little-shop-of-happiness.json`; reuse writing style guide and content folders. |
| Melani the Label | Exists | 26 discovered; 25 non-empty candidates | Collection sidecar live | Done | Keep validating; resolve known H1/keyword warnings over time. |
| Mr Gadget | Exists, test-only | Not applicable | Editorial, not Shopify collection | Exclude | Do not use collection sidecar workflow. Needs editorial SEO sidecar/workflow if activated. |
| Salad Servers Direct | Missing | 31 discovered; 29 non-empty candidates | Collection sidecar needed | High | Create `salad-servers-direct.json`; confirm `05_content` folder or equivalent. |
| Shop Rongrong | Missing | 82 discovered; only 1 non-empty by Shopify product JSON | Needs investigation | Medium | Confirm live canonical and whether product JSON is blocked/unusual before sidecar creation. |
| TravelKon | Missing | 0 collections | Operational/reporting or product/category workflow, not Shopify collection | Medium | Create operational sidecar for reports; collection SEO not applicable as currently detected. |

## Source Facts By Client

### Acorn Rentals

- Domain: `www.acornrentals.com.au`
- GA4: `properties/423383715`
- Analytics subject: `hello@agents.digital`
- Drive root: `1M2MXfkRFsAMy5nFoM2m7miNOnjBEkvoj`
- Audits folder: `1ZGPxHEygUPhes-0twOuoTkDBygIW-tAs`
- Reports folder: `1gupoXp_cjGHm3ixSEIs3PFpKTb2ataJ2`
- SE Ranking project: `11444792`, 26 keywords
- Monday board: `5026665037`
- Sidecar type: operational only

### Agents Digital

- Domain: `agents.digital`
- GA4: `properties/516619587`
- Analytics subject: `hello@agents.digital`
- Drive root: `1ZpzgOmzDHmb01ebq_N0lejCI74r3s1jd`
- Monday boards: Agency Ops boards, primary `5025901101`
- Sidecar type: internal operational only

### Avenue Hampers

- Domain: `www.avenuehampers.com.au`
- GA4: `properties/356217618`
- Analytics subject: `seo@agents.digital`
- Drive root: `1LGXJQosWUROG5s4MVxbNaFgMvXFd90en`
- Audits folder: `1zmOww76CYrUhQOB_wcQvUKUbcFsFzYmF`
- Content folder: `1i7UBwahKIavOVPXmO9CojLz9IHpBlSX7`
- Reports folder: `1VzFY_bDRX9jDNCeGzC53m5uKYsvOkacG`
- SE Ranking project: `11562866`, 167 keywords
- Monday board: `5026978865`
- Discovery: 103 collections after filter; 65 non-empty candidates; 38 empty
- Sidecar type: full collection sidecar
- Immediate known collection: `gifts-for-him`, target keyword candidate `hampers for men`, SERP-derived content range `350-700` words from 2026-05-11 review.

### Ducati Melbourne / Joe Rascal Ducati

- Domain: `www.ducatimelbourne.com.au`
- Related stream: `joerascalducati.com.au`
- GA4: `properties/402313624`
- Analytics subject: `seo@agents.digital`
- Drive root: `157-ddATrb2byi0VMJYKg9JET4RzqIFFr`
- Audits folder: `1zqzxqVT2aeJ1aahoGW3EM0qEoqomnB5x`
- Reports folder: `1dzj65zJm15qNxV0AK0VyefNsr1prGkd2`
- SE Ranking project: `10993280`, 100 keywords
- Monday board: `5025418481`
- Discovery: 0 Shopify collections
- Sidecar type: operational/dealer SEO only

### Joe Rascal Parent

- Drive root: `14gHf6UZjgZ751CUP6iLz3Sf6WTTQBWSN`
- Monday parent board: `5026853960`
- Status: parent/rollup record, not a collection SEO client
- Blocker: Drive subfolder scan needs repair before it becomes a reliable operational sidecar.

### Joe Rascal Harley

- Domain: `www.joerascalharley.com.au`
- GA4: `properties/513354197`
- Analytics subject: `seo@agents.digital`
- Drive root: `1XENbhUku8qau7HM5I7D9ivtIhrKpfU0s`
- Audits folder: `1zea_22Ldi8q7QU0qkBs53HxZXwA68AIJ`
- Reports folder: `1Vutz3IWesdKE21e4mw10P8V9Yw_cE6bD`
- Extra on-page folder: `1LMnA_YaJJq-e2h3E6D5v72ooOtLx5Xu6`
- SE Ranking project: `10993304`, 302 keywords
- Monday board: `5025418382`
- Discovery: 0 Shopify collections
- Sidecar type: operational/dealer SEO only

### Joe Rascal Global

- Domain: `joerascal.com`
- GA4: `properties/525910399`
- Analytics subject: currently routed through Joe Rascal Harley fallback
- Drive root: no dedicated folder
- Monday board: parent Joe Rascal `5026853960`
- Discovery: 0 Shopify collections
- Sidecar type: operational only after route/folder repair
- Blockers: add `joe rascal global` to `config/site-access.json`, create/confirm Drive folder.

### Little Shop of Happiness

- Domain: `www.littleshopofhappiness.com.au`
- GA4: `properties/399571311`
- Analytics subject: `seo@agents.digital`
- Drive root: `1wN3HSAcKrkXRLxuFA0OlHyGDqLDo9hx7`
- Audits folder: `1MFU9-6X1uJys3IyIod7KFziJz40K5J8C`
- Content folder: `1YuwEjmDT1cRsZp3aVPXzDxmjp8GadJaV`
- Blogs folder: `1OP37d2-kZS9EhV5dWbE9xTI613FCdmyV`
- Reports folder: `1D6IKdB56uC3uvgT9fOccT28Rl4zPo-qs`
- SE Ranking project: `11562890`, 228 keywords; duplicate inactive project `11660195`
- Monday board: `5026978841`
- Discovery: 215 collections after filter; 28 non-empty candidates; 187 empty
- Sidecar type: full collection/blog sidecar
- Reuse: `little-shop-of-happiness-writing-style.md`

### Melani the Label

- Domain: `melanithelabel.com`
- GA4: `properties/369346274`
- Analytics subject: `seo@agents.digital`
- Drive root: `1HWLcsHS38P5u_d_vfrWux3LaRVln9iMJ`
- Audits folder: `1j_tdnIT0mia1rJz0P2DU4zcs19jpQzS6`
- Reports folder: `1Gfvxg4DuAzv_W5bGBJ62r09ap0woX6Eu`
- SE Ranking project: `12019802`, 139 keywords / 278 pairs
- Engines: AU `1176139`, US `1179880`
- Monday board: `5028353257`
- Discovery: 26 collections after filter; 25 non-empty candidates
- Sidecar type: existing full collection sidecar
- Validator: 0 blockers, 10 H1/primary keyword warnings

### Mr Gadget

- Domain: `mrgadget.com.au`
- Status: test client only
- Site type: editorial publisher, not Shopify
- GA4: not connected
- SE Ranking: not created
- Monday board: `5028393076`
- Sidecar type: existing test/editorial sidecar only
- Validator: fails collection sidecar checks by design

### Salad Servers Direct

- Domain: `direct.saladservers.com.au`
- GA4: `properties/378662387`
- Analytics subject: `seo@agents.digital`
- Drive root: `1VTJy6FaSqLkOyRxaf7ZiAQuoIQVXatyf`
- Audits folder: `1JIyzafg5Q49ExzvJMqCR-Bsu1Hm16N9o`
- Keyword/meta folder: `1KAg-cobu8wSxFGDeT-nyw3mIQQYXWS0e`
- Reports folder: `1RrX29zwEAiEv-SJFiqfSfkZAqJuKa6Sp`
- SE Ranking project: `11273891`, 198 keywords
- Monday board: `5025899615`
- Discovery: 31 collections after filter; 29 non-empty candidates; 2 empty
- Sidecar type: full collection sidecar
- Blocker to confirm: content folder ID; current brief does not list a standard `05 Content`.

### Shop Rongrong

- Domain: likely `www.shoprongrong.com` for crawls; GA4 brief stores `http://shoprongrong.com`
- GA4: `properties/354478921`
- Analytics subject: `seo@agents.digital`
- Drive root: `1TTxwqCl5JurXCyva9kGK9rz5v66YzaXU`
- Audits folder: `1ywpJIkNJddGRLdaGTiAnyDksoxP85pWD`
- Reports folder: `1K66iztEtBye5mCowq-chwTkMr0E1uati`
- SE Ranking project: `11560829`, 519 keywords; duplicate inactive project `11619515`
- Monday board: `5026978284`
- Discovery: 82 collections after filter; only 1 non-empty by Shopify product JSON
- Sidecar type: needs investigation before full collection sidecar
- Blocker: confirm canonical domain and why product JSON returns empty for most collection URLs.

### TravelKon

- Domain: `www.travelkon.com.au`
- SEO GA4: `properties/387124003`
- App/cross-platform GA4: `properties/532415351`
- Analytics subject: `seo@agents.digital`
- Drive root: `175zcM_g56_jtpU1m9bzAMFvLFahXAqS3`
- Audits folder: `1aEbqpVIWbkaz8dkMZGKa14v6b5iJn_Jb`
- Reports folder: `1HCuM9DP0xZ9sjms8Y6C1AZhgWap_A5pr`
- SE Ranking project: `11580098`, 113 keywords
- Monday board: `5026863900`
- Discovery: 0 Shopify collections
- Sidecar type: operational/reporting only, or future product/category workflow if needed

## Recommended Build Order

1. Avenue Hampers: create collection sidecar first; already has content folder and active collection request.
2. Little Shop of Happiness: create collection/blog sidecar; strongest content workflow fit.
3. Salad Servers Direct: create collection sidecar after confirming content folder.
4. Shop Rongrong: investigate collection/product discovery before sidecar creation.
5. Operational-only sidecars: Acorn Rentals, TravelKon, Ducati Melbourne, Joe Rascal Harley.
6. Repair before sidecar: Joe Rascal Global and Joe Rascal parent Drive/routing.
7. Exclude from collection sidecars: Agents Digital and Mr Gadget.

## Validation Commands

For every created or updated sidecar:

```bash
.venv/bin/python scripts/validate_client_json.py --client-json docs/agent/clients/<client>.json
```

For collection-capable sidecars, after live keyword/page/SERP exports:

```bash
.venv/bin/python scripts/validate_collection_seo_state.py \
  --client-json docs/agent/clients/<client>.json \
  --seranking-keywords-json /tmp/<client>-keywords.json \
  --pages-json /tmp/<client>-pages.json \
  --serp-json docs/<client>-serp-scrape-<date>.json
```
