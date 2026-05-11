"""Critique Shopify collection content brief payloads for SEO completeness."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from collection_seo_utils import read_json


def critique(payload: dict[str, Any]) -> dict[str, Any]:
    critiques = []
    counter: Counter[str] = Counter()
    for brief in payload.get("briefs", []):
        if not isinstance(brief, dict):
            continue
        issues = _brief_issues(brief)
        for issue in issues:
            counter[issue["code"]] += 1
        critiques.append({
            "slug": brief.get("slug"),
            "collection_name": brief.get("collection_name"),
            "url": brief.get("url"),
            "doc_url": brief.get("content_brief_url", ""),
            "issues": issues,
            "score": max(0, 100 - sum(issue["points"] for issue in issues)),
        })
    return {
        "client": payload.get("client"),
        "summary": {
            "briefs": len(critiques),
            "issue_counts": dict(counter),
            "average_score": round(sum(c["score"] for c in critiques) / max(len(critiques), 1), 1),
        },
        "critiques": critiques,
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        f"{result.get('client')} - Collection Content Brief Critique",
        "",
        "Summary",
        f"Briefs reviewed: {result['summary']['briefs']}",
        f"Average completeness score: {result['summary']['average_score']}/100",
        "",
        "Repeated Issues",
    ]
    for code, count in sorted(result["summary"]["issue_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- {code}: {count}")
    lines.extend([
        "",
        "Overall Critique",
        (
            "The briefs are structurally usable for a writer and include primary keyword targets, "
            "supplemental keyword opportunities where supplied, page state, products, SERP context, "
            "Search Console opportunities where available, and internal links. Remaining issues should "
            "be reviewed as quality notes rather than automatic blockers unless the validator also fails."
        ),
        "",
        "Per-Collection Critique",
    ])
    for critique_row in result["critiques"]:
        lines.extend([
            "",
            f"## {critique_row['collection_name']} ({critique_row['slug']})",
            f"Score: {critique_row['score']}/100",
            f"URL: {critique_row['url']}",
        ])
        for issue in critique_row["issues"]:
            lines.append(f"- {issue['severity']}: {issue['message']}")
    return "\n".join(lines).strip() + "\n"


def _brief_issues(brief: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    keywords = brief.get("keywords") or {}
    if not keywords.get("secondary"):
        issues.append(_issue("warning", "missing_secondary_keywords", "No tracked secondary keywords are available.", 12))
    if not keywords.get("supplemental"):
        issues.append(_issue("blocking", "missing_supplemental_keywords", "Add SE Ranking supplemental keywords with real volume before drafting.", 20))
    if not brief.get("search_console_opportunities"):
        issues.append(_issue("warning", "missing_search_console_queries", "No useful non-brand Search Console opportunities were available after filtering.", 8))
    if len((brief.get("serp_context") or {}).get("serp_results") or []) < 3:
        issues.append(_issue("warning", "thin_serp_context", "SERP context has fewer than three competitor results.", 8))
    supporting = keywords.get("supporting") or []
    if supporting and not any(int(k.get("au_volume") or 0) > 0 or int(k.get("us_volume") or 0) > 0 for k in supporting):
        issues.append(_issue("info", "supporting_keywords_unvalidated", "Derived supporting variants have no real volume metrics.", 5))
    products = (brief.get("product_context") or {}).get("sample_product_titles") or []
    if len(products) < 4:
        issues.append(_issue("warning", "thin_product_context", "Product sample context has fewer than four products.", 8))
    links = brief.get("internal_links") or []
    if len(links) < 5:
        issues.append(_issue("blocking", "insufficient_internal_links", "Internal link plan has fewer than five targets.", 20))
    if brief.get("collection_name", "").isupper():
        issues.append(_issue("info", "shouty_collection_name", "Collection name is all caps from current H1; normalize tone in the final draft.", 3))
    return issues


def _issue(severity: str, code: str, message: str, points: int) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "points": points}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--briefs-json", required=True, type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-text", type=Path)
    args = parser.parse_args()

    result = critique(read_json(args.briefs_json, {}))
    if args.output_json:
        args.output_json.write_text(json.dumps(result, indent=2))
    text = render_report(result)
    if args.output_text:
        args.output_text.write_text(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
