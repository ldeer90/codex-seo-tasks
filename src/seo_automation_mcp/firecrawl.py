from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from .config import Settings
from .seo_analysis import (
    bounded_limit,
    merge_exclude_paths,
    validate_public_url,
)


class FirecrawlError(RuntimeError):
    """Raised when Firecrawl returns an error or an unexpected response."""


class FirecrawlClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.api_key = self.settings.require_firecrawl_key()
        self.base_url = self.settings.firecrawl_base_url.rstrip("/")

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def scrape_url(
        self,
        url: str,
        formats: list[Any] | None = None,
        *,
        only_main_content: bool = True,
    ) -> dict[str, Any]:
        validate_public_url(url)
        payload: dict[str, Any] = {
            "url": url,
            "formats": formats or ["markdown"],
            "onlyMainContent": only_main_content,
            "removeBase64Images": True,
            "blockAds": True,
        }
        return await self._request("POST", "/scrape", json=payload)

    async def scrape_urls(self, urls: list[str]) -> list[dict[str, Any]]:
        if not urls:
            raise ValueError("urls must contain at least one URL.")
        if len(urls) > self.settings.firecrawl_max_scrape_urls:
            raise ValueError(
                f"Too many URLs ({len(urls)}). Configured maximum is "
                f"{self.settings.firecrawl_max_scrape_urls}."
            )

        sem = asyncio.Semaphore(3)

        async def scrape_one(url: str) -> dict[str, Any]:
            async with sem:
                try:
                    return await self.scrape_url(url, formats=["markdown", "html", "links"])
                except Exception as exc:  # keep multi-URL audits from failing all pages
                    return {
                        "success": False,
                        "url": url,
                        "error": str(exc),
                        "data": {"metadata": {"sourceURL": url, "statusCode": "error"}},
                    }

        return await asyncio.gather(*(scrape_one(url) for url in urls))

    async def crawl_site(
        self,
        url: str,
        limit: int | None = None,
        include_paths: list[str] | None = None,
        exclude_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        validate_public_url(url)
        resolved_limit = bounded_limit(
            limit,
            self.settings.firecrawl_default_crawl_limit,
            self.settings.firecrawl_max_crawl_limit,
        )
        payload: dict[str, Any] = {
            "url": url,
            "includePaths": include_paths or [],
            "excludePaths": merge_exclude_paths(exclude_paths),
            "ignoreQueryParameters": True,
            "regexOnFullURL": False,
            "limit": resolved_limit,
            "crawlEntireDomain": False,
            "allowExternalLinks": False,
            "allowSubdomains": False,
            "ignoreRobotsTxt": False,
            "delay": 0.5,
            "maxConcurrency": 2,
            "scrapeOptions": {
                "formats": ["markdown", "html", "links"],
                "onlyMainContent": True,
                "removeBase64Images": True,
                "blockAds": True,
            },
        }
        start = await self._request("POST", "/crawl", json=payload)
        crawl_id = start.get("id")
        if not crawl_id:
            raise FirecrawlError("Firecrawl crawl response did not include an id.")
        status = await self._poll_crawl(crawl_id)
        return {
            "success": True,
            "id": crawl_id,
            "url": start.get("url", url),
            "limit": resolved_limit,
            "status": status.get("status"),
            "total": status.get("total"),
            "completed": status.get("completed"),
            "creditsUsed": status.get("creditsUsed"),
            "data": status.get("data", []),
        }

    async def _poll_crawl(self, crawl_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + self.settings.firecrawl_crawl_timeout_seconds
        last_status: dict[str, Any] = {}
        while time.monotonic() < deadline:
            last_status = await self._request("GET", f"/crawl/{crawl_id}")
            state = last_status.get("status")
            if state == "completed":
                return await self._collect_paginated_crawl_data(last_status)
            if state == "failed":
                raise FirecrawlError(f"Firecrawl crawl {crawl_id} failed.")
            await asyncio.sleep(3)
        completed = last_status.get("completed", 0)
        total = last_status.get("total", "unknown")
        raise FirecrawlError(
            f"Timed out waiting for Firecrawl crawl {crawl_id} "
            f"({completed}/{total} pages completed)."
        )

    async def _collect_paginated_crawl_data(self, status: dict[str, Any]) -> dict[str, Any]:
        collected = list(status.get("data") or [])
        next_url = status.get("next")
        while next_url:
            page = await self._request("GET", next_url)
            collected.extend(page.get("data") or [])
            next_url = page.get("next")
        status["data"] = collected
        status["completed"] = len(collected) or status.get("completed")
        return status

    async def _request(
        self,
        method: str,
        path_or_url: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = path_or_url if path_or_url.startswith("http") else f"{self.base_url}/v2{path_or_url}"
        async with httpx.AsyncClient(timeout=90) as client:
            for attempt in range(4):
                response = await client.request(method, url, headers=self._headers, json=json)
                if response.status_code in {429, 500, 502, 503, 504} and attempt < 3:
                    await asyncio.sleep(2**attempt)
                    continue
                if response.is_error:
                    raise FirecrawlError(self._error_message(method, path_or_url, response))
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise FirecrawlError(
                        f"Firecrawl returned non-JSON response for {method} {path_or_url}."
                    ) from exc
                if payload.get("success") is False:
                    error = payload.get("error") or payload.get("message") or "unknown error"
                    raise FirecrawlError(
                        f"Firecrawl request failed for {method} {path_or_url}: {error}"
                    )
                return payload
        raise FirecrawlError(f"Firecrawl request failed for {method} {path_or_url}.")

    @staticmethod
    def _error_message(method: str, path_or_url: str, response: httpx.Response) -> str:
        try:
            payload = response.json()
            detail = payload.get("error") or payload.get("message") or str(payload)
        except ValueError:
            detail = response.text[:500]
        return (
            f"Firecrawl request failed ({response.status_code}) for "
            f"{method} {path_or_url}: {detail}"
        )
