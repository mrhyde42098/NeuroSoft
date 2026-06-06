/* ═══════════════════════════════════════════════════════════════════════
 * pearsonProtected.js — Capa protegida para ítems verbatim Pearson
 * ───────────────────────────────────────────────────────────────────────
 * Diseño S5.x (refinamiento del S2.6): ACEPTACIÓN ÚNICA AL INSTALAR
 *
 * Modelo de cumplimiento:
 *   1. El clínico responsable acepta UNA SOLA VEZ al instalar/iniciar
 *      la app por primera vez, declarando:
 *        - Posee licencia válida del material (WISC-IV, WAIS-III).
 *        - Usará los ítems verbatim SOLO con fines clínicos.
 *        - No redistribuirá los ítems.
 *      Esta aceptación queda persistida en localStorage con versión
 *      para invalidar ante cambios legales.
 *   2. Una vez aceptada, los ítems verbatim son accesibles SIN
 *      confirmación adicional en cada acceso (flujo clínico fluido).
 *   3. Un sello discreto [Material con copyright] identifica visualmente
 *      los ítems verbatim, recordatorio continuo del licenciamiento.
 *   4. Cada acceso se registra automáticamente en audit log
 *      (POST /api/v1/audit/clinical-access) para trazabilidad legal.
 *   5. La aceptación es REVOCABLE en Configuración → Privacidad y
 *      cumplimiento.
 *
 * Cobertura legal:
 *   - Ley 23 de 1982 (Colombia) — Derechos de autor.
 *   - Ley 44 de 1993 — Modificaciones a Ley 23.
 *   - Decisión 486 de 2000 (CAN) — Régimen Común sobre Propiedad Intelectual.
 *   - Tratados OMPI (WIPO) — derechos de autor en software.
 *   - Editorial El Manual Moderno / Pearson — licenciamiento.
 *
 * Cobertura clínica (apoyo, no solo legal):
 *   - Acceso a instrucciones resumidas del ítem.
 *   - Marcador visual de prueba con copyright.
 *   - Recordatorio del manual original al pie del ítem.
 *   - Warning si la fecha de la licencia del usuario está próxima a vencer.
 *
 * Autor: NeuroSoft — 2026
 * ═══════════════════════════════════════════════════════════════════════ */

/* Versión del acuerdo: incrementar para forzar re-aceptación ante
 * cambios legales o de licenciamiento. */
export const VERSION_ACUERDO = "2.0.0";

/* Clave en localStorage: una sola, global (no por paciente/protocolo). */
const STORAGE_KEY = "ns_pearson_consent_global";
const STORAGE_VERSION_KEY = "ns_pearson_consent_version";

/**
 * Tests con ítems verbatim. Otros tests se renderizan sin restricciones.
 */
export const TESTS_VERBATIM = new Set([
  // WAIS-III
  "AdWAISCC",
  "AdWAISV",
  "AdWAISRO",
  "AdWAISFI",
  "AdWAISHI",
  "AdWAISI",
  "AdWAISL",
  "AdWAISC",
  "AdWAISA",
  "AdSemWais",
  "AdMatr",
  // WISC-IV
  "NiWiscSem",
  "NiWiscVoc",
  "NiWiscCom",
  "NiWiscDC",
  "NiWiscConD",
  "NiWiscMat",
  "NiWiscRDD",
  "NiWiscLN",
  "NiWiscCl",
  "NiWiscBusSim",
  "NiWiscAri",
  "NiWisFigInc",
  "NiWisInf",
  "NiWisPalCon",
]);

/**
 * Metadatos de la prueba verbatim: nombre legible, manual, año, ISBN.
 * Sirve para mostrar al clínico la fuente original con un click.
 */
