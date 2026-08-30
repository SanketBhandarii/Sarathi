import Link from "next/link";

import { CheckCircleIcon, ClockIcon, QuoteIcon, RadarIcon } from "@/components/icons";

export const dynamic = "force-static";

const PROBLEMS = [
  {
    number: "01",
    title: "You do not know what exists",
    body: "Thirty lakh people fight for SSC CGL. Meanwhile RBI Grade B, NABARD and SEBI take far fewer applicants, because far fewer people have heard of them.",
  },
  {
    number: "02",
    title: "You do not know if you qualify",
    body: "Eligibility is five rules multiplied together. Age, category relaxation, qualification, domicile, attempts used. Most students find out only after paying the fee.",
  },
  {
    number: "03",
    title: "Then the paperwork takes it away",
    body: "The photo must be 20 to 50 KB. The correction window opens for five days and nobody announces it. A year is lost to a form, not to an exam.",
  },
];

const DOES = [
  {
    icon: <RadarIcon className="h-[18px] w-[18px]" />,
    title: "Reads every notification",
    body: "Straight from ssc.gov.in, upsc.gov.in, ibps.in and the state commissions. Never from a job website.",
  },
  {
    icon: <CheckCircleIcon className="h-[18px] w-[18px]" />,
    title: "Gives a verdict on each one",
    body: "Not a list. An answer. You can apply, you cannot, or here is exactly what would make you eligible.",
  },
  {
    icon: <QuoteIcon className="h-[18px] w-[18px]" />,
    title: "Shows the line it read",
    body: "Every claim carries the page number and the sentence from the commission's own pdf. Check any of it yourself.",
  },
  {
    icon: <ClockIcon className="h-[18px] w-[18px]" />,
    title: "Holds every date",
    body: "Correction windows, fee dates, admit cards. It wakes you only when a date is actually yours.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-page">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="font-display text-[23px] font-semibold tracking-tight text-ink">
          Sarathi
        </span>
        <nav className="flex items-center gap-2.5">
          <Link
            href="/sign-in"
            className="rounded-[9px] px-3.5 py-2 text-[13.5px] font-medium text-ink-soft transition-colors hover:bg-line-soft hover:text-ink"
          >
            Sign in
          </Link>
          <Link
            href="/join"
            className="rounded-[9px] bg-accent px-4 py-2 text-[13.5px] font-medium text-white transition-colors hover:bg-accent-hover"
          >
            Start free
          </Link>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-6 pb-24">
        <section className="rounded-shell border border-line bg-shell px-6 py-16 text-center sm:px-12 sm:py-20">
          <p className="text-[13px] font-medium uppercase tracking-[0.14em] text-ink-faint">
            For one government exam aspirant
          </p>
          <h1 className="mx-auto mt-5 max-w-3xl font-display text-[40px] font-semibold leading-[1.1] tracking-tight text-ink sm:text-[54px]">
            You sit one exam a year. You fight paperwork all year.
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-[15px] leading-relaxed text-ink-soft">
            Sarathi watches every government exam in India for you, quietly, every day. It tells you
            only what you can actually get, and stays silent the rest of the time.
          </p>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/join"
              className="rounded-[10px] bg-accent px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-accent-hover"
            >
              Create your account
            </Link>
            <Link
              href="/dashboard"
              className="rounded-[10px] border border-line bg-shell px-6 py-3 text-[14px] font-medium text-ink transition-colors hover:bg-line-soft"
            >
              See a live example
            </Link>
          </div>
          <p className="mt-5 text-[12.5px] text-ink-faint">
            Free for students, permanently. No fee, no advertising.
          </p>
        </section>

        <section className="mt-6 grid gap-4 sm:grid-cols-3">
          {PROBLEMS.map((problem) => (
            <div key={problem.number} className="rounded-card border border-line bg-shell p-6">
              <span className="font-display text-[15px] font-semibold text-accent">
                {problem.number}
              </span>
              <h3 className="mt-3 text-[15px] font-semibold tracking-tight text-ink">
                {problem.title}
              </h3>
              <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">{problem.body}</p>
            </div>
          ))}
        </section>

        <section className="mt-6 overflow-hidden rounded-shell border border-line bg-shell">
          <div className="border-b border-line px-8 py-8">
            <h2 className="font-display text-[26px] font-semibold tracking-tight text-ink">
              An agent, not another app to open
            </h2>
            <p className="mt-2 max-w-2xl text-[13.5px] leading-relaxed text-ink-soft">
              Most nights Sarathi reads every notification, re checks every quote against the
              original pdf, and writes to you about none of it. Silence is the point.
            </p>
          </div>
          <div className="grid sm:grid-cols-2">
            {DOES.map((item, index) => (
              <div
                key={item.title}
                className={`px-8 py-7 ${index % 2 === 0 ? "sm:border-r" : ""} ${index < 2 ? "border-b" : ""} border-line`}
              >
                <span className="flex h-9 w-9 items-center justify-center rounded-[9px] bg-accent-soft text-accent">
                  {item.icon}
                </span>
                <h3 className="mt-3.5 text-[15px] font-semibold tracking-tight text-ink">
                  {item.title}
                </h3>
                <p className="mt-1.5 text-[13px] leading-relaxed text-ink-soft">{item.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-6 rounded-shell border border-line bg-ink px-8 py-12 text-center sm:px-12">
          <h2 className="mx-auto max-w-2xl font-display text-[28px] font-semibold leading-tight tracking-tight text-white sm:text-[34px]">
            A missed form costs a year of your life
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-[14px] leading-relaxed text-white/70">
            Fill your details once. After that Sarathi carries the dates, the rules and the
            paperwork, for as many years as you need it.
          </p>
          <Link
            href="/join"
            className="mt-8 inline-block rounded-[10px] bg-white px-6 py-3 text-[14px] font-medium text-ink transition-opacity hover:opacity-90"
          >
            Create your account
          </Link>
        </section>
      </main>
    </div>
  );
}
