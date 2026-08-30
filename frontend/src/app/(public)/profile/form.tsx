"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { AuthShell, Field, Problem, inputClass, submitClass } from "@/components/auth-shell";
import {
  ALWAYS_ON,
  EducationCard,
  type Entry,
  LEVEL_LABEL,
  type Level,
  ORDER,
  blankEntry,
  toPercentage,
} from "@/components/education-ladder";
import { auth } from "@/lib/auth";

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

const selectClass = `${inputClass} appearance-none`;

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

export function ProfileForm({ token }: { token: string }) {
  const router = useRouter();
  const [problem, setProblem] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [about, setAbout] = useState({
    name: "",
    date_of_birth: "",
    category: "UR",
    gender: "male",
    is_pwbd: false,
    is_ex_serviceman: false,
    state: "Maharashtra",
    district: "",
  });

  const [entries, setEntries] = useState<Entry[]>([
    blankEntry("class_10"),
    blankEntry("class_12"),
  ]);

  const chosen = new Set(entries.map((entry) => entry.level));
  const available = ORDER.filter((level) => !chosen.has(level));

  function setAboutField<K extends keyof typeof about>(key: K, value: (typeof about)[K]) {
    setAbout((current) => ({ ...current, [key]: value }));
  }

  function addLevel(level: Level) {
    setEntries((current) =>
      [...current, blankEntry(level)].sort(
        (a, b) => ORDER.indexOf(a.level) - ORDER.indexOf(b.level),
      ),
    );
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setProblem(null);

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
      setProblem("Please fill at least your 10th standard marks.");
      setBusy(false);
      return;
    }

    try {
      await auth.saveProfile({ ...about, qualifications }, token);
      router.push("/dashboard");
      router.refresh();
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
      setBusy(false);
    }
  }

  const highest = [...entries]
    .filter((entry) => entry.is_completed && entry.marks)
    .sort((a, b) => ORDER.indexOf(b.level) - ORDER.indexOf(a.level))[0];

  return (
    <AuthShell
      step="Step 3 of 3"
      title="Tell Sarathi about you"
      hint="Fill this once. Every verdict, every deadline and every document is worked out from these details."
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-5">
        <div className="flex flex-col gap-4">
          <Field label="Your full name" hint="Exactly as on your 10th standard certificate.">
            <input
              required
              value={about.name}
              onChange={(e) => setAboutField("name", e.target.value)}
              placeholder="Ravi Patil"
              className={inputClass}
            />
          </Field>

          <Field label="Date of birth" hint="Age limits are counted from this.">
            <input
              type="date"
              required
              max="2012-12-31"
              value={about.date_of_birth}
              onChange={(e) => setAboutField("date_of_birth", e.target.value)}
              className={inputClass}
            />
          </Field>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Category" hint="This decides your age relaxation and your fee.">
              <select
                value={about.category}
                onChange={(e) => setAboutField("category", e.target.value)}
                className={selectClass}
              >
                {CATEGORIES.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Gender">
              <select
                value={about.gender}
                onChange={(e) => setAboutField("gender", e.target.value)}
                className={selectClass}
              >
                {GENDERS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </Field>
          </div>

          <div className="flex flex-col gap-2.5 rounded-[9px] border border-line bg-page px-3.5 py-3">
            <label className="flex items-center gap-2.5 text-[13px] text-ink">
              <input
                type="checkbox"
                checked={about.is_pwbd}
                onChange={(e) => setAboutField("is_pwbd", e.target.checked)}
                className="h-4 w-4 accent-[#2563eb]"
              />
              I have a benchmark disability (PwBD)
            </label>
            <label className="flex items-center gap-2.5 text-[13px] text-ink">
              <input
                type="checkbox"
                checked={about.is_ex_serviceman}
                onChange={(e) => setAboutField("is_ex_serviceman", e.target.checked)}
                className="h-4 w-4 accent-[#2563eb]"
              />
              I am an ex serviceman
            </label>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="State of domicile" hint="This opens your state and city exams.">
              <select
                value={about.state}
                onChange={(e) => setAboutField("state", e.target.value)}
                className={selectClass}
              >
                {STATES.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="District">
              <input
                required
                value={about.district}
                onChange={(e) => setAboutField("district", e.target.value)}
                placeholder="Nagpur"
                className={inputClass}
              />
            </Field>
          </div>
        </div>

        <div className="border-t border-line pt-5">
          <h2 className="text-[15px] font-semibold tracking-tight text-ink">Your education</h2>
          <p className="mt-1 text-[12.5px] leading-relaxed text-ink-soft">
            Add every level you have finished, starting from 10th. Different exams ask for
            different levels, so the more you fill, the more Sarathi can check for you.
          </p>

          <div className="mt-4 flex flex-col gap-4">
            {entries.map((entry, index) => (
              <EducationCard
                key={entry.level}
                entry={entry}
                onChange={(next) =>
                  setEntries((current) => current.map((item, i) => (i === index ? next : item)))
                }
                onRemove={
                  ALWAYS_ON.includes(entry.level)
                    ? undefined
                    : () => setEntries((current) => current.filter((_, i) => i !== index))
                }
              />
            ))}
          </div>

          {available.length > 0 ? (
            <div className="mt-4">
              <p className="text-[12.5px] font-medium text-ink">Add another level</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {available.map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => addLevel(level)}
                    className="rounded-pill border border-line bg-shell px-3.5 py-1.5 text-[12.5px] font-medium text-ink-soft transition-colors hover:border-accent hover:text-accent"
                  >
                    + {LEVEL_LABEL[level]}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          {highest ? (
            <p className="mt-4 rounded-[9px] bg-accent-soft px-3.5 py-2.5 text-[12.5px] text-accent">
              Sarathi will treat {LEVEL_LABEL[highest.level].toLowerCase()} as your highest
              qualification, at about {toPercentage(highest)}%.
            </p>
          ) : null}
        </div>

        <Problem message={problem} />

        <button type="submit" disabled={busy} className={submitClass}>
          {busy ? "Saving" : "Start watching my exams"}
        </button>
      </form>
    </AuthShell>
  );
}
