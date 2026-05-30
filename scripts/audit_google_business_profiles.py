#!/usr/bin/env python3
"""Audit accessible Google Business Profile accounts and locations.

Uses a Desktop OAuth client JSON and stores the resulting user token under var/.
Never prints token or client-secret contents.
"""

from __future__ import annotations

import argparse
import csv
import json
import secrets
import sys
import threading
import webbrowser
from dataclasses import dataclass
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPE = "https://www.googleapis.com/auth/business.manage"
TOKEN_URI = "https://oauth2.googleapis.com/token"
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
ACCOUNT_API = "https://mybusinessaccountmanagement.googleapis.com/v1"
INFO_API = "https://mybusinessbusinessinformation.googleapis.com/v1"
PERFORMANCE_API = "https://businessprofileperformance.googleapis.com/v1"

LOCATION_READ_MASK = ",".join(
    [
        "name",
        "title",
        "storefrontAddress",
        "serviceArea",
        "categories",
        "phoneNumbers",
        "websiteUri",
        "regularHours",
        "openInfo",
        "metadata",
        "latlng",
    ]
)

DAILY_METRICS = [
    "CALL_CLICKS",
    "WEBSITE_CLICKS",
    "BUSINESS_DIRECTION_REQUESTS",
    "BUSINESS_CONVERSATIONS",
    "BUSINESS_BOOKINGS",
    "BUSINESS_FOOD_ORDERS",
]


@dataclass
class OAuthClient:
    client_id: str
    client_secret: str | None


class OAuthCallback(BaseHTTPRequestHandler):
    server: "OAuthServer"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        error = params.get("error", [None])[0]
        if code or error:
            self.server.auth_response = {
                "code": code,
                "state": params.get("state", [None])[0],
                "error": error,
            }
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"<html><body><h1>Google Business Profile auth complete.</h1>"
            b"<p>You can return to Codex now.</p></body></html>"
        )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


class OAuthServer(HTTPServer):
    auth_response: dict[str, str | None] | None = None


def load_oauth_client(path: Path) -> OAuthClient:
    data = json.loads(path.read_text())
    config = data.get("installed") or data.get("web")
    if not config or not config.get("client_id"):
        raise ValueError(f"{path} is not a valid OAuth client JSON file.")
    return OAuthClient(
        client_id=config["client_id"],
        client_secret=config.get("client_secret"),
    )


def save_token(token_file: Path, payload: dict[str, Any]) -> None:
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(json.dumps(payload, indent=2))
    token_file.chmod(0o600)


def load_cached_credentials(token_file: Path, oauth_client: OAuthClient) -> Credentials | None:
    if not token_file.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(token_file), scopes=[SCOPE])
    if creds.valid:
        return creds
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        payload = json.loads(creds.to_json())
        payload["client_id"] = oauth_client.client_id
        if oauth_client.client_secret:
            payload["client_secret"] = oauth_client.client_secret
        save_token(token_file, payload)
        return creds
    return None


