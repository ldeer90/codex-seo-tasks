"""Score sitemap-derived internal link candidates for a Shopify blog brief.

Agents fetch or export collection/blog sitemap URLs, save them to JSON/XML, then
run this helper before drafting. The output is a shortlist for Codex judgement,
not a final link plan.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from collection_seo_utils import read_json


STOP_WORDS = {
    "a", "an", "and", "are", "article", "blog", "blogs", "buy", "for", "from",
    "guide", "ideas", "in", "of", "on", "online",
    "shop", "the", "to", "with", "your",
}
UTILITY_PATTERNS = (
    "/account", "/cart", "/checkout", "/policies/", "/search", "/pages/contact",
    "/pages/privacy", "/pages/refund", "/pages/terms",
)


def build_candidates(
    *,
    brief_json: Path,
    collections_sitemap: Path,
    blogs_sitemap: Path | None = None,
    slug: str | None = None,
    title: str | None = None,
    collection_limit: int = 8,
    blog_limit: int = 5,
) -> dict[str, Any]:
    payload = read_json(brief_json, {}) if brief_json.suffix.lower() == ".json" else {}
    brief = _brief_for_target(payload, slug=slug, title=title)
    topic_text = _topic_text(brief)
    collection_entries = _load_entries(collections_sitemap, target_type="collection")
    blog_entries = _load_entries(blogs_sitemap, target_type="blog") if blogs_sitemap else []
    current_url = str(brief.get("url") or brief.get("canonical_url") or "")

    collections = _score_entries(collection_entries, topic_text, brief, "collection", current_url)
    blogs = _score_entries(blog_entries, topic_text, brief, "blog", current_url)

    result = {
        "ok": bool(collections[: min(collection_limit, 5)]),
        "summary": {
            "slug": brief.get("slug") or slug or "",
            "title": brief.get("title") or title or "",
            "collection_candidates": len(collections),
            "blog_candidates": len(blogs),
            "recommended_collection_links": min(len(collections), 5),
            "recommended_blog_links": min(len(blogs), blog_limit),
        },
        "collection_links": collections[:collection_limit],
        "blog_links": blogs[:blog_limit],
        "warning": [],
    }
    if not collections:
        result["warning"].append(_issue(
            "no_collection_candidates",
            "No collection links were selected from the sitemap export.",
        ))
    elif len(collections) < 5:
        result["warning"].append(_issue(
            "fewer_than_five_collection_candidates",
            f"Only {len(collections)} collection candidates were selected.",
        ))
    return result


def _score_entries(
    entries: list[dict[str, Any]],
    topic_text: str,
    brief: dict[str, Any],
    target_type: str,
    current_url: str,
) -> list[dict[str, Any]]:
    topic_tokens = _tokens(topic_text)
    primary = _primary_keyword(brief)
    scored = []
    for entry in entries:
        url = str(entry.get("url") or "")
        if not url or _is_utility(url) or _same_url(url, current_url):
            continue
        text = " ".join([str(entry.get("title") or ""), _slug_text(url)])
        entry_tokens = _tokens(text)
        overlap = topic_tokens & entry_tokens
        if not overlap and target_type == "blog":
            continue
        score = float(len(overlap) * 12)
        reasons = []
        if overlap:
            reasons.append(f"topic overlap: {', '.join(sorted(overlap))}")
        if target_type == "collection":
            score += 18
            reasons.append("commercial collection target")
        else:
            score += 8
            reasons.append("supporting editorial target")
        if primary and primary in text.lower():
            score += 10
            reasons.append("matches primary keyword language")
        milestone = _milestone_boost(topic_text, text)
        if milestone:
            score += milestone
            reasons.append("matches milestone birthday angle")
        if any(word in url for word in ("birthday", "gift", "hampers")):
            score += 6
            reasons.append("URL confirms gifting relevance")
        score += math.log10(max(10, len(url))) / 4
        if score < 12:
            continue
        scored.append({
            "target_type": target_type,
            "target_url": url,
            "target_title": entry.get("title") or _title_from_url(url),
            "suggested_anchor": _anchor(entry, topic_tokens),
            "placement_idea": _placement_idea(entry, target_type, topic_text),
            "rationale": "; ".join(reasons),
            "confidence": "high" if score >= 40 else "medium" if score >= 25 else "low",
            "score": round(score, 2),
        })
    scored.sort(key=lambda row: (-float(row["score"]), row["target_url"]))
    return scored


def _load_entries(path: Path | None, *, target_type: str) -> list[dict[str, Any]]:
    if not path:
        return []
    if path.suffix.lower() in {".xml", ".txt"}:
        text = path.read_text(errors="ignore")
        urls = re.findall(r"<loc>\s*([^<]+)\s*</loc>", text) or [line.strip() for line in text.splitlines()]
        return [_entry_from_url(url, target_type) for url in urls if _matches_type(url, target_type)]
    raw = read_json(path, {})
    rows = _extract_rows(raw, target_type)
    entries = []
    for row in rows:
        if isinstance(row, str):
            entries.append(_entry_from_url(row, target_type))
        elif isinstance(row, dict):
            url = str(row.get("url") or row.get("loc") or row.get("link") or "")
            if _matches_type(url, target_type):
                entries.append({
                    "url": url,
                    "title": row.get("title") or row.get("name") or _title_from_url(url),
                })
    return entries


def _extract_rows(raw: Any, target_type: str) -> list[Any]:
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, dict):
        return []
    keys = [f"{target_type}s", target_type, "urls", "items", "data"]
    for key in keys:
        value = raw.get(key)
        if isinstance(value, list):
            return value
    return []


def _entry_from_url(url: str, target_type: str) -> dict[str, str]:
    return {"url": url.strip(), "title": _title_from_url(url), "target_type": target_type}


def _matches_type(url: str, target_type: str) -> bool:
    if target_type == "collection":
        return "/collections/" in url
    return "/blogs/" in url


def _brief_for_target(payload: dict[str, Any], *, slug: str | None, title: str | None) -> dict[str, Any]:
    candidates: list[Any] = []
    if slug and isinstance(payload.get("by_slug"), dict) and isinstance(payload["by_slug"].get(slug), dict):
        return payload["by_slug"][slug]
    for key in ("briefs", "blogs", "articles"):
        if isinstance(payload.get(key), list):
            candidates.extend(payload[key])
    if isinstance(payload.get("brief"), dict):
        candidates.append(payload["brief"])
    if not candidates and payload:
        candidates.append(payload)
    for brief in candidates:
        if not isinstance(brief, dict):
            continue
        if slug and str(brief.get("slug")) == slug:
            return brief
        if title and _normalise(str(brief.get("title") or brief.get("article_title") or "")) == _normalise(title):
            return brief
    raise ValueError(f"Brief not found for slug/title: {slug or title}")


def _topic_text(brief: dict[str, Any]) -> str:
    keywords = brief.get("keywords") or {}
    pieces = [
        brief.get("title"),
        brief.get("article_title"),
        brief.get("slug"),
        brief.get("audience"),
        brief.get("intent"),
        _primary_keyword(brief),
    ]
    if isinstance(keywords, dict):
        secondary = keywords.get("secondary") or keywords.get("supplemental") or []
        for row in secondary:
            if isinstance(row, dict):
                pieces.append(row.get("keyword") or row.get("query"))
            elif isinstance(row, str):
                pieces.append(row)
    structure = brief.get("html_policy") or brief.get("structure") or {}
    for heading in structure.get("required_headings") or structure.get("outline") or []:
        if isinstance(heading, dict):
            pieces.append(heading.get("heading") or heading.get("title") or heading.get("text"))
        else:
            pieces.append(heading)
    return " ".join(str(piece) for piece in pieces if piece)


def _primary_keyword(brief: dict[str, Any]) -> str:
    keywords = brief.get("keywords") or {}
    primary = keywords.get("primary") if isinstance(keywords, dict) else None
    if isinstance(primary, dict):
        return str(primary.get("keyword") or primary.get("query") or "").lower()
    if isinstance(primary, str):
        return primary.lower()
    return str(brief.get("primary_keyword") or "").lower()


def _tokens(*values: str) -> set[str]:
    text = " ".join(values).lower()
    return {
        token for token in re.findall(r"[a-z0-9]+", text)
        if len(token) > 2 and token not in STOP_WORDS
    }


def _title_from_url(url: str) -> str:
    slug = _slug_text(url)
    return " ".join(part.capitalize() for part in slug.split())


def _slug_text(url: str) -> str:
    path = url.split("?", 1)[0].rstrip("/")
    slug = path.rsplit("/", 1)[-1]
    return re.sub(r"[-_]+", " ", slug)


def _anchor(entry: dict[str, Any], topic_tokens: set[str]) -> str:
    title = str(entry.get("title") or "").strip()
    if title:
        title = re.sub(r"\s*&\s*Gift Baskets.*$", "", title, flags=re.I)
        title = re.sub(r"\s*\|\s*.*$", "", title).strip()
    if title and len(title) <= 60:
        return title
    slug = _slug_text(str(entry.get("url") or ""))
    tokens = [part for part in slug.split() if part not in STOP_WORDS]
    if tokens:
        if topic_tokens & set(tokens):
            return " ".join(tokens[:5])
        return " ".join(tokens[:4])
    return "related guide"


def _placement_idea(entry: dict[str, Any], target_type: str, topic_text: str) -> str:
    anchor = _anchor(entry, _tokens(topic_text))
    if target_type == "collection":
        return f"Use where the article recommends a specific shopping path, with '{anchor}' as the natural next step."
    return f"Use as a supporting read where the article expands on '{anchor}' without distracting from the main CTA."


def _milestone_boost(topic_text: str, target_text: str) -> float:
    boost = 0.0
    for age in ("16", "18", "21", "30", "40", "50", "60", "70", "80"):
        if age in topic_text and age in target_text:
            boost += 8
    if "milestone" in topic_text.lower() and "birthday" in target_text.lower():
        boost += 4
    return boost


def _is_utility(url: str) -> bool:
    lower = url.lower()
    return any(pattern in lower for pattern in UTILITY_PATTERNS)


def _same_url(left: str, right: str) -> bool:
    return bool(left and right and left.rstrip("/") == right.rstrip("/"))


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _issue(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **details}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief-json", required=True, type=Path)
    parser.add_argument("--collections-sitemap", required=True, type=Path)
    parser.add_argument("--blogs-sitemap", type=Path)
    parser.add_argument("--slug")
    parser.add_argument("--title")
    parser.add_argument("--collection-limit", type=int, default=8)
    parser.add_argument("--blog-limit", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.slug and not args.title:
        raise SystemExit("Pass --slug or --title.")
    result = build_candidates(
        brief_json=args.brief_json,
        collections_sitemap=args.collections_sitemap,
        blogs_sitemap=args.blogs_sitemap,
        slug=args.slug,
        title=args.title,
        collection_limit=args.collection_limit,
        blog_limit=args.blog_limit,
    )
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text)
        print(f"Wrote blog internal link candidates to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
