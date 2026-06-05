/* ═══════════════════════════════════════════════════════════════════════
 * src/data/clinical.js — Constantes clinicas (extraidas de App.jsx)
 * ─────────────────────────────────────────────────────────────────────── */

export const OBS_TEMPLATES={apariencia_conducta:["El/la paciente se presenta orientado/a en persona, tiempo y espacio. Actitud colaboradora durante la sesión.","Contacto visual adecuado. Lenguaje espontáneo fluido y coherente.","Se observan signos de ansiedad/inquietud motora durante tareas de mayor demanda cognitiva.","Aspecto general acorde a edad y contexto. Higiene y vestimenta adecuadas."],atencion_concentracion:["Se evidencian dificultades en atención sostenida, con pérdida de foco ante estímulos distractores.","La velocidad de procesamiento se encuentra dentro de rangos esperados para su grupo normativo.","Presenta dificultades en tareas que requieren atención dividida y alternante."],memoria:["La curva de aprendizaje muestra un patrón ascendente con beneficio de la repetición.","Se evidencia disociación entre memoria libre (deficitaria) y con claves (preservada), sugiriendo dificultad en recuperación.","Adecuada consolidación a largo plazo con mínima pérdida en recuerdo diferido."],lenguaje:["Lenguaje expresivo fluido con adecuada articulación, sintaxis y prosodia.","Vocabulario acorde a nivel educativo. Comprensión de instrucciones preservada.","Dificultades en fluidez verbal fonológica con mejor rendimiento en semántica."],funciones_ejecutivas:["Se evidencian dificultades en flexibilidad cognitiva con tendencia a perseveración.","Adecuada capacidad de planificación y organización en tareas estructuradas.","Dificultades en control inhibitorio con respuestas impulsivas en tareas de interferencia."],habilidades_visoespaciales:["Adecuada capacidad de análisis y síntesis visoconstructiva.","Se evidencian dificultades en organización perceptual y planificación visoespacial."],impresion_diagnostica:["Los hallazgos sugieren un perfil compatible con {diagnóstico}, caracterizado por {características}.","El perfil neuropsicológico es consistente con las dificultades reportadas."],recomendaciones:["Intervención neuropsicológica enfocada en {áreas}.","Adaptaciones escolares/laborales: {adaptaciones}.","Valoración por {especialidad} para {motivo}.","Programa de estimulación cognitiva con énfasis en {dominios}."]};

export const CONDUCTAS={NiWiscDC:["Estilos de resolución: ensayo-error, fortuito, con estrategia","Nivel de planeación: ¿planea con cuidado o es impulsivo?","Colocación de cubos: adentro→afuera o viceversa (estilo analítico visual)","Coordinación motora y lateralidad: torpeza, temblores o firmeza","Consulta del modelo: si es constante → baja memoria visual o cautela","Preocupación por detalles: indica obsesión → impacto en velocidad","Perseverancia y tolerancia a la frustración: ¿se dan por vencidos?","Movimiento corporal: ¿rota su cuerpo o el diseño? → dificultades visoperceptuales","Reconocer el error: ¿no logra reconocer que su diseño difiere del modelo?"],NiWiscSem:["Beneficio de retroalimentación en ejemplo: flexibles vs rígidos o concretos","Extensión de respuestas: respuestas demasiado detalladas pueden sugerir obsesividad","Distinguir asociaciones sobreaprendidas en reactivos fáciles","Manejo de la frustración: ¿Dice constantemente 'no sé' o 'no se parecen'?","Las respuestas de defensividad/evitación se distinguen de dificultades de categorización","Autocorrecciones espontáneas: son válidas"],NiWiscRDD:["Estrategia de resolución: ¿agrupa números? ¿Desde el inicio o a medida que avanza?","Características del error: ¿traspone los números o los olvida por completo?","Inatención, discapacidad auditiva o ansiedad como factores","Interferencia por condiciones de aplicación: ruidos → no interpretable","Impulsividad: ¿repite muy rápido o antes de que termine la serie?","Autocorrecciones espontáneas: son válidas"],NiWiscConD:["Distinguir asociaciones sobreaprendidas en reactivos fáciles","Frustración: ¿Dice 'nada se parece'? Defensividad y evitación vs. dificultades","Reflexión previa: ¿estudia los dibujos antes? → estilo reflexivo","Verbalización durante la resolución del problema","Errores por interpretación social/cultural equivocada, no visoperceptuales","Autocorrecciones espontáneas: son válidas"],NiWiscCl:["Movimientos oculares: uso constante de clave → memoria deficiente o inseguridad","Si no reconoce el orden numérico → dificultad con conceptos numéricos","Si NO usa claves → buena retención y memoria visual/asociativa","Impulsividad: escribe símbolos rápido pero de forma descuidada","Planeación: si intenta escribir por símbolo (1, luego 2, etc.)","Ansiedad: manos tiemblan, aprieta lápiz, presiona duro","Perfeccionismo: tiempo excesivo perfeccionando → obsesividad","Inatención o fatiga a medida que avanza"],NiWiscVoc:["Pronunciación: ¿dificultades? ¿Inseguridad para expresarse?","Lenguaje no verbal: sustituye palabras con gestos","Problemas de recuperación: 'No sé' o 'lo tengo en la punta de la lengua' → baja rapidez léxica","Dificultades auditivas: inclinarse para oír, discriminación auditiva (confinar/confiar)","Exceso de palabras: compensación por inseguridad, obsesión o ineficiente expresión","Autocorrecciones espontáneas: son válidas"],NiWiscLN:["Estrategia de resolución: ¿agrupa o secuencia? ¿Desde el inicio o progresivo?","Error: ¿No puede reordenar aunque repita la secuencia literal?","Dificultades: inatención, discapacidad auditiva, ansiedad","Interferencia por condiciones: ruidos o distracciones → no interpretable","Tolerancia a la frustración: ¿persevera ante los errores?","Comprensión errónea: si trata como retención de dígitos → puntaje engañoso"],NiWiscMat:["Nivel de planeación: examina sistemáticamente o es impulsivo","Movimientos oculares: aproximación sistemática vs aleatoria","Frustración: ¿dice 'no sé' antes de observar? → indicador de frustración","Autocorrecciones espontáneas: son válidas"],NiWiscCom:["Respuestas muy extensas: ¿ocultar desconocimiento? ¿Obsesión?","Expresión verbal: anomias, circunstancialidad, tangencialidad, circunlocuciones","Inatención: ¿afecta desempeño en reactivos extensos?","Respuestas defensivas: indagar si sabe la respuesta ('No deberíamos usar cinturones')","Necesidad de motivación constante para dar otra respuesta","Error: ¿por habilidad verbal deficiente o juicio social pobre?","Reacción al pedir otra razón: amenazados/frustrados vs cómodos"],NiWiscBusSim:["Ansiedad: manos tiemblan, aprieta lápiz, presión dura al escribir","Atención: ¿se mantiene o disminuye? ¿Fatiga? Contar reactivos cada 30s","Revisión constante de cada fila → preocupación obsesiva por detalle","Impulsividad: identifica rápido pero de forma descuidada","Movimientos oculares: mirar constantemente → memoria deficiente; no volver al símbolo → buena retención"],NiWiscAri:["Representación mental: ¿puede representar mentalmente las cantidades?","Necesidad de repetición: ¿pide que repitan el problema?","Velocidad: respuesta rápida vs. demoras que sugieren cálculo inseguro","Ansiedad ante el tiempo: ¿se pone nervioso al saber que hay límite?","Uso de dedos o movimientos: ¿cuenta con los dedos?"],NiWisFigInc:["Impulsividad: ¿responde rápido sin examinar toda la imagen?","Exploración visual: ¿examina sistemáticamente o al azar?","Reconocimiento del detalle vs. la función: ¿identifica qué falta o qué hace?","Verbalización: ¿describe en voz alta lo que busca?"],NiWisPalCon:["Claves progresivas: ¿aprovecha las claves adicionales o se queda en la primera?","Vocabulario receptivo: ¿conoce las palabras en las claves?","Frustración ante las claves: ¿se rinde antes de escuchar todas?"],NiWisReg:["Atención sostenida: ¿mantiene ritmo constante?","Fatiga: ¿desacelera al final?","Impulsividad: ¿marca sin verificar?"],NiWisInf:["Tipo de conocimiento: ¿falla en información escolar vs cotidiana?","Estimulación ambiental: ¿las fallas sugieren poca exposición cultural?","Dificultades de recuperación: ¿sabe la respuesta pero no logra evocarla?","Motivación: ¿se rinde ante preguntas difíciles o intenta?","Verbalización: ¿respuestas escuetas o elaboradas?"],
AdWAISFI:["Tiempo de observación antes de responder","Exploración sistemática vs impulsiva de la imagen","¿Reconoce la función del objeto o sólo el detalle?","Verbalización espontánea mientras explora"],
AdWAISV:["Uso de circunloquios y gestos para compensar","Fluidez y acceso léxico (tip-of-the-tongue)","Articulación y prosodia","Respuestas concretas vs abstractas en ítems de alto nivel","Autocorrecciones espontáneas"],
AdSDWais:["Postura, agarre del lápiz, presión","Mira la clave todo el tiempo vs memoriza símbolos","Fatiga y disminución de velocidad al final","Impulsividad con errores","Perfeccionismo que enlentece"],
AdSemWais:["Respuestas concretas vs abstractas","Circunstancialidad, tangencialidad","Beneficia del ejemplo corregido","Tolerancia a la frustración con ítems difíciles"],
AdWAISCC:["Análisis y síntesis visual","Planeación inicial vs ensayo-error","Rotaciones del diseño o del propio cuerpo","Monitoreo del modelo","Persistencia tras error"],
AdWAISA:["Representación mental de cantidades","Pide repetir el problema","Velocidad de cálculo mental","Ansiedad ante el tiempo","Movimientos de dedos"],
AdMatr:["Exploración sistemática de opciones","Ensayo-error vs razonamiento analítico","Tolerancia a la frustración sin tiempo"],
AdDDir:["Agrupación espontánea de dígitos","Tipo de error: trasposición u olvido","Impulsividad en la respuesta","Interferencias ambientales"],
AdWAISI:["Recuperación léxica","Estimulación ambiental detectable en las fallas","Esfuerzo ante preguntas difíciles"],
AdWAISC:["Extensión de respuestas (obsesividad, defensividad)","Anomias, circunlocuciones","Juicio social vs habilidad verbal","Reacción al pedir otra razón"],
AdBusSim:["Ansiedad y tremor","Atención sostenida (comparar primeros 30s vs últimos)","Perfeccionismo vs impulsividad"],
ViBusSim:["Ansiedad y tremor","Atención sostenida (comparar primeros 30s vs últimos)","Perfeccionismo vs impulsividad"],
AdWAISL:["Estrategia de agrupación","Reorganización mental vs repetición literal","Frustración creciente"],
AdTMTA:["Planeación del recorrido visual","Errores y autocorrección","Fatiga / pérdida de ritmo"],
AdTMTB:["Alternancia cognitiva","Perseveraciones (sigue sólo números o sólo letras)","Flexibilidad tras error"],
NiFCROCop:["Estrategia de abordaje: global → detalle vs fragmentado","Uso del tiempo y de los colores","Organización espacial en la hoja","Copia fiel vs distorsiones perceptuales","Rotaciones/espejos","Impulsividad vs planeación"],
NiFCRORec:["Elementos recuperados espontáneamente","Organización mental del recuerdo","Intrusiones o confabulaciones","Beneficio del tiempo extra"],
AdFCRORec:["Fidelidad del recuerdo a 20-30 min","Orden de reconstrucción (estructura primero vs detalle)","Intrusiones","Ansiedad al recuperar"],
NiTMTA:["Planeación visual","Precisión de la línea","Autocorrección tras error"],
NiTMTB:["Alternancia número-letra sin perseverar","Tolerancia a la frustración","Velocidad vs precisión"],
SDMT:["Velocidad de procesamiento","Uso/memorización de la clave","Fatiga al final","Precisión vs velocidad"],
GBTotal:["Uso espontáneo de la clave semántica","Curva de aprendizaje","Intrusiones y perseveraciones","Beneficio del recuerdo con clave"],
CVLTTotal:["Estrategia de agrupación semántica","Intrusiones y falsos reconocimientos","Curva de aprendizaje","Interferencia proactiva/retroactiva"],
FluidP:["Organización por pistas fonéticas","Perseveraciones","Intrusiones de otras categorías","Decremento en los últimos 15s"],
FluidAnim:["Agrupación semántica (subcategorías)","Perseveraciones","Velocidad inicial vs final"],
FluidM:["Organización fonológica","Perseveraciones","Ritmo de producción"],
Denom48:["Acceso léxico (parafasias, circunloquios)","Beneficio de clave fonológica","Tiempo de respuesta"],
BNT:["Acceso léxico","Tipo de parafasia (semántica/fonológica)","Beneficio de claves"],
StroopAM:["Control inhibitorio","Costo de interferencia","Autocorrección"],
StroopAJ:["Control inhibitorio","Costo de interferencia","Velocidad y precisión"],
MMSE:["Orientación temporoespacial","Lenguaje y comprensión","Atención (resta o deletreo)","Memoria diferida","Praxia constructiva"],
NiFigHum:["Detalle y proporción","Omisiones de partes relevantes","Integración del esquema corporal","Indicadores proyectivos cualitativos"],
NiIntObj:["Análisis de partes-todo","Estrategia de integración","Perseveraciones"],
NiRecEmo:["Reconocimiento de emociones básicas","Confusiones prototípicas (miedo-sorpresa)","Verbalización espontánea"],
NiTestPC_R:["Velocidad y precisión","Ansiedad ante el tiempo","Impulsividad"],
NiENICDib:["Rastreo sistemático","Falsos positivos (impulsividad)","Fatiga"],
NiENIDen:["Acceso léxico","Parafasias","Beneficio de clave"],
NiFA:["Organización semántica","Perseveraciones","Ritmo"],
NiFM:["Organización fonológica","Perseveraciones"],
NiPrec:["Velocidad lectora","Errores de decodificación (sustituciones, omisiones)","Fluidez prosódica"],
NiLVS:["Comprensión inferencial","Velocidad","Uso de claves contextuales"],
NiCopTxt:["Calidad grafomotora","Precisión ortográfica","Uso del espacio"],
NiRecEscrita:["Organización textual","Errores ortográficos","Riqueza léxica"],
NiCalcEscrito:["Procedimiento algorítmico","Errores de valor posicional","Chequeo del resultado"],
NiENICMen:["Estrategia de cálculo","Representación mental","Velocidad"],
NiSt_Edades:["Control inhibitorio","Costo de interferencia según edad"],
NiENISInv:["Memoria de trabajo","Errores de secuencia","Impulsividad"],
EscKertesz:["Responde cuidador o paciente","Incongruencias con la observación clínica","Cambios conductuales reportados"],
EscQueja:["Conciencia de déficit","Rango temporal de la queja","Impacto funcional reportado"],
EscYesavage:["Verbalización afectiva","Congruencia con la observación","Ideación pasiva/activa"],
EscLawton:["AIVD con vs sin supervisión","Cambios recientes","Discordancia paciente-informante"],
EscSTAI:["Síntomas somáticos vs cognitivos","Rango temporal (estado/rasgo)"],
EscBeck:["Sesgo de deseabilidad","Síntomas somáticos vs cognitivos","Ideación suicida"],
EscASRS:["Congruencia con anamnesis","Cronicidad (infancia→adultez)"],
InstrConflICO:["Comprensión de la regla","Control de la interferencia","Autocorrección"],
RefranesICO:["Abstracción vs concretismo","Beneficio del ejemplo","Perseveraciones"],
GoNoGoICO:["Control inhibitorio","Falsos positivos","Fatiga al final"]};

export const GUIA_HC={desarrollo:"Condiciones de gestación hasta 2 semanas post-parto. Registrar: CPN (+/-), SFA, preeclampsia, IVU, RCIU, estrés materno, tipo de parto (vaginal, instrumentado, cesárea programada/urgencias/iterativa). Hitos del desarrollo en MESES; si no sabe → Demora/Normal. Peso normal ≥2500gr. Control esfínteres: diurno y nocturno; si diurno >3 años → demora.",antecedentes:"Patológicos: enfermedades agudas previas/actuales. Sensoriales: hipotonía, hipoacusia, limitaciones visuales, coordinación. Psiquiátricos: Dx desde psiquiatría (TEA, TDAH, Tourette, ansiedad, depresión). Farmacológicos: medicamentos ACTUALES con nombres correctos. Terapéuticos: procesos previos/actuales, continuidad, efectos. Familiares: núcleo + familia extensa hasta 3er grado, indicar línea materna/paterna.",familiar:"Vive con: nombres, edades, nivel educativo padres, cuidador principal, conductas parentales. ABC Niños: independencia en vestirse, comer, baño, cubiertos, cordones, bicicleta, dinero. Escolar: nombre colegio, rendimiento, público/privado, adaptación curricular, materias difíciles, pérdidas de año.",comportamiento:"Frecuencia, duración e intensidad de síntomas. Registrar: impulsividad, inquietud motora, relaciones sociales, tolerancia a la frustración, ansiedad (preocupación, temores, miedos), tristeza. Eventos vitales relevantes. Alteraciones en la percepción (texturas, olores, sonidos). Movimientos repetitivos (estereotipias, tics).",sueno:"NO poner 'normal'. Indicar: horas de sueño, facilidad para conciliar, continuo y reparador. Solo/acompañado (colecho). Respiración (ronca, AOS). Parasomnias (sonambulismo, somniloquios). Terrores nocturnos/pesadillas. Bruxismo, siestas, somnolencia diurna, ojeras.",alimentacion:"Patrón balanceado (todos los grupos). Selectividad por texturas/olores/formas. Come verduras/frutas. Dietas especiales (cetogénica, alergias). Patrón en exceso/defecto (hiperfagia, hipofagia, anorexia). Se demora comiendo, mastica o acumula, se distrae."};

