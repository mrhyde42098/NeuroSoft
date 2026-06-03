# 15 Casos clínicos ground-truth — NeuroSoft App (VALIDADOS)

> **Estado:** ✅ **VALIDADO 2026-05-19** contra el motor real (`ClinicalEngine`) usando baremos colombianos cargados (`BD_NEURO_MAESTRA.json`, 186 pruebas).
>
> **Origen de los escalares.** Cada PD listado fue ejecutado contra el motor oficial vía `docs/casos-clinicos/validar_casos.py`. Los escalares mostrados son los REALES (no aspiracionales). Resultado completo en `docs/casos-clinicos/RESULTADOS_VALIDACION.json`.
>
> **Cómo se construyeron los casos:**
> 1. Definimos el perfil clínico objetivo (TDAH, dislexia, Alzheimer, etc.).
> 2. Inventamos sociodemografía + HC compatible con el cuadro.
> 3. Asignamos PDs y los pasamos al motor.
> 4. Donde los escalares no correspondían al perfil → ajustamos PDs y re-validamos.
> 5. Repetimos hasta que el perfil de escalares coincida clínicamente con el cuadro narrado.
>
> **Lo que NO se hizo (importante):**
> - **Nunca se modificó `BD_NEURO_MAESTRA.json`** — los baremos son intocables.
> - **Nunca se "inventaron" escalares** — los escalares son los del motor con los baremos reales.
> - **Lo que sí es ficticio:** los nombres, la HC narrativa, los PDs (datos de pacientes ficticios). Esto es lícito porque son casos pedagógicos/QA, no informes clínicos reales.
>
> **Cobertura:** 5 infantiles (TDAH, dislexia, TEA, DI, TEPT) · 5 adulto joven (depresión, TCE, ansiedad, TDAH adulto, duelo) · 5 adulto mayor (DCL, Alzheimer, pseudodemencia, Parkinson, control normal).
>
> **Cómo re-validar:**
> ```powershell
> cd D:\NeuroSoftApp\neurosoft-backend
> venv\Scripts\python ..\docs\casos-clinicos\validar_casos.py
> ```
> Si algún escalar de la tabla cambia respecto al output del script, hay una regresión clínica.
>
> **Recordatorio legal:** son casos ficticios. Nombres inventados, escenarios construidos. Cualquier coincidencia con personas reales es involuntaria (Ley 1581/2012 — Habeas Data).

---

## INFANTIL (5)

---

### Caso 3 — Sebastián Castillo Gómez · TDAH combinado

**Sociodemografía**
- 8a 3m · M · diestro · Bogotá · 3° primaria, colegio público
- Nacimiento 2017-01-15 · Evaluación 2025-05-10
- Madre 35a (contadora) + abuela materna 62a. Padre separado.
- EPS Compensar · Remite pediatra

**Motivo de consulta**
La madre: *"No para quieto en clase, no termina los talleres, se levanta del puesto. Pierde los útiles, deja la tarea por la mitad. Le repito tres veces las cosas y no me hace caso. Esto viene desde primero, ahora con tercero empeoró."*

**Antecedentes**
- **Patológicos:** asma leve controlada (salbutamol PRN). Embarazo y parto normales.
- **Hitos:** dentro de rangos esperados.
- **Sensoriales:** visión y audición OK (control 2024).
- **Psiquiátricos:** ninguno previo.
- **Traumáticos:** caída en bici a los 5a sin pérdida de conciencia.
- **Quirúrgicos:** ninguno.
- **Familiares:** padre con sospecha TDAH no diagnosticado. Abuelo materno HTA.
- **ABC:** vestido limpio, colaborador con dificultad para sostener atención.
- **Escolar:** repitió por bajo desempeño en lecto-escritura. Conducta disruptiva moderada.
- **Sueño:** 9h, despertares ocasionales.
- **Alimentación:** selectivo.
- **Comportamiento:** frustración fácil ante tareas largas.

**Hipótesis pre-evaluación:** TDAH presentación combinada (DSM-5). Descartar DEA en lectura comórbida.

**Puntajes (validados con motor real):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| NiWiscDC | 30 | 13 | Superior |
| NiWiscSem | 18 | 12 | Promedio |
| NiWiscRDD | 11 | 7 | Promedio |
| NiWiscCl | 22 | 6 | **Limítrofe** |
| NiWiscVoc | 30 | 12 | Promedio |
| NiWiscLN | 11 | 8 | Promedio |
| NiWiscMat | 17 | 11 | Promedio |
| NiWiscCom | 18 | 11 | Promedio |
| NiWiscBusSim | 10 | 7 | Promedio |
| NiWiscAri | 14 | 7 | Promedio |

**Perfil clínico real:** CV/RP promedio-alto (escalares 11-13) · VP bajo (Claves 6, BusSim 7) · MT bajo-promedio (RDD 7, LN 8, Aritmética 7). **Compatible con TDAH combinado**: predominio de afectación en velocidad de procesamiento y memoria de trabajo, con razonamiento perceptual y comprensión verbal preservados.

**Impresión diagnóstica esperada:** F90.2 TDAH presentación combinada.

**Recomendaciones esperadas:** valoración psiquiátrica para considerar metilfenidato; adaptaciones escolares (ubicación cerca docente, instrucciones cortas, tiempo extra); psicoeducación familiar; terapia conductual estructurada.

---

### Caso 4 — Valentina Ospina Marín · Dislexia evolutiva

**Sociodemografía**
- 10a 6m · F · diestra · Medellín · 5° primaria, colegio privado
- Nacimiento 2014-10-22 · Evaluación 2025-05-19
- Padres + hermana menor. Padre ingeniero, madre arquitecta.
- EPS Sura · Remite psicopedagoga del colegio

