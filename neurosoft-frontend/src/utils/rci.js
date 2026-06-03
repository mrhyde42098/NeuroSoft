/* ═══════════════════════════════════════════════════════════════════════
 * src/utils/rci.js — Reliable Change Index (Jacobson & Truax 1991)
 * ───────────────────────────────────────────────────────────────────────
 * El RCI (Índice de Cambio Confiable) determina si la diferencia entre
 * una evaluación PRE y otra POST es **clínicamente significativa** o si
 * podría explicarse por el error de medición del test.
 *
 *   RCI = (X2 - X1) / S_diff
 *
 * Donde:
 *   X1, X2   = puntajes pre/post (escala estandarizada: Z, T, PE, CI…)
 *   S_diff   = SD_diff = SE_diff = sqrt(2) * SEM
 *   SEM      = SD_norm * sqrt(1 - r_xx)
 *   r_xx     = confiabilidad test-retest de la prueba
 *
 * Interpretación:
 *   |RCI| ≥ 1.96  → cambio significativo p<.05 (improbable por azar)
 *   |RCI| ≥ 1.64  → cambio sugestivo p<.10
 *   |RCI| <  1.64 → variación dentro del error de medición
 *
 * Signo:
 *   RCI > 0 → mejora (en pruebas donde mayor = mejor)
 *   RCI < 0 → deterioro
 *
 * Referencia clave:
 *   Jacobson NS, Truax P. *Clinical significance: a statistical approach
 *   to defining meaningful change in psychotherapy research.* J Consult
 *   Clin Psychol. 1991;59(1):12-19. doi:10.1037/0022-006x.59.1.12
 *
 * Configuraciones por defecto:
 *   • Pruebas con M=100, SD=15 (índices Wechsler) → SEM≈4.5 (r=0.90)
 *   • Pruebas con M=50, SD=10 (puntajes T) → SEM≈3.16 (r=0.90)
 *   • Pruebas con M=10, SD=3 (puntuaciones escalares) → SEM≈0.95 (r=0.90)
 *   • Z-score (M=0, SD=1) → SEM≈0.32 (r=0.90)
 * ═══════════════════════════════════════════════════════════════════════ */

/* Tabla de SEM por tipo de métrica + confiabilidad típica.
 * Los valores cubren los formatos más usados en NeuroSoft. */
export const SEM_DEFAULTS = {
  ci:      { mean: 100, sd: 15,  reliability: 0.95, semDefault: 3.35 },  // sqrt(225 * 0.05) ≈ 3.35
  indice:  { mean: 100, sd: 15,  reliability: 0.93, semDefault: 3.97 },
  t:       { mean: 50,  sd: 10,  reliability: 0.90, semDefault: 3.16 },
  pe:      { mean: 10,  sd: 3,   reliability: 0.85, semDefault: 1.16 },
  z:       { mean: 0,   sd: 1,   reliability: 0.85, semDefault: 0.39 },
  pd:      { mean: null, sd: null, reliability: 0.85, semDefault: null },
};

/* Calcula el SEM (Standard Error of Measurement). */
export function computeSEM(sd, reliability) {
  if (!Number.isFinite(sd) || !Number.isFinite(reliability) || reliability < 0 || reliability >= 1) {
    return null;
  }
  return sd * Math.sqrt(1 - reliability);
}

/* Calcula el SE_diff (= sqrt(2) * SEM) usado en el denominador del RCI. */
export function computeSEdiff(sem) {
  if (!Number.isFinite(sem) || sem <= 0) return null;
  return Math.sqrt(2) * sem;
}

/* Calcula el RCI dadas las dos puntuaciones y el SE_diff. */
export function computeRCI(pre, post, seDiff) {
  if (!Number.isFinite(pre) || !Number.isFinite(post) || !Number.isFinite(seDiff) || seDiff <= 0) {
    return null;
  }
  return (post - pre) / seDiff;
}

/* Interpretación clínica del RCI.
 * higherIsBetter: en pruebas de tiempo (TMT) menor = mejor, ajustar signo. */
export function interpretRCI(rci, { higherIsBetter = true } = {}) {
  if (!Number.isFinite(rci)) return null;
  const direction = higherIsBetter ? rci : -rci;
  const absRCI = Math.abs(rci);

  let level = "no_significativo";
  let pValue = "ns";
  if (absRCI >= 1.96) { level = "significativo"; pValue = "p<.05"; }
  else if (absRCI >= 1.64) { level = "sugestivo"; pValue = "p<.10"; }

  const change = level === "no_significativo"
    ? "estable"
    : direction > 0 ? "mejora" : "deterioro";

  const color = {
    mejora:    "#059669",
    estable:   "#6b7280",
    deterioro: "#dc2626",
  }[change];

  return {
    rci: Math.round(rci * 100) / 100,
    absRCI: Math.round(absRCI * 100) / 100,
    level,
    pValue,
    change,
    color,
    significant: absRCI >= 1.96,
    suggestive: absRCI >= 1.64 && absRCI < 1.96,
  };
}

/* Pipeline completo: pre + post + tipo de métrica → análisis RCI listo. */
export function analyzeRCI({ pre, post, metricKind = "indice", reliability, sem, higherIsBetter = true }) {
  /* Determinar SEM efectivo */
  let effectiveSEM = sem;
  if (!Number.isFinite(effectiveSEM)) {
    const defaults = SEM_DEFAULTS[metricKind];
    if (defaults) {
      const rel = Number.isFinite(reliability) ? reliability : defaults.reliability;
      effectiveSEM = computeSEM(defaults.sd, rel) ?? defaults.semDefault;
    }
  }
  const seDiff = computeSEdiff(effectiveSEM);
  const rci = computeRCI(pre, post, seDiff);
  if (rci === null) return null;
  return {
    pre, post,
    delta: post - pre,
    sem: Math.round(effectiveSEM * 100) / 100,
    seDiff: Math.round(seDiff * 100) / 100,
    ...interpretRCI(rci, { higherIsBetter }),
  };
}

/* Aplicar RCI a un conjunto de resultados pareados (mismo test_id en PRE y POST).
 * `pairs` es un array de { test_id, test_nombre, pre, post, metric }. */
export function analyzePairedResults(pairs) {
  if (!Array.isArray(pairs)) return [];
  return pairs
    .map((p) => {
      const analysis = analyzeRCI({
        pre: p.pre,
        post: p.post,
        metricKind: p.metric || "indice",
        higherIsBetter: p.higherIsBetter !== false,
      });
      return analysis ? { ...p, ...analysis } : null;
    })
    .filter(Boolean);
}
