from __future__ import annotations

from typing import Any

from .seo_analysis import PageSEOAudit


SITE_AUDIT_HEADERS = [
    "URL",
    "Status",
    "Title",
    "Meta Description",
    "H1",
    "H2 Count",
    "Word Count",
    "Canonical",
    "Main Content Summary",
    "Issues",
    "Recommendations",
]

COMBINED_REPORT_HEADERS = [
    "URL",
    "Landing Page",
    "Sessions",
    "Comparison Sessions",
    "Session Change",
    "Users",
    "Engaged Sessions",
    "Conversions",
    *SITE_AUDIT_HEADERS[1:],
]


def build_site_audit_sheet_values(pages: list[PageSEOAudit]) -> list[list[Any]]:
    return [SITE_AUDIT_HEADERS, *[page.to_sheet_row() for page in pages]]


def build_combined_sheet_values(rows: list[dict[str, Any]]) -> list[list[Any]]:
    values = [COMBINED_REPORT_HEADERS]
    for row in rows:
        audit: PageSEOAudit = row["audit"]
        current = row["current"]
        comparison = row.get("comparison", {})
        sessions = current.get("sessions", 0)
        comparison_sessions = comparison.get("sessions", 0)
        values.append(
            [
                audit.url,
                current.get("landing_page", ""),
                sessions,
                comparison_sessions,
                sessions - comparison_sessions,
                current.get("users", 0),
                current.get("engaged_sessions", 0),
                current.get("conversions", 0),
                audit.status,
                audit.title,
                audit.meta_description,
                audit.h1,
                len(audit.h2s),
                audit.word_count,
                audit.canonical,
                audit.main_content_summary,
                "\n".join(audit.issues),
                "\n".join(audit.recommendations),
            ]
        )
    return values


def build_firecrawl_audit_doc_text(
    *,
    client_name: str,
    start_url: str,
    limit: int,
    pages: list[PageSEOAudit],
    sheet_url: str,
) -> str:
    total_issues = sum(len(page.issues) for page in pages)
    missing_titles = sum(1 for page in pages if not page.title)
    low_content = sum(1 for page in pages if page.word_count < 300)
    missing_meta = sum(1 for page in pages if not page.meta_description)
    top_pages = sorted(pages, key=lambda page: len(page.issues), reverse=True)[:10]

    lines = [
        f"{client_name} Firecrawl SEO Audit",
        "",
        "Executive summary",
        f"Crawled start URL: {start_url}",
        f"Crawl limit: {limit}",
        f"Pages audited: {len(pages)}",
        f"Total issues detected: {total_issues}",
        "",
        "Main findings",
        f"- Missing titles: {missing_titles}",
        f"- Missing meta descriptions: {missing_meta}",
        f"- Pages below 300 words: {low_content}",
        "",
        "Highest priority pages",
    ]
    for page in top_pages:
        issues = "; ".join(page.issues) if page.issues else "No obvious issues"
        lines.append(f"- {page.url}: {issues}")
    lines.extend(
        [
            "",
            "Recommended actions",
            "- Fix pages returning non-200 statuses before content optimization.",
            "- Add or improve missing and weak titles, meta descriptions, and H1s.",
            "- Expand thin pages where the topic deserves more useful supporting content.",
            "- Add relevant internal links from and to important commercial pages.",
            "",
            f"Supporting Sheet: {sheet_url}",
        ]
    )
    return "\n".join(lines)


def build_combined_doc_text(
    *,
    client_name: str,
    website_url: str,
    start_date: str,
    end_date: str,
    comparison_start_date: str,
    comparison_end_date: str,
    rows: list[dict[str, Any]],
    sheet_url: str,
) -> str:
    total_sessions = sum(row["current"].get("sessions", 0) for row in rows)
    total_previous_sessions = sum(row.get("comparison", {}).get("sessions", 0) for row in rows)
    total_issues = sum(len(row["audit"].issues) for row in rows)
    gains = sorted(
        rows,
        key=lambda row: row["current"].get("sessions", 0)
        - row.get("comparison", {}).get("sessions", 0),
        reverse=True,
    )[:5]
    declines = sorted(
        rows,
        key=lambda row: row["current"].get("sessions", 0)
        - row.get("comparison", {}).get("sessions", 0),
    )[:5]
    issue_pages = sorted(rows, key=lambda row: len(row["audit"].issues), reverse=True)[:10]

    lines = [
        f"{client_name} Combined SEO Report",
        "",
        "Executive summary",
        f"Website: {website_url}",
        f"Reporting period: {start_date} to {end_date}",
        f"Comparison period: {comparison_start_date} to {comparison_end_date}",
        f"Audited landing pages: {len(rows)}",
        f"Organic sessions across audited pages: {total_sessions:g}",
        f"Comparison organic sessions: {total_previous_sessions:g}",
        f"Page-level issues found: {total_issues}",
        "",
        "Organic performance summary",
        f"Session change: {total_sessions - total_previous_sessions:g}",
        "",
        "Top landing pages",
    ]
    for row in rows[:10]:
        current = row["current"]
        audit: PageSEOAudit = row["audit"]
        lines.append(f"- {audit.url}: {current.get('sessions', 0):g} sessions")

    lines.append("")
    lines.append("Biggest gains")
    for row in gains:
        current = row["current"]
        previous = row.get("comparison", {})
        audit: PageSEOAudit = row["audit"]
        delta = current.get("sessions", 0) - previous.get("sessions", 0)
        lines.append(f"- {audit.url}: +{delta:g} sessions")

    lines.append("")
    lines.append("Biggest declines")
    for row in declines:
        current = row["current"]
        previous = row.get("comparison", {})
        audit: PageSEOAudit = row["audit"]
        delta = current.get("sessions", 0) - previous.get("sessions", 0)
        lines.append(f"- {audit.url}: {delta:g} sessions")

    lines.append("")
    lines.append("Page-level SEO issues")
    for row in issue_pages:
        audit: PageSEOAudit = row["audit"]
        issues = "; ".join(audit.issues) if audit.issues else "No obvious issues"
        lines.append(f"- {audit.url}: {issues}")

    lines.extend(
        [
            "",
            "Recommended actions",
            "- Prioritize fixes on pages with both traffic and clear SEO issues.",
            "- Protect pages with strong gains by checking title, meta, H1, and internal links.",
            "- Investigate pages with the biggest declines for content quality, intent, and indexing issues.",
            "- Use the supporting Sheet to assign page-level updates.",
            "",
            f"Supporting Sheet: {sheet_url}",
        ]
    )
    return "\n".join(lines)