**Motivo de consulta**
Padre: *"A Vale le va bien en todo menos en lectura y escritura. Lee muy lento, se traba con palabras nuevas, confunde b/d. En matemáticas y arte va bien. La profe dice que no es por falta de esfuerzo."*

**Antecedentes**
- **Patológicos:** ninguno. Embarazo y parto sin complicaciones.
- **Sensoriales:** optometría normal. Audiometría normal.
- **Psiquiátricos:** ninguno.
- **Quirúrgicos:** amigdalectomía a los 6a.
- **Familiares:** tío paterno con dislexia diagnosticada en adultez.
- **Escolar:** notas 4.0/5.0 en todas las áreas, excepto español (2.8) y sociales (3.2 — por lectura).
- **Comportamiento:** introvertida, autoexigente, baja autoestima académica reciente.

**Hipótesis pre-evaluación:** Dificultad específica del aprendizaje de la lectura. CI presumiblemente normal.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| NiWiscDC | 32 | 10 | Promedio |
| NiWiscSem | 24 | 11 | Promedio |
| NiWiscVoc | 35 | 10 | Promedio |
| NiWiscConD | 17 | 10 | Promedio |
| NiWiscCl | 50 | 12 | Promedio |
| NiWiscMat | 21 | 10 | Promedio |
| NiWiscBusSim | 30 | 13 | Superior |
| NiPrec (errores lectura) | 8 | 3 | **Bajo** |
| NiLVS (comprensión silenciosa) | 2 | 6 | **Limítrofe** |
| NiCopTxt (copia de texto) | 14 | 8 | Promedio |

**Perfil clínico real:** CI normal-alto (todos los WISC entre 10 y 13). Déficit específico en lecto-escritura: NiPrec=3 (muchos errores en lectura voz alta), NiLVS=6 (comprensión deficitaria). Patrón **clásico de dislexia evolutiva**: capacidad cognitiva preservada, dificultad específica en proceso lector.

**Impresión:** F81.0 Trastorno específico de la lectura.

**Recomendaciones:** intervención psicopedagógica (Orton-Gillingham); PIAR en el colegio; tiempo extra evaluaciones; trabajo de autoestima académica; reevaluación al año.

---

### Caso 5 — Mateo Quintero Salazar · TEA nivel 1

**Sociodemografía**
- 6a 2m · M · ambidiestro · Cali · Transición, colegio Montessori
- Nacimiento 2019-03-08 · Evaluación 2025-05-12
- Hijo único. Padre ingeniero, madre profesora. EPS Coomeva.
- Remite neuropediatra.

**Motivo de consulta**
Madre: *"Es muy inteligente con números y letras pero le cuesta hacer amigos. No me mira a los ojos. Le obsesionan trenes y dinosaurios. Cuando la rutina cambia se altera mucho."*

**Antecedentes**
- **Patológicos:** prematuro 36 sem, peso 2.4 kg. Hospitalización 3 días neonatal.
- **Hitos:** marcha al año, primeras palabras 14 m, frases 30 m (tardío).
- **Sensoriales:** hipersensibilidad táctil (no tolera lana).
- **Familiares:** primo materno con TEA.
- **Comportamiento:** intereses restringidos (trenes), alinear juguetes, pragmática del lenguaje alterada.
- **Alimentación:** selectivo, ~10 alimentos.
- **Sueño:** rituales rígidos, 10h.

**Hipótesis pre-evaluación:** TEA nivel 1 (requiere apoyo). CI presumiblemente normal-alto.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| NiWiscDC | 24 | 14 | Superior |
| NiWiscVoc | 28 | 16 | Superior |
| NiWiscSem | 16 | 14 | Superior |
| NiWiscMat | 18 | 16 | Superior |
| NiWiscCl | 22 | 7 | Promedio |
| NiRecEmo (reconocimiento de emociones) | 2 | 1 | **Bajo** |

**Perfil clínico real:** rendimiento cognitivo general **alto** (escalares 14-16 en WISC). Velocidad de procesamiento promedio bajo (Cl=7). Déficit marcado en cognición social (NiRecEmo escalar 1). **Patrón compatible con TEA nivel 1 sin discapacidad intelectual**: alto rendimiento académico estructurado + déficit en interpretación de emociones faciales.

**Impresión:** F84.0 TEA nivel 1.

**Recomendaciones:** confirmación con ADOS-2 + ADI-R; terapia ABA o DIR/Floortime; terapia ocupacional (integración sensorial); apoyo escolar; psicoeducación familiar.

---

### Caso 6 — Isabella Mendoza Ariza · Discapacidad intelectual leve

**Sociodemografía**
- 13a 7m · F · diestra · Cartagena · 5° primaria (rezago 2 años), colegio público inclusivo
- Nacimiento 2011-09-25 · Evaluación 2025-05-20
- Madre cabeza de familia (38a, vendedora) + hermanos (16, 10a). Padre ausente.
- EPS Mutual Ser · Remite orientadora del colegio

**Motivo de consulta**
Madre: *"Isa siempre fue más lenta para aprender. Le costó hablar, caminar, leer. En el colegio le dieron apoyo pero no avanza. Quiero saber si esto tiene un nombre."*

**Antecedentes**
- **Perinatales:** sufrimiento fetal, hipoxia perinatal. Hospitalización neonatal 5 días.
- **Hitos:** marcha 22 m, primeras palabras 24 m, frases 3.5a (todos tardíos).
- **Sensoriales:** optometría y audiometría OK.
- **Comportamiento:** dulce, sociable, ingenua para su edad. Sin disruptiva.

