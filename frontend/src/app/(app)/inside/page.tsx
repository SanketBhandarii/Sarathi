import { CheckCircleIcon, QuoteIcon, RadarIcon } from "@/components/icons";
import { Card, Offline, PageHead } from "@/components/ui";
import { longDate } from "@/lib/format";
import { todayDate } from "@/lib/today";

export const dynamic = "force-dynamic";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

interface Tool {
  name: string;
  what_it_does: string;
}

interface Agent {
  name: string;
  job: string;
  model_role: string;
  tools: Tool[];
}

interface Graph {
  agents: Agent[];
  edges: { frm: string; to: string; when: string }[];
  loops_back: boolean;
  max_passes: number;
}

interface CheckLine {
  field: string;
  page: number;
  quote: string;
  quote_is_on_that_page: boolean;
  match: string;
  value: number | null;
  value_is_in_the_quote: boolean | null;
}

interface Verify {
  exam_name: string;
  source_id: string;
  document_pages: number;
  quotes_checked: number;
  numbers_checked: number;
  problems: number;
  took_seconds: number;
  used_a_model: boolean;
  lines: CheckLine[];
}

async function load<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export default async function InsidePage() {
  const [graph, verify] = await Promise.all([
    load<Graph>("/inside/graph"),
    load<Verify>("/inside/verify"),
  ]);

  if (!graph) {
    return <Offline hint="The agents run on the backend." />;
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHead date={longDate(todayDate())} greeting="Inside Sarathi" />

      <p className="-mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
        Every number on the other screens came out of a government PDF. This page shows how, and
        it reads the wiring out of the running code rather than describing it.
      </p>

      <Card icon={<RadarIcon className="h-4 w-4" />} title="Two agents in a loop">
        <div className="border-t border-line px-5 py-5">
          <div className="grid gap-4 lg:grid-cols-2">
            {graph.agents.map((agent) => (
              <div key={agent.name} className="rounded-card border border-line bg-page px-4 py-4">
                <div className="flex items-center gap-2">
                  <span className="rounded-[6px] bg-accent px-2 py-0.5 text-[11px] font-medium text-white">
                    {agent.name}
                  </span>
                  <span className="text-[11.5px] text-ink-faint">Strands Agent</span>
                </div>
                <p className="mt-2 text-[12.5px] leading-relaxed text-ink">{agent.job}</p>
                <p className="mt-1 text-[11.5px] leading-relaxed text-ink-faint">
                  {agent.model_role}
                </p>

                <p className="mt-3 text-[11.5px] font-medium text-ink">
                  {agent.tools.length} tool{agent.tools.length === 1 ? "" : "s"}
                </p>
                <ul className="mt-1.5 flex flex-col gap-1.5">
                  {agent.tools.map((tool) => (
                    <li key={tool.name}>
                      <code className="rounded-[5px] bg-shell px-1.5 py-0.5 text-[11.5px] font-medium text-accent">
                        {tool.name}
                      </code>
                      <span className="ml-1.5 text-[11.5px] text-ink-soft">
                        {tool.what_it_does}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="mt-4 rounded-card border border-line bg-page px-4 py-3.5">
            <p className="text-[12px] font-medium text-ink">How they are wired</p>
            <ul className="mt-2 flex flex-col gap-1.5">
              {graph.edges.map((edge) => (
                <li key={`${edge.frm}-${edge.to}`} className="text-[12.5px] text-ink">
                  <code className="rounded-[5px] bg-shell px-1.5 py-0.5 text-[11.5px] text-accent">
                    {edge.frm}
                  </code>
                  <span className="mx-1.5 text-ink-faint">→</span>
                  <code className="rounded-[5px] bg-shell px-1.5 py-0.5 text-[11.5px] text-accent">
                    {edge.to}
                  </code>
                  <span className="ml-2 text-[11.5px] text-ink-soft">{edge.when}</span>
                </li>
              ))}
            </ul>
            <p className="mt-2.5 text-[11.5px] leading-relaxed text-ink-soft">
              That second edge is the point. It is a{" "}
              <span className="font-medium text-ink">cyclic Strands graph</span>: when the checker
              finds a problem, the work goes back to the reader instead of being saved. It gives up
              after {graph.max_passes} passes rather than looping forever.
            </p>
          </div>
        </div>
      </Card>

      {verify ? (
        <Card
          icon={<CheckCircleIcon className="h-4 w-4" />}
          title="Checking, right now, with no AI at all"
          action={
            <span className="rounded-pill bg-good-soft px-3 py-1 text-[12px] font-medium text-good">
              {verify.problems === 0 ? "all clean" : `${verify.problems} problems`}
            </span>
          }
        >
          <div className="border-t border-line px-5 py-4">
            <p className="text-[12.5px] leading-relaxed text-ink-soft">
              This ran when you opened the page. It took{" "}
              <span className="font-medium tabular text-ink">{verify.took_seconds}s</span> and used{" "}
              <span className="font-medium text-ink">no model</span>. It opened the real{" "}
              {verify.document_pages} page PDF for{" "}
              <span className="font-medium text-ink">{verify.exam_name}</span> and checked every
              claim twice: is the quoted sentence on the page it cites, and does the recorded
              number appear inside that sentence.
            </p>
            <p className="mt-2 text-[12px] leading-relaxed text-ink-faint">
              Both checks are plain code. We tested them by planting errors in real extracted data,
              changing a maximum age from 30 to 45. The AI verifier missed it. Arithmetic caught it
              instantly. So the checks that matter never depend on a model.
            </p>
          </div>

          <div className="overflow-x-auto scrollbar-thin border-t border-line">
            <table className="w-full min-w-[640px] text-left">
              <thead>
                <tr className="border-b border-line bg-page/40 text-[11px] font-medium uppercase tracking-wide text-ink-faint">
                  <th className="px-5 py-2.5 font-medium">Claim</th>
                  <th className="px-4 py-2.5 font-medium">Page</th>
                  <th className="px-4 py-2.5 font-medium">Quote is there</th>
                  <th className="px-4 py-2.5 font-medium">Number is in it</th>
                </tr>
              </thead>
              <tbody>
                {verify.lines.map((line) => (
                  <tr key={line.field} className="border-b border-line last:border-0">
                    <td className="px-5 py-2.5">
                      <p className="text-[12.5px] font-medium text-ink">{line.field}</p>
                      <p className="mt-0.5 flex items-start gap-1.5 text-[11px] text-ink-faint">
                        <QuoteIcon className="mt-[3px] h-2.5 w-2.5 shrink-0" />
                        <span>{line.quote.slice(0, 90)}</span>
                      </p>
                    </td>
                    <td className="px-4 py-2.5 text-[12px] tabular text-ink-soft">{line.page}</td>
                    <td className="px-4 py-2.5">
                      <span
                        className={`rounded-[6px] px-2 py-0.5 text-[11px] font-medium ${
                          line.quote_is_on_that_page
                            ? "bg-good-soft text-good"
                            : "bg-stop-soft text-stop"
                        }`}
                      >
                        {line.quote_is_on_that_page ? `yes, ${line.match}` : `no, ${line.match}`}
                      </span>
                    </td>
                    <td className="px-4 py-2.5">
                      {line.value_is_in_the_quote === null ? (
                        <span className="text-[11.5px] text-ink-faint">not a number</span>
                      ) : (
                        <span
                          className={`rounded-[6px] px-2 py-0.5 text-[11px] font-medium ${
                            line.value_is_in_the_quote
                              ? "bg-good-soft text-good"
                              : "bg-stop-soft text-stop"
                          }`}
                        >
                          {line.value_is_in_the_quote ? `yes, ${line.value}` : `no, ${line.value}`}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : null}

      <Card icon={<RadarIcon className="h-4 w-4" />} title="What decides your verdict">
        <div className="border-t border-line px-5 py-5">
          <p className="text-[13px] leading-relaxed text-ink">
            <span className="font-semibold">No model decides whether you can apply.</span> The
            agents read the document. Your age, your category relaxation, your qualification level,
            your marks, your domicile and your fee are worked out in plain Python from the rules
            they found.
          </p>
          <p className="mt-2 text-[12.5px] leading-relaxed text-ink-soft">
            That is deliberate. A model can be talked into agreeing that a diploma satisfies a
            degree requirement. Arithmetic cannot.
          </p>
        </div>
      </Card>
    </div>
  );
}