export const REACTIVOS={
  /* ── DISEÑO CON CUBOS (WISC-IV) — 14 ítems ── */
  NiWiscDC:{type:"items",label:"Diseño con Cubos",items:[
    {n:1,cubos:2,tiempo:30,max:2,desc:"2 cubos — Diseño simple horizontal"},
    {n:2,cubos:2,tiempo:30,max:2,desc:"2 cubos — Diseño diagonal"},
    {n:3,cubos:2,tiempo:30,max:2,desc:"2 cubos — Diseño con rotación"},
    {n:4,cubos:4,tiempo:30,max:4,desc:"4 cubos — Diseño 2×2 básico"},
    {n:5,cubos:4,tiempo:45,max:5,desc:"4 cubos — Patrón diagonal"},
    {n:6,cubos:4,tiempo:45,max:5,desc:"4 cubos — Patrón asimétrico"},
    {n:7,cubos:4,tiempo:45,max:5,desc:"4 cubos — Rotación compleja"},
    {n:8,cubos:4,tiempo:60,max:5,desc:"4 cubos — Patrón avanzado"},
    {n:9,cubos:9,tiempo:120,max:7,desc:"9 cubos — Diseño 3×3 simple",bonus:true},
    {n:10,cubos:9,tiempo:120,max:7,desc:"9 cubos — Patrón intermedio",bonus:true},
    {n:11,cubos:9,tiempo:120,max:7,desc:"9 cubos — Patrón complejo",bonus:true},
    {n:12,cubos:9,tiempo:120,max:7,desc:"9 cubos — Diagonal avanzado",bonus:true},
    {n:13,cubos:9,tiempo:120,max:7,desc:"9 cubos — Patrón experto",bonus:true},
    {n:14,cubos:9,tiempo:120,max:7,desc:"9 cubos — Diseño más difícil",bonus:true},
  ]},
  /* ── DISEÑO CON CUBOS (WAIS-III) — 14 ítems ── */
  AdWAISCC:{type:"items",label:"Cubos WAIS-III",items:[
    {n:1,cubos:2,tiempo:30,max:2,desc:"Diseño simple 2 cubos"},
    {n:2,cubos:2,tiempo:30,max:2,desc:"Diseño diagonal 2 cubos"},
    {n:3,cubos:4,tiempo:30,max:2,desc:"Diseño 2×2 simple"},
    {n:4,cubos:4,tiempo:30,max:2,desc:"Diseño 2×2 diagonal"},
    {n:5,cubos:4,tiempo:60,max:6,desc:"Diseño con tiempo",bonus:true},
    {n:6,cubos:4,tiempo:60,max:6,desc:"Diseño intermedio",bonus:true},
    {n:7,cubos:4,tiempo:60,max:6,desc:"Diseño complejo",bonus:true},
    {n:8,cubos:9,tiempo:120,max:7,desc:"9 cubos — simple",bonus:true},
    {n:9,cubos:9,tiempo:120,max:7,desc:"9 cubos — intermedio",bonus:true},
    {n:10,cubos:9,tiempo:120,max:7,desc:"9 cubos — complejo",bonus:true},
    {n:11,cubos:9,tiempo:120,max:7,desc:"9 cubos — avanzado",bonus:true},
    {n:12,cubos:9,tiempo:120,max:7,desc:"9 cubos — experto",bonus:true},
    {n:13,cubos:9,tiempo:120,max:7,desc:"9 cubos — difícil",bonus:true},
    {n:14,cubos:9,tiempo:120,max:7,desc:"9 cubos — máximo",bonus:true},
  ]},
  /* ── RETENCIÓN DE DÍGITOS (WISC-IV) ── */
  NiWiscRDD:{type:"digits",label:"Retención de Dígitos",sections:[{name:"Dígitos Directos",maxItems:8,trials:2,sequences:[{len:2,a:"2-9",b:"4-6"},{len:3,a:"3-8-6",b:"6-1-2"},{len:4,a:"3-4-1-7",b:"6-1-5-8"},{len:5,a:"5-2-1-8-6",b:"8-4-2-3-9"},{len:6,a:"3-8-9-1-7-4",b:"7-9-6-4-8-3"},{len:7,a:"5-1-7-4-2-3-8",b:"9-8-5-2-1-6-3"},{len:8,a:"1-8-4-5-9-7-6-3",b:"2-9-7-6-3-1-5-4"},{len:9,a:"5-3-8-7-1-2-4-6-9",b:"4-2-6-9-1-7-8-3-5"}]},{name:"Dígitos Inversos",maxItems:8,trials:2,sequences:[{len:2,a:"2-1",b:"1-3"},{len:2,a:"3-5",b:"6-4"},{len:3,a:"2-5-9",b:"5-7-4"},{len:4,a:"8-4-9-3",b:"7-2-9-6"},{len:5,a:"4-1-3-5-7",b:"9-7-8-5-2"},{len:6,a:"1-6-5-2-9-8",b:"3-6-7-1-9-4"},{len:7,a:"8-5-9-2-3-4-6",b:"4-5-7-9-2-8-1"},{len:8,a:"6-9-1-7-3-2-5-8",b:"3-1-7-9-5-4-8-2"}]}]},
  /* ── DÍGITOS WAIS-III ── */
  AdDDir:{type:"digits",label:"Dígitos WAIS-III",sections:[{name:"Dígitos Directos",maxItems:8,trials:2,sequences:[{len:2,a:"1-7",b:"6-3"},{len:3,a:"5-8-2",b:"6-9-4"},{len:4,a:"6-4-3-9",b:"7-2-8-6"},{len:5,a:"4-2-7-3-1",b:"7-5-8-3-6"},{len:6,a:"6-1-9-4-7-3",b:"3-9-2-4-8-7"},{len:7,a:"5-9-1-7-4-2-8",b:"4-1-7-9-3-8-6"},{len:8,a:"5-8-1-9-2-6-4-7",b:"3-8-2-9-5-1-7-4"},{len:9,a:"2-7-5-8-6-2-5-8-4",b:"7-1-3-9-4-2-5-6-8"}]},{name:"Dígitos Inversos",maxItems:8,trials:2,sequences:[{len:2,a:"2-4",b:"5-7"},{len:3,a:"6-2-9",b:"4-1-5"},{len:4,a:"3-2-7-9",b:"4-9-6-8"},{len:5,a:"1-5-2-8-6",b:"6-1-8-4-3"},{len:6,a:"5-3-9-4-1-8",b:"7-2-4-8-5-6"},{len:7,a:"8-1-2-9-3-6-5",b:"4-7-3-9-1-2-8"},{len:8,a:"9-4-3-7-6-2-5-8",b:"7-2-8-1-9-6-5-3"}]}]},
  /* ── SEMEJANZAS (WISC-IV) — 23 pares de conceptos
   * Scoring oficial: ítems 1-2 = 0/1 (sin 2 puntos), ítems 3-23 = 0/1/2.
   * Los pares siguen el orden de aplicación del protocolo WISC-IV.
   * El `scoring` global se mantiene como [0,1,2] para que la UI genere
   * los botones de captura; los ítems 1-2 reciben puntaje máximo 1. */
  NiWiscSem:{type:"scored_items",label:"Semejanzas",scoring:[0,1,2],maxPerItem:{1:1,2:1},items:[
    {n:1,pair:"Leche — Agua"},
    {n:2,pair:"Esfero — Lápiz"},
    {n:3,pair:"Gato — Ratón"},
    {n:4,pair:"Manzana — Banano"},
    {n:5,pair:"Camisa — Zapato"},
    {n:6,pair:"Invierno — Verano"},
    {n:7,pair:"Mariposa — Abeja"},
    {n:8,pair:"Madera — Ladrillos"},
    {n:9,pair:"Enojo — Alegría"},
    {n:10,pair:"Poeta — Pintor"},
    {n:11,pair:"Pintura — Estatua"},
    {n:12,pair:"Montaña — Lago"},
    {n:13,pair:"Hielo — Vapor"},
    {n:14,pair:"Codo — Rodilla"},
    {n:15,pair:"Mueca — Sonrisa"},
    {n:16,pair:"Inundación — Sequía"},
    {n:17,pair:"Primero — Último"},
    {n:18,pair:"Hule (Caucho) — Papel"},
    {n:19,pair:"Permiso — Prohibición"},
    {n:20,pair:"Sal — Agua"},
    {n:21,pair:"Venganza — Perdón"},
    {n:22,pair:"Realidad — Fantasía"},
    {n:23,pair:"Espacio — Tiempo"}
  ]},
  /* ── VOCABULARIO (WISC-IV) — 32 palabras (4 ilustradas + 28 verbales)
   * Ítems 1-4: palabras con imagen (Coche, Flor, Tren, Cubeta)
   * Ítems 5-32: palabras orales en orden de aplicación WISC-IV.
   * Eliminado "Rivalidad" duplicado (aparecía en n:14 y n:26). */
  NiWiscVoc:{type:"scored_items",label:"Vocabulario",scoring:[0,1,2],maxPerItem:{1:1,2:1,3:1,4:1},items:[
    {n:1,word:"Coche",ilustrado:true},
    {n:2,word:"Flor",ilustrado:true},
    {n:3,word:"Tren",ilustrado:true},
    {n:4,word:"Cubeta",ilustrado:true},
    {n:5,word:"Reloj"},
    {n:6,word:"Sombrilla"},
    {n:7,word:"Ladrón"},
    {n:8,word:"Vaca"},
    {n:9,word:"Sombrero"},
    {n:10,word:"Valiente"},
    {n:11,word:"Obedecer"},
    {n:12,word:"Bicicleta"},
    {n:13,word:"Antiguo"},
    {n:14,word:"Abecedario"},
    {n:15,word:"Remedar"},
    {n:16,word:"Fábula"},
    {n:17,word:"Emigrar"},
    {n:18,word:"Isla"},
    {n:19,word:"Absorber"},
    {n:20,word:"Salir"},
    {n:21,word:"Transparente"},
    {n:22,word:"Molestia"},
    {n:23,word:"Raramente"},
    {n:24,word:"Preciso"},
    {n:25,word:"Obligar"},
    {n:26,word:"Rivalidad"},
    {n:27,word:"Disparate"},
    {n:28,word:"Previsión"},
    {n:29,word:"Aflicción"},
    {n:30,word:"Arduo"},
    {n:31,word:"Unánime"},
    {n:32,word:"Dilatorio"},
    {n:33,word:"Enmienda"},
    {n:34,word:"Inminente"},
    {n:35,word:"Aberración"},
    {n:36,word:"Locuaz"}
  ]},
  /* ── COMPRENSIÓN (WISC-IV) — 18 preguntas, 0-1-2
   * Preguntas del protocolo WISC-IV en orden de aplicación. Las
   * primeras 8 son de razonamiento práctico (situaciones cotidianas);
   * las 9-18 son de razonamiento social abstracto (leyes, normas,
   * conceptos cívicos). Se omite el contenido de las respuestas
   * modelo (verificadas en baremos) — sólo se captura puntaje bruto. */
  NiWiscCom:{type:"scored_items",label:"Comprensión",scoring:[0,1,2],items:[
    {n:1,q:"¿Por qué la gente se cepilla los dientes?"},
    {n:2,q:"¿Por qué las personas deben comer verduras?"},
    {n:3,q:"¿Por qué los carros tienen cinturones en los asientos?"},
    {n:4,q:"¿Por qué es importante que los policías usen uniforme?"},
    {n:5,q:"¿Qué se supone que deberías hacer si te encuentras la cartera de una persona en una tienda?"},
    {n:6,q:"¿Qué deberías hacer si ves que está saliendo mucho humo por la ventana de la casa de tu vecino?"},
    {n:7,q:"¿Qué hacer si un niño más pequeño empieza a pelear contigo?"},
    {n:8,q:"¿Cuáles son algunas ventajas de tener bibliotecas públicas?"},
    {n:9,q:"¿Por qué es importante que el gobierno inspeccione la carne antes de venderla?"},
    {n:10,q:"¿Cuáles son las ventajas de hacer ejercicio y mantenerse activo?"},
    {n:11,q:"¿Por qué es importante disculparse cuando sabes que heriste a alguien?"},
    {n:12,q:"¿Dime algunas razones por las que debes apagar las luces cuando nadie las está usando?"},
    {n:13,q:"¿Por qué es importante dar derechos de autor a escritores y patentes a inventores?"},
    {n:14,q:"¿Por qué se debe cumplir una promesa?"},
    {n:15,q:"¿Por qué los médicos deben tomar clases adicionales después de haber practicado?"},
    {n:16,q:"¿Dime ventajas de leer noticias en un periódico en lugar de verlas en TV?"},
    {n:17,q:"¿Por qué es importante tener libertad de expresión en una democracia?"},
    {n:18,q:"¿Por qué es importante impedir que solo una compañía sea propietaria de todos los periódicos y estaciones?"},
    {n:19,q:"¿Por qué ponemos estampillas en las cartas?"},
    {n:20,q:"¿Por qué los medios de comunicación pueden ser una amenaza para las dictaduras?"},
    {n:21,q:"¿Cuáles son algunos problemas asociados con los cambios rápidos en ciencia y tecnología?"}
  ]},
  /* ── MATRICES (WISC-IV) — 0-1 ── */
  NiWiscMat:{type:"scored_items",label:"Matrices",scoring:[0,1],items:[
    {n:1,q:"Matriz 1 — completar en cuadernillo (5 opciones)"},
    {n:2,q:"Matriz 2 — completar en cuadernillo (5 opciones)"},
    {n:3,q:"Matriz 3 — completar en cuadernillo (5 opciones)"},
    {n:4,q:"Matriz 4 — completar en cuadernillo (5 opciones)"},
    {n:5,q:"Matriz 5 — completar en cuadernillo (5 opciones)"},
    {n:6,q:"Matriz 6 — completar en cuadernillo (5 opciones)"},
    {n:7,q:"Matriz 7 — completar en cuadernillo (5 opciones)"},
    {n:8,q:"Matriz 8 — completar en cuadernillo (5 opciones)"},
    {n:9,q:"Matriz 9 — completar en cuadernillo (5 opciones)"},
    {n:10,q:"Matriz 10 — completar en cuadernillo (5 opciones)"},
    {n:11,q:"Matriz 11 — completar en cuadernillo (5 opciones)"},
    {n:12,q:"Matriz 12 — completar en cuadernillo (5 opciones)"},
    {n:13,q:"Matriz 13 — completar en cuadernillo (5 opciones)"},
    {n:14,q:"Matriz 14 — completar en cuadernillo (5 opciones)"},
    {n:15,q:"Matriz 15 — completar en cuadernillo (5 opciones)"},
    {n:16,q:"Matriz 16 — completar en cuadernillo (5 opciones)"},
    {n:17,q:"Matriz 17 — completar en cuadernillo (5 opciones)"},
    {n:18,q:"Matriz 18 — completar en cuadernillo (5 opciones)"},
    {n:19,q:"Matriz 19 — completar en cuadernillo (5 opciones)"},
    {n:20,q:"Matriz 20 — completar en cuadernillo (5 opciones)"},
    {n:21,q:"Matriz 21 — completar en cuadernillo (5 opciones)"},
    {n:22,q:"Matriz 22 — completar en cuadernillo (5 opciones)"},
    {n:23,q:"Matriz 23 — completar en cuadernillo (5 opciones)"},
    {n:24,q:"Matriz 24 — completar en cuadernillo (5 opciones)"},
    {n:25,q:"Matriz 25 — completar en cuadernillo (5 opciones)"},
    {n:26,q:"Matriz 26 — completar en cuadernillo (5 opciones)"},
    {n:27,q:"Matriz 27 — completar en cuadernillo (5 opciones)"},
    {n:28,q:"Matriz 28 — completar en cuadernillo (5 opciones)"},
    {n:29,q:"Matriz 29 — completar en cuadernillo (5 opciones)"},
    {n:30,q:"Matriz 30 — completar en cuadernillo (5 opciones)"},
    {n:31,q:"Matriz 31 — completar en cuadernillo (5 opciones)"},
    {n:32,q:"Matriz 32 — completar en cuadernillo (5 opciones)"},
    {n:33,q:"Matriz 33 — completar en cuadernillo (5 opciones)"},
    {n:34,q:"Matriz 34 — completar en cuadernillo (5 opciones)"},
    {n:35,q:"Matriz 35 — completar en cuadernillo (5 opciones)"}
  ]},
  /* ── CONCEPTOS CON DIBUJOS — 0-1 ── */
  NiWiscConD:{type:"scored_items",label:"Conceptos con Dibujos",scoring:[0,1],items:[
    {n:1,q:"Lamina 1 — agrupar por categoria (cuadernillo)"},
    {n:2,q:"Lamina 2 — agrupar por categoria (cuadernillo)"},
    {n:3,q:"Lamina 3 — agrupar por categoria (cuadernillo)"},
    {n:4,q:"Lamina 4 — agrupar por categoria (cuadernillo)"},
    {n:5,q:"Lamina 5 — agrupar por categoria (cuadernillo)"},
    {n:6,q:"Lamina 6 — agrupar por categoria (cuadernillo)"},
    {n:7,q:"Lamina 7 — agrupar por categoria (cuadernillo)"},
    {n:8,q:"Lamina 8 — agrupar por categoria (cuadernillo)"},
    {n:9,q:"Lamina 9 — agrupar por categoria (cuadernillo)"},
    {n:10,q:"Lamina 10 — agrupar por categoria (cuadernillo)"},
    {n:11,q:"Lamina 11 — agrupar por categoria (cuadernillo)"},
    {n:12,q:"Lamina 12 — agrupar por categoria (cuadernillo)"},
    {n:13,q:"Lamina 13 — agrupar por categoria (cuadernillo)"},
    {n:14,q:"Lamina 14 — agrupar por categoria (cuadernillo)"},
    {n:15,q:"Lamina 15 — agrupar por categoria (cuadernillo)"},
    {n:16,q:"Lamina 16 — agrupar por categoria (cuadernillo)"},
    {n:17,q:"Lamina 17 — agrupar por categoria (cuadernillo)"},
    {n:18,q:"Lamina 18 — agrupar por categoria (cuadernillo)"},
    {n:19,q:"Lamina 19 — agrupar por categoria (cuadernillo)"},
    {n:20,q:"Lamina 20 — agrupar por categoria (cuadernillo)"},
    {n:21,q:"Lamina 21 — agrupar por categoria (cuadernillo)"},
    {n:22,q:"Lamina 22 — agrupar por categoria (cuadernillo)"},
    {n:23,q:"Lamina 23 — agrupar por categoria (cuadernillo)"},
    {n:24,q:"Lamina 24 — agrupar por categoria (cuadernillo)"},
    {n:25,q:"Lamina 25 — agrupar por categoria (cuadernillo)"},
    {n:26,q:"Lamina 26 — agrupar por categoria (cuadernillo)"},
    {n:27,q:"Lamina 27 — agrupar por categoria (cuadernillo)"},
    {n:28,q:"Lamina 28 — agrupar por categoria (cuadernillo)"}
  ]},
  /* ── INFORMACIÓN (WISC-IV) — 0-1 ── */
  NiWisInf:{type:"scored_items",label:"Información",scoring:[0,1],items:[
    {n:1,q:"¿Enséñame tu pie?"},
    {n:2,q:"¿[Señalando nariz] ¿Cómo se llama esto??"},
    {n:3,q:"¿Nombra algo que comas?"},
    {n:4,q:"¿Cuántas orejas tienes?"},
    {n:5,q:"¿Cuántos años tienes?"},
    {n:6,q:"¿Cuántas patas tiene un perro?"},
    {n:7,q:"¿Qué día le sigue al jueves?"},
    {n:8,q:"¿Nombra dos tipos de monedas?"},
    {n:9,q:"¿Qué mes sigue después de marzo?"},
    {n:10,q:"¿Qué se debe hacer para que el agua hierva?"},
    {n:11,q:"¿Cuántos días hay en una semana?"},
    {n:12,q:"¿Cuántos días hay en un año?"},
    {n:13,q:"¿Quién fue Cristóbal Colón?"},
    {n:14,q:"¿Cuáles son las cuatro estaciones del año?"},
    {n:15,q:"¿Cuántas cosas forman una docena?"},
    {n:16,q:"¿Qué hace el estómago?"},
    {n:17,q:"¿Cuál mes tiene un día adicional cada cuatro años?"},
    {n:18,q:"¿Qué es un fósil?"},
    {n:19,q:"¿Qué es la capa de ozono?"},
    {n:20,q:"¿Cómo regresa el oxígeno al aire?"},
    {n:21,q:"¿Qué son los jeroglíficos?"},
    {n:22,q:"¿Cuál país tiene la población más grande?"},
    {n:23,q:"¿Cuál es la capital de Grecia?"},
    {n:24,q:"¿Por qué se oxida el hierro?"},
    {n:25,q:"¿Qué hace que las hojas sean verdes?"},
    {n:26,q:"¿Quién fue Charles Darwin?"},
    {n:27,q:"¿De qué están hechos los diamantes?"},
    {n:28,q:"¿Quién fue Confucio?"},
    {n:29,q:"¿Qué es el solsticio de invierno?"},
    {n:30,q:"¿Qué es un barómetro?"},
    {n:31,q:"¿Qué es la fisión nuclear?"},
    {n:32,q:"¿Qué distancia hay entre Cd. de México y Nueva York?"},
    {n:33,q:"¿De dónde se obtiene la resina natural?"}
  ]},
  /* ── ARITMÉTICA (WISC-IV) — 0-1 con tiempo ── */
  NiWiscAri:{type:"scored_items",label:"Aritmética",scoring:[0,1],items:[
    {n:1,q:"Cuenta estos pájaros con tu dedo"},
    {n:2,q:"Cuenta estos pollitos con tu dedo"},
    {n:3,q:"Cuenta estos árboles con tu dedo"},
    {n:4,q:"¿Cuántas mariposas y grillos hay en total?"},
    {n:5,q:"¿Cuántas nueces quedarían si cada ardilla se come una?"},
    {n:6,q:"Roberto tiene 5 libros. Pierde 1. ¿Cuántos le quedan?"},
    {n:7,q:"¿Cuánto son 2 crayolas más 3 crayolas?"},
    {n:8,q:"José tiene 5 galletas. Le da una a Samuel y otra a Jimena. ¿Cuántas le quedan?"},
    {n:9,q:"Juan tenía 4 monedas y su mamá le dio 2 más. ¿Cuántas tiene en total?"},
    {n:10,q:"Si corto una manzana por la mitad ¿Cuántos pedazos tendré?"},
    {n:11,q:"Si tienes 10 caramelos y te comes 3, ¿cuántos te quedan?"},
    {n:12,q:"Si tienes 3 lápices en cada mano ¿Cuántos lápices tienes en total?"},
    {n:13,q:"Tres bicicletas llegan a un parque donde ya hay 12. ¿Cuántas hay ahora?"},
    {n:14,q:"Marcos tenía 8 pelotas y compró 6 más. ¿Cuántas tiene en total?"},
    {n:15,q:"Francisco ganó 10 calcomanías el lunes y 15 el martes. ¿Cuántas ganó en total?"},
    {n:16,q:"En un campo hay 3 vacas. Llegan 4 más y se van 2. ¿Cuántas quedan?"},
    {n:17,q:"Catalina tenía 12 globos y vendió 5. ¿Cuántos le quedaron?"},
    {n:18,q:"Juana compró 4 manzanas en una tienda y 2 en otra. Su mamá le dio 3 más. ¿Cuántas tiene?"},
    {n:19,q:"Si compras 2 plumas a 40 pesos cada una, ¿cuánto cambio te dan si pagas con 100?"},
    {n:20,q:"Tomás anotó 17 puntos en un juego y 15 en otro. ¿Cuántos anotó en total?"},
    {n:21,q:"Una feria tiene 8 concursos. Cada uno da 3 premios. ¿Cuántos premios en total?"},
    {n:22,q:"En una clase de karate se inscribieron 30 estudiantes. Se van 11. ¿Cuántos quedan?"},
    {n:23,q:"Rosa compró 3 libros a 2 pesos cada uno y un juguete de 7. ¿Cambio de 20 pesos?"},
    {n:24,q:"Laura mira 8 pájaros, 4 vuelan y llegan 2. ¿Cuántos observa ahora?"},
    {n:25,q:"Juan tiene el doble de dinero que Sergio. Juan tiene 17 pesos. ¿Cuánto tiene Sergio?"},
    {n:26,q:"Una escuela tiene 25 alumnos por salón y 500 en total. ¿Cuántos salones?"},
    {n:27,q:"Susana tenía 30 pesos y se gastó la mitad. Revistas cuestan 5 cada una. ¿Cuántas puede comprar?"},
    {n:28,q:"Una familia manejó 3 horas, descansó, y manejó 2 más. Total 300 km. ¿Velocidad promedio?"},
    {n:29,q:"Beatriz compró una carpeta usada por 2/3 del precio nuevo. Pagó 20. ¿Cuánto costaba nueva?"},
    {n:30,q:"La temperatura subió 12° entre las 4 y 8am, y 9° más entre 8 y 11am. ¿Promedio por hora?"},
    {n:31,q:"Un juego de 40 pesos se rebaja 15%. ¿Cuál es el precio en oferta?"},
    {n:32,q:"6 personas lavan 40 autos en 4 días. ¿Cuántas necesitan para lavar 40 en medio día?"},
    {n:33,q:"Vuelo de Carlos dura 2h, sale a las 3pm. Jaime vive a 150km, maneja a 60km/h. ¿A qué hora sale Jaime para llegar 30min antes?"},
    {n:34,q:"Diego sale 1h antes que Victoria. Diego a 40km/h, Victoria a 60km/h. ¿Qué tan adelantada estará Victoria 5h después de que Diego sale?"}
  ]},
  /* ── FIGURAS INCOMPLETAS (WISC-IV) — 0-1 ── */
  NiWisFigInc:{type:"scored_items",label:"Figuras Incompletas",scoring:[0,1],items:[
    {n:1,q:"Zorro — ¿qué parte falta?"},
    {n:2,q:"Chaqueta — ¿qué parte falta?"},
    {n:3,q:"Gato — ¿qué parte falta?"},
    {n:4,q:"Espejo — ¿qué parte falta?"},
    {n:5,q:"Hoja — ¿qué parte falta?"},
    {n:6,q:"Campana — ¿qué parte falta?"},
    {n:7,q:"Mano — ¿qué parte falta?"},
    {n:8,q:"Salto — ¿qué parte falta?"},
    {n:9,q:"Escalera — ¿qué parte falta?"},
    {n:10,q:"Cara de Mujer — ¿qué parte falta?"},
    {n:11,q:"Cinturón — ¿qué parte falta?"},
    {n:12,q:"Hombre — ¿qué parte falta?"},
    {n:13,q:"Mueble — ¿qué parte falta?"},
    {n:14,q:"Puerta — ¿qué parte falta?"},
    {n:15,q:"Tijeras — ¿qué parte falta?"},
    {n:16,q:"Reloj — ¿qué parte falta?"},
    {n:17,q:"Foco — ¿qué parte falta?"},
    {n:18,q:"Silbato — ¿qué parte falta?"},
    {n:19,q:"Bicicletas — ¿qué parte falta?"},
    {n:20,q:"Cerdo — ¿qué parte falta?"},
    {n:21,q:"Dado — ¿qué parte falta?"},
    {n:22,q:"Pelota — ¿qué parte falta?"},
    {n:23,q:"Banda — ¿qué parte falta?"},
    {n:24,q:"Bicicleta — ¿qué parte falta?"},
    {n:25,q:"Naranja — ¿qué parte falta?"},
    {n:26,q:"Perfil — ¿qué parte falta?"},
    {n:27,q:"Árbol — ¿qué parte falta?"},
    {n:28,q:"Puente — ¿qué parte falta?"},
    {n:29,q:"Sombrilla — ¿qué parte falta?"},
    {n:30,q:"Supermercado — ¿qué parte falta?"},
    {n:31,q:"Tina — ¿qué parte falta?"},
    {n:32,q:"Enrejado — ¿qué parte falta?"},
    {n:33,q:"Termómetro — ¿qué parte falta?"},
    {n:34,q:"Pez — ¿qué parte falta?"},
    {n:35,q:"Casa — ¿qué parte falta?"},
    {n:36,q:"Agua — ¿qué parte falta?"},
    {n:37,q:"Familia — ¿qué parte falta?"},
    {n:38,q:"Zapato — ¿qué parte falta?"}
  ]},
  /* ── PALABRAS EN CONTEXTO (WISC-IV) — 0-1 ── */
  NiWisPalCon:{type:"scored_items",label:"Palabras en Contexto",scoring:[0,1],items:[
    {n:1,q:"Sirve para secarte después de que te bañas"},
    {n:2,q:"Sirve para oler cosas"},
    {n:3,q:"Es un satélite natural"},
    {n:4,q:"Este es un animal con trompa y grandes orejas"},
    {n:5,q:"Se pone en la cabeza para protegerse del frío o del sol"},
    {n:6,q:"Tiene una perilla o picaporte y la gente puede abrirla para pasar"},
    {n:7,q:"Mezcla de tierra con la lluvia"},
    {n:8,q:"Tiene cosas del pasado o antiguas"},
    {n:9,q:"Líquido de colores"},
    {n:10,q:"Esta es una habitación donde la gente duerme"},
    {n:11,q:"Proviene de los charcos/estanques en la costa del mar"},
    {n:12,q:"Nacen al pie de las montañas"},
    {n:13,q:"Son los responsables de que tu cuerpo funcione"},
    {n:14,q:"Conduce a nuevos descubrimientos"},
    {n:15,q:"Facilita la convivencia de personas diferentes"},
    {n:16,q:"Son normas que debe respetar el ciudadano"},
    {n:17,q:"La gente lo hace para arreglar edificios viejos"},
    {n:18,q:"No se detiene"},
    {n:19,q:"Es un permiso oficial"},
    {n:20,q:"Lo festejas"},
    {n:21,q:"Nunca se ha visto"},
    {n:22,q:"Este es un lugar"},
    {n:23,q:"Puede ser un río"},
    {n:24,q:"Ha pasado"}
  ]},
  /* ── CLAVES — marcado automático por tiempo ── */
  NiWiscCl:{type:"timed_count",label:"Claves",maxTime:120,instruction:"Contar los símbolos correctos copiados en 120 segundos"},
  NiWiscBusSim:{type:"timed_count",label:"Búsqueda de Símbolos",maxTime:120,instruction:"Correctas - Incorrectas en 120 segundos"},
  /* ── LETRAS Y NÚMEROS (WISC-IV) — 3 trials por nivel, 10 niveles ──
   * Estructura: 10 niveles de dificultad creciente, 3 trials por nivel.
   * Cada trial es una secuencia mixta de letras (en voz) y números que
   * el niño debe repetir reordenando mentalmente (letras en orden
   * alfabético ascendente, números en orden numérico ascendente).
   * Tiempo sugerido: 90s para WISC-IV niños 6-16 años. */
  NiWiscLN:{type:"items",label:"Letras y Números",maxTime:90,items:[
    {n:1,secuencia:"L-1",desc:"Números ascendente, letras A-Z · modelo 1-L",trials:["L-1","L-1","L-1"]},
    {n:2,secuencia:"N-2",desc:"Números ascendente, letras A-Z · modelo 2-N",trials:["N-2","N-2","N-2"]},
    {n:3,secuencia:"B-5",desc:"Números ascendente, letras A-Z · modelo 5-B",trials:["B-5","B-5","B-5"]},
    {n:4,secuencia:"L-N-1",desc:"Números ascendente, letras A-Z · modelo 1-L-N",trials:["L-N-1","L-N-1","L-N-1"]},
    {n:5,secuencia:"L-N-2",desc:"Números ascendente, letras A-Z · modelo 2-L-N",trials:["L-N-2","L-N-2","L-N-2"]},
    {n:6,secuencia:"L-N-3",desc:"Números ascendente, letras A-Z · modelo 3-L-N",trials:["L-N-3","L-N-3","L-N-3"]},
    {n:7,secuencia:"F-R-3",desc:"Números ascendente, letras A-Z · modelo 3-F-R",trials:["F-R-3","F-R-3","F-R-3"]},
    {n:8,secuencia:"A-4-7",desc:"Números ascendente, letras A-Z · modelo 4-7-A",trials:["A-4-7","A-4-7","A-4-7"]},
    {n:9,secuencia:"M-S-3-4",desc:"Números ascendente, letras A-Z · modelo 3-4-M-S",trials:["M-S-3-4","M-S-3-4","M-S-3-4"]},
    {n:10,secuencia:"F-O-6-3",desc:"Números ascendente, letras A-Z · modelo 3-6-F-O",trials:["F-O-6-3","F-O-6-3","F-O-6-3"]}
  ]},
  /* ── REGISTRO (WISC-IV) — Registro de Símbolos versión
   * cronometrada de niños (no Claves). Se aplica a partir de los 7 años
   * con tiempo fijo de 45s, donde el niño copia símbolos
   * predibujados debajo de los números correspondientes. ── */
  NiWisReg:{type:"items",label:"Registro de Símbolos",maxTime:45,items:[
    {n:1,desc:"Serie 1 (fila 1)"},{n:2,desc:"Serie 2 (fila 2)"},{n:3,desc:"Serie 3 (fila 3)"},
    {n:4,desc:"Serie 4 (fila 4)"},{n:5,desc:"Serie 5 (fila 5)"},
  ]},
  /* ── FCRO (Rey-Osterrieth) — 18 elementos, 0/0.5/1/2 ── */
  NiFCROCop:{type:"fcro",label:"Figura Compleja de Rey — Copia",elements:[
    "Cruz exterior","Rectángulo grande","Cruz diagonal","Línea media horizontal",
    "Línea media vertical","Pequeño rectángulo interno","Segmento pequeño sobre rect.",
    "Cuatro líneas paralelas","Triángulo superior derecho","Línea pequeña dentro del rect.",
    "Círculo con 3 puntos","Cinco líneas paralelas cruzando rect.","Triángulo sobre lado derecho",
    "Rombo junto al rectángulo","Segmento horizontal dentro de triángulo","Segmento horizontal dentro de rect.",
    "Cruz inferior derecha","Cuadrado inferior izquierdo"
  ]},
  NiFCRORec:{type:"fcro",label:"Figura Compleja de Rey — Recobro",elements:[
    "Cruz exterior","Rectángulo grande","Cruz diagonal","Línea media horizontal",
    "Línea media vertical","Pequeño rectángulo interno","Segmento pequeño sobre rect.",
    "Cuatro líneas paralelas","Triángulo superior derecho","Línea pequeña dentro del rect.",
    "Círculo con 3 puntos","Cinco líneas paralelas cruzando rect.","Triángulo sobre lado derecho",
    "Rombo junto al rectángulo","Segmento horizontal dentro de triángulo","Segmento horizontal dentro de rect.",
    "Cruz inferior derecha","Cuadrado inferior izquierdo"
  ]},
  AdFCRORec:{type:"fcro",label:"FCRO Recobro Adultos",elements:[
    "Cruz exterior","Rectángulo grande","Cruz diagonal","Línea media horizontal",
    "Línea media vertical","Pequeño rectángulo interno","Segmento pequeño sobre rect.",
    "Cuatro líneas paralelas","Triángulo superior derecho","Línea pequeña dentro del rect.",
    "Círculo con 3 puntos","Cinco líneas paralelas cruzando rect.","Triángulo sobre lado derecho",
    "Rombo junto al rectángulo","Segmento horizontal dentro de triángulo","Segmento horizontal dentro de rect.",
    "Cruz inferior derecha","Cuadrado inferior izquierdo"
  ]},
  /* ── GROBER & BUSCHKE (RL/RI-16) — 16 palabras con clave semántica ── */
  GBTotal:{type:"memory_curve",label:"Grober & Buschke (RL/RI-16)",words:["Róbalo","Chaleco","Dominó","Orquídea","Dentista","Cereza","Cobre","Arpa","Cuervo","Palmera","Boxeo","Apio","Cumbia","Sarampión","Mecedora","Geografía"],
    categories:["Pescado","Prenda de vestir","Juego","Flor","Profesión","Fruta","Metal","Instrumento musical","Ave","Árbol","Deporte","Verdura","Baile","Enfermedad","Mueble","Asignatura"],
    trials:[
      {id:"RL1",name:"Recuerdo Libre 1",type:"free"},
      {id:"RC1",name:"Recuerdo con Clave 1",type:"cued"},
      {id:"RL2",name:"Recuerdo Libre 2",type:"free"},
      {id:"RC2",name:"Recuerdo con Clave 2",type:"cued"},
      {id:"RL3",name:"Recuerdo Libre 3",type:"free"},
      {id:"RC3",name:"Recuerdo con Clave 3",type:"cued"},
      {id:"RLD",name:"Recuerdo Libre Diferido",type:"free"},
      {id:"RCD",name:"Recuerdo con Clave Diferido",type:"cued"},
      {id:"Reconocimiento",name:"Reconocimiento",type:"recognition"}
    ]},
  /* ── CVLT — California Verbal Learning Test ── */
  CVLTTotal:{type:"memory_curve",label:"CVLT",words:["Lunes","Camisa","Clavel","Cuchara","Martes","Falda","Tulipán","Tenedor","Miércoles","Pantalón","Rosa","Cuchillo","Jueves","Chaleco","Margarita","Plato"],
    categories:["Día","Ropa","Flor","Cubierto","Día","Ropa","Flor","Cubierto","Día","Ropa","Flor","Cubierto","Día","Ropa","Flor","Cubierto"],
    trials:[
      {id:"E1",name:"Ensayo 1",type:"free"},{id:"E2",name:"Ensayo 2",type:"free"},
      {id:"E3",name:"Ensayo 3",type:"free"},{id:"E4",name:"Ensayo 4",type:"free"},
      {id:"E5",name:"Ensayo 5",type:"free"},{id:"LB",name:"Lista B (Interferencia)",type:"free"},
      {id:"CPRL",name:"Recuerdo CP Libre",type:"free"},{id:"CPRC",name:"Recuerdo CP con Clave",type:"cued"},
      {id:"LPRL",name:"Recuerdo LP Libre",type:"free"},{id:"LPRC",name:"Recuerdo LP con Clave",type:"cued"},
      {id:"Rec",name:"Reconocimiento",type:"recognition"}
    ]},
  /* ── TMT — Trail Making (tiempo + errores) ── */
  NiTMTA:{type:"tmt",label:"TMT-A",maxTime:180},
  NiTMTB:{type:"tmt",label:"TMT-B",maxTime:300},
  AdTMTA:{type:"tmt",label:"TMT-A Adultos",maxTime:300},
  AdTMTB:{type:"tmt",label:"TMT-B Adultos",maxTime:300},
  /* ── CARAS-R ── */
  NiTestPC_R:{type:"caras",label:"CARAS-R",totalItems:60,maxTime:180},
  /* ── Stroop ── */
  NiSt_Edades:{type:"stroop",label:"Stroop Niños",conditions:["Palabra","Color","Palabra-Color"]},
  StroopAM:{type:"stroop",label:"Stroop Adulto Mayor",conditions:["Palabra","Color","Palabra-Color"]},
  StroopAJ:{type:"stroop",label:"Stroop Adulto Joven",conditions:["Palabra","Color","Palabra-Color"]},
  /* ═══ WAIS-III — subpruebas verbales y de razonamiento (scored_items) ═══ */
  AdWAISV:{type:"scored_items",label:"Vocabulario WAIS-III",scoring:[0,1,2],items:[
    {n:1,word:"Cama"},
    {n:2,word:"Barco"},
    {n:3,word:"Desayuno"},
    {n:4,word:"Invierno"},
    {n:5,word:"Reunir"},
    {n:6,word:"Reparar"},
    {n:7,word:"Ayer"},
    {n:8,word:"Meditar"},
    {n:9,word:"Consumir"},
    {n:10,word:"Santuario"},
    {n:11,word:"Impedir"},
    {n:12,word:"Repugnancia"},
    {n:13,word:"Rechazo"},
    {n:14,word:"Confiar"},
    {n:15,word:"Generar"},
    {n:16,word:"Fortaleza"},
    {n:17,word:"Evolucionar"},
    {n:18,word:"Manada"},
    {n:19,word:"Moroso"},
    {n:20,word:"Sentencia"},
    {n:21,word:"Perímetro"},
    {n:22,word:"Compasión"},
    {n:23,word:"Remordimiento"},
    {n:24,word:"Peculiar"},
    {n:25,word:"Designar"},
    {n:26,word:"Reacio"},
    {n:27,word:"Tangible"},
    {n:28,word:"Plagiar"},
    {n:29,word:"Distinción"},
    {n:30,word:"Audaz"},
    {n:31,word:"Épico"},
    {n:32,word:"Panegírico"},
    {n:33,word:"Ominoso"}
  ]},
  AdSemWais:{type:"scored_items",label:"Semejanzas WAIS-III",scoring:[0,1,2],maxPerItem:{1:1,2:1,3:1,4:1,5:1},items:[
    {n:1,pair:"Naranja — Pera"},
    {n:2,pair:"Chaqueta — Pantalón"},
    {n:3,pair:"Perro — León"},
    {n:4,pair:"Calcetines — Zapatos"},
    {n:5,pair:"Tenedor — Cuchara"},
    {n:6,pair:"Mesa — Silla"},
    {n:7,pair:"Barco — Automóvil"},
    {n:8,pair:"Piano — Tambor"},
    {n:9,pair:"Ojo — Oído"},
    {n:10,pair:"Aire — Agua"},
    {n:11,pair:"Computador — Libro"},
    {n:12,pair:"Poema — Estatua"},
    {n:13,pair:"Mosca — Árbol"},
    {n:14,pair:"Huevo — Semilla"},
    {n:15,pair:"Vapor — Niebla"},
    {n:16,pair:"Amigo — Enemigo"},
    {n:17,pair:"Hibernación — Migración"},
    {n:18,pair:"Premio — Castigo"},
    {n:19,pair:"Trabajo — Juego"}
  ]},
  AdWAISI:{type:"scored_items",label:"Información WAIS-III",scoring:[0,1],items:[
    {n:1,q:"¿Qué día viene después del sábado?"},
    {n:2,q:"¿Cuántos años tiene?"},
    {n:3,q:"¿Qué forma tiene una pelota?"},
    {n:4,q:"¿Cuántos meses tiene un año?"},
    {n:5,q:"¿Qué es un termómetro?"},
    {n:6,q:"¿Quién escribió el Quijote?"},
    {n:7,q:"¿En qué continente está el Sahara?"},
    {n:8,q:"¿En qué dirección se oculta el sol?"},
    {n:9,q:"¿En qué continente está Egipto?"},
    {n:10,q:"¿Capital de Japón?"},
    {n:11,q:"¿Quién pintó la Capilla Sixtina?"},
    {n:12,q:"¿En qué país nacieron los Juegos Olímpicos?"},
    {n:13,q:"¿Cuáles son los continentes?"},
    {n:14,q:"¿Quién fue Cleopatra?"},
    {n:15,q:"¿A qué temperatura hierve el agua?"},
    {n:16,q:"¿Por qué es famoso Fleming?"},
    {n:17,q:"¿Qué es el Corán?"},
    {n:18,q:"¿Por qué la luna tiene luz?"},
    {n:19,q:"¿Teoría de la relatividad?"},
    {n:20,q:"¿Quién fue Gandhi?"},
    {n:21,q:"¿Tema principal de Génesis?"},
    {n:22,q:"¿Por qué es famosa Madame Curie?"},
    {n:23,q:"¿Velocidad de la luz?"},
    {n:24,q:"¿Quién fue Carlomagno?"},
    {n:25,q:"¿Quién fue Catalina la Grande?"},
    {n:26,q:"¿Quién escribió Fausto?"},
    {n:27,q:"¿Cuántos habitantes tiene la tierra?"},
    {n:28,q:"¿Dónde está la línea internacional que separa los días?"}
  ]},
  AdWAISC:{type:"scored_items",label:"Comprensión WAIS-III",scoring:[0,1,2],items:[
    {n:1,q:"¿Para qué usamos el dinero?"},
    {n:2,q:"¿Por qué la gente lleva reloj?"},
    {n:3,q:"¿Por qué lavamos la ropa?"},
    {n:4,q:"¿Qué hacer con sobre cerrado con dirección y sello?"},
    {n:5,q:"¿'Perro que ladra no muerde'?"},
    {n:6,q:"¿Para qué se pagan impuestos?"},
    {n:7,q:"¿Por qué los nacidos sordos no hablan?"},
    {n:8,q:"¿Por qué se necesita receta médica?"},
    {n:9,q:"¿Por qué leyes sobre trabajo infantil?"},
    {n:10,q:"¿Por qué testigos al casarnos?"},
    {n:11,q:"¿Por qué título antes de ejercer?"},
    {n:12,q:"¿Por qué cuesta más terreno en ciudad?"},
    {n:13,q:"¿Por qué es importante estudiar historia?"},
    {n:14,q:"¿Perdido en un bosque, ¿qué haría??"},
    {n:15,q:"¿Por qué cocinamos alimentos?"},
    {n:16,q:"¿Razones para libertad condicional?"},
    {n:17,q:"¿'Una golondrina no hace verano'?"},
    {n:18,q:"¿'A Dios rogando y con el mazo dando'?"}
  ]},
  AdMatr:{type:"scored_items",label:"Matrices WAIS-III",scoring:[0,1],items:[
    {n:1,q:"Matriz 1 — completar en cuadernillo (5 opciones)"},
    {n:2,q:"Matriz 2 — completar en cuadernillo (5 opciones)"},
    {n:3,q:"Matriz 3 — completar en cuadernillo (5 opciones)"},
    {n:4,q:"Matriz 4 — completar en cuadernillo (5 opciones)"},
    {n:5,q:"Matriz 5 — completar en cuadernillo (5 opciones)"},
    {n:6,q:"Matriz 6 — completar en cuadernillo (5 opciones)"},
    {n:7,q:"Matriz 7 — completar en cuadernillo (5 opciones)"},
    {n:8,q:"Matriz 8 — completar en cuadernillo (5 opciones)"},
    {n:9,q:"Matriz 9 — completar en cuadernillo (5 opciones)"},
    {n:10,q:"Matriz 10 — completar en cuadernillo (5 opciones)"},
    {n:11,q:"Matriz 11 — completar en cuadernillo (5 opciones)"},
    {n:12,q:"Matriz 12 — completar en cuadernillo (5 opciones)"},
    {n:13,q:"Matriz 13 — completar en cuadernillo (5 opciones)"},
    {n:14,q:"Matriz 14 — completar en cuadernillo (5 opciones)"},
    {n:15,q:"Matriz 15 — completar en cuadernillo (5 opciones)"},
    {n:16,q:"Matriz 16 — completar en cuadernillo (5 opciones)"},
    {n:17,q:"Matriz 17 — completar en cuadernillo (5 opciones)"},
    {n:18,q:"Matriz 18 — completar en cuadernillo (5 opciones)"},
    {n:19,q:"Matriz 19 — completar en cuadernillo (5 opciones)"},
    {n:20,q:"Matriz 20 — completar en cuadernillo (5 opciones)"},
    {n:21,q:"Matriz 21 — completar en cuadernillo (5 opciones)"},
    {n:22,q:"Matriz 22 — completar en cuadernillo (5 opciones)"},
    {n:23,q:"Matriz 23 — completar en cuadernillo (5 opciones)"},
    {n:24,q:"Matriz 24 — completar en cuadernillo (5 opciones)"},
    {n:25,q:"Matriz 25 — completar en cuadernillo (5 opciones)"},
    {n:26,q:"Matriz 26 — completar en cuadernillo (5 opciones)"}
  ]},
  AdWAISA:{type:"scored_items",label:"Aritmética WAIS-III",scoring:[0,1],items:[
    {n:1,q:"¿Cuántos cubos hay?"},
    {n:2,q:"¿Cuántos cubos hay?"},
    {n:3,q:"Si tiene 7 cubos y quita 2, ¿cuántos le quedan?"},
    {n:4,q:"Si tiene 3 libros y entrega 1, ¿cuántos le quedan?"},
    {n:5,q:"¿Cuántos son 4 libros más 5 libros?"},
    {n:6,q:"Un niño regala 6 caramelos de 10, ¿cuántos quedan?"},
    {n:7,q:"Maleta pesa 25kg, ¿cuánto pesan 6 iguales?"},
    {n:8,q:"Huevos en cajas de 6. Si quiere 36, ¿cuántas cajas?"},
    {n:9,q:"¿Cuántas horas para andar 24km a 3km/h?"},
    {n:10,q:"Roberto pesa doble que Cristina. Roberto=99kg, ¿Cristina?"},
    {n:11,q:"Recorrer 18km, ya recorrió 7.5km, ¿cuánto queda?"},
    {n:12,q:"Viaja 31 días cada 2 meses, ¿cuántos días en un año?"},
    {n:13,q:"415km en 5 horas, ¿velocidad media?"},
    {n:14,q:"5L de vino, llenar 7 botellas de 20cL, ¿cuánto queda?"},
    {n:15,q:"2/3 de capacidad = 500L, ¿capacidad total?"},
    {n:16,q:"60kg fruta, tira 15%, ¿cuántos kg quedan?"},
    {n:17,q:"Valor medio de 10, 9 y 20?"},
    {n:18,q:"6 trabajadores excavan 25m/día. 20% más, ¿metros cada uno?"},
    {n:19,q:"8 amarillas, 7 verdes, 5 azules. Probabilidad azul?"},
    {n:20,q:"8 personas en 6 días. ¿Cuántas para medio día?"}
  ]},
  AdWAISFI:{type:"scored_items",label:"Figuras Incompletas WAIS-III",scoring:[0,1],items:[
    {n:1,q:"Peine — ¿qué parte falta?"},
    {n:2,q:"Mesa — ¿qué parte falta?"},
    {n:3,q:"Cara — ¿qué parte falta?"},
    {n:4,q:"Maletín — ¿qué parte falta?"},
    {n:5,q:"Tren — ¿qué parte falta?"},
    {n:6,q:"Puerta — ¿qué parte falta?"},
    {n:7,q:"Gafas — ¿qué parte falta?"},
    {n:8,q:"Jarra — ¿qué parte falta?"},
    {n:9,q:"Alicates — ¿qué parte falta?"},
    {n:10,q:"Hoja — ¿qué parte falta?"},
    {n:11,q:"Tarta — ¿qué parte falta?"},
    {n:12,q:"Carrera — ¿qué parte falta?"},
    {n:13,q:"Chimenea — ¿qué parte falta?"},
    {n:14,q:"Espejo — ¿qué parte falta?"},
    {n:15,q:"Silla — ¿qué parte falta?"},
    {n:16,q:"Rosas — ¿qué parte falta?"},
    {n:17,q:"Cuchillo — ¿qué parte falta?"},
    {n:18,q:"Barca — ¿qué parte falta?"},
    {n:19,q:"Cesta — ¿qué parte falta?"},
    {n:20,q:"Ropas — ¿qué parte falta?"},
    {n:21,q:"Taquillas — ¿qué parte falta?"},
    {n:22,q:"Vaca — ¿qué parte falta?"},
    {n:23,q:"Deportivas — ¿qué parte falta?"},
    {n:24,q:"Mujer — ¿qué parte falta?"},
    {n:25,q:"Granero — ¿qué parte falta?"}
  ]},
  AdWAISL:{type:"items",label:"Letras y Números WAIS-III",maxTime:120,items:[
    {n:1,secuencia:"L-2",desc:"Números ascendente, letras A-Z · modelo 2-L",trials:["L-2","6-P","B-5"]},
    {n:2,secuencia:"F-7-L",desc:"Números ascendente, letras A-Z · modelo 7-F-L",trials:["F-7-L","R-4-D","H-1-8"]},
    {n:3,secuencia:"T-9-A-3",desc:"Números ascendente, letras A-Z · modelo 3-9-A-T",trials:["T-9-A-3","V-1-J-5","7-N-4-L"]},
    {n:4,secuencia:"8-D-6-G-1",desc:"Números ascendente, letras A-Z · modelo 1-6-8-D-G",trials:["8-D-6-G-1","K-2-C-7-S","5-P-3-Y-9"]},
    {n:5,secuencia:"M-4-E-7-Q-2",desc:"Números ascendente, letras A-Z · modelo 2-4-7-E-M-Q",trials:["M-4-E-7-Q-2","W-8-H-5-F-3","6-G-9-A-2-S"]},
    {n:6,secuencia:"R-3-B-4-Z-1-C",desc:"Números ascendente, letras A-Z · modelo 1-3-4-B-C-R-Z",trials:["R-3-B-4-Z-1-C","5-T-9-J-2-X-7","E-1-H-8-R-4-D"]},
    {n:7,secuencia:"5-H-9-S-2-N-6-A",desc:"Números ascendente, letras A-Z · modelo 2-5-6-9-A-H-N-S",trials:["5-H-9-S-2-N-6-A","D-1-R-9-B-4-K-3","7-M-2-T-6-F-1-Z"]}
  ]},
  /* Velocidad de procesamiento: conteo temporizado */
  AdSDWais:{type:"timed_count",label:"Clave de Números WAIS-III",maxTime:120,instruction:"Símbolos correctos en 120 s"},
  AdBusSim:{type:"timed_count",label:"Búsqueda de Símbolos WAIS-III",maxTime:120,instruction:"Correctas - Incorrectas en 120 s"},
  ViBusSim:{type:"timed_count",label:"Búsqueda de Símbolos Visuoespaciales",maxTime:120,instruction:"Correctas - Incorrectas en 120 s"},
  /* ═══ Complementarios — paneles de captura granular ═══ */
  /* Dígitos ENI-2 */
  NiRDD:{type:"digits",label:"Dígitos Directos ENI-2",sections:[
    {name:"Dígitos Directos",maxItems:8,trials:2,sequences:[
      {len:2,a:"4-7",b:"3-8"},{len:3,a:"5-1-9",b:"2-7-4"},
      {len:4,a:"3-9-1-8",b:"6-2-7-4"},{len:5,a:"1-5-8-2-6",b:"9-3-7-1-5"},
      {len:6,a:"2-4-7-1-9-5",b:"6-8-3-5-7-2"},{len:7,a:"9-2-6-1-4-8-3",b:"5-3-8-2-7-1-9"},
      {len:8,a:"7-4-9-6-2-5-1-8",b:"3-9-5-1-8-2-6-7"},{len:9,a:"8-5-2-9-1-7-4-3-6",b:"2-6-9-5-3-8-1-7-4"}
    ]}
  ]},
  NiENISInv:{type:"digits",label:"Dígitos Inversos ENI-2",sections:[
    {name:"Dígitos Inversos",maxItems:7,trials:2,sequences:[
      {len:2,a:"5-2",b:"4-7"},{len:3,a:"1-6-3",b:"8-2-5"},
      {len:4,a:"7-3-9-1",b:"6-4-8-2"},{len:5,a:"2-9-5-1-8",b:"4-7-3-6-1"},
      {len:6,a:"3-8-2-9-5-1",b:"7-4-1-6-9-3"},{len:7,a:"9-1-6-4-8-2-5",b:"5-3-7-1-9-4-8"}
    ]}
  ]},
  /* Fluidez verbal — contador simple con tiempo */
  FluidP:{type:"timed_count",label:"Fluidez Fonológica (P)",maxTime:60,instruction:"Palabras válidas con P en 60 s"},
  FluidM:{type:"timed_count",label:"Fluidez Fonológica (M)",maxTime:60,instruction:"Palabras válidas con M en 60 s"},
  FluidAnim:{type:"timed_count",label:"Fluidez Semántica — Animales",maxTime:60,instruction:"Animales válidos en 60 s"},
  NiFA:{type:"timed_count",label:"Fluidez Animales (niños)",maxTime:60,instruction:"Animales válidos en 60 s"},
  NiFM:{type:"timed_count",label:"Fluidez M (niños)",maxTime:60,instruction:"Palabras con M en 60 s"},
  /* SDMT — velocidad de procesamiento */
  SDMT:{type:"timed_count",label:"SDMT",maxTime:90,instruction:"Respuestas correctas en 90 s"},
  /* Denominación (Boston, BNT) — scored_items 0-1 */
  Denom48:{type:"scored_items",label:"Denominación 48 ítems",scoring:[0,1],items:Array.from({length:48},(_,i)=>({n:i+1,q:`Lámina ${i+1} — nominar imagen (cuadernillo)`}))},
  BNT:{
    type:"scored_items",
    label:"Boston Naming Test",
    requires_license:true,
    license_publisher:"Pro-Ed / Lippincott Williams & Wilkins",
    license_authors:"Kaplan, Goodglass, Weintraub (2001)",
    scoring:[0,1],
    items:[
      {n:1,q:"Lámina 1 (línea base facilitadora)"},
      {n:2,q:"Lámina 2"},
      {n:3,q:"Lámina 3"},
      {n:4,q:"Lámina 4"},
      {n:5,q:"Lámina 5"},
      {n:6,q:"Lámina 6"},
      {n:7,q:"Lámina 7"},
      {n:8,q:"Lámina 8"},
      {n:9,q:"Lámina 9"},
      {n:10,q:"Lámina 10"},
      {n:11,q:"Lámina 11"},
      {n:12,q:"Lámina 12"},
      {n:13,q:"Lámina 13"},
      {n:14,q:"Lámina 14"},
      {n:15,q:"Lámina 15"},
    ],
  },
  /* MMSE — secciones con puntaje parcial (scored_items 0-1, 30 ítems) */
  MMSE:{type:"scored_items",label:"MMSE",scoring:[0,1],items:[
    {n:1,q:"Orientación temporal — Año"},{n:2,q:"Orientación temporal — Estación"},{n:3,q:"Orientación temporal — Fecha (día del mes)"},{n:4,q:"Orientación temporal — Día de la semana"},{n:5,q:"Orientación temporal — Mes"},
    {n:6,q:"Orientación espacial — País"},{n:7,q:"Orientación espacial — Departamento/Estado"},{n:8,q:"Orientación espacial — Ciudad"},{n:9,q:"Orientación espacial — Lugar"},{n:10,q:"Orientación espacial — Piso/Sala"},
    {n:11,q:"Registro — Palabra 1"},{n:12,q:"Registro — Palabra 2"},{n:13,q:"Registro — Palabra 3"},
    {n:14,q:"Atención — Resta 100-7 (93)"},{n:15,q:"Atención — 86"},{n:16,q:"Atención — 79"},{n:17,q:"Atención — 72"},{n:18,q:"Atención — 65"},
    {n:19,q:"Recuerdo — Palabra 1"},{n:20,q:"Recuerdo — Palabra 2"},{n:21,q:"Recuerdo — Palabra 3"},
    {n:22,q:"Lenguaje — Nombrar reloj"},{n:23,q:"Lenguaje — Nombrar lápiz"},
    {n:24,q:"Lenguaje — Repetir frase"},
    {n:25,q:"Orden trifásica — Toma el papel"},{n:26,q:"Orden trifásica — Dóblelo"},{n:27,q:"Orden trifásica — Póngalo en el suelo"},
    {n:28,q:"Lectura — Cierre los ojos"},{n:29,q:"Escritura — Frase completa"},
    {n:30,q:"Praxia constructiva — Copiar pentágonos"}
  ]},
  /* Escalas auto-aplicadas — suma simple */
  EscYesavage:{type:"scored_items",label:"Yesavage GDS-15",scoring:[0,1],items:[
    {n:1,q:"¿Está básicamente satisfecho/a con su vida?"},
    {n:2,q:"¿Ha renunciado a muchas actividades o intereses?"},
    {n:3,q:"¿Siente que su vida está vacía?"},
    {n:4,q:"¿Se aburre a menudo?"},
    {n:5,q:"¿Está de buen humor la mayor parte del tiempo?"},
    {n:6,q:"¿Teme que algo malo le vaya a pasar?"},
    {n:7,q:"¿Se siente feliz la mayor parte del tiempo?"},
    {n:8,q:"¿Se siente a menudo desamparado/a o desamparada?"},
    {n:9,q:"¿Prefiere quedarse en casa antes que salir a hacer cosas nuevas?"},
    {n:10,q:"¿Cree que tiene más problemas de memoria que otras personas de su edad?"},
    {n:11,q:"¿Cree que es maravilloso estar vivo/a?"},
    {n:12,q:"¿Se siente inútil o sin valor?"},
    {n:13,q:"¿Se siente lleno/a de energía?"},
    {n:14,q:"¿Cree que su situación es desesperada?"},
    {n:15,q:"¿Cree que la mayoría de las personas están mejor que usted?"},
  ]},
  EscBeck:{type:"scored_items",label:"Beck BDI-II",scoring:[0,1,2,3],items:[
    {n:1,q:"Tristeza"},
    {n:2,q:"Pesimismo"},
    {n:3,q:"Fracaso pasado"},
    {n:4,q:"Pérdida de placer"},
    {n:5,q:"Sentimientos de culpa"},
    {n:6,q:"Sentimientos de castigo"},
    {n:7,q:"Autodesprecio"},
    {n:8,q:"Autocrítica"},
    {n:9,q:"Pensamientos o deseos suicidas"},
    {n:10,q:"Llanto"},
    {n:11,q:"Agitación"},
    {n:12,q:"Pérdida de interés"},
    {n:13,q:"Indecisión"},
    {n:14,q:"Desvalorización"},
    {n:15,q:"Pérdida de energía"},
    {n:16,q:"Cambios en el sueño"},
    {n:17,q:"Irritabilidad"},
    {n:18,q:"Cambios en el apetito"},
    {n:19,q:"Dificultad de concentración"},
    {n:20,q:"Cansancio o fatiga"},
    {n:21,q:"Pérdida de interés sexual"},
  ]},
  EscLawton:{type:"scored_items",label:"Lawton AIVD",scoring:[0,1],items:[
    {n:1,q:"Uso del teléfono"},
    {n:2,q:"Compra"},
    {n:3,q:"Manejo del dinero"},
    {n:4,q:"Preparación de alimentos"},
    {n:5,q:"Cuidado de la casa"},
    {n:6,q:"Uso de medios de transporte"},
    {n:7,q:"Responsabilidad sobre medicamentos"},
    {n:8,q:"Capacidad para realizar compras"},
  ]},
  /* Go/No-Go INECO FS */
  GoNoGoICO:{type:"scored_items",label:"Go/No-Go INECO",scoring:[0,1,2,3],items:[{n:1,q:"Comprende la regla"},{n:2,q:"Ejecuta correctamente"},{n:3,q:"Inhibe la respuesta"}]},
  InstrConflICO:{type:"scored_items",label:"Instrucciones Conflictivas INECO",scoring:[0,1,2,3],items:[{n:1,q:"Comprende la regla"},{n:2,q:"Alterna correctamente"},{n:3,q:"No persevera"}]},
  RefranesICO:{type:"scored_items",label:"Refranes INECO",scoring:[0,1,2],items:[{n:1,q:"Refrán 1"},{n:2,q:"Refrán 2"},{n:3,q:"Refrán 3"}]},
  /* CARAS-R captura simple por aciertos/errores/tiempo */
  /* Cancelación ENI-2 */
  NiENICDib:{type:"caras",label:"Cancelación de Dibujos ENI-2",totalItems:60,maxTime:180},

  /* ─── PRUEBAS NUEVAS S6: FCSRT, Tower of London, Token Test ─── */
  FCSRT:{type:"items",label:"FCSRT — Free and Cued Selective Reminding Task",items:[
    {n:1,desc:"Ensayo 1 · Recobro libre 60s",max:16},
    {n:2,desc:"Ensayo 1 · Recobro con clave categorial",max:16},
    {n:3,desc:"Ensayo 2 · Recobro libre 60s",max:16},
    {n:4,desc:"Ensayo 2 · Recobro con clave categorial",max:16},
    {n:5,desc:"Ensayo 3 · Recobro libre 60s",max:16},
    {n:6,desc:"Ensayo 3 · Recobro con clave categorial",max:16},
    {n:7,desc:"Recobro diferido libre (≥20 min)",max:16},
    {n:8,desc:"Recobro diferido con clave",max:16},
  ]},
  TowerOfLondon:{type:"scored_items",label:"Tower of London (Drexel)",scoring:[0,1,2,3],items:[
    {n:1,q:"Problema 1 (2 movimientos)"},
    {n:2,q:"Problema 2 (3 movimientos)"},
    {n:3,q:"Problema 3 (3 movimientos)"},
    {n:4,q:"Problema 4 (3 movimientos)"},
    {n:5,q:"Problema 5 (4 movimientos)"},
    {n:6,q:"Problema 6 (4 movimientos)"},
    {n:7,q:"Problema 7 (4 movimientos)"},
    {n:8,q:"Problema 8 (5 movimientos)"},
    {n:9,q:"Problema 9 (5 movimientos)"},
    {n:10,q:"Problema 10 (5 movimientos)"},
    {n:11,q:"Problema 11 (5 movimientos)"},
    {n:12,q:"Problema 12 (5 movimientos)"},
  ]},
  TokenTest:{type:"items",label:"Token Test — Versión corta De Renzi-Vignolo",items:Array.from({length:36},(_,i)=>({
    n:i+1,
    desc:`Orden ${i+1} ${i<10?"(Parte 1: simples)":i<20?"(Parte 2: 2 dimensiones)":i<30?"(Parte 3: 3 dimensiones)":"(Parte 4: complejas + temporales)"}`,
    max:1,
  }))},

  /* ─── Sprint 12: Pruebas editoriales con licencia comercial ─────────
   * Estas entradas declaran la estructura de captura para pruebas que
   * REQUIEREN LICENCIA del editor (Manual Moderno / Pearson). El campo
   * `requires_license: true` indica que el clínico debe poseer el
   * material editorial original; el sistema sólo facilita la captura
   * digital de puntajes. */
  NEUROPSI_AM:{
    type:"items",
    label:"NEUROPSI Atención y Memoria (3a ed)",
    requires_license:true,
    license_publisher:"Manual Moderno",
    license_authors:"Ostrosky-Solís, Gómez, Matute, Rosselli, Ardila, Pineda",
    edad_min:6,edad_max:85,
    items:[
      {n:1,desc:"Atención visual — Subtotal",max:10},
      {n:2,desc:"Atención auditiva — Subtotal",max:10},
      {n:3,desc:"Memoria de trabajo visual — Cubos Corsi",max:10},
      {n:4,desc:"Memoria de trabajo verbal — Dígitos inversos",max:8},
      {n:5,desc:"Memoria episódica verbal — Lista palabras (codificación)",max:36},
      {n:6,desc:"Memoria episódica verbal — Recobro libre diferido",max:12},
      {n:7,desc:"Memoria episódica verbal — Recobro con clave",max:12},
      {n:8,desc:"Memoria episódica verbal — Reconocimiento",max:12},
      {n:9,desc:"Memoria visoespacial — Figura compleja (codif.)",max:12},
      {n:10,desc:"Memoria visoespacial — Recobro diferido",max:12},
    ],
  },
  CERAD_Col:{
    type:"items",
    label:"CERAD-Col (Consortium for Establishment of Registry for AD)",
    requires_license:true,
    license_publisher:"University of Antioquia / Aguirre-Acevedo et al.",
    license_authors:"Aguirre-Acevedo D.C. et al.",
    edad_min:50,edad_max:90,
    items:[
      {n:1,desc:"Fluidez verbal semántica (animales 60s)",max:25},
      {n:2,desc:"Denominación de Boston (15 ítems)",max:15},
      {n:3,desc:"MMSE adaptado",max:30},
      {n:4,desc:"Memoria de palabras — Aprendizaje (3 ensayos)",max:30},
      {n:5,desc:"Praxias constructivas",max:11},
      {n:6,desc:"Recobro diferido (5-10 min)",max:10},
      {n:7,desc:"Reconocimiento (Sí/No)",max:10},
      {n:8,desc:"Praxias constructivas diferidas",max:11},
    ],
  },
  BANFE2:{
    type:"items",
    label:"BANFE-2 (Funciones Ejecutivas y Lóbulos Frontales)",
    requires_license:true,
    license_publisher:"Manual Moderno",
    license_authors:"Flores, Ostrosky, Lozano",
    edad_min:6,edad_max:80,
    items:[
      {n:1,desc:"Orbitomedial — Stroop (interferencia)",max:30},
      {n:2,desc:"Orbitomedial — Juego de cartas (decisión bajo riesgo)",max:60},
      {n:3,desc:"Orbitomedial — Laberintos",max:8},
      {n:4,desc:"Anterior prefrontal — Clasificación de cartas",max:64},
      {n:5,desc:"Anterior prefrontal — Refranes",max:6},
      {n:6,desc:"Anterior prefrontal — Metamemoria",max:24},
      {n:7,desc:"Dorsolateral — Torre de Hanoi (planeación)",max:8},
      {n:8,desc:"Dorsolateral — Fluidez verbal fonológica",max:25},
      {n:9,desc:"Dorsolateral — Memoria de trabajo visoespacial",max:18},
      {n:10,desc:"Dorsolateral — Memoria de trabajo verbal",max:20},
    ],
  },
  TOMM:{
    type:"items",
    label:"TOMM — Test of Memory Malingering",
    requires_license:true,
    license_publisher:"Multi-Health Systems (MHS)",
    license_authors:"Tombaugh T.N.",
    edad_min:16,edad_max:90,
    /* Indicador de validez de síntomas / detección de simulación. */
    items:[
      {n:1,desc:"Trial 1 (50 ítems)",max:50},
      {n:2,desc:"Trial 2 (50 ítems)",max:50},
      {n:3,desc:"Trial de retención (diferido)",max:50},
    ],
  },
  /* §12.5 — Rey 15-Item Test (dominio público, Rey 1964)
   * Indicador de validez de síntomas / screening de esfuerzo.
   * Cutoff: ≤9 ítems recordados sugiere bajo esfuerzo o simulación.
   * Cutoff combinado con reconocimiento: ≤9 Y recono ≤20 → alta especificidad.
   * Citar: Rey A. (1964). L'examen clinique en psychologie. Paris: PUF. */
  REY15:{
    type:"validity_grid",
    label:"Rey 15-Item Test",
    requires_license:false,
    edad_min:8,edad_max:99,
    cutoff_evocacion:9,   /* ≤9 = screening positivo para bajo esfuerzo */
    cutoff_reconocimiento:20,
    /* La grilla original (Rey 1964) — 5 filas × 3 columnas */
    grid:[
      ["A","B","C"],
      ["1","2","3"],
      ["a","b","c"],
      ["I","II","III"],
      ["□","○","△"],
    ],
    /* 15 ítems para marcar como recordados */
    items: [
      /* fila 0 */ {n:1,label:"A",fila:0},{n:2,label:"B",fila:0},{n:3,label:"C",fila:0},
      /* fila 1 */ {n:4,label:"1",fila:1},{n:5,label:"2",fila:1},{n:6,label:"3",fila:1},
      /* fila 2 */ {n:7,label:"a",fila:2},{n:8,label:"b",fila:2},{n:9,label:"c",fila:2},
      /* fila 3 */ {n:10,label:"I",fila:3},{n:11,label:"II",fila:3},{n:12,label:"III",fila:3},
      /* fila 4 */ {n:13,label:"□",fila:4},{n:14,label:"○",fila:4},{n:15,label:"△",fila:4},
    ],
  },
};

