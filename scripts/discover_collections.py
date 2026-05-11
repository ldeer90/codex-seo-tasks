"""Discover and classify Shopify collections for SEO prioritisation.

Pulls the sitemap, drops promo/utility slugs, fetches `/collections/<slug>/products.json`
in parallel for every survivor, and classifies each by product_type concentration.

Output: a list of dicts ready to drop into client.json[collections].

Usage:
    python scripts/discover_collections.py --domain melanithelabel.com --output /tmp/melani-collections.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from collections import Counter
from pathlib import Path
from typing import Literal

import httpx

ClassLabel = Literal["pure_category", "themed_category", "curated_edit", "style_edit", "empty"]

# Pass A: drop these immediately
DROP_PATTERNS = [
    r"-?sale($|-)", r"-2024", r"-2025", r"-2026",
    r"^eofy", r"^black-friday", r"^boxing-day",
    r"^coming-soon$", r"^back-in-stock$", r"^frontpage$",
    r"^the-latest$", r"^most-popular$", r"^new-arrivals$", r"^pre-order$",
    r"-edit$", r"-style$", r"-signatures$",
    r"^ombre$", r"-ombre$", r"^plum-", r"^chartreuse-", r"^unbound$",
    r"-collection$", r"-offer$", r"-nav-", r"^style-",
    r"^further-", r"^\d", r"-\d{2,}$", r"-\d{2,}-", r"\d{2,}$",  # promos / numbered slugs / year suffixes
    r"-1$",  # duplicate slug suffix (e.g. dresses-1)
]

# Promo/colour singletons (no clear category intent)
SINGLE_TOKEN_NON_CATEGORIES = {
    "frontpage", "ombre", "tailored", "resort",  # tailored/resort kept but flagged
}


def discover_sitemap_collections(domain: str) -> list[str]:
    base = f"https://{domain}"
    idx = httpx.get(f"{base}/sitemap.xml", follow_redirects=True, timeout=20).text
    submaps = re.findall(r"<loc>([^<]*sitemap_collections[^<]*)</loc>", idx)
    submaps = [s.replace("&amp;", "&") for s in submaps]
    if not submaps:
        # Some shops put collections directly in sitemap.xml
        return _filter_collections(re.findall(r"<loc>([^<]+)</loc>", idx))
    urls = []
    for sm in submaps:
        text = httpx.get(sm, follow_redirects=True, timeout=20).text
        urls.extend(re.findall(r"<loc>([^<]+)</loc>", text))
    return _filter_collections(urls)


def _filter_collections(urls: list[str]) -> list[str]:
    out = []
    for u in urls:
        if "/collections/" not in u:
            continue
        slug = u.rstrip("/").split("/collections/")[-1]
        if "/" in slug:  # nested e.g. /collections/x/products/y
            continue
        if slug.startswith("style-"):
            continue
        if any(re.search(p, slug) for p in DROP_PATTERNS):
            continue
        out.append(slug)
    # de-dupe preserving order
    seen = set()
    return [s for s in out if not (s in seen or seen.add(s))]


async def probe_collection(client: httpx.AsyncClient, domain: str, slug: str) -> dict:
    url = f"https://{domain}/collections/{slug}/products.json?limit=10"
    try:
        r = await client.get(url, timeout=10, follow_redirects=True)
        if r.status_code != 200:
            return {"slug": slug, "error": f"HTTP {r.status_code}"}
        products = r.json().get("products", [])
        types = [p.get("product_type", "") for p in products]
        type_counter = Counter(t for t in types if t)
        return {
            "slug": slug,
            "url": f"https://{domain}/collections/{slug}",
            "product_count_sample": len(products),
            "product_types": dict(type_counter),
            "sample_titles": [p.get("title", "")[:60] for p in products[:5]],
        }
    except Exception as e:
        return {"slug": slug, "error": str(e)}


def classify(probe: dict) -> ClassLabel:
    if "error" in probe:
        return "empty"
    n = probe["product_count_sample"]
    if n == 0:
        return "empty"
    types = probe["product_types"]
    total_typed = sum(types.values())
    if total_typed == 0:
        return "curated_edit"
    top_type, top_count = max(types.items(), key=lambda kv: kv[1])
    concentration = top_count / total_typed
    if concentration >= 0.8:
        probe["dominant_product_type"] = top_type
        return "pure_category"
    if len(types) <= 3 and concentration >= 0.5:
        probe["dominant_product_type"] = top_type
        return "themed_category"
    return "curated_edit"


# Heuristic primary-keyword guess from slug + dominant type
SLUG_TO_KEYWORD = {
    "maxis": "maxi dress",
    "minis": "mini dress",
    "midis": "midi dress",
    "gowns": "formal dresses",
    "dresses": "womens dresses",
    "all-dresses": "womens dresses",
    "long-sleeve": "long sleeve dress",
    "long-sleeve-tops": "long sleeve top",
    "crop-tops": "crop top",
    "tops": "going out tops",
    "bodysuit": "bodysuit",
    "lace-dresses": "lace dress",
    "lace-tops": "lace top",
    "printed-dresses": "printed dress",
    "printed-tops": "printed top",
    "sets": "two piece set",
    "jumpsuits": "jumpsuit",
    "skirt": "skirt",
    "skirts": "skirt",
    "mini-skirts": "mini skirt",
    "midi-skirts": "midi skirt",
    "maxi-skirts": "maxi skirt",
    "pants": "womens pants",
    "bridal": "bridal dress",
    "swim": "swimwear",
    "accessories": "womens accessories",
    "outerwear-collection": "womens outerwear",
    "outerwear": "womens outerwear",
    "tailored": "tailored clothing",
    "resort": "resort wear",
}


def primary_keyword_for(slug: str, dominant_type: str | None) -> str:
    if slug in SLUG_TO_KEYWORD:
        return SLUG_TO_KEYWORD[slug]
    base = slug.replace("-", " ")
    if dominant_type:
        return f"{base} {dominant_type.lower()}".strip()
    return base


async def run(domain: str) -> list[dict]:
    slugs = discover_sitemap_collections(domain)
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(probe_collection(client, domain, s) for s in slugs))
    classified = []
    for probe in results:
        cls = classify(probe)
        slug = probe["slug"]
        entry = {
            "slug": slug,
            "url": probe.get("url", f"https://{domain}/collections/{slug}"),
            "class": cls,
            "dominant_product_type": probe.get("dominant_product_type"),
            "product_count_sample": probe.get("product_count_sample", 0),
            "sample_product_titles": probe.get("sample_titles", []),
            "primary_keyword": primary_keyword_for(slug, probe.get("dominant_product_type")),
        }
        if "error" in probe:
            entry["error"] = probe["error"]
        classified.append(entry)
    return classified


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    collections = asyncio.run(run(args.domain))
    args.output.write_text(json.dumps(collections, indent=2))
    summary = Counter(c["class"] for c in collections)
    print(f"\nDiscovered {len(collections)} collections after filter:")
    for cls, n in summary.items():
        print(f"  {cls}: {n}")
    print(f"\nWrote → {args.output}")


if __name__ == "__main__":
    main()