**Hipótesis pre-evaluación:** DI leve (CI estimado 50-70). Secuela hipoxia perinatal.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| NiWiscDC | 20 | 5 | Limítrofe |
| NiWiscSem | 11 | 4 | **Bajo** |
| NiWiscRDD | 9 | 2 | **Bajo** |
| NiWiscConD | 9 | 1 | **Bajo** |
| NiWiscCl | 35 | 4 | **Bajo** |
| NiWiscVoc | 18 | 2 | **Bajo** |
| NiWiscLN | 8 | 1 | **Bajo** |
| NiWiscMat | 11 | 3 | **Bajo** |
| NiWiscCom | 11 | 1 | **Bajo** |
| NiWiscBusSim | 12 | 2 | **Bajo** |

**Perfil clínico real:** todos los subtests con escalares 1-5 (rango bajo/limítrofe). **Perfil parejo deficitario en todos los dominios** — compatible con discapacidad intelectual leve. CIT estimado ~60.

**Impresión:** F70 DI Leve (CIE-10) compatible con secuela de hipoxia perinatal.

**Recomendaciones:** aula de apoyo individualizada, PIAR; énfasis en habilidades adaptativas (AVD, dinero, vialidad); formación técnico-laboral al egresar bachillerato; apoyo a la madre; orientación vocacional adaptada.

---

### Caso 7 — Daniel Jaramillo Vásquez · TEPT infantil

**Sociodemografía**
- 9a 5m · M · diestro · Bucaramanga (procedencia Catatumbo rural) · 3° primaria
- Nacimiento 2015-12-05 · Evaluación 2025-05-15
- Familia desplazada. Madre 32a (trabajadora doméstica) + 2 hermanos (12, 5a). Padre asesinado.
- EPS Salud Total subsidiado · Remite psicóloga Unidad de Víctimas

**Motivo de consulta**
Madre (con apoyo psicóloga): *"Daniel cambió desde lo que pasó hace 8 meses. Vivíamos en una vereda del Catatumbo, hubo un enfrentamiento armado, vio cosas. Ahora tiene pesadillas, se asusta con ruidos fuertes, no quiere ir al colegio. Antes era buen estudiante."*

**Antecedentes**
- **Patológicos:** ninguno relevante pre-evento.
- **Traumáticos:** **exposición directa a evento de violencia armada (ago 2024). Desplazamiento forzado. Padre asesinado.**
- **Psiquiátricos:** sintomatología TEPT post-evento.
- **Sueño:** pesadillas 4-5/sem, despertares con sobresalto.
- **Comportamiento:** hipervigilancia, evitación de estímulos asociados (sonidos fuertes, hombres uniformados).

**Hipótesis pre-evaluación:** F43.1 TEPT infantil. Duelo paterno complicado.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| NiWiscDC | 24 | 9 | Promedio |
| NiWiscSem | 16 | 9 | Promedio |
| NiWiscRDD | 10 | 6 | **Limítrofe** |
| NiWiscCl | 35 | 8 | Promedio |
| NiWiscVoc | 23 | 7 | Promedio |
| NiWiscLN | 9 | 5 | **Limítrofe** |
| NiWiscMat | 15 | 7 | Promedio |
| NiWiscCom | 14 | 7 | Promedio |
| NiSt_Edades (Stroop) | 20 | 0 | **Bajo** |

**Perfil clínico real:** descenso leve generalizado (escalares 5-9), con afectación más visible en memoria de trabajo (RDD=6, LN=5) y atención compleja (Stroop=0). **Patrón compatible con afectación secundaria a TEPT**: el funcionamiento cognitivo previo era normal — los descensos reflejan interferencia atencional/emocional del cuadro post-trauma, no déficit orgánico primario.

**Impresión:** F43.1 TEPT + posible F43.21 Trastorno adaptativo con ánimo deprimido (duelo). Funcionamiento cognitivo recuperable con intervención.

**Recomendaciones:** psicoterapia TF-CBT (12-16 sesiones) o EMDR pediátrico; terapia familiar (madre); apoyo psicosocial Unidad de Víctimas; articulación con colegio; revaluación cognitiva a 6 meses post-intervención; NO medicar de entrada.

---

## ADULTO JOVEN (5)

---

### Caso 8 — Carolina Pineda Restrepo · Depresión mayor

**Sociodemografía**
- 24a 0m · F · diestra · Bogotá · Universitaria (Psicología, 8º sem en pausa académica)
- Nacimiento 2001-05-12 · Evaluación 2025-05-15
- Vive con pareja (26a, ingeniero). Padres en Medellín. EPS Sanitas. Remite psiquiatra.

**Motivo de consulta**
*"Ya no puedo estudiar. Antes era buena estudiante, ahora no me concentro, leo y no entiendo, se me olvidan las cosas. El psiquiatra dice que es la depresión, pero yo siento que algo más está mal en mi cabeza."*

**Antecedentes**
- **Psiquiátricos:** episodio depresivo mayor actual (8m de evolución). Manejo psiquiátrico desde hace 4m con sertralina 100 mg/día.
- **Familiares:** madre con depresión recurrente. Hermana mayor con trastorno de ansiedad.
- **Sueño:** 11h con dificultad para levantarse. Despertar precoz 5am.
- **Alimentación:** anhedonia, bajó 6 kg en 6m.
- **Estado emocional:** tristeza basal, llanto frecuente, **ideas pasivas de muerte sin plan ni intento**.

**Hipótesis pre-evaluación:** F32.2 Depresión mayor moderada-severa con queja cognitiva ("pseudodemencia depresiva"). Descartar TDAH no diagnosticado previo.

**Puntajes (validados):**

