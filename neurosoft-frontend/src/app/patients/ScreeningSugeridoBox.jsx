/* ═══════════════════════════════════════════════════════════════════════
 * src/app/patients/ScreeningSugeridoBox.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-8 — Sugerencias automáticas de escalas según el MC + edad + población.
 *
 * Se embebe en ClinicalHistoryPage debajo del campo MC. Reactivo:
 * al teclear el motivo de consulta, las reglas se evalúan y muestran
 * sugerencias clínicas relevantes con botón "Aplicar ahora" que lleva
 * al ScreeningPage con esa escala precargada.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useMemo } from "react";
import { I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { SCREENING_FORMS } from "../../data/screening.js";
import { sugerirScreenings } from "../../data/screeningSugerencias.js";

export default function ScreeningSugeridoBox({ motivoConsulta, edad, poblacion, onAplicar }) {
  const { reglas, screeningIds } = useMemo(
    () => sugerirScreenings({ motivoConsulta, edad, poblacion }),
    [motivoConsulta, edad, poblacion]
  );

  if (!reglas.length) return null;

  return (
    <div className="rounded-lg p-3"
      style={{
        background: "linear-gradient(135deg, rgba(13,148,136,0.06), rgba(13,148,136,0.02))",
        border: "1px solid rgba(13,148,136,0.18)",
      }}>
      <div className="flex items-start gap-2 mb-2">
        <I name="auto_awesome" fill style={{ color: TEAL, fontSize: 18 }} />
        <div className="flex-1">
          <p className="text-xs font-bold uppercase tracking-wider" style={{ color: TEAL }}>
            Escalas sugeridas según el motivo de consulta
          </p>
          <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
            Reglas: {reglas.map(r => r.titulo).join(" · ")}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {screeningIds.map(id => {
          const form = SCREENING_FORMS[id];
          if (!form) return null;
          return (
            <button
              key={id}
              onClick={() => onAplicar?.(id)}
              title={`${form.name} — ${form.ageRange || ""}\n${form.notes || ""}`}
              className="text-xs font-bold px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all"
              style={{
                background: "white",
                border: `1px solid ${TEAL}40`,
                color: "var(--ns-text)",
              }}>
              <span className="ns-mono font-extrabold" style={{ color: TEAL }}>
                {form.abbr || id}
              </span>
              <span style={{ color: "var(--ns-muted)" }}>{form.name?.slice(0, 30)}</span>
              <I name="arrow_forward" className="text-sm" style={{ color: TEAL }} />
            </button>
          );
        })}
      </div>
    </div>
  );
}
