export function Panel({
  title,
  subtitle,
  action,
  children,
}: {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="overflow-hidden rounded-card border border-line bg-surface">
      <div className="flex items-center justify-between gap-3 border-b border-line px-4 py-3">
        <div className="min-w-0">
          <h2 className="text-[13px] font-semibold text-ink">{title}</h2>
          {subtitle ? <p className="mt-0.5 text-[11.5px] text-ink-soft">{subtitle}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

export function Offline({ hint }: { hint: string }) {
  return (
    <div className="rounded-card border border-line bg-surface px-6 py-10 text-center">
      <p className="text-[13px] font-medium text-ink">Sarathi cannot reach its backend</p>
      <p className="mx-auto mt-2 max-w-md text-[12px] leading-relaxed text-ink-soft">{hint}</p>
      <pre className="mx-auto mt-4 w-fit rounded-[10px] bg-page px-4 py-2 text-left text-[11.5px] text-ink-soft">
        cd backend{"\n"}.venv/Scripts/python -m uvicorn app.main:app --reload
      </pre>
    </div>
  );
}