def run_local_oauth(client_secret_file: Path, token_file: Path) -> Credentials:
    oauth_client = load_oauth_client(client_secret_file)
    cached = load_cached_credentials(token_file, oauth_client)
    if cached:
        return cached

    state = secrets.token_urlsafe(24)
    server = OAuthServer(("127.0.0.1", 0), OAuthCallback)
    redirect_uri = f"http://127.0.0.1:{server.server_port}/"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    params = {
        "client_id": oauth_client.client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    auth_url = f"{AUTH_URI}?{urlencode(params)}"
    print("Opening Google OAuth consent in your browser...")
    print("If it does not open automatically, paste this URL into your browser:")
    print(auth_url)
    webbrowser.open(auth_url)

    try:
        while server.auth_response is None:
            server.handle_request()
    finally:
        server.server_close()

    response = server.auth_response or {}
    if response.get("error"):
        raise RuntimeError(f"OAuth failed: {response['error']}")
    if response.get("state") != state or not response.get("code"):
        raise RuntimeError("OAuth failed: missing code or state mismatch.")

    token_request = {
        "client_id": oauth_client.client_id,
        "code": response["code"],
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    if oauth_client.client_secret:
        token_request["client_secret"] = oauth_client.client_secret

    token_response = requests.post(TOKEN_URI, data=token_request, timeout=30)
    token_response.raise_for_status()
    token_payload = token_response.json()
    token_payload["client_id"] = oauth_client.client_id
    if oauth_client.client_secret:
        token_payload["client_secret"] = oauth_client.client_secret
    token_payload["token_uri"] = TOKEN_URI
    token_payload["scopes"] = [SCOPE]
    save_token(token_file, token_payload)
    return Credentials.from_authorized_user_info(token_payload, scopes=[SCOPE])


def request_json(
    creds: Credentials,
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    creds.before_request(Request(), method, url, {})
    response = requests.request(
        method,
        url,
        params=params,
        headers={"Authorization": f"Bearer {creds.token}"},
        timeout=30,
    )
    if response.status_code == 404:
        return {"_error": "404 not found", "_url": url}
    if response.status_code in {400, 403, 429}:
        return {"_error": response.text, "_url": url}
    response.raise_for_status()
    return response.json()


def paged_get(
    creds: Credentials,
    url: str,
    *,
    collection_key: str,
    params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    params = dict(params or {})
    rows: list[dict[str, Any]] = []
    while True:
        page = request_json(creds, "GET", url, params=params)
        if page.get("_error"):
            return [{"_error": page["_error"], "_url": page.get("_url", url)}]
        rows.extend(page.get(collection_key, []))
        token = page.get("nextPageToken")
        if not token:
            return rows
        params["pageToken"] = token


def list_accounts(creds: Credentials) -> list[dict[str, Any]]:
    return paged_get(creds, f"{ACCOUNT_API}/accounts", collection_key="accounts")


def list_locations(creds: Credentials, account_name: str) -> list[dict[str, Any]]:
    return paged_get(
        creds,
        f"{INFO_API}/{account_name}/locations",
        collection_key="locations",
        params={"readMask": LOCATION_READ_MASK, "pageSize": 100},
    )


def metric_total(metric_payload: dict[str, Any]) -> int | None:
    if metric_payload.get("_error"):
        return None
    total = 0
    seen_value = False
    for metric in metric_payload.get("multiDailyMetricTimeSeries", []):
        for daily_metric in metric.get("dailyMetricTimeSeries", []):
            for point in daily_metric.get("timeSeries", {}).get("datedValues", []):
                value = point.get("value")
                if value is None:
                    continue
                seen_value = True
                total += int(value)
    return total if seen_value else 0


def fetch_metric(
    creds: Credentials,
    location_name: str,
    metric: str,
    start: date,
    end: date,
) -> dict[str, Any]:
    location_id = location_name.split("/")[-1]
    params = {
        "dailyMetrics": metric,
        "dailyRange.startDate.year": start.year,
        "dailyRange.startDate.month": start.month,
        "dailyRange.startDate.day": start.day,
        "dailyRange.endDate.year": end.year,
        "dailyRange.endDate.month": end.month,
        "dailyRange.endDate.day": end.day,
    }
    return request_json(
        creds,
        "GET",
        f"{PERFORMANCE_API}/locations/{location_id}:fetchMultiDailyMetricsTimeSeries",
        params=params,
    )


def address_text(location: dict[str, Any]) -> str:
    address = location.get("storefrontAddress") or {}
    parts = address.get("addressLines", [])
    locality = address.get("locality")
    administrative_area = address.get("administrativeArea")
    postal_code = address.get("postalCode")
    region = address.get("regionCode")
    tail = " ".join(filter(None, [locality, administrative_area, postal_code, region]))
    return ", ".join([*parts, tail]).strip(", ")


def primary_category(location: dict[str, Any]) -> str:
    category = (location.get("categories") or {}).get("primaryCategory") or {}
    return category.get("displayName") or category.get("name") or ""


def flatten_location(
    account: dict[str, Any],
    location: dict[str, Any],
    metrics: dict[str, int | None],
) -> dict[str, Any]:
    open_info = location.get("openInfo") or {}
    metadata = location.get("metadata") or {}
    phone_numbers = location.get("phoneNumbers") or {}
    service_area = location.get("serviceArea") or {}
    return {
        "account": account.get("accountName") or account.get("name"),
        "account_type": account.get("type"),
        "location_name": location.get("name"),
        "title": location.get("title"),
        "status": open_info.get("status"),
        "can_reopen": open_info.get("canReopen"),
        "address": address_text(location),
        "service_area": json.dumps(service_area, sort_keys=True) if service_area else "",
        "primary_category": primary_category(location),
        "primary_phone": phone_numbers.get("primaryPhone"),
        "website": location.get("websiteUri"),
        "place_id": metadata.get("placeId"),
        "maps_uri": metadata.get("mapsUri"),
        **metrics,
    }


def write_outputs(rows: list[dict[str, Any]], raw: dict[str, Any], output_prefix: Path) -> None:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix(".json")
    csv_path = output_prefix.with_suffix(".csv")
    json_path.write_text(json.dumps(raw, indent=2, sort_keys=True))
    if rows:
        fieldnames = list(rows[0].keys())
        with csv_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {json_path}")
    if rows:
        print(f"Wrote {csv_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client-secret",
        type=Path,
        default=None,
        help="OAuth desktop client JSON. Defaults to the only client_secret_*.json in cwd.",
    )
    parser.add_argument(
        "--token-file",
        type=Path,
        default=Path("var/google-business-profile-token.json"),
    )
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=Path("var/google-business-profile-audit"),
    )
    return parser.parse_args()


def default_client_secret() -> Path:
    matches = sorted(Path.cwd().glob("client_secret_*.json"))
    if len(matches) != 1:
        raise RuntimeError("Pass --client-secret because there is not exactly one client_secret_*.json.")
    return matches[0]


def main() -> int:
    args = parse_args()
    client_secret = args.client_secret or default_client_secret()
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=args.days - 1)

    creds = run_local_oauth(client_secret, args.token_file)
    accounts = list_accounts(creds)
    if accounts and accounts[0].get("_error"):
        print("Google Business Profile API request failed:")
        print(accounts[0]["_error"])
        print()
        print("OAuth succeeded, but the Cloud project could not call accounts.list.")
        return 2
    rows: list[dict[str, Any]] = []
    raw: dict[str, Any] = {
        "date_range": {"start": start.isoformat(), "end": end.isoformat()},
        "accounts": accounts,
        "locations": [],
    }

    for account in accounts:
        account_name = account.get("name")
        if not account_name:
            continue
        locations = list_locations(creds, account_name)
        raw["locations"].append({"account": account, "locations": locations})
        for location in locations:
            if location.get("_error"):
                rows.append(
                    {
                        "account": account.get("accountName") or account.get("name"),
                        "account_type": account.get("type"),
                        "location_name": "",
                        "title": "",
                        "status": "",
                        "can_reopen": "",
                        "address": "",
                        "service_area": "",
                        "primary_category": "",
                        "primary_phone": "",
                        "website": "",
                        "place_id": "",
                        "maps_uri": "",
                        "error": location.get("_error"),
                    }
                )
                continue
            metrics: dict[str, int | None] = {}
            for metric in DAILY_METRICS:
                payload = fetch_metric(creds, location["name"], metric, start, end)
                metrics[metric.lower()] = metric_total(payload)
            rows.append(flatten_location(account, location, metrics))

    write_outputs(rows, raw, args.output_prefix)
    print()
    print(f"Accounts: {len(accounts)}")
    print(f"Locations: {len([row for row in rows if row.get('location_name')])}")
    for row in rows:
        title = row.get("title") or "(untitled)"
        status = row.get("status") or "unknown"
        actions = sum(
            value
            for key, value in row.items()
            if key
            in {
                "call_clicks",
                "website_clicks",
                "business_direction_requests",
                "business_conversations",
                "business_bookings",
                "business_food_orders",
            }
            and isinstance(value, int)
        )
        print(f"- {title}: {status}; {actions} tracked actions in {args.days} days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
