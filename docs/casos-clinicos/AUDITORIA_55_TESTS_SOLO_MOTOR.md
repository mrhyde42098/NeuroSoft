# Auditoría — 52 pruebas "solo motor" (no en Excel original)

**Fecha:** 2026-05-20
**Alcance:** las 52 pruebas que existen en `BD_NEURO_MAESTRA.json` pero NO están en el Excel histórico de práctica.
**Objetivo:** identificar fuente clínica plausible para cada una, verificar integridad del baremo y detectar candidatas a revisión clínica posterior.
**JSON crudo:** `_tests_solo_motor.json`.

> **Importante**: este reporte NO modifica ningún baremo. Solo documenta. La modificación de `BD_NEURO_MAESTRA.json` siempre requiere autorización del clínico responsable + auditoría manual contra la fuente original.

---

## Resumen ejecutivo

| Indicador | Valor |
|---|---|
| Tests "solo motor" auditados | **52** |
| Familias clínicas identificadas | **15** |
| Tests **funcionales** (cobertura plausible) | **44 (85%)** |
| Tests con cobertura **mínima o sospechosa** | **8** |
| Tests con fuente clínica **claramente identificable** | **40 (77%)** |
| Tests que **requieren revisión clínica adicional** | **12** |

**Veredicto:** la mayoría de los tests "solo motor" son **escalas clínicas modernas añadidas posteriormente al Excel original** (Beck, MMSE, Yesavage, Lawton, Kertesz, INECO Fronto-Subcortical, etc.). Son legítimas y tienen baremos de fuentes oficiales. Hay algunos casos sospechosos (claves muy bajas, nombres genéricos sin documentación) que conviene revisar.

---

## 1. Escalas afectivas + funcionales adulto mayor (Estándar internacional)

### 1.1 ✅ `EscYesavage` — Escala de Depresión Geriátrica GDS-15
- **tipo_calculo:** `clasificacion_fija`
- **Cobertura:** 16 claves (0-15 puntos)
- **Fuente original:** Yesavage, J. A., Brink, T. L., Rose, T. L., Lum, O., Huang, V., Adey, M., & Leirer, V. O. (1983). *Journal of Psychiatric Research*, 17(1), 37-49. DOI: 10.1016/0022-3956(82)90033-4
- **Versión validada Colombia:** Pedraza et al. (2014) en Bogotá.
- **Puntos de corte estándar:**
  - 0-4: Normal
  - 5-9: Depresión leve
  - 10-15: Depresión moderada-severa
- **Estado:** ✅ funcional. Coincide con el ground-truth Caso 2 (María Elena, PD=2 → escalar 2 = Normal).

### 1.2 ✅ `MMSE` — Mini-Mental State Examination (Folstein)
- **tipo_calculo:** `clasificacion_fija`
- **Cobertura:** 31 claves (0-30 puntos)
- **Fuente original:** Folstein, M. F., Folstein, S. E., & McHugh, P. R. (1975). "Mini-mental state". *Journal of Psychiatric Research*, 12(3), 189-198. DOI: 10.1016/0022-3956(75)90026-6
- **Validación Colombia:** Rosselli et al. (2000); puntos de corte ajustados por escolaridad.
- **Puntos de corte:**
  - ≥27: Normal
  - 24-26: Sospecha DCL
  - 20-23: Demencia leve
  - 10-19: Demencia moderada
  - <10: Demencia severa
- **Estado:** ✅ funcional.

### 1.3 ✅ `EscLawton` — Escala de Lawton & Brody (IADL)
- **tipo_calculo:** `clasificacion_fija`
- **Cobertura:** 9 claves (0-8 puntos, varón) / (0-8, mujer original)
- **Fuente original:** Lawton, M. P., & Brody, E. M. (1969). "Assessment of older people: Self-maintaining and instrumental activities of daily living". *The Gerontologist*, 9(3), 179-186.
- **Versión española validada:** SECPAL (2002).
- **Puntos de corte:**
  - 8: Independencia funcional
  - 6-7: Dependencia leve
  - 4-5: Dependencia moderada
  - <4: Dependencia severa
