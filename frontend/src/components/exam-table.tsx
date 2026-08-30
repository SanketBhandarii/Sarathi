"use client";

import { useState } from "react";

import { BucketPill } from "@/components/bucket-pill";
import { ChevronIcon, QuoteIcon } from "@/components/icons";
import { SOURCE_NAME, rupees, shortDate } from "@/lib/format";
import type { RadarEntry } from "@/lib/types";

function Citation({ page, quote }: { page: number; quote: string }) {
  return (
    <p className="mt-1 flex items-start gap-1.5 text-[11px] leading-relaxed text-ink-faint">
      <QuoteIcon className="mt-[3px] h-3 w-3 shrink-0" />
      <span>
        <span className="font-medium text-ink-soft">page {page}</span> — “{quote.slice(0, 150)}
        {quote.length > 150 ? "…" : ""}”
      </span>
    </p>
  );
}

function Details({ entry }: { entry: RadarEntry }) {
  return (
    <div className="border-t border-line bg-page/60 px-4 py-3">
      {entry.reasons.length === 0 ? (
        <p className="text-[12px] text-ink-soft">No details recorded for this exam yet.</p>
      ) : (
        <ul className="flex flex-col gap-2.5">
          {entry.reasons.map((reason, index) => (
            <li key={index}>
              <p
                className={`text-[12.5px] leading-relaxed ${
                  reason.blocks_application ? "font-medium text-stop" : "text-ink"
                }`}
              >
                {reason.text}
              </p>
              {reason.citation ? (
                <Citation page={reason.citation.page} quote={reason.citation.quote} />
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {entry.unchecked.length > 0 ? (
        <div className="mt-3 rounded-[10px] border border-wait/20 bg-wait-soft px-3 py-2">
          <p className="text-[11px] font-medium text-wait">We could not check everything here</p>
          <ul className="mt-1 flex flex-col gap-0.5">
            {entry.unchecked.map((item) => (
              <li key={item} className="text-[11px] text-wait">
                · {item}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

export function ExamTable({ entries }: { entries: RadarEntry[] }) {
  const [openRow, setOpenRow] = useState<string | null>(null);

  if (entries.length === 0) {
    return (
      <p className="px-4 py-8 text-center text-[13px] text-ink-soft">
        No exams here right now.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto scrollbar-thin">
      <table className="w-full min-w-[720px] border-collapse text-left">
        <thead>
          <tr className="border-b border-line text-[11px] font-medium uppercase tracking-wide text-ink-faint">
            <th className="px-4 py-2.5 font-medium">Exam</th>
            <th className="px-4 py-2.5 font-medium">Verdict</th>
            <th className="px-4 py-2.5 font-medium">Conducted by</th>
            <th className="px-4 py-2.5 font-medium">Closes</th>
            <th className="px-4 py-2.5 text-right font-medium">Fee</th>
            <th className="w-10 px-4 py-2.5" />
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => {
            const key = `${entry.source_id}-${entry.exam_name}`;
            const open = openRow === key;
            return (
              <tr key={key} className="border-b border-line align-top last:border-0">
                <td colSpan={6} className="p-0">
                  <div className={open ? "bg-surface" : ""}>
                    <button
                      type="button"
                      onClick={() => setOpenRow(open ? null : key)}
                      className="grid w-full grid-cols-[minmax(0,1fr)_auto] items-center gap-2 text-left transition-colors hover:bg-page/70"
                    >
                      <span className="grid min-w-0 grid-cols-[minmax(220px,2.4fr)_minmax(130px,1fr)_minmax(150px,1.2fr)_minmax(110px,0.9fr)_minmax(70px,0.6fr)] items-center gap-2">
                        <span className="truncate px-4 py-3 text-[13px] font-medium text-ink">
                          {entry.exam_name}
                        </span>
                        <span className="px-4 py-3">
                          <BucketPill bucket={entry.bucket} label={entry.headline} />
                        </span>
                        <span className="truncate px-4 py-3 text-[12px] text-ink-soft">
                          {SOURCE_NAME[entry.source_id] ?? entry.source_id.toUpperCase()}
                        </span>
                        <span className="px-4 py-3 text-[12px] text-ink-soft">
                          {entry.closing_text ?? "—"}
                        </span>
                        <span className="px-4 py-3 text-right text-[12px] tabular-nums text-ink-soft">
                          {rupees(entry.fee_payable)}
                        </span>
                      </span>
                      <span className="px-4 text-ink-faint">
                        <ChevronIcon
                          className={`h-4 w-4 transition-transform ${open ? "rotate-90" : ""}`}
                        />
                      </span>
                    </button>
                    {open ? <Details entry={entry} /> : null}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
