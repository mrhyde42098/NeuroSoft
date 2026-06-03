/* ═══════════════════════════════════════════════════════════════════════
 * src/data/casosSimulador.js
 * ───────────────────────────────────────────────────────────────────────
 * Casos clínicos para el simulador educativo (módulo Aprender).
 *
 * Cada caso presenta al estudiante:
 *   1. Datos sociodemográficos + Motivo de consulta
 *   2. Antecedentes relevantes
 *   3. Observación clínica del momento de evaluación
 *   4. Tabla de PDs + escalares (REALES, derivados del motor NeuroSoft)
 *
 * El estudiante debe:
 *   a) Identificar perfil cognitivo dominante (3-4 dominios débiles/fuertes)
 *   b) Proponer impresión diagnóstica DSM-5 + CIE-10
 *   c) Sugerir batería complementaria si corresponde
 *
 * Después puede ver "Interpretación experta" con análisis paso a paso.
 *
 * Casos basados en los 15 ground-truth (anonimizados, ya validados con motor).
 * ═══════════════════════════════════════════════════════════════════════ */

export const CASOS_SIMULADOR = [
  {
    id: "sim_tdah_inf",
    titulo: "Niño 8 años — bajo rendimiento escolar",
    dificultad: "facil",
    poblacion: "infantil",
    sociodemograficos: {
      edad: "8 años 4 meses", sexo: "Masculino", escolaridad: "Primaria",
      remitido_por: "Docente de aula",
    },
    motivo_consulta: "La docente reporta que el niño 'no presta atención en clase, se distrae con cualquier cosa, no termina las tareas, interrumpe a compañeros'. Los padres confirman conductas similares en casa: 'pierde sus cosas, olvida instrucciones, salta de una actividad a otra sin terminarlas'. Inicio: desde preescolar (5 años).",
    antecedentes: [
      "Embarazo y parto sin complicaciones. Lactancia materna exclusiva 6m.",
      "Hitos motores y de lenguaje dentro de lo esperado.",
      "Inicio escolar a los 5a sin adaptación dificultosa.",
      "Sin antecedentes médicos relevantes. Sin medicación actual.",
      "Padre con diagnóstico de TDAH inatento (adulto).",
      "Hermano mayor sano.",
    ],
    observacion: "Niño colaborador y socialmente apropiado. Latencia de respuesta normal. Durante las pruebas se levanta varias veces, juega con lápices, mira ventana. Necesita 3-4 redirecciones por subtest. Frustra fácilmente con tareas largas. Esfuerzo aparente preservado pero con fatiga atencional notoria a los 30 min.",
    perfil: {
      protocolo: "WISC-IV",
      escalares: [
        { test: "NiWiscDC", nombre: "Diseño con Cubos", dominio: "Razonamiento Perceptual", pd: 30, escalar: 12, interp: "Promedio alto" },
        { test: "NiWiscSem", nombre: "Semejanzas", dominio: "Comprensión Verbal", pd: 18, escalar: 12, interp: "Promedio alto" },
        { test: "NiWiscRDD", nombre: "Retención de Dígitos", dominio: "Memoria de Trabajo", pd: 11, escalar: 7, interp: "Promedio bajo" },
        { test: "NiWiscCl", nombre: "Claves", dominio: "Velocidad de Procesamiento", pd: 22, escalar: 6, interp: "Bajo" },
        { test: "NiWiscVoc", nombre: "Vocabulario", dominio: "Comprensión Verbal", pd: 30, escalar: 13, interp: "Promedio alto" },
        { test: "NiWiscLN", nombre: "Letras y Números", dominio: "Memoria de Trabajo", pd: 11, escalar: 8, interp: "Promedio bajo" },
        { test: "NiWiscMat", nombre: "Matrices", dominio: "Razonamiento Perceptual", pd: 17, escalar: 11, interp: "Promedio" },
        { test: "NiWiscCom", nombre: "Comprensión", dominio: "Comprensión Verbal", pd: 18, escalar: 11, interp: "Promedio" },
        { test: "NiWiscBusSim", nombre: "Búsqueda de Símbolos", dominio: "Velocidad de Procesamiento", pd: 10, escalar: 5, interp: "Bajo" },
        { test: "NiWiscAri", nombre: "Aritmética", dominio: "Memoria de Trabajo", pd: 14, escalar: 9, interp: "Promedio" },
      ],
      indices: [
        { id: "ICV", suma: 36, ci: 113, interp: "Promedio alto" },
        { id: "IRP", suma: 23, ci: 107, interp: "Promedio" },
        { id: "IMT", suma: 15, ci: 86, interp: "Promedio bajo" },
        { id: "IVP", suma: 11, ci: 73, interp: "Bajo" },
        { id: "CIT", suma: 85, ci: 97, interp: "Promedio" },
        { id: "ICG", ci: 110, interp: "Promedio alto" },
      ],
    },
    interpretacion_experta: {
      perfil_dominante:
        "Perfil disarmónico con FORTALEZAS en razonamiento verbal (ICV=113) y perceptual " +
        "(IRP=107), y DEBILIDADES marcadas en memoria de trabajo (IMT=86) y, especialmente, " +
        "velocidad de procesamiento (IVP=73 — Bajo). Discrepancia ICV-IVP=40 puntos: " +
        "significativa al 1%, infrecuente en población general.",
      hipotesis:
        "El patrón cognitivo es altamente sugestivo de TDAH presentación inatenta o combinada. " +
        "El IVP bajo refleja distractibilidad durante tareas que requieren atención sostenida " +
        "y velocidad. El IMT bajo refleja dificultad para mantener información activa. El ICG " +
        "(110, Promedio alto) representa mejor la capacidad intelectual real que el CIT " +
        "(97, Promedio), porque IMT/IVP están aplanando el promedio.",
      diagnostico_propuesto:
        "Compatible con Trastorno por Déficit de Atención e Hiperactividad, presentación " +
        "predominantemente inatenta o combinada (CIE-10: F90.0 / DSM-5: 314.00 o 314.01). " +
        "Diagnóstico definitivo requiere: (a) entrevista diagnóstica DSM-5 estructurada con " +
        "padres y docente, (b) descarte de comorbilidades (ansiedad, dislexia), (c) confirmación " +
        "de inicio de síntomas antes de los 12 años, (d) interferencia clínicamente " +
        "significativa en ≥2 contextos.",
      bateria_complementaria: [
        "SNAP-IV (padres + docente) para validación dimensional",
        "VANDERBILT (padres + docente) — útil por incluir tamizaje conducta + ansiedad",
        "CPT-3 (Continuous Performance Test) para confirmar perfil atencional",
        "Cuestionario WURS-25 (padres) si se sospecha persistencia familiar TDAH",
        "Despistaje dislexia: lectura/escritura con ENI-2",
      ],
      recomendaciones_clave: [
        "Reportar el ICG (110) como medida más representativa del potencial intelectual",
        "Recomendar evaluación psiquiátrica para descarte/confirmación DSM-5",
        "Iniciar adaptaciones escolares: instrucciones cortas, refuerzo positivo, recreos cognitivos",
        "Plan de intervención: CBT-TDAH adaptada + posible psicoestimulante (decisión psiquiatra)",
      ],
    },
    referencias_tecnicas: [
      "DSM-5 APA 2013 — Criterios TDAH",
      "Wechsler 2003 — WISC-IV Technical Manual",
      "Raiford et al. 2008 — ICG en WISC-IV",
      "Barkley 2015 — ADHD: Handbook for Diagnosis and Treatment",
    ],
  },
  {
    id: "sim_alzheimer_am",
    titulo: "Mujer 76 años — quejas de memoria progresivas",
    dificultad: "media",
    poblacion: "adulto_mayor",
    sociodemograficos: {
      edad: "76 años 9 meses", sexo: "Femenino", escolaridad: "Primaria Incompleta",
      remitido_por: "Médico geriatra",
    },
    motivo_consulta: "La paciente acude acompañada por hija. La hija refiere 'desde hace 1.5 años está más olvidadiza, repite preguntas, se le quema la comida, se desorienta en el barrio que conoce de toda su vida'. La paciente niega o minimiza: 'son cosas normales de la edad'. Familia preocupada por seguridad: 'el mes pasado dejó el gas abierto'.",
    antecedentes: [
      "HTA controlada con losartán. DM2 con metformina.",
      "Histerectomía hace 30 años. Sin otras cirugías relevantes.",
      "Sin antecedente vascular cerebral. RM cerebral reciente: atrofia hipocampal bilateral leve.",
      "Madre falleció con 'olvido senil' a los 82a.",
      "Viuda desde hace 10a. Vive sola hasta hace 6 meses, ahora con hija mayor.",
      "Pensionada como modista. Católica practicante. Funcionalmente activa hasta hace 2a.",
    ],
    observacion: "Mujer aliñada, orientada en persona pero desorientada parcialmente en tiempo (dice estar en 2015). Latencia de respuesta aumentada. Anosognosia: niega olvidos cuando se le señalan ejemplos concretos. Comportamiento social preservado, lenguaje conservado en superficie pero con anomias (busca palabras). Praxias preservadas. Sin alteraciones afectivas evidentes.",
    perfil: {
      protocolo: "Adulto Mayor Neuronorma + Grober",
      escalares: [
        { test: "ViRDD", nombre: "Dígitos Directos", dominio: "Atención", pd: 3, escalar: 7, interp: "Promedio bajo" },
        { test: "ViTMTA", nombre: "TMT-A", dominio: "Atención + velocidad", pd: 280, escalar: 5, interp: "Bajo" },
        { test: "ViGroberRLT", nombre: "Grober — Recuerdo Libre Total", dominio: "Memoria verbal codificación", pd: 4, escalar: 3, interp: "Bajo" },
        { test: "ViGroberML_Tot", nombre: "Grober — Recobro Libre Diferido", dominio: "Memoria verbal recobro", pd: 1, escalar: 2, interp: "Muy bajo" },
        { test: "ViGroberMC_Tot", nombre: "Grober — Recobro con Claves", dominio: "Memoria verbal con apoyo", pd: 3, escalar: 3, interp: "Bajo (no rescata con claves)" },
        { test: "ViFCROCo", nombre: "Figura Rey — Copia", dominio: "Visoconstrucción", pd: 18, escalar: 4, interp: "Bajo" },
        { test: "ViFCRORec", nombre: "Figura Rey — Recobro", dominio: "Memoria visual", pd: 2, escalar: 2, interp: "Muy bajo" },
        { test: "ViP", nombre: "Fluidez Fonémica P", dominio: "Lenguaje + EF", pd: 5, escalar: 4, interp: "Bajo" },
        { test: "ViAni", nombre: "Fluidez Semántica Animales", dominio: "Lenguaje", pd: 8, escalar: 5, interp: "Bajo" },
        { test: "ViYesavage", nombre: "GDS-15", dominio: "Escala afectiva", pd: 4, escalar: "Normal", interp: "Sin depresión" },
      ],
    },
    interpretacion_experta: {
      perfil_dominante:
        "Patrón **cortical posterior** clásico de Alzheimer probable:\n" +
        "1. MEMORIA EPISÓDICA SEVERAMENTE COMPROMETIDA — Grober muestra déficit tanto en " +
        "codificación (RLT=4 PD bajo) como, críticamente, en almacén/recobro: las claves " +
        "semánticas NO rescatan información (MC_Tot escalar 3, sin mejora respecto a libre). " +
        "Este patrón sugiere fallo de CONSOLIDACIÓN, no solo de recobro.\n" +
        "2. VISOCONSTRUCCIÓN ALTERADA — FCRO copia bajo (escalar 4), con compromiso adicional " +
        "del recobro visual.\n" +
        "3. LENGUAJE con compromiso de fluidez (especialmente fonémica), sin afasia franca.\n" +
        "4. ATENCIÓN básica relativamente preservada (RDD=7) con velocidad ya afectada.\n" +
        "5. SIN sintomatología depresiva (GDS=4) → descarta pseudodemencia.\n" +
        "6. ANOSOGNOSIA + RM con atrofia hipocampal son hallazgos congruentes.",
      hipotesis:
        "Trastorno Neurocognitivo Mayor por probable Enfermedad de Alzheimer, severidad " +
        "leve-moderada. Diferencial principal con DCL ya superado: hay afectación funcional " +
        "(seguridad en casa comprometida), múltiples dominios alterados y anosognosia.",
      diagnostico_propuesto:
        "Trastorno Neurocognitivo Mayor debido a probable Enfermedad de Alzheimer, severidad " +
        "moderada (CIE-10: F00.1 — Demencia en enfermedad de Alzheimer de inicio tardío / " +
        "DSM-5: 294.10).\n\n" +
        "Cumple criterios NIA-AA 2011 para Alzheimer probable:\n" +
        "- Cumple criterios de demencia (déficit en ≥2 dominios + funcional)\n" +
        "- Inicio insidioso y progresión gradual (1.5a)\n" +
        "- Patrón amnésico típico (déficit episódico + falta de respuesta a claves)\n" +
        "- Atrofia hipocampal en RM concuerda con patrón\n" +
        "- Sin evidencia de otra etiología que mejor explique",
      bateria_complementaria: [
        "Confirmar funcionalidad: Escala Lawton & Brody (IADL) y Barthel (ABVD)",
        "Cuantificar carga del cuidador: Zarit-7 a hija acompañante",
        "Evaluar síntomas neuropsiquiátricos: NPI-Q al cuidador",
        "Solicitar perfil de marcadores LCR (Aβ42, p-tau) si se busca confirmación etiológica",
        "Repetir evaluación neuropsico a 12 meses para documentar progresión (RCI si baremos disponibles)",
      ],
      recomendaciones_clave: [
        "Derivar a Geriatría para inicio de inhibidor colinesterasa (donepezilo)",
        "Plan de seguridad domiciliaria: alarmas gas, supervisión cocina, llaves codificadas",
        "Documentos legales (testamento, poderes) en estado actual antes de deterioro mayor",
        "Apoyo familiar y educación cuidador: cursos para familiares Alzheimer (Fundación Acción Familiar Alzheimer Colombia)",
        "Estimulación cognitiva grupal en centro día",
      ],
    },
    referencias_tecnicas: [
      "McKhann et al. 2011 — Criterios NIA-AA para Alzheimer",
      "Petersen 2004 — Diferencial DCL vs demencia",
      "Arango-Lasprilla & Rivera 2017 — Neuronorma Colombia",
      "Grober & Buschke 1987 — Lista de palabras con claves",
      "Wells 1979 — Pseudodemencia depresiva",
    ],
  },
  {
    id: "sim_depresion_adu",
    titulo: "Mujer 28 años — bajo ánimo postparto",
    dificultad: "media",
    poblacion: "adulto_joven",
    sociodemograficos: {
      edad: "28 años", sexo: "Femenino", escolaridad: "Universitaria",
      remitido_por: "Médica de familia",
    },
    motivo_consulta: "La paciente acude por iniciativa propia tras consulta médica. 'Hace 6 meses tuve a mi bebé. Pensé que iba a ser feliz y al contrario, me siento vacía, lloro todos los días, no disfruto nada, me siento culpable porque mi bebé está bien pero yo no puedo conectar con ella. A veces pienso que sería mejor desaparecer'. Niega plan suicida actual pero presenta ideación pasiva.",
    antecedentes: [
      "Embarazo planeado, sin complicaciones. Parto eutócico a término. Bebé sana.",
      "Antecedente personal: 1 episodio depresivo a los 19a tratado con CBT (recuperación completa).",
      "Antecedente familiar: madre con depresión recurrente.",
      "Vive con esposo (relación funcional). Sin red familiar amplia.",
      "Licencia maternidad termina en 2 semanas. Trabajo previo: ingeniera, alto rendimiento.",
      "Sin consumo de alcohol/sustancias. No medicación actual.",
    ],
    observacion: "Mujer aliñada con discreta descuido en presentación. Latencia de respuesta levemente aumentada. Afecto deprimido con ánimo congruente. Lentificación psicomotora leve. Discurso enlentecido, coherente. Insight conservado. Esfuerzo cooperativo, llanto controlado durante 2 momentos de la evaluación.",
    perfil: {
      protocolo: "Adulto Joven + Escalas afectivas",
      escalares: [
        { test: "PHQ-9", nombre: "PHQ-9", dominio: "Escala depresión", pd: 18, escalar: "Mod-Severa", interp: "Depresión moderadamente severa" },
        { test: "GAD-7", nombre: "GAD-7", dominio: "Escala ansiedad", pd: 10, escalar: "Moderada", interp: "Ansiedad moderada (comorbilidad)" },
        { test: "C-SSRS", nombre: "Riesgo suicida", dominio: "Riesgo", pd: 2, escalar: "Leve", interp: "Ideación pasiva, sin plan, sin intento previo" },
        { test: "AdWAISV", nombre: "Vocabulario WAIS-III", dominio: "Comprensión Verbal", pd: 48, escalar: 12, interp: "Promedio alto" },
        { test: "AdMatr", nombre: "Matrices WAIS-III", dominio: "Razonamiento Perceptual", pd: 21, escalar: 11, interp: "Promedio" },
        { test: "AdSDWais", nombre: "Símbolo-Dígito WAIS-III", dominio: "Velocidad Procesamiento", pd: 70, escalar: 8, interp: "Promedio bajo (lentificación)" },
        { test: "AdTMT_AB", nombre: "TMT A+B", dominio: "Atención + EF", pd: "A=45, B=95", escalar: "Z(A)=-0.8, Z(B)=-0.6", interp: "Levemente bajo (esperable en depresión)" },
      ],
    },
    interpretacion_experta: {
      perfil_dominante:
        "Perfil cognitivo COMPATIBLE con depresión postparto activa, sin déficit cognitivo " +
        "primario:\n" +
        "1. PHQ-9 = 18 (mod-severa) + GAD-7 = 10 (ansiedad comorbida) — patrón típico " +
        "depresivo postparto.\n" +
        "2. C-SSRS positivo en ideación pasiva: REQUIERE PLAN DE SEGURIDAD documentado.\n" +
        "3. Razonamiento intelectual PRESERVADO (Vocabulario=12, Matrices=11): no hay " +
        "deterioro cognitivo de fondo.\n" +
        "4. Lentificación cognitiva (SDMT=8, Z TMT-A=-0.8): expresión cognitiva del " +
        "embotamiento depresivo, ESPERABLE y REVERSIBLE con tratamiento.",
      hipotesis:
        "Trastorno Depresivo Mayor con inicio en posparto, episodio actual moderado-severo, " +
        "con ansiedad comórbida y riesgo suicida leve. Vulnerabilidad clara: episodio depresivo " +
        "previo + antecedente familiar materno. Factor precipitante: parto + cambio de rol + " +
        "aislamiento social. La cognición lentificada NO es deterioro: es expresión del cuadro " +
        "afectivo.",
      diagnostico_propuesto:
        "Trastorno Depresivo Mayor, episodio recurrente, severidad moderada, con inicio en " +
        "el periparto (CIE-10: F32.1 + F53.0 / DSM-5: 296.32 con especificador 'con inicio " +
        "en el periparto').\n\n" +
        "Comorbilidad: características ansiosas concurrentes.\n" +
        "Riesgo suicida: leve (ideación pasiva, sin plan, sin intento previo) — requiere plan " +
        "de seguridad activo y monitorización semanal.",
      bateria_complementaria: [
        "Escala de Depresión Postparto de Edimburgo (EPDS) — específica del cuadro",
        "Cuestionario de Apego Materno (MAQ) — evaluar conexión con bebé",
        "Re-evaluar C-SSRS en cada sesión por las primeras 4 semanas",
        "Si lentificación persiste tras remisión del cuadro afectivo: reevaluación neuropsico " +
          "completa (descartar componente endocrino — TSH, B12, folato)",
      ],
      recomendaciones_clave: [
        "DERIVACIÓN URGENTE a Psiquiatría: considerar antidepresivo compatible con lactancia " +
          "(sertralina es 1ª línea, evidencia en lactancia)",
        "Iniciar CBT-Postparto inmediatamente (Tarrier, Sockol — manuales validados)",
        "Activación conductual: 15 min actividad placentera diaria con bebé + sin bebé",
        "Plan de seguridad por escrito + acceso a línea de crisis (Línea 192 opc 4)",
        "Sesiones psicoeducativas a esposo: depresión postparto es enfermedad tratable, NO " +
          "es 'mala madre'",
        "Apoyo de red: grupos madres lactantes, terapia grupal de postparto si disponible",
      ],
    },
    referencias_tecnicas: [
      "DSM-5 APA 2013 — Especificador 'con inicio en el periparto'",
      "Cox et al. 1987 — EPDS",
      "Sockol 2018 — CBT postparto, meta-análisis d=0.65",
      "Posner et al. 2011 — C-SSRS",
      "Bauer et al. 2014 — Lactancia y antidepresivos",
    ],
  },
];

export const CATEGORIAS_SIMULADOR = [...new Set(CASOS_SIMULADOR.map(c => c.poblacion))].sort();
