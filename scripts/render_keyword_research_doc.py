"""Render a deterministic Collection SEO keyword research document body."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from collection_seo_utils import (
    engine_pair_stats,
    included_collections,
    normalise_url,
    parse_seranking_keywords,
    read_json,
)


def render_doc(client: dict[str, Any], keywords: list[dict[str, Any]]) -> str:
    collections = included_collections(client)
    stats = engine_pair_stats(keywords)
    by_url: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for keyword in keywords:
        by_url[normalise_url(keyword.get("link"))].append(keyword)

    lines = [
        f"{client.get('client')} - Collection Keyword Research",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Market scope: {client.get('market_scope', 'AU')}",
        f"SE Ranking project: {client.get('se_ranking', {}).get('project_id', '')}",
        f"Live tracked keywords: {stats['keyword_count']}",
        f"Live keyword-engine pairs: {stats['pair_count']}",
        f"Collections covered: {len(collections)}",
        "",
        "Executive Summary",
        "",
        (
            "This document reconciles the collection SEO sidecar with live SE Ranking "
            "exports. It lists each SEO-priority collection, primary keyword, search "
            "volume, tracking coverage, and target URL."
        ),
        "",
        "Collection Coverage",
        "",
    ]

    for collection in collections:
        url = collection.get("url", "")
        live = sorted(k.get("name") or k.get("keyword") or "" for k in by_url.get(normalise_url(url), []))
        lines.extend([
            f"## {collection.get('slug', '').replace('-', ' ').title()}",
            f"URL: {url}",
            f"Class: {collection.get('class', '')}",
            f"Primary keyword: {collection.get('primary_keyword', '')}",
            f"AU monthly volume: {collection.get('au_volume', 0)}",
            f"US monthly volume: {collection.get('us_volume', '')}",
            f"Tracked keywords: {len(live)}",
        ])
        if live:
            lines.append("Keyword set:")
            lines.extend(f"- {name}" for name in live)
        else:
            lines.append("Keyword set: Not tracked in the supplied SE Ranking export.")
        lines.append("")

    warnings = client.get("qa", {}).get("last_validation", {}).get("warnings")
    if warnings:
        lines.extend(["Validation Notes", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--seranking-keywords-json", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    client = read_json(args.client_json, {})
    keywords = parse_seranking_keywords(read_json(args.seranking_keywords_json, []))
    text = render_doc(client, keywords)
    if args.output:
        args.output.write_text(text)
        print(f"Wrote keyword research doc body to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
