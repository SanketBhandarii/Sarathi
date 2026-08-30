import type { Bucket } from "@/lib/types";

export const BUCKET_TONE: Record<Bucket, string> = {
  apply_now: "bg-good-soft text-good",
  coming_soon: "bg-cold-soft text-cold",
  not_yet: "bg-sun-soft text-sun",
  closed_for_now: "bg-mute-soft text-mute",
  not_for_you: "bg-stop-soft text-stop",
  unknown: "bg-wait-soft text-wait",
};

export const BODY_TONE: Record<string, string> = {
  ssc: "bg-[#7c5cff]",
  upsc: "bg-[#2563eb]",
  ibps: "bg-[#33c481]",
  mpsc: "bg-[#f5a524]",
  bmc: "bg-[#e879c8]",
};

export function rupees(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) return ",";
  return `₹${Math.round(amount).toLocaleString("en-IN")}`;
}

export function shortDate(iso: string | null): string {
  if (!iso) return ",";
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function longDate(date: Date): string {
  return date.toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
}

export function initials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

export function greetingFor(hour: number): string {
  if (hour < 12) return "Good Morning";
  if (hour < 17) return "Good Afternoon";
  return "Good Evening";
}
