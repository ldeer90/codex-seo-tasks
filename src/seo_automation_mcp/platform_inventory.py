from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from googleapiclient.errors import HttpError

from .config import Settings
from .google_clients import GoogleWorkspaceClient


DOCS_DIR = Path("docs")
INVENTORY_JSON = DOCS_DIR / "platform-inventory.json"
REFERENCE_MD = DOCS_DIR / "platform-reference.md"
MONDAY_MCP_SNAPSHOT = DOCS_DIR / "monday-mcp-snapshot.json"
FOLDER_MIME = "application/vnd.google-apps.folder"
MAX_DRIVE_DEPTH = 3
MONDAY_ENDPOINT = "https://api.monday.com/v2"
SE_RANKING_MCP_NAME = "se-ranking"
SE_RANKING_MCP_URL = "https://api.seranking.com/mcp"

GENERIC_CLIENT_NAMES = {
    "agents digital",
    "build vibe app",
    "client board",
    "content board",
    "expenses",
    "google ai studio",
    "heiych",
    "link building",
    "main workspace",
    "mcp getting started",
    "monthly seo task list",
    "sales",
    "screaming frog seo spider",
    "seo tasks",
    "untitled folder",
    "work templates",
}

CLIENT_ALIASES = {
    "acorn car rentals": "acorn rentals",
    "agents digital website": "agents digital",
    "ducati melbourne": "joe rascal ducati",
    "melanit the label": "melani the label",
    "salad servers direct": "salad servers",
    "travelkon app notification": "travelkon",
}


class MondayAPIError(RuntimeError):
    """Raised for Monday GraphQL errors."""


class MondayClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=90) as client:
            response = client.post(
                MONDAY_ENDPOINT,
                headers=headers,
                json={"query": query, "variables": variables or {}},
            )
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            messages = "; ".join(str(error.get("message", error)) for error in payload["errors"])
            raise MondayAPIError(messages)
        return payload.get("data", {})

    def list_workspaces(self) -> list[dict[str, Any]]:
        data = self.query(
            """
            query PlatformInventoryWorkspaces {
              workspaces(limit: 500) {
                id
                name
                description
                kind
                state
                created_at
                is_default_workspace
                owners_subscribers {
                  id
                  name
                  email
                }
              }
            }
            """
        )
        return data.get("workspaces", [])

    def list_boards(self) -> list[dict[str, Any]]:
        return self._list_boards_with_query(self._boards_query(include_optional=True))

    def list_folders_for_workspace(self, workspace_id: str) -> dict[str, Any]:
        queries = [
            """
            query PlatformInventoryFolders($workspaceIds: [ID!]) {
              folders(workspace_ids: $workspaceIds) {
                id
                name
                color
                parent {
                  id
                  name
                }
                children {
                  id
                  name
                }
              }
            }
            """,
            """
            query PlatformInventoryFoldersMinimal($workspaceIds: [ID!]) {
              folders(workspace_ids: $workspaceIds) {
                id
                name
              }
            }
            """,
        ]
        for query in queries:
            try:
                data = self.query(query, {"workspaceIds": [workspace_id]})
                return {"folders": data.get("folders", []), "error": None}
            except MondayAPIError as exc:
                last_error = str(exc)
        return {"folders": [], "error": last_error}

    def list_docs_for_workspace(self, workspace_id: str) -> dict[str, Any]:
        queries = [
            """
            query PlatformInventoryDocs($workspaceIds: [ID!]) {
              docs(workspace_ids: $workspaceIds) {
                id
                name
                workspace_id
                doc_folder_id
              }
            }
            """,
            """
            query PlatformInventoryDocsMinimal($workspaceIds: [ID!]) {
              docs(workspace_ids: $workspaceIds) {
                id
                name
              }
            }
            """,
        ]
        for query in queries:
            try:
                data = self.query(query, {"workspaceIds": [workspace_id]})
                return {"docs": data.get("docs", []), "error": None}
            except MondayAPIError as exc:
                last_error = str(exc)
        return {"docs": [], "error": last_error}

    def _list_boards_with_query(self, query: str) -> list[dict[str, Any]]:
        boards: list[dict[str, Any]] = []
        page = 1
        while True:
            try:
                data = self.query(query, {"limit": 100, "page": page})
            except MondayAPIError:
                if query != self._boards_query(include_optional=False):
                    return self._list_boards_with_query(self._boards_query(include_optional=False))
                raise
            page_boards = data.get("boards", [])
            boards.extend(page_boards)
            if len(page_boards) < 100:
                return boards
            page += 1

    @staticmethod
    def _boards_query(*, include_optional: bool) -> str:
        optional_fields = """
                board_folder_id
                description
                workspace_id
                owners {
                  id
                  name
                  email
                }
        """
        return f"""
            query PlatformInventoryBoards($limit: Int!, $page: Int!) {{
              boards(limit: $limit, page: $page) {{
                id
                name
                board_kind
                state
                url
                items_count
                {optional_fields if include_optional else ""}
                groups {{
                  id
                  title
                  color
                  archived
                  deleted
                }}
                columns {{
                  id
                  title
                  type
                  description
                  settings_str
                }}
              }}
            }}
        """


