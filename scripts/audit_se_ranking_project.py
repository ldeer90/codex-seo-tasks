"""Audit a SE Ranking project's keyword list — find 0-volume, low-volume, and duplicate keywords for cleanup.

Run mode (offline): you supply a JSON dump of `PROJECT_listKeywords` (so the script can be run in repo-only context). Volume data must also be pre-fetched and supplied as a {keyword: volume} dict.

Workflow context: from inside the agent harness, fetch listKeywords + getSearchVolume via MCP, dump both to /tmp, then run this script. Outputs a deletion-candidate JSON ready to feed into PROJECT_deleteKeywords.

Usage:
    python scripts/audit_se_ranking_project.py \
        --keywords-json /tmp/<client>-keywords.json \
        --volumes-json  /tmp/<client>-volumes.json \
        --brand-terms 'avenue hampers,my brand' \
        --min-volume 50 \
        --output /tmp/<client>-audit.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


def normalise(kw: str) -> str:
    """Collapse for dedup: lowercase, strip apostrophes/hyphens, single spaces."""
    return re.sub(r"\s+", " ", re.sub(r"[\-''’]", "", kw.lower())).strip()


def find_duplicates(keywords: list[dict]) -> list[int]:
    """Return IDs of duplicate keywords (keeps first lowercase variant)."""
    by_norm = defaultdict(list)
    for k in keywords:
        by_norm[normalise(k["name"])].append(k)
    drop_ids = []
    for norm, kws in by_norm.items():
        if len(kws) <= 1:
            continue
        # Keep the lowercase / lowest-id one
        kept = sorted(kws, key=lambda x: (not x["name"].islower(), int(x["id"])))[0]
        for k in kws:
            if k["id"] != kept["id"]:
                drop_ids.append(int(k["id"]))
    return drop_ids


def is_brand(name: str, brand_terms: list[str]) -> bool:
    n = name.lower()
    return any(b.lower() in n for b in brand_terms)


def audit(
    keywords: list[dict],
    volumes: dict[str, int],
    *,
    brand_terms: list[str],
    min_volume: int = 50,
) -> dict:
    """Categorise each keyword and produce a deletion proposal."""
    by_id = {int(k["id"]): k["name"] for k in keywords}
    dupe_ids = find_duplicates(keywords)

    zero, low, ok, brand_protected = [], [], [], []
    for k in keywords:
        kid = int(k["id"])
        name = k["name"]
        v = volumes.get(name, volumes.get(name.lower(), 0))
        rec = {"id": kid, "name": name, "vol": v}
        if is_brand(name, brand_terms):
            brand_protected.append(rec)
            continue
        if v == 0:
            zero.append(rec)
        elif v < min_volume:
            low.append(rec)
        else:
            ok.append(rec)

    delete_ids = list({r["id"] for r in zero} | {r["id"] for r in low} | set(dupe_ids))
    # Brand-protect everywhere
    delete_ids = [i for i in delete_ids if not is_brand(by_id[i], brand_terms)]

    return {
        "summary": {
            "total": len(keywords),
            "zero_volume": len(zero),
            "low_volume": len(low),
            "ok_volume": len(ok),
            "duplicates": len(dupe_ids),
            "brand_protected": len(brand_protected),
            "to_delete": len(delete_ids),
            "retained_after_cleanup": len(keywords) - len(delete_ids),
        },
        "delete_ids": sorted(delete_ids),
        "delete_with_reason": sorted(zero + low, key=lambda x: x["vol"]),
        "kept": sorted(ok, key=lambda x: -x["vol"]),
        "brand_protected": brand_protected,
        "duplicate_ids": dupe_ids,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--keywords-json", required=True, type=Path,
                   help="Output of PROJECT_listKeywords (the .data array)")
    p.add_argument("--volumes-json", required=True, type=Path,
                   help="Dict of {keyword: volume}")
    p.add_argument("--brand-terms", default="",
                   help="Comma-separated brand terms to protect from deletion")
    p.add_argument("--min-volume", type=int, default=50)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    raw = json.loads(args.keywords_json.read_text())
    keywords = raw.get("data", raw)
    volumes = json.loads(args.volumes_json.read_text())
    brand_terms = [t.strip() for t in args.brand_terms.split(",") if t.strip()]

    result = audit(keywords, volumes, brand_terms=brand_terms, min_volume=args.min_volume)
    args.output.write_text(json.dumps(result, indent=2))

    s = result["summary"]
    print("Audit complete:")
    print(f"  Total:            {s['total']}")
    print(f"  Zero volume:      {s['zero_volume']}")
    print(f"  Low volume <{args.min_volume}: {s['low_volume']}")
    print(f"  Duplicates:       {s['duplicates']}")
    print(f"  Brand-protected:  {s['brand_protected']}")
    print(f"  → DELETE:         {s['to_delete']}")
    print(f"  → RETAIN:         {s['retained_after_cleanup']}")
    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
