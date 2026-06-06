/* Acordeón de guía clínica — Materiales / Instrucción / Discontinuación / Calificación / Tips */
import React, { useMemo } from "react";
import { I } from "./primitives.jsx";

const SECTION_KEYS = [
  { key: "materiales", label: "Materiales", icon: "inventory_2" },
  { key: "instruccion", label: "Instrucción", icon: "record_voice_over" },
  { key: "discontinuacion", label: "Discontinuación", icon: "stop_circle" },
  { key: "calificacion", label: "Calificación", icon: "grading" },
  { key: "tips", label: "Tips clínicos", icon: "lightbulb" },
];

function parseSections(text) {
  if (!text || typeof text !== "string") return {};
  const out = {};
  const patterns = [
    [/materiales?:/i, "materiales"],
    [/instrucci[oó]n:/i, "instruccion"],
    [/discontinuaci[oó]n:/i, "discontinuacion"],
    [/calificaci[oó]n:/i, "calificacion"],
    [/tips?\s*cl[ií]nicos?:/i, "tips"],
  ];
  let current = "instruccion";
  const lines = text.split("\n");
  const buf = { materiales: [], instruccion: [], discontinuacion: [], calificacion: [], tips: [] };
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    let matched = false;
    for (const [re, key] of patterns) {
      if (re.test(trimmed)) {
        current = key;
        const rest = trimmed.replace(re, "").trim();
        if (rest) buf[current].push(rest);
        matched = true;
        break;
      }
    }
    if (!matched) buf[current].push(trimmed);
  }
  for (const [k, v] of Object.entries(buf)) {
    if (v.length) out[k] = v.join("\n");
  }
  return out;
}

export default function GuideAccordion({ text, defaultOpen = "instruccion" }) {
  const sections = useMemo(() => parseSections(text), [text]);
  const [open, setOpen] = React.useState(defaultOpen);

  if (!text) return null;

  const available = SECTION_KEYS.filter((s) => sections[s.key]);

  if (!available.length) {
    return (
      <div className="text-sm whitespace-pre-wrap leading-relaxed" style={{ color: "var(--ns-text)" }}>
        {text}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {available.map((s) => (
        <div
          key={s.key}
          className="rounded-lg border overflow-hidden"
          style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-bg)" }}
        >
          <button
            type="button"
            className="w-full flex items-center gap-2 px-3 py-2.5 text-left text-sm font-semibold"
            style={{ color: "var(--ns-text)" }}
            onClick={() => setOpen(open === s.key ? null : s.key)}
            aria-expanded={open === s.key}
          >
            <I name={s.icon} className="text-base opacity-70" />
            {s.label}
            <I name={open === s.key ? "expand_less" : "expand_more"} className="ml-auto text-lg opacity-50" />
          </button>
          {open === s.key && (
            <div
              className="px-3 pb-3 text-sm whitespace-pre-wrap leading-relaxed border-t"
              style={{ color: "var(--ns-muted)", borderColor: "var(--ns-card-b)" }}
            >
              {sections[s.key]}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
