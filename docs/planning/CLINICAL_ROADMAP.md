# NeuroSoft — Roadmap clínico final (v2)

> Informe integrado: modelo clínico de referencia + materiales de capacitación
> internos + investigación de baremos colombianos accesibles +
> protocolos de rehab basados en evidencia. Última revisión: mayo 2026.
>
> **Objetivo**: convertir NeuroSoft en el sistema de neuropsicología
> clínica más completo y clínicamente coherente disponible en Colombia,
> alineado con el flujo clínico estándar y con los estándares Neuronorma /
> Arango-Lasprilla.

---

## Tabla de contenido

1. [Modelo clínico de referencia — qué automatizar](#1-modelo-clínico-ins--qué-automatizar)
2. [Orden clínico de aplicación por protocolo](#2-orden-clínico-de-aplicación-por-protocolo)
3. [Protocolos alternos para casos especiales](#3-protocolos-alternos-para-casos-especiales)
4. [Reglas de análisis e interpretación (WISC, discrepancias, etc.)](#4-reglas-de-análisis-e-interpretación)
5. [Algoritmos diagnósticos por cuadro clínico](#5-algoritmos-diagnósticos-por-cuadro-clínico)
6. [Estímulos visuales faltantes](#6-estímulos-visuales-faltantes)
7. [Pruebas con baremos colombianos accesibles](#7-pruebas-con-baremos-colombianos-accesibles)
8. [Pruebas adicionales que un sistema clínico maduro debe tener](#8-pruebas-adicionales-críticas)
9. [Actividades de rehabilitación cognitiva faltantes](#9-actividades-de-rehabilitación-cognitiva-faltantes)
10. [Formatos administrativos y workflow clínico estándar](#10-formatos-administrativos-y-workflow-ins)
11. [Generación de informes y plantillas](#11-generación-de-informes-y-plantillas)
12. [Mejoras transversales](#12-mejoras-transversales)
13. [Plan priorizado por sprints](#13-plan-priorizado-por-sprints)
14. [Fuentes consultadas](#14-fuentes-consultadas)

---

## 1. Modelo clínico de referencia — qué automatizar opera con un flujo de **4 fases** y un evento de consulta de **90 minutos** (30 min HC + 60 min protocolo). NeuroSoft ya implementa el contenido pero no formaliza el flujo. La interfaz debe seguir las 4 fases explícitamente:

### 1.1 Fase 1 — Recepciónsuario (5 min)
- ✅ Identificación del paciente con cruce de orden + agendamiento.
- ✅ Consentimiento informado activo en NeuroSoft.
- ❌ **Falta**: confirmación obligatoria de identificación con DOC vs orden antes de habilitar la HC.
- ❌ **Falta**: registro de datos de contacto del **acompañante** como entidad separada (hoy se mete texto libre en HC).

### 1.2 Fase 2 — Historia clínica + escalas (25 min)
- ✅ HC con tabs Desarrollo / Antecedentes / Familiar-Social / Plan de Atención.
- ✅ Buscador CIE-10 integrado.
- ❌ **Falta**: campo dedicado para **MC del remitente** vs **MC subjetivo** vs **enfermedad actual** (hoy todo en una caja única). El formatoistema los separa explícitamente.
- ❌ **Falta**: bandeja de **escalas a entregar al acompañante** según motivo (TDAH→SNAP+SCARED; TEA→GADS+M-CHAT; geriátrico→Yesavage+Lawton+Zarit). Hoy las escalas se aplican manualmente; el sistema debería sugerirlas en función del MC y del grupo etario.
- ❌ **Falta**: hipótesis diagnóstica al cierre de la HC, antes de iniciar evaluación cognitiva. Es un campo que existe en pero no en NeuroSoft.

### 1.3 Fase 3 — Evaluación cognitiva (60 min)
- ✅ Selector de protocolo + cronómetro por subprueba.
- ✅ Reactivos ítem-por-ítem.
- ✅ Observaciones por dominio.
- ❌ **Falta crítico**: **orden clínico de aplicación** (ver §2). El ReactivePanel actual sigue el orden del manual editorial; el clínico real aplica en orden de menor a mayor demanda y con interferencia controlada (curva de memoria → llenarlo con otras pruebas → recobro diferido).
- ❌ **Falta**: indicador visual del **tiempo de intervalo de retención** ("Han pasado 18 min desde codificación de Grober. Ya puede aplicar recobro").
- ❌ **Falta**: marcadores de **conductas observadas en el momento** (checkboxes contextuales con CONDUCTAS WISC ya en el sistema), no sólo texto libre.

### 1.4 Fase 4 — Elaboraciónnforme (en simultáneo)
- ✅ Cálculo de scoring + interpretación + impresión diagnóstica.
- ✅ Genera PDF/DOCX/XLSX.
- ❌ **Falta**: marcador de **completitud por sección** (HC ✓, evaluación ✓, observaciones por dominio ⚠ 3/8). El clínico no debería poder enviar un informe con secciones vacías.
- ❌ **Falta**: **modo "informe inconcluso"** con plantillas de redacción específicas (texto sugerido cuando la batería no se completó por motivo X). tiene 4 categorías documentadas: batería completa pero requiere 2da orden / evaluación incompleta / NO evaluación con pruebas recientes / NO evaluación por estado del paciente.

---

## 2. Orden clínico de aplicación por protocolo

> **Esto es la pieza más crítica que falta.** El usuario lo describió: "primero curva de memoria, luego atención, luego ejecutivas, luego recobro". El orden no es estético: respeta la **interferencia** y los **intervalos de retención** de las pruebas de memoria.

### Principio general: estructura de las 60 minutos

```
0:00 Consigna inicial + ubicación del paciente
0:02 CODIFICACIÓN de prueba con recobro diferido
 (Grober & Buschke / HVLT / CVLT / Curva ENI)
0:08 ATENCIÓN de bajo costo verbal (no interfiere con memoria verbal)
 TMT-A, Span dígitos, SDMT, FCRO copia
0:25 FUNCIONES EJECUTIVAS (mayor demanda; interferencia útil)
 Stroop, TMT-B, INECO/Refranes, Go/No-Go
0:35 RECOBRO DIFERIDO de la curva (mín 20-30 min después)
 Grober libre + claves; HVLT delayed; FCRO recobro
0:42 LENGUAJE (Boston/Denominación, Fluidez P + Animales)
0:50 ÍNDICES COMPLEMENTARIOS / pruebas suplementarias
0:58 Cierre + observaciones cualitativas
```

### 2.1 Protocolo Adulto Mayor — Alfabeta (60 min, núcleo Neuronorma + )

| # | Hito | Pruebas | Tiempo |
|---|---|---|---|
| 1 | **Codificación memoria verbal** | Grober & Buschke (16 ítems con clave) o HVLT-R (12 palabras × 3 ensayos) | 6-8 min |
| 2 | **Visoconstrucción** | FCRO copia (sin recobro inmediato) | 4 min |
| 3 | **Atención básica** | TMT-A; Span de dígitos directos WAIS-III; Meses atrás (INECO) | 6 min |
| 4 | **Velocidad** | SDMT (90 s) | 2 min |
| 5 | **Memoria de trabajo** | Span de dígitos en regresión WAIS-III; Dígitos del Neuropsi | 4 min |
| 6 | **Función ejecutiva — verbal** | Refranes (INECO); Semejanzas WAIS | 8 min |
| 7 | **Función ejecutiva — perceptual** | TMT-B; Stroop (palabra → color → interferencia) | 8 min |
| 8 | **Recobro DIFERIDO** (≥20 min desde codificación) | Grober/HVLT recuerdo libre + claves + reconocimiento; FCRO recobro | 6 min |
| 9 | **Lenguaje** | Fluidez P (60 s) + Fluidez animales (60 s); Denominación de Boston (15 ítems) | 6 min |
| 10 | **Memoria remota y reciente** | Preguntas estructuradas (presidente actual, año, etc.) | 2 min |

**Observación**: este orden es lo que ** hace pero NeuroSoft hoy no enfuerza**. El clínico va con su criterio. Una mejora alta-prioridad es: **el sistema marca la prueba siguiente con un "next" automático y bloquea aplicar el recobro antes de los 20 min**.

### 2.2 Protocolo Adulto Joven — Alfabeta (60 min)

| # | Hito | Pruebas |
|---|---|---|
| 1 | Codificación verbal | CVLT (16 palabras × 5 ensayos + lista B + recobro corto) |
| 2 | Visoconstrucción | FCRO copia |
| 3 | Atención y velocidad | Span directo WAIS; SDMT; TMT-A |
| 4 | Memoria de trabajo | Span en regresión; Aritmética WAIS si aplica |
| 5 | Ejecutivas | Stroop; TMT-B; INECO Frontal Screening |
| 6 | Recobro CVLT | Recobro libre largo + claves + reconocimiento |
| 7 | Recobro FCRO | A 30 min de la copia |
| 8 | Lenguaje | Boston (forma corta); Fluidez M y Animales; Semejanzas WAIS |

### 2.3 Protocolo Niños — Estándar (90 min con HC)

Para niños **siempre inicia con CI** (descartar discapacidad global). Luego pruebas complementarias:

| # | Hito | Pruebas |
|---|---|---|
| 1 | Si MC sospecha trastorno cognitivo global | **WISC-IV completo** (15 subtests; la captura ítem-por-ítem ya existe) |
| 2 | Si CI está aplicado <6 meses | Saltar al complementario |
| 3 | Codificación memoria | Curva ENI-2 (4 ensayos) |
| 4 | Atención sostenida + velocidad | TMT-A, CARAS-R, Cancelación de dibujos ENI |
| 5 | Funciones ejecutivas | Fluidez M y Animales; Stroop infantil; Dígitos inversos ENI |
| 6 | Recobro ENI | A 20-30 min |
| 7 | Visoperceptual | FCRO copia + recobro; Integración de objetos; Reconocimiento facial; Figura humana |
| 8 | Lenguaje | Denominación ENI; Comprensión de oraciones |
| 9 | Habilidades académicas | Lectura voz alta; lectura silenciosa; copia de texto; cálculo escrito + mental |

### 2.4 Lo que falta implementar para soportar este orden

- **Campo `orden_aplicacion: int`** en cada prueba de `protos[].tests`. Hoy las pruebas se ordenan según definición; debe respetar el orden clínico, no el editorial.
- **Tipo de hito**: `codificacion | atencion | ejecutiva | recobro | lenguaje | visoespacial | escala | …`. El recobro tiene relación de dependencia con su codificación.
- **Cronómetro de intervalo de retención**: cuando se completa una prueba marcada `codificacion`, arranca un contador. Cuando llegue el momento del `recobro` correspondiente, el sistema avisa: "Recobro disponible — han pasado 22:14 desde codificación".
- **Bloqueo de aplicar recobro antesntervalo mínimo** (configurable, default 20 min).
- **Vista "siguiente prueba sugerida"** en lugar del Sel actual (que muestra todas mezcladas).

---

## 3. Protocolos alternos para casos especiales documenta protocolos alternos en su PDF "Protocolos Alternos para Casos Especiales". NeuroSoft hoy **no los implementa**.

### 3.1 Niños — Forma corta WISC-IV (Sattler 2010)

Cuando el niño tiene discapacidad sensorial o motora se aplica una **forma corta** y se estima el CIT por tabla:

- **Forma corta 1** (no verbal): DC + CD + MT + FI → Tabla Sattler convierte ∑escalares → CIT
- **Forma corta 2** (verbal): VB + SE + CM + PC → Tabla diferente

| Condición | Forma corta usada |
|---|---|
| Discapacidad auditiva (sin verbales) | **Forma corta 1**: DC, CD, MT, FI + opcional Claves+BS para IVP |
| Discapacidad visual (sin visuales) | **Forma corta 2**: VB, SE, CM, PC + opcional Dígitos+Aritmética |
| Visual + auditiva | Priorizar escalas; evaluación cualitativa |
| Motora (sin FCRO ni trazo ni velocidad) | Adaptar protocolo completo |

**Acción NeuroSoft**:
- Cargar la **tabla Sattler 2010** completa (∑escalares 4-76 → CIT corto 1 + CIT corto 2). Está en el PDF, son ~75 filas.
- Agregar selector "Forma corta" en EvalApplyPage que filtre los subtests aplicables.
- En el informe, declarar explícitamente: "Se aplicó Forma Corta 1 (Sattler, 2010) por afectación auditiva. CI estimado: 84 (IC 78-91)".

### 3.2 Adulto joven — Alfabeta con discapacidad

| Condición | Pruebas a aplicar |
|---|---|
| Hipoacusia | CVLT presentación visual; FCRO copia; TMT A-B; Span WAIS; FCRO recobro; **INECO visuales**; Recobro CVLT; Semejanzas WAIS visual; Fluidez M + Animales; Boston |
| Discapacidad visual | Sin pruebas visuales: CVLT; TMT A-B oral; Span; Dígitos Neuropsi; **INECO verbales**; Recobro CVLT; Semejanzas; Fluidez |
| Visual+auditiva | Priorizar escalas; evaluación cualitativa |
| Motora (sin FCRO/trazo/velocidad) | CVLT; TMT oral; SDMT oral; Span; Dígitos; INECO verbales; Recobro CVLT; Semejanzas; Fluidez; Boston; Stroop |

### 3.3 Adulto joven — Analfabeta

| | Pruebas |
|---|---|
| Codificación | **HVLT** (no CVLT — el CVLT requiere alfabetización conceptual) |
| Atención | TMT-A si conoce números; Span WAIS |
| Memoria visual | Casa, Margarita, Reloj (esquema sencillo) |
| Praxias | Gesto simbólico (mano dominante); Mímica y uso de objetos |
| Ejecutivas | INECO completo |
| Lenguaje | Fluidez M y Animales |
| Razonamiento | Semejanzas WAIS |
| Denominación | Boston |

### 3.4 Adulto mayor — Alfabeta con discapacidad

Idéntica estructura al adulto joven pero usa **Grober & Buschke** o **HVLT** según preferencia, e incorpora **INECO con subitems específicos**: Refranes, Meses atrás, Instrucciones conflictivas, Go/No-Go.

### 3.5 Adulto mayor — Analfabeta

| | Pruebas |
|---|---|
| Memoria | HVLT |
| Atención básica | TMT-A si reconoce números; Span; Casa-Margarita-Reloj |
| Praxias | Gesto simbólico; Mímica |
| Ejecutivas | INECO completo (instrucciones conflictivas, Go/No-Go) |
| Lenguaje | Fluidez P y Animales; Denominación |
| Conceptual | Semejanzas; Refranes |

### 3.6 Acción NeuroSoft

- Crear un selector **"Adaptación"** en EvalApplyPage:
 - Estándar
 - Hipoacusia (visual)
 - Visual (auditivo)
 - Visual+auditivo
 - Motor (sin praxias/velocidad)
 - Analfabeta
- Cada adaptación filtra el set de pruebas y carga las **alternativas** (HVLT en lugar de CVLT, etc.).
- En el informe, sección "Limitaciones": indicar la adaptación aplicada con justificación (debe quedar como evidencia clínica para auditoría).

---

## 4. Reglas de análisis e interpretación

### 4.1 Discrepancias WISC-IV (criterio )

NeuroSoft tiene `DISCREPANCY_PAIRS` para significancia estadística. Falta el criterio clínico explícito:

> **Una discrepancia ≥23 puntos (≥1,5 DT) entre índices del WISC-IV invalida el CIT como valor unitario** y obliga a reportar **ICG (Índice de Capacidad General)** o **ICC (Índice de Competencia Cognitiva)** como alternativa (Flanagan & Kaufman, 2009).

**Acción NeuroSoft**:
- Detectar automáticamente `max(ICV,IRP,IMT,IVP) - min(...) ≥ 23`.
- Calcular **ICG** = ∑escalares de Vocabulario, Semejanzas, Comprensión, DC, CD, MT (índice sin las pruebas de velocidad ni MT) → tabla de conversión.
- Calcular **ICC** = ∑escalares de IMT + IVP solamente → tabla.
- En el informe, plantilla automática con texto:

> *"Posterior a la correcta aplicación y calificación de la escala, se identifica que existe discrepancia significativa (>1.5 DT o ≥23 puntos) entre los índices que conforman el CIT (ICV+IRP+IMT+IVP), lo que afecta su uso como valor resumen de la habilidad intelectual global. Por lo anterior, se reporta el ICG (X) y el ICC (Y) como alternativas (ver: Flanagan & Kaufman, 2009)."*

### 4.2 Conductas a observar (ya parcial — escalar)

NeuroSoft tiene `CONDUCTAS` por test_id (texto libre como guía). El clínico real **marca** conductas específicas durante la aplicación. Mejora:

- Cada conducta de CONDUCTAS se vuelve un **checkbox** con texto auto-rellenado.
- Al cierreubtest, las conductas marcadas se incorporan al informe con plantilla:
 > "Durante la aplicación de Diseño con Cubos, el paciente mostró: estilo de resolución por ensayo y error, sin estrategia previa de planeación; consulta constante del modelo (sugiere baja memoria visual o cautela); torpeza motora bilateral; perseverancia adecuada ante la frustración."

### 4.3 Reglas de redacción específicas para niños

Del PDF Informe NPS WISC :
- **NUNCA usar "conserva" o "preserva"** en niños → usar "muestra adecuado desarrollo de…"
- Usar prefijo **DIS-** en lugar de **A-** (disfasia, no afasia; disgrafía, no agrafía).
- **NO repetir información de las gráficas en el texto**.
- **NO hablar de la prueba** sino de **la función cognitiva** ("muestra dificultad para mantener información verbal en línea para operar con ella" — no "obtuvo PD bajo en Aritmética").
- **Análisis bottom-up funcional** (de elemental a complejo).

NeuroSoft ya tiene `GUIA_INFORME` con muchas de estas reglas. Falta:
- Validador automático que detecte palabras prohibidas en informes pediátricos ("conserva", "afasia", "agrafía") y las marque al clínico antes de enviar.

---

## 5. Algoritmos diagnósticos por cuadro clínico maneja algoritmos por cuadro. NeuroSoft tiene `DIAGNOSTIC_ALGORITHMS` y `evaluarAlgoritmo` pero la cobertura es limitada. Lista de cuadros con criterios:

### 5.1 TDAH (Trastorno por Déficit de Atención e Hiperactividad)
- **Criterios DSM-5**: 6+ síntomas inatentos y/o 6+ hiperactivos-impulsivos por ≥6 meses, en ≥2 contextos, antes de los 12 años.
- **Escalas requeridas**: SNAP-IV (padres + maestros), SCARED (ansiedad comórbida), Conners-3, Vanderbilt, ASRS-v1.1 (adulto), BRIEF-2.
- **Perfil cognitivo esperado**:
 - ↓ Atención sostenida (Claves, Búsqueda Símbolos, CARAS-R)
 - ↓ MT (Span regresión, Aritmética)
 - ↓ Inhibición (Stroop interferencia, Go/No-Go)
 - ↓ Velocidad de procesamiento
 - **NO hay** déficit en CIT ni en visoperceptual primario
- **TCL (Tempo Cognitivo Lento)** como subtipo: lentificación + ensoñación + bajo arousal sin hiperactividad.

### 5.2 Discapacidad intelectual / Trastorno del desarrollo intelectual
- **Criterios**: CIT <70 en dos pruebas válidas + limitaciones adaptativas (Vineland, ABAS) + inicio antes de 18 años.
- **Niveles**: Leve (50-70), Medio (35-50), Severo (20-35), Profundo (<20).
- **Limítrofe**: 71-84.
- **Pruebas**: WISC-IV/WAIS-III + Vineland-3 + ABAS-3.

### 5.3 TEA (Trastorno del Espectro Autista) — DSM-5
- **Dos categorías**:
 1. Deficiencias en comunicación social
 2. Comportamientos restringidos y repetitivos (incluye sensibilidad sensorial)
- **Especificadores**: con/sin discapacidad intelectual; con/sin alteraciónenguaje; con/sin condición médica; nivel de severidad 1-2-3.
- **Escalas**: GADS, M-CHAT, ADOS-2, ADI-R, SCQ.
- **NeuroSoft tiene el manual GADS completo** (3352 líneas extraído del PDF) — implementar como prueba calificable.

### 5.4 DEA (Dificultades Específicas del Aprendizaje) — DSM-5
Tres criterios:
1. **Exclusión** — descartar otras causas (sensorial, motor, emocional, deprivación).
2. **Discrepancia** — desempeño académico ≥1-2 años bajo lo esperado para edad/escolaridad/CI.
3. **Especificidad** — dificultad limitada a 1-2 áreas (lectura/escritura/cálculo).

**Especificadores DSM-5**: con dificultad en lectura (dislexia), expresión escrita (disgrafía), matemática (discalculia).

### 5.5 TCL → TCM (Trastorno Cognitivo Leve / Mayor) — DSM-5
- **TCL**: declive **moderado** en ≥1 dominio cognitivo, NO interfiere con autonomía AVD.
- **TCM**: declive **significativo**, INTERFIERE con autonomía.
- **Criterios DCL Petersen**:
 1. Queja subjetiva (paciente o informante)
 2. Alteración objetiva en pruebas (≥1 DT bajo)
 3. Funcionalidad básicamente preservada
 4. NO demencia
- **Subtipos DCL**:
 - Amnésico simple (memoria sólo)
 - Amnésico múltiple
 - No-amnésico simple
 - No-amnésico múltiple
- **Tasa de conversión a demencia**: 25-45% a 5 años; tipo más frecuente Demencia Vascular y EA.

### 5.6 Secuelas cognitivas COVID-19 (long COVID)
- **Niebla mental**: ≥12 semanas post-infección.
- **Perfil afectado**:
 - Velocidad de procesamiento (la más afectada)
 - Funciones ejecutivas (inhibición, resolución problemas)
 - Recuperación de información verbal
 - Memoria a corto plazo
- **Pruebas recomendadas**: MoCA + WAIS-IV/III + protocolo Neuronorma.

### 5.7 Trastornos del estado de ánimo y ansiedad (impacto cognitivo)
- **Depresión mayor** (prevalencia Colombia 25.3%): ↓ FE (resolución problemas), atención, VP, memoria visual y verbal.
- **Ansiedad** (14.6%): ↓ atención y FE (MT, inhibición cognitiva).
- **Uso de sustancias** (9.6%): ↓ atención, MT, memoria episódica y semántica.
- **Acción NeuroSoft**: incorporar PHQ-9 + GAD-7 (escalas libres) como tamización rutinaria.

### 5.8 Acción NeuroSoft

NeuroSoft tiene `evaluarAlgoritmo`. Expansión necesaria:
- Cada cuadro arriba como JSON estructurado: criterios mínimos + pruebas requeridas + perfil esperado.
- Output estructurado: probabilidad estimada (alta/media/baja) + qué falta para cerrar el diagnóstico + diagnóstico diferencial.
- En el informe, sección **"Hipótesis diagnóstica"** se rellena automáticamente desde el algoritmo.

---

## 6. Estímulos visuales faltantes

### 6.1 Estado actual
- Estímulos nativos SVG: 10 (`AdFCRORec, AdWAISCC, MMSE, NiFCROCop, NiFCRORec, NiFigHum, NiTMTA, NiTMTB, NiWiscDC, NiWiscMat`).

### 6.2 Estímulos críticos por crear (SVG nativos, sin reproducir cuadernillos editoriales)

| Test | Estímulo |
|---|---|
| `NiWiscCl` / Claves WISC-IV | Plantilla pareo 9 dígitos→9 símbolos + 2 ítems de práctica |
| `NiWiscBusSim` / Búsqueda de Símbolos | Página de filas con target a la izquierda y opciones a la derecha |
| `AdSDWais` / Clave de Números WAIS-III | Idéntica estructura a Claves |
| `SDMT` / Symbol Digit Modalities | Reusable de Claves |
| `NiWisFigInc` / Figuras Incompletas (24 ítems) | Dibujos esquemáticos con detalle ausente |
| `AdWAISFI` / Figuras Incompletas WAIS | Idéntico enfoque |
| `NiWiscConD` / Conceptos con Dibujos | Filas de 2-3 dibujos por categoría conceptual |
| `NiWisPalCon` / Palabras en Contexto | Cuadrículas de 4 imágenes para pareo |
| `AdMatr` / Matrices WAIS-III | 26 matrices con celda faltante (geometría pura) |
| `NiIntObj` / Integración de Objetos | "Rompecabezas" recortados desordenados |
| `NiRecEmo` / Reconocimiento Expresiones | 6 caras esquemáticas (Ekman básicas) |
| `NiSt_Edades` / Stroop infantil | 3 láminas: palabras en negro / cuadros color / interferencia |
| `StroopAM`, `StroopAJ` | Idéntico patrón |
| `NiTestPC_R` / CARAS-R | Filas de caras con expresiones para tachar la diferente |
| `NiENICDib` / Cancelación Dibujos | Hoja con N targets a tachar entre distractores |
| `Denom48` / Denominación 48 ítems | Galería de 48 dibujos libres de copyright |
| `MMSE` ítem visoconstructivo | Pentágonos modelo |

### 6.3 Material disponible en la carpeta de capacitación

La carpeta tiene PDFs como referencia visual:
- `Informe NPS WISC .pdf` — ejemplo de tabla de subtests con valores
- `WISC IV TDAH y tempo cognitivo lento.pdf` — análisis subtest-por-subtest con conductas
- `GADS Manual.pdf` — manual completo de Gilliam Autism Scale (calificable)

**Acción**: ampliar `src/data/stimuli.jsx` con los 17 estímulos prioritarios. Cada uno como SVG paramétrico (`tamaño`, `color`, etc.). Mantener el principio: "Dibujos propios, NO reproducción de reactivos editoriales".

---

## 7. Pruebas con baremos colombianos accesibles

### 7.1 Neuronorma Colombia (Montañés-UNAL & Peña-Casanova) — 50-90 años

Batería de **12 tests** con baremos colombianos validados:
- Boston Naming Test (BNT)
- FCSRT (Free and Cued Selective Reminding) ← **Falta en NeuroSoft, sucesor de Grober**
- Fluidez semántica (animales) y fonológica (P)
- Stroop
- Rey-Osterrieth (copia y memoria)
- SDMT
- TMT A-B
- Tower of London ← **Falta en NeuroSoft**
- Token Test ← **Falta en NeuroSoft**
- Span de Dígitos (forward/backward) WAIS-III
- Cubos de Corsi ← **Falta en NeuroSoft**
- WCST modificada (M-WCST)

**Acción**: agregar `FCSRT, Tower of London, Token Test, Cubos de Corsi` a `REACTIVOS` y al baremo `BD_NEURO_MAESTRA.json` con datos NN.Co.

### 7.2 Arango-Lasprilla & Rivera (2015-2017) — multicentrico LATAM

5,402 adultos sanos 18-90 + 4,373 niños de 12 países (incluye Colombia). Cubre:
- HVLT-R (Hopkins Verbal Learning) ← **Ya parcial; usar baremos LATAM**
- BVMT-R (Brief Visuospatial Memory) ← **Falta**
- Rey-Osterrieth, Stroop, M-WCST, TMT
- Brief Test of Attention (BTA) ← **Falta**
- Fluidez fonológica + semántica
- BNT
- Pediátrico: TMT pediátrico, ROCF infantil, fluidez infantil

**Acción**: incorporar baremos Arango-Lasprilla **18-49 años** que es el rango hoy más débil en NeuroSoft (sólo 30 entradas vs 92 infantil).

### 7.3 Otras pruebas baremadas en Colombia

| Prueba | Baremo Colombia | Estado en NeuroSoft |
|---|---|---|
| MoCA-S | Pedraza et al. 2014/2016 (UNAL/Bogotá) — corte 20/21 MCI, 17/18 demencia | ✅ presente parcial; agregar cortes ajustados por escolaridad |
| BANFE-2 | Manual Moderno (Flores, Ostrosky, Lozano) — universitarios + niños | ❌ Falta |
| NEUROPSI Atención y Memoria 3a ed | Ostrosky — estandarizado en México **y Colombia**, 6-85 años | ❌ Falta — gran prueba de tamización |
| NEUROPSI Breve | Ostrosky | ❌ Falta — más rápida que la versión completa |
| CERAD-Col | Aguirre-Acevedo et al. (Antioquia) | ❌ Falta — gold standard tamización demencia |
| FDT (5 dígitos, Sedó) | Manual TEA-Hogrefe — incluye normas Colombia | ❌ Falta — alternativa al Stroop sin lectoescritura |
| TVIP (Peabody hispano) | Dunn et al. | ❌ Falta — vocabulario receptivo niños |
| K-BIT (Kaufman Brief Intelligence) | Pearson | ❌ Falta — tamización CI rápida |
| ENI-2 (5-16 años) | Matute, Rosselli, Ardila, Ostrosky 2013 | ✅ ya presente |
| ENI-Preescolar (3-5 años) | Matute et al. 2021 | ❌ Falta — preescolar es un hueco enorme |
| Bayley-III | — | ❌ Falta — desarrollo bebés/preescolares |

### 7.4 Pruebas internacionales libres

| Prueba | Licencia | Acción |
|---|---|---|
| MoCA | Public domain con registro gratuito | Verificar registro institucional |
| TMT-A/B | De facto público | OK ya |
| Mesulam SCT | Recreable (60 targets entre 300) | Implementable |
| Frontal Assessment Battery (FAB) | Publicación libre Dubois 2000 | Implementable |
| Brief Cognitive Assessment Tool (BCAT) | — | Implementable |
| Mini-Cog | Public domain | Implementable |
| PHQ-9 / GAD-7 | Public domain | **Implementable inmediato** |

---

## 8. Pruebas adicionales críticas

### 8.1 Cobertura adulto joven (18-49) — gran hueco
- **WAIS-IV Colombia** (Pearson 2014) — sucesora del WAIS-III; añade Visual Puzzles, Figure Weights, Cancellation
- **WMS-IV** — gold standard memoria adulto
- **D-KEFS** — 9 subtests ejecutivos
- **TAVEC** — Test Aprendizaje Verbal España-Complutense
- **Iowa Gambling Task (IGT)** — toma de decisiones
- **Hayling y Brixton** — control inhibitorio
- **Pirámide y la Palmera** — semántica conceptual

### 8.2 Cobertura preescolar (3-5 años) — gran hueco
- ENI-Preescolar
- WPPSI-IV (2:6-7:7)
- K-ABC-II preescolar
- Bayley-III
- EVENFE — funciones ejecutivas niños

### 8.3 Pruebas afasiológicas
- WAB-R (Western Aphasia Battery) — gold standard afasias
- BDAE (Boston) — subtipos afasia
- Token Test corto (ya mencionado en NN.Co)
- PALPA — procesamiento psicolingüístico

### 8.4 Pruebas atencionales especializadas
- CPT-3 / Conners CPT — sostenida y vigilancia
- TOVA — visual y auditiva
- BTA — Brief Test of Attention
- PASAT — atención dividida y velocidad

### 8.5 Escalas de estado emocional (LIBRES, alta prioridad)

| Prueba | Uso | Estado |
|---|---|---|
| **PHQ-9** | Depresión primer nivel | ❌ Falta — libre, 9 ítems |
| **GAD-7** | Ansiedad primer nivel | ❌ Falta — libre, 7 ítems |
| Beck Ansiedad (BAI) | Ansiedad | ❌ Falta |
| HADS (Hospital Anxiety Depression) | Comórbida | ❌ Falta |
| **SNAP-IV** (padres + maestros) | TDAH niño | ❌ Falta — libre, la usa |
| **SCARED** | Ansiedad niño | ❌ Falta — libre, la usa |
| **GADS** | TEA niño | ❌ Falta — manual completo en carpeta |
| **M-CHAT-R/F** | TEA tamización 16-30 meses | ❌ Falta — libre |
| Conners-3 | TDAH niño/adolescente | ❌ Falta |
| Vanderbilt | TDAH primaria | ❌ Falta |
| BRIEF-2 | Ejecutivas vida diaria | ❌ Falta |
| ADI-R / ADOS-2 / SCQ | TEA gold standard | ❌ Falta |
| MMPI-2-RF / MCMI-IV | Personalidad | ❌ Falta |

### 8.6 Pruebas de validez de síntomas (esfuerzo / simulación)
- **TOMM** (Test of Memory Malingering) — ya en baremos NN.Co pero no en `REACTIVOS`
- Rey 15-item Test
- Word Memory Test
- Reliable Digit Span (derivapan ya capturado)

### 8.7 Escalas funcionales y calidad de vida
- **Lawton & Brody (AIVD)** — ✅ presente parcial
- **Barthel** (ABVD) — ❌ Falta
- **FAQ** (Functional Activities Questionnaire) — ❌ Falta
- **CDR** (Clinical Dementia Rating) — ❌ Falta — gold standard severidad demencia
- **Zarit** — sobrecargauidador — ❌ Falta — la pide en geriátrico
- **NPI-Q** (Neuropsychiatric Inventory) — ❌ Falta
- **EQ-5D** / SF-12 — ❌ Falta

---

## 9. Actividades de rehabilitación cognitiva faltantes

### 9.1 Estado actual: 4 actividades
`stroop, n_back, fluency_verbal, tachado`

### 9.2 ATENCIÓN — Modelo APT (Sohlberg & Mateer)
4 niveles jerárquicos (sostenida → selectiva → alternante → dividida):

| Nivel | Actividad | Estado |
|---|---|---|
| Sostenida | Reaction Time simple — clic ante target aleatorio cada 2-30s | ❌ |
| Sostenida | CPT — letras/imágenes velocidad alta, responder al target | ❌ |
| Selectiva | Cancelación targets entre distractores | ✅ `tachado` |
| Selectiva | Visual search con distractores progresivos | ❌ |
| Alternante | Cambio de regla auditiva ("ahora suma; ahora resta") | ❌ |
| Alternante | Stroop alternante | ❌ |
| Dividida | Dual-task: tachado + serie auditiva paralela | ❌ |
| Dividida | PASAT computarizada | ❌ |

### 9.3 MEMORIA (mayor evidencia clínica)

| Actividad | Técnica | Estado |
|---|---|---|
| **Spaced Retrieval Training** (SRT) — recordar item con intervalos crecientes (30s, 1m, 2m, 4m, 8m) | Bourgeois 1990; gold standard demencia leve | ❌ |
| **Errorless Learning** (vanishing cues) | Wilson 1994 | ❌ |
| **Method of Loci** (palacio de la memoria) | Mejora capacidad MT | ❌ |
| **Reconocimiento facial** | Nombre-cara con SRT | ❌ |
| **Asociación verbal-imagen** | Pareo con feedback inmediato | ❌ |
| **Diario electrónico / agenda externa** | Compensatorio TBI | ❌ |
| **Dual N-back** visual+auditivo | Jaeggi 2008 | ✅ parcial |
| **Recuerdo prospectivo** | Planificar tarea con alarma a 5 min | ❌ |

### 9.4 FUNCIONES EJECUTIVAS

| Actividad | Estado |
|---|---|
| Tower of London / Tower of Hanoi | ❌ |
| Categorización con cambio de regla (estilo WCST) | ❌ |
| Iowa Gambling Task simplificada | ❌ |
| Go/No-Go progresivo | ❌ |
| Stop Signal Task | ❌ |
| Set-shifting | ❌ |
| Multitasking (objetivos paralelos con tiempo) | ❌ |
| Resolución de problemas en escenario | ❌ |
| Fluencia verbal con restricciones | ✅ parcial |

### 9.5 LENGUAJE / SEMÁNTICA

| Actividad | Estado |
|---|---|
| Denominación con jerarquía de claves (fonológica → semántica → pareada) | ❌ |
| Comprensión instrucciones progresivas (1→3 pasos) | ❌ |
| Lectura comprensiva con preguntas | ❌ |
| Categorización semántica | ❌ |
| Sinónimos / antónimos | ❌ |
| Refranes y abstracción | ❌ |

### 9.6 VISOESPACIAL / VISOCONSTRUCTIVO

| Actividad | Estado |
|---|---|
| Mental Rotation | ❌ |
| Reconocimiento líneas (Benton) | ❌ |
| Construcción de patrones (cubos digitales) | ❌ |
| Búsqueda visual lateralizada (heminegligencia) | ❌ |
| Copia de figura compleja progresiva | ❌ |
| Reconocimiento objetos en perspectivas atípicas | ❌ |

### 9.7 COGNICIÓN SOCIAL

| Actividad | Estado |
|---|---|
| Reconocimiento expresiones faciales (Ekman 6) | ❌ |
| Reading the Mind in the Eyes | ❌ |
| Faux pas test | ❌ |
| Inferencia de emociones por escenario | ❌ |

### 9.8 AVD COGNITIVAS (transferencia ecológica)

| Actividad | Estado |
|---|---|
| Manejo de dinero (vuelto + presupuesto) | ❌ |
| Lectura de etiquetas de medicamentos | ❌ |
| Planificación día simulado (compras → ruta → tiempos) | ❌ |
| Lectura de mapa / instrucciones | ❌ |

---

## 10. Formatos administrativos y workflow clínico estándar

Del PDF "Manual de uso formatos" — formatos que usa y NeuroSoft NO automatiza:

| Formato | Cuándo se usa | Estado NeuroSoft |
|---|---|---|
| **Consentimiento informado, derechos, deberes y manejo de datos** | Siempre | ✅ presente |
| **Consentimiento informado + contrato terapéutico** (rehab) | Inicio rehab | ❌ Falta — usar el consentimiento de evaluación, no es lo mismo |
| **Autorización entrega de informes a terceros** | Cuando solicitan envío a otra persona | ❌ Falta |
| **Declaración de retiro voluntario** | Paciente decide retirarse mid-consulta | ❌ Falta |
| **Declaración de retiro voluntario por motivos de salud** | Paciente se enferma durante consulta | ❌ Falta |
| **Volante de entrega de informe** | Cierre de consulta — explica cómo recibirá el informe | ❌ Falta |
| **Recibido informe en físico** | Paciente recoge informe impreso | ❌ Falta |
| **Reporte evento adverso** | Cuando ocurre incidente que afecta al paciente | ❌ Falta |
| **Declaración retiro de datos en investigación** | Paciente revoca consentimiento research | ❌ Falta |
| **Reporte de situaciones irregulares** | SAU o asistencial reportan incidente | ❌ Falta |
| **PQRS** (Petición, Queja, Reclamo, Sugerencia) | Usuario manifiesta inconformidad | ❌ Falta |

**Acción**: módulo "Formatos administrativos" en `src/app/config/` o sidebar dedicado, que genere PDFs precargados desde la HC actual (paciente, fecha, profesional) y los guarde como anexos auditables al evento.

---

## 11. Generación de informes y plantillas

### 11.1 Estructuranforme (del PDF "Informe guía WISC")

```
1. Información sociodemográfica
 - Nombre completo, documento, edad, escolaridad, ocupación
 - Fecha nacimiento, ciudad, acompañante (con relación)
 - Lateralidad
 - Remite (profesional + entidad)

2. Antecedentes médicos y comportamentales
 2.1 Motivo de consulta
 - MC del remitente (entre comillas + entidad)
 - Queja subjetivasuario o acompañante (entre comillas)
 - Enfermedad actual
 2.2 Desarrollo (gestación, parto, neonatal, hitos motor/lenguaje/esfínteres)
 2.3 Médicos: Patológicos, Sensoriales/Motores, Alérgicos, Tóxicos,
 Psiquiátricos, Terapéuticos, Farmacológicos, Traumáticos,
 Quirúrgicos, Familiares, Paraclínicos
3. Familiar / Social / Funcional
 - Vive con
 - ABC (auto-cuidado, alimentación, higiene)
 - Escolar / Laboral
 - Funciones cognitivas (queja en vida diaria)
 - Comportamiento / Ánimo
 - Patrón de Sueño
 - Patrón de Alimentación

4. Observación clínica (apariencia + actitud + colaboración + lenguaje)

5. Resultados (tabla con PD + PE + interpretación por subtest)
 5.1 Atención
 5.2 Memoria
 5.3 Praxias / Gnosias
 5.4 Lenguaje
 5.5 Funciones ejecutivas
 5.6 Funcionalidad / habilidades adaptativas

6. Tabla de índices (CIT, ICV, IRP, IMT, IVP, ICG si aplica)

7. Impresión diagnóstica
 - Diagnóstico principal CIE-10
 - Diagnósticos diferenciales considerados
 - Justificación clínica

8. Recomendaciones
 - Específicas por área
 - Remisiones
 - Seguimiento

9. Firmas (profesional + datos institucionales + sello)
```

NeuroSoft genera la mayoría pero falta:
- ❌ Separación explícita MC del remitente / MC subjetivo / Enfermedad actual.
- ❌ Sección "Funciones cognitivas" en queja subjetiva (lo que el paciente refiere de su cognición en vida diaria).
- ❌ Reservorio de **plantillas de redacción por dominio cognitivo** (NeuroSoft tiene `OBS_TEMPLATES` pero las maneja como banco editable más rico).
- ❌ Validador de palabras prohibidas en informe pediátrico (ya mencionado).
- ❌ **Reservorio de recomendaciones por cuadro clínico** ( tiene un docx específico — extraer y normalizar).

### 11.2 Reservorio de recomendaciones El archivo `Reservorio de recomendaciones de acuerdo a cuadro clínico .docx` (no extraído por estar en formato Office) contiene plantillas de recomendaciones por:
- TDAH
- TEA
- DEA (dislexia/disgrafía/discalculia)
- DCL/TCM
- Discapacidad intelectual
- Secuelas TCE
- Cuadros depresivos
- Cuadros ansiosos
- Long COVID
- Demencias

**Acción**: extraer este reservorio y cargarlo a `RECOMMENDATIONS_LIB` con keys por cuadro CIE-10 + edad + severidad.

### 11.3 Plantillas adicionales necesarias

NeuroSoft tiene `REPORT_TEMPLATES` con 4 (clinico, ejecutivo, escolar, geriátrico). Faltan:

| Plantilla | Uso |
|---|---|
| **Pediátrico bilingüe** | Versión simple para padres + versión técnica para colegio |
| **Junta médica** | Formato corto, conclusiones + recomendaciones numeradas |
| **Pre-pensión / Discapacidad** | Para procesos legales (Sanitas, Famisanar) |
| **Re-test / Control** | Comparación pre-post con RCI |
| **Telesalud** | Formato firmado digitalmente con QR de verificación |
| **Inconcluso** | Plantilla específica con texto sugerido por categoría |

---

## 12. Mejoras transversales

### 12.1 Sistema de baremos múltiples
Hoy `BD_NEURO_MAESTRA.json` es único archivo. Idealmente:
```
src/data/baremos/
 ├── neuronorma_colombia.json (50-90 años)
 ├── arango_lasprilla_2015.json (18-90 multicéntrico)
 ├── eni_2_colombia.json (5-16 años)
 ├── wisc_iv_colombia.json (Pearson)
 ├── wisc_iv_sattler_short.json (formas cortas)
 └── … etc.
```
El motor de scoring elige fuente según edad + escolaridad + protocolo + adaptación. **Trazabilidad**: cada resultado en informe lleva qué baremo usó.

### 12.2 Sistema de identidad clínica de la prueba
Cada prueba (`REACTIVOS`) debe llevar:
```js
{
 id: "NiWiscDC",
 nombre: "Diseño con Cubos",
 protocolo: "WISC-IV",
 dominio_cognitivo: "Visoespacial / Razonamiento Perceptual",
 hito: "visoespacial",
 orden_aplicacion: 4,
 baremo_default: "wisc_iv_colombia",
 baremos_alternativos: ["arango_lasprilla_2015"],
 tiempo_min_aplicacion: 5, // minutos
 tiempo_max_aplicacion: 15,
 requiere_estimulo_visual: true,
 conductas_observar: [...],
 adaptaciones: {
 hipoacusia: { aplicable: true, modificacion: "instrucciones por escrito" },
 visual: { aplicable: false },
 motora: { aplicable: false }
 },
 intervalo_minimo_recobro: null // sólo en pruebas de codificación
}
```

### 12.3 Indicadores e KPIs clínicos
Indicadores que monitorea (de "Inconclusos guide"):
- ✅ % evaluaciones completas (vs inconclusos)
- ✅ Tiempo entre consulta y envío de informe (target: ≤10 días hábiles)
- ❌ Tiempo total de la consulta (90 min target)
- ❌ % de informes con diagnóstico vs incompletos
- ❌ Distribución diagnóstica (top-N CIE-10 por mes)
- ❌ Productividad por profesional (informes/mes)

**Acción**: dashboard administrativo (rol coordinación) con estas métricas.

### 12.4 Discrepancia y RCI
- Calcular **ICG** y **ICC** automáticamente cuando discrepancia ≥23 puntos.
- **Reliable Change Index** para comparación pre-post (no solo delta-Z).
- **Tabla de prevalencia** de discrepancias (no solo significancia).

### 12.5 Detección de simulación / esfuerzo
- TOMM digital (50 ítems, 2 trials + retención)
- Reliable Digit Span (extraídopan ya capturado)
- Curva de aprendizaje atípica en RAVLT/HVLT
- Performance > expected en pruebas fáciles (efort symbol detection)

### 12.6 Telerehabilitación
- Notificación al clínico cuando paciente completa sesión home.
- Dashboard de adherencia con alertas (3 días sin sesión → reminder).
- Mensajería cifrada paciente↔clínico.
- Captura tiempo total + pausas + tiempo por ítem.

### 12.7 Habeas Data avanzado
- Anonimización para investigación (k-anonimato).
- Consentimiento granular: investigación / docencia / telesalud opt-in/opt-out independiente.

### 12.8 Accesibilidad
- Modo alto contraste para baja visión.
- Lectores de pantalla en formularios.
- Escalado fuente independiente del SO.
- Modo "evaluación a domicilio" con conexión limitada.

### 12.9 Soporte para asesoría entre profesionales menciona "se solicita asesoría en caso de ser necesario" como parte del flujo. Implementar:
- Botón "Solicitar segunda opinión" en EvalResultsPage que comparte el caso (anonimizado o con permiso) con un colega registrado.
- Hilo de chat por caso.
- Marca el caso como "en revisión" hasta que el revisor cierre.

---

## 13. Plan priorizado por sprints

### Sprint 1 — Quick wins clínicos (1 semana)
1. **Separar MC remitente / MC subjetivo / Enfermedad actual** en HC.
2. **PHQ-9 + GAD-7** como escalas libres en pestaña `escalas`.
3. **Validador de palabras prohibidas** en informes pediátricos.
4. **Reservorio de recomendaciones ** cargado en `RECOMMENDATIONS_LIB`.
5. **Volante de entrega + Retiro voluntario** como formatos administrativos en config.

### Sprint 2 — Orden clínico de aplicación (2 semanas)
1. Schema `orden_aplicacion` + `hito` + `intervalo_minimo_recobro` en cada prueba.
2. Sub-header de EvalApplyPage muestra **prueba siguiente sugerida**.
3. Cronómetro de **intervalo de retención** entre codificación y recobro.
4. Bloqueo de aplicar recobro antesntervalo mínimo.

### Sprint 3 — Protocolos alternos (1 semana)
1. Selector de **adaptación** (estándar / hipoacusia / visual / mixta / motora / analfabeta).
2. Tabla **Sattler 2010** completa para formas cortas WISC-IV.
3. Cálculo automático de CIT-corto y declaración en informe.

### Sprint 4 — Discrepancia ICG/ICC + RCI (1 semana)
1. Detección automática de discrepancia ≥23 puntos.
2. Cálculo ICG e ICC con tabla de conversión.
3. Plantilla de redacción automática.
4. RCI para pre-post.

### Sprint 5 — Estímulos críticos (2 semanas)
1. Crear los 17 SVG nativos prioritarios.
2. Vincular cada uno al test correspondiente en `NativeStimuli`.
3. Mostrar en EvalApplyPage como referencia.

### Sprint 6 — Pruebas faltantes priorizadas (3 semanas)
1. **FCSRT** (sucesor de Grober, baremos NN.Co listos)
2. **Cubos de Corsi** digital
3. **Tower of London** digital
4. **Token Test** corto
5. **GADS** calificable (manual ya en carpeta )
6. **SNAP-IV + SCARED + Vanderbilt** (escalas libres TDAH/ansiedad niño)
7. **Zarit** (escala cuidador)
8. **CDR** (Clinical Dementia Rating)

### Sprint 7 — Algoritmos diagnósticos completos (2 semanas)
1. Expandir `DIAGNOSTIC_ALGORITHMS` con TDAH, TEA, DEA, DCL/TCM, Long COVID, Depresión, Ansiedad.
2. Output estructurado: probabilidad + faltantes + diferenciales.
3. Auto-rellenado de "Hipótesis diagnóstica" en informe.

### Sprint 8 — Rehab cognitiva ampliada (4 semanas)
1. **Spaced Retrieval Training** (mayor evidencia demencia leve).
2. **Errorless Learning** con vanishing cues.
3. **Mental Rotation**.
4. **Reconocimiento expresiones Ekman**.
5. **Tower of London** rehab mode.
6. **Continuous Performance Task (CPT)**.
7. **Method of Loci** asistido.
8. **AVD ecológicas** (3-4 escenarios).

### Sprint 9 — Sistema de baremos múltiples (2 semanas)
1. Refactor `BD_NEURO_MAESTRA.json` → `src/data/baremos/*.json`.
2. Trazabilidad: cada resultado lleva qué baremo usó.
3. Cargar Neuronorma Colombia + Arango-Lasprilla 2015.

### Sprint 10 — Telerehab + adherencia (2 semanas)
1. Notificación al clínico cuando paciente completa sesión home.
2. Dashboard adherencia con alertas.
3. Mensajería cifrada.

### Sprint 11 — Indicadores y dashboard administrativo (1 semana)
1. Tiempo consulta + tiempo informe por profesional.
2. Distribución diagnóstica.
3. Productividad.
4. Vista para rol coordinación.

### Sprint 12 — Pruebas avanzadas y refinamiento (3 semanas)
1. **NEUROPSI Atención y Memoria** (estandarizado Colombia, Manual Moderno).
2. **CERAD-Col** (Aguirre-Acevedo).
3. **BANFE-2** integración con baremos.
4. **TOMM** + indicadores de validez.
5. **Plantillas de informe**: pediátrico bilingüe, junta médica, pre-pensión, re-test, telesalud, inconcluso.

---

## 14. Fuentes consultadas

### Materiales internos (carpeta de capacitaciones)
- *Modelo clínico de referencia* — [autor], [revisor] (Dirección Clínica, 29/oct/2024).
- *Algoritmos diagnósticos en NPS infantil* — Dirección Clínica.
- *Protocolos Alternos para Casos Especiales* — 2024.
- *Análisis de Discrepancias WISC IV * — V.1.
- *Manual Protocolo de atención al usuario Neuropsicología 2025* — Dirección Clínica.
- *Manual de uso formatos* — Comité HC.
- *Guía de manejo de informes inconclusos* — [autor] (21/mar/2024).
- *Informe NPS WISC * + *Informe guía WISC * — Coordinación Clínica.
- *WISC IV TDAH y tempo cognitivo lento* — Laura Camila Herrera.
- *TEA Clínica 2024* + *TEA y Caso Clínico* — [autor].
- *Trastorno neurocognitivo leve - Déficit cognitivo leve* — Melissa Torres.
- *Del TCL al TCM* — Camilo Achury.
- *Secuelas cognitivas del COVID-19* — Luisa Vidal.
- *Alteraciones neuropsiquiátricasdulto y adulto mayor* — Luisa Fernanda Vidal Agamez.
- *Tx Habilidades Escolares* (parte 1 y 2) — Laura Camila Herrera, Jaiver Camilo Achury.
- *GADS Manual* — calificación protocolos.
- *Reservorio de recomendaciones de acuerdo a cuadro clínico *.
- *Clasificación de RIPS 2025*.
- *STAI y SNAP * (xlsx).
- *Formato Diligenciamiento de Historia Clínica* — Coordinación Clínica V.1 26/ene/2024.

### Investigación bibliográfica externa
- Peña-Casanova J, Montañés P et al. *Neuronorma Colombia: aportes y características metodológicas*. Neurología (Elsevier) 2021.
 <https://www.elsevier.es/es-revista-neurologia-295-articulo-neuronorma-colombia-aportes-caracteristicas-metodologicas-S0213485321000785>
- Arango-Lasprilla JC, Rivera D et al. *Commonly used Neuropsychological Tests for Spanish Speakers: Normative Data from Latin America*. NeuroRehabilitation 2015.
 <https://journals.sagepub.com/doi/10.3233/NRE-151276>
- Rivera D, Arango-Lasprilla JC. *Methodology for the development of normative data for Spanish-speaking pediatric populations*. NeuroRehabilitation 2017.
 <https://journals.sagepub.com/doi/10.3233/NRE-172275>
- Pedraza OL et al. *Validation of the MoCA in Spanish for MCI and mild dementia in patients over 65 in Bogotá, Colombia*. International Journal of Geriatric Psychiatry 2014.
 <https://pubmed.ncbi.nlm.nih.gov/25320026/>
- Pedraza OL et al. *Confiabilidad, validez de criterio y discriminante del MoCA en adultos de Bogotá*. Acta Médica Colombiana 2016.
 <http://www.scielo.org.co/pdf/amc/v41n4/v41n4a04.pdf>
- Matute E, Rosselli M, Ardila A, Ostrosky-Solís F. *Evaluación Neuropsicológica Infantil (ENI)*.
 <https://www.fundacionsindano.com/wp-content/uploads/2017/11/M-Roselli-et-al.-2015-evaluacion-neuropsicologica-infantil.pdf>
- Sohlberg MM, Mateer CA. *Effectiveness of an attention-training program*. <https://pubmed.ncbi.nlm.nih.gov/3558744/>
- APT-III: <https://lapublishing.com/apt3-attention-process-training/>
- *Errorless learning and spaced retrieval techniques to relearn iADLs in mild Alzheimer's*. PMC. <https://pmc.ncbi.nlm.nih.gov/articles/PMC2626924/>
- *Effects of spaced retrieval training with errorless learning in dementia*. PMC. <https://pmc.ncbi.nlm.nih.gov/articles/PMC4616083/>
- *Computerized Cognitive Rehabilitation of Attention and Executive Function in Acquired Brain Injury*. PMC. <https://pmc.ncbi.nlm.nih.gov/articles/PMC5401713/>
- *Computer-assisted cognitive rehabilitation in neurological patients*. Frontiers Neurology 2023.
 <https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2023.1255319/full>
- HVLT-R Latin American norms (Arango-Lasprilla et al. 2015). <https://pubmed.ncbi.nlm.nih.gov/26639933/>
- BANFE-2 ficha técnica Manual Moderno Colombia. <https://colombia.manualmoderno.com/batera-a-neuropsicola-gica-de-funciones-ejecutivas-y-la-bulos-frontales-100-100.html>
- NEUROPSI Atención y Memoria (3a ed). <https://store.manualmoderno.com/neuropsi-atencion-memoria-117-100.html>
- FDT Test de los 5 dígitos (Sedó). <https://www.hogrefe-tea.com/recursos/Ejemplos/FDT_extracto-web.pdf>
- MoCA repositorio oficial. <https://mocacognition.com/>
- ACRM Cognitive Rehabilitation Manual. <https://acrm.org/meetings/cognitive-rehab-training/cognitive-rehabilitation-manual-2/>
- PEBL battery (open source). <http://pebl.sourceforge.net>
- ComplexSpan PsychoPy. <https://github.com/neuropsychology/ComplexSpan>
- Mesulam Symbol Cancellation Test (Strokengine). <https://strokengine.ca/en/assessments/single-letter-cancellation-test-slct/>
- Editorial CEPE. *Neuropsicología en Colombia. Datos normativos, estado actual y retos a futuro*.
 <https://editorialcepe.es/titulo/neuropsicologia-en-colombia-datos-normativos-estado-actual-y-retos-a-futuro/>
- Flanagan DP, Kaufman AS. *Essentials of WISC-IV Assessment* (2009). Wiley — fuente de ICG/ICC.
- Sattler JM. *Assessment of Children: Cognitive Foundations* (2010) — fuente de Formas Cortas WISC-IV.

---

*Roadmap vivo: cada sprint cerrado → marcar la sección correspondiente. Próxima revisión cuando se cierren ≥3 sprints.*
