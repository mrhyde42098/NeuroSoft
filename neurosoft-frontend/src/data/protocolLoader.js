/* ═══════════════════════════════════════════════════════════════════════
 * src/data/protocolLoader.js
 * ───────────────────────────────────────────────────────────────────────
 * Carga unificada de protocolos WISC-IV y WAIS-III para acceso a datos
 * por item: respuestas esperadas, tiempos, reglas de puntuacion.
 *
 * S5.x (Frente 6): además del lookup por test_id, ofrece:
 *   - sugerenciaProtocolo(edad, motivoConsulta, escolaridad)
 *   - tiempoEstimado(testId, escolaridad)
 *   - versionExtendidaQuejaMemoria(testId)
 *
 * Identidad institucional configurable vía ConfigPage (no se distribuye
 * con nombre de persona/tercero).
 * ═══════════════════════════════════════════════════════════════════════ */

import wisc4 from "./protocols/wisc_iv_protocolo.json";
import wais3 from "./protocols/wais_iii_protocolo.json";

const PROTOCOLS = [wisc4, wais3];

/* ── Sugerencia automática por edad + motivo de consulta ───────────── */

/**
 * Reglas de sugerencia de protocolo (S5.x — Frente 6).
 * Cada regla: { edadMin, edadMax, motivoIncluye?, escolaridad?, protocolo, justificacion }.
 * El clínico puede ignorar la sugerencia manualmente.
 */
const REGLAS_SUGERENCIA_PROTOCOLO = [
  {
    id: "wisc_iv_infantil",
    edadMin: 6, edadMax: 16,
    motivoIncluye: ["tdah", "dificultad_aprendizaje", "dislexia", "tdah_sospecha", "rendimiento_academico", "evaluacion_escolar", "neurodesarrollo"],
    protocolo: "wisc_iv",
    testIds: ["NiWiscSem", "NiWiscVoc", "NiWiscDC", "NiWiscConD", "NiWiscMat", "NiWiscRDD", "NiWiscLN", "NiWiscCl", "NiWiscBusSim"],
    justificacion: "WISC-IV es la prueba de referencia para evaluación cognitiva en población infantil y adolescente (6-16 años).",
    duracionTotalMin: 90,
  },
  {
    id: "wais_iii_adulto_joven",
    edadMin: 17, edadMax: 49,
    motivoIncluye: ["discapacidad", "demanda", "tamizaje_cognitivo", "evaluacion_adulto", "disfuncion_ejecutiva", "memoria_adulto", "tdah_adulto", "screening_clinico"],
    protocolo: "wais_iii",
    testIds: ["AdWAISCC", "AdWAISV", "AdWAISRO", "AdWAISFI", "AdWAISHI", "AdWAISI", "AdWAISL", "AdSemWais", "AdMatr", "AdRDI", "AdDReg"],
    justificacion: "WAIS-III es la prueba de referencia para evaluación cognitiva en adultos jóvenes (16-49 años).",
    duracionTotalMin: 110,
  },
  {
    id: "queja_memoria_adulto_mayor",
    edadMin: 50, edadMax: 110,
    motivoIncluye: ["queja_memoria", "deterioro_cognitivo", "demencia_sospecha", "alzheimer", "evaluacion_neuropsicologica", "tamizaje_demencia", "mild_cognitive_impairment", "mci", "deterioro_leve"],
    protocolo: "wais_iii",
    testIds: ["AdWAISCC", "AdWAISRO", "AdWAISFI", "AdWAISHI", "AdWAISL", "AdSemWais", "AdMatr", "AdRDI", "AdDReg"],
    justificacion: "Para adultos mayores con queja de memoria, batería ampliada con WAIS-III + pruebas de memoria Grober-Buschke (no incluidas en este cargador).",
    duracionTotalMin: 130,
  },
];

/**
 * Sugiere un protocolo según edad, motivo de consulta y escolaridad.
 * @param {number} edad
 * @param {string[]} motivosConsulta - array de motivos normalizados
 * @param {string} [escolaridad] - ej. "Universitaria", "Secundaria"
 * @returns {{ protocolo: string, testIds: string[], justificacion: string, duracionTotalMin: number, regla: string } | null}
 */
export function sugerenciaProtocolo(edad, motivosConsulta = [], escolaridad = null) {
  if (typeof edad !== "number" || edad < 0) return null;
  const motivos = Array.isArray(motivosConsulta)
    ? motivosConsulta.map((m) => String(m || "").toLowerCase().trim()).filter(Boolean)
    : [];
  // `escolaridad` se conserva en la firma para análisis futuro
  // (p. ej. ajustar selección de baremos en una versión extendida).
  void escolaridad;

  for (const regla of REGLAS_SUGERENCIA_PROTOCOLO) {
    if (edad < regla.edadMin || edad > regla.edadMax) continue;
    if (regla.motivoIncluye && regla.motivoIncluye.length > 0) {
      const inters = motivos.filter((m) =>
        regla.motivoIncluye.some((kw) => m.includes(kw) || kw.includes(m))
      );
      if (inters.length === 0) continue;
    }
    return {
      protocolo: regla.protocolo,
      testIds: regla.testIds,
      justificacion: regla.justificacion,
      duracionTotalMin: regla.duracionTotalMin,
      regla: regla.id,
    };
  }
  return null;
}

/**
 * Devuelve el protocolo por defecto según edad cuando NO hay un motivo claro.
 */
export function protocoloPorEdad(edad) {
  if (typeof edad !== "number" || edad < 0) return null;
  if (edad < 17) return "wisc_iv";
  return "wais_iii";
}

