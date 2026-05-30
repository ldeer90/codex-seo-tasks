"""Validate a client JSON file for completeness before running any SEO workflow.

Run this at Phase 0 of every workflow. It makes no live API calls.
Zero blockers required before proceeding to any deliverable phase.

Usage:
    python scripts/validate_client_json.py --client-json docs/agent/clients/<client>.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Top-level required fields
# ---------------------------------------------------------------------------

_REQUIRED_TOP_LEVEL: list[tuple[str, str]] = [
    ("client", "Legal or trading name used in Doc titles and Monday tasks."),
    ("brand_display_name", "Typographically correct brand name for first mention in copy. e.g. 'MÉLANI'."),
    ("brand_voice", "One paragraph describing the brand register and what good copy sounds like."),
    ("tone_direction", "One or two sentences of specific writer guidance."),
    ("domain", "Root domain without protocol. e.g. 'melanithelabel.com'."),
    ("market_scope", "One of: AU, US, AU+US."),
    ("usp", "Primary customer-facing benefit, factual."),
]

_OPTIONAL_TOP_LEVEL_WARNINGS: list[tuple[str, str]] = [
    ("brand_denylist", "Competitor/retailer brand names to filter from keyword research. Absence means only the global denylist applies."),
    ("ga4_property", "GA4 property ID. Required for traffic data pulls."),
]

_VALID_MARKET_SCOPES = {"AU", "US", "AU+US"}
_VALID_CLASSES = {"pure_category", "themed_category", "curated_edit", "occasion_edit", "fabric_edit"}
_VALID_WORKFLOW_PROFILES = {"full", "audit_only"}


def _workflow_profile(client: dict[str, Any]) -> str:
    profile = client.get("workflow_profile") or "full"
    return profile if profile in _VALID_WORKFLOW_PROFILES else "full"


# ---------------------------------------------------------------------------
# Per-collection required fields
# ---------------------------------------------------------------------------

_REQUIRED_COLLECTION_FIELDS: list[tuple[str, str]] = [
    ("slug", "Shopify collection handle."),
    ("url", "Full canonical URL."),
    ("class", f"One of: {', '.join(sorted(_VALID_CLASSES))}."),
    ("dominant_product_type", "Primary Shopify product type in UPPERCASE. Must match catalog reality, not be a shorthand."),
    ("primary_keyword", "The single target keyword for this collection page."),
    ("current_h1", "Current H1, scraped live."),
    ("last_scraped", "ISO date of most recent live scrape."),
]

_COLLECTION_VOLUME_FIELDS: dict[str, list[str]] = {
    "AU": ["au_volume"],
    "US": ["us_volume"],
    "AU+US": ["au_volume", "us_volume"],
}


# ---------------------------------------------------------------------------
# Issue helpers
# ---------------------------------------------------------------------------

def _blocking(code: str, message: str, **ctx: Any) -> dict[str, Any]:
    return {"severity": "blocking", "code": code, "message": message, **ctx}


def _warning(code: str, message: str, **ctx: Any) -> dict[str, Any]:
    return {"severity": "warning", "code": code, "message": message, **ctx}


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def _validate_top_level(client: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []

    for field, hint in _REQUIRED_TOP_LEVEL:
        val = client.get(field)
        if not val or (isinstance(val, str) and (not val.strip() or val.startswith("REQUIRED"))):
            issues.append(_blocking(
                "missing_required_field",
                f"'{field}' is required but missing or unfilled. {hint}",
                field=field,
            ))

    market = client.get("market_scope", "")
    if market and market not in _VALID_MARKET_SCOPES:
        issues.append(_blocking(
            "invalid_market_scope",
            f"market_scope '{market}' is not valid. Must be one of: {', '.join(sorted(_VALID_MARKET_SCOPES))}.",
        ))

    profile = client.get("workflow_profile")
    if profile and profile not in _VALID_WORKFLOW_PROFILES:
        issues.append(_blocking(
            "invalid_workflow_profile",
            f"workflow_profile '{profile}' is not valid. Must be one of: {', '.join(sorted(_VALID_WORKFLOW_PROFILES))}.",
        ))

    for field, hint in _OPTIONAL_TOP_LEVEL_WARNINGS:
        if not client.get(field):
            issues.append(_warning("missing_optional_field", f"'{field}' is absent. {hint}", field=field))

    return issues


def _validate_se_ranking(client: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    ser = client.get("se_ranking") or {}

    if not ser.get("project_id"):
        issues.append(_blocking("missing_se_ranking_project_id", "se_ranking.project_id is required."))

    market = client.get("market_scope", "")
    engines = ser.get("engines") or {}
    if "AU" in market and not engines.get("AU"):
        issues.append(_blocking("missing_se_ranking_engine_au", "se_ranking.engines.AU is required for AU market scope."))
    if "US" in market and not engines.get("US"):
        issues.append(_blocking("missing_se_ranking_engine_us", "se_ranking.engines.US is required for US market scope."))

    return issues


def _validate_drive(client: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    drive = client.get("drive") or {}
    audit_only = _workflow_profile(client) == "audit_only"

    if not drive.get("client_folder_id"):
        if audit_only:
            issues.append(_warning(
                "missing_drive_client_folder",
                "drive.client_folder_id is absent. Audit-only workflows may proceed, but Drive outputs must stop until a client folder is confirmed.",
            ))
        else:
            issues.append(_blocking("missing_drive_client_folder", "drive.client_folder_id is required."))

    folders = drive.get("folders") or {}
    has_content_folder = folders.get("05_content") or folders.get("content_briefs")
    if not has_content_folder:
        issues.append(_warning(
            "missing_content_folder",
            "drive.folders.05_content (or content_briefs) is absent. "
            "The agent will stop and ask before writing any content brief Doc.",
        ))

    return issues


def _validate_monday(client: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    monday = client.get("monday") or {}
    audit_only = _workflow_profile(client) == "audit_only"

    if not monday.get("board_id"):
        if audit_only:
            issues.append(_warning(
                "missing_monday_board_id",
                "monday.board_id is absent. Audit-only workflows may proceed, but Monday task creation must stop until a board is confirmed.",
            ))
        else:
            issues.append(_blocking("missing_monday_board_id", "monday.board_id is required for task creation."))

    groups = monday.get("groups") or {}
    if not any(groups.values()):
        issues.append(_warning(
            "missing_monday_group",
            "monday.groups has no target group. The agent will stop and ask before writing tasks.",
        ))

    return issues


def _validate_collections(client: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    collections = client.get("collections") or []
    market = client.get("market_scope", "")
    volume_fields = _COLLECTION_VOLUME_FIELDS.get(market, [])
    audit_only = _workflow_profile(client) == "audit_only"

    if not collections:
        if audit_only:
            issues.append(_warning(
                "no_collections",
                "No collections are defined. Audit-only workflows may proceed; content/collection workflows must stop until priority pages are added.",
            ))
            return issues
        issues.append(_blocking("no_collections", "No collections are defined. Add at least one collection object."))
        return issues

    slugs_seen: set[str] = set()
    for i, col in enumerate(collections):
        slug = col.get("slug") or f"collection[{i}]"

        if slug in slugs_seen:
            issues.append(_blocking("duplicate_slug", f"Duplicate slug '{slug}'.", slug=slug))
        slugs_seen.add(slug)

        for field, hint in _REQUIRED_COLLECTION_FIELDS:
            val = col.get(field)
            if not val or (isinstance(val, str) and (not val.strip() or val.startswith("REQUIRED"))):
                issues.append(_blocking(
                    "missing_collection_field",
                    f"[{slug}] '{field}' is required. {hint}",
                    slug=slug, field=field,
                ))

        for vfield in volume_fields:
            if not col.get(vfield):
                issues.append(_blocking(
                    "missing_collection_volume",
                    f"[{slug}] '{vfield}' is required for market_scope '{market}'.",
                    slug=slug, field=vfield,
                ))

        # Warn on collection class not in allowed set.
        col_class = col.get("class", "")
        if col_class and col_class not in _VALID_CLASSES:
            issues.append(_warning(
                "invalid_collection_class",
                f"[{slug}] class '{col_class}' is not a recognised value. Expected one of: {', '.join(sorted(_VALID_CLASSES))}.",
                slug=slug,
            ))

        # Warn on H1/primary keyword mismatch.
        h1 = (col.get("current_h1") or "").lower()
        primary = (col.get("primary_keyword") or "").lower()
        if h1 and primary:
            h1_tokens = set(h1.split())
            pk_tokens = set(primary.split())
            if not h1_tokens & pk_tokens:
                issues.append(_warning(
                    "h1_primary_keyword_mismatch",
                    f"[{slug}] H1 '{col.get('current_h1')}' shares no words with primary keyword '{col.get('primary_keyword')}'. "
                    "Recommend updating H1 or confirming the keyword target before writing the brief.",
                    slug=slug,
                ))

        # Warn on dominant_product_type absent or clearly mismatched.
        dpt = (col.get("dominant_product_type") or "").upper()
        if not dpt:
            issues.append(_warning(
                "missing_dominant_product_type",
                f"[{slug}] dominant_product_type is absent. Internal link scoring and catalog filtering will be degraded.",
                slug=slug,
            ))
        elif dpt in ("TOP", "TOPS") and any(
            w in (col.get("primary_keyword") or "").lower()
            for w in ("dress", "gown", "skirt", "jumpsuit", "swim")
        ):
            issues.append(_warning(
                "likely_dominant_product_type_mismatch",
                f"[{slug}] dominant_product_type is '{dpt}' but primary keyword suggests a different product category. "
                "Verify this is correct — a mismatch sends internal links to the wrong collections.",
                slug=slug,
            ))

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate_client_json(client_json: Path) -> dict[str, Any]:
    client = json.loads(client_json.read_text())

    issues: list[dict[str, Any]] = []
    issues += _validate_top_level(client)
    issues += _validate_se_ranking(client)
    issues += _validate_drive(client)
    issues += _validate_monday(client)
    issues += _validate_collections(client)

    blocking = [i for i in issues if i["severity"] == "blocking"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    ok = len(blocking) == 0
    return {
        "ok": ok,
        "client": client.get("client", str(client_json)),
        "summary": {
            "blocking_count": len(blocking),
            "warning_count": len(warnings),
            "collection_count": len(client.get("collections") or []),
        },
        "blocking": blocking,
        "warning": warnings,
    }


def _cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of human-readable summary.")
    args = parser.parse_args()

    result = validate_client_json(args.client_json)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["ok"] else 1)

    client_name = result["client"]
    summary = result["summary"]
    print(f"\nClient JSON Validation — {client_name}")
    print(f"Collections: {summary['collection_count']} | Blockers: {summary['blocking_count']} | Warnings: {summary['warning_count']}")

    if result["blocking"]:
        print("\nBLOCKERS (must fix before proceeding):")
        for issue in result["blocking"]:
            print(f"  [{issue['code']}] {issue['message']}")

    if result["warning"]:
        print("\nWARNINGS:")
        for issue in result["warning"]:
            print(f"  [{issue['code']}] {issue['message']}")

    if result["ok"]:
        print("\n✓ No blockers. Safe to proceed.")
    else:
        print(f"\n✗ {summary['blocking_count']} blocker(s) must be resolved before running any workflow.")

    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    _cli()
