"use client";

import { useState } from "react";

import { DocumentMaker, type BodyRules } from "@/components/document-maker";

export function BodyPicker({ rules }: { rules: BodyRules[] }) {
  const [chosen, setChosen] = useState(rules[0].source_id);
  const current = rules.find((item) => item.source_id === chosen) ?? rules[0];

  return (
    <div>
      <div className="flex flex-wrap gap-2 border-y border-line bg-page/40 px-5 py-3">
        {rules.map((item) => {
          const active = item.source_id === chosen;
          return (
            <button
              key={item.source_id}
              type="button"
              onClick={() => setChosen(item.source_id)}
              className={[
                "rounded-pill px-3.5 py-1.5 text-[12.5px] font-medium transition-colors",
                active
                  ? "bg-accent text-white"
                  : "border border-line bg-shell text-ink-soft hover:border-accent hover:text-accent",
              ].join(" ")}
            >
              {item.source_id.toUpperCase()}
            </button>
          );
        })}
      </div>

      <p className="px-5 pt-3.5 text-[12.5px] text-ink-soft">
        {current.body} asks for {current.specs.length}{" "}
        {current.specs.length === 1 ? "file" : "files"}.
      </p>

      <DocumentMaker rules={current} />
    </div>
  );
}
