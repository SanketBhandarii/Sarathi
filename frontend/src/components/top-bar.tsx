import type { Student } from "@/lib/types";
import { initials } from "@/lib/format";

export function TopBar({ student }: { student: Student | null }) {
  return (
    <header className="flex items-center justify-between border-b border-line bg-surface px-5 py-3 lg:px-7">
      <div className="flex items-center gap-2 text-[12px] text-ink-faint">
        <span className="rounded-pill bg-good-soft px-2 py-0.5 text-[11px] font-medium text-good">
          {student ? "Watching" : "Offline"}
        </span>
        <span className="hidden sm:inline">
          {student ? "Checked last night at 02:14" : "Start the backend to see live data"}
        </span>
      </div>

      <div className="flex items-center gap-3">
        {student ? (
          <>
            <div className="hidden text-right sm:block">
              <p className="text-[12px] font-medium leading-tight text-ink">{student.name}</p>
              <p className="text-[11px] leading-tight text-ink-faint">
                {student.category} · {Math.round(student.age_today)} years
              </p>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand text-[11px] font-semibold text-white">
              {initials(student.name)}
            </div>
          </>
        ) : null}
      </div>
    </header>
  );
}
