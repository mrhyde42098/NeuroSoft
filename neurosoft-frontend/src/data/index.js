/* ═══════════════════════════════════════════════════════════════════════
 * src/data/index.js — Punto único de acceso a constantes y datos clínicos
 * ───────────────────────────────────────────────────────────────────────
 * Este archivo es el "barrel" donde los nuevos módulos del frontend deben
 * importar las constantes clínicas. Hoy re-exporta lo que vive en
 * `src/clinicalData.js` y deja documentado qué constantes seguirán
 * migrando desde App.jsx en futuras sesiones (Fase A completa).
 *
 * Por qué no migramos todo en una sola sesión:
 *   - REACTIVOS, CONDUCTAS, NativeStimuli, INSTRUCCIONES son tablas de
 *     varios kilobytes con strings literales; un fallo al copiar romperia
 *     páginas críticas (EvalApply, Reactive Panel, screenings).
 *   - Mover requiere también actualizar 30+ referencias en App.jsx.
 *
 * Plan de migración recomendado para próxima sesión:
 *   1) Crear constants/clinical.js con OBS_TEMPLATES, SCREENING_FORMS,
 *      CONDUCTAS, GUIA_HC, GUIA_INFORME, REACTIVOS, INSTRUCCIONES.
 *   2) Crear constants/ui.js con SHORTCUTS, DISCREPANCY_PAIRS,
 *      REPORT_TEMPLATES, CONSENT_LABELS.
 *   3) Crear constants/stimuli.js con NativeStimuli + helpers gráficos.
 *   4) En App.jsx, reemplazar cada `const X = …` por `import { X } from
 *      "./data/constants/…"` validando cada cambio con `vite build`.
 * ═══════════════════════════════════════════════════════════════════════ */

export {
  RECOMMENDATIONS_LIB,
  DIAGNOSTIC_ALGORITHMS,
  DSM5_DIAGNOSES,
  PROTOCOL_SUGGESTIONS,
  CUADROS_CLINICOS,
  INCONCLUSO_REASONS,
  protocoloPorEdad,
  evaluarAlgoritmo,
} from "./datosClinicos.js";

/* ─── Catálogo de dominios cognitivos (compartido por Rehab + Eval) ─ */
export const COGNITIVE_DOMAINS = [
  { id: "atencion",                 label: "Atención" },
  { id: "memoria",                  label: "Memoria" },
  { id: "memoria_trabajo",          label: "Memoria de trabajo" },
  { id: "funciones_ejecutivas",     label: "Funciones ejecutivas" },
  { id: "lenguaje",                 label: "Lenguaje" },
  { id: "visoespacial",             label: "Visoespacial" },
  { id: "velocidad_procesamiento",  label: "Velocidad de procesamiento" },
];

export const DOMAIN_COLORS = {
  atencion:                "#6366f1",
  memoria:                 "#0d9488",
  memoria_trabajo:         "#0891b2",
  funciones_ejecutivas:    "#ec4899",
  lenguaje:                "#d97706",
  visoespacial:            "#7c3aed",
  velocidad_procesamiento: "#dc2626",
};
