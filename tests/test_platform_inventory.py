from seo_automation_mcp.platform_inventory import (
    client_key,
    render_markdown_reference,
    web_stream_summaries,
)


def test_client_key_normalises_ga4_and_subitem_noise() -> None:
    assert client_key("Avenue Hampers - GA4") == "avenue hampers"
    assert client_key("Subitems of TravelKon") == "travelkon"
    assert client_key("Acorn Car Rentals") == "acorn rentals"
    assert client_key("Melanit the Label") == "melani the label"
    assert client_key("SEO Tasks") == ""


def test_web_stream_summaries_extracts_default_uri() -> None:
    streams = web_stream_summaries(
        [
            {
                "name": "properties/123/dataStreams/456",
                "displayName": "Web",
                "webStreamData": {
                    "defaultUri": "https://example.com",
                    "measurementId": "G-TEST",
                },
            }
        ]
    )

    assert streams == [
        {
            "name": "Web",
            "stream": "properties/123/dataStreams/456",
            "default_uri": "https://example.com",
            "measurement_id": "G-TEST",
        }
    ]


def test_render_markdown_reference_includes_se_ranking_mcp() -> None:
    markdown = render_markdown_reference(
        {
            "generated_at": "2026-05-08T00:00:00+00:00",
            "credentials": {
                "google_delegated_subjects": ["seo@agents.digital"],
                "google_output_delegated_subject": "hello@agents.digital",
                "google_site_access_map": "config/site-access.json",
                "monday_api_key_configured": False,
                "se_ranking_mcp_name": "se-ranking",
                "se_ranking_mcp_url": "https://api.seranking.com/mcp",
            },
            "google": {"subjects": {}},
            "monday": {"workspace_count": 0, "board_count": 0, "workspaces": []},
            "se_ranking": {
                "mcp": {
                    "name": "se-ranking",
                    "url": "https://api.seranking.com/mcp",
                    "configured": True,
                    "status": "enabled",
                    "auth": "OAuth",
                },
                "inventory_scope": "connector mapping only",
                "exports_project_data": False,
                "recommended_uses": ["keyword ranking lookups"],
                "guardrails": ["Use the remote MCP server instead of storing an API key."],
            },
            "cross_platform_client_map": {"clients": [], "unmatched": {}},
        }
    )

    assert "## SE Ranking Inventory" in markdown
    assert "- MCP server: `se-ranking`" in markdown
    assert "- Auth: OAuth" in markdown
    assert "keyword ranking lookups" in markdown
