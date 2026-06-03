/* ═══════════════════════════════════════════════════════════════════════
 * src/data/protocolosClinicos.js
 * ───────────────────────────────────────────────────────────────────────
 * §F3 — Protocolos clínicos y guías paso a paso para evaluación
 * neuropsicológica y psicoterapia.
 *
 * Cada protocolo incluye: pasos ordenados, instrumentos sugeridos,
 * criterios de avance, referencias bibliográficas y nivel de evidencia.
 *
 * Offline-friendly. Fuentes verificadas: APA, NICE, OMS, MinSalud Colombia.
 * ═══════════════════════════════════════════════════════════════════════ */

export const PROTOCOLOS = [
  // ══════════════════════════════════════════════════════════════
  // NEUROPSICOLOGÍA — EVALUACIÓN
  // ══════════════════════════════════════════════════════════════

  {
    id: "eval_tdah_infantil",
    nombre: "Evaluación para TDAH Infantil",
    area: "neuropsicologia_infantil",
    disciplina: "neuropsicologia",
    descripcion: "Protocolo estructurado para evaluación de TDAH en niños 6-16 años según criterios DSM-5 y guías NICE 2018.",
    nivel_evidencia: "A",
    tiempo_estimado_min: 180,
    pasos: [
      { orden: 1, titulo: "Entrevista clínica inicial",
        descripcion: "Anamnesis completa del desarrollo. Motivo de consulta: quién remite, qué observan padres y docentes, desde cuándo. Historia prenatal/perinatal, hitos del desarrollo, antecedentes familiares TDAH.",
        instrumentos: ["Entrevista semiestructurada padres", "Cuestionario desarrollo"],
        tiempo_min: 45 },
      { orden: 2, titulo: "Escalas de tamizaje",
        descripcion: "Aplicar SNAP-IV (padres + docente) y SCARED-41 (ansiedad) simultáneamente para diferencial TDAH vs ansiedad.",
        instrumentos: ["SNAP-IV", "SCARED-41", "VANDERBILT"],
        tiempo_min: 20 },
      { orden: 3, titulo: "Evaluación cognitiva WISC-IV",
        descripcion: "Aplicar batería WISC-IV completa. Prestar especial atención a IMT (memoria trabajo) y IVP (velocidad procesamiento) — típicamente bajos en TDAH.",
        instrumentos: ["WISC-IV (10 subtests principales)"],
        tiempo_min: 90 },
      { orden: 4, titulo: "Perfil ejecutivo",
        descripcion: "Evaluar inhibición (Stroop), flexibilidad (TMT-B, WCST) y atención sostenida (CPT si disponible).",
        instrumentos: ["Stroop", "TMT A+B", "WCST", "CPT (si disponible)"],
        tiempo_min: 30 },
      { orden: 5, titulo: "Integración y diagnóstico",
        descripcion: "Correlacionar hallazgos WISC + perfil ejecutivo + escalas padres/docente. Criterios DSM-5: ≥6 síntomas inatención/hiperactividad, inicio <12a, presentes en ≥2 contextos, interfieren funcionamiento.",
        instrumentos: ["DSM-5 criterios TDAH"],
        tiempo_min: 20 },
    ],
    referencias: ["ref-apa-2013", "NICE 2018 NG87", "Pliszka 2007 AACAP practice parameter"],
  },

  {
    id: "eval_dcl_demencia",
    nombre: "Evaluación para Deterioro Cognitivo y Demencia",
    area: "neuropsicologia_adulto_mayor",
    disciplina: "neuropsicologia",
    descripcion: "Protocolo para evaluación de queja cognitiva en adulto mayor. Diferencial: envejecimiento normal vs DCL vs demencia (Alzheimer, vascular, DFT, Lewy).",
    nivel_evidencia: "A",
    tiempo_estimado_min: 150,
    pasos: [
      { orden: 1, titulo: "Tamizaje cognitivo + estado ánimo",
        descripcion: "MMSE o MoCA + GDS-15 (Yesavage). Si MoCA <26 o Yesavage ≥10, profundizar.",
        instrumentos: ["MoCA", "GDS-15", "MMSE"],
        tiempo_min: 25 },
      { orden: 2, titulo: "Evaluación funcional",
        descripcion: "Lawton & Brody (actividades instrumentales) + Barthel (básicas). Determinar si hay pérdida funcional (criterio demencia) o preservación (DCL).",
        instrumentos: ["Lawton IADL", "Barthel ADL"],
        tiempo_min: 15 },
      { orden: 3, titulo: "Memoria episódica (prueba central)",
        descripcion: "Grober & Buschke completo: 3 ensayos codificación + recobro libre + recobro con claves + reconocimiento 20 min. Diferencial: déficit codificación (Alzheimer) vs déficit recobro (depresión).",
        instrumentos: ["Grober & Buschke"],
        tiempo_min: 30 },
      { orden: 4, titulo: "Perfil cognitivo completo",
        descripcion: "Atención (TMT-A, dígitos), funciones ejecutivas (TMT-B, Stroop, fluidez), lenguaje (denominación, fluidez semántica/fonémica), visoespacial (FCRO copia).",
        instrumentos: ["TMT A+B", "Stroop", "FCRO", "Fluidez verbal", "Denominación"],
        tiempo_min: 45 },
      { orden: 5, titulo: "Integración y clasificación",
        descripcion: "Clasificar según criterios NIA-AA 2011 (Alzheimer), NINDS-AIREN (vascular), Rascovsky 2011 (DFT). Nivel: DCL (funcionalidad preservada) vs Demencia mayor (pérdida funcional).",
        instrumentos: ["DSM-5 TNC", "Escala CDR", "NPI-Q (síntomas psicológicos)"],
        tiempo_min: 20 },
    ],
    referencias: ["McKhann et al. 2011 NIA-AA", "Petersen 2004 DCL criteria", "Grober & Buschke 1987"],
  },

  // ══════════════════════════════════════════════════════════════
  // PSICOLOGÍA CLÍNICA — TERAPIA
  // ══════════════════════════════════════════════════════════════

  {
    id: "terapia_cbt_depresion",
    nombre: "Protocolo CBT para Depresión",
    area: "psicoterapia",
    disciplina: "psicologia_clinica",
    descripcion: "Protocolo estructurado de Terapia Cognitivo-Conductual para Trastorno Depresivo Mayor según manual de Beck (1979, revisado 2011). 12-20 sesiones.",
    nivel_evidencia: "A",
    tiempo_estimado_min: 0,
    pasos: [
      { orden: 1, titulo: "Psicoeducación y modelo cognitivo",
        descripcion: "Explicar modelo cognitivo: pensamientos → emociones → conductas. Triada cognitiva depresiva: visión negativa de sí mismo, mundo y futuro. Establecer objetivos SMART.",
        sesiones: "1-2", tecnicas: ["Psicoeducación", "Registro diario pensamientos", "Escala BDI-II/PHQ-9 basal"] },
      { orden: 2, titulo: "Activación conductual",
        descripcion: "Programar actividades placenteras y de dominio. Romper ciclo: inactividad → bajo refuerzo → más depresión. Jerarquía desde lo más fácil.",
        sesiones: "2-4", tecnicas: ["Programación semanal actividades", "Escala dominio/placer 0-10"] },
      { orden: 3, titulo: "Identificación pensamientos automáticos",
        descripcion: "Capturar pensamientos automáticos ante situaciones activadoras. Registrar emoción asociada (0-100). Identificar distorsiones cognitivas (Beck: 10 distorsiones).",
        sesiones: "3-6", tecnicas: ["Registro ABC (Ellis)", "Flecha descendente", "Lista distorsiones"] },
      { orden: 4, titulo: "Reestructuración cognitiva",
        descripcion: "Cuestionar pensamientos disfuncionales con evidencia. Diálogo socrático. Generar pensamiento alternativo basado en evidencia. Re-atribución de auto-culpa.",
        sesiones: "5-10", tecnicas: ["Diálogo socrático", "Experimentos conductuales", "Gráfico pastel responsabilidad"] },
      { orden: 5, titulo: "Prevención de recaídas",
        descripcion: "Identificar señales tempranas (cambios sueño, aislamiento). Plan de acción escrito. Programar sesiones de refuerzo (booster: 1, 3, 6 meses post-alta).",
        sesiones: "10-12", tecnicas: ["Plan prevención recaídas", "Carta a uno mismo", "Sesiones booster"] },
    ],
    referencias: ["ref-beck-1979", "Beck 2011 CBT Basics", "Hofmann et al. 2012 meta-analysis (d=0.71)"],
  },

  {
    id: "intervencion_crisis_suicida",
    nombre: "Intervención en Crisis Suicida",
    area: "intervencion_crisis",
    disciplina: "psicologia_clinica",
    descripcion: "Protocolo de intervención inmediata ante ideación o intento suicida. Basado en C-SSRS + Plan de Seguridad (Stanley & Brown 2012) + PAP (OMS 2011).",
    nivel_evidencia: "A",
    tiempo_estimado_min: 90,
    pasos: [
      { orden: 1, titulo: "Evaluación de riesgo (C-SSRS)",
        descripcion: "Aplicar Columbia Suicide Severity Rating Scale. 6 preguntas escalonadas: deseo estar muerto → ideación activa → método → intención → plan → intentos previos.",
        instrumentos: ["C-SSRS"],
        tiempo_min: 15 },
      { orden: 2, titulo: "Clasificación nivel de riesgo",
        descripcion: "Bajo: ideación pasiva sin plan. Moderado: ideación activa con método. Alto: plan específico + medio disponible. Inminente: plan + intención ejecutarlo HOY.",
        instrumentos: ["C-SSRS + juicio clínico"],
        tiempo_min: 5 },
      { orden: 3, titulo: "Plan de seguridad (Stanley & Brown)",
        descripcion: "6 pasos escritos: (1) señales alarma, (2) estrategias internas, (3) contactos sociales, (4) contactos profesionales (líneas crisis: 106, 192-4), (5) restringir medios letales, (6) razones para vivir.",
        instrumentos: ["Plan de seguridad (formato físico)"],
        tiempo_min: 20 },
      { orden: 4, titulo: "Derivación según nivel",
        descripcion: "Bajo-moderado: seguimiento ambulatorio intensificado + contactar red apoyo. Alto-inminente: NO dejar solo, acompañar a urgencias psiquiátricas, activar red familiar, contactar psiquiatra.",
        instrumentos: ["Red de contactos", "Derivación a urgencias"],
        tiempo_min: 15 },
      { orden: 5, titulo: "Seguimiento 24-72h",
        descripcion: "Llamada o sesión de seguimiento en 24-72h. Re-evaluar C-SSRS. Ajustar plan según evolución. Coordinar con psiquiatra si medicación.",
        instrumentos: ["C-SSRS re-evaluación", "Coordinación interdisciplinaria"],
        tiempo_min: 20 },
    ],
    referencias: ["Stanley & Brown 2012", "ref-ley1090-2006", "OMS 2011 mhGAP"],
  },
];

export const AREAS_PROTOCOLOS = [
  { id: "neuropsicologia_infantil", label: "Neuropsicología Infantil" },
  { id: "neuropsicologia_adulto_mayor", label: "Neuropsicología Adulto Mayor" },
  { id: "psicoterapia", label: "Psicoterapia" },
  { id: "intervencion_crisis", label: "Intervención en Crisis" },
];
