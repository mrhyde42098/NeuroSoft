# Validación de baremos vs CASOS_GROUND_TRUTH.md

**Fecha cierre:** 2026-05-19
**Estado:** ✅ **CERRADO** — los 15 casos clínicos están validados contra el motor real.

---

## Resumen ejecutivo final

| Métrica | Valor |
|---|---|
| Casos validados | **15 / 15** |
| Pruebas evaluadas | **110** (suma de pruebas en todos los casos) |
| Advertencias del motor | **0** |
| Pruebas `sin dato` | **0** |
| Baremos modificados en `BD_NEURO_MAESTRA.json` | **0** (regla del proyecto, intocable) |
| Bugs del MCP server detectados | **2 críticos**, ambos corregidos |

**Conclusión:** todos los escalares listados en `CASOS_GROUND_TRUTH.md` son los **producidos por el motor real** (`ClinicalEngine` + `strategies.py`) usando los baremos colombianos vigentes en `BD_NEURO_MAESTRA.json`. Lo único inventado es:
1. Los **datos demográficos** (nombres, fechas, motivos de consulta) — ficción QA, no PHI.
2. Los **PDs** — iterados manualmente hasta que el perfil escalar resultante coincidiera con el cuadro clínico narrado.

Los escalares **NO** fueron escritos a mano: son output del motor.

---

## Método de validación

Script: `docs/casos-clinicos/validar_casos.py`

```python
from app.domain.clinical_engine.engine import ClinicalEngine
from app.domain.clinical_engine.context import PatientContext

ctx = PatientContext.from_demographics(
    birth_date=fn, evaluation_date=fe,
    sexo=caso["sexo"], escolaridad=caso["escolaridad"],
)
result = engine.score(
    paciente_id=f"caso_{caso['id']}",
    puntajes=caso["puntajes"],
    patient_context=ctx,
)
```

Se itera por cada caso, se valida que:
- Todas las pruebas tienen escalar numérico o clasificación textual.
- Ninguna queda en `sin_norma` o sin clave encontrada.
- Las advertencias del motor (`result.advertencias`) están vacías.

Output completo en `RESULTADOS_VALIDACION.json` (un objeto por caso con los 7-10 puntajes resueltos).

---

## Bugs del MCP server (corregidos)

### ✅ Bug 1 · `_am_range` retornaba "8190" para edades fuera de AM

**Síntoma:** `score_prueba("AdTMTA", pd=45, edad_anios=24)` devolvía escalar usando la banda Neuronorma AM `8190` (81-90 años).

**Causa:** `mcp-servers/baremos/server.py:_am_range()` caía a `8190` por defecto cuando edad ∉ [50, 90].

**Fix:** retorna `None` si edad < 50. `score_prueba` responde `metadata.sin_norma=True` con motivo explícito.

### ✅ Bug 2 · ViGroberRLT etiquetada `wais_range` con claves Neuronorma AM

**Síntoma:** key `"70004"` no encontrada → resultado `_not_found`.

**Causa raíz:** la BD tiene `ViGroberRLT.tipo_calculo = "wais_range"` pero sus 419 claves tienen formato AM. Inconsistencia histórica de datos.

**Resolución:**
- NO se toca `BD_NEURO_MAESTRA.json` (regla intocable).
- El motor real (`strategies.py:202-209`) ya tiene fallback que prueba claves AM cuando la WAIS falla.
- El MCP server replica ese fallback y emite `note: "fallback AM aplicado"`.

---

## Cobertura por caso

Los 15 casos cubren los tres grandes grupos poblacionales y los principales perfiles clínicos relevantes en Colombia:

### Infantil (5 casos)
| ID | Perfil | Pruebas usadas |
|---|---|---|
| 3 | TDAH combinado (8a) | WISC-IV: 10 subtests |
| 4 | Dislexia (10a) | WISC-IV + ENI-2 |
| 5 | TEA Nivel 1 (12a) | WISC-IV + Mente-Ojos infantil |
| 6 | Discapacidad intelectual leve (9a) | WISC-IV |
| 7 | TEPT por maltrato (11a) | WISC-IV + ENI-2 atención |

### Adulto joven (5 casos)
| ID | Perfil | Pruebas usadas |
|---|---|---|
| 8 | Depresión mayor (24a) | WAIS-III + TMT-AB |
| 9 | TCE moderado (32a) | WAIS-III + Stroop + TMT |
| 10 | Ansiedad generalizada (28a) | WAIS-III + atención |
| 11 | TDAH adulto (35a) | WAIS-III + EF |
| 12 | Duelo complicado (41a) | WAIS-III + memoria |

### Adulto mayor (5 casos)
| ID | Perfil | Pruebas usadas |
|---|---|---|
| 13 | Deterioro cognitivo leve (68a) | Neuronorma AM completo |
| 14 | Alzheimer probable (76a, Primaria) | Neuronorma AM + Yesavage |
| 15 | Pseudodemencia depresiva (72a) | Neuronorma AM + Yesavage |
| 16 | Parkinson DCL (70a) | Neuronorma AM + EF |
| 17 | Control normal (65a, Universitaria) | Neuronorma AM |

---

## Próximos pasos (opcionales)

1. **Generar fixtures JSON automatizados** vía `/snapshot-paciente` para que estos 15 casos corran como tests de regresión en CI.
2. **Revisar etiqueta `wais_range` de ViGroberRLT** en BD — decidir con el equipo clínico si se corrige a `desconocido` o se mantiene el fallback (decisión de compatibilidad, no de motor).
3. **Ampliar cobertura** a perfiles menos comunes: epilepsia temporal, HIV-cognitivo, esclerosis múltiple, trastorno bipolar con afectación cognitiva.

---

## Reglas inviolables que se respetaron

1. **NUNCA modificar `BD_NEURO_MAESTRA.json`** sin consultar al usuario.
2. **El motor real es la fuente de verdad**, no el MCP. El MCP es proxy de inspección.
3. **Los escalares NO se inventan** — siempre son output del motor. Si un PD no produce el escalar esperado, se ajusta el PD, jamás el baremo.
4. **Los casos son ficción QA** — sin PHI real (Ley 1581/2012 — Habeas Data).
