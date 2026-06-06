/* ═══════════════════════════════════════════════════════════════════════
 * clinicalData.js — Base de conocimiento clínico para NeuroSoft
 * ───────────────────────────────────────────────────────────────────────
 * Contenido generado originalmente para este proyecto, basado en:
 *   - DSM-5 (APA, 2013/2022)
 *   - Criterios CIE-10
 *   - Literatura de práctica neuropsicológica (Lezak, Strauss, Flanagan)
 *   - Pautas de interpretación WISC-IV / WAIS-III (Wechsler, Kaufman)
 * Todos los textos de recomendación son redactados para este sistema.
 * ═══════════════════════════════════════════════════════════════════════ */

/* ── 1. BIBLIOTECA DE RECOMENDACIONES POR CUADRO CLÍNICO ──
 * Estructura: { cuadro_id: { nombre, keywords, categorias: { cat: [recs] } } }
 * Las recomendaciones se redactan como texto de un párrafo, listas para
 * copiar/pegar/editar por el profesional.
 */
export const RECOMMENDATIONS_LIB = {
  tdah: {
    nombre: "TDAH — Trastorno por Déficit de Atención e Hiperactividad",
    cie: "F90",
    keywords: ["atención", "hiperactividad", "impulsividad", "autorregulación", "tdah", "déficit atencional"],
    categorias: {
      escolar: [
        "Ubicar al estudiante en las primeras filas del aula, alejado de ventanas y zonas de alto tránsito, para reducir distractores.",
        "Fraccionar las tareas largas en bloques cortos con pausas breves entre cada uno. Permitir movimiento controlado entre bloques.",
        "Ofrecer instrucciones una a una, de forma concreta y verificando comprensión con parafraseo del estudiante.",
        "Extender los tiempos de evaluación y permitir uso de agenda visual o checklist para monitorear avance.",
        "Retroalimentación inmediata y frecuente. Evitar correcciones en gran grupo; preferir devolución individual.",
        "Establecer rutinas predecibles: mismo orden de actividades cada día, con transiciones anticipadas.",
      ],
      familiar: [
        "Mantener rutinas diarias estables para sueño, alimentación, estudio y ocio. Evitar cambios bruscos no anticipados.",
        "Dar instrucciones de una sola tarea a la vez, con contacto visual previo. Evitar impartir varias órdenes simultáneas desde otro lugar de la casa.",
        "Usar sistemas visuales de refuerzo (tableros, fichas) para metas conductuales concretas, con logros alcanzables a corto plazo.",
        "Reducir el tiempo de pantalla pasivo y fomentar actividades de alta demanda motora: deporte, baile, juegos al aire libre.",
        "Los padres/cuidadores deben coordinar consignas entre sí para mantener consistencia en los límites.",
      ],
      terapeutico: [
        "Intervención neuropsicológica con énfasis en control inhibitorio, flexibilidad cognitiva y automonitoreo.",
        "Psicoterapia cognitivo-conductual para trabajar autoestima, manejo de la frustración y habilidades sociales.",
        "Valoración por psiquiatría infantil o de adultos según el caso, para definir pertinencia de manejo farmacológico.",
        "Terapia ocupacional con enfoque en integración sensorial si hay disregulación motora o sensorial asociada.",
        "Considerar entrenamiento en mindfulness adaptado a la edad como complemento a la terapia formal.",
      ],
      ambiental: [
        "Garantizar un espacio de estudio fijo, ordenado, con iluminación adecuada y sin ruido ambiental intenso.",
        "Retirar del entorno de trabajo objetos, dispositivos o materiales no relacionados con la tarea en curso.",
        "Usar cronómetros visuales (Time Timer o similares) para hacer tangible el paso del tiempo en tareas.",
      ],
    },
  },
  tea: {
    nombre: "TEA — Trastorno del Espectro Autista",
    cie: "F84",
    keywords: ["autismo", "tea", "comunicación social", "intereses restringidos", "estereotipias", "sensorial"],
    categorias: {
      comunicacion_social: [
        "Intervención en pragmática del lenguaje: turnos conversacionales, inferencias, contacto visual funcional, identificación de expresiones faciales.",
        "Guiones sociales y modelado de rol para situaciones predecibles (saludar, pedir ayuda, resolver conflictos).",
        "Fomento de juego interactivo estructurado con pares; evitar forzar interacciones masivas sin preparación previa.",
        "Uso de apoyos visuales (pictogramas, secuencias, agendas) cuando el lenguaje verbal no alcanza a sostener la comprensión.",
      ],
      manejo_conductual: [
        "Anticipación de cambios mediante agendas visuales y transiciones preparadas con antelación. Evitar cambios súbitos de rutina.",
        "Identificación de desencadenantes conductuales (triggers) y registro para prevenir crisis sensoriales o de ansiedad.",
        "Refuerzo positivo sistemático de conductas adaptativas; evitar castigos que generen confusión sobre la regla.",
      ],
      sensorial: [
        "Valoración por terapia ocupacional con perfil sensorial para identificar hiper/hiposensibilidades específicas.",
        "Adecuaciones ambientales: reducir ruido blanco, luz fluorescente parpadeante, texturas aversivas en uniformes o materiales.",
        "Incorporar pausas sensoriales programadas (espacios calmos, squeezers, audífonos con cancelación si aplica).",
      ],
      escolar: [
        "Plan de adaptación curricular individualizado con apoyos concretos para transiciones, trabajo colaborativo y evaluaciones.",
        "Asignar un/a docente de apoyo o sombra según necesidad y etapa educativa.",
        "Sensibilización del grupo de pares y del equipo docente sobre las características del estudiante, con su consentimiento.",
      ],
      familiar: [
        "Psicoeducación para la familia sobre perfil sensorial, comunicación y manejo conductual específicos del caso.",
        "Red de apoyo con otras familias; grupos de padres facilitan información práctica y soporte emocional.",
        "Documentar en un pasaporte personal la información clínica y las necesidades clave para profesionales nuevos.",
      ],
    },
  },
  discapacidad_intelectual: {
    nombre: "Discapacidad Intelectual",
    cie: "F70-F79",
    keywords: ["discapacidad intelectual", "ci bajo", "retardo", "adaptativo", "limitaciones"],
    categorias: {
      escolar: [
        "Ajuste curricular significativo con objetivos funcionales y evaluación por logros individuales.",
        "Enseñanza por tarea concreta, modelado, repetición distribuida y encadenamiento inverso.",
        "Promover habilidades de vida diaria como contenido transversal dentro del currículo.",
      ],
      adaptativo: [
        "Programa de entrenamiento en habilidades adaptativas: aseo personal, manejo de dinero, transporte, cocina básica.",
        "Uso de apoyos visuales y tecnológicos (apps de recordatorios, pictogramas) para sostener la autonomía.",
        "Entrenamiento en reconocimiento de situaciones de riesgo y solicitud de ayuda.",
      ],
      familiar: [
        "Acompañamiento psicosocial a la familia, con foco en expectativas realistas y prevención de sobreprotección.",
        "Coordinación con red de servicios sociales y educativos especiales del sistema territorial.",
        "Planificación a largo plazo sobre proyecto de vida, apoyo en la adultez y autonomía progresiva.",
      ],
    },
  },
  dea: {
    nombre: "Dificultades Específicas del Aprendizaje",
    cie: "F81",
    keywords: ["dislexia", "disgrafía", "discalculia", "aprendizaje", "lectura", "escritura", "cálculo"],
    categorias: {
      escolar: [
        "Intervención pedagógica especializada en el área específica comprometida (lectura/escritura/cálculo).",
        "Adaptaciones de acceso: ampliación de tiempo, lectura en voz alta de enunciados, uso de calculadora cuando el objeto evaluado no sea el cálculo.",
        "Evaluaciones con formato alternativo (oral, proyecto) cuando la modalidad escrita penaliza desproporcionadamente.",
      ],
      terapeutico: [
        "Terapia de aprendizaje con enfoque multisensorial (método Orton-Gillingham o similar) para dislexia.",
        "Entrenamiento en conciencia fonológica, fluidez lectora y comprensión a partir de textos de dificultad graduada.",
        "Intervención en cálculo con manipulativos concretos antes de abstracción simbólica.",
      ],
      familiar: [
        "Evitar la sobreexposición a tareas que refuerzan la experiencia de fracaso. Priorizar lectura compartida por placer.",
        "Proteger la autoestima académica: separar identidad del estudiante de su rendimiento escolar.",
        "Seguimiento coordinado entre colegio, tutor terapéutico y hogar.",
      ],
    },
  },
  deterioro_cognitivo_leve: {
    nombre: "Trastorno Neurocognitivo Leve (DCL)",
    cie: "G31.84",
    keywords: ["dcl", "deterioro cognitivo", "tnc leve", "memoria anciano", "queja cognitiva", "mild cognitive"],
    categorias: {
      intervencion_cognitiva: [
        "Programa estructurado de estimulación cognitiva con ejercicios de memoria episódica, atención, lenguaje y funciones ejecutivas.",
        "Entrenamiento en estrategias compensatorias: agendas externas, recordatorios, rutinas escritas, método de loci.",
        "Seguimiento neuropsicológico cada 6-12 meses para monitorear evolución del perfil cognitivo.",
      ],
      estilo_vida: [
        "Actividad física aeróbica regular (mínimo 150 minutos semanales) como factor protector cognitivo.",
        "Dieta de estilo mediterráneo o MIND, con énfasis en vegetales, pescado, frutos secos y reducción de ultraprocesados.",
        "Higiene del sueño con horarios estables, 7-8 horas nocturnas, evaluación de apnea si hay ronquido o somnolencia diurna.",
        "Participación social activa: clubes, voluntariado, grupos familiares. El aislamiento es factor de riesgo.",
      ],
      medico: [
        "Control metabólico estricto: hipertensión, diabetes, dislipidemia, hipotiroidismo si aplica.",
        "Revisar polifarmacia, especialmente anticolinérgicos y benzodiazepinas, con el médico tratante.",
        "Tamizaje de déficits nutricionales (B12, folato, vitamina D) y depresión subyacente.",
      ],
      familiar: [
        "Psicoeducación a la familia sobre el concepto de DCL y su diferencia con demencia establecida.",
        "Ajustar expectativas sobre conducción, manejo financiero y autonomía según hallazgos funcionales, sin retirar prematuramente.",
        "Registro de cambios en una bitácora para la próxima consulta.",
      ],
    },
  },
  demencia: {
    nombre: "Trastorno Neurocognitivo Mayor (Demencia)",
    cie: "F00-F03",
    keywords: ["demencia", "alzheimer", "tnc mayor", "deterioro global", "frontotemporal", "cuerpos lewy", "vascular"],
    categorias: {
      manejo_cognitivo: [
        "Terapia de estimulación cognitiva grupal o individual adaptada al estadio, con reminiscencia y orientación a la realidad cuando corresponda.",
        "Simplificar el entorno: reducir objetos superfluos, etiquetas en cajones/puertas, relojes y calendarios visibles.",
        "Rutina diaria estable y predecible; evitar cambios de domicilio o de cuidador cuando sea posible.",
      ],
      conductual: [
        "Identificar desencadenantes de agitación (dolor, hambre, frío, sobreestimulación) antes de considerar manejo farmacológico.",
        "Estrategias no farmacológicas primero: música familiar, caminatas, muñecas terapéuticas, actividad manual.",
        "Evitar confrontación directa; usar redirección y validación emocional.",
      ],
      seguridad: [
        "Asegurar el hogar: desconectar estufa cuando no se usa, retirar tapetes sueltos, instalar barras de apoyo en baño.",
        "Pulsera o tarjeta identificativa con contacto de emergencia. Valorar dispositivos de geolocalización si hay riesgo de deambulación.",
        "Retirar progresivamente la conducción de vehículos cuando haya indicadores de riesgo.",
      ],
      cuidador: [
        "Evaluar y prevenir sobrecarga del cuidador con instrumentos específicos (Zarit).",
        "Red de apoyo: grupos de familiares, respiro periódico, delegación de tareas entre familia.",
        "Asesoría legal temprana: poder preventivo, directrices anticipadas, decisiones financieras.",
      ],
    },
  },
  ansiedad: {
    nombre: "Trastorno de Ansiedad / Síntomas Ansiosos",
    cie: "F41",
    keywords: ["ansiedad", "preocupación", "pánico", "tag", "ansiedad generalizada", "fobia"],
    categorias: {
      terapeutico: [
        "Psicoterapia cognitivo-conductual con enfoque en reestructuración cognitiva y exposición graduada cuando aplique.",
        "Entrenamiento en técnicas de regulación emocional: respiración diafragmática, relajación muscular progresiva, grounding sensorial.",
        "Valoración por psiquiatría si los síntomas limitan el funcionamiento o persisten pese a intervención psicoterapéutica.",
      ],
      estilo_vida: [
        "Actividad física regular como estabilizador anímico y ansiolítico natural.",
        "Reducción de cafeína, nicotina y alcohol; revisar consumo nocturno de pantallas.",
        "Higiene del sueño; considerar mindfulness o yoga como prácticas complementarias.",
      ],
    },
  },
  depresion: {
    nombre: "Síntomas Depresivos",
    cie: "F32-F33",
    keywords: ["depresión", "ánimo bajo", "anhedonia", "tristeza", "desesperanza"],
    categorias: {
      terapeutico: [
        "Psicoterapia basada en evidencia (TCC, terapia interpersonal) con foco en activación conductual.",
        "Valoración por psiquiatría para evaluar pertinencia de manejo farmacológico.",
        "Si hay ideación suicida: contención, plan de seguridad y derivación urgente a red de salud mental.",
      ],
      estilo_vida: [
        "Activación conductual diaria: lista de actividades placenteras programadas aunque no haya motivación inicial.",
        "Exposición a luz natural en la mañana; ejercicio aeróbico regular.",
        "Recuperación de redes de apoyo social; evitar el aislamiento.",
      ],
    },
  },
  dano_cerebral_adquirido: {
    nombre: "Daño Cerebral Adquirido (TCE, ACV, post-quirúrgico)",
    cie: "S06 / I63",
    keywords: ["tce", "acv", "trauma craneal", "ictus", "ecv", "post quirúrgico", "secuelas cerebrales"],
    categorias: {
      rehabilitacion: [
        "Neurorrehabilitación interdisciplinaria: neuropsicología, fonoaudiología, terapia física y ocupacional según perfil de secuelas.",
        "Entrenamiento en estrategias compensatorias para memoria (externas: agenda, alarmas) y atención (pausas programadas, ambiente controlado).",
        "Intervención en metacognición para reconocer propias limitaciones y solicitar ayuda oportuna.",
      ],
      ocupacional: [
        "Reintegro laboral progresivo, con ajuste de funciones al perfil cognitivo residual. Evitar reincorporación total abrupta.",
        "Informe neuropsicológico para medicina laboral con recomendaciones específicas sobre capacidades y restricciones.",
      ],
      familiar: [
        "Psicoeducación familiar sobre cambios conductuales y emocionales esperables tras daño cerebral.",
        "Acompañamiento emocional: el paciente y la familia pueden requerir psicoterapia por duelo por la identidad previa.",
      ],
    },
  },
  covid_secuelas: {
    nombre: "Secuelas cognitivas post-COVID",
    cie: "U09.9",
    keywords: ["covid", "niebla mental", "brain fog", "post covid", "long covid", "secuelas covid"],
    categorias: {
      cognitivo: [
        "Programa de reentrenamiento cognitivo gradual con énfasis en atención, velocidad de procesamiento y memoria de trabajo.",
        "Ajuste de cargas cognitivas progresivas, evitando sobreesfuerzos que prolongan el malestar post-actividad.",
        "Reevaluación a 3 y 6 meses para documentar evolución.",
      ],
      medico: [
        "Seguimiento por medicina interna para valorar comorbilidades persistentes (disautonomía, fatiga crónica, disnea).",
        "Tamizaje de depresión, ansiedad y trastornos del sueño secundarios.",
      ],
      estilo_vida: [
        "Gestión del ritmo actividad-descanso (pacing) para evitar el empeoramiento post-esfuerzo.",
        "Higiene del sueño rigurosa y reintroducción gradual de actividad física guiada.",
      ],
    },
  },

  tempo_cognitivo_lento: {
    nombre: "Tempo Cognitivo Lento / CDHS",
    cie: "F98.8",
    keywords: ["tcl", "tempo cognitivo lento", "cdhs", "lentitud", "soñar despierto", "hipoactividad", "desconexión cognitiva"],
    categorias: {
      cognitivo: [
        "Entrenamiento en autorregulación atencional: técnicas de anclaje, señales visuales que indiquen el retorno a la tarea.",
        "Uso de rutinas muy estructuradas con recordatorios visuales frecuentes y tareas de corta duración.",
        "Actividades de alta demanda atencional con refuerzo inmediato al mantenimiento de la atención (no solo a la tarea terminada).",
        "Diferenciar del TDAH: el TCL no responde igual a estimulantes; estrategias conductual-cognitivas son prioritarias.",
      ],
      familiar: [
        "Psicoeducación a la familia sobre el TCL como patrón de lentitud cognitiva, no pereza ni falta de voluntad.",
        "Reducir expectativas de velocidad; dar tiempo adicional antes de solicitar respuesta.",
        "Proporcionar ambiente sin distracciones y con apoyo visual externo para orientar tareas.",
      ],
      escolar: [
        "Tiempo extra en evaluaciones y tareas escritas.",
        "Instrucciones por escrito además de verbales; repetición cuando el paciente no responde inmediatamente.",
        "Posición estratégica en el aula, cerca del docente, lejos de ventanas y pasillos.",
        "Permitir al estudiante hacer preguntas sin penalización; fomentar la participación en clima de seguridad.",
      ],
      medico: [
        "Descartar hipotiroidismo, déficit de hierro, anemia, trastornos del sueño como factores contribuyentes.",
        "Evaluación de estado de ánimo (GDS-15 o PHQ-9): la depresión puede manifestarse como lentitud.",
      ],
    },
  },

  alteraciones_neuropsiquiatricas: {
    nombre: "Alteraciones Neuropsiquiátricas (demencias / DA / ACV)",
    cie: "F09",
    keywords: ["neuropsiquiatrico", "apatia", "agitacion", "alucinaciones", "delirios", "desinhibicion", "labilidad", "irritabilidad", "demencia conductual"],
    categorias: {
      manejo_conductual: [
        "Aplicar estrategia DICE (Describir conducta, Investigar causas, Crear plan, Evaluar). No medicar antes de descartar causas ambientales.",
        "Para agitación/agresión: identificar desencadenantes (dolor, necesidades básicas insatisfechas, confusión ambiental).",
        "Para apatía: actividades estructuradas, cortas, con significado personal previo; refuerzo positivo inmediato.",
        "Para desinhibición: supervisión cercana, reencuadre y redirección; evitar confrontación directa.",
        "Para labilidad emocional: respuesta tranquila del cuidador, evitar sobre-estimulación emocional.",
      ],
      cuidador: [
        "Psicoeducación sobre síntomas neuropsiquiátricos: son síntomas de la enfermedad, no conductas intencionales.",
        "Grupos de apoyo para cuidadores y programas de respiro.",
        "Evaluación periódica de sobrecarga del cuidador (Escala de Zarit).",
        "Coordinación con psiquiatría para manejo farmacológico si síntomas severos o refractarios.",
      ],
      ambiental: [
        "Adaptar el entorno: reducir ruido, mantener iluminación adecuada, rutinas predecibles y horarios estables.",
        "Señales visuales claras (letreros, fotos) para orientación en el hogar.",
        "Supervisión de medicación; revisar polifarmacia como posible factor desencadenante.",
      ],
    },
  },

  integracion_sensorial: {
    nombre: "Trastorno del Procesamiento Sensorial / Integración Sensorial",
    cie: "F88",
    keywords: ["integracion sensorial", "procesamiento sensorial", "hipersensibilidad", "hiposensibilidad", "sensory processing"],
    categorias: {
      terapeutico: [
        "Valoración por terapia ocupacional especializada en integración sensorial (SI) para elaborar perfil sensorial completo.",
        "Programa de dieta sensorial individualizado según hiper/hiposensibilidades identificadas.",
        "Técnicas de modulación sensorial: actividades propioceptivas, vestibulares o táctiles según el perfil.",
        "Integración de input sensorial de manera gradual y controlada en el contexto natural del niño.",
      ],
      escolar: [
        "Adecuaciones ambientales: reducir iluminación fluorescente parpadeante, nivel de ruido y texturas aversivas.",
        "Incorporar pausas sensoriales programadas (espacio calmo, materiales específicos).",
        "Permitir uso de audífonos con cancelación activa si hipersensibilidad auditiva.",
        "Coordinar con docentes sobre las características sensoriales del estudiante.",
      ],
      familiar: [
        "Psicoeducación sobre el procesamiento sensorial diferente del hijo/a: no capricho, sino diferencia neurológica.",
        "Adaptar el hogar: ropa sin costuras, alimentos con texturas toleradas, espacios seguros para autorregulación.",
        "Anticipar situaciones de sobre-estimulación (ambientes ruidosos, ferias, supermercados).",
        "Estrategias de apoyo ante meltdown/shutdown: espacio seguro, técnicas de calma sin forzar contacto.",
      ],
    },
  },

  neuropsicologia_forense: {
    nombre: "Evaluación para Fines Legales / Pensión / Discapacidad",
    cie: "Z04",
    keywords: ["forense", "pension", "discapacidad", "legal", "incapacidad", "minuto", "pjr", "calificacion", "junta"],
    categorias: {
      proceso: [
        "La evaluación debe realizarse con criterios de validez de síntomas (pruebas de esfuerzo cognitivo, p.ej. Rey 15-item Test).",
        "Documentar las condiciones de evaluación, nivel de esfuerzo aparente y cooperación del evaluado.",
        "El informe debe ser descriptivo, preciso y basado únicamente en datos objetivos.",
        "Evitar lenguaje diagnóstico conclusivo sin respaldo en datos; distinguir rendimiento cognitivo de capacidad funcional.",
      ],
      informe: [
        "Incluir: datos sociodemográficos completos, historia clínica relevante, pruebas aplicadas, puntajes y percentiles.",
        "No incluir recomendaciones de tratamiento que puedan sesgar la evaluación forense.",
        "Consignar limitaciones del estudio y condiciones que puedan afectar la interpretación.",
      ],
      derivacion: [
        "Si se detecta posible simulación o exageración de síntomas: documentar, NO confrontar al paciente.",
        "Derivar a psiquiatría si se sospecha trastorno facticio o ganancia secundaria.",
      ],
    },
  },

  tept: {
    nombre: "Trastorno por Estrés Postraumático (TEPT)",
    cie: "F43.1",
    keywords: ["ptsd", "tept", "trauma", "estrés postraumático", "estrés agudo", "flashback", "reexperimentación", "evitación"],
    categorias: {
      terapeutico: [
        "La primera línea de tratamiento recomendada es la psicoterapia enfocada en el trauma: TF-CBT (niños/adolescentes) o CPT/PE (adultos) con terapeuta certificado.",
        "EMDR (Desensibilización y Reprocesamiento por Movimientos Oculares): evidencia nivel A para adultos, B para niños/adolescentes — derivar a profesional certificado.",
        "Valoración por psiquiatría para considerar farmacoterapia adjunta: sertraline o paroxetine son de primera línea.",
        "Evitar exposición innecesaria a estímulos traumáticos en sesión hasta que el paciente tenga herramientas de regulación emocional.",
        "Psicoeducación sobre la respuesta normal al trauma y los síntomas de TEPT: normalizar la experiencia sin minimizarla.",
        "Evaluación del riesgo de suicidio en cada sesión: el TEPT aumenta el riesgo especialmente en la fase de evitación.",
      ],
      familiar: [
        "Psicoeducación a la familia o cuidadores sobre TEPT: síntomas, triggers frecuentes y respuestas de apoyo adaptativas.",
        "Instruir al entorno sobre el manejo de flashbacks: anclaje sensorial, voz tranquila, no restringir físicamente sin consenso.",
        "Evitar en el hogar discusiones sobre los detalles del evento traumático sin preparación terapéutica previa.",
        "Fomentar rutinas predecibles y entornos seguros que reduzcan la activación del sistema nervioso.",
      ],
      escolar: [
        "Informar a orientación escolar (con consentimiento) para facilitar ajustes: tiempos adicionales, salida de actividades que generen alta activación.",
        "Reducir exposición a estímulos que puedan ser triggers en el contexto educativo (ruidos intensos, imágenes, noticias).",
        "Plan de manejo de crisis en el aula: identificar a un adulto de confianza al que el estudiante pueda acudir si experimenta reexperimentación.",
      ],
      cognitivo_rehabilitacion: [
        "El TEPT puede afectar memoria episódica, atención sostenida y funciones ejecutivas — evaluar y tratar déficits cognitivos secundarios.",
        "Técnicas de estabilización y regulación: respiración diafragmática, grounding sensorial (5-4-3-2-1), mindfulness adaptado.",
        "Registros de pensamiento cognitivo-conductual para abordar cogniciones traumáticas: culpa, vergüenza, amenaza permanente.",
      ],
    },
  },

  long_covid_cognitivo: {
    nombre: "Secuelas cognitivas post-COVID (niebla mental)",
    cie: "U09.9",
    keywords: ["long covid", "post covid", "niebla mental", "niebla cognitiva", "fatiga post viral", "brain fog"],
    categorias: {
      cognitivo_rehabilitacion: [
        "Rehabilitación cognitiva graduada: empezar por tareas de baja demanda cognitiva y aumentar progresivamente según tolerancia.",
        "Identificar el 'umbral de fatiga cognitiva' individual: registrar síntomas post-esfuerzo (PCE) y respetar periodos de descanso.",
        "Gestión del ritmo de actividades: técnica del 'pacing' — alternar periodos de actividad con descanso para evitar empeoramiento post-esfuerzo.",
        "Estrategias compensatorias: agendas, alarmas, listas de verificación para compensar déficits de memoria y atención.",
        "Trabajar velocidad de procesamiento con actividades graduadas: puzzles, lecturas cortas, ejercicios de atención sostenida.",
      ],
      medico: [
        "Derivar a medicina interna o unidad de Long COVID para descarte de comorbilidades: anemia, hipotiroidismo, déficit B12/D, apnea del sueño.",
        "Reportar y registrar síntomas autonómicos: POTS (taquicardia ortostática), mareos posturales — consulta cardiológica si aplica.",
        "Evaluar la calidad del sueño con escala de Epworth y PSQ; el insomnio y la hipersomnia contribuyen a la niebla cognitiva.",
        "La actividad física debe ser graduada y monitoreada — el ejercicio de alta intensidad puede empeorar el PEM (malestar post-esfuerzo).",
      ],
      familiar: [
        "Psicoeducación sobre la naturaleza del Long COVID: los síntomas son reales, no de origen psiquiátrico exclusivo.",
        "El entorno debe adaptar expectativas funcionales: evitar comparar el rendimiento actual con el previo a la infección.",
        "Facilitar la autonomía del paciente respetando sus límites energéticos — evitar sobreprotección que inhiba la recuperación.",
      ],
      escolar_laboral: [
        "Gestionar ajustes razonables: horario reducido, extensión de tiempos, posibilidad de trabajo/estudio remoto.",
        "Comunicar a docentes o empleadores el diagnóstico y los ajustes necesarios con soporte del equipo médico.",
        "Documentar incapacidades laborales adecuadamente para protección legal del trabajador.",
      ],
    },
  },
};

