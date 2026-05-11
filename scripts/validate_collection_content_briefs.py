"""Validate rendered Shopify collection content brief inputs before live writes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from collection_seo_utils import included_collections, read_json


def validate(*, client_json: Path, briefs_json: Path) -> dict[str, Any]:
    client = read_json(client_json, {})
    payload = read_json(briefs_json, {})
    expected = {str(c.get("slug")) for c in included_collections(client)}
    briefs = payload.get("briefs") or []
    by_slug = {str(b.get("slug")): b for b in briefs if isinstance(b, dict)}

    blocking: list[dict[str, Any]] = []
    warning: list[dict[str, Any]] = []
    info: list[dict[str, Any]] = []

    missing = sorted(expected - set(by_slug))
    extra = sorted(set(by_slug) - expected)
    if missing:
        blocking.append(_issue("missing_briefs", "Brief JSON is missing included collections.", slugs=missing))
    if extra:
        warning.append(_issue("extra_briefs", "Brief JSON contains slugs not included by the sidecar.", slugs=extra))

    require_us = "US" in str(client.get("market_scope", "")).upper()
    for slug in sorted(expected & set(by_slug)):
        _validate_one(by_slug[slug], require_us=require_us, blocking=blocking, warning=warning)

    if payload.get("blocking"):
        blocking.append(_issue(
            "upstream_blockers",
            "Brief build payload still contains upstream blockers.",
            count=len(payload.get("blocking") or []),
        ))

    info.append(_issue(
        "brief_counts",
        "Collection content brief payload parsed successfully.",
        expected_collections=len(expected),
        briefs=len(briefs),
    ))

    return {
        "ok": not blocking,
        "summary": {
            "client": client.get("client"),
            "expected_collections": len(expected),
            "briefs": len(briefs),
            "blocking_count": len(blocking),
            "warning_count": len(warning),
        },
        "blocking": blocking,
        "warning": warning,
        "info": info,
    }


def _validate_one(
    brief: dict[str, Any],
    *,
    require_us: bool,
    blocking: list[dict[str, Any]],
    warning: list[dict[str, Any]],
) -> None:
    slug = str(brief.get("slug"))
    primary = ((brief.get("keywords") or {}).get("primary") or {})
    if int(primary.get("au_volume") or 0) <= 0:
        blocking.append(_issue("missing_primary_au_volume", "Primary keyword has no AU volume.", slug=slug))
    if require_us and int(primary.get("us_volume") or 0) <= 0:
        blocking.append(_issue("missing_primary_us_volume", "Primary keyword has no US volume.", slug=slug))
    if not primary.get("source"):
        blocking.append(_issue("missing_keyword_source", "Primary keyword is missing a source label.", slug=slug))
    if not ((brief.get("keywords") or {}).get("supplemental") or []):
        blocking.append(_issue(
            "missing_supplemental_keywords",
            "No supplemental SE Ranking keyword opportunities are attached.",
            slug=slug,
        ))
    if not (brief.get("search_console_opportunities") or []):
        warning.append(_issue(
            "missing_search_console_opportunities",
            "No Search Console opportunity queries are attached.",
            slug=slug,
        ))

    page = brief.get("current_page") or {}
    for field in ("title", "h1", "copy_summary"):
        if not page.get(field):
            blocking.append(_issue("missing_current_page_field", f"Current page field '{field}' is missing.", slug=slug))
    if not page.get("meta_description"):
        warning.append(_issue("missing_meta_description", "No current meta description was detected.", slug=slug))

    # Warn when H1 doesn't contain any token of the primary keyword — signals likely keyword/H1 mismatch.
    h1 = (page.get("h1") or "").lower()
    primary_kw = (primary.get("keyword") or "").lower()
    primary_tokens = set(primary_kw.split())
    h1_tokens = set(h1.split())
    if primary_tokens and not primary_tokens & h1_tokens:
        warning.append(_issue(
            "h1_primary_keyword_mismatch",
            f"H1 '{page.get('h1')}' shares no words with primary keyword '{primary.get('keyword')}'. "
            "Consider updating the H1 or confirming the primary keyword is correct.",
            slug=slug,
        ))

    products = (brief.get("product_context") or {}).get("sample_product_titles") or []
    if not products:
        blocking.append(_issue("missing_product_context", "No product sample titles are present.", slug=slug))

    serp_results = (brief.get("serp_context") or {}).get("serp_results") or []
    if not serp_results:
        blocking.append(_issue("missing_serp_context", "No structured SERP results are present.", slug=slug))
    elif not any(result.get("title") for result in serp_results):
        blocking.append(_issue("missing_serp_titles", "SERP results do not include competitor titles.", slug=slug))

    links = brief.get("internal_links") or []
    if len(links) < 5:
        blocking.append(_issue("insufficient_internal_links", "Fewer than five internal links are present.", slug=slug))
    if any(link.get("target_slug") == slug for link in links):
        blocking.append(_issue("self_internal_link", "Internal link plan contains a self-link.", slug=slug))
    for link in links:
        if not link.get("anchor_text") or not link.get("target_url") or not link.get("placement"):
            blocking.append(_issue("incomplete_internal_link", "Internal link entry is missing anchor, URL, or placement.", slug=slug))
            break

    recommendations = brief.get("content_recommendations") or {}
    if not recommendations.get("structure") or not recommendations.get("keyword_inclusion"):
        blocking.append(_issue("missing_content_recommendations", "Content recommendations are incomplete.", slug=slug))
    if not brief.get("writer_prompt"):
        blocking.append(_issue("missing_writer_prompt", "Writer/LLM prompt is missing.", slug=slug))
    if len(brief.get("qa_checklist") or []) < 4:
        warning.append(_issue("thin_qa_checklist", "Brief QA checklist has fewer than four checks.", slug=slug))


def _issue(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **details}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--briefs-json", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = validate(client_json=args.client_json, briefs_json=args.briefs_json)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text)
        print(f"Wrote content brief validation to {args.output}")
    else:
        print(text)
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
