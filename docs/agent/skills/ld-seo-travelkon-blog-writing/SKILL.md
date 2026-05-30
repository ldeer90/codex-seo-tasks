---
name: ld-seo-travelkon-blog-writing
description: Use only when creating or editing TravelKon blog/article content. Write or revise TravelKon Shopify/WordPress blog HTML in a professional travel-tech voice, using approved briefs, the TravelKon internal linking map, stored WordPress CTA pattern snippets, destination scenarios, and strict validation.
---

# LD SEO TravelKon Blog Writing

Use this TravelKon-specific variant when creating, editing, or revising TravelKon blog/article content only, especially destination connectivity articles about SIMs, eSIMs, roaming, phone setup, data usage, or travel tech. Do not use this skill for other clients.

## Required Reading

1. `docs/agent/workflows/blog-content-writing.md`
2. `docs/agent/skills/ld-seo-shopify-blog-writing/SKILL.md`
3. `docs/agent/clients/travelkon.md`
4. `docs/agent/clients/travelkon-timeline.md`
5. `docs/agent/clients/travelkon-writing-style.md`
6. `docs/agent/clients/travelkon-internal-linking-map.md`
7. When adding or editing blog CTAs, read the stored CTA index at `var/reports/travelkon-wordpress-patterns-2026-05-27/travelkon-wordpress-pattern-index-2026-05-27.csv`, then load only the relevant snippet file from `var/reports/travelkon-wordpress-patterns-2026-05-27/snippets/`. Use the full archive `var/reports/travelkon-wordpress-patterns-2026-05-27/travelkon-wordpress-pattern-archive-2026-05-27.md` only when choosing between unclear CTA options.
8. When converting a draft into WordPress/Gutenberg block editor code, read `docs/agent/skills/ld-seo-travelkon-blog-writing/references/wp-block-editor-structure.md`.

## Voice Rule

Write like a professional travel-tech editor, not a generic SEO article generator.

- Start from a real travel moment: airport arrivals, ride-share pickup, hotel check-in, map navigation, ferry or train tickets, group chats, bank OTPs, translation apps, hotspot needs, or low-battery logistics.
- Add named destination detail where it genuinely helps: airports, neighbourhoods, landmarks, transport systems, route types, tourist areas, and common apps.
- Explain the technology in plain language, with practical consequences for the traveller.
- Keep claims careful. Never promise universal coverage, cheapest pricing, guaranteed speed, instant activation in every case, or all-device compatibility.
- Use personality through specificity. Avoid jokes, fluff, hype, and generic lines that could fit any country.

## Internal Linking Rule

Use the TravelKon internal linking map before choosing final links.

- Place the first commercial link after the reader's problem has been framed.
- Use category links at comparison or decision points.
- Use product links only after plan-fit caveats such as device compatibility, network, data, activation, or hotspot needs.
- Use supporting blog links as onward reading, not as filler.
- Avoid repeating exact-match anchor text. Make anchors sound like natural editorial copy.

## Web Research Rule

Every TravelKon destination connectivity article needs a small web-research pass before final copy.

- Use web research to verify current destination, airport, registration, transport, app-use, or official tourism context.
- Prefer non-competing sources for external links: official airports, customs/regulators, government tourism boards, public transport authorities, official attraction pages, and official device/platform support pages.
- Do not link to competing eSIM/SIM retailers, affiliate SIM comparison sites, or other travel-connectivity sellers in the final article body. Competitor pages can inform SERP structure only.
- Telco/network operator pages may be used cautiously as factual sources for network or activation claims, but avoid linking them if TravelKon sells an equivalent product and a non-competing source can support the same point.
- Keep external links sparse: usually 0-2 per article, only where they support a claim the reader would reasonably want to verify.
- Add any external source URL to the approved brief JSON before validation so `validate_blog_html_copy.py` can enforce link control.
- Do not surface research labels in the final body. Never write phrases such as "non-TravelKon reference", "external source", "official source", "useful reference", or anything that explains why a source was selected.
- Because the article is published on the TravelKon blog, avoid third-person self-reference such as "TravelKon's guide" or "TravelKon's article" unless the brand name is genuinely needed for clarity.

## Product Research Rule

Before recommending a TravelKon product in body copy, inspect the relevant live category and product pages.