/* ── 2. ALGORITMOS DIAGNÓSTICOS (reglas de decisión) ──
 * Cada algoritmo tiene un conjunto de criterios. Se evalúan contra el
 * perfil del paciente y devuelven una impresión diagnóstica con nivel de
 * sospecha (alta / media / baja / no_indicativo).
 */
export const DIAGNOSTIC_ALGORITHMS = {
  discapacidad_intelectual: {
    nombre: "Discapacidad Intelectual",
    marco: "DSM-5 / CIE-10",
    criterios: [
      { id: "ci_total", pregunta: "CI total < 70 (–2 DE) en prueba válida", peso: 3 },
      { id: "adaptativo", pregunta: "Limitaciones en funcionamiento adaptativo (conceptual, social o práctico)", peso: 3 },
      { id: "onset", pregunta: "Inicio en el período de desarrollo (antes de 18 años)", peso: 2 },
      { id: "descarta_sensorial", pregunta: "Se descartan déficits sensoriales graves como causa primaria", peso: 1 },
    ],
    interpretacion: {
      alta: "Los tres criterios principales (CI, adaptativo, inicio) están presentes: impresión de DI probable.",
      media: "Algunos criterios presentes pero perfil mixto: ampliar evaluación funcional.",
      baja: "Criterios insuficientes para DI; revisar diagnósticos diferenciales.",
    },
  },
  tdah: {
    nombre: "TDAH",
    marco: "DSM-5",
    criterios: [
      { id: "inatencion", pregunta: "≥6 síntomas de inatención (niños) o ≥5 (adultos) según escalas", peso: 3 },
      { id: "hiperactividad", pregunta: "≥6 síntomas de hiperactividad/impulsividad (niños) o ≥5 (adultos)", peso: 2 },
      { id: "funciones_ejecutivas", pregunta: "Rendimiento bajo (≤-1 DE) en tareas ejecutivas (TMT-B, Stroop, CPT)", peso: 2 },
      { id: "ambientes", pregunta: "Síntomas en ≥2 ambientes (casa, colegio/trabajo, social)", peso: 2 },
      { id: "onset_12", pregunta: "Síntomas presentes antes de los 12 años", peso: 1 },
      { id: "no_mejor_explicado", pregunta: "No explicado mejor por otro trastorno (ansiedad, sueño, sustancia)", peso: 1 },
    ],
    interpretacion: {
      alta: "Patrón compatible con TDAH: sintomatología en múltiples ambientes + bajo rendimiento ejecutivo.",
      media: "Perfil sugestivo pero requiere complementar con escalas validadas y observación conductual.",
      baja: "Perfil no indicativo; considerar ansiedad, trastorno del sueño, problema visual/auditivo.",
    },
  },
  tea: {
    nombre: "TEA — Trastorno del Espectro Autista",
    marco: "DSM-5",
    criterios: [
      { id: "comunicacion_social", pregunta: "Déficits persistentes en comunicación social (reciprocidad, no verbal, relaciones)", peso: 3 },
      { id: "comportamientos_restringidos", pregunta: "Patrones restrictivos/repetitivos (≥2: estereotipias, rituales, intereses, sensorial)", peso: 3 },
      { id: "onset_temprano", pregunta: "Síntomas desde primera infancia (aunque puedan visibilizarse después)", peso: 2 },
      { id: "funcional", pregunta: "Afectación clínicamente significativa del funcionamiento", peso: 1 },
      { id: "descarta_di", pregunta: "No mejor explicado por discapacidad intelectual aislada", peso: 1 },
    ],
    interpretacion: {
      alta: "Perfil consistente con TEA: déficits sociales + patrones restrictivos + inicio temprano.",
      media: "Hallazgos parciales; ampliar con ADOS-2/ADI-R y observación en contexto natural.",
      baja: "Criterios insuficientes; valorar diagnósticos diferenciales (TEL, trastorno de apego, ansiedad social).",
    },
  },
  dea: {
    nombre: "Dificultad Específica del Aprendizaje",
    marco: "DSM-5",
    criterios: [
      { id: "area_especifica", pregunta: "Rendimiento bajo (≤-1.5 DE) en lectura, escritura o cálculo, específicamente", peso: 3 },
      { id: "ci_normal", pregunta: "CI global dentro del rango promedio o superior", peso: 3 },
      { id: "persistencia", pregunta: "Dificultades persistentes ≥6 meses pese a intervención escolar", peso: 2 },
      { id: "interfere", pregunta: "Interferencia significativa en rendimiento académico u ocupacional", peso: 2 },
      { id: "descarta_otros", pregunta: "No explicado por discapacidad intelectual, déficit sensorial o falta de instrucción", peso: 2 },
    ],
    interpretacion: {
      alta: "Patrón de DEA probable: déficit específico con inteligencia general preservada y exclusión de otras causas.",
      media: "Perfil parcial; discrepancia CI-rendimiento presente pero falta confirmar persistencia o especificidad.",
      baja: "No cumple criterios para DEA; considerar factores instruccionales, emocionales o TDAH comórbido.",
    },
  },
  /* §dedupe-fix (2026-05-18): la definición original de `dcl` (versión
   * abreviada) se eliminó porque más abajo en este mismo archivo, línea ~717,
   * hay una definición más completa con marco DSM-5 + Petersen 2004 + Winblad
   * revisado. JavaScript usa la última (sobrescribe), así que la primera era
   * dead code y, peor, podía confundir si alguien la editaba sin saber. */
  demencia: {
    nombre: "Demencia (TNC mayor)",
    marco: "DSM-5 / CIE-10 · TNC mayor",
    cie10: "F00–F03",
    criterios: [
      { id: "declive_objetivo",    pregunta: "Declive significativo (≤-2 DE) respecto al nivel previo en ≥1 dominio cognitivo", peso: 3 },
      { id: "multidominio",        pregunta: "Alteración en ≥2 dominios cognitivos (memoria, ejecutivas, lenguaje, visoespacial, etc.)", peso: 2 },
      { id: "interferencia_avd",   pregunta: "Interferencia significativa en actividades de la vida diaria (instrumentales o básicas)", peso: 3 },
      { id: "no_delirium",         pregunta: "Los déficits no ocurren exclusivamente durante un delirium", peso: 2 },
      { id: "no_otro_trastorno",   pregunta: "No mejor explicado por otro trastorno mental (depresión mayor, esquizofrenia)", peso: 2 },
      { id: "etiologia_identificable", pregunta: "Historia/imágenes sugieren etiología (Alzheimer, vascular, frontotemporal, cuerpos de Lewy)", peso: 1 },
    ],
    interpretacion: {
      alta: "Perfil compatible con TNC mayor (demencia). Referir a neurología, coordinar estudios de imagen y valoración funcional.",
      media: "Hallazgos parciales; confirmar con informante, descartar depresión/delirium y repetir evaluación en 3-6 meses.",
      baja: "Criterios insuficientes para demencia; considerar DCL, depresión o efecto de medicación.",
    },
  },
  dano_cerebral: {
    nombre: "Daño Cerebral Adquirido / TNC debido a TCE",
    marco: "DSM-5 · TNC debido a lesión cerebral",
    cie10: "F07.2 / S06",
    criterios: [
      { id: "evento",          pregunta: "Evento identificable (TCE, ACV, hipoxia, tumor, infección SNC, cirugía)", peso: 3 },
      { id: "cambio_post",     pregunta: "Cambio cognitivo/conductual temporalmente asociado al evento", peso: 3 },
      { id: "deficit_focal",   pregunta: "Patrón compatible con localización de la lesión (focal o difuso)", peso: 2 },
      { id: "persistencia",    pregunta: "Déficits persisten >6 meses (estabilidad o mejoría lenta)", peso: 1 },
      { id: "no_premorbido",   pregunta: "Sin evidencia de deterioro equivalente previo al evento", peso: 2 },
    ],
    interpretacion: {
      alta: "Cuadro consistente con secuelas neuropsicológicas del evento documentado. Diseñar plan de rehabilitación.",
      media: "Hallazgos compatibles; correlacionar con imágenes y descartar factores comórbidos (dolor, medicación, afecto).",
      baja: "Relación causal débil; investigar factores premórbidos, psicógenos o efectos medicamentosos.",
    },
  },
  depresion: {
    nombre: "Trastorno Depresivo Mayor",
    marco: "DSM-5 · F32/F33 CIE-10",
    cie10: "F32 / F33",
    criterios: [
      { id: "estado_animo",   pregunta: "Ánimo deprimido la mayor parte del día, casi todos los días (≥2 semanas)", peso: 3 },
      { id: "anhedonia",      pregunta: "Disminución marcada del interés o placer en casi todas las actividades", peso: 3 },
      { id: "sintomas_asoc",  pregunta: "≥3 síntomas adicionales: sueño, apetito, psicomotor, fatiga, culpa, concentración, ideación", peso: 2 },
      { id: "interferencia",  pregunta: "Malestar clínicamente significativo o deterioro funcional", peso: 2 },
      { id: "no_sustancia",   pregunta: "No atribuible a sustancia o condición médica general", peso: 1 },
      { id: "pseudodemencia", pregunta: "Quejas cognitivas desproporcionadas al rendimiento objetivo (pseudodemencia depresiva)", peso: 1 },
    ],
    interpretacion: {
      alta: "Patrón compatible con Trastorno Depresivo Mayor. Correlacionar con BDI-II/HAM-D y considerar impacto en rendimiento cognitivo.",
      media: "Síntomas depresivos presentes pero perfil parcial; considerar distimia, ajuste o duelo.",
      baja: "No cumple criterios plenos; descartar ansiedad, anhedonia por fatiga o trastorno del sueño.",
    },
  },
  ansiedad: {
    nombre: "Trastorno de Ansiedad Generalizada",
    marco: "DSM-5 · F41.1 CIE-10",
    cie10: "F41.1",
    criterios: [
      { id: "preocupacion",   pregunta: "Ansiedad/preocupación excesiva ≥6 meses sobre múltiples eventos", peso: 3 },
      { id: "dificil_control",pregunta: "El paciente encuentra difícil controlar la preocupación", peso: 2 },
      { id: "sintomas_fisicos", pregunta: "≥3 síntomas: inquietud, fatiga, concentración, irritabilidad, tensión muscular, sueño", peso: 2 },
      { id: "interferencia",  pregunta: "Malestar o deterioro significativo en áreas importantes", peso: 2 },
      { id: "no_sustancia",   pregunta: "No atribuible a sustancias ni condición médica", peso: 1 },
      { id: "no_otro",        pregunta: "No mejor explicado por otro trastorno mental (p. ej., pánico, TOC, TEA)", peso: 1 },
    ],
    interpretacion: {
      alta: "Perfil compatible con TAG. Complementar con STAI/GAD-7; intervención psicoterapéutica indicada.",
      media: "Síntomas de ansiedad parciales; considerar ansiedad situacional, fobia específica o ajuste.",
      baja: "Criterios insuficientes para TAG; revisar factores contextuales o comorbilidad.",
    },
  },
  tce_postraumatico: {
    nombre: "Síndrome postconmocional / TNC debido a TCE",
    marco: "DSM-5 · TNC debido a lesión cerebral traumática",
    cie10: "F072 / S06",
    criterios: [
      { id: "evento_tce", pregunta: "Antecedente documentado de TCE (cerrado o penetrante) con evidencia (Glasgow, imagen, pérdida de conciencia, amnesia post-traumática)", peso: 3 },
      { id: "linea_temporal", pregunta: "Cambio cognitivo iniciado o exacerbado tras el evento (línea temporal clara)", peso: 3 },
      { id: "atencion_velocidad", pregunta: "Afectación de atención sostenida y/o velocidad de procesamiento (≤-1 DE)", peso: 2 },
      { id: "memoria_episodica", pregunta: "Memoria episódica afectada (consolidación o recuperación)", peso: 2 },
      { id: "ejecutivas", pregunta: "Disfunción ejecutiva (planeación, inhibición, flexibilidad)", peso: 2 },
      { id: "conducta", pregunta: "Cambios conductuales (irritabilidad, apatía, desinhibición)", peso: 1 },
      { id: "no_premorbido", pregunta: "Estos cambios NO eran característicos del paciente antes del TCE", peso: 1 },
      { id: "interferencia", pregunta: "Interferencia clínicamente significativa con AVD/laboral/social", peso: 2 },
    ],
    interpretacion: {
      alta: "Perfil compatible con secuelas neuropsicológicas de TCE. Coordinar rehabilitación cognitiva específica + manejo conductual + psicoeducación familiar. Reevaluar a 6 meses.",
      media: "Hallazgos parciales; descartar superposición con TEPT, depresión reactiva o efecto medicamentoso. Considerar profundizar con APT (Sohlberg).",
      baja: "Criterios insuficientes para atribuir las dificultades al TCE; considerar otras etiologías o cuadros comórbidos.",
    },
  },
  trastorno_lenguaje: {
    nombre: "Trastorno del Desarrollo del Lenguaje (TDL / disfasia evolutiva)",
    marco: "DSM-5 · Trastornos del neurodesarrollo",
    cie10: "F803 / F800 / F801",
    criterios: [
      { id: "vocabulario_reducido", pregunta: "Vocabulario expresivo reducido respecto al esperado para edad/escolaridad", peso: 2 },
      { id: "estructuracion", pregunta: "Dificultad en la estructuración de oraciones (sintaxis) y/o discurso narrativo", peso: 3 },
      { id: "comprensión", pregunta: "Comprensión verbal afectada (Token Test ≤-1.5 DE o BNT con muchas anomias)", peso: 2 },
      { id: "ci_normal", pregunta: "CI no verbal dentro de rango promedio o superior (descarta DI primaria)", peso: 2 },
      { id: "no_sensorial", pregunta: "Audición y visión preservadas (descarta hipoacusia)", peso: 2 },
      { id: "no_tea", pregunta: "Comunicación social adecuada en lo no verbal (descarta TEA primario)", peso: 1 },
      { id: "onset_temprano", pregunta: "Síntomas presentes desde el período del desarrollo del lenguaje (3-5 años)", peso: 2 },
      { id: "interferencia_escolar", pregunta: "Interfiere con rendimiento escolar / comunicación cotidiana", peso: 2 },
    ],
    interpretacion: {
      alta: "Perfil consistente con TDL. Derivar a fonoaudiología; coordinar plan escolar con adaptaciones (más tiempo de procesamiento, apoyos visuales, evaluación oral).",
      media: "Hallazgos parciales; descartar dislexia comórbida, hipoacusia leve o efecto de bilingüismo en transición. Reevaluar tras 3-6 meses de intervención.",
      baja: "Criterios insuficientes; valorar variación normal del desarrollo o factores ambientales (estimulación lingüística limitada).",
    },
  },
  long_covid: {
    nombre: "Secuelas cognitivas post-COVID (Long COVID / niebla mental)",
    marco: "OMS (post-COVID condition) / DSM-5 TNC inducido por condición médica",
    cie10: "U09.9",
    criterios: [
      { id: "antecedente_covid", pregunta: "Antecedente confirmado o probable de infección por SARS-CoV-2", peso: 3 },
      { id: "duracion_3_meses", pregunta: "Síntomas persistentes ≥12 semanas tras la infección aguda", peso: 3 },
      { id: "velocidad_baja", pregunta: "Velocidad de procesamiento baja (≤-1 DE en SDMT/Claves WAIS)", peso: 2 },
      { id: "ejecutivas_afectadas", pregunta: "Inhibición o resolución de problemas afectada (Stroop, TMT-B, INECO)", peso: 2 },
      { id: "memoria_corto_plazo", pregunta: "Recuperación de información verbal disminuida (HVLT/CVLT)", peso: 2 },
      { id: "queja_funcional", pregunta: "Empeoramiento del rendimiento laboral/escolar referido por el paciente", peso: 2 },
      { id: "no_explica_otro", pregunta: "No mejor explicado por depresión mayor activa, hipotiroidismo, trastorno del sueño primario", peso: 1 },
    ],
    interpretacion: {
      alta: "Perfil compatible con secuelas cognitivas post-COVID. Combinar rehabilitación cognitiva + manejo del sueño + actividad física graduada. Reevaluar a 3 meses.",
      media: "Hallazgos sugestivos parciales. Descartar depresión post-infección, déficit de B12/ferritina, apnea del sueño. Considerar repetir evaluación.",
      baja: "Criterios insuficientes para atribuir las dificultades a Long COVID; valorar otras causas reversibles.",
    },
  },

  tempo_cognitivo_lento: {
    nombre: "Tempo Cognitivo Lento (TCL) / CDHS",
    marco: "Barkley 2012 / DSM-5 (investigación) — no diagnóstico oficial DSM-5/CIE-11",
    criterios: [
      { id: "ivp_selectivo", pregunta: "IVP significativamente bajo (≤85) con ICV e IRP en rango promedio (≥90)", peso: 3 },
      { id: "ensonyacion", pregunta: "Ensoñación diurna excesiva: se pierde en sus propios pensamientos, parece ausente", peso: 2 },
      { id: "hipoactividad", pregunta: "Movimientos lentos o escasos, hipoactividad general sin causa médica", peso: 2 },
      { id: "confusion_mental", pregunta: "Confusión mental reportada: niebla cognitiva, lentitud para comprender", peso: 2 },
      { id: "no_hiperactividad", pregunta: "Ausencia de hiperactividad motora significativa (no cumple TDAH-hiperactivo)", peso: 1 },
      { id: "duracion_6m", pregunta: "Síntomas presentes por ≥6 meses, inapropiados para la edad", peso: 2 },
      { id: "no_depresion", pregunta: "No mejor explicado por Trastorno Depresivo Mayor activo", peso: 2 },
    ],
    interpretacion: {
      alta: "Perfil compatible con Tempo Cognitivo Lento (CDHS). Verificar: trastornos del sueño, hipotiroidismo, déficit de hierro. Diferencial con TDAH inatento: el TCL NO responde igual a estimulantes.",
      media: "Hallazgos parcialmente sugestivos. Profundizar en síntomas de ensoñación, hipoactividad y niebla mental. Descartar depresión, hipotiroidismo y apnea del sueño.",
      baja: "Criterios insuficientes para TCL; considerar TDAH inatento, depresión o hipotiroidismo.",
    },
  },

  integracion_sensorial: {
    nombre: "Trastorno del Procesamiento Sensorial",
    marco: "Ayres SI Framework / DSM-5 especificador TEA (sensorial)",
    criterios: [
      { id: "hipersensibilidad", pregunta: "Hipersensibilidad a estímulos: auditivos, táctiles, olfatorios, visuales o gustativos", peso: 2 },
      { id: "hiposensibilidad", pregunta: "Hiposensibilidad o búsqueda excesiva de estimulación sensorial", peso: 2 },
      { id: "impacto_funcional", pregunta: "Impacto en funcionamiento cotidiano (ropa, alimentación, entorno escolar)", peso: 3 },
      { id: "patron_persistente", pregunta: "Patrón persistente por ≥6 meses en múltiples contextos", peso: 2 },
      { id: "no_exclusion", pregunta: "No mejor explicado por condición sensorial primaria (sordera, ceguera)", peso: 1 },
    ],
    interpretacion: {
      alta: "Perfil sugestivo de trastorno del procesamiento sensorial. Derivar a terapia ocupacional especializada en Integración Sensorial para perfil sensorial completo y dieta sensorial individualizada.",
      media: "Hallazgos parciales. Profundizar con cuestionarios de perfil sensorial (SPM, SSPQ). Evaluar comorbilidad con TEA.",
      baja: "Criterios insuficientes. Los síntomas pueden ser situacionales o relacionados con otro trastorno.",
    },
  },

  tce: {
    nombre: "TCE — Traumatismo Craneoencefálico con secuelas neuropsicológicas",
    marco: "DSM-5 TNC Debido a TCE / GCS + criterios TNC Mayor/Leve",
    criterios: [
      { id: "antecedente_tce", pregunta: "Antecedente documentado de TCE con pérdida de conciencia, amnesia post-traumática o alteración neurológica aguda", peso: 3 },
      { id: "velocidad_afectada", pregunta: "Velocidad de procesamiento reducida (IVP/TMT-A/B enlentecidos)", peso: 2 },
      { id: "ejecutivas_afectadas", pregunta: "Disfunción ejecutiva: inhibición, planificación, flexibilidad cognitiva afectadas", peso: 2 },
      { id: "memoria", pregunta: "Memoria explícita afectada (verbal o visual)", peso: 2 },
      { id: "neuro_psiq", pregunta: "Síntomas neuropsiquiátricos (irritabilidad, apatía, desinhibición, ansiedad)", peso: 2 },
      { id: "impacto_funcional", pregunta: "Impacto significativo en funcionamiento laboral, académico o social", peso: 2 },
    ],
    interpretacion: {
      alta: "Perfil compatible con secuelas neuropsicológicas de TCE. Derivar a neurología + neurorrehabilitación. Reportar a EPS o ARL según corresponda (accidente laboral/tránsito).",
      media: "Hallazgos parcialmente compatibles con TCE. Profundizar en historia del trauma y síntomas agudos. Descartar TEPT comórbido.",
      baja: "Criterios insuficientes; considerar otras etiologías del perfil cognitivo.",
    },
  },

  tept: {
    nombre: "Trastorno por Estrés Postraumático (TEPT)",
    marco: "DSM-5 / CIE-11",
    cie10: "F43.1",
    criterios: [
      { id: "evento_a", pregunta: "Criterio A: Exposición a muerte real/amenazada, lesión grave o violencia sexual (directo, testigo, indirecto o exposición extrema)", peso: 3 },
      { id: "intrusion_b", pregunta: "Criterio B: ≥1 síntoma de intrusión (flashbacks, pesadillas, malestar intenso a recordatorios, reacciones fisiológicas)", peso: 3 },
      { id: "evitacion_c", pregunta: "Criterio C: ≥1 síntoma de evitación (pensamientos, lugares, personas asociados al trauma)", peso: 2 },
      { id: "cognicion_d", pregunta: "Criterio D: ≥2 síntomas de cognición/estado de ánimo negativo (amnesia, creencias negativas, culpa, emociones negativas, anhedonia, alienación)", peso: 2 },
      { id: "arousal_e", pregunta: "Criterio E: ≥2 síntomas de hiperactivación/reactividad (irritabilidad, conductas autodestructivas, hipervigilancia, sobresalto, sueño, concentración)", peso: 2 },
      { id: "duracion_f", pregunta: "Criterio F: Duración > 1 mes", peso: 1 },
      { id: "impacto_g", pregunta: "Criterio G: Malestar clínico significativo o deterioro del funcionamiento", peso: 1 },
    ],
    interpretacion: {
      alta: "Cumplimiento de los cinco criterios DSM-5 (A-G): TEPT probable. Derivar a psicoterapia especializada (TF-CBT/CPT/PE/EMDR) y evaluación psiquiátrica para farmacoterapia.",
      media: "Criterios parcialmente cumplidos: considerar Trastorno de Estrés Agudo, Trastorno de Adaptación o TEPT subclínico. Profundizar con CAPS-5 o PCL-5.",
      baja: "Criterios insuficientes para TEPT; valorar depresión, ansiedad, duelo complicado.",
    },
  },

  dcl: {
    nombre: "Deterioro Cognitivo Leve (DCL / TNC Leve)",
    marco: "DSM-5 / Petersen 2004 / Criterios Winblad revisados",
    cie10: "G31.84",
    criterios: [
      { id: "queja", pregunta: "Queja cognitiva subjetiva (del paciente o informante)", peso: 1 },
      { id: "objetivo_1de", pregunta: "Rendimiento ≤-1 DE en ≥1 dominio cognitivo en prueba estandarizada", peso: 3 },
      { id: "preserva_funcional", pregunta: "Funcionamiento instrumental y laboral esencialmente preservado", peso: 2 },
      { id: "no_demencia", pregunta: "No cumple criterios de demencia (TNC Mayor)", peso: 2 },
      { id: "descarte_depresion", pregunta: "Síntomas no mejor explicados por depresión mayor activa (GDS-15 < 5)", peso: 2 },
      { id: "descarte_delirium", pregunta: "No hay delirium ni otra causa médica aguda", peso: 1 },
    ],
    interpretacion: {
      alta: "DCL probable: queja + déficit objetivo + función preservada + sin depresión mayor. Seguimiento 6-12 meses + GDS + FAQ. Derivar a neurología.",
      media: "Hallazgos sugestivos. Descartar depresión (Yesavage), hipotiroidismo, déficit B12. Repetir evaluación en 6 meses.",
      baja: "Criterios insuficientes. Si hay queja subjetiva sin déficit objetivo: TCL subjetivo — seguimiento anual.",
    },
  },
};

