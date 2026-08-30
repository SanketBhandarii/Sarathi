"use client";

import { Field, inputClass } from "@/components/auth-shell";

export type Level =
  | "class_10"
  | "class_12"
  | "iti"
  | "diploma"
  | "graduation"
  | "post_graduation";

export interface Entry {
  level: Level;
  board_or_university: string;
  college: string;
  stream: string;
  marks_kind: "percentage" | "cgpa";
  marks: string;
  cgpa_scale: string;
  passed_year: string;
  is_completed: boolean;
  current_semester: string;
}

export const LEVEL_LABEL: Record<Level, string> = {
  class_10: "10th standard",
  class_12: "12th standard",
  iti: "ITI",
  diploma: "Diploma",
  graduation: "Graduation",
  post_graduation: "Post graduation",
};

const LEVEL_NOTE: Record<Level, string> = {
  class_10: "Needed for MTS, GD Constable and India Post GDS.",
  class_12: "Needed for CHSL, NDA and many clerk posts.",
  iti: "Needed for some technical and railway posts.",
  diploma: "Needed for Junior Engineer posts.",
  graduation: "Needed for CGL, bank PO and UPSC.",
  post_graduation: "Needed for a few teaching and research posts.",
};

const BOARD_LABEL: Record<Level, string> = {
  class_10: "Board",
  class_12: "Board",
  iti: "Council or board",
  diploma: "Board or university",
  graduation: "University",
  post_graduation: "University",
};

export const ORDER: Level[] = [
  "class_10",
  "class_12",
  "iti",
  "diploma",
  "graduation",
  "post_graduation",
];

export const ALWAYS_ON: Level[] = ["class_10"];

export function blankEntry(level: Level): Entry {
  return {
    level,
    board_or_university: "",
    college: "",
    stream: "",
    marks_kind: level === "graduation" || level === "post_graduation" ? "cgpa" : "percentage",
    marks: "",
    cgpa_scale: "10",
    passed_year: "",
    is_completed: true,
    current_semester: "",
  };
}

export function toPercentage(entry: Entry): number | null {
  const marks = Number(entry.marks);
  if (!entry.marks || Number.isNaN(marks)) return null;
  if (entry.marks_kind === "percentage") return Math.round(marks * 100) / 100;
  const scale = Number(entry.cgpa_scale) || 10;
  if (scale <= 0) return null;
  return Math.round((marks / scale) * 10000) / 100;
}

const ONLY_DIGITS = /[^0-9]/g;
const ONLY_NUMBER = /[^0-9.]/g;

export function EducationCard({
  entry,
  onChange,
  onRemove,
}: {
  entry: Entry;
  onChange: (next: Entry) => void;
  onRemove?: () => void;
}) {
  const set = <K extends keyof Entry>(key: K, value: Entry[K]) =>
    onChange({ ...entry, [key]: value });

  const percentage = toPercentage(entry);
  const showsCollege = entry.level !== "class_10" && entry.level !== "class_12";
  const showsStream = entry.level !== "class_10";

  return (
    <div className="rounded-card border border-line bg-page px-4 py-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-[13.5px] font-semibold text-ink">{LEVEL_LABEL[entry.level]}</h3>
          <p className="mt-0.5 text-[11.5px] text-ink-faint">{LEVEL_NOTE[entry.level]}</p>
        </div>
        {onRemove ? (
          <button
            type="button"
            onClick={onRemove}
            className="rounded-[7px] px-2 py-1 text-[11.5px] font-medium text-ink-faint transition-colors hover:bg-line hover:text-stop"
          >
            Remove
          </button>
        ) : null}
      </div>

      <div className="mt-3.5 flex flex-col gap-3.5">
        <Field label={BOARD_LABEL[entry.level]}>
          <input
            value={entry.board_or_university}
            onChange={(e) => set("board_or_university", e.target.value)}
            placeholder={entry.level === "graduation" ? "RTM Nagpur University" : "Maharashtra State Board"}
            className={inputClass}
          />
        </Field>

        {showsCollege ? (
          <Field label="College">
            <input
              value={entry.college}
              onChange={(e) => set("college", e.target.value)}
              placeholder="GH Raisoni College of Engineering"
              className={inputClass}
            />
          </Field>
        ) : null}

        {showsStream ? (
          <Field label={entry.level === "class_12" ? "Stream" : "Branch or subject"}>
            <input
              value={entry.stream}
              onChange={(e) => set("stream", e.target.value)}
              placeholder={entry.level === "class_12" ? "Science" : "Computer Science"}
              className={inputClass}
            />
          </Field>
        ) : null}

        <div className="grid gap-3.5 sm:grid-cols-2">
          <Field label="Marks are in">
            <select
              value={entry.marks_kind}
              onChange={(e) => set("marks_kind", e.target.value as Entry["marks_kind"])}
              className={`${inputClass} appearance-none`}
            >
              <option value="percentage">Percentage</option>
              <option value="cgpa">CGPA</option>
            </select>
          </Field>

          <Field label={entry.marks_kind === "cgpa" ? "Your CGPA" : "Your percentage"}>
            <input
              inputMode="decimal"
              value={entry.marks}
              onChange={(e) => set("marks", e.target.value.replace(ONLY_NUMBER, "").slice(0, 5))}
              placeholder={entry.marks_kind === "cgpa" ? "6.4" : "78.4"}
              className={inputClass}
            />
          </Field>
        </div>

        {entry.marks_kind === "cgpa" ? (
          <div className="grid gap-3.5 sm:grid-cols-2">
            <Field label="Out of">
              <select
                value={entry.cgpa_scale}
                onChange={(e) => set("cgpa_scale", e.target.value)}
                className={`${inputClass} appearance-none`}
              >
                <option value="10">10</option>
                <option value="4">4</option>
                <option value="7">7</option>
              </select>
            </Field>
            <div className="flex items-end pb-1">
              {percentage !== null ? (
                <p className="text-[11.5px] leading-relaxed text-ink-soft">
                  That is about <span className="font-medium text-ink">{percentage}%</span>. Forms
                  usually ask for a percentage. Use the conversion your university prints if it
                  differs.
                </p>
              ) : null}
            </div>
          </div>
        ) : null}

        <div className="grid gap-3.5 sm:grid-cols-2">
          <Field label={entry.is_completed ? "Year you passed" : "Year you expect to pass"}>
            <input
              inputMode="numeric"
              value={entry.passed_year}
              onChange={(e) => set("passed_year", e.target.value.replace(ONLY_DIGITS, "").slice(0, 4))}
              placeholder="2026"
              className={inputClass}
            />
          </Field>

          {!entry.is_completed ? (
            <Field label="Current semester">
              <input
                inputMode="numeric"
                value={entry.current_semester}
                onChange={(e) =>
                  set("current_semester", e.target.value.replace(ONLY_DIGITS, "").slice(0, 2))
                }
                placeholder="7"
                className={inputClass}
              />
            </Field>
          ) : null}
        </div>

        <label className="flex items-center gap-2.5 text-[12.5px] text-ink">
          <input
            type="checkbox"
            checked={entry.is_completed}
            onChange={(e) => set("is_completed", e.target.checked)}
            className="h-4 w-4 accent-[#2563eb]"
          />
          I have finished this
        </label>
      </div>
    </div>
  );
}
