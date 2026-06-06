/* ═══════════════════════════════════════════════════════════════════════
 * Mapeo CIE-10 → CIE-11 (complementario HC / informes).
 * RIPS export sigue usando solo CIE-10 hasta confirmación MinSalud.
 * Fuente: transición OMS / Res. 1442-2024 Colombia (plazo ~ago 2027).
 * ═══════════════════════════════════════════════════════════════════════ */

/** @type {Record<string, { cie11: string, nombre11: string }>} */
export const CIE10_TO_CIE11 = {
  F32: { cie11: "6A70", nombre11: "Trastorno depresivo único" },
  F320: { cie11: "6A70.0", nombre11: "Episodio depresivo único, leve" },
  F321: { cie11: "6A70.1", nombre11: "Episodio depresivo único, moderado" },
  F322: { cie11: "6A70.2", nombre11: "Episodio depresivo único, grave" },
  F90: { cie11: "6A05", nombre11: "Trastorno por déficit de atención con hiperactividad" },
  F900: { cie11: "6A05.0", nombre11: "TDAH, presentación combinada" },
  F909: { cie11: "6A05.2", nombre11: "TDAH, presentación combinada (sin especificación)" },
  F84: { cie11: "6A02", nombre11: "Trastorno del espectro autista" },
  F840: { cie11: "6A02.0", nombre11: "TEA sin discapacidad intelectual" },
  F431: { cie11: "6B40", nombre11: "Trastorno por estrés postraumático" },
  F438C: { cie11: "6B41", nombre11: "Trastorno de estrés postraumático complejo" },
  F43: { cie11: "6B40", nombre11: "Trastorno por estrés postraumático" },
  G30: { cie11: "6D80", nombre11: "Demencia por enfermedad de Alzheimer" },
  G3184: { cie11: "6D70", nombre11: "Deterioro cognitivo leve" },
  F03: { cie11: "6D86", nombre11: "Demencia, no especificada" },
  F94: { cie11: "6B42", nombre11: "Trastorno de duelo prolongado" },
  F94P: { cie11: "6B42", nombre11: "Trastorno de duelo prolongado (DSM-5-TR)" },
};

export function mapCie10ToCie11(codigo10) {
  if (!codigo10) return null;
  const k = String(codigo10).replace(/\./g, "").toUpperCase();
  const direct = CIE10_TO_CIE11[k] || CIE10_TO_CIE11[codigo10];
  if (direct) return direct;
  const base = k.slice(0, 3);
  return CIE10_TO_CIE11[base] || null;
}

export function formatDualCoding(codigo10, nombre10) {
  const m = mapCie10ToCie11(codigo10);
  if (!m) return `CIE-10: ${codigo10} — ${nombre10 || ""}`.trim();
  return `CIE-10: ${codigo10} — ${nombre10 || ""} | CIE-11: ${m.cie11} — ${m.nombre11}`;
}