| Test | PD | Escalar/T | Interpretación |
|---|---:|---:|---|
| AdWAISV (Vocabulario) | 48 | 12 | Promedio |
| AdSemWais (Semejanzas) | 21 | 10 | Promedio |
| AdSDWais (Claves) | 70 | 8 | Promedio |
| AdDDir (Dígitos directos) | 9 | 4 | **Bajo** |
| AdMatr (Matrices) | 21 | 11 | Promedio |
| AdWAISFI (Figuras incompletas) | 19 | 8 | Promedio |
| AdTMT_AB (TMT A+B z-score) | 90 | z=9.2 | Lentificación |
| AdBeck (BDI-II) | 32 | — | **Severa** |

**Perfil clínico real:** intelecto preservado (WAIS 8-12), bajo en MT (Dígitos 4), lentificación marcada en TMT (z=9.2 superior). Beck 32 = depresión severa. **Patrón clásico de pseudodemencia depresiva**: déficit selectivo en velocidad/MT con razonamiento preservado, alta carga afectiva.

**Impresión:** F32.2 Depresión mayor severa con queja cognitiva. Perfil compatible con depresión, NO con deterioro primario. Pronóstico de recuperación cognitiva con remisión sintomática.

**Recomendaciones:** ajustar sertralina (100→150) o cambio si no respuesta a 12 sem; TCC 16-20 sesiones; plan de seguridad por ideación pasiva; reevaluación a 6 meses post-remisión.

---

### Caso 9 — Juan Pablo Velandia Rojas · TCE moderado

**Sociodemografía**
- 31a 5m · M · diestro · Cali · Técnico (mecánica industrial SENA)
- Nacimiento 1993-12-10 · Evaluación 2025-05-18
- Esposa (29a, secretaria) + hija (4a). EPS Nueva EPS. Remite fisiatra.

**Motivo de consulta**
*"Tuve un accidente en moto hace 4 meses. UCI 8 días, cirugía. Físicamente bien, pero la cabeza no me funciona igual. Olvido cosas, antes manejaba el taller mentalmente, ahora no puedo organizar. La esposa dice que estoy de mal genio, antes era tranquilo."*

**Antecedentes**
- **TCE moderado** (ene 2025): Glasgow 11/15, fractura temporal derecha, contusión fronto-temporal dcha. Hospitalización 22 días.
- **Quirúrgicos:** craneotomía descompresiva (ene 2025).
- **Patológicos:** HTA leve (losartán 50).
- **Cambio de personalidad pos-TCE:** mayor irritabilidad.

**Hipótesis pre-evaluación:** S06.9 Secuelas cognitivo-conductuales post-TCE moderado. Énfasis fronto-temporal dcho (atención, FE, conducta).

**Puntajes (validados):**

| Test | PD | Escalar/T | Interpretación |
|---|---:|---:|---|
| AdWAISV | 42 | 9 | Promedio |
| AdSemWais | 19 | 9 | Promedio |
| AdSDWais (Claves) | 50 | 5 | **Limítrofe** |
| AdDDir | 9 | 4 | **Bajo** |
| AdMatr | 17 | 8 | Promedio |
| AdWAISCC (Cubos) | 28 | 5 | **Limítrofe** |
| AdTMT_AB | 130 | z=14.8 | **Lentificación severa** |
| AdStroop_Corr | 28 | T=0 | **Bajo** |

**Perfil clínico real:** WAIS verbal preservado (9), atención/MT muy afectados (Dígitos 4, Cubos 5, Claves 5). TMT con lentificación severa (z=14.8). Stroop=0 (déficit inhibición). **Compromiso predominante en FE, velocidad y atención** — perfil cognitivo compatible con TCE moderado fronto-temporal.

**Impresión:** F07.2 Síndrome cognitivo-conductual orgánico post-TCE moderado.

**Recomendaciones:** rehabilitación neuropsicológica intensiva 6m (atención, FE, velocidad); psicoeducación familiar sobre secuelas TCE; TCC regulación emocional; reincorporación laboral gradual (no manejar maquinaria); evitar alcohol; reevaluación a 6m/12m.

---

### Caso 10 — Camila Herrera Gómez · Ansiedad generalizada

**Sociodemografía**
- 22a 11m · F · diestra · Pereira · Universitaria (Derecho 6º sem)
- Nacimiento 2002-06-18 · Evaluación 2025-05-18
- Vive con 2 compañeras de apartamento. Familia en Manizales. EPS Sura. Remite médico general.

**Motivo de consulta**
*"Estoy muy ansiosa todo el tiempo. Pienso en todo lo que puede salir mal, no duermo bien. Me cuesta concentrarme en la lectura, releo 3 veces lo mismo. ¿Tengo problema cognitivo o todo es ansiedad?"*

**Antecedentes**
- **Psiquiátricos:** ansiedad desde adolescencia, intensificada 18m (cambio de ciudad). Sin manejo previo.
- **Familiares:** madre con trastorno de pánico.
- **Tóxicos:** cafeína intensa (6 tazas/día). Cigarrillo ocasional en exámenes.
- **Sueño:** latencia 1-2h por rumiación, despertares.
- **Comportamiento:** hipervigilancia, conducta de chequeo.

**Hipótesis pre-evaluación:** F41.1 TAG. Funcionamiento cognitivo intacto con interferencia atencional secundaria.

**Puntajes (validados):**

| Test | PD | Escalar/T | Interpretación |
|---|---:|---:|---|
| AdWAISV | 48 | 12 | Promedio |
| AdSemWais | 24 | 12 | Promedio |
| AdSDWais | 75 | 10 | Promedio |
| AdDDir | 11 | 6 | **Limítrofe** |
| AdMatr | 21 | 11 | Promedio |
| AdTMT_AB | 75 | z=7.1 | Lentificación leve |
| AdStroop_Corr | 42 | T=0 | **Bajo** |
| EscSTAI (Ansiedad) | 55 | — | Alta |

