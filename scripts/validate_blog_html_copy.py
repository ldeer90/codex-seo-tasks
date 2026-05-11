"""Validate final Shopify blog HTML copy against an approved blog brief."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from collection_seo_utils import read_json


BASE_ALLOWED_TAGS = {"h2", "h3", "p", "a", "strong", "em", "br", "ul", "ol", "li", "blockquote"}
UNSUPPORTED_CLAIM_PATTERNS = [
    re.compile(r"\baustralian[- ]made\b", re.I),
    re.compile(r"\bmade in australia\b", re.I),
    re.compile(r"\bfree shipping\b", re.I),
    re.compile(r"\bsustainable\b|\beco[- ]friendly\b|\bethical\b", re.I),
    re.compile(r"\bguaranteed\b", re.I),
    re.compile(r"\bclinically proven\b|\bscientifically proven\b", re.I),
    re.compile(r"\b\d+%\b", re.I),
]


class BlogParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.links: list[dict[str, str]] = []
        self.text_parts: list[str] = []
        self.headings: list[dict[str, str]] = []
        self.errors: list[str] = []
        self._current_href = ""
        self._current_heading = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        if tag == "a":
            attrs_dict = {key: value or "" for key, value in attrs}
            self._current_href = attrs_dict.get("href", "")
            if not self._current_href:
                self.errors.append("Anchor tag is missing href.")
        if tag in {"h1", "h2", "h3", "h4"}:
            self._current_heading = tag

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._current_href = ""
        if tag == self._current_heading:
            self._current_heading = ""

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        self.text_parts.append(text)
        if self._current_href:
            self.links.append({"href": self._current_href, "anchor": text})
        if self._current_heading:
            self.headings.append({"tag": self._current_heading, "text": text})


def validate_blog_html(
    *,
    brief_json: Path,
    html: Path,
    slug: str | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    payload = read_json(brief_json, {})
    brief = _brief_for_target(payload, slug=slug, title=title)
    html_text = html.read_text()
    parser = BlogParser()
    parser.feed(html_text)

    blocking: list[dict[str, Any]] = []
    warning: list[dict[str, Any]] = []

    for error in parser.errors:
        blocking.append(_issue("invalid_anchor", error))

    structure = _structure(brief)
    allowed_tags = _allowed_tags(structure)
    if not allowed_tags:
        blocking.append(_issue(
            "missing_brief_defined_html_policy",
            "Blog brief must define allowed HTML tags before final copy can be validated.",
        ))
        allowed_tags = BASE_ALLOWED_TAGS
    for tag in parser.tags:
        if tag not in allowed_tags:
            blocking.append(_issue("disallowed_html_tag", f"Tag <{tag}> is not allowed by the brief.", tag=tag))

    required_headings = _required_headings(structure)
    if not required_headings:
        blocking.append(_issue(
            "missing_brief_defined_structure",
            "Blog brief must define required headings or an outline before final copy can be validated.",
        ))
    else:
        present = [_normalise_text(item["text"]) for item in parser.headings]
        for heading in required_headings:
            if _normalise_text(heading) not in present:
                blocking.append(_issue("missing_required_heading", f"Required heading is missing: {heading}", heading=heading))

    text = " ".join(parser.text_parts)
    words = re.findall(r"\b[\w'-]+\b", text)
    primary = _primary_keyword(brief)
    if primary and primary.lower() not in text.lower()[:500]:
        blocking.append(_issue("primary_keyword_not_near_start", "Primary keyword is not present near the opening copy."))
    if primary:
        count = _keyword_count(primary, text)
        density = count / max(1, len(words))
        if density > 0.04 and count >= 4:
            blocking.append(_issue("keyword_stuffing", f"Primary keyword density is too high: {density:.1%}.", keyword=primary))

    for phrase in _banned_phrases(brief):
        if phrase and phrase.lower() in text.lower():
            blocking.append(_issue("banned_phrase_used", f"Banned phrase used: {phrase}", phrase=phrase))

    approved_links = _approved_links(brief)
    for link in parser.links:
        if link["href"] not in approved_links:
            blocking.append(_issue("unapproved_link", f"Unapproved link used: {link['href']}", url=link["href"]))

    if _requires_sources(brief) and not any(_is_external(link["href"]) for link in parser.links):
        blocking.append(_issue("missing_required_source_link", "Brief requires source links, but no approved external/source link was included."))

    supported_text = json.dumps(brief, ensure_ascii=False).lower()
    for pattern in UNSUPPORTED_CLAIM_PATTERNS:
        for match in pattern.finditer(text):
            if match.group(0).lower() not in supported_text:
                blocking.append(_issue(
                    "unsupported_claim",
                    f"Claim appears in draft but is not supported by the brief: {match.group(0)}",
                    claim=match.group(0),
                ))

    min_words = _word_bound(brief, "min_words")
    max_words = _word_bound(brief, "max_words")
    if min_words and len(words) < min_words:
        warning.append(_issue("short_copy", f"Copy is short at {len(words)} words; brief target minimum is {min_words}."))
    if max_words and len(words) > max_words:
        warning.append(_issue("long_copy", f"Copy is long at {len(words)} words; brief target maximum is {max_words}."))
    if not parser.links:
        warning.append(_issue("no_links", "No approved links were included."))

    return {
        "ok": not blocking,
        "summary": {
            "slug": brief.get("slug") or slug or "",
            "title": brief.get("title") or title or "",
            "word_count": len(words),
            "links": len(parser.links),
            "blocking_count": len(blocking),
            "warning_count": len(warning),
        },
        "blocking": blocking,
        "warning": warning,
    }


def _brief_for_target(payload: dict[str, Any], *, slug: str | None, title: str | None) -> dict[str, Any]:
    if slug and isinstance(payload.get("by_slug"), dict) and isinstance(payload["by_slug"].get(slug), dict):
        return payload["by_slug"][slug]
    candidates: list[Any] = []
    for key in ("briefs", "blogs", "articles"):
        if isinstance(payload.get(key), list):
            candidates.extend(payload[key])
    if isinstance(payload.get("brief"), dict):
        candidates.append(payload["brief"])
    if not candidates and any(key in payload for key in ("slug", "title", "keywords", "primary_keyword")):
        candidates.append(payload)
    for brief in candidates:
        if not isinstance(brief, dict):
            continue
        if slug and str(brief.get("slug")) == slug:
            return brief
        brief_title = str(brief.get("title") or brief.get("article_title") or "")
        if title and _normalise_text(brief_title) == _normalise_text(title):
            return brief
    target = slug or title or "<unspecified>"
    raise ValueError(f"Blog brief not found for target: {target}")


def _structure(brief: dict[str, Any]) -> dict[str, Any]:
    for key in ("html_policy", "html_structure", "structure", "content_structure"):
        value = brief.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _allowed_tags(structure: dict[str, Any]) -> set[str]:
    raw = structure.get("allowed_tags") or structure.get("allowed_html_tags")
    if not isinstance(raw, list):
        return set()
    return {str(tag).lower().strip("<> ") for tag in raw if str(tag).strip()}


def _required_headings(structure: dict[str, Any]) -> list[str]:
    raw = structure.get("required_headings") or structure.get("heading_outline") or structure.get("outline")
    if not isinstance(raw, list):
        return []
    headings: list[str] = []
    for item in raw:
        if isinstance(item, str):
            headings.append(item)
        elif isinstance(item, dict):
            value = item.get("heading") or item.get("text") or item.get("title")
            if value:
                headings.append(str(value))
    return headings


def _primary_keyword(brief: dict[str, Any]) -> str:
    keywords = brief.get("keywords") or {}
    primary = keywords.get("primary") if isinstance(keywords, dict) else None
    if isinstance(primary, dict):
        return str(primary.get("keyword") or primary.get("query") or "").strip()
    if isinstance(primary, str):
        return primary.strip()
    return str(brief.get("primary_keyword") or "").strip()


def _banned_phrases(brief: dict[str, Any]) -> list[str]:
    phrases: list[str] = []
    for source in (brief, brief.get("content_recommendations") or {}, brief.get("style_rules") or {}):
        raw = source.get("banned_phrases") if isinstance(source, dict) else None
        if isinstance(raw, list):
            phrases.extend(str(item) for item in raw if str(item).strip())
    return phrases


def _approved_links(brief: dict[str, Any]) -> set[str]:
    links: set[str] = set()
    fields = (
        brief.get("internal_links") or [],
        brief.get("approved_links") or [],
        brief.get("approved_external_links") or [],
        brief.get("sources") or [],
    )
    for rows in fields:
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, str):
                links.add(row)
            elif isinstance(row, dict):
                for key in ("target_url", "url", "href", "source_url"):
                    if row.get(key):
                        links.add(str(row[key]))
    return links


def _requires_sources(brief: dict[str, Any]) -> bool:
    if brief.get("requires_sources") is True:
        return True
    requirements = brief.get("source_requirements")
    if isinstance(requirements, dict):
        return bool(requirements.get("required"))
    return False


def _word_bound(brief: dict[str, Any], key: str) -> int:
    for source in (brief, brief.get("content_requirements") or {}, brief.get("structure") or {}):
        if isinstance(source, dict) and source.get(key):
            try:
                return int(source[key])
            except (TypeError, ValueError):
                return 0
    return 0


def _is_external(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def _keyword_count(keyword: str, text: str) -> int:
    return len(re.findall(rf"\b{re.escape(keyword.lower())}\b", text.lower()))


def _normalise_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _issue(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **details}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief-json", required=True, type=Path)
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--slug")
    parser.add_argument("--title")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.slug and not args.title:
        raise SystemExit("Pass --slug or --title.")

    result = validate_blog_html(brief_json=args.brief_json, slug=args.slug, title=args.title, html=args.html)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text)
        print(f"Wrote blog HTML validation to {args.output}")
    else:
        print(text)
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
