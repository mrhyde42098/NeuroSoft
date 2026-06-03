/* ═══════════════════════════════════════════════════════════════════════
 * IQIndices.jsx — Cálculo de Índices y CI (WISC-IV / WAIS-III)
 * ───────────────────────────────────────────────────────────────────────
 * Implementa el flujo clásico de cálculo de CI compuesto:
 *
 *   PD (puntaje directo)
 *        ↓  (tabla normativa por edad del manual oficial)
 *   PE (puntuación escalar, M=10, SD=3)
 *        ↓  (suma de PE de subtests de cada índice)
 *   Índice compuesto (M=100, SD=15) → ICV, IRP, IMT, IVP
 *        ↓
 *   CIT (Coeficiente Intelectual Total)
 *
 * Debido a que los baremos oficiales (PD→PE por edad) son material
 * con copyright del manual Wechsler, este módulo espera que el clínico
 * ingrese la PE manualmente tras consultar la tabla correspondiente.
 * La conversión PE→Índice usa una aproximación normal estándar
 * (válida como orientación; reemplazable por tabla exacta si el usuario
 * la captura en configuración).
 *
 * Autor: NeuroSoft — 2026
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useMemo, useState } from "react";

/* ─── Composición de índices ────────────────────────────────────────── */
export const INDICES_WISC = {
  ICV: { label: "Comprensión Verbal", subtests: ["NiWiscSem", "NiWiscVoc", "NiWiscCom"] },
  IRP: { label: "Razonamiento Perceptual", subtests: ["NiWiscDC", "NiWiscConD", "NiWiscMat"] },
  IMT: { label: "Memoria de Trabajo", subtests: ["NiWiscRDD", "NiWiscLN"] },
  IVP: { label: "Velocidad de Procesamiento", subtests: ["NiWiscCl", "NiWiscBusSim"] },
};

export const INDICES_WAIS = {
  ICV: { label: "Comprensión Verbal", subtests: ["AdSemWais", "AdWAISV", "AdWAISI"] },
  IRP: { label: "Razonamiento Perceptual", subtests: ["AdWAISCC", "AdMatr", "AdWAISFI"] },
  IMT: { label: "Memoria de Trabajo", subtests: ["AdDDir", "AdWAISA", "AdWAISL"] },
  // §S1.5-fix: WAIS-III IVP son Claves + Búsqueda de Símbolos (no se suman
  // dos pruebas del mismo nombre). El bug histórico "AdBusSim + ViBusSim"
  // era texto suelto; el baremo real es Claves de WAIS-III.
  IVP: { label: "Velocidad de Procesamiento", subtests: ["AdWAISC", "AdBusSim"] },
};

/* ─── Conversión aproximada suma-PE → índice compuesto ──────────────── */
/* PE tiene M=10, SD=3. La suma de n PE independientes tiene
 * M=10n y SD≈3√n. El índice compuesto se escala a M=100, SD=15. */
export function sumPEtoIndex(sumPE, n) {
  if (!n || sumPE === null || sumPE === undefined || Number.isNaN(sumPE)) return null;
  const expectedMean = 10 * n;
  const expectedSD   = 3 * Math.sqrt(n);
  const z = (sumPE - expectedMean) / expectedSD;
  return Math.round(100 + 15 * z);
}

/* ─── Clasificación del compuesto — 6 bandas (S1.5) ────────────────── */
/* DSM-5-TR + práctica clínica estándar 2024:
 *   ≥130  Superior
 *   120-129 Promedio Alto
 *   90-119  Promedio
 *   80-89   Promedio Bajo
 *   70-79   Bajo (DSM-5-TR A: requiere adaptaciones)
 *   <70     Muy Bajo (discapacidad intelectual posible)
 * Para CI 70-79, mostrar nota DSM-5-TR A sobre adaptaciones necesarias.
 */
export function classifyIQ(iq) {
  if (iq === null || iq === undefined) return "—";
  if (iq >= 130) return "Superior";
  if (iq >= 120) return "Promedio Alto";
  if (iq >= 90)  return "Promedio";
  if (iq >= 80)  return "Promedio Bajo";
  if (iq >= 70)  return "Bajo";
  return "Muy Bajo";
}

/* DSM-5-TR Criterio A para Discapacidad Intelectual:
 *   "Funcionamiento intelectual inferior a 70-75"
 * Mostrar nota cuando CI en rango 70-79 (zona gris).
 */
export function dsm5AAdvertencia(iq) {
  if (iq === null || iq === undefined) return null;
  if (iq >= 70 && iq <= 79) {
    return "DSM-5-TR Criterio A: en este rango el clínico debe confirmar " +
           "funcionamiento adaptativo (criterio B) y edad de inicio " +
           "antes de 18 años (criterio C) para considerar DI.";
  }
  if (iq < 70) {
    return "DSM-5-TR Criterio A cumplido (>2 DE bajo la media). " +
           "Evaluar criterio B (funcionamiento adaptativo) y C (inicio <18a).";
  }
  return null;
}

export function classifyColor(iq) {
  if (iq === null || iq === undefined) return "#94A3B8";
  if (iq >= 130) return "#059669";  // Superior
  if (iq >= 120) return "#0D9488";  // Promedio Alto
  if (iq >= 90)  return "#0F766E";  // Promedio
  if (iq >= 80)  return "#F59E0B";  // Promedio Bajo
  if (iq >= 70)  return "#F97316";  // Bajo
  return "#DC2626";                  // Muy Bajo
}

/* ─── Intervalo de confianza 95% (SEM por edad) ──────────────────────── */
/* SEM depende de la edad (Wechsler):
 *   6-7 años: SEM ≈ 6
 *   8-12 años: SEM ≈ 5
 *   13-16 años: SEM ≈ 4
 *   Adulto: SEM ≈ 5
 * Por defecto 5 si no se especifica edad.
 */
