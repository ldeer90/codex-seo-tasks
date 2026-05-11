from __future__ import annotations

import csv
import inspect
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_metadata_suggestions as metadata  # noqa: E402
import validate_collection_seo_state as validator  # noqa: E402
from seo_automation_mcp.google_clients import GoogleWorkspaceClient  # noqa: E402


def test_structured_serp_titles_are_slug_scoped() -> None:
    serp = {
        "maxis": {
            "serp_results": [
                {"url": "https://competitor.test/maxi-dresses", "title": "Maxi Dresses | Brand"},
                {"url": "https://competitor.test/other", "title": "Long Dresses | Brand"},
            ]
        },
        "minis": {"serp_results": [{"title": "Mini Dresses | Brand"}]},
    }

    assert metadata.pick_top_competitor_titles(serp, "maxis") == [
        "Maxi Dresses | Brand",
        "Long Dresses | Brand",
    ]


def test_legacy_flat_serp_still_works() -> None:
    serp = [
        {"url": "https://competitor.test/collections/maxis", "title": "Maxis | Brand"},
        {"url": "https://competitor.test/collections/minis", "title": "Minis | Brand"},
    ]

    assert metadata.pick_top_competitor_titles(serp, "maxis") == ["Maxis | Brand"]


def test_generator_falls_back_to_sidecar_current_page_fields(tmp_path: Path) -> None:
    client_json = tmp_path / "client.json"
    serp_json = tmp_path / "serp.json"
    pages_json = tmp_path / "pages.json"
    output = tmp_path / "out.csv"

    client_json.write_text(json.dumps(_client(collection_count=1)))
    serp_json.write_text(json.dumps({"slug-0": {"serp_results": [{"title": "Keyword 0 | Brand"}]}}))
    pages_json.write_text("{}")

    metadata.run(client_json, serp_json, pages_json, output)
    rows = list(csv.DictReader(output.open()))

    assert rows[0]["Current Title"] == "Keyword 0 | Test Brand"
    assert rows[0]["Current H1"] == "Keyword 0"


def test_generator_refuses_incomplete_outputs(tmp_path: Path) -> None:
    client = _client(collection_count=3)
    for collection in client["collections"]:
        collection.pop("au_volume", None)
        collection.pop("current_title", None)
        collection.pop("current_h1", None)

    client_json = tmp_path / "client.json"
    serp_json = tmp_path / "serp.json"
    pages_json = tmp_path / "pages.json"
    output = tmp_path / "out.csv"
    client_json.write_text(json.dumps(client))
    serp_json.write_text("{}")
    pages_json.write_text("{}")

    with pytest.raises(ValueError, match="Refusing to write incomplete"):
        metadata.run(client_json, serp_json, pages_json, output)


def test_title_drops_descriptor_to_stay_under_limit() -> None:
    title = metadata.build_title(
        "extra long formal evening dress",
        "Test Brand",
        "A Very Long Descriptor That Will Not Fit",
        max_len=60,
    )

    assert title == "Extra Long Formal Evening Dresses | Test Brand"
    assert len(title) <= 60


def test_metadata_descriptor_prefers_sidecar_then_serp_patterns() -> None:
    collection = {
        "slug": "coffee-machines",
        "primary_keyword": "coffee machines",
        "metadata_descriptor": "Manual & Automatic",
    }
    assert metadata.descriptor_for_collection(collection) == "Manual & Automatic"

    collection.pop("metadata_descriptor")
    assert metadata.descriptor_for_collection(
        collection,
        serp_patterns={"recommended_descriptor": "Espresso At Home"},
    ) == "Espresso At Home"


def test_metadata_row_includes_serp_considerations() -> None:
    row = metadata.render_row(
        slug="coffee-machines",
        url="https://example.test/collections/coffee-machines",
        primary_keyword="coffee machines",
        brand="Test Brand",
        au_volume=1000,
        us_volume=None,
        current_title="Coffee Machines",
        current_h1="Coffee Machines",
        descriptor="Espresso At Home",
        usp="Free returns",
        competitor_titles=["Coffee Machines | Competitor"],
        serp_patterns={"title_formula": "Keyword | Modifier | Brand", "copy_angles": ["home espresso"]},
    )
    assert row["Suggested Title"] == "Coffee Machines | Espresso At Home | Test Brand"
    assert "home espresso" in row["SERP Considerations"]


def test_validator_passes_synced_state(tmp_path: Path) -> None:
    client_json = tmp_path / "client.json"
    keywords_json = tmp_path / "keywords.json"
    pages_json = tmp_path / "pages.json"
    serp_json = tmp_path / "serp.json"

    client_json.write_text(json.dumps(_client(collection_count=1)))
    keywords_json.write_text(json.dumps({
        "data": [
            {
                "id": "1",
                "name": "keyword 0",
                "link": "https://example.test/collections/slug-0",
                "site_engine_ids": [101, 202],
            }
        ]
    }))
    pages_json.write_text(json.dumps({"slug-0": {"title": "Keyword 0 | Test Brand", "h1": "Keyword 0"}}))
    serp_json.write_text(json.dumps({
        "slug-0": {
            "serp_results": [{"title": "Keyword 0 | Competitor"}],
        }
    }))

    result = validator.validate(
        client_json=client_json,
        seranking_keywords_json=keywords_json,
        pages_json=pages_json,
        serp_json=serp_json,
    )

    assert result["ok"] is True
    assert result["summary"]["live_pair_count"] == 2


