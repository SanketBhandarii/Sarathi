import { CalendarIcon, ClockIcon } from "@/components/icons";
import { Card, Offline, PageHead } from "@/components/ui";
import { api } from "@/lib/api";
import { currentUser } from "@/lib/session";
import { todayDate, todayIso } from "@/lib/today";
import { longDate, shortDate } from "@/lib/format";
import type { AgeCliff, Deadline } from "@/lib/types";

export const dynamic = "force-dynamic";

const URGENCY_TONE: Record<Deadline["urgency"], string> = {
  today: "bg-stop-soft text-stop",
  "this week": "bg-sun-soft text-sun",
  "this month": "bg-cold-soft text-cold",
  later: "bg-mute-soft text-mute",
};

export default async function DeadlinesPage() {
  const session = await currentUser();
  const studentId = session?.me.student_id;
  if (!studentId) return <Offline hint="Your profile is not ready yet." />;

  const today = todayIso();
  let deadlines: Deadline[];
  let cliff: AgeCliff;
  try {
    [deadlines, cliff] = await Promise.all([
      api.deadlines(studentId, { today }),
      api.ageCliff(studentId, { today }),
    ]);
  } catch {
    return <Offline hint="Deadlines are worked out from the notifications on the backend." />;
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHead date={longDate(todayDate())} greeting="Deadlines" />

      <p className="-mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
        Every date here was read out of the commission&apos;s own notification, not copied from a
        job website.
      </p>

      {cliff.has_warning ? (
        <div className="rounded-card border border-sun/25 bg-sun-soft px-5 py-4">
          <p className="text-[11.5px] font-medium uppercase tracking-wide text-sun/80">Age limit</p>
          <p className="mt-1 text-[14px] font-medium text-sun">{cliff.message}</p>
          <ul className="mt-2 flex flex-col gap-1">
            {cliff.exams_closing.map((exam) => (
              <li key={exam.exam_name} className="text-[12px] text-sun">
                · {exam.exam_name}. Your limit is {exam.limit_for_you}, closes{" "}
                {shortDate(exam.closes_on)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <Card icon={<CalendarIcon className="h-4 w-4" />} title="Coming up">
        {deadlines.length === 0 ? (
          <p className="px-5 py-10 text-center text-[13px] text-ink-soft">
            No deadline needs you right now.
          </p>
        ) : (
          <ul className="border-t border-line">
            {deadlines.map((deadline) => (
              <li
                key={`${deadline.source_id}-${deadline.exam_name}`}
                className="border-b border-line px-5 py-4 last:border-0"
              >
                <div className="flex flex-wrap items-center gap-2.5">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-[7px] px-2.5 py-1 text-[12px] font-medium ${URGENCY_TONE[deadline.urgency]}`}
                  >
                    <ClockIcon className="h-3.5 w-3.5" />
                    {deadline.days_left} days left
                  </span>
                  <p className="text-[13.5px] font-medium text-ink">{deadline.exam_name}</p>
                  {deadline.you_can_apply ? (
                    <span className="rounded-[6px] bg-good-soft px-2 py-0.5 text-[11px] font-medium text-good">
                      you qualify
                    </span>
                  ) : null}
                </div>
                <p className="mt-2 text-[12.5px] text-ink-soft">{deadline.plain_words}</p>
                {deadline.citation_quote ? (
                  <p className="mt-1 text-[11.5px] text-ink-faint">
                    page {deadline.citation_page}: “{deadline.citation_quote.slice(0, 130)}”
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
