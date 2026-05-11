"""Analyse Screaming Frog CLI exports into a compact audit summary.

The script is intentionally tolerant of filename/column drift between SEO Spider
versions. It favours the official Issues Overview export when present and falls
back to counting common tab exports.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            with path.open(newline="", encoding=encoding) as handle:
                return list(csv.DictReader(handle))
        except UnicodeError:
            continue
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _csv_files(export_dir: Path) -> list[Path]:
    return sorted(path for path in export_dir.rglob("*.csv") if path.is_file())


def _norm(value: str) -> str:
    return "".join(char.lower() for char in value if char.isalnum())


def _find_file(files: list[Path], *needles: str) -> Path | None:
    normalised_needles = [_norm(needle) for needle in needles]
    for path in files:
        name = _norm(path.stem)
        if all(needle in name for needle in normalised_needles):
            return path
    return None


def _first_value(row: dict[str, str], *columns: str) -> str:
    lookup = {_norm(key): value for key, value in row.items()}
    for column in columns:
        value = lookup.get(_norm(column))
        if value is not None:
            return value.strip()
    return ""


def _safe_int(value: str) -> int:
    clean = value.replace(",", "").strip()
    if not clean:
        return 0
    try:
        return int(float(clean))
    except ValueError:
        return 0


def _count_rows(files: list[Path], *needles: str) -> int:
    path = _find_file(files, *needles)
    return len(_read_csv(path)) if path else 0


def _parse_internal_rows(files: list[Path]) -> list[dict[str, str]]:
    path = _find_file(files, "internal", "all") or _find_file(files, "internal", "html")
    return _read_csv(path) if path else []


def _parse_issues_overview(files: list[Path]) -> list[dict[str, Any]]:
    path = _find_file(files, "issues", "overview")
    if not path:
        return []

    issues: list[dict[str, Any]] = []
    for row in _read_csv(path):
        issue = _first_value(row, "Issue Name", "Issue", "Name")
        count = _safe_int(_first_value(row, "URLs", "URL Count", "Occurrences", "Count"))
        issue_type = _first_value(row, "Issue Type", "Type")
        priority = _first_value(row, "Issue Priority", "Priority")
        if issue:
            issues.append(
                {
                    "issue": issue,
                    "count": count,
                    "type": issue_type,
                    "priority": priority,
                }
            )
    return sorted(issues, key=lambda item: item["count"], reverse=True)


def _derived_metrics(files: list[Path], internal_rows: list[dict[str, str]]) -> dict[str, int]:
    status_codes: Counter[str] = Counter()
    non_indexable = 0
    for row in internal_rows:
        status = _first_value(row, "Status Code", "Status")
        if status:
            status_codes[status] += 1
        indexability = _first_value(row, "Indexability")
        if indexability and indexability.lower() != "indexable":
            non_indexable += 1

    internal_error_rows = sum(
        count
        for status, count in status_codes.items()
        if status and (status.startswith("4") or status.startswith("5"))
    )

    return {
        "internal_rows": len(internal_rows),
        "internal_3xx": sum(count for status, count in status_codes.items() if status.startswith("3")),
        "internal_4xx_5xx": internal_error_rows,
        "non_indexable": non_indexable,
        "missing_titles": _count_rows(files, "page", "titles", "missing"),
        "duplicate_titles": _count_rows(files, "page", "titles", "duplicate"),
        "long_titles": _count_rows(files, "page", "titles", "over"),
        "missing_meta_descriptions": _count_rows(files, "meta", "description", "missing"),
        "duplicate_meta_descriptions": _count_rows(files, "meta", "description", "duplicate"),
        "missing_h1": _count_rows(files, "h1", "missing"),
        "multiple_h1": _count_rows(files, "h1", "multiple"),
        "missing_canonicals": _count_rows(files, "canonicals", "missing"),
        "canonicalised": _count_rows(files, "canonicals", "canonicalised"),
        "images_missing_alt_text": _count_rows(files, "images", "missing", "alt", "text"),
        "structured_data_validation": _count_rows(files, "structured", "data", "validation"),
        "urls_not_in_sitemap": _count_rows(files, "sitemaps", "urls", "not", "sitemap"),
    }


def analyse_export(export_dir: Path) -> dict[str, Any]:
    files = _csv_files(export_dir)
    internal_rows = _parse_internal_rows(files)
    issues = _parse_issues_overview(files)
    metrics = _derived_metrics(files, internal_rows)

    return {
        "export_dir": str(export_dir),
        "analysed_at": datetime.now(timezone.utc).isoformat(),
        "csv_file_count": len(files),
        "metrics": metrics,
        "top_issues": issues[:15],
        "files": [str(path.relative_to(export_dir)) for path in files],
    }


def _markdown(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    lines = [
        "# Screaming Frog Audit Summary",
        "",
        f"- Export directory: `{summary['export_dir']}`",
        f"- CSV files analysed: {summary['csv_file_count']}",
        f"- Internal rows: {metrics['internal_rows']}",
        f"- Internal 3xx rows: {metrics['internal_3xx']}",
        f"- Internal 4xx/5xx rows: {metrics['internal_4xx_5xx']}",
        f"- Non-indexable rows: {metrics['non_indexable']}",
        "",
        "## Common SEO Checks",
        "",
        "| Check | Count |",
        "|---|---:|",
    ]
    for key in (
        "missing_titles",
        "duplicate_titles",
        "long_titles",
        "missing_meta_descriptions",
        "duplicate_meta_descriptions",
        "missing_h1",
        "multiple_h1",
        "missing_canonicals",
        "canonicalised",
        "images_missing_alt_text",
        "structured_data_validation",
        "urls_not_in_sitemap",
    ):
        lines.append(f"| {key.replace('_', ' ').title()} | {metrics[key]} |")

    if summary["top_issues"]:
        lines.extend(["", "## Top Issues", "", "| Issue | Count | Type | Priority |", "|---|---:|---|---|"])
        for issue in summary["top_issues"][:10]:
            lines.append(
                "| {issue} | {count} | {type} | {priority} |".format(
                    issue=issue["issue"].replace("|", "\\|"),
                    count=issue["count"],
                    type=issue["type"],
                    priority=issue["priority"],
                )
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-dir", required=True, type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    summary = analyse_export(args.export_dir)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(summary, indent=2) + "\n")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(_markdown(summary))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
