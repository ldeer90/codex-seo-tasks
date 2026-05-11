from __future__ import annotations

import pytest

from seo_automation_mcp.collection_opportunities import (
    collection_slug_from_landing_page,
    merge_landing_page_rows,
    summarise_collection_opportunities,
)
from seo_automation_mcp.google_clients import GoogleWorkspaceClient


def test_collection_slug_from_landing_page_accepts_relative_and_absolute_urls() -> None:
    assert collection_slug_from_landing_page("/collections/hampers-for-him?sort=best") == "hampers-for-him"
    assert (
        collection_slug_from_landing_page(
            "https://www.example.com/collections/hampers-for-her/products/example"
        )
        == "hampers-for-her"
    )
    assert collection_slug_from_landing_page("/products/example") == ""
    assert collection_slug_from_landing_page("/collections/all") == ""


def test_merge_landing_page_rows_deduplicates_session_and_revenue_pulls() -> None:
    session_rows = [
        {
            "landing_page": "/collections/hampers-for-him",
            "channel": "Organic Search",
            "sessions": 120,
            "revenue": 240,
            "conversions": 3,
        },
        {
            "landing_page": "/collections/corporate-hampers",
            "channel": "Organic Search",
            "sessions": 90,
            "revenue": 0,
        },
    ]
    revenue_rows = [
        {
            "landing_page": "/collections/hampers-for-him",
            "channel": "Organic Search",
            "sessions": 120,
            "revenue": 240,
            "conversions": 3,
        },
        {
            "landing_page": "/collections/christmas-hampers",
            "channel": "Organic Search",
            "sessions": 12,
            "revenue": 600,
            "purchases": 4,
        },
    ]

    merged = merge_landing_page_rows(session_rows, revenue_rows)
    by_page = {row["landing_page"]: row for row in merged}

    assert len(merged) == 3
    assert by_page["/collections/hampers-for-him"]["sessions"] == 120
    assert by_page["/collections/hampers-for-him"]["revenue"] == 240
    assert by_page["/collections/christmas-hampers"]["revenue"] == 600


def test_summarise_collection_opportunities_prioritises_revenue_decline_and_monetisation() -> None:
    summary = summarise_collection_opportunities(
        current_rows=[
            {
                "landing_page": "/collections/hampers-for-him",
                "channel": "Organic Search",
                "sessions": 300,
                "users": 250,
                "engaged_sessions": 180,
                "conversions": 8,
                "revenue": 650,
                "purchases": 7,
            },
            {
                "landing_page": "/collections/corporate-hampers",
                "channel": "Organic Search",
                "sessions": 400,
                "users": 330,
                "engaged_sessions": 240,
                "conversions": 0,
                "revenue": 0,
                "purchases": 0,
            },
        ],
        comparison_rows=[
            {
                "landing_page": "/collections/hampers-for-him",
                "channel": "Organic Search",
                "sessions": 360,
                "users": 310,
                "engaged_sessions": 220,
                "conversions": 10,
                "revenue": 900,
                "purchases": 9,
            }
        ],
        website_url="https://www.avenuehampers.com.au",
        limit=10,
    )

    rows = {row["slug"]: row for row in summary["opportunities"]}

    assert summary["count"] == 2
    assert rows["hampers-for-him"]["priority_bucket"] == "Protect / Rescue"
    assert rows["hampers-for-him"]["delta"]["revenue"] == -250
    assert rows["corporate-hampers"]["priority_bucket"] == "Monetise"
    assert summary["totals"]["sessions"] == 700
    assert summary["totals"]["revenue"] == 650


def test_ga4_landing_page_report_rejects_unknown_order_metric_before_api_call() -> None:
    client = GoogleWorkspaceClient.__new__(GoogleWorkspaceClient)

    with pytest.raises(ValueError, match="Unsupported GA4 order metric"):
        client.run_ga4_landing_page_report(
            ga4_property_id="properties/123",
            start_date="2026-04-01",
            end_date="2026-04-30",
            limit=10,
            order_metric="screenPageViews",
        )
