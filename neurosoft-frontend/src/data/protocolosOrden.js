/* ═══════════════════════════════════════════════════════════════════════
 * src/data/protocolosOrden.js
 * ───────────────────────────────────────────────────────────────────────
 * §M-6 — Orden clínico de aplicación por protocolo.
 *
 * El clínico real NO aplica las pruebas en orden alfabético ni del manual
 * editorial. Aplica respetando:
 *   1. Interferencia (no aplicar memoria verbal seguido de fluidez verbal)
 *   2. Intervalos de retención (codificación → 20 min → recobro)
 *   3. Demanda creciente (atención básica antes que ejecutivas pesadas)
 *
 * Reglas extraídas del CLINICAL_ROADMAP §2.
 *
 * Cada protocolo define:
 *   • orden: array de test_ids o "hitos" abstractos en el orden óptimo
 *   • pares_codificacion_recobro: [{ codificacion, recobro, min_minutos }]
 *     → bloquea el recobro hasta que pasen N minutos desde la codificación
 *   • interferencias: [{ a, b, razon }] → advierte si se intenta encadenar
 *
 * Lo usa ReactivePanel/EvalApplyPage para sugerir el siguiente paso clínico
 * y bloquear acciones inseguras (recobro prematuro).
 * ═══════════════════════════════════════════════════════════════════════ */

/**
 * @typedef {Object} ParCodifReobro
 * @property {string} codificacion - test_id de la prueba de codificación
 * @property {string} recobro      - test_id de la prueba de recobro diferido
 * @property {number} min_minutos  - tiempo mínimo a esperar antes del recobro
 * @property {string} nombre       - etiqueta para mostrar al clínico
 */

/**
 * @typedef {Object} Interferencia
 * @property {string} a - test_id
 * @property {string} b - test_id que NO debe ir inmediatamente después
 * @property {string} razon - explicación clínica
 */

/**
 * @typedef {Object} ProtocoloOrden
 * @property {string} id
 * @property {string} nombre
 * @property {string} poblacion
 * @property {string[]} orden_recomendado - test_ids en orden óptimo
 * @property {ParCodifReobro[]} pares_codificacion_recobro
 * @property {Interferencia[]} interferencias
 * @property {string[]} hitos - descripción narrativa
 */

/** @type {Record<string, string>} — mapeo test_id → nombre legible */
export const NOMBRES_PRUEBAS = {
  // WISC-IV
  NiWiscDC: "Diseño con Cubos", NiWiscSem: "Semejanzas", NiWiscRDD: "Retención de Dígitos",
  NiWiscConD: "Conceptos con Dibujos", NiWiscCl: "Claves", NiWiscVoc: "Vocabulario",
  NiWiscLN: "Letras y Números", NiWiscMat: "Matrices", NiWiscCom: "Comprensión",
  NiWiscBusSim: "Búsqueda de Símbolos", NiWisFigInc: "Figuras Incompletas",
  NiWiscAri: "Aritmética", NiWisInf: "Información", NiWisPalCon: "Palabras en Contexto",
  NiWisReg: "Registros", REY15: "Rey 15-Item (Validez)",
  // WAIS-III
  AdWAISFI: "Figuras Incompletas", AdWAISV: "Vocabulario", AdSDWais: "Clave de Números",
  AdSemWais: "Semejanzas", AdWAISCC: "Diseño con Cubos", AdWAISA: "Aritmética",
  AdWAISI: "Información", AdWAISC: "Comprensión", AdWAISL: "Letras y Números",
  AdWAISHI: "Historietas", AdWAISRO: "Rompecabezas", AdDDir: "Dígitos Directos",
  AdDPros: "Dígitos Progresión", AdDReg: "Dígitos Regresión", AdRDI: "Dígitos Inverso",
  AdBusSim: "Búsqueda de Símbolos", AdMatr: "Matrices",
  // Neuronorma AM
  ViGroberRLT: "Grober — RL Ensayo 1", ViGroberML_Tot: "Grober — Recobro Libre",
  ViGroberMC_Tot: "Grober — Recobro Claves", ViFCROCo: "Figura Rey — Copia",
  ViFCRORec: "Figura Rey — Recobro", ViTMTA: "TMT-A", ViTMTB: "TMT-B",
  ViRDD: "Dígitos Directos", ViRDInv: "Dígitos Inversos", ViSimDig: "Símbolo-Dígito",
  ViStP: "Stroop — Palabra", ViStC: "Stroop — Color", ViStPC: "Stroop — Interferencia",
  ViWCat: "WCST — Categorías", ViP: "Fluidez Fonémica", ViAni: "Fluidez Semántica",
  ViYesavage: "GDS-15 (Yesavage)",
  // Adulto Joven
  AdCVLT: "CVLT — Lista", AdFCRO_Rey: "Figura Rey", AdTMT_AB: "TMT A+B",
  AdStroop_Corr: "Stroop (Corrección)", AdTL_Torre: "Torre de Londres",
  // Screening
  MMSE: "MMSE", MoCA: "MoCA", ACEIII: "ACE-III", PHQ9: "PHQ-9", GAD7: "GAD-7",
  BAI: "BAI", HADS: "HADS", Barthel: "Barthel", Lawton: "Lawton",
  // Screening infantil
  SNAPIV: "SNAP-IV", GADS: "GADS", CDI: "CDI", CPRS: "CPRS", CTRS: "CTRS",
  GDS15: "GDS-15", PCL5: "PCL-5",
};

