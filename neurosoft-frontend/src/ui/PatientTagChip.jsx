/* ═══════════════════════════════════════════════════════════════════════
 * PatientTagChip.jsx — Etiqueta atómica QW-6
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";
import { I } from "./primitives.jsx";

export function tagColor(tag, presetColor) {
  if (presetColor) return presetColor;
  let h = 0;
  for (let i = 0; i < (tag || "").length; i++) h = (h * 31 + tag.charCodeAt(i)) >>> 0;
  const palette = ["#0d9488", "#6366f1", "#0891b2", "#7c3aed", "#d97706", "#dc2626"];
  return palette[h % palette.length];
}

export default function PatientTagChip({
  tag,
  color,
  onRemove,
  size = "sm",
  readonly = false,
}) {
  const bg = tagColor(tag, color);
  const pad = size === "md" ? "px-2.5 py-1 text-[10px]" : "px-2 py-0.5 text-[9px]";
  return (
    <span
      className={`inline-flex items-center gap-0.5 font-bold rounded-full text-white ${pad}`}
      style={{ background: bg }}
    >
      {tag}
      {!readonly && onRemove && (
        <button
          type="button"
          onClick={(e) => { e.stopPropagation(); onRemove(tag); }}
          className="ml-0.5 p-0 leading-none opacity-80 hover:opacity-100"
          aria-label={`Quitar etiqueta ${tag}`}
        >
          <I name="close" className="text-[10px]" />
        </button>
      )}
    </span>
  );
}

export function PatientTagList({ tags = [], maxVisible = 3, colorMap = {}, onRemove, readonly }) {
  const visible = tags.slice(0, maxVisible);
  const rest = tags.length - visible.length;
  return (
    <div className="flex flex-wrap gap-1">
      {visible.map((t) => (
        <PatientTagChip
          key={t}
          tag={t}
          color={colorMap[t]}
          onRemove={onRemove}
          readonly={readonly}
        />
      ))}
      {rest > 0 && (
        <span className="text-[9px] font-bold px-2 py-0.5 rounded-full"
          style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
          +{rest}
        </span>
      )}
    </div>
  );
}