export const DEFAULT_RECOBRO_SECONDS = 20 * 60;

export const HITO_LABELS = {
  codificacion: "Codificacion",
  atencion: "Atencion",
  ejecutiva: "Funcion ejecutiva",
  recobro: "Recobro diferido",
  lenguaje: "Lenguaje",
  visoespacial: "Visoespacial",
  escala: "Escala",
};

export const TEST_APPLICATION_META = {
  GBTotal: { orden_aplicacion: 1, hito: "codificacion" },
  CVLTTotal: { orden_aplicacion: 1, hito: "codificacion" },
  "NiEniE1 + NiEniE2 + NiEniE3 + NiEniE4 = NiEniLT": { orden_aplicacion: 1, hito: "codificacion" },
  NiFCROCop: { orden_aplicacion: 2, hito: "codificacion" },
  AdTMTA: { orden_aplicacion: 3, hito: "atencion" },
  NiTMTA: { orden_aplicacion: 3, hito: "atencion" },
  AdSDWais: { orden_aplicacion: 4, hito: "atencion" },
  SDMT: { orden_aplicacion: 4, hito: "atencion" },
  AdDDir: { orden_aplicacion: 5, hito: "atencion" },
  NiRDD: { orden_aplicacion: 5, hito: "atencion" },
  NiTestPC_R: { orden_aplicacion: 6, hito: "atencion" },
  NiENICDib: { orden_aplicacion: 7, hito: "atencion" },
  InstrConflICO: { orden_aplicacion: 8, hito: "ejecutiva" },
  AdTMTB: { orden_aplicacion: 9, hito: "ejecutiva" },
  NiTMTB: { orden_aplicacion: 9, hito: "ejecutiva" },
  AdSemWais: { orden_aplicacion: 10, hito: "ejecutiva" },
  RefranesICO: { orden_aplicacion: 11, hito: "ejecutiva" },
  StroopAM: { orden_aplicacion: 12, hito: "ejecutiva" },
  StroopAJ: { orden_aplicacion: 12, hito: "ejecutiva" },
  NiSt_Edades: { orden_aplicacion: 12, hito: "ejecutiva" },
  GoNoGoICO: { orden_aplicacion: 13, hito: "ejecutiva" },
  NiENISInv: { orden_aplicacion: 13, hito: "ejecutiva" },
  AdFCRORec: { orden_aplicacion: 14, hito: "recobro", intervalo_minimo_recobro: DEFAULT_RECOBRO_SECONDS, codificacion_de: "NiFCROCop" },
  NiFCRORec: { orden_aplicacion: 14, hito: "recobro", intervalo_minimo_recobro: DEFAULT_RECOBRO_SECONDS, codificacion_de: "NiFCROCop" },
  FluidP: { orden_aplicacion: 15, hito: "lenguaje" },
  FluidM: { orden_aplicacion: 15, hito: "lenguaje" },
  FluidAnim: { orden_aplicacion: 16, hito: "lenguaje" },
  NiFA: { orden_aplicacion: 16, hito: "lenguaje" },
  Denom48: { orden_aplicacion: 17, hito: "lenguaje" },
  BNT: { orden_aplicacion: 17, hito: "lenguaje" },
  NiENIDen: { orden_aplicacion: 17, hito: "lenguaje" },
  AdWAISV: { orden_aplicacion: 18, hito: "lenguaje" },
  NiWiscVoc: { orden_aplicacion: 18, hito: "lenguaje" },
  NiPrec: { orden_aplicacion: 18, hito: "lenguaje" },
  NiLVS: { orden_aplicacion: 19, hito: "lenguaje" },
  NiCopTxt: { orden_aplicacion: 20, hito: "lenguaje" },
  NiRecEscrita: { orden_aplicacion: 21, hito: "lenguaje" },
  NiCalcEscrito: { orden_aplicacion: 22, hito: "escala" },
  NiENICMen: { orden_aplicacion: 23, hito: "escala" },
  NiIntObj: { orden_aplicacion: 24, hito: "visoespacial" },
  NiRecEmo: { orden_aplicacion: 25, hito: "visoespacial" },
  NiFigHum: { orden_aplicacion: 26, hito: "visoespacial" },
  MMSE: { orden_aplicacion: 27, hito: "escala" },
  EscKertesz: { orden_aplicacion: 28, hito: "escala" },
  EscQueja: { orden_aplicacion: 29, hito: "escala" },
  EscYesavage: { orden_aplicacion: 30, hito: "escala" },
  EscLawton: { orden_aplicacion: 31, hito: "escala" },
  EscSTAI: { orden_aplicacion: 32, hito: "escala" },
  EscBeck: { orden_aplicacion: 33, hito: "escala" },
  EscASRS: { orden_aplicacion: 34, hito: "escala" },
};

