"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  CalendarIcon,
  FileIcon,
  GridIcon,
  HelpIcon,
  JournalIcon,
  PlusIcon,
  RadarIcon,
  SettingsIcon,
} from "@/components/icons";

const LINKS = [
  { href: "/", label: "Dashboard", icon: GridIcon },
  { href: "/radar", label: "Exam Radar", icon: RadarIcon },
  { href: "/deadlines", label: "Deadlines", icon: CalendarIcon },
  { href: "/documents", label: "Documents", icon: FileIcon },
  { href: "/journal", label: "Agent Journal", icon: JournalIcon },
];

const LAYER_DOTS = [
  { label: "Central government", tone: "bg-[#7c5cff]" },
  { label: "Maharashtra", tone: "bg-[#33c481]" },
  { label: "Nagpur district", tone: "bg-[#f5a524]" },
];

export function Sidebar({ unread }: { unread: number }) {
  const pathname = usePathname();

  return (
    <aside className="hidden w-[228px] shrink-0 flex-col border-r border-line bg-rail lg:flex">
      <div className="px-7 pb-6 pt-7">
        <span className="font-display text-[23px] font-semibold tracking-tight text-ink">
          Sarathi
        </span>
      </div>

      <nav className="flex flex-col gap-1 px-4">
        {LINKS.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={[
                "flex items-center gap-3 rounded-[9px] px-3.5 py-2.5 text-[13.5px] transition-colors",
                active
                  ? "bg-accent font-medium text-white shadow-[0_1px_2px_rgba(37,99,235,0.35)]"
                  : "text-ink-soft hover:bg-line-soft hover:text-ink",
              ].join(" ")}
            >
              <Icon />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="mx-4 my-5 border-t border-line" />

      <div className="px-4">
        <div className="flex items-center justify-between px-3.5 pb-2">
          <span className="text-[13.5px] font-medium text-ink">Your layers</span>
          <button type="button" aria-label="About layers" className="text-ink-faint hover:text-ink">
            <PlusIcon className="h-4 w-4" />
          </button>
        </div>
        <ul className="flex flex-col gap-0.5">
          {LAYER_DOTS.map(({ label, tone }) => (
            <li
              key={label}
              className="flex items-center gap-3 rounded-[9px] px-3.5 py-2 text-[13px] text-ink-soft"
            >
              <span className={`h-2.5 w-2.5 rounded-[4px] ${tone}`} />
              {label}
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-auto flex flex-col gap-1 px-4 pb-6">
        <button
          type="button"
          className="flex items-center gap-3 rounded-[9px] px-3.5 py-2.5 text-[13.5px] text-ink-soft transition-colors hover:bg-line-soft hover:text-ink"
        >
          <SettingsIcon />
          Settings
        </button>
        <button
          type="button"
          className="flex items-center gap-3 rounded-[9px] px-3.5 py-2.5 text-[13.5px] text-ink-soft transition-colors hover:bg-line-soft hover:text-ink"
        >
          <HelpIcon />
          Help
          {unread > 0 ? (
            <span className="ml-auto rounded-[6px] bg-good-soft px-1.5 py-0.5 text-[11px] font-medium text-good">
              {unread}
            </span>
          ) : null}
        </button>
      </div>
    </aside>
  );
}
