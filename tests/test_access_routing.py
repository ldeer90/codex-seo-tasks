from pathlib import Path

from seo_automation_mcp.access_routing import GoogleAccessRouter
from seo_automation_mcp.config import Settings


def settings(path: Path) -> Settings:
    return Settings(
        firecrawl_api_key=None,
        firecrawl_base_url="https://api.firecrawl.dev",
        firecrawl_default_crawl_limit=25,
        firecrawl_max_crawl_limit=100,
        firecrawl_max_scrape_urls=50,
        firecrawl_crawl_timeout_seconds=180,
        google_application_credentials="/tmp/service.json",
        google_cloud_project="project",
        google_delegated_subject="seo@agents.digital",
        google_delegated_subjects=("seo@agents.digital", "hello@agents.digital"),
        google_output_delegated_subject="hello@agents.digital",
        google_site_access_map_path=str(path),
        google_drive_reports_folder_id="folder",
        default_ga4_property_id=None,
        monday_api_key=None,
    )


def test_resolves_property_before_client_and_host(tmp_path: Path) -> None:
    rules = tmp_path / "site-access.json"
    rules.write_text(
        """
        {
          "default_google_subject": "seo@agents.digital",
          "properties": {"properties/123": "hello@agents.digital"},
          "clients": {"client": "seo@agents.digital"},
          "hosts": {"example.com": "seo@agents.digital"}
        }
        """
    )

    subjects = GoogleAccessRouter(settings(rules)).resolve(
        client_name="Client",
        website_url="https://www.example.com",
        ga4_property_id="123",
    )

    assert subjects.analytics.subject == "hello@agents.digital"
    assert subjects.analytics.source == "property"


def test_resolves_parent_host_and_output_subject(tmp_path: Path) -> None:
    rules = tmp_path / "site-access.json"
    rules.write_text(
        """
        {
          "hosts": {"example.com": "hello@agents.digital"}
        }
        """
    )

    subjects = GoogleAccessRouter(settings(rules)).resolve(
        website_url="https://shop.example.com/products",
    )

    assert subjects.analytics.subject == "hello@agents.digital"
    assert subjects.analytics.source == "host"
    assert subjects.output.subject == "hello@agents.digital"
