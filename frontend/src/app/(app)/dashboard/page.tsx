import { CheckCircleIcon, ClockIcon, RadarIcon, ShareIcon, PlusIcon, ListIcon, JournalIcon, CalendarIcon } from "@/components/icons";
import { ExamTable } from "@/components/exam-table";
import { Card, GhostButton, Offline, PageHead, PillButton, StatStrip } from "@/components/ui";
import { api } from "@/lib/api";
import { currentUser } from "@/lib/session";
import { todayDate, todayIso } from "@/lib/today";
import { greetingFor, longDate, rupees } from "@/lib/format";
import type { AgeCliff, Deadline, JournalRun, Radar, SavingsSummary } from "@/lib/types";

export const dynamic = "force-dynamic";

async function load(studentId: number, today: string) {
  try {
    const [radar, deadlines, savings, cliff, journal] = await Promise.all([
      api.radar(studentId, { today }),
      api.deadlines(studentId, { today }),
      api.savings(studentId),
      api.ageCliff(studentId, { today }),
      api.journal(studentId, 4),
    ]);
    return { radar, deadlines, savings, cliff, journal };
  } catch {
    return null;
  }
}

function UrgencyDot({ days }: { days: number }) {
  const tone = days <= 7 ? "bg-stop" : days <= 30 ? "bg-sun" : "bg-cold";
  return <span className={`h-full w-[3px] shrink-0 rounded-full ${tone}`} />;
}

export default async function DashboardPage() {
  const session = await currentUser();
  const studentId = session?.me.student_id;
  if (!studentId) return <Offline hint="Your profile is not ready yet." />;

  const today = todayIso();
  const data = await load(studentId, today);
  if (!data) {
    return <Offline hint="This dashboard reads live data from the FastAPI backend." />;
  }

  const { radar, deadlines, savings, cliff, journal } = data as {
    radar: Radar;
    deadlines: Deadline[];
    savings: SavingsSummary;
    cliff: AgeCliff;
    journal: JournalRun[];
  };


  const canApply = radar.entries.filter((e) => e.bucket === "apply_now");
  const totalChecks = journal.reduce((sum, run) => sum + run.checks_run, 0);

  return (
    <div className="flex flex-col gap-6">
      <PageHead
        date={longDate(todayDate())}
        greeting={`${greetingFor(todayDate().getHours() || 19)}! ${radar.student_name.split(" ")[0]},`}
        actions={
          <>
            <GhostButton icon={<ShareIcon />}>Share</GhostButton>
            <GhostButton icon={<PlusIcon className="h-[15px] w-[15px]" />}>Add exam</GhostButton>
          </>
        }
      />

      <StatStrip
        items={[
          {
            icon: <RadarIcon className="h-[15px] w-[15px]" />,
            value: String(radar.total_watched),
            label: "Exams Watched",
          },
          {
            icon: <CheckCircleIcon />,
            value: String(canApply.length),
            label: "You Can Apply",
          },
          {
            icon: <ClockIcon />,
            value: String(deadlines.filter((d) => d.days_left <= 30).length),
            label: "Closing Soon",
          },
          {
            icon: <ListIcon className="h-[15px] w-[15px]" />,
            value: rupees(savings.total_saved),
            label: "Fee You Save",
          },
        ]}
      />

      {cliff.has_warning ? (
        <div className="rounded-card border border-sun/25 bg-sun-soft px-5 py-3.5">
          <p className="text-[13px] font-medium text-sun">{cliff.message}</p>
        </div>
      ) : null}

      <Card
        icon={<ListIcon />}
        title="Open for you"
        chip="This month"
        action={<PillButton>See all</PillButton>}
      >
        <ExamTable entries={canApply} />
      </Card>

      <div className="grid gap-5 xl:grid-cols-2">
        <Card icon={<CalendarIcon className="h-4 w-4" />} title="What is closing">
          {deadlines.length === 0 ? (
            <p className="px-5 py-10 text-center text-[13px] text-ink-soft">
              Nothing closing in the next few months.
            </p>
          ) : (
            <ul className="border-t border-line">
              {deadlines.map((deadline) => (
                <li
                  key={`${deadline.source_id}-${deadline.exam_name}`}
                  className="flex gap-3 border-b border-line px-5 py-3.5 last:border-0"
                >
                  <UrgencyDot days={deadline.days_left} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-[13.5px] font-medium text-ink">
                      {deadline.exam_name}
                    </p>
                    <p className="mt-0.5 text-[12px] text-ink-soft">{deadline.plain_words}</p>
                  </div>
                  <span className="shrink-0 self-center rounded-[7px] bg-line-soft px-2.5 py-1 text-[12px] font-medium tabular text-ink-soft">
                    {deadline.days_left}d
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card icon={<JournalIcon className="h-4 w-4" />} title="What Sarathi did">
          <div className="border-t border-line px-5 py-4">
            <p className="text-[12.5px] leading-relaxed text-ink-soft">
              {totalChecks.toLocaleString("en-IN")} checks across the last {journal.length} runs.
              Most nights it finds nothing worth telling you, and says nothing.
            </p>
          </div>
          <ul className="border-t border-line">
            {journal.map((run) => (
              <li key={run.id} className="flex items-start gap-3 border-b border-line px-5 py-3.5 last:border-0">
                <span
                  className={`mt-1 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border ${
                    run.was_silent ? "border-line bg-shell" : "border-wait bg-wait"
                  }`}
                >
                  {run.was_silent ? null : (
                    <svg viewBox="0 0 24 24" className="h-2.5 w-2.5 text-white" fill="none" stroke="currentColor" strokeWidth="3.4">
                      <path d="m6 12.5 4 4 8-9" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  )}
                </span>
                <div className="min-w-0 flex-1">
                  <p className={`text-[13px] ${run.was_silent ? "text-ink-soft" : "font-medium text-ink"}`}>
                    {run.was_silent
                      ? "Checked everything, said nothing"
                      : `Told you about ${run.messages_sent} thing${run.messages_sent === 1 ? "" : "s"}`}
                  </p>
                  <p className="mt-0.5 text-[11.5px] text-ink-faint">
                    {run.checks_run} checks · {run.sources_checked} sources · {run.seconds_taken}s
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}
