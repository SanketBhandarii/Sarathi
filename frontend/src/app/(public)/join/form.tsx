"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { AuthShell, Field, Problem, inputClass, submitClass } from "@/components/auth-shell";
import { auth } from "@/lib/auth";

export function JoinForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [problem, setProblem] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setProblem(null);
    try {
      await auth.signUp(email.trim(), password);
      router.push(`/verify?email=${encodeURIComponent(email.trim())}`);
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
      setBusy(false);
    }
  }

  return (
    <AuthShell
      step="Step 1 of 3"
      title="Create your account"
      hint="We will send a six digit code to your email to make sure it is really yours."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/sign-in" className="font-medium text-accent hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <Field label="Email">
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@gmail.com"
            className={inputClass}
          />
        </Field>

        <Field label="Password" hint="At least 8 characters. Not only numbers.">
          <input
            type="password"
            required
            minLength={8}
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Something only you know"
            className={inputClass}
          />
        </Field>

        <Problem message={problem} />

        <button type="submit" disabled={busy} className={submitClass}>
          {busy ? "Sending your code" : "Send me a code"}
        </button>
      </form>
    </AuthShell>
  );
}
