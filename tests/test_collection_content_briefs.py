from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_collection_content_brief_inputs as builder  # noqa: E402
import build_blog_internal_link_candidates as blog_links  # noqa: E402
import render_collection_content_brief_doc as renderer  # noqa: E402
import validate_blog_html_copy as blog_html_validator  # noqa: E402
import validate_collection_html_copy as html_validator  # noqa: E402
import validate_collection_content_briefs as validator  # noqa: E402


def test_internal_link_scoring_returns_top_five_without_self_links() -> None:
    collections = _collections(7)

    links = builder.select_internal_links(collections[0], collections, limit=5)

    assert len(links) == 5
    assert all(link["target_slug"] != "dresses" for link in links)
    assert all(link["anchor_text"] for link in links)
    assert all(link["target_url"] for link in links)


def test_build_briefs_creates_writer_ready_payload(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)

    payload = builder.build_briefs(
        client_json=paths["client"],
        seranking_keywords_json=paths["keywords"],
        volume_json_au=paths["volumes_au"],
        volume_json_us=paths["volumes_us"],
        pages_json=paths["pages"],
        serp_json=paths["serp"],
        product_json=paths["products"],
        supplemental_keywords_json=paths["supplemental"],
    )

    first = payload["briefs"][0]
    assert payload["summary"]["collections"] == 6
    assert first["keywords"]["primary"]["au_volume"] > 0
    assert len(first["internal_links"]) == 5
    assert first["writer_prompt"]
    assert first["product_context"]["sample_product_titles"]


