"""Evaluate collection keyword candidates before adding them to SE Ranking.

This is an offline quality gate. Agents fetch candidate keywords from SE Ranking
Data API, Search Console, SERP exports, or product-derived sources, save them to
JSON, then run this script to score page fit, rankability, cannibalisation risk,
and business usefulness.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from collection_seo_utils import included_collections, parse_volume_map, read_json


STOP_TOKENS = {
    "the", "and", "for", "with", "from", "shop", "buy", "online", "australia",
    "australian", "women", "womens", "mens", "men", "collection", "collections",
}

CATALOG_MISMATCH_PATTERNS: list[tuple[re.Pattern[str], set[str]]] = [
    (re.compile(r"\b(kids?|children|girls?|boys?|toddler|baby|infant)\b"), {"KIDS", "CHILDREN", "GIRLS", "BOYS"}),
    (re.compile(r"\b(maternity|pregnancy|nursing|breastfeeding)\b"), {"MATERNITY", "NURSING"}),
    (re.compile(r"\b(period|menstrual|period[- ]proof)\b"), {"PERIOD", "PERIOD_PROOF"}),
    (re.compile(r"\b(mens?|menswear|male)\b"), {"MENS", "MENSWEAR"}),
    (re.compile(r"\b(plus size|curvy|extended size)\b"), {"PLUS", "CURVY"}),
]

DEFAULT_BRAND_DENYLIST = {
    "kmart", "target", "myer", "david jones", "asos", "boohoo", "shein", "zara",
    "seafolly", "baku", "speedo", "zimmermann", "aje", "ganni", "showpo",
    "white fox", "princess polly", "meshki",
}


def evaluate_candidates(
    *,
    client_json: Path,
    candidates_json: Path,
    volume_json_au: Path | None = None,
    volume_json_us: Path | None = None,
    gsc_json: Path | None = None,
    serp_json: Path | None = None,
    min_volume: int = 100,
    max_difficulty: int = 70,
    min_score: float = 0.55,
    top_n: int = 8,
) -> dict[str, Any]:
    client = read_json(client_json, {})
    collections = included_collections(client)
    candidates = _normalise_candidates(read_json(candidates_json, {}), collections)
    au_volumes = parse_volume_map(read_json(volume_json_au, {}) if volume_json_au else {})
    us_volumes = parse_volume_map(read_json(volume_json_us, {}) if volume_json_us else {})
    gsc = _normalise_gsc(read_json(gsc_json, {}) if gsc_json else {})
    serp = read_json(serp_json, {}) if serp_json else {}
    denylist = DEFAULT_BRAND_DENYLIST | {normalise_keyword(v) for v in client.get("brand_denylist") or []}

    primary_owner = {
        normalise_keyword(c.get("primary_keyword")): str(c.get("slug"))
        for c in collections
        if c.get("primary_keyword")
    }
    by_slug = {str(c.get("slug")): c for c in collections}
    accepted: dict[str, list[dict[str, Any]]] = {}
    rejected: list[dict[str, Any]] = []

    for slug, rows in candidates.items():
        collection = by_slug.get(slug)
        if not collection:
            continue
        scored: list[dict[str, Any]] = []
        catalog_types = _catalog_types(collection)
        for row in rows:
            keyword = normalise_keyword(row.get("keyword") or row.get("query") or row.get("name"))
            if not keyword:
                continue
            reject_reason = _hard_reject_reason(
                keyword=keyword,
                slug=slug,
                primary_owner=primary_owner,
                denylist=denylist,
                catalog_types=catalog_types,
            )
            if reject_reason:
                rejected.append(_rejection(keyword, slug, reject_reason))
                continue

            au_volume = _volume(keyword, row, au_volumes, "au_volume")
            us_volume = _volume(keyword, row, us_volumes, "us_volume")
            if au_volume < min_volume:
                rejected.append(_rejection(keyword, slug, "low_au_volume", str(au_volume)))
                continue

            difficulty = _difficulty(row)
            if difficulty is not None and difficulty > max_difficulty:
                rejected.append(_rejection(keyword, slug, "too_difficult", str(difficulty)))
                continue

            fit = _page_fit(keyword, collection)
            cannibalisation = _cannibalisation_risk(keyword, slug, collections)
            rankability = _rankability_score(difficulty)
            volume_score = _volume_score(au_volume)
            gsc_score, gsc_reason = _gsc_score(keyword, gsc.get(slug, []))
            serp_score, serp_reason = _serp_score(keyword, serp.get(slug, {}) if isinstance(serp, dict) else {})
            intent_score = _intent_score(row)

            score = (
                fit * 0.30
                + rankability * 0.20
                + volume_score * 0.20
                + gsc_score * 0.15
                + serp_score * 0.10
                + intent_score * 0.05
                - cannibalisation * 0.25
            )
            if score < min_score:
                rejected.append(_rejection(keyword, slug, "low_expert_score", f"{score:.2f}"))
                continue
            rationale = _rationale(
                keyword=keyword,
                fit=fit,
                rankability=rankability,
                volume=au_volume,
                gsc_reason=gsc_reason,
                serp_reason=serp_reason,
                cannibalisation=cannibalisation,
            )
            scored.append({
                "keyword": keyword,
                "target_url": collection.get("url", ""),
                "collection_slug": slug,
                "au_volume": au_volume,
                "us_volume": us_volume,
                "difficulty": difficulty if difficulty is not None else "",
                "intent": row.get("intent") or row.get("intents") or "",
                "source": row.get("source") or "SE Ranking candidate export",
                "expert_score": round(score, 4),
                "score_breakdown": {
                    "page_fit": round(fit, 3),
                    "rankability": round(rankability, 3),
                    "volume": round(volume_score, 3),
                    "gsc": round(gsc_score, 3),
                    "serp": round(serp_score, 3),
                    "intent": round(intent_score, 3),
                    "cannibalisation_penalty": round(cannibalisation, 3),
                },
                "rationale": rationale,
                "tracking_recommendation": "add_to_se_ranking",
            })

        scored.sort(key=lambda item: (-item["expert_score"], -int(item["au_volume"]), item["keyword"]))
        accepted[slug] = _dedupe_keywords(scored)[:top_n]

    return {
        "client": client.get("client"),
        "summary": {
            "collections": len(collections),
            "collections_with_candidates": sum(1 for rows in accepted.values() if rows),
            "accepted_keywords": sum(len(rows) for rows in accepted.values()),
            "rejected_keywords": len(rejected),
            "filters": {
                "min_volume": min_volume,
                "max_difficulty": max_difficulty,
                "min_score": min_score,
                "top_n": top_n,
            },
        },
        "by_slug": accepted,
        "rejected": rejected[:300],
    }


def _hard_reject_reason(
    *,
    keyword: str,
    slug: str,
    primary_owner: dict[str, str],
    denylist: set[str],
    catalog_types: set[str],
) -> str:
    owner = primary_owner.get(keyword)
    if owner and owner != slug:
        return f"primary_keyword_of_{owner}"
    if any(re.search(r"\b" + re.escape(brand) + r"\b", keyword) for brand in denylist if brand):
        return "brand_or_retailer_contamination"
    for pattern, required in CATALOG_MISMATCH_PATTERNS:
        if pattern.search(keyword) and not (catalog_types & required):
            return "catalog_mismatch"
    return ""


def _page_fit(keyword: str, collection: dict[str, Any]) -> float:
    keyword_tokens = tokens(keyword)
    signals = tokens(
        collection.get("slug"),
        collection.get("primary_keyword"),
        collection.get("current_h1"),
        collection.get("dominant_product_type"),
        " ".join(str(t) for t in collection.get("sample_product_titles") or []),
    )
    if not keyword_tokens or not signals:
        return 0.0
    return len(keyword_tokens & signals) / len(keyword_tokens | signals)


def _cannibalisation_risk(keyword: str, slug: str, collections: list[dict[str, Any]]) -> float:
    kw_tokens = tokens(keyword)
    if not kw_tokens:
        return 0.0
    current_overlap = 0
    highest_other = 0
    for collection in collections:
        overlap = len(kw_tokens & tokens(collection.get("primary_keyword"), collection.get("slug")))
        if collection.get("slug") == slug:
            current_overlap = overlap
        else:
            highest_other = max(highest_other, overlap)
    if highest_other <= current_overlap:
        return 0.0
    return min(1.0, (highest_other - current_overlap) / max(len(kw_tokens), 1))


def _rankability_score(difficulty: float | None) -> float:
    if difficulty is None:
        return 0.55
    return max(0.0, 1.0 - (difficulty / 80.0))


def _volume_score(volume: int) -> float:
    if volume <= 0:
        return 0.0
    return min(1.0, math.log10(volume + 1) / math.log10(40000))


def _gsc_score(keyword: str, rows: list[dict[str, Any]]) -> tuple[float, str]:
    for row in rows:
        query = normalise_keyword(row.get("query") or row.get("keyword"))
        if query != keyword:
            continue
        position = _float(row.get("position"))
        impressions = _float(row.get("impressions"))
        if position >= 8 and impressions > 0:
            return 1.0, f"GSC shows impressions at average position {position:g}"
        if impressions > 0:
            return 0.45, "GSC already shows impressions"
    return 0.0, ""


def _serp_score(keyword: str, node: dict[str, Any]) -> tuple[float, str]:
    text_parts = []
    for result in node.get("serp_results") or []:
        if isinstance(result, dict):
            text_parts.append(str(result.get("title") or ""))
            text_parts.append(str(result.get("h1") or ""))
    haystack = " ".join(text_parts).lower()
    kw_tokens = tokens(keyword)
    if not haystack or not kw_tokens:
        return 0.0, ""
    overlap = sum(1 for token in kw_tokens if token in haystack)
    if overlap == len(kw_tokens):
        return 0.8, "SERP competitors commonly use this phrase or close variants"
    if overlap:
        return 0.35, "SERP competitors use overlapping language"
    return 0.0, ""


def _intent_score(row: dict[str, Any]) -> float:
    intent = str(row.get("intent") or row.get("intents") or "").lower()
    if any(term in intent for term in ("transaction", "commercial")):
        return 1.0
    if "informational" in intent or "navigational" in intent:
        return 0.25
    return 0.65


def _rationale(
    *,
    keyword: str,
    fit: float,
    rankability: float,
    volume: int,
    gsc_reason: str,
    serp_reason: str,
    cannibalisation: float,
) -> str:
    parts = [
        f"'{keyword}' fits this collection with page-fit score {fit:.2f}",
        f"has AU volume {volume}",
        f"rankability score {rankability:.2f}",
    ]
    if gsc_reason:
        parts.append(gsc_reason)
    if serp_reason:
        parts.append(serp_reason)
    if cannibalisation:
        parts.append(f"cannibalisation risk remains {cannibalisation:.2f}, review manually")
    return "; ".join(parts) + "."


def _normalise_candidates(raw: Any, collections: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    if isinstance(raw, dict) and isinstance(raw.get("by_slug"), dict):
        raw = raw["by_slug"]
    if isinstance(raw, dict):
        return {
            str(slug): _rows(rows)
            for slug, rows in raw.items()
            if isinstance(rows, list)
        }
    if isinstance(raw, list):
        by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in _rows(raw):
            keyword = normalise_keyword(row.get("keyword") or row.get("query"))
            best_slug = ""
            best_score = -1
            for collection in collections:
                overlap = len(tokens(keyword) & tokens(collection.get("primary_keyword"), collection.get("slug")))
                if overlap > best_score:
                    best_score = overlap
                    best_slug = str(collection.get("slug"))
            if best_slug:
                by_slug[best_slug].append(row)
        return dict(by_slug)
    return {}


def _rows(rows: Any) -> list[dict[str, Any]]:
    out = []
    for row in rows if isinstance(rows, list) else []:
        if isinstance(row, str):
            out.append({"keyword": row})
        elif isinstance(row, dict):
            out.append(row)
    return out


def _normalise_gsc(raw: Any) -> dict[str, list[dict[str, Any]]]:
    if isinstance(raw, dict) and isinstance(raw.get("by_slug"), dict):
        raw = raw["by_slug"]
    if not isinstance(raw, dict):
        return {}
    return {str(k): v for k, v in raw.items() if isinstance(v, list)}


def _catalog_types(collection: dict[str, Any]) -> set[str]:
    values = {str(v).upper() for v in collection.get("product_types") or []}
    if collection.get("dominant_product_type"):
        values.add(str(collection["dominant_product_type"]).upper())
    return values


def _volume(keyword: str, row: dict[str, Any], volume_map: dict[str, int], field: str) -> int:
    return int(volume_map.get(keyword) or row.get(field) or row.get("volume") or row.get("search_volume") or 0)


def _difficulty(row: dict[str, Any]) -> float | None:
    for key in ("difficulty", "kd", "keyword_difficulty"):
        if row.get(key) is None:
            continue
        try:
            return float(row[key])
        except (TypeError, ValueError):
            return None
    return None


def _dedupe_keywords(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for row in rows:
        keyword = row["keyword"]
        if keyword in seen:
            continue
        seen.add(keyword)
        out.append(row)
    return out


def normalise_keyword(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def tokens(*values: Any) -> set[str]:
    return {
        token for value in values
        for token in re.findall(r"[a-z0-9]+", str(value).lower())
        if token not in STOP_TOKENS and len(token) > 2
    }


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _rejection(keyword: str, slug: str, reason: str, detail: str = "") -> dict[str, str]:
    return {"keyword": keyword, "slug": slug, "reason": reason, "detail": detail}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--candidates-json", required=True, type=Path)
    parser.add_argument("--volume-json-au", type=Path)
    parser.add_argument("--volume-json-us", type=Path)
    parser.add_argument("--gsc-json", type=Path)
    parser.add_argument("--serp-json", type=Path)
    parser.add_argument("--min-volume", type=int, default=100)
    parser.add_argument("--max-difficulty", type=int, default=70)
    parser.add_argument("--min-score", type=float, default=0.55)
    parser.add_argument("--top-n", type=int, default=8)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    result = evaluate_candidates(
        client_json=args.client_json,
        candidates_json=args.candidates_json,
        volume_json_au=args.volume_json_au,
        volume_json_us=args.volume_json_us,
        gsc_json=args.gsc_json,
        serp_json=args.serp_json,
        min_volume=args.min_volume,
        max_difficulty=args.max_difficulty,
        min_score=args.min_score,
        top_n=args.top_n,
    )
    args.output.write_text(json.dumps(result, indent=2))
    s = result["summary"]
    print(
        f"Wrote keyword candidate evaluation to {args.output}\n"
        f"  Accepted: {s['accepted_keywords']} | Rejected: {s['rejected_keywords']} | "
        f"Collections covered: {s['collections_with_candidates']} / {s['collections']}"
    )


if __name__ == "__main__":
    main()
