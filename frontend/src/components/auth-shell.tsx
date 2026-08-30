import Link from "next/link";

export function AuthShell({
  step,
  title,
  hint,
  children,
  footer,
}: {
  step?: string;
  title: string;
  hint: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-page">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
        <Link href="/" className="font-display text-[23px] font-semibold tracking-tight text-ink">
          Sarathi
        </Link>
      </header>

      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 pb-16">
        <div className="rounded-shell border border-line bg-shell px-7 py-8">
          {step ? (
            <p className="text-[11.5px] font-medium uppercase tracking-[0.14em] text-ink-faint">
              {step}
            </p>
          ) : null}
          <h1 className="mt-2 font-display text-[26px] font-semibold leading-tight tracking-tight text-ink">
            {title}
          </h1>
          <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">{hint}</p>
          <div className="mt-6">{children}</div>
        </div>
        {footer ? <div className="mt-5 text-center text-[13px] text-ink-soft">{footer}</div> : null}
      </main>
    </div>
  );
}

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-[12.5px] font-medium text-ink">{label}</span>
      {children}
      {hint ? <span className="mt-1 block text-[11.5px] text-ink-faint">{hint}</span> : null}
    </label>
  );
}

export const inputClass =
  "mt-1.5 w-full rounded-[9px] border border-line bg-page px-3.5 py-2.5 text-[13.5px] text-ink outline-none transition-colors placeholder:text-ink-faint focus:border-accent focus:bg-shell";

export const submitClass =
  "w-full rounded-[10px] bg-accent px-4 py-2.5 text-[14px] font-medium text-white transition-colors hover:bg-accent-hover disabled:opacity-60";

export function Problem({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p className="mt-4 rounded-[9px] bg-stop-soft px-3.5 py-2.5 text-[12.5px] text-stop">{message}</p>
  );
}
