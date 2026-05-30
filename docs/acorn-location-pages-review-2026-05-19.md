# Acorn Rentals Location Page Review - 2026-05-19

## Scope

Reviewed the live Acorn Rentals sitemap and sampled the main location page sets:

- State pages: `/new-south-wales/`, `/victoria/`, `/queensland/`, `/south-australia/`, `/western-australia/`
- City accident pages: `/car-accident-sydney/`, `/car-accident-melbourne/`, `/car-accident-brisbane/`, `/car-accident-perth/`, `/car-accident-adelaide/`
- Service-area pages: `/service-areas/` and `/service-areas/*`

Raw audit exports:

- `docs/acorn-location-pages-review-raw-2026-05-19.json`
- `docs/acorn-service-area-pages-audit-2026-05-19.json`

## Executive Summary

Acorn has a good commercial opportunity in location search, but the current location footprint is messy. The city accident pages are the best foundation, while the state pages are too thin and the `/service-areas/` suburb pages create a significant quality and index-management problem.

The priority should be to strengthen a small set of high-value state/city pages first, then decide which suburb/service-area pages are worth keeping. Do not create more suburb pages until the existing canonical, sitemap, H1, duplicate-template, and comments/sidebar issues are cleaned up.

## Key Findings

| Area | Finding | Impact | Priority |
|---|---|---|---|
| Location footprint | 179 location-like URLs are in the page sitemap; 167 are service-area pages. | Large footprint for a niche service, with thin/duplicated pages likely diluting quality. | High |
| Service-area canonicals | 79 service-area URLs return 200 but canonicalise to `/service-areas/`. | Mixed signals: pages are in sitemap but tell Google the hub is canonical. | High |
| Service-area H1s | 80 service-area pages sampled/fetched have no H1. | Weak page targeting and template quality. | High |
| Thin service pages | 88 service-area pages are under 350 words. | Doorway/thin-content risk and low conversion value. | High |
| Duplicate service templates | 79 service pages share the exact title `Service Areas | Top Courtesy Car Company in Australia`; only 89 unique titles/hashes across 167 pages. | Duplicate and near-duplicate location content. | High |
| State pages | QLD, SA, and WA have generic titles and no meta descriptions; all state pages are very short. | Missed opportunity for state-level location intent. | Medium |
| City pages | City pages have reasonable word count, but inconsistent titles, weak meta copy, blog sidebar headings, and Perth lacks an H1. | These pages can rank better with moderate cleanup. | High |
| UX/template | Several page types expose blog template elements such as `Recent Posts`, `Categories`, `Meta`, and `Leave a Reply`. | Looks unpolished and distracts from lead generation. | Medium |

## Page Set Review

### 1. `/locations/`

- Title: `Locations - Acorn Rentals`
- Meta description: missing
- H1: missing
- Word count: about 165

This should be the national location hub, but currently it is too thin to do much SEO work. It should introduce Acorn's accident replacement vehicle coverage, link clearly to state/city pages, and explain that support is service-area based rather than pretending Acorn has physical rental branches everywhere.

Recommended action:

- Add a real H1 such as `Accident Replacement Vehicle Locations Across Australia`.
- Add a concise meta description.
- Add state sections for NSW, VIC, QLD, SA, WA, ACT/TAS/NT if serviceable.
- Link to priority city pages and the application CTA.
- Avoid generic car-rental positioning; keep the page focused on not-at-fault accident replacement vehicles.

### 2. State Pages

| URL | Title | Meta | H1 | Words |
|---|---|---|---|---:|
| `/new-south-wales/` | `Not at Fault Accident Car Hire NSW | Acorn Rental` | Present | Missing | 189 |
| `/victoria/` | `Not at Fault Accident Car Hire Victoria | Acorn Rental` | Present | Missing | 88 |
| `/queensland/` | `Queensland - Acorn Rentals` | Missing | Missing | 125 |
| `/south-australia/` | `South Australia - Acorn Rentals` | Missing | Missing | 113 |
| `/western-australia/` | `Western Australia - Acorn Rentals` | Missing | Missing | 105 |

The state pages are underdeveloped. NSW and VIC at least have targeted titles/meta, but QLD, SA, and WA look unfinished. These should be serviceable state landing pages rather than thin directory pages.

Recommended action:

- Rewrite titles around `Not at Fault Accident Car Hire [State]`.
- Add H1s and meta descriptions to every state page.
- Add 500-800 words of useful, state-specific content:
  - who Acorn helps
  - what happens after a not-at-fault accident
  - delivery to home, repairer, or workplace where available
  - major service regions/cities
  - eligibility and required accident details
- Add internal links to city pages and the accident replacement vehicle page.
- Add FAQs that are consistent across states but lightly localised.

### 3. City Accident Pages

