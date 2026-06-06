/* ═══════════════════════════════════════════════════════════════════════
 * src/data/screening.js — Formularios de screening
 * ───────────────────────────────────────────────────────────────────────
 * Soporta dos tipos de instrumento:
 *
 *   • kind="binary_domains"  → ítems 0/1 agrupados en dominios (MMSE,
 *                              MoCA, ACE-III). Cutoff único.
 *
 *   • kind="likert_flat"     → ítems 0-3 (escala Likert), lista plana,
 *                              cutoffs por severidad (PHQ-9, GAD-7).
 *
 * Las versiones en español de PHQ-9 y GAD-7 son las traducciones
 * validadas y de dominio público publicadas por Spitzer, Kroenke et al.
 * y disponibles libremente en https://www.phqscreeners.com/.
 *
 * Validaciones colombianas: PHQ-9 — Cassiani-Miranda et al. 2017
 * (Acta Médica Colombiana); GAD-7 — Camargo et al. 2021.
 * ═══════════════════════════════════════════════════════════════════════ */

export const SCREENING_FORMS = {
  /* ─── Cognitivos (binarios por dominio) ─────────────────────── */
  MMSE: {
    name: "Mini-Mental State Examination",
    abbr: "MMSE",
    kind: "binary_domains",
    domain: "Cognitivo",
    maxScore: 30, cutoff: 24,
    ageRange: "Adulto / adulto mayor",
    domains: [
      { name: "Orientación Temporal", max: 5, items: ["¿Año?", "¿Estación?", "¿Día del mes?", "¿Día de la semana?", "¿Mes?"] },
      { name: "Orientación Espacial", max: 5, items: ["¿País?", "¿Departamento?", "¿Ciudad?", "¿Lugar?", "¿Piso?"] },
      { name: "Registro", max: 3, items: ["PELOTA", "BANDERA", "ÁRBOL"] },
      { name: "Atención y Cálculo", max: 5, items: ["100-7", "93-7", "86-7", "79-7", "72-7"] },
      { name: "Recuerdo", max: 3, items: ["Palabra 1", "Palabra 2", "Palabra 3"] },
      { name: "Lenguaje y Praxis", max: 9, items: [
        "Nombrar: reloj", "Nombrar: lápiz", "Repetir frase",
        "Orden 1: tome papel", "Orden 2: dóblelo", "Orden 3: póngalo en suelo",
        "Lea: CIERRE LOS OJOS", "Escriba una frase", "Copie pentágonos",
      ]},
    ],
  },
  MoCA: {
    name: "Montreal Cognitive Assessment",
    abbr: "MoCA",
    kind: "binary_domains",
    domain: "Cognitivo",
    maxScore: 30, cutoff: 26,
    ageRange: "Adulto / adulto mayor",
    normProfiles: {
      internacional: { cutoff: 26, label: "Estándar internacional (<26)" },
      colombia_primaria: { cutoff: 21, label: "Bogotá primaria (Pineros 2018)" },
      colombia_bachillerato: { cutoff: 23, label: "Bogotá bachillerato" },
      colombia_universitario: { cutoff: 24, label: "Bogotá universitarios" },
    },
    defaultNormProfile: "internacional",
    /* Cortes adicionales validados en Bogotá (Pedraza et al. 2014/2016):
     *   ≤20 → DCL  ·  ≤17 → demencia leve. Ajustar según escolaridad. */
    notes: "Validación Bogotá: ≤20 sugiere DCL; ≤17 sugiere demencia leve. Use perfil normativo por escolaridad.",
    domains: [
      { name: "Visuoespacial/Ejecutivo", max: 5, items: ["TMT-B adaptado", "Copia cubo", "Reloj: contorno", "Reloj: números", "Reloj: agujas"] },
      { name: "Identificación", max: 3, items: ["León", "Rinoceronte", "Camello"] },
      { name: "Atención", max: 6, items: [
        "Dígitos directos 2-1-8-5-4", "Dígitos inversos 7-4-2",
        "Concentración: golpe en A", "Resta 93", "Resta 86", "Resta 79",
      ]},
      { name: "Lenguaje", max: 3, items: ["Repetir frase 1", "Repetir frase 2", "Fluidez letra F ≥11"] },
      { name: "Abstracción", max: 2, items: ["Tren - Bicicleta", "Reloj - Regla"] },
      { name: "Recuerdo Diferido", max: 5, items: ["ROSTRO", "SEDA", "IGLESIA", "CLAVEL", "ROJO"] },
      { name: "Orientación", max: 6, items: ["Fecha", "Mes", "Año", "Día", "Lugar", "Ciudad"] },
    ],
  },
  ACE3: {
    name: "Addenbrooke's Cognitive Examination III",
    abbr: "ACE-III",
    kind: "binary_domains",
    domain: "Cognitivo",
    maxScore: 100, cutoff: 82,
    ageRange: "Adulto / adulto mayor",
    normProfiles: {
      internacional: { cutoff: 82, label: "Internacional ACE-III" },
      colombia: { cutoff: 87, label: "Colombia Ospina 2015 (ACE-R)" },
    },
    defaultNormProfile: "colombia",
    domains: [
      { name: "Atención", max: 18, items: [
        "Día", "Fecha", "Mes", "Año", "Estación",
        "Lugar", "Ciudad", "Repetir 3 palabras", "Resta 100-7 ×5", "MUNDO al revés",
      ]},
      { name: "Memoria", max: 26, items: [
        "Recuerdo 3 palabras", "Nombre-dirección aprendizaje ×3",
        "Figuras famosas ×4", "Nombre-dirección recuerdo", "Reconocimiento",
      ]},
      { name: "Fluencia", max: 14, items: ["Fluencia letra P", "Fluencia animales"] },
      { name: "Lenguaje", max: 26, items: [
        "Comprensión palabras", "Comprensión frases",
        "Repetición palabras", "Repetición frases",
        "Denominación ×12", "Lectura",
      ]},
      { name: "Visuoespacial", max: 16, items: ["Infinitos", "Cubo", "Reloj", "Contar puntos", "Letras fragmentadas"] },
    ],
  },

  /* ─── Emocionales (Likert, libres) ──────────────────────────── */
  PHQ9: {
    name: "Patient Health Questionnaire-9",
    abbr: "PHQ-9",
    kind: "likert_flat",
    domain: "Depresión",
    maxScore: 27,
    ageRange: "≥18 años",
    license: "Dominio público — Spitzer, Kroenke, Williams (1999). https://www.phqscreeners.com/",
    questionPrefix:
      "Durante las últimas 2 semanas, ¿con qué frecuencia le han molestado los siguientes problemas?",
    scaleLabels: [
      "Nunca",
      "Varios días",
      "Más de la mitad de los días",
      "Casi todos los días",
    ],
    items: [
      "Poco interés o placer en hacer las cosas.",
      "Se ha sentido decaído(a), deprimido(a) o sin esperanza.",
      "Dificultad para dormir, mantenerse dormido(a) o ha dormido demasiado.",
      "Se ha sentido cansado(a) o con poca energía.",
      "Falta de apetito o ha comido en exceso.",
      "Se ha sentido mal con usted mismo(a), ha sentido que es un fracaso o que ha decepcionado a su familia.",
      "Dificultad para concentrarse en cosas como leer el periódico o ver televisión.",
      "Se ha movido o hablado tan lento que otras personas lo notan, o lo contrario: ha estado tan inquieto(a) que se ha movido más de lo usual.",
      "Pensamientos de que estaría mejor muerto(a) o de hacerse daño de alguna manera.",
    ],
    /* Cutoffs Kroenke et al. 2001 / Spanish validation
     * Cassiani-Miranda et al. 2017. */
    severity: [
      { max: 4,  label: "Mínima",            color: "#10b981" },
      { max: 9,  label: "Leve",              color: "#84cc16" },
      { max: 14, label: "Moderada",          color: "#f59e0b" },
      { max: 19, label: "Moderada-severa",   color: "#ea580c" },
      { max: 27, label: "Severa",            color: "#dc2626" },
    ],
    clinicalCutoff: 10,
    clinicalCutoffs: { ap_colombia: 7, clinica: 10 },
    defaultClinicalContext: "ap_colombia",
    /* Ítem 9 = ideación suicida; cualquier respuesta ≥1 amerita
     * exploración inmediata por el clínico. */
    redFlagItems: [8],
    redFlagMessage:
      "Ítem 9 (ideación suicida) con respuesta positiva. Indagar en la consulta y considerar protocolo de riesgo.",
  },
  GAD7: {
    name: "Generalized Anxiety Disorder Scale-7",
    abbr: "GAD-7",
    kind: "likert_flat",
    domain: "Ansiedad",
    maxScore: 21,
    ageRange: "≥18 años",
    license: "Dominio público — Spitzer, Kroenke, Williams (2006). https://www.phqscreeners.com/",
    questionPrefix:
      "Durante las últimas 2 semanas, ¿con qué frecuencia le han molestado los siguientes problemas?",
    scaleLabels: [
      "Nunca",
      "Varios días",
      "Más de la mitad de los días",
      "Casi todos los días",
    ],
    items: [
      "Se ha sentido nervioso(a), ansioso(a) o muy alterado(a).",
      "No ha podido parar o controlar la preocupación.",
      "Se ha preocupado demasiado por diferentes cosas.",
      "Ha tenido dificultad para relajarse.",
      "Se ha sentido tan inquieto(a) que le ha sido difícil estarse quieto(a).",
      "Se ha molestado o irritado fácilmente.",
      "Ha sentido miedo como si algo terrible pudiera pasar.",
    ],
    severity: [
      { max: 4,  label: "Mínima",   color: "#10b981" },
      { max: 9,  label: "Leve",     color: "#84cc16" },
      { max: 14, label: "Moderada", color: "#f59e0b" },
      { max: 21, label: "Severa",   color: "#dc2626" },
    ],
    clinicalCutoff: 10, // ≥10 → considerar derivación
  },

  /* ─── SNAP-IV: TDAH y conducta oposicionista (niños 6-18) ─── */
  SNAPIV: {
    name: "SNAP-IV (versión corta) — Padres / maestros",
    abbr: "SNAP-IV",
    kind: "likert_flat",
    domain: "TDAH / oposicionista",
    maxScore: 54, // 18 ítems × 3
    ageRange: "6-18 años",
    license: "Dominio público — Swanson, Nolan, Pelham (1980, 2003). Sin restricción de uso clínico.",
    questionPrefix:
      "Para cada ítem, marque qué tan presente está la conducta en el niño/adolescente:",
    scaleLabels: [
      "Nada",
      "Un poco",
      "Bastante",
      "Mucho",
    ],
    items: [
      /* Inatención (1-9) */
      "No presta atención suficiente a los detalles o comete errores por descuido en sus tareas.",
      "Tiene dificultad para mantener la atención en tareas o juegos.",
      "No parece escuchar cuando se le habla directamente.",
      "No sigue las instrucciones y no termina las tareas escolares u obligaciones (no por desafío).",
      "Tiene dificultad para organizar tareas y actividades.",
      "Evita o le disgustan las tareas que requieren esfuerzo mental sostenido.",
      "Pierde objetos necesarios para tareas o actividades (lápices, libros, herramientas).",
      "Se distrae fácilmente con estímulos externos.",
      "Es descuidado/olvidadizo en las actividades diarias.",
      /* Hiperactividad-Impulsividad (10-18) */
      "Mueve manos o pies en exceso o se retuerce en el asiento.",
      "Abandona el asiento en clase u otras situaciones donde se espera que permanezca sentado.",
      "Corre o trepa en exceso en situaciones donde es inadecuado.",
      "Le cuesta jugar o dedicarse tranquilamente a actividades de ocio.",
      "Está \"en marcha\" o actúa como si \"tuviera un motor\".",
      "Habla en exceso.",
      "Responde precipitadamente antes de que se haya completado la pregunta.",
      "Tiene dificultad para esperar su turno.",
      "Interrumpe o se entromete con otros.",
    ],
    /* Cortes orientativos: ≥1.78 promedio inatención o hiperactividad
     * (es decir, sumando los 9 ítems → ≥16) sugiere screening positivo.
     * Aquí se usa el sum total con cutoff 16 por subescala como guía. */
    severity: [
      { max: 17,  label: "Negativo",      color: "#10b981" },
      { max: 32,  label: "Inatención significativa o hiperactividad significativa", color: "#f59e0b" },
      { max: 54,  label: "Riesgo TDAH alto",   color: "#dc2626" },
    ],
    clinicalCutoff: 16, // suma ≥16 en cualquier subescala
    notes: "Promedios ≥1.78 en inatención o hiperactividad (suma ≥16 en su subescala) sugieren screening positivo. La SNAP-IV no diagnostica; complemente con Vanderbilt, Conners o entrevista DSM-5.",
  },

  /* ─── SCARED-C: ansiedad infantil (8-18 años) — versión corta 5 ítems ─── */
  SCARED5: {
    name: "SCARED-5 — Screening corto de ansiedad infantil",
    abbr: "SCARED-5",
    kind: "likert_flat",
    domain: "Ansiedad infantil",
    maxScore: 10, // 5 ítems × 2
    ageRange: "8-18 años",
    license: "Dominio público — Birmaher et al. 1999, versión corta validada. Use libre clínico/académico.",
    questionPrefix:
      "Cuando le pasa algo o piensa en algo, ¿con qué frecuencia se siente así?",
    scaleLabels: [
      "Casi nunca",
      "A veces",
      "Muchas veces",
    ],
    items: [
      "Me siento muy preocupado(a).",
      "Tengo miedo cuando estoy lejos de mis padres.",
      "Cuando estoy en grupo me da miedo o vergüenza.",
      "Me cuesta dormirme o me despierto en la noche con miedo.",
      "Tengo dolores de estómago o de cabeza cuando estoy preocupado(a).",
    ],
    severity: [
      { max: 2,  label: "Negativo",         color: "#10b981" },
      { max: 4,  label: "Leve",             color: "#84cc16" },
      { max: 7,  label: "Moderado",         color: "#f59e0b" },
      { max: 10, label: "Riesgo elevado",   color: "#dc2626" },
    ],
    clinicalCutoff: 3, // ≥3 sugiere aplicar SCARED-41 completo
  },

  /* ─── Zarit Burden Interview (corta 7 ítems) — sobrecarga del cuidador ─── */
  ZARIT7: {
    name: "Zarit Burden Interview — Versión corta 7 ítems",
    abbr: "Zarit-7",
    kind: "likert_flat",
    domain: "Sobrecarga del cuidador",
    maxScore: 28, // 7 × 4
    ageRange: "Cuidador principal (≥18)",
    license: "Dominio público — Bédard et al. 2001 (versión corta). Validación española González-Salvador 1999.",
    questionPrefix:
      "Como cuidador, ¿con qué frecuencia se ha sentido así?:",
    scaleLabels: [
      "Nunca",
      "Rara vez",
      "Algunas veces",
      "Bastantes veces",
      "Casi siempre",
    ],
    items: [
      "Cree que su familiar le pide más ayuda de la que realmente necesita.",
      "Cree que, debido al tiempo que dedica a su familiar, no tiene suficiente tiempo para usted.",
      "Se siente agobiado(a) por intentar compatibilizar el cuidado con sus responsabilidades laborales/familiares.",
      "Piensa que el comportamiento de su familiar le hace sentirse incómodo(a).",
      "Se siente enfadado(a) cuando está cerca de su familiar.",
      "Cree que su familiar le afecta negativamente las relaciones con otros familiares o amigos.",
      "Se siente incapaz de cuidar a su familiar mucho tiempo más.",
    ],
    severity: [
      { max: 7,  label: "No sobrecarga",        color: "#10b981" },
      { max: 16, label: "Sobrecarga leve",      color: "#f59e0b" },
      { max: 28, label: "Sobrecarga intensa",   color: "#dc2626" },
    ],
    clinicalCutoff: 17,
    notes: "Sobrecarga intensa (≥17) requiere intervención: psicoeducación al cuidador, redes de apoyo, descarga periódica.",
  },

  /* ─── BAI — Inventario de Ansiedad de Beck (Beck Anxiety Inventory) ─── */
  BAI: {
    name: "Beck Anxiety Inventory",
    abbr: "BAI",
    kind: "likert_flat",
    domain: "Ansiedad",
    maxScore: 63,
    ageRange: "≥18 años",
    license: "Propiedad de Beck Institute / Pearson. Requiere licencia de uso clínico. Incluido para referencia estructural.",
    questionPrefix:
      "Indique en qué medida le ha molestado cada síntoma durante la última semana:",
    scaleLabels: ["Nada en absoluto", "Levemente", "Moderadamente", "Severamente"],
    items: [
      "Entumecimiento u hormigueo.",
      "Sensación de calor.",
      "Temblor de piernas.",
      "Incapacidad para relajarse.",
      "Miedo a que ocurra lo peor.",
      "Mareos.",
      "Palpitaciones o aceleración del corazón.",
      "Sensación de inestabilidad.",
      "Terror.",
      "Nerviosismo.",
      "Sensación de ahogo.",
      "Temblor de manos.",
      "Temblor generalizado.",
      "Miedo a perder el control.",
      "Dificultad para respirar.",
      "Miedo a morir.",
      "Asustadizo.",
      "Indigestión o molestia abdominal.",
      "Desmayos.",
      "Rubor.",
      "Sudoración (no por calor).",
    ],
    severity: [
      { max: 7,  label: "Ansiedad mínima",     color: "#10b981" },
      { max: 15, label: "Ansiedad leve",        color: "#84cc16" },
      { max: 25, label: "Ansiedad moderada",    color: "#f59e0b" },
      { max: 63, label: "Ansiedad severa",      color: "#dc2626" },
    ],
    clinicalCutoff: 16,
    notes: "Beck, Epstein, Brown & Steer (1988). Puntuaciones ≥16 requieren evaluación especializada.",
  },

  /* ─── HADS — Hospital Anxiety and Depression Scale ─────────────────── */
  HADS: {
    name: "Hospital Anxiety and Depression Scale",
    abbr: "HADS",
    kind: "likert_flat",
    domain: "Ansiedad / Depresión",
    maxScore: 42, // 14 ítems × 3
    ageRange: "≥18 años",
    license: "Zigmond & Snaith 1983. Propiedad de NFER-Nelson/GL Assessment. Requiere licencia para uso clínico masivo.",
    questionPrefix:
      "Para cada ítem, marque cómo se ha sentido durante la última semana:",
    scaleLabels: ["Nunca / Nada", "Ocasionalmente / Algo", "A menudo / Bastante", "Casi siempre / Mucho"],
    items: [
      /* A = Ansiedad (ítems impares: 1,3,5,7,9,11,13) */
      "Me siento tenso(a) o nervioso(a). [A]",
      "Sigo disfrutando de las mismas cosas que antes. [D]",
      "Siento una especie de temor como si algo malo fuera a suceder. [A]",
      "Puedo reírme y ver el lado gracioso de las cosas. [D]",
      "Tengo la cabeza llena de preocupaciones. [A]",
      "Me siento alegre. [D]",
      "Puedo estar sentado(a) tranquilamente y sentirme relajado(a). [A]",
      "Me siento como si cada día estuviera más lento(a). [D]",
      "Tengo una sensación extraña, como de tener mariposas en el estómago. [A]",
      "He perdido el interés por mi aspecto personal. [D]",
      "Me siento inquieto(a) como si no pudiera parar de moverme. [A]",
      "Espero las cosas con ilusión. [D]",
      "De repente siento sensaciones de pánico. [A]",
      "Soy capaz de disfrutar con un buen libro o programa de radio/televisión. [D]",
    ],
    severity: [
      { max: 13, label: "Normal (ansiedad/depresión no probable)", color: "#10b981" },
      { max: 21, label: "Caso dudoso / borderline", color: "#f59e0b" },
      { max: 42, label: "Caso probable de ansiedad/depresión", color: "#dc2626" },
    ],
    clinicalCutoff: 15,
    notes: "Ítems [A]=Ansiedad, [D]=Depresión. Corte por subescala ≥8 sugiere caso probable. HADS-A suma ítems 1,3,5,7,9,11,13; HADS-D suma 2,4,6,8,10,12,14.",
  },

  /* ─── NPI-Q — Neuropsychiatric Inventory Questionnaire ─────────────── */
  /* §dedupe-fix (2026-05-18): esta entrada `NPIQ` (versión likert_flat)
   * estaba duplicada con otra definición más abajo (binary_domains, cuidador).
   * JavaScript usaba la segunda — esta era dead code y rompía el linter.
   * Renombrada a NPIQ_FLAT para preservar las dos variantes si en el futuro
   * se quiere ofrecer ambas modalidades de aplicación. */
  NPIQ_FLAT: {
    name: "Neuropsychiatric Inventory Questionnaire",
    abbr: "NPI-Q",
    kind: "likert_flat",
    domain: "Síntomas neuropsiquiátricos",
    maxScore: 36, // 12 dominios × 3
    ageRange: "Adulto mayor / demencia",
    license: "Kaufer et al. 2000. Dominio público para uso clínico. Citar: Kaufer DI et al., J Neuropsychiatry Clin Neurosci 2000.",
    questionPrefix:
      "En el último mes, ¿ha presentado el paciente estos síntomas? (0=No; 1=Leve, 2=Moderado, 3=Severo si está presente):",
    scaleLabels: ["Ausente", "Leve", "Moderado", "Severo"],
    items: [
      "Delirios — creencias falsas (creer que roban, que la pareja engaña, etc.).",
      "Alucinaciones — ve u oye cosas que no existen.",
      "Agitación / agresividad — conducta disruptiva, resistencia al cuidado.",
      "Depresión / disforia — tristeza, llanto, desesperanza.",
      "Ansiedad — nerviosismo, tensión sin causa aparente.",
      "Euforia / exaltación — alegría exagerada, risas inapropiadas.",
      "Apatía / indiferencia — pérdida de interés y motivación.",
      "Desinhibición — comportamientos impulsivos o socialmente inadecuados.",
      "Irritabilidad / labilidad emocional — cambios de humor, frustración fácil.",
      "Conducta motora aberrante — repetición de movimientos sin fin.",
      "Trastornos del sueño — alteraciones del ciclo sueño-vigilia.",
      "Apetito y alimentación — cambios en apetito o conducta alimentaria.",
    ],
    severity: [
      { max: 5,  label: "Mínimo / sin impacto",    color: "#10b981" },
      { max: 11, label: "Leve — monitorear",        color: "#84cc16" },
      { max: 20, label: "Moderado — intervención",  color: "#f59e0b" },
      { max: 36, label: "Severo — urgente",         color: "#dc2626" },
    ],
    clinicalCutoff: 12,
    notes: "Aplicar al cuidador/familiar. Una puntuación ≥12 suele indicar impacto significativo y requiere manejo farmacológico/no-farmacológico.",
  },

  /* ─── Barthel — Índice de Barthel (actividades básicas de vida diaria) ─ */
  BARTHEL: {
    name: "Índice de Barthel — Actividades Básicas de la Vida Diaria",
    abbr: "Barthel",
    kind: "binary_domains",
    domain: "Funcionalidad básica",
    maxScore: 100,
    cutoff: 60,
    ageRange: "Adulto mayor / cualquier edad con discapacidad",
    license: "Mahoney & Barthel 1965. Dominio público. Citar: Mahoney FI, Barthel DW. Funct Evaluation 1965.",
    domains: [
      { name: "Comer", max: 10, items: ["Independiente (10)", "Necesita ayuda (5)", "Dependiente (0)"] },
      { name: "Trasladarse silla/cama", max: 15, items: ["Independiente (15)", "Mínima ayuda (10)", "Gran ayuda (5)", "Dependiente (0)"] },
      { name: "Aseo personal", max: 5, items: ["Independiente (5)", "Dependiente (0)"] },
      { name: "Uso del WC", max: 10, items: ["Independiente (10)", "Necesita ayuda (5)", "Dependiente (0)"] },
      { name: "Bañarse/ducharse", max: 5, items: ["Independiente (5)", "Dependiente (0)"] },
      { name: "Desplazamiento", max: 15, items: ["Independiente ≥50m (15)", "Con ayuda ≥50m (10)", "Silla de ruedas (5)", "Dependiente (0)"] },
      { name: "Subir y bajar escaleras", max: 10, items: ["Independiente (10)", "Necesita ayuda (5)", "Dependiente (0)"] },
      { name: "Vestirse y desvestirse", max: 10, items: ["Independiente (10)", "Necesita ayuda (5)", "Dependiente (0)"] },
      { name: "Control de esfínter anal", max: 10, items: ["Continente (10)", "Accidente ocasional (5)", "Incontinente (0)"] },
      { name: "Control de esfínter vesical", max: 10, items: ["Continente (10)", "Accidente ocasional (5)", "Incontinente (0)"] },
    ],
    severityTable: [
      { min: 91, max: 100, label: "Independiente",         color: "#10b981" },
      { min: 61, max: 90,  label: "Dependencia leve",      color: "#84cc16" },
      { min: 41, max: 60,  label: "Dependencia moderada",  color: "#f59e0b" },
      { min: 21, max: 40,  label: "Dependencia severa",    color: "#ea580c" },
      { min: 0,  max: 20,  label: "Dependencia total",     color: "#dc2626" },
    ],
    notes: "Puntuación máxima: 100 (independencia total). <60: requiere ayuda significativa. Registrar el puntaje real en el campo PD; el sistema lo mapea a categoría funcional.",
  },

  /* ─── FAQ — Functional Activities Questionnaire (Pfeffer) ──────────── */
  FAQ: {
    name: "Functional Activities Questionnaire (Pfeffer)",
    abbr: "FAQ",
    kind: "likert_flat",
    domain: "Funcionalidad instrumental",
    maxScore: 30, // 10 ítems × 3
    ageRange: "Adulto mayor ≥60",
    license: "Pfeffer et al. 1982. Dominio público para uso clínico/investigación. Citar: Pfeffer RI et al., J Gerontol 1982.",
    questionPrefix:
      "¿Cómo califica la capacidad del paciente en cada actividad instrumental? (0=Normal, 1=Con dificultad/ayuda, 2=Otro lo hace, 3=No hace/incapaz):",
    scaleLabels: [
      "Normal / nunca lo hizo pero podría",
      "Con dificultad / necesita ayuda",
      "Depende de otro para hacerlo",
      "No puede / incapaz",
    ],
    items: [
      "Llenar cheques, pagar facturas, llevar cuentas bancarias.",
      "Llenar formularios u organizar documentos importantes.",
      "Hacer compras solo(a) (ropa, comida, artículos del hogar).",
      "Jugar juegos de habilidad (ajedrez, naipes, solitario).",
      "Calentar agua, hacer café — apagar la estufa.",
      "Preparar una comida balanceada.",
      "Estar al tanto de noticias actuales (periódico, radio, TV).",
      "Prestar atención, entender y comentar sobre un programa de TV, libro, revista.",
      "Recordar citas, eventos familiares, ocasiones especiales.",
      "Manejar sus propios medicamentos (dosis, horarios).",
    ],
    severity: [
      { max: 5,  label: "Normal / sin alteración funcional", color: "#10b981" },
      { max: 8,  label: "Deterioro leve (posible DCL)",      color: "#84cc16" },
      { max: 14, label: "Deterioro moderado",                color: "#f59e0b" },
      { max: 30, label: "Deterioro severo",                  color: "#dc2626" },
    ],
    clinicalCutoff: 9,
    notes: "FAQ ≥9 sugiere deterioro funcional instrumentalmente relevante; apoya diagnóstico de demencia leve. Validación americana Pfeffer 1982; cortes revisados NIA-AA 2011.",
  },

  /* ─── VANDERBILT — NICHQ Vanderbilt Assessment Scale (TDAH escolar) ── */
  VANDERBILT: {
    name: "NICHQ Vanderbilt Assessment Scale — Versión para padres",
    abbr: "Vanderbilt",
    kind: "likert_flat",
    domain: "TDAH escolar",
    maxScore: 54, // 18 ítems DSM × 3 (sin ítems de conducta ni rendimiento)
    ageRange: "6-12 años",
    license: "NICHQ / American Academy of Pediatrics. Dominio público para uso clínico. https://www.nichq.org/",
    questionPrefix:
      "En los últimos 6 meses, ¿con qué frecuencia ha tenido el niño/niña estos comportamientos?",
    scaleLabels: ["Nunca", "Ocasionalmente", "A menudo", "Siempre"],
    items: [
      /* Inatención (1-9) */
      "No le presta atención a los detalles o comete errores por descuido en el trabajo escolar.",
      "Tiene problemas para mantenerse atento en tareas o actividades lúdicas.",
      "No parece escuchar cuando se le habla directamente.",
      "No sigue las instrucciones y no termina las tareas escolares u otras obligaciones.",
      "Tiene dificultades para organizar tareas y actividades.",
      "Evita, le disgusta o es reacio a comprometerse en tareas que requieren esfuerzo mental sostenido.",
      "Pierde cosas necesarias para las tareas o actividades.",
      "Se distrae fácilmente con estímulos externos.",
      "Es olvidadizo en las actividades diarias.",
      /* Hiperactividad-Impulsividad (10-18) */
      "Mueve en exceso las manos o los pies, o se retuerce en el asiento.",
      "Se levanta de su asiento en el salón de clases cuando se espera que permanezca sentado.",
      "Corre o trepa en situaciones en las que no es apropiado.",
      "Tiene dificultad para jugar o involucrarse en actividades de ocio tranquilamente.",
      "Está 'en marcha' o actúa como si 'tuviera un motor'.",
      "Habla demasiado.",
      "Da las respuestas antes de que se hayan terminado de hacer las preguntas.",
      "Tiene problemas esperando su turno.",
      "Interrumpe o se entromete con los demás.",
    ],
    severity: [
      { max: 13, label: "Negativo / sin indicadores", color: "#10b981" },
      { max: 26, label: "Indicadores leves",          color: "#f59e0b" },
      { max: 54, label: "Riesgo TDAH — derivar",      color: "#dc2626" },
    ],
    clinicalCutoff: 14,
    notes: "Suma ≥14 en inatención (ítems 1-9) o hiperactividad (10-18) sugiere screening positivo. Complementar con versión maestros y Conners-3 o EDAH para diagnóstico definitivo.",
  },

  /* ─── M-CHAT-R/F — Modified Checklist for Autism in Toddlers ─────── */
  MCHAT: {
    name: "M-CHAT-R/F — Modified Checklist for Autism in Toddlers",
    abbr: "M-CHAT-R/F",
    kind: "binary_domains",
    domain: "TEA (screening temprano)",
    maxScore: 20,
    cutoff: 3, // ≥3 falla: seguimiento; ≥8 falla: derivación inmediata
    ageRange: "16-30 meses",
    license: "Robins, Fein & Barton 1999/2009. Libre para uso clínico e investigación. https://mchatscreen.com/",
    domains: [
      { name: "Ítems críticos (alto valor predictivo)", max: 6, items: [
        "¿Su hijo(a) señala con el dedo para pedir algo?",
        "¿Su hijo(a) mira hacia donde usted señala?",
        "¿Alguna vez su hijo(a) juega a hacer como si fuera otra persona (juego simbólico)?",
        "¿Le señala su hijo(a) cosas que le parecen interesantes?",
        "¿Le trae su hijo(a) objetos para mostrarle algo?",
        "¿Mantiene contacto visual durante 1-2 segundos?",
      ]},
      { name: "Ítems adicionales", max: 14, items: [
        "¿Le gusta que le balanceen o le hagan caballito?",
        "¿Su hijo(a) se interesa por otros niños?",
        "¿A su hijo(a) le gusta trepar (escaleras, muebles)?",
        "¿Su hijo(a) disfruta esconderse y ser buscado?",
        "¿Responde cuando se le llama por su nombre?",
        "¿Imita acciones que usted hace?",
        "¿Responde cuando usted le sonríe?",
        "¿Camina sin apoyarse a los 18 meses (o caminó)?",
        "¿Su hijo(a) mira cosas que usted está mirando?",
        "¿Su hijo(a) tiene movimientos peculiares con los dedos?",
        "¿Intenta que usted lo(a) mire?",
        "¿Comprende lo que se le dice?",
        "¿Se queda mirando fijamente el vacío o camina sin propósito?",
        "¿Mira su propio rostro en el espejo?",
      ]},
    ],
    notes: "Fallo en ≥3 ítems (o ≥2 ítems críticos): derivar a entrevista de seguimiento M-CHAT-R/F. Fallo ≥8: derivación inmediata a especialista TEA. Ítems críticos fallar 1 sólo requiere seguimiento.",
  },

  /* ─── CDR-SoB simplificado (Clinical Dementia Rating — Sum of Boxes) ─
   * Versión adaptada a la estructura likert_flat (valores enteros 0-3).
   * El CDR original usa 0/0.5/1/2/3 por dominio; aquí se omite 0.5 para
   * compatibilidad con el componente — para precisión legal usar tabla
   * Morris (1993) original. */
  CDR: {
    name: "Clinical Dementia Rating — Sum of Boxes (simplificado)",
    abbr: "CDR-SoB",
    kind: "likert_flat",
    domain: "Severidad demencia",
    maxScore: 18, // 6 dominios × 3
    ageRange: "Adulto mayor",
    license: "Hughes/Berg/Morris 1982, 1993 — uso clínico libre. Citar Washington University CDR.",
    questionPrefix:
      "Estado funcional del paciente en cada dominio (0=Sin alteración, 3=Severo):",
    scaleLabels: ["Sin alteración", "Leve", "Moderado", "Severo"],
    items: [
      "Memoria — pérdida en vida diaria.",
      "Orientación — temporal/espacial.",
      "Juicio y resolución de problemas.",
      "Asuntos comunitarios — independencia fuera del hogar.",
      "Hogar y aficiones — funcionamiento en casa.",
      "Cuidado personal — vestido, aseo, alimentación.",
    ],
    severity: [
      { max: 0,  label: "Normal",                color: "#10b981" },
      { max: 4,  label: "Muy leve / cuestionable", color: "#84cc16" },
      { max: 9,  label: "Demencia leve",         color: "#f59e0b" },
      { max: 15, label: "Demencia moderada",     color: "#ea580c" },
      { max: 18, label: "Demencia severa",       color: "#dc2626" },
    ],
    clinicalCutoff: 5, // CDR-SoB ≥5 sugiere demencia clínica
    notes: "CDR original usa también valor 0.5 por dominio. Para el cálculo CDR-Global y para informes legales se debe consultar el algoritmo Morris (1993) en Washington University CDR.",
  },

  /* ─── GDS-15: Escala de Depresión Geriátrica (Yesavage) ─────────────
   * Sheikh & Yesavage 1986. Versión corta de 15 ítems, dominio público.
   * Respuesta: Sí/No. Items en MAYÚSCULA indican respuesta patológica=1.
   * Validada en Colombia por Morales et al. (2014). */
  GDS15: {
    name: "Escala de Depresión Geriátrica — GDS-15 (Yesavage corta)",
    abbr: "GDS-15",
    kind: "binary_domains",
    domain: "Depresión",
    maxScore: 15, cutoff: 5,
    ageRange: "Adulto mayor (≥60 años)",
    license: "Sheikh & Yesavage 1986. Dominio público. Validación Colombia: Morales et al. 2014.",
    domains: [
      {
        name: "Síntomas depresivos geriátricos",
        max: 15,
        items: [
          "¿Está básicamente satisfecho/a con su vida? (NO=1)",
          "¿Ha abandonado muchas de sus actividades e intereses? (SÍ=1)",
          "¿Siente que su vida está vacía? (SÍ=1)",
          "¿Se aburre con frecuencia? (SÍ=1)",
          "¿Está de buen humor la mayor parte del tiempo? (NO=1)",
          "¿Teme que le va a pasar algo malo? (SÍ=1)",
          "¿Se siente feliz la mayor parte del tiempo? (NO=1)",
          "¿Se siente a menudo abandonado/a? (SÍ=1)",
          "¿Prefiere quedarse en casa a salir y hacer cosas nuevas? (SÍ=1)",
          "¿Cree que tiene más problemas de memoria que la mayoría? (SÍ=1)",
          "¿Cree que es maravilloso estar vivo/a ahora? (NO=1)",
          "¿Se siente bastante inútil tal y como está ahora? (SÍ=1)",
          "¿Se siente lleno/a de energía? (NO=1)",
          "¿Siente que su situación es desesperanzadora? (SÍ=1)",
          "¿Cree que la mayoría de la gente está mejor que usted? (SÍ=1)",
        ],
      },
    ],
    severity: [
      { max: 4,  label: "Sin depresión",    color: "#10b981" },
      { max: 9,  label: "Depresión leve",   color: "#f59e0b" },
      { max: 15, label: "Depresión severa", color: "#dc2626" },
    ],
    notes: "Corte ≥5: posible depresión; corte ≥10: probable depresión severa. Integrar con historia clínica y criterios DSM-5. IMPORTANTE: Yesavage ≥5 es criterio de exclusión para diagnóstico de DCL (considerar tratar depresión primero y reevaluar cognición a los 3 meses).",
  },

  /* ─── STAI: Inventario de Ansiedad Estado-Rasgo ──────────────────────
   * Spielberger, Gorsuch & Lushene (1970). Adaptación española: TEA Ediciones.
   * 40 ítems: 20 Estado (cómo se siente AHORA) + 20 Rasgo (cómo se siente GENERALMENTE).
   * Escala: 1-4. Algunos ítems son inversos (marcados con *). */
  STAI: {
    name: "Inventario de Ansiedad Estado-Rasgo (STAI)",
    abbr: "STAI",
    kind: "likert_flat",
    domain: "Ansiedad",
    maxScore: 120, /* 40 ítems × max 3 en escala 0-3 */
    ageRange: "≥16 años",
    license: "Spielberger et al. 1970. Adaptación española TEA Ediciones. Uso con licencia en contexto clínico.",
    questionPrefix: "Seleccione cómo se siente (Estado: ahora mismo · Rasgo: en general):",
    scaleLabels: ["Nada", "Algo", "Bastante", "Mucho"],
    reverseItems: [0, 1, 4, 7, 9, 10, 14, 15, 18, 19, 20, 25, 26, 29, 32, 35, 38],
    items: [
      /* ESTADO (ítems 1-20) — "¿Cómo se siente ahora mismo?" */
      "Me siento calmado/a *",
      "Me siento seguro/a *",
      "Estoy tenso/a",
      "Estoy contrariado/a",
      "Me siento cómodo/a *",
      "Me siento alterado/a",
      "Estoy preocupado/a actualmente por posibles desgracias",
      "Me siento descansado/a *",
      "Me siento angustiado/a",
      "Me siento confortable *",
      "Tengo confianza en mí mismo/a *",
      "Me siento nervioso/a",
      "Estoy agitado/a",
      "Me siento muy atado/a (como oprimido/a)",
      "Estoy relajado/a *",
      "Me siento satisfecho/a *",
      "Estoy preocupado/a",
      "Me siento muy agitado/a y aturdido/a",
      "Me siento alegre *",
      "En este momento me siento bien *",
      /* RASGO (ítems 21-40) — "¿Cómo se siente GENERALMENTE?" */
      "Me siento bien *",
      "Me canso rápidamente",
      "Siento ganas de llorar",
      "Quisiera ser tan feliz como otros",
      "Pierdo oportunidades por no poder decidirme rápidamente",
      "Me siento descansado/a *",
      "Soy una persona tranquila, serena y sosegada *",
      "Veo que las dificultades se amontonan y no puedo superarlas",
      "Me preocupo demasiado por cosas sin importancia",
      "Soy feliz *",
      "Suelo tomar las cosas demasiado seriamente",
      "Me falta confianza en mí mismo/a",
      "Me siento seguro/a *",
      "Trato de evitar enfrentarme a los problemas y dificultades",
      "Me siento melancólico/a",
      "Estoy satisfecho/a *",
      "Me rondan pensamientos sin importancia que me molestan",
      "Me afectan tanto los desengaños que no me puedo olvidar de ellos",
      "Soy una persona estable *",
      "Cuando pienso en los asuntos que tengo entre manos me pongo tenso/a y agitado/a",
    ],
    severity: [
      { max: 37,  label: "Ansiedad baja",      color: "#10b981" },
      { max: 59,  label: "Ansiedad moderada",  color: "#f59e0b" },
      { max: 79,  label: "Ansiedad elevada",   color: "#ea580c" },
      { max: 120, label: "Ansiedad muy alta",  color: "#dc2626" },
    ],
    clinicalCutoff: 38, /* ≈ original ≥39 Estado ó ≥39 Rasgo en escala 1-4 */
    notes: "Ítems marcados con * son inversos y el sistema los corrige automáticamente para el total y las subescalas. STAI-E: refleja ansiedad situacional; STAI-R: rasgo ansioso estable. Cutoff por subescala ≥19/60 (escala 0-3) sugiere ansiedad clínica. Percentiles normativos por edad y sexo en manual TEA.",
    subescalas: [
      { nombre: "Estado (E)", items: 20, descripcion: "Cómo se siente ahora mismo", cutoff_propio: 19 },
      { nombre: "Rasgo (R)",  items: 20, descripcion: "Cómo se siente en general",  cutoff_propio: 19 },
    ],
  },

  /* ─── SCARED-41: Screen for Child Anxiety Related Disorders (completo)
   * Birmaher et al. (1997). Escala de 41 ítems para niños 8-18 años.
   * Auto-reporte niño/a O reporte de padres (versiones paralelas).
   * Escala: 0=No es cierto/casi nunca, 1=Algo cierto/a veces, 2=Muy cierto/casi siempre.
   * Validación Colombia: Pineda et al. (2012). */
  SCARED41: {
    name: "SCARED-41 — Screen for Child Anxiety Related Disorders (versión completa)",
    abbr: "SCARED-41",
    kind: "likert_flat",
    domain: "Ansiedad infantil",
    maxScore: 82,
    ageRange: "8-18 años",
    license: "Birmaher et al. 1997. Dominio público. Validación Colombia: Pineda et al. 2012.",
    questionPrefix: "Selecciona qué tan cierto es cada enunciado sobre ti (0=No/casi nunca, 1=A veces, 2=Sí/casi siempre):",
    scaleLabels: ["No/casi nunca", "A veces", "Sí/casi siempre"],
    items: [
      /* Trastorno de pánico / somático (ítems 1,6,9,12,15,18,19,22,24,27,30,34,38) */
      "Cuando me asusto, me cuesta respirar.",
      "Me duele la cabeza cuando estoy en la escuela.",
      "No me gustan estar con personas que no conozco bien.",
      "Me asusto cuando duermo fuera de casa.",
      "Me preocupo porque la gente me quiera.",
      "Cuando me asusto, siento que me voy a desmayar.",
      "Soy nervioso/a.",
      "Sigo a mi mamá o papá a todos lados.",
      "Me da miedo mirar de frente a la gente que no conozco bien.",
      "Me preocupo mucho.",
      "Cuando me asusto, siento que las cosas no son reales.",
      "Me da miedo dormir solo/a.",
      "Me preocupo mucho acerca de ser tan bueno/a como otros estudiantes.",
      "Cuando me asusto, siento que mi corazón late muy fuerte.",
      "Me da un miedo terrible que mis papás me abandonen.",
      "Cuando me asusto, siento como si todo fuera a salir muy mal.",
      "Me pongo nervioso/a de ir a la escuela.",
      "Cuando me asusto, siento que el corazón me late muy fuerte o que mi corazón va a dejar de latir.",
      "Me tiemblan las manos.",
      "Sueño que le pasa algo malo a mis papás.",
      "Me preocupa que las cosas vayan a salir mal.",
      "Cuando me asusto, sudo mucho.",
      "Soy un preocupón/preocupona.",
      "Me despierto con miedo durante la noche.",
      "Me da mucho miedo cuando tengo que presentar algo en la escuela.",
      "Cuando me asusto, me siento muy mal.",
      "Cuando me asusto, siento que me voy a ahogar.",
      "Los pensamientos de muerte o que me voy a morir se me vienen a la cabeza.",
      "Me siento nervioso/a cuando estoy con personas que no conozco bien.",
      "Cuando me asusto, siento que mis manos o pies se entumen.",
      "Me da miedo ir al colegio.",
      "Me preocupa por las cosas que sucedieron en el pasado.",
      "Cuando me asusto, siento que me voy a atragantar.",
      "Evito situaciones que me ponen nervioso/a.",
      "Me preocupa que puedan robarme o hacerme daño.",
      "Me da miedo ir a los lugares sin mis papás.",
      "Evito ir a los lugares que me asustan.",
      "Cuando estoy nervioso/a, me duele el estómago.",
      "Las preocupaciones me molestan mucho.",
      "Cuando me asusto, siento que voy a volverme loco/a o que voy a perder el control.",
      "Me preocupa que algo malo me pueda pasar.",
    ],
    severity: [
      { max: 24, label: "Sin ansiedad clínica", color: "#10b981" },
      { max: 29, label: "Leve",                 color: "#84cc16" },
      { max: 39, label: "Moderada",             color: "#f59e0b" },
      { max: 82, label: "Severa",               color: "#dc2626" },
    ],
    clinicalCutoff: 25,
    /* Subescalas SCARED-41 — §S2.4-fix */
    /* Índices 0-based según Birmaher et al. 1997 (ítems 1-based = idx+1):
     *   Pánico/Somático (13):  1, 6, 9, 12, 15, 18, 19, 22, 24, 27, 30, 34, 38
     *   GAD (9):               5, 8, 11, 14, 17, 18, 22, 24, 38
     *   Separación (8):        4, 8, 12, 14, 22, 25, 27, 29
     *   Fobia Social (7):      3, 10, 14, 18, 22, 27, 35
     *   Fobia Escolar (4):     1, 6, 12, 19
     * Bug histórico: solo 10/8/6/8/2 items asignados (sobraban 16).
     * Cross-loadings entre subescalas son conocidos y reportados en
     * Muris et al. 1998, Birmaher et al. 1999.
     */
    subescalas_info: [
      { nombre: "Pánico/Somático",        items_idx: [0, 5, 8, 11, 14, 17, 18, 21, 23, 26, 29, 33, 37], cutoff: 7 },
      { nombre: "Ansiedad Generalizada",  items_idx: [4, 7, 10, 13, 16, 17, 21, 23, 37],                       cutoff: 9 },
      { nombre: "Ansiedad de Separación", items_idx: [3, 7, 11, 13, 21, 24, 26, 28],                          cutoff: 5 },
      { nombre: "Fobia Social",           items_idx: [2, 9, 13, 17, 21, 26, 34],                              cutoff: 8 },
      { nombre: "Fobia Escolar",          items_idx: [0, 5, 11, 18],                                          cutoff: 3 },
    ],
    notes: "Corte total ≥25: probable trastorno de ansiedad. Subescalas permiten identificar tipo específico (índices 0-based según Birmaher 1997). Diferente del SCARED-5 (tamizaje rápido). Validado para Colombia por Pineda et al. 2012.",
  },

  /* ─── NPI-Q: Neuropsychiatric Inventory Questionnaire (Cummings 1994)
   * Versión breve del NPI administrada a cuidadores.
   * 12 dominios de síntomas neuropsiquiátricos. Frecuencia × Intensidad.
   * Dominio público para uso clínico y de investigación. */
  NPIQ: {
    name: "Inventario Neuropsiquiátrico — NPI-Q (versión cuidador)",
    abbr: "NPI-Q",
    kind: "binary_domains",
    domain: "Síntomas neuropsiquiátricos",
    maxScore: 36,
    cutoff: 4,
    ageRange: "Adulto mayor (reportado por cuidador)",
    license: "Cummings et al. 1994. Dominio público — uso clínico y de investigación.",
    domains: [
      {
        name: "Delirios",
        max: 3,
        items: [
          "¿Cree que alguien le está robando?",
          "¿Cree que su pareja le es infiel?",
          "¿Cree que hay personas en la casa que en realidad no están?",
        ],
      },
      {
        name: "Alucinaciones",
        max: 3,
        items: [
          "¿Ve cosas que otros no pueden ver?",
          "¿Escucha voces o ruidos?",
          "¿Siente que le tocan cuando en realidad no hay nadie?",
        ],
      },
      {
        name: "Agitación / Agresión",
        max: 3,
        items: [
          "¿Se opone a recibir ayuda de otros?",
          "¿Es terco/a y difícil de manejar?",
          "¿Grita, insulta o amenaza a otros?",
        ],
      },
      {
        name: "Depresión / Disforia",
        max: 3,
        items: [
          "¿Dice sentirse triste o llorar con frecuencia?",
          "¿Dice que es una carga para los demás?",
          "¿Habla de muerte o ha hecho intentos de hacerse daño?",
        ],
      },
      {
        name: "Ansiedad",
        max: 3,
        items: [
          "¿Se pone muy nervioso/a cuando se separa de usted?",
          "¿Tiene períodos de angustia sin razón aparente?",
          "¿Tiene miedos exagerados o irracionales?",
        ],
      },
      {
        name: "Euforia / Elación",
        max: 3,
        items: [
          "¿Está de buen humor de manera inapropiada?",
          "¿Se ríe sin razón aparente?",
          "¿Hace comentarios inapropiados o bromas de mal gusto?",
        ],
      },
      {
        name: "Apatía / Indiferencia",
        max: 3,
        items: [
          "¿Ha perdido interés en las actividades que antes disfrutaba?",
          "¿Parece indiferente y falto/a de motivación?",
          "¿Tiene dificultad para iniciar actividades por sí mismo/a?",
        ],
      },
      {
        name: "Desinhibición",
        max: 3,
        items: [
          "¿Hace o dice cosas inapropiadas en público?",
          "¿Hace comentarios sexuales fuera de lugar?",
          "¿Le habla a desconocidos como si los conociera de siempre?",
        ],
      },
      {
        name: "Irritabilidad / Labilidad",
        max: 3,
        items: [
          "¿Se pone irritable o molesto/a fácilmente?",
          "¿Tiene cambios de humor repentinos y sin razón?",
          "¿Discute por cosas sin importancia?",
        ],
      },
      {
        name: "Comportamiento motor aberrante",
        max: 3,
        items: [
          "¿Camina sin rumbo o abre y cierra cajones repetidamente?",
          "¿Repite los mismos movimientos o acciones?",
          "¿Manipula objetos sin propósito aparente?",
        ],
      },
      {
        name: "Trastornos del sueño / Conducta nocturna",
        max: 3,
        items: [
          "¿Le despierta por las noches o se levanta demasiado temprano?",
          "¿Camina por la casa de noche o hace cosas inapropiadas?",
          "¿Duerme demasiado durante el día?",
        ],
      },
      {
        name: "Trastornos del apetito y la alimentación",
        max: 3,
        items: [
          "¿Ha cambiado su apetito (come más o menos que antes)?",
          "¿Ha cambiado el tipo de alimentos que le gustan?",
          "¿Tiene conductas inapropiadas al comer (come muy rápido, come cosas no comestibles)?",
        ],
      },
    ],
    severity: [
      { max: 3,  label: "Sin síntomas significativos", color: "#10b981" },
      { max: 8,  label: "Leve",                        color: "#84cc16" },
      { max: 18, label: "Moderado",                    color: "#f59e0b" },
      { max: 36, label: "Severo",                      color: "#dc2626" },
    ],
    notes: "Administrado al cuidador/familiar. Suma ≥4: indicador de síntomas neuropsiquiátricos clínicamente significativos. El perfil de dominios afectados ayuda a orientar el tipo de demencia (p.ej., alucinaciones visuales → Lewy; desinhibición → DFT; delirios → EA avanzada). Complementar con CDR y FAQ.",
  },

  /* ─── ASRS-v1.1: Adult ADHD Self-Report Scale (adultos 18+) ─────────
   * Kessler et al. 2005. Desarrollado con la OMS. Dominio público.
   * 18 ítems basados en criterios DSM-IV (compatible con DSM-5).
   * Parte A (6 ítems) es el tamizaje; Parte B (12 ítems) amplía el análisis. */
  ASRS: {
    name: "ASRS-v1.1 — Adult ADHD Self-Report Scale",
    abbr: "ASRS",
    kind: "likert_flat",
    domain: "TDAH adultos",
    maxScore: 72,
    ageRange: "≥18 años",
    license: "Kessler et al. 2005, OMS. Dominio público. https://www.who.int/",
    questionPrefix: "¿Con qué frecuencia le ocurre lo siguiente? (0=Nunca, 4=Muy frecuente)",
    scaleLabels: ["Nunca", "Raramente", "A veces", "Frecuente", "Muy frecuente"],
    items: [
      /* PARTE A — Tamizaje (ítems 1-6) */
      "¿Con qué frecuencia le sucede que comete errores en su trabajo por no prestar suficiente atención a los detalles o por descuido?",
      "¿Con qué frecuencia tiene dificultades para mantener la atención en tareas tediosas o repetitivas?",
      "¿Con qué frecuencia tiene dificultades para concentrarse en lo que le dicen, incluso cuando le hablan directamente?",
      "¿Con qué frecuencia deja proyectos sin terminar por haberse entretenido en otras cosas?",
      "¿Con qué frecuencia pospone o evita comenzar tareas que requieren mucho esfuerzo mental?",
      "¿Con qué frecuencia pierde u olvida dónde pone las cosas importantes?",
      /* PARTE B — Ampliación (ítems 7-18) */
      "¿Con qué frecuencia se distrae con lo que sucede a su alrededor?",
      "¿Con qué frecuencia le cuesta relajarse en momentos de descanso?",
      "¿Con qué frecuencia le resulta difícil permanecer sentado/a en reuniones o situaciones donde se espera que lo esté?",
      "¿Con qué frecuencia se siente impulsado/a a moverse o como si lo/la empujaran un motor?",
      "¿Con qué frecuencia habla en exceso en situaciones sociales?",
      "¿Con qué frecuencia en una conversación termina las frases de las personas antes de que ellas las acaben?",
      "¿Con qué frecuencia tiene dificultad para esperar su turno en situaciones en las que es necesario?",
      "¿Con qué frecuencia interrumpe a otros cuando están ocupados?",
      "¿Con qué frecuencia tiene dificultades para controlar sus emociones?",
      "¿Con qué frecuencia sus actividades son poco organizadas?",
      "¿Con qué frecuencia tiene dificultad para planificar las cosas con anticipación?",
      "¿Con qué frecuencia tiene problemas para llevar a cabo las actividades diarias en el orden correcto?",
    ],
    severity: [
      { max: 13, label: "No sugiere TDAH",       color: "#10b981" },
      { max: 23, label: "Probable TDAH leve",    color: "#f59e0b" },
      { max: 72, label: "Probable TDAH moderado-severo", color: "#dc2626" },
    ],
    clinicalCutoff: 14,
    notes: "Parte A (ítems 1-6): suma ≥14 en estos 6 ítems = screening positivo con alta especificidad. Parte B amplía el análisis. No diagnóstico solo — requiere evaluación neuropsicológica completa y criterios DSM-5 completos. En adultos se exigen 5+ síntomas (no 6).",
    subescalas: [
      { nombre: "Parte A — Inatención (tamizaje)", items: 6, cutoff_propio: 14 },
      { nombre: "Parte B — Análisis ampliado",    items: 12, cutoff_propio: null },
    ],
  },

  /* ─── CONNERS-3 abreviado (padres) — TDAH en niños 6-18 años ────────
   * Conners 2008. Basado en DSM-5. Items de 0-3.
   * Versión ABREVIADA de 10 ítems para tamizaje rápido en consulta. */
  CONNERS_ABR: {
    name: "Conners-3 Abreviado — Padres (10 ítems de tamizaje)",
    abbr: "Conners-3(A)",
    kind: "likert_flat",
    domain: "TDAH / oposicionista",
    maxScore: 30,
    ageRange: "6-18 años (reporte padres)",
    license: "Conners 2008 — Multi-Health Systems. Versión abreviada de uso referencial. Requiere licencia para uso formal.",
    questionPrefix: "¿Con qué frecuencia observa las siguientes conductas en su hijo/a? (0=Nunca, 3=Muy frecuente)",
    scaleLabels: ["Nunca/casi nunca", "Ocasionalmente", "A menudo", "Muy frecuente"],
    items: [
      "Está en constante movimiento, parece que lo/la impulsa un motor.",
      "Tiene dificultades para mantenerse sentado/a cuando se espera que lo/la esté.",
      "Se distrae fácilmente con estímulos del entorno.",
      "No presta atención a los detalles o comete errores por descuido en las tareas.",
      "Tiene dificultad para mantener la atención en tareas o actividades de juego.",
      "Parece no escuchar cuando se le habla directamente.",
      "No completa las tareas escolares, los quehaceres u otras actividades.",
      "Pierde cosas necesarias para tareas y actividades.",
      "Actúa antes de pensar.",
      "Tiene dificultad para esperar su turno.",
    ],
    severity: [
      { max: 9,  label: "No significativo",       color: "#10b981" },
      { max: 19, label: "Indicador leve",          color: "#f59e0b" },
      { max: 30, label: "Indicador significativo", color: "#dc2626" },
    ],
    clinicalCutoff: 10,
    notes: "Tamizaje referencial únicamente. Para evaluación formal usar Conners-3 completo con perfiles normativos por edad y sexo. Corte ≥10: aplicar SNAP-IV completo y evaluación neuropsicológica.",
  },

  /* ─── Zarit Burden Interview (versión 22 ítems) — Sobrecarga cuidador
   * Zarit, Reever & Bach-Peterson 1980. Dominio público. */
  ZARIT: {
    name: "Escala de Sobrecarga del Cuidador de Zarit (22 ítems)",
    abbr: "Zarit",
    kind: "likert_flat",
    domain: "Sobrecarga del cuidador",
    maxScore: 88,
    ageRange: "Cuidadores de personas con demencia o dependencia",
    license: "Zarit et al. 1980. Dominio público. Validación española: Martín et al. 1996.",
    questionPrefix: "¿Con qué frecuencia se siente así en su rol de cuidador/a? (0=Nunca, 4=Casi siempre)",
    scaleLabels: ["Nunca", "Casi nunca", "A veces", "Bastante a menudo", "Casi siempre"],
    items: [
      "¿Cree que su familiar le pide más ayuda de la que realmente necesita?",
      "¿Cree que debido al tiempo que dedica a su familiar no tiene suficiente tiempo para usted?",
      "¿Se siente estresado/a por tener que cuidar a su familiar y además atender otras responsabilidades?",
      "¿Se siente avergonzado/a por la conducta de su familiar?",
      "¿Se siente irritado/a cuando está cerca de su familiar?",
      "¿Cree que la situación actual afecta negativamente su relación con otros familiares o amigos?",
      "¿Tiene miedo por el futuro de su familiar?",
      "¿Cree que su familiar depende de usted?",
      "¿Se siente agotado/a cuando tiene que estar junto a su familiar?",
      "¿Cree que su salud se ha resentido por cuidar a su familiar?",
      "¿Cree que no tiene la intimidad que desearía debido a su familiar?",
      "¿Cree que su vida social se ha visto afectada negativamente por tener que cuidar a su familiar?",
      "¿Se siente incómodo/a por tener invitados en casa a causa de su familiar?",
      "¿Cree que su familiar espera que usted le cuide como si fuera la única persona con la que puede contar?",
      "¿Cree que no tiene suficiente dinero para cuidar a su familiar además de sus otros gastos?",
      "¿Cree que no será capaz de cuidar a su familiar por mucho más tiempo?",
      "¿Siente que ha perdido el control de su vida desde que comenzó la enfermedad de su familiar?",
      "¿Desearía poder dejar el cuidado de su familiar a otra persona?",
      "¿Se siente indeciso/a sobre qué hacer con su familiar?",
      "¿Cree que debería hacer más por su familiar?",
      "¿Cree que podría cuidar mejor a su familiar?",
      "Globalmente, ¿en qué medida se siente agobiado/a por tener que cuidar a su familiar?",
    ],
    severity: [
      { max: 46, label: "Sobrecarga leve o ausente",  color: "#10b981" },
      { max: 55, label: "Sobrecarga moderada",        color: "#f59e0b" },
      { max: 88, label: "Sobrecarga intensa",         color: "#dc2626" },
    ],
    clinicalCutoff: 47,
    notes: "Corte ≥47: sobrecarga clínicamente significativa. Corte ≥56: sobrecarga severa — considerar respiro para el cuidador e intervención prioritaria. Complementar con psicoeducación y grupos de apoyo.",
  },

  /* ─── FAB: Frontal Assessment Battery (Dubois et al. 2000) ──────────────
   * 6 subtareas administradas directamente al paciente (5-10 min).
   * Detecta disfunción del lóbulo frontal en demencias (DFT, EP, etc.).
   * Cada subtarea puntúa 0-3. Total 0-18.
   * Corte ≤12: sugestivo de disfunción frontal.
   * Versión adaptada al español con normas colombianas (Arango-Lasprilla 2015). */
  IFS: {
    name: "INECO Frontal Screening (IFS) — versión Colombia",
    abbr: "IFS",
    kind: "binary_domains",
    domain: "Cognitivo ejecutivo",
    maxScore: 30,
    cutoff: 17.5,
    ageRange: "Adulto / adulto mayor",
    license: "Torralva et al. 2009. Validación Colombia: Romero-Vanegas et al. 2014 (corte 17.5/30).",
    notes: "Corte Colombia 17.5 (sens 92.8%, esp 86.3%). Diferencia DFT vs Alzheimer/depresión. No sustituye evaluación completa.",
    domains: [
      { name: "Programación motora", max: 3, items: ["Luria 3/3", "2/3", "1/3", "0/3"] },
      { name: "Conflicto", max: 3, items: ["Opuestas sin error", "1 error", "2 errores", "≥3 errores"] },
      { name: "Flexibilidad", max: 3, items: ["Fluidez ≥12", "9-11", "6-8", "<6"] },
      { name: "Abstracción", max: 3, items: ["3/3 refranes", "2/3", "1/3", "0/3"] },
      { name: "Go/No-Go", max: 3, items: ["Sin errores", "1 error", "2 errores", "≥3 errores"] },
      { name: "Atención espacial", max: 3, items: ["3/3", "2/3", "1/3", "0/3"] },
      { name: "Memoria de trabajo", max: 3, items: ["Directa+inversa OK", "solo directa", "solo inversa", "falla ambas"] },
      { name: "Inhibición", max: 3, items: ["Stroop adaptado OK", "leve", "moderado", "severo"] },
    ],
  },
  FAB: {
    name: "Frontal Assessment Battery (FAB) — Batería de Evaluación Frontal",
    abbr: "FAB",
    kind: "binary_domains",
    domain: "Cognitivo",
    maxScore: 18, cutoff: 13,
    ageRange: "Adulto / adulto mayor",
    license: "Dubois et al. 2000 (Neurology). Dominio público. Normas colombianas: Arango-Lasprilla et al. 2015.",
    domains: [
      {
        name: "Conceptualización (Semejanzas)",
        max: 3,
        items: [
          "3/3: plátano-naranja-pera (frutas) + mesa-silla-cama (muebles) + tulipán-rosa-margarita (flores)",
          "2/3: solo 2 correctas",
          "1/3: solo 1 correcta — 0/3: ninguna",
        ],
      },
      {
        name: "Flexibilidad mental (Fluidez lexical en 1 min)",
        max: 3,
        items: [
          "≥9 palabras en 1 min → 3 pts",
          "7-8 palabras → 2 pts · 5-6 palabras → 1 pt",
          "<5 palabras → 0 pts",
        ],
      },
      {
        name: "Programación motora (Serie de Luria)",
        max: 3,
        items: [
          "≥6 secuencias correctas solo → 3 pts",
          "≥3 secuencias con instrucción verbal → 2 pts · ≥6 con el examinador presente → 1 pt",
          "No puede reproducir la serie con el examinador → 0 pts",
        ],
      },
      {
        name: "Sensibilidad a la interferencia (Instrucciones opuestas)",
        max: 3,
        items: [
          "Sin errores → 3 pts",
          "1-2 errores → 2 pts",
          ">2 errores → 1 pt · Imita al examinador ≥4 veces → 0 pts",
        ],
      },
      {
        name: "Control inhibitorio (Go / No-Go)",
        max: 3,
        items: [
          "Sin errores → 3 pts",
          "1-2 errores → 2 pts",
          ">2 errores → 1 pt · Toca siempre → 0 pts",
        ],
      },
      {
        name: "Autonomía ambiental (Comportamiento de prensión)",
        max: 3,
        items: [
          "No toma las manos → 3 pts",
          "Duda y pregunta si debe → 2 pts",
          "Toma las manos sin instrucción de hacerlo → 1 pt",
          "Toma las manos aunque se le pida no hacerlo → 0 pts",
        ],
      },
    ],
    notes: "Administración directa (no autoinforme). Corte ≤12 sugiere disfunción prefrontal. FAB distingue DFT (muy bajo) de Alzheimer temprano (más preservado). Útil en EP, DV y evaluación de capacidad para el trabajo. Tiempo: 5-10 min.",
  },

  /* ─── IES-R: Impact of Event Scale Revised (Weiss & Marmar 1997) ─────
   * 22 ítems en 3 subescalas: Intrusión (8), Evitación (8), Hiperactivación (6).
   * Escala: 0=nada · 1=un poco · 2=moderadamente · 3=bastante · 4=extremadamente.
   * Para adultos que han vivido un evento traumático. Dominio público.
   * Validación en Colombia: Rodríguez-Guarín et al. (2020). */
  IESR: {
    name: "Escala de Impacto de Eventos Revisada (IES-R)",
    abbr: "IES-R",
    kind: "likert_flat",
    domain: "Trauma / PTSD",
    maxScore: 88, /* 22 ítems × 4 */
    ageRange: "Adulto (con antecedente de evento traumático)",
    license: "Weiss & Marmar 1997. Dominio público. Validación Colombia: Rodríguez-Guarín et al. 2020.",
    questionPrefix: "En los últimos 7 días, ¿cuánta dificultad le causó cada una de las siguientes situaciones relacionadas con el evento?",
    scaleLabels: ["Nada", "Un poco", "Moderada", "Bastante", "Extrema"],
    items: [
      /* Intrusión (ítems 1-8 en la versión original: 1,2,3,6,9,16,20,22) */
      "Cualquier recuerdo sobre ello me volvían sentimientos al respecto.",
      "Tenía sueños perturbadores sobre ello.",
      "Otras cosas me hacían pensar en ello.",
      "Me sentía irritable y enojado/a.",
      "Trataba de no pensar en ello cuando me venía a la mente.",
      "Pensaba en ello cuando no quería.",
      "Las imágenes del evento aparecían en mi mente de repente.",
      "Me sentía como si todavía estuviera ocurriendo o como si volviera a ocurrir.",
      /* Evitación (ítems originales: 5,7,8,11,12,13,17,22) */
      "Traté de quitármelo de la mente.",
      "Traté de no hablar de ello.",
      "Me di cuenta de que aún tenía muchos sentimientos al respecto, pero no los trate.",
      "Mis sentimientos al respecto estaban algo entumecidos.",
      "Intenté no pensar en ello.",
      "Sabía que todavía tenía muchos sentimientos al respecto, pero no los afronté.",
      "Evité dejarme perturbar cuando pensé en ello o se lo recordaron.",
      "Intenté no pensar en ello.",
      /* Hiperactivación (ítems originales: 4,10,14,15,18,19,21) */
      "Tuve dificultades para quedarme dormido/a.",
      "Tenía estallidos de sentimientos fuertes sobre ello.",
      "Trataba de sentir como si no hubiera ocurrido o de que no era real.",
      "Tenía imágenes sobre ello.",
      "Me sobresaltaba y asustaba fácilmente.",
      "Traté de no pensar en ello.",
    ],
    severity: [
      { max: 23, label: "Sin estrés postraumático significativo", color: "#10b981" },
      { max: 32, label: "PTSD probable leve",                    color: "#f59e0b" },
      { max: 43, label: "PTSD moderado — evaluación indicada",   color: "#ea580c" },
      { max: 88, label: "PTSD severo",                           color: "#dc2626" },
    ],
    clinicalCutoff: 33,
    subescalas: [
      { nombre: "Intrusión",        items: 8, descripcion: "Recuerdos y flashbacks involuntarios", cutoff_propio: 12 },
      { nombre: "Evitación",        items: 8, descripcion: "Evasión de recuerdos o situaciones",    cutoff_propio: 8  },
      { nombre: "Hiperactivación",  items: 6, descripcion: "Arousal, vigilancia excesiva",          cutoff_propio: 9  },
    ],
    notes: "Aplicar solo cuando existe un evento traumático identificado. Corte ≥33: PTSD probable. Corte ≥37 en estudios con alta especificidad. Evaluar también impacto funcional y disociación. No reemplaza diagnóstico clínico por criterios DSM-5.",
    redFlagItems: [7, 19], /* Reexperimentación intensa y despersonalización */
    redFlagMessage: "Se identificaron síntomas de reexperimentación intensa o disociación. Priorizar evaluación clínica y consideración de riesgo.",
  },

  /* ─── PCL-5: PTSD Checklist for DSM-5 (Weathers et al. 2013) ───────────
   * Versión breve de 20 ítems auto-aplicado, basado en criterios DSM-5.
   * Escala: 0=nada · 4=extremadamente. Dominio público (VA / PTSD).
   * Normas en español: Bovin et al. 2016. */
  PCL5: {
    name: "PTSD Checklist for DSM-5 (PCL-5)",
    abbr: "PCL-5",
    kind: "likert_flat",
    domain: "Trauma / PTSD",
    maxScore: 80, /* 20 ítems × 4 */
    ageRange: "Adultos (≥18 años)",
    license: "Weathers et al. 2013 (VA/DoD). Dominio público. https://www.ptsd.va.gov/",
    questionPrefix: "En el último mes, ¿cuánto le ha molestado cada uno de los siguientes problemas relacionados con una experiencia estresante del pasado?",
    scaleLabels: ["Nada", "Un poco", "Moderada", "Bastante", "Extrema"],
    items: [
      /* Criterio B — Intrusión */
      "Recuerdos repetidos, perturbadores e involuntarios de la experiencia estresante.",
      "Sueños perturbadores de la experiencia estresante.",
      "De repente sentirse o actuar como si la experiencia estresante estuviera ocurriendo de nuevo.",
      "Sentirse muy alterado/a cuando algo le recuerda la experiencia.",
      "Tener reacciones físicas fuertes cuando algo le recuerda la experiencia.",
      /* Criterio C — Evitación */
      "Evitar recuerdos, pensamientos o sentimientos relacionados con la experiencia.",
      "Evitar personas, lugares o situaciones que le recuerden la experiencia.",
      /* Criterio D — Cogniciones negativas */
      "Tener problemas para recordar partes importantes de la experiencia.",
      "Tener creencias negativas acerca de uno mismo, de los demás o del mundo.",
      "Culparse a sí mismo/a o a otros de la experiencia o de lo que pasó después.",
      "Tener sentimientos negativos intensos (miedo, horror, ira, culpa o vergüenza).",
      "Perder el interés en actividades que antes disfrutaba.",
      "Sentirse distante o alejado/a de las personas.",
      "Tener dificultad para experimentar sentimientos positivos.",
      /* Criterio E — Hiperactivación */
      "Comportamiento irritable, arrebatos de ira o actuar agresivamente.",
      "Asumir riesgos o hacer cosas que podrían hacerle daño.",
      "Estar siempre en guardia, vigilante o alerta.",
      "Sobresaltarse fácilmente.",
      "Tener dificultades para concentrarse.",
      "Problemas para dormir.",
    ],
    severity: [
      { max: 19, label: "Sin indicadores significativos de PTSD", color: "#10b981" },
      { max: 31, label: "PTSD probable leve",                     color: "#f59e0b" },
      { max: 49, label: "PTSD moderado",                          color: "#ea580c" },
      { max: 80, label: "PTSD severo",                            color: "#dc2626" },
    ],
    clinicalCutoff: 31,
    notes: "Corte ≥31: PTSD probable (especificidad ≈0.82, sensibilidad ≈0.90 en Bovin 2016). Permite evaluar los 4 clusters DSM-5 de síntomas. No es diagnóstico — complementar con entrevista clínica (CAPS-5 si disponible). Los 20 ítems corresponden a los 20 síntomas DSM-5 del TEPT.",
  },

  /* ─── BDI-II — Beck Depression Inventory II (depresión en adultos) ─ */
  BDI2: {
    name: "Inventario de Depresión de Beck II (BDI-II)",
    abbr: "BDI-II",
    kind: "likert_flat",
    domain: "Estado de ánimo / Depresión",
    maxScore: 63, /* 21 ítems × 3 */
    ageRange: "Adultos (≥18 años)",
    license: "Beck, Steer & Brown 1996. Pearson. Uso clínico bajo licencia. Citar: Beck AT et al. Manual BDI-II.",
    questionPrefix: "En las últimas 2 semanas, incluyendo hoy, ¿cómo se ha sentido respecto a cada una de estas afirmaciones? Elija la que mejor describa su estado.",
    scaleLabels: ["0", "1", "2", "3"],
    items: [
      "Tristeza: No me siento triste / Me siento triste / Estoy triste todo el tiempo / Estoy tan triste que no puedo soportarlo",
      "Pesimismo: No me siento desanimado / Siento menos entusiasmo que antes / No espero que las cosas me salgan bien / Siento que el futuro no tiene esperanza",
      "Fracaso: No me siento fracasado / He fracasado más de lo debido / Veo que he tenido más fracasos que los demás / Siento que soy un fracaso total",
      "Pérdida de placer: Disfruto las cosas como siempre / No disfruto las cosas tanto como antes / No obtengo placer de casi nada / No siento ningún placer en absoluto",
      "Culpa: No me siento culpable / Me siento culpable bastante a menudo / Me siento culpable la mayor parte del tiempo / Me siento culpable constantemente",
      "Castigo: No creo estar siendo castigado / Siento que puedo ser castigado / Espero ser castigado / Siento que estoy siendo castigado",
      "Disconformidad con uno mismo: No estoy decepcionado de mí / Estoy decepcionado de mí mismo / Me da vergüenza (o desagrado) de mí mismo / Me detesto a mí mismo",
      "Autocrítica: No soy más crítico conmigo que antes / Soy más crítico conmigo que antes / Me culpo por todos mis errores / Me culpo por todo lo malo que sucede",
      "Ideación suicida: No tengo pensamientos suicidas / Tengo pensamientos suicidas pero no los llevaría a cabo / Me gustaría suicidarme / Me suicidaría si tuviera la oportunidad",
      "Llanto: No lloro más de lo habitual / Lloro más que antes / Lloro por cualquier cosa / Quisiera llorar pero no puedo",
      "Agitación: No estoy más inquieto o agitado que de costumbre / Me siento más inquieto o agitado que de costumbre / Estoy tan inquieto que me cuesta quedarme quieto / Estoy tan agitado que tengo que moverme o hacer algo",
      "Interés social: No he perdido el interés en los demás / Estoy menos interesado en los demás que antes / He perdido la mayor parte del interés en los demás / He perdido todo el interés en los demás",
      "Indecisión: Tomo decisiones como siempre / Me cuesta más tomar decisiones que antes / Tengo mucha dificultad para tomar decisiones / No puedo tomar ninguna decisión",
      "Autoimagen: No siento que me vea peor que antes / Me preocupa parecer avejentado o poco atractivo / Siento que hay cambios permanentes en mi aspecto / Me veo feo/rechazante",
      "Capacidad de trabajo: Puedo trabajar tan bien como antes / Debo esforzarme más para empezar a hacer algo / Tengo que obligarme a mí mismo para hacer las cosas / No puedo hacer nada en absoluto",
      "Trastornos del sueño: Puedo dormir tan bien como siempre / No duermo tan bien como antes / Me despierto varias horas antes de lo habitual / No puedo dormir en absoluto",
      "Fatigabilidad: No me canso más de lo habitual / Me canso más fácilmente que antes / Cualquier cosa que hago me cansa / Estoy demasiado fatigado para hacer cualquier cosa",
      "Apetito: Mi apetito no ha cambiado / Mi apetito es menor que antes / Mi apetito es mucho menor que antes / No tengo ningún apetito",
      "Pérdida de peso: No he perdido peso / He perdido más de 2 kg / He perdido más de 4 kg / He perdido más de 7 kg",
      "Hipocondría: No estoy más preocupado de mi salud de lo habitual / Estoy preocupado por dolores o problemas físicos / Estoy tan preocupado por mi salud que me cuesta pensar en otra cosa / Estoy tan preocupado por mi salud que no puedo pensar en nada más",
      "Libido: No he notado cambios en mi interés sexual / Estoy menos interesado en el sexo que antes / Estoy mucho menos interesado en el sexo ahora / He perdido completamente el interés sexual",
    ],
    severity: [
      { max: 13, label: "Depresión mínima",              color: "#10b981" },
      { max: 19, label: "Depresión leve",                color: "#84cc16" },
      { max: 28, label: "Depresión moderada",            color: "#f59e0b" },
      { max: 63, label: "Depresión severa",              color: "#dc2626" },
    ],
    clinicalCutoff: 14,
    redFlags: [
      { itemIndex: 9, thresholds: [2, 3], message: "⚠ Ideación suicida presente. Aplicar C-SSRS inmediatamente (Módulo Sesiones Clínicas)." },
    ],
    notes: "Corte ≥14: depresión mínima. Corte ≥20: depresión moderada. Corte ≥29: depresión severa. Validado en Colombia (Gómez-Maquet et al. 2012, Univ. de los Andes). El ítem 9 evalúa ideación suicida — si ≥2, aplicar C-SSRS según protocolo institucional.",
  },

  /* ─── MOCA-BASIC — MoCA para baja escolaridad ─ */
  MOCABasic: {
    name: "Montreal Cognitive Assessment Basic (MoCA-Basic)",
    abbr: "MoCA-Basic",
    kind: "binary_domains",
    domain: "Cognitivo",
    maxScore: 30, cutoff: 23,
    ageRange: "Adulto mayor con baja escolaridad (≤5 años)",
    license: "Nasreddine et al. 2015. www.mocatest.org. Requiere certificación. Citar la versión original.",
    domains: [
      { name: "Función Ejecutiva", max: 6, items: ["Fluidez fonémica", "Trail Making simplificado", "Abstracción"] },
      { name: "Identificación", max: 5, items: ["León", "Rinoceronte", "Camello", "Elefante", "Jirafa"] },
      { name: "Orientación", max: 6, items: ["Día", "Mes", "Año", "Lugar", "Ciudad", "País"] },
      { name: "Cálculo", max: 3, items: ["100-7", "93-7", "86-7"] },
      { name: "Lenguaje", max: 5, items: ["Repetir frase A", "Repetir frase B", "Denominación", "Fluidez animales 1 min"] },
      { name: "Abstracción", max: 3, items: ["Semejanza tren-bicicleta", "Semejanza reloj-regla", "Proverbio"] },
      { name: "Recuerdo Diferido", max: 2, items: ["Recuerdo libre 1 (palabras)", "Recuerdo libre 2"] },
    ],
    notes: "Diseñado para poblaciones con escolaridad ≤5 años, donde el MoCA estándar tiene bajo rendimiento (efecto piso). Corte sugerido: ≤23 sugiere DCL. Ajustar según edad y escolaridad. Validación latinoamericana: Delgado et al. 2019 (Chile).",
  },
};