**Perfil clínico real:** WAIS general 10-12 (preservado), MT afectada secundariamente (Dígitos=6), lentificación leve en TMT. **No hay sustrato cognitivo de deterioro** — la queja subjetiva refleja la interferencia atencional propia del cuadro ansioso, no un déficit orgánico.

**Impresión:** F41.1 Trastorno de Ansiedad Generalizada. Funcionamiento cognitivo dentro de promedio.

**Recomendaciones:** TCC para TAG (15-20 sesiones, reestructuración + relajación); reducir cafeína (objetivo ≤2/día); higiene del sueño; mindfulness/MBSR; considerar ISRS si TCC sin respuesta a 12 sem; NO repetir evaluación cognitiva.

---

### Caso 11 — Andrés Mauricio Torres · TDAH adulto

**Sociodemografía**
- 28a 6m · M · diestro · Cúcuta · Universitaria incompleta (Ingeniería sistemas 7º sem, repitiendo materias)
- Nacimiento 1996-10-22 · Evaluación 2025-05-18
- Vive con padres (60, 57a). Pareja estable 3a (vive aparte). Ocupación: dev freelance. EPS Coomeva. Autorremitido.

**Motivo de consulta**
*"Toda la vida he sido distraído, desorganizado. Empiezo proyectos y no los termino. Llevo años repitiendo materias por no entregar trabajos a tiempo. Mi novia me dijo que mire si tengo TDAH."*

**Antecedentes**
- **Hitos infancia:** "fue inquieto" según la madre, sin diagnóstico.
- **Tóxicos:** cannabis recreacional 1-2/mes desde los 22a.
- **Familiares:** hermano menor con TDAH diagnosticado en infancia.
- **Sueño:** irregular (acuesta 3am, levanta mediodía).
- **Académico:** 10 años en pregrado, promedio 3.2/5.0.

**Hipótesis pre-evaluación:** F90.0 TDAH adulto (combinado o inatento). Descartar comorbilidad afectiva.

**Puntajes (validados):**

| Test | PD | Escalar/T | Interpretación |
|---|---:|---:|---|
| AdWAISV | 50 | 12 | Promedio |
| AdSemWais | 25 | 13 | Superior |
| AdSDWais | 65 | 8 | Promedio |
| AdDDir | 9 | 4 | **Bajo** |
| AdMatr | 21 | 11 | Promedio |
| AdTMT_AB | 110 | z=12.0 | **Lentificación** |
| AdStroop_Corr | 30 | T=0 | **Bajo** |
| EscASRS | 42 | — | Alto (≥36 sugestivo) |

**Perfil clínico real:** WAIS general 11-13 (intelecto promedio-alto), Dígitos 4 (MT afectada), TMT z=12 (FE/velocidad lentificada), Stroop=0 (inhibición). **Patrón TDAH adulto** — capacidad intelectual preservada pero rendimiento ejecutivo descendido. ASRS 42 (sugestivo).

**Impresión:** F90.0 TDAH adulto presentación combinada. Funcionamiento intelectual promedio. Disfunción atribuible al cuadro.

**Recomendaciones:** evaluación psiquiátrica (atomoxetina/metilfenidato); TCC adaptada TDAH adulto (Safren); coaching de hábitos; suspensión de cannabis; higiene del sueño; plan académico realista.

---

### Caso 12 — Diana Camila Suárez Pérez · Duelo complicado + depresión

**Sociodemografía**
- 35a 3m · F · diestra · Pasto · Universitaria (Lic. Pedagogía Infantil)
- Nacimiento 1990-02-15 · Evaluación 2025-05-19
- Esposo (37a, contador). Sin más hijos. EPS Salud Total. Remite psiquiatra.

**Motivo de consulta**
*"Perdí a mi hijo de 4 años hace 14 meses por leucemia. Estoy en tratamiento psiquiátrico pero no logro salir de esto. No logro concentrarme, todo me recuerda a él."*

**Antecedentes**
- **Traumáticos:** pérdida del hijo (mar 2024) por leucemia.
- **Psiquiátricos:** depresión mayor + duelo prolongado actual. Manejo con escitalopram 20 mg + clonazepam 0.5 HS. Psicoterapia 8m.
- **Laboral:** dejó de trabajar hace 8m (incapacidad continua).
- **Sueño:** 10-12h con clonazepam.
- **Comportamiento:** anhedonia, evitación, rumiación constante.

**Hipótesis pre-evaluación:** F43.8 / 6B42 (CIE-11) Duelo prolongado + F32.1 EDM moderado comórbido.

**Puntajes (validados):**

| Test | PD | Escalar/T | Interpretación |
|---|---:|---:|---|
| AdWAISV | 48 | 12 | Promedio |
| AdSemWais | 22 | 12 | Promedio |
| AdSDWais | 65 | 10 | Promedio |
| AdDDir | 9 | 6 | **Limítrofe** |
| AdMatr | 19 | 12 | Promedio |
| AdTMT_AB | 100 | z=10.6 | Lentificación |
| AdBeck | 28 | — | **Moderada** |

**Perfil clínico real:** WAIS general preservado (10-12), MT en limítrofe (Dígitos 6), TMT z=10.6 (lentificación moderada). Beck 28 moderada. **Perfil cognitivo compatible con cuadro afectivo activo** (lentificación + queja > objetivo) — sin sustrato de deterioro cognitivo primario. Pronóstico favorable.

**Impresión:** F43.8 / 6B42 Trastorno por duelo prolongado + F32.1 EDM moderado comórbido.

**Recomendaciones:** psicoterapia específica para duelo prolongado (Prigerson — CGT); mantener psiquiatría, ajustar si no respuesta 16 sem; reincorporación gradual; grupo de padres en duelo; reevaluación a 6m post-intervención.

---

## ADULTO MAYOR (5)

---

### Caso 13 — Hernando Restrepo Villegas · DCL amnésico

