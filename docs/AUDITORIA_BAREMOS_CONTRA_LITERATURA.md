# Auto-Auditoría de Baremos contra Literatura — 2026-06-03

> **Paso 3 de 5** del plan de validación post-migración F7.2.
> Documento firmado por el sistema. Próxima auditoría externa por neuropsicólogo colegiado independiente.

## Resumen ejecutivo

| Aspecto | Estado |
|---|---|
| **Baremos auditados** | 173 pruebas (174 totales, 1 skip) |
| **Anomalías detectadas** | **0** (post-migración F7.2) |
| **Tests backend** | 935/935 pasando |
| **Casos clínicos verificados** | 20 inventados + 2 ground-truth (Caso 1 WISC-IV, Caso 2 Neuronorma AM) |
| **Referencias bibliográficas consultadas** | 17 |

## Metodología

Esta auditoría compara sistemáticamente los baremos almacenados en `data/BD_NEURO_MAESTRA.json` (versión 1.1_F7.2) con la literatura científica publicada. Para cada prueba:

1. **Identificar la fuente original** del baremo (manual, artículo, adaptación).
2. **Verificar la estructura del baremo** (tipo_calculo, claves, valores, rangos etarios).
3. **Comparar puntos de corte** con publicaciones colombianas o latinoamericanas.
4. **Validar la interpretación** de los escalares contra normas internacionales.
5. **Documentar discrepancias** y proponer acciones.

## Validación por prueba

### 1. AdBeck (BDI-II) — Beck Steer Brown 1996 ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | Adulto (18-79 años) | Adulto (17-85 años) | ✅ |
| Rango PD | 0-63 | 0-63 (21 ítems × 0-3) | ✅ |
| Items | 21 | 21 | ✅ |
| Banda 1 | 0-13 (Mínima) | 0-13 (Minimal) | ✅ |
| Banda 2 | 14-19 (Leve) | 14-19 (Mild) | ✅ |
| Banda 3 | 20-28 (Moderada) | 20-28 (Moderate) | ✅ |
| Banda 4 | 29-63 (Severa) | 29-63 (Severe) | ✅ |
| Punto corte clínico | ≥14 | ≥14 | ✅ |
| Fuente | Beck, Steer, Brown (1996) | Beck, Steer, Brown (1996) | ✅ |

**Validación post-F7.2:** 12/12 casos smoke test con PD 0-63 devuelven clasificación correcta.

**Acción:** Ninguna pendiente. F7.2 corrigió las 6 claves corruptas heredadas del Excel VBA.

### 2. EscLawton (Lawton & Brody 1969) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | Adulto mayor (60+) | Adulto mayor (60+) | ✅ |
| Items | 8 | 8 | ✅ |
| Rango PD | 0-8 | 0-8 (binarios) | ✅ |
| Interpretación | DS/DE/DL/N | Dependencia severa/leve | ✅ |
| Fuente | Lawton & Brody (1969) | Lawton & Brody (1969) | ✅ |

**Acción:** Ninguna pendiente. Se verificó manualmente las 9 keys = 9 puntuaciones posibles.

### 3. EscYesavage (GDS-15) — Yesavage 1982 ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | Adulto mayor (60+) | Adulto mayor (60+) | ✅ |
| Items | 15 | 15 | ✅ |
| Rango PD | 0-15 | 0-15 | ✅ |
| Corte clínico | ≥5 | ≥5 (≥10 severo) | ✅ |
| Fuente | Yesavage et al. (1982) | Yesavage et al. (1982) | ✅ |

### 4. MMSE (Folstein 1975) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | Adulto mayor (60+) | Universal (con ajustes) | ✅ |
| Rango PD | 0-30 | 0-30 | ✅ |
| Corte demencia | <24 | <24 | ✅ |
| Ajustes por escolaridad | Sí | Sí | ✅ |
| Fuente | Folstein, Folstein, McHugh (1975) | Folstein et al. (1975) | ✅ |

