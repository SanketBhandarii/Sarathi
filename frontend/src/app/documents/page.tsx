import { DocumentMaker } from "@/components/document-maker";
import { Card, Offline } from "@/components/ui";
import type { DocumentSpec } from "@/lib/types";

export const dynamic = "force-dynamic";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function loadSpecs(): Promise<DocumentSpec[] | null> {
  try {
    const response = await fetch(`${BASE}/documents/specs`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as DocumentSpec[];
  } catch {
    return null;
  }
}

export default async function DocumentsPage() {
  const specs = await loadSpecs();

  if (!specs) {
    return <Offline hint="The document maker runs on the backend." />;
  }

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-[19px] font-semibold tracking-tight text-ink">My Documents</h1>
        <p className="mt-1 max-w-2xl text-[12.5px] leading-relaxed text-ink-soft">
          Forms reject a photo that is one kilobyte too big. Give Sarathi the picture from your
          phone once and it makes every file at the exact size the notification asks for.
        </p>
      </div>

      <Card
        title="What IBPS PO asks for"
      >
        <ul className="divide-y divide-line">
          {specs.map((spec) => (
            <li key={spec.kind} className="flex items-center justify-between gap-3 px-4 py-2.5">
              <span className="text-[12.5px] font-medium text-ink">{spec.label}</span>
              <span className="text-[11.5px] tabular-nums text-ink-soft">{spec.needed}</span>
            </li>
          ))}
        </ul>
      </Card>

      <Card title="Make my files">
        <DocumentMaker specs={specs} />
      </Card>
    </div>
  );
}
