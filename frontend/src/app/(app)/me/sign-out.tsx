"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { endSession } from "@/lib/auth";

export function SignOut({ email }: { email: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  async function onClick() {
    setBusy(true);
    await endSession();
    router.push("/sign-in");
    router.refresh();
  }

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-card border border-line bg-shell px-5 py-4">
      <div>
        <p className="text-[12.5px] font-medium text-ink">Signed in as {email}</p>
        <p className="mt-0.5 text-[11.5px] text-ink-soft">
          Sign out to use a different account on this computer.
        </p>
      </div>
      <button
        type="button"
        onClick={onClick}
        disabled={busy}
        className="cursor-pointer whitespace-nowrap rounded-[9px] border border-line bg-page px-4 py-2.5 text-[12.5px] font-medium text-ink transition-colors hover:border-stop hover:text-stop disabled:cursor-not-allowed disabled:opacity-60"
      >
        {busy ? "Signing out" : "Sign out"}
      </button>
    </div>
  );
}
