"""Score sitemap-derived internal link candidates for a Shopify collection brief.

This is the collection-page counterpart to build_blog_internal_link_candidates.py.
It keeps final link selection in Codex judgement, but prevents collection copy
from being drafted with an empty internal-link plan when a sitemap is available.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from build_blog_internal_link_candidates import build_candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief-json", required=True, type=Path)
    parser.add_argument("--collections-sitemap", required=True, type=Path)
    parser.add_argument("--slug")
    parser.add_argument("--title")
    parser.add_argument("--collection-limit", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.slug and not args.title:
        raise SystemExit("Pass --slug or --title.")

    result = build_candidates(
        brief_json=args.brief_json,
        collections_sitemap=args.collections_sitemap,
        blogs_sitemap=None,
        slug=args.slug,
        title=args.title,
        collection_limit=1000,
        blog_limit=0,
    )
    result["collection_links"] = _rerank_collection_links(
        result.get("collection_links") or [],
        topic_text=_topic_text(args.brief_json, slug=args.slug, title=args.title),
    )[: args.collection_limit]
    result["summary"]["recommended_collection_links"] = min(
        result["summary"].get("collection_candidates", 0),
        4,
    )
    result["blog_links"] = []
    result["summary"]["recommended_blog_links"] = 0
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text)
        print(f"Wrote collection internal link candidates to {args.output}")
    else:
        print(text)


def _topic_text(brief_json: Path, *, slug: str | None, title: str | None) -> str:
    payload = json.loads(brief_json.read_text())
    candidates = payload.get("briefs") or [payload]
    for brief in candidates:
        if not isinstance(brief, dict):
            continue
        if slug and brief.get("slug") != slug:
            continue
        if title and str(brief.get("title", "")).lower() != title.lower():
            continue
        keywords = brief.get("keywords") or {}
        primary = keywords.get("primary") if isinstance(keywords, dict) else None
        primary_text = primary.get("keyword") if isinstance(primary, dict) else primary
        supplemental = keywords.get("supplemental") if isinstance(keywords, dict) else []
        return " ".join(
            str(part)
            for part in [
                brief.get("slug"),
                brief.get("title"),
                brief.get("intent"),
                brief.get("audience"),
                primary_text,
                " ".join(str(item) for item in supplemental or []),
            ]
            if part
        ).lower()
    return " ".join(part for part in (slug or "", title or "") if part).lower()


def _rerank_collection_links(links: list[dict], *, topic_text: str) -> list[dict]:
    recipient_male = bool(re.search(r"\b(men|mens|him|dad|father|brother|husband|male)\b", topic_text))
    christmas_topic = "christmas" in topic_text
    corporate_topic = "corporate" in topic_text
    friend_topic = "friend" in topic_text
    baby_topic = "baby" in topic_text or "parent" in topic_text

    for link in links:
        text = f"{link.get('target_url', '')} {link.get('target_title', '')}".lower()
        adjustment = 0.0
        if recipient_male and any(term in text for term in (
            "beer", "wine", "whiskey", "gin", "alcohol", "coffee", "dad", "father", "brother",
            "self-care", "care-package", "birthday",
        )):
            adjustment += 18
        if recipient_male and any(term in text for term in ("for-her", "mum", "mother", "bridesmaid")):
            adjustment -= 20
        if "christmas" in text and not christmas_topic:
            adjustment -= 18
        if "corporate" in text and not corporate_topic:
            adjustment -= 12
        if "friend" in text and not friend_topic:
            adjustment -= 10
        if any(term in text for term in ("baby", "parent")) and not baby_topic:
            adjustment -= 14
        link["score"] = round(float(link.get("score") or 0) + adjustment, 2)
        if adjustment:
            rationale = link.get("rationale", "")
            link["rationale"] = f"{rationale}; collection-specific adjustment {adjustment:+.0f}".strip("; ")
    return sorted(links, key=lambda row: (-float(row.get("score") or 0), row.get("target_url", "")))


if __name__ == "__main__":
    main()
