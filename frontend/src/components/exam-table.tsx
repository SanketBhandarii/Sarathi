"use client";

import { useState } from "react";

import { ChevronIcon, ListIcon, QuoteIcon, RadarIcon, GridIcon } from "@/components/icons";
import { BODY_TONE, BUCKET_TONE } from "@/lib/format";
import type { RadarEntry } from "@/lib/types";

function Pill({ entry }: { entry: RadarEntry }) {
  return (
    <span
      className={`inline-flex whitespace-nowrap rounded-[7px] px-2.5 py-1 text-[12px] font-medium ${BUCKET_TONE[entry.bucket]}`}
    >
      {entry.headline}
    </span>
  );
}

function Details({ entry }: { entry: RadarEntry }) {
  return (
    <div className="border-t border-line bg-page/50 px-5 py-4">
      {entry.reasons.length === 0 ? (
        <p className="text-[12.5px] text-ink-soft">Nothing recorded for this exam yet.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {entry.reasons.map((reason, index) => (
            <li key={index}>
              <p
                className={`text-[13px] leading-relaxed ${
                  reason.blocks_application ? "font-medium text-stop" : "text-ink"
                }`}
              >
                {reason.text}
              </p>
              {reason.citation ? (
                <p className="mt-1 flex items-start gap-1.5 text-[11.5px] leading-relaxed text-ink-faint">
                  <QuoteIcon className="mt-[3px] h-3 w-3 shrink-0" />
                  <span>
                    <span className="font-medium text-ink-soft">page {reason.citation.page}</span> — “
                    {reason.citation.quote.slice(0, 155)}
                    {reason.citation.quote.length > 155 ? "…" : ""}”
                  </span>
                </p>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {entry.unchecked.length > 0 ? (
        <div className="mt-3 rounded-[9px] border border-sun/20 bg-sun-soft px-3 py-2">
          <p className="text-[11.5px] font-medium text-sun">We could not check everything here</p>
          {entry.unchecked.map((item) => (
            <p key={item} className="mt-0.5 text-[11.5px] text-sun">
              · {item}
            </p>
          ))}
        </div>
      ) : null}
    </div>
  );
}

const COLS = "grid-cols-[minmax(0,2.6fr)_minmax(0,1.5fr)_minmax(0,1.3fr)_44px]";

export function ExamTable({ entries }: { entries: RadarEntry[] }) {
  const [open, setOpen] = useState<string | null>(null);

  if (entries.length === 0) {
    return <p className="px-5 py-10 text-center text-[13px] text-ink-soft">Nothing here right now.</p>;
  }

  return (
    <div className="overflow-x-auto scrollbar-thin">
      <div className="min-w-[660px]">
        <div className={`grid ${COLS} border-y border-line bg-page/40`}>
          <div className="flex items-center gap-2 border-r border-line px-5 py-3 text-[13px] font-medium text-ink-soft">
            <ListIcon className="h-4 w-4" />
            Exam
          </div>
          <div className="flex items-center gap-2 border-r border-line px-5 py-3 text-[13px] font-medium text-ink-soft">
            <GridIcon className="h-4 w-4" />
            Conducted by
          </div>
          <div className="flex items-center gap-2 px-5 py-3 text-[13px] font-medium text-ink-soft">
            <RadarIcon className="h-4 w-4" />
            Verdict
          </div>
          <div />
        </div>

        {entries.map((entry) => {
          const key = `${entry.source_id}-${entry.exam_name}`;
          const isOpen = open === key;
          return (
            <div key={key} className="border-b border-line last:border-0">
              <button
                type="button"
                onClick={() => setOpen(isOpen ? null : key)}
                className={`grid w-full ${COLS} items-center text-left transition-colors hover:bg-page/50`}
              >
                <span className="min-w-0 border-r border-line px-5 py-3.5">
                  <span className="flex items-center gap-2.5">
                    <span className={`h-2 w-2 shrink-0 rounded-full ${BODY_TONE[entry.source_id] ?? "bg-ink-faint"}`} />
                    <span className="truncate text-[13.5px] font-medium text-ink">{entry.exam_name}</span>
                  </span>
                  <span className="mt-0.5 block truncate pl-[18px] text-[11.5px] text-ink-faint">
                    {entry.official_title}
                  </span>
                </span>
                <span className="min-w-0 truncate border-r border-line px-5 py-3.5 text-[13px] text-ink-soft">
                  {entry.body_full}
                </span>
                <span className="px-5 py-3.5">
                  <Pill entry={entry} />
                </span>
                <span className="flex items-center justify-center text-ink-faint">
                  <ChevronIcon className={`h-4 w-4 transition-transform ${isOpen ? "rotate-90" : ""}`} />
                </span>
              </button>
              {isOpen ? <Details entry={entry} /> : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
