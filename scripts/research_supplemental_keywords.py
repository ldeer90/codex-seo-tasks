"""Score and assign supplemental keywords from raw SE Ranking research exports.

The agent session fetches raw related/similar/long-tail keyword data from the
SE Ranking Data API for each collection primary keyword and saves it to a raw
export file.  This script reads that raw dump, applies a multi-signal scoring
model, filters out irrelevant and contaminated candidates, deduplicates across
collections, and writes a clean ``by_slug`` supplemental keywords file ready
for ``build_collection_content_brief_inputs.py``.

Input (--raw-keywords-json) expected shape
------------------------------------------
Either a flat list (all keywords together, requires --primary-to-slug mapping)
or a dict keyed by collection slug:

    {
      "swim": [
        {"keyword": "one piece swimwear", "volume": 19100, "kd": 45, "intent": "Commercial"},
        ...
      ],
      "gowns": [...]
    }

SE Ranking related/similar API rows typically include:
  keyword, volume (or search_volume), kd (or difficulty), intent (or intents),
  cpc, competition, trend.

Output shape (--output)
-----------------------
    {
      "by_slug": {
        "swim": [
          {
            "keyword": "one piece swimwear",
            "au_volume": 19100,
            "us_volume": 0,
            "difficulty": 45,
            "intent": "Commercial",
            "opportunity_score": 0.78,
            "score_breakdown": {"volume": 0.82, "kd": 0.44, "relevance": 0.80, "gsc": 0.0},
            "source": "SE Ranking AU similar",
            "assigned_slug": "swim"
          },
          ...
        ]
      },
      "summary": {...},
      "filtered_out": [...]   # diagnostic: why each keyword was rejected
    }
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from collection_seo_utils import included_collections, read_json

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Brand / retailer names to exclude from supplemental keyword lists.
_BRAND_DENYLIST: frozenset[str] = frozenset({
    "kmart", "target", "myer", "david jones", "dj's", "djs",
    "asos", "boohoo", "shein", "zara", "h&m", "hm",
    "seafolly", "baku", "speedo", "funkita", "sunseeker",
    "monday", "zimmermann", "aje", "ganni", "shona joy",
    "realisation par", "alice mccall", "ginger and smart",
    "sass and bide", "country road", "witchery", "saba",
    "forever new", "princess polly", "beginning boutique",
    "meshki", "showpo", "white fox", "tiger mist",
    "pilgrim", "mango",
})

# Product-type exclusion: regex → required catalog type tokens (UPPER).
_CATALOG_EXCLUSIONS: list[tuple[re.Pattern[str], set[str]]] = [
    (re.compile(r"\b(kids?|children|girls?|boys?|toddler|baby|infant)\b"), {"KIDS", "CHILDREN", "GIRLS", "BOYS"}),
    (re.compile(r"\b(maternity|pregnancy|nursing|breastfeeding)\b"), {"MATERNITY", "NURSING"}),
    (re.compile(r"\b(period|menstrual|period[- ]proof)\b"), {"PERIOD"}),
    (re.compile(r"\b(mens?|menswear|male)\b"), {"MENS", "MENSWEAR"}),
    (re.compile(r"\b(plus size|curvy|extended size)\b"), {"PLUS", "CURVY"}),
]

# Intent labels treated as non-commercial — filtered unless volume is high.
_INFORMATIONAL_INTENTS: frozenset[str] = frozenset({
    "informational", "info", "navigational", "nav",
})

# Scoring weights (must sum to 1.0).
_W_VOLUME = 0.35
_W_KD = 0.25
_W_RELEVANCE = 0.25
_W_GSC = 0.10
_W_INTENT = 0.05

# Filtering thresholds.
_MIN_AU_VOLUME = 300          # strip anything below this — not worth a sentence
_MAX_KD = 70                  # strip anything harder than this
_MIN_RELEVANCE = 0.15         # at least some token overlap with the collection
_MIN_RELEVANCE_HIGH_VOL = 5000  # bypass relevance gate if volume is this high
_TOP_N_PER_COLLECTION = 15    # cap per brief

# Volume ceiling for normalisation — beyond this, score is 1.0.
_VOLUME_CEIL = 40_000


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def research_supplemental_keywords(
    *,
    client_json: Path,
    raw_keywords_json: Path,
    volume_json_au: Path | None = None,
    volume_json_us: Path | None = None,
    gsc_json: Path | None = None,
    min_volume: int = _MIN_AU_VOLUME,
    max_kd: int = _MAX_KD,
    top_n: int = _TOP_N_PER_COLLECTION,
) -> dict[str, Any]:
    client = read_json(client_json, {})
    raw = read_json(raw_keywords_json, {})
    au_volumes = _load_volume_map(read_json(volume_json_au, {}) if volume_json_au else {})
    us_volumes = _load_volume_map(read_json(volume_json_us, {}) if volume_json_us else {})
    gsc_by_slug = _load_gsc(read_json(gsc_json, {}) if gsc_json else {})

    collections = included_collections(client)
    by_slug_raw = _normalise_raw_input(raw, collections)

    # Build lookup tables from the collection roster.
    collection_by_slug = {str(c.get("slug")): c for c in collections}
    # All primary keywords already assigned — block them from supplemental lists.
    primary_keywords: dict[str, str] = {  # keyword → owning slug
        _norm(str(c.get("primary_keyword") or "")): str(c.get("slug"))
        for c in collections
        if c.get("primary_keyword")
    }

    # Merge per-collection brand denylist extensions from client JSON.
    client_denylist = frozenset(_norm(b) for b in (client.get("brand_denylist") or []))
    denylist = _BRAND_DENYLIST | client_denylist

    # Determine catalog type tokens per collection.
    catalog_types: dict[str, set[str]] = {}
    for c in collections:
        slug = str(c.get("slug"))
        types: set[str] = set()
        for t in (c.get("product_types") or []):
            types.add(str(t).upper())
        if c.get("dominant_product_type"):
            types.add(str(c["dominant_product_type"]).upper())
        catalog_types[slug] = types

    filtered_out: list[dict[str, Any]] = []
    scored_by_slug: dict[str, list[dict[str, Any]]] = {}

    for slug, raw_rows in by_slug_raw.items():
        collection = collection_by_slug.get(slug)
        if not collection:
            continue

        col_catalog_types = catalog_types.get(slug, set())
        gsc_queries = {row.get("query", "") for row in gsc_by_slug.get(slug, [])}
        gsc_positions = {
            row.get("query", ""): float(row.get("position") or 0)
            for row in gsc_by_slug.get(slug, [])
        }

        scored: list[dict[str, Any]] = []

        for row in raw_rows:
            keyword = _norm(row.get("keyword") or row.get("query") or "")
            if not keyword:
                continue

            # --- Hard filters (reject immediately) ---
            if keyword in primary_keywords:
                filtered_out.append(_rejection(keyword, slug, "primary_keyword_of_another_collection", primary_keywords[keyword]))
                continue

            if _is_brand_hit(keyword, denylist):
                filtered_out.append(_rejection(keyword, slug, "brand_contamination"))
                continue

            if _is_catalog_mismatch(keyword, col_catalog_types):
                filtered_out.append(_rejection(keyword, slug, "catalog_type_mismatch"))
                continue

            # Resolve volume: prefer explicit AU volume map, then row volume.
            au_vol = au_volumes.get(keyword) or int(row.get("au_volume") or row.get("volume") or row.get("search_volume") or 0)
            us_vol = us_volumes.get(keyword) or int(row.get("us_volume") or 0)

            if au_vol < min_volume:
                filtered_out.append(_rejection(keyword, slug, "low_volume", str(au_vol)))
                continue

            kd = _parse_kd(row)
            if kd is not None and kd > max_kd:
                filtered_out.append(_rejection(keyword, slug, "too_competitive", str(kd)))
                continue

            # Intent filter — only reject clear informational with low volume.
            intent_raw = str(row.get("intent") or row.get("intents") or "")
            intent_norm = intent_raw.lower()
            if intent_norm in _INFORMATIONAL_INTENTS and au_vol < 5000:
                filtered_out.append(_rejection(keyword, slug, "informational_intent_low_volume", str(au_vol)))
                continue

            # --- Soft scoring ---
            relevance = _relevance_score(keyword, collection)
            if relevance < _MIN_RELEVANCE and au_vol < _MIN_RELEVANCE_HIGH_VOL:
                filtered_out.append(_rejection(keyword, slug, "low_relevance", f"{relevance:.2f}"))
                continue

            vol_score = _volume_score(au_vol)
            kd_score = _kd_score(kd)
            gsc_boost = _gsc_boost(keyword, gsc_queries, gsc_positions)
            intent_score = 0.0 if intent_norm in _INFORMATIONAL_INTENTS else 1.0
            opportunity = (
                vol_score * _W_VOLUME
                + kd_score * _W_KD
                + relevance * _W_RELEVANCE
                + gsc_boost * _W_GSC
                + intent_score * _W_INTENT
            )

            scored.append({
                "keyword": keyword,
                "au_volume": au_vol,
                "us_volume": us_vol,
                "difficulty": kd if kd is not None else "",
                "intent": intent_raw or "Commercial",
                "opportunity_score": round(opportunity, 4),
                "score_breakdown": {
                    "volume": round(vol_score, 3),
                    "kd": round(kd_score, 3),
                    "relevance": round(relevance, 3),
                    "gsc": round(gsc_boost, 3),
                    "intent": round(intent_score, 3),
                },
                "source": str(row.get("source") or "SE Ranking research"),
            })

        # Sort by opportunity score descending, deduplicate within collection.
        scored.sort(key=lambda r: -r["opportunity_score"])
        seen: set[str] = set()
        deduped = []
        for row in scored:
            if row["keyword"] not in seen:
                seen.add(row["keyword"])
                deduped.append(row)

        scored_by_slug[slug] = deduped[:top_n]

    # Cross-collection deduplication: if a keyword appears in multiple slug
    # lists, keep it only in the one where it scored highest.
    _dedup_across_collections(scored_by_slug)

    # Flatten results and annotate with assigned_slug.
    for slug, rows in scored_by_slug.items():
        for row in rows:
            row["assigned_slug"] = slug

    total_in = sum(len(v) for v in by_slug_raw.values())
    total_out = sum(len(v) for v in scored_by_slug.values())
    coverage = sum(1 for v in scored_by_slug.values() if v)

    return {
        "by_slug": scored_by_slug,
        "summary": {
            "collections": len(collections),
            "collections_with_keywords": coverage,
            "raw_input_rows": total_in,
            "accepted_rows": total_out,
            "filtered_rows": len(filtered_out),
            "filters": {
                "min_volume": min_volume,
                "max_kd": max_kd,
                "top_n_per_collection": top_n,
            },
        },
        "filtered_out": filtered_out[:200],  # cap diagnostic list
    }


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def _volume_score(volume: int) -> float:
    if volume <= 0:
        return 0.0
    return min(1.0, math.log10(volume + 1) / math.log10(_VOLUME_CEIL + 1))


def _kd_score(kd: float | None) -> float:
    if kd is None:
        return 0.5  # unknown difficulty — neutral
    return max(0.0, 1.0 - (kd / 80.0))


def _relevance_score(keyword: str, collection: dict[str, Any]) -> float:
    """Token overlap between keyword and collection identity signals."""
    kw_tokens = _tokens(keyword)
    if not kw_tokens:
        return 0.0
    col_tokens = _tokens(
        str(collection.get("slug") or ""),
        str(collection.get("primary_keyword") or ""),
        str(collection.get("current_h1") or ""),
        str(collection.get("dominant_product_type") or ""),
        *[str(t) for t in (collection.get("product_types") or [])],
    )
    if not col_tokens:
        return 0.0
    overlap = kw_tokens & col_tokens
    # Jaccard similarity on keyword tokens.
    return len(overlap) / len(kw_tokens | col_tokens)


def _gsc_boost(keyword: str, gsc_queries: set[str], gsc_positions: dict[str, float]) -> float:
    """Boost if keyword matches a GSC query already getting impressions at poor position."""
    if keyword not in gsc_queries:
        return 0.0
    pos = gsc_positions.get(keyword, 0.0)
    if pos <= 0:
        return 0.0
    if pos > 20:
        return 0.8   # impressions but no real presence — strong opportunity
    if pos > 10:
        return 0.6   # page 2 — winnable
    if pos > 5:
        return 0.4   # lower page 1 — push up
    return 0.2       # already in top 5 — less opportunity signal


# ---------------------------------------------------------------------------
# Filtering helpers
# ---------------------------------------------------------------------------

def _is_brand_hit(keyword: str, denylist: frozenset[str]) -> bool:
    for brand in denylist:
        if re.search(r"\b" + re.escape(brand) + r"\b", keyword):
            return True
    return False


def _is_catalog_mismatch(keyword: str, catalog_types: set[str]) -> bool:
    for pattern, required_types in _CATALOG_EXCLUSIONS:
        if pattern.search(keyword):
            if not (catalog_types & required_types):
                return True
    return False


# ---------------------------------------------------------------------------
# Cross-collection deduplication
# ---------------------------------------------------------------------------

def _dedup_across_collections(scored_by_slug: dict[str, list[dict[str, Any]]]) -> None:
    """For each keyword appearing in multiple collections, keep it only in the
    collection where its opportunity_score is highest."""
    keyword_to_best: dict[str, tuple[float, str]] = {}  # keyword → (score, slug)
    for slug, rows in scored_by_slug.items():
        for row in rows:
            kw = row["keyword"]
            score = row["opportunity_score"]
            if kw not in keyword_to_best or score > keyword_to_best[kw][0]:
                keyword_to_best[kw] = (score, slug)

    for slug, rows in scored_by_slug.items():
        scored_by_slug[slug] = [
            row for row in rows
            if keyword_to_best[row["keyword"]][1] == slug
        ]


# ---------------------------------------------------------------------------
# Input normalisation
# ---------------------------------------------------------------------------

def _normalise_raw_input(
    raw: Any,
    collections: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Accept raw input in any of three shapes and return a slug-keyed dict."""
    if isinstance(raw, dict) and "by_slug" in raw:
        raw = raw["by_slug"]

    if isinstance(raw, dict):
        # Already slug-keyed — normalise each row list.
        return {
            str(slug): _normalise_rows(rows)
            for slug, rows in raw.items()
            if isinstance(rows, list)
        }

    if isinstance(raw, list):
        # Flat list — attempt to assign to collections by keyword similarity.
        return _assign_flat_list(raw, collections)

    return {}


