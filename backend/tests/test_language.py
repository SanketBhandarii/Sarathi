from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.eligibility.layers import Layer
from app.eligibility.verdict import Bucket
from app.language.phrases import PHRASES, Language, say
from app.language.render import bucket_label, layer_label
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_every_phrase_has_both_languages():
    for key, entry in PHRASES.items():
        assert Language.ENGLISH in entry, f"{key} has no english"
        assert Language.HINDI in entry, f"{key} has no hindi"
        assert entry[Language.HINDI].strip()


def test_every_bucket_has_a_hindi_label():
    for bucket in Bucket:
        label = bucket_label(bucket, Language.HINDI)
        assert label
        assert not label.startswith("bucket.")


def test_every_layer_has_a_hindi_label():
    for layer in Layer:
        label = layer_label(layer, Language.HINDI)
        assert label
        assert not label.startswith("layer.")


def test_placeholders_are_filled_in_both_languages():
    for language in (Language.ENGLISH, Language.HINDI):
        text = say("relaxation.extra_years", language, years=3, category="OBC")
        assert "3" in text and "OBC" in text
        assert "{" not in text


def test_a_missing_value_does_not_crash_the_sentence():
    text = say("relaxation.extra_years", Language.HINDI)
    assert text
    assert "{years}" in text or "साल" in text


def test_an_unknown_key_returns_the_key_rather_than_breaking():
    assert say("no.such.phrase", Language.HINDI) == "no.such.phrase"


def test_radar_endpoint_answers_in_hindi(client):
    body = client.get(
        "/students/1/radar", params={"today": "2026-08-29", "lang": "hi"}
    ).json()
    assert body["language"] == "hi"
    headlines = {e["headline"] for e in body["entries"]}
    assert any(any("\u0900" <= ch <= "\u097f" for ch in h) for h in headlines)


def test_radar_defaults_to_english(client):
    body = client.get("/students/1/radar", params={"today": "2026-08-29"}).json()
    assert body["language"] == "en"
