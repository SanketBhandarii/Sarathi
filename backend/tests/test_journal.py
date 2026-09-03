from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app

from tests.conftest import A_DAY_NEAR_A_DEADLINE, A_QUIET_DAY


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_a_quiet_day_sends_nothing(client, student_id):
    body = client.post(
        f"/students/{student_id}/journal/run", params={"today": A_QUIET_DAY.isoformat()}
    ).json()
    assert body["messages_sent"] == 0
    assert body["was_silent"] is True
    assert body["checks_run"] > 0


def test_a_day_near_a_deadline_sends_one_message(client, student_id):
    body = client.post(
        f"/students/{student_id}/journal/run", params={"today": A_DAY_NEAR_A_DEADLINE.isoformat()}
    ).json()
    assert body["messages_sent"] >= 1
    assert body["was_silent"] is False


def test_the_agent_does_the_same_work_whether_it_speaks_or_not(client, student_id):
    quiet = client.post(f"/students/{student_id}/journal/run", params={"today": A_QUIET_DAY.isoformat()}).json()
    busy = client.post(f"/students/{student_id}/journal/run", params={"today": A_DAY_NEAR_A_DEADLINE.isoformat()}).json()

    assert quiet["sources_checked"] == busy["sources_checked"]
    assert quiet["citations_verified"] == busy["citations_verified"]
    assert quiet["messages_sent"] < busy["messages_sent"]


def test_every_run_records_what_it_looked_at(client, student_id):
    body = client.post(f"/students/{student_id}/journal/run", params={"today": A_QUIET_DAY.isoformat()}).json()
    assert body["events"]
    assert any(e["kind"] == "source_checked" for e in body["events"])
    assert any("nothing needed your attention" in e["detail"] for e in body["events"])


def test_journal_history_is_returned_newest_first(client, student_id):
    runs = client.get(f"/students/{student_id}/journal", params={"limit": 5}).json()
    assert runs
    stamps = [r["ran_at"] for r in runs]
    assert stamps == sorted(stamps, reverse=True)