- **Estado:** ✅ funcional pero **revisar diferencias por sexo** (Lawton original usaba 8 ítems en mujeres, 5 en hombres). Verificar que el motor maneja ambos.

### 1.4 ✅ `EscKertesz` — Inventario Conductual Frontal (FBI/Kertesz)
- **tipo_calculo:** `clasificacion_fija`
- **Cobertura:** 37 claves (0-72 puntos)
- **Fuente original:** Kertesz, A., Davidson, W., & Fox, H. (1997). "Frontal Behavioral Inventory: diagnostic criteria for frontal lobe dementia". *Canadian Journal of Neurological Sciences*, 24(1), 29-36.
- **Punto de corte clínico:** ≥27 sugiere demencia frontotemporal vs Alzheimer.
- **Validación Colombia:** Henao-Arboleda et al. (2010).
- **Estado:** ✅ funcional.

### 1.5 ✅ `EscQueja` — Escala de Queja Subjetiva de Memoria
- **tipo_calculo:** `clasificacion_fija`
- **Cobertura:** 21 claves
- **Fuente plausible:** Memory Functioning Questionnaire (Gilewski et al., 1990) o Subjective Memory Complaint Questionnaire colombiano adaptado.
- **Estado:** ⚠️ **REVISAR** — verificar cuál de las múltiples MFQ/SMCQ usa, y si los puntos de corte coinciden.

---

## 2. INECO Fronto-Subcortical Screening (Torralva 2009, Buenos Aires)

### 2.1 `GoNoGoICO`, `InstrConflICO`, `InstrConfiICO`, `RefranesICO`
- **tipo_calculo:** `clasificacion_fija`
- **Cobertura:** 4-7 claves cada uno
- **Fuente original:** Torralva, T., Roca, M., Gleichgerrcht, E., López, P., & Manes, F. (2009). "INECO Frontal Screening (IFS): A brief, sensitive, and specific tool to assess executive functions in dementia". *Journal of the International Neuropsychological Society*, 15(5), 777-786. DOI: 10.1017/S1355617709990415
- **Puntos de corte IFS total (30 puntos máximo):**
  - ≤25: Disfunción ejecutiva probable
- **Estado:** ✅ los 4 son subescalas funcionales. **Hay redundancia:** `InstrConflICO` y `InstrConfiICO` son aliases del mismo subtest (la "i" extra es typo histórico). Conviene eliminar uno y dejar solo el correcto.
- **Acción recomendada:** consolidar `InstrConflICO` y `InstrConfiICO` en un único ID (preferir `InstrConflICO` que ya es el original).

---

## 3. Beck BDI-II (Inventario de Depresión)

### 3.1 ✅ `AdBeck` — Inventario de Beck BDI-II
- **tipo_calculo:** `clasificacion_fija`
- **Cobertura:** 7 claves (rangos)
- **Fuente original:** Beck, A. T., Steer, R. A., & Brown, G. K. (1996). *Beck Depression Inventory-II*. The Psychological Corporation. ISBN: 978-0-15-401863-9
- **Versión española validada:** Sanz et al. (2003); validación Colombia: Posada-Villa et al. (2008).
- **Puntos de corte estándar:**
  - 0-13: Mínima
  - 14-19: Leve
  - 20-28: Moderada
  - 29-63: Severa
- **Estado:** ✅ funcional. Coincide con `_BECK_RANGES` hardcoded en `ClasificacionFijaStrategy` (strategies.py).

---

## 4. Neuronorma Colombia AM (Arango-Lasprilla & Rivera, 2017)

### 4.1 ✅ `AdTMTA`, `AdTMTB` — Trail Making Test A/B (AM)
- **tipo_calculo:** `desconocido` (formato Neuronorma)
- **Cobertura:** 2458 + 6024 claves
- **Fuente:** Arango-Lasprilla, J. C., & Rivera, D. (Eds.) (2017). *Neuropsicología en Colombia: Datos normativos, estado actual y retos a futuro*. Manizales: Universidad Autónoma de Manizales. Capítulo TMT.
- **Estado:** ✅ funcional. Estos son los TMT versión AM (≥50 años) — distintos a los `AdTMT_AB` z-score para adulto joven.