export const METADATOS_VERBATIM = {
  AdWAISCC: {
    nombre: "Claves (WAIS-III)",
    manual: "WAIS-III — Manual Técnico",
    editorial: "Editorial El Manual Moderno / Pearson",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Cuaderno de Estímulos, ítems 1-93",
  },
  AdWAISV: {
    nombre: "Vocabulario (WAIS-III)",
    manual: "WAIS-III — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Lista de palabras A y B",
  },
  AdWAISRO: {
    nombre: "Retención de Dígitos (WAIS-III)",
    manual: "WAIS-III — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Secuencias 1-9 y 2-9",
  },
  AdWAISFI: {
    nombre: "Figuras Incompletas (WAIS-III)",
    manual: "WAIS-III — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Láminas 1-25",
  },
  AdWAISHI: {
    nombre: "Historias (WAIS-III)",
    manual: "WAIS-III — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Historias A-E",
  },
  AdWAISI: {
    nombre: "Información (WAIS-III)",
    manual: "WAIS-III — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Preguntas 1-33",
  },
  AdWAISL: {
    nombre: "Letras y Números (WAIS-III)",
    manual: "WAIS-III — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Secuencias 1-7",
  },
  NiWiscSem: {
    nombre: "Semejanzas (WISC-IV)",
    manual: "WISC-IV — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Lista de 26 pares de palabras",
  },
  NiWiscVoc: {
    nombre: "Vocabulario (WISC-IV)",
    manual: "WISC-IV — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Lista de 32 palabras A y B",
  },
  NiWiscDC: {
    nombre: "Diseño con Cubos (WISC-IV)",
    manual: "WISC-IV — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Diseños 1-14 (cubos) y 1-9 (modelos)",
  },
  NiWiscConD: {
    nombre: "Conceptos (WISC-IV)",
    manual: "WISC-IV — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Láminas 1-28",
  },
  NiWiscMat: {
    nombre: "Matrices (WISC-IV)",
    manual: "WISC-IV — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "35 ítems",
  },
  NiWiscRDD: {
    nombre: "Retención de Dígitos (WISC-IV)",
    manual: "WISC-IV — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Secuencias 1-8 directo, 1-7 inverso",
  },
  NiWiscLN: {
    nombre: "Letras y Números (WISC-IV)",
    manual: "WISC-IV — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Secuencias 1-10",
  },
  NiWiscCl: {
    nombre: "Claves (WISC-IV)",
    manual: "WISC-IV — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Hoja de codificación y símbolos",
  },
  NiWiscBusSim: {
    nombre: "Búsqueda de Símbolos (WISC-IV)",
    manual: "WISC-IV — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Bloques de búsqueda de símbolos",
  },
  NiWiscCom: {
    nombre: "Comprensión (WISC-IV)",
    manual: "WISC-IV — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Preguntas situacionales 1-21",
  },
  NiWiscAri: {
    nombre: "Aritmética (WISC-IV)",
    manual: "WISC-IV — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Problemas 1-34",
  },
  NiWisFigInc: {
    nombre: "Figuras Incompletas (WISC-IV)",
    manual: "WISC-IV — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Láminas 1-38",
  },
  NiWisInf: {
    nombre: "Información (WISC-IV)",
    manual: "WISC-IV — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Preguntas 1-33",
  },
  NiWisPalCon: {
    nombre: "Palabras en Contexto (WISC-IV)",
    manual: "WISC-IV — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 2007,
    isbn: "978-968-426-987-0",
    pagina: "Ítems con pistas 1-24",
  },
  AdSemWais: {
    nombre: "Semejanzas (WAIS-III)",
    manual: "WAIS-III — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Pares 1-19",
  },
  AdWAISC: {
    nombre: "Comprensión (WAIS-III)",
    manual: "WAIS-III — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Situaciones 1-18",
  },
  AdWAISA: {
    nombre: "Aritmética (WAIS-III)",
    manual: "WAIS-III — Manual de Aplicación",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Problemas 1-20",
  },
  AdMatr: {
    nombre: "Matrices (WAIS-III)",
    manual: "WAIS-III — Cuaderno de Estímulos",
    editorial: "Editorial El Manual Moderno",
    anio: 1997,
    isbn: "978-968-426-984-9",
    pagina: "Ítems A-C y 1-26",
  },
};

/**
 * Determina si un test tiene ítems verbatim.
 */
export function esVerbatim(testId) {
  if (!testId) return false;
  return TESTS_VERBATIM.has(testId);
}

/**
 * Devuelve metadatos de la prueba (manual, ISBN, página) si es verbatim.
 */
export function metadatosVerbatim(testId) {
  if (!esVerbatim(testId)) return null;
  return METADATOS_VERBATIM[testId] || null;
}

/**
 * Verifica si el clínico aceptó el acuerdo global de uso de material
 * con copyright en la versión actual.
 *
 * @returns {{
 *   aceptado: boolean,
 *   version: string | null,
 *   fechaAceptacion: string | null,
 *   versionActual: string,
 *   requiereReAceptacion: boolean,
 * }}
 */
export function estadoAceptacionGlobal() {
  const versionAceptada = safeLS.get(STORAGE_VERSION_KEY);
  const fechaAceptacion = safeLS.get(STORAGE_KEY);
  const versionActual = VERSION_ACUERDO;
  return {
    aceptado: versionAceptada === versionActual && !!fechaAceptacion,
    version: versionAceptada,
    fechaAceptacion,
    versionActual,
    requiereReAceptacion: versionAceptada !== versionActual,
  };
}

/**
 * Registra la aceptación del acuerdo global.
 * @param {string} [usuarioId] - ID del clínico que acepta (para audit)
 * @param {string} [usuarioNombre] - Nombre legible
 */
export function registrarAceptacionGlobal(usuarioId = null, usuarioNombre = null) {
  const ts = new Date().toISOString();
  safeLS.set(STORAGE_VERSION_KEY, VERSION_ACUERDO);
  safeLS.set(STORAGE_KEY, ts);
  if (usuarioId) safeLS.set("ns_pearson_consent_user_id", usuarioId);
  if (usuarioNombre) safeLS.set("ns_pearson_consent_user_name", usuarioNombre);
  // Auditar aceptación
  try {
    registrarAceptacionEnBackend(usuarioId, usuarioNombre, VERSION_ACUERDO, ts);
  } catch {
    // Best effort — la UI seguirá funcionando offline.
  }
}