/** Busca el nombre legible; si no está en el mapa, devuelve el test_id. */
export const nombrePrueba = (testId) => NOMBRES_PRUEBAS[testId] || testId;

/** @type {ProtocoloOrden[]} */
export const PROTOCOLOS_ORDEN = [
  /* ═══ Adulto Mayor — Neuronorma + Grober & Buschke ═══ */
  {
    id: "adulto_mayor",
    nombre: "Adulto Mayor (Neuronorma + Grober)",
    poblacion: "adulto_mayor",
    orden_recomendado: [
      // 0:00 Codificación memoria verbal (CLAVE: hay que esperar 20 min antes del recobro)
      "ViGroberRLT",      // Grober — recobro libre ensayo 1 (codificación)
      // 0:08 Visoconstrucción (no interfiere con memoria verbal)
      "ViFCROCo",         // Figura Rey copia
      // 0:12 Atención básica + memoria de trabajo
      "ViTMTA",
      "ViRDD",            // Dígitos directos
      "ViRDInv",          // Dígitos inversos
      "ViSimDig",         // Símbolo-dígito (velocidad)
      // 0:22 Función ejecutiva
      "ViStP",            // Stroop palabra
      "ViStC",            // Stroop color
      "ViStPC",           // Stroop interferencia
      "ViTMTB",           // TMT-B (alternancia)
      "ViWCat",           // WCST categorías
      // 0:35 RECOBRO DIFERIDO (≥20 min desde codificación)
      "ViGroberML_Tot",   // Grober — recobro libre total
      "ViGroberMC_Tot",   // Grober — recobro con claves
      "ViFCRORec",        // Figura Rey recobro
      // 0:45 Lenguaje
      "ViP",              // Fluidez fonémica
      "ViAni",            // Fluidez semántica
      // 0:55 Estados afectivos
      "ViYesavage",       // GDS-15 al final
    ],
    pares_codificacion_recobro: [
      { codificacion: "ViGroberRLT", recobro: "ViGroberML_Tot", min_minutos: 20, nombre: "Grober — Recuerdo Libre Total" },
      { codificacion: "ViGroberRLT", recobro: "ViGroberMC_Tot", min_minutos: 20, nombre: "Grober — Recuerdo con Claves" },
      { codificacion: "ViFCROCo",    recobro: "ViFCRORec",      min_minutos: 20, nombre: "Figura Rey — Recobro" },
    ],
    interferencias: [
      { a: "ViGroberRLT", b: "ViP",   razon: "Fluidez fonémica interfiere con memoria verbal recién codificada" },
      { a: "ViGroberRLT", b: "ViAni", razon: "Fluidez semántica interfiere con memoria verbal recién codificada" },
    ],
    hitos: [
      "0:00 Consigna + ubicación",
      "0:02 Codificación memoria verbal (Grober)",
      "0:08 Visoconstrucción (Rey copia)",
      "0:12 Atención + memoria de trabajo",
      "0:22 Función ejecutiva",
      "0:35 ⏱ Recobro diferido (≥20 min desde codificación)",
      "0:45 Lenguaje (fluidez)",
      "0:55 Estado afectivo (Yesavage)",
    ],
  },

  /* ═══ Adulto Joven — WAIS-III + Memoria Verbal + EF ═══ */
  {
    id: "adulto_joven",
    nombre: "Adulto Joven (WAIS-III + EF)",
    poblacion: "adulto_joven",
    orden_recomendado: [
      "AdCVLT",           // Lista de palabras CVLT (codificación)
      "AdFCRO_Rey",       // Figura Rey copia/recobro inmediato
      "AdTMT_AB",         // TMT A y B (atención + ejecutiva)
      "AdStroop_Corr",    // Stroop con corrección por edad
      "AdDDir",           // Dígitos directos
      "AdDPros",          // Dígitos progresión
      "AdDReg",           // Dígitos regresión
      "AdRDI",            // Dígitos inverso
      "AdSDWais",         // Símbolo-dígito WAIS
      "AdBusSim",         // Búsqueda de símbolos
      "AdMatr",           // Matrices
      "AdWAISCC",         // Cubos
      "AdSemWais",        // Semejanzas
      "AdWAISV",          // Vocabulario
      "AdWAISA",          // Aritmética
      "AdWAISI",          // Información
      "AdWAISC",          // Comprensión
      "AdWAISL",          // Letras y números
      "AdWAISFI",         // Figuras incompletas
      "AdWAISHI",         // Historietas
      "AdWAISRO",         // Rompecabezas
      "AdTL_Torre",       // Torre de Londres (ejecutiva compleja)
    ],
    pares_codificacion_recobro: [
      { codificacion: "AdCVLT",     recobro: "AdCVLT",     min_minutos: 20, nombre: "CVLT — Recobro diferido" },
      { codificacion: "AdFCRO_Rey", recobro: "AdFCRO_Rey", min_minutos: 30, nombre: "Figura Rey — Recobro diferido" },
    ],
    interferencias: [],
    hitos: [
      "0:00 Codificación memoria verbal (CVLT)",
      "0:06 Figura Rey copia",
      "0:12 Atención + velocidad de procesamiento",
      "0:25 Funciones ejecutivas",
      "0:35 Memoria de trabajo + Vocabulario/Información",
      "0:55 Recobros diferidos",
    ],
  },

  /* ═══ Infantil — WISC-IV + ENI-2 ═══ */
  {
    id: "infantil_wisc",
    nombre: "Infantil — WISC-IV + ENI-2",
    poblacion: "infantil",
    orden_recomendado: [
      "NiEniMLP",         // Lista de palabras ENI (codificación)
      "NiWiscDC",         // Diseño con Cubos
      "NiWiscSem",        // Semejanzas
      "NiWiscRDD",        // Regresión Dígitos Directos
      "NiWiscConD",       // Conceptos con dibujos
      "NiWiscCl",         // Claves (atención sostenida)
      "NiWiscMat",        // Matrices
      "NiWiscVoc",        // Vocabulario
      "NiWiscLN",         // Números y letras
      "NiWiscBusSim",     // Búsqueda de símbolos
      "NiWiscCom",        // Comprensión
      "NiWiscAri",        // Aritmética
      "NiENIRHis",        // ENI lectura historia
      "NiENICDib",        // ENI copia dibujo
      "NiEniReco",        // ENI recobro
      "NiENIMLPCl",       // ENI MLP con claves (recobro diferido)
    ],
    pares_codificacion_recobro: [
      { codificacion: "NiEniMLP", recobro: "NiEniReco",    min_minutos: 20, nombre: "ENI — Recobro espontáneo" },
      { codificacion: "NiEniMLP", recobro: "NiENIMLPCl",  min_minutos: 20, nombre: "ENI — Recobro con claves" },
    ],
    interferencias: [],
    hitos: [
      "0:00 Codificación memoria verbal (ENI MLP)",
      "0:05 WISC-IV subtests principales",
      "0:40 Lenguaje + cálculo",
      "0:50 ENI lectura/copia",
      "0:55 Recobros ENI (≥20 min)",
    ],
  },
];