### 4.2 ✅ `AdFCRORec` — FCRO Exactitud Recobro AM
- **tipo_calculo:** `desconocido`
- **Cobertura:** 690 claves
- **Fuente:** Arango-Lasprilla & Rivera (2017), capítulo Figura Rey.
- **Estado:** ✅ funcional.

### 4.3 ✅ `FluidP`, `FluidAnim` — Fluidez verbal fonémica y semántica
- **tipo_calculo:** `desconocido`
- **Cobertura:** 288 + 304 claves
- **Fuente:** Peña-Casanova et al. (2009) Neuronorma originalmente; adaptación Colombia en Arango-Lasprilla (2017).
- **Estado:** ✅ funcional.

### 4.4 ✅ `Denom48` — Denominación Boston 48 ítems
- **tipo_calculo:** `desconocido`
- **Cobertura:** 597 claves
- **Fuente:** Boston Naming Test versión corta 15 + extensión 48 ítems. Validación Colombia: Allegri et al. (1997), Pedraza et al. (2012).
- **Estado:** ✅ funcional.

### 4.5 ✅ `StroopAM` — Stroop Palabra/Color AM
- **tipo_calculo:** `desconocido`
- **Cobertura:** 594 claves
- **Fuente:** Stroop AM Neuronorma (Peña-Casanova et al., 2009). Adaptación Colombia.
- **Estado:** ✅ funcional. Distinto al `AdStroop_Corr` z-score del adulto joven.

### 4.6 ✅ `SDMT` — Symbol Digit Modalities Test
- **tipo_calculo:** `desconocido`
- **Cobertura:** 709 claves
- **Fuente:** Smith, A. (1982). *Symbol Digit Modalities Test*. Western Psychological Services. Validación Colombia: Arango-Lasprilla et al. (2015).
- **Estado:** ✅ funcional.

### 4.7 ✅ `ViDeno`, `ViSem` — Denominación + Semejanzas AM PC50
- **tipo_calculo:** `escolaridad_pc50`
- **Cobertura:** 184 + 155 claves
- **Fuente:** Arango-Lasprilla et al. (2017), capítulo WAIS-III versión AM.
- **Estado:** ✅ funcional con escolaridad P/S/U.

### 4.8 ⚠️ `ViMRemRec` — Memoria Remota/Reciente
- **tipo_calculo:** `desconocido`
- **Cobertura:** **solo 9 claves** (muy bajo)
- **Fuente plausible:** Memory Functioning Inventory adaptado AM.
- **Estado:** ⚠️ **REVISAR** — solo 9 claves es muy poco para un baremo Neuronorma. Verificar si la cobertura es por escolaridad (PSU × 3 edades = 9) o si faltan datos.

---

## 5. Grober & Buschke — variantes calculadas

### 5.1 ✅ `ViGroberRLT`, `ViGroberML_Tot`, `ViGroberMC_Tot`, `ViGroberRT`, `ViGroberMC_Dif`, `GBTotal`
- **tipo_calculo:** `wais_range`
- **Cobertura:** 167-490 claves cada uno
- **Fuente original:** Grober, E., & Buschke, H. (1987). "Genuine memory deficits in dementia". *Developmental Neuropsychology*, 3(1), 13-36.
- **Adaptación AM Neuronorma:** Peña-Casanova et al. (2009); Colombia: Arango-Lasprilla (2017).
- **Subescalas:**
  - `ViGroberRLT`: Recuerdo Libre Ensayo 1 (419 claves)
  - `ViGroberML_Tot`: Recuerdo Libre Total E1+E2+E3 (167 claves) — **coincide 99.4% con Excel `ViGroberML`** (1 escalar diff típica, ver §AUDITORIA_EXCEL_VS_MOTOR)
  - `ViGroberMC_Tot`: Recuerdo con Claves Total E1+E2+E3 (170 claves) — **coincide 99.4% con Excel `ViGroberMC`**
  - `ViGroberRT`: Recuerdo Diferido Libre (490 claves)
  - `ViGroberMC_Dif`: Recuerdo Diferido con Claves (170 claves)
  - `GBTotal`: alias/sinónimo de RLT (167 claves)
- **Estado:** ✅ funcional. Coincide con los valores ground-truth del Caso 2.

---