@dataclass(frozen=True)
class GeneratedFiles:
    inventory_json: Path
    reference_md: Path


class PlatformInventoryGenerator:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()

    def collect(self) -> dict[str, Any]:
        subjects = list(self.settings.google_subject_candidates())
        inventory = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scope": {
                "mode": "structure-only",
                "drive_folder_depth": MAX_DRIVE_DEPTH,
                "exports_drive_file_contents": False,
                "exports_monday_item_bodies": False,
                "scrapes_client_websites": False,
            },
            "credentials": {
                "google_delegated_subjects": subjects,
                "google_output_delegated_subject": self.settings.google_output_delegated_subject,
                "google_site_access_map": self.settings.google_site_access_map_path,
                "monday_api_key_configured": bool(self.settings.monday_api_key),
                "se_ranking_mcp_name": SE_RANKING_MCP_NAME,
                "se_ranking_mcp_url": SE_RANKING_MCP_URL,
                "secrets_redacted": True,
            },
            "google": self._collect_google(subjects),
            "monday": self._collect_monday(),
            "se_ranking": self._collect_se_ranking(),
        }
        inventory["cross_platform_client_map"] = build_cross_platform_client_map(inventory)
        return inventory

    def write(self, inventory: dict[str, Any]) -> GeneratedFiles:
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        INVENTORY_JSON.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
        REFERENCE_MD.write_text(render_markdown_reference(inventory))
        return GeneratedFiles(inventory_json=INVENTORY_JSON, reference_md=REFERENCE_MD)

    def generate(self) -> GeneratedFiles:
        return self.write(self.collect())

    def _collect_google(self, subjects: list[str]) -> dict[str, Any]:
        return {
            "subjects": {
                subject: {
                    "ga4": self._collect_ga4(subject),
                    "drive": self._collect_drive(subject),
                }
                for subject in subjects
            }
        }

    def _collect_ga4(self, subject: str) -> dict[str, Any]:
        client = GoogleWorkspaceClient(self.settings, delegated_subject=subject)
        try:
            admin = client._service("analyticsadmin", "v1beta")
            account_summaries = _paged_account_summaries(admin)
            properties = []
            for account in account_summaries:
                for summary in account.get("propertySummaries", []):
                    property_name = summary.get("property", "")
                    properties.append(
                        {
                            "account": {
                                "name": account.get("displayName", ""),
                                "resource": account.get("account", ""),
                            },
                            "summary": summary,
                            "property": _safe_google_call(
                                lambda name=property_name: admin.properties().get(name=name).execute()
                            ),
                            "data_streams": _safe_google_call(
                                lambda name=property_name: admin.properties()
                                .dataStreams()
                                .list(parent=name, pageSize=200)
                                .execute()
                                .get("dataStreams", [])
                            ),
                        }
                    )
            return {
                "ok": True,
                "account_count": len(account_summaries),
                "property_count": len(properties),
                "properties": properties,
            }
        except Exception as exc:
            return {"ok": False, "error": _error_message(exc), "properties": []}

    def _collect_drive(self, subject: str) -> dict[str, Any]:
        client = GoogleWorkspaceClient(self.settings, delegated_subject=subject)
        try:
            drive = client._service("drive", "v3")
            about = drive.about().get(fields="user(emailAddress,displayName,permissionId)").execute()
            root_folders = list_drive_folders(
                drive,
                q=f"mimeType='{FOLDER_MIME}' and 'root' in parents and trashed=false",
                corpora="user",
            )
            shared_folders = list_drive_folders(
                drive,
                q=f"mimeType='{FOLDER_MIME}' and sharedWithMe=true and trashed=false",
                corpora="user",
            )
            shared_drives = list_shared_drives(drive)
            return {
                "ok": True,
                "about_user": about.get("user", {}),
                "root_folders": [
                    build_drive_folder_tree(drive, folder, max_depth=MAX_DRIVE_DEPTH)
                    for folder in root_folders
                ],
                "shared_with_me_folders": [
                    build_drive_folder_tree(drive, folder, max_depth=MAX_DRIVE_DEPTH)
                    for folder in shared_folders
                ],
                "shared_drives": [
                    {
                        **shared_drive,
                        "top_level_folders": [
                            build_drive_folder_tree(
                                drive,
                                folder,
                                max_depth=MAX_DRIVE_DEPTH,
                                drive_id=shared_drive["id"],
                            )
                            for folder in list_drive_folders(
                                drive,
                                q=(
                                    f"mimeType='{FOLDER_MIME}' and "
                                    f"'{shared_drive['id']}' in parents and trashed=false"
                                ),
                                corpora="drive",
                                driveId=shared_drive["id"],
                            )
                        ],
                    }
                    for shared_drive in shared_drives
                ],
            }
        except Exception as exc:
            return {"ok": False, "error": _error_message(exc)}

    def _collect_monday(self) -> dict[str, Any]:
        if not self.settings.monday_api_key:
            if MONDAY_MCP_SNAPSHOT.exists():
                snapshot = json.loads(MONDAY_MCP_SNAPSHOT.read_text())
                snapshot["source"] = snapshot.get("source") or "monday_mcp_snapshot"
                return snapshot
            return {
                "ok": False,
                "source": "monday_mcp_preferred",
                "error": "MONDAY_API_KEY is not configured. Use monday MCP for interactive inventory.",
                "workspaces": [],
            }
        try:
            monday = MondayClient(self.settings.require_monday_api_key())
            workspaces = monday.list_workspaces()
            boards = monday.list_boards()
            boards_by_workspace = defaultdict(list)
            for board in boards:
                boards_by_workspace[str(board.get("workspace_id", ""))].append(normalise_monday_board(board))
            enriched_workspaces = []
            for workspace in workspaces:
                workspace_id = str(workspace.get("id", ""))
                folders = monday.list_folders_for_workspace(workspace_id)
                docs = monday.list_docs_for_workspace(workspace_id)
                enriched_workspaces.append(
                    {
                        **workspace,
                        "folders": folders["folders"],
                        "folders_error": folders["error"],
                        "docs": docs["docs"],
                        "docs_error": docs["error"],
                        "boards": boards_by_workspace.get(workspace_id, []),
                    }
                )
            unknown_workspace_boards = boards_by_workspace.get("", [])
            return {
                "ok": True,
                "source": "monday_api",
                "workspace_count": len(enriched_workspaces),
                "board_count": len(boards),
                "workspaces": enriched_workspaces,
                "boards_without_workspace": unknown_workspace_boards,
            }
        except Exception as exc:
            return {"ok": False, "error": _error_message(exc), "workspaces": []}

    def _collect_se_ranking(self) -> dict[str, Any]:
        mcp_status = detect_codex_mcp_server(SE_RANKING_MCP_NAME)
        return {
            "ok": bool(mcp_status.get("configured")),
            "source": "remote_mcp",
            "mcp": {
                "name": SE_RANKING_MCP_NAME,
                "url": SE_RANKING_MCP_URL,
                **mcp_status,
            },
            "inventory_scope": "connector mapping only",
            "exports_project_data": False,
            "recommended_uses": [
                "keyword ranking lookups",
                "project and website SEO metrics",
                "competitor and SERP research",
                "site audit data when requested for a client workflow",
            ],
            "guardrails": [
                "Use the remote MCP server instead of storing an SE Ranking API key in this repo.",
                "Keep default reference passes structure-only unless a task requests client/project data.",
                "Do not export keyword lists, competitor data, or audit details into docs unless needed for a report.",
            ],
        }


