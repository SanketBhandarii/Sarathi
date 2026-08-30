import type {
  AgeCliff,
  Deadline,
  JournalRun,
  Language,
  Radar,
  SavingsSummary,
  Student,
} from "@/lib/types";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function get<T>(path: string, params?: Record<string, string | undefined>): Promise<T> {
  const url = new URL(path, BASE);
  for (const [key, value] of Object.entries(params ?? {})) {
    if (value !== undefined) url.searchParams.set(key, value);
  }

  const response = await fetch(url.toString(), { cache: "no-store" });
  if (!response.ok) {
    throw new ApiError(`${path} returned ${response.status}`, response.status);
  }
  return (await response.json()) as T;
}

export interface ViewOptions {
  today?: string;
  lang?: Language;
}

export const api = {
  student: (id: number) => get<Student>(`/students/${id}`),

  radar: (id: number, options: ViewOptions = {}) =>
    get<Radar>(`/students/${id}/radar`, { today: options.today, lang: options.lang }),

  deadlines: (id: number, options: ViewOptions = {}) =>
    get<Deadline[]>(`/students/${id}/deadlines`, { today: options.today }),

  journal: (id: number, limit = 10) =>
    get<JournalRun[]>(`/students/${id}/journal`, { limit: String(limit) }),

  savings: (id: number) => get<SavingsSummary>(`/students/${id}/savings`),

  ageCliff: (id: number, options: ViewOptions = {}) =>
    get<AgeCliff>(`/students/${id}/age-cliff`, { today: options.today }),
};

export const DEMO_TODAY = "2026-08-29";
export const DEMO_STUDENT = 1;
