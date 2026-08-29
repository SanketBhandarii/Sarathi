from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import truststore

truststore.inject_into_ssl()

from PIL import Image, ImageDraw

from agents.spec_extractor import extract_specs
from app.core.config import get_settings
from app.documents.maker import CannotMeetSpec, make_document
from app.documents.spec import KIND_LABEL
from app.extraction.document import load_pages


def sample_upload(width: int = 2400, height: int = 3200) -> bytes:
    image = Image.new("RGB", (width, height), (238, 242, 250))
    draw = ImageDraw.Draw(image)
    for x in range(0, width, 31):
        draw.line([(x, 0), (x + 95, height)], fill=(128, 96, 172), width=3)
    draw.ellipse([width // 4, height // 5, 3 * width // 4, 3 * height // 5], fill=(206, 176, 146))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def main(match: str) -> int:
    settings = get_settings()
    index = json.loads((settings.notifications_path / "index.json").read_text("utf-8"))
    doc = next(d for d in index["documents"] if match.lower() in d["title"].lower())

    pages = load_pages(settings.notifications_path / doc["relative_path"])
    specs = extract_specs(pages)
    if not specs:
        print("no document rules found in this notification")
        return 1

    source = sample_upload()
    out_dir = Path(settings.notifications_path).parent / "documents"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"{doc['title'][:56]}")
    print(f"your upload: {len(source) // 1024} KB, 2400 x 3200")
    print()

    for spec in specs:
        try:
            made = make_document(source, spec)
        except CannotMeetSpec as error:
            print(f"  {KIND_LABEL[spec.kind]:<18} could not be made: {error}")
            continue

        target = out_dir / f"{doc['sha256'][:8]}_{spec.kind.value}.jpg"
        target.write_bytes(made.payload)
        state = "matches" if made.matches(spec) else "DOES NOT MATCH"
        print(f"  {KIND_LABEL[spec.kind]:<18} {made.width_px}x{made.height_px}px  "
              f"{made.size_kb:>5.1f} KB   {state}")
        print(f"      needs: {spec.describe()}")
        if spec.citation:
            print(f"      page {spec.citation.page}: \"{spec.citation.quote[:74]}\"")
        print(f"      saved: {target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "CRP-PO"))