def test_validator_blocks_broken_sidecar_state(tmp_path: Path) -> None:
    client = _client(collection_count=1)
    client["collections"][0].pop("au_volume")
    client["collections"][0].pop("current_h1")

    client_json = tmp_path / "client.json"
    keywords_json = tmp_path / "keywords.json"
    client_json.write_text(json.dumps(client))
    keywords_json.write_text(json.dumps({"data": []}))

    result = validator.validate(client_json=client_json, seranking_keywords_json=keywords_json)
    codes = {issue["code"] for issue in result["blocking"]}

    assert result["ok"] is False
    assert "missing_live_keywords" in codes
    assert "missing_au_volume" in codes
    assert "missing_current_page_state" in codes


def test_validator_flags_malformed_serp_and_missing_engine(tmp_path: Path) -> None:
    client_json = tmp_path / "client.json"
    keywords_json = tmp_path / "keywords.json"
    serp_json = tmp_path / "serp.json"

    client_json.write_text(json.dumps(_client(collection_count=1)))
    keywords_json.write_text(json.dumps({
        "data": [
            {
                "id": "1",
                "name": "keyword 0",
                "link": "https://example.test/collections/slug-0",
                "site_engine_ids": [101],
            }
        ]
    }))
    serp_json.write_text(json.dumps({"slug-0": {"bad": []}}))

    result = validator.validate(
        client_json=client_json,
        seranking_keywords_json=keywords_json,
        serp_json=serp_json,
    )
    codes = {issue["code"] for issue in result["blocking"]}

    assert "missing_engine_pair" in codes
    assert "malformed_structured_serp" in codes


def test_validator_resolves_repo_relative_deliverable_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    client_dir = repo / "docs" / "agent" / "clients"
    deliverable = repo / "docs" / "serp.json"
    client_dir.mkdir(parents=True)
    deliverable.parent.mkdir(parents=True, exist_ok=True)
    deliverable.write_text("{}")

    client = _client(collection_count=1)
    client["deliverables"]["competitor_serp_json"] = {"path": "docs/serp.json"}
    client_json = client_dir / "client.json"
    keywords_json = tmp_path / "keywords.json"
    pages_json = tmp_path / "pages.json"
    serp_json = tmp_path / "serp.json"
    client_json.write_text(json.dumps(client))
    keywords_json.write_text(json.dumps({
        "data": [
            {
                "id": "1",
                "name": "keyword 0",
                "link": "https://example.test/collections/slug-0",
                "site_engine_ids": [101, 202],
            }
        ]
    }))
    pages_json.write_text(json.dumps({"slug-0": {"title": "Keyword 0 | Test Brand", "h1": "Keyword 0"}}))
    serp_json.write_text(json.dumps({"slug-0": {"serp_results": [{"title": "Keyword 0"}]}}))

    result = validator.validate(
        client_json=client_json,
        seranking_keywords_json=keywords_json,
        pages_json=pages_json,
        serp_json=serp_json,
    )

    warning_codes = {issue["code"] for issue in result["warning"]}
    assert "missing_deliverable_path" not in warning_codes


def test_google_workspace_doc_methods_support_folder_and_overwrite() -> None:
    create_doc_sig = inspect.signature(GoogleWorkspaceClient.create_doc)
    overwrite_sig = inspect.signature(GoogleWorkspaceClient.overwrite_doc_text)
    overwrite_sheet_sig = inspect.signature(GoogleWorkspaceClient.overwrite_sheet_values)

    assert "folder_id" in create_doc_sig.parameters
    assert list(overwrite_sig.parameters)[:3] == ["self", "document_id", "text"]
    assert list(overwrite_sheet_sig.parameters)[:3] == ["self", "spreadsheet_id", "values"]
    assert "sheet_name" in overwrite_sheet_sig.parameters


def test_google_workspace_has_dynamic_sheet_id_helper() -> None:
    assert hasattr(GoogleWorkspaceClient, "_first_grid_sheet_id")


def _client(collection_count: int) -> dict:
    collections = []
    for i in range(collection_count):
        collections.append({
            "slug": f"slug-{i}",
            "url": f"https://example.test/collections/slug-{i}",
            "class": "pure_category",
            "primary_keyword": f"keyword {i}",
            "au_volume": 100 + i,
            "us_volume": 1000 + i,
            "current_title": f"Keyword {i} | Test Brand",
            "current_h1": f"Keyword {i}",
            "competitor_top3_urls": ["https://competitor.test/slug"],
        })
    return {
        "client": "Test Brand",
        "domain": "example.test",
        "market_scope": "AU+US",
        "se_ranking": {
            "project_id": 1,
            "engines": {"AU": 101, "US": 202},
        },
        "deliverables": {
            "metadata_suggestions_sheet": {"coverage": f"{collection_count} of {collection_count} SEO-priority collections"}
        },
        "collections": collections,
        "discovery_summary": {"total_after_filter": collection_count},
    }