/* ═══════════════════════════════════════════════════════════════════════
 * F8.1 — Refactor por CONSTRUCTO (no por nombre)
 * ───────────────────────────────────────────────────────────────────────
 * El campo libre ``domain`` de cada SCREENING_FORMS no normaliza:
 *   - "Ansiedad", "Ansiedad / Depresión", "Ansiedad infantil" coexisten
 *   - "Estado de ánimo / Depresión" vs "Depresión" causan duplicados
 *
 * Esta sección añade un índice normalizado ``constructo`` + ``poblacion_objetivo``
 * sin tocar la estructura existente (backwards compat con ScreeningPage.jsx).
 *
 * Taxonomía de constructos psicológicos canónicos (basada en DSM-5-TR,
 * Marinus & Arango-Lasprilla 2017, Sattler 2008):
 *   - depresion             : PHQ9, BDI2, GDS15, HADS(subdep)
 *   - ansiedad              : GAD7, BAI, STAI, HADS(subanx)
 *   - ansiedad_infantil     : SCARED5, SCARED41
 *   - tdah_infantil         : SNAPIV, CONNERS_ABR
 *   - tdah_escolar          : VANDERBILT
 *   - tdah_adulto           : ASRS
 *   - tea_early_screening   : MCHAT
 *   - cognitivo_global      : MMSE, MoCA, ACE3, MOCABasic
 *   - cognitivo_ejecutivo   : FAB
 *   - demencia_severidad    : CDR
 *   - funcionalidad_basica  : BARTHEL
 *   - funcionalidad_instrum : FAQ
 *   - neuropsiquiatria      : NPIQ, NPIQ_FLAT
 *   - sobrecarga_cuidador   : ZARIT, ZARIT7
 *   - trauma_ptsd           : IESR, PCL5
 *
 * Poblaciones: 'infantil' (≤11), 'adolescente' (12-17), 'adulto' (18-64),
 * 'adulto_mayor' (≥65), 'cuidador' (proxy).
 *
 * Los formularios con poblacion_objetivo='universal' se usan en cualquier edad.
 * ═══════════════════════════════════════════════════════════════════════ */

