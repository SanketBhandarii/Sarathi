"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { AuthShell, Field, Problem, inputClass, submitClass } from "@/components/auth-shell";
import { auth, startSession } from "@/lib/auth";

export default function SignInPage() {
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
      const session = await auth.signIn(email.trim(), password);
      await startSession(session);
      router.push(session.student_id ? "/dashboard" : "/profile");
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      hint="Sign in to see what Sarathi found for you."
      footer={
        <>
          New here?{" "}
          <Link href="/join" className="font-medium text-accent hover:underline">
            Create an account
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
        <Field label="Password">
          <input
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={inputClass}
          />
        </Field>

        <Problem message={problem} />

        <button type="submit" disabled={busy} className={submitClass}>
          {busy ? "Signing in" : "Sign in"}
        </button>
      </form>
    </AuthShell>
  );
}
