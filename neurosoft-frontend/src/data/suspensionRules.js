/* ═══════════════════════════════════════════════════════════════════════
 * suspensionRules.js — Reglas de suspensión WISC-IV / WAIS-III
 * ───────────────────────────────────────────────────────────────────────
 * S1.7 del PLAN_MAESTRO: detección automática de criterios de
 * suspensión para tests Wechsler según manuales oficiales.
 *
 * Reglas WISC-IV (cap. 3, p. 50-52):
 *   - Suspensión por BASAL: 2 puntuaciones perfectas (0 errores) consecutivas
 *     en los primeros reactivos → suspender.
 *   - Suspensión por TECHO: en los últimos reactivos todas las
 *     puntuaciones son 0 → suspender (ya no hay más items que el paciente
 *     pueda fallar).
 *   - Discontinuación por tiempo máximo: si el clínico fija un tiempo
 *     límite por reactivo, agotar el tiempo en N consecutivos → suspender.
 *
 * Reglas WAIS-III (cap. 4):
 *   - Similar a WISC-IV con reactivos de inicio diferentes.
 *
 * Esta utilidad NO aplica la suspensión automáticamente (el clínico decide);
 * SOLO notifica cuándo se cumple un criterio para que el clínico pueda
 * documentar la decisión en el informe.
 *
 * Autor: NeuroSoft — 2026
 * ═══════════════════════════════════════════════════════════════════════ */

/**
 * Detecta criterios de suspensión aplicables a una secuencia de items.
 *
 * @param {Object} opts
 * @param {number[]} opts.puntajes - Lista de puntajes por item (0=error, 1=acierto).
 * @param {boolean} [opts.invertido] - true si 0=acierto (Stroop, Claves).
 * @param {number} [opts.basalN=2] - N consecutivas perfectas al inicio.
 * @param {number} [opts.techoN=5] - N consecutivas perfectas al final.
 * @returns {Object} { basal, techo, tiempoExcedido, razones[] }
 */
export function detectarSuspension(opts) {
  const {
    puntajes = [],
    invertido = false,
    basalN = 2,
    techoN = 5,
    limiteTiempoSeg = null,
    tiemposPorItem = [],
  } = opts;

  const exitoso = (v) => (invertido ? v === 0 : v === 1);

  const razones = [];
  let basal = false;
  let techo = false;
  let tiempoExcedido = false;

  if (puntajes.length === 0) {
    return { basal, techo, tiempoExcedido, razones: ["Sin puntajes capturados"] };
  }

  // ─── Regla BASAL: N perfectas consecutivas al inicio ───
  let consecutivasIniciales = 0;
  for (let i = 0; i < puntajes.length && i < basalN + 1; i++) {
    if (exitoso(puntajes[i])) {
      consecutivasIniciales++;
    } else {
      break;
    }
  }
  if (consecutivasIniciales >= basalN) {
    basal = true;
    razones.push(
      `Basal alcanzado: ${consecutivasIniciales} puntajes perfectos ` +
      `consecutivos al inicio (≥${basalN} requerido por manual WISC-IV/WAIS-III).`
    );
  }

  // ─── Regla TECHO: N perfectas consecutivas al final ───
  if (puntajes.length >= techoN) {
    let consecutivasFinales = 0;
    for (let i = puntajes.length - 1; i >= 0; i--) {
      if (exitoso(puntajes[i])) {
        consecutivasFinales++;
      } else {
        break;
      }
    }
    if (consecutivasFinales >= techoN) {
      techo = true;
      razones.push(
        `Techo alcanzado: ${consecutivasFinales} puntajes perfectos ` +
        `consecutivos al final (≥${techoN} requerido).`
      );
    }
  }

  // ─── Regla TIEMPO: si hay tiempos por item y limite, contar excesos ───
  if (limiteTiempoSeg != null && tiemposPorItem.length > 0) {
    const excesos = tiemposPorItem.filter((t) => t > limiteTiempoSeg).length;
    if (excesos >= 3) {
      tiempoExcedido = true;
      razones.push(
        `Límite de tiempo (${limiteTiempoSeg}s) excedido en ${excesos} items.`
      );
    }
  }

  return { basal, techo, tiempoExcedido, razones };
}

/**
 * Sugerencia textual para mostrar al clínico en la UI.
 *
 * @param {Object} suspension - Salida de detectarSuspension().
 * @returns {string|null} - Mensaje o null si no aplica.
 */
export function mensajeSuspension(suspension) {
  if (!suspension) return null;
  if (suspension.razones.length === 0) return null;
  return "⚠ " + suspension.razones.join(" ");
}

/**
 * Razón principal que se incluirá en el informe clínico si
 * el clínico decide documentar la suspensión.
 *
 * @param {Object} suspension - Salida de detectarSuspension().
 * @returns {string} - Razón principal en una línea, o "" si no aplica.
 */
export function razonDocumentar(suspension) {
  if (!suspension || suspension.razones.length === 0) return "";
  return suspension.razones[0];
}