export const CONSTRUCTOS = {
  depresion: {
    label: "Depresión",
    descripcion: "Síntomas depresivos, anhedonia, ideación suicida.",
    color: "#6366f1",
    icono: "sentiment_very_dissatisfied",
  },
  ansiedad: {
    label: "Ansiedad",
    descripcion: "Síntomas ansiosos generalizados, pánico, fobias.",
    color: "#0ea5e9",
    icono: "mood_bad",
  },
  ansiedad_infantil: {
    label: "Ansiedad infantil",
    descripcion: "Escalas de ansiedad adaptadas para menores.",
    color: "#06b6d4",
    icono: "child_care",
  },
  tdah_infantil: {
    label: "TDAH infantil",
    descripcion: "TDAH y comportamiento oposicionista (padres/docentes).",
    color: "#f59e0b",
    icono: "bolt",
  },
  tdah_escolar: {
    label: "TDAH escolar",
    descripcion: "TDAH en contexto escolar (padres + docentes).",
    color: "#f97316",
    icono: "school",
  },
  tdah_adulto: {
    label: "TDAH adulto",
    descripcion: "Auto-reporte de TDAH en adultos (ASRS).",
    color: "#fb923c",
    icono: "self_improvement",
  },
  tea_early_screening: {
    label: "TEA (screening temprano)",
    descripcion: "Signos tempranos de Trastorno del Espectro Autista.",
    color: "#a855f7",
    icono: "visibility",
  },
  cognitivo_global: {
    label: "Cribado cognitivo global",
    descripcion: "MMSE, MoCA y similares para deterioro cognitivo.",
    color: "#0d9488",
    icono: "psychology",
  },
  cognitivo_ejecutivo: {
    label: "Función ejecutiva",
    descripcion: "Funciones ejecutivas (FAB).",
    color: "#14b8a6",
    icono: "account_tree",
  },
  demencia_severidad: {
    label: "Severidad demencia",
    descripcion: "Estadificación clínica de demencia (CDR).",
    color: "#7c3aed",
    icono: "elderly",
  },
  funcionalidad_basica: {
    label: "Funcionalidad básica (ABVD)",
    descripcion: "Actividades básicas de la vida diaria.",
    color: "#16a34a",
    icono: "accessibility_new",
  },
  funcionalidad_instrum: {
    label: "Funcionalidad instrumental (AIVD)",
    descripcion: "Actividades instrumentales de la vida diaria.",
    color: "#22c55e",
    icono: "directions_walk",
  },
  neuropsiquiatria: {
    label: "Síntomas neuropsiquiátricos",
    descripcion: "Inventario neuropsiquiátrico (NPI-Q).",
    color: "#e11d48",
    icono: "psychology_alt",
  },
  sobrecarga_cuidador: {
    label: "Sobrecarga del cuidador",
    descripcion: "Zarit para cuidadores principales.",
    color: "#dc2626",
    icono: "volunteer_activism",
  },
  trauma_ptsd: {
    label: "Trauma / PTSD",
    descripcion: "Tamizaje de estrés post-traumático.",
    color: "#b91c1c",
    icono: "crisis_alert",
  },
};