/** Devuelve protocolo para un test_id dado (busca en cada protocolo). */
export function protocoloParaTest(testId) {
  return PROTOCOLOS_ORDEN.find(p => p.orden_recomendado.includes(testId));
}

/** Devuelve par codificación-recobro si testId es de tipo recobro. */
export function parRecobroPara(testId) {
  for (const p of PROTOCOLOS_ORDEN) {
    const par = p.pares_codificacion_recobro.find(pr => pr.recobro === testId);
    if (par) return { ...par, protocolo: p.id };
  }
  return null;
}

/** Devuelve el siguiente test recomendado dado el último aplicado. */
export function siguienteTestRecomendado(testIdActual, protocoloId = null) {
  const proto = protocoloId
    ? PROTOCOLOS_ORDEN.find(p => p.id === protocoloId)
    : protocoloParaTest(testIdActual);
  if (!proto) return null;
  const idx = proto.orden_recomendado.indexOf(testIdActual);
  if (idx === -1 || idx === proto.orden_recomendado.length - 1) return null;
  return proto.orden_recomendado[idx + 1];
}

/** Verifica si un test causa interferencia con el siguiente. */
export function detectarInterferencia(testActual, testSiguiente) {
  for (const p of PROTOCOLOS_ORDEN) {
    const inter = p.interferencias.find(i => i.a === testActual && i.b === testSiguiente);
    if (inter) return inter;
  }
  return null;
}
