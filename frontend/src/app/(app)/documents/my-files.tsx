"use client";

import { useState } from "react";

import { PlusIcon } from "@/components/icons";
import { readProblem } from "@/lib/auth";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

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
}

export interface SizedFile {
  source_id: string;
  body: string;
  needed: string;
  width_px: number;
  height_px: number;
  size_kb: number;
  matches: boolean;
  padded: boolean;
  image_base64: string;
}

const WHAT_TO_GIVE: Record<Kind, string> = {
  photograph: "a passport style photo of your face",
  signature: "a picture of your signature on white paper",
  thumb_impression: "a picture of your left thumb impression",
};

function saveToDisk(base64: string, filename: string): void {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);

  const url = URL.createObjectURL(new Blob([bytes], { type: "image/jpeg" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function Slot({
  document: item,
  made,
  token,
  onSaved,
}: {
  document: MasterDocument;
  made: SizedFile[];
  token: string;
  onSaved: (kind: Kind) => void;
}) {
  const [saved, setSaved] = useState(Boolean(item.file_id));
  const [preview, setPreview] = useState<string | null>(item.view_url);
  const [sizes, setSizes] = useState<SizedFile[]>(made);
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);

  async function loadSizes() {
    setBusy(true);
    setProblem(null);
    try {
      const response = await fetch(`${BASE}/me/documents/${item.kind}/sizes`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(readProblem(data));

      const made = data as SizedFile[];
      if (made.length === 0) {
        throw new Error(`No commission asks for a ${item.label.toLowerCase()}.`);
      }
      setSizes(made);
    } catch (error) {
      setProblem(
        error instanceof Error ? error.message : "Sarathi could not make the sizes just now.",
      );
    } finally {
      setBusy(false);
    }
  }

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
      setSaved(true);
      onSaved(item.kind);
      await loadSizes();
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
      setPreview(null);
      setSaved(false);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="border-b border-line px-5 py-5 last:border-0">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-[14px] font-semibold text-ink">{item.label}</h3>
            {saved ? (
              <span className="rounded-[6px] bg-good-soft px-2 py-0.5 text-[11px] font-medium text-good">
                saved
              </span>
            ) : (
              <span className="rounded-[6px] bg-sun-soft px-2 py-0.5 text-[11px] font-medium text-sun">
                not added yet
              </span>
            )}
          </div>
          <p className="mt-1 text-[12.5px] text-ink-soft">Give {WHAT_TO_GIVE[item.kind]}.</p>
          <p className="mt-0.5 text-[11.5px] leading-relaxed text-ink-faint">{item.guidance}</p>
          {item.is_private ? (
            <p className="mt-1 text-[11px] text-ink-faint">
              Kept private. Only you can open it, using a link that expires.
            </p>
          ) : null}
        </div>

        <div className="flex items-center gap-3">
          {preview ? (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={preview}
              alt={item.label}
              className="h-[72px] w-[72px] rounded-[8px] border border-line object-cover"
            />
          ) : null}

          <div className="flex flex-col gap-2">
            <label className="flex cursor-pointer items-center gap-1.5 whitespace-nowrap rounded-[9px] border border-line bg-shell px-3.5 py-2 text-[12.5px] font-medium text-ink transition-colors hover:border-accent hover:text-accent">
              <PlusIcon className="h-[15px] w-[15px]" />
              {busy ? "Saving" : saved ? "Replace" : `Add your ${item.label.toLowerCase()}`}
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={onPick}
                disabled={busy}
              />
            </label>

            {saved ? (
              <button
                type="button"
                onClick={loadSizes}
                disabled={busy}
                className="cursor-pointer rounded-[9px] border border-line bg-page px-3.5 py-2 text-[12.5px] font-medium text-ink transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-60"
              >
                {busy ? "Working" : "Make the sizes again"}
              </button>
            ) : null}
          </div>
        </div>
      </div>

      {problem ? (
        <p className="mt-3 rounded-[8px] bg-stop-soft px-3 py-2 text-[12px] text-stop">{problem}</p>
      ) : null}

      {saved && sizes.length === 0 && !problem ? (
        <p className="mt-3 rounded-[8px] bg-sun-soft px-3 py-2 text-[12px] text-sun">
          Sarathi could not make the sizes for this picture. Press &quot;Make the sizes again&quot;.
        </p>
      ) : null}

      {sizes.length > 0 ? (
        <div className="mt-4">
          <p className="text-[12px] font-medium text-ink">
            Made from your picture, in the size each commission asks for
          </p>
          <div className="mt-2.5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {sizes.map((size) => (
              <div key={size.source_id} className="rounded-card border border-line bg-page p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[12.5px] font-semibold text-ink">
                    {size.source_id.toUpperCase()}
                  </span>
                  <span
                    className={`rounded-[6px] px-2 py-0.5 text-[10.5px] font-medium ${
                      size.matches ? "bg-good-soft text-good" : "bg-stop-soft text-stop"
                    }`}
                  >
                    {size.matches ? "ready" : "no fit"}
                  </span>
                </div>

                <div className="mt-2.5 flex items-center justify-center rounded-[8px] bg-shell py-2.5">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={`data:image/jpeg;base64,${size.image_base64}`}
                    alt={`${item.label} for ${size.source_id}`}
                    className="max-h-[86px] rounded-[5px] border border-line"
                  />
                </div>

                <p className="mt-2 text-[11.5px] tabular text-ink">
                  {size.width_px} × {size.height_px} px · {size.size_kb} KB
                </p>
                <p className="mt-0.5 text-[11px] leading-relaxed text-ink-faint">
                  needs {size.needed}
                </p>

                <button
                  type="button"
                  onClick={() => saveToDisk(size.image_base64, `${item.kind}_${size.source_id}.jpg`)}
                  className="mt-2.5 block w-full cursor-pointer rounded-[8px] bg-brand px-3 py-1.5 text-center text-[11.5px] font-medium text-white transition-opacity hover:opacity-90"
                >
                  Save
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function SheetButton({ token }: { token: string }) {
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);

  async function onClick() {
    setBusy(true);
    setProblem(null);
    try {
      const response = await fetch(`${BASE}/me/documents/sheet`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      if (!response.ok) throw new Error("Sarathi could not make your sheet just now.");

      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "sarathi_documents.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-1.5">
      <button
        type="button"
        onClick={onClick}
        disabled={busy}
        className="cursor-pointer whitespace-nowrap rounded-[9px] bg-ink px-4 py-2.5 text-[12.5px] font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {busy ? "Making your sheet" : "Download my sheet as PDF"}
      </button>
      {problem ? <p className="text-[11.5px] text-stop">{problem}</p> : null}
    </div>
  );
}

export function MyFiles({
  documents,
  sizes,
  token,
}: {
  documents: MasterDocument[];
  sizes: Record<string, SizedFile[]>;
  token: string;
}) {
  const [added, setAdded] = useState<Set<Kind>>(
    new Set(documents.filter((item) => item.file_id).map((item) => item.kind)),
  );

  return (
    <div>
      <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-3">
        <p className="text-[12.5px] text-ink-soft">
          {added.size} of {documents.length} added
        </p>
        {added.size === documents.length ? (
          <span className="rounded-pill bg-good-soft px-2.5 py-1 text-[11.5px] font-medium text-good">
            all set
          </span>
        ) : null}
      </div>
      <div className="border-y border-line bg-accent-soft px-5 py-3.5">
        <p className="text-[12px] leading-relaxed text-accent">
          Upload each picture once. Sarathi stores the original and makes every size a commission
          asks for, so you do not have to resize anything. Your signature and thumb impression are
          kept private.
        </p>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-5 py-4">
        <div>
          <p className="text-[12.5px] font-medium text-ink">One sheet with everything on it</p>
          <p className="mt-0.5 text-[11.5px] leading-relaxed text-ink-soft">
            Your details, pictures and marks on one page you can keep or print. It has a Sarathi
            watermark, so keep it for your own use. Do not upload it to a form.
          </p>
        </div>
        <SheetButton token={token} />
      </div>
      {documents.map((item) => (
        <Slot
          key={item.kind}
          document={item}
          made={sizes[item.kind] ?? []}
          token={token}
          onSaved={(kind) => setAdded((current) => new Set(current).add(kind))}
        />
      ))}
    </div>
  );
}
