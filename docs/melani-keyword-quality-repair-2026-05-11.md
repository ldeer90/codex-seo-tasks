# Melani the Label - Keyword Quality Repair

Date: 2026-05-11

## Decision

Do not regenerate or update the Melani collection content briefs from the current keyword inputs. The existing brief Docs are structurally useful, but the keyword layer needs repair first.

The main repair is to use live SE Ranking tracked keywords as the secondary keyword source, then add curated supplemental terms only when they are relevant to the specific collection. The existing placeholder-style secondary keywords such as `formal dresses online 1` must not be used in writer prompts.

## Evidence Checked

- Client sidecar: `docs/agent/clients/melani-the-label.json`
- Client brief: `docs/agent/clients/melani-the-label.md`
- Existing critique Doc: `1b73AMrNjpT3SydIwuiXvXGazN7oPZR1cP-RNJtc8cpA`
- Existing content brief Docs in Drive folder `1FgN47UW7vxWD3gD2KIcyghgy0ID8tcGI`
- Metadata Sheet: `1mdtafbzz2yfnaKL-ux0q0RvnkBeJEnnDedGdgF28PRo`
- Live SE Ranking project: `12019802`
- Fresh SE Ranking AU/US Data API spot checks on primaries and weak clusters

## High-Priority Fixes

1. `/collections/dresses` and `/collections/all-dresses` currently both use `womens dresses`. Keep `womens dresses` on `/collections/all-dresses`; treat `/collections/dresses` as a Shop All/curated page unless the client confirms it should replace All Dresses as the SEO target.
2. Replace placeholder secondary keywords in all content briefs with real live tracked keywords from SE Ranking.
3. Re-check fresh AU/US volumes before rebuilding brief JSON. Several sidecar/Sheet volumes are stale or inconsistent with fresh Data API checks.
4. Give low-confidence pages a merchandising check before final brief regeneration: `accessories`, `tailored`, `printed-dresses`, and `dresses`.
5. Keep supplemental keywords capped and reasoned. Do not use competitor brands, sibling page primaries, or terms the collection cannot satisfy.

## Repaired Keyword Map