def test_build_briefs_refuses_missing_product_context(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    products = json.loads(paths["products"].read_text())
    products["dresses"] = {"products": []}
    paths["products"].write_text(json.dumps(products))
    client = json.loads(paths["client"].read_text())
    client["collections"][0]["sample_product_titles"] = []
    paths["client"].write_text(json.dumps(client))

    with pytest.raises(ValueError, match="missing_product_context"):
        builder.build_briefs(
            client_json=paths["client"],
            seranking_keywords_json=paths["keywords"],
            volume_json_au=paths["volumes_au"],
            volume_json_us=paths["volumes_us"],
            pages_json=paths["pages"],
            serp_json=paths["serp"],
            product_json=paths["products"],
            supplemental_keywords_json=paths["supplemental"],
        )


def test_validator_blocks_incomplete_brief_payload(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    payload = builder.build_briefs(
        client_json=paths["client"],
        seranking_keywords_json=paths["keywords"],
        volume_json_au=paths["volumes_au"],
        volume_json_us=paths["volumes_us"],
        pages_json=paths["pages"],
        serp_json=paths["serp"],
        product_json=paths["products"],
        supplemental_keywords_json=paths["supplemental"],
    )
    payload["briefs"][0]["internal_links"] = []
    briefs_path = tmp_path / "briefs.json"
    briefs_path.write_text(json.dumps(payload))

    result = validator.validate(client_json=paths["client"], briefs_json=briefs_path)
    codes = {issue["code"] for issue in result["blocking"]}

    assert result["ok"] is False
    assert "insufficient_internal_links" in codes


def test_renderer_includes_required_sections(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    payload = builder.build_briefs(
        client_json=paths["client"],
        seranking_keywords_json=paths["keywords"],
        volume_json_au=paths["volumes_au"],
        volume_json_us=paths["volumes_us"],
        pages_json=paths["pages"],
        serp_json=paths["serp"],
        product_json=paths["products"],
        supplemental_keywords_json=paths["supplemental"],
    )

    doc = renderer.render_brief_doc(payload["briefs"][0], client=payload["client"])

    assert "## Overview" in doc
    assert "## Keywords To Work Into The Page" in doc
    assert "## Internal Links" in doc
    assert "## Recommended Heading Hierarchy" in doc
    assert "## SEO Review" in doc
    assert "## Example Copy" in doc
    assert "### Page Title" in doc
    assert "### Meta Description" in doc


def test_html_copy_validator_blocks_unsupported_claims_and_bad_structure(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    payload = builder.build_briefs(
        client_json=paths["client"],
        seranking_keywords_json=paths["keywords"],
        volume_json_au=paths["volumes_au"],
        volume_json_us=paths["volumes_us"],
        pages_json=paths["pages"],
        serp_json=paths["serp"],
        product_json=paths["products"],
        supplemental_keywords_json=paths["supplemental"],
    )
    briefs_path = tmp_path / "briefs.json"
    briefs_path.write_text(json.dumps(payload))
    html_path = tmp_path / "copy.html"
    html_path.write_text(
        "<h2>Shop Womens Dresses</h2><h3>Fit</h3>"
        "<p>womens dresses made in Australia with free shipping.</p>"
    )

    result = html_validator.validate_html(briefs_json=briefs_path, slug="dresses", html=html_path)
    codes = {issue["code"] for issue in result["blocking"]}

    assert "invalid_h3_count" in codes
    assert "unsupported_claim" in codes


def test_html_copy_validator_passes_clean_collection_html(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    payload = builder.build_briefs(
        client_json=paths["client"],
        seranking_keywords_json=paths["keywords"],
        volume_json_au=paths["volumes_au"],
        volume_json_us=paths["volumes_us"],
        pages_json=paths["pages"],
        serp_json=paths["serp"],
        product_json=paths["products"],
        supplemental_keywords_json=paths["supplemental"],
    )
    briefs_path = tmp_path / "briefs.json"
    briefs_path.write_text(json.dumps(payload))
    target_url = payload["briefs"][0]["internal_links"][0]["target_url"]
    html_path = tmp_path / "copy.html"
    html_path.write_text(
        "<h2>Womens Dresses For Easy Styling</h2>"
        "<p>womens dresses at Test Store are organised for shoppers comparing the visible collection range. "
        "Use the page to compare fits, lengths, and styling directions before choosing a dress.</p>"
        "<h3>Choose The Shape That Fits The Plan</h3>"
        f"<p>Browse pieces with a clear occasion in mind, then compare related "
        f"<a href=\"{target_url}\">dress edits</a> when another length or silhouette would suit better.</p>"
        "<h3>Keep The Copy Specific</h3>"
        "<p>The final paragraph stays useful for shoppers by describing category choices without adding shipping, "
        "origin, sustainability, stock, or product claims that are not in the approved brief.</p>"
    )

    result = html_validator.validate_html(briefs_json=briefs_path, slug="dresses", html=html_path)

    assert result["ok"] is True


def test_blog_html_validator_blocks_missing_structure_and_unapproved_claims(tmp_path: Path) -> None:
    brief_path = tmp_path / "blog-brief.json"
    brief_path.write_text(json.dumps({
        "briefs": [{
            "slug": "dress-guide",
            "title": "Dress Guide",
            "keywords": {"primary": {"keyword": "dress guide"}},
            "internal_links": [{"target_url": "https://example.test/collections/dresses"}],
            "banned_phrases": ["look no further"],
        }]
    }))
    html_path = tmp_path / "blog.html"
    html_path.write_text(
        "<h2>Dress Guide</h2><p>This dress guide includes clinically proven tips and "
        "<a href=\"https://other.test/source\">an unapproved link</a>.</p>"
    )

    result = blog_html_validator.validate_blog_html(brief_json=brief_path, slug="dress-guide", html=html_path)
    codes = {issue["code"] for issue in result["blocking"]}

    assert "missing_brief_defined_html_policy" in codes
    assert "missing_brief_defined_structure" in codes
    assert "unsupported_claim" in codes
    assert "unapproved_link" in codes


def test_blog_html_validator_passes_brief_defined_html_with_lists(tmp_path: Path) -> None:
    brief_path = tmp_path / "blog-brief.json"
    brief_path.write_text(json.dumps({
        "briefs": [{
            "slug": "dress-guide",
            "title": "Dress Guide",
            "keywords": {"primary": {"keyword": "dress guide"}},
            "html_policy": {
                "allowed_tags": ["h2", "h3", "p", "a", "ul", "li", "strong"],
                "required_headings": ["Dress Guide", "How To Compare Dress Styles"],
            },
            "internal_links": [{"target_url": "https://example.test/collections/dresses"}],
            "approved_external_links": ["https://example.test/source"],
            "source_requirements": {"required": True},
            "content_requirements": {"min_words": 20, "max_words": 220},
            "banned_phrases": ["look no further"],
        }]
    }))
    html_path = tmp_path / "blog.html"
    html_path.write_text(
        "<h2>Dress Guide</h2>"
        "<p>This dress guide helps shoppers compare styles without relying on unsupported promises.</p>"
        "<h3>How To Compare Dress Styles</h3>"
        "<p>Start with the occasion, then compare length, neckline, and styling needs.</p>"
        "<ul><li><strong>Fit:</strong> choose the outline that suits the plan.</li>"
        "<li><a href=\"https://example.test/collections/dresses\">Browse dresses</a> for the current range.</li>"
        "<li><a href=\"https://example.test/source\">Read the approved source</a>.</li></ul>"
    )

    result = blog_html_validator.validate_blog_html(brief_json=brief_path, slug="dress-guide", html=html_path)

    assert result["ok"] is True


def test_blog_internal_link_candidates_prioritise_relevant_collections_and_blogs(tmp_path: Path) -> None:
    brief_path = tmp_path / "blog-brief.json"
    brief_path.write_text(json.dumps({
        "briefs": [{
            "slug": "birthday-gift-ideas-milestone-birthdays",
            "title": "Birthday Gift Ideas for Milestone Birthdays",
            "keywords": {
                "primary": {"keyword": "birthday gift ideas"},
                "secondary": [
                    {"keyword": "21st birthday gifts"},
                    {"keyword": "50th birthday gifts"},
                    {"keyword": "birthday hampers"},
                ],
            },
            "html_policy": {
                "allowed_tags": ["h2", "h3", "p", "a"],
                "required_headings": ["Birthday Gift Ideas for Milestone Birthdays"],
            },
        }]
    }))
    collections_path = tmp_path / "collections.json"
    collections_path.write_text(json.dumps({
        "collections": [
            {"url": "https://example.test/collections/birthdays-1", "title": "Birthday Gift Hampers"},
            {"url": "https://example.test/collections/21st-birthday-gifts", "title": "21st Birthday Gifts"},
            {"url": "https://example.test/collections/50th-birthday-gifts", "title": "50th Birthday Gifts"},
            {"url": "https://example.test/collections/corporate-gifts", "title": "Corporate Gifts"},
            {"url": "https://example.test/collections/christmas-hampers", "title": "Christmas Hampers"},
        ]
    }))
    blogs_path = tmp_path / "blogs.json"
    blogs_path.write_text(json.dumps({
        "blogs": [
            {"url": "https://example.test/blogs/news/perth-same-day-hampers", "title": "Perth Same-Day Hampers"},
            {"url": "https://example.test/blogs/news/mothers-day-meaning", "title": "The Meaning Behind Mother's Day"},
        ]
    }))

    result = blog_links.build_candidates(
        brief_json=brief_path,
        collections_sitemap=collections_path,
        blogs_sitemap=blogs_path,
        slug="birthday-gift-ideas-milestone-birthdays",
    )
    collection_urls = [row["target_url"] for row in result["collection_links"]]
    blog_urls = [row["target_url"] for row in result["blog_links"]]

    assert result["ok"] is True
    assert collection_urls[0] in {
        "https://example.test/collections/birthdays-1",
        "https://example.test/collections/21st-birthday-gifts",
    }
    assert "https://example.test/collections/birthdays-1" in collection_urls
    assert "https://example.test/blogs/news/perth-same-day-hampers" in blog_urls
    assert all(row["suggested_anchor"] for row in result["collection_links"])


def _write_fixture_files(tmp_path: Path) -> dict[str, Path]:
    client = _client()
    paths = {
        "client": tmp_path / "client.json",
        "keywords": tmp_path / "keywords.json",
        "volumes_au": tmp_path / "volumes-au.json",
        "volumes_us": tmp_path / "volumes-us.json",
        "pages": tmp_path / "pages.json",
        "serp": tmp_path / "serp.json",
        "products": tmp_path / "products.json",
        "supplemental": tmp_path / "supplemental.json",
    }
    paths["client"].write_text(json.dumps(client))
    paths["keywords"].write_text(json.dumps({
        "data": [
            {
                "name": collection["primary_keyword"],
                "link": collection["url"],
                "site_engine_ids": [1, 2],
            }
            for collection in client["collections"]
        ]
    }))
    paths["volumes_au"].write_text(json.dumps({
        collection["primary_keyword"]: collection["au_volume"]
        for collection in client["collections"]
    }))
    paths["volumes_us"].write_text(json.dumps({
        collection["primary_keyword"]: collection["us_volume"]
        for collection in client["collections"]
    }))
    paths["pages"].write_text(json.dumps({
        collection["slug"]: {
            "title": collection["current_title"],
            "h1": collection["current_h1"],
            "meta_description": collection["current_meta_description"],
            "main_content_summary": f"Current copy for {collection['current_h1']} grounded in the visible collection.",
        }
        for collection in client["collections"]
    }))
    paths["serp"].write_text(json.dumps({
        collection["slug"]: {
            "serp_results": [
                {
                    "position": 1,
                    "title": f"{collection['current_h1']} Online | Competitor",
                    "url": f"https://competitor.test/{collection['slug']}",
                    "h1": collection["current_h1"],
                    "h2s": ["How to choose", "Shop the range"],
                    "meta_description": "Competitor collection description.",
                }
            ],
            "patterns": {"copy_angles": ["style-led"], "title_formula": "Keyword | Brand"},
        }
        for collection in client["collections"]
    }))
    paths["products"].write_text(json.dumps({
        collection["slug"]: {
            "products": [
                {"title": f"{collection['current_h1']} Product A"},
                {"title": f"{collection['current_h1']} Product B"},
            ]
        }
        for collection in client["collections"]
    }))
    paths["supplemental"].write_text(json.dumps({
        "by_slug": {
            collection["slug"]: [
                {
                    "keyword": f"{collection['primary_keyword']} online",
                    "au_volume": max(500, collection["au_volume"] // 2),
                    "us_volume": max(500, collection["us_volume"] // 2),
                    "difficulty": 30,
                    "source": "SE Ranking AU related",
                    "reasoning": "Relevant category variant with commercial intent.",
                }
            ]
            for collection in client["collections"]
        }
    }))
    return paths


def _client() -> dict:
    return {
        "client": "Test Store",
        "domain": "example.test",
        "market_scope": "AU+US",
        "collections": _collections(6),
    }


def _collections(count: int) -> list[dict]:
    seeds = [
        ("dresses", "womens dresses", "Dresses", "DRESSES", 10000),
        ("maxis", "maxi dress", "Maxis", "DRESSES", 8000),
        ("minis", "mini dress", "Minis", "DRESSES", 7000),
        ("tops", "going out tops", "Tops", "TOP", 6000),
        ("skirts", "skirt", "Skirts", "SKIRTS", 5000),
        ("sets", "two piece set", "Sets", "TOP", 4000),
        ("pants", "womens pants", "Pants", "PANTS", 3000),
    ]
    collections = []
    for slug, keyword, h1, product_type, volume in seeds[:count]:
        collections.append({
            "slug": slug,
            "url": f"https://example.test/collections/{slug}",
            "class": "pure_category",
            "dominant_product_type": product_type,
            "primary_keyword": keyword,
            "au_volume": volume,
            "us_volume": volume * 2,
            "current_title": f"{h1} - Test Store",
            "current_h1": h1,
            "current_meta_description": f"Shop {h1.lower()} at Test Store.",
            "sample_product_titles": [f"{h1} Product"],
            "product_count_sample": 2,
        })
    return collections