/* ── 2.b · Diagnósticos DSM-5 estructurados ─────────────────────────────
 * Mapa id → {codigo_cie10, dsm5_seccion, criterios_esenciales (A,B,C,...)}
 * Pensado para el "DSM-5 Picker" de la impresión diagnóstica. */
export const DSM5_DIAGNOSES = {
  // NEURODESARROLLO
  F70:  { nombre: "Discapacidad intelectual leve",           dsm5: "Trastornos del neurodesarrollo", ci_rango: "50-69" },
  F71:  { nombre: "Discapacidad intelectual moderada",       dsm5: "Trastornos del neurodesarrollo", ci_rango: "35-49" },
  F72:  { nombre: "Discapacidad intelectual grave",          dsm5: "Trastornos del neurodesarrollo", ci_rango: "20-34" },
  F73:  { nombre: "Discapacidad intelectual profunda",       dsm5: "Trastornos del neurodesarrollo", ci_rango: "<20" },
  F840: { nombre: "Trastorno del espectro autista",          dsm5: "Trastornos del neurodesarrollo" },
  // §S1.6-fix: CIE-10 oficial. F90.0 = "Trastorno de la actividad y de la
  // atención" (predominio inatento). F90.1 = "Trastorno hipercinético
  // disocial" (con síntomas hiperactivo-impulsivos + disocial). F90.9 =
  // "Sin especificación" (presentación combinada cuando DSM-5 usa 3
  // presentaciones). F988 NO es código de TDAH (F98.8 = "Otros
  // trastornos comportamiento/emociones inicio infancia").
  F900: { nombre: "TDAH — Trastorno de la actividad y de la atención (F90.0, predominio inatento)", dsm5: "Trastornos del neurodesarrollo" },
  F901: { nombre: "TDAH — Trastorno hipercinético disocial (F90.1, predominio hiperactivo/impulsivo + disocial)", dsm5: "Trastornos del neurodesarrollo" },
  F909: { nombre: "TDAH — Trastorno hipercinético sin especificación (F90.9, presentación combinada)", dsm5: "Trastornos del neurodesarrollo" },
  F810: { nombre: "Trastorno específico del aprendizaje — lectura",    dsm5: "Trastornos del neurodesarrollo" },
  F811: { nombre: "Trastorno específico del aprendizaje — escritura",  dsm5: "Trastornos del neurodesarrollo" },
  F812: { nombre: "Trastorno específico del aprendizaje — cálculo",    dsm5: "Trastornos del neurodesarrollo" },
  F803: { nombre: "Trastorno del lenguaje",                  dsm5: "Trastornos del neurodesarrollo" },
  // TNC
  F03:  { nombre: "Demencia no especificada",                dsm5: "Trastornos neurocognitivos" },
  F000: { nombre: "Demencia tipo Alzheimer (inicio precoz)", dsm5: "Trastornos neurocognitivos" },
  F001: { nombre: "Demencia tipo Alzheimer (inicio tardío)", dsm5: "Trastornos neurocognitivos" },
  F010: { nombre: "Demencia vascular",                       dsm5: "Trastornos neurocognitivos" },
  F020: { nombre: "Demencia por enfermedad de Pick (FTD)",   dsm5: "Trastornos neurocognitivos" },
  G3184:{ nombre: "Deterioro cognitivo leve",                dsm5: "Trastornos neurocognitivos (TNC leve)" },
  F072: { nombre: "Síndrome postconmocional / TNC debido a TCE", dsm5: "TNC debido a lesión cerebral traumática" },
  F04:  { nombre: "Síndrome amnésico orgánico",              dsm5: "Trastornos neurocognitivos" },
  // AFECTIVOS
  F320: { nombre: "Episodio depresivo leve",                 dsm5: "Trastornos depresivos" },
  F321: { nombre: "Episodio depresivo moderado",             dsm5: "Trastornos depresivos" },
  F322: { nombre: "Episodio depresivo grave sin psicosis",   dsm5: "Trastornos depresivos" },
  F330: { nombre: "Trastorno depresivo recurrente",          dsm5: "Trastornos depresivos" },
  F341: { nombre: "Distimia / Trastorno depresivo persistente", dsm5: "Trastornos depresivos" },
  // ANSIEDAD
  F410: { nombre: "Trastorno de pánico",                     dsm5: "Trastornos de ansiedad" },
  F411: { nombre: "Trastorno de ansiedad generalizada",      dsm5: "Trastornos de ansiedad" },
  F400: { nombre: "Agorafobia",                              dsm5: "Trastornos de ansiedad" },
  F401: { nombre: "Fobia social / Trastorno de ansiedad social", dsm5: "Trastornos de ansiedad" },
  F930: { nombre: "Trastorno de ansiedad por separación",    dsm5: "Trastornos de ansiedad" },
  // TRAUMA
  F431: { nombre: "Trastorno por estrés postraumático (TEPT)",        dsm5: "Trastornos asociados a trauma" },
  F438: { nombre: "Trastorno de estrés agudo",                        dsm5: "Trastornos asociados a trauma" },
  F432: { nombre: "Trastorno de adaptación",                          dsm5: "Trastornos asociados a trauma" },
  F438C:{ nombre: "TEPT complejo (CIE-11 6B41) — por trauma crónico", dsm5: "Trastornos asociados a trauma (CIE-11)", cie11: "6B41" },
  F94P:  { nombre: "Trastorno de duelo prolongado (DSM-5-TR)", dsm5: "Trastornos relacionados con trauma y factores de estrés", cie11: "6B42" },
  R4581: { nombre: "Comportamiento suicida actual — encuentro inicial", dsm5: "Otros problemas de atención clínica (DSM-5-TR)", z: true },
  R4582: { nombre: "Antecedentes de conducta suicida", dsm5: "Otros problemas de atención clínica (DSM-5-TR)", z: true },
  R4583: { nombre: "Autolesiones no suicidas actuales", dsm5: "Otros problemas de atención clínica (DSM-5-TR)", z: true },
  // NEUROLÓGICOS / POST-INFECCIOSOS
  U099: { nombre: "Condición post-COVID / Secuelas Long COVID",        dsm5: "TNC inducido por condición médica" },
  F068: { nombre: "TNC leve debido a condición médica (post-COVID, post-ACV, etc.)", dsm5: "Trastornos neurocognitivos" },
  // OTROS
  F421: { nombre: "Trastorno obsesivo-compulsivo (TOC)",               dsm5: "Trastornos obsesivo-compulsivos" },
  F50:  { nombre: "Trastornos de la conducta alimentaria",             dsm5: "TCA" },
  F20:  { nombre: "Esquizofrenia",                                     dsm5: "Trastornos del espectro esquizofrénico" },
  F250: { nombre: "Trastorno esquizoafectivo",                         dsm5: "Trastornos del espectro esquizofrénico" },
  F198: { nombre: "Trastorno cognitivo por uso de sustancias",         dsm5: "Trastornos por consumo de sustancias" },
  F70Z: { nombre: "Z-code · Sin diagnóstico psiquiátrico formal",      dsm5: "Evaluación sin diagnóstico", z: true },
};