**Sociodemografía**
- 72a 4m · M · diestro · Manizales · Universitaria (Ingeniería civil, 5 años)
- Nacimiento 1953-01-08 · Evaluación 2025-05-15
- Esposa 68a (jubilada docente). 2 hijas adultas. EPS Sanitas. Remite geriatra.

**Motivo de consulta**
*"Mi esposa nota que repito preguntas, olvido conversaciones recientes. Yo siento que sigo funcionando bien."*

**Antecedentes**
- **Patológicos:** HTA controlada (losartán+amlodipino), hipotiroidismo (levotiroxina), DM2 (metformina).
- **Quirúrgicos:** cataratas 2020, prostatectomía por HPB 2018.
- **Tóxicos:** tabaco hasta 1995 (1 paquete/día x 20a).
- **Familiares:** madre con Alzheimer Dx a los 78a (falleció a los 84a).
- **AVD:** independiente. **AIVD:** conserva pero esposa supervisa más.
- **Conducta:** conciencia parcial del problema, autoirónico.

**Hipótesis pre-evaluación:** G31.84 DCL amnésico monodominio. Riesgo elevado conversión a EA por historia familiar.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| ViRDD | 6 | 14 | Superior |
| ViRDInv | 4 | 13 | Superior |
| ViTMTA | 60 | 10 | Promedio |
| ViTMTB | 145 | 10 | Promedio |
| ViStP | 95 | 13 | Superior |
| ViGroberRLT (recuerdo libre) | 18 | 8 | Promedio |
| ViGroberML_Tot | 8 | 10 | Promedio |
| ViGroberMC_Tot (recuerdo con clave) | 14 | 9 | Promedio |
| ViAni (fluidez Animales) | 16 | 10 | Promedio |
| ViYesavage | 2 | — | Normal |

**Perfil clínico real:** atención, velocidad y FE preservadas (10-14). Memoria episódica con ligera afectación en recuerdo libre (Grober RLT=8) y **beneficio con claves** (MC_Tot=9). Sin depresión. **Patrón compatible con DCL amnésico incipiente** (Petersen 2004 + NIA-AA 2011): déficit selectivo en memoria libre con preservación de codificación (típico hipocampal).

**Impresión:** G31.84 DCL amnésico monodominio. Riesgo conversión a EA elevado por historia materna.

**Recomendaciones:** RMN cerebral + perfil tiroideo/B12; optimizar control metabólico; estimulación cognitiva con énfasis memoria; ejercicio aeróbico ≥150 min/sem; dieta MIND; higiene sueño; seguimiento neuropsicológico cada 6-12m.

---

### Caso 14 — Rosa Inés Cárdenas Mejía · Alzheimer leve

**Sociodemografía**
- 76a 9m · F · diestra · Tunja · Primaria (5 años, completa)
- Nacimiento 1948-08-05 · Evaluación 2025-05-12
- Vive con hija (52a, profesora) + 2 nietos (14, 17a). Esposo fallecido hace 15a. EPS Famisanar. Remite neurólogo.

**Motivo de consulta**
Hija: *"Mi mamá cambió mucho en los últimos 2 años. Ya no cocina porque deja la estufa prendida. Me pregunta lo mismo 5 veces. Se pierde si sale sola. A veces no reconoce a las nietas más jóvenes."*

**Antecedentes**
- **Patológicos:** HTA mal controlada, dislipidemia, hipotiroidismo, ACV silente (RMN: microinfartos lacunares).
- **Familiares:** madre con "olvidos en la vejez" no diagnosticados (falleció a los 82a).
- **AVD:** vestido con supervisión, aseo con recordatorios.
- **AIVD:** dependiente (cocina, finanzas, medicación) — hija asume.
- **Comportamiento:** sin conciencia clara del problema.

**Hipótesis pre-evaluación:** F00.0 / G30.0 Enfermedad de Alzheimer leve (NIA-AA McKhann 2011). Componente vascular comórbido.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| ViRDD | 3 | 6 | Limítrofe |
| ViRDInv | 2 | 7 | Promedio |
| ViTMTA | 280 | 5 | **Limítrofe** |
| ViStP | 60 | 8 | Promedio |
| ViGroberRLT | 4 | 2 | **Bajo** |
| ViGroberML_Tot | 1 | 5 | Limítrofe |
| ViGroberMC_Tot | 8 | 5 | **Limítrofe** |
| ViAni | 8 | 5 | **Limítrofe** |
| FluidP | 4 | 5 | **Limítrofe** |
| Denom48 | 28 | 7 | Promedio |
| ViYesavage | 4 | — | Normal |

**Perfil clínico real:** déficit GENERALIZADO (escalares 2-8). Memoria muy afectada (Grober RLT escalar 2, **clave: poca recuperación con claves** MC_Tot=5 → codificación afectada, signo cortical EA, no hipocampal puro). Fluidez verbal limítrofe. **Patrón compatible con Alzheimer leve** — múltiples dominios afectados, interferencia con AVD/AIVD.

**Impresión:** F00.0 / G30.0 EA leve, componente vascular comórbido (mixta probable).

**Recomendaciones:** valoración neurología para inhibidor colinesterasa (donepecilo); optimizar HTA; suspender omeprazol crónico; estimulación cognitiva grupal; plan de cuidado (medicación supervisada, NO conducir, NO salir sola, NO finanzas); trámites legales mientras conserva capacidad; apoyo al cuidador.

---

### Caso 15 — Luis Eduardo Pérez Quintero · Pseudodemencia depresiva

**Sociodemografía**
- 68a 1m · M · diestro · Villavicencio · Secundaria (técnico electricidad)
- Nacimiento 1957-04-18 · Evaluación 2025-05-18
- Vive solo (viudo hace 6m). Hija 45a en Bogotá. EPS Nueva EPS. Remite geriatra.

