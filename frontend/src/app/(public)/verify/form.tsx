"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { AuthShell, Field, Problem, inputClass, submitClass } from "@/components/auth-shell";
import { auth, startSession } from "@/lib/auth";

function VerifyForm() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email") ?? "";

  const [code, setCode] = useState("");
  const [problem, setProblem] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setProblem(null);
    try {
      const session = await auth.verify(email, code.trim());
      await startSession(session);
      router.push("/profile");
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
      setBusy(false);
    }
  }

  async function onResend() {
    setProblem(null);
    try {
      const result = await auth.resend(email);
      setNote(result.message);
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
    }
  }

  return (
    <AuthShell
      step="Step 2 of 3"
      title="Type your code"
      hint={`We sent six digits to ${email || "your email"}. It works for ten minutes.`}
      footer={
        <button type="button" onClick={onResend} className="font-medium text-accent hover:underline">
          Send the code again
        </button>
      }
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <Field label="Six digit code">
          <input
            inputMode="numeric"
            pattern="\d{6}"
            maxLength={6}
            required
            autoFocus
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
            placeholder="000000"
            className={`${inputClass} text-center text-[20px] font-semibold tracking-[0.35em]`}
          />
        </Field>

        {note ? (
          <p className="rounded-[9px] bg-accent-soft px-3.5 py-2.5 text-[12.5px] text-accent">{note}</p>
        ) : null}
        <Problem message={problem} />

        <button type="submit" disabled={busy || code.length !== 6} className={submitClass}>
          {busy ? "Checking" : "Confirm my email"}
        </button>
      </form>
    </AuthShell>
  );
}

export function VerifyScreen() {
  return (
    <Suspense fallback={null}>
      <VerifyForm />
    </Suspense>
  );
}
