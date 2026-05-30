---
name: ld-seo-travelkon-internal-linking
description: TravelKon-specific internal linking workflow using sitemap, GA4, Search Console, priority clusters, and reusable link maps for blogs, categories, and products.
---

# LD SEO TravelKon Internal Linking

Use this skill when the user asks for TravelKon internal linking, link maps, anchor suggestions, blog-to-product links, destination cluster links, or reusable TravelKon link guidance.

This is a client-specific companion skill. It does not replace the general `ld-seo-content-briefs` or `ld-seo-shopify-blog-writing` skills; it supplies the TravelKon internal-link evidence and selection rules those workflows should use.

## Required Reading

1. `docs/agent/clients/travelkon.md`
2. `docs/agent/clients/travelkon-timeline.md`
3. `docs/agent/clients/travelkon-internal-linking-map.md`
4. Latest CSV exports in `var/reports/travelkon-internal-linking/`
5. If writing or briefing blog content, also read `docs/agent/skills/ld-seo-content-briefs/SKILL.md` or `docs/agent/skills/ld-seo-shopify-blog-writing/SKILL.md` as appropriate.

## Source Files

Latest baseline generated 2026-05-19:

- Summary map: `docs/agent/clients/travelkon-internal-linking-map.md`
- Raw full map CSV: `var/reports/travelkon-internal-linking/travelkon-internal-linking-map-2026-05-19.csv`
- Raw full map JSON: `var/reports/travelkon-internal-linking/travelkon-internal-linking-map-2026-05-19.json`
- Priority pages CSV: `var/reports/travelkon-internal-linking/travelkon-internal-linking-priority-pages-2026-05-19.csv`
- Link opportunities CSV: `var/reports/travelkon-internal-linking/travelkon-internal-linking-opportunities-2026-05-19.csv`
- Export script: `var/tmp/travelkon_internal_linking_export.py`
- Output builder: `var/tmp/build_travelkon_internal_linking_outputs.py`
- Downloaded sitemap XML: `var/tmp/travelkon-sitemaps/`

## Evidence Rules

- Treat the TravelKon Rank Math sitemap as a query-string sitemap source. `https://www.travelkon.com.au/?sitemap=1` works; the robots-listed `https://www.travelkon.com.au/sitemap_index.xml` returned 404 on 2026-05-19.
- Use GA4 web property `properties/387124003`, not the app notification property.
- Use Search Console domain property `sc-domain:travelkon.com.au` via `seo@agents.digital` when available.
- Prefer the most recent generated map. If it is older than 60 days, regenerate before major linking recommendations.
- Search Console rows are thresholded. Do not expect GSC clicks/impressions to equal GA4 sessions/revenue.
- Before bulk link implementation, sanity-check target product availability, plan inclusions, destination coverage, and whether the target page is still live.

## Link Selection Rules

1. Pick the destination/topic cluster first: Japan, Europe & UK, Bali/Indonesia, Vietnam, Singapore, Thailand, South Korea, China/HK/Macau, USA/Canada, Global/Regional, or Support/eSIM Education.
2. Use the cluster's top category as the default hub target.
3. Add product links only where the source page has commercial or troubleshooting intent.
4. Use Search Console query language for anchors, but avoid repeated exact-match anchors across many pages.
5. Keep blog articles natural: usually 2-4 internal links for short articles and 4-7 for long guides.
6. Never use cart, checkout, account, upload, pagination, legal, admin, or PDF URLs as source pages for a planned link map.
7. Use support pages as trust/support links, not as primary commercial hubs, unless the article is about setup, activation, data usage, or troubleshooting.

## Cluster Pattern

- Destination blog -> destination eSIM category -> best-fit product.
- Destination SIM/eSIM comparison blog -> both eSIM and SIM category where available -> one priority product.
- Generic eSIM education blog -> global/regional eSIM category -> relevant destination category if the section mentions a destination.
- Troubleshooting/support blog -> relevant setup/troubleshooting page -> destination product/category only where country-specific.
- Category hub -> top products in the same destination/region.
- Category hub -> sibling SIM/eSIM category when the user intent naturally compares both.

## Regeneration Flow

Run from the repo root:

```bash
PYTHONPATH=src .venv/bin/python var/tmp/travelkon_internal_linking_export.py
python3 var/tmp/build_travelkon_internal_linking_outputs.py
```

Then read back:

```bash
python3 - <<'PY'
import csv, json
print(json.load(open('var/reports/travelkon-internal-linking/travelkon-internal-linking-export-meta-2026-05-19.json')))
rows=list(csv.DictReader(open('var/reports/travelkon-internal-linking/travelkon-internal-linking-opportunities-2026-05-19.csv')))
print(len(rows), rows[0] if rows else None)
PY
```

Update filenames/dates when regenerating. If you create a new dated map, update `docs/agent/clients/travelkon-internal-linking-map.md` so future agents read the latest summary.

## Deliverables

For a quick linking recommendation, return:

- target cluster
- target page/hub
- 3-8 source URLs
- recommended anchor variants
- why those links matter
- caveats such as product availability or crowded/cannibalising topics

For a reusable map refresh, produce:

- raw map CSV/JSON
- priority pages CSV
- opportunities CSV
- short markdown summary in `docs/agent/clients/travelkon-internal-linking-map.md`
- timeline entry in `docs/agent/clients/travelkon-timeline.md`

## Proof Block

Include date range, sitemap source and URL count, GA4 property, Search Console property/subject, generated files, opportunity count, caveats, and whether the client timeline was updated.
