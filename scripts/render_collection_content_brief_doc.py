"""Render writer-ready Google Doc bodies for Shopify collection content briefs."""

from __future__ import annotations

import argparse
import re
from urllib.parse import urlparse
from pathlib import Path
from typing import Any

from collection_seo_utils import read_json


def render_brief_doc(brief: dict[str, Any], *, client: str = "") -> str:
    keywords = brief.get("keywords") or {}
    primary = keywords.get("primary") or {}
    current = brief.get("current_page") or {}
    recommendations = brief.get("content_recommendations") or {}

    proposed = brief.get("proposed_page_elements") or {}
    url = str(brief.get("url") or "")
    page_name = proposed.get("proposed_h1") or current.get("h1") or brief.get("collection_name") or primary.get("keyword")

    lines = [
        f"{client}: {page_name} Page Copy".strip(": "),
        "",
        "## Overview",
        "",
        "| Item | Detail |",
        "|---|---|",
        f"| Website | {_cell(_site_from_url(url))} |",
        f"| Page | {_cell(page_name)} |",
        "| Page type | Collection page |",
        "| Keyword source | SE Ranking keyword research, current page data, SERP context, product range review, and Search Console where available. |",
        f"| Content approach | {_cell(_content_angle(brief, recommendations))} |",
        "",
        "---",
        "",
        "## Keywords To Work Into The Page",
        "",
        "| Keyword | Monthly Searches | How To Use It |",
        "|---|---:|---|",
    ]

    for row in _keyword_rows(keywords):
        lines.append(
            f"| {_cell(row.get('keyword'))} | {_cell(_volume_label(row))} | {_cell(_keyword_note(row, primary.get('keyword')))} |"
        )
    lines.extend([
        "",
        "## Internal Links",
        "",
        "| Anchor Text | Destination |",
        "|---|---|",
    ])
    for link in brief.get("internal_links", []):
        lines.append(f"| {_cell(link.get('anchor_text'))} | {_cell(link.get('target_url'))} |")
    lines.extend(["", "## Recommended Heading Hierarchy", ""])
    lines.extend(_heading_hierarchy_table(brief, recommendations))
    lines.extend(["", "## SEO Review", ""])
    lines.extend(_seo_review_table(brief, keywords, recommendations))
    lines.extend([
        "",
        "## Example Copy",
        "",
        "### Page Title",
        "",
        proposed.get("proposed_title") or current.get("title") or "",
        "",
        "### Meta Description",
        "",
        proposed.get("proposed_meta_description") or current.get("meta_description") or "",
        "",
        "### H1",
        "",
        page_name,
    ])
    lines.extend(_example_copy_lines(brief))
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_all(payload: dict[str, Any]) -> dict[str, str]:
    client = str(payload.get("client") or "")
    return {
        str(brief.get("slug")): render_brief_doc(brief, client=client)
        for brief in payload.get("briefs", [])
        if isinstance(brief, dict) and brief.get("slug")
    }