export const POBLACIONES = {
  universal: "Universal (todas las edades)",
  infantil: "Infantil (≤ 11 años)",
  adolescente: "Adolescente (12-17 años)",
  adulto: "Adulto (18-64 años)",
  adulto_mayor: "Adulto mayor (≥ 65 años)",
  cuidador: "Cuidador (proxy)",
};


/**
 * SCREENING_INDEX — índice normalizado por test_id.
 * Backwards compat: NO modifica SCREENING_FORMS, solo agrega metadata.
 *
 * Para añadir un nuevo test: agregar fila aquí con constructo, poblacion_objetivo,
 * y opcionalmente poblacion_alternativa (p. ej. universal + adultos mayores).
 */
export const SCREENING_INDEX = {
  /* Cognitivo */
  MMSE:        { constructo: "cognitivo_global",    poblacion_objetivo: ["adulto", "adulto_mayor"] },
  MoCA:        { constructo: "cognitivo_global",    poblacion_objetivo: ["adulto", "adulto_mayor"] },
  ACE3:        { constructo: "cognitivo_global",    poblacion_objetivo: ["adulto", "adulto_mayor"] },
  MOCABasic:   { constructo: "cognitivo_global",    poblacion_objetivo: ["adulto_mayor"], notas_poblacion: "Diseñado para escolaridad ≤5 años" },
  IFS:         { constructo: "cognitivo_ejecutivo", poblacion_objetivo: ["adulto", "adulto_mayor"], notas_poblacion: "Corte CO 17.5" },
  FAB:         { constructo: "cognitivo_ejecutivo", poblacion_objetivo: ["adulto", "adulto_mayor"] },
  CDR:         { constructo: "demencia_severidad",  poblacion_objetivo: ["adulto_mayor"] },

  /* Depresión */
  PHQ9:        { constructo: "depresion",           poblacion_objetivo: ["universal"] },
  BDI2:        { constructo: "depresion",           poblacion_objetivo: ["universal"] },
  GDS15:       { constructo: "depresion",           poblacion_objetivo: ["adulto_mayor"] },
  HADS:        { constructo: "depresion",           poblacion_objetivo: ["adulto", "adulto_mayor"], notas_poblacion: "Escala combinada ansiedad+depresión" },

  /* Ansiedad */
  GAD7:        { constructo: "ansiedad",            poblacion_objetivo: ["universal"] },
  BAI:         { constructo: "ansiedad",            poblacion_objetivo: ["universal"] },
  STAI:        { constructo: "ansiedad",            poblacion_objetivo: ["adolescente", "adulto"] },

  /* Ansiedad infantil */
  SCARED5:     { constructo: "ansiedad_infantil",   poblacion_objetivo: ["infantil", "adolescente"] },
  SCARED41:    { constructo: "ansiedad_infantil",   poblacion_objetivo: ["infantil", "adolescente"] },

  /* TDAH */
  SNAPIV:      { constructo: "tdah_infantil",       poblacion_objetivo: ["infantil", "adolescente"] },
  CONNERS_ABR: { constructo: "tdah_infantil",       poblacion_objetivo: ["infantil", "adolescente"], notas_poblacion: "Conners-3 abreviado" },
  VANDERBILT:  { constructo: "tdah_escolar",        poblacion_objetivo: ["infantil", "adolescente"] },
  ASRS:        { constructo: "tdah_adulto",         poblacion_objetivo: ["adulto"] },

  /* TEA */
  MCHAT:       { constructo: "tea_early_screening", poblacion_objetivo: ["infantil"], notas_poblacion: "Edad 16-30 meses" },

  /* Funcionalidad */
  BARTHEL:     { constructo: "funcionalidad_basica",poblacion_objetivo: ["adulto", "adulto_mayor"] },
  FAQ:         { constructo: "funcionalidad_instrum",poblacion_objetivo: ["adulto_mayor"] },

  /* Neuropsiquiatría */
  NPIQ:        { constructo: "neuropsiquiatria",    poblacion_objetivo: ["adulto_mayor"] },
  NPIQ_FLAT:   { constructo: "neuropsiquiatria",    poblacion_objetivo: ["adulto_mayor"], notas_poblacion: "Versión plana Likert" },

  /* Cuidador */
  ZARIT:       { constructo: "sobrecarga_cuidador", poblacion_objetivo: ["cuidador"] },
  ZARIT7:      { constructo: "sobrecarga_cuidador", poblacion_objetivo: ["cuidador"], notas_poblacion: "Zarit-7 abreviado" },

  /* Trauma / PTSD */
  IESR:        { constructo: "trauma_ptsd",         poblacion_objetivo: ["universal"] },
  PCL5:        { constructo: "trauma_ptsd",         poblacion_objetivo: ["adulto"] },
};


