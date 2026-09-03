from __future__ import annotations

import io
from dataclasses import dataclass, field
from datetime import date

from PIL import Image, ImageDraw, ImageFont

from app.documents.spec import DocumentKind

PAGE = (1240, 1754)
MARGIN = 90

INK = (26, 27, 31)
SOFT = (99, 103, 110)
FAINT = (150, 154, 161)
LINE = (223, 226, 231)
PAPER = (255, 255, 255)
WATERMARK = (243, 245, 248)

GAP = 40
BOX = ((PAGE[0] - MARGIN * 2 - GAP * 2) // 3, 400)


@dataclass(frozen=True)
class SheetPicture:
    kind: DocumentKind
    label: str
    payload: bytes | None
    width_px: int | None
    height_px: int | None


@dataclass(frozen=True)
class SheetDetails:
    name: str
    date_of_birth: date
    category: str
    state: str
    district: str
    made_on: date
    education: list[tuple[str, str]] = field(default_factory=list)


def _font(size: int) -> ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _paint_watermark(canvas: Image.Image) -> None:
    side = max(PAGE) * 2
    layer = Image.new("RGB", (side, side), PAPER)
    brush = ImageDraw.Draw(layer)
    mark = _font(120)
    across, down = 660, 340

    for row in range(0, side, down):
        shift = 0 if (row // down) % 2 == 0 else across // 2
        for column in range(-across, side, across):
            brush.text((column + shift, row), "Sarathi", font=mark, fill=WATERMARK)

    tilted = layer.rotate(30, resample=Image.BICUBIC, fillcolor=PAPER)
    left = (side - PAGE[0]) // 2
    top = (side - PAGE[1]) // 2
    canvas.paste(tilted.crop((left, top, left + PAGE[0], top + PAGE[1])), (0, 0))


def _draw_detail_row(
    draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value: str, width: int
) -> int:
    draw.text((x, y), label, font=_font(23), fill=FAINT)
    draw.text((x, y + 30), value, font=_font(29), fill=INK)
    draw.line([(x, y + 74), (x + width, y + 74)], fill=LINE, width=1)
    return y + 100


def _draw_picture(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    picture: SheetPicture,
    left: int,
    top: int,
) -> None:
    draw.rectangle([left, top, left + BOX[0], top + BOX[1]], outline=LINE, width=2)
    draw.text((left + 18, top + 18), picture.label, font=_font(26), fill=INK)

    inner_top = top + 62
    inner = (BOX[0] - 36, BOX[1] - 120)

    if picture.payload is None:
        draw.text(
            (left + 18, inner_top + inner[1] // 2 - 14),
            "not added yet",
            font=_font(24),
            fill=FAINT,
        )
        return

    art = Image.open(io.BytesIO(picture.payload)).convert("RGB")
    art.thumbnail(inner, Image.LANCZOS)
    canvas.paste(art, (left + 18 + (inner[0] - art.width) // 2, inner_top))

    draw.text(
        (left + 18, top + BOX[1] - 44),
        f"{picture.width_px} by {picture.height_px} pixels",
        font=_font(22),
        fill=SOFT,
    )


def make_sheet(details: SheetDetails, pictures: list[SheetPicture]) -> bytes:
    canvas = Image.new("RGB", PAGE, PAPER)
    _paint_watermark(canvas)
    draw = ImageDraw.Draw(canvas)

    draw.text((MARGIN, MARGIN), "Sarathi", font=_font(34), fill=SOFT)
    draw.text((MARGIN, MARGIN + 48), "Your document sheet", font=_font(58), fill=INK)
    draw.text(
        (MARGIN, MARGIN + 122),
        f"Made for {details.name} on {details.made_on.strftime('%d %B %Y')}",
        font=_font(26),
        fill=SOFT,
    )

    top = MARGIN + 190
    draw.line([(MARGIN, top), (PAGE[0] - MARGIN, top)], fill=LINE, width=2)

    column_width = (PAGE[0] - MARGIN * 2 - GAP) // 2
    left_y = top + 34
    right_y = top + 34

    left_y = _draw_detail_row(draw, MARGIN, left_y, "Name", details.name, column_width)
    left_y = _draw_detail_row(
        draw,
        MARGIN,
        left_y,
        "Date of birth",
        details.date_of_birth.strftime("%d %B %Y"),
        column_width,
    )

    right_x = MARGIN + column_width + GAP
    right_y = _draw_detail_row(draw, right_x, right_y, "Category", details.category, column_width)
    right_y = _draw_detail_row(
        draw, right_x, right_y, "Home", f"{details.district}, {details.state}", column_width
    )

    pictures_top = max(left_y, right_y) + 40
    for index, picture in enumerate(pictures[:3]):
        _draw_picture(canvas, draw, picture, MARGIN + index * (BOX[0] + GAP), pictures_top)

    after_pictures = pictures_top + BOX[1] + 50

    if details.education:
        draw.text((MARGIN, after_pictures), "Your education", font=_font(30), fill=INK)
        after_pictures += 46
        for level, detail in details.education[:6]:
            draw.text((MARGIN, after_pictures), level, font=_font(25), fill=INK)
            draw.text((MARGIN + 340, after_pictures), detail, font=_font(25), fill=SOFT)
            after_pictures += 38
        after_pictures += 22

    note_top = after_pictures
    draw.line([(MARGIN, note_top), (PAGE[0] - MARGIN, note_top)], fill=LINE, width=1)
    draw.text(
        (MARGIN, note_top + 26),
        "Keep this sheet for yourself. Do not upload it to any form.",
        font=_font(28),
        fill=INK,
    )
    draw.text(
        (MARGIN, note_top + 66),
        "A form wants one picture in the exact size that commission asks for.",
        font=_font(24),
        fill=SOFT,
    )
    draw.text(
        (MARGIN, note_top + 100),
        "Download those from the Documents page. They carry no watermark.",
        font=_font(24),
        fill=SOFT,
    )

    out = io.BytesIO()
    canvas.save(out, format="PDF", resolution=150.0)
    return out.getvalue()
