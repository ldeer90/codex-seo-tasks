from __future__ import annotations

from typing import Any
from urllib.parse import urljoin, urlparse


def collection_slug_from_landing_page(landing_page: str, path_prefix: str = "/collections/") -> str:
    path = urlparse(landing_page).path if landing_page.startswith(("http://", "https://")) else landing_page
    path = path.split("?", 1)[0].rstrip("/")
    prefix = path_prefix if path_prefix.startswith("/") else f"/{path_prefix}"
    prefix = prefix.rstrip("/") + "/"
    if not path.startswith(prefix):
        return ""
    slug = path[len(prefix):].split("/", 1)[0].strip()
    if not slug or slug in {"all", "frontpage"}:
        return ""
    return slug


def summarise_collection_opportunities(
    *,
    current_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    website_url: str,
    path_prefix: str = "/collections/",
    limit: int | None = None,
) -> dict[str, Any]:
    comparison_by_slug = _aggregate_by_slug(comparison_rows, website_url, path_prefix)
    current_by_slug = _aggregate_by_slug(current_rows, website_url, path_prefix)

    opportunities = []
    for slug, current in current_by_slug.items():
        comparison = comparison_by_slug.get(slug, _empty_metrics(slug, current["url"]))
        row = _opportunity_row(slug=slug, current=current, comparison=comparison)
        opportunities.append(row)

    opportunities.sort(
        key=lambda row: (
            -float(row["priority_score"]),
            -float(row["current"].get("revenue") or 0),
            -float(row["current"].get("sessions") or 0),
        )
    )
    if limit:
        opportunities = opportunities[:limit]

    return {
        "count": len(opportunities),
        "path_prefix": path_prefix,
        "totals": _totals(opportunities),
        "opportunities": opportunities,
    }


