from __future__ import annotations

import io

import pytest
from PIL import Image, ImageDraw

from app.documents.maker import CannotMeetSpec, make_document
from app.documents.spec import DocumentKind, DocumentSpec, IBPS_PO_SPECS


def photo_bytes(width: int = 2400, height: int = 3200, quality: int = 95) -> bytes:
    image = Image.new("RGB", (width, height), (238, 242, 250))
    draw = ImageDraw.Draw(image)
    for x in range(0, width, 29):
        draw.line([(x, 0), (x + 90, height)], fill=(130, 95, 170), width=3)
    draw.ellipse([width // 4, height // 5, 3 * width // 4, 3 * height // 5], fill=(205, 175, 145))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()


@pytest.mark.parametrize("spec", IBPS_PO_SPECS, ids=lambda s: s.kind.value)
def test_every_ibps_spec_is_met_exactly(spec):
    made = make_document(photo_bytes(), spec)
    assert made.matches(spec)
    assert made.width_px == spec.width_px
    assert made.height_px == spec.height_px
    assert spec.min_kb <= made.size_kb <= spec.max_kb


@pytest.mark.parametrize("spec", IBPS_PO_SPECS, ids=lambda s: s.kind.value)
def test_result_is_still_a_readable_image(spec):
    made = make_document(photo_bytes(), spec)
    reopened = Image.open(io.BytesIO(made.payload))
    reopened.load()
    assert reopened.size == (spec.width_px, spec.height_px)
    assert reopened.format == "JPEG"


def test_photograph_needs_no_padding():
    spec = next(s for s in IBPS_PO_SPECS if s.kind is DocumentKind.PHOTOGRAPH)
    assert make_document(photo_bytes(), spec).padded is False


def test_a_tiny_source_image_still_meets_the_spec():
    spec = next(s for s in IBPS_PO_SPECS if s.kind is DocumentKind.PHOTOGRAPH)
    made = make_document(photo_bytes(120, 160, quality=40), spec)
    assert made.matches(spec)


def test_impossible_spec_is_reported_not_faked():
    impossible = DocumentSpec(
        kind=DocumentKind.PHOTOGRAPH, width_px=4000, height_px=4000, min_kb=1, max_kb=2
    )
    with pytest.raises(CannotMeetSpec):
        make_document(photo_bytes(), impossible)


def test_describe_reads_in_plain_words():
    spec = next(s for s in IBPS_PO_SPECS if s.kind is DocumentKind.PHOTOGRAPH)
    text = spec.describe()
    assert "200 x 230 pixels" in text
    assert "20 to 50 KB" in text
