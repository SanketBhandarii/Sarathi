"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthShell, Field, Problem, inputClass, submitClass } from "@/components/auth-shell";
import { auth, readSession } from "@/lib/auth";

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

const ONLY_DIGITS = /[^0-9]/g;
const ONLY_NUMBER = /[^0-9.]/g;

export default function ProfilePage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [problem, setProblem] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [form, setForm] = useState({
    name: "",
    date_of_birth: "",
    category: "UR",
    gender: "male",
    is_pwbd: false,
    is_ex_serviceman: false,
    state: "Maharashtra",
    district: "",
    degree: "",
    stream: "",
    completed_year: "",
    percentage: "",
    is_completed: true,
  });

  useEffect(() => {
    const session = readSession();
    if (!session) {
      router.replace("/sign-in");
      return;
    }
    setToken(session.token);
  }, [router]);

  function set<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    setProblem(null);
    try {
      await auth.saveProfile(
        {
          ...form,
          stream: form.stream || null,
          completed_year: form.completed_year ? Number(form.completed_year) : null,
          percentage: form.percentage ? Number(form.percentage) : null,
        },
        token,
      );
      router.push("/dashboard");
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
      setBusy(false);
    }
  }

  return (
    <AuthShell
      step="Step 3 of 3"
      title="Tell Sarathi about you"
      hint="Fill this once. Every verdict, every deadline and every document is worked out from these details."
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <Field label="Your full name" hint="Exactly as on your 10th standard certificate.">
          <input
            required
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
            placeholder="Ravi Patil"
            className={inputClass}
          />
        </Field>

        <Field label="Date of birth" hint="Age limits are counted from this.">
          <input
            type="date"
            required
            max="2012-12-31"
            value={form.date_of_birth}
            onChange={(e) => set("date_of_birth", e.target.value)}
            className={inputClass}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Category" hint="This decides your age relaxation and your fee.">
            <select
              value={form.category}
              onChange={(e) => set("category", e.target.value)}
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
              value={form.gender}
              onChange={(e) => set("gender", e.target.value)}
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
              checked={form.is_pwbd}
              onChange={(e) => set("is_pwbd", e.target.checked)}
              className="h-4 w-4 accent-[#2563eb]"
            />
            I have a benchmark disability (PwBD)
          </label>
          <label className="flex items-center gap-2.5 text-[13px] text-ink">
            <input
              type="checkbox"
              checked={form.is_ex_serviceman}
              onChange={(e) => set("is_ex_serviceman", e.target.checked)}
              className="h-4 w-4 accent-[#2563eb]"
            />
            I am an ex serviceman
          </label>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="State of domicile" hint="This opens your state and city exams.">
            <select
              value={form.state}
              onChange={(e) => set("state", e.target.value)}
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
              value={form.district}
              onChange={(e) => set("district", e.target.value)}
              placeholder="Nagpur"
              className={inputClass}
            />
          </Field>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Highest qualification">
            <input
              required
              value={form.degree}
              onChange={(e) => set("degree", e.target.value)}
              placeholder="B.Tech"
              className={inputClass}
            />
          </Field>

          <Field label="Stream" hint="Leave blank if it does not apply.">
            <input
              value={form.stream}
              onChange={(e) => set("stream", e.target.value)}
              placeholder="Computer Science"
              className={inputClass}
            />
          </Field>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Year of passing">
            <input
              inputMode="numeric"
              value={form.completed_year}
              onChange={(e) => set("completed_year", e.target.value.replace(ONLY_DIGITS, "").slice(0, 4))}
              placeholder="2026"
              className={inputClass}
            />
          </Field>

          <Field label="Percentage" hint="If your marksheet shows CGPA, use the conversion your university prints.">
            <input
              inputMode="decimal"
              value={form.percentage}
              onChange={(e) => set("percentage", e.target.value.replace(ONLY_NUMBER, "").slice(0, 5))}
              placeholder="58"
              className={inputClass}
            />
          </Field>
        </div>

        <label className="flex items-center gap-2.5 rounded-[9px] border border-line bg-page px-3.5 py-3 text-[13px] text-ink">
          <input
            type="checkbox"
            checked={form.is_completed}
            onChange={(e) => set("is_completed", e.target.checked)}
            className="h-4 w-4 accent-[#2563eb]"
          />
          I have finished this degree
        </label>

        <Problem message={problem} />

        <button type="submit" disabled={busy || !token} className={submitClass}>
          {busy ? "Saving" : "Start watching my exams"}
        </button>
      </form>
    </AuthShell>
  );
}
