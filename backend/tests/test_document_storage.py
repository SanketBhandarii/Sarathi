from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from app.documents.spec import DocumentKind
from app.documents.storage import PRIVATE_KINDS, LocalDocumentStore, _file_name


def jpeg_bytes(colour=(200, 170, 140)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (200, 230), colour).save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


@pytest.fixture
def store(tmp_path: Path) -> LocalDocumentStore:
    return LocalDocumentStore(tmp_path)


def test_a_photograph_is_public(store):
    saved = store.save(1, DocumentKind.PHOTOGRAPH, jpeg_bytes())
    assert saved.is_private is False


@pytest.mark.parametrize("kind", sorted(PRIVATE_KINDS, key=lambda k: k.value))
def test_signatures_and_thumbprints_are_private(store, kind):
    saved = store.save(1, kind, jpeg_bytes())
    assert saved.is_private is True


def test_the_file_lands_on_disk_and_is_still_an_image(store, tmp_path):
    saved = store.save(7, DocumentKind.PHOTOGRAPH, jpeg_bytes())
    written = tmp_path / saved.file_id
    assert written.exists()
    reopened = Image.open(io.BytesIO(written.read_bytes()))
    reopened.load()
    assert reopened.size == (200, 230)


def test_the_same_image_gets_the_same_name(store):
    payload = jpeg_bytes()
    first = store.save(1, DocumentKind.PHOTOGRAPH, payload)
    second = store.save(1, DocumentKind.PHOTOGRAPH, payload)
    assert first.file_id == second.file_id


def test_different_students_do_not_share_a_name():
    payload = jpeg_bytes()
    assert _file_name(1, DocumentKind.PHOTOGRAPH, payload) != _file_name(
        2, DocumentKind.PHOTOGRAPH, payload
    )


def test_different_images_do_not_share_a_name(store):
    one = _file_name(1, DocumentKind.PHOTOGRAPH, jpeg_bytes((10, 20, 30)))
    two = _file_name(1, DocumentKind.PHOTOGRAPH, jpeg_bytes((200, 100, 50)))
    assert one != two
