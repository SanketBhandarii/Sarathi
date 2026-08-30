import { Offline, Panel } from "@/components/panel";
import { DEMO_STUDENT, DEMO_TODAY, api } from "@/lib/api";
import { shortDate } from "@/lib/format";
import type { AgeCliff, Deadline } from "@/lib/types";

export const dynamic = "force-dynamic";

const URGENCY_TONE: Record<Deadline["urgency"], string> = {
  today: "bg-stop-soft text-stop",
  "this week": "bg-wait-soft text-wait",
  "this month": "bg-cold-soft text-cold",
  later: "bg-mute-soft text-mute",
};

export default async function DeadlinesPage() {
  let deadlines: Deadline[];
  let cliff: AgeCliff;
  try {
    [deadlines, cliff] = await Promise.all([
      api.deadlines(DEMO_STUDENT, { today: DEMO_TODAY }),
      api.ageCliff(DEMO_STUDENT, { today: DEMO_TODAY }),
    ]);
  } catch {
    return <Offline hint="Deadlines are worked out from the notifications on the backend." />;
  }

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-[19px] font-semibold tracking-tight text-ink">Deadlines</h1>
        <p className="mt-1 text-[12.5px] text-ink-soft">
          Dates taken from the official notification, not from a job website.
        </p>
      </div>

      {cliff.has_warning ? (
        <div className="rounded-card border border-wait/25 bg-wait-soft px-4 py-3">
          <p className="text-[12px] font-medium uppercase tracking-wide text-wait/80">Age limit</p>
          <p className="mt-1 text-[13px] font-medium text-wait">{cliff.message}</p>
          <ul className="mt-2 flex flex-col gap-1">
            {cliff.exams_closing.map((exam) => (
              <li key={exam.exam_name} className="text-[11.5px] text-wait">
                · {exam.exam_name} — your limit is {exam.limit_for_you}, closes{" "}
                {shortDate(exam.closes_on)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <Panel
        title="Coming up"
        subtitle={
          deadlines.length === 0
            ? "Nothing closing in the next few months."
            : `${deadlines.length} date${deadlines.length === 1 ? "" : "s"} to keep.`
        }
      >
        {deadlines.length === 0 ? (
          <p className="px-4 py-8 text-center text-[13px] text-ink-soft">
            No deadline needs you right now.
          </p>
        ) : (
          <ul className="divide-y divide-line">
            {deadlines.map((deadline) => (
              <li key={`${deadline.source_id}-${deadline.exam_name}`} className="px-4 py-3.5">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`rounded-pill px-2.5 py-1 text-[11px] font-medium ${URGENCY_TONE[deadline.urgency]}`}
                  >
                    {deadline.days_left} days left
                  </span>
                  <p className="text-[13px] font-medium text-ink">{deadline.exam_name}</p>
                  {deadline.you_can_apply ? (
                    <span className="rounded-pill bg-good-soft px-2 py-0.5 text-[10.5px] font-medium text-good">
                      you qualify
                    </span>
                  ) : null}
                </div>
                <p className="mt-1.5 text-[12px] text-ink-soft">{deadline.plain_words}</p>
                {deadline.citation_quote ? (
                  <p className="mt-1 text-[11px] text-ink-faint">
                    page {deadline.citation_page} — “{deadline.citation_quote.slice(0, 120)}”
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  );
}
