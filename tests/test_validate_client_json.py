"""Tests for the client JSON validator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import validate_client_json as vcj  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _minimal_client() -> dict:
    """A fully valid minimal client JSON."""
    return {
        "client": "Test Brand",
        "brand_display_name": "TEST",
        "brand_voice": "Clean and direct. Copy leads with product detail.",
        "tone_direction": "Lead with fit and fabric. Avoid filler.",
        "domain": "testbrand.com",
        "market_scope": "AU",
        "usp": "Free shipping over $80",
        "se_ranking": {"project_id": 12345, "engines": {"AU": 67890}},
        "drive": {
            "client_folder_id": "abc123",
            "folders": {"05_content": "def456"},
        },
        "monday": {"board_id": 9999, "groups": {"current_month": "group_abc"}},
        "collections": [
            {
                "slug": "dresses",
                "url": "https://testbrand.com/collections/dresses",
                "class": "pure_category",
                "dominant_product_type": "DRESSES",
                "primary_keyword": "womens dresses",
                "au_volume": 10000,
                "current_h1": "Dresses",
                "last_scraped": "2026-05-10",
            }
        ],
    }


def _write(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "client.json"
    p.write_text(json.dumps(data))
    return p


# ---------------------------------------------------------------------------
# Top-level field tests
# ---------------------------------------------------------------------------

def test_valid_client_passes(tmp_path: Path) -> None:
    result = vcj.validate_client_json(_write(tmp_path, _minimal_client()))
    assert result["ok"] is True
    assert result["summary"]["blocking_count"] == 0


def test_missing_brand_display_name_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    del client["brand_display_name"]
    result = vcj.validate_client_json(_write(tmp_path, client))
    codes = [i["code"] for i in result["blocking"]]
    assert "missing_required_field" in codes
    assert any(i["field"] == "brand_display_name" for i in result["blocking"])


def test_missing_brand_voice_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    del client["brand_voice"]
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i.get("field") == "brand_voice" for i in result["blocking"])


def test_missing_tone_direction_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    del client["tone_direction"]
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i.get("field") == "tone_direction" for i in result["blocking"])


def test_unfilled_template_placeholder_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    client["brand_voice"] = "REQUIRED — One paragraph describing the brand register."
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert result["ok"] is False
    assert any(i.get("field") == "brand_voice" for i in result["blocking"])


def test_invalid_market_scope_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    client["market_scope"] = "GLOBAL"
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "invalid_market_scope" for i in result["blocking"])


def test_missing_brand_denylist_warns_not_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert result["ok"] is True
    assert any(i.get("field") == "brand_denylist" for i in result["warning"])


# ---------------------------------------------------------------------------
# SE Ranking tests
# ---------------------------------------------------------------------------

def test_missing_se_ranking_project_id_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    client["se_ranking"] = {"engines": {"AU": 67890}}
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "missing_se_ranking_project_id" for i in result["blocking"])


def test_missing_au_engine_for_au_scope_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    client["se_ranking"]["engines"] = {}
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "missing_se_ranking_engine_au" for i in result["blocking"])


def test_us_engine_required_for_us_scope(tmp_path: Path) -> None:
    client = _minimal_client()
    client["market_scope"] = "AU+US"
    client["collections"][0]["us_volume"] = 50000
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "missing_se_ranking_engine_us" for i in result["blocking"])


# ---------------------------------------------------------------------------
# Drive / Monday tests
# ---------------------------------------------------------------------------

def test_missing_drive_folder_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    del client["drive"]["client_folder_id"]
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "missing_drive_client_folder" for i in result["blocking"])


def test_missing_content_folder_warns(tmp_path: Path) -> None:
    client = _minimal_client()
    client["drive"]["folders"] = {}
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert result["ok"] is True
    assert any(i["code"] == "missing_content_folder" for i in result["warning"])


def test_missing_monday_board_id_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    del client["monday"]["board_id"]
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "missing_monday_board_id" for i in result["blocking"])


# ---------------------------------------------------------------------------
# Collection tests
# ---------------------------------------------------------------------------

def test_no_collections_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    client["collections"] = []
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "no_collections" for i in result["blocking"])


def test_missing_dominant_product_type_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    del client["collections"][0]["dominant_product_type"]
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(
        i["code"] == "missing_collection_field" and i.get("field") == "dominant_product_type"
        for i in result["blocking"]
    )


def test_h1_primary_keyword_mismatch_warns(tmp_path: Path) -> None:
    client = _minimal_client()
    client["collections"][0]["current_h1"] = "Minis"
    client["collections"][0]["primary_keyword"] = "mini dress"
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert result["ok"] is True
    assert any(i["code"] == "h1_primary_keyword_mismatch" for i in result["warning"])


def test_h1_matching_primary_keyword_no_warning(tmp_path: Path) -> None:
    client = _minimal_client()
    client["collections"][0]["current_h1"] = "Dresses"
    client["collections"][0]["primary_keyword"] = "womens dresses"
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert not any(i["code"] == "h1_primary_keyword_mismatch" for i in result["warning"])


def test_duplicate_slug_blocks(tmp_path: Path) -> None:
    client = _minimal_client()
    client["collections"].append(client["collections"][0].copy())
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "duplicate_slug" for i in result["blocking"])


def test_dominant_product_type_mismatch_warns(tmp_path: Path) -> None:
    client = _minimal_client()
    client["collections"][0]["dominant_product_type"] = "TOP"
    client["collections"][0]["primary_keyword"] = "mini dress"
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "likely_dominant_product_type_mismatch" for i in result["warning"])


def test_us_volume_required_for_au_us_scope(tmp_path: Path) -> None:
    client = _minimal_client()
    client["market_scope"] = "AU+US"
    client["se_ranking"]["engines"]["US"] = 11111
    # us_volume not set on collection
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "missing_collection_volume" and "us_volume" in i.get("message", "") for i in result["blocking"])


def test_invalid_collection_class_warns(tmp_path: Path) -> None:
    client = _minimal_client()
    client["collections"][0]["class"] = "random_class"
    result = vcj.validate_client_json(_write(tmp_path, client))
    assert any(i["code"] == "invalid_collection_class" for i in result["warning"])
