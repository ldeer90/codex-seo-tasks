from __future__ import annotations

import mimetypes
from datetime import date
from pathlib import Path
from typing import Any

from .config import Settings


GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


class GoogleWorkspaceClient:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        delegated_subject: str | None = None,
    ) -> None:
        self.settings = settings or Settings.from_env()
        self.credentials_path = self.settings.require_google_credentials()
        self.delegated_subject = delegated_subject or self.settings.google_delegated_subject
        self._credentials = None

    @property
    def credentials(self) -> Any:
        if self._credentials is None:
            from google.oauth2 import service_account

            self._credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=GOOGLE_SCOPES,
            )
            if self.delegated_subject:
                self._credentials = self._credentials.with_subject(self.delegated_subject)
        return self._credentials

    def _service(self, name: str, version: str) -> Any:
        from googleapiclient.discovery import build

        return build(name, version, credentials=self.credentials, cache_discovery=False)

    def create_sheet(
        self,
        title: str,
        values: list[list[Any]],
        *,
        folder_id: str | None = None,
    ) -> dict[str, str]:
        sheets = self._service("sheets", "v4")
        created = (
            sheets.spreadsheets()
            .create(body={"properties": {"title": title}}, fields="spreadsheetId,spreadsheetUrl")
            .execute()
        )
        spreadsheet_id = created["spreadsheetId"]
        if values:
            (
                sheets.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range="A1",
                    valueInputOption="RAW",
                    body={"values": values},
                )
                .execute()
            )
            self._auto_resize_sheet(spreadsheet_id, len(values[0]))
        target_folder = folder_id or self.settings.require_reports_folder_id()
        self._move_to_folder(spreadsheet_id, target_folder)
        return {
            "id": spreadsheet_id,
            "url": created.get(
                "spreadsheetUrl", f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            ),
        }

    def overwrite_sheet_values(
        self,
        spreadsheet_id: str,
        values: list[list[Any]],
        *,
        sheet_name: str = "Untitled",
    ) -> dict[str, str]:
        """Replace plain values in a Google Sheet tab."""
        sheets = self._service("sheets", "v4")
        quoted_sheet = _quote_sheet_name(sheet_name)
        sheets.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"{quoted_sheet}!A:Z",
            body={},
        ).execute()
        if values:
            sheets.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{quoted_sheet}!A1",
                valueInputOption="RAW",
                body={"values": values},
            ).execute()
            self._auto_resize_sheet(spreadsheet_id, len(values[0]))
        return {
            "id": spreadsheet_id,
            "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
        }

    def create_doc(
        self,
        title: str,
        text: str,
        *,
        folder_id: str | None = None,
    ) -> dict[str, str]:
        docs = self._service("docs", "v1")
        created = docs.documents().create(body={"title": title}).execute()
        document_id = created["documentId"]
        self.overwrite_doc_text(document_id, text)
        target_folder = folder_id or self.settings.require_reports_folder_id()
        self._move_to_folder(document_id, target_folder)
        return {
            "id": document_id,
            "url": f"https://docs.google.com/document/d/{document_id}/edit",
        }

    def upload_file(
        self,
        path: str | Path,
        *,
        title: str | None = None,
        folder_id: str | None = None,
        mime_type: str | None = None,
    ) -> dict[str, str]:
        drive = self._service("drive", "v3")
        file_path = Path(path)
        target_folder = folder_id or self.settings.require_reports_folder_id()
        resolved_mime_type = mime_type or mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

        from googleapiclient.http import MediaFileUpload

        media = MediaFileUpload(str(file_path), mimetype=resolved_mime_type, resumable=True)
        created = (
            drive.files()
            .create(
                body={
                    "name": title or file_path.name,
                    "parents": [target_folder],
                },
                media_body=media,
                fields="id, webViewLink",
            )
            .execute()
        )
        file_id = created["id"]
        return {
            "id": file_id,
            "url": created.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view"),
        }

    def overwrite_doc_text(self, document_id: str, text: str) -> dict[str, str]:
        """Replace the body text of an existing Google Doc."""
        docs = self._service("docs", "v1")
        document = docs.documents().get(documentId=document_id).execute()
        content = document.get("body", {}).get("content", [])
        end_index = content[-1].get("endIndex", 1) if content else 1
        requests: list[dict[str, Any]] = []
        if end_index > 2:
            requests.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index - 1}}})
        if text:
            requests.append({"insertText": {"location": {"index": 1}, "text": text}})
        if requests:
            docs.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
        return {
            "id": document_id,
            "url": f"https://docs.google.com/document/d/{document_id}/edit",
        }

    def run_ga4_report(
        self,
        *,
        ga4_property_id: str,
        start_date: str,
        end_date: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        analytics = self._service("analyticsdata", "v1beta")
        body = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [
                {"name": "landingPagePlusQueryString"},
                {"name": "sessionDefaultChannelGroup"},
            ],
            "metrics": [
                {"name": "sessions"},
                {"name": "totalUsers"},
                {"name": "engagedSessions"},
                {"name": "conversions"},
            ],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "sessionDefaultChannelGroup",
                    "stringFilter": {"matchType": "EXACT", "value": "Organic Search"},
                }
            },
            "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
            "limit": limit,
        }
        response = (
            analytics.properties()
            .runReport(property=ga4_property_id, body=body)
            .execute()
        )
        return self._parse_ga4_rows(response)

    def run_ga4_landing_page_report(
        self,
        *,
        ga4_property_id: str,
        start_date: str,
        end_date: str,
        limit: int,
        channel: str = "Organic Search",
        path_prefix: str | None = None,
        order_metric: str = "sessions",
    ) -> list[dict[str, Any]]:
        allowed_order_metrics = {"sessions", "totalRevenue", "conversions", "ecommercePurchases"}
        if order_metric not in allowed_order_metrics:
            raise ValueError(f"Unsupported GA4 order metric: {order_metric}")

        analytics = self._service("analyticsdata", "v1beta")
        filters: list[dict[str, Any]] = [
            {
                "filter": {
                    "fieldName": "sessionDefaultChannelGroup",
                    "stringFilter": {"matchType": "EXACT", "value": channel},
                }
            }
        ]
        if path_prefix:
            filters.append(
                {
                    "filter": {
                        "fieldName": "landingPagePlusQueryString",
                        "stringFilter": {"matchType": "BEGINS_WITH", "value": path_prefix},
                    }
                }
            )
        body = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [
                {"name": "landingPagePlusQueryString"},
                {"name": "sessionDefaultChannelGroup"},
            ],
            "metrics": [
                {"name": "sessions"},
                {"name": "totalUsers"},
                {"name": "engagedSessions"},
                {"name": "conversions"},
                {"name": "totalRevenue"},
                {"name": "ecommercePurchases"},
            ],
            "dimensionFilter": {"andGroup": {"expressions": filters}},
            "orderBys": [{"metric": {"metricName": order_metric}, "desc": True}],
            "limit": limit,
        }
        response = analytics.properties().runReport(property=ga4_property_id, body=body).execute()
        return self._parse_ga4_rows(response)

    def get_ga4_property(self, ga4_property_id: str) -> dict[str, Any]:
        admin = self._service("analyticsadmin", "v1beta")
        return admin.properties().get(name=ga4_property_id).execute()

    def _parse_ga4_rows(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in response.get("rows", []):
            dimensions = row.get("dimensionValues", [])
            metrics = row.get("metricValues", [])
            rows.append(
                {
                    "landing_page": dimensions[0].get("value", "") if dimensions else "",
                    "channel": dimensions[1].get("value", "") if len(dimensions) > 1 else "",
                    "sessions": _number(metrics, 0),
                    "users": _number(metrics, 1),
                    "engaged_sessions": _number(metrics, 2),
                    "conversions": _number(metrics, 3),
                    "revenue": _number(metrics, 4),
                    "purchases": _number(metrics, 5),
                }
            )
        return rows

    def _auto_resize_sheet(self, spreadsheet_id: str, column_count: int) -> None:
        sheets = self._service("sheets", "v4")
        sheet_id = self._first_grid_sheet_id(spreadsheet_id)
        body = {
            "requests": [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": max(column_count, 1),
                        }
                    }
                }
            ]
        }
        sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    def _first_grid_sheet_id(self, spreadsheet_id: str) -> int:
        sheets = self._service("sheets", "v4")
        spreadsheet = sheets.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets(properties(sheetId,sheetType,index))",
        ).execute()
        grid_sheets = [
            sheet["properties"]
            for sheet in spreadsheet.get("sheets", [])
            if sheet.get("properties", {}).get("sheetType") == "GRID"
        ]
        if not grid_sheets:
            return 0
        return int(sorted(grid_sheets, key=lambda props: props.get("index", 0))[0]["sheetId"])

    def _move_to_reports_folder(self, file_id: str) -> None:
        self._move_to_folder(file_id, self.settings.require_reports_folder_id())

    def _move_to_folder(self, file_id: str, folder_id: str) -> None:
        drive = self._service("drive", "v3")
        file = drive.files().get(fileId=file_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents", []))
        kwargs: dict[str, Any] = {
            "fileId": file_id,
            "addParents": folder_id,
            "fields": "id, parents",
        }
        if previous_parents:
            kwargs["removeParents"] = previous_parents
        drive.files().update(**kwargs).execute()


def dated_title(client_name: str, report_name: str) -> str:
    return f"{client_name} - {report_name} - {date.today().isoformat()}"


def _quote_sheet_name(sheet_name: str) -> str:
    return "'" + sheet_name.replace("'", "''") + "'"


def _number(values: list[dict[str, str]], index: int) -> float:
    try:
        raw = values[index].get("value", "0")
    except IndexError:
        return 0.0
    try:
        return float(raw)
    except ValueError:
        return 0.0
