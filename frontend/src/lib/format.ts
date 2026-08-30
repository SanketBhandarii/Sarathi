import type { Bucket } from "@/lib/types";

export const BUCKET_TONE: Record<Bucket, string> = {
  apply_now: "bg-good-soft text-good",
  coming_soon: "bg-cold-soft text-cold",
  not_yet: "bg-wait-soft text-wait",
  closed_for_now: "bg-mute-soft text-mute",
  not_for_you: "bg-stop-soft text-stop",
  unknown: "bg-mute-soft text-mute",
};

export const BUCKET_ORDER: Bucket[] = [
  "apply_now",
  "coming_soon",
  "not_yet",
  "closed_for_now",
  "unknown",
  "not_for_you",
];

export const SOURCE_NAME: Record<string, string> = {
  ssc: "Staff Selection Commission",
  upsc: "Union Public Service Commission",
  ibps: "Banking (IBPS)",
  mpsc: "Maharashtra PSC",
  bmc: "Mumbai (BMC)",
};

export function rupees(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) return "—";
  return `₹${Math.round(amount).toLocaleString("en-IN")}`;
}

export function shortDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
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