def merge_landing_page_rows(*row_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_page: dict[tuple[str, str], dict[str, Any]] = {}
    metric_keys = ("sessions", "users", "engaged_sessions", "conversions", "revenue", "purchases")

    for rows in row_groups:
        for row in rows:
            landing_page = str(row.get("landing_page") or "")
            if not landing_page:
                continue
            channel = str(row.get("channel") or "")
            target = by_page.setdefault(
                (landing_page, channel),
                {
                    "landing_page": landing_page,
                    "channel": channel,
                    **{key: 0.0 for key in metric_keys},
                },
            )
            for key in metric_keys:
                target[key] = max(_num(target.get(key)), _num(row.get(key)))

    return list(by_page.values())


def classify_priority(
    *,
    sessions: float,
    revenue: float,
    conversions: float,
    session_delta: float,
    revenue_delta: float,
) -> str:
    if revenue >= 500 or conversions >= 5:
        if session_delta < 0 or revenue_delta < 0:
            return "Protect / Rescue"
        return "Protect"
    if sessions >= 250 and (revenue > 0 or conversions > 0):
        return "Grow"
    if sessions >= 250 and revenue <= 0 and conversions <= 0:
        return "Monetise"
    if revenue > 0 or conversions > 0:
        return "Monetise"
    if session_delta < -50:
        return "Rescue"
    return "Build / Validate"


def _aggregate_by_slug(
    rows: list[dict[str, Any]],
    website_url: str,
    path_prefix: str,
) -> dict[str, dict[str, Any]]:
    by_slug: dict[str, dict[str, Any]] = {}
    for row in rows:
        landing_page = str(row.get("landing_page") or "")
        slug = collection_slug_from_landing_page(landing_page, path_prefix)
        if not slug:
            continue
        target = by_slug.setdefault(slug, _empty_metrics(slug, _absolute_collection_url(website_url, landing_page)))
        target["sessions"] += _num(row.get("sessions"))
        target["users"] += _num(row.get("users"))
        target["engaged_sessions"] += _num(row.get("engaged_sessions"))
        target["conversions"] += _num(row.get("conversions"))
        target["revenue"] += _num(row.get("revenue"))
        target["purchases"] += _num(row.get("purchases"))
        target["landing_pages"].append(landing_page)
    return by_slug


def _opportunity_row(
    *,
    slug: str,
    current: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    session_delta = current["sessions"] - comparison["sessions"]
    revenue_delta = current["revenue"] - comparison["revenue"]
    conversion_delta = current["conversions"] - comparison["conversions"]
    priority_score = _priority_score(
        sessions=current["sessions"],
        revenue=current["revenue"],
        conversions=current["conversions"],
        purchases=current["purchases"],
        session_delta=session_delta,
        revenue_delta=revenue_delta,
    )
    bucket = classify_priority(
        sessions=current["sessions"],
        revenue=current["revenue"],
        conversions=current["conversions"],
        session_delta=session_delta,
        revenue_delta=revenue_delta,
    )
    return {
        "slug": slug,
        "url": current["url"],
        "priority_bucket": bucket,
        "priority_score": round(priority_score, 2),
        "current": _rounded_metrics(current),
        "comparison": _rounded_metrics(comparison),
        "delta": {
            "sessions": round(session_delta, 2),
            "conversions": round(conversion_delta, 2),
            "revenue": round(revenue_delta, 2),
        },
        "notes": _notes(bucket, current, session_delta, revenue_delta),
    }


def _priority_score(
    *,
    sessions: float,
    revenue: float,
    conversions: float,
    purchases: float,
    session_delta: float,
    revenue_delta: float,
) -> float:
    score = 0.0
    score += min(revenue / 20, 60)
    score += min(sessions / 20, 35)
    score += min(conversions * 5, 30)
    score += min(purchases * 8, 30)
    if session_delta < 0:
        score += min(abs(session_delta) / 15, 20)
    if revenue_delta < 0:
        score += min(abs(revenue_delta) / 25, 20)
    return score


def _notes(bucket: str, current: dict[str, Any], session_delta: float, revenue_delta: float) -> list[str]:
    notes = [f"Bucket: {bucket}."]
    if current["revenue"] > 0:
        notes.append("Revenue-attributed landing page; treat as commercial priority.")
    if current["sessions"] > 0 and current["revenue"] <= 0 and current["conversions"] <= 0:
        notes.append("Traffic without visible revenue/conversions; review intent, merchandising, and copy.")
    if session_delta < 0:
        notes.append("Organic sessions declined versus comparison period.")
    if revenue_delta < 0:
        notes.append("Revenue declined versus comparison period.")
    return notes


def _empty_metrics(slug: str, url: str) -> dict[str, Any]:
    return {
        "slug": slug,
        "url": url,
        "sessions": 0.0,
        "users": 0.0,
        "engaged_sessions": 0.0,
        "conversions": 0.0,
        "revenue": 0.0,
        "purchases": 0.0,
        "landing_pages": [],
    }


def _rounded_metrics(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "sessions": round(float(row.get("sessions") or 0), 2),
        "users": round(float(row.get("users") or 0), 2),
        "engaged_sessions": round(float(row.get("engaged_sessions") or 0), 2),
        "conversions": round(float(row.get("conversions") or 0), 2),
        "revenue": round(float(row.get("revenue") or 0), 2),
        "purchases": round(float(row.get("purchases") or 0), 2),
    }


def _totals(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "sessions": round(sum(float(row["current"]["sessions"]) for row in rows), 2),
        "conversions": round(sum(float(row["current"]["conversions"]) for row in rows), 2),
        "revenue": round(sum(float(row["current"]["revenue"]) for row in rows), 2),
        "purchases": round(sum(float(row["current"]["purchases"]) for row in rows), 2),
    }


def _absolute_collection_url(website_url: str, landing_page: str) -> str:
    if landing_page.startswith(("http://", "https://")):
        parsed = urlparse(landing_page)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    return urljoin(website_url.rstrip("/") + "/", landing_page.lstrip("/")).split("?", 1)[0].rstrip("/")


def _num(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