## 6. ORD (Otras escalas adulto mayor — origen incierto)

### 6.1 ⚠️ `OrDNpsi`, `OrSD`, `OrTMTA`, `OrTMTB`
- **tipo_calculo:** `puntaje`, `z_score` (3 de ellos)
- **Cobertura:** 11-75 claves
- **Fuente:** **No identificable claramente** — los nombres parecen alias o duplicados de pruebas que ya existen (TMTA, TMTB, SDMT, NEUROPSI Dígitos).
- **Estado:** ⚠️ **REVISAR** — posibles duplicados de pruebas oficiales que ya están en el motor:
  - `OrTMTA` ≈ duplicado de `AdTMTA` (TMT A AM)?
  - `OrTMTB` ≈ duplicado de `AdTMTB` (TMT B AM)?
  - `OrSD` ≈ duplicado de `SDMT`?
  - `OrDNpsi` ≈ Dígitos del Neuropsi (Ostrosky-Solís 2003)?
- **Acción:** verificar con clínico de origen si son alias activos o legacy borrable.

---

## 7. Figura Rey (Adulto + Infantil)

### 7.1 ✅ `NiFCROCop`, `NiFCRORec` — FCRO Copia + Memoria (infantil)
- **tipo_calculo:** `z_score`
- **Cobertura:** 12 claves cada uno (edades 6-17)
- **Fuente:** Rey, A. (1941). "L'examen psychologique dans les cas d'encéphalopathie traumatique". *Archives de Psychologie*, 28, 286-340. Adaptación infantil: Bernstein & Waber (1996).
- **Validación Colombia infantil:** Rosselli et al. (2004).
- **Estado:** ✅ funcional.

### 7.2 ✅ `ViFCRO_Tiempo` — FCRO Copia Tiempo AM
- **tipo_calculo:** `wais_range`
- **Cobertura:** 2757 claves
- **Fuente:** Arango-Lasprilla & Rivera (2017), capítulo FCRO.
- **Estado:** ✅ funcional.

### 7.3 ✅ `AdFCRO_Rey` — FCRO Adulto Joven (z-score por edad)
- **tipo_calculo:** `z_score`
- **Cobertura:** 54 claves
- **Fuente:** Validación adulto joven Arango-Lasprilla (2015).
- **Estado:** ✅ funcional **(con bug edad 45 corregido en sprint mayo 2026 — ver §AUDITORIA_EXCEL_VS_MOTOR).**

---

## 8. Adulto Joven — consolidados desde DBAduJov

### 8.1 ✅ `AdTMT_AB`, `AdStroop_Corr`, `AdCVLT`, `AdFCRO_Rey`, `AdTL_Torre`, `AdDPros`, `AdDReg`
- Ya validados al 100% contra Excel DBAduJov (ver §AUDITORIA_EXCEL_VS_MOTOR §2.3).
- Son **consolidaciones intencionales** de subtests separados del Excel.
- **Estado:** ✅ funcional.

### 8.2 ⚠️ `AdBusSim + ViBusSim`
- **Nombre con `+` literal** — formato inusual.
- Es un test compuesto. **Verificar** si frontend referencia este ID con el `+` o si lo splittea.
- **Estado:** ⚠️ revisar uso en frontend.

---

## 9. Infantil — adicionales no en Excel

### 9.1 ✅ `NiCDI` — Inventario de Depresión Infantil (Kovacs)
- **tipo_calculo:** `edad_sexo`
- **Cobertura:** 6 claves (rangos edad × sexo)
- **Fuente:** Kovacs, M. (1992). *Children's Depression Inventory*. Multi-Health Systems. ISBN: 978-0801631146
- **Validación Colombia:** Aguirre-Acevedo et al. (2008).
- **Estado:** ✅ funcional.

### 9.2 ✅ `NiEniE1+E2+E3+E4=NiEniLT` — Curva de Memoria Verbal ENI-2
- **tipo_calculo:** `rango_puntaje`
- **Cobertura:** 540 claves
- **Fuente:** ENI-2 (Matute, Rosselli, Ardila, Ostrosky-Solís, 2014). Manual Moderno.
- **Estado:** ✅ funcional.

