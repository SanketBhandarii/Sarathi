import { AlertIcon, ChevronIcon } from "@/components/icons";
import { Card, Offline, PageHead } from "@/components/ui";
import { longDate, shortDate } from "@/lib/format";
import { currentUser } from "@/lib/session";
import { todayDate } from "@/lib/today";

export const dynamic = "force-dynamic";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

interface PublishedCorrection {
  exam_name: string;
  official_title: string;
  body: string;
  source_id: string;
  origin_url: string;
  fetched_on: string;
  we_could_read_it: boolean;
  what_we_can_say: string;
}

async function load(studentId: number): Promise<PublishedCorrection[] | null> {
  try {
    const response = await fetch(`${BASE}/students/${studentId}/changes`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as PublishedCorrection[];
  } catch {
    return null;
  }
}

export default async function ChangesPage() {
  const session = await currentUser();
  const studentId = session?.me.student_id;
  if (!studentId) return <Offline hint="Your profile is not ready yet." />;

  const corrections = await load(studentId);
  if (!corrections) {
    return <Offline hint="Corrections are worked out on the backend." />;
  }

  const unreadable = corrections.filter((c) => !c.we_could_read_it).length;

  return (
    <div className="flex flex-col gap-6">
      <PageHead date={longDate(todayDate())} greeting="Corrections" />

      <p className="-mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
        Commissions change dates and rules after they publish, and they do it in a separate notice
        most students never see. Sarathi watches for those notices. When it can read one, it tells
        you exactly what changed and admits what it told you before was wrong.
      </p>

      {corrections.length === 0 ? (
        <Card icon={<AlertIcon className="h-4 w-4" />} title="Nothing has changed">
          <p className="border-t border-line px-5 py-10 text-center text-[13px] text-ink-soft">
            No commission has published a correction for the exams you are watching.
          </p>
        </Card>
      ) : (
        <Card
          icon={<AlertIcon className="h-4 w-4" />}
          title={`${corrections.length} correction${corrections.length === 1 ? "" : "s"} published`}
        >
          <ul className="border-t border-line">
            {corrections.map((item) => (
              <li key={item.origin_url} className="border-b border-line px-5 py-4 last:border-0">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-[13.5px] font-medium text-ink">{item.exam_name}</p>
                  <span
                    className={`rounded-[6px] px-2 py-0.5 text-[11px] font-medium ${
                      item.we_could_read_it
                        ? "bg-good-soft text-good"
                        : "bg-sun-soft text-sun"
                    }`}
                  >
                    {item.we_could_read_it ? "read" : "scanned, cannot read"}
                  </span>
                  <span className="text-[11.5px] text-ink-faint">
                    seen {shortDate(item.fetched_on)}
                  </span>
                </div>

                <p className="mt-1 text-[12px] text-ink-soft">{item.official_title}</p>
                <p className="mt-2 text-[12.5px] leading-relaxed text-ink">
                  {item.what_we_can_say}
                </p>

                <a
                  href={item.origin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-flex items-center gap-1.5 rounded-[9px] border border-line bg-shell px-3.5 py-2 text-[12.5px] font-medium text-ink transition-colors hover:border-accent hover:text-accent"
                >
                  Open the notice from {item.body}
                  <ChevronIcon className="h-3.5 w-3.5" />
                </a>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {unreadable > 0 ? (
        <div className="rounded-card border border-line bg-page px-5 py-4">
          <p className="text-[12.5px] font-medium text-ink">
            Why {unreadable} of these say &quot;cannot read&quot;
          </p>
          <p className="mt-1.5 text-[12px] leading-relaxed text-ink-soft">
            UPSC and MPSC publish corrections as photographs of paper rather than as text. There is
            nothing in the file to read. Sarathi will not invent what a notice says, so it does the
            one useful thing it can: it tells you the correction exists, which is the part students
            usually miss, and takes you straight to the commission&apos;s own page.
          </p>
        </div>
      ) : null}
    </div>
  );
}