/* ── Tiempos estimados por test ──────────────────────────────────── */

/**
 * Tiempos estimados de aplicación (en minutos) por subtest.
 * Datos basados en manuales originales y experiencia clínica.
 * Sirve para:
 *  - Cronómetro global de la sesión.
 *  - Aviso al paciente/clínico del progreso estimado.
 */
const TIEMPOS_ESTIMADOS_MIN = {
  // WISC-IV
  NiWiscSem: 7, NiWiscVoc: 7, NiWiscDC: 8, NiWiscConD: 6,
  NiWiscMat: 7, NiWiscRDD: 5, NiWiscLN: 4, NiWiscCl: 4, NiWiscBusSim: 4,
  // WISC-IV índices
  NiWISCIndComVer: 0, NiWISCIndRazPer: 0, NiWISCIndMemTra: 0,
  NiWISCIndVelPro: 0, NiWISCTot: 0,
  // WAIS-III
  AdWAISCC: 4, AdWAISV: 8, AdWAISRO: 6, AdWAISFI: 5, AdWAISHI: 8,
  AdWAISI: 6, AdWAISL: 4, AdSemWais: 6, AdMatr: 7, AdRDI: 4, AdDReg: 5,
  AdWAISC: 0, AdWAISA: 0, AdWAISICV: 0, AdWAISICP: 0, AdWAISIMT: 0,
  AdWAISIVP: 0, AdWASIEVer: 0, AdWAISEMan: 0,
};

export function tiempoEstimado(testId) {
  return TIEMPOS_ESTIMADOS_MIN[testId] ?? null;
}

/**
 * Devuelve el tiempo total estimado (en minutos) para una lista de tests.
 * Excluye los índices compuestos (valor 0).
 */
export function tiempoTotalEstimado(testIds = []) {
  return testIds.reduce((acc, t) => acc + (TIEMPOS_ESTIMADOS_MIN[t] || 0), 0);
}

/* ── Versión extendida para queja de memoria ─────────────────────── */

/**
 * Lista de pruebas adicionales recomendadas en batería de queja
 * subjetiva de memoria (adulto mayor o adulto con sospecha de
 * deterioro). NO son administradas por defecto, se agregan cuando
 * el motivo de consulta es queja de memoria.
 */
const PRUEBAS_QUEJA_MEMORIA_EXTENDIDA = [
  {
    testId: "AdRDI",
    nombre: "Diseño con cubos (WAIS-III)",
    razon: "Evaluar construcción visuoespacial, sensible a demencia.",
  },
  {
    testId: "AdDReg",
    nombre: "Dígitos en regresión (WAIS-III)",
    razon: "Memoria de trabajo, sensible a deterioro subcortical.",
  },
  {
    testId: "AdSemWais",
    nombre: "Semejanzas WAIS",
    razon: "Razonamiento abstracto verbal, sensible a compromiso frontotemporal.",
  },
  {
    testId: "AdWAISHI",
    nombre: "Historias (WAIS-III)",
    razon: "Memoria lógica verbal, evalúa codificación y evocación.",
  },
  {
    testId: "AdWAISL",
    nombre: "Letras y números (WAIS-III)",
    razon: "Memoria de trabajo manipulativa, sensible a compromiso atencional y ejecutivo.",
  },
];

export function versionExtendidaQuejaMemoria() {
  return PRUEBAS_QUEJA_MEMORIA_EXTENDIDA;
}

/**
 * Detecta si la consulta es por queja de memoria y devuelve la versión
 * extendida; si no, devuelve null.
 */
export function sugerenciaQuejaMemoria(motivosConsulta = []) {
  const motivos = Array.isArray(motivosConsulta)
    ? motivosConsulta.map((m) => String(m || "").toLowerCase().trim())
    : [];
  const kws = ["queja_memoria", "memoria", "olvido", "deterioro", "demencia", "mci", "alzheimer"];
  const coincide = motivos.some((m) => kws.some((k) => m.includes(k)));
  if (!coincide) return null;
  return versionExtendidaQuejaMemoria();
}

/* ── API original (preservada) ──────────────────────────────────── */

/**
 * Busca el subtest en todos los protocolos cargados.
 * @param {string} testId - ej. "NiWiscSem", "AdSemWais"
 * @returns {object|null} datos del subtest (items, reglas, etc.)
 */
export function getSubtest(testId) {
  for (const proto of PROTOCOLS) {
    const st = proto?.subtests?.[testId];
    if (st) return st;
  }
  return null;
}

/**
 * Busca un item especifico dentro del subtest.
 * @param {string} testId - ej. "NiWiscSem"
 * @param {number|string} itemNum - numero del item
 * @returns {object|null} datos del item (resp_2pt, resp_1pt, tiempo_seg, etc.)
 */
export function getItem(testId, itemNum) {
  const st = getSubtest(testId);
  if (!st?.items) return null;
  return st.items.find(i => i.num === itemNum || String(i.num) === String(itemNum)) || null;
}

/**
 * Devuelve el tiempo maximo del item actual (para timer auto-ajustable).
 * Solo aplica a pruebas con items que tienen tiempo_seg individual.
 * @returns {number|null} segundos, o null si no hay dato por item
 */
export function getItemTime(testId, itemNum) {
  const item = getItem(testId, itemNum);
  return item?.tiempo_seg || null;
}

/**
 * Indica si este test tiene datos de protocolo (respuestas, tiempos, etc.)
 */
export function hasProtocolData(testId) {
  return !!getSubtest(testId);
}
