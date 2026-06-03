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
"AdBusSim + ViBusSim":["Ansiedad y tremor","Atención sostenida (comparar primeros 30s vs últimos)","Perfeccionismo vs impulsividad"],
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
  NiWiscRDD:{type:"digits",label:"Retención de Dígitos",sections:[
    {name:"Dígitos Directos",maxItems:8,trials:2,sequences:[
      {len:2,a:"2-9",b:"4-6"},{len:3,a:"3-8-6",b:"6-1-2"},
      {len:4,a:"3-4-1-7",b:"6-1-5-8"},{len:5,a:"8-4-2-3-9",b:"5-2-1-8-6"},
      {len:6,a:"3-8-9-1-7-4",b:"7-9-6-4-8-3"},{len:7,a:"5-1-7-4-2-3-8",b:"9-8-5-2-1-6-3"},
      {len:8,a:"1-6-4-5-9-7-6-3",b:"2-9-7-6-3-1-5-4"},{len:9,a:"5-3-8-7-1-2-4-6-9",b:"4-2-6-9-1-7-8-3-5"}
    ]},
    {name:"Dígitos Inversos",maxItems:8,trials:2,sequences:[
      {len:2,a:"2-5",b:"6-3"},{len:3,a:"5-7-4",b:"2-5-9"},
      {len:4,a:"7-2-9-6",b:"8-4-9-3"},{len:5,a:"4-1-3-5-7",b:"9-7-8-5-2"},
      {len:6,a:"1-6-5-2-9-8",b:"3-6-7-1-9-4"},{len:7,a:"8-5-9-2-3-4-2",b:"4-5-7-9-2-8-1"},
      {len:8,a:"6-9-1-6-3-2-5-8",b:"3-1-7-9-5-4-8-2"}
    ]}
  ]},
  /* ── DÍGITOS WAIS-III ── */
  AdDDir:{type:"digits",label:"Dígitos WAIS-III",sections:[
    {name:"Dígitos Directos",maxItems:8,trials:2,sequences:[
      {len:2,a:"1-7",b:"6-3"},{len:3,a:"5-8-2",b:"6-9-4"},
      {len:4,a:"6-4-3-9",b:"7-2-8-6"},{len:5,a:"4-2-7-3-1",b:"7-5-8-3-6"},
      {len:6,a:"6-1-9-4-7-3",b:"3-9-2-4-8-7"},{len:7,a:"5-9-1-7-4-2-8",b:"4-1-7-9-3-8-6"},
      {len:8,a:"5-8-1-9-2-6-4-7",b:"3-8-2-9-5-1-7-4"},{len:9,a:"2-7-5-8-6-2-5-8-4",b:"7-1-3-9-4-2-5-6-8"}
    ]},
    {name:"Dígitos Inversos",maxItems:7,trials:2,sequences:[
      {len:2,a:"2-4",b:"5-8"},{len:3,a:"6-2-9",b:"4-1-5"},
      {len:4,a:"3-2-7-9",b:"4-9-6-8"},{len:5,a:"1-5-2-8-6",b:"6-1-8-4-3"},
      {len:6,a:"5-3-9-4-1-8",b:"7-2-4-8-5-6"},{len:7,a:"8-1-2-9-3-6-5",b:"4-7-3-9-1-2-8"}
    ]}
  ]},
  /* ── SEMEJANZAS (WISC-IV) — pares de conceptos, 0-1-2 ── */
  NiWiscSem:{type:"scored_items",label:"Semejanzas",scoring:[0,1,2],items:[
    {n:1,pair:"Rueda — Pelota"},{n:2,pair:"Rojo — Azul"},{n:3,pair:"Leche — Agua"},
    {n:4,pair:"Gato — Ratón"},{n:5,pair:"Teléfono — Radio"},{n:6,pair:"Centímetro — Kilogramo"},
    {n:7,pair:"Enojo — Alegría"},{n:8,pair:"Codo — Rodilla"},{n:9,pair:"Pintura — Escultura"},
    {n:10,pair:"Primero — Último"},{n:11,pair:"Olla — Sartén"},{n:12,pair:"Periódico — Revista"},
    {n:13,pair:"Poema — Novela"},{n:14,pair:"Montaña — Lago"},{n:15,pair:"Oxígeno — Vapor"},
    {n:16,pair:"Libertad — Justicia"},{n:17,pair:"Ciudad — Pueblo"},{n:18,pair:"Venganza — Perdón"},
    {n:19,pair:"Sal — Agua"},{n:20,pair:"Hibernación — Migración"},{n:21,pair:"Trabajo — Juego"},
    {n:22,pair:"Emperador — General"},{n:23,pair:"Proporción — Razón"}
  ]},
  /* ── VOCABULARIO (WISC-IV) — 0-1-2 ── */
  NiWiscVoc:{type:"scored_items",label:"Vocabulario",scoring:[0,1,2],items:[
    {n:1,word:"Reloj"},{n:2,word:"Vaca"},{n:3,word:"Sombrero"},{n:4,word:"Bicicleta"},
    {n:5,word:"Paraguas"},{n:6,word:"Ladrón"},{n:7,word:"Alfabeto"},{n:8,word:"Isla"},
    {n:9,word:"Valiente"},{n:10,word:"Absurdo"},{n:11,word:"Antigua"},{n:12,word:"Peligro"},
    {n:13,word:"Migrar"},{n:14,word:"Rivalidad"},{n:15,word:"Precisar"},{n:16,word:"Generar"},
    {n:17,word:"Fábula"},{n:18,word:"Dilema"},{n:19,word:"Inminente"},{n:20,word:"Remordimiento"},
    {n:21,word:"Compasión"},{n:22,word:"Enmienda"},{n:23,word:"Arrogante"},{n:24,word:"Espécimen"},
    {n:25,word:"Acongojado"},{n:26,word:"Rivalidad"},{n:27,word:"Enigma"},{n:28,word:"Erudición"},
    {n:29,word:"Aberración"},{n:30,word:"Prodigio"},{n:31,word:"Tangible"},{n:32,word:"Cónclave"},
    {n:33,word:"Ubérrimo"},{n:34,word:"Dédalo"}
  ]},
  /* ── COMPRENSIÓN (WISC-IV) — 0-1-2 ── */
  NiWiscCom:{type:"scored_items",label:"Comprensión",scoring:[0,1,2],items:[
    {n:1,q:"¿Qué debes hacer si te cortas el dedo?"},{n:2,q:"¿Qué debes hacer si encuentras una billetera?"},
    {n:3,q:"¿Por qué es bueno comer frutas y verduras?"},{n:4,q:"¿Qué debes hacer si ves humo?"},
    {n:5,q:"¿Por qué hay que usar cinturón de seguridad?"},{n:6,q:"¿Por qué es importante ir a la escuela?"},
    {n:7,q:"¿Qué significa 'más vale prevenir que lamentar'?"},{n:8,q:"¿Por qué es importante cumplir las promesas?"},
    {n:9,q:"¿Por qué hay policías?"},{n:10,q:"¿Qué es una constitución?"},
    {n:11,q:"¿Por qué hay impuestos?"},{n:12,q:"¿Por qué es importante la libertad de prensa?"},
    {n:13,q:"¿Qué significa 'quien mucho abarca poco aprieta'?"},{n:14,q:"¿Por qué los jueces son importantes?"},
    {n:15,q:"¿Qué significa 'en boca cerrada no entran moscas'?"},{n:16,q:"¿Por qué se separan los poderes del Estado?"},
    {n:17,q:"¿Qué harías si ves a alguien robando?"},{n:18,q:"¿Por qué es importante el derecho al voto?"},
    {n:19,q:"¿Qué significa copyright?"},{n:20,q:"¿Por qué existen las leyes?"},{n:21,q:"¿Qué es la democracia?"}
  ]},
  /* ── MATRICES (WISC-IV) — 0-1 ── */
  NiWiscMat:{type:"scored_items",label:"Matrices",scoring:[0,1],items:Array.from({length:35},(_, i)=>({n:i+1,q:`Ítem ${i+1}`}))},
  /* ── CONCEPTOS CON DIBUJOS — 0-1 ── */
  NiWiscConD:{type:"scored_items",label:"Conceptos con Dibujos",scoring:[0,1],items:Array.from({length:28},(_,i)=>({n:i+1,q:`Ítem ${i+1}`}))},
  /* ── INFORMACIÓN (WISC-IV) — 0-1 ── */
  NiWisInf:{type:"scored_items",label:"Informacion",scoring:[0,1],items:Array.from({length:33},(_,i)=>({n:i+1,q:`Ítem ${i+1}`}))},
  /* ── ARITMÉTICA (WISC-IV) — 0-1 con tiempo ── */
  NiWiscAri:{type:"scored_items",label:"Aritmetica",scoring:[0,1],items:Array.from({length:34},(_,i)=>({n:i+1,q:`Item ${i+1}`}))},
  /* ── FIGURAS INCOMPLETAS (WISC-IV) — 0-1 ── */
  NiWisFigInc:{type:"scored_items",label:"Figuras Incompletas",scoring:[0,1],items:Array.from({length:38},(_,i)=>({n:i+1,q:`Item ${i+1}`}))},
  /* ── PALABRAS EN CONTEXTO (WISC-IV) — 0-1 ── */
  NiWisPalCon:{type:"scored_items",label:"Palabras en Contexto",scoring:[0,1],items:Array.from({length:24},(_,i)=>({n:i+1,q:`Item ${i+1}`}))},
  /* ── CLAVES — marcado automático por tiempo ── */
  NiWiscCl:{type:"timed_count",label:"Claves",maxTime:120,instruction:"Contar los símbolos correctos copiados en 120 segundos"},
  NiWiscBusSim:{type:"timed_count",label:"Búsqueda de Símbolos",maxTime:120,instruction:"Correctas - Incorrectas en 120 segundos"},
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
  AdWAISV:{type:"scored_items",label:"Vocabulario WAIS-III",scoring:[0,1,2],items:Array.from({length:33},(_,i)=>({n:i+1,q:`Ítem ${i+1}`}))},
  AdSemWais:{type:"scored_items",label:"Semejanzas WAIS-III",scoring:[0,1,2],items:Array.from({length:19},(_,i)=>({n:i+1,q:`Par ${i+1}`}))},
  AdWAISI:{type:"scored_items",label:"Información WAIS-III",scoring:[0,1],items:Array.from({length:28},(_,i)=>({n:i+1,q:`Pregunta ${i+1}`}))},
  AdWAISC:{type:"scored_items",label:"Comprensión WAIS-III",scoring:[0,1,2],items:Array.from({length:18},(_,i)=>({n:i+1,q:`Situación ${i+1}`}))},
  AdMatr:{type:"scored_items",label:"Matrices WAIS-III",scoring:[0,1],items:Array.from({length:26},(_,i)=>({n:i+1,q:`Matriz ${i+1}`}))},
  AdWAISA:{type:"scored_items",label:"Aritmética WAIS-III",scoring:[0,1],items:Array.from({length:20},(_,i)=>({n:i+1,q:`Problema ${i+1}`}))},
  AdWAISFI:{type:"scored_items",label:"Figuras Incompletas WAIS-III",scoring:[0,1],items:Array.from({length:25},(_,i)=>({n:i+1,q:`Lámina ${i+1}`}))},
  AdWAISL:{type:"scored_items",label:"Letras y Números WAIS-III",scoring:[0,1],items:Array.from({length:21},(_,i)=>({n:i+1,q:`Serie ${i+1}`}))},
  /* Velocidad de procesamiento: conteo temporizado */
  AdSDWais:{type:"timed_count",label:"Clave de Números WAIS-III",maxTime:120,instruction:"Símbolos correctos en 120 s"},
  "AdBusSim + ViBusSim":{type:"timed_count",label:"Búsqueda de Símbolos WAIS-III",maxTime:120,instruction:"Correctas - Incorrectas en 120 s"},
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
  Denom48:{type:"scored_items",label:"Denominación 48 ítems",scoring:[0,1],items:Array.from({length:48},(_,i)=>({n:i+1,q:`Ítem ${i+1}`}))},
  BNT:{type:"scored_items",label:"Boston Naming Test",scoring:[0,1],items:Array.from({length:15},(_,i)=>({n:i+1,q:`Lámina ${i+1}`}))},
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
  EscYesavage:{type:"scored_items",label:"Yesavage GDS-15",scoring:[0,1],items:Array.from({length:15},(_,i)=>({n:i+1,q:`Ítem ${i+1}`}))},
  EscBeck:{type:"scored_items",label:"Beck BDI-II",scoring:[0,1,2,3],items:Array.from({length:21},(_,i)=>({n:i+1,q:`Síntoma ${i+1}`}))},
  EscLawton:{type:"scored_items",label:"Lawton AIVD",scoring:[0,1],items:Array.from({length:8},(_,i)=>({n:i+1,q:`AIVD ${i+1}`}))},
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
  "AdBusSim + ViBusSim":{mat:"Cuadernillo de respuestas, lápiz sin borrador, cronómetro.",inst:"Ítems de práctica hasta comprensión. Luego: 'Marque SÍ si alguno de los símbolos de arriba aparece en el grupo. Marque NO si no aparece. Lo más rápido posible.'",disc:"Tiempo: 120 s exactos.",tip:"Completar práctica antes del tiempo cronometrado. Trabajar izquierda a derecha sin saltar. Solo corregir en práctica. Registrar el último ítem al detener el tiempo. Omisiones no restan.",puntaje:"Correctas − Incorrectas. Omisiones no restan. Máx: 60"},
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
