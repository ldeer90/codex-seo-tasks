from __future__ import annotations

from typing import Any

from googleapiclient.errors import HttpError

from .access_routing import GoogleAccessRouter
from .collection_opportunities import merge_landing_page_rows, summarise_collection_opportunities
from .config import Settings
from .firecrawl import FirecrawlClient
from .google_clients import GoogleWorkspaceClient, dated_title
from .reports import (
    build_combined_doc_text,
    build_combined_sheet_values,
    build_firecrawl_audit_doc_text,
    build_site_audit_sheet_values,
)
from .seo_analysis import (
    PageSEOAudit,
    build_absolute_urls,
    bounded_limit,
    extract_page_seo_from_firecrawl,
    normalise_url,
)


async def scrape_urls_for_audit(
    urls: list[str],
    *,
    settings: Settings | None = None,
) -> list[PageSEOAudit]:
    client = FirecrawlClient(settings)
    scrapes = await client.scrape_urls(urls)
    return [extract_page_seo_from_firecrawl(result) for result in scrapes]


async def create_site_audit_sheet(
    *,
    client_name: str,
    urls: list[str],
    settings: Settings | None = None,
) -> dict[str, Any]:
    settings = settings or Settings.from_env()
    subjects = GoogleAccessRouter(settings).resolve(client_name=client_name)
    pages = await scrape_urls_for_audit(urls, settings=settings)
    google = GoogleWorkspaceClient(settings, delegated_subject=subjects.output.subject)
    sheet = google.create_sheet(
        dated_title(client_name, "Site Audit"),
        build_site_audit_sheet_values(pages),
    )
    return {
        "client_name": client_name,
        "sheet": sheet,
        "pages_audited": len(pages),
        "google_subjects": subjects.to_dict(),
        "rows": [page.to_dict() for page in pages],
    }


