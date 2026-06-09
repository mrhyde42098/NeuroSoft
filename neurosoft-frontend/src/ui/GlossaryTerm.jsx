/* ═══════════════════════════════════════════════════════════════════════
 * src/ui/GlossaryTerm.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §P4 — Componente reutilizable para envolver términos técnicos con
 * tooltip de definición al hover/click.
 *
 * Uso:
 *   <GlossaryTerm term="ICV">ICV</GlossaryTerm>
 *   <GlossaryTerm term="MMSE">Mini-Mental</GlossaryTerm>
 *
 * Si el término existe en GLOSARIO (data/aprenderContent.js), muestra
 * tooltip con definición + ejemplo + botón "Ver más" que abre la página
 * de glosario completa. Si no existe, renderiza el texto sin envolver.
 *
 * Accesible: roles ARIA, manejo de teclado (Esc cierra).
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState, useRef, useEffect } from "react";
import { GLOSARIO } from "../data/aprenderContent.js";
import { I } from "./primitives.jsx";
import { TEAL } from "./tokens.js";

/* Index por término (case-sensitive — los términos son siglas) */
const GLOSARIO_INDEX = Object.fromEntries(GLOSARIO.map(g => [g.termino, g]));

export default function GlossaryTerm({ term, children, color = TEAL, underline = true, printSafe = true }) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef(null);
  const def = GLOSARIO_INDEX[term];

  /* Cerrar al click fuera + Esc */
  useEffect(() => {
    if (!open) return;
    const onDoc = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    };
    const onKey = (e) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // Si el término no está en el glosario, renderizar texto plano sin envolver
  if (!def) return <span>{children || term}</span>;

  if (printSafe && typeof window !== "undefined" && window.matchMedia?.("(print)")?.matches) {
    return <span className="glossary-term-trigger">{children || term}</span>;
  }

  return (
    <span ref={wrapRef} className="relative inline-block glossary-term-wrap">
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); setOpen(o => !o); }}
        title={def.nombre_completo || def.termino}
        className="cursor-help font-medium glossary-term-trigger"
        style={{
          color: open ? color : "inherit",
          borderBottom: underline ? `1px dotted ${color}` : "none",
          background: "transparent",
          padding: 0, border: "none",
        }}
        aria-expanded={open}
        aria-haspopup="dialog">
        {children || term}
      </button>

      {open && (
        <div
          role="dialog"
          aria-label={`Definición de ${def.termino}`}
          className="glossary-term-popover"
          style={{
            position: "absolute",
            zIndex: 100,
            top: "100%", left: 0,
            marginTop: 6,
            width: 320,
            background: "var(--ns-card)",
            border: `1px solid var(--ns-card-b)`,
            borderLeft: `3px solid ${color}`,
            borderRadius: 8,
            boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
            padding: 14,
            fontWeight: "normal",
            fontSize: 12,
            lineHeight: 1.5,
            textAlign: "left",
          }}>
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="font-bold ns-mono text-xs" style={{ color }}>{def.termino}</p>
              {def.nombre_completo && (
                <p className="text-xs" style={{ color: "var(--ns-muted)" }}>{def.nombre_completo}</p>
              )}
            </div>
            <button onClick={() => setOpen(false)} aria-label="Cerrar"
              className="p-0.5 hover:bg-gray-100 rounded" style={{ color: "var(--ns-muted)" }}>
              <I name="close" className="text-xs" />
            </button>
          </div>

          <p style={{ color: "var(--ns-text)", marginBottom: 8 }}>{def.definicion}</p>

          {def.ejemplo && (
            <div style={{ background: "var(--ns-subtle)", padding: 8, borderRadius: 4, marginBottom: 8 }}>
              <p className="text-[10px] font-bold uppercase tracking-wider mb-1"
                style={{ color: "var(--ns-muted)" }}>Ejemplo</p>
              <p className="ns-serif-italic text-xs">{def.ejemplo}</p>
            </div>
          )}

          {def.ver_tambien?.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              <span className="text-[10px]" style={{ color: "var(--ns-muted)" }}>Ver:</span>
              {def.ver_tambien.slice(0, 5).map(rel => (
                <span key={rel} className="text-[10px] ns-mono px-1 rounded"
                  style={{ background: `${color}15`, color }}>{rel}</span>
              ))}
            </div>
          )}

          {def.fuente && (
            <p className="text-[10px] ns-serif-italic pt-2 border-t"
              style={{ color: "var(--ns-muted)", borderColor: "var(--ns-card-b)" }}>
              {def.fuente}
            </p>
          )}

          <a
            href="#/aprender/glosario"
            className="text-[10px] font-bold mt-2 inline-block glossary-term-no-print"
            style={{ color }}
            onClick={() => setOpen(false)}
          >
            Ver en Centro Aprender →
          </a>
        </div>
      )}
    </span>
  );
}
