import { FileIcon } from "@/components/icons";
import { Card, Offline, PageHead } from "@/components/ui";
import { longDate } from "@/lib/format";
import { currentUser } from "@/lib/session";
import { todayDate } from "@/lib/today";

import { MyFiles, type MasterDocument } from "./my-files";

export const dynamic = "force-dynamic";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

async function loadDocuments(token: string): Promise<MasterDocument[] | null> {
  try {
    const response = await fetch(`${BASE}/me/documents`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as MasterDocument[];
  } catch {
    return null;
  }
}

export default async function DocumentsPage() {
  const session = await currentUser();
  if (!session?.me.student_id) {
    return <Offline hint="Fill your details first, then come back here." />;
  }

  const documents = await loadDocuments(session.token);
  if (!documents) {
    return <Offline hint="The document maker runs on the backend." />;
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHead date={longDate(todayDate())} greeting="My Documents" />

      <p className="-mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
        Each commission asks for a different size, and a form rejects a file that is even slightly
        too large. Upload your photo, signature and thumb impression once. Sarathi stores them and
        makes the exact size each form needs.
      </p>

      <Card
        icon={<FileIcon className="h-4 w-4" />}
        title="Your pictures"
      >
        <MyFiles documents={documents} token={session.token} />
      </Card>

      <p className="text-[11.5px] leading-relaxed text-ink-faint">
        Sizes are taken from each commission&apos;s instructions and from the notifications Sarathi
        has read. Check the notification before you upload.
      </p>
    </div>
  );
}
