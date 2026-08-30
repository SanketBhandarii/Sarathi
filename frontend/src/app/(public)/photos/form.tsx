"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { AuthShell, Problem, submitClass } from "@/components/auth-shell";
import { readProblem } from "@/lib/auth";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export type Kind = "photograph" | "signature" | "thumb_impression";

export interface MasterDocument {
  kind: Kind;
  label: string;
  guidance: string;
  file_id: string | null;
  view_url: string | null;
  is_private: boolean;
  width_px: number | null;
  height_px: number | null;
  byte_size: number | null;
}

const REQUIRED: Kind[] = ["photograph", "signature"];

function Tile({
  document: item,
  token,
  onDone,
}: {
  document: MasterDocument;
  token: string;
  onDone: (next: MasterDocument) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  async function onPick(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setBusy(true);
    setProblem(null);
    setPreview(URL.createObjectURL(file));

    const form = new FormData();
    form.append("file", file);

    try {
      const response = await fetch(`${BASE}/me/documents/${item.kind}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(readProblem(data));
      onDone(data as MasterDocument);
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
      setPreview(null);
    } finally {
      setBusy(false);
    }
  }

  const uploaded = Boolean(item.file_id);
  const shown = preview ?? (item.is_private ? null : item.view_url);

  return (
    <div className="rounded-card border border-line bg-page px-4 py-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-[13.5px] font-semibold text-ink">{item.label}</h3>
            {uploaded ? (
              <span className="rounded-[6px] bg-good-soft px-2 py-0.5 text-[11px] font-medium text-good">
                saved
              </span>
            ) : REQUIRED.includes(item.kind) ? (
              <span className="rounded-[6px] bg-sun-soft px-2 py-0.5 text-[11px] font-medium text-sun">
                needed
              </span>
            ) : (
              <span className="rounded-[6px] bg-mute-soft px-2 py-0.5 text-[11px] font-medium text-mute">
                optional
              </span>
            )}
          </div>
          <p className="mt-1 text-[11.5px] leading-relaxed text-ink-faint">{item.guidance}</p>
        </div>

        {shown ? (
          /* eslint-disable-next-line @next/next/no-img-element */
          <img
            src={shown}
            alt={item.label}
            className="h-16 w-16 shrink-0 rounded-[8px] border border-line object-cover"
          />
        ) : null}
      </div>

      <label className="mt-3 flex cursor-pointer items-center justify-center rounded-[9px] border border-dashed border-line-soft bg-shell px-4 py-3 text-[12.5px] font-medium text-ink-soft transition-colors hover:border-accent hover:text-accent">
        {busy ? "Uploading" : uploaded ? "Choose a different picture" : "Choose a picture"}
        <input type="file" accept="image/*" className="hidden" onChange={onPick} disabled={busy} />
      </label>

      {uploaded && item.width_px ? (
        <p className="mt-2 text-[11.5px] text-ink-faint">
          Saved at {item.width_px} by {item.height_px}
          {item.is_private ? ", kept private" : ""}. Sarathi will make every size a form asks for
          from this one.
        </p>
      ) : null}

      {problem ? (
        <p className="mt-2 rounded-[8px] bg-stop-soft px-3 py-2 text-[12px] text-stop">{problem}</p>
      ) : null}
    </div>
  );
}

export function PhotosForm({
  token,
  initial,
}: {
  token: string;
  initial: MasterDocument[];
}) {
  const router = useRouter();
  const [documents, setDocuments] = useState(initial);
  const [problem, setProblem] = useState<string | null>(null);

  const missing = REQUIRED.filter(
    (kind) => !documents.find((item) => item.kind === kind)?.file_id,
  );

  function finish() {
    if (missing.length > 0) {
      const names = documents
        .filter((item) => missing.includes(item.kind))
        .map((item) => item.label.toLowerCase());
      setProblem(`Please add your ${names.join(" and ")} first.`);
      return;
    }
    router.push("/dashboard");
    router.refresh();
  }

  return (
    <AuthShell
      step="Step 4 of 4"
      title="Add your photo and signature"
      hint="Give these once. Sarathi keeps the original and makes every size a form asks for, so you never resize anything again."
    >
      <div className="flex flex-col gap-4">
        {documents.map((item, index) => (
          <Tile
            key={item.kind}
            document={item}
            token={token}
            onDone={(next) =>
              setDocuments((current) =>
                current.map((existing, i) => (i === index ? { ...existing, ...next } : existing)),
              )
            }
          />
        ))}

        <div className="rounded-[9px] border border-line bg-accent-soft px-3.5 py-3">
          <p className="text-[12px] leading-relaxed text-accent">
            Your signature is kept private. Only you can open it, through a link that expires.
            Nobody can reach it by guessing the address.
          </p>
        </div>

        <Problem message={problem} />

        <button type="button" onClick={finish} className={submitClass}>
          Finish and see my exams
        </button>

        <button
          type="button"
          onClick={() => {
            router.push("/dashboard");
            router.refresh();
          }}
          className="text-[12.5px] font-medium text-ink-soft transition-colors hover:text-ink"
        >
          I will add these later
        </button>
      </div>
    </AuthShell>
  );
}