/* ── 2b. CIE-10 SUGERIDOS POR POBLACIÓN ───────────────────────────────────
 * Códigos neuropsicológicos frecuentes ordenados por grupo etario.
 * Se muestran como dropdown inicial en Historia Clínica al enfocar el campo
 * (sin necesidad de escribir). La edad del paciente ya fue capturada al
 * registrarlo, por lo que se puede filtrar desde el primer momento.
 *
 * Formato: [{ codigo, nombre, dsm5 }]
 * ─────────────────────────────────────────────────────────────────────────*/
export const CIE_POR_POBLACION = {
  infantil: [
    { codigo:"F900", nombre:"TDAH (F90.0, predominio inatento)",                dsm5:"Neurodesarrollo" },
    { codigo:"F901", nombre:"TDAH hipercinético disocial (F90.1)",              dsm5:"Neurodesarrollo" },
    { codigo:"F909", nombre:"TDAH sin especificación (F90.9, combinada)",       dsm5:"Neurodesarrollo" },
    { codigo:"F840", nombre:"Trastorno del espectro autista (TEA)",      dsm5:"Neurodesarrollo" },
    { codigo:"F810", nombre:"Dificultad de aprendizaje — lectura",       dsm5:"Neurodesarrollo" },
    { codigo:"F811", nombre:"Dificultad de aprendizaje — escritura",     dsm5:"Neurodesarrollo" },
    { codigo:"F812", nombre:"Dificultad de aprendizaje — cálculo",       dsm5:"Neurodesarrollo" },
    { codigo:"F803", nombre:"Trastorno del lenguaje / TDL",              dsm5:"Neurodesarrollo" },
    { codigo:"F70",  nombre:"Discapacidad intelectual leve (CI 50-69)",  dsm5:"Neurodesarrollo" },
    { codigo:"F71",  nombre:"Discapacidad intelectual moderada (CI 35-49)", dsm5:"Neurodesarrollo" },
    { codigo:"F930", nombre:"Trastorno de ansiedad por separación",      dsm5:"Ansiedad" },
    { codigo:"F411", nombre:"Trastorno de ansiedad generalizada",        dsm5:"Ansiedad" },
    { codigo:"F431", nombre:"Trastorno por estrés postraumático (TEPT)", dsm5:"Trauma" },
    { codigo:"F421", nombre:"Trastorno obsesivo-compulsivo (TOC)",       dsm5:"TOC" },
    { codigo:"F072", nombre:"TNC por TCE / Síndrome postconmocional",    dsm5:"TNC" },
    { codigo:"F809", nombre:"Trastorno del desarrollo no especificado",  dsm5:"Neurodesarrollo" },
  ],
  adulto_joven: [
    { codigo:"F900", nombre:"TDAH (F90.0, predominio inatento adulto)",  dsm5:"Neurodesarrollo" },
    { codigo:"F901", nombre:"TDAH hipercinético disocial (F90.1)",       dsm5:"Neurodesarrollo" },
    { codigo:"F909", nombre:"TDAH sin especificación (F90.9)",            dsm5:"Neurodesarrollo" },
    { codigo:"G3184",nombre:"Deterioro cognitivo leve (DCL)",            dsm5:"TNC leve" },
    { codigo:"F320", nombre:"Episodio depresivo leve",                   dsm5:"Depresivo" },
    { codigo:"F321", nombre:"Episodio depresivo moderado",               dsm5:"Depresivo" },
    { codigo:"F322", nombre:"Episodio depresivo grave sin psicosis",     dsm5:"Depresivo" },
    { codigo:"F341", nombre:"Distimia / Depresión persistente",          dsm5:"Depresivo" },
    { codigo:"F411", nombre:"Trastorno de ansiedad generalizada",        dsm5:"Ansiedad" },
    { codigo:"F410", nombre:"Trastorno de pánico",                       dsm5:"Ansiedad" },
    { codigo:"F431", nombre:"Trastorno por estrés postraumático (TEPT)", dsm5:"Trauma" },
    { codigo:"F072", nombre:"TNC debido a TCE",                          dsm5:"TNC" },
    { codigo:"U099", nombre:"Condición post-COVID / Long COVID",         dsm5:"TNC médico" },
    { codigo:"F068", nombre:"TNC leve por condición médica",             dsm5:"TNC" },
    { codigo:"F840", nombre:"Trastorno del espectro autista (TEA)",      dsm5:"Neurodesarrollo" },
    { codigo:"F421", nombre:"Trastorno obsesivo-compulsivo (TOC)",       dsm5:"TOC" },
    { codigo:"F198", nombre:"TNC por uso de sustancias",                 dsm5:"Sustancias" },
  ],
  adulto_mayor: [
    { codigo:"G3184",nombre:"Deterioro cognitivo leve (DCL)",            dsm5:"TNC leve" },
    { codigo:"F001", nombre:"Demencia tipo Alzheimer (inicio tardío)",   dsm5:"TNC mayor" },
    { codigo:"F010", nombre:"Demencia vascular",                         dsm5:"TNC mayor" },
    { codigo:"F000", nombre:"Demencia tipo Alzheimer (inicio precoz)",   dsm5:"TNC mayor" },
    { codigo:"F020", nombre:"Demencia frontotemporal (DFT-Pick)",        dsm5:"TNC mayor" },
    { codigo:"F03",  nombre:"Demencia no especificada",                  dsm5:"TNC mayor" },
    { codigo:"F04",  nombre:"Síndrome amnésico orgánico",                dsm5:"TNC" },
    { codigo:"F320", nombre:"Episodio depresivo leve",                   dsm5:"Depresivo" },
    { codigo:"F321", nombre:"Episodio depresivo moderado",               dsm5:"Depresivo" },
    { codigo:"F341", nombre:"Distimia / Depresión persistente",          dsm5:"Depresivo" },
    { codigo:"F411", nombre:"Trastorno de ansiedad generalizada",        dsm5:"Ansiedad" },
    { codigo:"F431", nombre:"Trastorno por estrés postraumático",        dsm5:"Trauma" },
    { codigo:"U099", nombre:"Condición post-COVID / Long COVID",         dsm5:"TNC médico" },
    { codigo:"F068", nombre:"TNC leve por condición médica",             dsm5:"TNC" },
    { codigo:"F072", nombre:"TNC debido a TCE",                          dsm5:"TNC" },
  ],
};