| Slug | Recommendation | Primary Keyword | Real Secondary Keywords To Use | Supplemental Direction | Confidence |
|---|---|---|---|---|---|
| `dresses` | Do not treat as separate SEO brief unless confirmed. Avoid duplicating `all-dresses`. | Shop All / non-SEO target | None required; link out to `all-dresses`, `gowns`, `minis`, `midis`, `maxis`. | If copy is needed, write brand/shop-all copy, not an exact-match `womens dresses` SEO brief. | Medium |
| `all-dresses` | Own the broad dress hub. | `womens dresses` | `dresses australia`; `online dresses australia`; `dress shop australia`; `buy dress online australia` | Add only high-intent broad dress variants, not occasion-specific terms owned by child pages. | High |
| `gowns` | Keep as formalwear hub. | `formal dresses` | `formal dress`; `evening gown`; `evening gowns`; `cocktail dress`; `cocktail dresses australia`; `ball gown`; `evening dresses australia`; `long formal dress`; `formal gown` | `black formal dress`; `formal dresses for wedding guest`; `evening wear`; `gown dress`; colour terms only if products support them. | High |
| `midis` | Keep as midi-dress page. | `midi dress` | `midi dresses`; `midi dress for women`; `midi dress australia`; `midi dress with sleeves`; `midi party dresses`; `formal midi dress`; `womens midi dress`; `summer midi dress`; `midi dresses for women` | Occasion and sleeve variants where products support them. | High |
| `minis` | Keep as mini-dress page. | `mini dress` | `mini dresses`; `mini dress australia`; `short dress`; `going out dresses`; `party dress`; `bodycon dress`; `womens mini dress` | Party/going-out variants only where product sample supports fitted or occasion dressing. | High |
| `maxis` | Keep as maxi-dress page, but refresh US volume. | `maxi dress` | `maxi dresses`; `maxi dress australia`; `maxi dress for women`; `floral maxi dress`; `summer maxi dress`; `womens maxi dress`; `boho maxi dress` | Long-tail colour/occasion terms after product check. | High |
| `long-sleeve` | Keep as long-sleeve dress page. | `long sleeve dress` | `long sleeve dresses`; `long sleeve maxi dress`; `long sleeve midi dress`; `long sleeve formal dress` | Use sleeve/occasion variants; avoid top terms. | High |
| `lace-dresses` | Keep as lace-dress page. | `lace dress` | `lace dresses australia`; `lace midi dress`; `white lace dress`; `lace formal dress`; `lace wedding guest dress` | Wedding guest/formal variants if product set supports them. | High |
| `printed-dresses` | Reconsider primary. `printed dress` is too weak/stale; `floral dress` has stronger demand if the range is floral-led. | `floral dress` pending product check | `printed dresses`; `print dress`; `printed midi dress`; `printed maxi dress`; `floral dress` | Use `printed dress` as secondary/supporting, not primary, unless product range is not floral-led. | Medium |
| `bridal` | Keep, but copy must avoid implying bridal gowns if the range is occasion/white dresses. | `bridal dress` | `wedding guest dress`; `bridal shower dress`; `engagement dress`; `white dress australia`; `bridal gown australia`; `hen party dress` | Prioritise pre-wedding/white occasion terms over bridal-gown claims unless product data supports gowns. | Medium |
| `sets` | Keep, with clearer co-ord/matching-set cluster. | `two piece set` | `matching set australia`; `co-ord set australia`; `womens matching set`; `two piece outfit` | `two piece skirt set`; `two piece set skirt and top`; `two piece pants set`; exclude lounge terms unless the range is loungewear. | High |
| `tops` | Keep as going-out tops hub. | `going out tops` | `womens tops australia`; `dressy tops`; `fashion tops australia`; `going out tops` | `womens going out tops`; `black going out tops`; `going out tops for women`; colour terms only if products support them. | High |
| `crop-tops` | Keep as crop-top page. | `crop top` | `crop tops australia`; `womens crop top`; `linen crop top`; `formal crop top` | Add `floral crop top` only if floral cropped products are present; avoid cannibalising `printed-tops`. | High |
| `long-sleeve-tops` | Keep as long-sleeve top page. | `long sleeve top` | `long sleeve tops`; `long sleeve crop top` | Add fitted/crop variants only if product set supports them. | High |
| `lace-tops` | Keep as lace-top page. | `lace top` | `lace tops`; `lace blouse`; `white lace top`; `lace crop top` | Add colour/style terms only where products support them. | High |
| `printed-tops` | Keep, but make the product angle explicit. | `floral top` | `printed top`; `printed tops`; `floral top` | `floral tops for women`; `ladies floral tops`; `floral long sleeve top`; `floral corset top`; reject `floral tops target`. | High |
| `bodysuit` | Keep as bodysuit page. | `bodysuit` | `womens bodysuit`; `bodysuit australia`; `long sleeve bodysuit`; `black bodysuit` | Use fit/sleeve/colour variants only if products support them. | High |
| `pants` | Keep as women’s pants page. | `womens pants` | `tailored pants`; `wide leg pants`; `linen pants`; `dress pants womens` | Avoid generic tailoring-service terms. | High |
| `skirt` | Change primary wording for brief/title to plural category language. | `skirts` or `womens skirts` | `skirts australia`; `womens skirts`; `midi skirt`; `maxi skirt australia` | Keep `skirt` as broad supporting term, not writer-facing primary phrasing. | Medium |
| `mini-skirts` | Keep as mini-skirt page. | `mini skirt` | `mini skirts`; `mini skirt australia`; `short skirt`; `pleated mini skirt` | Add style variants only if product set supports them. | High |
| `midi-skirts` | Keep as midi-skirt page. | `midi skirt` | `midi skirts`; `midi skirt australia`; `pleated midi skirt`; `silk midi skirt`; `formal midi skirt` | Use fabric/style terms only if present. | High |
| `maxi-skirts` | Keep as maxi-skirt page. | `maxi skirt` | `maxi skirts`; `long skirt`; `maxi skirt australia` | Add fabric/silhouette variants after product check. | High |
| `jumpsuits` | Keep, but AU/US volume discrepancy needs a fresh export before final brief rebuild. | `jumpsuit` | `jumpsuits australia`; `womens jumpsuit`; `playsuit`; `formal jumpsuit`; `wide leg jumpsuit` | Use `playsuit` only if the collection includes playsuit-style products. | Medium |
| `swim` | Keep as swimwear page. | `swimwear` | `bikini`; `bikini australia`; `one piece swimsuit`; `womens swimwear`; `bikini set` | Avoid competitor/swimwear brand terms; focus on product types present. | High |
| `resort` | Keep, but avoid informational-only language. | `resort wear` | `holiday outfits`; `vacation dress`; `beach dress` | `resort wear dresses`; `resort wear sundresses`; `womens resort wear australia`; exclude men/plus-size/local brand terms. | Medium |
| `accessories` | Reconsider primary because products appear to be head pieces/accessories, not a broad accessories range. | `hair accessories` or `headpiece` pending product check | `hair accessories`; `statement earrings`; `headpiece`; `womens accessories` | Use `women's accessories` only as broad support; primary should match actual merch. | Medium |
| `tailored` | Needs merch confirmation before final brief. Current sidecar type is too broad/mixed. | `tailored clothing` pending product check | None confirmed live in project export during QA. | Consider `tailored pants`, `womens tailored clothing`, or a product-led page brief after confirming the collection purpose. | Low |

## Terms To Reject

- Competitor and retailer terms: `asos`, `zara`, `target`, `princess polly`, `meshki`, `showpo`, `white fox`, `tiger mist`, and similar.
- Sibling page primaries used as supplemental terms on another page unless they are internal-link anchors.
- Generic generated variants with no volume, such as `<primary> online 1`.
- Men’s, kids, maternity, plus-size, gym, travel, or local-service terms unless the collection actually contains that category.

## Next Build Rules

1. Re-export `PROJECT_listKeywords` and save it to `/tmp/melani-keywords.json`.
2. Export fresh AU and US volumes for all primary and live secondary keywords.
3. Build supplemental keywords per slug from SE Ranking related/similar/long-tail rows, but keep only terms with a written fit reason.
4. Rebuild `/tmp/melani-content-briefs.json`.
5. Run `validate_collection_content_briefs.py` and `critique_collection_content_briefs.py`.
6. Only update the 27 Google Docs after the repaired payload removes the missing-secondary and placeholder-keyword issues.
