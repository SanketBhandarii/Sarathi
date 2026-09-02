"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Field, Problem, inputClass } from "@/components/auth-shell";
import {
  EducationCard,
  type Entry,
  LEVEL_LABEL,
  type Level,
  ORDER,
  blankEntry,
} from "@/components/education-ladder";
import { SettingsIcon } from "@/components/icons";
import { Card } from "@/components/ui";
import { auth } from "@/lib/auth";
import type { MyProfile, SavedQualification } from "@/lib/mine";

const STATES = [
  "Maharashtra", "Bihar", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Gujarat",
  "Karnataka", "Tamil Nadu", "Telangana", "Andhra Pradesh", "West Bengal", "Odisha",
  "Punjab", "Haryana", "Kerala", "Jharkhand", "Chhattisgarh", "Assam", "Delhi",
  "Uttarakhand", "Himachal Pradesh", "Goa", "Jammu and Kashmir",
];

const CATEGORIES = [
  { value: "UR", label: "General / Unreserved" },
  { value: "OBC", label: "OBC (Non Creamy Layer)" },
  { value: "SC", label: "Scheduled Caste" },
  { value: "ST", label: "Scheduled Tribe" },
  { value: "EWS", label: "EWS" },
];

const GENDERS = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
  { value: "transgender", label: "Transgender" },
];

const selectClass = `${inputClass} cursor-pointer appearance-none`;

function numberOrNull(value: string): number | null {
  const trimmed = value.trim();
  if (trimmed === "") return null;
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : null;
}

