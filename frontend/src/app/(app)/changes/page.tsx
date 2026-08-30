import { JournalIcon, QuoteIcon } from "@/components/icons";
import { Card, Offline, PageHead } from "@/components/ui";
import { longDate, shortDate } from "@/lib/format";
import { currentUser } from "@/lib/session";
import { todayDate } from "@/lib/today";

export const dynamic = "force-dynamic";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

interface RuleChange {
  kind: string;
  field: string;
  told_you: string | null;
  now_says: string | null;
  is_worse_for_student: boolean;
  plain_words: string;
  old_citation: { page: number; quote: string } | null;
  new_citation: { page: number; quote: string } | null;
}

interface ExamChange {
  exam_name: string;
  source_id: string;
  noticed_on: string;
  from_a_real_second_version: boolean;
  how_this_was_made: string;
  corrigendum: {
    apology: string;
    has_changes: boolean;
    changes: RuleChange[];
  };
}

async function load(studentId: number): Promise<ExamChange[] | null> {
  try {
    const response = await fetch(`${BASE}/students/${studentId}/changes`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as ExamChange[];
  } catch {
    return null;
  }
}

function Change({ change }: { change: RuleChange }) {
  const bothQuotes =
    change.old_citation !== null &&
    change.new_citation !== null &&
    change.old_citation.quote.trim() !== change.new_citation.quote.trim();

  return (
    <li
      className={`rounded-card border px-4 py-3.5 ${
        change.is_worse_for_student ? "border-stop/25 bg-stop-soft" : "border-line bg-page"
      }`}
    >
      <p
        className={`text-[13px] leading-relaxed ${
          change.is_worse_for_student ? "font-medium text-stop" : "text-ink"
        }`}
      >
        {change.plain_words}
      </p>

      <div className={`mt-2.5 grid gap-2 ${bothQuotes ? "sm:grid-cols-2" : ""}`}>
        {bothQuotes && change.old_citation ? (
          <div className="rounded-[8px] border border-line bg-shell px-3 py-2">
            <p className="text-[10.5px] font-medium uppercase tracking-wide text-ink-faint">
              What I told you
            </p>
            <p className="mt-1 flex items-start gap-1.5 text-[11.5px] leading-relaxed text-ink-soft">
              <QuoteIcon className="mt-[3px] h-3 w-3 shrink-0" />
              <span>
                page {change.old_citation.page}: “{change.old_citation.quote.slice(0, 110)}”
              </span>
            </p>
          </div>
        ) : null}

        {change.new_citation ? (
          <div className="rounded-[8px] border border-accent/25 bg-accent-soft px-3 py-2">
            <p className="text-[10.5px] font-medium uppercase tracking-wide text-accent/80">
              {bothQuotes ? "What it says now" : "The line this came from"}
            </p>
            <p className="mt-1 flex items-start gap-1.5 text-[11.5px] leading-relaxed text-accent">
              <QuoteIcon className="mt-[3px] h-3 w-3 shrink-0" />
              <span>
                page {change.new_citation.page}: “{change.new_citation.quote.slice(0, 110)}”
              </span>
            </p>
          </div>
        ) : null}
      </div>
    </li>
  );
}

export default async function ChangesPage() {
  const session = await currentUser();
  const studentId = session?.me.student_id;
  if (!studentId) return <Offline hint="Your profile is not ready yet." />;

  const changes = await load(studentId);
  if (!changes) {
    return <Offline hint="Corrections are worked out on the backend." />;
  }

  const urgent = changes.filter((c) =>
    c.corrigendum.changes.some((change) => change.is_worse_for_student),
  ).length;

  return (
    <div className="flex flex-col gap-6">
      <PageHead date={longDate(todayDate())} greeting="When I was wrong" />

      <p className="-mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
        Indian commissions change dates and rules after they publish. Most websites quietly update
        and say nothing. Sarathi re reads every notification, and when what it told you no longer
        matches the document, it says so.
      </p>

      {urgent > 0 ? (
        <div className="rounded-card border border-stop/25 bg-stop-soft px-5 py-4">
          <p className="text-[13.5px] font-medium text-stop">
            {urgent} {urgent === 1 ? "exam has" : "exams have"} moved earlier than I told you.
            You have less time than you thought.
          </p>
        </div>
      ) : null}

      {changes.length === 0 ? (
        <Card icon={<JournalIcon className="h-4 w-4" />} title="Nothing has changed">
          <p className="border-t border-line px-5 py-10 text-center text-[13px] text-ink-soft">
            Every rule still matches what I told you.
          </p>
        </Card>
      ) : null}

      {changes.map((change) => (
        <Card
          key={`${change.source_id}-${change.exam_name}`}
          icon={<JournalIcon className="h-4 w-4" />}
          title={change.exam_name}
        >
          <div className="border-t border-line px-5 py-4">
            <p className="text-[13.5px] font-medium text-ink">{change.corrigendum.apology}</p>
            <p className="mt-1 text-[11.5px] text-ink-faint">
              Noticed on {shortDate(change.noticed_on)}
            </p>

            <ul className="mt-4 flex flex-col gap-3">
              {change.corrigendum.changes.map((item, index) => (
                <Change key={index} change={item} />
              ))}
            </ul>

            {!change.from_a_real_second_version ? (
              <p className="mt-4 rounded-[9px] border border-line bg-page px-3.5 py-2.5 text-[11.5px] leading-relaxed text-ink-soft">
                <span className="font-medium text-ink">How this one was made: </span>
                {change.how_this_was_made}
              </p>
            ) : null}
          </div>
        </Card>
      ))}
    </div>
  );
}
