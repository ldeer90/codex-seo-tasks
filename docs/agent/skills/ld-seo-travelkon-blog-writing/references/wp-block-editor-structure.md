# TravelKon WordPress Block Editor Structure

Use this reference only for TravelKon blog creation/editing tasks where the user asks for WordPress-ready, Gutenberg, block editor, or pattern-based code.

## Source Model

Reviewed public rendered output from 16 `travelkon-vs-*` posts, including Airalo, Saily, Simify, SimCorner, Holafly, Nomad, Telstra, Optus, Vodafone, Woolworths Everyday Mobile Roaming, GoSIM, Global Starlink, Roameo, OneSimCard, and WorldSIM.

Important limitation: the public REST API does not expose `content.raw` without WordPress edit permission, and registered pattern endpoints returned `401`. The structure below is reconstructed from rendered public block output and is suitable for WordPress Code Editor paste-in, but authenticated WordPress editor output is preferred when available.

## Base Article Shape

Do not include the post title as an H1 unless the user explicitly asks. WordPress supplies the post title.

Use this sequence as the default base for comparison or commercial-support TravelKon articles:

1. Opening paragraphs: 2-4 paragraphs that frame the traveller problem and mention the primary topic naturally.
2. `Quick Answer`: H2 plus 2-4 short paragraphs with the practical answer.
3. Brand, product, or option comparison: H2 plus a striped comparison table.
4. `Why TravelKon Stands Out`: H2 plus concise proof-oriented paragraphs.
5. `Price and Plan Structure`: H2, with careful non-stale wording unless live prices were requested and checked.
6. Destination or use-case sections: H2 blocks for Japan, Europe, Bali, Indonesia, Asia Regional, or the specific destinations in the draft.
7. CTA blocks inside destination/use-case sections: usually one broad category CTA and/or one two-button product CTA.
8. Secondary decision sections: data, unlimited/fair use, calls/texts/hotspot, top-up/app/ease of use, activation/support/refund notes.
9. `Who TravelKon Is Better For`: H2 plus a list when the content supports it.
10. `Final Verdict`, `Our Honest Take`, or equivalent: H2 plus a clear recommendation.
11. `FAQs`: H2 followed by H3 questions and paragraph answers.

## Block Code Conventions

Output WordPress Code Editor-ready block code, not Markdown.

Paragraph:

```html
<!-- wp:paragraph -->
<p>Paragraph text with <a href="https://www.travelkon.com.au/example/">natural anchor text</a>.</p>
<!-- /wp:paragraph -->
```

H2:

```html
<!-- wp:heading -->
<h2 class="wp-block-heading"><strong>Quick Answer</strong></h2>
<!-- /wp:heading -->
```

H3:

```html
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading"><strong>Is TravelKon better for Europe?</strong></h3>
<!-- /wp:heading -->
```

Striped comparison table:

```html
<!-- wp:table {"hasFixedLayout":true,"className":"is-style-stripes"} -->
<figure class="wp-block-table is-style-stripes"><table class="has-fixed-layout"><thead><tr><th><strong>Feature</strong></th><th><strong>TravelKon</strong></th><th><strong>Alternative</strong></th></tr></thead><tbody><tr><td><p><strong>Best fit</strong></p></td><td><p>Traveller-first summary.</p></td><td><p>Alternative summary.</p></td></tr></tbody></table></figure>
<!-- /wp:table -->
```

Unordered list:

```html
<!-- wp:list -->
<ul class="wp-block-list"><li>First useful point.</li><li>Second useful point.</li></ul>
<!-- /wp:list -->
```

Ordered checklist:

```html
<!-- wp:list {"ordered":true} -->
<ol class="wp-block-list"><li><strong>Check compatibility</strong><br>Confirm the phone supports eSIM before departure.</li></ol>
<!-- /wp:list -->
```

Image block, only when the user supplies or approves a WordPress media URL:

```html
<!-- wp:image {"sizeSlug":"large"} -->
<figure class="wp-block-image size-large"><a href="https://images.travelkon.com.au/wp-content/uploads/example.jpg"><img src="https://images.travelkon.com.au/wp-content/uploads/example-1024x576.jpg" alt="plain descriptive alt text"/></a></figure>
<!-- /wp:image -->
```

## CTA Pattern Placement

Use stored CTA snippets from:

`var/reports/travelkon-wordpress-patterns-2026-05-27/snippets/`

Use the index first:

`var/reports/travelkon-wordpress-patterns-2026-05-27/travelkon-wordpress-pattern-index-2026-05-27.csv`

Placement pattern from the `travelkon-vs-*` posts:

- Destination H2.
- Optional image or short scenario paragraph.
- One relevant CTA block.
- Short product-fit explanation.
- Optional second CTA block when two product options genuinely help.
- Comparison table or decision summary.

Do not insert CTA blocks after every heading. Use them where the reader has enough context to decide.

## Draft Conversion Process

When converting a draft into WordPress block editor code:

1. Preserve the approved argument and headings unless they are structurally broken.
2. Remove Markdown syntax such as `#`, `##`, `**`, and pipe tables; convert to proper WP block HTML.
3. Convert headings to `wp:heading` comments with `wp-block-heading` classes and bold heading text.
4. Convert body paragraphs to `wp:paragraph`.
5. Convert bullet/checklist content to `wp:list`.
6. Convert tables to `wp:table` with `is-style-stripes` and `has-fixed-layout` unless the table is too small to need a fixed layout.
7. Insert only the relevant CTA snippets from the TravelKon CTA archive.
8. Keep internal links natural and contextual. Avoid standalone asset-style anchors such as "the Indonesia eSIM product page".
9. Re-check CTA target pages when product claims, availability, unlimited data, calls/texts, hotspot, or destination coverage matter.
10. Return a full WordPress Code Editor block-code version, not mixed prose plus code, unless the user asks for commentary.

## QA Before Returning

- No Markdown headings remain.
- Every `<!-- wp:* -->` opening has a matching closing comment where required.
- No raw code fence markers are inside the final article artifact.
- CTA blocks come from the TravelKon CTA archive or authenticated WordPress pattern library.
- Tables are readable on mobile: keep cells short and avoid over-wide comparison rows.
- Product and plan claims are conservative and checked against live pages when used.
- Link check all selected internal, CTA, and external URLs.
