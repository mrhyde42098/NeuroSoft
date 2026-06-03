/* ═══════════════════════════════════════════════════════════════════════
 * src/data/neuronormaColombia.js
 * ───────────────────────────────────────────────────────────────────────
 * Catálogo de pruebas con datos normativos COLOMBIANOS publicados en:
 *
 *   Arango-Lasprilla, J. C., & Rivera, D. (Eds.). (2017).
 *   "Neuropsicología en Colombia: Datos normativos, estado actual
 *    y retos a futuro".
 *
 * Este módulo NO contiene baremos numéricos (esos están en el backend en
 * BD_NEURO_MAESTRA.json). Solo metadatos clínicos que permiten:
 *   • Mostrar un badge "Norma colombiana disponible"
 *   • Citar la referencia bibliográfica en el informe
 *   • Documentar la variable de ajuste obligatoria (Edad + Escolaridad)
 *
 * Mapeo: clave = test_id (NeuroSoft) → metadata Neuronorma.
 * ═══════════════════════════════════════════════════════════════════════ */

export const NEURONORMA_COLOMBIA_REF = {
  cita: "Arango-Lasprilla, J. C., & Rivera, D. (Eds.). (2017). Neuropsicología en Colombia: Datos normativos, estado actual y retos a futuro.",
  citaCorta: "Arango-Lasprilla & Rivera, 2017",
  url: "https://www.researchgate.net/publication/315761461",
};

/* §nn-co: segunda referencia colombiana — Neuronorma Colombia (NN.Co)
 * de Patricia Montañés et al. (UNAL, 2020). Proyecto SEPARADO del libro
 * Arango-Lasprilla 2017. Mejor estratificación etaria para >50 años:
 * 10 grupos etarios (vs 2 del 2017) y regresión múltiple por escolaridad. */
export const NEURONORMA_COLOMBIA_NNCO_REF = {
  cita: "Espitia Mendieta, A. D., Duarte, S., & Montañés, P. et al. (2020). Neuronorma Colombia: protocolo, normas, plataforma. Universidad Nacional de Colombia.",
  citaCorta: "Montañés et al., 2020 (NN.Co)",
  url: "https://www.elsevier.es/en-revista-neurologia-english-edition--495-articulo-neuronorma-colombia-contributions-methodological-characteristics-S2173580823000627",
  poblacion: "Adultos 50-90 años (N=438), 10 grupos etarios × 3 niveles escolaridad",
  metodo: "Regresión múltiple por escolaridad: NNSAE = NSSA − (β × [Educación−11])",
  ventaja: "Estratificación etaria más fina para mayores de 75 años (el libro 2017 colapsa >77 en un único grupo).",
};

/**
 * Pruebas que cuentan con normas colombianas publicadas en el libro.
 *
 * Campos por entrada:
 *   - capitulo:        número de capítulo en el libro
 *   - dominio:         dominio cognitivo evaluado
 *   - ajuste:          variables de ajuste OBLIGATORIAS para la corrección
 *   - tipoPuntuacion:  "percentil" | "puntuacion_T" | "ambos"
 *   - estratosEdad:    rangos de edad usados en las tablas normativas
 *   - estratosEducacion: rangos de escolaridad (años de educación formal)
 *   - puntuaciones:    qué se debe registrar
 *   - tiempoLimite:    en segundos si aplica
 *   - notaClinica:     interpretación o regla relevante
 */
