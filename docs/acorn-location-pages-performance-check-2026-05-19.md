# Acorn Rentals Location Pages Performance Check - 2026-05-19

## Scope

- Page set: `/locations/`, five state pages, five city accident pages, `/service-areas/`, and service-area child pages from the location-page review.
- GA4 period: current 90 days, `2026-02-18` to `2026-05-18`; YoY comparison, `2025-02-18` to `2025-05-18`.
- GA4 property: `properties/423383715`, read via `hello@agents.digital`.
- SEO channel focus: Organic Search. All-channel numbers are included only to diagnose whether non-organic sessions are useful.
- SE Ranking: project `11444792`, Google Australia search engine `968494`, checked on `2026-05-19`.
- Caveat: SE Ranking Google Search Console feed is not connected. Native GSC was not pulled in this step, so this is GA4 + SE Ranking rather than full GSC query/page reporting.

## Executive Read

The location set is earning **177 organic sessions** in the last 90 days, up from **94 YoY** (+88.3%). Engagement is acceptable on organic traffic: **111 engaged sessions**, or **62.7%**.

The scale is still modest. These pages are not yet a major organic acquisition surface, and there are **0 recorded conversions/revenue** attributed to the location-page set in GA4 for this period. That does not mean they have no assisted value, but landing-page performance alone does not yet justify expanding the suburb-page footprint.

All-channel traffic is much larger at **573 sessions**, but engagement is weak: **22.7%**. Most of that gap is Direct traffic to `/service-areas/` and service-area child pages, which looks low-value compared with organic sessions.

## Organic Performance By Page Set

| Page set | Organic sessions | YoY sessions | YoY change | Engaged sessions | Engagement rate | Conversions |
|---|---:|---:|---:|---:|---:|---:|
| State pages | 55 | 22 | +150.0% | 38 | 69.1% | 0 |
| Service-area child pages | 73 | 45 | +62.2% | 45 | 61.6% | 0 |
| /service-areas/ hub | 22 | 0 | n/a | 9 | 40.9% | 0 |
| City accident pages | 19 | 21 | -9.5% | 13 | 68.4% | 0 |
| /locations/ hub | 8 | 6 | +33.3% | 6 | 75.0% | 0 |

## Top Organic Location Pages

| Page | Organic sessions | YoY sessions | YoY change | Engaged sessions | Engagement rate |
|---|---:|---:|---:|---:|---:|
| `/new-south-wales/` | 22 | 2 | +1000.0% | 15 | 68.2% |
| `/service-areas/` | 22 | 0 | n/a | 9 | 40.9% |
| `/western-australia/` | 14 | 9 | +55.6% | 7 | 50.0% |
| `/car-accident-melbourne/` | 10 | 7 | +42.9% | 7 | 70.0% |
| `/locations/` | 8 | 6 | +33.3% | 6 | 75.0% |
| `/service-areas/sydney-smash-repairs/` | 8 | 2 | +300.0% | 6 | 75.0% |
| `/queensland/` | 7 | 2 | +250.0% | 6 | 85.7% |
| `/victoria/` | 7 | 2 | +250.0% | 5 | 71.4% |
| `/service-areas/cabramatta-smash-repairs/` | 6 | 1 | +500.0% | 2 | 33.3% |
| `/car-accident-perth/` | 5 | 12 | -58.3% | 2 | 40.0% |
| `/south-australia/` | 5 | 7 | -28.6% | 5 | 100.0% |
| `/service-areas/cessnock-smash-repairs/` | 4 | 1 | +300.0% | 4 | 100.0% |
| `/service-areas/maitland-smash-repairs/` | 4 | 4 | +0.0% | 1 | 25.0% |
| `/service-areas/burwood-smash-repairs/` | 3 | 0 | n/a | 2 | 66.7% |
| `/service-areas/campbelltown-smash-repairs/` | 3 | 0 | n/a | 1 | 33.3% |

## All-Channel Diagnostic

