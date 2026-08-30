"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { ClockIcon, FileIcon, HomeIcon, JournalIcon, RadarIcon } from "@/components/icons";

const LINKS = [
  { href: "/", label: "Home", icon: HomeIcon },
  { href: "/radar", label: "Exam Radar", icon: RadarIcon },
  { href: "/deadlines", label: "Deadlines", icon: ClockIcon },
  { href: "/documents", label: "My Documents", icon: FileIcon },
  { href: "/journal", label: "Agent Journal", icon: JournalIcon },
];

export function Sidebar({ studentName, district }: { studentName: string; district: string }) {
  const pathname = usePathname();

  return (
    <aside className="hidden w-[248px] shrink-0 flex-col border-r border-line bg-surface lg:flex">
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-[10px] bg-brand text-[13px] font-semibold text-white">
          सा
        </div>
        <div className="min-w-0">
          <p className="truncate text-[13px] font-semibold text-ink">Sarathi</p>
          <p className="truncate text-[11px] text-ink-faint">{district}</p>
        </div>
      </div>

      <nav className="flex flex-col gap-0.5 px-3">
        {LINKS.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={[
                "flex items-center gap-3 rounded-[10px] px-3 py-2 text-[13px] transition-colors",
                active
                  ? "bg-brand-soft font-medium text-ink"
                  : "text-ink-soft hover:bg-brand-soft/60 hover:text-ink",
              ].join(" ")}
            >
              <Icon />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto px-3 pb-5">
        <div className="rounded-card border border-line bg-page px-4 py-4">
          <p className="text-[12px] font-medium text-ink">{studentName}</p>
          <p className="mt-1 text-[11px] leading-relaxed text-ink-soft">
            Sarathi checks every exam for you each night. It only writes when something needs you.
          </p>
        </div>
      </div>
    </aside>
  );
}