/* ── 3. SUGERENCIAS DE PROTOCOLO POR EDAD ──
 * Devuelve lista de pruebas core + opcionales según edad del paciente.
 * edad_anios: número. retorna { core: [], opcionales: [], notas: "" }
 */
export const PROTOCOL_SUGGESTIONS = {
  preescolar: {
    rango: [3, 5],
    nombre: "Preescolar (3-5 años)",
    core: ["WPPSI-IV", "ENI-2 (subescalas básicas)", "Figura Humana", "Escala Vineland-II"],
    opcionales: ["M-CHAT (tamizaje TEA)", "Battelle"],
    dominios_clave: ["desarrollo global", "lenguaje", "motor"],
    tiempo_min: 60,
    tiempo_max: 90,
  },
  infantil: {
    rango: [6, 12],
    nombre: "Infantil (6-12 años)",
    core: [
      "WISC-IV o WISC-V",
      "ENI-2 Memoria Verbal (curva + recobro)",
      "FCRO (copia y recobro)",
      "TMT-A/B (≥9 años)",
      "CARAS-R o Cancelación",
      "Fluidez verbal (semántica y fonológica)",
      "Stroop",
    ],
    opcionales: ["BANFE-3", "SNAP-IV", "Escala Conners", "Lectura/Escritura/Cálculo académicos", "CBCL"],
    por_sospecha: {
      tdah: ["SNAP-IV", "Conners", "CPT"],
      tea: ["ADOS-2", "ADI-R", "Reconocimiento de emociones"],
      dea: ["Lectura-Evaluación", "PROLEC-R", "Evalec"],
    },
    dominios_clave: ["atención", "memoria", "funciones ejecutivas", "aprendizaje escolar"],
    tiempo_min: 120,
    tiempo_max: 180,
  },
  adolescente: {
    rango: [13, 17],
    nombre: "Adolescente (13-17 años)",
    core: [
      "WISC-V o WAIS-IV (según edad)",
      "ENI-2 o Rey-AVLT",
      "FCRO",
      "TMT-A/B",
      "Fluidez verbal",
      "Stroop",
      "Semejanzas / Vocabulario",
    ],
    opcionales: ["BANFE-3", "STAI-A", "BDI-II", "Wisconsin", "Torre de Londres", "SCARED-41", "IES-R"],
    por_sospecha: {
      tdah: ["SNAP-IV", "Conners-3", "CPT"],
      tea: ["ADOS-2", "ADI-R", "SRS-2", "Reconocimiento de emociones"],
      trauma: ["PCL-5", "IES-R", "CAPS-5 (referido a psicología especializada)"],
      dea: ["PROLEC-R", "Lectura-Evaluación", "EVALEA"],
    },
    dominios_clave: ["funciones ejecutivas", "memoria", "rendimiento académico", "regulación emocional"],
    tiempo_min: 120,
    tiempo_max: 150,
  },
  adulto_joven: {
    rango: [18, 59],
    nombre: "Adulto Joven (18-59 años)",
    core: [
      "WAIS-IV o WAIS-III",
      "Rey-AVLT o CVLT",
      "FCRO (copia y recobro)",
      "TMT-A/B",
      "Dígitos directos e inversos",
      "Fluidez verbal (fonológica y semántica)",
      "Denominación (Boston)",
      "Stroop",
      "Semejanzas",
    ],
    opcionales: ["BANFE-3", "STAI", "PHQ-9", "PASAT", "WCST", "Torre de Londres/Hanoi", "SDMT", "PCL-5", "IES-R"],
    por_sospecha: {
      tdah: ["ASRS", "CPT", "Escala Barkley"],
      dano_cerebral: ["PASAT", "SDMT", "TMT ampliado", "Evaluación de conciencia de déficit"],
      trauma: ["PCL-5", "IES-R", "CAPS-5 (referido)", "PHQ-9", "STAI"],
      long_covid: ["SDMT", "PASAT", "PHQ-9", "Escala de Fatiga (FSS)", "TMT-A/B"],
    },
    dominios_clave: ["memoria", "atención", "funciones ejecutivas", "velocidad de procesamiento"],
    tiempo_min: 90,
    tiempo_max: 150,
  },
  adulto_mayor: {
    rango: [60, 120],
    nombre: "Adulto Mayor (60+ años)",
    core: [
      "Tamizaje: MMSE o MoCA (inicial obligatorio)",
      "Grober-Buschke (memoria verbal controlada)",
      "FCRO (copia y recobro)",
      "TMT-A/B o SDMT",
      "Dígitos directos e inversos",
      "Fluidez verbal",
      "Denominación (Boston 15 o 48 ítems)",
      "Semejanzas",
      "Stroop o Go/No-Go",
      "Yesavage (tamizaje depresión)",
    ],
    opcionales: ["NPI (con informante)", "Hamilton Ansiedad", "Lawton (AIVD)", "Barthel (AVD)", "BANFE-3", "HVLT"],
    dominios_clave: ["memoria episódica verbal", "funciones ejecutivas", "lenguaje", "estado anímico"],
    tamizaje_inicial: true,
    tiempo_min: 100,
    tiempo_max: 150,
    nota: "Estratificar baremos por edad Y escolaridad. Incluir informante para AIVD y cambios de conducta.",
  },
};