/* Helpers (no mutan el estado, son funciones puras) */

/**
 * Devuelve los IDs de SCREENING_FORMS que mapean a un constructo dado.
 * @param {string} constructo - clave de CONSTRUCTOS (p. ej. "depresion")
 * @returns {string[]} IDs de tests
 */
export function getFormsPorConstructo(constructo) {
  return Object.entries(SCREENING_INDEX)
    .filter(([, meta]) => meta.constructo === constructo)
    .map(([id]) => id);
}

/**
 * Devuelve la lista de constructos con al menos un test disponible.
 * @returns {Array<{id: string, label: string, count: number, color: string, icono: string, descripcion: string}>}
 */
export function getConstructosDisponibles() {
  const counts = {};
  for (const [, meta] of Object.entries(SCREENING_INDEX)) {
    counts[meta.constructo] = (counts[meta.constructo] || 0) + 1;
  }
  return Object.entries(CONSTRUCTOS)
    .filter(([id]) => counts[id] > 0)
    .map(([id, meta]) => ({
      id,
      label: meta.label,
      descripcion: meta.descripcion,
      color: meta.color,
      icono: meta.icono,
      count: counts[id],
    }));
}

/**
 * Devuelve los IDs de SCREENING_FORMS aplicables a una población.
 * Tests con ``poblacion_objetivo = ['universal']`` se incluyen siempre.
 * @param {string} poblacion - "infantil" | "adolescente" | "adulto" | "adulto_mayor" | "cuidador"
 * @returns {string[]} IDs de tests
 */
