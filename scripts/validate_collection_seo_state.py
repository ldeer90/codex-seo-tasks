"""Validate Collection SEO sidecar state against offline MCP exports.

This script makes no live API calls. Fetch live MCP data in the agent session,
save it to JSON, then run this validator before creating client deliverables.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from collection_seo_utils import (
    coverage_label,
    engine_pair_stats,
    included_collections,
    keyword_names_for_url,
    page_state_by_slug,
    parse_seranking_keywords,
    read_json,
)


def validate(
    *,
    client_json: Path,
    seranking_keywords_json: Path,
    pages_json: Path | None = None,
    serp_json: Path | None = None,
) -> dict[str, Any]:
    client = read_json(client_json, {})
    keywords = parse_seranking_keywords(read_json(seranking_keywords_json, []))
    pages = page_state_by_slug(read_json(pages_json, {}) if pages_json else {})
    serp = read_json(serp_json, None) if serp_json else None

    blocking: list[dict[str, Any]] = []
    warning: list[dict[str, Any]] = []
    info: list[dict[str, Any]] = []

    collections = included_collections(client)
    stats = engine_pair_stats(keywords)
    market_scope = str(client.get("market_scope", "AU")).upper()
    expected_engines = _expected_engine_ids(client, market_scope)

    if not collections:
        blocking.append(_issue("no_collections", "Sidecar has no included collections."))

    summary = client.get("discovery_summary") or {}
    expected_total = summary.get("total_after_filter")
    if expected_total is not None and int(expected_total) != len(client.get("collections", [])):
        warning.append(_issue(
            "collection_count_mismatch",
            "Discovery summary total_after_filter does not match sidecar collection count.",
            expected=expected_total,
            actual=len(client.get("collections", [])),
        ))

    _check_cached_deliverable_paths(_repo_root_for_client_json(client_json), client, warning)
    _check_keyword_coverage(collections, keywords, expected_engines, blocking, warning)
    _check_sidecar_volumes(collections, market_scope, blocking)
    _check_current_page_state(collections, pages, blocking)
    _check_deliverable_coverage(client, collections, stats, warning)
    _check_serp_shape(collections, serp, serp_json, blocking, warning)

    info.append(_issue(
        "live_seranking_counts",
        "SE Ranking export counts parsed successfully.",
        keyword_count=stats["keyword_count"],
        pair_count=stats["pair_count"],
    ))

    result = {
        "ok": not blocking,
        "summary": {
            "client": client.get("client"),
            "included_collections": len(collections),
            "live_keyword_count": stats["keyword_count"],
            "live_pair_count": stats["pair_count"],
            "blocking_count": len(blocking),
            "warning_count": len(warning),
        },
        "blocking": blocking,
        "warning": warning,
        "info": info,
    }
    return result


def _expected_engine_ids(client: dict[str, Any], market_scope: str) -> list[int]:
    engines = client.get("se_ranking", {}).get("engines", {})
    expected = []
    if "AU" in engines:
        expected.append(int(engines["AU"]))
    if "US" in market_scope and "US" in engines:
        expected.append(int(engines["US"]))
    return expected


def _repo_root_for_client_json(client_json: Path) -> Path:
    parts = client_json.parts
    if len(parts) >= 4 and parts[-3:] == ("agent", "clients", client_json.name):
        return client_json.parents[3]
    return client_json.parent


def _check_cached_deliverable_paths(
    repo_root: Path,
    client: dict[str, Any],
    warning: list[dict[str, Any]],
) -> None:
    for key, value in (client.get("deliverables") or {}).items():
        if not isinstance(value, dict):
            continue
        path = value.get("path")
        if path and not (repo_root / path).exists():
            warning.append(_issue(
                "missing_deliverable_path",
                f"Deliverable path for {key} does not exist.",
                path=path,
            ))


def _check_keyword_coverage(
    collections: list[dict[str, Any]],
    keywords: list[dict[str, Any]],
    expected_engines: list[int],
    blocking: list[dict[str, Any]],
    warning: list[dict[str, Any]],
) -> None:
    for collection in collections:
        slug = collection.get("slug")
        names = keyword_names_for_url(keywords, collection.get("url", ""))
        primary = str(collection.get("primary_keyword", "")).lower().strip()
        if not names:
            issue = _issue(
                "missing_live_keywords",
                "No live SE Ranking keywords target this collection URL.",
                slug=slug,
                url=collection.get("url"),
            )
            if collection.get("tracking_required") is False:
                warning.append({
                    **issue,
                    "message": "Collection is intentionally not required to be tracked in SE Ranking.",
                })
            else:
                blocking.append(issue)
        elif primary and primary not in names:
            warning.append(_issue(
                "primary_keyword_not_tracked",
                "Collection has live keywords but its primary keyword is not tracked.",
                slug=slug,
                primary_keyword=collection.get("primary_keyword"),
            ))

    if expected_engines:
        for kw in keywords:
            kw_engines = {int(e) for e in (kw.get("site_engine_ids") or [])}
            missing = [e for e in expected_engines if e not in kw_engines]
            if missing:
                blocking.append(_issue(
                    "missing_engine_pair",
                    "A live keyword is missing one or more expected search engines.",
                    keyword=kw.get("name") or kw.get("keyword"),
                    missing_site_engine_ids=missing,
                ))
                if len(blocking) > 25:
                    blocking.append(_issue(
                        "missing_engine_pair_truncated",
                        "More engine-pair errors exist; output truncated.",
                    ))
                    break


def _check_sidecar_volumes(
    collections: list[dict[str, Any]],
    market_scope: str,
    blocking: list[dict[str, Any]],
) -> None:
    for collection in collections:
        if collection.get("allow_zero_volume") is True:
            continue
        if int(collection.get("au_volume") or 0) <= 0:
            blocking.append(_issue(
                "missing_au_volume",
                "Included collection is missing AU volume in the sidecar.",
                slug=collection.get("slug"),
                primary_keyword=collection.get("primary_keyword"),
            ))
        if "US" in market_scope and int(collection.get("us_volume") or 0) <= 0:
            blocking.append(_issue(
                "missing_us_volume",
                "Included AU+US collection is missing US volume in the sidecar.",
                slug=collection.get("slug"),
                primary_keyword=collection.get("primary_keyword"),
            ))


def _check_current_page_state(
    collections: list[dict[str, Any]],
    pages: dict[str, dict[str, Any]],
    blocking: list[dict[str, Any]],
) -> None:
    for collection in collections:
        slug = collection.get("slug")
        page = pages.get(str(slug), {})
        title = page.get("title") or collection.get("current_title")
        h1 = page.get("h1") or collection.get("current_h1")
        if not title or not h1:
            blocking.append(_issue(
                "missing_current_page_state",
                "Current title/H1 is missing from pages export and sidecar.",
                slug=slug,
                has_title=bool(title),
                has_h1=bool(h1),
            ))


def _check_deliverable_coverage(
    client: dict[str, Any],
    collections: list[dict[str, Any]],
    stats: dict[str, int],
    warning: list[dict[str, Any]],
) -> None:
    sidecar_stats = client.get("se_ranking", {})
    if sidecar_stats.get("keyword_count") and int(sidecar_stats["keyword_count"]) != stats["keyword_count"]:
        warning.append(_issue(
            "keyword_count_stale",
            "Sidecar keyword_count differs from live SE Ranking export.",
            sidecar=sidecar_stats.get("keyword_count"),
            live=stats["keyword_count"],
        ))
    if sidecar_stats.get("pair_count") and int(sidecar_stats["pair_count"]) != stats["pair_count"]:
        warning.append(_issue(
            "pair_count_stale",
            "Sidecar pair_count differs from live SE Ranking export.",
            sidecar=sidecar_stats.get("pair_count"),
            live=stats["pair_count"],
        ))

    expected = coverage_label(len(collections), len(collections))
    for key, deliverable in (client.get("deliverables") or {}).items():
        if not isinstance(deliverable, dict):
            continue
        coverage = deliverable.get("coverage")
        if coverage and not _coverage_matches(coverage, len(collections)):
            warning.append(_issue(
                "stale_deliverable_coverage",
                f"Deliverable {key} coverage does not match included collection count.",
                coverage=coverage,
                expected=expected,
            ))


def _check_serp_shape(
    collections: list[dict[str, Any]],
    serp: Any,
    serp_json: Path | None,
    blocking: list[dict[str, Any]],
    warning: list[dict[str, Any]],
) -> None:
    if serp_json is None:
        warning.append(_issue("serp_json_not_provided", "No SERP JSON provided for validation."))
        return
    if serp is None:
        blocking.append(_issue("serp_json_missing", "SERP JSON path was provided but could not be read."))
        return
    if isinstance(serp, dict):
        missing = []
        malformed = []
        for collection in collections:
            slug = collection.get("slug")
            node = serp.get(str(slug))
            if not isinstance(node, dict):
                missing.append(slug)
                continue
            results = node.get("serp_results")
            if not isinstance(results, list):
                malformed.append(slug)
        if missing:
            blocking.append(_issue(
                "missing_structured_serp",
                "Structured SERP JSON is missing included collections.",
                slugs=missing,
            ))
        if malformed:
            blocking.append(_issue(
                "malformed_structured_serp",
                "Structured SERP entries must contain serp_results arrays.",
                slugs=malformed,
            ))
    elif isinstance(serp, list):
        warning.append(_issue(
            "legacy_flat_serp",
            "SERP JSON is a legacy flat list. Generator can read it, but structured per-slug JSON is required for cache-safe workflows.",
        ))
    else:
        blocking.append(_issue(
            "invalid_serp_json",
            "SERP JSON must be either a structured object or legacy flat list.",
            actual_type=type(serp).__name__,
        ))

    missing_competitors = [
        c.get("slug") for c in collections
        if not c.get("competitor_top3_urls")
    ]
    if missing_competitors:
        warning.append(_issue(
            "missing_competitor_top3_urls",
            "Sidecar is missing competitor_top3_urls for included collections.",
            slugs=missing_competitors,
        ))


def _coverage_matches(coverage: str, total: int) -> bool:
    match = re.search(r"(\d+)\s+of\s+(\d+)", coverage)
    if not match:
        return True
    return int(match.group(1)) == total and int(match.group(2)) == total


def _issue(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **details}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--seranking-keywords-json", required=True, type=Path)
    parser.add_argument("--pages-json", type=Path)
    parser.add_argument("--serp-json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = validate(
        client_json=args.client_json,
        seranking_keywords_json=args.seranking_keywords_json,
        pages_json=args.pages_json,
        serp_json=args.serp_json,
    )
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text)

    s = result["summary"]
    print(
        f"Collection SEO QA: {'PASS' if result['ok'] else 'FAIL'} "
        f"({s['blocking_count']} blockers, {s['warning_count']} warnings)"
    )
    print(
        f"Client: {s.get('client')} | Collections: {s['included_collections']} | "
        f"Live keywords: {s['live_keyword_count']} | Pairs: {s['live_pair_count']}"
    )
    if not result["ok"]:
        for issue in result["blocking"][:10]:
            print(f"- BLOCKING {issue['code']}: {issue['message']}")
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
