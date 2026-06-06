/* ═══════════════════════════════════════════════════════════════════════
 * Validez de síntomas — criterios Slick et al. 1999 + cortes TOMM/Rey.
 * ═══════════════════════════════════════════════════════════════════════ */

export const SLICK_CRITERIA = [
  {
    id: "A",
    label: "Incentivo externo significativo",
    desc: "Laboral, forense, indemnización, pensión, litigio.",
  },
  {
    id: "B",
    label: "Evidencia psicométrica",
    desc: "≥1 prueba de validez fallida (TOMM Trial 2 <45, Rey ≤9, etc.).",
  },
  {
    id: "C",
    label: "Evidencia comportamental",
    desc: "Inconsistencia entre queja, observación y rendimiento.",
  },
  {
    id: "D",
    label: "No explicable solo por trastorno",
    desc: "Comportamiento no atribuible plenamente a condición psiquiátrica/neurológica.",
  },
];

/** @param {{ tomTrial2?: number, rey15?: number, incentivoExterno?: boolean, svtFallidas?: number }} p */
export function evaluarValidezSlick(p) {
  const flags = [];
  if (p.incentivoExterno) flags.push("A");
  const svt = [];
  if (p.tommTrial2 != null && p.tommTrial2 < 45) svt.push("TOMM Trial 2");
  if (p.rey15 != null && p.rey15 <= 9) svt.push("Rey 15-Item");
  if ((p.svtFallidas || 0) > 0 || svt.length > 0) flags.push("B");
  const nSvt = svt.length + (p.svtFallidas || 0);
  return {
    criterios: flags,
    svtFallidas: svt,
    alerta:
      nSvt > 0
        ? `ADVERTENCIA: posible respuesta no creíble (${svt.join(", ")}). Considerar criterios Slick y contexto forense.`
        : null,
    tomCorte: 45,
  };
}

export const VALIDEZ_TESTS = [
  { test_id: "REY15", nombre: "Rey 15-Item", corte: "≤9 ítems", dominio: "Validez de síntomas" },
  { test_id: "TOMM", nombre: "TOMM", corte: "Trial 2 <45/50", dominio: "Validez de síntomas" },
];
