# Auditoría de Baremos — Pruebas Faltantes

> **Estado:** plan de expansión — NO modifica `BD_NEURO_MAESTRA.json` sin
> consulta previa al autor.
> **Última revisión:** junio 2026 (Sprint 4).
> **Versión del sistema:** 2.0.0

---

## 1. Estado actual

- **168 pruebas** en `BD_NEURO_MAESTRA.json`.
- **112.643 claves** de baremo.
- **15 fixtures ground-truth** con **134 escalares verificados**.
- Cobertura: **33/168 pruebas (20%)** testeadas en motor.
- Baremos principales cubiertos: WISC-IV, WAIS-III, ENI-2, K-ABC, K-BIT,
  Neuropsi, BANFE, BNT, Test Barcelona, Grober (Buschke), Yesavage,
  Beck, Lawton, INECO FS, Neuronorma Colombia AM/infantil/adulto joven.

---

## 2. Pruebas prioritarias a AGREGAR (35+)

### 2.1 Tamizaje neuropsicológico (corto, alta utilidad clínica)

| Prueba | Costo implementación | Validación colombiana | Notas |
|---|---|---|---|
| **MoCA (Montreal Cognitive Assessment)** | Bajo | Nasreddine 2005 + validación Colombia pendiente | 30 puntos, sensible a DCL |
| **MMSE (Mini-Mental State Examination)** | Bajo | Folstein 1975 + Icaza 1999 Chile | 30 puntos, screening demencia |
| **PHQ-9 (Patient Health Questionnaire)** | Muy bajo | Kroenke 2001 + Colombia validada | 9 ítems depresión |
| **GAD-7** | Muy bajo | Spitzer 2006 + validación latinoamericana | 7 ítems ansiedad |
| **BDI-II (Beck Depression Inventory)** | Bajo | Beck 1996 + adaptación española | 21 ítems |
| **BAI (Beck Anxiety Inventory)** | Bajo | Beck 1988 | 21 ítems |
| **HADS (Hospital Anxiety and Depression Scale)** | Bajo | Zigmond 1983 + validación Colombia | 14 ítems (7+7) |
| **GDS-15 (Geriatric Depression Scale)** | Bajo | Yesavage 1982 + validación Colombia | 15 ítems sí/no |
| **PCL-5 (PTSD Checklist)** | Bajo | Weathers 2013 + validación latinoamericana | 20 ítems TEPT |
| **C-SSRS (Columbia Suicide Severity)** | Bajo | Columbia University + Posner 2011 | 6 ítems, riesgo suicida |
| **AUDIT-C** | Muy bajo | Saunders 1993 | 3 ítems consumo alcohol |
| **CAGE** | Muy bajo | Ewing 1984 | 4 ítems alcoholismo |
| **Escala de Pittsburgh (calidad de sueño)** | Bajo | Buysse 1989 | 19 ítems autoaplicada |

### 2.2 Atención y funciones ejecutivas

| Prueba | Costo implementación | Validación colombiana | Notas |
|---|---|---|---|
| **Stroop Test** (versión Golden 1978) | Bajo | Golden 1978 + Golden 2002 | Interferencia atencional |
| **Trail Making Test A y B** | Bajo | Reitan 1958 + normas Tombaugh 2004 | Velocidad + set-shifting |
| **WCST (Wisconsin Card Sorting Test)** | Alto | Grant 1993 + Berg 1948 | Flexibilidad cognitiva |
| **Torre de Londres (TOL)** | Medio | Krikorian 1994 | Planificación |
| **5 Point Test** | Medio | Regard 1982 | Fluidez figural |
| **FAB (Frontal Assessment Battery)** | Bajo | Dubois 2000 | Screening frontal |
| **INECO Frontal Screening (IFS)** | Bajo | Torralva 2009 + INECO | Screening frontal (ya en motor) |

### 2.3 Memoria

| Prueba | Costo implementación | Validación colombiana | Notas |
|---|---|---|---|
| **Rey Auditory Verbal Learning Test (RAVLT)** | Medio | Rey 1964 + Schmidt 1996 | Lista de palabras |
| **California Verbal Learning Test (CVLT)** | Alto | Delis 1987 | Curva de aprendizaje |
| **Benson Figure Recall** | Bajo | Kaplan 1983 | Figura compleja alternativa |
| **WMS-R Logical Memory** | Medio | Wechsler 1987 | Memoria lógica |
| **Test de Memoria de la figura de Rey (recuerdo)** | Bajo | Osterrieth 1944 (ya tenemos copia) | Evocación diferida |

### 2.4 Lenguaje

