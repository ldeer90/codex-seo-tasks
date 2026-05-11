"""Render writer-ready Google Doc bodies for Shopify collection content briefs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from collection_seo_utils import read_json


def render_brief_doc(brief: dict[str, Any], *, client: str = "") -> str:
    keywords = brief.get("keywords") or {}
    primary = keywords.get("primary") or {}
    current = brief.get("current_page") or {}
    products = brief.get("product_context") or {}
    serp = brief.get("serp_context") or {}
    recommendations = brief.get("content_recommendations") or {}

    proposed = brief.get("proposed_page_elements") or {}
    lines = [
        f"{client} - Collection Content Brief - {brief.get('collection_name', '')}".strip(" -"),
        "",
        "Collection",
        f"URL: {brief.get('url', '')}",
        f"Current title: {current.get('title', '')}",
        f"Current H1: {current.get('h1', '')}",
        f"Current meta description: {current.get('meta_description', '')}",
        f"Current copy summary: {current.get('copy_summary', '')}",
        "",
        "Proposed Page Elements",
        f"Proposed title: {proposed.get('proposed_title', '')}",
        f"Proposed meta description: {proposed.get('proposed_meta_description', '')}",
        f"Title change needed: {'Yes' if proposed.get('title_change_needed') else 'No'}",
        f"Meta change needed: {'Yes' if proposed.get('meta_change_needed') else 'No'}",
        f"Note: {proposed.get('note', '')}",
        "",
        "Keyword Strategy",
        f"Primary keyword: {primary.get('keyword', '')}",
        f"AU monthly volume: {primary.get('au_volume', 0)}",
        f"US monthly volume: {primary.get('us_volume', '')}",
        f"Intent: {keywords.get('intent', '')}",
        f"Source: {primary.get('source', '')}",
        "",
    ]

    _append_keyword_group(lines, "Secondary Keywords", keywords.get("secondary") or [])
    _append_keyword_group(lines, "Supplemental Keyword Opportunities", keywords.get("supplemental") or [])
    _append_keyword_group(lines, "Supporting Keyword Variants", keywords.get("supporting") or [])

    lines.extend(["Search Console Opportunities"])
    gsc_rows = brief.get("search_console_opportunities") or []
    if not gsc_rows:
        lines.append("- None supplied in the validated export.")
    for row in gsc_rows[:10]:
        lines.append(
            "- {query} | clicks: {clicks} | impressions: {impressions} | position: {position}".format(
                query=row.get("query", ""),
                clicks=row.get("clicks", 0),
                impressions=row.get("impressions", 0),
                position=row.get("position", 0),
            )
        )
    lines.append("")

    lines.extend([
        "Product Reality",
        f"Product sample source: {products.get('source', '')}",
        f"Product types: {', '.join(products.get('product_types') or [])}",
        "Sample products:",
    ])
    lines.extend(f"- {title}" for title in products.get("sample_product_titles", []))
    lines.append("")

    lines.extend(["SERP And Competitor Context", "Observed competitor titles and headings:"])
    for result in serp.get("serp_results", [])[:5]:
        lines.append(
            f"- Position {result.get('position', '')}: {result.get('title', '')} "
            f"({result.get('url', '')})"
        )
        if result.get("h1"):
            lines.append(f"  H1: {result.get('h1')}")
        if result.get("h2s"):
            lines.append(f"  H2 themes: {', '.join(result.get('h2s', [])[:3])}")
    patterns = serp.get("patterns") or {}
    if patterns:
        lines.extend([
            "",
            f"Common title formula: {patterns.get('title_formula', '')}",
            f"Common H1 pattern: {patterns.get('common_h1', '')}",
            f"Copy angles: {', '.join(patterns.get('copy_angles') or [])}",
        ])
    lines.append("")

    lines.extend([f"Recommended Length: {recommendations.get('recommended_length', '')}"])
    lines.append("")
    heading_structure = recommendations.get("suggested_heading_structure") or []
    if heading_structure:
        lines.extend(["Required HTML Heading Structure"])
        lines.extend(f"- {item}" for item in heading_structure)
        lines.append("Note: Output must use <h2> and two <h3> tags. No <h1>. Wrap body copy in <p> tags.")
        lines.append("")
    lines.extend(["Recommended Content Structure"])
    lines.extend(f"- {item}" for item in recommendations.get("structure", []))
    lines.append("")
    lines.extend(["Natural Keyword Inclusion"])
    lines.extend(f"- {item}" for item in recommendations.get("keyword_inclusion", []))
    lines.append("")
    lines.extend(["Humanised Writing Guidance"])
    lines.extend(f"- {item}" for item in recommendations.get("humanised_guidance", []))
    lines.append("")
    banned = recommendations.get("banned_phrases") or []
    if banned:
        lines.extend(["Banned Phrases (do not use)"])
        lines.extend(f"- {phrase}" for phrase in banned)
        lines.append("")

    lines.extend([
        "Internal Linking Plan",
        "Use these links only where they help the shopper compare related ranges.",
    ])
    for link in brief.get("internal_links", []):
        lines.extend([
            f"- {link.get('target_collection', '')}",
            f"  URL: {link.get('target_url', '')}",
            f"  Anchor: {link.get('anchor_text', '')}",
            f"  Placement: {link.get('placement', '')}",
            f"  Rationale: {link.get('rationale', '')}",
        ])
    lines.append("")

    lines.extend([
        "Writer / LLM Prompt (output: clean HTML)",
        brief.get("writer_prompt", ""),
        "",
        "Final Draft QA",
    ])
    lines.extend(f"- {item}" for item in brief.get("qa_checklist", []))
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_all(payload: dict[str, Any]) -> dict[str, str]:
    client = str(payload.get("client") or "")
    return {
        str(brief.get("slug")): render_brief_doc(brief, client=client)
        for brief in payload.get("briefs", [])
        if isinstance(brief, dict) and brief.get("slug")
    }


def _append_keyword_group(lines: list[str], heading: str, keywords: list[dict[str, Any]]) -> None:
    lines.append(heading)
    if not keywords:
        lines.append("- None supplied in the validated export.")
    for keyword in keywords:
        kd = keyword.get("difficulty") or keyword.get("kd") or ""
        kd_part = f" | KD: {kd}" if kd else ""
        lines.append(
            "- {keyword} | AU: {au} | US: {us}{kd} | Source: {source}".format(
                keyword=keyword.get("keyword", ""),
                au=keyword.get("au_volume", 0),
                us=keyword.get("us_volume", ""),
                kd=kd_part,
                source=keyword.get("source", ""),
            )
        )
    lines.append("")


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
