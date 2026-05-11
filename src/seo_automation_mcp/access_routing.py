from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .config import Settings


@dataclass(frozen=True)
class SubjectResolution:
    subject: str | None
    source: str
    key: str

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


@dataclass(frozen=True)
class GoogleSubjects:
    analytics: SubjectResolution
    output: SubjectResolution

    def to_dict(self) -> dict[str, dict[str, str | None]]:
        return {
            "analytics": self.analytics.to_dict(),
            "output": self.output.to_dict(),
        }


class GoogleAccessRouter:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.rules = self._load_rules(self.settings.google_site_access_map_path)

    def resolve(
        self,
        *,
        client_name: str | None = None,
        website_url: str | None = None,
        ga4_property_id: str | None = None,
    ) -> GoogleSubjects:
        analytics = self.resolve_analytics_subject(
            client_name=client_name,
            website_url=website_url,
            ga4_property_id=ga4_property_id,
        )
        output = self.resolve_output_subject(analytics_subject=analytics.subject)
        return GoogleSubjects(analytics=analytics, output=output)

    def resolve_analytics_subject(
        self,
        *,
        client_name: str | None = None,
        website_url: str | None = None,
        ga4_property_id: str | None = None,
    ) -> SubjectResolution:
        property_key = _property_key(ga4_property_id)
        if property_key:
            match = self._lookup("properties", property_key)
            if match:
                return SubjectResolution(match, "property", property_key)
            numeric_match = self._lookup("properties", property_key.removeprefix("properties/"))
            if numeric_match:
                return SubjectResolution(numeric_match, "property", property_key)

        host = _host_key(website_url)
        while host:
            match = self._lookup("hosts", host)
            if match:
                return SubjectResolution(match, "host", host)
            host = _parent_host(host)

        client_key = _client_key(client_name)
        if client_key:
            match = self._lookup("clients", client_key)
            if match:
                return SubjectResolution(match, "client", client_key)

        default_subject = (
            self.rules.get("default_google_subject")
            or self.settings.google_delegated_subject
            or _first(self.settings.google_subject_candidates())
        )
        return SubjectResolution(default_subject, "default", "")

    def resolve_output_subject(self, *, analytics_subject: str | None = None) -> SubjectResolution:
        subject = (
            self.settings.google_output_delegated_subject
            or self.rules.get("default_output_subject")
            or analytics_subject
            or self.settings.google_delegated_subject
            or _first(self.settings.google_subject_candidates())
        )
        source = "output_default" if subject != analytics_subject else "analytics_subject"
        return SubjectResolution(subject, source, "")

    def _lookup(self, section: str, key: str) -> str | None:
        value = self.rules.get(section, {}).get(key)
        return str(value) if value else None

    @staticmethod
    def _load_rules(path: str | None) -> dict[str, Any]:
        if not path:
            return {}
        resolved = Path(path).expanduser()
        if not resolved.is_absolute():
            cwd_path = Path.cwd() / resolved
            repo_path = Path(__file__).resolve().parents[2] / resolved
            resolved = cwd_path if cwd_path.exists() else repo_path
        if not resolved.exists():
            return {}
        with resolved.open() as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError(f"Google site access map must be a JSON object: {resolved}")
        for key in ("properties", "clients", "hosts"):
            if key in data and not isinstance(data[key], dict):
                raise ValueError(f"Google site access map field {key!r} must be an object.")
        return data


def _property_key(value: str | None) -> str:
    if not value:
        return ""
    stripped = value.strip()
    return stripped if stripped.startswith("properties/") else f"properties/{stripped}"


def _client_key(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def _host_key(value: str | None) -> str:
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = (parsed.hostname or "").lower()
    return host.removeprefix("www.")


def _parent_host(host: str) -> str:
    parts = host.split(".")
    if len(parts) <= 2:
        return ""
    return ".".join(parts[1:])


def _first(values: tuple[str, ...]) -> str | None:
    return values[0] if values else None