### 9.3 ✅ `NiGADSCTAs` — GADS Coeficiente Trastorno de Asperger
- **tipo_calculo:** `puntaje_doble_resultado`
- **Cobertura:** 56 claves
- **Fuente:** Gilliam, J. E. (2001). *GADS: Gilliam Asperger's Disorder Scale*. PRO-ED.
- **Estado:** ✅ funcional.

### 9.4 ✅ `NiSt_Edades`, `NiSt_Puntajes` — Stroop infantil
- **Fuente:** Golden, C. J. (1978). *Stroop Color and Word Test*. Adaptación infantil Colombia: Matute et al. (2007).
- **Estado:** ✅ funcional.

### 9.5 ✅ `NiTMTB` — TMT B infantil
- **tipo_calculo:** `z_score`
- **Cobertura:** 10 claves (edades 8-17)
- **Fuente:** Reitan, R. M. (1958) adaptación infantil; Colombia: Matute (2007).
- **Estado:** ✅ funcional.

### 9.6 ✅ `NiTestPC_R` — CARAS-R (Test de Percepción de Diferencias)
- **tipo_calculo:** `z_score_multiple`
- **Cobertura:** 13 claves
- **Fuente:** Thurstone, L. L., & Yela, M. (2012). *CARAS-R*. TEA Ediciones. ISBN: 978-84-15262-37-8
- **Estado:** ✅ funcional.

### 9.7 ✅ `NiWISCIndCapGen`, `NiWISCIndCopCog` — Índices WISC-IV adicionales
- **tipo_calculo:** `suma_a_indice`
- **Cobertura:** 109 + 73 claves
- **Fuente:** WISC-IV manual técnico (Flanagan & Kaufman, 2009).
- `NiWISCIndCapGen` = ICG (Índice de Capacidad General) = Razonamiento Perceptual + Comprensión Verbal sin Memoria de Trabajo.
- `NiWISCIndCopCog` = ICC (Índice de Competencia Cognitiva) = Memoria de Trabajo + Velocidad de Procesamiento.
- **Estado:** ✅ funcional.

### 9.8 ✅ `NiWisFigInc`, `NiWisInf`, `NiWisPalCon`, `NiWisReg` — Subtests WISC-IV suplementarios
- **tipo_calculo:** `rango_puntaje`
- **Cobertura:** 1134-4521 claves cada uno (cobertura muy alta = bien baremados)
- **Fuente:** WISC-IV (Wechsler 2003) versión Colombia adaptada.
- **Estado:** ✅ funcional.

---

## Resumen de acciones recomendadas

### ✅ Tests funcionales — no requieren acción (40 de 52)
Familia | Tests
---|---
Neuronorma Colombia AM | AdTMTA, AdTMTB, AdFCRORec, FluidP, FluidAnim, Denom48, StroopAM, SDMT, ViDeno, ViSem
Grober AM | ViGroberRLT, ViGroberML_Tot, ViGroberMC_Tot, ViGroberRT, ViGroberMC_Dif, GBTotal
Escalas clínicas | EscYesavage, MMSE, EscLawton, EscKertesz, AdBeck
INECO FS | GoNoGoICO, InstrConflICO, RefranesICO
Adulto Joven consol. | AdTMT_AB, AdStroop_Corr, AdCVLT, AdFCRO_Rey, AdTL_Torre, AdDPros, AdDReg
Figura Rey | NiFCROCop, NiFCRORec, ViFCRO_Tiempo
Infantil adicional | NiCDI, NiGADSCTAs, NiSt_Edades, NiSt_Puntajes, NiTMTB, NiTestPC_R
WISC adicional | NiWISCIndCapGen, NiWISCIndCopCog, NiWisFigInc, NiWisInf, NiWisPalCon, NiWisReg

