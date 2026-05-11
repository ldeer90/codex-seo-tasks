"""Shared helpers for offline Collection SEO QA scripts."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


DROP_CLASSES = {"style_edit", "promo_drop", "empty"}


def read_json(path: Path | None, default: Any = None) -> Any:
    if path is None or not path.exists():
        return default
    return json.loads(path.read_text())


def included_collections(client: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        c for c in client.get("collections", [])
        if c.get("class") not in DROP_CLASSES and c.get("include", True) is not False
    ]


def normalise_url(url: str | None) -> str:
    if not url:
        return ""
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = re.sub(r"/+$", "", parsed.path or "")
    return urlunsplit((scheme, netloc, path, "", ""))


def parse_seranking_keywords(raw: Any) -> list[dict[str, Any]]:
    data = raw.get("data", raw) if isinstance(raw, dict) else raw
    if not isinstance(data, list):
        return []
    return [k for k in data if isinstance(k, dict)]


def parse_volume_map(raw: Any) -> dict[str, int]:
    """Accept plain maps or common SE Ranking response shapes."""
    if raw is None:
        return {}
    if isinstance(raw, dict):
        if all(isinstance(v, (int, float, str)) for v in raw.values()):
            return {_norm_keyword(k): _to_int(v) for k, v in raw.items()}
        for key in ("data", "result", "keywords"):
            if key in raw:
                return parse_volume_map(raw[key])
    if isinstance(raw, list):
        out: dict[str, int] = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            keyword = item.get("keyword") or item.get("name") or item.get("query")
            volume = (
                item.get("volume")
                or item.get("search_volume")
                or item.get("searchVolume")
                or item.get("avg_monthly_searches")
                or 0
            )
            if keyword:
                out[_norm_keyword(str(keyword))] = _to_int(volume)
        return out
    return {}


def keyword_index(keywords: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_url: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for kw in keywords:
        by_url[normalise_url(kw.get("link") or kw.get("target_url"))].append(kw)
    return dict(by_url)


def keyword_names_for_url(keywords: list[dict[str, Any]], url: str) -> set[str]:
    target = normalise_url(url)
    return {
        _norm_keyword(k.get("name") or k.get("keyword") or "")
        for k in keywords
        if normalise_url(k.get("link") or k.get("target_url")) == target
    }


def engine_pair_stats(keywords: list[dict[str, Any]]) -> dict[str, int]:
    pair_count = 0
    for kw in keywords:
        engines = kw.get("site_engine_ids") or []
        if isinstance(engines, list):
            pair_count += len(engines)
    return {"keyword_count": len(keywords), "pair_count": pair_count}


def page_state_by_slug(raw: Any) -> dict[str, dict[str, Any]]:
    """Normalise current page crawls from dict or legacy list shapes."""
    if not raw:
        return {}
    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items() if isinstance(v, dict)}
    out: dict[str, dict[str, Any]] = {}
    if isinstance(raw, list):
        for row in raw:
            if not isinstance(row, dict):
                continue
            slug = row.get("slug") or _slug_from_url(row.get("url"))
            if slug:
                out[str(slug)] = row
    return out


def coverage_label(covered: int, total: int, noun: str = "SEO-priority collections") -> str:
    return f"{covered} of {total} {noun}"


def _slug_from_url(url: str | None) -> str:
    path = urlsplit(url or "").path.rstrip("/")
    if "/collections/" not in path:
        return ""
    return path.split("/collections/")[-1]


def _norm_keyword(keyword: str) -> str:
    return re.sub(r"\s+", " ", keyword.lower()).strip()


def _to_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0
