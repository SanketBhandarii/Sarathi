"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { PlusIcon } from "@/components/icons";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

export function CheckNow({ studentId }: { studentId: number }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [said, setSaid] = useState<string | null>(null);

  async function run() {
    setBusy(true);
    setSaid(null);
    try {
      const response = await fetch(`${BASE}/students/${studentId}/journal/run`, {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok) throw new Error("could not run");
      const data = (await response.json()) as {
        checks_run: number;
        messages_sent: number;
      };
      setSaid(
        data.messages_sent === 0
          ? `${data.checks_run} checks, nothing needs you`
          : `${data.messages_sent} thing${data.messages_sent === 1 ? "" : "s"} need you`,
      );
      router.refresh();
    } catch {
      setSaid("could not check just now");
    } finally {
      setBusy(false);
      setTimeout(() => setSaid(null), 6000);
    }
  }

  return (
    <div className="flex items-center gap-2.5">
      {said ? <span className="hidden text-[12px] text-ink-soft sm:inline">{said}</span> : null}
      <button
        type="button"
        onClick={run}
        disabled={busy}
        className="flex items-center gap-1.5 rounded-[9px] bg-accent px-3.5 py-2 text-[13px] font-medium text-white transition-colors hover:bg-accent-hover disabled:opacity-60"
      >
        <PlusIcon className="h-[15px] w-[15px]" />
        {busy ? "Checking" : "Check now"}
      </button>
    </div>
  );
}
