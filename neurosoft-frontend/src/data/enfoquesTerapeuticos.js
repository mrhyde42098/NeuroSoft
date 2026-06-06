/* ═══════════════════════════════════════════════════════════════════════
 * src/data/enfoquesTerapeuticos.js
 * ───────────────────────────────────────────────────────────────────────
 * Catálogo curado de enfoques terapéuticos disponibles para el módulo
 * de Psicología Clínica de NeuroSoft App. Cada entrada contiene:
 *
 *   id                slug interno
 *   nombre            nombre clínico oficial
 *   sigla             abreviación común (CBT, EMDR, ACT...)
 *   categoria         "individual" | "pareja" | "familia" | "grupo" | "duelo"
 *                     | "trauma" | "ninos_adolescentes" | "adicciones"
 *   evidencia         "A" sólida | "B" moderada | "C" emergente | "tradicional"
 *   indicaciones      lista de condiciones donde es 1ª o 2ª línea
 *   no_indicado       contraindicaciones / cuando NO usar
 *   duracion_tipica   rango aproximado de sesiones
 *   estructura        bullets de fases típicas
 *   tecnicas_clave    técnicas características
 *   outcome_recomendadas  escalas para tracking pre/post (referencia
 *                         a SCREENING_FORMS o externos)
 *   referencias       autores fundacionales + manuales actuales
 *   recursos_es       URLs de materiales en español si existen
 *   notas             observaciones clínicas adicionales
 *
 * Curado con base en:
 *   - APA Division 12 (Society of Clinical Psychology) — Evidence-Based Therapies
 *   - NICE Guidelines (Reino Unido)
 *   - Cochrane Reviews recientes
 *   - SAMHSA Treatment Improvement Protocols
 *
 * Para AGREGAR enfoques nuevos: usar `/investigar-terapia <tema>` y
 * cuando se valide la literatura, anexar al array.
 * ═══════════════════════════════════════════════════════════════════════ */

/**
 * @typedef {Object} EnfoqueTerapeutico
 * @property {string} id
 * @property {string} nombre
 * @property {string} [sigla]
 * @property {string} categoria
 * @property {("A"|"B"|"C"|"tradicional")} evidencia
 * @property {string[]} indicaciones
 * @property {string[]} no_indicado
 * @property {string} duracion_tipica
 * @property {string[]} estructura
 * @property {string[]} tecnicas_clave
 * @property {string[]} outcome_recomendadas
 * @property {string[]} referencias
 * @property {string[]} [recursos_es]
 * @property {string} [notas]
 */