/* ── 4. INFORMES INCONCLUSOS — catálogo de razones y acciones ──*/
export const INCONCLUSO_REASONS = [
  {
    id: "bateria_mas_segunda_orden",
    titulo: "Batería completa + requiere segunda orden",
    descripcion: "Se aplicó el protocolo principal completo pero el análisis clínico sugiere complementar con pruebas adicionales.",
    accion: "Generar nueva orden clínica para pruebas complementarias con el mismo prestador. Justificar en la conclusión del informe la necesidad de ampliar el análisis.",
    plazo_dias: 10,
  },
  {
    id: "evaluacion_incompleta",
    titulo: "Evaluación incompleta por factores del paciente",
    descripcion: "No fue posible completar el protocolo cuantitativo por fatiga, resistencia, limitación sensorial, cognitiva o conductual del paciente durante la sesión.",
    accion: "Documentar cualitativamente las áreas no evaluadas. Agendar segunda cita con el mismo prestador. En el informe aclarar el motivo y qué pruebas no se aplicaron.",
    plazo_dias: 10,
  },
  {
    id: "evaluacion_reciente",
    titulo: "Evaluación reciente en otra institución",
    descripcion: "El paciente trae evaluación vigente (<6-12 meses) de otro prestador; no se justifica reaplicar la batería.",
    accion: "Diligenciar historia clínica completa + observación clínica + conclusión. Emitir informe con sección cognitiva omitida, justificando.",
    plazo_dias: 5,
  },
  {
    id: "cancelado_paciente",
    titulo: "Paciente no continuó proceso",
    descripcion: "El paciente decidió no continuar la evaluación o no asistió a las citas programadas.",
    accion: "Cerrar el caso con informe de cierre que registre el estado alcanzado y recomendaciones mínimas según la información disponible.",
    plazo_dias: 15,
  },
];