def _paged_account_summaries(admin: Any) -> list[dict[str, Any]]:
    summaries = []
    token = None
    while True:
        response = admin.accountSummaries().list(pageSize=200, pageToken=token or "").execute()
        summaries.extend(response.get("accountSummaries", []))
        token = response.get("nextPageToken")
        if not token:
            return summaries


def list_drive_folders(drive: Any, **params: Any) -> list[dict[str, Any]]:
    folders = []
    token = None
    while True:
        response = (
            drive.files()
            .list(
                pageSize=100,
                pageToken=token or None,
                fields=(
                    "nextPageToken, files(id,name,webViewLink,parents,driveId,"
                    "createdTime,modifiedTime)"
                ),
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                **params,
            )
            .execute()
        )
        folders.extend(response.get("files", []))
        token = response.get("nextPageToken")
        if not token:
            return sorted(folders, key=lambda item: item.get("name", "").lower())


def list_shared_drives(drive: Any) -> list[dict[str, str]]:
    shared_drives = []
    token = None
    while True:
        response = (
            drive.drives()
            .list(pageSize=100, pageToken=token or None, fields="nextPageToken, drives(id,name)")
            .execute()
        )
        shared_drives.extend(response.get("drives", []))
        token = response.get("nextPageToken")
        if not token:
            return sorted(shared_drives, key=lambda item: item.get("name", "").lower())


