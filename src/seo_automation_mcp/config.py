from __future__ import annotations

import os
from dataclasses import dataclass, replace

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - allows import before dependencies are installed

    def load_dotenv(*_args: object, **_kwargs: object) -> bool:
        return False


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


def _csv_env(name: str) -> tuple[str, ...]:
    raw = os.getenv(name)
    if not raw:
        return ()
    return tuple(value.strip() for value in raw.split(",") if value.strip())


@dataclass(frozen=True)
class Settings:
    firecrawl_api_key: str | None
    firecrawl_base_url: str
    firecrawl_default_crawl_limit: int
    firecrawl_max_crawl_limit: int
    firecrawl_max_scrape_urls: int
    firecrawl_crawl_timeout_seconds: int
    google_application_credentials: str | None
    google_cloud_project: str | None
    google_delegated_subject: str | None
    google_delegated_subjects: tuple[str, ...]
    google_output_delegated_subject: str | None
    google_site_access_map_path: str | None
    google_drive_reports_folder_id: str | None
    default_ga4_property_id: str | None
    monday_api_key: str | None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY") or None,
            firecrawl_base_url=os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev"),
            firecrawl_default_crawl_limit=_int_env("FIRECRAWL_DEFAULT_CRAWL_LIMIT", 25),
            firecrawl_max_crawl_limit=_int_env("FIRECRAWL_MAX_CRAWL_LIMIT", 100),
            firecrawl_max_scrape_urls=_int_env("FIRECRAWL_MAX_SCRAPE_URLS", 50),
            firecrawl_crawl_timeout_seconds=_int_env("FIRECRAWL_CRAWL_TIMEOUT_SECONDS", 180),
            google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or None,
            google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT") or None,
            google_delegated_subject=os.getenv("GOOGLE_DELEGATED_SUBJECT") or None,
            google_delegated_subjects=_csv_env("GOOGLE_DELEGATED_SUBJECTS"),
            google_output_delegated_subject=os.getenv("GOOGLE_OUTPUT_DELEGATED_SUBJECT") or None,
            google_site_access_map_path=os.getenv("GOOGLE_SITE_ACCESS_MAP") or None,
            google_drive_reports_folder_id=os.getenv("GOOGLE_DRIVE_REPORTS_FOLDER_ID") or None,
            default_ga4_property_id=os.getenv("DEFAULT_GA4_PROPERTY_ID") or None,
            monday_api_key=os.getenv("MONDAY_API_KEY") or None,
        )

    def require_firecrawl_key(self) -> str:
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY is required. Add it to your environment or .env.")
        return self.firecrawl_api_key

    def require_google_credentials(self) -> str:
        if not self.google_application_credentials:
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS is required for Google Docs, Sheets, Drive, and GA4."
            )
        return self.google_application_credentials

    def require_reports_folder_id(self) -> str:
        if not self.google_drive_reports_folder_id:
            raise ValueError("GOOGLE_DRIVE_REPORTS_FOLDER_ID is required to save reports.")
        return self.google_drive_reports_folder_id

    def require_monday_api_key(self) -> str:
        if not self.monday_api_key:
            raise ValueError("MONDAY_API_KEY is required. Add it to your environment or .env.")
        return self.monday_api_key

    def resolve_ga4_property_id(self, ga4_property_id: str | None) -> str:
        value = ga4_property_id or self.default_ga4_property_id
        if not value:
            raise ValueError("ga4_property_id or DEFAULT_GA4_PROPERTY_ID is required.")
        return value if value.startswith("properties/") else f"properties/{value}"

    def google_subject_candidates(self) -> tuple[str, ...]:
        subjects: list[str] = []
        for subject in (
            self.google_delegated_subject,
            *self.google_delegated_subjects,
            self.google_output_delegated_subject,
        ):
            if subject and subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)

    def with_google_delegated_subject(self, subject: str | None) -> "Settings":
        return replace(self, google_delegated_subject=subject)
