from __future__ import annotations

import pytest

from app.core.config import get_settings
from app.storage.cache import NotificationCache

JUNK_TITLES = ("Common mistakes", "Request for Proposal")
NOTIFICATION_TITLES = ("CRP-PO",)


@pytest.fixture(scope="module")
def documents():
    docs = NotificationCache(get_settings().notifications_path).index.documents
    if not docs:
        pytest.skip("run scripts.refresh_notices first")
    return docs


def test_every_cached_document_has_been_classified(documents):
    unclassified = [d.title for d in documents if d.kind is None]
    assert unclassified == []


def test_tenders_and_guidance_notes_are_not_treated_as_notifications(documents):
    for needle in JUNK_TITLES:
        matches = [d for d in documents if needle.lower() in d.title.lower()]
        for doc in matches:
            assert doc.kind == "other", f"{doc.title} was wrongly kept"


def test_real_notifications_are_kept(documents):
    for needle in NOTIFICATION_TITLES:
        matches = [d for d in documents if needle.lower() in d.title.lower()]
        assert matches, f"no cached document matching {needle}"
        for doc in matches:
            assert doc.kind == "recruitment_notification"


def test_classification_carries_a_reason(documents):
    for doc in documents:
        assert doc.kind_reason and len(doc.kind_reason) > 10
