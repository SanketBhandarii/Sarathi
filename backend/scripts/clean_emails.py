from __future__ import annotations

import sys

from app.auth.hygiene import sweep_users
from app.db.base import session_scope


def main() -> int:
    with session_scope() as session:
        report = sweep_users(session)

    for label, rows in [
        ("throwaway", report.throwaway),
        ("does not receive mail", report.undeliverable),
        ("never confirmed in 24h", report.expired_unverified),
    ]:
        for email in rows:
            print(f"  removed [{label}] {email}")

    print()
    print(f"removed {report.total} account(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
