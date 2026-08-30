import { ExamTable } from "@/components/exam-table";
import { Offline, Panel } from "@/components/panel";
import { StatCard } from "@/components/stat-card";
import { DEMO_STUDENT, DEMO_TODAY, api } from "@/lib/api";
import { rupees } from "@/lib/format";
import type { AgeCliff, Deadline, Radar, SavingsSummary } from "@/lib/types";

export const dynamic = "force-dynamic";

async function load() {
  try {
    const [radar, deadlines, savings, cliff] = await Promise.all([
      api.radar(DEMO_STUDENT, { today: DEMO_TODAY }),
      api.deadlines(DEMO_STUDENT, { today: DEMO_TODAY }),
      api.savings(DEMO_STUDENT),
      api.ageCliff(DEMO_STUDENT, { today: DEMO_TODAY }),
    ]);
    return { radar, deadlines, savings, cliff };
  } catch {
    return null;
  }
}

export default async function HomePage() {
  const data = await load();

  if (!data) {
    return (
      <Offline hint="The dashboard reads live data from the FastAPI backend. Start it and refresh this page." />
    );
  }

  const { radar, deadlines, savings, cliff } = data as {
    radar: Radar;
    deadlines: Deadline[];
    savings: SavingsSummary;
    cliff: AgeCliff;
  };

  const canApply = radar.counts.apply_now ?? 0;
  const soon = deadlines.filter((d) => d.days_left <= 30).length;
  const openNow = radar.entries.filter((e) => e.bucket === "apply_now");

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-[19px] font-semibold tracking-tight text-ink">
          Good evening, {radar.student_name.split(" ")[0]}
        </h1>
        <p className="mt-1 text-[12.5px] text-ink-soft">
          Sarathi is watching {radar.total_watched} exams for you. Everything below is checked
          against the government&apos;s own notification.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatCard
          tone="blue"
          value={String(canApply)}
          label={canApply === 1 ? "exam you can apply for" : "exams you can apply for"}
          hint="Checked against your age, category and state"
        />
        <StatCard
          tone="peach"
          value={String(soon)}
          label={soon === 1 ? "deadline this month" : "deadlines this month"}
          hint={deadlines[0] ? deadlines[0].plain_words.slice(0, 58) : "Nothing closing soon"}
        />
        <StatCard
          tone="violet"
          value={rupees(savings.total_saved)}
          label="you do not have to pay"
          hint={savings.total_saved > 0 ? savings.message.slice(0, 58) : "No fee concession for you"}
        />
      </div>

      {cliff.has_warning ? (
        <div className="rounded-card border border-wait/25 bg-wait-soft px-4 py-3">
          <p className="text-[12.5px] font-medium text-wait">{cliff.message}</p>
        </div>
      ) : null}

      <Panel
        title="You can apply now"
        subtitle="Open forms you actually qualify for. Tap a row to see the clause that proves it."
      >
        <ExamTable entries={openNow} />
      </Panel>

      <Panel
        title="Everything Sarathi watches"
        subtitle={`${radar.total_watched} exams, nothing hidden — sorted and labelled, never filtered away.`}
      >
        <ExamTable entries={radar.entries} />
      </Panel>
    </div>
  );
}