function text(value: string): string | null {
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

function toEntry(saved: SavedQualification): Entry {
  return {
    level: saved.level,
    board_or_university: saved.board_or_university ?? "",
    college: saved.college ?? "",
    stream: saved.stream ?? "",
    marks_kind: saved.marks_kind,
    marks: saved.marks === null ? "" : String(saved.marks),
    cgpa_scale: saved.cgpa_scale === null ? "10" : String(saved.cgpa_scale),
    passed_year: saved.passed_year === null ? "" : String(saved.passed_year),
    is_completed: saved.is_completed,
    current_semester: saved.current_semester === null ? "" : String(saved.current_semester),
  };
}

export function ProfileEditor({ profile, token }: { profile: MyProfile; token: string }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const [about, setAbout] = useState({
    name: profile.name,
    date_of_birth: profile.date_of_birth,
    category: profile.category,
    gender: profile.gender,
    is_pwbd: profile.is_pwbd,
    is_ex_serviceman: profile.is_ex_serviceman,
    state: profile.state,
    district: profile.district,
  });

  const [entries, setEntries] = useState<Entry[]>(
    profile.qualifications.length > 0
      ? profile.qualifications.map(toEntry)
      : [blankEntry("class_10")],
  );

  const chosen = new Set(entries.map((entry) => entry.level));
  const available = ORDER.filter((level) => !chosen.has(level));

  function setAboutField<K extends keyof typeof about>(key: K, value: (typeof about)[K]) {
    setAbout((current) => ({ ...current, [key]: value }));
    setSaved(false);
  }

  function addLevel(level: Level) {
    setEntries((current) =>
      [...current, blankEntry(level)].sort(
        (a, b) => ORDER.indexOf(a.level) - ORDER.indexOf(b.level),
      ),
    );
    setSaved(false);
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setProblem(null);
    setSaved(false);

    const qualifications = entries
      .filter((entry) => entry.marks || entry.passed_year || entry.board_or_university)
      .map((entry) => ({
        level: entry.level,
        board_or_university: text(entry.board_or_university),
        college: text(entry.college),
        stream: text(entry.stream),
        marks_kind: entry.marks_kind,
        marks: numberOrNull(entry.marks),
        cgpa_scale: entry.marks_kind === "cgpa" ? (numberOrNull(entry.cgpa_scale) ?? 10) : null,
        passed_year: numberOrNull(entry.passed_year),
        is_completed: entry.is_completed,
        current_semester: numberOrNull(entry.current_semester),
      }));

    if (qualifications.length === 0) {
      setProblem("Please keep at least your 10th standard marks.");
      setBusy(false);
      return;
    }

    try {
      await auth.saveProfile({ ...about, qualifications }, token);
      setSaved(true);
      setOpen(false);
      router.refresh();
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  if (!open) {
    return (
      <Card icon={<SettingsIcon className="h-4 w-4" />} title="Change your details">
        <div className="border-t border-line px-5 py-4">
          <p className="text-[12.5px] leading-relaxed text-ink-soft">
            Moved district, finished your degree, got your category certificate? Update it here and
            Sarathi works out every exam again straight away.
          </p>
          {saved ? (
            <p className="mt-2.5 rounded-[9px] bg-good-soft px-3.5 py-2 text-[12.5px] font-medium text-good">
              Saved. Your exams have been judged again.
            </p>
          ) : null}
          <button
            type="button"
            onClick={() => setOpen(true)}
            className="mt-3.5 cursor-pointer rounded-[9px] bg-ink px-4 py-2.5 text-[12.5px] font-medium text-white transition-opacity hover:opacity-90"
          >
            Edit my details
          </button>
        </div>
      </Card>
    );
  }

  return (
    <Card icon={<SettingsIcon className="h-4 w-4" />} title="Change your details">
      <form onSubmit={onSubmit} className="border-t border-line px-5 py-5">
        <div className="flex flex-col gap-3.5">
          <Field label="Your full name">
            <input
              value={about.name}
              onChange={(e) => setAboutField("name", e.target.value)}
              className={inputClass}
              required
            />
          </Field>

          <div className="grid gap-3.5 sm:grid-cols-2">
            <Field label="Date of birth">
              <input
                type="date"
                value={about.date_of_birth}
                onChange={(e) => setAboutField("date_of_birth", e.target.value)}
                className={`${inputClass} cursor-pointer`}
                required
              />
            </Field>
            <Field label="Gender">
              <select
                value={about.gender}
                onChange={(e) => setAboutField("gender", e.target.value)}
                className={selectClass}
              >
                {GENDERS.map((one) => (
                  <option key={one.value} value={one.value}>
                    {one.label}
                  </option>
                ))}
              </select>
            </Field>
          </div>

          <Field label="Your category">
            <select
              value={about.category}
              onChange={(e) => setAboutField("category", e.target.value)}
              className={selectClass}
            >
              {CATEGORIES.map((one) => (
                <option key={one.value} value={one.value}>
                  {one.label}
                </option>
              ))}
            </select>
          </Field>

          <div className="grid gap-3.5 sm:grid-cols-2">
            <Field label="State">
              <select
                value={about.state}
                onChange={(e) => setAboutField("state", e.target.value)}
                className={selectClass}
              >
                {STATES.map((one) => (
                  <option key={one} value={one}>
                    {one}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="District">
              <input
                value={about.district}
                onChange={(e) => setAboutField("district", e.target.value)}
                className={inputClass}
                required
              />
            </Field>
          </div>

          <label className="flex cursor-pointer items-center gap-2.5 text-[12.5px] text-ink">
            <input
              type="checkbox"
              checked={about.is_pwbd}
              onChange={(e) => setAboutField("is_pwbd", e.target.checked)}
              className="h-4 w-4 cursor-pointer accent-[#2563eb]"
            />
            I have a benchmark disability certificate
          </label>

          <label className="flex cursor-pointer items-center gap-2.5 text-[12.5px] text-ink">
            <input
              type="checkbox"
              checked={about.is_ex_serviceman}
              onChange={(e) => setAboutField("is_ex_serviceman", e.target.checked)}
              className="h-4 w-4 cursor-pointer accent-[#2563eb]"
            />
            I am an ex serviceman
          </label>
        </div>

        <div className="mt-6 flex flex-col gap-3.5">
          <p className="text-[13px] font-semibold text-ink">Your education</p>
          {entries.map((entry, index) => (
            <EducationCard
              key={entry.level}
              entry={entry}
              onChange={(next) =>
                setEntries((current) => current.map((one, at) => (at === index ? next : one)))
              }
              onRemove={
                entry.level === "class_10"
                  ? undefined
                  : () => setEntries((current) => current.filter((_, at) => at !== index))
              }
            />
          ))}

          {available.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {available.map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => addLevel(level)}
                  className="cursor-pointer rounded-[9px] border border-line bg-page px-3.5 py-2 text-[12.5px] font-medium text-ink transition-colors hover:border-accent hover:text-accent"
                >
                  Add {LEVEL_LABEL[level]}
                </button>
              ))}
            </div>
          ) : null}
        </div>

        {problem ? (
          <div className="mt-4">
            <Problem message={problem} />
          </div>
        ) : null}

        <div className="mt-5 flex flex-wrap items-center gap-2.5">
          <button
            type="submit"
            disabled={busy}
            className="cursor-pointer rounded-[9px] bg-ink px-4 py-2.5 text-[12.5px] font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {busy ? "Saving" : "Save my details"}
          </button>
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="cursor-pointer rounded-[9px] border border-line px-4 py-2.5 text-[12.5px] font-medium text-ink-soft transition-colors hover:bg-line-soft"
          >
            Cancel
          </button>
        </div>
      </form>
    </Card>
  );
}
