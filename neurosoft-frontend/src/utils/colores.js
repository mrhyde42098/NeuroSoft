/* ═══════════════════════════════════════════════════════════════════════
 * src/utils/colores.js — Helpers compartidos entre páginas
 * ───────────────────────────────────────────────────────────────────────
 * Funciones puras pequeñas que se usan en varias páginas. No dependen
 * de React; pueden importarse desde cualquier módulo sin acoplamientos.
 * ═══════════════════════════════════════════════════════════════════════ */

/**
 * Color por nivel de interpretación clínica.
 *
 * Soporta tres familias de etiquetas:
 *   1. Estándar WISC/WAIS: Bajo / Limítrofe / Promedio / Superior
 *   2. Escalas clínicas (Yesavage, MMSE, Lawton): Normal / Déficit Leve /
 *      Déficit Extremo / Déficit Severo (códigos N/DL/DE/DS del baremo).
 *   3. Beck BDI-II (fallback): Mínima / Leve / Moderada / Severa.
 *
 * Si la etiqueta no se reconoce, devuelve gris neutro.
 */
export const lc = (i) => ({
  // Estándar WISC/WAIS
  "Bajo":            "#ba1a1a",
  "Limítrofe":       "#943700",
  "Promedio":        "#006a6a",
  "Superior":        "#0D9488",
  // Escalas clínicas (Yesavage GDS-15, MMSE, Lawton, etc.)
  "Normal":          "#006a6a",
  "Deficit Leve":    "#943700",
  "Deficit Extremo": "#ba1a1a",
  "Deficit Severo":  "#7c1212",
  // Beck BDI-II
  "Mínima":          "#006a6a",
  "Leve":            "#943700",
  "Moderada":        "#ba1a1a",
  "Severa":          "#7c1212",
}[i] || "#434655");
