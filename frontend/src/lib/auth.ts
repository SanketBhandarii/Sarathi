const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export interface Session {
  email: string;
  is_verified: boolean;
  student_id: number | null;
  token: string;
}

export interface Me {
  email: string;
  student_id: number | null;
  has_profile: boolean;
  name: string | null;
}


interface FieldProblem {
  loc?: (string | number)[];
  msg?: string;
}

const FIELD_NAMES: Record<string, string> = {
  name: "your name",
  date_of_birth: "your date of birth",
  district: "your district",
  state: "your state",
  marks: "the marks",
  cgpa_scale: "the CGPA scale",
  passed_year: "the year",
  current_semester: "the semester",
  board_or_university: "the board or university",
  email: "your email",
  password: "your password",
};

function describeField(problem: FieldProblem): string {
  const parts = (problem.loc ?? []).filter((part) => typeof part === "string");
  const last = parts[parts.length - 1] as string | undefined;
  return last ? (FIELD_NAMES[last] ?? last.replace(/_/g, " ")) : "one of the fields";
}

export function readProblem(data: unknown): string {
  if (typeof data === "string") return data;

  const detail = (data as { detail?: unknown })?.detail;
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail) && detail.length > 0) {
    const fields = Array.from(new Set(detail.map((item) => describeField(item as FieldProblem))));
    if (fields.length === 1) {
      return `Please check ${fields[0]}.`;
    }
    return `Please check ${fields.slice(0, -1).join(", ")} and ${fields[fields.length - 1]}.`;
  }

  return "Something went wrong. Please try again.";
}

async function post<T>(path: string, body: unknown, token?: string): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: "include",
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(readProblem(data));
  }
  return data as T;
}

export const auth = {
  signUp: (email: string, password: string) =>
    post<{ message: string }>("/auth/sign-up", { email, password }),

  verify: (email: string, code: string) => post<Session>("/auth/verify", { email, code }),

  resend: (email: string) => post<{ message: string }>("/auth/resend-code", { email }),

  signIn: (email: string, password: string) => post<Session>("/auth/sign-in", { email, password }),

  saveProfile: (profile: Record<string, unknown>, token: string) =>
    post<Me>("/auth/profile", profile, token),

  async me(token: string): Promise<Me> {
    const response = await fetch(`${BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: "include",
      cache: "no-store",
    });
    if (!response.ok) throw new Error("Please sign in again.");
    return (await response.json()) as Me;
  },
};

export async function startSession(session: Session): Promise<void> {
  keepSession(session);
  await fetch("/api/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: session.token }),
  });
}

export async function endSession(): Promise<void> {
  forgetSession();
  await fetch("/api/session", { method: "DELETE" });
}

const KEY = "sarathi.session";

export function keepSession(session: Session): void {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(session));
  } catch {
    /* storage can be blocked, the cookie still works */
  }
}

export function readSession(): Session | null {
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

export function forgetSession(): void {
  try {
    window.localStorage.removeItem(KEY);
  } catch {
    /* nothing to do */
  }
}
