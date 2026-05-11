"""Tests for the supplemental keyword intelligence/scoring layer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import research_supplemental_keywords as researcher  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _client() -> dict:
    return {
        "client": "Test Store",
        "domain": "example.test",
        "market_scope": "AU",
        "collections": [
            {
                "slug": "dresses",
                "url": "https://example.test/collections/dresses",
                "class": "pure_category",
                "dominant_product_type": "DRESSES",
                "primary_keyword": "womens dresses",
                "au_volume": 10000,
                "us_volume": 20000,
                "current_h1": "Dresses",
            },
            {
                "slug": "maxis",
                "url": "https://example.test/collections/maxis",
                "class": "pure_category",
                "dominant_product_type": "DRESSES",
                "primary_keyword": "maxi dress",
                "au_volume": 8000,
                "us_volume": 16000,
                "current_h1": "Maxis",
            },
            {
                "slug": "swim",
                "url": "https://example.test/collections/swim",
                "class": "pure_category",
                "dominant_product_type": "SWIM",
                "primary_keyword": "swimwear",
                "au_volume": 12000,
                "us_volume": 40000,
                "current_h1": "SWIM",
            },
        ],
    }


def _write_client(tmp_path: Path, client: dict | None = None) -> Path:
    p = tmp_path / "client.json"
    p.write_text(json.dumps(client or _client()))
    return p


def _write_raw(tmp_path: Path, raw: dict) -> Path:
    p = tmp_path / "raw.json"
    p.write_text(json.dumps(raw))
    return p


# ---------------------------------------------------------------------------
# Core scoring tests
# ---------------------------------------------------------------------------

def test_relevant_high_volume_keyword_passes_and_scores_well(tmp_path: Path) -> None:
    raw = {
        "dresses": [
            {"keyword": "floral dress", "volume": 5000, "kd": 30, "intent": "Commercial"},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    slugs = result["by_slug"]
    assert "dresses" in slugs
    keywords = [r["keyword"] for r in slugs["dresses"]]
    assert "floral dress" in keywords
    row = next(r for r in slugs["dresses"] if r["keyword"] == "floral dress")
    assert row["opportunity_score"] > 0.5
    assert row["au_volume"] == 5000
    assert row["difficulty"] == 30


def test_brand_contaminated_keyword_is_rejected(tmp_path: Path) -> None:
    raw = {
        "swim": [
            {"keyword": "kmart swimwear", "volume": 18000, "kd": 20},
            {"keyword": "monday swimwear", "volume": 12000, "kd": 25},
            {"keyword": "speedo swimwear", "volume": 8000, "kd": 15},
            {"keyword": "one piece swimwear", "volume": 9000, "kd": 35},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    accepted = {r["keyword"] for r in result["by_slug"].get("swim", [])}
    assert "kmart swimwear" not in accepted
    assert "monday swimwear" not in accepted
    assert "speedo swimwear" not in accepted
    assert "one piece swimwear" in accepted

    rejected_reasons = {r["keyword"]: r["reason"] for r in result["filtered_out"]}
    assert rejected_reasons.get("kmart swimwear") == "brand_contamination"


def test_catalog_mismatch_keyword_is_rejected(tmp_path: Path) -> None:
    raw = {
        "swim": [
            {"keyword": "kids swimwear", "volume": 8000, "kd": 25},
            {"keyword": "girls swimwear", "volume": 9000, "kd": 20},
            {"keyword": "period swimwear", "volume": 6000, "kd": 15},
            {"keyword": "womens swimwear", "volume": 7000, "kd": 30},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    accepted = {r["keyword"] for r in result["by_slug"].get("swim", [])}
    assert "kids swimwear" not in accepted
    assert "girls swimwear" not in accepted
    assert "period swimwear" not in accepted
    assert "womens swimwear" in accepted


def test_low_volume_keyword_is_rejected(tmp_path: Path) -> None:
    raw = {
        "dresses": [
            {"keyword": "cocktail dress au", "volume": 50, "kd": 10},
            {"keyword": "cocktail dress", "volume": 2000, "kd": 40},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    accepted = {r["keyword"] for r in result["by_slug"].get("dresses", [])}
    assert "cocktail dress au" not in accepted
    assert "cocktail dress" in accepted


def test_too_competitive_keyword_is_rejected(tmp_path: Path) -> None:
    raw = {
        "dresses": [
            {"keyword": "dresses online", "volume": 50000, "kd": 85},  # above max_kd
            {"keyword": "casual dress", "volume": 6000, "kd": 40},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    accepted = {r["keyword"] for r in result["by_slug"].get("dresses", [])}
    assert "dresses online" not in accepted
    assert "casual dress" in accepted


def test_primary_keyword_of_another_collection_is_rejected(tmp_path: Path) -> None:
    raw = {
        "dresses": [
            {"keyword": "maxi dress", "volume": 8000, "kd": 30},  # primary of maxis
            {"keyword": "wrap dress", "volume": 3500, "kd": 35},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    accepted = {r["keyword"] for r in result["by_slug"].get("dresses", [])}
    assert "maxi dress" not in accepted
    assert "wrap dress" in accepted


def test_cross_collection_dedup_assigns_keyword_to_best_fit(tmp_path: Path) -> None:
    """A keyword appearing in two slug lists should end up only in the better fit."""
    raw = {
        "dresses": [
            {"keyword": "floral maxi dress", "volume": 4000, "kd": 30},
        ],
        "maxis": [
            {"keyword": "floral maxi dress", "volume": 4000, "kd": 30},
        ],
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    in_dresses = any(r["keyword"] == "floral maxi dress" for r in result["by_slug"].get("dresses", []))
    in_maxis = any(r["keyword"] == "floral maxi dress" for r in result["by_slug"].get("maxis", []))
    # Must appear in exactly one collection.
    assert in_dresses != in_maxis, "Keyword should be deduplicated to exactly one collection"


def test_gsc_boost_applied_for_position_gap_queries(tmp_path: Path) -> None:
    """A keyword matching a GSC query at position > 10 should score higher."""
    gsc = {
        "by_slug": {
            "dresses": [
                {"query": "evening dress au", "clicks": 5, "impressions": 800, "position": 18},
            ]
        }
    }
    gsc_path = tmp_path / "gsc.json"
    gsc_path.write_text(json.dumps(gsc))

    raw_with_gsc = {
        "dresses": [
            {"keyword": "evening dress au", "volume": 1500, "kd": 25},
            {"keyword": "black cocktail dress", "volume": 1500, "kd": 25},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw_with_gsc),
        gsc_json=gsc_path,
    )
    rows = {r["keyword"]: r for r in result["by_slug"].get("dresses", [])}
    assert "evening dress au" in rows
    assert rows["evening dress au"]["score_breakdown"]["gsc"] > 0.5


def test_summary_counts_are_correct(tmp_path: Path) -> None:
    raw = {
        "swim": [
            {"keyword": "kmart swimwear", "volume": 18000, "kd": 20},
            {"keyword": "one piece swimwear", "volume": 9000, "kd": 35},
            {"keyword": "swimwear australia", "volume": 4000, "kd": 40},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    s = result["summary"]
    assert s["raw_input_rows"] == 3
    assert s["accepted_rows"] == 2   # kmart rejected
    assert s["filtered_rows"] == 1


def test_flat_list_input_assigns_to_best_matching_collection(tmp_path: Path) -> None:
    raw = [
        {"keyword": "midi dress australia", "volume": 3000, "kd": 30},
        {"keyword": "swimwear australia", "volume": 5000, "kd": 40},
    ]
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    all_kw = {r["keyword"] for rows in result["by_slug"].values() for r in rows}
    # At least one should have been assigned and accepted.
    assert len(all_kw) >= 1


def test_client_brand_denylist_extension(tmp_path: Path) -> None:
    client = _client()
    client["brand_denylist"] = ["rivalstore"]
    raw = {
        "dresses": [
            {"keyword": "rivalstore dresses", "volume": 5000, "kd": 20},
            {"keyword": "evening dress", "volume": 3000, "kd": 35},
        ]
    }
    result = researcher.research_supplemental_keywords(
        client_json=_write_client(tmp_path, client),
        raw_keywords_json=_write_raw(tmp_path, raw),
    )
    accepted = {r["keyword"] for r in result["by_slug"].get("dresses", [])}
    assert "rivalstore dresses" not in accepted
    assert "evening dress" in accepted
