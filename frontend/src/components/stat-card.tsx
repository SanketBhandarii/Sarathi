type Tone = "blue" | "peach" | "violet";

const TONES: Record<Tone, string> = {
  blue: "from-[#dbe7fb] via-[#e8ecfb] to-[#f2f0fc]",
  peach: "from-[#fde8dc] via-[#fdeee4] to-[#fbf3ec]",
  violet: "from-[#f3e4f7] via-[#f3e9fb] to-[#eeeefc]",
};

export function StatCard({
  tone,
  value,
  label,
  hint,
}: {
  tone: Tone;
  value: string;
  label: string;
  hint?: string;
}) {
  return (
    <div
      className={`stat-sheen rounded-card border border-line bg-gradient-to-br ${TONES[tone]} px-4 py-4`}
    >
      <p className="relative text-[24px] font-semibold leading-none tracking-tight text-ink">
        {value}
      </p>
      <p className="relative mt-2 text-[12px] font-medium text-ink">{label}</p>
      {hint ? <p className="relative mt-0.5 text-[11px] text-ink-soft">{hint}</p> : null}
    </div>
  );
}