const inferHito = (test = {}) => {
  const src = `${test.test_id || ""} ${test.nombre || ""} ${test.label || ""} ${test.dominio || ""}`.toLowerCase();
  if (src.includes("recobro")) return "recobro";
  if (src.includes("grober") || src.includes("cvlt") || src.includes("curva memoria") || src.includes("fcro copia")) return "codificacion";
  if (src.includes("tmt-b") || src.includes("stroop") || src.includes("go no go") || src.includes("refran") || src.includes("semejanza")) return "ejecutiva";
  if (src.includes("tmt-a") || src.includes("digito") || src.includes("sdmt") || src.includes("clave") || src.includes("atencion") || src.includes("busqueda")) return "atencion";
  if (src.includes("fluidez") || src.includes("boston") || src.includes("denominacion") || src.includes("vocabulario") || src.includes("lectura") || src.includes("escritura")) return "lenguaje";
  if (src.includes("figura") || src.includes("cubos") || src.includes("matrices") || src.includes("objetos") || src.includes("faciales")) return "visoespacial";
  return "escala";
};

export const inferClinicalMeta = (testId, test = {}, fallbackOrder = 900) => {
  const exact = TEST_APPLICATION_META[testId] || {};
  const hito = exact.hito || inferHito({ ...test, test_id: testId });
  return {
    orden_aplicacion: exact.orden_aplicacion ?? fallbackOrder,
    hito,
    intervalo_minimo_recobro: exact.intervalo_minimo_recobro ?? (hito === "recobro" ? DEFAULT_RECOBRO_SECONDS : null),
    codificacion_de: exact.codificacion_de ?? (hito === "recobro" ? "NiFCROCop" : null),
  };
};

