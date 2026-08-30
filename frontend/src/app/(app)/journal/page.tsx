import { Card, Offline } from "@/components/ui";
import { api } from "@/lib/api";
import { currentUser } from "@/lib/session";
import type { JournalRun } from "@/lib/types";

export const dynamic = "force-dynamic";

function whenRan(iso: string): string {
  const at = new Date(iso);
  return at.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function Counter({ value, label }: { value: number | string; label: string }) {
  return (
    <div>
      <p className="text-[17px] font-semibold leading-none tabular-nums text-ink">{value}</p>
      <p className="mt-1 text-[11px] text-ink-soft">{label}</p>
    </div>
  );
}

function Run({ run }: { run: JournalRun }) {
  const spoke = run.messages_sent > 0;
  return (
    <li className="px-4 py-4">
      <div className="flex flex-wrap items-center gap-2">
        <p className="text-[12.5px] font-medium text-ink">{whenRan(run.ran_at)}</p>
        <span
          className={`rounded-pill px-2.5 py-1 text-[11px] font-medium ${
            spoke ? "bg-cold-soft text-cold" : "bg-mute-soft text-mute"
          }`}
        >
          {spoke
            ? `${run.messages_sent} message${run.messages_sent === 1 ? "" : "s"} sent`
            : "said nothing"}
        </span>
        <span className="text-[11px] text-ink-faint">took {run.seconds_taken}s</span>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Counter value={run.sources_checked} label="sources checked" />
        <Counter value={run.citations_verified} label="quotes re-checked" />
        <Counter value={run.rules_evaluated} label="rules evaluated" />
        <Counter value={run.messages_sent} label="messages to you" />
      </div>

      <ul className="mt-3 flex flex-col gap-1 border-l border-line pl-3">
        {run.events.map((event, index) => (
          <li
            key={index}
            className={`text-[11.5px] leading-relaxed ${
              event.worth_telling ? "font-medium text-ink" : "text-ink-faint"
            }`}
          >
            {event.worth_telling ? "→ " : "· "}
            {event.detail}
          </li>
        ))}
      </ul>
    </li>
  );
}

export default async function JournalPage() {
  const session = await currentUser();
  const studentId = session?.me.student_id;
  if (!studentId) return <Offline hint="Your profile is not ready yet." />;

  let runs: JournalRun[];
  try {
    runs = await api.journal(studentId, 12);
  } catch {
    return <Offline hint="The journal is written by the agent into Postgres each night." />;
  }

  const silent = runs.filter((run) => run.was_silent).length;
  const totalChecks = runs.reduce((sum, run) => sum + run.checks_run, 0);

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-[19px] font-semibold tracking-tight text-ink">Agent Journal</h1>
        <p className="mt-1 max-w-2xl text-[12.5px] leading-relaxed text-ink-soft">
          Most nights Sarathi reads every notification, re-checks every quote against the original
          pdf, and then writes to you about none of it. This page is the proof that it was working.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-card border border-line bg-surface px-4 py-4">
          <p className="text-[24px] font-semibold leading-none tabular-nums text-ink">
            {totalChecks.toLocaleString("en-IN")}
          </p>
          <p className="mt-2 text-[12px] font-medium text-ink">checks run</p>
          <p className="mt-0.5 text-[11px] text-ink-soft">across the runs below</p>
        </div>
        <div className="rounded-card border border-line bg-surface px-4 py-4">
          <p className="text-[24px] font-semibold leading-none tabular-nums text-ink">{silent}</p>
          <p className="mt-2 text-[12px] font-medium text-ink">
            night{silent === 1 ? "" : "s"} it stayed quiet
          </p>
          <p className="mt-0.5 text-[11px] text-ink-soft">nothing needed you</p>
        </div>
        <div className="rounded-card border border-line bg-surface px-4 py-4">
          <p className="text-[24px] font-semibold leading-none tabular-nums text-ink">
            {runs.reduce((sum, run) => sum + run.messages_sent, 0)}
          </p>
          <p className="mt-2 text-[12px] font-medium text-ink">messages sent</p>
          <p className="mt-0.5 text-[11px] text-ink-soft">only when it mattered</p>
        </div>
      </div>

      <Card title="Every run">
        {runs.length === 0 ? (
          <p className="px-4 py-8 text-center text-[13px] text-ink-soft">
            No runs recorded yet.
          </p>
        ) : (
          <ul className="divide-y divide-line">
            {runs.map((run) => (
              <Run key={run.id} run={run} />
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