/* ── 5. CUADROS A EVALUAR — mapa cuadro → algoritmo + recomendaciones ──
 * Atajo para el selector de la UI.
 */
export const CUADROS_CLINICOS = [
  { id: "tdah",                   nombre: "TDAH",                           grupos: ["infantil", "adolescente", "adulto_joven"] },
  { id: "tempo_cognitivo_lento",  nombre: "Tempo Cognitivo Lento / CDHS",   grupos: ["infantil", "adolescente", "adulto_joven"] },
  { id: "tea",                    nombre: "TEA",                            grupos: ["preescolar", "infantil", "adolescente", "adulto_joven"] },
  { id: "discapacidad_intelectual", nombre: "Discapacidad Intelectual",     grupos: ["infantil", "adolescente", "adulto_joven"] },
  { id: "dea",                    nombre: "Dificultades de Aprendizaje",    grupos: ["infantil", "adolescente"] },
  { id: "integracion_sensorial",  nombre: "Procesamiento Sensorial",        grupos: ["preescolar", "infantil", "adolescente"] },
  { id: "dcl",                    nombre: "Deterioro Cognitivo Leve (DCL)", grupos: ["adulto_mayor", "adulto_joven"] },
  { id: "demencia",               nombre: "Demencia / TNC Mayor",           grupos: ["adulto_mayor"] },
  { id: "tce",                    nombre: "TCE / Daño Cerebral Adquirido",  grupos: ["infantil", "adolescente", "adulto_joven", "adulto_mayor"] },
  { id: "long_covid",             nombre: "Secuelas Post-COVID",            grupos: ["adulto_joven", "adulto_mayor"] },
  { id: "tept",                   nombre: "TEPT / Trauma",                  grupos: ["infantil", "adolescente", "adulto_joven", "adulto_mayor"] },
  { id: "ansiedad",               nombre: "Síntomas ansiosos",              grupos: ["adolescente", "adulto_joven", "adulto_mayor"] },
  { id: "depresion",              nombre: "Síntomas depresivos",            grupos: ["adolescente", "adulto_joven", "adulto_mayor"] },
  { id: "neuropsicologia_forense", nombre: "Evaluación Forense / Pensional", grupos: ["infantil", "adolescente", "adulto_joven", "adulto_mayor"] },
];