**Motivo de consulta**
*"Mi mujer murió en noviembre. Desde entonces siento que la cabeza no me funciona, olvido citas, no quiero hacer nada. El doctor dice que es duelo pero me hicieron exámenes y mandaron acá porque no mejoro."*

**Antecedentes**
- **Patológicos:** HTA, EPOC leve (exfumador).
- **Psiquiátricos:** episodio depresivo a los 40a (auto-resolvió). Cuadro actual: **depresión moderada-severa 6m post-pérdida de esposa**, último 2m con escitalopram 10 (subdosis).
- **Traumáticos:** pérdida esposa (nov 2024) por cáncer pancreático.
- **Sueño:** despertar precoz 4-5am.
- **Alimentación:** una vez/día, pérdida 7 kg en 6m.
- **Comportamiento:** **ideación pasiva de muerte sin plan**. Autoreproche.

**Hipótesis pre-evaluación:** F32.2 Depresión mayor severa con queja cognitiva (pseudodemencia). DIFERENCIAL CLAVE vs DCL/EA.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| ViRDD | 5 | 11 | Promedio |
| ViRDInv | 3 | 9 | Promedio |
| ViTMTA | 110 | 6 | **Limítrofe** |
| ViStP | 75 | 8 | Promedio |
| ViGroberRLT | 22 | 9 | Promedio |
| ViGroberML_Tot | 9 | 9 | Promedio |
| ViGroberMC_Tot | 14 | 8 | Promedio |
| ViAni | 14 | 8 | Promedio |
| ViYesavage | 11 | — | **Déficit Extremo (≥10 = severa)** |

**Perfil clínico real:** atención + memoria PRESERVADAS (escalares 8-11). Velocidad ligeramente baja (TMT-A=6). **Grober con beneficio normal con claves** (MC_Tot=8) — codificación intacta, signo de NO deterioro cortical. Yesavage 11 (depresión severa). **Patrón clásico de pseudodemencia depresiva**: queja subjetiva intensa con rendimiento objetivo dentro de lo normal, beneficio con claves preserved.

**Impresión:** F32.2 EDM severo con queja cognitiva — **pseudodemencia depresiva**, NO deterioro cognitivo primario.

**Recomendaciones:** ajustar escitalopram 10→20, considerar mirtazapina HS; psicoterapia para duelo + activación conductual; asegurar acompañamiento; plan de seguridad; seguimiento psiquiátrico mensual; **reevaluación neuropsicológica a 6m post-remisión** (confirmar reversibilidad).

---

### Caso 16 — Magdalena Sánchez Tobón · Parkinson con deterioro cognitivo

**Sociodemografía**
- 70a 10m · F · diestra · Popayán · Primaria Incompleta (3 años)
- Nacimiento 1954-07-02 · Evaluación 2025-05-19
- Hija 45a (secretaria) + yerno 48a + 2 nietos. EPS Asmet Salud. Remite neurólogo.

**Motivo de consulta**
Hija: *"A mi mamá hace 6 años le diagnosticaron Parkinson. Toma medicamentos. Ahora está más lenta, no solo para caminar, también para pensar. Repite las cosas. El neurólogo quiere saber si esto es parte del Parkinson."*

**Antecedentes**
- **Patológicos:** Parkinson idiopático Dx 2019, HTA, hipotiroidismo.
- **Psiquiátricos:** episodio depresivo leve 2022, manejo con sertralina 50.
- **Farmacológicos:** levodopa/carbidopa 250/25 c/8h, pramipexol 0.5 c/12h, enalapril 20, levotiroxina 75, sertralina 50.
- **Traumáticos:** 2 caídas en 12m (Parkinson, sin TCE).
- **Conducta:** hipomimia (máscara), bradicinesia, temblor leve mano derecha.
- **AVD:** vestido con dificultad (botones), aseo con supervisión.
- **AIVD:** dependiente.
- **Sueño:** alterado (sueños vívidos).

**Hipótesis pre-evaluación:** G31.83 PD-MCI vs G31.84 PDD. Perfil esperado disejecutivo + velocidad + visoespacial, memoria preservada relativamente.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| ViRDD | 5 | 11 | Promedio |
| ViRDInv | 3 | 10 | Promedio |
| ViTMTA | 260 | 4 | **Bajo** |
| ViTMTB | 602 | 3 | **Bajo** |
| ViStP | 52 | 6 | **Limítrofe** |
| ViGroberRLT | 16 | 7 | Promedio |
| ViGroberML_Tot | 6 | 6 | **Limítrofe** |
| ViGroberMC_Tot | 13 | 7 | Promedio |
| ViAni | 10 | 7 | Promedio |
| FluidP | 6 | 6 | **Limítrofe** |
| ViYesavage | 4 | — | Normal |

**Perfil clínico real:** atención preservada (RDD=11), TMT muy afectado (A=4, B=3), Stroop bajo (6), fluidez verbal descendida (6-7). Memoria con beneficio normal de claves (signo subcortical). **Patrón disejecutivo-velocidad-fluidez con relativa preservación amnésica** — compatible con PD-MCI (perfil subcortical típico).

**Impresión:** G31.83 DCL asociado a Parkinson (PD-MCI), perfil disejecutivo-visoespacial-procesamiento. No es perfil cortical de EA (preserva codificación).

**Recomendaciones:** articulación con neurología (titular levodopa puede mejorar cognición); valorar suspender pramipexol (agonistas pueden empeorar cognición); rehabilitación cognitiva FE+velocidad; LSVT BIG (TF parkinson); LSVT LOUD (logopedia); TO (AVD/AIVD); reevaluación cada 12m.

---

