# Auditoría Detallada de Baremos — 18 Pruebas Marcadas ✅

> **Generado:** 2026-06-03 11:38  ·  **Versión del motor:** ?  ·  **Total pruebas en BD:** 173

Esta auditoría es de **sólo lectura**: NO modifica `BD_NEURO_MAESTRA.json`. Identifica cobertura, gaps y posibles anomalías en los baremos de las 18 pruebas marcadas ✅ en el `PLAN_MAESTRO_GLOBAL.md` §7.2.

> **Nota:** Algunas pruebas marcadas viven en `src/data/screening.js` (módulo de tamizaje) en lugar de `BD_NEURO_MAESTRA.json` (motor clínico). El presente script audita esta última fuente. La auditoría del módulo screening vive en `/audit-completo` (skill).

## 1. Resumen ejecutivo

- Pruebas auditadas: **25**
- Pruebas encontradas en BD: **25**
- Pruebas NO encontradas: **0**
- Anomalías detectadas: **0**
- Pruebas sin baremos: **0**

## 2. Detalle por prueba

| Test ID | Categoría | Tipo cálculo | N claves | Min | Max | Forma | Anomalías |
|---|---|---|---:|---:|---:|---|---|
| `AdBeck` | screening | clasificacion_fija | 5 | 0.0 | 0.0 | ✔ short-form | — |
| `AdWAISCC` | wais_iii | wais_range | 414 | 1.0 | 19.0 | — | — |
| `AdWAISEMan` | wais_iii | suma_a_indice | 91 | 47.0 | 155.0 | — | — |
| `AdWAISFI` | wais_iii | wais_range | 156 | 1.0 | 19.0 | — | — |
| `AdWAISHI` | wais_iii | wais_range | 138 | 1.0 | 19.0 | — | — |
| `AdWAISI` | wais_iii | wais_range | 174 | 1.0 | 19.0 | — | — |
| `AdWAISICP` | wais_iii | suma_a_indice | 55 | 50.0 | 150.0 | — | — |
| `AdWAISICV` | wais_iii | suma_a_indice | 55 | 50.0 | 150.0 | — | — |
| `AdWAISIMT` | wais_iii | suma_a_indice | 55 | 50.0 | 150.0 | — | — |
| `AdWAISIVP` | wais_iii | suma_a_indice | 37 | 54.0 | 143.0 | — | — |
| `AdWAISL` | wais_iii | wais_range | 132 | 1.0 | 19.0 | — | — |
| `AdWAISRO` | wais_iii | wais_range | 318 | 1.0 | 19.0 | — | — |
| `AdWAISV` | wais_iii | wais_range | 402 | 1.0 | 19.0 | — | — |
| `AdWASIEVer` | wais_iii | suma_a_indice | 109 | 48.0 | 155.0 | — | — |
| `EscKertesz` | screening | clasificacion_fija | 37 | — | — | ✔ short-form | — |
| `EscLawton` | screening | clasificacion_fija | 9 | — | — | ✔ short-form | — |
| `EscYesavage` | screening | clasificacion_fija | 16 | — | — | ✔ short-form | — |
| `FluidAnim` | lenguaje | desconocido | 304 | 1.0 | 18.0 | — | — |
| `FluidP` | lenguaje | desconocido | 288 | 2.0 | 18.0 | — | — |
| `MMSE` | screening | clasificacion_fija | 31 | — | — | ✔ short-form | — |
| `NiFCROCop` | visuoespacial | z_score | 12 | 11.76 | 35.1 | — | — |
| `NiFCRORec` | visuoespacial | z_score | 12 | 5.63 | 22.7 | — | — |
| `SDMT` | atencion_velocidad | desconocido | 709 | 2.0 | 18.0 | — | — |
| `ViTMTA` | atencion_velocidad | desconocido | 2458 | 2.0 | 18.0 | — | — |
| `ViTMTB` | atencion_velocidad | desconocido | 6023 | 2.0 | 18.0 | — | — |

## 5. Recomendaciones

1. Para cada prueba con `cobertura_baja` (n<10), evaluar si la población clínica requiere más cobertura. Si no aplica, documentar y mantener.
2. Para pruebas con `valor_maximo_atipico` (>200), verificar contra el manual original. NO modificar sin consulta al autor.
3. Pruebas NO encontradas: evaluar si el id está mal escrito o si realmente no está implementado (ver §7.2 del plan maestro).
4. Esta auditoría debe ejecutarse antes de cada release y el reporte debe adjuntarse a la documentación clínica del sistema.

---

**Normograma aplicable:** Resolución 1995 de 1999 art. 11 (calidad del dato clínico) · Ley 1581 de 2012 (Habeas Data) · ISO/IEC 25012 (calidad de datos).

**Generado por:** `scripts/audit_baremos_18.py`