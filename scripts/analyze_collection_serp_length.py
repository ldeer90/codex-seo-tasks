"""Summarise competitor collection copy length from a saved SERP scrape review.

Input rows should include `descriptive_word_estimate`, `name`, and `url`.
The output gives a pragmatic target range for collection body copy. It is a
guide for Codex judgement, not an instruction to pad copy to match noisy pages.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def analyse(rows: list[dict[str, Any]]) -> dict[str, Any]:
    usable = [
        row for row in rows
        if isinstance(row, dict)
        and not row.get("error")
        and 120 <= int(row.get("descriptive_word_estimate") or 0) <= 1800
    ]
    counts = sorted(int(row.get("descriptive_word_estimate") or 0) for row in usable)
    if not counts:
        return {
            "ok": False,
            "message": "No usable competitor length estimates found.",
            "recommended_min_words": 220,
            "recommended_max_words": 320,
            "basis": "fallback",
        }

    median = int(statistics.median(counts))
    lower = _percentile(counts, 0.25)
    upper = _percentile(counts, 0.75)
    target_min = max(220, min(350, lower))
    target_max = max(target_min + 80, min(650, upper if upper >= 300 else median + 120))
    if median >= 650:
        target_max = max(target_max, 700)
    return {
        "ok": True,
        "competitors_used": len(usable),
        "word_estimates": counts,
        "median_words": median,
        "recommended_min_words": int(target_min),
        "recommended_max_words": int(target_max),
        "basis": "trimmed competitor descriptive copy estimates",
        "notes": [
            "Ignore obvious product-card/nav noise and blocked pages.",
            "Use the range to guide useful depth, not to pad copy.",
            "If top pages include FAQs/bottom SEO blocks, consider adding a concise FAQ or extra H3 section only when Shopify layout allows it.",
        ],
        "sources": [
            {
                "name": row.get("name"),
                "url": row.get("url"),
                "descriptive_word_estimate": int(row.get("descriptive_word_estimate") or 0),
            }
            for row in usable
        ],
    }


def _percentile(values: list[int], q: float) -> int:
    if not values:
        return 0
    idx = round((len(values) - 1) * q)
    return int(values[idx])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serp-length-json", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = json.loads(args.serp_length_json.read_text())
    if not isinstance(rows, list):
        raise SystemExit("SERP length JSON must be a list of rows.")
    result = analyse(rows)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text)
        print(f"Wrote SERP length analysis to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
