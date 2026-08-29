from __future__ import annotations

import sys

from app.core.config import get_settings
from app.sources.ssc_calendar import fetch_calendar
from app.storage.calendar_store import CalendarStore


def main() -> int:
    entries = fetch_calendar()
    store = CalendarStore(get_settings().exams_path)
    store.put(entries)
    print(f"saved {len(entries)} exams from the ssc calendar to {store.path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
