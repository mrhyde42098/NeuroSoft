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
            title={it.nombre}
            className={`flex items-center gap-2 px-2 py-1.5 rounded-md text-left text-xs transition-colors w-full ${
              active ? "font-bold" : "font-medium opacity-80"
            }`}
            style={{
              background: active ? "rgba(13,148,136,0.12)" : "transparent",
              color: active ? "#0D9488" : "var(--ns-text)",
            }}
          >
            <span
              className="w-2 h-2 rounded-full shrink-0"
              style={{ background: dotColor }}
              aria-hidden
            />
            <span className="font-mono text-[11px] tracking-tight shrink-0 w-10">
              {abbr(it.test_id, it.nombre)}
            </span>
            <span className="truncate opacity-70 hidden xl:inline">
              {it.dominio || ""}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
