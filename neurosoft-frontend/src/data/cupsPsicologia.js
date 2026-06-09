/* Fallback offline mínimo; fuente autoritativa: GET /api/v1/cups/psicologia */
export const CUPS_PSICOLOGIA_FALLBACK = [
  { codigo: "940301", nombre: "Consulta psicología primera vez" },
  { codigo: "940302", nombre: "Consulta psicología control" },
  { codigo: "940303", nombre: "Consulta psicología interdisciplinaria" },
  { codigo: "940680", nombre: "Evaluación neuropsicológica — otra" },
  { codigo: "940681", nombre: "Evaluación neuropsicológica infantil" },
  { codigo: "940682", nombre: "Evaluación neuropsicológica adulto" },
  { codigo: "940683", nombre: "Terapia neuropsicológica" },
  { codigo: "940686", nombre: "Rehabilitación neuropsicológica" },
  { codigo: "940304", nombre: "Intervención psicoterapéutica individual" },
  { codigo: "940305", nombre: "Intervención psicoterapéutica familiar" },
];

/** @deprecated Usar hook useCupsPsicologia() */
export const CUPS_PSICOLOGIA = CUPS_PSICOLOGIA_FALLBACK;