def build_drive_folder_tree(
    drive: Any,
    folder: dict[str, Any],
    *,
    max_depth: int,
    depth: int = 1,
    drive_id: str | None = None,
) -> dict[str, Any]:
    node = {
        "id": folder.get("id", ""),
        "name": folder.get("name", ""),
        "url": folder.get("webViewLink", ""),
        "driveId": folder.get("driveId", drive_id or ""),
        "children": [],
    }
    if depth >= max_depth:
        return node
    params: dict[str, Any] = {
        "q": f"mimeType='{FOLDER_MIME}' and '{folder['id']}' in parents and trashed=false",
        "corpora": "drive" if drive_id else "user",
    }
    if drive_id:
        params["driveId"] = drive_id
    node["children"] = [
        build_drive_folder_tree(
            drive,
            child,
            max_depth=max_depth,
            depth=depth + 1,
            drive_id=drive_id,
        )
        for child in list_drive_folders(drive, **params)
    ]
    return node


def normalise_monday_board(board: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": board.get("id", ""),
        "name": board.get("name", ""),
        "url": board.get("url", ""),
        "workspace_id": str(board.get("workspace_id", "")),
        "folder_id": board.get("board_folder_id", ""),
        "kind": board.get("board_kind", ""),
        "state": board.get("state", ""),
        "item_count": board.get("items_count"),
        "owners": board.get("owners", []),
        "groups": [
            {
                "id": group.get("id", ""),
                "title": group.get("title", ""),
                "color": group.get("color", ""),
                "archived": group.get("archived", False),
                "deleted": group.get("deleted", False),
            }
            for group in board.get("groups", [])
        ],
        "columns": [
            {
                "id": column.get("id", ""),
                "title": column.get("title", ""),
                "type": column.get("type", ""),
                "description": column.get("description") or "",
                "settings": parse_column_settings(column.get("settings_str")),
            }
            for column in board.get("columns", [])
        ],
    }


def parse_column_settings(settings_str: str | None) -> Any:
    if not settings_str:
        return {}
    try:
        return json.loads(settings_str)
    except json.JSONDecodeError:
        return settings_str


