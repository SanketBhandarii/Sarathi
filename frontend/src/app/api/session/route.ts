import { NextResponse } from "next/server";

const COOKIE = "sarathi_token";
const MAX_AGE = 60 * 60 * 24 * 30;

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as { token?: string };
  if (!body.token) {
    return NextResponse.json({ error: "no token given" }, { status: 400 });
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.set(COOKIE, body.token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: MAX_AGE,
  });
  return response;
}

export async function DELETE() {
  const response = NextResponse.json({ ok: true });
  response.cookies.set(COOKIE, "", { httpOnly: true, path: "/", maxAge: 0 });
  return response;
}
