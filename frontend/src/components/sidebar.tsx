"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  AlertIcon,
  CalendarIcon,
  CogIcon,
  FileIcon,
  GridIcon,
  JournalIcon,
  RadarIcon,
} from "@/components/icons";

const LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: GridIcon },
  { href: "/radar", label: "Exam Radar", icon: RadarIcon },
  { href: "/deadlines", label: "Deadlines", icon: CalendarIcon },
  { href: "/documents", label: "Documents", icon: FileIcon },
  { href: "/changes", label: "Corrections", icon: AlertIcon },
  { href: "/journal", label: "Agent Journal", icon: JournalIcon },
  { href: "/inside", label: "Inside Sarathi", icon: CogIcon },
];

export function Sidebar({ state, district }: { state: string; district: string }) {
  const layers = [
    { label: "Central government", tone: "bg-[#7c5cff]" },
    { label: state, tone: "bg-[#33c481]" },
    { label: `${district} district`, tone: "bg-[#f5a524]" },
  ];

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
          const active = pathname === href || pathname.startsWith(href + "/");
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
        <p className="px-3.5 pb-2 text-[13.5px] font-medium text-ink">Your layers</p>
        <ul className="flex flex-col gap-0.5">
          {layers.map(({ label, tone }) => (
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

      <div className="mt-auto px-4 pb-6">
        <div className="rounded-card border border-line bg-page px-3.5 py-3">
          <p className="text-[12px] font-medium text-ink">Sarathi checks every night</p>
          <p className="mt-1 text-[11.5px] leading-relaxed text-ink-soft">
            It only writes to you when a date or a rule actually needs you.
          </p>
        </div>
      </div>

    </aside>
  );
}