def build_cross_platform_client_map(inventory: dict[str, Any]) -> dict[str, Any]:
    buckets: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"ga4": [], "drive": [], "monday": [], "subjects": set()}
    )
    for subject, google_data in inventory.get("google", {}).get("subjects", {}).items():
        for item in google_data.get("ga4", {}).get("properties", []):
            summary = item.get("summary", {})
            key = client_key(summary.get("displayName") or item.get("account", {}).get("name", ""))
            if key:
                buckets[key]["ga4"].append(
                    {
                        "subject": subject,
                        "account": item.get("account", {}),
                        "property": summary,
                        "streams": web_stream_summaries(item.get("data_streams")),
                    }
                )
                buckets[key]["subjects"].add(subject)
        drive = google_data.get("drive", {})
        for section in ("root_folders", "shared_with_me_folders"):
            for folder in flatten_drive_folders(drive.get(section, [])):
                key = client_key(folder.get("name", ""))
                if key:
                    buckets[key]["drive"].append(
                        {
                            "subject": subject,
                            "section": section,
                            "id": folder.get("id", ""),
                            "name": folder.get("name", ""),
                            "url": folder.get("url", ""),
                        }
                    )
                    buckets[key]["subjects"].add(subject)
    for workspace in inventory.get("monday", {}).get("workspaces", []):
        for board in workspace.get("boards", []):
            key = client_key(board.get("name", ""))
            if key:
                buckets[key]["monday"].append(
                    {
                        "workspace_id": workspace.get("id", ""),
                        "workspace": workspace.get("name", ""),
                        "board_id": board.get("id", ""),
                        "name": board.get("name", ""),
                        "url": board.get("url", ""),
                    }
                )
    clients = []
    unmatched = {"ga4": [], "drive": [], "monday": []}
    for key, value in sorted(buckets.items()):
        has_ga4 = bool(value["ga4"])
        has_drive = bool(value["drive"])
        has_monday = bool(value["monday"])
        entry = {
            "client_key": key,
            "subjects": sorted(value["subjects"]),
            "ga4": value["ga4"],
            "drive": value["drive"],
            "monday": value["monday"],
        }
        clients.append(entry)
        if has_ga4 and not (has_drive or has_monday):
            unmatched["ga4"].append(key)
        if has_drive and not (has_ga4 or has_monday):
            unmatched["drive"].append(key)
        if has_monday and not (has_ga4 or has_drive):
            unmatched["monday"].append(key)
    return {"clients": clients, "unmatched": unmatched}


