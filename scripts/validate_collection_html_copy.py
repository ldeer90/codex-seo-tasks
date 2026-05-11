"""Validate final Shopify collection HTML copy against an approved brief."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from collection_seo_utils import read_json


ALLOWED_TAGS = {"h2", "h3", "p", "a", "strong", "em", "br"}
UNSUPPORTED_CLAIM_PATTERNS = [
    re.compile(r"\baustralian[- ]made\b", re.I),
    re.compile(r"\bmade in australia\b", re.I),
    re.compile(r"\bfree shipping\b", re.I),
    re.compile(r"\bsustainable\b|\beco[- ]friendly\b|\bethical\b", re.I),
    re.compile(r"\bguaranteed\b", re.I),
]


class CopyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.links: list[dict[str, str]] = []
        self.text_parts: list[str] = []
        self.errors: list[str] = []
        self._current_href = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        if tag not in ALLOWED_TAGS:
            self.errors.append(f"Tag <{tag}> is not allowed.")
        if tag == "a":
            attrs_dict = {key: value or "" for key, value in attrs}
            self._current_href = attrs_dict.get("href", "")
            if not self._current_href:
                self.errors.append("Anchor tag is missing href.")

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._current_href = ""

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        self.text_parts.append(text)
        if self._current_href:
            self.links.append({"href": self._current_href, "anchor": text})


def validate_html(*, briefs_json: Path, slug: str, html: Path) -> dict[str, Any]:
    payload = read_json(briefs_json, {})
    brief = _brief_for_slug(payload, slug)
    html_text = html.read_text()
    parser = CopyParser()
    parser.feed(html_text)

    blocking: list[dict[str, Any]] = []
    warning: list[dict[str, Any]] = []

    for error in parser.errors:
        blocking.append(_issue("invalid_html_tag", error))

    h2_count = parser.tags.count("h2")
    h3_count = parser.tags.count("h3")
    if h2_count != 1:
        blocking.append(_issue("invalid_h2_count", f"Expected exactly one <h2>; found {h2_count}."))
    if h3_count != 2:
        blocking.append(_issue("invalid_h3_count", f"Expected exactly two <h3>; found {h3_count}."))
    if "h1" in parser.tags:
        blocking.append(_issue("h1_not_allowed", "Final collection copy must not include <h1>."))

    text = " ".join(parser.text_parts)
    words = re.findall(r"\b[\w'-]+\b", text)
    primary = ((brief.get("keywords") or {}).get("primary") or {}).get("keyword", "")
    if primary and primary.lower() not in text.lower()[:350]:
        blocking.append(_issue("primary_keyword_not_near_start", "Primary keyword is not present near the opening copy."))

    for phrase in ((brief.get("content_recommendations") or {}).get("banned_phrases") or []):
        if phrase and phrase.lower() in text.lower():
            blocking.append(_issue("banned_phrase_used", f"Banned phrase used: {phrase}", phrase=phrase))

    approved_links = {
        str(link.get("target_url"))
        for link in brief.get("internal_links") or []
        if link.get("target_url")
    }
    for link in parser.links:
        if link["href"] not in approved_links:
            blocking.append(_issue("unapproved_internal_link", f"Unapproved link used: {link['href']}"))

    supported_text = json.dumps(brief, ensure_ascii=False).lower()
    for pattern in UNSUPPORTED_CLAIM_PATTERNS:
        match = pattern.search(text)
        if match and match.group(0).lower() not in supported_text:
            blocking.append(_issue(
                "unsupported_claim",
                f"Claim appears in draft but is not supported by the brief: {match.group(0)}",
                claim=match.group(0),
            ))

    min_words = _word_bound(brief, "min_words") or 220
    max_words = _word_bound(brief, "max_words") or 320
    if len(words) < min_words:
        warning.append(_issue(
            "short_copy",
            f"Copy is short at {len(words)} words; target minimum is {min_words}.",
        ))
    if len(words) > max_words:
        warning.append(_issue(
            "long_copy",
            f"Copy is long at {len(words)} words; target maximum is {max_words}.",
        ))

    min_links = _min_internal_links(brief)
    if len(parser.links) < min_links:
        message = f"Only {len(parser.links)} approved internal link(s) included; target minimum is {min_links}."
        if brief.get("require_internal_links") is True:
            blocking.append(_issue("missing_required_internal_links", message))
        else:
            warning.append(_issue("too_few_internal_links", message))

    return {
        "ok": not blocking,
        "summary": {
            "slug": slug,
            "word_count": len(words),
            "links": len(parser.links),
            "blocking_count": len(blocking),
            "warning_count": len(warning),
        },
        "blocking": blocking,
        "warning": warning,
    }


def _brief_for_slug(payload: dict[str, Any], slug: str) -> dict[str, Any]:
    for brief in payload.get("briefs") or []:
        if isinstance(brief, dict) and str(brief.get("slug")) == slug:
            return brief
    raise ValueError(f"Brief not found for slug: {slug}")


def _word_bound(brief: dict[str, Any], key: str) -> int:
    for source in (brief, brief.get("content_requirements") or {}, brief.get("structure") or {}):
        if isinstance(source, dict) and source.get(key):
            try:
                return int(source[key])
            except (TypeError, ValueError):
                return 0
    return 0


def _min_internal_links(brief: dict[str, Any]) -> int:
    for source in (brief, brief.get("content_requirements") or {}, brief.get("structure") or {}):
        if isinstance(source, dict) and source.get("min_internal_links") is not None:
            try:
                return max(0, int(source["min_internal_links"]))
            except (TypeError, ValueError):
                return 0
    if brief.get("internal_links"):
        return 1
    return 0


def _issue(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **details}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--briefs-json", required=True, type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = validate_html(briefs_json=args.briefs_json, slug=args.slug, html=args.html)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text)
        print(f"Wrote HTML copy validation to {args.output}")
    else:
        print(text)
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
