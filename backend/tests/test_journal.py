from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_a_quiet_day_sends_nothing(client):
    body = client.post(
        "/students/1/journal/run", params={"today": "2026-07-15"}
    ).json()
    assert body["messages_sent"] == 0
    assert body["was_silent"] is True
    assert body["checks_run"] > 0


def test_a_day_near_a_deadline_sends_one_message(client):
    body = client.post(
        "/students/1/journal/run", params={"today": "2026-08-29"}
    ).json()
    assert body["messages_sent"] >= 1
    assert body["was_silent"] is False


def test_the_agent_does_the_same_work_whether_it_speaks_or_not(client):
    quiet = client.post("/students/1/journal/run", params={"today": "2026-07-15"}).json()
    busy = client.post("/students/1/journal/run", params={"today": "2026-08-29"}).json()
    assert quiet["checks_run"] == busy["checks_run"]
    assert quiet["messages_sent"] < busy["messages_sent"]


def test_every_run_records_what_it_looked_at(client):
    body = client.post("/students/1/journal/run", params={"today": "2026-07-15"}).json()
    assert body["events"]
    assert any(e["kind"] == "source_checked" for e in body["events"])
    assert any("nothing needed your attention" in e["detail"] for e in body["events"])


def test_journal_history_is_returned_newest_first(client):
    runs = client.get("/students/1/journal", params={"limit": 5}).json()
    assert runs
    stamps = [r["ran_at"] for r in runs]
    assert stamps == sorted(stamps, reverse=True)