### Caso 17 — José Antonio Bermúdez Caro · Control normal (envejecimiento típico)

**Sociodemografía**
- 65a 3m · M · diestro · Barranquilla · Universitaria (Economía + posgrado en finanzas, 18a escolaridad)
- Nacimiento 1960-02-10 · Evaluación 2025-05-12
- Esposa 63a (médica jubilada). 2 hijos adultos. Pensionado activo (asesor independiente). EPS Sanitas. Autorremitido (prevención).

**Motivo de consulta**
*"Vengo por prevención, no por problema. Mi mamá murió a los 92 sin demencia, mi papá a los 80. Me siento bien. Trabajo medio tiempo, leo, viajo. A veces se me olvidan nombres pero los recupero. ¿Estoy bien?"*

**Antecedentes**
- **Patológicos:** HTA controlada, dislipidemia controlada (atorvastatina).
- **Familiares:** longevidad familiar sin demencia.
- **Estilo de vida:** dieta mediterránea estricta, vino 1 copa/cena, ejercicio 5d/sem (natación + caminata).
- **AVD/AIVD:** independiente total. Maneja, viaja, finanzas familiares, asesora clientes.
- **Sueño:** 7h, conciliación normal.
- **Comportamiento:** eutímico, locuaz, sentido del humor.

**Hipótesis pre-evaluación:** envejecimiento cognitivo típico. Queja subjetiva sin sustrato objetivo. No DCL.

**Puntajes (validados):**

| Test | PD | Escalar | Interpretación |
|---|---:|---:|---|
| ViRDD | 7 | 15 | Superior |
| ViRDInv | 5 | 15 | Superior |
| ViTMTA | 45 | 10 | Promedio |
| ViTMTB | 110 | 9 | Promedio |
| ViStP | 110 | 14 | Superior |
| ViGroberRLT | 30 | 12 | Promedio |
| ViGroberML_Tot | 14 | 14 | Superior |
| ViGroberMC_Tot | 16 | 18 | Superior |
| ViAni | 22 | 12 | Promedio |
| FluidP | 18 | 11 | Promedio |
| ViYesavage | 1 | — | Normal |

**Perfil clínico real:** rendimiento promedio-superior en todos los dominios (escalares 9-18). Memoria episódica preservada con beneficio normal de claves. Sin depresión. **Patrón de control normal** — el escolaridad alta + ocupación intelectual + estilo de vida saludable se reflejan en el rendimiento.

**Impresión:** Z00.0 Sin patología. Envejecimiento cognitivo típico/saludable. Queja subjetiva no patológica.

**Recomendaciones:** mantener estilo de vida (dieta MIND, ejercicio, vida social, actividad intelectual); continuar control de factores cardiovasculares; tranquilizar respecto a quejas subjetivas; reevaluación de control en 3-5a o si aparecen quejas funcionales; vacunación al día.

---

## Cómo validar todos los casos

```bash
cd D:\NeuroSoftApp\neurosoft-backend
venv\Scripts\python ..\docs\casos-clinicos\validar_casos.py
# Output: tabla por caso con escalares reales del motor.
# JSON detallado en docs/casos-clinicos/RESULTADOS_VALIDACION.json
```

## Pruebas que se usaron y por qué

| Tipo | Pruebas | Cobertura |
|---|---|---|
| `rango_puntaje` (WISC-IV, ENI-2) | NiWiscDC, NiWiscSem, NiWiscRDD, NiWiscCl, NiWiscVoc, NiWiscLN, NiWiscMat, NiWiscCom, NiWiscBusSim, NiWiscAri, NiWiscConD, NiRecEmo, NiSt_Edades, NiPrec, NiLVS, NiCopTxt | Casos 3-7 |
| `wais_range` (WAIS-III) | AdWAISV, AdSemWais, AdSDWais, AdDDir, AdMatr, AdWAISFI, AdWAISCC | Casos 8-12 |
| `z_score` (Arango-Lasprilla LATAM) | AdTMT_AB | Casos 8-12 |
| `ajuste` (Neuronorma con corrección) | AdStroop_Corr | Casos 9, 10, 11 |
| `desconocido` (Neuronorma AM) | ViRDD, ViRDInv, ViTMTA, ViTMTB, ViStP, ViGroberRLT, ViGroberML_Tot, ViGroberMC_Tot, ViAni, FluidP, Denom48 | Casos 13-17 |
| `clasificacion_fija` (escalas) | ViYesavage, AdBeck, EscSTAI, EscASRS | Casos 7, 8, 10, 11, 12, 13-17 |
| Ajuste por escolaridad | Aplica a Neuronorma AM (casos 14, 16) | Automático |

## Pruebas descartadas y por qué

- **AdTMTA / AdTMTB**: pese a prefijo "Ad", en la BD tienen claves AM (50+). Para adulto joven se usa `AdTMT_AB` (z_score).
- **FluidP** en adulto joven: solo tiene baremos para AM (50+).

## Reglas de mantenimiento

1. **NUNCA modificar `BD_NEURO_MAESTRA.json`** — los baremos son intocables (regla de proyecto).
2. **Cambios en `strategies.py`** → correr `validar_casos.py` y los 27 tests del engine. Cualquier divergencia en escalares = regresión clínica.
3. **Agregar nuevos casos**: añadir al array `CASOS` en `validar_casos.py`, ejecutar y luego documentar el caso aquí.
4. **PDs ficticios pero válidos**: los PDs deben estar dentro de los rangos del baremo de cada prueba. Si dudas, verificar con `mcp__neurosoft-baremos__get_baremo_keys`.

---

**Validación cerrada 2026-05-19.** 15 casos, 110 pruebas, 0 advertencias, 0 "sin dato". Todos los escalares listados son los producidos por el motor real con los baremos colombianos vigentes.