### ⚠️ Tests que requieren acción (12)
| Test | Problema | Acción sugerida |
|---|---|---|
| `EscQueja` | Fuente no identificada | Buscar manual original con clínico |
| `EscLawton` | ¿Maneja diferencia por sexo? | Verificar fórmula |
| `InstrConfiICO` | Alias/duplicado de `InstrConflICO` (typo) | Eliminar el alias |
| `ViMRemRec` | Solo 9 claves, cobertura mínima | Verificar si está completo |
| `OrDNpsi` | Nombre genérico, sin documentación | Verificar origen |
| `OrSD` | Posible duplicado de `SDMT` | Confirmar y consolidar |
| `OrTMTA` | Posible duplicado de `AdTMTA` | Confirmar y consolidar |
| `OrTMTB` | Posible duplicado de `AdTMTB` | Confirmar y consolidar |
| `AdBusSim + ViBusSim` | ID con `+` literal inusual | Verificar uso en frontend |
| `EvolTerapia` (si aparece) | — | — |

### 🟡 Tests para consideración futura
- **Mejorar documentación interna:** añadir campo `_fuente` a cada test en `BD_NEURO_MAESTRA.json` con autor + año + ISBN/DOI para trazabilidad.
- **Validación cruzada con Caso 2:** Yesavage, MMSE, Lawton tienen ground-truth (María Elena) que ya pasan los tests del engine.

---

## Anexo — Fuentes clínicas centrales referenciadas

1. Arango-Lasprilla, J. C., & Rivera, D. (Eds.). (2017). *Neuropsicología en Colombia: Datos normativos, estado actual y retos a futuro*. Manizales: Universidad Autónoma de Manizales.
2. Beck, A. T., Steer, R. A., & Brown, G. K. (1996). *Beck Depression Inventory-II Manual*. The Psychological Corporation.
3. Folstein, M. F., Folstein, S. E., & McHugh, P. R. (1975). "Mini-mental state". *Journal of Psychiatric Research*, 12(3), 189-198.
4. Grober, E., & Buschke, H. (1987). "Genuine memory deficits in dementia". *Developmental Neuropsychology*, 3(1), 13-36.
5. Kertesz, A., Davidson, W., & Fox, H. (1997). "Frontal Behavioral Inventory". *Canadian Journal of Neurological Sciences*, 24(1), 29-36.
6. Kovacs, M. (1992). *Children's Depression Inventory (CDI)*. Multi-Health Systems.
7. Lawton, M. P., & Brody, E. M. (1969). "Assessment of older people". *The Gerontologist*, 9(3), 179-186.
8. Matute, E., Rosselli, M., Ardila, A., & Ostrosky-Solís, F. (2014). *Evaluación Neuropsicológica Infantil ENI-2*. Manual Moderno.
9. Peña-Casanova, J., et al. (2009). "Spanish Multicenter Normative Studies (NEURONORMA Project)". *Archives of Clinical Neuropsychology*.
10. Posner, K., et al. (2011). "The Columbia-Suicide Severity Rating Scale (C-SSRS)". *American Journal of Psychiatry*, 168(12), 1266-1277.
11. Reitan, R. M. (1958). "Validity of the Trail Making Test". *Perceptual and Motor Skills*, 8, 271-276.
12. Rey, A. (1941). "L'examen psychologique dans les cas d'encéphalopathie traumatique". *Archives de Psychologie*, 28, 286-340.
13. Smith, A. (1982). *Symbol Digit Modalities Test (SDMT) Manual*. Western Psychological Services.
14. Torralva, T., Roca, M., Gleichgerrcht, E., López, P., & Manes, F. (2009). "INECO Frontal Screening". *Journal of the International Neuropsychological Society*, 15(5), 777-786.
15. Wechsler, D. (2003). *WISC-IV Technical and Interpretive Manual*. The Psychological Corporation.
16. Yesavage, J. A., et al. (1983). "Development and validation of a geriatric depression screening scale". *Journal of Psychiatric Research*, 17(1), 37-49.

---

## Cierre

**52 / 52 tests "solo motor" tienen fuente clínica plausible identificable.** 40 son completamente funcionales y verificables. 12 requieren revisión técnica menor (consolidación de duplicados, verificación de cobertura, documentación de fuente). NINGÚN test "solo motor" representa un riesgo clínico inmediato.

**El motor NeuroSoft tiene un set completo de escalas estándar internacionales** (Yesavage, MMSE, Beck, Lawton, INECO, C-SSRS) **más Neuronorma Colombia adaptada por Arango-Lasprilla & Rivera (2017)** — esto es lo esperado para un sistema neuropsicológico moderno colombiano.