/* ── 6. HELPER: sugerir protocolo según edad ── */
export function protocoloPorEdad(edad_anios) {
  if (edad_anios == null) return null;
  for (const key of Object.keys(PROTOCOL_SUGGESTIONS)) {
    const p = PROTOCOL_SUGGESTIONS[key];
    if (edad_anios >= p.rango[0] && edad_anios <= p.rango[1]) {
      return { key, ...p };
    }
  }
  return null;
}

/* ── 7. HELPER: evaluar algoritmo diagnóstico contra un set de respuestas ── */
export function evaluarAlgoritmo(algoritmoId, respuestas) {
  const alg = DIAGNOSTIC_ALGORITHMS[algoritmoId];
  if (!alg) return null;
  const total = alg.criterios.reduce((s, c) => s + c.peso, 0);
  const obtenido = alg.criterios.reduce((s, c) => s + (respuestas[c.id] ? c.peso : 0), 0);
  const ratio = obtenido / total;
  let nivel;
  if (ratio >= 0.75) nivel = "alta";
  else if (ratio >= 0.5) nivel = "media";
  else nivel = "baja";
  return {
    algoritmo: alg.nombre,
    marco: alg.marco,
    ratio,
    nivel,
    interpretacion: alg.interpretacion[nivel],
    criterios_cumplidos: alg.criterios.filter(c => respuestas[c.id]).map(c => c.pregunta),
    criterios_faltantes: alg.criterios.filter(c => !respuestas[c.id]).map(c => c.pregunta),
  };
}