def flatten_drive_folders(folders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened = []
    for folder in folders:
        flattened.append(folder)
        flattened.extend(flatten_drive_folders(folder.get("children", [])))
    return flattened


def web_stream_summaries(data_streams: Any) -> list[dict[str, str]]:
    if not isinstance(data_streams, list):
        return []
    summaries = []
    for stream in data_streams:
        web = stream.get("webStreamData", {})
        summaries.append(
            {
                "name": stream.get("displayName", ""),
                "stream": stream.get("name", ""),
                "default_uri": web.get("defaultUri", ""),
                "measurement_id": web.get("measurementId", ""),
            }
        )
    return summaries


def client_key(name: str) -> str:
    value = name.lower()
    value = re.sub(r"\bga4\b", " ", value)
    value = re.sub(r"\bsubitems?\s+of\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = CLIENT_ALIASES.get(value, value)
    if value in GENERIC_CLIENT_NAMES:
        return ""
    return value


def render_markdown_reference(inventory: dict[str, Any]) -> str:
    lines = [
        "# Platform Reference",
        "",
        f"Generated: {inventory['generated_at']}",
        "",
        "This is a structure-only reference for future SEO automation sessions. "
        "It intentionally excludes API keys, private keys, Drive file contents, "
        "Monday item bodies, private updates, SE Ranking project exports, and website scrape content.",
        "",
        "## Credential And Routing Notes",
        "",
        f"- Google delegated subjects: {', '.join(inventory['credentials']['google_delegated_subjects'])}",
        f"- Google output subject: {inventory['credentials'].get('google_output_delegated_subject') or ''}",
        f"- Google site access map: {inventory['credentials'].get('google_site_access_map') or ''}",
        f"- Monday API key configured: {inventory['credentials']['monday_api_key_configured']}",
        (
            f"- SE Ranking MCP: {inventory['credentials'].get('se_ranking_mcp_name') or SE_RANKING_MCP_NAME} "
            f"({inventory['credentials'].get('se_ranking_mcp_url') or SE_RANKING_MCP_URL})"
        ),
        "",
        "## GA4 Inventory",
        "",
        "| Subject | Account | Property | Property ID | Web Streams |",
        "| --- | --- | --- | --- | --- |",
    ]
    for subject, google_data in inventory.get("google", {}).get("subjects", {}).items():
        ga4 = google_data.get("ga4", {})
        for item in ga4.get("properties", []):
            summary = item.get("summary", {})
            streams = web_stream_summaries(item.get("data_streams"))
            stream_text = "<br>".join(
                compact_join([stream["name"], stream["default_uri"], stream["measurement_id"]])
                for stream in streams
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_cell(subject),
                        md_cell(item.get("account", {}).get("name", "")),
                        md_cell(summary.get("displayName", "")),
                        md_cell(summary.get("property", "")),
                        md_cell(stream_text),
                    ]
                )
                + " |"
            )
    lines.extend(["", "## Drive Inventory", ""])
    for subject, google_data in inventory.get("google", {}).get("subjects", {}).items():
        drive = google_data.get("drive", {})
        lines.extend(
            [
                f"### {subject}",
                "",
                f"- My Drive top-level folders: {len(drive.get('root_folders', []))}",
                f"- Shared-with-me folders: {len(drive.get('shared_with_me_folders', []))}",
                f"- Shared drives: {len(drive.get('shared_drives', []))}",
                "",
            ]
        )
        lines.extend(render_folder_section("My Drive", drive.get("root_folders", [])))
        lines.extend(render_folder_section("Shared With Me", drive.get("shared_with_me_folders", [])))
    lines.extend(["", "## Monday.com Inventory", ""])
    monday = inventory.get("monday", {})
    lines.extend(
        [
            f"- Workspaces: {monday.get('workspace_count', 0)}",
            f"- Boards: {monday.get('board_count', 0)}",
            "",
        ]
    )
    for workspace in monday.get("workspaces", []):
        lines.extend(
            [
                f"### {workspace.get('name', '')}",
                "",
                f"- Workspace ID: `{workspace.get('id', '')}`",
                f"- Boards: {len(workspace.get('boards', []))}",
                f"- Folders: {len(workspace.get('folders', []))}",
                f"- Docs: {len(workspace.get('docs', []))}",
                "",
                "| Board | Board ID | Items | Groups | Columns |",
                "| --- | --- | ---: | ---: | ---: |",
            ]
        )
        for board in workspace.get("boards", []):
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_cell(board.get("name", "")),
                        md_cell(board.get("id", "")),
                        md_cell(str(board.get("item_count") or 0)),
                        md_cell(str(len(board.get("groups", [])))),
                        md_cell(str(len(board.get("columns", [])))),
                    ]
                )
                + " |"
            )
        lines.append("")
    se_ranking = inventory.get("se_ranking", {})
    mcp = se_ranking.get("mcp", {})
    lines.extend(
        [
            "## SE Ranking Inventory",
            "",
            f"- MCP server: `{mcp.get('name') or SE_RANKING_MCP_NAME}`",
            f"- URL: {mcp.get('url') or SE_RANKING_MCP_URL}",
            f"- Configured in Codex: {mcp.get('configured')}",
            f"- Status: {mcp.get('status') or ''}",
            f"- Auth: {mcp.get('auth') or 'MCP/client-managed'}",
            f"- Inventory scope: {se_ranking.get('inventory_scope') or 'connector mapping only'}",
            f"- Exports project data: {se_ranking.get('exports_project_data', False)}",
            "",
            "Recommended uses:",
            "",
        ]
    )
    for use in se_ranking.get("recommended_uses", []):
        lines.append(f"- {use}")
    lines.extend(["", "Guardrails:", ""])
    for guardrail in se_ranking.get("guardrails", []):
        lines.append(f"- {guardrail}")
    lines.append("")
    lines.extend(["## Cross-Platform Client Map", ""])
    lines.extend(
        [
            "| Client Key | GA4 | Drive | Monday | Subjects |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for entry in inventory.get("cross_platform_client_map", {}).get("clients", []):
        lines.append(
            "| "
            + " | ".join(
                [
                    md_cell(entry["client_key"]),
                    str(len(entry["ga4"])),
                    str(len(entry["drive"])),
                    str(len(entry["monday"])),
                    md_cell(", ".join(entry["subjects"])),
                ]
            )
            + " |"
        )
    unmatched = inventory.get("cross_platform_client_map", {}).get("unmatched", {})
    lines.extend(
        [
            "",
            "## Unmatched Structure Names",
            "",
            f"- GA4 only: {', '.join(unmatched.get('ga4', [])) or 'None'}",
            f"- Drive only: {', '.join(unmatched.get('drive', [])) or 'None'}",
            f"- Monday only: {', '.join(unmatched.get('monday', [])) or 'None'}",
            "",
        ]
    )
    return "\n".join(lines)


def render_folder_section(title: str, folders: list[dict[str, Any]]) -> list[str]:
    if not folders:
        return [f"#### {title}", "", "- None", ""]
    lines = [f"#### {title}", ""]
    for folder in folders:
        lines.extend(render_folder_tree(folder))
    lines.append("")
    return lines


def render_folder_tree(folder: dict[str, Any], depth: int = 0) -> list[str]:
    indent = "  " * depth
    lines = [f"{indent}- {folder.get('name', '')} (`{folder.get('id', '')}`)"]
    for child in folder.get("children", []):
        lines.extend(render_folder_tree(child, depth + 1))
    return lines


def compact_join(values: list[str]) -> str:
    return " - ".join(value for value in values if value)


def md_cell(value: Any) -> str:
    text = str(value or "")
    return text.replace("|", "\\|").replace("\n", "<br>")


def _safe_google_call(call: Any) -> Any:
    try:
        return call()
    except HttpError as exc:
        return {"error": _error_message(exc)}


def _error_message(exc: Exception) -> str:
    if isinstance(exc, HttpError):
        try:
            payload = json.loads(exc.content.decode("utf-8"))
            return payload.get("error", {}).get("message") or str(exc)
        except Exception:
            return str(exc)
    return str(exc)


def detect_codex_mcp_server(name: str) -> dict[str, Any]:
    codex = shutil.which("codex")
    if not codex:
        return {
            "configured": None,
            "status": "codex_cli_unavailable",
            "auth": "",
        }
    try:
        completed = subprocess.run(
            [codex, "mcp", "list"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except Exception as exc:
        return {
            "configured": None,
            "status": "codex_mcp_list_failed",
            "auth": "",
            "error": _error_message(exc),
        }
    if completed.returncode != 0:
        return {
            "configured": None,
            "status": "codex_mcp_list_failed",
            "auth": "",
        }
    for line in completed.stdout.splitlines():
        fields = line.split()
        if fields and fields[0] == name:
            return {
                "configured": True,
                "listed_url": fields[1] if len(fields) > 1 else "",
                "status": fields[3] if len(fields) > 3 else "",
                "auth": fields[4] if len(fields) > 4 else "",
            }
    return {
        "configured": False,
        "status": "not_listed",
        "auth": "",
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SEO Automation platform tools")
    parser.add_argument(
        "--client-folders",
        action="store_true",
        help=(
            "Scan 1-2 levels of subfolders inside each client Drive folder "
            "and write docs/client-folder-map.json. "
            "Does not touch any other files."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override output path for --client-folders (default: docs/client-folder-map.json)",
    )
    args = parser.parse_args()

    if args.client_folders:
        scan_client_folders_main(output_path=args.output)
    else:
        generated = PlatformInventoryGenerator().generate()
        print(f"Wrote {generated.inventory_json}")
        print(f"Wrote {generated.reference_md}")


# ---------------------------------------------------------------------------
# Client folder scanner (Path A from the session brief)
# ---------------------------------------------------------------------------

# Canonical list of client folders under Agents Digital / Clients.
# Keys match the client slug in docs/agent/clients/*.md.
# Update this table when a new client is onboarded.
CLIENT_FOLDERS: list[tuple[str, str]] = [
    ("_ CLIENT TEMPLATE",        "1NSxmr_AUHoweWrFfKotEvBiJ88zdwOPZ"),
    ("Acorn Rentals",            "1M2MXfkRFsAMy5nFoM2m7miNOnjBEkvoj"),
    ("AVENUE Hampers",           "1LGXJQosWUROG5s4MVxbNaFgMvXFd90en"),
    ("Joe Rascal",               "14gHf6UZjgZ751CUP6iLz3Sf6WTTQBWSN"),
    ("Joe Rascal Ducati",        "157-ddATrb2byi0VMJYKg9JET4RzqIFFr"),
    ("Joe Rascal Harley",        "1XENbhUku8qau7HM5I7D9ivtIhrKpfU0s"),
    ("Little Shop of Happiness", "1wN3HSAcKrkXRLxuFA0OlHyGDqLDo9hx7"),
    ("Melani the Label",         "1HWLcsHS38P5u_d_vfrWux3LaRVln9iMJ"),
    ("New Client Forms",         "1eFoEqwgMyuWyMbQuOZZAzK4xtfQTB7Ao"),
    ("Salad Servers",            "1VTJy6FaSqLkOyRxaf7ZiAQuoIQVXatyf"),
    ("Shop Rongrong",            "1TTxwqCl5JurXCyva9kGK9rz5v66YzaXU"),
    ("TravelKon",                "175zcM_g56_jtpU1m9bzAMFvLFahXAqS3"),
]

# Preferred subjects to try, in order.  hello@ owns the tree; seo@ has read access.
_SCAN_SUBJECTS = ("hello@agents.digital", "seo@agents.digital")


def _drive_for_subject(settings: Settings, subject: str) -> Any:
    return GoogleWorkspaceClient(settings, delegated_subject=subject)._service("drive", "v3")


def scan_client_folder(
    settings: Settings,
    folder_id: str,
    folder_name: str,
    *,
    depth: int = 2,
) -> dict[str, Any]:
    """Return a folder-tree dict for *folder_id*, trying each subject in turn."""
    stub: dict[str, Any] = {"id": folder_id, "name": folder_name, "webViewLink": ""}
    last_error: str = ""
    for subject in _SCAN_SUBJECTS:
        try:
            drive = _drive_for_subject(settings, subject)
            tree = build_drive_folder_tree(drive, stub, max_depth=depth)
            return {
                "folder_id": folder_id,
                "subject_used": subject,
                "tree": tree,
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            last_error = _error_message(exc)
    return {
        "folder_id": folder_id,
        "subject_used": None,
        "tree": None,
        "error": last_error,
    }


def scan_all_client_folders(
    settings: Settings | None = None,
    *,
    depth: int = 2,
) -> dict[str, Any]:
    """Scan all known client folders and return a mapping keyed by client name."""
    settings = settings or Settings.from_env()
    results: dict[str, Any] = {}
    for name, folder_id in CLIENT_FOLDERS:
        print(f"  scanning {name} ({folder_id}) …")
        results[name] = scan_client_folder(settings, folder_id, name, depth=depth)
    return results


def scan_client_folders_main(output_path: str | None = None) -> None:
    """CLI entry point for --client-folders."""
    settings = Settings.from_env()
    output = Path(output_path) if output_path else DOCS_DIR / "client-folder-map.json"
    print(f"Scanning client Drive folders (depth=2) → {output}")
    results = scan_all_client_folders(settings)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2))
    ok = sum(1 for v in results.values() if v.get("tree") is not None)
    failed = sum(1 for v in results.values() if v.get("tree") is None)
    print(f"Done. {ok} folders scanned, {failed} failed.")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