| Page set | All-channel sessions | Organic sessions | Direct sessions | All-channel engagement rate | Note |
|---|---:|---:|---:|---:|---|
| /service-areas/ hub | 170 | 22 | 148 | 6.5% | Large Direct volume, very low engagement. |
| Service-area child pages | 281 | 73 | 208 | 20.6% | Direct volume outweighs organic; quality varies. |
| State pages | 67 | 55 | 12 | 62.7% | Mostly organic and relatively engaged. |
| City accident pages | 46 | 19 | 27 | 28.3% | Organic engagement good, Direct engagement weak. |
| /locations/ hub | 9 | 8 | 1 | 66.7% | Small but mostly useful organic traffic. |

## Ranking Signals

| Keyword | Volume | Current rank | Landing page signal | Interpretation |
|---|---:|---:|---|---|
| accident car hire brisbane | 10 | 5 | `/car-accident-brisbane/` | Good match: city page is ranking well for the intended Brisbane accident-hire query. |
| not at fault car hire sydney | 50 | 14 | Home page recently; target is `/car-accident-sydney/` | Opportunity/cannibalisation: Sydney query is not consistently landing on the Sydney page. |
| car rental jurien bay | 10 | 8 | `/western-australia/` | Low-volume generic location term is ranking, but this is not Acorn's strongest accident-replacement intent. |
| car hire mudgee nsw | 390 | Not top 100 | `/new-south-wales/` seen historically | Not ranking currently despite a state-page association. |
| car rental bathurst nsw | 720 | Not top 100 | `/new-south-wales/` seen historically | Not ranking currently; broad car-rental location intent may be mismatched. |
| car rental melbourne victoria | 33,100 | Not top 100 | No current landing page | High-volume generic rental term is not realistically owned by current location pages. |
| car rental company perth | 22,200 | Not top 100 | No current landing page | High-volume generic rental term is outside current accident-support positioning. |

## What This Means

1. **State pages are currently the best-performing SEO layer.** They produced 55 organic sessions, led by `/new-south-wales/` and `/western-australia/`, despite being thin and missing core on-page elements from the technical review.
2. **Service-area pages generate more organic sessions than city pages, but the architecture risk is high.** The child pages brought 73 organic sessions, yet the earlier review found canonical, H1, duplication, and thin-content problems across that set.
3. **The city accident pages have better strategic fit than their current traffic suggests.** Brisbane ranks well for a directly relevant accident-hire query, while Melbourne attracts broader not-at-fault/rental intent. Sydney is underperforming because the tracked Sydney query is landing on the home page rather than the Sydney page.
4. **The `/service-areas/` hub is a quality concern.** It has 170 all-channel sessions, but only 11 engaged sessions, and 148 Direct sessions with almost no engagement. I would not use this as evidence that the suburb strategy is working.
5. **No recorded conversions means we should optimise before scaling.** The pages may support assisted journeys or phone calls not captured as conversions, but GA4 landing-page data does not show conversion value from the set yet.

## Recommended Priority

1. **Fix tracking clarity first:** confirm whether Acorn phone/apply interactions are tracked as GA4 key events. If not, these pages will keep looking conversion-poor even if they help leads.
2. **Rewrite and strengthen the five state pages:** NSW, VIC, QLD, SA, WA. They already show the strongest organic signal and need H1s, better titles/meta, accident-replacement positioning, eligibility CTAs, and links into city pages.
3. **Improve city accident pages next:** prioritise Sydney and Brisbane first. Sydney needs to win back the `not at fault car hire sydney` landing-page match; Brisbane already has ranking proof and should be protected.
4. **Consolidate `/service-areas/` before expanding suburbs:** decide which child pages deserve indexable pages, which should canonicalise/noindex, and remove blog-template artefacts. Do not build more suburb pages until this is resolved.
5. **Build internal links from relevant accident blogs and core service pages:** point city/state intent to the correct location pages instead of letting the homepage and Melbourne page absorb unrelated location queries.

## Files

- Raw GA4 performance export: `docs/acorn-location-pages-performance-2026-05-19.json`
- Technical location review: `docs/acorn-location-pages-review-2026-05-19.md`