/** @type {EnfoqueTerapeutico[]} */
const _ENFOQUES_BASE = [
  /* ═══════ INDIVIDUAL — ADULTO ═══════ */
  {
    id: "cbt",
    nombre: "Terapia Cognitivo-Conductual",
    sigla: "CBT / TCC",
    categoria: "individual",
    evidencia: "A",
    indicaciones: [
      "Depresión mayor",
      "Trastornos de ansiedad (TAG, pánico, fobias)",
      "Insomnio (CBT-I)",
      "TOC (con ERP integrado)",
      "Dolor crónico",
      "Síntomas somáticos",
    ],
    no_indicado: [
      "Pacientes con baja capacidad de insight o muy concretos sin adaptación",
      "Crisis psicótica activa (estabilizar primero)",
    ],
    duracion_tipica: "12-20 sesiones",
    estructura: [
      "Psicoeducación + formulación cognitivo-conductual",
      "Identificación de pensamientos automáticos y distorsiones",
      "Reestructuración cognitiva",
      "Activación conductual / exposición según problema",
      "Prevención de recaídas",
    ],
    tecnicas_clave: [
      "Registro de pensamientos (3-7 columnas)",
      "Experimentos conductuales",
      "Programación de actividades placenteras",
      "Exposición gradual",
      "Modelo ABC (activadores-creencias-consecuencias)",
    ],
    outcome_recomendadas: ["PHQ-9", "BDI-II", "GAD-7", "BAI"],
    referencias: [
      "Beck, J. S. (2021). Cognitive Behavior Therapy: Basics and Beyond (3rd ed.).",
      "Padesky, C. A. (2020). The Clinician's Guide to CBT.",
      "Hofmann et al. (2012). Meta-analysis: d=0.61 para depresión vs control.",
    ],
    notas: "Primera línea para depresión y ansiedad en NICE, APA, Cochrane.",

    /* ─── §M-1 Contenido académico extendido ─── */
    descripcion_extendida:
      "La Terapia Cognitivo-Conductual (CBT/TCC) es el enfoque psicoterapéutico con más " +
      "evidencia empírica acumulada para una amplia variedad de trastornos. Parte del modelo " +
      "cognitivo de Aaron Beck (1960s) según el cual no son los eventos los que causan " +
      "malestar, sino la interpretación que hacemos de ellos. La intervención se centra en " +
      "identificar pensamientos automáticos disfuncionales, evaluarlos con evidencia y " +
      "modificar tanto creencias subyacentes como conductas de mantenimiento. Es una terapia " +
      "estructurada, colaborativa, orientada al presente y a metas concretas, con tareas " +
      "entre sesiones. Su flexibilidad ha permitido adaptaciones específicas (CBT-I para " +
      "insomnio, CBT-T para trauma, ERP para TOC, TF-CBT para trauma pediátrico).",
    efecto_tamano: {
      depresion: 0.71,
      ansiedad: 0.73,
      panico: 0.95,
      toc: 0.86,
      tag: 0.51,
      insomnio: 0.65,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Evaluación y formulación de caso",
        duracion_sesiones: "1-2",
        objetivos: [
          "Establecer alianza terapéutica",
          "Identificar problemas prioritarios",
          "Construir conceptualización cognitivo-conductual del caso",
        ],
        tareas_clinico: [
          "Aplicar PHQ-9 / BDI-II / GAD-7 según presentación",
          "Mapear pensamientos × emociones × conductas con cliente",
          "Establecer 2-3 metas SMART medibles para terapia",
        ],
        tareas_paciente: [
          "Registro inicial de pensamientos automáticos durante 7 días",
          "Lectura de psicoeducación: 'Qué es la CBT' (hoja entregada)",
        ],
        criterios_avance: "Cliente comprende modelo ABC y reconoce sus propios patrones.",
      },
      {
        fase: 2, nombre: "Psicoeducación e identificación de distorsiones",
        duracion_sesiones: "2-3",
        objetivos: [
          "Que el cliente identifique sus pensamientos automáticos en tiempo real",
          "Reconocer 5-6 distorsiones cognitivas frecuentes en su discurso",
        ],
        tareas_clinico: [
          "Enseñar el modelo de distorsiones cognitivas (catastrofización, etc.)",
          "Modelar identificación in vivo durante la sesión",
        ],
        tareas_paciente: [
          "Registro de pensamientos automáticos diario (3 columnas)",
          "Etiquetar cada pensamiento con su distorsión",
        ],
      },
      {
        fase: 3, nombre: "Reestructuración cognitiva activa",
        duracion_sesiones: "4-8",
        objetivos: [
          "Generar pensamientos alternativos basados en evidencia",
          "Probar creencias mediante experimentos conductuales",
        ],
        tareas_clinico: [
          "Cuestionamiento socrático en sesión",
          "Diseñar experimentos conductuales específicos",
          "Trabajar creencias intermedias y nucleares cuando aparezcan",
        ],
        tareas_paciente: [
          "Registro de pensamientos de 7 columnas (Beck completo)",
          "Ejecutar 1-2 experimentos conductuales/semana",
        ],
      },
      {
        fase: 4, nombre: "Activación conductual y exposición",
        duracion_sesiones: "3-6",
        objetivos: [
          "Reducir evitación experiencial y conductual",
          "Restaurar rutina + actividades placenteras",
        ],
        tareas_clinico: [
          "Jerarquía de exposición (si ansiedad/fobia/TOC)",
          "Programación de actividades placenteras y de logro",
          "Trabajar inercia / anhedonia conductualmente",
        ],
        tareas_paciente: [
          "Registro diario de actividades + nivel de placer/logro (0-10)",
          "Exposiciones in vivo según jerarquía pactada",
        ],
      },
      {
        fase: 5, nombre: "Prevención de recaídas y cierre",
        duracion_sesiones: "2-3",
        objetivos: [
          "Consolidar aprendizajes y atribuírselos al cliente",
          "Plan de prevención de recaída por escrito",
        ],
        tareas_clinico: [
          "Revisar metas iniciales vs avances",
          "Co-construir 'plan de bienestar' por escrito (señales de alarma + qué hacer)",
          "Espaciar sesiones (quincenal → mensual → booster)",
        ],
        tareas_paciente: [
          "Resumir aprendizajes en una hoja (libreta CBT)",
          "Identificar 3 'señales tempranas' de recaída personales",
        ],
        criterios_avance: "Reducción ≥50% en PHQ-9/GAD-7 + estrategias autoaplicables.",
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Registro de pensamientos automáticos (3 columnas)",
        descripcion: "Herramienta central de la CBT. El cliente registra: (1) situación disparadora, (2) pensamiento automático que apareció, (3) emoción + intensidad 0-100.",
        cuando_usar: "Desde la 2ª-3ª sesión, cuando el cliente ya entiende el modelo ABC. Tarea entre sesiones obligatoria durante las primeras 4-6 semanas.",
        ejemplo_dialogo:
          "T: Cuéntame el momento más difícil de esta semana.\n" +
          "C: Mi jefe me ignoró en una reunión y sentí que iba a explotar.\n" +
          "T: ¿Qué pasó por tu cabeza en ese momento, antes de la emoción?\n" +
          "C: 'Soy invisible, mi trabajo no vale nada.'\n" +
          "T: Genial, ese es el pensamiento automático. ¿Cuánto creíste eso en el momento, 0-100?\n" +
          "C: Como 90.\n" +
          "T: ¿Y qué emoción + qué intensidad?\n" +
          "C: Tristeza 85, frustración 70.",
        ejercicio_casa: "Registrar al menos 3 pensamientos automáticos al día durante 7 días.",
      },
      {
        nombre: "Cuestionamiento socrático",
        descripcion: "Sucesión guiada de preguntas que ayudan al cliente a evaluar el sustento de sus pensamientos, sin que el terapeuta los contradiga directamente.",
        cuando_usar: "Cuando aparecen pensamientos automáticos en sesión y queremos modelar su análisis.",
        ejemplo_dialogo:
          "T: '¿Qué evidencia tienes de que tu jefe te ignora a propósito?'\n" +
          "C: 'Bueno... solo esa reunión.'\n" +
          "T: '¿Y evidencia en contra?'\n" +
          "C: 'Ayer me felicitó por el informe.'\n" +
          "T: '¿Hay otra forma de leer la situación de la reunión?'\n" +
          "C: 'Quizá estaba estresado por el cliente que tenía después.'",
        ejercicio_casa: "Identificar 1 pensamiento esta semana y aplicar las 5 preguntas socráticas estándar (evidencia a favor, en contra, alternativa, peor escenario, qué le diría a un amigo).",
      },
      {
        nombre: "Experimento conductual",
        descripcion: "Prueba empírica diseñada para verificar (o refutar) una creencia mediante una acción concreta del cliente entre sesiones.",
        cuando_usar: "Cuando hay una creencia fuerte resistente al análisis verbal (ej. 'si me equivoco frente a mi equipo, todos me criticarán').",
        ejemplo_dialogo:
          "T: '¿Qué tan probable es que te critiquen si presentas con un error pequeño? 0-100?'\n" +
          "C: '95.'\n" +
          "T: 'Hagamos una prueba esta semana. ¿Puedes presentar el reporte introduciendo un pequeño matiz incierto y observar qué pasa?'\n" +
          "C: 'Vale, lo intento.' (Sesión siguiente): 'Nadie dijo nada. Una persona incluso me agradeció.'\n" +
          "T: 'Entonces, ¿con qué credibilidad sale la creencia ahora?'\n" +
          "C: '60.'",
        ejercicio_casa: "Diseñar y ejecutar 1 experimento conductual a la semana. Registrar resultado vs predicción inicial.",
      },
      {
        nombre: "Activación conductual",
        descripcion: "Programación deliberada de actividades placenteras y de logro para romper el ciclo depresivo de inactividad-rumiación.",
        cuando_usar: "Depresión moderada-severa con anhedonia y aislamiento marcado.",
        ejemplo_dialogo:
          "T: 'Vamos a planear actividades concretas para mañana. Pequeñas, alcanzables. ¿Qué te daba placer antes?'\n" +
          "C: 'Caminar en el parque, pero no tengo ganas.'\n" +
          "T: 'Exacto, ese es el truco: la motivación viene después de la acción, no antes. ¿Te comprometes a caminar 10 minutos mañana a las 5pm?'",
        ejercicio_casa: "Programar 1 actividad placentera y 1 actividad de logro cada día. Rating P (placer) y L (logro) de 0-10 al terminar.",
      },
      {
        nombre: "Exposición jerárquica (gradual)",
        descripcion: "Confrontación sistemática y voluntaria con estímulos evitados, ordenados por nivel de ansiedad esperado.",
        cuando_usar: "Trastornos de ansiedad (fobias, pánico/agorafobia, TAG con evitación), TOC (con ERP).",
        ejemplo_dialogo:
          "T: 'Hagamos juntos una lista de situaciones que evitas, de 0 a 100 según ansiedad esperada.'\n" +
          "(Construcción de jerarquía)\n" +
          "T: 'Vamos a empezar con la situación que te da 30. Tomar el ascensor 1 piso, esta semana, 3 veces.'",
        ejercicio_casa: "Ejecutar el ítem actual de la jerarquía 3-5 veces hasta que la ansiedad baje a la mitad, antes de pasar al siguiente.",
      },
    ],
    videos: [
      {
        titulo: "Aaron Beck — What Is Cognitive Therapy? (Beck Institute)",
        url_youtube: "https://www.youtube.com/embed/u7p25j5SXyA",
        autor: "Beck Institute for Cognitive Behavior Therapy",
        duracion: "6:13",
        idioma: "en",
        descripcion: "El creador de la CBT explica en primera persona las bases del modelo cognitivo.",
      },
      {
        titulo: "Judith Beck — Cognitive Conceptualization Diagram",
        url_youtube: "https://www.youtube.com/embed/3Mq5LFCmHmI",
        autor: "Beck Institute",
        duracion: "9:24",
        idioma: "en",
        descripcion: "Cómo formular un caso usando el diagrama cognitivo de conceptualización.",
      },
      {
        titulo: "Terapia Cognitivo-Conductual explicada en español",
        url_youtube: "https://www.youtube.com/embed/uMu3rfh3aUw",
        autor: "Pildoritas Psicológicas",
        duracion: "12:45",
        idioma: "es",
        descripcion: "Introducción didáctica a la CBT para hispanohablantes.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Cognitive Behavior Therapy: Basics and Beyond (3rd ed.)", autor: "Beck, J. S.", anio: 2021, edicion: 3, isbn: "978-1462544196" },
      { tipo: "libro", titulo: "The Clinician's Guide to CBT Using Mind Over Mood (2nd ed.)", autor: "Padesky, C. A. & Greenberger, D.", anio: 2020, edicion: 2, isbn: "978-1462542574" },
      { tipo: "libro", titulo: "Manual práctico de terapia cognitivo-conductual", autor: "Caballo, V. (Ed.)", editorial: "Pirámide", anio: 2019, isbn: "978-8436841237" },
      { tipo: "paper", titulo: "The efficacy of cognitive behavioral therapy: a review of meta-analyses", autores: "Hofmann, S. G., Asnaani, A., Vonk, I. J. J., Sawyer, A. T., & Fang, A.", anio: 2012, doi: "10.1007/s10608-012-9476-1" },
      { tipo: "paper", titulo: "Cognitive behavior therapy for depression: meta-analytic comparison with pharmacotherapy", autores: "Cuijpers, P., Karyotaki, E., Reijnders, M., & Ebert, D. D.", anio: 2018, doi: "10.1002/wps.20453" },
      { tipo: "guia", titulo: "NICE Guideline NG222 — Depression in adults: treatment and management", autor: "NICE", anio: 2022, url: "https://www.nice.org.uk/guidance/ng222" },
      { tipo: "guia", titulo: "APA Clinical Practice Guideline for the Treatment of Depression Across Three Age Cohorts", autor: "American Psychological Association", anio: 2019, url: "https://www.apa.org/depression-guideline" },
    ],
    casos_practicos: [
      {
        titulo: "Mujer 32a — Depresión moderada postparto",
        motivo_consulta: "Llevo 4 meses sin disfrutar nada con mi bebé. Lloro todos los días, me siento culpable y pienso que no soy buena madre.",
        hipotesis: "Episodio depresivo mayor postparto (CIE-10: F32.1 + F53.0). Distorsiones cognitivas centrales: 'debería' rígido y catastrofización sobre maternidad. Aislamiento social y reducción de actividades placenteras.",
        plan_aplicado: [
          "12 sesiones CBT semanales + 2 sesiones booster a 3 meses",
          "Fase 1-2: psicoeducación + registro de pensamientos automáticos",
          "Fase 3: reestructuración del 'mandato maternal' rígido (¿qué dice el deber? ¿qué dicen las madres reales?)",
          "Fase 4: activación conductual gradual (15 min de actividad placentera al día → 1 hora)",
          "Fase 5: prevención de recaída + escala de señales tempranas personalizada",
        ],
        evolucion: "PHQ-9 inicial 16 (mod-severa) → final 4 (mínima). Recuperación del vínculo con bebé reportada en sesión 8. Sin recaída a 6 meses.",
        reflexion: "La activación conductual fue clave antes que la reestructuración. Cuando ella misma comprobó que disfrutaba momentos puntuales con su bebé, las creencias culpógenas empezaron a perder credibilidad por sí solas.",
      },
      {
        titulo: "Hombre 45a — Trastorno de pánico con agorafobia",
        motivo_consulta: "Tuve un ataque en el bus hace 6 meses. Desde entonces no puedo salir solo y mi mundo se redujo a casa-oficina-casa.",
        hipotesis: "Trastorno de pánico con agorafobia (CIE-10: F40.01). Interpretaciones catastróficas de sensaciones corporales + evitación masiva como factor mantenedor.",
        plan_aplicado: [
          "16 sesiones CBT con foco en exposición interoceptiva + in vivo",
          "Fase 1: psicoeducación del ciclo del pánico (hiperventilación → mareo → catástrofe)",
          "Fase 2-3: experimentos interoceptivos en sesión (hiperventilar voluntariamente 60s) para romper interpretación catastrófica",
          "Fase 4: jerarquía de exposición in vivo (caminar 1 cuadra solo → bus 2 paradas → bus + viajar parado → bus en hora pico)",
          "Fase 5: plan booster + reducción gradual de medicación con psiquiatra",
        ],
        evolucion: "Reducción de ataques de 4/semana a 0 en sesión 10. Movilidad completa recuperada en sesión 14. PDSS pasó de 18 a 2.",
        reflexion: "La clave fue convencerlo de que las sensaciones corporales NO son peligrosas (experimentos interoceptivos repetidos), antes de pedirle exposición in vivo.",
      },
    ],
    recursos_descargables: [
      { titulo: "Registro de pensamientos automáticos (3 columnas)", tipo: "plantilla", url: "https://www.psicoactiva.com/wp-content/uploads/2020/05/Registro-Pensamientos-Automaticos.pdf" },
      { titulo: "Registro de pensamientos Beck (7 columnas)", tipo: "plantilla", url: "https://beckinstitute.org/wp-content/uploads/2021/08/Dysfunctional-Thought-Record.pdf" },
      { titulo: "Hoja paciente: 'Qué es la CBT' (psicoeducación)", tipo: "psicoeducacion", url: "https://www.cci.health.wa.gov.au/-/media/CCI/Mental-Health-Professionals/Generic/Information-Sheets/What-is-CBT.pdf" },
      { titulo: "Programación de actividades placenteras (semanal)", tipo: "paciente", url: "https://www.therapistaid.com/worksheets/pleasant-activity-schedule.pdf" },
      { titulo: "Lista de distorsiones cognitivas + ejemplos", tipo: "psicoeducacion", url: "https://www.therapistaid.com/worksheets/cognitive-distortions.pdf" },
    ],
  },
  {
    id: "act",
    nombre: "Terapia de Aceptación y Compromiso",
    sigla: "ACT",
    categoria: "individual",
    evidencia: "A",
    indicaciones: [
      "Depresión resistente",
      "Dolor crónico",
      "Ansiedad / preocupación crónica",
      "Estrés laboral / burnout",
      "Trastornos psicóticos (como complemento)",
    ],
    no_indicado: [
      "Crisis aguda (estabilizar primero)",
    ],
    duracion_tipica: "8-16 sesiones",
    estructura: [
      "Identificación de valores personales",
      "Defusión cognitiva (no fight con pensamientos)",
      "Aceptación de experiencia interna",
      "Yo-contexto / yo-observador",
      "Acción comprometida con valores",
    ],
    tecnicas_clave: [
      "Hexágono ACT (6 procesos)",
      "Metáforas (autobús, hojas en el río)",
      "Mindfulness aplicado",
      "Compromiso conductual con valores",
    ],
    outcome_recomendadas: ["AAQ-II", "CFQ", "PHQ-9"],
    referencias: [
      "Hayes, S. C., Strosahl, K. D., & Wilson, K. G. (2012). Acceptance and Commitment Therapy (2nd ed.).",
      "Wilson, K. G. & Luciano, C. (2002). Terapia de Aceptación y Compromiso (libro en español).",
    ],
    /* ─── §M-1 Contenido académico extendido ─── */
    descripcion_extendida:
      "La Terapia de Aceptación y Compromiso (ACT, pronunciada como verbo en inglés) es una " +
      "terapia contextual-conductual de tercera generación creada por Steven Hayes (años 80-90). " +
      "Se basa en la Teoría del Marco Relacional (RFT) y sostiene que el sufrimiento psicológico " +
      "proviene de la rigidez psicológica: evitar experiencias internas (pensamientos, emociones) " +
      "en lugar de actuar conforme a los propios valores. El objetivo no es eliminar síntomas, " +
      "sino aumentar la flexibilidad psicológica mediante seis procesos centrales (hexáflex): " +
      "aceptación, defusión cognitiva, contacto con el presente, yo-contexto, valores y acción " +
      "comprometida. Es efectiva en depresión resistente, dolor crónico, ansiedad y burnout.",
    efecto_tamano: {
      depresion: 0.55,
      ansiedad: 0.52,
      dolor_cronico: 0.64,
      estres_laboral: 0.66,
      psicosis: 0.40,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Análisis funcional + creative hopelessness",
        duracion_sesiones: "1-2",
        objetivos: [
          "Mapear las estrategias de control/evitación del cliente",
          "Generar 'desesperanza creativa': reconocer que lo que ha hecho NO funciona",
        ],
        tareas_clinico: [
          "Preguntar 'qué has intentado y qué resultados has obtenido a corto y largo plazo'",
          "Validar el esfuerzo + cuestionar la eficacia",
        ],
        tareas_paciente: ["Lista personal de estrategias usadas + resultado obtenido"],
      },
      {
        fase: 2, nombre: "Defusión cognitiva",
        duracion_sesiones: "2-4",
        objetivos: [
          "Crear distancia entre el cliente y sus pensamientos ('tengo un pensamiento' vs 'soy ese pensamiento')",
        ],
        tareas_clinico: [
          "Ejercicios de defusión (cantar el pensamiento, repetirlo 100 veces)",
          "Metáforas: hojas en el río, pasajeros del autobús",
        ],
        tareas_paciente: ["Practicar defusión 5 min/día con un pensamiento difícil"],
      },
      {
        fase: 3, nombre: "Aceptación + contacto con el presente",
        duracion_sesiones: "2-4",
        objetivos: [
          "Hacer espacio a la experiencia interna sin pelear con ella",
          "Mindfulness orientado a la flexibilidad",
        ],
        tareas_clinico: [
          "Ejercicio del 'observador' (yo-contexto)",
          "Hojas en el río extendido a emociones",
        ],
        tareas_paciente: ["Mindfulness corporal 10 min/día"],
      },
      {
        fase: 4, nombre: "Clarificación de valores",
        duracion_sesiones: "2-3",
        objetivos: [
          "Identificar valores (no metas) en 4-6 dominios vitales",
        ],
        tareas_clinico: [
          "Ejercicio del funeral (¿qué te gustaría que dijeran de ti?)",
          "Compass de valores Hayes — rating de importancia × consistencia",
        ],
        tareas_paciente: ["Escribir 1 valor por dominio: relaciones, trabajo, ocio, crecimiento personal, salud"],
      },
      {
        fase: 5, nombre: "Acción comprometida + prevención de recaída",
        duracion_sesiones: "3-5",
        objetivos: [
          "Trasladar valores a comportamiento concreto observable",
          "Manejar barreras psicológicas con flexibilidad",
        ],
        tareas_clinico: [
          "Definir 1-2 acciones SMART por valor",
          "Anticipar barreras + plan de defusión cuando aparezcan",
        ],
        tareas_paciente: ["Registro semanal de acciones-valor + barreras encontradas + cómo respondió"],
        criterios_avance: "Acción consistente con valores observable + reducción AAQ-II",
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Hojas en el río (defusión)",
        descripcion: "Visualización en la que el cliente imagina poner cada pensamiento en una hoja que flota por un río, sin pelear con ella ni perseguirla.",
        cuando_usar: "Cuando aparecen pensamientos rumiativos persistentes que el cliente no logra 'pensar mejor'.",
        ejemplo_dialogo:
          "T: 'Imagina que estás sentado junto a un río. Pasan hojas. Cada vez que aparece un pensamiento, ponlo en una hoja y deja que se vaya.'\n" +
          "(Pausa 2 min)\n" +
          "T: '¿Qué notaste?' C: 'Pude verlos sin engancharme.' T: 'Exacto. Ese es el espacio donde puedes elegir cómo actuar.'",
        ejercicio_casa: "Practicar 5 min al día durante 7 días.",
      },
      {
        nombre: "Compass de valores",
        descripcion: "Identificación sistemática de valores en 8-10 dominios vitales, con calificación 0-10 de (a) importancia personal y (b) consistencia con la conducta actual.",
        cuando_usar: "Fase 4. Cuando el cliente ya tiene defusión básica y necesita norte para acción.",
        ejemplo_dialogo:
          "T: 'En el dominio relaciones íntimas, ¿qué tipo de pareja/amigo querrías ser?' C: 'Presente, cariñoso.' T: '¿De 0 a 10, qué tan importante es?' C: '10.' T: '¿Y qué tan consistente has estado con eso esta semana?' C: '4.' T: 'Esa brecha es donde vamos a trabajar.'",
        ejercicio_casa: "Rellenar compass por escrito. Identificar 2 dominios con mayor brecha y comprometerse a 1 acción concreta esta semana.",
      },
      {
        nombre: "Metáfora de los pasajeros del autobús",
        descripcion: "El cliente es el conductor del autobús de su vida; los pasajeros son sus pensamientos/emociones difíciles que gritan instrucciones. Puede manejar hacia sus valores aunque los pasajeros griten.",
        cuando_usar: "Cuando el cliente cree que tiene que 'esperar a sentirse mejor' para actuar.",
        ejemplo_dialogo:
          "T: 'Imagina que vas conduciendo hacia algo importante (su valor). Los pasajeros del fondo gritan: \"detente, esto es peligroso, vas a fracasar\". ¿Tienes que pararte a discutir con ellos? ¿O puedes seguir conduciendo con ellos a bordo?'",
        ejercicio_casa: "Esta semana, identifica 1 momento en que actuaste hacia un valor a pesar de pasajeros gritones. Notarlo en una libreta.",
      },
    ],
    videos: [
      {
        titulo: "Steven Hayes — Acceptance and Commitment Therapy (TEDx)",
        url_youtube: "https://www.youtube.com/embed/v6kfvE-IL3o",
        autor: "Steven Hayes",
        duracion: "18:14",
        idioma: "en",
        descripcion: "Charla TEDx del creador de ACT sobre la flexibilidad psicológica.",
      },
      {
        titulo: "ACT en 6 procesos — el Hexáflex explicado",
        url_youtube: "https://www.youtube.com/embed/MJUu8x_yWeI",
        autor: "Russ Harris",
        duracion: "8:42",
        idioma: "en",
        descripcion: "Russ Harris explica visualmente los 6 procesos centrales de ACT.",
      },
      {
        titulo: "Introducción a ACT en español — Carmen Luciano",
        url_youtube: "https://www.youtube.com/embed/8e0z6w0RkRk",
        autor: "Carmen Luciano (PhD)",
        duracion: "14:30",
        idioma: "es",
        descripcion: "La principal referente hispana de ACT explica los fundamentos.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Acceptance and Commitment Therapy: The Process and Practice of Mindful Change (2nd ed.)", autor: "Hayes, S. C., Strosahl, K. D. & Wilson, K. G.", anio: 2012, edicion: 2, isbn: "978-1609189624" },
      { tipo: "libro", titulo: "ACT made simple", autor: "Harris, R.", anio: 2019, edicion: 2, isbn: "978-1684033010" },
      { tipo: "libro", titulo: "Terapia de Aceptación y Compromiso (ACT)", autor: "Wilson, K. G. & Luciano, M. C.", editorial: "Pirámide", anio: 2002, isbn: "978-8436817126" },
      { tipo: "paper", titulo: "Acceptance and commitment therapy: model, processes and outcomes", autores: "Hayes, S. C., Luoma, J. B., Bond, F. W., Masuda, A., & Lillis, J.", anio: 2006, doi: "10.1016/j.brat.2005.06.006" },
      { tipo: "paper", titulo: "Efficacy of ACT for chronic pain: meta-analysis", autores: "Veehof, M. M., Trompetter, H. R., Bohlmeijer, E. T., & Schreurs, K. M.", anio: 2016, doi: "10.1080/16506073.2015.1098724" },
    ],
    casos_practicos: [
      {
        titulo: "Mujer 38a — Dolor crónico lumbar + depresión secundaria",
        motivo_consulta: "Llevo 3 años con dolor lumbar. He probado todo. Ya no puedo trabajar ni salir. Me siento inútil.",
        hipotesis: "Dolor crónico (CIE-10: M54.5) + episodio depresivo (F32.1) secundario. Patrón de fusión cognitiva con el dolor ('el dolor manda') + evitación experiencial masiva.",
        plan_aplicado: [
          "12 sesiones ACT semanales",
          "Fase 1: análisis funcional — todo el día está organizado en torno a no sentir dolor",
          "Fase 2: defusión del pensamiento 'el dolor me detiene'",
          "Fase 4: clarificación de valores — quiere ser madre presente para su hija",
          "Fase 5: acciones-valor pequeñas a pesar del dolor (15 min de juego con su hija, aceptando el dolor)",
        ],
        evolucion: "AAQ-II inicial 38 → final 18. Reactivación funcional al 70% al cierre. Reportó: 'el dolor sigue, pero ya no me detiene'.",
        reflexion: "ACT no eliminó el dolor sino que cambió la relación del cliente con él. Ese era el cambio realmente posible y clínicamente significativo.",
      },
    ],
    recursos_descargables: [
      { titulo: "AAQ-II en español (Aceptación y Acción)", tipo: "plantilla", url: "https://contextualscience.org/files/AAQ-II_Spanish.pdf" },
      { titulo: "Compass de valores Hayes (8 dominios)", tipo: "plantilla", url: "https://contextualscience.org/files/Bullseye_Values_Survey.pdf" },
      { titulo: "Hoja paciente: ¿Qué es ACT?", tipo: "psicoeducacion", url: "https://www.actmindfully.com.au/wp-content/uploads/2019/07/What_Is_ACT_-_Russ_Harris.pdf" },
    ],
  },
  {
    id: "dbt",
    nombre: "Terapia Dialéctico-Conductual",
    sigla: "DBT",
    categoria: "individual",
    evidencia: "A",
    indicaciones: [
      "Trastorno Límite de Personalidad (TLP)",
      "Autolesiones / conductas suicidas crónicas",
      "Desregulación emocional severa",
      "Trastornos alimentarios (bulimia / atracón)",
    ],
    no_indicado: [
      "Sin compromiso del paciente de asistir a grupo de habilidades",
      "Sin equipo de consulta DBT disponible (programa completo)",
    ],
    duracion_tipica: "12 meses (programa estándar)",
    estructura: [
      "Pre-tratamiento + compromiso",
      "Sesión individual semanal (jerarquía: vida-terapia-calidad de vida)",
      "Grupo de habilidades semanal (4 módulos)",
      "Coaching telefónico entre sesiones",
      "Equipo de consulta para el terapeuta",
    ],
    tecnicas_clave: [
      "Mindfulness (mente sabia)",
      "Tolerancia al malestar (TIPP, ACEPTAR)",
      "Regulación emocional",
      "Efectividad interpersonal (DEAR MAN)",
      "Análisis cadenal de comportamientos problema",
    ],
    outcome_recomendadas: ["BSL-23", "DSHI", "DERS"],
    referencias: [
      "Linehan, M. M. (1993, 2014). DBT Skills Training Manual.",
      "Linehan, M. M. (2014). Manual de Habilidades DBT (edición en español).",
    ],
    notas: "Programa estructurado completo es caro y largo. Versiones adaptadas (DBT-A para adolescentes, RO-DBT para sobre-control) existen.",
  },
  {
    id: "emdr",
    nombre: "Desensibilización y Reprocesamiento por Movimientos Oculares",
    sigla: "EMDR",
    categoria: "trauma",
    evidencia: "A",
    indicaciones: [
      "Trastorno de Estrés Postraumático (TEPT)",
      "Trauma único o complejo",
      "Duelo traumático",
      "Fobia específica con componente traumático",
    ],
    no_indicado: [
      "Psicosis activa",
      "Disociación severa sin estabilización previa",
      "Crisis suicida activa",
    ],
    duracion_tipica: "8-12 sesiones (trauma único); 20+ trauma complejo",
    estructura: [
      "Fase 1: Historia del paciente y plan de tratamiento",
      "Fase 2: Preparación y recursos",
      "Fase 3: Evaluación de la memoria diana (SUD, VOC)",
      "Fase 4: Desensibilización (movimientos oculares bilaterales)",
      "Fase 5: Instalación de creencia positiva",
      "Fase 6: Examen corporal",
      "Fase 7: Cierre",
      "Fase 8: Reevaluación",
    ],
    tecnicas_clave: [
      "Estimulación bilateral (visual, auditiva, táctil)",
      "Protocolo estándar de 8 fases",
      "SUD (Subjective Units of Disturbance) 0-10",
      "VOC (Validity of Cognition) 1-7",
      "Lugar seguro (recurso de regulación)",
    ],
    outcome_recomendadas: ["PCL-5", "IES-R"],
    referencias: [
      "Shapiro, F. (2018). EMDR Therapy: Basic Principles, Protocols, and Procedures (3rd ed.).",
      "Solomon, R. M. & Shapiro, F. (2008). EMDR and the Adaptive Information Processing Model.",
    ],
    notas: "Requiere entrenamiento certificado por EMDR Institute o EMDR Iberoamérica. NICE 2018 y OMS lo recomiendan como primera línea para TEPT.",
    /* ─── §M-1 Contenido académico extendido ─── */
    descripcion_extendida:
      "EMDR (Eye Movement Desensitization and Reprocessing) es una psicoterapia integrativa " +
      "desarrollada por Francine Shapiro (1987) que utiliza estimulación bilateral (movimientos " +
      "oculares, tapping, sonidos alternantes) mientras el paciente accede a memorias " +
      "perturbadoras. Se basa en el modelo de Procesamiento Adaptativo de la Información (PAI): " +
      "las memorias traumáticas quedan almacenadas de forma disfuncional (con sensaciones, " +
      "emociones y creencias originales 'congeladas') y la estimulación bilateral activa un " +
      "mecanismo natural de reprocesamiento que las integra adaptativamente. Sigue un protocolo " +
      "estructurado de 8 fases. Aprobado por NICE, OMS, APA y Departamento de Defensa de EE.UU. " +
      "como tratamiento de primera línea para TEPT.",
    efecto_tamano: {
      tept: 1.05,
      trauma_unico: 1.36,
      trauma_complejo: 0.87,
      duelo_traumatico: 0.74,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Historia clínica y plan de tratamiento",
        duracion_sesiones: "1-2",
        objetivos: [
          "Mapear memorias diana (pasadas), disparadores actuales y plantillas a futuro",
          "Evaluar disociación (DES-II) y estabilidad para EMDR",
        ],
        tareas_clinico: [
          "Aplicar PCL-5 + IES-R + DES-II",
          "Construir lista priorizada de memorias diana",
        ],
        tareas_paciente: ["Lectura sobre EMDR (psicoeducación)"],
        criterios_avance: "Estabilidad emocional + lista de targets pactada",
      },
      {
        fase: 2, nombre: "Preparación y recursos",
        duracion_sesiones: "1-3",
        objetivos: [
          "Enseñar técnicas de estabilización: lugar seguro, contenedor",
          "Generar recursos internos antes de tocar trauma",
        ],
        tareas_clinico: [
          "Instalar 'lugar seguro' con estimulación bilateral suave (BLE)",
          "Práctica de contenedor (caja de seguridad)",
        ],
        tareas_paciente: ["Practicar lugar seguro 1×/día"],
        criterios_avance: "Cliente accede al lugar seguro confiablemente",
      },
      {
        fase: 3, nombre: "Evaluación de la memoria diana",
        duracion_sesiones: "Parte de cada sesión activa",
        objetivos: [
          "Identificar: imagen peor + cognición negativa (NC) + cognición positiva deseada (PC) + emoción + sensación corporal + SUD (0-10) + VOC (1-7)",
        ],
        tareas_clinico: [
          "Guía cuidadosa para evitar evitación",
          "Validar la dificultad de mirar la imagen",
        ],
      },
      {
        fase: 4, nombre: "Desensibilización (reprocesamiento)",
        duracion_sesiones: "Cuerpo central — varias sesiones por memoria",
        objetivos: [
          "Reducir SUD hasta 0-1 mediante series de estimulación bilateral",
        ],
        tareas_clinico: [
          "Series de ~24 movimientos oculares (variable)",
          "Entre series: 'qué notas ahora'",
          "Cognitive interweave si bloqueo",
        ],
        criterios_avance: "SUD ≤1 sostenido a través de 2-3 series",
      },
      {
        fase: 5, nombre: "Instalación de la cognición positiva",
        duracion_sesiones: "Parte de cada sesión",
        objetivos: ["Aumentar VOC de la PC hasta 7"],
        tareas_clinico: [
          "Vincular PC con la memoria reprocesada + BLE corta",
        ],
      },
      {
        fase: 6, nombre: "Examen corporal",
        duracion_sesiones: "Parte de cada sesión",
        objetivos: ["Verificar que no quedan sensaciones corporales residuales"],
      },
      {
        fase: 7, nombre: "Cierre",
        duracion_sesiones: "Final de cada sesión",
        objetivos: ["Volver a estado estable antes de finalizar (lugar seguro, contenedor)"],
      },
      {
        fase: 8, nombre: "Reevaluación",
        duracion_sesiones: "Inicio de la siguiente sesión",
        objetivos: ["Verificar consolidación del reprocesamiento entre sesiones"],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Instalación del lugar seguro",
        descripcion: "Construcción de un recurso interno: una imagen mental (real o imaginaria) donde el cliente se siente completamente seguro, anclada con BLE corta.",
        cuando_usar: "Fase 2 obligatoriamente antes de tocar cualquier memoria traumática.",
        ejemplo_dialogo:
          "T: 'Imagina un lugar donde te sientas completamente seguro. ¿Cómo es? ¿Qué ves? ¿Qué hueles? ¿Qué sientes en el cuerpo?'\n" +
          "(BLE 6-8 movimientos)\n" +
          "T: 'Date una palabra para anclarlo.' C: 'Río.' T: 'Cuando necesites volver, recuerda 'río' y la imagen.'",
        ejercicio_casa: "Practicar acceso al lugar seguro 1× al día con palabra-ancla.",
      },
      {
        nombre: "Protocolo estándar 8 fases — memoria diana",
        descripcion: "El protocolo central. Cliente sostiene en mente: imagen peor + NC + emoción + sensación corporal mientras sigue los movimientos oculares del terapeuta.",
        cuando_usar: "Una vez completadas fases 1-2 y verificada estabilidad.",
        ejemplo_dialogo:
          "T: 'Trae a tu mente la imagen peor de aquel día. ¿Qué pensamiento negativo tienes de ti mismo cuando la miras?' C: 'Soy un cobarde.'\n" +
          "T: '¿Cómo te gustaría pensar?' C: 'Hice lo mejor que pude.'\n" +
          "T: 'De 1-7, cuánto crees ahora la positiva.' C: '2.'\n" +
          "T: '¿Qué emoción? ¿Dónde la sientes en el cuerpo?' C: 'Vergüenza. Pecho.'\n" +
          "T: '0-10, cuán perturbador es ahora.' C: '8.'\n" +
          "T: 'Sigue mis dedos.' (BLE × 24 movimientos)\n" +
          "T: 'Respira. ¿Qué notas ahora?' C: 'Aparece la imagen de mi mamá llorando.'\n" +
          "T: 'Sigue con eso.' (BLE × 24)\n" +
          "(Iteración hasta SUD = 0)",
        ejercicio_casa: "Anotar lo que aparezca entre sesiones (sueños, asociaciones, recuerdos). NO reprocesar solo.",
      },
      {
        nombre: "Cognitive interweave (intervención cuando hay bloqueo)",
        descripcion: "Frase corta del terapeuta que aporta información faltante y desbloquea el reprocesamiento estancado.",
        cuando_usar: "Cuando SUD no baja después de varias series — el cliente está 'looping'.",
        ejemplo_dialogo:
          "Si el cliente dice 'soy responsable de lo que pasó' siendo niño en momento del trauma:\n" +
          "T: '¿Quién era el adulto en esa situación?' (interweave de responsabilidad)\n" +
          "Si el cliente está atascado en miedo a un evento ya pasado:\n" +
          "T: '¿Estás ahora a salvo?' (interweave de tiempo presente)",
      },
    ],
    videos: [
      {
        titulo: "Francine Shapiro — Introduction to EMDR (Beck Institute)",
        url_youtube: "https://www.youtube.com/embed/Z45y6JD2H_w",
        autor: "Francine Shapiro",
        duracion: "12:08",
        idioma: "en",
        descripcion: "La creadora de EMDR explica el modelo PAI y el protocolo de 8 fases.",
      },
      {
        titulo: "EMDR: cómo funciona en español",
        url_youtube: "https://www.youtube.com/embed/h-Z01uRy3jU",
        autor: "EMDR Iberoamérica",
        duracion: "9:30",
        idioma: "es",
        descripcion: "Explicación visual del proceso para hispanohablantes.",
      },
      {
        titulo: "EMDR fase 4 — reprocesamiento (demostración)",
        url_youtube: "https://www.youtube-nocookie.com/embed/Pb6C9pBv8Ss",
        autor: "EMDR Institute",
        duracion: "18:40",
        idioma: "en",
        descripcion: "Demostración del movimiento bilateral y reprocesamiento en fase 4 (material público EMDR Institute).",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Eye Movement Desensitization and Reprocessing (EMDR) Therapy: Basic Principles, Protocols, and Procedures (3rd ed.)", autor: "Shapiro, F.", anio: 2018, edicion: 3, isbn: "978-1462532766" },
      { tipo: "libro", titulo: "Manual de terapia EMDR", autor: "Shapiro, F. (trad.)", editorial: "Pax", anio: 2017, isbn: "978-9688609743" },
      { tipo: "paper", titulo: "EMDR for PTSD: a meta-analysis", autores: "Chen, L., Zhang, G., Hu, M., & Liang, X.", anio: 2015, doi: "10.1097/NMD.0000000000000306" },
      { tipo: "paper", titulo: "Comparing EMDR vs trauma-focused CBT for PTSD: meta-analysis", autores: "Bisson, J. I., et al.", anio: 2013, doi: "10.1002/14651858.CD003388.pub4" },
      { tipo: "guia", titulo: "NICE NG116 — PTSD: management", autor: "NICE", anio: 2018, url: "https://www.nice.org.uk/guidance/ng116" },
      { tipo: "guia", titulo: "WHO Guidelines for the Management of Conditions Specifically Related to Stress", autor: "OMS", anio: 2013, url: "https://www.who.int/publications/i/item/9789241505406" },
    ],
    casos_practicos: [
      {
        titulo: "Mujer 26a — TEPT por accidente de tránsito",
        motivo_consulta: "Hace 8 meses tuve un accidente. No puedo volver a manejar. Tengo pesadillas, sobresaltos, evito todo lo del carro.",
        hipotesis: "TEPT (CIE-10: F43.1) por trauma único. PCL-5 = 52. Disociación leve (DES-II 18). Apta para EMDR estándar.",
        plan_aplicado: [
          "10 sesiones EMDR",
          "Fase 1-2 (2 sesiones): historia, instalación lugar seguro 'playa de Cartagena'",
          "Fase 3-7 (7 sesiones): reprocesamiento de memoria diana = momento del impacto",
          "Memoria target adicional: ver el carro destruido al día siguiente",
          "Fase 8 + cierre: prevención + plantilla a futuro (manejar gradualmente)",
        ],
        evolucion: "PCL-5 inicial 52 → final 14 (sub-umbral). Volvió a manejar en sesión 8. Pesadillas cesaron en sesión 5. Sin recaída a 12 meses.",
        reflexion: "Trauma único reciente responde rapidísimo a EMDR cuando hay estabilidad emocional previa. El lugar seguro fue crítico para mantener la regulación durante el reprocesamiento.",
      },
    ],
    recursos_descargables: [
      { titulo: "PCL-5 (Posttraumatic Stress Checklist) en español", tipo: "plantilla", url: "https://www.ptsd.va.gov/professional/assessment/documents/PCL5_Standard_form_Spanish.pdf" },
      { titulo: "IES-R (Impact of Event Scale-Revised) en español", tipo: "plantilla", url: "https://www.cesfam.cl/wp-content/uploads/2017/05/IES-R-version-castellana.pdf" },
      { titulo: "DES-II (escala de disociación) en español", tipo: "plantilla", url: "https://www.isst-d.org/wp-content/uploads/2020/09/DES-II-Espanol.pdf" },
      { titulo: "Audio: lugar seguro guiado (10 min)", tipo: "audio", url: "https://www.emdr.com/audio/safe-place-spanish.mp3" },
    ],
  },
  {
    id: "mbct",
    nombre: "Terapia Cognitiva Basada en Mindfulness",
    sigla: "MBCT",
    categoria: "individual",
    evidencia: "A",
    indicaciones: [
      "Prevención de recaída en depresión (≥3 episodios)",
      "Depresión residual",
      "Ansiedad generalizada",
    ],
    no_indicado: [
      "Episodio depresivo agudo severo (estabilizar primero)",
      "Trauma reciente sin estabilización",
    ],
    duracion_tipica: "8 sesiones grupales (programa estructurado)",
    estructura: [
      "Sesión 1: Piloto automático",
      "Sesión 2: Vivir en la cabeza",
      "Sesión 3: Reuniendo la mente dispersa",
      "Sesión 4: Reconociendo aversión",
      "Sesión 5: Permitir / dejar ser",
      "Sesión 6: Los pensamientos no son hechos",
      "Sesión 7: ¿Cómo cuidarme mejor?",
      "Sesión 8: Mantenimiento",
    ],
    tecnicas_clave: [
      "Escaneo corporal",
      "Meditación sentada",
      "Yoga consciente",
      "Espacio de 3 minutos para respirar",
      "Registro de eventos placenteros/desagradables",
    ],
    outcome_recomendadas: ["PHQ-9", "FFMQ", "RRS"],
    referencias: [
      "Segal, Z., Williams, M., & Teasdale, J. (2018). Mindfulness-Based Cognitive Therapy for Depression (2nd ed.).",
    ],
  },
  {
    id: "tf_cbt",
    nombre: "Terapia Cognitivo-Conductual Focalizada en Trauma",
    sigla: "TF-CBT",
    categoria: "trauma",
    evidencia: "A",
    indicaciones: [
      "Trauma en niños y adolescentes (3-18 años)",
      "Abuso sexual infantil",
      "Violencia doméstica",
      "Duelo traumático infantil",
    ],
    no_indicado: [
      "Niños sin cuidador disponible para participar en componentes parentales",
    ],
    duracion_tipica: "12-25 sesiones (componente paciente + componente cuidador)",
    estructura: [
      "Componentes PRACTICE:",
      "P — Psicoeducación + habilidades de Padres",
      "R — Relajación",
      "A — modulación Afectiva",
      "C — procesamiento Cognitivo del trauma",
      "T — narrativa del Trauma",
      "I — exposición In vivo",
      "C — sesiones Conjuntas padre-niño",
      "E — Enhancing safety + future development",
    ],
    tecnicas_clave: [
      "Narrativa gradual del trauma",
      "Procesamiento cognitivo",
      "Entrenamiento parental",
    ],
    outcome_recomendadas: ["UCLA PTSD-RI", "TSCC", "CDI-2"],
    referencias: [
      "Cohen, J. A., Mannarino, A. P., & Deblinger, E. (2017). Treating Trauma and Traumatic Grief in Children and Adolescents (2nd ed.).",
    ],
  },
  {
    id: "cpt",
    nombre: "Terapia de Procesamiento Cognitivo",
    sigla: "CPT",
    categoria: "trauma",
    evidencia: "A",
    indicaciones: [
      "TEPT en adultos (especialmente trauma militar, violencia sexual)",
      "Comorbilidad TEPT + depresión",
    ],
    no_indicado: [
      "Disociación severa no estabilizada",
    ],
    duracion_tipica: "12 sesiones (protocolo estándar)",
    estructura: [
      "Sesiones 1-3: Psicoeducación + impacto del trauma",
      "Sesiones 4-7: Trabajando puntos atorados (stuck points)",
      "Sesiones 8-12: Cinco temas (seguridad, confianza, poder, estima, intimidad)",
    ],
    tecnicas_clave: [
      "Identificación de stuck points",
      "Hojas de trabajo ABC, Challenging Questions, Patterns of Problematic Thinking",
      "Cuenta del impacto (Impact Statement)",
    ],
    outcome_recomendadas: ["PCL-5", "PHQ-9"],
    referencias: [
      "Resick, P. A., Monson, C. M., & Chard, K. M. (2017). Cognitive Processing Therapy: Veteran/Military Version.",
    ],
  },
  {
    id: "ipt",
    nombre: "Psicoterapia Interpersonal",
    sigla: "IPT",
    categoria: "individual",
    evidencia: "A",
    indicaciones: [
      "Depresión mayor",
      "Depresión postparto",
      "Bulimia nerviosa",
      "Distimia",
    ],
    no_indicado: [
      "Pacientes con dificultad para identificar relaciones interpersonales como foco",
    ],
    duracion_tipica: "12-16 sesiones",
    estructura: [
      "Fase inicial (1-3 ses): formulación + foco en uno de los 4 dominios",
      "  → Duelo / Disputa de rol / Transición de rol / Déficit interpersonal",
      "Fase intermedia (4-12 ses): trabajo en el dominio elegido",
      "Fase de cierre (13-16 ses): consolidación + prevención",
    ],
    tecnicas_clave: [
      "Inventario interpersonal",
      "Análisis de comunicación",
      "Role-playing",
      "Trabajo en transición de roles",
    ],
    outcome_recomendadas: ["PHQ-9", "BDI-II"],
    referencias: [
      "Weissman, M. M., Markowitz, J. C., & Klerman, G. L. (2017). The Guide to Interpersonal Psychotherapy.",
    ],
  },
  {
    id: "esquemas",
    nombre: "Terapia Centrada en Esquemas",
    sigla: "ST",
    categoria: "individual",
    evidencia: "B",
    indicaciones: [
      "Trastornos de personalidad (TLP, evitativo, dependiente, narcisista)",
      "Depresión crónica resistente a CBT",
      "Patrones interpersonales recurrentes",
    ],
    no_indicado: [
      "Crisis aguda sin estabilización previa",
    ],
    duracion_tipica: "1-3 años",
    estructura: [
      "Evaluación de esquemas tempranos desadaptativos (18 esquemas Young)",
      "Identificación de modos (modo niño, padre punitivo, etc.)",
      "Reparentalización limitada",
      "Trabajo cognitivo, experiencial y conductual",
    ],
    tecnicas_clave: [
      "YSQ (Young Schema Questionnaire)",
      "Imaginería con reparentalización",
      "Silla vacía / diálogo de modos",
      "Carta a la figura significativa",
    ],
    outcome_recomendadas: ["YSQ-S3", "SMI"],
    referencias: [
      "Young, J. E., Klosko, J. S., & Weishaar, M. E. (2003). Schema Therapy: A Practitioner's Guide.",
    ],
  },

  /* ═══════ PAREJA ═══════ */
  {
    id: "gottman",
    nombre: "Método Gottman",
    sigla: "Gottman",
    categoria: "pareja",
    evidencia: "A",
    indicaciones: [
      "Pareja en conflicto activo",
      "Pre-divorcio (último intento)",
      "Pareja post-aventura (con ciertas condiciones)",
      "Prevención (parejas en buen momento)",
    ],
    no_indicado: [
      "Violencia doméstica activa o reciente",
      "Adicción no tratada en uno de los miembros",
    ],
    duracion_tipica: "10-25 sesiones",
    estructura: [
      "Evaluación (3 sesiones): conjunta + individuales + retroalimentación",
      "Sound Relationship House (7 niveles): mapas de amor, cariño, acercamiento, perspectiva positiva, manejo de conflicto, sueños de vida, significado compartido",
      "Antídotos a los 4 jinetes (crítica, desprecio, defensividad, obstruccionismo)",
    ],
    tecnicas_clave: [
      "Mapa de amor (love maps)",
      "Reparación durante conflicto",
      "Diálogo de sueños",
      "Rituales de conexión",
    ],
    outcome_recomendadas: ["CSI-32", "DAS"],
    referencias: [
      "Gottman, J. M. & Gottman, J. S. (2017). The Gottman Method Couple Therapy.",
      "Gottman, J. M. (1999). The Marriage Clinic.",
    ],
  },
  {
    id: "eft_pareja",
    nombre: "Terapia Centrada en Emociones para Parejas",
    sigla: "EFT-C",
    categoria: "pareja",
    evidencia: "A",
    indicaciones: [
      "Inseguridad en el vínculo de apego adulto",
      "Pareja con patrones de retirada-persecución",
      "Reparación de traumas relacionales menores",
    ],
    no_indicado: [
      "Violencia doméstica activa",
      "Aventura sin compromiso de honestidad",
    ],
    duracion_tipica: "8-20 sesiones",
    estructura: [
      "Etapa 1: Desescalada del ciclo negativo",
      "Etapa 2: Reestructuración del vínculo (acceso a emociones primarias)",
      "Etapa 3: Consolidación + soluciones a problemas pendientes",
    ],
    tecnicas_clave: [
      "Identificación del ciclo (persecutor-distanciador)",
      "Acceso a emociones primarias (vulnerables)",
      "Demostración (enactment)",
      "Reparación de heridas de apego",
    ],
    outcome_recomendadas: ["CSI-32", "ECR-S"],
    referencias: [
      "Johnson, S. M. (2019). Attachment Theory in Practice: EFT with Individuals, Couples, and Families.",
      "Johnson, S. M. (2008). Hold Me Tight (libro autoayuda — traducido).",
    ],
  },
  {
    id: "tcc_pareja",
    nombre: "Terapia Conductual-Cognitiva de Pareja",
    sigla: "CBCT",
    categoria: "pareja",
    evidencia: "A",
    indicaciones: [
      "Pareja con conflictos comunicacionales",
      "Insatisfacción marital",
    ],
    no_indicado: ["Violencia doméstica"],
    duracion_tipica: "12-20 sesiones",
    estructura: [
      "Evaluación de áreas problema",
      "Entrenamiento en comunicación efectiva",
      "Resolución de problemas estructurada",
      "Reestructuración cognitiva de atribuciones",
    ],
    tecnicas_clave: [
      "Comunicación constructiva (yo-mensajes)",
      "Acuerdo de comportamiento",
      "Distorsiones cognitivas sobre la pareja",
    ],
    outcome_recomendadas: ["DAS", "CSI-32"],
    referencias: [
      "Epstein, N. B. & Baucom, D. H. (2002). Enhanced Cognitive-Behavioral Therapy for Couples.",
    ],
  },

  /* ═══════ FAMILIA ═══════ */
  {
    id: "sistemica_estructural",
    nombre: "Terapia Estructural Familiar",
    sigla: "Sistémica",
    categoria: "familia",
    evidencia: "B",
    indicaciones: [
      "Familias con problemas de jerarquía / límites",
      "Adolescente sintomático",
      "Trastornos alimentarios en adolescentes",
    ],
    no_indicado: [
      "Violencia familiar activa",
    ],
    duracion_tipica: "6-20 sesiones",
    estructura: [
      "Unión (joining) con la familia",
      "Mapeo de estructura familiar (límites, jerarquías, alianzas)",
      "Reestructuración (intervenciones)",
      "Consolidación",
    ],
    tecnicas_clave: [
      "Genograma",
      "Escultura familiar",
      "Reformulación (reframing)",
      "Tareas paradójicas (uso cuidadoso)",
    ],
    outcome_recomendadas: ["FACES-IV", "SCORE-15"],
    referencias: [
      "Minuchin, S. (1974). Families and Family Therapy.",
      "Minuchin, S., Nichols, M. P., & Lee, W.-Y. (2007). Assessing Families and Couples.",
    ],
  },
  {
    id: "fbt_alimentaria",
    nombre: "Terapia Familiar (Maudsley) para Anorexia/Bulimia Adolescente",
    sigla: "FBT",
    categoria: "familia",
    evidencia: "A",
    indicaciones: [
      "Anorexia nerviosa adolescente (12-18 años)",
      "Bulimia nerviosa adolescente",
    ],
    no_indicado: [
      "Adultos (existen variantes pero distinto)",
      "Comorbilidad psiquiátrica severa sin estabilización",
    ],
    duracion_tipica: "20 sesiones en 6-12 meses",
    estructura: [
      "Fase 1: Padres a cargo de la realimentación",
      "Fase 2: Retornar control al adolescente gradualmente",
      "Fase 3: Identidad adolescente normal sin TCA",
    ],
    tecnicas_clave: [
      "Externalización del TCA",
      "Empoderamiento parental",
      "Picnic familiar terapéutico (sesión 2)",
    ],
    outcome_recomendadas: ["EDE-Q", "IMC tracking"],
    referencias: [
      "Lock, J. & Le Grange, D. (2013). Treatment Manual for Anorexia Nervosa: A Family-Based Approach.",
    ],
  },

  /* ═══════ DUELO ═══════ */
  {
    id: "duelo_worden",
    nombre: "Modelo de Worden — 4 Tareas del Duelo",
    sigla: "Worden",
    categoria: "duelo",
    evidencia: "tradicional",
    indicaciones: [
      "Duelo normal complicado",
      "Pérdidas significativas (muerte, separación, pérdida laboral, salud)",
    ],
    no_indicado: [
      "Duelo prolongado >12 meses con síntomas severos → considerar PGT específica",
    ],
    duracion_tipica: "6-20 sesiones",
    estructura: [
      "Tarea I: Aceptar la realidad de la pérdida",
      "Tarea II: Procesar el dolor del duelo",
      "Tarea III: Adaptarse a un mundo sin el fallecido (externa, interna, espiritual)",
      "Tarea IV: Recolocar emocionalmente al fallecido y continuar viviendo",
    ],
    tecnicas_clave: [
      "Carta al fallecido",
      "Lugar de memoria",
      "Rituales de despedida",
      "Conversación con silla vacía",
    ],
    outcome_recomendadas: ["TRIG", "ICG-r"],
    referencias: [
      "Worden, J. W. (2018). Grief Counseling and Grief Therapy (5th ed.).",
      "Worden, J. W. (2013). El tratamiento del duelo (4ª ed., en español).",
    ],
  },
  {
    id: "duelo_neimeyer",
    nombre: "Terapia de Reconstrucción de Significado en el Duelo",
    sigla: "Neimeyer",
    categoria: "duelo",
    evidencia: "B",
    indicaciones: [
      "Duelo complicado",
      "Pérdida violenta o traumática",
      "Crisis de significado existencial",
    ],
    no_indicado: ["Crisis suicida activa"],
    duracion_tipica: "10-20 sesiones",
    estructura: [
      "Narrativa de la pérdida",
      "Reconstrucción del significado de la vida",
      "Diálogo con el ser perdido (cartas, sillas)",
      "Reintegración del legado",
    ],
    tecnicas_clave: [
      "Diálogo imaginal con el ausente",
      "Línea de vida con la pérdida integrada",
      "Reconstrucción narrativa",
    ],
    outcome_recomendadas: ["ICG-r", "MILQ"],
    referencias: [
      "Neimeyer, R. A. (2016). Techniques of Grief Therapy: Assessment and Intervention.",
      "Neimeyer, R. A. (2002). Aprender de la pérdida (libro en español).",
    ],
  },
  {
    id: "pgt",
    nombre: "Terapia de Duelo Prolongado",
    sigla: "PGT",
    categoria: "duelo",
    evidencia: "A",
    indicaciones: [
      "Trastorno de duelo prolongado (DSM-5-TR / CIE-11)",
      "Síntomas de duelo persistentes >12 meses con disfunción",
    ],
    no_indicado: [
      "Duelo agudo reciente <6 meses (normal)",
    ],
    duracion_tipica: "16 sesiones (protocolo manualizado)",
    estructura: [
      "Psicoeducación sobre duelo prolongado",
      "Revisión de la muerte (similar a exposición)",
      "Visualización imaginal del fallecido",
      "Reconstrucción de metas y significados",
    ],
    tecnicas_clave: [
      "Exposición a la narrativa de la muerte",
      "Diálogo imaginal estructurado",
      "Trabajo con sueños del fallecido",
    ],
    outcome_recomendadas: ["ICG-r", "PG-13-R"],
    referencias: [
      "Shear, M. K. et al. (2005, 2014). Treatment of complicated grief. JAMA.",
    ],
  },

  /* ═══════ ADICCIONES ═══════ */
  {
    id: "entrevista_motivacional",
    nombre: "Entrevista Motivacional",
    sigla: "EM / MI",
    categoria: "adicciones",
    evidencia: "A",
    indicaciones: [
      "Adicciones (alcohol, drogas, tabaco)",
      "Adherencia a tratamiento médico",
      "Cambios de estilo de vida",
      "Ambivalencia general (no solo adicciones)",
    ],
    no_indicado: [
      "Paciente ya en plena acción (mejor pasar a tratamiento específico)",
    ],
    duracion_tipica: "1-4 sesiones (a menudo combinada con otros enfoques)",
    estructura: [
      "Enganche (engaging)",
      "Foco (focusing)",
      "Evocar (evoking) lenguaje de cambio",
      "Planificar (planning)",
    ],
    tecnicas_clave: [
      "OARS (preguntas abiertas, afirmaciones, escucha reflexiva, sumarios)",
      "Reflejo del cambio talk",
      "Balance decisional",
      "Escalas de importancia / confianza 0-10",
    ],
    outcome_recomendadas: ["AUDIT", "DAST-10", "URICA"],
    referencias: [
      "Miller, W. R. & Rollnick, S. (2023). Motivational Interviewing: Helping People Change (4th ed.).",
      "Miller, W. R. & Rollnick, S. (2015). La entrevista motivacional (3ª ed., en español).",
    ],
  },
  {
    id: "modelo_transteorico",
    nombre: "Modelo Transteórico del Cambio (Prochaska-DiClemente)",
    sigla: "MTT",
    categoria: "adicciones",
    evidencia: "B",
    indicaciones: [
      "Marco para entender en qué etapa está el paciente",
      "Útil con cualquier conducta a cambiar",
    ],
    no_indicado: [
      "No es terapia por sí solo — usar como marco junto a otra técnica",
    ],
    duracion_tipica: "marco transversal, no protocolo aislado",
    estructura: [
      "Precontemplación",
      "Contemplación",
      "Preparación",
      "Acción",
      "Mantenimiento",
      "(Recaída como parte del proceso)",
    ],
    tecnicas_clave: [
      "Identificar etapa actual",
      "Intervenciones adaptadas a la etapa (no acción si está en precontemplación)",
    ],
    outcome_recomendadas: ["URICA"],
    referencias: [
      "Prochaska, J. O. & DiClemente, C. C. (1983, 2005).",
    ],
  },

  /* ═══════ NIÑOS Y ADOLESCENTES ═══════ */
  {
    id: "pmt",
    nombre: "Entrenamiento Parental Conductual",
    sigla: "PMT / BPT",
    categoria: "ninos_adolescentes",
    evidencia: "A",
    indicaciones: [
      "Trastornos de conducta disruptiva (TDAH, TOC, TND)",
      "Niños 2-12 años con problemas de comportamiento",
    ],
    no_indicado: [
      "Maltrato infantil activo (intervenir protección primero)",
    ],
    duracion_tipica: "10-16 sesiones (PCIT, Triple P, Incredible Years)",
    estructura: [
      "Psicoeducación sobre desarrollo y conducta",
      "Aumentar interacciones positivas (CDI / Child-Directed Interaction)",
      "Establecimiento de límites efectivos (PDI / Parent-Directed Interaction)",
      "Manejo de berrinches y conductas problema",
    ],
    tecnicas_clave: [
      "Tiempo especial / juego dirigido",
      "Refuerzo positivo de conducta apropiada",
      "Time-out estructurado",
      "Tabla de comportamiento",
    ],
    outcome_recomendadas: ["ECBI", "SDQ"],
    referencias: [
      "Webster-Stratton, C. (2017). The Incredible Years.",
      "Eyberg, S. M. & Funderburk, B. (2011). PCIT Protocol.",
    ],
  },

  /* ═══════ PSICOTERAPIAS BREVES + EXISTENCIALES ═══════ */
  {
    id: "pdt_breve",
    nombre: "Psicoterapia Psicodinámica Breve",
    sigla: "STDP / PDT",
    categoria: "individual",
    evidencia: "B",
    indicaciones: [
      "Depresión leve-moderada",
      "Problemas relacionales recurrentes",
      "Síntomas con origen conflictual identificable",
    ],
    no_indicado: [
      "Paciente sin capacidad de mentalización mínima",
      "Crisis suicida activa",
    ],
    duracion_tipica: "16-40 sesiones",
    estructura: [
      "Foco dinámico identificado al inicio",
      "Triángulo del conflicto (sentimiento-defensa-ansiedad)",
      "Triángulo de las personas (transferencia / actual / pasado)",
      "Cierre con consolidación",
    ],
    tecnicas_clave: [
      "Interpretación moderada de transferencia",
      "Trabajo con defensas",
      "Insight conectado a cambio conductual",
    ],
    outcome_recomendadas: ["IIP-32", "PHQ-9"],
    referencias: [
      "Shedler, J. (2010). The efficacy of psychodynamic psychotherapy. American Psychologist.",
      "Leichsenring, F. (2009). Psychodynamic psychotherapy: a meta-analytic review.",
    ],
  },
  {
    id: "logoterapia",
    nombre: "Logoterapia",
    sigla: "Frankl",
    categoria: "individual",
    evidencia: "tradicional",
    indicaciones: [
      "Crisis de sentido / vacío existencial",
      "Duelo + búsqueda de significado",
      "Pacientes con enfermedad terminal o pérdidas significativas",
    ],
    no_indicado: [
      "Psicopatología severa sin estabilización",
    ],
    duracion_tipica: "Variable, 10-40 sesiones",
    estructura: [
      "Diálogo socrático sobre sentido",
      "Exploración de los 3 valores (creativos, experienciales, actitudinales)",
      "Trabajo con intención paradójica + dereflexión cuando aplica",
    ],
    tecnicas_clave: [
      "Diálogo socrático",
      "Intención paradójica",
      "Dereflexión",
      "Modificación de actitudes",
    ],
    outcome_recomendadas: ["PIL", "MLQ"],
    referencias: [
      "Frankl, V. E. (1959/1991). El hombre en busca de sentido.",
      "Längle, A. (2003). Análisis Existencial.",
    ],
    notas: "Evidencia empírica limitada por su naturaleza filosófica; eficacia documentada en estudios cualitativos.",
  },
  {
    id: "humanistica",
    nombre: "Terapia Centrada en la Persona",
    sigla: "PCT / Rogers",
    categoria: "individual",
    evidencia: "B",
    indicaciones: [
      "Crisis vital normativa",
      "Búsqueda de autoconocimiento",
      "Counseling de baja-moderada complejidad",
    ],
    no_indicado: [
      "Patología severa que requiere intervención estructurada (TLP, psicosis)",
    ],
    duracion_tipica: "10-50 sesiones",
    estructura: [
      "No directivo, sigue el proceso del paciente",
    ],
    tecnicas_clave: [
      "Empatía",
      "Aceptación incondicional positiva",
      "Congruencia",
      "Reflejo de sentimientos",
    ],
    outcome_recomendadas: ["CORE-OM", "PHQ-9"],
    referencias: [
      "Rogers, C. R. (1957). The necessary and sufficient conditions of therapeutic personality change.",
      "Mearns, D. & Cooper, M. (2017). Working at Relational Depth.",
    ],
  },

  /* ═══════ INTEGRATIVOS / TERCERA OLA ═══════ */
  {
    id: "compasion_cft",
    nombre: "Terapia Centrada en la Compasión",
    sigla: "CFT",
    categoria: "individual",
    evidencia: "B",
    indicaciones: [
      "Vergüenza y autocrítica",
      "Depresión con autoataque",
      "Trauma con culpa significativa",
    ],
    no_indicado: [
      "Pacientes con miedo intenso a la compasión sin preparación previa",
    ],
    duracion_tipica: "12-20 sesiones",
    estructura: [
      "Psicoeducación 3 sistemas emocionales (amenaza, logro, calma)",
      "Práctica de mente compasiva (CMT)",
      "Diálogos de yo-compasivo / yo-crítico",
    ],
    tecnicas_clave: [
      "Respiración rítmica calmante",
      "Imaginería del lugar seguro / yo-compasivo",
      "Carta compasiva a uno mismo",
    ],
    outcome_recomendadas: ["SCS", "FSCRS"],
    referencias: [
      "Gilbert, P. (2010). Compassion Focused Therapy: Distinctive Features.",
      "Gilbert, P. (2014). Terapia centrada en la compasión (edición en español).",
    ],
  },
];

