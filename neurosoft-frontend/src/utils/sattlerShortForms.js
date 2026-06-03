/* ═══════════════════════════════════════════════════════════════════════
 * src/utils/sattlerShortForms.js — Formas cortas WISC-IV (Sattler 2010)
 * ───────────────────────────────────────────────────────────────────────
 * Cuando un niño tiene discapacidad sensorial o motora que impide
 * aplicar la batería completa del WISC-IV, aplica una FORMA CORTA
 * (Sattler 2010) y estima el CIT por tabla.
 *
 * • Forma Corta 1 (NO VERBAL): DC + CD + MT + FI
 * • Forma Corta 2 (VERBAL): VB + SE + CM + PC
 *
 * La tabla devuelve el CI estimado a partir de la suma de puntuaciones
 * escalares (4 subtests, rango 4-76).
 *
 * Origen: Sattler JM. Assessment of Children: Cognitive Foundations
 * (5th ed., 2010), p. 711.
 * ═══════════════════════════════════════════════════════════════════════ */

/* Tabla Sattler 2010 — ∑escalares (4..76) → CIT estimado.
 * Cada entrada: [forma1_NO_verbal_CIT, forma2_VERBAL_CIT].
 * Valores tomados de "Análisis de Formas Cortas WISC-IV (Sattler 2010)"
 * , V.1. */
export const SATTLER_SHORT_TABLE = {
 4: [42, 47], 5: [44, 48], 6: [45, 50], 7: [47, 51],
 8: [48, 53], 9: [50, 54], 10: [52, 56], 11: [53, 57],
 12: [55, 59], 13: [57, 60], 14: [58, 62], 15: [60, 63],
 16: [61, 64], 17: [63, 66], 18: [65, 67], 19: [66, 69],
 20: [68, 70], 21: [69, 72], 22: [71, 73], 23: [73, 75],
 24: [74, 76], 25: [76, 78], 26: [77, 79], 27: [79, 81],
 28: [81, 82], 29: [82, 84], 30: [84, 85], 31: [86, 87],
 32: [87, 88], 33: [89, 90], 34: [90, 91], 35: [92, 93],
 36: [94, 94], 37: [95, 96], 38: [97, 97], 39: [98, 99],
 40: [100,100], 41: [102,101], 42: [103,103], 43: [105,104],
 44: [106,106], 45: [108,107], 46: [110,109], 47: [111,110],
 48: [113,112], 49: [114,113], 50: [116,114], 51: [118,116],
 52: [119,117], 53: [121,119], 54: [123,120], 55: [124,121],
 56: [126,123], 57: [127,124], 58: [129,126], 59: [131,127],
 60: [132,129], 61: [134,130], 62: [135,131], 63: [137,133],
 64: [139,134], 65: [140,136], 66: [142,137], 67: [143,139],
 68: [145,140], 69: [147,141], 70: [148,143], 71: [150,144],
 72: [152,146], 73: [153,147], 74: [155,149], 75: [156,150],
 76: [158,151],
};

/* Calcula CIT estimado a partir de las puntuaciones escalares.
 * @param scaledSum: número entre 4 y 76 inclusive.
 * @param form: 1 (no verbal) o 2 (verbal).
 * @returns CIT estimado (entero) o null si fuera de rango.
 */
export function estimateCITFromShortForm(scaledSum, form = 1) {
 const idx = form === 1 ? 0 : 1;
 if (!Number.isFinite(scaledSum)) return null;
 const rounded = Math.round(scaledSum);
 if (rounded < 4 || rounded > 76) return null;
 const row = SATTLER_SHORT_TABLE[rounded];
 return row ? row[idx] : null;
}

