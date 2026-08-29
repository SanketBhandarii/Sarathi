from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image

from app.documents.spec import DocumentSpec

KB = 1024
QUALITY_STEPS = (40, 55, 65, 75, 82, 88, 92, 95, 97, 98, 99, 100)
SUBSAMPLING_STEPS = (2, 1, 0)


@dataclass(frozen=True)
class MadeDocument:
    payload: bytes
    width_px: int
    height_px: int
    size_kb: float
    quality_used: int
    padded: bool

    def matches(self, spec: DocumentSpec) -> bool:
        if spec.width_px and self.width_px != spec.width_px:
            return False
        if spec.height_px and self.height_px != spec.height_px:
            return False
        if spec.min_kb is not None and self.size_kb < spec.min_kb:
            return False
        if spec.max_kb is not None and self.size_kb > spec.max_kb:
            return False
        return True


class CannotMeetSpec(RuntimeError):
    pass


def _fit_to_box(image: Image.Image, width: int, height: int) -> Image.Image:
    canvas = Image.new("RGB", (width, height), (255, 255, 255))
    copy = image.convert("RGB")
    copy.thumbnail((width, height), Image.LANCZOS)
    canvas.paste(copy, ((width - copy.width) // 2, (height - copy.height) // 2))
    return canvas


def _encode(image: Image.Image, quality: int, subsampling: int) -> bytes:
    buffer = io.BytesIO()
    image.save(
        buffer, format="JPEG", quality=quality, subsampling=subsampling, optimize=True
    )
    return buffer.getvalue()


def _pad_to_minimum(payload: bytes, minimum_bytes: int) -> bytes:
    shortfall = minimum_bytes - len(payload)
    if shortfall <= 0:
        return payload
    length = shortfall + 2
    comment = b"\xff\xfe" + length.to_bytes(2, "big") + b" " * (length - 2)
    return payload[:2] + comment + payload[2:]


def make_document(source: bytes, spec: DocumentSpec) -> MadeDocument:
    image = Image.open(io.BytesIO(source))
    width = spec.width_px or image.width
    height = spec.height_px or image.height
    fitted = _fit_to_box(image, width, height)

    max_bytes = int(spec.max_kb * KB) if spec.max_kb is not None else None
    min_bytes = int(spec.min_kb * KB) if spec.min_kb is not None else None

    in_range: list[tuple[int, bytes, int]] = []
    under_max: list[tuple[int, bytes, int]] = []

    for subsampling in SUBSAMPLING_STEPS:
        for quality in QUALITY_STEPS:
            payload = _encode(fitted, quality, subsampling)
            size = len(payload)
            if max_bytes is not None and size > max_bytes:
                continue
            under_max.append((size, payload, quality))
            if min_bytes is None or size >= min_bytes:
                in_range.append((size, payload, quality))

    if in_range:
        size, payload, quality = max(in_range, key=lambda item: item[2])
        return MadeDocument(payload, width, height, round(size / KB, 1), quality, False)

    if not under_max:
        raise CannotMeetSpec(
            f"cannot fit a {spec.kind.value} under {spec.max_kb} KB at {width}x{height}"
        )

    size, payload, quality = max(under_max, key=lambda item: item[0])
    padded = _pad_to_minimum(payload, min_bytes) if min_bytes else payload
    return MadeDocument(
        payload=padded,
        width_px=width,
        height_px=height,
        size_kb=round(len(padded) / KB, 1),
        quality_used=quality,
        padded=len(padded) != size,
    )
