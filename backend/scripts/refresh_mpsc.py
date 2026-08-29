from __future__ import annotations

import sys

from app.core.config import get_settings
from app.sources import mpsc
from app.storage.cache import NotificationCache


def main() -> int:
    cache = NotificationCache(get_settings().notifications_path)
    stored = 0

    for document, payload in mpsc.fetch_documents():
        origin = f"{mpsc.NOTIFICATIONS_URL}#{document.advt_no}"
        try:
            saved = cache.store_bytes(mpsc.id, document.subject, origin, payload)
        except ValueError:
            print(f"  not a pdf: {document.subject[:52]}")
            continue
        stored += 1
        pages = saved.page_count if saved.page_count is not None else "?"
        print(f"  {pages:>3}p {saved.byte_size // 1024:>6}kb  {document.subject[:56]}")

    print()
    print(f"stored {stored} maharashtra documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
