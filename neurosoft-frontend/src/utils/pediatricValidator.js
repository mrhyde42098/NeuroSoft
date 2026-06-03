/* ═══════════════════════════════════════════════════════════════════════
 * src/utils/pediatricValidator.js — Validador de redacción pediátrica
 * ───────────────────────────────────────────────────────────────────────
 * Reglas (Guía Informe NPS WISC) para informes de niños:
 * • NUNCA usar "conserva" o "preserva" → usar "muestra adecuado…"
 * • Usar prefijo DIS- en lugar de A-:
 * afasia → disfasia
 * agrafía → disgrafía
 * alexia → dislexia
 * acalculia → discalculia
 * apraxia → dispraxia
 * • NO hablar de la prueba sino de la función cognitiva.
 *
 * El validador es advisory (warnings no bloqueantes). Devuelve un array
 * de objetos `{severity, term, message, suggestion}` que la UI muestra
 * antes de guardar.
 *
 * Uso:
 * import { validatePediatricText, isChildAge } from "./pediatricValidator";
 * const warnings = validatePediatricText(texto);
 * ═══════════════════════════════════════════════════════════════════════ */

const FORBIDDEN_TERMS = [
 /* Términos prohibidos generales pediátricos */
 {
 pattern: /\bconserv[ao]s?\b/gi,
 severity: "warn",
 suggestion: 'En niños, en lugar de "conserva" use "muestra adecuado desarrollo de…" o "se evidencia adecuado funcionamiento en…".',
 },
 {
 pattern: /\bpreserv[ao]s?\b/gi,
 severity: "warn",
 suggestion: 'Evite "preserva" en niños — implica que algo previo era íntegro. Prefiera "muestra adecuado desarrollo de…".',
 },
 /* Prefijo A- → DIS- */
 {
 pattern: /\bafasia\b/gi,
 severity: "error",
 suggestion: 'En niños use "disfasia" (los cuadros congénitos llevan prefijo DIS-, no A-).',
 },
 {
 pattern: /\bagraf[ií]a\b/gi,
 severity: "error",
 suggestion: 'En niños use "disgrafía" (no "agrafía").',
 },
 {
 pattern: /\balexia\b/gi,
 severity: "error",
 suggestion: 'En niños use "dislexia" (no "alexia").',
 },
 {
 pattern: /\bacalculia\b/gi,
 severity: "error",
 suggestion: 'En niños use "discalculia" (no "acalculia").',
 },
 {
 pattern: /\bapraxia\b/gi,
 severity: "error",
 suggestion: 'En niños use "dispraxia" (no "apraxia").',
 },
 /* Hablar de la prueba en vez de la función */
 {
 pattern: /\b(WISC[- ]?I?V?|WAIS[- ]?I+I?I?V?|en el subtest|en la subprueba|en la prueba de Cubos|en Vocabulario|en Semejanzas|en Matrices|en Claves|en B[uú]squeda de S[ií]mbolos)\b/gi,
 severity: "info",
 suggestion: "Hable de la FUNCIÓN COGNITIVA evaluada, noombre de la prueba. Ej: en lugar de \"obtuvo un puntaje bajo en Aritmética\" use \"se evidencia dificultad para realizar operaciones aritméticas mentalmente, lo que afecta la memoria de trabajo verbal\".",
 },
];

/**
 * @param text {string} texto a validar (un dominio o el informe completo)
 * @returns {Array<{severity, term, message, suggestion}>}
 */
export function validatePediatricText(text) {
 if (!text || typeof text !== "string") return [];
 const out = [];
 const seen = new Set();
 for (const rule of FORBIDDEN_TERMS) {
 const matches = text.match(rule.pattern);
 if (!matches) continue;
 /* Deduplicar términos ya reportados (no repetir el mismo error 3 veces) */
 const unique = [...new Set(matches.map((m) => m.toLowerCase()))];
 unique.forEach((term) => {
 const key = `${rule.severity}:${term}`;
 if (seen.has(key)) return;
 seen.add(key);
 out.push({
 severity: rule.severity,
 term,
 suggestion: rule.suggestion,
 });
 });
 }
 return out;
}

/* Heurística: ¿el paciente es un niño? Recibe la fecha de nacimiento o
 * la edad en años. ≤17 años = pediátrico. */
export function isChildAge(fechaNacimiento) {
 if (typeof fechaNacimiento === "number") return fechaNacimiento <= 17;
 if (!fechaNacimiento) return false;
 try {
 const dob = new Date(fechaNacimiento);
 if (Number.isNaN(dob.getTime())) return false;
 const age = Math.floor((Date.now() - dob.getTime()) / (365.25 * 24 * 3600 * 1000));
 return age <= 17;
 } catch {
 return false;
 }
}

/* Valida un objeto de observaciones por dominio (obsT del EvalResults).
 * Devuelve { domain → warnings[] }. */
export function validatePediatricObservations(obsByDomain) {
 const out = {};
 Object.entries(obsByDomain || {}).forEach(([domain, text]) => {
 const w = validatePediatricText(text);
 if (w.length > 0) out[domain] = w;
 });
 return out;
}
