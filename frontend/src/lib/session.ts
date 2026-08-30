import { cookies } from "next/headers";

import type { Me } from "@/lib/auth";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
export const COOKIE = "sarathi_token";

export interface ServerSession {
  token: string;
  me: Me;
}

export async function readToken(): Promise<string | null> {
  const jar = await cookies();
  return jar.get(COOKIE)?.value ?? null;
}

export async function currentUser(): Promise<ServerSession | null> {
  const token = await readToken();
  if (!token) return null;

  try {
    const response = await fetch(`${BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return { token, me: (await response.json()) as Me };
  } catch {
    return null;
  }
}

export async function whereToResume(): Promise<string | null> {
  const session = await currentUser();
  if (!session) return null;
  return session.me.student_id ? "/dashboard" : "/profile";
}
