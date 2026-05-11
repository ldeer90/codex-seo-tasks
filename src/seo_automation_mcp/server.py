from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import Settings
from .firecrawl import FirecrawlClient
from .seo_analysis import (
    extract_page_seo_from_firecrawl,
    normalise_scrape_result,
)
from .workflows import (
    create_combined_seo_report as run_create_combined_seo_report,
    create_firecrawl_seo_audit_doc as run_create_firecrawl_seo_audit_doc,
    create_site_audit_sheet as run_create_site_audit_sheet,
    ga4_collection_opportunities as run_ga4_collection_opportunities,
    resolve_google_access_subjects as run_resolve_google_access_subjects,
)

mcp = FastMCP("SEO Automation")


@mcp.tool()
async def crawl_site(
    url: str,
    limit: int | None = None,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Crawl a website or section and return discovered page data from Firecrawl."""
    client = FirecrawlClient(Settings.from_env())
    return await client.crawl_site(
        url=url,
        limit=limit,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
    )


@mcp.tool()
async def scrape_url(url: str, formats: list[str] | None = None) -> dict[str, Any]:
    """Scrape one URL with Firecrawl and return markdown, metadata, and requested formats."""
    client = FirecrawlClient(Settings.from_env())
    return await client.scrape_url(url=url, formats=formats or ["markdown"])


@mcp.tool()
async def scrape_urls(urls: list[str]) -> dict[str, Any]:
    """Scrape multiple URLs and return normalized Firecrawl page data."""
    client = FirecrawlClient(Settings.from_env())
    results = await client.scrape_urls(urls)
    return {"count": len(results), "pages": [normalise_scrape_result(result) for result in results]}


@mcp.tool()
async def extract_page_seo(url: str) -> dict[str, Any]:
    """Scrape one URL and return page-level SEO fields, issues, and recommendations."""
    client = FirecrawlClient(Settings.from_env())
    result = await client.scrape_url(url=url, formats=["markdown", "html", "links"])
    return extract_page_seo_from_firecrawl(result).to_dict()


@mcp.tool()
async def create_site_audit_sheet(client_name: str, urls: list[str]) -> dict[str, Any]:
    """Scrape URLs, create a Google Sheet in the reports folder, and write one row per URL."""
    return await run_create_site_audit_sheet(
        client_name=client_name,
        urls=urls,
        settings=Settings.from_env(),
    )


@mcp.tool()
async def create_firecrawl_seo_audit_doc(
    client_name: str,
    start_url: str,
    limit: int | None = None,
) -> dict[str, Any]:
    """Crawl a site, create a crawl Sheet and SEO audit Doc, and return both links."""
    return await run_create_firecrawl_seo_audit_doc(
        client_name=client_name,
        start_url=start_url,
        limit=limit,
        settings=Settings.from_env(),
    )


@mcp.tool()
def resolve_google_access_subject(
    client_name: str | None = None,
    website_url: str | None = None,
    ga4_property_id: str | None = None,
    validate_ga4_access: bool = True,
) -> dict[str, Any]:
    """Return which delegated Google email will be used for a client/site/property."""
    return run_resolve_google_access_subjects(
        client_name=client_name,
        website_url=website_url,
        ga4_property_id=ga4_property_id,
        validate_ga4_access=validate_ga4_access,
        settings=Settings.from_env(),
    )


@mcp.tool()
def ga4_collection_opportunities(
    client_name: str,
    ga4_property_id: str | None,
    website_url: str,
    start_date: str,
    end_date: str,
    comparison_start_date: str,
    comparison_end_date: str,
    channel: str = "Organic Search",
    path_prefix: str = "/collections/",
    limit: int = 100,
) -> dict[str, Any]:
    """Read GA4 collection landing-page performance and return prioritised collection opportunities."""
    return run_ga4_collection_opportunities(
        client_name=client_name,
        ga4_property_id=ga4_property_id,
        website_url=website_url,
        start_date=start_date,
        end_date=end_date,
        comparison_start_date=comparison_start_date,
        comparison_end_date=comparison_end_date,
        channel=channel,
        path_prefix=path_prefix,
        limit=limit,
        settings=Settings.from_env(),
    )


@mcp.tool()
async def create_combined_seo_report(
    client_name: str,
    ga4_property_id: str | None,
    website_url: str,
    start_date: str,
    end_date: str,
    comparison_start_date: str,
    comparison_end_date: str,
    crawl_limit: int | None = None,
) -> dict[str, Any]:
    """Create a combined GA4 + Firecrawl SEO report Doc and supporting Sheet."""
    return await run_create_combined_seo_report(
        client_name=client_name,
        ga4_property_id=ga4_property_id,
        website_url=website_url,
        start_date=start_date,
        end_date=end_date,
        comparison_start_date=comparison_start_date,
        comparison_end_date=comparison_end_date,
        crawl_limit=crawl_limit,
        settings=Settings.from_env(),
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
