const OVERRIDE = process.env.NEXT_PUBLIC_DEMO_TODAY;

export function todayIso(): string {
  if (OVERRIDE) return OVERRIDE;
  return new Date().toISOString().slice(0, 10);
}

export function todayDate(): Date {
  return new Date(`${todayIso()}T12:00:00`);
}
