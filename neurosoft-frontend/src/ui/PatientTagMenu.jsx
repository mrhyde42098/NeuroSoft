/* Popover para añadir etiquetas QW-6 */
import React, { useEffect, useRef, useState } from "react";
import { I } from "./primitives.jsx";
import { TEAL } from "./tokens.js";

export const TAG_PRESETS = [
  { label: "Evaluación Completa", color: "#0d9488" },
  { label: "Control Mensual", color: "#6366f1" },
  { label: "RIPS Generado", color: "#0891b2" },
  { label: "Particular", color: "#7c3aed" },
  { label: "EPS", color: "#d97706" },
  { label: "Prioritario", color: "#dc2626" },
];

export default function PatientTagMenu({ onSelect, existing = [] }) {
  const [open, setOpen] = useState(false);
  const [custom, setCustom] = useState("");
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return;
    const close = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [open]);

  const pick = (label) => {
    if (!label || existing.includes(label)) return;
    onSelect(label);
    setOpen(false);
    setCustom("");
  };

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-amber-500 hover:text-white text-gray-400 transition-all"
        onClick={(e) => { e.stopPropagation(); setOpen((o) => !o); }}
        title="Etiqueta"
        aria-expanded={open}
      >
        <I name="label" className="text-lg" />
      </button>
      {open && (
        <div
          className="absolute right-0 top-full mt-1 z-50 w-52 rounded-xl border shadow-lg p-2 text-xs"
          style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}
          role="menu"
        >
          <p className="text-[10px] font-bold uppercase tracking-wider px-2 py-1" style={{ color: "var(--ns-muted)" }}>
            Añadir etiqueta
          </p>
          {TAG_PRESETS.filter((p) => !existing.includes(p.label)).map((p) => (
            <button
              key={p.label}
              type="button"
              className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-teal-50 flex items-center gap-2"
              onClick={() => pick(p.label)}
            >
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: p.color }} />
              {p.label}
            </button>
          ))}
          <div className="flex gap-1 mt-2 px-1">
            <input
              value={custom}
              onChange={(e) => setCustom(e.target.value)}
              placeholder="Personalizada…"
              className="flex-1 px-2 py-1 rounded-lg text-xs border"
              style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-input)" }}
              onKeyDown={(e) => { if (e.key === "Enter") pick(custom.trim()); }}
            />
            <button
              type="button"
              className="px-2 py-1 rounded-lg text-white font-bold"
              style={{ background: TEAL }}
              onClick={() => pick(custom.trim())}
            >
              +
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
