"""Sync Collection SEO sidecar fields from offline MCP exports."""

from __future__ import annotations

import argparse
import copy
import json
from datetime import date
from pathlib import Path
from typing import Any

from collection_seo_utils import (
    coverage_label,
    engine_pair_stats,
    included_collections,
    keyword_names_for_url,
    page_state_by_slug,
    parse_seranking_keywords,
    parse_volume_map,
    read_json,
)


def sync_sidecar(
    *,
    client_json: Path,
    seranking_keywords_json: Path,
    volume_json_au: Path,
    volume_json_us: Path | None = None,
    pages_json: Path | None = None,
) -> dict[str, Any]:
    client = copy.deepcopy(read_json(client_json, {}))
    keywords = parse_seranking_keywords(read_json(seranking_keywords_json, []))
    au_volumes = parse_volume_map(read_json(volume_json_au, {}))
    us_volumes = parse_volume_map(read_json(volume_json_us, {}) if volume_json_us else {})
    pages = page_state_by_slug(read_json(pages_json, {}) if pages_json else {})
    today = date.today().isoformat()

    stats = engine_pair_stats(keywords)
    client.setdefault("se_ranking", {})["keyword_count"] = stats["keyword_count"]
    client.setdefault("se_ranking", {})["pair_count"] = stats["pair_count"]
    client["se_ranking"]["last_synced"] = today

    included = included_collections(client)
    included_slugs = {c.get("slug") for c in included}
    covered = 0

    for collection in client.get("collections", []):
        slug = collection.get("slug")
        if slug not in included_slugs:
            continue
        names = keyword_names_for_url(keywords, collection.get("url", ""))
        collection["tracked_keywords"] = sorted(names)
        collection["tracked_keyword_count"] = len(names)
        if names:
            covered += 1

        primary = str(collection.get("primary_keyword", "")).lower().strip()
        if primary:
            if primary in au_volumes:
                collection["au_volume"] = au_volumes[primary]
            if us_volumes and primary in us_volumes:
                collection["us_volume"] = us_volumes[primary]

        page = pages.get(str(slug), {})
        if page:
            title = page.get("title") or page.get("current_title")
            h1 = page.get("h1") or page.get("current_h1")
            meta = page.get("meta_description") or page.get("description")
            if title:
                collection["current_title"] = title
            if h1:
                collection["current_h1"] = h1
            if meta:
                collection["current_meta_description"] = meta
            collection["last_scraped"] = today

    deliverables = client.setdefault("deliverables", {})
    keyword_sheet = deliverables.setdefault("keyword_research_sheet", {})
    keyword_sheet["coverage"] = coverage_label(covered, len(included))
    keyword_sheet["updated"] = today
    metadata_sheet = deliverables.get("metadata_suggestions_sheet")
    if isinstance(metadata_sheet, dict):
        metadata_sheet["coverage"] = coverage_label(covered, len(included))

    client.setdefault("qa", {})["last_sidecar_sync"] = {
        "date": today,
        "live_keyword_count": stats["keyword_count"],
        "live_pair_count": stats["pair_count"],
        "collections_with_live_keywords": covered,
        "included_collections": len(included),
    }
    return client


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--seranking-keywords-json", required=True, type=Path)
    parser.add_argument("--volume-json-au", required=True, type=Path)
    parser.add_argument("--volume-json-us", type=Path)
    parser.add_argument("--pages-json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    synced = sync_sidecar(
        client_json=args.client_json,
        seranking_keywords_json=args.seranking_keywords_json,
        volume_json_au=args.volume_json_au,
        volume_json_us=args.volume_json_us,
        pages_json=args.pages_json,
    )
    text = json.dumps(synced, indent=2)
    if args.output:
        args.output.write_text(text)
        print(f"Wrote synced sidecar to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
