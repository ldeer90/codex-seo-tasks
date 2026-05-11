"""Run Screaming Frog SEO Spider headlessly for an LD SEO client audit."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_screaming_frog_export import analyse_export  # noqa: E402
from seo_automation_mcp.config import Settings  # noqa: E402
from seo_automation_mcp.google_clients import GoogleWorkspaceClient  # noqa: E402


DEFAULT_CLI = (
    "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/"
    "ScreamingFrogSEOSpiderLauncher"
)
DEFAULT_CONFIG = ROOT / "Codex Shopify Standard SEO Spider Config.seospiderconfig"

DEFAULT_EXPORT_TABS = [
    "Internal:All",
    "Response Codes:Internal All",
    "Page Titles:All",
    "Page Titles:Missing",
    "Page Titles:Duplicate",
    "Meta Description:All",
    "Meta Description:Missing",
    "Meta Description:Duplicate",
    "H1:All",
    "H1:Missing",
    "H1:Multiple",
    "H2:All",
    "Canonicals:All",
    "Canonicals:Missing",
    "Canonicals:Canonicalised",
    "Directives:All",
    "Images:Missing Alt Text",
    "Structured Data:All",
    "Structured Data:Validation Errors",
    "Sitemaps:All",
    "Sitemaps:URLs not in Sitemap",
]

DEFAULT_BULK_EXPORTS = [
    "Issues:All",
    "Links:All Inlinks",
    "Links:All Outlinks",
    "Response Codes:Internal:Internal All Error (4xx 5xx & No Response) Inlinks",
    "Images:Images Missing Alt Text Inlinks",
    "Canonicals:Non-Indexable Canonical Inlinks",
]

DEFAULT_REPORTS = [
    "Crawl Overview",
    "Issues Overview",
    "Redirects:Redirect Chains",
    "Canonicals:Non-Indexable Canonicals",
    "Structured Data:Validation Errors & Warnings Summary",
    "HTTP Headers:HTTP Header Summary",
]


def _slug(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in value]
    return "-".join("".join(chars).split("-"))


def _load_client(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _client_start_url(client: dict[str, Any]) -> str:
    domain = client["domain"].strip()
    if domain.startswith(("http://", "https://")):
        return domain
    return f"https://{domain}"


def _command(
    *,
    cli_path: Path,
    crawl_mode: str,
    start_url: str,
    config: Path,
    output_dir: Path,
    export_format: str,
    task_name: str,
    export_tabs: list[str],
    bulk_exports: list[str],
    reports: list[str],
    save_crawl: bool,
) -> list[str]:
    command = [
        str(cli_path),
        "--crawl-sitemap" if crawl_mode == "sitemap" else "--crawl",
        start_url,
        "--headless",
        "--config",
        str(config),
        "--output-folder",
        str(output_dir),
        "--export-format",
        export_format,
        "--overwrite",
        "--task-name",
        task_name,
        "--export-tabs",
        ",".join(export_tabs),
        "--bulk-export",
        ",".join(bulk_exports),
        "--save-report",
        ",".join(reports),
    ]
    if save_crawl:
        command.append("--save-crawl")
    return command


def _write_manifest(
    *,
    path: Path,
    client: dict[str, Any],
    start_url: str,
    config: Path,
    command: list[str],
    completed: subprocess.CompletedProcess[str],
    summary: dict[str, Any],
    drive_upload: dict[str, str] | None,
) -> None:
    manifest = {
        "client": client["client"],
        "domain": client.get("domain"),
        "start_url": start_url,
        "config": str(config),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "returncode": completed.returncode,
        "command": command,
        "summary": summary,
        "drive_upload": drive_upload,
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n")


def _zip_dir(source_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file() and path != zip_path:
                archive.write(path, path.relative_to(source_dir))


def _upload_zip(zip_path: Path, *, title: str, folder_id: str) -> dict[str, str]:
    settings = Settings.from_env()
    google = GoogleWorkspaceClient(settings, delegated_subject=settings.google_output_delegated_subject)
    return google.upload_file(
        zip_path,
        title=title,
        folder_id=folder_id,
        mime_type="application/zip",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--start-url")
    parser.add_argument(
        "--crawl-mode",
        choices=["spider", "sitemap"],
        default="spider",
        help="Use spider mode from the start URL or sitemap mode from a sitemap URL.",
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG, type=Path)
    parser.add_argument("--cli-path", default=os.getenv("SCREAMING_FROG_CLI", DEFAULT_CLI), type=Path)
    parser.add_argument("--output-root", default=ROOT / "var" / "screaming-frog", type=Path)
    parser.add_argument("--export-format", choices=["csv", "xls", "xlsx", "gsheet"], default="csv")
    parser.add_argument("--save-crawl", action="store_true")
    parser.add_argument("--upload-to-drive", action="store_true")
    parser.add_argument("--drive-folder-id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = _load_client(args.client_json)
    start_url = args.start_url or (
        f"{_client_start_url(client).rstrip('/')}/sitemap.xml"
        if args.crawl_mode == "sitemap"
        else _client_start_url(client)
    )
    run_slug = f"{date.today().isoformat()}-{_slug(client['client'])}-screaming-frog-{args.crawl_mode}"
    output_dir = args.output_root / run_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    task_name = f"{client['client']} Screaming Frog Audit {date.today().isoformat()}"

    command = _command(
        cli_path=args.cli_path,
        crawl_mode=args.crawl_mode,
        start_url=start_url,
        config=args.config,
        output_dir=output_dir,
        export_format=args.export_format,
        task_name=task_name,
        export_tabs=DEFAULT_EXPORT_TABS,
        bulk_exports=DEFAULT_BULK_EXPORTS,
        reports=DEFAULT_REPORTS,
        save_crawl=args.save_crawl,
    )

    if args.dry_run:
        print(json.dumps({"command": command, "output_dir": str(output_dir)}, indent=2))
        return

    if not args.cli_path.exists():
        raise SystemExit(f"Screaming Frog CLI not found: {args.cli_path}")
    if not args.config.exists():
        raise SystemExit(f"Screaming Frog config not found: {args.config}")

    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (output_dir / "screaming-frog.stdout.log").write_text(completed.stdout)
    (output_dir / "screaming-frog.stderr.log").write_text(completed.stderr)
    if completed.returncode != 0:
        raise SystemExit(
            f"Screaming Frog exited with {completed.returncode}. "
            f"See {output_dir / 'screaming-frog.stderr.log'}"
        )

    summary = analyse_export(output_dir)
    summary_json = output_dir / "analysis-summary.json"
    summary_md = output_dir / "analysis-summary.md"
    summary_json.write_text(json.dumps(summary, indent=2) + "\n")
    # Reuse the analysis script for markdown if needed by downstream workflows.
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("analyze_screaming_frog_export.py")),
            "--export-dir",
            str(output_dir),
            "--markdown-output",
            str(summary_md),
        ],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )

    drive_upload = None
    if args.upload_to_drive:
        folder_id = args.drive_folder_id or client.get("drive", {}).get("folders", {}).get("03_audits")
        if not folder_id:
            raise SystemExit("No Drive folder id supplied and client sidecar has no drive.folders.03_audits")
        zip_path = output_dir.with_suffix(".zip")
        if zip_path.exists():
            zip_path.unlink()
        _zip_dir(output_dir, zip_path)
        shutil.copy2(zip_path, output_dir / zip_path.name)
        drive_upload = _upload_zip(
            zip_path,
            title=f"{client['client']} - Screaming Frog Export - {date.today().isoformat()}.zip",
            folder_id=folder_id,
        )

    _write_manifest(
        path=output_dir / "manifest.json",
        client=client,
        start_url=start_url,
        config=args.config,
        command=command,
        completed=completed,
        summary=summary,
        drive_upload=drive_upload,
    )
    print(json.dumps({"output_dir": str(output_dir), "summary": summary, "drive_upload": drive_upload}, indent=2))


if __name__ == "__main__":
    main()
