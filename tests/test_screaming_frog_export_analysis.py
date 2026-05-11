from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from analyze_screaming_frog_export import analyse_export  # noqa: E402


def test_analyse_export_uses_issues_overview_and_tab_counts(tmp_path: Path) -> None:
    (tmp_path / "internal_all.csv").write_text(
        "Address,Status Code,Indexability\n"
        "https://example.com/,200,Indexable\n"
        "https://example.com/old,301,Non-Indexable\n"
        "https://example.com/missing,404,Non-Indexable\n"
    )
    (tmp_path / "issues_overview.csv").write_text(
        "Issue Name,URLs,Issue Type,Issue Priority\n"
        "Missing Meta Description,12,Issue,Medium\n"
        "Missing H1,2,Issue,High\n"
    )
    (tmp_path / "page_titles_missing.csv").write_text("Address\nhttps://example.com/no-title\n")
    (tmp_path / "meta_description_missing.csv").write_text(
        "Address\nhttps://example.com/a\nhttps://example.com/b\n"
    )
    (tmp_path / "h1_missing.csv").write_text("Address\nhttps://example.com/no-h1\n")

    summary = analyse_export(tmp_path)

    assert summary["csv_file_count"] == 5
    assert summary["metrics"]["internal_rows"] == 3
    assert summary["metrics"]["internal_3xx"] == 1
    assert summary["metrics"]["internal_4xx_5xx"] == 1
    assert summary["metrics"]["non_indexable"] == 2
    assert summary["metrics"]["missing_titles"] == 1
    assert summary["metrics"]["missing_meta_descriptions"] == 2
    assert summary["metrics"]["missing_h1"] == 1
    assert summary["top_issues"][0]["issue"] == "Missing Meta Description"
    assert summary["top_issues"][0]["count"] == 12
