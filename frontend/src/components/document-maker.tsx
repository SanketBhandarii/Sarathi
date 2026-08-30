"use client";

import { useState } from "react";

import { PlusIcon } from "@/components/icons";
import { readProblem } from "@/lib/auth";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

export type Kind = "photograph" | "signature" | "thumb_impression";

export interface Spec {
  kind: Kind;
  label: string;
  width_px: number | null;
  height_px: number | null;
  min_kb: number | null;
  max_kb: number | null;
  needed: string;
}

export interface BodyRules {
  source_id: string;
  body: string;
  specs: Spec[];
  warnings: string[];
  checked_against: string;
}

interface Made {
  label: string;
  width_px: number;
  height_px: number;
  size_kb: number;
  padded: boolean;
  matches_spec: boolean;
  needed: string;
  image_base64: string;
}

const WHAT_TO_GIVE: Record<Kind, string> = {
  photograph: "a passport style photo of your face",
  signature: "a picture of your signature on white paper",
  thumb_impression: "a picture of your left thumb impression",
};

const HOW_TO_TAKE: Record<Kind, string> = {
  photograph:
    "Stand against a plain light wall, face the camera, no cap and no dark glasses.",
  signature:
    "Sign on white paper with a black pen, then photograph just the signature. Not in capital letters.",
  thumb_impression:
    "Press your left thumb in black or blue ink on white paper, then photograph just the mark.",
};

function SpecRow({
  spec,
  sourceId,
}: {
  spec: Spec;
  sourceId: string;
}) {
  const [made, setMade] = useState<Made | null>(null);
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [gaveKb, setGaveKb] = useState<number | null>(null);

  async function onPick(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setBusy(true);
    setProblem(null);
    setGaveKb(Math.round(file.size / 1024));

    const form = new FormData();
    form.append("file", file);
    form.append("kind", spec.kind);
    form.append("width_px", String(spec.width_px ?? 0));
    form.append("height_px", String(spec.height_px ?? 0));
    if (spec.min_kb !== null) form.append("min_kb", String(spec.min_kb));
    if (spec.max_kb !== null) form.append("max_kb", String(spec.max_kb));

    try {
      const response = await fetch(`${BASE}/documents/make`, { method: "POST", body: form });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(readProblem(data));
      setMade(data as Made);
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Please try again.");
      setMade(null);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="border-b border-line px-5 py-5 last:border-0">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-[14px] font-semibold text-ink">{spec.label}</h3>
            {made ? (
              <span
                className={`rounded-[6px] px-2 py-0.5 text-[11px] font-medium ${
                  made.matches_spec ? "bg-good-soft text-good" : "bg-stop-soft text-stop"
                }`}
              >
                {made.matches_spec ? "ready" : "does not match"}
              </span>
            ) : null}
          </div>
          <p className="mt-1 text-[12.5px] text-ink-soft">
            Give {WHAT_TO_GIVE[spec.kind]}.
          </p>
          <p className="mt-0.5 text-[11.5px] leading-relaxed text-ink-faint">
            {HOW_TO_TAKE[spec.kind]}
          </p>
          <p className="mt-1.5 text-[11.5px] tabular text-ink-soft">
            {sourceId.toUpperCase()} wants {spec.needed}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {made ? (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={`data:image/jpeg;base64,${made.image_base64}`}
              alt={made.label}
              className="max-h-[92px] rounded-[8px] border border-line bg-shell"
            />
          ) : null}

          <label className="flex cursor-pointer items-center gap-1.5 whitespace-nowrap rounded-[9px] border border-line bg-shell px-3.5 py-2 text-[12.5px] font-medium text-ink transition-colors hover:border-accent hover:text-accent">
            <PlusIcon className="h-[15px] w-[15px]" />
            {busy ? "Making" : made ? "Choose another" : `Choose your ${spec.label.toLowerCase()}`}
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={onPick}
              disabled={busy}
            />
          </label>
        </div>
      </div>

      {made ? (
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <p className="text-[12px] tabular text-ink">
            {gaveKb} KB in, {made.width_px} × {made.height_px} px at {made.size_kb} KB out
          </p>
          <a
            href={`data:image/jpeg;base64,${made.image_base64}`}
            download={`${spec.kind}.jpg`}
            className="rounded-[8px] bg-brand px-3 py-1.5 text-[12px] font-medium text-white transition-opacity hover:opacity-90"
          >
            Save this file
          </a>
          {made.padded ? (
            <span className="text-[11.5px] text-ink-faint">
              Padded to reach the smallest size this form allows.
            </span>
          ) : null}
        </div>
      ) : null}

      {problem ? (
        <p className="mt-3 rounded-[8px] bg-stop-soft px-3 py-2 text-[12px] text-stop">{problem}</p>
      ) : null}
    </div>
  );
}

export function DocumentMaker({ rules }: { rules: BodyRules }) {
  return (
    <div>
      {rules.warnings.length > 0 ? (
        <div className="border-b border-line bg-sun-soft px-5 py-3.5">
          {rules.warnings.map((warning) => (
            <p key={warning} className="text-[12px] leading-relaxed text-sun">
              {warning}
            </p>
          ))}
        </div>
      ) : null}

      {rules.specs.map((spec) => (
        <SpecRow key={spec.kind} spec={spec} sourceId={rules.source_id} />
      ))}
    </div>
  );
}
