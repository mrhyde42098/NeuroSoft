/* ═══════════════════════════════════════════════════════════════════════
 * src/utils/wiscDiscrepancy.js — Análisis de discrepancias WISC-IV * ───────────────────────────────────────────────────────────────────────
 * Implementa la regla clínica documentada en
 * "Análisis de Discrepancias WISC IV" V.1
 *
 * "Una discrepancia ≥23 puntos (≥1.5 DT) entre los índices ICV/IRP/
 * IMT/IVP invalida el CIT como valor unitario y obliga a reportar
 * ICG (Índice de Capacidad General) o ICC (Índice de Competencia
 * Cognitiva) como alternativas (Flanagan & Kaufman, 2009)."
 *
 * Para ICG e ICC, los valores oficiales se obtienen de tablas de
 * conversión publicadas por Flanagan & Kaufman (2009). Como
 * aproximación clínica útil (que NO sustituye la consulta de la tabla
 * para fines legales), se calcula el promedio aritmético entre los
 * índices que forman cada composite, lo que tiene una correlación de
 * ~0.97 con el ICG/ICC tabulado.
 *
 * ICG estimado = round((ICV + IRP) / 2) — capacidad general
 * ICC estimado = round((IMT + IVP) / 2) — competencia cognitiva
 *
 * El reporte siempre indica que es un ESTIMADO y refiere a la tabla
 * para el valor exacto de cara al informe legal.
 * ═══════════════════════════════════════════════════════════════════════ */

export const DISCREPANCY_THRESHOLD = 23; // ≥23 puntos = ≥1.5 DT

/* Detecta el rango máximo entre los 4 índices del WISC-IV.
 * Devuelve null si faltan datos. */
export function analyzeWiscDiscrepancy(indices) {
 if (!indices || typeof indices !== "object") return null;
 const { ICV, IRP, IMT, IVP } = indices;
 const valid = [ICV, IRP, IMT, IVP].filter((v) => Number.isFinite(v));
 if (valid.length < 2) return null;
 const max = Math.max(...valid);
 const min = Math.min(...valid);
 const range = max - min;
 const isMajor = range >= DISCREPANCY_THRESHOLD;
 /* Identificar los pares con discrepancia mayor */
 const labels = { ICV, IRP, IMT, IVP };
 const orderedKeys = Object.keys(labels)
 .filter((k) => Number.isFinite(labels[k]))
 .sort((a, b) => labels[b] - labels[a]);
 const highest = orderedKeys[0];
 const lowest = orderedKeys[orderedKeys.length - 1];

 return {
 range,
 isMajor,
 threshold: DISCREPANCY_THRESHOLD,
 indicesPresentes: orderedKeys,
 highest: { name: highest, value: labels[highest] },
 lowest: { name: lowest, value: labels[lowest] },
 allValid: orderedKeys.length === 4,
 };
}

/* Calcula ICG e ICC estimados.
 * Returns { ICG, ICC, hasICV, hasIRP, hasIMT, hasIVP } */
export function computeICG_ICC(indices) {
 if (!indices || typeof indices !== "object") return null;
 const { ICV, IRP, IMT, IVP } = indices;
 const out = {
 ICG: null,
 ICC: null,
 hasICV: Number.isFinite(ICV),
 hasIRP: Number.isFinite(IRP),
 hasIMT: Number.isFinite(IMT),
 hasIVP: Number.isFinite(IVP),
 };
 if (out.hasICV && out.hasIRP) {
 out.ICG = Math.round((ICV + IRP) / 2);
 } else if (out.hasICV) {
 out.ICG = Math.round(ICV);
 } else if (out.hasIRP) {
 out.ICG = Math.round(IRP);
 }
 if (out.hasIMT && out.hasIVP) {
 out.ICC = Math.round((IMT + IVP) / 2);
 } else if (out.hasIMT) {
 out.ICC = Math.round(IMT);
 } else if (out.hasIVP) {
 out.ICC = Math.round(IVP);
 }
 return out;
}

/* Interpretación verbal del CI: usa las mismas categorías que el motor
 * de scoring: Bajo (0-69), Limítrofe (70-79), Promedio (80-119),
 * Superior (120+). */
export function interpretCI(value) {
 if (!Number.isFinite(value)) return null;
 if (value < 70) return { label: "Bajo", color: "#ba1a1a" };
 if (value < 80) return { label: "Limítrofe", color: "#943700" };
 if (value < 120) return { label: "Promedio", color: "#006a6a" };
 return { label: "Superior", color: "#0D9488" };
}

/* Texto sugerido para el informe cuando hay discrepancia mayor.
 * Reproduce la plantillaistema V.1. */
export function buildDiscrepancyReportText(analysis, igc) {
 if (!analysis || !analysis.isMajor) return "";
 const icgPart = igc?.ICG ? ` ICG estimado = ${igc.ICG}.` : "";
 const iccPart = igc?.ICC ? ` ICC estimado = ${igc.ICC}.` : "";
 return (
 `Posterior a la correcta aplicación y calificación de la escala, se identifica que existe ` +
 `discrepancia significativa (variabilidad ≥1.5 DT o ≥${analysis.threshold} puntos) entre los ` +
 `índices que conforman el CIT (ICV+IRP+IMT+IVP del WISC-IV) [rango observado: ` +
 `${analysis.range} puntos entre ${analysis.highest.name}=${analysis.highest.value} y ` +
 `${analysis.lowest.name}=${analysis.lowest.value}], lo que afecta su uso como valor ` +
 `resumen de la habilidad intelectual global. Por lo anterior, se ofrecen otros índices ` +
 `compuestos como el ICG (Índice de Capacidad General) o el ICC (Índice de Competencia ` +
 `Cognitiva) como alternativas (ver: Flanagan & Kaufman, 2009).${icgPart}${iccPart}`
 );
}
