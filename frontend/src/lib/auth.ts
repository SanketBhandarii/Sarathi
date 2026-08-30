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
    throw new Error(data.detail ?? "Something went wrong. Please try again.");
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
