/* ═══════════════════════════════════════════════════════════════════════
 * GlossaryLegend.jsx — Barra compacta de términos con tooltips (§N2)
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";
import { I } from "./primitives.jsx";
import GlossaryTerm from "./GlossaryTerm.jsx";
import { TEAL } from "./tokens.js";

const TERMS_BY_POBLACION = {
  infantil: ["ICV", "IRP", "IMT", "IVP", "CIT", "ICG", "ICC"],
  adulto_joven: ["ICV", "IRP", "IMT", "IVP", "CIT", "ICG", "ICC", "POI", "PSI"],
  adulto_mayor: ["ICV", "IRP", "IMT", "IVP", "CIT", "ICG", "ICC", "POI", "PSI"],
};

const TERMS_TRANSVERSAL = ["RIPS", "CIE-11", "ENI-2", "SVT", "TOMM"];

export default function GlossaryLegend({
  poblacion = "infantil",
  extraTerms = [],
  title = "Índices y términos clave",
  className = "",
}) {
  const pop = (poblacion || "infantil").toLowerCase();
  const base = TERMS_BY_POBLACION[pop] || TERMS_BY_POBLACION.infantil;
  const terms = [...new Set([...base, ...TERMS_TRANSVERSAL, ...extraTerms])];

  return (
    <div
      className={`rounded-xl p-3 mb-6 text-xs flex items-center gap-1 flex-wrap glossary-legend ${className}`}
      style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}
    >
      <I name="info" className="text-base shrink-0" style={{ color: TEAL }} />
      <span className="font-bold mr-2">{title}:</span>
      {terms.map((t, i) => (
        <React.Fragment key={t}>
          {i > 0 && <span>·</span>}
          <GlossaryTerm term={t}>{t}</GlossaryTerm>
        </React.Fragment>
      ))}
      <span className="ml-2 opacity-70 glossary-legend-hint">(click para definición)</span>
    </div>
  );
}
