"""Generate title tag, H1, and meta description suggestions for collection pages.

Inputs:
  --client-json  path to docs/agent/clients/<client>.json
  --serp-json    competitor SERP scrape (from competitor-keyword-research workflow)
  --pages-json   client current-pages scrape (slug → {title, h1, meta_description})
  --output       CSV path

Pure functions (build_title, build_h1, build_meta, score_status) are importable
for unit tests and reuse from other workflow runners.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Literal

from collection_seo_utils import included_collections, page_state_by_slug

Status = Literal["New", "Tweak", "OK", "Missing H1"]

PIPE = " | "
EM_DASH = "–"


def _title_case_keyword(keyword: str) -> str:
    title = " ".join(w.capitalize() for w in keyword.split())
    return title.replace("Womens ", "Women's ")


def build_h1(keyword: str) -> str:
    """Title-cased primary keyword as the H1.

    The H1 stays close to the raw keyword so Google's keyword-to-page mapping
    is unambiguous. Pluralisation handling: most fashion category keywords are
    already plural (`maxi dress` → `Maxi Dresses`).
    """
    base = _title_case_keyword(keyword)
    # Smart plural for common category nouns
    singular_to_plural = {
        "Dress": "Dresses",
        "Top": "Tops",
        "Skirt": "Skirts",
        "Jumpsuit": "Jumpsuits",
        "Set": "Sets",
        "Pant": "Pants",
        "Bodysuit": "Bodysuits",
        "Gown": "Gowns",
    }
    words = base.split()
    if words and words[-1] in singular_to_plural:
        words[-1] = singular_to_plural[words[-1]]
    return " ".join(words)


def build_title(
    keyword: str,
    brand: str,
    descriptor: str | None = None,
    *,
    max_len: int = 60,
) -> str:
    """Construct a title-tag suggestion: `<H1> | <Descriptor> | <Brand>`.

    Descriptor is dropped automatically if the result would exceed max_len.
    """
    h1 = build_h1(keyword)
    full = f"{h1}{PIPE}{descriptor}{PIPE}{brand}" if descriptor else f"{h1}{PIPE}{brand}"
    if len(full) <= max_len:
        return full
    # Drop descriptor if too long
    bare = f"{h1}{PIPE}{brand}"
    return bare


def build_meta(
    keyword: str,
    brand: str,
    usp: str = "",
    serp_angle: str | None = None,
    *,
    max_len: int = 155,
) -> str:
    """Construct a meta description ending with a soft CTA."""
    h1 = build_h1(keyword)
    verified_usp = (usp or "").strip().rstrip(".")
    angle = _safe_serp_angle(serp_angle)
    parts = [f"Shop {h1.lower()} at {brand}."]
    if verified_usp:
        parts.append(f"{verified_usp}.")
    if angle:
        parts.append(f"Find styles for {angle}.")
    parts.append("Browse the collection.")
    candidate = " ".join(parts)
    if len(candidate) <= max_len:
        return candidate
    # Trim USP if needed
    fallback = f"Shop {h1.lower()} at {brand}. Browse the range."
    return fallback[:max_len]


def score_status(
    current_title: str | None,
    current_h1: str | None,
    primary_keyword: str,
    brand: str,
    *,
    max_len: int = 60,
) -> Status:
    """Classify a current-on-page state.

    Order of checks matters: missing H1 dominates, then keyword presence,
    then formatting (separator/brand casing/length).
    """
    if not current_h1 or current_h1.strip() == "":
        return "Missing H1"
    title = (current_title or "").lower()
    if primary_keyword.lower() not in title:
        return "New"
    bad_separator = EM_DASH in (current_title or "")
    wrong_brand_case = brand.lower() in title and brand not in (current_title or "")
    too_long = len(current_title or "") > max_len
    if bad_separator or wrong_brand_case or too_long:
        return "Tweak"
    return "OK"


def pick_top_competitor_titles(serp_json: Any, slug: str, n: int = 3) -> list[str]:
    """Pull the top-N competitor title tags for a given collection slug.

    Prefer the structured shape saved by the current workflow:
    `{slug: {"serp_results": [{"title": ...}]}}`.

    Legacy flat lists are still supported, but only as a fallback for old
    cached Melani data.
    """
    if isinstance(serp_json, dict):
        entry = serp_json.get(slug) or {}
        if not isinstance(entry, dict):
            return []
        results = entry.get("serp_results") or []
        if not isinstance(results, list):
            return []
        return [_clean_title(r.get("title")) for r in results if _clean_title(r.get("title"))][:n]

    if not isinstance(serp_json, list):
        return []

    needles = [slug, slug.rstrip("s"), slug.replace("-", " ")]
    matches = []
    for entry in serp_json:
        if not isinstance(entry, dict):
            continue
        url = (entry.get("url") or "").lower()
        title = _clean_title(entry.get("title"))
        if not title:
            continue
        if any(n in url for n in needles):
            matches.append(title)
        if len(matches) >= n:
            break
    return matches


def serp_entry_for_slug(serp_json: Any, slug: str) -> dict[str, Any]:
    if not isinstance(serp_json, dict):
        return {}
    entry = serp_json.get(slug)
    return entry if isinstance(entry, dict) else {}


def _clean_title(title: Any) -> str:
    text = re.sub(r"\s+", " ", str(title or "")).strip()
    if not text or "404" in text.lower():
        return ""
    return text


def render_row(
    *,
    slug: str,
    url: str,
    primary_keyword: str,
    brand: str,
    au_volume: int,
    us_volume: int | None,
    current_title: str | None,
    current_h1: str | None,
    descriptor: str | None,
    usp: str,
    competitor_titles: list[str],
    serp_patterns: dict[str, Any] | None = None,
) -> dict[str, str]:
    suggested_title = build_title(primary_keyword, brand, descriptor)
    suggested_h1 = build_h1(primary_keyword)
    suggested_meta = build_meta(
        primary_keyword,
        brand,
        usp,
        serp_angle=_primary_serp_angle(serp_patterns or {}),
    )
    status = score_status(current_title, current_h1, primary_keyword, brand)
    return {
        "Collection": slug.replace("-", " ").title(),
        "URL": url,
        "Primary Keyword": primary_keyword,
        "AU Volume": str(au_volume or 0),
        "US Volume": str(us_volume or "") if us_volume is not None else "",
        "Current Title": current_title or "",
        "Suggested Title": suggested_title,
        "Current H1": current_h1 or "",
        "Suggested H1": suggested_h1,
        "Suggested Meta Description": suggested_meta,
        "Status": status,
        "Competitor Patterns (Top 3 Titles)": " / ".join(competitor_titles),
        "SERP Considerations": _serp_considerations(serp_patterns or {}, competitor_titles),
    }


def descriptor_for_collection(
    collection: dict,
    *,
    competitor_titles: list[str] | None = None,
    serp_patterns: dict[str, Any] | None = None,
) -> str | None:
    """Prefer client/state/SERP descriptors; avoid vertical-specific hardcoding."""
    for key in ("metadata_descriptor", "title_descriptor", "seo_descriptor"):
        value = _clean_descriptor(collection.get(key))
        if value:
            return value
    patterns = serp_patterns or {}
    for key in ("recommended_descriptor", "title_descriptor", "modifier"):
        value = _clean_descriptor(patterns.get(key))
        if value:
            return value
    from_titles = _descriptor_from_competitor_titles(
        competitor_titles or [],
        collection.get("primary_keyword") or "",
    )
    if from_titles:
        return from_titles
    return None


def _clean_descriptor(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip(" |-")
    if not text or text.upper().startswith("REQUIRED"):
        return ""
    if len(text) > 38:
        return ""
    return text


def _descriptor_from_competitor_titles(titles: list[str], primary_keyword: str) -> str:
    """Extract a short modifier seen in competitor title formulas.

    This is deliberately conservative: if the titles do not expose a clean,
    repeated descriptor, return empty rather than inventing one.
    """
    primary_tokens = _tokens(primary_keyword)
    candidates: list[str] = []
    for title in titles:
        parts = [p.strip(" -–|") for p in re.split(r"\s+[|–-]\s+", title) if p.strip()]
        for part in parts[1:3]:
            tokens = _tokens(part)
            if not tokens or tokens & {"sale", "clearance", "afterpay", "shipping"}:
                continue
            if len(tokens & primary_tokens) >= max(1, len(primary_tokens) - 1):
                continue
            cleaned = _clean_descriptor(part)
            if cleaned:
                candidates.append(cleaned)
    if not candidates:
        return ""
    counts: dict[str, int] = {}
    for candidate in candidates:
        key = candidate.lower()
        counts[key] = counts.get(key, 0) + 1
    best = max(candidates, key=lambda c: (counts[c.lower()], -len(c)))
    return best if counts[best.lower()] >= 2 else ""


def _tokens(value: Any) -> set[str]:
    stop = {"shop", "online", "buy", "the", "and", "for", "with", "women", "womens", "mens"}
    return {
        token for token in re.findall(r"[a-z0-9]+", str(value).lower())
        if token not in stop and len(token) > 2
    }


def _primary_serp_angle(patterns: dict[str, Any]) -> str:
    angles = patterns.get("copy_angles") or patterns.get("content_angles") or []
    if isinstance(angles, list) and angles:
        return str(angles[0])
    return ""


def _safe_serp_angle(angle: str | None) -> str:
    text = re.sub(r"\s+", " ", str(angle or "")).strip(" .")
    if not text or len(text) > 50:
        return ""
    banned = {"cheap", "sale", "clearance", "guaranteed"}
    if _tokens(text) & banned:
        return ""
    return text


def _serp_considerations(patterns: dict[str, Any], competitor_titles: list[str]) -> str:
    parts = []
    if patterns.get("title_formula"):
        parts.append(f"title formula: {patterns.get('title_formula')}")
    angle = _primary_serp_angle(patterns)
    if angle:
        parts.append(f"copy angle: {angle}")
    if competitor_titles:
        parts.append("competitor title patterns reviewed")
    return "; ".join(parts)


def current_page_for(collection: dict, pages: dict[str, dict]) -> dict[str, str]:
    """Use fresh page data first, then sidecar fallback fields."""
    slug = collection["slug"]
    page = pages.get(slug, {})
    return {
        "title": page.get("title") or collection.get("current_title") or "",
        "h1": page.get("h1") or collection.get("current_h1") or "",
        "meta_description": (
            page.get("meta_description")
            or page.get("description")
            or collection.get("current_meta_description")
            or ""
        ),
    }


def assert_completion(rows: list[dict[str, str]], *, market_scope: str, allow_incomplete: bool) -> None:
    if allow_incomplete or not rows:
        return
    missing_volume = [
        r["Collection"] for r in rows
        if int(r.get("AU Volume") or 0) <= 0
        or ("US" in market_scope.upper() and not r.get("US Volume"))
    ]
    missing_page_state = [
        r["Collection"] for r in rows
        if not r.get("Current Title") or not r.get("Current H1")
    ]
    limit = max(1, int(len(rows) * 0.1))
    messages = []
    if len(missing_volume) > limit:
        messages.append(
            f"{len(missing_volume)} of {len(rows)} rows are missing required volume data: "
            f"{', '.join(missing_volume[:10])}"
        )
    if len(missing_page_state) > limit:
        messages.append(
            f"{len(missing_page_state)} of {len(rows)} rows are missing current title/H1 data: "
            f"{', '.join(missing_page_state[:10])}"
        )
    if messages:
        raise ValueError(
            "Refusing to write incomplete metadata suggestions. "
            + " ".join(messages)
            + " Pass --allow-incomplete only for diagnostic drafts."
        )


def run(
    client_json: Path,
    serp_json: Path,
    pages_json: Path,
    output: Path,
    *,
    allow_incomplete: bool = False,
) -> None:
    client = json.loads(client_json.read_text())
    brand = client["client"]
    serp = json.loads(serp_json.read_text()) if serp_json.exists() else []
    pages = page_state_by_slug(json.loads(pages_json.read_text()) if pages_json.exists() else {})

    fieldnames = [
        "Collection", "URL", "Primary Keyword", "AU Volume", "US Volume",
        "Current Title", "Suggested Title", "Current H1", "Suggested H1",
        "Suggested Meta Description", "Status", "Competitor Patterns (Top 3 Titles)",
        "SERP Considerations",
    ]
    rows = []
    for col in included_collections(client):
        slug = col["slug"]
        page = current_page_for(col, pages)
        serp_entry = serp_entry_for_slug(serp, slug)
        competitor_titles = pick_top_competitor_titles(serp, slug)
        serp_patterns = serp_entry.get("patterns") if isinstance(serp_entry.get("patterns"), dict) else {}
        descriptor = descriptor_for_collection(
            col,
            competitor_titles=competitor_titles,
            serp_patterns=serp_patterns,
        )
        usp = client.get("usp", "")
        rows.append(render_row(
            slug=slug,
            url=col["url"],
            primary_keyword=col["primary_keyword"],
            brand=brand,
            au_volume=col.get("au_volume", 0),
            us_volume=col.get("us_volume"),
            current_title=page.get("title"),
            current_h1=page.get("h1"),
            descriptor=descriptor,
            usp=usp,
            competitor_titles=competitor_titles,
            serp_patterns=serp_patterns,
        ))

    assert_completion(rows, market_scope=client.get("market_scope", "AU"), allow_incomplete=allow_incomplete)

    with output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--serp-json", required=True, type=Path)
    parser.add_argument("--pages-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    run(
        args.client_json,
        args.serp_json,
        args.pages_json,
        args.output,
        allow_incomplete=args.allow_incomplete,
    )


if __name__ == "__main__":
    main()