async def create_firecrawl_seo_audit_doc(
    *,
    client_name: str,
    start_url: str,
    limit: int | None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    settings = settings or Settings.from_env()
    subjects = GoogleAccessRouter(settings).resolve(client_name=client_name, website_url=start_url)
    resolved_limit = bounded_limit(
        limit,
        settings.firecrawl_default_crawl_limit,
        settings.firecrawl_max_crawl_limit,
    )
    firecrawl = FirecrawlClient(settings)
    crawl = await firecrawl.crawl_site(start_url, limit=resolved_limit)
    pages = [extract_page_seo_from_firecrawl(result) for result in crawl.get("data", [])]

    google = GoogleWorkspaceClient(settings, delegated_subject=subjects.output.subject)
    sheet = google.create_sheet(
        dated_title(client_name, "Firecrawl Site Audit"),
        build_site_audit_sheet_values(pages),
    )
    doc = google.create_doc(
        dated_title(client_name, "Firecrawl SEO Audit"),
        build_firecrawl_audit_doc_text(
            client_name=client_name,
            start_url=start_url,
            limit=resolved_limit,
            pages=pages,
            sheet_url=sheet["url"],
        ),
    )
    return {
        "client_name": client_name,
        "doc": doc,
        "sheet": sheet,
        "pages_audited": len(pages),
        "crawl_id": crawl.get("id"),
        "google_subjects": subjects.to_dict(),
    }


async def create_combined_seo_report(
    *,
    client_name: str,
    ga4_property_id: str | None,
    website_url: str,
    start_date: str,
    end_date: str,
    comparison_start_date: str,
    comparison_end_date: str,
    crawl_limit: int | None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    settings = settings or Settings.from_env()
    resolved_limit = bounded_limit(
        crawl_limit,
        settings.firecrawl_default_crawl_limit,
        min(settings.firecrawl_max_crawl_limit, settings.firecrawl_max_scrape_urls),
    )
    property_name = settings.resolve_ga4_property_id(ga4_property_id)
    subjects = GoogleAccessRouter(settings).resolve(
        client_name=client_name,
        website_url=website_url,
        ga4_property_id=property_name,
    )
    analytics_subject = _resolve_accessible_ga4_subject(
        settings=settings,
        ga4_property_id=property_name,
        preferred_subject=subjects.analytics.subject,
    )
    output_subject = subjects.output.subject
    google = GoogleWorkspaceClient(settings, delegated_subject=analytics_subject)
    current_rows = google.run_ga4_report(
        ga4_property_id=property_name,
        start_date=start_date,
        end_date=end_date,
        limit=resolved_limit,
    )
    comparison_rows = google.run_ga4_report(
        ga4_property_id=property_name,
        start_date=comparison_start_date,
        end_date=comparison_end_date,
        limit=resolved_limit,
    )
    comparison_by_page = {row["landing_page"]: row for row in comparison_rows}
    urls = build_absolute_urls(
        website_url,
        [row["landing_page"] for row in current_rows],
        limit=resolved_limit,
    )

    audits_by_url: dict[str, PageSEOAudit] = {}
    if urls:
        firecrawl = FirecrawlClient(settings)
        scrapes = await firecrawl.scrape_urls(urls)
        audits_by_url = {
            normalise_url(audit.url): audit
            for audit in (extract_page_seo_from_firecrawl(result) for result in scrapes)
            if audit.url
        }

    combined_rows: list[dict[str, Any]] = []
    for current in current_rows:
        url = build_absolute_urls(website_url, [current["landing_page"]], limit=1)
        if not url:
            continue
        audit = audits_by_url.get(normalise_url(url[0]))
        if not audit:
            continue
        combined_rows.append(
            {
                "current": current,
                "comparison": comparison_by_page.get(current["landing_page"], {}),
                "audit": audit,
            }
        )

    output_google = GoogleWorkspaceClient(settings, delegated_subject=output_subject)
    sheet = output_google.create_sheet(
        dated_title(client_name, "Combined SEO Report Data"),
        build_combined_sheet_values(combined_rows),
    )
    doc = output_google.create_doc(
        dated_title(client_name, "Combined SEO Report"),
        build_combined_doc_text(
            client_name=client_name,
            website_url=website_url,
            start_date=start_date,
            end_date=end_date,
            comparison_start_date=comparison_start_date,
            comparison_end_date=comparison_end_date,
            rows=combined_rows,
            sheet_url=sheet["url"],
        ),
    )
    return {
        "client_name": client_name,
        "doc": doc,
        "sheet": sheet,
        "ga4_property_id": property_name,
        "landing_pages_audited": len(combined_rows),
        "google_subjects": {
            **subjects.to_dict(),
            "analytics": {
                **subjects.analytics.to_dict(),
                "subject": analytics_subject,
            },
            "output": {
                **subjects.output.to_dict(),
                "subject": output_subject,
            },
        },
    }


def ga4_collection_opportunities(
    *,
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
    settings: Settings | None = None,
) -> dict[str, Any]:
    settings = settings or Settings.from_env()
    property_name = settings.resolve_ga4_property_id(ga4_property_id)
    subjects = GoogleAccessRouter(settings).resolve(
        client_name=client_name,
        website_url=website_url,
        ga4_property_id=property_name,
    )
    analytics_subject = _resolve_accessible_ga4_subject(
        settings=settings,
        ga4_property_id=property_name,
        preferred_subject=subjects.analytics.subject,
    )
    google = GoogleWorkspaceClient(settings, delegated_subject=analytics_subject)
    source_limit = max(limit, 250)
    current_by_sessions = google.run_ga4_landing_page_report(
        ga4_property_id=property_name,
        start_date=start_date,
        end_date=end_date,
        limit=source_limit,
        channel=channel,
        path_prefix=path_prefix,
        order_metric="sessions",
    )
    current_by_revenue = google.run_ga4_landing_page_report(
        ga4_property_id=property_name,
        start_date=start_date,
        end_date=end_date,
        limit=source_limit,
        channel=channel,
        path_prefix=path_prefix,
        order_metric="totalRevenue",
    )
    comparison_by_sessions = google.run_ga4_landing_page_report(
        ga4_property_id=property_name,
        start_date=comparison_start_date,
        end_date=comparison_end_date,
        limit=source_limit,
        channel=channel,
        path_prefix=path_prefix,
        order_metric="sessions",
    )
    comparison_by_revenue = google.run_ga4_landing_page_report(
        ga4_property_id=property_name,
        start_date=comparison_start_date,
        end_date=comparison_end_date,
        limit=source_limit,
        channel=channel,
        path_prefix=path_prefix,
        order_metric="totalRevenue",
    )
    current_rows = merge_landing_page_rows(current_by_sessions, current_by_revenue)
    comparison_rows = merge_landing_page_rows(comparison_by_sessions, comparison_by_revenue)
    summary = summarise_collection_opportunities(
        current_rows=current_rows,
        comparison_rows=comparison_rows,
        website_url=website_url,
        path_prefix=path_prefix,
        limit=limit,
    )
    return {
        "client_name": client_name,
        "ga4_property_id": property_name,
        "website_url": website_url,
        "date_range": {"start_date": start_date, "end_date": end_date},
        "comparison_date_range": {
            "start_date": comparison_start_date,
            "end_date": comparison_end_date,
        },
        "channel": channel,
        "source_limit_per_ordering": source_limit,
        "google_subjects": {
            **subjects.to_dict(),
            "analytics": {
                **subjects.analytics.to_dict(),
                "subject": analytics_subject,
                "validated": True,
            },
        },
        **summary,
    }


def resolve_google_access_subjects(
    *,
    client_name: str | None = None,
    website_url: str | None = None,
    ga4_property_id: str | None = None,
    settings: Settings | None = None,
    validate_ga4_access: bool = True,
) -> dict[str, Any]:
    settings = settings or Settings.from_env()
    property_name = settings.resolve_ga4_property_id(ga4_property_id) if ga4_property_id else None
    subjects = GoogleAccessRouter(settings).resolve(
        client_name=client_name,
        website_url=website_url,
        ga4_property_id=property_name,
    )
    result = subjects.to_dict()
    if property_name and validate_ga4_access:
        result["analytics"]["subject"] = _resolve_accessible_ga4_subject(
            settings=settings,
            ga4_property_id=property_name,
            preferred_subject=subjects.analytics.subject,
        )
        result["analytics"]["validated"] = True
    else:
        result["analytics"]["validated"] = False
    result["candidates"] = list(settings.google_subject_candidates())
    return result


def _resolve_accessible_ga4_subject(
    *,
    settings: Settings,
    ga4_property_id: str,
    preferred_subject: str | None,
) -> str | None:
    candidates: list[str | None] = []
    for subject in (preferred_subject, *settings.google_subject_candidates(), None):
        if subject not in candidates:
            candidates.append(subject)

    errors: list[str] = []
    for subject in candidates:
        try:
            GoogleWorkspaceClient(settings, delegated_subject=subject).get_ga4_property(ga4_property_id)
            return subject
        except HttpError as exc:
            if exc.resp.status in {401, 403, 404}:
                label = subject or "<service account>"
                errors.append(f"{label}: {exc.resp.status}")
                continue
            raise

    tried = ", ".join(errors) if errors else "no configured subjects"
    raise ValueError(f"No configured Google delegated subject can access {ga4_property_id}: {tried}")