export const withClinicalOrder = (test, fallbackOrder = 900) => ({
  ...test,
  ...inferClinicalMeta(test.test_id, test, fallbackOrder),
});

export const prepareClinicalProtocolTests = (tests = []) =>
  tests
    .map((test, index) => ({ ...withClinicalOrder(test, index + 1), _orden_original: index }))
    .sort((a, b) => (a.orden_aplicacion - b.orden_aplicacion) || (a._orden_original - b._orden_original))
    .map(({ _orden_original, ...test }) => test);

export const isClinicalTestDone = (test, puntajes = {}) =>
  puntajes[test?.test_id] != null && puntajes[test.test_id] !== "";

export const getRetentionStorageKey = (scope, testId) =>
  `ns_codif_t_${scope || "default"}_${testId}`;

export const getRetentionStatus = (test, tests = [], startedAtByTest = {}, now = Date.now()) => {
  if (!test || test.hito !== "recobro") return { isRecobro: false, isBlocked: false, isReady: true };
  const codificacionId = test.codificacion_de;
  const codificacion = tests.find((x) => x.test_id === codificacionId);
  const startedAt = Number(startedAtByTest[codificacionId] || 0);
  const requiredMs = (test.intervalo_minimo_recobro || DEFAULT_RECOBRO_SECONDS) * 1000;
  if (!codificacionId || !startedAt) {
    return { isRecobro: true, isBlocked: true, isReady: false, missingCodificacion: true, codificacion };
  }
  const elapsedMs = Math.max(0, now - startedAt);
  return {
    isRecobro: true,
    isBlocked: elapsedMs < requiredMs,
    isReady: elapsedMs >= requiredMs,
    elapsedMs,
    requiredMs,
    remainingMs: Math.max(0, requiredMs - elapsedMs),
    codificacion,
  };
};

