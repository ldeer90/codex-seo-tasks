from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import evaluate_collection_keyword_candidates as evaluator  # noqa: E402


def test_candidate_evaluator_accepts_rankable_collection_fit(tmp_path: Path) -> None:
    client = _client()
    client_path = tmp_path / "client.json"
    candidates_path = tmp_path / "candidates.json"
    gsc_path = tmp_path / "gsc.json"
    serp_path = tmp_path / "serp.json"
    client_path.write_text(json.dumps(client))
    candidates_path.write_text(json.dumps({
        "by_slug": {
            "dresses": [
                {
                    "keyword": "floral dress",
                    "volume": 5000,
                    "difficulty": 30,
                    "intent": "Commercial",
                    "source": "SE Ranking related",
                },
                {"keyword": "kids dress", "volume": 9000, "difficulty": 20},
                {"keyword": "maxi dress", "volume": 8000, "difficulty": 25},
            ]
        }
    }))
    gsc_path.write_text(json.dumps({
        "by_slug": {
            "dresses": [{"query": "floral dress", "impressions": 500, "position": 16}]
        }
    }))
    serp_path.write_text(json.dumps({
        "dresses": {
            "serp_results": [
                {"title": "Floral Dress Online | Competitor", "h1": "Floral Dresses"}
            ]
        }
    }))

    result = evaluator.evaluate_candidates(
        client_json=client_path,
        candidates_json=candidates_path,
        gsc_json=gsc_path,
        serp_json=serp_path,
        min_score=0.4,
    )

    accepted = {row["keyword"] for row in result["by_slug"]["dresses"]}
    rejected = {row["keyword"]: row["reason"] for row in result["rejected"]}
    assert "floral dress" in accepted
    assert rejected["kids dress"] == "catalog_mismatch"
    assert rejected["maxi dress"] == "primary_keyword_of_maxis"
    assert result["by_slug"]["dresses"][0]["rationale"]


def _client() -> dict:
    return {
        "client": "Test Store",
        "market_scope": "AU",
        "collections": [
            {
                "slug": "dresses",
                "url": "https://example.test/collections/dresses",
                "class": "pure_category",
                "dominant_product_type": "DRESSES",
                "primary_keyword": "womens dresses",
                "current_h1": "Dresses",
                "sample_product_titles": ["Floral Dress", "Black Dress"],
            },
            {
                "slug": "maxis",
                "url": "https://example.test/collections/maxis",
                "class": "pure_category",
                "dominant_product_type": "DRESSES",
                "primary_keyword": "maxi dress",
                "current_h1": "Maxi Dresses",
                "sample_product_titles": ["Maxi Dress"],
            },
        ],
    }
