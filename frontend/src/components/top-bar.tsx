import { BellIcon, CaretIcon, PlusIcon, SearchIcon } from "@/components/icons";
import { initials } from "@/lib/format";
import type { Student } from "@/lib/types";

export function TopBar({ student, hasNews }: { student: Student | null; hasNews: boolean }) {
  return (
    <header className="flex items-center gap-4 border-b border-line px-6 py-3.5">
      <label className="flex h-9 min-w-0 flex-1 items-center gap-2.5 rounded-[9px] border border-line bg-page px-3 text-ink-faint transition-colors focus-within:border-line-soft focus-within:bg-shell lg:max-w-[440px]">
        <SearchIcon />
        <input
          type="search"
          placeholder="Search an exam, a date, a document"
          className="min-w-0 flex-1 bg-transparent text-[13px] text-ink outline-none placeholder:text-ink-faint"
        />
        <kbd className="hidden rounded-[5px] border border-line bg-shell px-1.5 py-0.5 text-[10.5px] font-medium text-ink-faint sm:block">
          ⌘ K
        </kbd>
      </label>

      <div className="ml-auto flex items-center gap-2.5">
        <div className="hidden items-stretch overflow-hidden rounded-[9px] sm:flex">
          <button
            type="button"
            className="flex items-center gap-1.5 bg-accent px-3.5 py-2 text-[13px] font-medium text-white transition-colors hover:bg-accent-hover"
          >
            <PlusIcon className="h-[15px] w-[15px]" />
            Check now
          </button>
          <span className="w-px bg-white/25" />
          <button
            type="button"
            aria-label="More actions"
            className="bg-accent px-2 text-white transition-colors hover:bg-accent-hover"
          >
            <CaretIcon />
          </button>
        </div>

        <button
          type="button"
          aria-label="Notifications"
          className="relative flex h-9 w-9 items-center justify-center rounded-[9px] text-ink-soft transition-colors hover:bg-line-soft hover:text-ink"
        >
          <BellIcon />
          {hasNews ? (
            <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-[#e879c8]" />
          ) : null}
        </button>

        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-ink text-[11.5px] font-semibold text-white">
          {student ? initials(student.name) : "—"}
        </div>
      </div>
    </header>
  );
}