| Prueba | Costo implementación | Validación colombiana | Notas |
|---|---|---|---|
| **Boston Naming Test (BNT)** | Medio | Kaplan 1983 (ya en motor) | Denominación |
| **Token Test** | Bajo | De Renzi 1962 | Comprensión verbal |
| **Fluencia verbal fonológica (PMR)** | Bajo | Benton 1967 | Fonológica |
| **Fluencia verbal semántica (animales)** | Bajo | Newcombe 1969 | Semántica |
| **COWAT (Controlled Oral Word Association)** | Bajo | Benton 1978 | Fonológica anglosajona |
| **Test de vocabulario de WAIS** | Bajo | Wechsler | Ya cubierto por WAIS-III |

### 2.5 Visuoespacial y visuoconstructivo

| Prueba | Costo implementación | Validación colombiana | Notas |
|---|---|---|---|
| **Rey-Osterrieth Complex Figure (Copia)** | Bajo | Osterrieth 1944 (ya tenemos copia) | Copia |
| **Figura de Benson** | Bajo | Kaplan 1983 | Alternativa a Rey |
| **Cubos de WAIS/WISC** | Bajo | Wechsler (ya cubierto) | Razonamiento visuoespacial |
| **Test de la Hora (Clock Drawing Test)** | Bajo | Tuokko 1995 | Cribado visuoespacial |

### 2.6 Estimación intelectual breve

| Prueba | Costo implementación | Validación colombiana | Notas |
|---|---|---|---|
| **K-BIT (Kaufman Brief Intelligence Test)** | Medio | Kaufman 1990 (ya en motor) | CI breve |
| **Test de Matrices Progresivas de Raven** | Bajo | Raven 1936 | Razonamiento abstracto |
| **WASI (Weschsler Abbreviated Scale of Intelligence)** | Medio | Wechsler 1999 | 4 subtests |
| **Sattler Short Forms** | Bajo | Sattler 2008 (ya en utils) | Estimación rápida |

---

## 3. Criterios de aceptación para agregar un baremo

Antes de agregar una nueva prueba al motor, se requiere:

1. **Fuente verificable**: paper con normas originales + validación
   colombiana/latinoamericana preferiblemente.
2. **Datos cuantitativos**: tabla de baremos en formato
   `rango_puntaje`, `wais_range`, `z_score`, `suma_a_indice`,
   `puntaje_directo_a_t`, `puntaje_doble_resultado`, `edad_sexo` o
   `clasificacion_fija` — o derivable a uno de estos.
3. **Fixture de prueba**: al menos 1 caso clínico con resultado
   conocido que sirva de ground truth.
4. **Sin copyright restrictivo**: no agregar pruebas con copyright activo
   (WISC-V, WAIS-IV, RIAS, RBANS, CVLT-II) a menos que el usuario
   posea la licencia.
5. **Test de regresión**: agregar el caso al motor y verificar que pasa.

---

## 4. Pruebas YA implementadas con copyright activo

Estas se manejan con la **capa protegida Pearson** (S2.6):

- WISC-IV (versión 2003) — 16 tests verbatim con checkbox
- WAIS-III (versión 1997) — Ítems de búsqueda simbólica, vocabulario, etc.

El clínico debe confirmar consentimiento antes de acceder al texto
verbatim. Ver `pearsonProtected.js` (frontend) y
`audit.py` endpoint `POST /audit/clinical-access` (backend).

---

## 5. Backlog priorizado (orden sugerido)

1. **PHQ-9 / GAD-7** (ya usados en `screening.js`, falta motor)
2. **MoCA** (screening cognitivo de 5 min, altísima demanda)
3. **MMSE** (screening demencia AM)
4. **PCL-5** (TEPT, Ley 1448/2011 víctimas)
5. **Stroop Test** (interferencia atencional, baremos colombianos disponibles)
6. **Trail Making Test** (velocidad + set-shifting, normas Tombaugh)
7. **5 Point Test** (fluidez figural, no verbal)
8. **Rey Figure copia** (ya tenemos la copia, falta recuerdo)
9. **C-SSRS** (ya en `risk_assessments`, falta motor)
10. **Torre de Londres** (planificación)
11. **Test de la Hora** (rápido, baremos múltiples)
12. **Token Test** (comprensión verbal)

---

## 6. Cómo contribuir (futuro)

Para agregar una nueva prueba:

1. Abrir issue con la prueba propuesta y fuente bibliográfica.
2. Obtener visto bueno del autor.
3. Crear la entrada en `data/BD_NEURO_MAESTRA.json` con la
   estructura correcta (ver `data/ESTRUCTURA.md` o equivalente).
4. Crear tests en `tests/unit/clinical_engine/`.
5. Crear al menos 1 fixture ground truth en
   `tests/fixtures/casos_ground_truth/`.
6. Verificar que `pytest tests/ -q` pasa sin regresión.
7. Documentar en `docs/casos-clinicos/AUDITORIA_NUEVA_PRUEBA.md`.