- Capture the current product name, URL, data allowance, validity, countries covered, SIM/eSIM format, call/text status, hotspot/tethering notes, activation notes, expiry/use-by notes, compatibility caveats, and stock status where visible.
- If a product is out of stock, do not make it the main recommendation. Mention it only when useful as a caveat, and make the availability status clear.
- Treat "unlimited" carefully. Check for fair-use limits, country-specific roaming caps, speed reductions, and hotspot conditions before using the word in copy.
- Avoid price claims unless the user specifically asks for pricing; prices move quickly and can make otherwise useful copy stale.
- Do not invent network, coverage, device compatibility, calls/SMS, activation, hotspot, or refund details. If the product page is unclear, write conservatively and send the reader to compare the current product details.

## WordPress CTA Pattern Rule

Use the stored TravelKon CTA button snippets whenever the task involves inserting, replacing, or planning CTAs inside TravelKon blog posts.

- Scope this rule to TravelKon blogs only.
- Choose CTA snippets by destination, product family, and reader intent. Prefer the closest specific destination/product snippet over a broad category snippet.
- Treat the snippet files as Gutenberg block code that can be pasted into the WordPress code editor or merged into Shopify/HTML drafts when appropriate.
- Before using a snippet, re-check the linked TravelKon category/product pages if the CTA depends on product availability, plan inclusions, unlimited/fair-use wording, or destination coverage.
- Do not paste every CTA pattern into an article. Use CTAs where they help the reader decide what to buy next.
- The public WordPress pattern endpoints were permission-gated when archived. If authenticated WordPress access is available, prefer the live editor-side registered pattern library over the reconstructed public snippets, then update the archive/timeline if it differs materially.

## WordPress Block Editor Code Rule

When the user provides a draft blog and asks for a WordPress-ready version, Gutenberg code, block editor code, pattern code, or a version that can be pasted into WordPress:

- Use `references/wp-block-editor-structure.md` as the base structure.
- Model the article flow on TravelKon's `travelkon-vs-*` posts when the article is a comparison, commercial-support, destination, SIM/eSIM, roaming, or travel-tech buying guide.
- Output WordPress Code Editor-ready block code with `<!-- wp:* -->` comments, not Markdown.
- Do not include the post title/H1 unless explicitly requested.
- Convert Markdown headings, lists, and tables into proper WordPress blocks.
- Insert the relevant stored CTA snippets where the reader has enough product/destination context to act.
- If no CTA snippet fits the draft, use a natural internal link instead and flag the missing snippet as a caveat.
- Before returning, check the code for balanced block comments, no Markdown leftovers, no unsupported product claims, and working CTA/internal links.

## Drafting Workflow

Follow `ld-seo-shopify-blog-writing` fully, with these TravelKon additions:

1. Confirm the approved brief and required headings.
2. Check the TravelKon internal linking map for category, product, and blog targets.
3. Inspect the relevant TravelKon category and product pages before writing product recommendations.
4. If CTAs are needed, choose the relevant stored TravelKon WordPress CTA snippet and verify its target page still fits.
5. Review live or cached TravelKon posts for tone and structural patterns.
6. Run web research and separate sources into final-link candidates and competitor/SERP-only references.
7. Review top relevant SERP/article sources where SE Ranking export is unavailable.
8. Draft Shopify article body HTML only unless the user asks for a Google Doc or WordPress-ready block editor code.
9. Validate with `scripts/validate_blog_html_copy.py`.
10. Check selected internal, CTA, and external links return 200.
11. Append the TravelKon timeline with outputs, validator status, caveats, and next action.

## Quality Checks

Before calling a TravelKon article ready, confirm:

- It has at least 3 concrete destination scenarios.
- It names location-specific places, routes, or travel moments naturally.
- It includes the approved primary keyword near the opening without sounding forced.
- Internal links are placed where the reader would actually want the destination.
- CTA blocks, if used, come from the TravelKon CTA archive or authenticated WordPress pattern library and match the article's destination/product intent.
- WordPress block editor outputs follow the TravelKon `travelkon-vs-*` structure reference and contain block comments instead of Markdown.
- Product recommendations match the current TravelKon product pages and do not overstate unlimited data, stock, compatibility, hotspot, or call/text inclusions.
- External links, if used, point to non-competing official or authority sources.
- The article does not read like a templated comparison page with the country name swapped.
