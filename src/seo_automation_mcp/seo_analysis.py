from __future__ import annotations

import ipaddress
import re
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse


DEFAULT_EXCLUDE_PATHS = [
    r".*/admin(/.*)?$",
    r".*/wp-admin(/.*)?$",
    r".*/login(/.*)?$",
    r".*/logout(/.*)?$",
    r".*/account(/.*)?$",
    r".*/my-account(/.*)?$",
    r".*/cart(/.*)?$",
    r".*/checkout(/.*)?$",
    r".*/payment(/.*)?$",
    r".*/payments(/.*)?$",
    r".*/order(/.*)?$",
    r".*/orders(/.*)?$",
]

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
H1_RE = re.compile(r"^\s{0,3}#(?!#)\s+(.+?)\s*#*\s*$", re.MULTILINE)
H2_RE = re.compile(r"^\s{0,3}##(?!#)\s+(.+?)\s*#*\s*$", re.MULTILINE)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
MARKDOWN_DECORATION_RE = re.compile(r"[*_`>#\[\]()]+")


@dataclass(frozen=True)
class PageSEOAudit:
    url: str
    status: str
    title: str
    meta_description: str
    h1: str
    h2s: list[str]
    word_count: int
    canonical: str
    main_content_summary: str
    internal_links: list[str]
    issues: list[str]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_sheet_row(self) -> list[Any]:
        return [
            self.url,
            self.status,
            self.title,
            self.meta_description,
            self.h1,
            len(self.h2s),
            self.word_count,
            self.canonical,
            self.main_content_summary,
            "\n".join(self.issues),
            "\n".join(self.recommendations),
        ]


class ParsedHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.h1s: list[str] = []
        self.h2s: list[str] = []
        self.links: list[str] = []
        self.text_parts: list[str] = []
        self._capture_title = False
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key.lower(): value or "" for key, value in attrs_list}
        tag = tag.lower()

        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
            return

        if tag == "title":
            self._capture_title = True
            return

        if tag == "meta":
            name = (attrs.get("name") or attrs.get("property") or "").lower()
            if name in {"description", "og:description"} and not self.description:
                self.description = clean_text(attrs.get("content", ""))
            return

        if tag == "link":
            rel = attrs.get("rel", "").lower()
            if "canonical" in rel and not self.canonical:
                self.canonical = attrs.get("href", "").strip()
            return

        if tag in {"h1", "h2"}:
            self._heading_tag = tag
            self._heading_parts = []
            return

        if tag == "a":
            href = attrs.get("href", "").strip()
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
            return

        if tag == "title":
            self._capture_title = False
            return

        if self._heading_tag == tag:
            heading = clean_text(" ".join(self._heading_parts))
            if heading:
                if tag == "h1":
                    self.h1s.append(heading)
                elif tag == "h2":
                    self.h2s.append(heading)
            self._heading_tag = None
            self._heading_parts = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._capture_title:
            self.title = clean_text(f"{self.title} {data}")
        if self._heading_tag:
            self._heading_parts.append(data)
        stripped = clean_text(data)
        if stripped:
            self.text_parts.append(stripped)


def validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"URL must be an absolute http(s) URL: {url}")
    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded credentials are not allowed.")
    host = parsed.hostname or ""
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".local"):
        raise ValueError("Localhost and .local URLs are not allowed for crawl/scrape tools.")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip and (ip.is_private or ip.is_loopback or ip.is_link_local):
        raise ValueError("Private, loopback, and link-local IP URLs are not allowed.")
    return url


def bounded_limit(limit: int | None, default: int, maximum: int) -> int:
    resolved = default if limit is None else int(limit)
    if resolved < 1:
        raise ValueError("limit must be at least 1.")
    if resolved > maximum:
        raise ValueError(f"limit {resolved} exceeds configured maximum {maximum}.")
    return resolved