export const PRUEBAS_NEURONORMA_COLOMBIA = {
  // ── Capítulo III: Figura Compleja de Rey ──────────────────────────
  NiFCROCop: {
    nombre: "Figura Compleja de Rey-Osterrieth — Copia",
    capitulo: 3,
    dominio: "Habilidades visoconstructivas",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "percentil",
    estratosEdad: ["18-35", "36-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Copia (0-36)", "Tiempo de copia (s)"],
    notaClinica: "Mide praxis constructiva, planificación y organización visoespacial.",
  },
  NiFCRORec: {
    nombre: "Figura Compleja de Rey-Osterrieth — Memoria",
    capitulo: 3,
    dominio: "Memoria visual",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "percentil",
    estratosEdad: ["18-35", "36-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Memoria inmediata (0-36)", "Memoria diferida (0-36)"],
    notaClinica: "Sensible a daño en lóbulo temporal derecho y parietal.",
  },
  AdFCRO_Rey: {
    nombre: "Figura Compleja de Rey (adulto joven)",
    capitulo: 3,
    dominio: "Praxias / Memoria visual",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "percentil",
    estratosEdad: ["18-35", "36-55", "56-75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Copia (0-36)", "Recobro (0-36)"],
  },

  // ── Capítulo IV: Stroop ───────────────────────────────────────────
  NiSt_Edades: {
    nombre: "Stroop — Test de Colores y Palabras",
    capitulo: 4,
    dominio: "Atención selectiva e inhibición",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-35", "36-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Palabras (n)", "Colores (n)", "Palabra-Color (n)", "Interferencia"],
    tiempoLimite: 45,
    notaClinica: "Interferencia = PC − [(P × C) / (P + C)]. Mide control inhibitorio.",
  },
  AdStroop_Corr: {
    nombre: "Stroop — Adulto",
    capitulo: 4,
    dominio: "Función ejecutiva",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-35", "36-55", "56-75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["P", "C", "PC", "Interferencia"],
    tiempoLimite: 45,
  },
  StroopAM: {
    nombre: "Stroop — Adulto Mayor",
    capitulo: 4,
    dominio: "Función ejecutiva",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["P", "C", "PC"],
    tiempoLimite: 45,
  },

  // ── Capítulo V: M-WCST (Wisconsin Modificado) ─────────────────────
  ViWCat: {
    nombre: "M-WCST — Wisconsin Modificado",
    capitulo: 5,
    dominio: "Funciones ejecutivas / Flexibilidad cognitiva",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "ambos",
    estratosEdad: ["18-35", "36-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Categorías completadas (máx 6)", "Errores totales", "Errores perseverativos"],
    notaClinica: "Errores perseverativos = el indicador clínico más relevante.",
  },

  // ── Capítulo VI: TMT-A y TMT-B ────────────────────────────────────
  NiTMTA: {
    nombre: "TMT-A — Test del Trazo Parte A",
    capitulo: 6,
    dominio: "Atención sostenida / Velocidad visomotora",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Tiempo en segundos (máx 100)"],
    tiempoLimite: 100,
    notaClinica: "Mayor tiempo = peor rendimiento (puntuación inversa).",
  },
  NiTMTB: {
    nombre: "TMT-B — Test del Trazo Parte B",
    capitulo: 6,
    dominio: "Flexibilidad cognitiva / Atención alternante",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Tiempo en segundos (máx 300)"],
    tiempoLimite: 300,
  },
  AdTMTA: {
    nombre: "TMT-A (adulto)",
    capitulo: 6,
    dominio: "Atención",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-55", "56-75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    tiempoLimite: 100,
  },
  AdTMTB: {
    nombre: "TMT-B (adulto)",
    capitulo: 6,
    dominio: "Atención",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-55", "56-75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    tiempoLimite: 300,
  },

  // ── Capítulo VIII: Fluidez Verbal ────────────────────────────────
  FluidM: {
    nombre: "Fluidez Verbal Fonológica (F-A-S/M)",
    capitulo: 8,
    dominio: "Lenguaje / Funciones ejecutivas",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-35", "36-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Total palabras correctas (60 s)"],
    tiempoLimite: 60,
  },
  FluidP: {
    nombre: "Fluidez Verbal Fonológica (P)",
    capitulo: 8,
    dominio: "Lenguaje / Funciones ejecutivas",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    tiempoLimite: 60,
  },
  FluidAnim: {
    nombre: "Fluidez Verbal Semántica — Animales",
    capitulo: 8,
    dominio: "Lenguaje / Acceso léxico",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-35", "36-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Total animales correctos (60 s)"],
    tiempoLimite: 60,
  },
  FluidAnimales: {
    nombre: "Fluidez Semántica Animales",
    capitulo: 8,
    dominio: "Lenguaje",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
  },
  NiFA: {
    nombre: "Fluidez Semántica Animales (ENI)",
    capitulo: 8,
    dominio: "Lenguaje",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
  },
  NiFM: {
    nombre: "Fluidez Fonológica M (ENI)",
    capitulo: 8,
    dominio: "Lenguaje",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
  },

  // ── Capítulo IX: BNT (Boston Naming Test) ────────────────────────
  BNT: {
    nombre: "Boston Naming Test (BNT)",
    capitulo: 9,
    dominio: "Lenguaje / Denominación por confrontación visual",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "ambos",
    estratosEdad: ["18-35", "36-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Aciertos espontáneos (0-60)", "Con clave semántica", "Con clave fonológica"],
    notaClinica: "La denominación disminuye con la edad y aumenta con la escolaridad. Sensible a afasia anómica.",
  },
  Denom48: {
    nombre: "Denominación 48 ítems",
    capitulo: 9,
    dominio: "Lenguaje",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "ambos",
  },

  // ── Capítulo X: SDMT ──────────────────────────────────────────────
  SDMT: {
    nombre: "Símbolos y Dígitos (SDMT)",
    capitulo: 10,
    dominio: "Velocidad de procesamiento / Atención sostenida",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "puntuacion_T",
    estratosEdad: ["18-35", "36-55", "56-75", ">75"],
    estratosEducacion: ["1-5", "6-12", ">12"],
    puntuaciones: ["Oral (aciertos)", "Escrito (aciertos)"],
    tiempoLimite: 90,
  },

  // ── Capítulo XII: TOMM ────────────────────────────────────────────
  REY15: {
    nombre: "Rey 15-Item Test (validez de síntomas)",
    capitulo: 12,
    dominio: "Validez de síntomas / Detección de simulación",
    ajuste: ["edad", "escolaridad"],
    tipoPuntuacion: "percentil",
    puntuaciones: ["Total recordados (máx 15)", "Reconocimiento (opcional)"],
    notaClinica: "Punto de corte ≤9: sospecha de bajo esfuerzo (Rey 1964). Boone et al. (2002) sugiere combinar con reconocimiento.",
  },
};