export const getSuggestedClinicalTest = (
  tests = [],
  puntajes = {},
  startedAtByTest = {},
  now = Date.now(),
  currentIndex = -1,
) => {
  // 1. Pendientes (sin PD aún) EXCLUYENDO la prueba en la que ya estamos.
  //    Si no excluimos la actual, se sugiere ella misma y el botón
  //    "Ir a esta" hace setCur(cur) → no navega a ningún lado.
  const pending = tests
    .map((test, index) => ({ test, index, status: getRetentionStatus(test, tests, startedAtByTest, now) }))
    .filter(({ test, index }) => !isClinicalTestDone(test, puntajes) && index !== currentIndex);

  // 2. Preferimos una disponible (no bloqueada por intervalo de recobro);
  //    si todas están bloqueadas, devolvemos la primera para que el
  //    clínico al menos vea cuál sigue y cuánto le falta.
  const available = pending.find(({ status }) => !status.isBlocked);
  return available || pending[0] || null;
};

export const formatRetentionRemaining = (ms = 0) => {
  const totalSeconds = Math.max(0, Math.ceil(ms / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  if (minutes <= 0) return `${seconds}s`;
  return `${minutes} min ${String(seconds).padStart(2, "0")}s`;
};

Object.entries(REACTIVOS).forEach(([testId, cfg], index) => {
  Object.assign(cfg, inferClinicalMeta(testId, { label: cfg.label }, index + 1));
});

export const INSTRUCCIONES={
  NiWiscDC:{mat:"9 cubos bicolor (rojo/blanco), cuadernillo de estímulos, cronómetro.",inst:"Ítems 1-3: construir el modelo físico frente al niño y pedir que lo replique. Ítems 4-14: mostrar el diseño impreso, retirar el cuadernillo y pedir que construya con los cubos.",disc:"Discontinuar tras 3 ítems consecutivos de 0.",tip:"Edad 6-7: inicio ítem 1. Edad 8-9: inicio ítem 3. Edad 10-16: inicio ítem 5. Retroceder si no obtiene puntaje perfecto en los primeros 2 ítems administrados. Tiempos: ítems 1-5 = 30 s (2 cubos) · ítems 4-8 = 60 s (4 cubos) · ítems 9-14 = 120 s (9 cubos). Bonificación por velocidad en ítems 5-14.",puntaje:"0-4 por ítem según tiempo + bonificación. Máx: 68"},
  NiWiscSem:{mat:"Cuadernillo de estímulos (ítems 1-4 ilustrados, ítems 5-23 verbales).",inst:"Ítems 1-4: mostrar imagen y preguntar '¿Qué tienen en común estos dos?' Ítems 5+: oral, '¿En qué se parecen [X] y [Y]?'",disc:"Discontinuar tras 5 ítems consecutivos de 0.",tip:"Edad 6-7: inicio ítem 1. Edad 8-9: inicio ítem 3. Edad 10-16: inicio ítem 5. Retroceder si no puntúa perfectamente en los 2 primeros ítems administrados. Puntaje: 0=incorrecto/irrelevante; 1=similitud concreta ('ambos son redondos'); 2=similitud categorial/abstracta ('ambos son frutas'). Prompt permitido en ítem de muestra únicamente.",puntaje:"0-2 por ítem. Máx: 44"},
  NiWiscRDD:{mat:"Administración oral. Sin material visual.",inst:"Directos: 'Repite los números que te digo en el mismo orden.' Inversos: 'Ahora repítelos empezando por el último.' Dictar a 1 dígito/segundo, sin entonación.",disc:"Discontinuar cada subparte (Directos / Inversos) al fallar los 2 intentos de un mismo ítem.",tip:"Siempre administrar los 2 intentos de cada ítem aunque el primero sea correcto. No anticipar la tarea de Inversos antes de empezar. Directos: series de 2-9 dígitos. Inversos: series de 2-8 dígitos. Registrar el orden exacto de la respuesta del niño, no solo si es correcto.",puntaje:"1 pt por intento correcto. Directos máx: 16 · Inversos máx: 16 · Total: 32"},
  NiWiscConD:{mat:"Cuadernillo de estímulos con filas de dibujos.",inst:"Señalar un dibujo de cada fila que va junto o forma un grupo con los de arriba.",disc:"Discontinuar tras 5 puntajes consecutivos de 0.",tip:"El niño debe elegir qué dibujos comparten una categoría conceptual. No se da retroalimentación excepto en ejemplos.",puntaje:"0-1 por ítem. Máx: 28"},
  NiWiscCl:{mat:"Cuadernillo de respuestas (hoja de claves), lápiz sin borrador, cronómetro.",inst:"Copiar símbolos que corresponden a números usando la clave de referencia, de izquierda a derecha, lo más rápido posible.",disc:"Tiempo: 120 segundos exactos.",tip:"Forma A (6-7 años): formas simples. Forma B (8-16 años): símbolos abstractos. NO se permite borrar.",puntaje:"1 por símbolo correcto. Máx: Forma A: 65, Forma B: 119"},
  NiWiscVoc:{mat:"Cuadernillo de estímulos (ítems 1-4 ilustrados, ítems 5-36 verbales).",inst:"Ítems 1-4: mostrar imagen, '¿Qué es esto?'. Ítems 5+: oral, 'Dime qué significa [palabra].'",disc:"Discontinuar tras 5 ítems consecutivos de 0.",tip:"Edad 6-7: inicio ítem 5. Edad 8-9: inicio ítem 7. Edad 10-11: inicio ítem 9. Edad 12-16: inicio ítem 11. Retroceder si falla en los primeros 2 ítems. Puntaje: 0=incorrecto/vago; 1=uso funcional simple o sinónimo ('cuchillo=cortar'); 2=definición con concepto+atributos ('cuchillo=utensilio con filo para cortar alimentos'). Prompt para resp. de 1 pt: '¿Puedes decirme algo más?' (solo una vez).",puntaje:"0-2 por ítem. Máx: 68"},
  NiWiscLN:{mat:"Administración oral. Sin material visual.",inst:"'Voy a decirte letras y números mezclados. Repítelos poniendo primero los números del menor al mayor y luego las letras en orden alfabético.' Ej: 'B-3-A' → '3-A-B'.",disc:"Discontinuar al fallar los 3 intentos de un mismo ítem.",tip:"Solo para edades 8-16 (no aplicar a 6-7 años). Ritmo de dictado: 1 elemento/segundo. Siempre 3 intentos por ítem. Nunca repetir la secuencia al niño. Si pide repetición: 'Lo siento, no puedo repetirlo'. Registrar errores de transposición (olvida el orden) vs. olvido completo.",puntaje:"1 pt por intento correcto. Máx: 30"},
  NiWiscMat:{mat:"Cuadernillo de estímulos con matrices de 5 opciones.",inst:"'Mira este diseño al que le falta una parte. Señala cuál de estas opciones (señalar fila inferior) completa correctamente el diseño.'",disc:"Discontinuar tras 4 ítems consecutivos de 0 o 4 incorrectos en 5 consecutivos.",tip:"Edad 6-7: inicio ítem 4. Edad 8-9: inicio ítem 7. Edad 10-16: inicio ítem 11. Retroceder si falla los primeros 2 ítems administrados. Sin tiempo límite estricto — pero registrar si el niño tarda > 30 s en responder. Sin retroalimentación.",puntaje:"0-1 por ítem. Máx: 35"},
  NiWiscCom:{mat:"Cuadernillo de estímulos (imágenes ítems 1-2, verbal ítems 3-21).",inst:"'Te voy a hacer unas preguntas sobre situaciones de la vida diaria. Responde lo mejor que puedas.'",disc:"Discontinuar tras 4 ítems consecutivos de 0.",tip:"Edad 6-7: inicio ítem 1. Edad 8-9: inicio ítem 3. Edad 10-16: inicio ítem 5. Retroceder si no puntúa en los primeros 2. Puntaje: 0=incorrecto; 1=una razón válida; 2=dos razones o concepto general completo. Prompt para resp. de 1 pt: '¿Por qué más?' o '¿Puedes darme otra razón?' (solo una vez por ítem).",puntaje:"0-2 por ítem. Máx: 42"},
  NiWiscBusSim:{mat:"Cuadernillo de respuestas, lápiz, cronómetro.",inst:"Observar los dos símbolos objetivo y marcar SÍ o NO si aparecen en el grupo de búsqueda.",disc:"Tiempo: 120 segundos exactos.",tip:"Forma A (6-7 años): figuras simples. Forma B (8-16 años): símbolos abstractos. Marcar X rápido y con precisión.",puntaje:"Correctas - Incorrectas. Máx: Forma A: 45, Forma B: 60"},
  NiWisFigInc:{mat:"Cuadernillo de estímulos, cronómetro.",inst:"Identificar qué parte importante falta en cada imagen dentro del tiempo.",disc:"Discontinuar tras 5 puntajes consecutivos de 0.",tip:"20 segundos por ítem. El niño debe señalar o nombrar la parte faltante. Suplementaria.",puntaje:"0-1 por ítem. Máx: 38"},
  NiWiscAri:{mat:"Cuadernillo de estímulos (bloques visuales para ítems iniciales), cronómetro.",inst:"Resolver problemas aritméticos mentalmente (sin papel ni lápiz).",disc:"Discontinuar tras 4 puntajes consecutivos de 0.",tip:"Tiempos variables por ítem (30-45s). Suplementaria. Repetir el problema UNA vez si lo pide.",puntaje:"0-1 por ítem. Máx: 34"},
  NiWisInf:{mat:"Ningún material visual. Solo administración oral.",inst:"Responder preguntas de conocimiento general.",disc:"Discontinuar tras 5 puntajes consecutivos de 0.",tip:"Edad 6-8: inicio ítem 5. Edad 9-11: inicio ítem 10. Edad 12-16: inicio ítem 12. Suplementaria.",puntaje:"0-1 por ítem. Máx: 33"},
  NiWisPalCon:{mat:"Ningún material visual. Solo administración oral.",inst:"Adivinar una palabra a partir de pistas progresivas.",disc:"Discontinuar tras 5 puntajes consecutivos de 0.",tip:"Máximo 5 pistas por ítem. Suplementaria. Cada pista adicional reduce el puntaje.",puntaje:"5 a 1 según pistas usadas. Máx: 120"},
  NiWisReg:{mat:"Cuadernillo de respuestas, lápiz, cronómetro.",inst:"Buscar y marcar figuras objetivo entre distractores en una página.",disc:"Tiempo: 45 segundos exactos.",tip:"Suplementaria. Velocidad de procesamiento. Forma A y B.",puntaje:"Correctas - Incorrectas"},
  /* ── WAIS-III — Regla general de retroceso: si el inicio ≠ ítem 1 y falla
   *   los primeros 2 ítems administrados → regresar al ítem 1 y avanzar.
   *   Adultos mayores (75+ años) siempre inician en ítem 1 en todos los tests. */
  AdWAISFI:{mat:"Cuadernillo de estímulos, cronómetro.",inst:"'Observa este dibujo. ¿Qué parte importante le falta?' Si no responde en 15 s: '¿Qué falta aquí?'. Respuesta válida: señalar la parte o nombrarla.",disc:"Discontinuar tras 5 ítems consecutivos de 0. Tiempo límite: 20 s por ítem.",tip:"Inicio: ítem 6 (16-74 a.) / ítem 1 (75+ a.). Retroceder si falla ítems 6 y 7. No aceptar 'no sé' sin esperar al menos 10 s. Señalar o nombrar la parte es igualmente válido.",puntaje:"0-1 por ítem. Máx: 25"},
  AdWAISV:{mat:"Administración oral. Sin material visual.",inst:"'Le voy a decir unas palabras. Dígame qué significa cada una.' Presentar una palabra a la vez, claramente.",disc:"Discontinuar tras 6 ítems consecutivos de 0.",tip:"Inicio: ítem 4 (todas las edades). Retroceder si falla ítems 4 o 5. Puntaje: 0=incorrecta/vaga/idiosincrásica; 1=sinónimo simple o uso funcional ('tijeras=cortar'); 2=definición con concepto general + atributos ('tijeras=instrumento con dos hojas para cortar'). Prompt para respuesta de 1 pt: '¿Qué más puede decirme?' (solo una vez por ítem).",puntaje:"0-2 por ítem. Máx: 66"},
  AdSDWais:{mat:"Hoja de respuestas con clave impresa, lápiz sin borrador, cronómetro.",inst:"Completar ítems de práctica hasta que el examinado comprenda. Luego: 'Ahora haga lo mismo lo más rápido posible. Empiece aquí.' Iniciar cronómetro.",disc:"Tiempo: 120 s exactos. Detener al indicar el tiempo.",tip:"Trabajar de izquierda a derecha sin saltar casillas. No usar borrador — tachar y corregir al lado. No memorizar la clave. Anotar el último símbolo completado al detener.",puntaje:"Símbolos correctos en 120 s. Máx: 133"},
  AdSemWais:{mat:"Administración oral. Sin material visual.",inst:"'Le voy a decir dos palabras. Dígame en qué se parecen.' Ejemplo de práctica: '¿En qué se parecen un perro y un gato?'",disc:"Discontinuar tras 4 ítems consecutivos de 0.",tip:"Inicio: ítem 1 (todas las edades). Sin retroceso. Puntaje: 0=incorrecto/sin relación; 1=similitud concreta o funcional ('sirven para comer'); 2=similitud abstracta/categorial ('son animales/mamíferos'). Prompt permitido si respuesta vaga: '¿En qué más?' (máximo una vez).",puntaje:"0-2 por ítem. Máx: 33"},
  AdWAISCC:{mat:"9 cubos bicolor (rojo/blanco), cuadernillo de estímulos, cronómetro.",inst:"Ítems 1-2: demostrar el diseño con cubos y pedir que lo replique. Ítems 3+: mostrar la imagen impresa, el examinado replica con sus cubos.",disc:"Discontinuar tras 3 ítems consecutivos de 0.",tip:"Inicio: ítem 5 (16-74 a.) / ítem 1 (75+ a.). Retroceder si falla ítems 5 y 6. Tiempos: ítems 1-8 = 60 s · ítems 9-14 = 120 s. Bonificación por velocidad solo en ítems 9-14 (completar en <31 s o <75 s según ítem). No rotar el cuadernillo.",puntaje:"0-4 por ítem según tiempo + bonificación. Total aprox. 0-68"},
  AdWAISA:{mat:"Cronómetro. (Ítems iniciales pueden mostrar imagen en el cuadernillo según edición.)",inst:"'Le voy a leer unos problemas de matemáticas. Resuélvalos mentalmente y dígame la respuesta cuando la tenga. Sin papel ni lápiz.'",disc:"Discontinuar tras 4 ítems consecutivos de 0.",tip:"Inicio: ítem 5 (16-74 a.) / ítem 1 (75+ a.). Retroceder si falla ítems 5 y 6. Tiempos: ítems 1-12 ≈ 30 s · ítems 13-16 ≈ 60 s · ítems 17-20 ≈ 120 s. Repetir el enunciado UNA sola vez si se solicita. No dar retroalimentación.",puntaje:"0-1 por ítem. Máx: 22"},
  AdMatr:{mat:"Cuadernillo de estímulos con matrices de 5 opciones.",inst:"'Observe esta figura a la que le falta una parte. Señale cuál de estas opciones (señalar la fila inferior) completa correctamente el diseño.'",disc:"Discontinuar tras 4 ítems consecutivos de 0 o 4 incorrectos en 5 consecutivos.",tip:"Inicio: ítem 4 (16-74 a.) / ítem 1 (75+ a.). Retroceder si falla ítems 4 y 5. Permitir hasta 30 s por ítem. Sin retroalimentación. Respuesta válida: señalar o decir el número/letra de la opción.",puntaje:"0-1 por ítem. Máx: 26"},
  AdDDir:{mat:"Administración oral. Sin material visual.",inst:"Directos: 'Repita los números que le digo en el mismo orden.' Inversos: 'Ahora repítalos empezando por el último y terminando por el primero.'",disc:"Discontinuar cada subparte (Directos / Inversos) al fallar los 2 intentos de un mismo ítem.",tip:"Ritmo: 1 dígito/segundo, sin entonación. Siempre administrar 2 intentos por ítem aunque el primero sea correcto. No anticipar los Inversos antes de empezar la prueba. Directos: series de 2-9 dígitos. Inversos: series de 2-8 dígitos. Siempre iniciar por la serie más corta en ambas partes.",puntaje:"1 pt por intento correcto. Directos máx: 16 · Inversos máx: 14 · Total: 30"},
  AdWAISI:{mat:"Administración oral. Sin material visual.",inst:"'Le voy a hacer algunas preguntas. Responda lo mejor que pueda.'",disc:"Discontinuar tras 6 ítems consecutivos de 0.",tip:"Inicio: ítem 5 (16-74 a.) / ítem 1 (75+ a.). Retroceder si falla ítems 5 y 6. Prompt si respuesta incompleta: '¿Qué más sabe sobre eso?' (solo una vez). No dar pistas temáticas ni categorías.",puntaje:"0-1 por ítem. Máx: 28"},
  AdWAISC:{mat:"Administración oral. Sin material visual.",inst:"'Le voy a hacer preguntas sobre situaciones de la vida diaria. Responda lo mejor que pueda.'",disc:"Discontinuar tras 4 ítems consecutivos de 0.",tip:"Inicio: ítem 3 (16-74 a.) / ítem 1 (75+ a.). Retroceder si falla ítems 3 y 4. Puntaje: 0=irrelevante; 1=una razón válida o concepto parcial; 2=dos razones válidas o concepto general completo. Prompt para respuesta de 1 pt: '¿Por qué más?' (solo una vez por ítem).",puntaje:"0-2 por ítem. Máx: 36"},
  AdBusSim:{mat:"Cuadernillo de respuestas WAIS-III, lápiz sin borrador, cronómetro.",inst:"Ítems de práctica hasta comprensión. Luego: 'Marque SÍ si alguno de los símbolos de arriba aparece en el grupo. Marque NO si no aparece. Lo más rápido posible.'",disc:"Tiempo: 120 s exactos.",tip:"Completar práctica antes del tiempo cronometrado. Trabajar izquierda a derecha sin saltar. Solo corregir en práctica. Registrar el último ítem al detener el tiempo. Omisiones no restan.",puntaje:"Correctas − Incorrectas. Omisiones no restan. Máx: 60"},
  ViBusSim:{mat:"Cuadernillo de respuestas (adulto mayor), lápiz sin borrador, cronómetro.",inst:"Ítems de práctica hasta comprensión. Luego: 'Marque SÍ si alguno de los símbolos de arriba aparece en el grupo. Marque NO si no aparece. Lo más rápido posible.'",disc:"Tiempo: 120 s exactos.",tip:"Completar práctica antes del tiempo cronometrado. Trabajar izquierda a derecha sin saltar. Solo corregir en práctica. Registrar el último ítem al detener el tiempo. Omisiones no restan.",puntaje:"Correctas − Incorrectas. Omisiones no restan. Máx: 60"},
  AdWAISL:{mat:"Administración oral. Sin material visual.",inst:"'Voy a decirle letras y números mezclados. Repítalos poniendo primero los números del menor al mayor y luego las letras en orden alfabético.' Ej: '6-B-3' → '3-6-B'.",disc:"Discontinuar al fallar los 3 intentos de un mismo ítem.",tip:"Rango: 16-89 años. Siempre 3 intentos por ítem, dictados a 1 elemento/segundo. Nunca repetir la serie al examinado ('Lo siento, no puedo repetirla'). Si la serie tiene solo letras o solo números, el orden es igual. Puntaje 1 por cada intento correcto.",puntaje:"1 pt por intento correcto. Máx: 21"},
  /* Complementarios comunes */
  NiFCROCop:{mat:"Hoja en blanco, lápices de colores (6), cronómetro. Modelo de la FCRO.",inst:"Copiar la Figura Compleja de Rey-Osterrieth con la mayor precisión posible.",disc:"Tiempo máximo: 5 minutos.",tip:"Dar un color diferente cada 45-60 segundos para registrar la estrategia de copia. Sistema Taylor de 18 elementos.",puntaje:"0-2 por elemento (18 elementos). Máx: 36"},
  NiFCRORec:{mat:"Hoja en blanco, lápiz.",inst:"Dibujar de memoria la figura que copió anteriormente (esperar 20-30 min tras la copia).",disc:"Tiempo máximo: 5 minutos.",tip:"NO avisar al paciente que deberá recordar la figura. Calificar con el mismo sistema Taylor de 18 elementos.",puntaje:"0-2 por elemento. Máx: 36"},
  NiTMTA:{mat:"Hoja TMT-A, lápiz, cronómetro.",inst:"Conectar números del 1 al 25 en orden ascendente lo más rápido posible sin levantar el lápiz.",disc:"Tiempo máximo: 180 segundos (niños). Si comete error, señalar y continuar desde el último correcto.",tip:"Aplicable a partir de 9 años. Registrar tiempo en segundos y errores.",puntaje:"Tiempo en segundos. Menos tiempo = mejor rendimiento"},
  NiTMTB:{mat:"Hoja TMT-B, lápiz, cronómetro.",inst:"Alternar entre números y letras en orden: 1-A-2-B-3-C... lo más rápido posible.",disc:"Tiempo máximo: 300 segundos (niños).",tip:"Aplicable a partir de 9 años. Más sensible a función ejecutiva que TMT-A.",puntaje:"Tiempo en segundos. Menos tiempo = mejor rendimiento"},
  AdTMTA:{mat:"Hoja TMT-A, lápiz, cronómetro.",inst:"Conectar números del 1 al 25 en orden ascendente lo más rápido posible.",disc:"Tiempo máximo: 300 segundos.",tip:"Registrar tiempo y errores. Corregir errores en el momento.",puntaje:"Tiempo en segundos"},
  AdTMTB:{mat:"Hoja TMT-B, lápiz, cronómetro.",inst:"Alternar números y letras: 1-A-2-B-3-C... lo más rápido posible.",disc:"Tiempo máximo: 300 segundos.",tip:"Mide flexibilidad cognitiva y alternancia.",puntaje:"Tiempo en segundos"},
  NiTestPC_R:{mat:"Cuadernillo CARAS-R, lápiz, cronómetro.",inst:"Identificar cuál de las 3 caras es diferente. Marcar con X.",disc:"Tiempo: 180 segundos (3 minutos).",tip:"60 ítems. Mide atención sostenida y selectiva visual.",puntaje:"Aciertos - Errores. ICI = (A-E)/(A+E)"},
  SDMT:{mat:"Hoja SDMT, lápiz, cronómetro.",inst:"Escribir el número que corresponde a cada símbolo según la clave. 90 segundos.",disc:"Tiempo: 90 segundos exactos.",tip:"Similar a Claves pero inverso (del símbolo al número). Mide velocidad de procesamiento.",puntaje:"Respuestas correctas en 90s. Máx: 110"},
  GBTotal:{mat:"16 tarjetas con palabras, tarjeta de claves semánticas.",inst:"Aprendizaje de 16 palabras en 4 categorías. 3 ensayos de recuerdo libre + con clave. Recuerdo diferido a 20 min.",disc:"3 ensayos de adquisición + recuerdo diferido libre y con clave.",tip:"Registrar intrusiones y perseveraciones por ensayo. Curva de aprendizaje y beneficio de claves.",puntaje:"Total recuerdo libre + con clave por ensayo. Máx por ensayo: 16"},
  CVLTTotal:{mat:"Lista A (16 palabras, 4 categorías), Lista B (interferencia), hoja de registro.",inst:"5 ensayos de aprendizaje libre de Lista A, luego Lista B, recuerdo inmediato y diferido (20 min) libre y con clave semántica.",disc:"5 aprendizajes + interferencia + corto + largo + reconocimiento.",tip:"Registrar intrusiones, perseveraciones, agrupaciones semánticas y serial. Interferencia proactiva y retroactiva.",puntaje:"Total ensayos 1-5 (máx 80). Recuerdo corto/largo (máx 16 cada uno). d′ de reconocimiento."},
  FluidP:{mat:"Cronómetro, hoja de registro.",inst:"Decir todas las palabras que empiecen con la letra P durante 60 s (no nombres propios ni derivados).",disc:"60 segundos.",tip:"Registrar en bloques de 15 s para detectar decremento. Contar perseveraciones e intrusiones (excluir del total).",puntaje:"Palabras válidas en 60 s"},
  FluidM:{mat:"Cronómetro, hoja de registro.",inst:"Decir todas las palabras que empiecen con la letra M durante 60 s.",disc:"60 segundos.",tip:"Registrar perseveraciones e intrusiones.",puntaje:"Palabras válidas en 60 s"},
  FluidAnim:{mat:"Cronómetro.",inst:"Decir todos los animales que recuerde durante 60 s.",disc:"60 segundos.",tip:"Registrar subgrupos (granja, salvajes, acuáticos) para evaluar estrategia semántica.",puntaje:"Animales válidos en 60 s"},
  Denom48:{mat:"Cuadernillo 48 ítems, claves fonológicas y semánticas.",inst:"Nombrar cada imagen. Ante bloqueo: clave semántica, luego fonológica si persiste.",disc:"20 s por ítem. Fin si el paciente falla 6 consecutivos.",tip:"Registrar parafasias semánticas/fonológicas, circunloquios y beneficio de clave.",puntaje:"Nombradas correctamente (esp/clave). Máx: 48"},
  BNT:{mat:"Boston Naming Test — cuadernillo 60 o 15 ítems.",inst:"Nombrar la figura presentada. Dar clave semántica y luego fonológica si hay anomia.",disc:"Fallo en 6 ítems consecutivos.",tip:"Documentar tipo de parafasia y beneficio de claves.",puntaje:"Correctas sin clave. Máx según versión (15 o 60)"},
  StroopAM:{mat:"Lámina palabras, lámina colores, lámina palabra-color.",inst:"Leer las palabras, después nombrar colores, después nombrar el color de la tinta (inhibición).",disc:"45 s por lámina.",tip:"Calcular interferencia según fórmula de Golden.",puntaje:"Palabras en 45 s por lámina; interferencia = PC - (P·C)/(P+C)"},
  StroopAJ:{mat:"Lámina palabras, lámina colores, lámina palabra-color.",inst:"Leer palabras, nombrar colores, nombrar color de la tinta.",disc:"45 s por lámina.",tip:"Registrar autocorrecciones y errores.",puntaje:"Palabras en 45 s; interferencia = PC - (P·C)/(P+C)"},
  MMSE:{mat:"Protocolo MMSE, lápiz, hoja.",inst:"Administrar las 11 tareas (orientación, registro, atención/cálculo, memoria diferida, lenguaje, praxia).",disc:"Aplicación secuencial sin discontinuación.",tip:"Ajustar por escolaridad (puntos de corte variables).",puntaje:"0-30"},
  EscKertesz:{mat:"Cuestionario FBI/Kertesz.",inst:"Aplicar al cuidador principal. Marcar frecuencia/intensidad de cada ítem.",disc:"Completar todos los ítems.",tip:"Útil para demencias frontotemporales; contrastar con observación directa.",puntaje:"Suma ponderada"},
  EscQueja:{mat:"Cuestionario de queja subjetiva de memoria.",inst:"Aplicar al paciente. Indicar frecuencia percibida de fallos.",disc:"Ninguna.",tip:"Complementar con informante para detectar anosognosia.",puntaje:"Puntaje total"},
  EscYesavage:{mat:"Yesavage 15 ítems.",inst:"Responder sí/no a cada ítem con base en las últimas dos semanas.",disc:"—",tip:"Tamizaje de depresión en adulto mayor. Corte ≥5 depresión, ≥10 depresión severa.",puntaje:"0-15"},
  EscLawton:{mat:"Escala de Lawton (AIVD).",inst:"Aplicar al cuidador o paciente.",disc:"—",tip:"8 ítems AIVD; mujeres 0-8, hombres 0-5.",puntaje:"0-8 / 0-5"},
  EscSTAI:{mat:"STAI — 40 ítems (estado y rasgo).",inst:"Responder en escala Likert.",disc:"—",tip:"Interpretar estado vs rasgo por separado.",puntaje:"0-60 por subescala"},
  EscBeck:{mat:"BDI-II, 21 ítems.",inst:"Seleccionar la opción que mejor describa la última semana.",disc:"—",tip:"Cortes: 0-13 mínima · 14-19 leve · 20-28 moderada · 29-63 severa.",puntaje:"0-63"},
  EscASRS:{mat:"ASRS v1.1.",inst:"Responder 18 ítems sobre síntomas TDAH en adultos.",disc:"—",tip:"Parte A (6 ítems) es tamizaje; Parte B diagnóstica.",puntaje:"Ítems positivos / total"},
  InstrConflICO:{mat:"Protocolo INECO FS.",inst:"Tocar la mesa según la consigna del examinador (1 golpe → 2; 2 golpes → 0).",disc:"Fallo en la regla.",tip:"Mide control inhibitorio y comprensión de reglas contradictorias.",puntaje:"0-3"},
  RefranesICO:{mat:"3 refranes.",inst:"Explicar el significado abstracto del refrán.",disc:"—",tip:"Evaluar abstracción: concretismo → frontal.",puntaje:"0-6 (0-2 por refrán)"},
  GoNoGoICO:{mat:"Protocolo INECO FS.",inst:"Golpear la mesa ante señal go, inhibir ante señal no-go.",disc:"Fallo en la regla.",tip:"Control inhibitorio / perseveración.",puntaje:"0-3"},
  NiFigHum:{mat:"Hoja en blanco, lápiz.",inst:"Dibujar una figura humana completa, como la mejor pueda hacer.",disc:"—",tip:"Baremos Goodenough-Harris o Koppitz según edad.",puntaje:"Ítems presentes (máx según baremo)"},
  NiIntObj:{mat:"Cuadernillo ENI-2 Integración de Objetos.",inst:"Identificar el objeto que forman las partes.",disc:"Según manual ENI-2.",tip:"Evaluar análisis parte-todo.",puntaje:"Aciertos"},
  NiRecEmo:{mat:"Láminas de emociones faciales (ENI-2).",inst:"Nombrar la emoción que expresa cada rostro.",disc:"—",tip:"Prototípicas vs complejas; confusiones frecuentes miedo-sorpresa.",puntaje:"Aciertos"},
  NiENICDib:{mat:"Cuadernillo ENI-2 Cancelación de Dibujos, lápiz, cronómetro.",inst:"Tachar todas las figuras iguales al modelo.",disc:"Según ENI-2.",tip:"Registrar omisiones y falsos positivos.",puntaje:"Aciertos - Errores"},
  NiENIDen:{mat:"Láminas ENI-2 Denominación.",inst:"Nombrar la imagen.",disc:"Manual ENI-2.",tip:"Registrar parafasias.",puntaje:"Aciertos"},
  NiFA:{mat:"Cronómetro.",inst:"Decir todos los animales que recuerde en 60 s.",disc:"60 s.",tip:"Registrar subcategorías y perseveraciones.",puntaje:"Animales válidos"},
  NiFM:{mat:"Cronómetro.",inst:"Decir palabras que empiecen con M en 60 s.",disc:"60 s.",tip:"Registrar perseveraciones.",puntaje:"Palabras válidas"},
  NiPrec:{mat:"Texto estandarizado por grado, cronómetro.",inst:"Leer en voz alta con la mejor velocidad y precisión posibles.",disc:"Al terminar el texto.",tip:"Registrar tiempo, errores, sustituciones, omisiones e inserciones.",puntaje:"Palabras/minuto · precisión %"},
  NiLVS:{mat:"Texto + preguntas.",inst:"Leer en silencio y responder preguntas literales e inferenciales.",disc:"—",tip:"Controlar tiempo de lectura.",puntaje:"Preguntas correctas"},
  NiCopTxt:{mat:"Texto modelo + hoja.",inst:"Copiar el texto cuidando letra, ortografía y puntuación.",disc:"—",tip:"Evaluar grafomotricidad y errores ortográficos.",puntaje:"Errores totales"},
  NiRecEscrita:{mat:"Hoja en blanco.",inst:"Escribir un texto de al menos 5 renglones sobre un tema.",disc:"Límite de 10 minutos.",tip:"Evaluar riqueza léxica, sintaxis y ortografía.",puntaje:"Rúbrica ENI-2"},
  NiCalcEscrito:{mat:"Hoja con operaciones ENI-2.",inst:"Resolver las operaciones con lápiz y papel.",disc:"Manual ENI-2.",tip:"Observar procedimiento, valor posicional.",puntaje:"Aciertos"},
  NiENICMen:{mat:"Protocolo ENI-2 cálculo mental.",inst:"Resolver los problemas mentalmente.",disc:"Manual ENI-2.",tip:"Registrar estrategia y tiempo.",puntaje:"Aciertos"},
  NiSt_Edades:{mat:"Láminas Stroop versión infantil.",inst:"Leer palabras, nombrar colores, nombrar color de la tinta.",disc:"45 s por lámina.",tip:"Interferencia corregida por edad.",puntaje:"Ítems en 45 s · interferencia"},
  NiENISInv:{mat:"Ninguno (oral).",inst:"Repetir secuencias de dígitos en orden inverso.",disc:"Fallo en los dos intentos del mismo ítem.",tip:"Ajustar por edad ENI-2.",puntaje:"Intentos correctos"},
  NiRDD:{mat:"Ninguno (oral).",inst:"Repetir secuencias de dígitos en orden directo.",disc:"Fallo en los dos intentos del mismo ítem.",tip:"Span máximo en dígitos.",puntaje:"Intentos correctos"},

  /* ─── PRUEBAS NUEVAS (Sprint 6) ─── */
  FCSRT:{mat:"16 cartas con dibujos agrupados en 4 categorías. Cronómetro.",inst:"1) Mostrar 4 cartas y pedir identificarlas por categoría. 2) Recobro libre 60s. 3) Recobro con clave categorial. 4) Repetir 3 ensayos. 5) Recobro diferido a 20-30 min.",disc:"3 ensayos completos.",tip:"Sucesor moderno de Grober & Buschke. Baremos Neuronorma Colombia disponibles para ≥50 años.",puntaje:"Free recall total (0-48) · Total recall (0-48) · Recobro diferido"},
  TowerOfLondon:{mat:"Tablero con 3 varillas + 3 discos de colores diferentes (Drexel).",inst:"Igualar la configuración objetivo moviendo un disco a la vez. Mín. de movimientos por problema. 12 problemas (2-5 movimientos óptimos).",disc:"3 fallos consecutivos.",tip:"Mide planeación. Registrar movimientos totales, tiempo, problemas resueltos en mínimo.",puntaje:"Problemas resueltos en mínimo (0-12) · Movimientos extra · Tiempo total"},
  TokenTest:{mat:"20 tokens (2 colores × 2 tamaños × 5 formas) versión corta De Renzi-Vignolo 1962.",inst:"Ejecutar 36 órdenes verbales de complejidad creciente: desde 'toque el círculo rojo' hasta 'antes de tocar el cuadrado verde, toque el círculo azul'.",disc:"36 ítems completados o 5 fallos consecutivos.",tip:"Mide comprensión verbal. Sensible a afasia receptiva. Baremos Neuronorma Colombia.",puntaje:"Aciertos (0-36) · cuts: ≤29 sospecha afasia receptiva"},

  /* ─── Sprint 12: requieren material editorial ─── */
  NEUROPSI_AM:{mat:"Kit NEUROPSI Atención y Memoria 3a ed (Manual Moderno). REQUIERE LICENCIA.",inst:"Seguir protocolo del manual. El sistema captura sólo puntajes para cómputo del perfil.",disc:"Por subtest según manual.",tip:"Estandarizado para México y Colombia, 6-85 años. Excelente tamización combinada de atención + memoria.",puntaje:"Suma de subtests · perfil normalizado por edad"},
  CERAD_Col:{mat:"Kit CERAD-Col (validación Aguirre-Acevedo et al.). REQUIERE LICENCIA.",inst:"Protocolo CERAD adaptado: 8 subpruebas en ~30 min.",disc:"Por subtest.",tip:"Gold standard para tamización de demencia. Baremos colombianos validados.",puntaje:"Suma + perfil por dominio"},
  BANFE2:{mat:"Kit BANFE-2 (Manual Moderno). REQUIERE LICENCIA.",inst:"15 subpruebas agrupadas en 3 dominios: Orbitomedial, Anterior Prefrontal, Dorsolateral.",disc:"Por subtest según manual.",tip:"Estandarizado niños 6-7 años + universitarios colombianos. Perfil ejecutivo completo.",puntaje:"Subtotales por dominio + total"},
  TOMM:{mat:"Kit TOMM (MHS). REQUIERE LICENCIA.",inst:"Trial 1 + Trial 2 + Trial diferido (~5-10 min cada uno).",disc:"Al completar los 3 trials.",tip:"Indicador de validez de síntomas / detección de simulación. Trial 2 ≥45 sugiere esfuerzo normal.",puntaje:"Aciertos por trial (0-50 cada uno) · corte clínico: Trial 2 < 45"}
};

export const GUIA_INFORME={observacion:"Partir del estado general: alertamiento, movilidad, disposición para consulta. Describir condiciones motoras, sensoriales y conductuales-emocionales relevantes. Cambios con/sin cuidador.",atencion:"Red de vigilancia: alerta tónica/fásica (Posner). Atención focal (Span-dígitos directos). Velocidad de procesamiento (índice IVP + tiempos límite en todas las pruebas). Sostenida (Claves como predictor). Selectiva (Búsqueda de Símbolos, sensibilidad a estímulos). Sistema Atencional Superior si aplica.",memoria:"N/A en WISC básico. Si se aplicaron pruebas complementarias, describir aquí.",praxias:"Iniciar estableciendo funcionalidad sensoperceptual/motora. Si hay bajo tono → describir. Analizar Cubos: análisis y síntesis visuales, manipulación, ubicación y lateralidad como posibles interferencias.",lenguaje:"Iniciar con lenguaje espontáneo: expresivo (iniciativa, fluidez, articulación, sintaxis, prosodia, semántica, pragmática) y comprensivo (comprensión del discurso, seguimiento de instrucciones). Modelo Ellis y Young ampliado. Conceptualización verbal (Vocabulario): partir del léxico.",funciones_ejecutivas:"Categorización (Semejanzas, Conceptos con Dibujos): de asociación básica a abstracción. MT verbal: sostenimiento, uso de info, operaciones. Razonamiento no verbal (Matrices): igualación, emparejamiento, secuenciación. Juicio social (Comprensión). Autorregulación: impulsividad, planeación, metacognición. Mediación del lenguaje como regulador (Luria).",reglas_ninos:"NUNCA usar 'conserva' o 'preserva' en niños. Usar DIS- en vez de A- (disfasia, no afasia). No repetir info de gráfica. No hablar de la prueba sino de la función cognitiva. Análisis bottom-up funcional."};
