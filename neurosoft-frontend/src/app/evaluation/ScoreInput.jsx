/* src/app/evaluation/ScoreInput.jsx — Input de puntaje con validación visual y feedback */
import React, { useMemo } from "react";
import { I } from "../../ui/primitives.jsx";

/* Rangos aproximados de PD para pruebas comunes (solo para validación visual de sanity check).
 * Estos no reemplazan el baremo, solo previenen errores de tipeo obvios. */
const SANITY_RANGES = {
  // WISC-IV
  NiWiscDC: [0, 70], NiWiscSem: [0, 44], NiWiscVoc: [0, 68],
  NiWiscLN: [0, 30], NiWiscCl: [0, 120], NiWiscMat: [0, 35],
  NiWiscCom: [0, 42], NiWiscAri: [0, 30], NiWiscBusSim: [0, 120],
  NiWiscRDD: [0, 30], NiWiscConD: [0, 35],
  // WAIS-III
  AdWAISV: [0, 70], AdSemWais: [0, 40], AdWAISC: [0, 35],
  AdWAISI: [0, 33], AdWAISA: [0, 25], AdWAISL: [0, 21],
  AdSDWais: [0, 133], AdMatr: [0, 26], AdWAISFI: [0, 25],
  AdWAISCC: [0, 90], AdDDir: [0, 20],
  // AM
  ViTMTA: [0, 300], ViTMTB: [0, 500], ViRDD: [0, 12],
  ViRDInv: [0, 12], ViStP: [0, 120], ViStC: [0, 100],
  ViAni: [0, 40], ViSem: [0, 30], ViYesavage: [0, 15],
  EscYesavage: [0, 15],
};

const SENTINEL_NA = 9999;

export default function ScoreInput({ testId, value, onChange, className = "", size = "md" }) {
  const range = SANITY_RANGES[testId];
  const num = value === "" || value === null || value === undefined ? null : Number(value);
  const isXl = size === "xl";

  const status = useMemo(() => {
    if (num === null || isNaN(num)) return { type: "empty", icon: null, color: "", msg: "" };
    if (num === SENTINEL_NA || num >= 9999) return { type: "invalid", icon: "error", color: "#DC2626", msg: "Use vacío si no aplicó la prueba" };
    if (num < 0) return { type: "invalid", icon: "error", color: "#DC2626", msg: "No puede ser negativo" };
    if (range) {
      if (num > range[1] * 1.5) return { type: "warn", icon: "warning", color: "#D97706", msg: `Muy alto (máx baremo ~${range[1]})` };
      if (num > range[1]) return { type: "high", icon: "warning", color: "#D97706", msg: `Excede máx ~${range[1]} — verifique` };
    }
    return { type: "ok", icon: "check_circle", color: "#0D9488", msg: "" };
  }, [num, range]);

  const ringColor = status.type === "invalid" ? "#DC2626" : status.type === "warn" || status.type === "high" ? "#D97706" : "";

  return (
    <div className={`relative ${className}`}>
      {isXl && (
        <span className="block text-[10px] font-bold uppercase tracking-widest mb-1" style={{ color: "var(--ns-muted)" }}>
          Puntaje directo (PD)
        </span>
      )}
      <input
        data-testid="current-score-input"
        type="number"
        min={0}
        max={range ? range[1] * 2 : 500}
        value={value || ""}
        onChange={onChange}
        className={`${isXl ? "w-28 h-16 text-3xl" : "w-20 h-12 text-2xl"} font-extrabold text-center rounded-2xl border-none ring-2 transition-all duration-200 outline-none`}
        style={{
          background: "var(--ns-input)",
          color: status.type === "invalid" ? "#DC2626" : status.type === "warn" || status.type === "high" ? "#D97706" : "#0D9488",
          boxShadow: ringColor ? `0 0 0 3px ${ringColor}30` : "none",
        }}
        placeholder="—"
      />
      {/* Status indicator */}
      {status.icon && (
        <div className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-white shadow-sm flex items-center justify-center">
          <I name={status.icon} className="text-[12px]" style={{ color: status.color }} />
        </div>
      )}
      {/* Tooltip message */}
      {status.msg && (
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-[9px] font-bold px-2 py-0.5 rounded-full"
             style={{ background: `${status.color}15`, color: status.color }}>
          {status.msg}
        </div>
      )}
    </div>
  );
}
