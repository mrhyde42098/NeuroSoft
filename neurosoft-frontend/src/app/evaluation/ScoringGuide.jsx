/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/ScoringGuide.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Muestra la guia de puntuacion 0/1/2 del manual WISC-IV/WAIS-III
 * para cada item de pruebas verbales (Semejanzas, Vocabulario, Comprension).
 *
 * Se alimenta del protocolo JSON (wisc_iv_protocolo.json) que contiene
 * las respuestas esperadas extraidas del manual original.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { I } from "../../ui/primitives.jsx";

export default function ScoringGuide({ item, testId }) {
  const [show, setShow] = useState(true);

  const hasScore2 = !!(item.resp_2pt);
  const hasScore1 = !!(item.resp_1pt);
  const hasScore0 = !!(item.resp_0pt);
  const hasSingleAnswer = !!(item.respuesta && !hasScore2 && !hasScore1);
  const hasData = hasScore2 || hasScore1 || hasScore0 || hasSingleAnswer;

  if (!item || !hasData) return null;

  if (!show) {
    return (
      <button
        onClick={() => setShow(true)}
        className="text-[10px] font-bold px-2 py-1 rounded-lg mt-1 hover:opacity-80 transition-all"
        style={{ color: "#7c3aed", background: "rgba(124,58,237,0.08)" }}
        title="Ver guia de puntuacion del manual"
      >
        <I name="menu_book" className="text-xs mr-1" />
        Guia de puntuacion (0-1-2)
      </button>
    );
  }

  return (
    <div className="mt-2 p-2.5 rounded-lg space-y-1.5"
      style={{ background: "rgba(124,58,237,0.04)", border: "1px solid rgba(124,58,237,0.12)" }}>
      <div className="flex items-center gap-1.5 mb-1">
        <I name="menu_book" className="text-xs" style={{ color: "#7c3aed" }} fill />
        <span className="text-[10px] font-extrabold uppercase tracking-wider" style={{ color: "#7c3aed" }}>
          Manual — {hasSingleAnswer ? "respuesta esperada" : "puntuacion"}
        </span>
        {(
          <button onClick={() => setShow(false)} className="ml-auto text-[9px] font-bold px-1.5 py-0.5 rounded hover:bg-purple-100" style={{ color: "#7c3aed" }}>
            Ocultar
          </button>
        )}
      </div>

      {/* Respuesta unica (Figuras Incompletas, Informacion, Aritmetica) */}
      {hasSingleAnswer && (
        <div className="flex items-start gap-2 text-xs">
          <span className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-extrabold text-white"
            style={{ background: "#10b981" }}>✓</span>
          <span className="leading-snug font-semibold" style={{ color: "var(--ns-text)" }}>{item.respuesta}</span>
        </div>
      )}

      {/* Scoring 2-1-0 (Semejanzas, Vocabulario, Comprension) */}
      {hasScore2 && (
        <div className="flex items-start gap-2 text-[11px]">
          <span className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-extrabold text-white"
            style={{ background: "#10b981" }}>2</span>
          <span className="leading-snug" style={{ color: "var(--ns-text)" }}>{item.resp_2pt}</span>
        </div>
      )}

      {hasScore1 && (
        <div className="flex items-start gap-2 text-[11px]">
          <span className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-extrabold text-white"
            style={{ background: "#f59e0b" }}>1</span>
          <span className="leading-snug" style={{ color: "var(--ns-text)" }}>{item.resp_1pt}</span>
        </div>
      )}

      {hasScore0 && (
        <div className="flex items-start gap-2 text-[11px]">
          <span className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-extrabold text-white"
            style={{ background: "#94a3b8" }}>0</span>
          <span className="leading-snug" style={{ color: "var(--ns-muted)" }}>{item.resp_0pt}</span>
        </div>
      )}

      {/* Guia de respuesta (items de ejemplo) */}
      {item.respuesta_guia && (
        <div className="mt-2 pt-2 border-t" style={{ borderColor: "rgba(124,58,237,0.15)" }}>
          <p className="text-[10px] font-bold mb-1" style={{ color: "#7c3aed" }}>Respuesta esperada:</p>
          <p className="text-[11px] leading-snug" style={{ color: "var(--ns-text)" }}>{item.respuesta_guia}</p>
        </div>
      )}
    </div>
  );
}

/* Solo se muestra si es item de 2 puntos (colapsable) o si tiene datos */
export function shouldShowGuide(item) {
  return item && (item.resp_2pt || item.resp_1pt || item.resp_0pt || (item.respuesta && !item.resp_2pt && !item.resp_1pt));
}