def merge_exclude_paths(exclude_paths: list[str] | None) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for pattern in [*DEFAULT_EXCLUDE_PATHS, *(exclude_paths or [])]:
        if pattern and pattern not in seen:
            seen.add(pattern)
            merged.append(pattern)
    return merged


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def normalise_url(url: str, base_url: str | None = None) -> str:
    absolute = urljoin(base_url, url) if base_url else url
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "/",
            "",
            parsed.query,
            "",
        )
    )


def filter_internal_links(source_url: str, links: list[str]) -> list[str]:
    source = urlparse(source_url)
    if not source.netloc:
        return []
    internal: list[str] = []
    seen: set[str] = set()
    for link in links:
        absolute = normalise_url(link, source_url)
        parsed = urlparse(absolute)
        if not absolute or parsed.netloc != source.netloc:
            continue
        if _path_is_guarded(parsed.path):
            continue
        if absolute not in seen:
            seen.add(absolute)
            internal.append(absolute)
    return internal


def _path_is_guarded(path: str) -> bool:
    lowered = path.lower()
    guarded_fragments = (
        "/admin",
        "/wp-admin",
        "/login",
        "/logout",
        "/account",
        "/my-account",
        "/cart",
        "/checkout",
        "/payment",
        "/order",
    )
    return any(fragment in lowered for fragment in guarded_fragments)


def parse_html(html: str) -> ParsedHTML:
    parser = ParsedHTML()
    if html:
        parser.feed(html)
        parser.close()
    return parser


def markdown_headings(markdown: str) -> tuple[list[str], list[str]]:
    h1s = [clean_text(match.group(1)) for match in H1_RE.finditer(markdown or "")]
    h2s = [clean_text(match.group(1)) for match in H2_RE.finditer(markdown or "")]
    return [h for h in h1s if h], [h for h in h2s if h]


def markdown_to_text(markdown: str) -> str:
    without_images = MARKDOWN_IMAGE_RE.sub("", markdown or "")
    with_link_text = MARKDOWN_LINK_RE.sub(r"\1", without_images)
    no_decoration = MARKDOWN_DECORATION_RE.sub(" ", with_link_text)
    return clean_text(no_decoration)


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def summarize_text(text: str, max_words: int = 55) -> str:
    words = WORD_RE.findall(text or "")
    if not words:
        return ""
    summary = " ".join(words[:max_words])
    if len(words) > max_words:
        summary = f"{summary}..."
    return summary


def extract_page_seo_from_firecrawl(scrape_result: dict[str, Any]) -> PageSEOAudit:
    data = scrape_result.get("data", scrape_result)
    metadata = data.get("metadata") or {}
    markdown = data.get("markdown") or ""
    html = data.get("html") or data.get("rawHtml") or ""
    parsed = parse_html(html)
    markdown_h1s, markdown_h2s = markdown_headings(markdown)

    source_url = clean_text(
        metadata.get("sourceURL")
        or metadata.get("url")
        or data.get("url")
        or scrape_result.get("url")
        or ""
    )
    title = clean_text(metadata.get("title") or parsed.title)
    meta_description = clean_text(
        metadata.get("description") or metadata.get("ogDescription") or parsed.description
    )
    canonical = clean_text(
        metadata.get("canonical")
        or metadata.get("canonicalUrl")
        or metadata.get("canonicalURL")
        or parsed.canonical
    )
    h1s = parsed.h1s or markdown_h1s
    h2s = parsed.h2s or markdown_h2s
    raw_links = data.get("links") or parsed.links
    internal_links = filter_internal_links(source_url, [str(link) for link in raw_links])

    body_text = markdown_to_text(markdown) or clean_text(" ".join(parsed.text_parts))
    word_count = count_words(body_text)
    status_code = metadata.get("statusCode") or metadata.get("status_code")
    status = str(status_code or "unknown")
    issues, recommendations = assess_page(
        status=status,
        title=title,
        meta_description=meta_description,
        h1s=h1s,
        word_count=word_count,
        canonical=canonical,
        internal_links=internal_links,
    )

    return PageSEOAudit(
        url=source_url,
        status=status,
        title=title,
        meta_description=meta_description,
        h1=h1s[0] if h1s else "",
        h2s=h2s,
        word_count=word_count,
        canonical=canonical,
        main_content_summary=summarize_text(body_text),
        internal_links=internal_links,
        issues=issues,
        recommendations=recommendations,
    )


