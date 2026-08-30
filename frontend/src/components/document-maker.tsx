"use client";

import { useState } from "react";

import type { DocumentSpec, MadeDocument } from "@/lib/types";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function makeOne(file: File, spec: DocumentSpec): Promise<MadeDocument> {
  const form = new FormData();
  form.append("file", file);
  form.append("kind", spec.kind);
  form.append("width_px", String(spec.width_px ?? 0));
  form.append("height_px", String(spec.height_px ?? 0));
  if (spec.min_kb !== null) form.append("min_kb", String(spec.min_kb));
  if (spec.max_kb !== null) form.append("max_kb", String(spec.max_kb));

  const response = await fetch(`${BASE}/documents/make`, { method: "POST", body: form });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: "could not make this file" }));
    throw new Error(detail.detail ?? "could not make this file");
  }
  return (await response.json()) as MadeDocument;
}

export function DocumentMaker({ specs }: { specs: DocumentSpec[] }) {
  const [made, setMade] = useState<MadeDocument[]>([]);
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [sourceSize, setSourceSize] = useState<number | null>(null);

  async function onPick(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setBusy(true);
    setProblem(null);
    setMade([]);
    setSourceSize(file.size);

    try {
      const results: MadeDocument[] = [];
      for (const spec of specs) {
        results.push(await makeOne(file, spec));
      }
      setMade(results);
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="px-4 py-4">
      <label className="flex cursor-pointer flex-col items-center justify-center rounded-card border border-dashed border-line-strong bg-page px-6 py-8 text-center transition-colors hover:border-ink-faint">
        <span className="text-[13px] font-medium text-ink">
          {busy ? "Making your files…" : "Choose a photo from your phone"}
        </span>
        <span className="mt-1 text-[11.5px] text-ink-soft">
          Any size. Sarathi makes every file this form asks for.
        </span>
        <input type="file" accept="image/*" className="hidden" onChange={onPick} disabled={busy} />
      </label>

      {sourceSize !== null ? (
        <p className="mt-3 text-[11.5px] text-ink-soft">
          You gave a file of {Math.round(sourceSize / 1024)} KB.
        </p>
      ) : null}

      {problem ? (
        <p className="mt-3 rounded-[10px] bg-stop-soft px-3 py-2 text-[12px] text-stop">{problem}</p>
      ) : null}

      {made.length > 0 ? (
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          {made.map((item) => (
            <div key={item.kind} className="rounded-card border border-line bg-surface p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-[12.5px] font-medium text-ink">{item.label}</p>
                <span
                  className={`rounded-pill px-2 py-0.5 text-[10.5px] font-medium ${
                    item.matches_spec ? "bg-good-soft text-good" : "bg-stop-soft text-stop"
                  }`}
                >
                  {item.matches_spec ? "matches" : "does not match"}
                </span>
              </div>

              <div className="mt-3 flex items-center justify-center rounded-[10px] bg-page py-3">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`data:image/jpeg;base64,${item.image_base64}`}
                  alt={item.label}
                  className="max-h-[130px] rounded-[6px] border border-line"
                />
              </div>

              <p className="mt-2 text-[11.5px] tabular-nums text-ink">
                {item.width_px} × {item.height_px} px · {item.size_kb} KB
              </p>
              <p className="mt-0.5 text-[11px] text-ink-soft">needs {item.needed}</p>
              {item.padded ? (
                <p className="mt-1 text-[10.5px] text-ink-faint">
                  Padded to reach the smallest size this form allows.
                </p>
              ) : null}

              <a
                href={`data:image/jpeg;base64,${item.image_base64}`}
                download={`${item.kind}.jpg`}
                className="mt-3 block rounded-[10px] bg-brand px-3 py-2 text-center text-[12px] font-medium text-white transition-opacity hover:opacity-90"
              >
                Save this file
              </a>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