/**
 * Revoca la aceptación. La próxima vez que se intente acceder a un
 * ítem verbatim, se mostrará de nuevo el diálogo.
 */
export function revocarAceptacionGlobal() {
  safeLS.remove(STORAGE_KEY);
  safeLS.remove(STORAGE_VERSION_KEY);
  safeLS.remove("ns_pearson_consent_user_id");
  safeLS.remove("ns_pearson_consent_user_name");
  try {
    registrarRevocacionEnBackend();
  } catch {
    // Best effort.
  }
}

/* ─────────────────────────────────────────────────────────────
 * Backwards compat: API antigua (per-patient/protocol)
 * Mantenida para no romper integraciones existentes; ahora son
 * aliases de la API global con un wrapper deprecado.
 * ───────────────────────────────────────────────────────────── */

/**
 * @deprecated Usar `estadoAceptacionGlobal()` en su lugar.
 * Conserva firma previa por retrocompat.
 */
export function tieneConsentimiento(/* patientId, protocolo */) {
  return estadoAceptacionGlobal().aceptado;
}

/**
 * @deprecated Usar `registrarAceptacionGlobal()` en su lugar.
 */
export function registrarConsentimiento(/* patientId, protocolo */) {
  registrarAceptacionGlobal();
}

/**
 * @deprecated Usar `revocarAceptacionGlobal()` en su lugar.
 */
export function revocarConsentimiento(/* patientId, protocolo */) {
  revocarAceptacionGlobal();
}

/* Sello discreto: NO interrumpe el flujo, solo identifica visualmente
 * que el contenido tiene copyright. */
export const SELLO_PROTEGIDO = {
  texto: "© Material con copyright",
  claseCSS: "ns-pearson-protected",
  ariaLabel:
    "Ítem de prueba psicológica con derechos de autor; el acceso queda " +
    "registrado en la auditoría clínica.",
  tooltip:
    "Material con copyright. Acceso registrado para cumplimiento de " +
    "Ley 23 de 1982 (Colombia). Solo uso clínico.",
};

/**
 * Hook para registrar el evento de auditoría cuando se muestra un ítem.
 * Se llama UNA VEZ por ítem mostrado (no por cada render), deduplicado
 * por (testId, itemIndex) en la misma sesión.
 */
const _accesosRegistrados = new Set();

export async function registrarAccesoItem(testId, itemIndex, contexto = {}) {
  if (!testId) return;
  const key = `${testId}:${itemIndex ?? "_"}`;
  if (_accesosRegistrados.has(key)) return; // dedupe intra-sesión
  _accesosRegistrados.add(key);
  try {
    const { default: api } = await import("../api/client.js");
    await api.post("/api/v1/audit/clinical-access", {
      test_id: testId,
      item_index: itemIndex ?? null,
      action: "view_verbatim_item",
      timestamp: new Date().toISOString(),
      ...contexto,
    });
  } catch (e) {
    // Si el endpoint no existe, no rompemos la app
    console.debug("[pearsonProtected] audit log no disponible:", e?.message);
  }
}

/**
 * Helper para el panel de React: dado un test_id, devuelve
 * el comportamiento a aplicar.
 *
 * @returns {{
 *   protegido: boolean,
 *   requiereAceptacion: boolean,
 *   aceptado: boolean,
 *   sello: object | null,
 *   metadatos: object | null,
 * }}
 */
export function estadoProteccion(testId) {
  const protegido = esVerbatim(testId);
  const global = estadoAceptacionGlobal();
  return {
    protegido,
    requiereAceptacion: protegido && !global.aceptado,
    aceptado: protegido && global.aceptado,
    sello: protegido ? SELLO_PROTEGIDO : null,
    metadatos: protegido ? metadatosVerbatim(testId) : null,
  };
}

/* ═══════════════════════════════════════════════════════════════
 * Internos
 * ═══════════════════════════════════════════════════════════════ */

const safeLS = {
  get(k) {
    try { return localStorage.getItem(k); } catch { return null; }
  },
  set(k, v) {
    try { localStorage.setItem(k, v); } catch { /* ignore */ }
  },
  remove(k) {
    try { localStorage.removeItem(k); } catch { /* ignore */ }
  },
};

async function registrarAceptacionEnBackend(usuarioId, usuarioNombre, version, ts) {
  try {
    const { default: api } = await import("../api/client.js");
    await api.post("/api/v1/audit/clinical-access", {
      test_id: "__consent__",
      item_index: null,
      action: "accept_verbatim_terms",
      timestamp: ts,
      context: { version, usuario_id: usuarioId, usuario_nombre: usuarioNombre },
    });
  } catch { /* offline OK */ }
}

async function registrarRevocacionEnBackend() {
  try {
    const { default: api } = await import("../api/client.js");
    await api.post("/api/v1/audit/clinical-access", {
      test_id: "__consent__",
      item_index: null,
      action: "revoke_verbatim_terms",
      timestamp: new Date().toISOString(),
    });
  } catch { /* offline OK */ }
}
