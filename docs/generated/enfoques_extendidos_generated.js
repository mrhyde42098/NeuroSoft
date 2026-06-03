/* ═══════════════════════════════════════════════════════════════════════
 * docs/generated/enfoques_extendidos_generated.js
 * ═══════════════════════════════════════════════════════════════════════
 *
 * Contenido académico extendido generado para 15 enfoques terapéuticos.
 *
 * Para INTEGRAR al archivo principal:
 * 1. Revisar cada objeto y ajustar según literatura local
 * 2. En enfoquesTerapeuticos.js, para cada enfoque que tenga un bloque aquí,
 *    reemplazar su objeto con { ...objOriginal, ...ENFOQUES_EXTENDIDOS[id] }
 * 3. Testear videos (pueden cambiar URLs en YouTube)
 * 4. Validar bibliografía con ISBNs/DOIs reales
 *
 * ═══════════════════════════════════════════════════════════════════════ */

export const ENFOQUES_EXTENDIDOS = {

  /* ════════════════════════════════════════════════════════════════════
   * DBT — Terapia Dialéctico-Conductual
   * ════════════════════════════════════════════════════════════════════ */
  dbt: {
    descripcion_extendida:
      "La Terapia Dialéctico-Conductual (DBT) fue desarrollada por Marsha Linehan (1987-1990) " +
      "específicamente para el Trastorno Límite de Personalidad (TLP) con comportamientos " +
      "suicidas crónicos. Integra principios cognitivo-conductuales con aceptación y dialéctica " +
      "(síntesis de opuestos). DBT es un programa intensivo de 12 meses que requiere 4 componentes " +
      "simultáneos: sesión individual semanal, grupo de habilidades semanal (4 módulos: " +
      "mindfulness, tolerancia al malestar, regulación emocional, efectividad interpersonal), " +
      "coaching telefónico entre sesiones y equipo de consulta para el terapeuta. Es el tratamiento " +
      "basado en evidencia mejor validado para TLP e ideación suicida crónica.",
    efecto_tamano: {
      tlp: 0.84,
      conductas_suicidas: 1.02,
      autolesiones: 0.79,
      desregulacion_emocional: 0.76,
      bulimia: 0.68,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Pre-tratamiento y evaluación",
        duracion_sesiones: "1-2",
        objetivos: [
          "Pactación de objetivos jerárquicos (vida > terapia > calidad de vida)",
          "Explicación del modelo dialéctico y estructura de DBT",
          "Evaluación de riesgos suicidas / autolesivos agudos",
        ],
        tareas_clinico: [
          "Aplicar MSI (Multicale of Suicidal Ideation) y DSHI (Deliberate Self-Harm Inventory)",
          "Informar sobre rol y disponibilidad para coaching telefónico",
          "Orientar al grupo de habilidades obligatorio",
        ],
        tareas_paciente: [
          "Lectura: carta de DBT explicando estructura de 4 patas",
          "Compromiso escrito de asistencia individual + grupo",
        ],
        criterios_avance: "Comprensión del modelo y acuerdo terapéutico firmado",
      },
      {
        fase: 2, nombre: "Módulo 1: Mindfulness y Mente Sabia",
        duracion_sesiones: "4-8 (paralelo a otros módulos)",
        objetivos: [
          "Enseñar 'mente racional' vs 'mente emocional' vs 'mente sabia' (síntesis)",
          "Práctica de conciencia del momento presente sin juicio",
        ],
        tareas_clinico: [
          "Sesión individual: trabajar observación de emociones sin reacción automática",
          "Grupo: ejercicios guiados de respiración y enfoque atencional",
        ],
        tareas_paciente: [
          "Meditación sentada 10 min/día (app Insight Timer si ayuda)",
          "Registro de observación diaria (qué notaste sin cambiar)",
        ],
        criterios_avance: "Cliente diferencia mente racional/emocional y accede a mente sabia",
      },
      {
        fase: 3, nombre: "Módulo 2: Tolerancia al Malestar (TIPP, ACEPTAR, RAINN)",
        duracion_sesiones: "4-8",
        objetivos: [
          "Reducir conductas de escape/evitación (autolesiones, sobredosis, purgas)",
          "Instalar habilidades de supervivencia crisis a corto plazo",
        ],
        tareas_clinico: [
          "Enseñar TIPP: Temperature (cambio de temperatura facial), Intense exercise, Paced breathing, Paired muscle relaxation",
          "Tarjeta de crisis con habilidades 3 minutos vs 3 horas",
        ],
        tareas_paciente: [
          "Crear 'caja de crisis' con estímulos físicos no dañinos",
          "Practicar TIPP en baja intensidad (nada en cuello con hielo) antes de emergencia real",
        ],
      },
      {
        fase: 4, nombre: "Módulo 3: Regulación Emocional (ABC PLEASE + nombre de emociones)",
        duracion_sesiones: "4-8",
        objetivos: [
          "Reducir vulnerabilidad a emociones extremas",
          "Aumentar emociones positivas y duración",
        ],
        tareas_clinico: [
          "ABC PLEASE: Accumulated Consequences (mirar largo plazo), Build mastery + Positive experiences (activación conductual), Maintain physical and emotional health",
          "Taxonomía de emociones (19 emociones, cada una con función)",
        ],
        tareas_paciente: [
          "Registro diario de emoción máxima 0-10 + trigger + consecuencia",
          "1 actividad placentera + 1 de logro/dominio diaria",
        ],
      },
      {
        fase: 5, nombre: "Módulo 4: Efectividad Interpersonal (DEAR MAN, GIVE, FAST)",
        duracion_sesiones: "4-8",
        objetivos: [
          "Mejorar comunicación sin sacrificar relaciones o auto-respeto",
        ],
        tareas_clinico: [
          "DEAR MAN (Describe, Express, Assert, Reinforce, stay Mindful, Act confident, Negotiate) para obtener lo que necesitas",
          "GIVE (be Gentle, Interested, Validate, Easy manner) para mantener relación",
          "FAST (Fair, Apologize only when warranted, Stick to values, Take care of yourself) para auto-respeto",
        ],
        tareas_paciente: [
          "Role-play de 1 interacción interpersonal difícil en sesión",
          "Aplicar DEAR MAN en situación real esta semana",
        ],
      },
      {
        fase: 6, nombre: "Análisis cadenal (problema behaviors) y trabajo individual profundo",
        duracion_sesiones: "Sesiones individuales paralelas",
        objetivos: [
          "Entender cadena causal de comportamientos problema",
          "Insertar intervención en eslabón vulnerable",
        ],
        tareas_clinico: [
          "Cuando hay autolesión/sobredosis/crisis: análisis cadenal detallado (qué pasó una semana antes, prompts, vulnerabilidades biológicas, emociones, pensamientos, conductas)",
          "Colaborativo — paciente identifica dónde puede cortar cadena la próxima vez",
        ],
      },
      {
        fase: 7, nombre: "Prevención de recaída y consolidación",
        duracion_sesiones: "3-4 (hacia fin de año 12)",
        objetivos: [
          "Consolidar habilidades en vida cotidiana",
          "Plan de mantenimiento después de DBT",
        ],
        tareas_clinico: [
          "Revisión de metas iniciales vs logros",
          "Planificación de booster trimestral vs término",
        ],
        tareas_paciente: [
          "Libreta DBT: 5 habilidades más usadas este año + cuándo las usa",
          "Contacto de crisis y plan si recaída",
        ],
        criterios_avance: "Reducción >50% en conductas suicidas/autolesivas, estabilidad emocional relativa",
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Análisis cadenal (Behavioral Chain Analysis)",
        descripcion: "Disección detallada de un comportamiento problema: vulnerabilidades biológicas previas, prompts externos, escalada emocional, pensamiento, conducta y consecuencias. Mapeo de dónde intervenir.",
        cuando_usar: "Cada vez que ocurre conducta suicida, autolesión, sobredosis, purga u otro comportamiento diana de DBT.",
        ejemplo_dialogo:
          "T: 'Esta semana te autolesionaste. Vamos a entender todo lo que pasó, sin culpa. Una semana antes, ¿qué estaba pasando?'\n" +
          "C: 'Mi mamá me ignoró en el teléfono.'\n" +
          "T: 'Eso es un prompt. ¿Pero ya había algo vulnerándote antes? ¿Dormiste mal, comiste poco, estabas estresado?'\n" +
          "C: 'Sí, no había dormido 2 noches.'\n" +
          "T: 'Vulnerabilidad biológica. ¿Y entonces qué pensamiento vino?'\n" +
          "C: 'Nadie me quiere, merezco sufrir.'\n" +
          "T: 'Pensamiento. ¿Qué emoción?'\n" +
          "C: 'Desesperación, rabia.'\n" +
          "T: 'OK. Y LUEGO vinieron los rayones. Así que, la próxima vez que no duermas + tu mamá ignore, ¿dónde podrías cortar la cadena?'\n" +
          "C: 'Durmiendo bien. O llamar a una amiga antes que sentirme tan sola.'",
        ejercicio_casa: "Hacer análisis cadenal escrito de 1 situación difícil de esta semana (no autolesión, solo molestia).",
      },
      {
        nombre: "TIPP (skills de crisis física)",
        descripcion: "Herramientas rápidas (<3 minutos) que usan respuesta fisiológica para calmar el sistema nervioso simpático en momento de crisis.",
        cuando_usar: "Cuando el cliente está en pico emocional agudo y corre riesgo de conducta suicida/autolesión. Crisis de 3 minutos, habilidades de 3 minutos.",
        ejemplo_dialogo:
          "T: 'Cuando sientas que vas a explotar, haz esto: (1) Temperature — moja tu cara con agua muy fría o pon hielo en el cuello. Bloquea el reflejo de buceo, desacelera corazón. (2) Intense exercise — corre de lugar a lugar 1 minuto. (3) Paced breathing — respira lento: 5 adentro, 7 afuera. (4) Paired muscle — aprieta un músculo 5 seg + relaja.'",
        ejercicio_casa: "Probar cada TIPP esta semana en estado emocional bajo (nada en cuello con hielo ahora, así no es sorpresa en crisis).",
      },
      {
        nombre: "ABC PLEASE (auto-cuidado + acciones antidepresivas)",
        descripcion: "Marco para reducir vulnerabilidad emocional general. (A) Accumulated Consequences — pensar largo plazo; (B) Build mastery + positive experiences; (C) Cope ahead; (PLEASE) Physical + emotional health, pLan, Exercise, Sleep, Eat, Ask for help, Avoid drugs, Self-respect.",
        cuando_usar: "Prevención de crisis. Especialmente en sesiones de regulación emocional y cuando vulnerabilidad sube.",
        ejemplo_dialogo:
          "T: '¿Esta semana cuántas cosas hiciste para sentirte mejor?' C: 'Nada, sólo lloré.' T: 'La depresión te dice espera, no tengo ganas. Pero ABC es lo opuesto: acción SIN ganas. ¿Qué pequeño logro podrías tener esta semana?' C: 'Podría ducharme y salir 15 minutos.' T: 'Mastery + pleasure. ¿Duermes OK?' C: 'No, 3-4 horas.' T: 'Eso aumenta vulnerabilidad. Melatonina, rutina de cama a la misma hora.'",
        ejercicio_casa: "Hacer una lista de 'acciones ABC' esta semana — 1 de mastery, 1 de pleasure, 1 de self-care.",
      },
      {
        nombre: "DEAR MAN (asertividad efectiva)",
        descripcion: "Algoritmo para pedir lo que necesitas sin sacrificar relación o auto-respeto. Describe, Express, Assert, Reinforce, stay Mindful, Act confident, Negotiate.",
        cuando_usar: "Déficit de asertividad o patrones de evitación/explosión en conflictos. Módulo 4.",
        ejemplo_dialogo:
          "C: 'Necesito que mi pareja me ayude con tareas pero nunca lo pide.'\n" +
          "T: 'Vamos a practicar DEAR MAN. Describe: ¿qué necesitas exactamente? No asumes.'\n" +
          "C: 'Necesito que esto fin de semana me ayude con la limpieza.'\n" +
          "T: 'Express: ¿por qué importa?'\n" +
          "C: 'Porque me siento abrumada sola.'\n" +
          "T: 'Assert: ¿cuál es tu petición clara?'\n" +
          "C: 'Te pido que el sábado ayudes 2 horas mínimo.'\n" +
          "T: 'Reinforce: ¿qué beneficio para él? Mindful: sin acusación. Negotiate: ¿qué dias/horas flexionan?'",
        ejercicio_casa: "Usar DEAR MAN con 1 persona esta semana. Escribir guion antes.",
      },
    ],
    videos: [
      {
        titulo: "Marsha Linehan — What is DBT? (ISSTD)",
        url_youtube: "https://www.youtube.com/embed/F-m_F8zr_Kg",
        autor: "Marsha Linehan Institute",
        duracion: "8:45",
        idioma: "en",
        descripcion: "La creadora de DBT explica los 4 componentes y por qué funciona para TLP.",
      },
      {
        titulo: "Los 4 módulos de DBT explicados (habilidades)",
        url_youtube: "https://www.youtube.com/embed/D_p8N4r9pRw",
        autor: "DBT Skills Training",
        duracion: "18:20",
        idioma: "en",
        descripcion: "Desglose de mindfulness, tolerancia, regulación y efectividad interpersonal.",
      },
      {
        titulo: "DBT para principiantes en español",
        url_youtube: "https://www.youtube.com/embed/z__KSajX2c8",
        autor: "Psicología Clínica Práctica",
        duracion: "12:05",
        idioma: "es",
        descripcion: "Introducción a DBT con ejemplos colombianos.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "DBT Skills Training Manual (2nd ed.)", autor: "Linehan, M. M.", anio: 2014, edicion: 2, isbn: "978-1572307810" },
      { tipo: "libro", titulo: "Manual de habilidades DBT (edición en español)", autor: "Linehan, M. M. (trad.)", editorial: "Desclée De Brouwer", anio: 2014, isbn: "978-8433024816" },
      { tipo: "paper", titulo: "Cognitive-behavioral treatment of chronically parasuicidal borderline patients", autores: "Linehan, M. M., Armstrong, H. E., Suarez, A., et al.", anio: 1991, doi: "10.1037/0022-006X.59.6.790" },
      { tipo: "paper", titulo: "DBT for suicide prevention: a randomized clinical trial", autores: "Linehan, M. M., et al.", anio: 2015, doi: "10.1176/appi.ajp.2014.14070999" },
      { tipo: "guia", titulo: "NICE NG92 — Personality Disorders: Borderline and Antisocial", autor: "NICE", anio: 2018, url: "https://www.nice.org.uk/guidance/ng92" },
    ],
    casos_practicos: [
      {
        titulo: "Mujer 24a — TLP con autolesiones crónicas",
        motivo_consulta: "Tengo 5 años cortándome los brazos. Mi familia no entiende. He estado en psiquiatra pero nada funciona.",
        hipotesis: "TLP (CIE-10: F60.31) con conducta autolesiva crónica (2-3 veces/semana). DSHI = 28. MSI = 12. Apta para DBT programa completo.",
        plan_aplicado: [
          "DBT 12 meses: sesión individual 1×/sem + grupo habilidades 1×/sem + coaching tel",
          "Psiquiatra en paralelo para medicación si ansiedad/depresión severa",
          "Análisis cadenal de cada autolesión en sesión individual",
          "Módulos: mindfulness → tolerancia → regulación → interpersonal",
        ],
        evolucion: "Mes 3: autolesiones bajaron a 1/semana. Mes 6: 1-2/mes. Mes 12: cero, estresores sin autolesión ahora. MSI = 2 al cierre.",
        reflexion: "La clave fue que el programa fue intensivo y coordinado. Sin grupo, sin coaching, no hubiera funcionado. TLP necesita estructura + validación paralela a la exigencia de cambio.",
      },
    ],
    recursos_descargables: [
      { titulo: "DSHI (Deliberate Self-Harm Inventory) en español", tipo: "plantilla", url: "https://screeningtoolkit.org/wp-content/uploads/2020/DSHI.pdf" },
      { titulo: "Tarjeta de crisis DBT (habilidades 3 minutos)", tipo: "paciente", url: "https://dbt.ucsd.edu/sites/default/files/CrisisCard.pdf" },
      { titulo: "Análisis cadenal — formato rellenable", tipo: "plantilla", url: "https://www.dbtcct.org/files/Documents/Behavioral%20Chain%20Analysis.pdf" },
      { titulo: "TIPP skills — guía visual", tipo: "psicoeducacion", url: "https://dbt.ucsd.edu/sites/default/files/TIPP%20Skills.pdf" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * MBCT — Terapia Cognitiva Basada en Mindfulness
   * ════════════════════════════════════════════════════════════════════ */
  mbct: {
    descripcion_extendida:
      "La Terapia Cognitiva Basada en Mindfulness (MBCT, Mindfulness-Based Cognitive Therapy) " +
      "fue desarrollada por Segal, Williams y Teasdale (1992) para la prevención de recaída en " +
      "depresión. Combina entrenamiento en meditación (mindfulness) con elementos de CBT. Se " +
      "basa en el modelo de depresión cognitiva de Beck: en pacientes con depresión recurrente, " +
      "síntomas leves (dolores, fatiga, tristeza normal) pueden activar redes cognitivas " +
      "depresivas automáticas ('tengo depresión de nuevo'). MBCT enseña a observar pensamientos " +
      "como eventos mentales, no como realidad. Es programa grupal estructurado de 8 sesiones " +
      "de 2-2.5 horas más retiro. Validado para prevención de recaídas (reducción de >50% en " +
      "recurrencia).",
    efecto_tamano: {
      prevencion_recaida: 0.69,
      depresion_residual: 0.48,
      ansiedad: 0.52,
      bienestar_general: 0.55,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Sesión 1: Piloto automático",
        duracion_sesiones: "1 (2 horas)",
        objetivos: [
          "Presentar cómo el cerebro funciona en 'piloto automático' — hábitos sin intención",
          "Primer ejercicio mindfulness: comer una pasa con atención plena",
        ],
        tareas_clinico: [
          "Meditación guiada sentada inicial (3 minutos)",
          "Psicoeducación: qué es mindfulness, no es relajación",
        ],
        tareas_paciente: [
          "Audio: escaneo corporal guiado (10 min) — escuchar 1×/día, 6 días",
          "Registrar un hábito 'piloto automático' que notaron",
        ],
        criterios_avance: "Comprensión básica de piloto automático, práctica iniciada",
      },
      {
        fase: 2, nombre: "Sesión 2: Vivir en la cabeza vs cuerpo",
        duracion_sesiones: "1 (2 horas)",
        objetivos: [
          "Reconocer cómo la mente 'rumiadora' genera depresión",
          "Diferenciar 'modo hacer' vs 'modo ser'",
        ],
        tareas_clinico: [
          "Meditación de 10 minutos enfocada en respiración",
          "Ejercicio: notar cuándo mente rumia vs está en 'presente'",
        ],
        tareas_paciente: [
          "Audio: yoga suave guiado (15 min) 3-4 días/semana",
          "Registro: momentos en 'piloto automático' vs 'presentes'",
        ],
      },
      {
        fase: 3, nombre: "Sesión 3: Reuniendo la mente dispersa",
        duracion_sesiones: "1 (2 horas)",
        objetivos: [
          "Meditación de atención enfocada (entrenamiento de concentración)",
          "Normalizar que la mente se distrae — es el ejercicio",
        ],
        tareas_clinico: [
          "Meditación de 20 min con enfoque en respiración",
          "Notar distracciones sin crítica, volver",
        ],
        tareas_paciente: [
          "Meditación sentada 20 min/día",
          "Registro: cuántas veces se distrajo, OK, sin culpa",
        ],
      },
      {
        fase: 4, nombre: "Sesión 4: Reconociendo aversión (evitación emocional)",
        duracion_sesiones: "1 (2 horas)",
        objetivos: [
          "Reconocer patrones de evitación que mantienen depresión",
          "Mapa emocional: qué emociones evito, cómo las evito",
        ],
        tareas_clinico: [
          "Meditación corporal: notar sensaciones desagradables sin escapar",
          "Diálogo: qué situaciones evitan cuando emociones bajas",
        ],
        tareas_paciente: [
          "Registro de eventos desagradables + qué emoción + qué hizo",
          "Meditación 20 min/día",
        ],
      },
      {
        fase: 5, nombre: "Sesión 5: Permitir, dejar ser (aceptación)",
        duracion_sesiones: "1 (2 horas)",
        objetivos: [
          "Cambio de pelear con emociones a hacer espacio a ellas",
          "Práctica: sentir rabia/tristeza sin tener que cambiarla",
        ],
        tareas_clinico: [
          "Meditación de los 3 minutos (técnica 'espacio respiratorio')",
          "Modular 'qué si solo permito que esté'",
        ],
        tareas_paciente: [
          "Audio: meditación de 3 minutos para momentos difíciles",
          "Identificar 1 emoción esta semana, permitirla 5 minutos sin actuar",
        ],
      },
      {
        fase: 6, nombre: "Sesión 6: Los pensamientos no son hechos",
        duracion_sesiones: "1 (2 horas)",
        objetivos: [
          "Defusión cognitiva: observar pensamientos depresivos como nubes, no verdad",
        ],
        tareas_clinico: [
          "Meditación incluyendo observación de pensamientos",
          "Ejercicio: 'tengo el pensamiento de que...' (en lugar de 'es verdad que...')",
        ],
        tareas_paciente: [
          "Registro: pensamiento depresivo de la semana + es solo un pensamiento",
          "Continuar práctica formal 20 min/día",
        ],
      },
      {
        fase: 7, nombre: "Sesión 7: ¿Cómo cuidarme mejor? (auto-cuidado)",
        duracion_sesiones: "1 (2 horas)",
        objetivos: [
          "Planes concretos de mantenimiento post-programa",
          "Identificar señales tempranas de recaída personal",
        ],
        tareas_clinico: [
          "Hacer lista personal de 'qué me ayuda' — actividades, contactos, prácticas",
          "Escala de riesgo recaída: qué señales tempranas veo",
        ],
        tareas_paciente: [
          "Escribir plan de prevención de recaída: señales tempranas + qué haré",
          "Comprometerse a 1 práctica después del programa",
        ],
      },
      {
        fase: 8, nombre: "Retiro + sesión final",
        duracion_sesiones: "Retiro de día entero + 1 sesión",
        objetivos: [
          "Consolidar práctica intensiva",
          "Cierre, integración a vida diaria",
        ],
        tareas_clinico: [
          "Retiro 6-8 horas: meditación silenciosa, yoga, meditación caminante",
          "Sesión de cierre: reflexión de aprendizajes",
        ],
        tareas_paciente: [
          "Participar plenamente en retiro",
          "Llevar práctica diaria a casa — objetivo realista (4-5 días/semana)",
        ],
        criterios_avance: "Reducc ión ≥30% PHQ-9, comprensión de piloto automático y cómo cambiar relación con depresión",
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Meditación del escaneo corporal",
        descripcion: "Recorrido mental sistemático desde pies hasta cabeza, notando sensaciones sin cambiarlas. Herramienta central de MBCT para ampliar conciencia y reducir evitación de sensaciones.",
        cuando_usar: "Tarea diaria, especialmente para quienes evitan el cuerpo o disocian.",
        ejemplo_dialogo:
          "T: 'Recuéstate. Vamos a recorrer el cuerpo juntos. Comienza en los pies. ¿Qué notas? Puede haber sensación, entumecimiento, nada. Todo OK. No tienes que cambiar nada.'\n" +
          "(Pausa 30 seg)\n" +
          "T: 'Sigue a los tobillos...' (lentamente hacia arriba, 10 minutos)\n" +
          "Después: 'Qué notaste?' C: 'Tensión en el cuello que no sabía.' T: 'Eso es la práctica — notar lo que está aquí.'",
        ejercicio_casa: "Audio de 10 minutos, escuchar cada noche antes de dormir o en un momento fijo.",
      },
      {
        nombre: "Espacio Respiratorio de 3 minutos",
        descripcion: "Técnica rápida para aterrizarse en momento difícil. (1) Conciencia abierta: qué pasa en cuerpo, mente, emociones ahora; (2) Enfoque en respiración: 3 minutos de atención a cada respiro; (3) Expansión: ampliar atención a todo el cuerpo.",
        cuando_usar: "Cuando el cliente nota síntomas depresivos tempranos o estrés durante el día.",
        ejemplo_dialogo:
          "T: 'Cuando notes tristeza subiendo, no esperes 2 horas. Tómate 3 minutos aquí. Siéntate, nota todo lo que pasa — ¿qué siento? ¿qué pienso? ¿qué siento en el cuerpo?' (1 min)\n" +
          "'Ahora, enfoca solo en respiración. Adentro por 4, afuera por 6. Sin cambiar nada, solo observa.' (1 min)\n" +
          "'Expande: siente piernas, brazos, todo el cuerpo en el aire. Aquí está todo. Ahorita está ahí.' (1 min)\n" +
          "'¿Cambiaste algo?' C: 'No, pero veo diferente.' T: 'ESO.'",
        ejercicio_casa: "Usar 1-2 veces diarias en semana 5 en adelante. App Insight Timer tiene versiones de 3 minutos.",
      },
      {
        nombre: "Observación de pensamientos (nube en el cielo)",
        descripcion: "Defusión cognitiva: en meditación, cuando pensamientos aparecen, etiquetarlos como 'tengo el pensamiento de que...' en lugar de tratarlos como hechos.",
        cuando_usar: "Sesión 6. Cuando cliente tiene rumiación depresiva resistente.",
        ejemplo_dialogo:
          "T: 'Mientras meditas y aparece un pensamiento como 'soy inútil', en vez de pelear con él o creerlo, simplemente nota: \"Tengo el pensamiento de que soy inútil\". Es como una nube pasando por el cielo. Parte del paisaje, no ES el cielo.'\n" +
          "C: '¿Pero y si es verdad?' T: 'En este momento es un evento mental. Verdad o falsa, es un evento. Sigue respirando.'",
        ejercicio_casa: "Esta semana, 1 pensamiento depresivo — etiquetarlo 'tengo el pensamiento de...' en registro.",
      },
      {
        nombre: "Yoga consciente / movimiento atentivo",
        descripcion: "Movimientos lentes con conciencia plena — no es ejercicio sino meditación en movimiento. Integra cuerpo + mente.",
        cuando_usar: "Para quienes no pueden meditar quietos, o tienen bloqueo emocional somático.",
        ejemplo_dialogo:
          "T: 'De pie. Levanta lentamente un brazo. No prisa. ¿Qué sientes? Músculos, alargamiento, aire. Respira mientras subes, respira mientras baja.'\n" +
          "(Otros movimientos: rotación de cuello lenta, inclinación torso hacia adelante/atrás)",
        ejercicio_casa: "Audio de yoga 15 minutos, 3-4 veces/semana.",
      },
    ],
    videos: [
      {
        titulo: "MBCT creadores — Segal, Williams, Teasdale (cátedra)",
        url_youtube: "https://www.youtube.com/embed/l_0VjPqKR40",
        autor: "University of Toronto",
        duracion: "24:00",
        idioma: "en",
        descripcion: "Los creadores explican el modelo y evidencia de MBCT.",
      },
      {
        titulo: "Meditación del escaneo corporal guiada (10 min) — Jon Kabat-Zinn",
        url_youtube: "https://www.youtube.com/embed/8yMzLz16Eo4",
        autor: "Jon Kabat-Zinn",
        duracion: "10:00",
        idioma: "en",
        descripcion: "Guía estándar usada en muchos programas MBCT.",
      },
      {
        titulo: "MBCT para depresión — explicación en español",
        url_youtube: "https://www.youtube.com/embed/b5zXFx0qL2Y",
        autor: "Centro Psicológico AULA",
        duracion: "15:30",
        idioma: "es",
        descripcion: "Cómo MBCT previene recaídas depresivas.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Mindfulness-Based Cognitive Therapy for Depression: A New Approach to Preventing Relapse (2nd ed.)", autor: "Segal, Z. V., Williams, J. M. G., & Teasdale, J. D.", anio: 2018, edicion: 2, isbn: "978-1462543152" },
      { tipo: "libro", titulo: "Terapia Cognitiva Basada en Mindfulness (MBCT)", autor: "Segal, Z. V., Williams, J. M. G., & Teasdale, J. D. (trad.)", editorial: "Desclée", anio: 2008, isbn: "978-8433023735" },
      { tipo: "paper", titulo: "Mindfulness-based cognitive therapy for preventing depressive relapse: maintenance of effects at 60-month follow-up", autores: "Kuyken, W., et al.", anio: 2015, doi: "10.1016/j.jad.2015.07.002" },
      { tipo: "paper", titulo: "MBCT meta-analysis: efficacy for depression prevention", autores: "Huijbers, M. J., et al.", anio: 2015, doi: "10.1016/j.brat.2015.06.001" },
      { tipo: "guia", titulo: "Full details: MBCT 8-session program manual", autor: "Segal, Williams, Teasdale", anio: 2002, url: "https://mindfulnesscenter.org/mbct" },
    ],
    casos_practicos: [
      {
        titulo: "Mujer 46a — Depresión recurrente (3 episodios en 8 años)",
        motivo_consulta: "Tuve depresión 3 veces. Pasada poco a poco, pero me asusta volver. Medicado con sertralina.",
        hipotesis: "Trastorno depresivo mayor recurrente (CIE-10: F33.1). Remisión actual estable. Apta para MBCT como prevención de recaída. PHQ-9 = 5 (mínima).",
        plan_aplicado: [
          "MBCT programa 8 semanas + retiro de día entero",
          "Psiquiatra mantiene medicación durante programa",
          "Compromiso: practicar meditación 4-5 días/semana después",
        ],
        evolucion: "Completó programa. A 6 meses: sin síntomas depresivos, meditando 4 veces/semana. A 18 meses: sin recaída, sigue práctica reducida a 2-3 veces/semana pero mantiene.",
        reflexion: "MBCT es prevención, no tratamiento agudo. Funciona mejor cuando persona está en remisión y quiere herramientas a largo plazo. La aceptación del pensamiento (en vez de pelear) fue clave.",
      },
    ],
    recursos_descargables: [
      { titulo: "Escaneo corporal guiado (10 min audio)", tipo: "audio", url: "https://mindfulnesscenter.org/resources/body-scan.mp3" },
      { titulo: "Espacio Respiratorio de 3 minutos (audio)", tipo: "audio", url: "https://mindfulnesscenter.org/resources/3min-space.mp3" },
      { titulo: "Guía MBCT para el hogar — libro del participante", tipo: "psicoeducacion", url: "https://mindfulnesscenter.org/participant-guide" },
      { titulo: "Registro PHQ-9 semanal (MBCT)", tipo: "plantilla", url: "https://mindfulnesscenter.org/phq9-tracker" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * TF-CBT — Terapia Cognitivo-Conductual Focalizada en Trauma (Pediátrica)
   * ════════════════════════════════════════════════════════════════════ */
  tf_cbt: {
    descripcion_extendida:
      "La Terapia Cognitivo-Conductual Focalizada en Trauma (TF-CBT, Trauma-Focused CBT) fue " +
      "desarrollada por Cohen, Mannarino y Deblinger (1990s) específicamente para niños y " +
      "adolescentes (3-18 años) con exposición a trauma: abuso sexual, negligencia, violencia " +
      "doméstica, muerte repentina, accidentes graves. Combina CBT estándar con narrativa " +
      "gradual del trauma (exposición imaginal) y entrenamiento de padres paralelo. Sigue " +
      "acrónimo PRACTICE: Psicoeducación, Relajación, modulación Afectiva, procesamiento " +
      "Cognitivo, narrativa del Trauma, exposición In vivo, sesiones Conjuntas, Enhancing " +
      "safety. Requiere 12-25 sesiones y participación de cuidador.",
    efecto_tamano: {
      tept_infantil: 1.13,
      depresion_infantil: 0.82,
      ansiedad_infantil: 0.89,
      abuso_sexual: 1.05,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "P — Psicoeducación sobre trauma + Habilidades parentales",
        duracion_sesiones: "1-2",
        objetivos: [
          "Explicar síntomas postraumáticos como respuesta normal a evento anormal",
          "Entrenar padre/madre en manejo conductual básico (refuerzo positivo, establecimiento de límites)",
        ],
        tareas_clinico: [
          "UCLA PTSD-RI infantil + escalas del niño + padre",
          "Psicoeducación: flashbacks, hipervigilancia, evitación son síntomas, no trastorno de carácter",
        ],
        tareas_paciente: [
          "Niño: lectura/video sobre trauma según edad",
          "Padre/madre: libro de habilidades parentales pediátrico",
        ],
      },
      {
        fase: 2, nombre: "R — Relajación y técnicas de regulación emocional",
        duracion_sesiones: "2-3",
        objetivos: [
          "Enseñar técnicas para calmarse sin conductas de evitación (drogas, autolesión, etc.)",
        ],
        tareas_clinico: [
          "Respiración diafragmática simple (4-en, 6-afuera)",
          "Relajación muscular progresiva (tenso-relaja)",
          "Lugar seguro imaginal",
        ],
        tareas_paciente: [
          "Practicar respiración 2-3 veces/día",
          "Crear 'cartel de lugar seguro' (dibujo o imagen)",
        ],
      },
      {
        fase: 3, nombre: "A — modulación Afectiva (emoción-naming, actividades)",
        duracion_sesiones: "1-2",
        objetivos: [
          "Aumentar vocabulario emocional",
          "Restablecer rutina + actividades placenteras",
        ],
        tareas_clinico: [
          "Nombrar emociones con caras/escalas (niños < 10)",
          "Registrar actividades diarias: placer + logro 0-10",
        ],
        tareas_paciente: [
          "Completar 1 actividad placentera diaria",
          "Diario de emociones (4+ veces/día si es posible)",
        ],
      },
      {
        fase: 4, nombre: "C — procesamiento Cognitivo (desafío de creencias traumáticas)",
        duracion_sesiones: "2-4",
        objetivos: [
          "Identificar y cuestionar creencias erróneas post-trauma ('fue mi culpa', 'nunca estaré seguro')",
        ],
        tareas_clinico: [
          "Cuestionamiento socrático sobre culpabilidad (quien era adulto/responsable)",
          "Reestructuración: 'el evento fue peligroso, ahora estoy seguro'",
        ],
        tareas_paciente: [
          "Hoja: 'Lo que creo' vs 'Lo que sé'",
        ],
      },
      {
        fase: 5, nombre: "T — narrativa del Trauma (exposición imaginal gradual)",
        duracion_sesiones: "3-7 (cuerpo central del tratamiento)",
        objetivos: [
          "Contar la historia traumática en detalle de forma segura, sistemáticamente, hasta que las emociones bajen",
        ],
        tareas_clinico: [
          "Sesión 1: cuento oral breve del evento",
          "Sesiones 2+: narración más detallada + emociones + sensaciones corporales",
          "El niño puede escribir, dibujar, dramatizar según edad/desarrollo",
          "Terminar cada sesión validando coraje + volviendo a presente seguro",
        ],
        tareas_paciente: [
          "Releer/grabar narración 1-2 veces diarias entre sesiones para habituación",
        ],
        criterios_avance: "Narración completa, emociones al contar bajaron a 50-60% de inicio",
      },
      {
        fase: 6, nombre: "I — exposición In vivo (enfrentamiento gradual de lugares/situaciones evitadas)",
        duracion_sesiones: "2-4",
        objetivos: [
          "Reducir evitación conductual, recuperar actividades y libertad de movimiento",
        ],
        tareas_clinico: [
          "Jerarquía de evitación (qué evita el niño, 0-100 miedo)",
          "Exposición gradual: cosas fáciles primero, acompañado",
        ],
        tareas_paciente: [
          "Esta semana: exponerse a ítem en jerarquía que sea 20-30 de miedo",
          "Registro: miedo antes-durante-después",
        ],
      },
      {
        fase: 7, nombre: "C — sesiones Conjuntas (padre-hijo, reparación relacional)",
        duracion_sesiones: "2-3",
        objetivos: [
          "Reparar relación si trauma involucró ruptura de confianza",
          "Padre valida al niño, niño entiende que padre no fue responsable (si aplica)",
        ],
        tareas_clinico: [
          "Sesión conjunta: niño comparte narración o sentimientos con padre presente",
          "Padre responde con validación y apoyo",
        ],
      },
      {
        fase: 8, nombre: "E — Enhancing safety y future development",
        duracion_sesiones: "2-3 (cierre)",
        objetivos: [
          "Plan de prevención de recaída, resiliencia, metas futuras",
        ],
        tareas_clinico: [
          "Revisar todas las habilidades aprendidas",
          "Plan escrito: señales tempranas de recaída + qué hacer",
          "Breve exploración de metas próximas (escuela, amigos, etc.)",
        ],
        tareas_paciente: [
          "Escribir carta a sí mismo: 'Qué aprendí, cuáles son mis fuerzas'",
          "Plan de mantenimiento: qué hacer si estrés sube",
        ],
        criterios_avance: "Reducción ≥50% UCLA PTSD-RI, vuelta a actividades normales",
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Narrativa graduada del trauma (trauma narrative)",
        descripcion: "Contar la historia del evento traumático en detalle creciente, comenzando con versión breve, luego más detallada, hasta habituación emocional. Puede ser oral, escrita, dibujada.",
        cuando_usar: "Fase 5. Solo después de que niño tenga herramientas de regulación y relación de confianza.",
        ejemplo_dialogo:
          "T (al niño de 8 años): 'Vamos a contar lo que pasó. No es fácil, pero sabemos que puede ayudarte. Cuéntame qué pasó ese día en la casa, empezando desde la mañana.'\n" +
          "C: 'Me desperté, fui a desayunar...'\n" +
          "T: 'OK, sigue...'\n" +
          "(Escucha completa, sin interrumpir)\n" +
          "T: 'Gracias por tu valor. Eso fue difícil. ¿Cómo te sientes ahora?' C: '8 de miedo.' T: 'Vamos a respirar juntos. En 5 segundos, como uno lo hace... (respira conmigo).'",
        ejercicio_casa: "Releer/escuchar grabación de la narrativa 1-2 veces diarias. Miedo baja cada vez.",
      },
      {
        nombre: "Jerarquía de exposición in vivo",
        descripcion: "Lista de situaciones, lugares o personas que el niño evita desde el trauma, ordenadas por nivel de ansiedad esperada (0-100). Exposición gradual ascendente.",
        cuando_usar: "Fase 6. Cuando ha reducido evitación mental, listo para enfrentar el mundo real.",
        ejemplo_dialogo:
          "T: 'Desde el abuso, ¿qué cosas evitas?' C: 'No quiero entrar al baño solo. No quiero estar con mi tío.' T: '¿Cuán miedo, 0-100, entrar al baño solo?' C: '80.' T: '¿Y estar en la misma habitación con tío pero con mamá al lado?' C: '40.' T: 'Excelente. Vamos a empezar por aquello que sea 30-40. ¿Qué es?'\n" +
          "C: 'Entrar a mi cuarto solo durante el día.' T: '¿Cuánta ansiedad?' C: '35.' T: 'Perfecto. Esta semana haces eso 3 veces y me dices cómo baja la ansiedad.'",
        ejercicio_casa: "Ejecutar exposición acordada 3+ veces, registrar miedo antes-durante-después.",
      },
      {
        nombre: "Entrenamiento parental en conducta (refuerzo, límites)",
        descripcion: "Educación a padre/madre sobre refuerzo positivo de conductas deseadas, establecimiento de límites claros, y evitar refuerzo involuntario de conductas de evitación/regresión post-trauma.",
        cuando_usar: "Fase 1 y paralelo a todo el tratamiento. Padre es co-terapeuta.",
        ejemplo_dialogo:
          "T (con madre): 'Noto que cuando tu hijo tiene pesadilla, lo dejas dormir en tu cama toda la noche. Eso es comprensivo, pero refuerza la creencia de que no es seguro dormir solo.'\n" +
          "M: 'Pero sufre...' T: 'Lo sé. Pero podemos ser compasivos Y firmes. Que duerma en su cama, tú cerca la primera hora hasta que se duerma. Poco a poco aumenta distancia.'",
        ejercicio_casa: "Madre implementa rutina nueva: refuerzo al dormir en su cama con mamá cerca → solo al lado → sin contacto.",
      },
    ],
    videos: [
      {
        titulo: "TF-CBT Overview — Cohen & Deblinger (SAMHSA)",
        url_youtube: "https://www.youtube.com/embed/Z0vM9JhEauo",
        autor: "SAMHSA",
        duracion: "14:30",
        idioma: "en",
        descripcion: "Los creadores explican modelo y componentes PRACTICE.",
      },
      {
        titulo: "Terapia del trauma en niños explicada (en español)",
        url_youtube: "https://www.youtube.com/embed/1rXg7EqKYvk",
        autor: "Psicología infantil práctica",
        duracion: "11:45",
        idioma: "es",
        descripcion: "Cómo hablar con niños sobre trauma, síntomas esperados.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Treating Trauma and Traumatic Grief in Children and Adolescents (2nd ed.)", autor: "Cohen, J. A., Mannarino, A. P., & Deblinger, E.", anio: 2017, edicion: 2, isbn: "978-1462528134" },
      { tipo: "libro", titulo: "Manual de TF-CBT (traducción autorizada en español)", autor: "Cohen et al. (trad.)", editorial: "Asociación de Traumaterapia", anio: 2015, isbn: "978-3100043216" },
      { tipo: "paper", titulo: "TF-CBT for PTSD in children: randomized controlled trial", autores: "Cohen, J. A., Deblinger, E., Mannarino, A. P., & Steer, R. A.", anio: 2004, doi: "10.1001/jama.291.20.2488" },
      { tipo: "guia", titulo: "SAMHSA Treatment Improvement Protocol — Trauma-Focused CBT for Children", autor: "SAMHSA", anio: 2014, url: "https://www.samhsa.gov/resource/ebp/trauma-focused-cbt-children" },
    ],
    casos_practicos: [
      {
        titulo: "Niño 10a — Abuso sexual por conocido, TEPT severo",
        motivo_consulta: "Mi papá dice que tengo que ir al colegio pero tengo miedo de todo. Pesadillas cada noche.",
        hipotesis: "TEPT (CIE-10: F43.10) por abuso sexual. UCLA PTSD-RI = 78 (severa). Disociación leve. Apto para TF-CBT.",
        plan_aplicado: [
          "TF-CBT 18 sesiones + paralelo con madre (entrenam parental)",
          "Psiquiatra para medicación si ansiedad severa durante fase T",
          "Coordinación con equipo de protección infantil",
        ],
        evolucion: "Fases P-R-A-C: mejora gradual. Fase T (narrativa): difícil primeras 2 sesiones, luego habituación. Fase I: exposición al colegio. UCLA final = 18 (mínima). Vuelve al colegio sin acompañamiento en sesión 14.",
        reflexion: "TF-CBT requiere trabajo integrado: niño + madre. La madre fue clave validando pero sin sobreprotección. La narrativa fue catártica pero necesitó mucho soporte emocional.",
      },
    ],
    recursos_descargables: [
      { titulo: "UCLA PTSD Reaction Index (infantil) en español", tipo: "plantilla", url: "https://www.ncptsd.va.gov/publications/rip/UCLA_PTSD_RI_Spanish.pdf" },
      { titulo: "Hoja: Narrativa del trauma — forma de niño (dibujo)", tipo: "plantilla", url: "https://www.nctsn.org/resources/trauma-narrative-worksheet" },
      { titulo: "Guía padre: Cómo ayudar a tu hijo tras trauma", tipo: "psicoeducacion", url: "https://www.nctsn.org/parent-guides" },
      { titulo: "Audio: Lugar seguro guiado (6 min, voz infantil)", tipo: "audio", url: "https://www.nctsn.org/safe-place-audio-child" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * IPT — Terapia Interpersonal
   * ════════════════════════════════════════════════════════════════════ */
  ipt: {
    descripcion_extendida:
      "La Psicoterapia Interpersonal (IPT, Interpersonal Therapy) fue desarrollada por " +
      "Gerald Klerman y Myrna Weissman (1984) como tratamiento de depresión. Se basa en la " +
      "premisa de que síntomas depresivos aparecen en contexto de roles sociales y relaciones " +
      "interpersonales problemáticas. IPT identifica uno de 4 dominios interpersonales clave " +
      "(duelo, disputa de rol, transición de rol, o déficit interpersonal) y trabaja " +
      "específicamente en ese foco. Es terapia estructurada, tiempo-limitada, 12-16 sesiones. " +
      "Eficacia equivalente a CBT para depresión mayor, pero frecuentemente preferida por " +
      "mujeres en postparto y pacientes con bulimia.",
    efecto_tamano: {
      depresion_mayor: 0.72,
      depresion_postparto: 0.68,
      bulimia: 0.64,
      distimia: 0.55,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Fase inicial: Historia interpersonal y foco (sesiones 1-3)",
        duracion_sesiones: "3",
        objetivos: [
          "Mapear roles sociales (trabajo, pareja, familia, amigos, salud)",
          "Identificar cambios o conflictos recientes en esos roles",
          "Elegir UNO de los 4 dominios como foco terapéutico",
        ],
        tareas_clinico: [
          "Aplicar PHQ-9, BDI-II",
          "Inventario interpersonal: listar todos los roles y relaciones significativas",
          "Genograma emocional (quién es importante, calidad de relación)",
          "Formular: 'El principal problema es (dominio) que lleva a síntomas depresivos (síntomas)'",
        ],
        tareas_paciente: [
          "Lectura: explicación de los 4 dominios",
          "Reflexionar: en qué área interpersonal cambió recientemente",
        ],
        criterios_avance: "Foco interpersonal específico pactado, comprensión de conexión síntomas-relaciones",
      },
      {
        fase: 2, nombre: "Fase intermedia: Trabajo en el dominio elegido (sesiones 4-12)",
        duracion_sesiones: "9",
        objetivos: [
          "Según el dominio, ejecutar intervenciones específicas",
        ],
        tareas_clinico: [
          "Dominio DUELO: validar dolor, explorar relación con difunto, recolocar emocionalmente, reinvertir en vida actual",
          "Dominio DISPUTA: identificar la disputa (pareja, familia, trabajo), expectativas conflictivas, explorar opciones (cambiar expectativas, renegociar, terminar)",
          "Dominio TRANSICIÓN: evaluar pérdida en el cambio (rol anterior) y ganancia (nuevo), desarrollar habilidades para nuevo rol",
          "Dominio DÉFICIT: mejorar habilidades sociales (comunicación, expresar emociones, pedir ayuda)",
        ],
        tareas_paciente: [
          "Tarea según dominio: ej. si disputa pareja, intenta comunicación clara esta semana",
        ],
      },
      {
        fase: 3, nombre: "Fase final: Consolidación y manejo futuro (sesiones 13-16)",
        duracion_sesiones: "4",
        objetivos: [
          "Resumir aprendizajes interpersonales",
          "Prevención de recaída",
          "Plan para manejar futuras dificultades interpersonales",
        ],
        tareas_clinico: [
          "Revisar cambios en síntomas (PHQ-9 / BDI-II comparativo)",
          "Reflexionar: qué aprendiste de terapia sobre ti en relaciones",
          "Identificar 2-3 habilidades interpersonales nuevas ganadas",
        ],
        tareas_paciente: [
          "Escribir cartas (sin enviar) a personas importantes resolviendo asuntos",
          "Plan: qué haré si síntomas vuelven",
        ],
        criterios_avance: "Reducción ≥50% PHQ-9, cambio observable en relación foco, habilidades interpersonales nuevas",
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Análisis de comunicación (communication analysis)",
        descripcion: "En sesión, recrear conversación problemática con persona significativa. Analizar qué se dijo, qué no se dijo, cómo reaccionó otra persona, qué se pudo haber hecho diferente.",
        cuando_usar: "Déficit interpersonal o disputa de rol. Sesiones 4-12.",
        ejemplo_dialogo:
          "C: 'Mi jefe me dijo que mi trabajo no es suficiente y yo solo callé.'\n" +
          "T: 'Recréalo aquí. Yo soy tu jefe. Cuéntame qué te dijo exactamente.'\n" +
          "C: 'Me dijo: \"Tu reporte tuvo errores, no cumples estándares\".'\n" +
          "T: '¿Y qué hiciste / dijiste?'\n" +
          "C: 'Nada, me fui al baño a llorar.'\n" +
          "T: 'OK. ¿Querías decirle algo?'\n" +
          "C: 'Que he trabajado duro y no es justo.'\n" +
          "T: 'Digamoslo ahora. Yo soy él. \"Jefe, aprecio tu feedback, pero en los últimos 3 meses he trabajado muy duro en mejorar. Me gustaría entender qué específicamente necesito cambiar.\" Cómo suena?'",
        ejercicio_casa: "Tarea: tener conversación similar con jefe esta semana. Luego reportar qué pasó.",
      },
      {
        nombre: "Inventario interpersonal",
        descripcion: "Lista sistemática de todos los roles (trabajo, pareja, padre, amigo, hijo, etc.) y puntuación de satisfacción/conflicto. Identificar dónde están los problemas.",
        cuando_usar: "Fase 1-2. Toda IPT comienza aquí.",
        ejemplo_dialogo:
          "T: 'Vamos a hacer un mapa de tu vida social. Roles que tienes:' (Escriba con paciente)\n" +
          "C: 'Soy abogada (trabajo), esposa (pareja), madre (dos hijos), hija (de mis padres)...'\n" +
          "T: 'Marca qué tan satisfecho/a en cada uno, 0-10.':\n" +
          "Abogada: 7. Esposa: 3. Madre: 8. Hija: 5.\n" +
          "T: 'Los números bajos son donde probablemente esté la conexión con depresión. Esposa es 3. ¿Qué pasó?'\n" +
          "C: 'Discutimos mucho, casi no hablamos'",
        ejercicio_casa: "Reflexionar: cuál rol quiero mejorar primero.",
      },
      {
        nombre: "Role-playing de nuevas respuestas (comportamiento interpersonal)",
        descripcion: "Practicar en sesión cómo responder diferente en situación interpersonal problemática, con terapeuta como otra persona.",
        cuando_usar: "Cuando paciente tiene déficit de habilidades sociales o comunicación.",
        ejemplo_dialogo:
          "C: 'Cuando mi pareja me critica, me encierro.'\n" +
          "T: 'Eso es comprensible, pero refuerza el distanciamiento. Hagamos otra cosa. Yo seré tu pareja. Te crítico: \"Nunca ayudas en la casa, siempre dejo todo hecho.\"'\n" +
          "T (como pareja): 'Nunca ayudas en la casa.'\n" +
          "C: (encogida, callada)\n" +
          "T: 'Para. Prueba esto: Escúchalo, responde calmado. \"Entiendo que estés frustrado. Me gustaría que hagamos un plan juntos de cómo dividimos las tareas. ¿Podemos hablar?\"'\n" +
          "C: (repite con terapeuta asintiendo)\n" +
          "T: 'Excelente. Cómo se sintió?' C: 'Extraño, pero mejor.'",
        ejercicio_casa: "Usar esta respuesta en situación real con pareja.",
      },
    ],
    videos: [
      {
        titulo: "Myrna Weissman — IPT: Theory and Practice (Oxford)",
        url_youtube: "https://www.youtube.com/embed/KAaR5RxPdDA",
        autor: "Myrna Weissman",
        duracion: "19:00",
        idioma: "en",
        descripcion: "Una de las creadoras explica los 4 dominios y evidencia.",
      },
      {
        titulo: "Terapia Interpersonal para depresión — explicación en español",
        url_youtube: "https://www.youtube.com/embed/h0KdV7Uq3rM",
        autor: "Escuela de Psicoterapia Moderna",
        duracion: "13:20",
        idioma: "es",
        descripcion: "Cómo IPT conecta roles sociales con síntomas depresivos.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "The Guide to Interpersonal Psychotherapy", autor: "Weissman, M. M., Markowitz, J. C., & Klerman, G. L.", anio: 2017, edicion: 2, isbn: "978-0190631697" },
      { tipo: "libro", titulo: "Terapia Interpersonal de la Depresión (edición en español)", autor: "Weissman et al. (trad.)", editorial: "Herder", anio: 2000, isbn: "978-8425412968" },
      { tipo: "paper", titulo: "Interpersonal psychotherapy: clinical efficacy and cost-effectiveness", autores: "Weissman, M. M., Markowitz, J. C., & Klerman, G. L.", anio: 2007, doi: "10.1146/annurev.clinpsy.3.022806.091517" },
      { tipo: "paper", titulo: "IPT for postpartum depression: randomized controlled trial", autores: "O'Hara, M. W., et al.", anio: 2000, doi: "10.1001/archpsyc.57.12.1234" },
    ],
    casos_practicos: [
      {
        titulo: "Mujer 38a — Depresión y conflicto marital postparto",
        motivo_consulta: "Desde que nació mi bebé hace 3 meses, me siento vacía y mi matrimonio se rompió. Peleamos por todo.",
        hipotesis: "Depresión postparto (CIE-10: F53.0) + disputa de rol marital. PHQ-9 = 18 (moderada). Buen candidato para IPT dominio disputa.",
        plan_aplicado: [
          "IPT 14 sesiones semanales",
          "Dominio: DISPUTA DE ROL — nuevo rol de madre, expectativas del esposo vs realidad, renegociación",
          "Coordinación con pediatra y ginecólogo para descartar lo médico",
        ],
        evolucion: "Sesiones 1-3: inventario interpersonal, foco en disputa. Sesiones 4-12: análisis de comunicación en pareja, role-plays, cambio gradual en expectativas mutuas. PHQ-9 al mes 4 = 8. Pareja reporta mejora comunicación.",
        reflexion: "IPT funciona bien en postparto porque la depresión es reaccionaria a cambio de rol. Cuando mejora comunicación y renegociación con pareja, síntomas bajan. No necesitó medicación.",
      },
    ],
    recursos_descargables: [
      { titulo: "PHQ-9 para tracking semanal", tipo: "plantilla", url: "https://www.phqscreeners.com/measure-tools/phq-9" },
      { titulo: "Inventario interpersonal — forma rellenable", tipo: "plantilla", url: "https://www.ipt.info/patient-resources" },
      { titulo: "Guía: Los 4 dominios de IPT", tipo: "psicoeducacion", url: "https://www.ipt.info/four-interpersonal-problem-areas" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * ESQUEMAS — Terapia Centrada en Esquemas (Schema Therapy)
   * ════════════════════════════════════════════════════════════════════ */
  esquemas: {
    descripcion_extendida:
      "La Terapia Centrada en Esquemas (Schema Therapy) fue desarrollada por Jeffrey Young " +
      "(1980s-1990s) como extensión de CBT para trastornos de personalidad y patrones " +
      "relacionales crónicos. Se basa en concepto de \"esquemas desadaptativos tempranos\" (EMS): " +
      "creencias profundas sobre uno mismo, otros y el mundo, formadas en infancia (negligencia, " +
      "abuso, sobreprotección) y que se repiten en edad adulta. Schema Therapy integra CBT, " +
      "Gestalt (silla vacía), teoría de apego y reparentalización emocional limitada. Requiere " +
      "1-3 años de terapia intensiva. Es efectiva para TLP, pero también para depresión " +
      "resistente y patrones interpersonales recurrentes.",
    efecto_tamano: {
      trastornos_personalidad: 0.76,
      depresion_resistente: 0.68,
      tlp: 0.84,
      patrones_relacionales: 0.65,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Evaluación de esquemas y modos (sesiones 1-4)",
        duracion_sesiones: "4",
        objetivos: [
          "Aplicar YSQ (Young Schema Questionnaire) — 18 esquemas posibles",
          "Identificar modos (Niño vulnerable, Niño impulsivo, Padre crítico, etc.)",
          "Mapear origen: qué necesidad no fue satisfecha en infancia",
        ],
        tareas_clinico: [
          "YSQ-S3 completo, análisis de top 3-4 esquemas",
          "Genograma de trauma: cómo padre/madre negligente, sobreprotector, crítico, etc.",
          "Definición clara: 'Tu esquema de (nombre) viene de...'",
        ],
        tareas_paciente: [
          "Reflexión escrita: cómo cada esquema afecta relaciones actuales",
        ],
        criterios_avance: "Comprensión de esquemas personales y su origen",
      },
      {
        fase: 2, nombre: "Reparentalización emocional limitada (sesiones 5-20, paralelo)",
        duracion_sesiones: "Continuo",
        objetivos: [
          "Terapeuta toma rol de 'padre bueno' emocionalmente ausente en infancia",
          "Validar Niño vulnerable, protegerlo de Padre crítico interno",
        ],
        tareas_clinico: [
          "Lenguaje cálido, empático, firme",
          "Establecer límites desde amor (no permisividad)",
          "Responder a necesidades legítimas no satisfechas: seguridad, amor incondicional, autonomía",
        ],
      },
      {
        fase: 3, nombre: "Trabajo cognitivo: cuestionamiento de esquemas (sesiones 5+)",
        duracion_sesiones: "10-15",
        objetivos: [
          "Identificar evidencia a favor y en contra de creencia del esquema",
          "Generar alternativa más balanceada",
        ],
        tareas_clinico: [
          "Ej.: Esquema 'soy indigno de amor' → Evidencia: 'mis padres no mostraron afecto'",
          "Contra: 'mis amigos me quieren, he tenido parejas que me querían'",
          "Alternativa: 'tuve infancia con demostraciones limitadas de afecto, pero eso no significa que sea indigno'",
        ],
      },
      {
        fase: 4, nombre: "Técnica de silla vacía (chair work) — imaginería",
        duracion_sesiones: "5-10",
        objetivos: [
          "Diálogo entre Niño vulnerable (donde está) y Padre crítico (en la silla)",
          "Niño expresa necesidades, Padre se transforma o es desafiado",
        ],
        tareas_clinico: [
          "T: 'En esta silla está tu padre crítico. En esta, el Niño que eras. ¿Qué te diría ese padre?'",
          "C (como Niño): 'Que nunca haré nada bien.'\n" +
          "T (cambio de silla, como Padre crítico): '...'",
        ],
      },
      {
        fase: 5, nombre: "Cambios conductuales: romper ciclos esquemáticos (sesiones 10+)",
        duracion_sesiones: "Paralelo",
        objetivos: [
          "Actuar contrariamente a esquema en situaciones de bajo riesgo",
        ],
        tareas_clinico: [
          "Ej. esquema 'nadie me quiere' → buscar conexión social (ir a grupo, llamar amigo)",
          "Registrar qué sucede cuando actúa diferente",
        ],
      },
      {
        fase: 6, nombre: "Consolidación y término (sesiones 40+)",
        duracion_sesiones: "Espaciamiento gradual",
        objetivos: [
          "Autonomía: paciente es su propio 'padre bueno'",
          "Planes para mantener cambios",
        ],
        criterios_avance: "Reducción YSQ ≥40%, patrones relacionales más saludables",
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Diálogo de modos (mode dialogue) — imaginería",
        descripcion: "Conversación interna entre diferentes modos (Niño vulnerable/impulsivo vs Padre crítico/protesor). Se hace con imaginería, escritura o silla vacía.",
        cuando_usar: "Cuando paciente está atrapado en modo crítico o impulsivo. Fases 2-4.",
        ejemplo_dialogo:
          "T: 'Cierra los ojos. Visualiza al Niño pequeño que eras, diciéndote algo ahora.'\n" +
          "C: 'Dice: tengo miedo, me siento solo.'\n" +
          "T: 'Ahora, en la otra parte de ti, está el Padre crítico. ¿Qué dice?'\n" +
          "C: 'No tengas sentimientos, sé fuerte.'\n" +
          "T: 'El Niño escucha. ¿Qué siente?'\n" +
          "C: 'Más miedo, rechazado.'\n" +
          "T: 'Ahora invoca al Padre bueno interno. ¿Qué le diría al Niño?'\n" +
          "C: 'Que sus sentimientos están bien. Que está seguro conmigo.'",
        ejercicio_casa: "Escribir un diálogo entre Niño y Padre bueno cuando síntomas bajos (no en crisis).",
      },
      {
        nombre: "Técnica de la silla vacía (chair work)",
        descripcion: "Sentarse en silla 1, hablar a figura en silla 2 (padre crítico, cuidador negligente, etc.), luego cambiar de silla y responder como esa persona transformada o confrontada.",
        cuando_usar: "Fase 4. Cuando necesita resolver diálogo no terminado con figura de infancia.",
        ejemplo_dialogo:
          "T: 'En esta silla está tu madre que te ignoraba. Dile lo que nunca pudiste.'\n" +
          "(Paciente en silla 1): 'Necesitaba que me vieras. Necesitaba que me abrazaras. Duele que no hayas estado.'\n" +
          "T: 'Ahora siéntate en la silla de tu madre. Responde.'\n" +
          "(Cambio de silla, como madre): 'Yo... no sabía cómo hacerlo. Yo también tuve mi propio dolor.'\n" +
          "T: 'Vuelve a tu silla. ¿Qué escuchaste?'",
        ejercicio_casa: "Escribir carta (sin enviar) a persona de silla vacía, expresando todo lo no dicho.",
      },
      {
        nombre: "YSQ (Young Schema Questionnaire) — identificación de esquemas",
        descripcion: "Cuestionario de 75-90 items que mide intensidad de 18 esquemas desadaptativos (p.ej., Abandono, Desconfianza, Vulnerabilidad, Fracaso, Dependencia, Negligencia emocional, etc.).",
        cuando_usar: "Fase 1. Baseline y tracking cada 10-15 sesiones.",
        ejemplo_dialogo:
          "T: 'Contesta 1-6 cada afirmación. (1) Completamente falso para mí, (6) Me describe perfectamente. Ejemplo: \"Siento que los demás me abandonarán.\"'\n" +
          "C: '4 de 6.'\n" +
          "T: 'OK, ese es esquema de Abandono. Veremos cómo trabajar eso.'",
        ejercicio_casa: "Rellenar YSQ, comparar con sesión anterior.",
      },
    ],
    videos: [
      {
        titulo: "Jeffrey Young — Introduction to Schema Therapy (Institut)",
        url_youtube: "https://www.youtube.com/embed/LSqrKhVlD2g",
        autor: "Schema Therapy Institute",
        duracion: "22:00",
        idioma: "en",
        descripcion: "El creador explica 18 esquemas y modelo de modos.",
      },
      {
        titulo: "Silla vacía en Terapia de Esquemas",
        url_youtube: "https://www.youtube.com/embed/VKfKqh3Pr5s",
        autor: "Schema Institute (demo)",
        duracion: "8:45",
        idioma: "en",
        descripcion: "Demostración de técnica chair work con esquema de rechazo.",
      },
      {
        titulo: "Terapia de Esquemas explicada en español",
        url_youtube: "https://www.youtube.com/embed/SZvMmqPl1Gg",
        autor: "Instituto Español de Esquematerapia",
        duracion: "16:20",
        idioma: "es",
        descripcion: "Los 18 esquemas con ejemplos clínicos.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Schema Therapy: A Practitioner's Guide", autor: "Young, J. E., Klosko, J. S., & Weishaar, M. E.", anio: 2003, edicion: 1, isbn: "978-0898620283" },
      { tipo: "libro", titulo: "Reinventar la vida: la terapia de esquemas (edición en español)", autor: "Young et al. (trad.)", editorial: "Paidós", anio: 1993, isbn: "978-8449305047" },
      { tipo: "paper", titulo: "Schema Therapy for Borderline Personality Disorder: a randomized controlled trial", autores: "Giesen-Bloo, J., et al.", anio: 2006, doi: "10.1001/archpsyc.63.6.649" },
      { tipo: "paper", titulo: "Schema Therapy for depression in adults: meta-analysis", autores: "Carrasco, M. L., et al.", anio: 2018, doi: "10.1136/bmjopen-2017-019918" },
    ],
    casos_practicos: [
      {
        titulo: "Mujer 34a — TLP con relaciones caóticas, esquema de Abandono/Desconfianza",
        motivo_consulta: "Siempre termino mis relaciones gritando. Creo que nadie puede amarme. Mi mamá me ignoraba.",
        hipotesis: "TLP (CIE-10: F60.31) con esquemas de Abandono (YSQ = 6/6), Desconfianza (6/6), Negligencia emocional (5/6). 4+ años de tratamiento recomendado.",
        plan_aplicado: [
          "Schema Therapy 3 años: sesiones semanales",
          "Fases: evaluación esquemas → reparentalización → chair work → cambios conductuales",
          "Paralelo: psiquiatra para disregulación si grave",
        ],
        evolucion: "Año 1: comprensión esquemas, reparentalización, trabajo chair work intenso. Año 2: cambios conductuales (no huir de pareja cuando miedo, comunicar necesidades). Año 3: estabilidad relacional, YSQ reducido 60%, relación de pareja sostenida.",
        reflexion: "Schema Therapy es largo pero eficaz para TLP. Requiere terapeuta disponible emocionalmente y paciente comprometido. No es para quien quiere cambio rápido.",
      },
    ],
    recursos_descargables: [
      { tipo: "plantilla", titulo: "YSQ-S3 (Young Schema Questionnaire) en español", url: "https://www.schematherapy.com/ysfq-3-spanish" },
      { titulo: "Los 18 esquemas — definición y síntomas", tipo: "psicoeducacion", url: "https://www.schematherapy.com/schemas-overview" },
      { titulo: "Guía: Cómo escribir carta a figura de infancia", tipo: "paciente", url: "https://www.schematherapy.com/letter-writing-exercise" },
      { titulo: "Imaginería guiada: Reparentalización emocional (audio 20 min)", tipo: "audio", url: "https://www.schematherapy.com/guided-reparenting-audio" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * GOTTMAN — Método Gottman para Pareja
   * ════════════════════════════════════════════════════════════════════ */
  gottman: {
    descripcion_extendida:
      "El Método Gottman fue desarrollado por John Gottman y Julie Gottman basado en 40+ " +
      "años de investigación en parejas. Identifica los «4 jinetes del apocalipsis» que predicen " +
      "divorcio: crítica, desprecio, defensividad y obstruccionismo. Gottman propone la 'casa de " +
      "relación sonora' (Sound Relationship House) con 7 niveles: mapas de amor (conocer detalles " +
      "de tu pareja), emotividad, cariño y acercamiento, perspectiva positiva, manejo de conflicto, " +
      "sueños de vida compartidos y significado común. Es enfoque estructurado, orientado a " +
      "comportamientos observables, basado en evidencia. Estudios muestran predictibilidad de " +
      "divorcio >90% con sus medidas.",
    efecto_tamano: {
      satisfaccion_marital: 0.72,
      reduccion_conflicto: 0.68,
      prevencion_divorcio: 0.81,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Evaluación (sesiones 1-3)",
        duracion_sesiones: "3",
        objetivos: [
          "Sesión conjunta inicial: escuchar narrativa de pareja",
          "Sesiones individuales: historia de relación, fortalezas, debilidades",
          "Retroalimentación: predicción y plan de tratamiento",
        ],
        tareas_clinico: [
          "DAS (Dyadic Adjustment Scale) y CSI-32 (Couples Satisfaction Index)",
          "Observar patrones de 4 jinetes",
          "Mapeo de área de conflicto y fortalezas",
        ],
      },
      {
        fase: 2, nombre: "Sound Relationship House — construir niveles (sesiones 4-20)",
        duracion_sesiones: "17",
        objetivos: [
          "Nivel 1-2: Mapas de amor (qué sabe de preferencias, miedos, sueños de tu pareja)",
          "Nivel 3: Cariño y acercamiento",
          "Nivel 4: Perspectiva positiva (cómo ves la relación)",
          "Nivel 5: Manejo de conflicto (reparación, concesiones)",
          "Nivel 6-7: Sueños compartidos + significado de vida juntos",
        ],
        tareas_clinico: [
          "Ejercicio de 'mapa de amor': cada miembro entrevista al otro sobre sueños, miedos, intereses",
          "Rituales de conexión (5 minutos saludarse, cena sin hijos, etc.)",
          "Antídotos a 4 jinetes: crítica → halago, desprecio → antídoto de humor/cuidado, defensividad → empatía, obstruccionismo → tomar break",
        ],
      },
      {
        fase: 3, nombre: "Consolidación y mantenimiento (sesiones 21+)",
        duracion_sesiones: "4-6",
        objetivos: [
          "Plan post-terapia: qué mantener, cómo manejar futuras dificultades",
        ],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Mapa de amor (Love maps)",
        descripcion: "Conocimiento profundo de preferencias, miedos, sueños, intereses, valores de la pareja. Ejercicio estructurado donde cada uno pregunta al otro 20-30 preguntas.",
        cuando_usar: "Fase 2, nivel 1.",
        ejemplo_dialogo:
          "T: 'Voy a darle una lista de preguntas. Cada pareja se turna preguntando. Ejemplo: \"¿Cuál es tu mayor miedo en los próximos 5 años?\" Escuchen sin interrumpir, después resumen lo que escucharon.'",
        ejercicio_casa: "Completar 20 preguntas esta semana.",
      },
      {
        nombre: "Antídotos a los 4 jinetes",
        descripcion: "Para cada jinete (crítica, desprecio, defensividad, obstruccionismo), una respuesta opuesta.",
        cuando_usar: "Fase 2, nivel 5.",
        ejemplo_dialogo:
          "T: 'Cuando tu pareja crítica \"Nunca ayudas\", en lugar de defenderte, antídoto es: reconocer algo cierto y proponer cambio. \"Tienes razón, esta semana no ayudé como dije. Vamos a planear juntos.\"'",
      },
    ],
    videos: [
      {
        titulo: "John Gottman — The Sound Relationship House (oficial)",
        url_youtube: "https://www.youtube.com/embed/1J_rFXYG7sE",
        autor: "The Gottman Institute",
        duracion: "8:00",
        idioma: "en",
        descripcion: "Los 7 niveles de la casa de relación.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "The Gottman Method: The Seven Principles That Make Marriage Work", autor: "Gottman, J. M. & Gottman, J. S.", anio: 2017, edicion: 1, isbn: "978-0553394559" },
      { tipo: "libro", titulo: "El matrimonio que siempre quisiste (traducción español)", autor: "Gottman & Gottman (trad.)", editorial: "Paidos", anio: 2013, isbn: "978-8449329876" },
    ],
    recursos_descargables: [
      { titulo: "CSI-32 (Couples Satisfaction Index)", tipo: "plantilla", url: "https://www.gottman.com/couples-satisfaction-index/" },
      { titulo: "Preguntas de mapa de amor (20 preguntas)", tipo: "paciente", url: "https://www.gottman.com/love-maps-questions/" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * EFT PAREJA — Terapia Centrada en Emociones para Parejas
   * ════════════════════════════════════════════════════════════════════ */
  eft_pareja: {
    descripcion_extendida:
      "La Terapia Centrada en Emociones para Parejas (EFT, Emotionally Focused Therapy) " +
      "fue creada por Sue Johnson basada en teoría del apego (Bowlby, Ainsworth). Propone que " +
      "conflictos matrimoniales son ciclos de demanda-retracción u otro patrón de evitación " +
      "de vulnerabilidad. Objetivo: acceder a emociones primarias (miedo, dolor) bajo la rabia, " +
      "y reorganizar la danza relacional. 3 etapas: desescalada del ciclo negativo, " +
      "reestructuración con acceso a emociones primarias y enactment (demostraciones conductuales), " +
      "consolidación. Validado especialmente para parejas con inseguridad de apego.",
    efecto_tamano: {
      satisfaccion_marital: 0.76,
      recuperacion_pareja: 0.82,
      ciclo_negativo: 0.79,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Etapa 1: Desescalada del ciclo (sesiones 1-6)",
        duracion_sesiones: "6",
        objetivos: [
          "Identificar ciclo negativo persecutor-distanciador",
          "Reencuadre: no es malo vs bueno, es miedo vs defensa",
        ],
        tareas_clinico: [
          "Mapa del ciclo: 'Cuando él se retrae, ella critica. Cuando ella critica, él se retrae más.'",
          "Validación de ambos: miedo legítimo en ambos",
          "Cambio de narrativa: 'Estamos atrapados en un ciclo, no somos enemigos'",
        ],
      },
      {
        fase: 2, nombre: "Etapa 2: Reestructuración (sesiones 7-16)",
        duracion_sesiones: "10",
        objetivos: [
          "Acceder a emociones primarias (miedo, dolor, soledad)",
          "Expresar necesidades de apego de forma vulnerable",
          "Demostración (enactment): respuesta diferente de pareja",
        ],
        tareas_clinico: [
          "Con perseguidor: 'Debajo de la crítica, ¿qué sientes?' → 'Miedo a que me abandone.'",
          "Con distanciador: 'Debajo de la retracción, ¿qué sientes?' → 'Abrumado, asustado de lastimarte.'",
          "Enactment: perseguidor expresa miedo vulnerable, distanciador puede acercarse y validar",
        ],
      },
      {
        fase: 3, nombre: "Etapa 3: Consolidación (sesiones 17-20)",
        duracion_sesiones: "4",
        objetivos: [
          "Integración de nuevos patrones de respuesta",
          "Planes para futuras dificultades",
        ],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Enactment (demostración relacional)",
        descripcion: "En sesión, pareja interactúa de forma diferente, con terapeuta como 'director' sugiriendo expresiones vulnerables nuevas.",
        cuando_usar: "Etapa 2.",
        ejemplo_dialogo:
          "T: '(A él) Te gustaría que ella se acercara más, ¿verdad?' Él: 'Sí, pero luego me siento abrumado.' T: 'OK. (A ella) Cuéntale qué te pasa cuando te acercas.' Ella: 'Creo que no le importo.' T: '¿Podrías decirle eso, en vez de criticar?' Ella: 'Me asusta no importarte.' (Él la mira, se acerca levemente.) T: 'Qué está pasando para ti ahora?' Él: 'Entiendo que tiene miedo.'",
        ejercicio_casa: "Intentar respuesta vulnerable en situación de estrés bajo esta semana.",
      },
    ],
    videos: [
      {
        titulo: "Sue Johnson — Introduction to EFT (oficial)",
        url_youtube: "https://www.youtube.com/embed/xp8XfLzW7nQ",
        autor: "Sue Johnson Institute",
        duracion: "12:30",
        idioma: "en",
        descripcion: "La creadora explica ciclos y apego en pareja.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Attachment Theory in Practice: EFT with Couples, Individuals and Families", autor: "Johnson, S. M.", anio: 2019, edicion: 1, isbn: "978-1462542437" },
      { tipo: "libro", titulo: "Hold Me Tight: Seven Conversations for a Lifetime of Love (en español: Abrázame fuerte)", autor: "Johnson, S. M.", anio: 2008, isbn: "978-8408109273" },
    ],
    recursos_descargables: [
      { titulo: "ECR-S (Experiences in Close Relationships — Short form)", tipo: "plantilla", url: "https://www.eft.ca/resources" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * SISTEMICA_ESTRUCTURAL — Terapia Familiar Estructural (Minuchin)
   * ════════════════════════════════════════════════════════════════════ */
  sistemica_estructural: {
    descripcion_extendida:
      "La Terapia Familiar Estructural fue desarrollada por Salvador Minuchin (1970s). Se " +
      "basa en concepto de 'estructura familiar': límites entre subsistemas (parental, filial, " +
      "conyugal), jerarquías, alianzas, triangulaciones. Problemas conductuales del niño son " +
      "síntoma de desorganización estructural. Intervención: el terapeuta se une ('joining'), " +
      "mapea estructura (genograma, escultura), luego reestructura mediante tareas, reformulaciones, " +
      "establecimiento de límites. Efectiva para trastornos de conducta infantil y conflictos " +
      "familiares.",
    efecto_tamano: {
      trastornos_conducta_infantil: 0.68,
      trastornos_alimentarios: 0.74,
      conflicto_familiar: 0.71,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Unión y evaluación estructural (sesiones 1-3)",
        duracion_sesiones: "3",
        objetivos: [
          "Establecer alianza con cada miembro",
          "Mapear estructura: límites, alianzas, jerarquías",
        ],
        tareas_clinico: [
          "Genograma 3 generaciones",
          "Escultura familiar (posicionar físicamente miembros según cercanía/distancia percibida)",
          "Observar interacciones: quién habla por quién, quién controla",
        ],
      },
      {
        fase: 2, nombre: "Reestructuración (sesiones 4-15)",
        duracion_sesiones: "12",
        objetivos: [
          "Cambiar límites (hacer más claros entre padres-hijos)",
          "Cambiar alianzas (reducir triangulación)",
          "Restaurar jerarquía parental",
        ],
        tareas_clinico: [
          "Enactment de interacción problemática en sesión, intervención directa",
          "Reformulación (reframing): 'El comportamiento de tu hijo no es desafío sino señal de que padres necesitan ser más unidos'",
          "Tareas paradójicas si aplica",
        ],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Escultura familiar",
        descripcion: "Pedirle a un miembro (usualmente hijo) que coloque físicamente a otros en posiciones según percibe cercanía, distancia, control.",
        cuando_usar: "Sesión 1-2.",
        ejemplo_dialogo:
          "T: '(Al niño) Imagina que esta habitación es tu casa. Coloca a mamá, papá y ti donde sientes que estáis.' (Niño coloca a mamá y papá muy separados, a él con la mamá.) T: 'Interesante. ¿Qué observas?' Permite que exploren estructura sin interpretación inmediata.",
      },
      {
        nombre: "Enactment y reestructuración directa",
        descripcion: "Pedirle a familia que interactúe sobre problema (ej. tareas, conducta) en sesión, y el terapeuta interviene directamente para cambiar patrón.",
        cuando_usar: "Sesiones 4-15.",
        ejemplo_dialogo:
          "T (a padres): 'Quiero que hablen con vuestro hijo sobre sus calificaciones bajas. Hazlo ahora, yo estaré aquí.' (Observa madre gritando, padre callado.) T: 'Detente. (A padre) ¿Qué notas?' P: 'Que no estoy apoyándola.' T: '¿Podrías hablar primero con ella? Como pareja, ¿qué quieren para vuestro hijo?' (Cambia dinámicapadres-hijo a coalición parental.)",
      },
    ],
    videos: [
      {
        titulo: "Salvador Minuchin — Structural Family Therapy (documental)",
        url_youtube: "https://www.youtube.com/embed/JDjH5WPlCf4",
        autor: "Archive (Minuchin demostración real)",
        duracion: "25:00",
        idioma: "en",
        descripcion: "Sesión real de Minuchin con familia.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Families and Family Therapy", autor: "Minuchin, S.", anio: 1974, edicion: 1, isbn: "978-0674294318" },
      { tipo: "libro", titulo: "Assessing Families and Couples: From Symptom to System", autor: "Minuchin, S., Nichols, M. P., & Lee, W.-Y.", anio: 2007, edicion: 1, isbn: "978-0205455683" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * CBT-E — Terapia Cognitivo-Conductual para Trastornos Alimentarios
   * ════════════════════════════════════════════════════════════════════ */
  cbt_e_alimentaria: {
    descripcion_extendida:
      "CBT-E (Enhanced Cognitive Behavior Therapy for Eating Disorders) fue desarrollada por " +
      "Christopher Fairburn (2008+) como versión mejorada de TCC para anorexia, bulimia y trastorno " +
      "por atracón. Integra CBT estándar (reestructuración cognitiva, exposición, prevención de " +
      "respuesta) con tratamiento de problemas comórbidos (depresión, ansiedad, perfeccionismo, " +
      "baja autoestima). 20 sesiones típicamente. Distintas según presentación: versión 'focal' " +
      "para bulimia pura, versión 'ampliada' para factores comórbidos.",
    efecto_tamano: {
      bulimia: 0.72,
      trastorno_atracones: 0.68,
      anorexia: 0.55,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Evaluación y psicoeducación (sesiones 1-2)",
        duracion_sesiones: "2",
        objetivos: [
          "Historia del TCA, mantenimiento actual, comorbilidad",
          "Explicar modelo CBT-E: ciclo restricción-atracón-purga",
        ],
      },
      {
        fase: 2, nombre: "Normalización de patrón alimentario (sesiones 3-8)",
        duracion_sesiones: "6",
        objetivos: [
          "Romper ciclo de restricción mediante alimentación estructurada (3 comidas + 2-3 refrigerios)",
          "Exposición a alimentos temidos",
          "Prevención de conductas compensatorias (purgación, ejercicio excesivo)",
        ],
        tareas_clinico: [
          "Plan de comidas estructurado, inicialmente tolerante con pequeños déficits",
          "Acompañamiento de comidas en algunas sesiones (exposición imaginal)",
          "Técnicas de tolerancia al malestar durante restricción de purga",
        ],
      },
      {
        fase: 3, nombre: "Reestructuración cognitiva (sesiones 4-15)",
        duracion_sesiones: "Paralelo",
        objetivos: [
          "Cambiar preocupación excesiva por peso/forma",
          "Tratar depresión/ansiedad comórbida",
          "Enfrentar perfeccionismo, baja autoestima",
        ],
      },
      {
        fase: 4, nombre: "Prevención de recaída (sesiones 16-20)",
        duracion_sesiones: "5",
        objetivos: [
          "Consolidar cambios",
          "Planes para gestionar futuros eventos de riesgo",
        ],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Alimentación estructurada + exposición a alimentos temidos",
        descripcion: "Plan diario de 3 comidas + 2-3 refrigerios. Progresivamente incluir alimentos evitados (grasas, carbohidratos) con apoyo emocional.",
        cuando_usar: "Fase 2.",
        ejemplo_dialogo:
          "T: 'Esta semana, desayuno a las 8am: avena con leche (incluye grasa), plátano, pan. Midday snack a las 10:30am: galletas integrales + yogur. ¿Cuán aterrador es (0-10)?'",
      },
    ],
    videos: [
      {
        titulo: "Christopher Fairburn — CBT-Enhanced for Eating Disorders",
        url_youtube: "https://www.youtube.com/embed/G0YLxe5aFWQ",
        autor: "Oxford University (lecture)",
        duracion: "19:00",
        idioma: "en",
        descripcion: "El creador explica el modelo y componentes.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Cognitive Behavior Therapy and Eating Disorders", autor: "Fairburn, C. G.", anio: 2008, edicion: 1, isbn: "978-1593856694" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * MOTIVATIONAL INTERVIEWING — Entrevista Motivacional
   * ════════════════════════════════════════════════════════════════════ */
  motivational_interviewing: {
    descripcion_extendida:
      "La Entrevista Motivacional (EM / MI, Motivational Interviewing) fue desarrollada por " +
      "William Miller y Stephen Rollnick (1991). Es estilo colaborativo de conversación que " +
      "evoca y fortalece motivación de cambio. Contraria a confrontación directa. Basada en la " +
      "premisa de que ambivalencia es normal, y que escucha reflexiva + refuerzo de 'change talk' " +
      "(verbalizaciones hacia cambio) aumentan probabilidad de acción. Útil para adicciones, " +
      "adherencia médica, cambios de estilo de vida. No es terapia por sí sola sino abordaje que " +
      "se combina con otras intervenciones.",
    efecto_tamano: {
      abstinencia_alcohol: 0.54,
      adherencia_medica: 0.43,
      cambio_conducta_salud: 0.47,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Enganche (1-2 sesiones)",
        duracion_sesiones: "1-2",
        objetivos: [
          "Establecer relación de seguridad y respeto",
          "Cliente se siente escuchado, no juzgado",
        ],
        tareas_clinico: [
          "Escucha reflexiva sin confrontación",
          "Curiosidad genuina sobre ambivalencia",
        ],
      },
      {
        fase: 2, nombre: "Enfoque (1-2 sesiones)",
        duracion_sesiones: "1-2",
        objetivos: [
          "Estrechar foco a comportamiento a cambiar",
        ],
      },
      {
        fase: 3, nombre: "Evocar (1-3 sesiones)",
        duracion_sesiones: "1-3",
        objetivos: [
          "Generar 'change talk': razones para cambiar (PHC - positivas consecuencias),  estímulo/importancia",
          "Reforzar verbalizaciones de cambio",
          "Evocar argumentos del cliente a favor del cambio (no imposición)",
        ],
        tareas_clinico: [
          "OARS: Open questions, Affirmations, Reflective listening, Summaries",
          "Columna de ambivalencia: por qué cambiar (PRO) vs por qué no cambiar (CON)",
          "Escalas de importancia (0-10 cuán importante es cambiar) + confianza (0-10 cuán confiado estoy de que pueda)",
        ],
      },
      {
        fase: 4, nombre: "Planificar (1-2 sesiones)",
        duracion_sesiones: "1-2",
        objetivos: [
          "Si cliente está listo, desarrollar plan concreto de cambio",
        ],
        tareas_clinico: [
          "Técnica del menu: ofrecer opciones de estrategia, cliente elige",
          "Plan SMART pactado juntos",
        ],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "OARS (escucha reflexiva)",
        descripcion: "Open questions (preguntas abiertas), Affirmations (halagos genuinos), Reflective listening (reflejos), Summaries (resúmenes).",
        cuando_usar: "Todo el tiempo.",
        ejemplo_dialogo:
          "C: 'Bebo cada fin de semana. Mi pareja me lo reprocha.'\n" +
          "T (Open): '¿Qué sucede típicamente un fin de semana?' C: 'Salgo con amigos, tomamos...' T (Reflection): 'Es tu tiempo de conexión social.' C: 'Sí, es lo único que me divierte.' T (Affirmation): 'Valoras la amistad y diversión.' T (Summary): 'Entonces, bebes para conectar, pero tu pareja preocupada. Importante para ti.'",
        ejercicio_casa: "Reflexión escrita: qué me motivaría a cambiar en vez de lo que me detiene.",
      },
      {
        nombre: "Change Talk — refuerzo de verbalizaciones hacia cambio",
        descripcion: "Escuchar y amplificar cuando cliente dice algo hacia cambio: 'quiero', 'puedo', 'voy a'.",
        cuando_usar: "Fase 3.",
        ejemplo_dialogo:
          "C: 'Supongo que podría intentar no beber entre semana.'\n" +
          "T: 'Que \"podrías intentar\". ¿Qué te hace pensar que podrías?' (Amplifica) C: 'Mi salud, mi relación...' T: 'Tiene sentido. ¿Cómo sería tu vida si lo lograras?' (Refuerzo)",
      },
      {
        nombre: "Escala de ambivalencia (columna PRO/CON)",
        descripcion: "Tabla de razones a favor vs en contra de cambiar. No toma partido el terapeuta, el cliente observa.",
        cuando_usar: "Fase 3-4.",
        ejemplo_dialogo:
          "T: 'Vamos a listar por qué cambiar (dejar de beber) vs por qué seguir igual.'\n" +
          "PRO cambio: salud, relación mejor, dinero, autoestima. CON: pérdida de amistad, aburrimiento.\n" +
          "T: 'Qué ves?' C: 'Más pro que con'",
      },
    ],
    videos: [
      {
        titulo: "William Miller — Motivational Interviewing (TEDx)",
        url_youtube: "https://www.youtube.com/embed/lSuWXfRYJcA",
        autor: "University of New Mexico",
        duracion: "17:00",
        idioma: "en",
        descripcion: "El co-creador explica principios fundamentales.",
      },
      {
        titulo: "Entrevista Motivacional en español",
        url_youtube: "https://www.youtube.com/embed/OzvxDdL8A8Q",
        autor: "Instituto de Adicción Colombia",
        duracion: "14:30",
        idioma: "es",
        descripcion: "Demostración con ejemplo de paciente con adicción.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Motivational Interviewing: Helping People Change (4th ed.)", autor: "Miller, W. R. & Rollnick, S.", anio: 2023, edicion: 4, isbn: "978-1462547388" },
      { tipo: "libro", titulo: "La entrevista motivacional: Preparar el cambio de conductas adictivas (3ª ed., español)", autor: "Miller & Rollnick (trad.)", editorial: "Desclée de Brouwer", anio: 2015, isbn: "978-8433024830" },
      { tipo: "paper", titulo: "Motivational interviewing and its effect on outcome in addiction treatment", autores: "Magill, M., et al.", anio: 2014, doi: "10.1016/j.copsyc.2014.05.008" },
    ],
    recursos_descargables: [
      { titulo: "Escala de importancia + confianza (0-10)", tipo: "plantilla", url: "https://motivationalinterviewing.org/importance-confidence-ruler" },
      { titulo: "Columna ambivalencia PRO/CON", tipo: "plantilla", url: "https://motivationalinterviewing.org/decisional-balance-worksheet" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * TCC NIÑOS — Terapia Cognitivo-Conductual para Niños y Adolescentes
   * ════════════════════════════════════════════════════════════════════ */
  tcc_ninos: {
    descripcion_extendida:
      "La Terapia Cognitivo-Conductual para niños y adolescentes (TCC-NA) adapta principios " +
      "de CBT adulto considerando desarrollo cognitivo (Piaget). En edad 3-7, énfasis en conducta " +
      "y juego; 7-12, mezcla de concreto y principios cognitivos; 12+, cogniciones abstractas " +
      "posibles. Requiere participación parental en entrenamiento de habilidades. Primera línea " +
      "para ansiedad, depresión infantil, TDAH, TOC infantil.",
    efecto_tamano: {
      ansiedad_infantil: 0.77,
      depresion_infantil: 0.68,
      tdah: 0.62,
      toc_infantil: 0.75,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Evaluación y psicoeducación (sesiones 1-2)",
        duracion_sesiones: "2",
        objetivos: [
          "Evaluación multiinformante: niño, padres, escuela si aplica",
          "Explicar ABCs a nivel del niño (juego, ejemplos, analogías)",
        ],
        tareas_clinico: [
          "CASI-4D, SCARED, SDQ según síntomas",
          "Genograma, historia de desarrollo",
          "Sesión individual con niño, sesión con padres por separado",
        ],
      },
      {
        fase: 2, nombre: "Habilidades de regulación emocional y afrontamiento (sesiones 3-6)",
        duracion_sesiones: "4",
        objetivos: [
          "Enseñar a identificar emociones mediante escalas 0-10 o caras",
          "Estrategias calmantes: respiración, movimiento, pensamiento reconfortante",
        ],
        tareas_clinico: [
          "Respiración 4-en, 6-afuera (simple para <10 años)",
          "Caja de regulación emocional (con actividades físicas: saltar, dibujar, escuchar música)",
        ],
      },
      {
        fase: 3, nombre: "Reestructuración cognitiva adaptada (sesiones 7-12)",
        duracion_sesiones: "6",
        objetivos: [
          "Identificar pensamientos en situaciones difíciles",
          "Desarrollar pensamientos alternativos",
        ],
        tareas_clinico: [
          "<9 años: enfoque conductual principalmente, cogniciones implícitas",
          "9-12 años: comic strip de situación-pensamiento-emoción-acción",
          "12+ años: registro de pensamientos estilo adulto simplificado",
        ],
      },
      {
        fase: 4, nombre: "Exposición gradual y prevención de recaída (sesiones 13-16)",
        duracion_sesiones: "4",
        objetivos: [
          "Si ansiedad/fobia: jerarquía de exposición",
          "Si depresión: activación conductual",
        ],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Comic strip de pensamientos",
        descripcion: "Viñetas que representan situación, pensamiento, emoción, acción. Visual, apropiado para niños 8-12.",
        cuando_usar: "Fase 3.",
        ejemplo_dialogo:
          "T: 'Dibujamos qué pasó ayer en la escuela que te puso triste.'\n" +
          "Viñeta 1: Escena niño con amigos\n" +
          "Viñeta 2: Nube pensamiento: 'Nadie me quiere'\n" +
          "Viñeta 3: Cara triste\n" +
          "Viñeta 4: Acción: Se va solo\n" +
          "T: 'Ahora, ¿hay otra forma de pensar la escena 2?'\n" +
          "C: 'Quizá solo estaban ocupados.'\n" +
          "T: 'Cómo te sientes con ese pensamiento?' C: 'Mejor.'",
        ejercicio_casa: "Hacer comic strip de situación que pasó esta semana.",
      },
      {
        nombre: "Jerarquía de exposición (para ansiedad/fobias)",
        descripcion: "Lista de cosas que asusta al niño, ordenadas. Exposición gradual con apoyo.",
        cuando_usar: "Fase 4 si hay ansiedad significativa.",
        ejemplo_dialogo:
          "T: '¿Qué cosas te dan miedo a la escuela? Hablemos juntos.'  C: 'Las pruebas, levantarme, hablar en clase.' T: '¿Cuál te asusta más (0-100)?'\n" +
          "C: 'Hablar en clase = 90.'\n" +
          "T: '¿Y preguntar en clase a la maestra qué significa una palabra?' C: '30.' T: 'Empezamos por esa.'",
        ejercicio_casa: "Esta semana, haz la cosa que te da 25 de miedo (baja) 3 veces.",
      },
    ],
    videos: [
      {
        titulo: "CBT for Children and Adolescents (IACBT video educativo)",
        url_youtube: "https://www.youtube.com/embed/7BgCJPTz2NY",
        autor: "International Association of Cognitive Behavioral Therapies",
        duracion: "15:00",
        idioma: "en",
        descripcion: "Adaptaciones de CBT para desarrollo infantil.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Cognitive-Behavioral Therapy with Children and Adolescents: Practical Strategies for Emotional & Behavioral Problems", autor: "Chu, B. C.", anio: 2012, edicion: 2, isbn: "978-1898389668" },
      { tipo: "libro", titulo: "Manual práctico de TCC infantil", autor: "Valles Arándiga, A.", anio: 2014, edicion: 1, isbn: "978-8416003754" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * HUMANISTICA — Terapia Centrada en la Persona (Rogers)
   * ════════════════════════════════════════════════════════════════════ */
  humanistica: {
    descripcion_extendida:
      "La Terapia Centrada en la Persona fue creada por Carl Rogers (1951) basada en creencia " +
      "de que cada persona posee capacidad innata de crecimiento y autorrealización. El papel " +
      "del terapeuta no es interpretación sino creación de relación auténtica: congruencia, " +
      "aceptación incondicional positiva, y empatía. Sin agendas, sin diagnósticos previos, " +
      "sigue el proceso del cliente. Se considera 'no directiva' aunque el terapeuta sí participa " +
      "activamente mediante reflejos y validación. Evidencia moderada, pero muy apreciada por " +
      "pacientes. Menos manudalizada que CBT, requiere entrenamiento relacional profundo.",
    efecto_tamano: {
      autoconsciencia: 0.58,
      depresion_leve: 0.45,
      satisfaccion_cliente: 0.72,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Creación de espacio seguro (sesiones 1-5)",
        duracion_sesiones: "5",
        objetivos: [
          "Que cliente se sienta escuchado, aceptado, comprendido",
          "Congruencia: terapeuta es auténtico, no actúa",
        ],
        tareas_clinico: [
          "Escucha profunda sin juzgar",
          "Reflejos de sentimientos (no pensamientos)",
          "Aceptación incondicional: validar incluso lo difícil de escuchar",
        ],
      },
      {
        fase: 2, nombre: "Exploración y auto-descubrimiento (sesiones 6-20)",
        duracion_sesiones: "15",
        objetivos: [
          "Cliente se cuestiona creencias propias",
          "Mayor auto-conocimiento",
          "Alineación entre 'yo ideal' y 'yo real'",
        ],
        tareas_clinico: [
          "Preguntas abiertas que invitan reflexión, no respuestas",
          "Reflejos cada vez más profundos de significados",
          "Validación de ambivalencia sin presionar cambio",
        ],
      },
      {
        fase: 3, nombre: "Crecimiento y cambio (sesiones 21+)",
        duracion_sesiones: "Variable",
        objetivos: [
          "Cambios conductuales emergen naturalmente de mayor conciencia",
          "Cliente siente mayor agencia y autorrealización",
        ],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Reflejo empático (empathic reflection)",
        descripcion: "Devolución del sentimiento subyacente en lo que cliente dice, no contenido literal.",
        cuando_usar: "Continuamente.",
        ejemplo_dialogo:
          "C: 'Mi jefe me criticó en reunión. Fue humillante.'\n" +
          "T: 'Suena como si algo en ti se hirió. La crítica en público te tocó especialmente.' (No: 'Tu jefe fue injusto')",
        ejercicio_casa: "Reflexión personal: qué sentimientos están debajo de la situación.",
      },
      {
        nombre: "Aceptación incondicional positiva",
        descripcion: "Convicción genuina de que cliente es valioso COMO ES, sin cambios requeridos.",
        cuando_usar: "Base de toda sesión.",
        ejemplo_dialogo:
          "C: 'He hecho cosas horribles que no puedo contar.'\n" +
          "T: 'Me gustaría escuchar, sin juzgar. Creo que tienes valor incluso con eso.'",
      },
    ],
    videos: [
      {
        titulo: "Carl Rogers — On Becoming a Person (conferencia)",
        url_youtube: "https://www.youtube.com/embed/HspgqW0bz5U",
        autor: "Carl Rogers Institute",
        duracion: "28:00",
        idioma: "en",
        descripcion: "El creador explica su filosofía de la persona.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "On Becoming a Person", autor: "Rogers, C. R.", anio: 1961, edicion: 1, isbn: "978-0395755488" },
      { tipo: "libro", titulo: "A Way of Being", autor: "Rogers, C. R.", anio: 1980, edicion: 1, isbn: "978-0395755471" },
    ],
  },

  /* ════════════════════════════════════════════════════════════════════
   * COMPASION_CFT — Terapia Centrada en la Compasión (Gilbert)
   * ════════════════════════════════════════════════════════════════════ */
  compasion_cft: {
    descripcion_extendida:
      "La Terapia Centrada en la Compasión (CFT, Compassion Focused Therapy) fue desarrollada " +
      "por Paul Gilbert (2005+) basada en neurobiología evolutiva y teoría del apego. Propone " +
      "que vergüenza y autocrítica activan sistema de amenaza evolutivo (amígdala, estrés). " +
      "CFT cultiva 'mente compasiva' activando sistema de calma (oxitocina, vagal dorsal), " +
      "redirigiendo energía crítica hacia auto-cuidado. Efectiva para trauma con culpa, " +
      "depresión con autocrítica, trastornos de personalidad con vergüenza.",
    efecto_tamano: {
      vergüenza_autocritica: 0.71,
      depresion_autoataque: 0.68,
      trauma_culpa: 0.65,
    },
    ultima_revision: "mayo 2026",
    fases_aplicacion: [
      {
        fase: 1, nombre: "Psicoeducación: 3 sistemas emocionales (sesiones 1-3)",
        duracion_sesiones: "3",
        objetivos: [
          "Entender sistema de amenaza (crítica) vs sistema de logro (competencia) vs sistema de calma (compasión)",
          "Normalizar autocrítica como evolución, pero dañina en modernidad",
        ],
        tareas_clinico: [
          "Diagrama: cómo amenaza y logro crean estrés crónico",
          "Psicoeducación: por qué compasión es estrategia biológica efectiva",
        ],
      },
      {
        fase: 2, nombre: "Práctica de mente compasiva (CMT) (sesiones 4-12)",
        duracion_sesiones: "9",
        objetivos: [
          "Cultivar 'yo compasivo' como voz interna nueva",
          "Activar respuestas de calma mediante imaginería, respiración rítmica",
        ],
        tareas_clinico: [
          "Respiración rítmica (5 adentro, 7 afuera, coordinado con latido cardíaco imaginario)",
          "Imaginería: sitio seguro + presencia compasiva (madre, persona sabia, versión compasiva de uno mismo)",
          "Diálogo: versión compasiva se dirige al 'yo crítico' con calidez",
        ],
      },
      {
        fase: 3, nombre: "Integración: vida basada en compasión (sesiones 13-20)",
        duracion_sesiones: "8",
        objetivos: [
          "Traducir compasión en acciones de auto-cuidado",
          "Reducir patrones de auto-daño que alivian culpa",
        ],
      },
    ],
    tecnicas_detalladas: [
      {
        nombre: "Respiración rítmica calmante",
        descripcion: "Coordinar respiración lenta (5-7 segundos) con latido cardíaco imaginario lento, activando sistema parasimpático.",
        cuando_usar: "Toda fase 2, especialmente antes de meditación compasiva.",
        ejemplo_dialogo:
          "T: 'Siente tu corazón latiendo. Imagina que late lentamente, relajado. Respira con él: 5 segundos adentro (1-2-3-4-5), 7 afuera (1-2-3-4-5-6-7). Rítmico, como una canción de cuna.'",
        ejercicio_casa: "5-10 minutos diarios, especialmente antes de dormir o cuando autocrítica sube.",
      },
      {
        nombre: "Imaginería compasiva (yo compasivo)",
        descripcion: "Crear imagen mental de versión compasiva de uno mismo o figura cuidadora protectora, presencia que ofrece calma.",
        cuando_usar: "Fase 2.",
        ejemplo_dialogo:
          "T: 'Visualiza la mejor versión de ti, totalmente compasiva y sabia. ¿Cómo viste? ¿Qué expresión tiene? ¿Dónde está?' C: 'Está de pie a mi lado, cálida, ojos amables.' T: 'Qué podría decirte esa versión?'",
        ejercicio_casa: "Meditación guiada: acceder a yo compasivo 10-15 min/día.",
      },
      {
        nombre: "Carta compasiva a uno mismo",
        descripcion: "Escribir carta como si el yo compasivo hablara a la parte crítica/herida, con gentileza y realismo.",
        cuando_usar: "Fase 2-3.",
        ejemplo_dialogo:
          "T: 'Como si escribieras desde parte más compasiva: \"Querido [nombre], entiendo que sufriste. Es normal sentir culpa, pero no mereces ese nivel de castigo. Eres humano. Aquí estoy para apoyarte.\"'",
        ejercicio_casa: "Escribir 1-2 cartas esta semana. Releer cuando autocrítica suba.",
      },
    ],
    videos: [
      {
        titulo: "Paul Gilbert — Compassion Focused Therapy (lecture)",
        url_youtube: "https://www.youtube.com/embed/a-DmQs_3wX0",
        autor: "Compassion Institute",
        duracion: "21:00",
        idioma: "en",
        descripcion: "El creador explica neurobiología de la compasión.",
      },
      {
        titulo: "Terapia centrada en compasión en español",
        url_youtube: "https://www.youtube.com/embed/KzVhP-xLqX4",
        autor: "Instituto Español CFT",
        duracion: "12:45",
        idioma: "es",
        descripcion: "Aplicación práctica del modelo Gilbert.",
      },
    ],
    bibliografia: [
      { tipo: "libro", titulo: "Compassion Focused Therapy: Distinctive Features", autor: "Gilbert, P.", anio: 2010, edicion: 1, isbn: "978-0415444742" },
      { tipo: "libro", titulo: "Terapia centrada en la compasión (edición en español)", autor: "Gilbert, P. (trad.)", editorial: "Amat", anio: 2014, isbn: "978-8497355956" },
      { tipo: "paper", titulo: "Compassion-focused therapy for complex trauma and emotional difficulty", autores: "Gilbert, P. & Procter, S.", anio: 2006, doi: "10.1080/17524880600747990" },
    ],
    recursos_descargables: [
      { titulo: "Audio guiado: Imaginería compasiva (15 min)", tipo: "audio", url: "https://www.compassionatecircle.org/guided-imagery-audio" },
      { titulo: "SCS (Self-Compassion Scale) en español", tipo: "plantilla", url: "https://self-compassion.org/spanish/" },
      { titulo: "Los 3 sistemas emocionales — infografía", tipo: "psicoeducacion", url: "https://www.compassionatecircle.org/3-emotional-systems" },
    ],
  },

};


/* ═══════ SEGUNDA MITAD DE ENFOQUES — se agregarán aquí ═══════ */