def normalise_scrape_result(scrape_result: dict[str, Any]) -> dict[str, Any]:
    data = scrape_result.get("data", scrape_result)
    metadata = data.get("metadata") or {}
    audit = extract_page_seo_from_firecrawl(scrape_result)
    return {
        "success": scrape_result.get("success", True),
        "url": audit.url,
        "status": audit.status,
        "title": audit.title,
        "meta_description": audit.meta_description,
        "markdown": data.get("markdown") or "",
        "metadata": metadata,
        "links": data.get("links") or [],
        "error": scrape_result.get("error") or metadata.get("error") or "",
    }


def assess_page(
    *,
    status: str,
    title: str,
    meta_description: str,
    h1s: list[str],
    word_count: int,
    canonical: str,
    internal_links: list[str],
) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    recommendations: list[str] = []

    try:
        status_int = int(status)
    except ValueError:
        status_int = 0

    if status_int >= 400:
        issues.append(f"Page returned HTTP {status_int}.")
        recommendations.append("Fix the URL, redirect, or server issue before auditing content quality.")

    title_len = len(title)
    if not title:
        issues.append("Missing title tag.")
        recommendations.append("Add a descriptive, unique title tag.")
    elif title_len < 30:
        issues.append(f"Title tag is short ({title_len} characters).")
        recommendations.append("Expand the title with the primary topic and useful intent modifiers.")
    elif title_len > 60:
        issues.append(f"Title tag is long ({title_len} characters).")
        recommendations.append("Trim the title so the main topic appears early and is less likely to truncate.")

    description_len = len(meta_description)
    if not meta_description:
        issues.append("Missing meta description.")
        recommendations.append("Add a unique meta description that summarizes the page and search intent.")
    elif description_len < 70:
        issues.append(f"Meta description is short ({description_len} characters).")
        recommendations.append("Make the meta description more useful and specific.")
    elif description_len > 160:
        issues.append(f"Meta description is long ({description_len} characters).")
        recommendations.append("Shorten the meta description and keep the strongest message near the start.")

    if not h1s:
        issues.append("Missing H1.")
        recommendations.append("Add one visible H1 aligned with the page's primary search intent.")
    elif len(h1s) > 1:
        issues.append(f"Multiple H1s found ({len(h1s)}).")
        recommendations.append("Use a single primary H1 and demote secondary headings to H2/H3.")

    if word_count < 300:
        issues.append(f"Low main content word count ({word_count} words).")
        recommendations.append("Expand the page with helpful, client-approved content that answers the query.")

    if not canonical:
        issues.append("Canonical URL not found.")
        recommendations.append("Add a self-referencing canonical unless another canonical target is intentional.")

    if not internal_links:
        issues.append("No internal links detected in extracted content.")
        recommendations.append("Add relevant internal links to important supporting or conversion pages.")

    if not issues:
        recommendations.append("No obvious technical content issues found in the extracted page data.")

    return issues, recommendations


def build_absolute_urls(base_url: str, paths_or_urls: list[str], limit: int | None = None) -> list[str]:
    validate_public_url(base_url)
    urls: list[str] = []
    seen: set[str] = set()
    for value in paths_or_urls:
        absolute = normalise_url(value, base_url)
        if not absolute or _path_is_guarded(urlparse(absolute).path):
            continue
        if absolute not in seen:
            seen.add(absolute)
            urls.append(absolute)
        if limit and len(urls) >= limit:
            break
    return urls