export function getFormsPorPoblacion(poblacion) {
  return Object.entries(SCREENING_INDEX)
    .filter(
      ([, meta]) =>
        meta.poblacion_objetivo.includes("universal") ||
        meta.poblacion_objetivo.includes(poblacion)
    )
    .map(([id]) => id);
}

/**
 * Devuelve los IDs de SCREENING_FORMS que aplican para una edad dada.
 * Mapea edad → población y luego consulta el índice.
 * @param {number} edad - años cumplidos
 * @param {boolean} esCuidador - si el respondiente es cuidador (proxy)
 * @returns {string[]} IDs de tests
 */
export function getFormsPorEdad(edad, esCuidador = false) {
  let poblacion;
  if (esCuidador) poblacion = "cuidador";
  else if (edad <= 11) poblacion = "infantil";
  else if (edad <= 17) poblacion = "adolescente";
  else if (edad <= 64) poblacion = "adulto";
  else poblacion = "adulto_mayor";
  return getFormsPorPoblacion(poblacion);
}

/**
 * Sugiere screenings por constructos de interés (motivo de consulta).
 * Helper de alto nivel: cruza motivos con constructos.
 * @param {string[]} constructos_deseados - claves de CONSTRUCTOS
 * @param {number} edad - años cumplidos
 * @param {boolean} esCuidador
 * @returns {string[]} IDs de tests sugeridos
 */
export function sugerirPorConstructos(constructos_deseados, edad, esCuidador = false) {
  const formasPorEdad = new Set(getFormsPorEdad(edad, esCuidador));
  return constructos_deseados.flatMap((c) =>
    getFormsPorConstructo(c).filter((id) => formasPorEdad.has(id))
  );
}

/**
 * Devuelve el objeto CONSTRUCTOS + SCREENING_INDEX enriquecido para un ID.
 * Útil para tooltips o detalles.
 * @param {string} testId
 * @returns {{ form: object, constructo: object, index: object } | null}
 */
export function getScreeningMetadata(testId) {
  const form = SCREENING_FORMS[testId];
  const index = SCREENING_INDEX[testId];
  if (!form || !index) return null;
  const constructo = CONSTRUCTOS[index.constructo];
  return { form, constructo, index };
}

