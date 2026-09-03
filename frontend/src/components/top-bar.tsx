import Link from "next/link";

import { CheckNow } from "@/components/check-now";
import { initials } from "@/lib/format";
import type { Student } from "@/lib/types";

export function TopBar({
  student,
  studentId,
  urgent,
  photoUrl,
}: {
  student: Student | null;
  studentId: number;
  urgent: number;
  photoUrl: string | null;
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
            className="cursor-pointer truncate text-[12.5px] text-ink-soft transition-colors hover:text-ink"
          >
            {urgent} {urgent === 1 ? "date needs" : "dates need"} your attention
          </Link>
        ) : (
          <span className="hidden truncate text-[12.5px] text-ink-soft sm:inline">
            Nothing needs your attention
          </span>
        )}
      </div>

      <div className="ml-auto flex items-center gap-3">
        <CheckNow studentId={studentId} />

        {student ? (
          <Link
            href="/me"
            title="Your profile"
            className="group flex cursor-pointer items-center gap-2.5 rounded-pill py-1 pl-2.5 pr-1 transition-colors hover:bg-line-soft"
          >
            <div className="hidden text-right sm:block">
              <p className="text-[12px] font-medium leading-tight text-ink">{student.name}</p>
              <p className="text-[11px] leading-tight text-ink-faint">
                {student.category}, {Math.round(student.age_today)} years
              </p>
            </div>
            {photoUrl ? (
              <img
                src={photoUrl}
                alt={student.name}
                className="h-9 w-9 rounded-full border border-line object-cover"
              />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-ink text-[11.5px] font-semibold text-white">
                {initials(student.name)}
              </div>
            )}
          </Link>
        ) : null}
      </div>
    </header>
  );
}