/**
 * Retorna metadata si la prueba tiene normas colombianas, null si no.
 */
export function getNeuronormaInfo(testId) {
  if (!testId) return null;
  /* test_id puede venir con prefijos compuestos (ej. "AdBusSim + ViBusSim").
   * Tomamos solo la primera palabra antes del espacio o el "+". */
  const cleanId = String(testId).split(/[\s+]/)[0].trim();
  return PRUEBAS_NEURONORMA_COLOMBIA[cleanId] || PRUEBAS_NEURONORMA_COLOMBIA[testId] || null;
}

/* Listado por capítulo para uso en HelpPage. */
export const CAPITULOS_NEURONORMA = [
  { n: 3,  titulo: "Figura Compleja de Rey-Osterrieth",  pruebas: ["Copia", "Memoria inmediata", "Memoria diferida"] },
  { n: 4,  titulo: "Stroop — Colores y Palabras",         pruebas: ["Palabras", "Colores", "Palabra-Color", "Interferencia"] },
  { n: 5,  titulo: "M-WCST (Wisconsin Modificado)",       pruebas: ["Categorías", "Errores perseverativos", "Errores totales"] },
  { n: 6,  titulo: "Test del Trazo (TMT)",                pruebas: ["TMT-A (tiempo)", "TMT-B (tiempo)"] },
  { n: 7,  titulo: "BTA (Brief Test of Attention)",       pruebas: ["Total aciertos", "Índice de Atención"] },
  { n: 8,  titulo: "Fluidez Verbal",                       pruebas: ["FAS fonológica", "Animales semántica"] },
  { n: 9,  titulo: "Boston Naming Test (BNT)",            pruebas: ["Aciertos espontáneos", "Con clave"] },
  { n: 10, titulo: "SDMT (Símbolos y Dígitos)",           pruebas: ["Oral", "Escrito"] },
  { n: 11, titulo: "HVLT-R (Hopkins Verbal Learning)",    pruebas: ["Aprendizaje", "Recuerdo diferido", "Reconocimiento"] },
  { n: 12, titulo: "TOMM (validez de síntomas)",          pruebas: ["Ensayo I", "Ensayo II", "Retención"] },
];

/* Variables de ajuste: regla común a todas las pruebas del libro. */
export const REGLAS_AJUSTE = {
  titulo: "Variables de ajuste obligatorias",
  bullets: [
    "EDAD: variable continua, agrupada en estratos (18-35, 36-55, 56-75, >75).",
    "ESCOLARIDAD: años de educación formal (1-5, 6-12, >12).",
    "Ambas se aplican SIEMPRE en conjunto — no es válido ajustar solo por una.",
    "Las puntuaciones directas se transforman a percentil (y a T para algunas pruebas) usando regresión parcial.",
  ],
};
