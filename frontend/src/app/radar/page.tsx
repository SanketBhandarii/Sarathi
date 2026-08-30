import { ExamTable } from "@/components/exam-table";
import { Card, Offline } from "@/components/ui";
import { DEMO_STUDENT, DEMO_TODAY, api } from "@/lib/api";
import type { Layer, Radar } from "@/lib/types";

export const dynamic = "force-dynamic";

const LAYER_ORDER: Layer[] = [
  "central",
  "your_state",
  "your_city",
  "open_to_all_states",
  "another_state",
];

const LAYER_NOTE: Record<Layer, string> = {
  central: "Open to every Indian, wherever you live.",
  your_state: "These need your state's domicile, and you have it.",
  your_city: "Your own city and district. National websites rarely show these.",
  open_to_all_states: "Other states that take applicants from anywhere.",
  another_state: "Closed to you because they need a different state's domicile.",
};

export default async function RadarPage() {
  let radar: Radar;
  try {
    radar = await api.radar(DEMO_STUDENT, { today: DEMO_TODAY });
  } catch {
    return <Offline hint="The Radar reads every exam from the backend." />;
  }

  const layers = LAYER_ORDER.map((layer) => ({
    layer,
    entries: radar.entries.filter((entry) => entry.layer === layer),
  })).filter((group) => group.entries.length > 0);

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-[19px] font-semibold tracking-tight text-ink">Exam Radar</h1>
        <p className="mt-1 text-[12.5px] text-ink-soft">
          Every exam Sarathi watches, in four layers. Nothing is hidden — exams you cannot take
          are shown too, with the reason.
        </p>
      </div>

      {layers.map(({ layer, entries }) => (
        <Card
          key={layer}
          title={entries[0].layer_label}
          action={
            <span className="rounded-pill bg-brand-soft px-2.5 py-1 text-[11px] font-medium text-ink-soft">
              {entries.length}
            </span>
          }
        >
          <ExamTable entries={entries} />
        </Card>
      ))}
    </div>
  );
}
