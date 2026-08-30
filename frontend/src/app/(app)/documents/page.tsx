import { FileIcon } from "@/components/icons";
import { BodyPicker } from "./picker";
import { Card, Offline, PageHead } from "@/components/ui";
import { longDate } from "@/lib/format";
import { todayDate } from "@/lib/today";
import type { BodyRules } from "@/components/document-maker";

export const dynamic = "force-dynamic";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

async function loadRules(): Promise<BodyRules[] | null> {
  try {
    const response = await fetch(`${BASE}/documents/specs`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as BodyRules[];
  } catch {
    return null;
  }
}

export default async function DocumentsPage() {
  const rules = await loadRules();

  if (!rules || rules.length === 0) {
    return <Offline hint="The document maker runs on the backend." />;
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHead date={longDate(todayDate())} greeting="My Documents" />

      <p className="-mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
        A form will reject a photo that is one kilobyte too big. Give each picture once and
        Sarathi makes it the exact size that commission asks for. Every commission asks for
        something different, so pick the one you are applying to.
      </p>

      <Card icon={<FileIcon className="h-4 w-4" />} title="Make my files">
        <BodyPicker rules={rules} />
      </Card>

      <p className="text-[11.5px] leading-relaxed text-ink-faint">
        Sizes are taken from each commission&apos;s own instructions. When we have read a
        notification directly, its sizes are used instead. Always check the notification before
        you upload.
      </p>
    </div>
  );
}