| URL | Title | H1 | Words | Main issue |
|---|---|---|---:|---|
| `/car-accident-sydney/` | `Not at Fault Accident Car Hire Sydney | Acorn Rentals` | `Car Accident Sydney` | 724 | H1 is vague; meta reads awkwardly. |
| `/car-accident-melbourne/` | `Not at Fault Accident Car Hire Melbourne | Acorn Rental` | `Car Accident Melbourne` | 670 | Good target, but copy/template needs polish. |
| `/car-accident-brisbane/` | `Car Accident Brisbane - Acorn Rentals` | `Car Accident Brisbane` | 669 | Title is less commercial than Sydney/Melbourne. |
| `/car-accident-perth/` | `Car Accident Perth - Acorn Rentals` | Missing | 704 | Missing H1; title should target not-at-fault hire. |
| `/car-accident-adelaide/` | `Car Accident Adelaide - Acorn Rentals` | `Car Accident Adelaide` | 718 | Title/H1 should target replacement vehicle intent. |

These are the strongest location assets. They already have enough content to improve quickly and are more commercially relevant than the suburb-level smash repair pages.

Recommended action:

- Standardise title pattern:
  - `Not at Fault Accident Car Hire [City] | Acorn Rentals`
  - or `Accident Replacement Vehicle [City] | Acorn Rentals`
- Standardise H1 pattern:
  - `Not at Fault Accident Car Hire in [City]`
- Rewrite meta descriptions; current wording like `Need A Replacement Cars` is grammatically weak.
- Remove blog sidebar headings from the main content structure.
- Add a clear above-the-fold eligibility CTA.
- Add a short `How it works in [City]` section.
- Add nearby service-area/internal links only where genuinely helpful.
- Add one FAQ block per page:
  - Can I get a replacement car after a not-at-fault accident in [City]?
  - What details do I need to apply?
  - Can Acorn deliver to my repairer?
  - What if the at-fault driver disputes liability?

### 4. `/service-areas/` Hub

- Title: `Service Areas | Top Courtesy Car Company in Australia`
- Meta description: present
- H1: missing
- Word count: about 809

This is a useful hub concept, but it needs a clearer role. It should either be:

- a curated service-area directory that links to only approved/valuable pages, or
- the canonical home for suburb-level coverage, with weaker suburb pages removed/noindexed.

Recommended action:

- Add a proper H1.
- Reframe from `Top Courtesy Car Company` to Acorn's actual positioning: eligible not-at-fault accident replacement vehicles.
- Add grouped state/city navigation.
- Remove sidebar/comment artefacts.
- Link back to the location hub and main accident replacement vehicle page.

### 5. Individual Service-Area Pages

This is the highest-risk area.

Quantified findings across 167 `/service-areas/` pages:

- 79 pages canonicalise to `/service-areas/` despite being live 200 URLs in the sitemap.
- 80 pages have no H1.
- 88 pages are under 350 words.
- 79 pages share the same title: `Service Areas | Top Courtesy Car Company in Australia`.
- Several pages include `Leave a Reply`, `Recent Posts`, `Categories`, and `Meta` headings.
- Duplicate/near-duplicate examples exist, such as `/service-areas/victoria-smash-repairs/` and `/service-areas/victoria-smash-repairs-2/`.

Recommended action:

- Decide which service-area pages should be indexable.
- Remove canonicalised suburb pages from the XML sitemap if they are not intended to rank.
- For pages not worth keeping, 301 redirect to the closest state/city page or keep canonicalised and noindex them.
- For pages worth keeping, make them self-canonical and rewrite them with genuinely local usefulness.
- Disable comments and remove blog sidebar widgets from all service-area/location templates.
- Avoid creating hundreds of interchangeable suburb pages unless they have unique local value, clear demand, and a conversion pathway.

## Recommended Location Architecture

### Keep And Improve

Primary pages:

- `/locations/`
- `/new-south-wales/`
- `/victoria/`
- `/queensland/`
- `/south-australia/`
- `/western-australia/`
- `/car-accident-sydney/`
- `/car-accident-melbourne/`
- `/car-accident-brisbane/`
- `/car-accident-perth/`
- `/car-accident-adelaide/`

These should become the main SEO and conversion assets.

### Audit Before Keeping

Suburb/service-area pages should be kept only where they satisfy at least one of:

- real search demand
- genuine operational relevance
- internal linking support from state/city hub
- unique local copy, not just spun template content
- clear conversion route

### Deprioritise Or Consolidate

Canonicalised and thin service-area pages should be consolidated. The current state sends mixed signals by listing many URLs in the sitemap while many canonicalise to the hub.

## Suggested Next Work

1. Fix technical/template issues first:
   - H1s
   - meta descriptions
   - comments/sidebar artefacts
   - canonical/sitemap alignment

2. Rewrite the five city pages:
   - Sydney
   - Melbourne
   - Brisbane
   - Perth
   - Adelaide

3. Rewrite the five state pages as supporting hubs.

4. Decide the suburb/service-area policy:
   - indexable local pages only where justified
   - otherwise noindex/redirect/canonicalise and remove from sitemap

5. Add location keyword tracking coverage:
   - `not at fault car hire [city]`
   - `accident replacement vehicle [city]`
   - `accident car hire [city]`
   - `courtesy car after accident [city]`

## SEO View

The best near-term opportunity is not creating more location pages. It is making the existing city and state pages look intentional, useful, and conversion-led. The current service-area footprint looks like a legacy location-page build that needs pruning and quality control. Once cleaned, Acorn can build a much stronger local landing-page system around not-at-fault accident hire rather than generic smash repair suburb terms.
