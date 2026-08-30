import Link from "next/link";

import { CheckNow } from "@/components/check-now";
import { initials } from "@/lib/format";
import type { Student } from "@/lib/types";

export function TopBar({
  student,
  studentId,
  urgent,
}: {
  student: Student | null;
  studentId: number;
  urgent: number;
}) {
  return (
    <header className="flex items-center gap-4 border-b border-line px-6 py-3.5">
      <div className="flex min-w-0 items-center gap-2.5">
        <span className="rounded-pill bg-good-soft px-2.5 py-1 text-[11.5px] font-medium text-good">
          Watching
        </span>
        {urgent > 0 ? (
          <Link
            href="/deadlines"
            className="truncate text-[12.5px] text-ink-soft transition-colors hover:text-ink"
          >
            {urgent} {urgent === 1 ? "date needs" : "dates need"} you soon
          </Link>
        ) : (
          <span className="hidden truncate text-[12.5px] text-ink-soft sm:inline">
            Nothing needs you right now
          </span>
        )}
      </div>

      <div className="ml-auto flex items-center gap-3">
        <CheckNow studentId={studentId} />

        {student ? (
          <div className="flex items-center gap-2.5">
            <div className="hidden text-right sm:block">
              <p className="text-[12px] font-medium leading-tight text-ink">{student.name}</p>
              <p className="text-[11px] leading-tight text-ink-faint">
                {student.category} · {Math.round(student.age_today)} years
              </p>
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-ink text-[11.5px] font-semibold text-white">
              {initials(student.name)}
            </div>
          </div>
        ) : null}
      </div>
    </header>
  );
}
