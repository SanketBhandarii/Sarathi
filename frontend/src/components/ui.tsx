import { CaretIcon } from "@/components/icons";

export function PageHead({
  date,
  greeting,
  actions,
}: {
  date: string;
  greeting: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div>
        <p className="text-[12.5px] text-ink-soft">{date}</p>
        <h1 className="mt-1.5 font-display text-[30px] font-semibold leading-tight tracking-tight text-ink sm:text-[34px]">
          {greeting}
        </h1>
      </div>
      {actions ? <div className="flex items-center gap-2.5 pt-1">{actions}</div> : null}
    </div>
  );
}

export function GhostButton({
  children,
  icon,
}: {
  children: React.ReactNode;
  icon?: React.ReactNode;
}) {
  return (
    <button
      type="button"
      className="flex items-center gap-2 rounded-[9px] border border-line bg-shell px-3.5 py-2 text-[13px] font-medium text-ink transition-colors hover:bg-line-soft"
    >
      {icon}
      {children}
    </button>
  );
}

export function StatStrip({
  items,
}: {
  items: { icon: React.ReactNode; value: string; label: string }[];
}) {
  return (
    <div className="inline-flex flex-wrap items-center gap-x-1 gap-y-2 rounded-pill border border-line bg-shell px-5 py-3">
      {items.map((item, index) => (
        <div key={item.label} className="flex items-center">
          {index > 0 ? <span className="mx-4 hidden h-5 w-px bg-line sm:block" /> : null}
          <span className="flex items-center gap-2.5 text-ink-soft">
            {item.icon}
            <span className="text-[14.5px] font-semibold tabular text-ink">{item.value}</span>
            <span className="text-[13px] text-ink-soft">{item.label}</span>
          </span>
        </div>
      ))}
    </div>
  );
}

export function Card({
  icon,
  title,
  chip,
  action,
  children,
}: {
  icon?: React.ReactNode;
  title: string;
  chip?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="overflow-hidden rounded-card border border-line bg-shell">
      <div className="flex flex-wrap items-center gap-3 px-5 py-4">
        {icon ? <span className="text-ink-soft">{icon}</span> : null}
        <h2 className="text-[16px] font-semibold tracking-tight text-ink">{title}</h2>
        {chip ? (
          <button
            type="button"
            className="flex items-center gap-1.5 rounded-[8px] border border-line px-2.5 py-1 text-[12px] font-medium text-ink-soft transition-colors hover:bg-line-soft"
          >
            {chip}
            <CaretIcon className="h-3 w-3" />
          </button>
        ) : null}
        {action ? <div className="ml-auto">{action}</div> : null}
      </div>
      {children}
    </section>
  );
}

export function PillButton({ children }: { children: React.ReactNode }) {
  return (
    <button
      type="button"
      className="rounded-pill bg-line-soft px-3.5 py-1.5 text-[12.5px] font-medium text-ink-soft transition-colors hover:bg-line hover:text-ink"
    >
      {children}
    </button>
  );
}

export function Offline({ hint }: { hint: string }) {
  return (
    <div className="rounded-card border border-line bg-shell px-6 py-12 text-center">
      <p className="text-[14px] font-medium text-ink">Sarathi cannot reach its backend</p>
      <p className="mx-auto mt-2 max-w-md text-[12.5px] leading-relaxed text-ink-soft">{hint}</p>
      <pre className="mx-auto mt-4 w-fit rounded-[9px] bg-page px-4 py-2.5 text-left text-[11.5px] text-ink-soft">
        cd backend{"\n"}.venv/Scripts/python -m uvicorn app.main:app --reload
      </pre>
    </div>
  );
}