/* ═══════ Helpers ═══════ */

/** Lista única de categorías presentes en el catálogo. */
/* §M-1 (mayo 2026): aplicar contenido académico extendido generado por agente Haiku
 * (`enfoquesExtendidos.js`) sobre el catálogo base. Los IDs sin entrada en
 * ENFOQUES_EXTENDIDOS quedan con sus campos base; los IDs con entrada
 * obtienen `descripcion_extendida`, `fases_aplicacion`, `tecnicas_detalladas`,
 * `videos`, `bibliografia`, `casos_practicos`, `recursos_descargables`.
 * Si el spread sobrescribe un campo base (ej. `descripcion_extendida` ya
 * existía), prevalece el del módulo extendido. */
import { ENFOQUES_EXTENDIDOS as _EXTENDIDOS } from "./enfoquesExtendidos.js";
export const ENFOQUES_TERAPEUTICOS = _ENFOQUES_BASE.map(e => ({
  ...e,
  ..._EXTENDIDOS[e.id] || {},
}));

export const CATEGORIAS_ENFOQUE = [...new Set(ENFOQUES_TERAPEUTICOS.map(e => e.categoria))];

/** Niveles de evidencia con descripción humana. */
export const NIVELES_EVIDENCIA = {
  A: "Sólida — múltiples RCT / meta-análisis recientes (APA Div 12, NICE, Cochrane)",
  B: "Moderada — algunos RCT o evidencia naturalística consistente",
  C: "Emergente — estudios preliminares prometedores",
  tradicional: "Tradicional — base teórica sólida, evidencia empírica limitada o cualitativa",
};

/** Busca un enfoque por id. */
export const getEnfoque = (id) => ENFOQUES_TERAPEUTICOS.find(e => e.id === id);

/** Enfoques recomendados por problema clínico. */
export const ENFOQUES_POR_PROBLEMA = {
  "depresion": ["cbt", "ipt", "act", "mbct", "pdt_breve"],
  "ansiedad": ["cbt", "act", "mbct"],
  "tept": ["emdr", "cpt", "tf_cbt"],
  "tlp": ["dbt", "esquemas"],
  "duelo": ["duelo_worden", "duelo_neimeyer", "pgt"],
  "pareja": ["gottman", "eft_pareja", "tcc_pareja"],
  "alimentario": ["fbt_alimentaria", "cbt"],
  "adicciones": ["entrevista_motivacional", "cbt"],
  "ninos_conducta": ["pmt", "tf_cbt"],
  "trauma_complejo": ["emdr", "esquemas", "dbt"],
  "existencial": ["logoterapia", "humanistica"],
  "autocritica_verguenza": ["compasion_cft"],
};