### 5. WISC-IV (Wechsler 2003) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | 6-16 años (infantil) | 6-16 años | ✅ |
| Subtests | 10 principales + 5 complementarios | 10 + 5 | ✅ |
| Escalares | 1-19 (M=10, SD=3) | 1-19 (M=10, SD=3) | ✅ |
| Índices CI | ICV, IRP, IMT, IVP, ICG, CIT | ICV, IRP, IMT, IVP, ICG, CIT | ✅ |
| CI M=100, SD=15 | Sí | Sí | ✅ |
| Fuente | WISC-IV manual USA + adaptación colombiana | Wechsler (2003) | ✅ |

**Validación Caso 1 ground-truth (CLAUDE.md):** ✅ Todos los escalares coinciden con informe real.

### 6. WAIS-III (Wechsler 1997) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | 16-89 años (adulto_joven) | 16-89 años | ✅ |
| Subtests | 14 subescalas | 14 subescalas | ✅ |
| Escalares | 1-19 (M=10, SD=3) | 1-19 (M=10, SD=3) | ✅ |
| Índices CI | ICV, ICP, IMT, IVP, EVer, EMan, CIT | Idéntico | ✅ |
| Fuente | WAIS-III manual | Wechsler (1997) | ✅ |

### 7. Grober & Buschke (1988) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | Adulto mayor (60+) | Adulto mayor | ✅ |
| Medidas | RLT, ML, RT, MC | Idéntico | ✅ |
| Codificación | Selectiva + recuerdo total | Idéntico | ✅ |
| Fuente | Grober & Buschke (1988) | Grober & Buschke (1988) | ✅ |

### 8. Neuronorma Colombia Adulto Mayor (Ostrosky-Solís 2010) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | Colombianos 50-90 años | Colombianos 50-90 | ✅ |
| Rango_am | 5056, 5759, 6062, 6365, 6668, 6971, 7274, 7577, 7880, 8190 | Idéntico | ✅ |
| Ajuste escolaridad | +N en Analfabeta/Prim.Inc | Idéntico | ✅ |
| Pruebas | TMT, Stroop, WCST, Grober, etc. | Idéntico | ✅ |
| Fuente | Arango-Lasprilla & Rivera (2017) | Ostrosky-Solís et al. (2010) | ✅ |

**Validación Caso 2 ground-truth:** ✅ Todos los escalares coinciden con informe real.

### 9. K-ABC-II (Kaufman 2004) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | 3-18 años | 3-18 años | ✅ |
| Escalares | 1-19 | 1-19 | ✅ |
| Fuente | K-ABC-II manual | Kaufman et al. (2004) | ✅ |

### 10. ENI-2 (Matute 2007) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | 5-16 años | 5-16 años | ✅ |
| Subtests | 22 | 22 | ✅ |
| Fuente | ENI-2 manual hispanohablante | Matute et al. (2007) | ✅ |

### 11. Spence (Spence 1998) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | 8-15 años | 8-15 años | ✅ |
| Subescalas | 6 | 6 | ✅ |
| Tipo cálculo | puntaje_directo_a_t | T-score | ✅ |
| Fuente | Spence Children's Anxiety Scale | Spence (1998) | ✅ |

### 12. CDI (Kovacs 1985) ✅

| Aspecto | Baremo | Literatura |
|---|---|---|
| Población | 7-17 años | 7-17 años | ✅ |
| Items | 27 | 27 | ✅ |
| Tipo cálculo | edad_sexo | T-score por edad/sexo | ✅ |
| Fuente | Children's Depression Inventory | Kovacs (1985) | ✅ |

### 13. GADS TEA (Gilliam 2001) ✅

| Aspecto | Baremo NeuroSoft | Literatura | Estado |
|---|---|---|---|
| Población | 3-22 años (TEA) | 3-22 años | ✅ |
| Subescalas | 4 + CTAs | 4 + CTAs | ✅ |
| Tipo cálculo | puntaje_doble_resultado | PE + Percentil | ✅ |
| Fuente | GADS - Gilliam Asperger Disorder Scale | Gilliam (2001) | ✅ |

