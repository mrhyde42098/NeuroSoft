/* ═══════════════════════════════════════════════════════════════════════
 * src/data/screeningSugerencias.js
 * ───────────────────────────────────────────────────────────────────────
 * §M-8 — Reglas de sugerencia de escalas según motivo de consulta + edad.
 *
 * Cada regla define: matchers (texto MC, edad mínima/máxima, población),
 * y screening IDs a sugerir (deben existir en SCREENING_FORMS).
 *
 * Las reglas son aditivas: un caso puede activar varias y mostrar la
 * unión de sus escalas sugeridas (sin duplicar).
 *
 * IDs válidos (data/screening.js):
 *   MMSE, MoCA, ACE3, PHQ9, GAD7, SNAPIV, SCARED5, ZARIT7, BAI, HADS,
 *   NPIQ_FLAT, BARTHEL, FAQ, VANDERBILT, MCHAT, CDR, GDS15, STAI,
 *   SCARED41, NPIQ, ASRS, CONNERS_ABR, ZARIT, FAB, IFS, IESR, PCL5
 * ═══════════════════════════════════════════════════════════════════════ */

/**
 * @typedef {Object} ReglaScreening
 * @property {string} id - Identificador interno de la regla
 * @property {string} titulo - Etiqueta visible
 * @property {string} razon - Explicación clínica corta de por qué se sugiere
 * @property {RegExp[]} [keywords] - Patrones que matchean el MC (insensitivo a mayúsculas)
 * @property {number} [edadMin] - Edad mínima (años) para que aplique
 * @property {number} [edadMax] - Edad máxima (años) para que aplique
 * @property {string[]} [poblacion] - "infantil" | "adulto_joven" | "adulto_mayor"
 * @property {string[]} screeningIds - IDs de screening a sugerir
 */

