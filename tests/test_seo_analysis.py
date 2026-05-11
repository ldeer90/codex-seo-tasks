from seo_automation_mcp.seo_analysis import (
    build_absolute_urls,
    extract_page_seo_from_firecrawl,
    merge_exclude_paths,
)


def test_extract_page_seo_from_firecrawl_html_and_markdown() -> None:
    result = {
        "success": True,
        "data": {
            "markdown": "# Main Service\n\n## Benefits\n\nHelpful service content for local clients.",
            "html": """
              <html>
                <head>
                  <title>Local SEO Services for Melbourne Businesses</title>
                  <meta name="description" content="Practical local SEO services for Melbourne businesses that need more qualified organic leads.">
                  <link rel="canonical" href="https://example.com/services/local-seo">
                </head>
                <body>
                  <h1>Main Service</h1>
                  <h2>Benefits</h2>
                  <p>Helpful service content for local clients.</p>
                  <a href="/contact">Contact</a>
                  <a href="https://external.example/test">External</a>
                </body>
              </html>
            """,
            "metadata": {
                "sourceURL": "https://example.com/services/local-seo",
                "statusCode": 200,
            },
        },
    }

    audit = extract_page_seo_from_firecrawl(result)

    assert audit.url == "https://example.com/services/local-seo"
    assert audit.title == "Local SEO Services for Melbourne Businesses"
    assert audit.h1 == "Main Service"
    assert audit.h2s == ["Benefits"]
    assert audit.canonical == "https://example.com/services/local-seo"
    assert audit.internal_links == ["https://example.com/contact"]


def test_build_absolute_urls_filters_guarded_paths() -> None:
    urls = build_absolute_urls(
        "https://example.com",
        ["/services", "/cart", "https://example.com/checkout", "https://example.com/about"],
    )

    assert urls == ["https://example.com/services", "https://example.com/about"]


def test_merge_exclude_paths_keeps_defaults_and_user_patterns() -> None:
    merged = merge_exclude_paths([r".*/private(/.*)?$"])

    assert r".*/checkout(/.*)?$" in merged
    assert r".*/private(/.*)?$" in merged