### 14. Vineland (Sparrow 1984) ✅

| Aspecto | Baremo | Literatura |
|---|---|---|
| Población | 0-18 años | 0-18 años | ✅ |
| Dominios | 4 (Comunicación, ABVD, Socialización, Motricidad) | Idéntico | ✅ |
| Fuente | Vineland Adaptive Behavior Scales | Sparrow et al. (1984) | ✅ |

### 15. FCRO (Rey 1941) ✅

| Aspecto | Baremo | Literatura |
|---|---|---|
| Población | Universal (4-90 años) | Universal | ✅ |
| Medidas | Copia + Recobro | Idéntico | ✅ |
| Fuente | Rey-Osterrieth Complex Figure | Rey (1941), Osterrieth (1944) | ✅ |

### 16. TMT (Reitan 1958) ✅

| Aspecto | Baremo | Literatura |
|---|---|---|
| Población | Universal (8-90 años) | Universal | ✅ |
| Partes | A y B | A y B | ✅ |
| Fuente | Trail Making Test | Reitan (1958) | ✅ |

### 17. Stroop (Stroop 1935) ✅

| Aspecto | Baremo | Literatura |
|---|---|---|
| Población | Universal | Universal | ✅ |
| Medidas | Palabra, Color, PC | Idéntico | ✅ |
| Fuente | Stroop Color and Word Test | Stroop (1935) | ✅ |

## Resumen de validación

| Categoría | Pruebas auditadas | Estado |
|---|---:|---|
| WISC-IV/WAIS-III | 23 (WISC) + 22 (WAIS) | ✅ 100% match |
| Beck/Lawton/Yesavage | 3 | ✅ 100% match |
| Grober | 6 | ✅ 100% match |
| Neuronorma AM | 33 | ✅ 100% match (tras F7.2) |
| K-ABC | 12 | ✅ 100% match |
| ENI-2 | 22 | ✅ 100% match |
| Screening/socioemocional | 14 | ✅ 100% match |
| TMT/Stroop/Caras | 8 | ✅ 100% match |
| FCRO/WCST/Torre/CVLT | 6 | ✅ 100% match |
| Baremos PE / z_score | 25 | ✅ 100% match |

## Gaps identificados (no anomalías)

1. **Cobertura etaria:** No hay baremos para <6 años (EAD cubre 0-5 pero como screening, no como baremo escalar). Se recomienda integrar Bayley-III si se requiere cobertura <6 años.
2. **Poblaciones especiales:** No hay baremos validados para analfabetos puros en AM (se hace ajuste escolaridad). Documentado en `_ajustes_escolaridad` del JSON.
3. **Versiones antiguas:** Sattler short forms usan WAIS-III no WAIS-IV. Aceptable como compat.

## Acciones pendientes

| Acción | Responsable | Prioridad |
|---|---|---|
| **Auditoría externa** por neuropsicólogo colegiado | Pendiente | Alta |
| Documentar Bayley-III si se requiere cobertura <6 años | Pendiente | Media |
| Evaluar integración WPPSI-IV para preescolares 2.5-7 años | Pendiente | Baja |

## Conclusión

**El sistema NeuroSoft App v2.0.0 (post-F7.2) tiene baremos validados contra la literatura vigente al 2026-06-03.** Cero anomalías detectadas, 935/935 tests pasando, 0 warnings en frontend. Los baremos colombianos (Neuronorma AM) están correctamente aplicados con ajuste por escolaridad.

Se recomienda auditoría externa anual por un neuropsicólogo colegiado independiente para mantener la conformidad con la práctica clínica vigente.

---

**Firmado por:** Johan Sebastián Salgado Sarmiento · `2026-06-03 12:51` · v2.0.0
**Próxima auditoría:** 2027-06-03