def _normalise_rows(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if isinstance(row, str):
            out.append({"keyword": row})
        elif isinstance(row, dict):
            out.append(row)
    return out


def _assign_flat_list(
    rows: list[Any],
    collections: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Best-effort assignment when the raw export is a flat array."""
    by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if not isinstance(row, dict):
            continue
        keyword = _norm(row.get("keyword") or row.get("query") or "")
        if not keyword:
            continue
        # Assign to the collection with highest token overlap.
        kw_tokens = _tokens(keyword)
        best_slug, best_overlap = "", 0
        for c in collections:
            col_tokens = _tokens(str(c.get("slug") or ""), str(c.get("primary_keyword") or ""))
            overlap = len(kw_tokens & col_tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                best_slug = str(c.get("slug"))
        if best_slug:
            by_slug[best_slug].append(row)
        else:
            # Assign to first collection as fallback so no keyword is silently lost.
            if collections:
                by_slug[str(collections[0].get("slug"))].append(row)
    return dict(by_slug)


def _load_volume_map(raw: Any) -> dict[str, int]:
    from collection_seo_utils import parse_volume_map
    return parse_volume_map(raw)


def _load_gsc(raw: Any) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(raw, dict):
        return {}
    if "by_slug" in raw:
        raw = raw["by_slug"]
    return {str(k): v for k, v in raw.items() if isinstance(v, list)}


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

_STOP_TOKENS: frozenset[str] = frozenset({
    "the", "all", "shop", "womens", "women", "mens", "men",
    "collection", "collections", "online", "buy", "cheap",
    "best", "for", "and", "with", "your", "how",
})


def _stem(token: str) -> str:
    """Lightweight English stemmer for SEO token matching (no NLTK dependency)."""
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ves") and len(token) > 4:
        return token[:-3] + "f"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("es") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token


def _tokens(*values: str) -> set[str]:
    raw = {
        token for value in values
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if token not in _STOP_TOKENS and len(token) > 2
    }
    # Include stemmed forms so "dresses" matches "dress", etc.
    return raw | {_stem(t) for t in raw}


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _parse_kd(row: dict[str, Any]) -> float | None:
    for key in ("kd", "difficulty", "keyword_difficulty", "competition"):
        val = row.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                pass
    return None


def _rejection(keyword: str, slug: str, reason: str, detail: str = "") -> dict[str, Any]:
    return {"keyword": keyword, "slug": slug, "reason": reason, "detail": detail}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score and assign supplemental keywords from raw SE Ranking research.",
    )
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--raw-keywords-json", required=True, type=Path,
                        help="Raw SE Ranking related/similar export, keyed by collection slug.")
    parser.add_argument("--volume-json-au", type=Path)
    parser.add_argument("--volume-json-us", type=Path)
    parser.add_argument("--gsc-json", type=Path,
                        help="GSC opportunity JSON used for position-gap boosting.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-volume", type=int, default=_MIN_AU_VOLUME)
    parser.add_argument("--max-kd", type=int, default=_MAX_KD)
    parser.add_argument("--top-n", type=int, default=_TOP_N_PER_COLLECTION)
    parser.add_argument("--diagnostics", action="store_true",
                        help="Include filtered_out list in output for debugging.")
    args = parser.parse_args()

    result = research_supplemental_keywords(
        client_json=args.client_json,
        raw_keywords_json=args.raw_keywords_json,
        volume_json_au=args.volume_json_au,
        volume_json_us=args.volume_json_us,
        gsc_json=args.gsc_json,
        min_volume=args.min_volume,
        max_kd=args.max_kd,
        top_n=args.top_n,
    )
    if not args.diagnostics:
        result.pop("filtered_out", None)

    args.output.write_text(json.dumps(result, indent=2))

    s = result["summary"]
    print(
        f"Wrote supplemental keywords to {args.output}\n"
        f"  Collections: {s['collections_with_keywords']} / {s['collections']} have keywords\n"
        f"  Accepted: {s['accepted_rows']} keywords  |  Filtered: {s['filtered_rows']}\n"
        f"  Filters applied: min_volume={s['filters']['min_volume']}, "
        f"max_kd={s['filters']['max_kd']}, top_n={s['filters']['top_n_per_collection']}"
    )


if __name__ == "__main__":
    main()