export function iqConfidenceInterval(iq, sem = 5) {
  if (iq === null) return [null, null];
  const z = 1.96;
  return [Math.round(iq - z * sem), Math.round(iq + z * sem)];
}

/* SEM por edad para WISC-IV/WAIS-III (Sattler, 2008) */
export function semPorEdad(years) {
  if (years == null) return 5;
  if (years < 8) return 6;
  if (years < 13) return 5;
  if (years < 17) return 4;
  return 5;
}

/* ─── Widget de entrada de PE por subtest ───────────────────────────── */
function PEInput({ value, onChange, label, testId }) {
  return (
    <div className="flex items-center justify-between gap-2 p-2 rounded-lg hover:bg-slate-50">
      <div className="flex-1 min-w-0">
        <p className="text-[11px] text-slate-700 truncate" title={label}>{label}</p>
        <p className="text-[9px] font-mono text-slate-400">{testId}</p>
      </div>
      <input
        type="number" min="1" max="19"
        value={value ?? ""}
        onChange={e => onChange(e.target.value === "" ? null : Number(e.target.value))}
        className="w-14 h-8 text-center text-xs font-bold rounded-lg border border-slate-200 focus:ring-2 focus:ring-teal-500/30"
        placeholder="PE"
      />
    </div>
  );
}

/* ─── Panel principal de índices ────────────────────────────────────── */
export function IQPanel({ protocol = "wisc_iv", subtestLabels = {} }) {
  const INDICES = protocol === "wais_iii" ? INDICES_WAIS : INDICES_WISC;
  const [pe, setPE] = useState({});

  const compute = useMemo(() => {
    const out = {};
    let totalSum = 0, totalCount = 0, usable = true;
    for (const [code, ix] of Object.entries(INDICES)) {
      const values = ix.subtests.map(t => pe[t]).filter(v => v !== null && v !== undefined);
      const sum = values.reduce((a, b) => a + b, 0);
      const n = values.length;
      const complete = n === ix.subtests.length;
      const index = complete ? sumPEtoIndex(sum, n) : null;
      out[code] = { label: ix.label, sum, n, index, complete, subtests: ix.subtests };
      if (complete) { totalSum += sum; totalCount += n; }
      else usable = false;
    }
    out.CIT = usable
      ? {
          label: "CI Total",
          sum: totalSum, n: totalCount,
          index: sumPEtoIndex(totalSum, totalCount),
          complete: true, subtests: [],
        }
      : { label: "CI Total", complete: false, index: null, sum: 0, n: 0, subtests: [] };
    return out;
  }, [pe, INDICES]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm">Cálculo de CI — {protocol === "wais_iii" ? "WAIS-III" : "WISC-IV"}</h3>
        <span className="text-[9px] text-slate-400 italic">
          Ingrese la PE de cada subtest (tomada del manual según edad)
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {Object.entries(INDICES).map(([code, ix]) => (
          <div key={code} className="rounded-xl border border-slate-200 bg-white p-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-[10px] font-mono font-bold text-teal-600">{code}</p>
                <p className="text-[11px] font-semibold text-slate-700">{ix.label}</p>
              </div>
              {compute[code].complete && (
                <div className="text-right">
                  <p className="text-[9px] text-slate-400">Índice</p>
                  <p className="text-xl font-black" style={{ color: classifyColor(compute[code].index) }}>
                    {compute[code].index}
                  </p>
                </div>
              )}
            </div>
            <div className="space-y-0.5">
              {ix.subtests.map(t => (
                <PEInput key={t} testId={t}
                         label={subtestLabels[t] || t}
                         value={pe[t]}
                         onChange={v => setPE(p => ({ ...p, [t]: v }))} />
              ))}
            </div>
            {compute[code].complete && (
              <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-500">
                <span>Suma PE: <b>{compute[code].sum}</b></span>
                <span className="font-semibold" style={{ color: classifyColor(compute[code].index) }}>
                  {classifyIQ(compute[code].index)}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* CI Total */}
      <div className="rounded-2xl p-4 text-white"
           style={{ background: `linear-gradient(135deg, ${classifyColor(compute.CIT.index)}, #0F766E)` }}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest opacity-70">Coeficiente Intelectual Total</p>
            <p className="text-4xl font-black tabular-nums">
              {compute.CIT.index ?? "—"}
            </p>
            <p className="text-xs opacity-90">{classifyIQ(compute.CIT.index)}</p>
            {dsm5AAdvertencia(compute.CIT.index) && (
              <p className="mt-2 text-[10px] italic bg-white/15 rounded px-2 py-1 leading-tight">
                ⚠ {dsm5AAdvertencia(compute.CIT.index)}
              </p>
            )}
          </div>
          <div className="text-right text-[11px] opacity-80">
            {compute.CIT.complete && (
              <>
                <p>Suma total PE: {compute.CIT.sum}</p>
                <p>IC 95%: {iqConfidenceInterval(compute.CIT.index).filter(Boolean).join(" – ") || "—"}</p>
                <p>Basado en {compute.CIT.n} subtests</p>
              </>
            )}
            {!compute.CIT.complete && (
              <p className="italic">Complete todos los subtests de los 4 índices</p>
            )}
          </div>
        </div>
      </div>

      <p className="text-[9px] text-slate-400 italic">
        Nota: la conversión suma-PE → índice usa la aproximación normal estándar
        (M=100, SD=15). Para un valor idéntico al manual, consulte la tabla de
        conversión oficial (WISC-IV Tabla A.3 / WAIS-III Tabla A.6) según edad.
      </p>
    </div>
  );
}

export default IQPanel;
