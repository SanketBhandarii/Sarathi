from __future__ import annotations

import sys

from app.core.config import get_settings
from app.sources import registry
from app.storage.cache import NotificationCache


def main() -> int:
    settings = get_settings()
    cache = NotificationCache(settings.notifications_path)

    stored = 0
    skipped = 0
    failed = 0

    for source in registry.SOURCES:
        notices = source.fetch_notices()
        with_pdf = [n for n in notices if n.document_url]
        print(f"{source.id:6} {len(notices):>3} notices  {len(with_pdf):>3} with pdf")

        for notice in with_pdf:
            assert notice.document_url
            if cache.get(notice.document_url):
                skipped += 1
                continue
            try:
                document = cache.store(
                    source_id=source.id,
                    title=notice.title,
                    origin_url=notice.document_url,
                    referer=source.home_url + "/",
                )
                stored += 1
                pages = document.page_count if document.page_count is not None else "?"
                size_kb = document.byte_size // 1024
                print(f"       saved  {pages:>3}p {size_kb:>5}kb  {notice.title[:52]}")
            except Exception as error:
                failed += 1
                print(f"       FAIL   {type(error).__name__}  {notice.title[:52]}")

    print()
    print(f"stored {stored}, already cached {skipped}, failed {failed}")
    print(f"cache: {cache.root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