/* Definición de cada forma corta */
export const SATTLER_FORMS = {
 1: {
 name: "Forma Corta 1 (No verbal)",
 abbr: "FC1",
 description: "Para discapacidad auditiva o evaluación con bajo apoyo verbal.",
 subtests: [
 { id: "NiWiscDC", label: "Diseño con Cubos (DC)" },
 { id: "NiWiscConD", label: "Conceptos con Dibujos (CD)" },
 { id: "NiWiscMat", label: "Matrices (MT)" },
 { id: "NiWisFigInc",label: "Figuras Incompletas (FI)" },
 ],
 ciIndex: "ICG aproximado (Razonamiento Perceptual + algo de Comprensión)",
 },
 2: {
 name: "Forma Corta 2 (Verbal)",
 abbr: "FC2",
 description: "Para discapacidad visual o evaluación con bajo apoyo visoespacial.",
 subtests: [
 { id: "NiWiscVoc", label: "Vocabulario (VB)" },
 { id: "NiWiscSem", label: "Semejanzas (SE)" },
 { id: "NiWiscCom", label: "Comprensión (CM)" },
 { id: "NiWisPalCon", label: "Palabras en Contexto (PC)" },
 ],
 ciIndex: "ICG aproximado (Comprensión Verbal + algo de razonamiento)",
 },
};

/* Catálogo de adaptaciones — qué forma corta o protocolo usar */
export const ADAPTATIONS = {
 estandar: {
 label: "Estándar",
 short: "Sin adaptaciones",
 description: "Aplicación completa del protocolo.",
 excludes: [],
 forma_corta: null,
 },
 hipoacusia: {
 label: "Hipoacusia / Discapacidad auditiva",
 short: "Sin pruebas verbales",
 description: "Excluir o adaptar con instrucciones escritas las pruebas que requieren input auditivo. CVLT con presentación visual cuando posible.",
 excludes: ["CVLTTotal" /* presentar visualmente */],
 forma_corta: 1,
 },
 ceguera: {
 label: "Discapacidad visual / Baja visión",
 short: "Sin pruebas visuales",
 description: "Excluir pruebas que requieren input visual (FCRO copia, TMT, Cubos, Matrices). Usar variantes orales (TMT-A/B oral, SDMT oral).",
 excludes: ["NiFCROCop", "NiFCRORec", "AdFCRORec", "NiTMTA", "NiTMTB", "AdTMTA", "AdTMTB", "NiWiscDC", "AdWAISCC", "NiWiscMat", "AdMatr", "NiWisFigInc", "AdWAISFI", "NiIntObj", "NiRecEmo", "NiFigHum", "SDMT", "AdSDWais"],
 forma_corta: 2,
 },
 visual_auditiva: {
 label: "Visual + auditiva",
 short: "Priorizar escalas",
 description: "Cuadro grave: priorizar escalas conductuales y evaluación cualitativa. CI no es viable.",
 excludes: ["NiWiscDC","NiWiscMat","NiWisFigInc","NiFCROCop","NiFCRORec","NiTMTA","NiTMTB","CVLTTotal","GBTotal","NiWiscSem","NiWiscVoc","NiWiscCom","NiWisPalCon"],
 forma_corta: null,
 },
 motora: {
 label: "Discapacidad motora",
 short: "Sin praxias ni velocidad",
 description: "Excluir FCRO, pruebas de trazo, claves, símbolos y velocidad. Adaptar a respuestas verbales.",
 excludes: ["NiFCROCop", "NiFCRORec", "AdFCRORec", "NiTMTA", "NiTMTB", "AdTMTA", "AdTMTB", "NiWiscCl", "AdSDWais", "NiWiscBusSim", "AdBusSim + ViBusSim", "SDMT", "NiWisReg", "NiCopTxt"],
 forma_corta: 2,
 },
 analfabeta: {
 label: "Analfabeta / sin escolarización",
 short: "Sin lectoescritura",
 description: "Usar HVLT en lugar de CVLT. TMT-A solo si reconoce números. Excluir pruebas de lectura/escritura.",
 excludes: ["CVLTTotal", "NiPrec", "NiLVS", "NiCopTxt", "NiRecEscrita", "NiCalcEscrito", "NiWiscRDD", "NiWisInf"],
 forma_corta: null,
 },
};