def _keyword_rows(keywords: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    primary = dict(keywords.get("primary") or {})
    if primary.get("keyword"):
        primary["role"] = "primary"
        rows.append(primary)
    for group, role in (
        ("secondary", "supporting"),
        ("supplemental", "supporting"),
        ("supporting", "variant"),
    ):
        for row in keywords.get(group) or []:
            if not row.get("keyword"):
                continue
            item = dict(row)
            item["role"] = role
            if item["keyword"] not in {existing.get("keyword") for existing in rows}:
                rows.append(item)
    return rows[:12]


def _volume_label(row: dict[str, Any]) -> str:
    au = int(row.get("au_volume") or 0)
    us = int(row.get("us_volume") or 0)
    if us > 0:
        return f"AU {au:,} / US {us:,}"
    return f"{au:,}"


def _keyword_note(row: dict[str, Any], primary: Any) -> str:
    keyword = row.get("keyword", "")
    if row.get("role") == "primary" or keyword == primary:
        return "Primary target for the page opening, title/meta recommendations, and main copy direction."
    if row.get("reasoning"):
        return str(row["reasoning"])
    if row.get("intent"):
        return f"Use where the copy supports {row.get('intent')} intent."
    if row.get("source"):
        return f"Use naturally as a supporting phrase from {row.get('source')}."
    return "Use naturally where it helps the shopper compare the collection."


def _heading_hierarchy_table(brief: dict[str, Any], recommendations: dict[str, Any]) -> list[str]:
    current = brief.get("current_page") or {}
    proposed = brief.get("proposed_page_elements") or {}
    primary = ((brief.get("keywords") or {}).get("primary") or {}).get("keyword", "")
    structure = recommendations.get("suggested_heading_structure") or []
    rows = [
        "| Page Section | Recommended Heading | Heading Level | SEO Role |",
        "|---|---|---|---|",
        f"| Hero | {_cell(proposed.get('proposed_h1') or current.get('h1') or brief.get('collection_name') or primary).upper()} | H1 | Clear page topic. Use once only. |",
    ]
    if structure:
        body_labels = ["Intro", "Section 1", "Section 2", "Section 3", "Section 4", "Section 5"]
        body_index = 0
        for item in structure:
            level = _heading_level(item)
            if level == "H1":
                continue
            label = body_labels[min(body_index, len(body_labels) - 1)]
            body_index += 1
            rows.append(
                f"| {label} | {_cell(_heading_text(item)).upper()} | {_cell(level)} | {_cell(_heading_role(level))} |"
            )
    else:
        rows.extend([
            f"| Intro | {_cell(primary.title()).upper()} | H2 | Opens with the primary keyword and the strongest shopper intent. |",
            "| Section 1 | SHOPPER DECISION ANGLE | H3 | Help shoppers compare styles, uses, or product types. |",
            "| Section 2 | RELATED STYLE GUIDANCE | H3 | Ground the copy in visible products and natural internal links. |",
        ])
    return rows


def _example_copy_lines(brief: dict[str, Any]) -> list[str]:
    example = brief.get("example_copy") or {}
    if isinstance(example, dict) and example.get("sections"):
        return _structured_example_copy(example)

    recommendations = brief.get("content_recommendations") or {}
    keywords = brief.get("keywords") or {}
    primary = (keywords.get("primary") or {}).get("keyword") or "collection"
    page_name = (
        (brief.get("proposed_page_elements") or {}).get("proposed_h1")
        or brief.get("collection_name")
        or _title_keyword(primary)
    )
    products = (brief.get("product_context") or {}).get("sample_product_titles") or []
    product_hint = ", ".join(products[:3]) if products else "the current range"
    headings = [_heading_text(item) for item in recommendations.get("suggested_heading_structure") or []]
    h2 = headings[0] if headings else _title_keyword(primary)
    h3s = headings[1:3] or ["Shop The Range", "How To Style The Collection"]

    return [
        "",
        "### H2",
        "",
        h2,
        "",
        (
            f"Shop {primary} styles designed to make the {page_name.lower()} range easy to compare. "
            f"Use this section to introduce the collection, the main shopper intent, and the verified product context without adding unsupported claims."
        ),
        "",
        "### H3",
        "",
        h3s[0],
        "",
        (
            f"Ground this section in visible products such as {product_hint}. Explain the most useful style, fit, colour, fabric, or occasion differences a shopper needs before choosing."
        ),
        "",
        "### H3",
        "",
        h3s[1] if len(h3s) > 1 else "Related Styles",
        "",
        "Use this section to guide shoppers toward related ranges and natural internal links where those links help them compare options.",
    ]


def _structured_example_copy(example: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if example.get("hero_subheading"):
        lines.extend(["", "### Hero Subheading", "", str(example["hero_subheading"])])
    for section in example.get("sections") or []:
        if not isinstance(section, dict):
            continue
        heading_label = section.get("label") or section.get("heading_level") or "H2"
        heading = section.get("heading") or ""
        body = section.get("body") or ""
        lines.extend(["", f"### {heading_label}", "", str(heading)])
        if body:
            lines.extend(["", str(body)])
        for note in section.get("notes") or []:
            lines.append(str(note))
    return lines


def _seo_review_table(
    brief: dict[str, Any],
    keywords: dict[str, Any],
    recommendations: dict[str, Any],
) -> list[str]:
    primary = (keywords.get("primary") or {}).get("keyword", "")
    current = brief.get("current_page") or {}
    supplemental = keywords.get("supplemental") or []
    return [
        "| Area | Recommendation |",
        "|---|---|",
        f"| Overall structure | {_cell('Use the collection H1 once, then keep the body copy organised around one H2 and two focused H3 sections.')} |",
        f"| Keyword coverage | {_cell(f'Prioritise {primary}; include {len(supplemental)} researched supporting phrases only where they read naturally.')} |",
        f"| Search intent | {_cell(keywords.get('intent') or 'Support commercial collection comparison and buying confidence.')} |",
        f"| Page balance | {_cell('Keep the copy useful and product-led; avoid turning the page into a generic SEO paragraph.')} |",
        f"| Current page | {_cell('Current copy is present and should be refreshed.' if current.get('copy_summary') else 'Current copy is thin or unavailable in the export; ground updates in product and SERP evidence.')} |",
    ]


def _product_table(products: dict[str, Any]) -> list[str]:
    titles = products.get("sample_product_titles") or []
    if not titles:
        return ["No product sample titles were supplied in the validated export."]
    rows = ["| Product | Note |", "|---|---|"]
    for title in titles[:10]:
        rows.append(f"| {_cell(title)} | Use only if relevant to the collection angle; do not invent product attributes. |")
    if products.get("product_types"):
        rows.extend(["", f"Product types: {', '.join(products.get('product_types') or [])}."])
    if products.get("source"):
        rows.append(f"Product sample source: {products.get('source')}.")
    return rows


def _content_angle(brief: dict[str, Any], recommendations: dict[str, Any]) -> str:
    structure = recommendations.get("structure") or []
    if structure:
        return " ".join(str(item).rstrip(".") + "." for item in structure[:2])
    primary = ((brief.get("keywords") or {}).get("primary") or {}).get("keyword", "")
    return (
        f"Frame the page around shoppers comparing {primary or 'this collection'} and deciding whether the visible range fits their needs."
    )


def _recommendation_line(prefix: str, value: Any) -> str:
    return f"{prefix}: {value}" if value else prefix


def _title_keyword(value: Any) -> str:
    return str(value or "").title()


def _site_from_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return ""


def _heading_level(item: Any) -> str:
    text = str(item)
    match = re.search(r"\b(H[1-6])\b", text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else "Body heading"


def _heading_text(item: Any) -> str:
    text = re.sub(r"^\s*H[1-6]\s*(?:\([^)]*\))?\s*:\s*", "", str(item), flags=re.IGNORECASE)
    text = re.sub(r"</?h[1-6][^>]*>", "", text, flags=re.IGNORECASE)
    return text.strip()


def _heading_role(level: str) -> str:
    if level == "H2":
        return "Primary body-copy section; carry the main shopper decision angle."
    if level == "H3":
        return "Supporting section; answer a specific product, style, or comparison need."
    return "Support readable structure without adding another H1."


def _cell(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).replace("|", "-").strip()


def _paragraph(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _safe_filename(slug: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", slug.lower()).strip("-") or "collection"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--briefs-json", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--slug")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = read_json(args.briefs_json, {})
    docs = render_all(payload)
    if args.slug:
        if args.slug not in docs:
            raise SystemExit(f"Slug not found in briefs JSON: {args.slug}")
        text = docs[args.slug]
        if args.output:
            args.output.write_text(text)
            print(f"Wrote content brief doc body to {args.output}")
        else:
            print(text)
        return

    if not args.output_dir:
        raise SystemExit("Pass --output-dir when rendering all briefs, or --slug with --output.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for slug, text in docs.items():
        path = args.output_dir / f"{_safe_filename(slug)}.txt"
        path.write_text(text)
    print(f"Wrote {len(docs)} content brief doc bodies to {args.output_dir}")


if __name__ == "__main__":
    main()
