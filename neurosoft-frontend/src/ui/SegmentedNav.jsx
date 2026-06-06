/* Navegador angosto de subtests — abreviaturas + estado por punto */
import React from "react";

const ABBR = {
  NiWiscDC: "DC",
  NiWiscSem: "SEM",
  NiWiscVoc: "VOC",
  NiWiscCom: "COM",
  NiWiscRDD: "RDD",
  NiWiscLN: "LN",
  NiWiscCl: "CL",
  NiWiscAri: "ARI",
  NiWiscBusSim: "BS",
  NiWiscMat: "MAT",
  NiWiscRetDig: "RET",
  NiWiscRetFig: "RF",
  NiWiscCod: "COD",
  NiFCROCop: "FCRO",
  NiFCRORec: "REC",
  AdWAISCC: "DC",
  AdSemWais: "SEM",
  AdWAISC: "COM",
  AdDDir: "RDD",
  AdWAISV: "VOC",
  AdSDWais: "CL",
  AdWAISA: "ARI",
  AdWAISFI: "BS",
  AdMatr: "MAT",
  AdWAISI: "COD",
};

function abbr(testId, nombre) {
  if (ABBR[testId]) return ABBR[testId];
  if (!nombre) return testId?.slice(0, 4) || "?";
  const words = nombre.split(/\s+/);
  if (words.length >= 2) return words.map((w) => w[0]).join("").toUpperCase().slice(0, 5);
  return nombre.slice(0, 4).toUpperCase();
}

export default function SegmentedNav({ items, current, onSelect, getStatus }) {
  return (
    <nav className="flex flex-col gap-1 w-full" aria-label="Navegador de subtests">
      {items.map((it, i) => {
        const active = current === i;
        const status = getStatus?.(it, i) || "empty";
        const dotColor =
          status === "done" ? "#15803D" :
          status === "partial" ? "#B45309" :
          "var(--ns-card-b)";
        return (
          <button
            key={it.test_id || i}
            type="button"
            onClick={() => onSelect(i)}
            title={`${i + 1}. ${it.nombre}${it.dominio ? " · " + it.dominio : ""}`}
            className={`flex items-center gap-2 px-2 py-1.5 rounded-md text-left text-[13px] transition-colors w-full ${
              active ? "font-bold" : "font-medium opacity-90"
            }`}
            style={{
              background: active ? "rgba(13,148,136,0.12)" : "transparent",
              color: active ? "#0D9488" : "var(--ns-text)",
            }}
          >
            <span
              className="w-2.5 h-2.5 rounded-full shrink-0"
              style={{ background: dotColor }}
              aria-hidden
            />
            <span className="font-mono text-[10px] tracking-tight shrink-0 w-9 text-center px-1 py-0.5 rounded"
              style={{ background: active ? "rgba(13,148,136,0.18)" : "var(--ns-subtle)", color: active ? "#0D9488" : "var(--ns-muted)" }}>
              {abbr(it.test_id, it.nombre)}
            </span>
            <span className="flex-1 min-w-0 truncate">{it.nombre}</span>
            {it.es_escala_diferida && (
              <span className="text-[9px] font-bold uppercase shrink-0 px-1 py-0.5 rounded bg-sky-100 text-sky-700">Escala</span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
