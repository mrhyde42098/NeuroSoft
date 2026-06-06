/* Panel de validez de síntomas — criterios Slick + referencia TOMM/Rey */

import React, { useState } from "react";
import { Label } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import SectionCard from "../../ui/SectionCard.jsx";
import { SLICK_CRITERIA, evaluarValidezSlick, VALIDEZ_TESTS } from "../../data/validezClinica.js";

export default function ValidezPanel({ onInsertObs }) {
  const [incentivo, setIncentivo] = useState(false);
  const [tommT2, setTommT2] = useState("");
  const [rey, setRey] = useState("");
  const evalRes = evaluarValidezSlick({
    incentivoExterno: incentivo,
    tommTrial2: tommT2 === "" ? null : Number(tommT2),
    rey15: rey === "" ? null : Number(rey),
  });

  return (
    <SectionCard
      title="Validez de síntomas (peritaje / Slick 1999)"
      icon="gavel"
      eyebrow="Peritaje"
      subtitle='Complementa la batería con REY15 y TOMM desde Evaluación → protocolo "Validez de síntomas".'
    >
      <label className="flex items-center gap-2 text-xs">
        <input type="checkbox" checked={incentivo} onChange={(e) => setIncentivo(e.target.checked)} />
        Incentivo externo significativo (laboral, forense, pensión)
      </label>
      <div className="grid grid-cols-2 gap-3 mt-4">
        <div>
          <Label className="text-xs">TOMM Trial 2 (0-50)</Label>
          <input
            type="number"
            min={0}
            max={50}
            value={tommT2}
            onChange={(e) => setTommT2(e.target.value)}
            className="w-full text-xs rounded-lg px-2 py-1.5"
            style={{ background: "var(--ns-input)" }}
            placeholder="corte &lt;45"
          />
        </div>
        <div>
          <Label className="text-xs">Rey 15-Item (ítems recordados)</Label>
          <input
            type="number"
            min={0}
            max={15}
            value={rey}
            onChange={(e) => setRey(e.target.value)}
            className="w-full text-xs rounded-lg px-2 py-1.5"
            style={{ background: "var(--ns-input)" }}
            placeholder="corte ≤9"
          />
        </div>
      </div>
      {evalRes.alerta && (
        <p className="text-xs font-bold p-3 rounded-lg mt-4" style={{ background: "#fef3c7", color: "#92400e" }}>
          {evalRes.alerta}
        </p>
      )}
      <ul className="text-[11px] space-y-1 mt-4">
        {SLICK_CRITERIA.map((c) => (
          <li key={c.id} className={evalRes.criterios.includes(c.id) ? "font-bold" : ""} style={{ color: evalRes.criterios.includes(c.id) ? TEAL : "var(--ns-muted)" }}>
            {c.id}) {c.label} — {c.desc}
          </li>
        ))}
      </ul>
      {onInsertObs && (
        <button
          type="button"
          onClick={() => {
            const txt = [
              "Validez de síntomas (Slick et al. 1999):",
              evalRes.alerta || "Sin alerta automática por SVT.",
              `Criterios marcados: ${evalRes.criterios.join(", ") || "ninguno"}.`,
            ].join("\n");
            onInsertObs(txt);
          }}
          className="mt-4 text-xs font-bold px-4 py-2 rounded-full text-white"
          style={{ background: TEAL }}
        >
          Insertar en observaciones
        </button>
      )}
      <p className="text-[10px] mt-3" style={{ color: "var(--ns-muted)" }}>
        Pruebas SVT en catálogo: {VALIDEZ_TESTS.map((t) => t.nombre).join(", ")}.
      </p>
    </SectionCard>
  );
}