/** @type {ReglaScreening[]} */
export const REGLAS_SCREENING = [
  /* ── INFANTIL ────────────────────────────────────────────── */
  {
    id: "tdah_inf",
    titulo: "Sospecha TDAH infantil/adolescente",
    razon: "Patrón inatento o hiperactivo en niños/adolescentes",
    keywords: [
      /\b(tdah|d[ée]ficit\s+de\s+atenci[oó]n|hiperactivid|inatent|distra[ií]b|impulsiv)/i,
      /\bdificultad(es)?\s+(de|para|en)\s+(atender|concentrar|prestar\s+atenci)/i,
      /\bbajo\s+rendimiento\s+(acad[ée]mico|escolar)/i,
    ],
    edadMin: 4, edadMax: 17,
    poblacion: ["infantil"],
    screeningIds: ["SNAPIV", "VANDERBILT", "CONNERS_ABR"],
  },
  {
    id: "ansiedad_inf",
    titulo: "Sospecha ansiedad infantil",
    razon: "Síntomas ansiosos en menores: SCARED es estándar",
    keywords: [
      /\b(ansied|miedo|fobia|p[aá]nico|separaci[oó]n)/i,
      /\bnervios|inquiet|preocupaci/i,
    ],
    edadMin: 6, edadMax: 17,
    poblacion: ["infantil"],
    screeningIds: ["SCARED5", "SCARED41"],
  },
  {
    id: "tea_inf",
    titulo: "Sospecha de TEA / desarrollo atípico",
    razon: "Tamizaje de espectro autista (M-CHAT en preescolares)",
    keywords: [
      /\b(tea|autism|asperger|espectro\s+autista)/i,
      /\b(socializaci[oó]n|comunicaci[oó]n)\s+(at[ií]pic|limitada|alterada)/i,
      /\bestereotip|repetitiv/i,
    ],
    edadMin: 1, edadMax: 6,
    poblacion: ["infantil"],
    screeningIds: ["MCHAT"],
  },
  {
    id: "duelo_trauma_inf",
    titulo: "Sospecha de trauma en infancia",
    razon: "Eventos adversos / abuso / pérdida en menores",
    keywords: [
      /\b(maltrato|abuso|trauma|p[eé]rdida|duelo|tept|estr[eé]s\s+postraum)/i,
    ],
    edadMin: 8, edadMax: 17,
    poblacion: ["infantil"],
    screeningIds: ["IESR"],
  },

  /* ── ADULTO JOVEN ─────────────────────────────────────────── */
  {
    id: "depresion_adu",
    titulo: "Sospecha de depresión (adulto)",
    razon: "PHQ-9 / BAI son primera línea de tamizaje",
    keywords: [
      /\b(depre|tristeza|desesperanza|an[ií]edon|sin\s+motivaci|llant)/i,
      /\b(insomnio|hipersomnia)\s+(asociad|persistente)/i,
    ],
    poblacion: ["adulto_joven"],
    screeningIds: ["PHQ9", "BAI", "HADS"],
  },
  {
    id: "ansiedad_adu",
    titulo: "Sospecha de ansiedad (adulto)",
    razon: "GAD-7 es estándar internacional para TAG",
    keywords: [
      /\b(ansied|p[aá]nico|fobia|preocupaci|nervios|crisis)/i,
    ],
    poblacion: ["adulto_joven"],
    screeningIds: ["GAD7", "BAI", "STAI"],
  },
  {
    id: "tdah_adu",
    titulo: "Sospecha de TDAH adulto",
    razon: "ASRS es la escala oficial OMS para TDAH adulto",
    keywords: [
      /\btdah/i,
      /\b(d[ée]ficit\s+de\s+atenci[oó]n|inatent|olvido|procras|hiperactividad?)\s+(adulto|en\s+el\s+adulto)?/i,
    ],
    edadMin: 18,
    poblacion: ["adulto_joven"],
    screeningIds: ["ASRS"],
  },
  {
    id: "trauma_adu",
    titulo: "Sospecha de TEPT / trauma adulto",
    razon: "PCL-5 es validada DSM-5 para TEPT",
    keywords: [
      /\b(trauma|tept|estr[eé]s\s+postraum|abuso|violenci|accidente|asalto)/i,
    ],
    poblacion: ["adulto_joven", "adulto_mayor"],
    screeningIds: ["PCL5", "IESR"],
  },

  /* ── ADULTO MAYOR ─────────────────────────────────────────── */
  {
    id: "deterioro_am",
    titulo: "Sospecha de deterioro cognitivo (AM)",
    razon: "Tamizaje cognitivo + funcional + ánimo en adulto mayor",
    keywords: [
      /\b(deterioro\s+cognit|p[eé]rdida\s+de\s+memoria|olvido|demenc|alzheim|d[éce]l)/i,
      /\bdesori?ent[a-z]*/i,
    ],
    edadMin: 50,
    poblacion: ["adulto_mayor"],
    screeningIds: ["MoCA", "MMSE", "ACE3", "IFS", "GDS15", "FAQ", "BARTHEL"],
  },
  {
    id: "bvftd_am",
    titulo: "Sospecha DFT / función frontal",
    razon: "IFS Colombia (corte 17.5) discrimina mejor bvFTD vs Alzheimer/depresión",
    keywords: [
      /\b(dft|frontotemporal|pick|conducta|apat[ií]a|desinhib)/i,
      /\b(funci[oó]n\s+ejecutiva|frontal)/i,
    ],
    edadMin: 45,
    poblacion: ["adulto_mayor", "adulto_joven"],
    screeningIds: ["IFS", "MoCA", "ACE3"],
  },
  {
    id: "forense_validez",
    titulo: "Contexto medicolegal / peritaje",
    razon: "Validez de síntomas obligatoria antes de batería completa (Slick 1999)",
    keywords: [
      /\b(peritaje|forense|indemnizaci[oó]n|pensi[oó]n|laboral|simulaci[oó]n|litigio)/i,
    ],
    poblacion: ["adulto_joven", "adulto_mayor"],
    screeningIds: ["PHQ9", "GAD7"],
    notaValidez: "Aplicar protocolo Evaluación → Validez (REY15 + TOMM)",
  },
  {
    id: "depresion_am",
    titulo: "Sospecha de pseudodemencia / depresión geriátrica",
    razon: "Yesavage GDS-15 es estándar para depresión en AM",
    keywords: [
      /\b(depre|tristeza|llant|an[ií]edon|desesperan)/i,
    ],
    edadMin: 50,
    poblacion: ["adulto_mayor"],
    screeningIds: ["GDS15", "PHQ9"],
  },
  {
    id: "cuidador_am",
    titulo: "Sobrecarga del cuidador",
    razon: "Cuando hay mención de cuidador familiar, evaluar Zarit",
    keywords: [
      /\b(cuidador|cuidadora|familiar\s+a\s+cargo|carga\s+familiar)/i,
    ],
    edadMin: 50,
    poblacion: ["adulto_mayor"],
    screeningIds: ["ZARIT7", "ZARIT"],
  },
  {
    id: "parkinson_am",
    titulo: "Sospecha de Parkinson o disfunción frontal",
    razon: "FAB para disfunción frontal subcortical",
    keywords: [
      /\bparkinson|disfunci[oó]n\s+frontal|temblor|bradiquinesia/i,
    ],
    edadMin: 50,
    poblacion: ["adulto_mayor"],
    screeningIds: ["FAB", "MoCA"],
  },
  {
    id: "npi_demencia",
    titulo: "Síntomas neuropsiquiátricos en demencia",
    razon: "NPI-Q para conductuales en demencia (al cuidador)",
    keywords: [
      /\b(agitaci|conductas|agresividad|alucinaci|delir|insomnio\s+nocturno)/i,
    ],
    edadMin: 60,
    poblacion: ["adulto_mayor"],
    screeningIds: ["NPIQ_FLAT", "NPIQ"],
  },
];

/**
 * Calcula qué reglas matchean un caso dado.
 * @param {Object} params
 * @param {string} params.motivoConsulta - Texto del MC (puede ser cualquiera de los 3 sub-campos)
 * @param {number|null} params.edad - Edad en años (null si desconocida)
 * @param {string|null} params.poblacion - "infantil" | "adulto_joven" | "adulto_mayor"
 * @returns {{reglas: ReglaScreening[], screeningIds: string[]}}
 *   reglas: las que aplicaron, en orden de definición.
 *   screeningIds: lista deduplicada de IDs sugeridos.
 */
export function sugerirScreenings({ motivoConsulta, edad, poblacion }) {
  const mc = (motivoConsulta || "").toString();
  const reglasActivas = [];
  for (const r of REGLAS_SCREENING) {
    // Filtro población
    if (r.poblacion?.length && poblacion && !r.poblacion.includes(poblacion)) continue;
    // Filtro edad
    if (edad != null) {
      if (r.edadMin != null && edad < r.edadMin) continue;
      if (r.edadMax != null && edad > r.edadMax) continue;
    }
    // Filtro keywords
    if (r.keywords?.length) {
      const match = r.keywords.some(re => re.test(mc));
      if (!match) continue;
    }
    reglasActivas.push(r);
  }
  const ids = new Set();
  for (const r of reglasActivas) r.screeningIds.forEach(id => ids.add(id));
  return { reglas: reglasActivas, screeningIds: [...ids] };
}
