from __future__ import annotations

from datetime import date
from typing import Any

from app.core.http import build_client
from app.sources.base import Notice

API_BASE = "https://ssc.gov.in/api/admin/5.1"
HOME_URL = "https://ssc.gov.in"

id = "ssc"
name = "Staff Selection Commission"
home_url = HOME_URL
official_domains = ("ssc.gov.in", "ssc.nic.in")


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None


def _get(path: str) -> list[dict[str, Any]]:
    with build_client(referer=HOME_URL + "/") as client:
        response = client.get(f"{API_BASE}/{path}", headers={"Accept": "application/json"})
        response.raise_for_status()
        payload = response.json()
    data = payload.get("data", payload)
    return data if isinstance(data, list) else []


def fetch_notices() -> list[Notice]:
    return [
        Notice(
            source_id=id,
            title=row.get("advertisementName", "").strip(),
            detail_url=f"{HOME_URL}/candidate-portal",
            opens_on=_parse_date(row.get("startDate")),
            closes_on=_parse_date(row.get("endDate")),
            year=str(row.get("year") or "") or None,
        )
        for row in _get("getAllCandiateAdvertisements")
        if row.get("advertisementName")
    ]


def fetch_categories() -> list[dict[str, Any]]:
    return _get("categories")


def fetch_disabilities() -> list[dict[str, Any]]:
    return _get("disabilities")


def fetch_districts() -> list[dict[str, Any]]:
    return _get("districts")


def fetch_education_boards() -> list[dict[str, Any]]:
    return _get("educationBoards")
