"""Build deterministic Shopify collection content brief inputs.

The script is offline-only: fetch live SE Ranking, page scrape, SERP, and
product exports in the agent session, save them as JSON, then pass them here.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from collection_seo_utils import (
    included_collections,
    normalise_url,
    page_state_by_slug,
    parse_seranking_keywords,
    parse_volume_map,
    read_json,
)

# Retailer and brand names that contaminate supplemental keyword lists.
# Add more as needed; matching is whole-word, case-insensitive.
_DEFAULT_BRAND_DENYLIST: frozenset[str] = frozenset({
    "kmart", "target", "myer", "david jones", "dj's", "djs",
    "asos", "boohoo", "shein", "zara", "h&m", "hm",
    "seafolly", "baku", "speedo", "funkita", "sunseeker",
    "monday", "zimmermann", "aje", "ganni", "shona joy",
    "realisation par", "alice mccall", "ginger and smart",
    "sass and bide", "country road", "witchery", "saba",
    "forever new", "princess polly", "beginning boutique",
    "meshki", "showpo", "white fox", "tiger mist",
    "pilgrim", "mango",
})

# Product categories that signal irrelevant content when the catalog doesn't include them.
_CATALOG_EXCLUSION_PATTERNS: list[tuple[re.Pattern[str], set[str]]] = [
    (re.compile(r"\b(kids?|children|girls?|boys?|toddler|baby|infant)\b"), {"KIDS", "CHILDREN", "GIRLS", "BOYS"}),
    (re.compile(r"\b(maternity|pregnancy|nursing|breastfeeding)\b"), {"MATERNITY", "NURSING"}),
    (re.compile(r"\b(period|menstrual|period[- ]proof)\b"), {"PERIOD", "PERIOD_PROOF"}),
    (re.compile(r"\b(mens?|menswear|male)\b"), {"MENS", "MENSWEAR"}),
    (re.compile(r"\b(plus size|curvy|extended size)\b"), {"PLUS", "CURVY"}),
]


def build_briefs(
    *,
    client_json: Path,
    seranking_keywords_json: Path,
    volume_json_au: Path,
    volume_json_us: Path | None = None,
    pages_json: Path | None = None,
    serp_json: Path | None = None,
    product_json: Path | None = None,
    supplemental_keywords_json: Path | None = None,
    gsc_json: Path | None = None,
    allow_incomplete: bool = False,
) -> dict[str, Any]:
    client = read_json(client_json, {})
    keywords = parse_seranking_keywords(read_json(seranking_keywords_json, []))
    au_volumes = parse_volume_map(read_json(volume_json_au, {}))
    us_volumes = parse_volume_map(read_json(volume_json_us, {}) if volume_json_us else {})
    pages = page_state_by_slug(read_json(pages_json, {}) if pages_json else {})
    serp = read_json(serp_json, {}) if serp_json else {}
    products = _normalise_product_export(read_json(product_json, {}) if product_json else {})
    supplemental = _normalise_supplemental_keywords(
        read_json(supplemental_keywords_json, {}) if supplemental_keywords_json else {}
    )
    gsc = _normalise_gsc_export(read_json(gsc_json, {}) if gsc_json else {})

    collections = included_collections(client)
    by_url = _keywords_by_url(keywords)

    # Merge default denylist with any client-specific additions.
    client_denylist = frozenset(
        _norm_keyword(b) for b in (client.get("brand_denylist") or [])
    )
    brand_denylist = _DEFAULT_BRAND_DENYLIST | client_denylist

    blocking: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    briefs: list[dict[str, Any]] = []

    for collection in collections:
        brief = _build_collection_brief(
            client=client,
            collection=collection,
            collections=collections,
            keywords_by_url=by_url,
            au_volumes=au_volumes,
            us_volumes=us_volumes,
            pages=pages,
            serp=serp,
            products=products,
            supplemental=supplemental,
            gsc=gsc,
            brand_denylist=brand_denylist,
        )
        briefs.append(brief)

    _dedup_supplemental_across_briefs(briefs)

    for brief in briefs:
        for issue in _validate_brief(brief, require_us="US" in str(client.get("market_scope", "")).upper()):
            if issue["severity"] == "blocking":
                blocking.append(issue)
            else:
                warnings.append(issue)

    if blocking and not allow_incomplete:
        messages = "; ".join(f"{i['slug']} [{i['code']}]: {i['message']}" for i in blocking[:8])
        if len(blocking) > 8:
            messages += f"; and {len(blocking) - 8} more"
        raise ValueError(
            "Refusing to build incomplete collection content briefs. "
            f"{messages}. Pass --allow-incomplete only for diagnostic drafts."
        )

    return {
        "client": client.get("client"),
        "domain": client.get("domain"),
        "market_scope": client.get("market_scope", "AU"),
        "generated": date.today().isoformat(),
        "source_files": {
            "client_json": str(client_json),
            "seranking_keywords_json": str(seranking_keywords_json),
            "volume_json_au": str(volume_json_au),
            "volume_json_us": str(volume_json_us) if volume_json_us else "",
            "pages_json": str(pages_json) if pages_json else "",
            "serp_json": str(serp_json) if serp_json else "",
            "product_json": str(product_json) if product_json else "",
            "supplemental_keywords_json": str(supplemental_keywords_json) if supplemental_keywords_json else "",
            "gsc_json": str(gsc_json) if gsc_json else "",
        },
        "summary": {
            "collections": len(briefs),
            "blocking": len(blocking),
            "warnings": len(warnings),
        },
        "blocking": blocking,
        "warnings": warnings,
        "briefs": briefs,
    }


def _build_collection_brief(
    *,
    client: dict[str, Any],
    collection: dict[str, Any],
    collections: list[dict[str, Any]],
    keywords_by_url: dict[str, list[dict[str, Any]]],
    au_volumes: dict[str, int],
    us_volumes: dict[str, int],
    pages: dict[str, dict[str, Any]],
    serp: Any,
    products: dict[str, dict[str, Any]],
    supplemental: dict[str, list[dict[str, Any]]],
    gsc: dict[str, list[dict[str, Any]]],
    brand_denylist: frozenset[str] | None = None,
) -> dict[str, Any]:
    slug = str(collection.get("slug", ""))
    primary = _norm_keyword(collection.get("primary_keyword", ""))
    page = _current_page(collection, pages.get(slug, {}))
    product_context = _product_context(collection, products.get(slug, {}))
    serp_context = _serp_context(slug, serp)
    live_keywords = keywords_by_url.get(normalise_url(collection.get("url")), [])
    keyword_set = _keyword_set(
        primary=primary,
        live_keywords=live_keywords,
        collection=collection,
        au_volumes=au_volumes,
        us_volumes=us_volumes,
        supplemental=supplemental.get(slug, []),
        brand_denylist=brand_denylist,
    )
    links = select_internal_links(collection, collections, limit=5, page=page)

    name = _collection_name(collection, page)
    brand = str(client.get("client") or client.get("brand") or "")
    return {
        "slug": slug,
        "collection_name": name,
        "url": collection.get("url", ""),
        "class": collection.get("class", ""),
        "current_page": page,
        "proposed_page_elements": _proposed_page_elements(
            client=client,
            name=name,
            primary=keyword_set["primary"]["keyword"],
            brand=brand,
            page=page,
            serp_context=serp_context,
            product_context=product_context,
        ),
        "keywords": keyword_set,
        "product_context": product_context,
        "serp_context": serp_context,
        "search_console_opportunities": gsc.get(slug, []),
        "internal_links": links,
        "content_recommendations": _content_recommendations(name, keyword_set, product_context, serp_context),
        "writer_prompt": _writer_prompt(client, name, collection, keyword_set, links),
        "qa_checklist": _qa_checklist(),
    }


def select_internal_links(
    source: dict[str, Any],
    collections: list[dict[str, Any]],
    *,
    limit: int = 5,
    page: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    scored = []
    existing_urls = {
        normalise_url(link.get("url") or link.get("href"))
        for link in ((page or {}).get("existing_internal_links") or [])
        if link.get("url") or link.get("href")
    }
    source_context = " ".join([
        str((page or {}).get("copy_summary") or ""),
        str(source.get("current_h1") or ""),
        str(source.get("primary_keyword") or ""),
    ])
    for target in collections:
        if target.get("slug") == source.get("slug"):
            continue
        if normalise_url(target.get("url")) in existing_urls:
            continue
        score, reasons = _link_score(source, target, source_context=source_context)
        scored.append((score, str(target.get("slug", "")), target, reasons))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [_internal_link_payload(source, target, score, reasons) for score, _, target, reasons in scored[:limit]]


def _link_score(
    source: dict[str, Any],
    target: dict[str, Any],
    *,
    source_context: str = "",
) -> tuple[float, list[str]]:
    reasons = []
    score = 0.0
    source_tokens = _tokens(source.get("slug", ""), source.get("primary_keyword", ""))
    target_tokens = _tokens(target.get("slug", ""), target.get("primary_keyword", ""))
    overlap = source_tokens & target_tokens
    if overlap:
        score += 12 * len(overlap)
        reasons.append(f"shared topic tokens: {', '.join(sorted(overlap))}")
    if source.get("dominant_product_type") and source.get("dominant_product_type") == target.get("dominant_product_type"):
        score += 18
        reasons.append("same dominant product type")
    target_volume = int(target.get("au_volume") or 0)
    if target_volume > 0:
        score += math.log10(target_volume + 10) * 4
        reasons.append("meaningful AU search demand")
    class_boost = {"pure_category": 6, "themed_category": 4, "curated_edit": 2}.get(str(target.get("class")), 0)
    score += class_boost
    if target.get("slug") in {"all-dresses", "dresses"}:
        score += 3
        reasons.append("useful hub page")
    context_overlap = _tokens(source_context) & target_tokens
    if context_overlap:
        score += 8 * len(context_overlap)
        reasons.append(f"fits existing copy context: {', '.join(sorted(context_overlap))}")
    priority = str(target.get("business_priority") or target.get("strategic_priority") or "").lower()
    if priority in {"high", "priority", "p1", "1"}:
        score += 10
        reasons.append("high business priority")
    elif priority in {"medium", "p2", "2"}:
        score += 5
        reasons.append("medium business priority")
    if not reasons:
        reasons.append("closest available relevant collection")
    return score, reasons


def _internal_link_payload(
    source: dict[str, Any],
    target: dict[str, Any],
    score: float,
    reasons: list[str],
) -> dict[str, Any]:
    anchor = _anchor_text(target.get("primary_keyword") or target.get("current_h1") or target.get("slug", ""))
    source_name = _title_from_slug(source.get("slug", ""))
    target_name = _title_from_slug(target.get("slug", ""))
    placement = (
        f"Use {anchor} where the copy helps shoppers compare {source_name} with {target_name}; "
        "skip it if that comparison cannot be made naturally."
    )
    return {
        "target_slug": target.get("slug", ""),
        "target_collection": target_name,
        "target_url": target.get("url", ""),
        "anchor_text": anchor,
        "placement": placement,
        "rationale": "; ".join(reasons),
        "score": round(score, 2),
    }


def _keyword_set(
    *,
    primary: str,
    live_keywords: list[dict[str, Any]],
    collection: dict[str, Any],
    au_volumes: dict[str, int],
    us_volumes: dict[str, int],
    supplemental: list[dict[str, Any]],
    brand_denylist: frozenset[str] | None = None,
) -> dict[str, Any]:
    primary_au = au_volumes.get(primary, int(collection.get("au_volume") or 0))
    primary_us = us_volumes.get(primary, int(collection.get("us_volume") or 0))
    catalog_types = {str(t).upper() for t in (collection.get("product_types") or [])}
    if collection.get("dominant_product_type"):
        catalog_types.add(str(collection["dominant_product_type"]).upper())
    seen = {primary}
    secondary = []
    for keyword in live_keywords:
        name = _norm_keyword(keyword.get("name") or keyword.get("keyword") or "")
        if not name or name in seen:
            continue
        seen.add(name)
        secondary.append({
            "keyword": name,
            "au_volume": au_volumes.get(name, 0),
            "us_volume": us_volumes.get(name, 0),
            "difficulty": keyword.get("difficulty") or keyword.get("kd") or "",
            "source": "SE Ranking tracked keyword export",
        })
    supporting = []
    for variant, source in _derived_keyword_variants(collection, primary):
        if variant and variant not in seen:
            seen.add(variant)
            supporting.append({
                "keyword": variant,
                "au_volume": au_volumes.get(variant, 0),
                "us_volume": us_volumes.get(variant, 0),
                "source": source,
            })
    supplemental_keywords = []
    effective_denylist = brand_denylist if brand_denylist is not None else _DEFAULT_BRAND_DENYLIST
    for row in supplemental:
        name = _norm_keyword(row.get("keyword") or row.get("query") or "")
        if not name or name in seen:
            continue
        if _is_brand_contaminated(name, effective_denylist):
            continue
        if _is_catalog_mismatch(name, catalog_types):
            continue
        seen.add(name)
        supplemental_keywords.append({
            "keyword": name,
            "au_volume": int(row.get("au_volume") or row.get("volume") or 0),
            "us_volume": int(row.get("us_volume") or 0),
            "difficulty": row.get("difficulty") or row.get("kd") or "",
            "intent": row.get("intent") or row.get("intents") or "",
            "source": row.get("source") or "SE Ranking supplemental keyword research",
            "reasoning": row.get("reasoning") or "",
        })
    return {
        "primary": {
            "keyword": primary,
            "au_volume": primary_au,
            "us_volume": primary_us,
            "source": "SE Ranking volume export or synced sidecar",
        },
        "secondary": secondary[:8],
        "supplemental": supplemental_keywords[:12],
        "supporting": supporting[:8],
        "intent": _intent_for_keyword(primary),
    }


def _is_brand_contaminated(keyword: str, denylist: frozenset[str]) -> bool:
    for brand in denylist:
        if re.search(r"\b" + re.escape(brand) + r"\b", keyword):
            return True
    return False


def _is_catalog_mismatch(keyword: str, catalog_types: set[str]) -> bool:
    for pattern, required_types in _CATALOG_EXCLUSION_PATTERNS:
        if pattern.search(keyword):
            if not (catalog_types & required_types):
                return True
    return False


def _proposed_page_elements(
    *,
    client: dict[str, Any],
    name: str,
    primary: str,
    brand: str,
    page: dict[str, Any],
    serp_context: dict[str, Any],
    product_context: dict[str, Any],
) -> dict[str, Any]:
    primary_title = primary.title()
    brand_part = f" | {brand}" if brand else ""

    # Use SERP title formula if available, otherwise standard pattern.
    patterns = serp_context.get("patterns") or {}
    formula = str(patterns.get("title_formula") or "")
    if formula and "|" in formula:
        proposed_title = f"{primary_title}{brand_part}"
    else:
        proposed_title = f"{primary_title}{brand_part}"

    # Build meta only from verified client/product facts.
    samples = product_context.get("sample_product_titles") or []
    product_hint = f" featuring {samples[0]}" if samples else ""
    usp = _verified_usp(client)
    usp_sentence = f" {usp}." if usp else ""
    proposed_meta = f"Shop {primary} at {brand}{product_hint}.{usp_sentence} Browse the collection.".strip()

    current_title = page.get("title") or ""
    current_meta = page.get("meta_description") or ""
    return {
        "proposed_title": proposed_title,
        "proposed_meta_description": proposed_meta[:160],
        "title_change_needed": current_title.lower() != proposed_title.lower(),
        "meta_change_needed": (
            not current_meta
            or primary not in current_meta.lower()
        ),
        "note": (
            "Proposed title follows SERP-observed formula. "
            "Adjust meta to match actual product angle and brand voice before publishing."
        ),
    }


def _verified_usp(client: dict[str, Any]) -> str:
    """Return a factual client USP only when explicitly present in sidecar state."""
    usp = _clean_text(client.get("usp") or client.get("brand_usp") or "")
    if not usp or usp.upper().startswith("REQUIRED"):
        return ""
    return usp.rstrip(".")


def _dedup_supplemental_across_briefs(briefs: list[dict[str, Any]]) -> None:
    """Remove supplemental keywords assigned to a better-fit brief.

    For each keyword appearing in multiple briefs, keep it only in the brief
    whose primary keyword shares the most token overlap with it.
    """
    # Build keyword → list of (brief_index, primary) pairs.
    keyword_to_briefs: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for idx, brief in enumerate(briefs):
        primary = brief["keywords"]["primary"]["keyword"]
        for kw in brief["keywords"].get("supplemental") or []:
            keyword_to_briefs[kw["keyword"]].append((idx, primary))

    # For keywords claimed by multiple briefs, find the best owner.
    for keyword, claimants in keyword_to_briefs.items():
        if len(claimants) <= 1:
            continue
        kw_tokens = _tokens(keyword)
        scored = sorted(
            claimants,
            key=lambda pair: -len(_tokens(pair[1]) & kw_tokens),
        )
        best_idx = scored[0][0]
        losers = {idx for idx, _ in claimants if idx != best_idx}
        for idx in losers:
            brief = briefs[idx]
            brief["keywords"]["supplemental"] = [
                kw for kw in brief["keywords"]["supplemental"]
                if kw["keyword"] != keyword
            ]


def _current_page(collection: dict[str, Any], page: dict[str, Any]) -> dict[str, Any]:
    markdown = str(page.get("markdown") or "")
    summary = (
        page.get("main_content_summary")
        or page.get("content_summary")
        or _summarise_markdown(markdown)
        or collection.get("current_meta_description")
        or ""
    )
    links = page.get("internal_links") or page.get("links") or []
    return {
        "title": page.get("title") or collection.get("current_title") or "",
        "h1": page.get("h1") or collection.get("current_h1") or "",
        "meta_description": (
            page.get("meta_description")
            or page.get("description")
            or collection.get("current_meta_description")
            or ""
        ),
        "word_count": int(page.get("word_count") or _word_count(markdown) or 0),
        "copy_summary": _clean_text(summary),
        "existing_internal_links": _normalise_links(links)[:20],
    }


def _product_context(collection: dict[str, Any], product_export: dict[str, Any]) -> dict[str, Any]:
    titles = _product_titles_from_export(product_export)
    if not titles:
        titles = [str(t).strip() for t in collection.get("sample_product_titles", []) if str(t).strip()]
    product_types = product_export.get("product_types") if isinstance(product_export, dict) else []
    if not product_types and collection.get("dominant_product_type"):
        product_types = [collection.get("dominant_product_type")]
    return {
        "sample_product_titles": titles[:12],
        "product_types": [str(t) for t in product_types if t],
        "product_count_sample": int(product_export.get("product_count_sample") or collection.get("product_count_sample") or len(titles)),
        "source": "product export" if product_export else "sidecar sample_product_titles",
    }


def _serp_context(slug: str, serp: Any) -> dict[str, Any]:
    if not isinstance(serp, dict) or not isinstance(serp.get(slug), dict):
        return {"serp_results": [], "patterns": {}, "source": "missing structured SERP export"}
    node = serp[slug]
    results = []
    for result in node.get("serp_results") or []:
        if not isinstance(result, dict):
            continue
        results.append({
            "position": result.get("position"),
            "title": _clean_text(result.get("title", "")),
            "url": result.get("url", ""),
            "h1": _clean_text(result.get("h1", "")),
            "h2s": [_clean_text(h) for h in result.get("h2s", [])[:5]],
            "meta_description": _clean_text(result.get("meta_description", "")),
        })
    return {
        "serp_results": results[:5],
        "patterns": node.get("patterns") or {},
        "source": "structured SERP export",
    }


def _content_recommendations(
    name: str,
    keyword_set: dict[str, Any],
    product_context: dict[str, Any],
    serp_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    primary = keyword_set["primary"]["keyword"]
    products = product_context.get("sample_product_titles") or []
    product_note = ", ".join(products[:4]) if products else "the visible product range"

    # Derive word count target from SERP if available.
    serp_results = (serp_context or {}).get("serp_results") or []
    word_counts = [int(r.get("word_count") or 0) for r in serp_results if r.get("word_count")]
    if word_counts:
        avg_wc = sum(word_counts) // len(word_counts)
        target_low = max(150, avg_wc - 30)
        target_high = min(350, avg_wc + 50)
        length_target = f"{target_low}–{target_high} words, matching observed SERP competition."
    else:
        length_target = "180–260 words of useful collection copy before or around the product grid."

    # Supplemental keywords to weave in.
    supp_names = [kw["keyword"] for kw in (keyword_set.get("supplemental") or [])[:3]]
    supp_hint = (
        f"Weave in close variants naturally: {', '.join(supp_names)}."
        if supp_names else
        "Use close variants naturally; do not repeat the same phrase in every sentence."
    )

    return {
        "recommended_length": length_target,
        "suggested_heading_structure": [
            f"H1: {name} — keep existing, do not change",
            "H2: One required subheading. Must carry a point of view — a style, occasion, fit, or shopper-decision angle. Not a repeat of the H1 and not a bare keyword phrase. Example angles: 'Shop by Occasion', 'Built for Repeating', 'Styled for the Week Ahead'.",
            "H3 (×2): Two required subheadings below the H2. Each must orient the shopper around a real distinction — colour range, fabric/fit, occasion tier, or product type. Do not use the primary keyword as a heading. Do not repeat the H2 angle.",
        ],
        "structure": [
            f"Open with {primary} and the main shopping intent in one natural sentence.",
            f"Ground the copy in real products or silhouettes from this collection, such as {product_note}.",
            "Add one short styling, occasion, or fit paragraph based on the SERP patterns.",
            "Include the internal links only where they help the shopper compare related ranges.",
        ],
        "keyword_inclusion": [
            f"Use the primary keyword '{primary}' once near the start.",
            supp_hint,
            "Prefer human category language over forced exact-match phrasing.",
        ],
        "humanised_guidance": [
            "Write for someone deciding what to wear, not for a crawler.",
            "Use concrete product, fit, fabric, occasion, or styling details that are present in the source data.",
            "Avoid generic claims that are not supported by the page, products, or client brief.",
        ],
        "banned_phrases": [
            "elevate your wardrobe",
            "effortlessly chic",
            "explore our range",
            "discover our collection",
            "perfect for any occasion",
            "look no further",
        ],
    }


def _writer_prompt(
    client: dict[str, Any],
    name: str,
    collection: dict[str, Any],
    keyword_set: dict[str, Any],
    links: list[dict[str, Any]],
) -> str:
    anchors = ", ".join(link["anchor_text"] for link in links[:5])
    primary = keyword_set["primary"]["keyword"]
    brand = str(client.get("client") or "")
    brand_display = str(client.get("brand_display_name") or brand)
    usp = _verified_usp(client)
    brand_voice = str(client.get("brand_voice") or "")
    tone_direction = str(client.get("tone_direction") or "")

    supp_keywords = [kw["keyword"] for kw in (keyword_set.get("supplemental") or [])[:4]]
    if supp_keywords:
        supp_note = (
            f" Place these supplemental keywords where they fit naturally — use each as a complete phrase "
            f"in the form a searcher would type it, not broken up as adjectives: {', '.join(supp_keywords)}."
        )
    else:
        supp_note = ""

    voice_block = ""
    if brand_voice or tone_direction:
        voice_block = (
            f" Brand voice: {brand_voice}" if brand_voice else ""
        ) + (
            f" Tone direction: {tone_direction}" if tone_direction else ""
        )
    usp_instruction = (
        f"Brand USP: {usp}."
        if usp else
        "Do not add brand, shipping, origin, or product claims unless they appear in this brief."
    )

    return (
        f"Write collection page copy for {brand} — {name}. "
        f"Use '{brand_display}' as the brand name on first mention, then '{brand}' thereafter. "
        f"Target the primary keyword '{primary}' naturally near the opening sentence. "
        f"{usp_instruction} "
        f"{voice_block} "
        f"Word count: 200–250 words total across all sections. "
        f"Ground every claim in the product sample titles and SERP context in this brief. "
        f"When you name a product, add a one-phrase descriptor (silhouette, fabric, key feature) so the name means something. "
        f"{supp_note} "
        f"Include at least three of these internal link anchors where they read naturally: {anchors}. "
        f"Avoid: 'elevate your wardrobe', 'effortlessly chic', 'explore our range', 'discover our collection', "
        f"'perfect for any occasion', 'look no further', unsupported competitive comparisons, or any claim not in the brief. "
        f"Output clean HTML only — no markdown, no commentary, no introduction. "
        f"Use exactly this structure: one <h2> subheading, two <h3> subheadings beneath it, and <p> tags for body copy. "
        f"Do not include <h1> or any element outside this structure."
    ).strip()


def _qa_checklist() -> list[str]:
    return [
        "Output is clean HTML — one <h2>, two <h3>s, and <p> tags only. No markdown, no <h1>, no wrapper elements.",
        "H2 subheading uses a style, occasion, or fit angle — not a repeat of the H1.",
        "Both H3 subheadings are distinct from each other and from the H2.",
        "Proposed title tag is updated from current — primary keyword in the right position.",
        "Proposed meta description is updated — primary keyword present, no generic filler.",
        "Primary keyword appears naturally near the beginning of the copy.",
        "Copy is 200–250 words total and uses real product, fit, fabric, occasion, or style details.",
        "At least three recommended internal links are included where they read naturally.",
        "No banned phrases: 'elevate', 'effortlessly chic', 'explore our range', 'discover our collection', 'any occasion'.",
        "No unsupported claims — every assertion can be grounded in the product sample or brand brief.",
    ]


def _validate_brief(brief: dict[str, Any], *, require_us: bool) -> list[dict[str, Any]]:
    issues = []
    slug = brief["slug"]
    primary = brief["keywords"]["primary"]
    if int(primary.get("au_volume") or 0) <= 0:
        issues.append(_issue("blocking", "missing_primary_au_volume", "Primary keyword has no AU volume.", slug))
    if require_us and int(primary.get("us_volume") or 0) <= 0:
        issues.append(_issue("blocking", "missing_primary_us_volume", "Primary keyword has no US volume.", slug))
    page = brief.get("current_page") or {}
    if not page.get("title") or not page.get("h1") or not page.get("copy_summary"):
        issues.append(_issue("blocking", "missing_current_page_data", "Current title, H1, or copy summary is missing.", slug))
    elif not page.get("meta_description"):
        issues.append(_issue("warning", "missing_meta_description", "No current meta description was detected.", slug))
    if not (brief.get("product_context") or {}).get("sample_product_titles"):
        issues.append(_issue("blocking", "missing_product_context", "No product sample titles are available.", slug))
    if not (brief.get("serp_context") or {}).get("serp_results"):
        issues.append(_issue("blocking", "missing_serp_context", "No structured SERP results are available.", slug))
    if len(brief.get("internal_links") or []) < 5:
        issues.append(_issue("blocking", "insufficient_internal_links", "Fewer than five internal link candidates are available.", slug))
    if not (brief.get("keywords") or {}).get("supplemental"):
        issues.append(_issue("blocking", "missing_supplemental_keywords", "No supplemental SE Ranking keyword opportunities are attached.", slug))
    if not brief.get("writer_prompt"):
        issues.append(_issue("blocking", "missing_writer_prompt", "Writer prompt is missing.", slug))
    return issues


def _normalise_product_export(raw: Any) -> dict[str, dict[str, Any]]:
    if not raw:
        return {}
    if isinstance(raw, dict):
        if all(isinstance(v, (dict, list)) for v in raw.values()):
            return {str(k): _normalise_product_node(v) for k, v in raw.items()}
        slug = raw.get("slug")
        if slug:
            return {str(slug): _normalise_product_node(raw)}
    out = {}
    if isinstance(raw, list):
        for row in raw:
            if not isinstance(row, dict):
                continue
            slug = row.get("slug") or _slug_from_url(row.get("url"))
            if slug:
                out[str(slug)] = _normalise_product_node(row)
    return out


def _normalise_product_node(node: Any) -> dict[str, Any]:
    if isinstance(node, list):
        return {"products": node, "product_count_sample": len(node)}
    if isinstance(node, dict):
        products = node.get("products") or node.get("data") or node.get("items") or []
        titles = node.get("product_titles") or node.get("sample_product_titles") or []
        return {
            "products": products,
            "product_titles": titles,
            "product_types": node.get("product_types") or [],
            "product_count_sample": node.get("product_count_sample") or len(products) or len(titles),
        }
    return {}


def _normalise_supplemental_keywords(raw: Any) -> dict[str, list[dict[str, Any]]]:
    if not raw:
        return {}
    if isinstance(raw, dict):
        if isinstance(raw.get("by_slug"), dict):
            return {
                str(slug): _normalise_keyword_rows(rows)
                for slug, rows in raw["by_slug"].items()
            }
        return {
            str(slug): _normalise_keyword_rows(rows)
            for slug, rows in raw.items()
            if isinstance(rows, list)
        }
    return {}


def _normalise_keyword_rows(rows: Any) -> list[dict[str, Any]]:
    out = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if isinstance(row, str):
            out.append({"keyword": row})
        elif isinstance(row, dict):
            out.append(row)
    return out


def _normalise_gsc_export(raw: Any) -> dict[str, list[dict[str, Any]]]:
    if not raw:
        return {}
    if isinstance(raw, dict) and isinstance(raw.get("by_slug"), dict):
        return {
            str(slug): _normalise_gsc_rows(rows)
            for slug, rows in raw["by_slug"].items()
        }
    if isinstance(raw, dict):
        return {
            str(slug): _normalise_gsc_rows(rows)
            for slug, rows in raw.items()
            if isinstance(rows, list)
        }
    return {}


def _normalise_gsc_rows(rows: Any) -> list[dict[str, Any]]:
    out = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        query = _norm_keyword(row.get("query") or row.get("keyword") or "")
        if not query:
            continue
        out.append({
            "query": query,
            "clicks": _to_float(row.get("clicks")),
            "impressions": _to_float(row.get("impressions")),
            "ctr": _to_float(row.get("ctr")),
            "position": _to_float(row.get("position")),
            "source": row.get("source") or "Google Search Console",
        })
    return out


def _product_titles_from_export(node: dict[str, Any]) -> list[str]:
    titles = [str(t).strip() for t in node.get("product_titles", []) if str(t).strip()]
    for product in node.get("products", []):
        if isinstance(product, dict):
            title = product.get("title") or product.get("name")
            if title:
                titles.append(str(title).strip())
        elif str(product).strip():
            titles.append(str(product).strip())
    return list(dict.fromkeys(titles))


def _keywords_by_url(keywords: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_url: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for keyword in keywords:
        by_url[normalise_url(keyword.get("link") or keyword.get("target_url"))].append(keyword)
    return dict(by_url)


def _derived_keyword_variants(collection: dict[str, Any], primary: str) -> list[tuple[str, str]]:
    variants = []
    h1 = _norm_keyword(collection.get("current_h1", ""))
    if h1:
        variants.append((h1, "current H1"))
    product_type = _norm_keyword(collection.get("dominant_product_type", ""))
    if product_type:
        variants.append((product_type, "dominant product type"))
    if primary.endswith(" dress"):
        variants.append((primary + "es", "primary keyword plural variant"))
    elif not primary.endswith("s"):
        variants.append((primary + "s", "primary keyword plural variant"))
    return variants


def _intent_for_keyword(keyword: str) -> str:
    occasion_terms = {"formal", "bridal", "going out", "resort"}
    if any(term in keyword for term in occasion_terms):
        return "Commercial collection intent with occasion-led comparison and style reassurance."
    return "Commercial collection intent: the searcher is comparing products and needs range, fit, and style confidence."


def _normalise_links(links: Any) -> list[dict[str, str]]:
    out = []
    if not isinstance(links, list):
        return out
    for link in links:
        if isinstance(link, dict):
            href = link.get("url") or link.get("href")
            text = link.get("text") or link.get("anchor") or ""
        else:
            href = str(link)
            text = ""
        if href:
            out.append({"url": str(href), "anchor": _clean_text(text)})
    return out


def _collection_name(collection: dict[str, Any], page: dict[str, Any]) -> str:
    return page.get("h1") or _title_from_slug(collection.get("slug", ""))


def _title_from_slug(slug: str) -> str:
    return str(slug).replace("-", " ").title()


def _anchor_text(text: str) -> str:
    anchor = _norm_keyword(text).replace("womens", "women's")
    return anchor or "related collection"


def _tokens(*values: Any) -> set[str]:
    stop = {"the", "all", "shop", "womens", "women", "collection", "collections"}
    return {
        token for value in values
        for token in re.findall(r"[a-z0-9]+", str(value).lower())
        if token not in stop and len(token) > 2
    }


def _summarise_markdown(markdown: str) -> str:
    text = _clean_text(re.sub(r"\[[^\]]+\]\([^)]+\)", "", markdown))
    words = text.split()
    return " ".join(words[:45])


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _norm_keyword(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _slug_from_url(url: str | None) -> str:
    match = re.search(r"/collections/([^/?#]+)", url or "")
    return match.group(1) if match else ""


def _issue(severity: str, code: str, message: str, slug: str) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "slug": slug}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--seranking-keywords-json", required=True, type=Path)
    parser.add_argument("--volume-json-au", required=True, type=Path)
    parser.add_argument("--volume-json-us", type=Path)
    parser.add_argument("--pages-json", type=Path)
    parser.add_argument("--serp-json", type=Path)
    parser.add_argument("--product-json", type=Path)
    parser.add_argument("--supplemental-keywords-json", type=Path)
    parser.add_argument("--gsc-json", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    result = build_briefs(
        client_json=args.client_json,
        seranking_keywords_json=args.seranking_keywords_json,
        volume_json_au=args.volume_json_au,
        volume_json_us=args.volume_json_us,
        pages_json=args.pages_json,
        serp_json=args.serp_json,
        product_json=args.product_json,
        supplemental_keywords_json=args.supplemental_keywords_json,
        gsc_json=args.gsc_json,
        allow_incomplete=args.allow_incomplete,
    )
    args.output.write_text(json.dumps(result, indent=2))
    print(f"Wrote {len(result['briefs'])} collection content briefs to {args.output}")


if __name__ == "__main__":
    main()
