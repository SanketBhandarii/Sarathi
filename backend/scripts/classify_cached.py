from __future__ import annotations

import sys

import truststore

truststore.inject_into_ssl()

from agents.classifier import classify
from app.core.config import get_settings
from app.extraction.document import load_pages
from app.storage.cache import NotificationCache


def main() -> int:
    cache = NotificationCache(get_settings().notifications_path)
    changed = 0

    for document in cache.index.documents:
        if document.kind is not None:
            print(f"  known   {document.kind:<26} {document.title[:44]}")
            continue

        pages = load_pages(document.path_under(cache.root))
        verdict = classify(pages, document.title)
        document.kind = verdict.kind
        document.kind_reason = verdict.reason
        changed += 1
        print(f"  {verdict.kind:<26} {document.title[:44]}")

    if changed:
        cache._save_index()

    kept = [d for d in cache.index.documents if d.kind == "recruitment_notification"]
    print()
    print(f"{len(kept)} recruitment notifications of {len(cache.index.documents)} cached documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
