"""
Crawl Melani the Label collection pages and extract keyword signals.
Usage: python scripts/melani_collection_keywords.py
Credits used: ~1 per page crawled (free plan)
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

from seo_automation_mcp.firecrawl import FirecrawlClient  # noqa: E402


SITE_URL = "https://melanithelabel.com"
INCLUDE_PATHS = ["/collections/.*"]
CRAWL_LIMIT = 30


def extract_keywords_from_page(page: dict) -> dict:
    metadata = page.get("metadata", {})
    content = page.get("markdown", "") or ""
    url = metadata.get("sourceURL", "")

    # Collection slug → readable keyword
    slug = url.rstrip("/").split("/collections/")[-1].split("?")[0] if "/collections/" in url else ""
    slug_keyword = slug.replace("-", " ").strip()

    title = metadata.get("title", "").replace(" | Mélani the Label", "").replace(" | Melani the Label", "").strip()
    description = metadata.get("description", "").strip()
    og_title = metadata.get("og:title", "").replace(" | Mélani the Label", "").strip()

    # Extract H1 and H2s from markdown
    h1s = re.findall(r"^#\s+(.+)$", content, re.MULTILINE)
    h2s = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)

    # Word count
    word_count = len(content.split())

    return {
        "url": url,
        "slug_keyword": slug_keyword,
        "title": title,
        "og_title": og_title,
        "description": description,
        "h1": h1s[0] if h1s else "",
        "h2s": h2s[:5],
        "word_count": word_count,
    }


async def main():
    client = FirecrawlClient()

    print(f"Crawling {SITE_URL}/collections/* (limit {CRAWL_LIMIT} pages)...")
    result = await client.crawl_site(
        url=SITE_URL,
        limit=CRAWL_LIMIT,
        include_paths=INCLUDE_PATHS,
    )

    pages = result.get("data", [])
    credits = result.get("creditsUsed", "?")
    print(f"Crawl complete. Pages: {len(pages)}, Credits used: {credits}")

    rows = []
    for page in pages:
        data = page.get("data") or page
        extracted = extract_keywords_from_page(data)
        if extracted["slug_keyword"]:  # skip non-collection pages
            rows.append(extracted)

    # Sort by slug for readability
    rows.sort(key=lambda r: r["slug_keyword"])

    print(f"\n{'─'*80}")
    print(f"{'COLLECTION':<35} {'TITLE TAG':<35} {'WORD COUNT'}")
    print(f"{'─'*80}")
    for r in rows:
        slug = r["slug_keyword"][:34]
        title = (r["title"] or r["og_title"])[:34]
        print(f"{slug:<35} {title:<35} {r['word_count']}")

    print(f"\n{'─'*80}")
    print("H1s and descriptions per collection:\n")
    for r in rows:
        print(f"  [{r['slug_keyword']}]")
        if r["h1"]:
            print(f"    H1:   {r['h1']}")
        if r["description"]:
            print(f"    Meta: {r['description'][:120]}")
        if r["h2s"]:
            print(f"    H2s:  {', '.join(r['h2s'][:3])}")
        print()

    # Save raw output
    out_path = Path(__file__).parent.parent / "docs" / "melani-collections-crawl.json"
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"Raw data saved to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
