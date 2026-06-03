# Plan de Migración de Baremos — F7.2

**Origen:** Auditoría sistemática de `data/BD_NEURO_MAESTRA.json` (F7.1) · 25 pruebas marcadas como prioritarias verificadas, 3 anomalías detectadas, 22 OK.

**Regla de oro:** La base de datos clínica es **intocable sin consulta previa al responsable del tratamiento** (ver `CLAUDE.md` raíz y sub-`CLAUDE.md` backend). Este documento describe el plan propuesto, no la ejecución.

---

## 1. Anomalías confirmadas en F7.1

### 1.1 `AdBeck` — Inventario de Beck BDI-II · **CRÍTICO** ❌

**Estado actual en `data/BD_NEURO_MAESTRA.json`:**

```json
{
  "id": "AdBeck",
  "nombre": "Inventario de Beck BDI-II",
  "tipo_calculo": "clasificacion_fija",
  "tipo_metrica": "ci",
  "baremos": {
    "Rango": ["EDAD", "DIG"],
    "16190": [1619, 0],
    "16191": [1619, 1],
    "16192": [1619, 2],
    "16193": [1619, 3],
    "16194": [1619, 4],
    "16195": [1619, 5]
  }
}
```

**Problema:** Los 6 rangos con prefijo `1619` y valores `[1619, 0-5]` no corresponden a ningún baremo válido del BDI-II. La convención del sistema VBA original tiene una estructura `{RANGO_EDAD}{PD_3digitos}` (p. ej. `16190` = 16-19 años, PD 0) pero los valores `[1619, 0]` carecen de clasificación reconocida.

**Baremo oficial Beck BDI-II (Beck, Steer & Brown, 1996):**

| Suma 21 ítems (0-63) | Clasificación |
|---|---|
| 0-13 | Mínimo |
| 14-19 | Leve |
| 20-28 | Moderado |
| 29-63 | Severo |

No requiere baremo por edad ni sexo: la suma total es la métrica y la clasificación es fija. El `tipo_calculo` apropiado es `clasificacion_fija`.

**Riesgo clínico:** Si el motor consulta `AdBeck` y devuelve `[1619, 0]` en `metadata`, **toda interpretación downstream queda corrupta** (la integración cuantitativa-cualitativa — principio P1 — no puede operar sin una categoría real).

**Verificación adicional:** Se presume que esta anomalía proviene de la migración desde el Excel original `SistemaHC_Prac Johan_Sebastian_Salgado.xlsm`. No se ha localizado la fila/columna exacta en ese archivo.

**Acción propuesta (no ejecutada, pendiente de aprobación):**

1. **Bloqueo defensivo** — agregar a la lista de pruebas en cuarentena en `app/domain/clinical_engine/loader.py` para que el motor devuelva `_not_found` y muestre advertencia `"baremo en revisión"` en la UI.
2. **Reemplazo por baremo oficial BDI-II** — `baremos = { "0": "Mínimo", "14": "Leve", "20": "Moderado", "29": "Severo" }` (con `tipo_calculo: "clasificacion_fija"`, `tipo_metrica: "clasidad"`).
3. **Backup** — `data/BD_NEURO_MAESTRA.backup-pre-f7-2-adbeck.json` antes de cualquier cambio.
4. **Validación** — ejecutar los 27 tests del engine + 134 tests ground truth después del cambio. Caso clínico de smoke test: paciente 28a, BDI-II = 22 → "Moderado".

### 1.2 `EscLawton` — Escala de Lawton y Brody (IADL) · **FALSO POSITIVO** ✅

**Estado actual:**

```json
{
  "id": "EscLawton",
  "nombre": "Escala de Lawton y Brody (IADL)",
  "tipo_calculo": "clasificacion_fija",
  "tipo_metrica": "ci",
  "baremos": {
    "0": "DS", "1": "DS", "2": "DS", "3": "DE",
    "4": "DE", "5": "DL", "6": "DL", "7": "DL", "8": "N"
  }
}
```

**Problema reportado por F7.1:** `n_claves = 9` se marcó como "cobertura_baja" (`n < 10`).

**Diagnóstico:** **Falso positivo**. La Escala de Lawton tiene 8 ítems por construcción (original Lawton & Brody, 1969). El rango posible de la suma es 0-8. La tabla tiene exactamente 9 claves (0, 1, 2, …, 8) y cubre **el 100 % del espacio de puntuaciones posibles**. La heurística `n < 10` del audit es inadecuada para instrumentos intrínsecamente cortos.

**Baremo oficial Lawton IADL (versión validada en Colombia, confirmada en Arango-Lasprilla & Rivera, 2017):**

| Suma (0-8) | Clasificación |
|---|---|
| 0-2 | Dependencia Severa (DS) |
| 3-4 | Dependencia Establecida (DE) |
| 5-7 | Dependencia Leve (DL) |
| 8 | Normal / Independiente (N) |

**Conclusión:** No requiere migración. La heurística del audit debe afinarse para distinguir entre "n bajo por diseño" y "n bajo por dato faltante".

**Acción propuesta (mejora del audit, no del baremo):**

1. Mantener la regla general `n < 10 → cobertura_baja`.
2. Agregar una **lista blanca de instrumentos intrínsecamente cortos** que se eximen de la regla:
   - `EscLawton` (IADL, 8 ítems)
   - `EscYesavage` (GDS-15, 15 ítems con corte fijo)
   - `C-SSRS` (6 ítems con corte)
   - `EscPfeffer` (FAQ, 10 ítems)
   - `EscHamilton` (HAM-A 14 ítems, HAM-D 17 ítems)
   - Cualquier test con `tipo_calculo = "clasificacion_fija"` donde el rango PD es ≤ 30.
3. Documentar la lista blanca en `scripts/audit_baremos_18.py`.

### 1.3 `AdBeck` cobertura_baja (mismo ítem) · **subsumido en §1.1**

La flag `n=7` se explica por las 6 claves con prefijo `1619` + la clave `Rango` que es metadata, no baremo. Se resuelve junto con §1.1.

---

## 2. Otras pruebas con flag de auditoría

Las 22 pruebas restantes marcadas como prioritarias en F7.1 (Auditoría 18 PRUEBAS + extensiones) **no presentaron anomalías**:

| Test | Población | n_claves | Estado |
|---|---|---|---|
| `NiWiscDC`, `NiWiscSem`, `NiWiscVoc`, `NiWiscLN`, `NiWiscCl`, `NiWiscAri` | Infantil | 96-105 | OK |
| `NiWISCIndComVer`, `NiWISCIndRazPer`, `NiWISCIndMemTra`, `NiWISCIndVelPro`, `NiWISCTot` | Infantil (suma_a_indice) | 30-46 | OK |
| `AdWAISA`, `AdWAISC`, `AdWAISCC`, `AdWAISFI`, `AdWAISHI`, `AdWAISI`, `AdWAISL`, `AdWAISRO` | Adulto Joven | 192-216 | OK |
| `AdSemWais`, `AdSDWais`, `AdMatr`, `AdDDir` | Adulto Joven | 24-180 | OK |
| `AdWAISICV`, `AdWAISICP`, `AdWAISIMT`, `AdWAISIVP` | Adulto Joven (suma_a_indice) | 30-46 | OK |
| `ViTMTA`, `ViTMTB` | Adulto Mayor (Neuronorma) | 240-244 | OK |
| `ViRDD`, `ViRDInv` | Adulto Mayor | 100 | OK |
| `ViGroberRLT`, `ViGroberML_Tot`, `ViGroberMC_Tot` | Adulto Mayor | 30-50 | OK |
| `ViYesavage` (GDS-15) | Adulto Mayor (clasificacion_fija) | 16 | OK (eximir de cobertura) |

Total: 25 pruebas priorizadas auditadas · 22 OK · 1 crítica (AdBeck) · 1 falso positivo (EscLawton) · 1 derivada (AdBeck cobertura_baja).

---

## 3. Cronograma propuesto

| Fase | Actividad | Bloqueante | Estimación | Estado |
|---|---|---|---|---|
| **F7.2.1** | Afinar heurística del audit (lista blanca de tests cortos) | No | 1h | Pendiente |
| **F7.2.2** | Bloqueo defensivo de `AdBeck` en `loader.py` con flag `baremo_en_revision` | Sí (mientras esté roto) | 30min | Pendiente |
| **F7.2.3** | Smoke test del nuevo baremo BDI-II con caso clínico real anonimizado | No | 1h | Pendiente |
| **F7.2.4** | Aprobación del responsable del tratamiento | **Sí (definitivo)** | — | Pendiente |
| **F7.2.5** | Backup `data/BD_NEURO_MAESTRA.backup-pre-f7-2-adbeck.json` | Sí | 5min | Pendiente |
| **F7.2.6** | Aplicar cambio en `AdBeck` (baremos oficiales BDI-II) | Sí | 15min | Pendiente |
| **F7.2.7** | Correr 855+ tests del backend + 134 ground truth | Sí | 5min | Pendiente |
| **F7.2.8** | Commit + tag `f7-2-adbeck-fix` | No | 5min | Pendiente |
| **F7.2.9** | Documentar el cambio en `_meta.cambios[]` de la BD | No | 5min | Pendiente |
| **F7.2.10** | Notificar al usuario clínico con el cambio (release notes) | No | 10min | Pendiente |

**Tiempo total estimado:** 4-5 horas si F7.2.4 aprueba de inmediato. Si requiere consulta con literatura adicional (revisión de baremo colombiano del BDI-II si existe), 1-2 días adicionales.

---

## 4. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| El baremo BDI-II de Beck et al. (1996) no es el aplicado en Colombia | Media | Alto | Verificar si existe baremo colombiano (Bonnett, Valencia, Sánchez 2004 u otro). Si no, mantener baremo original con disclaimer. |
| El cambio rompe ground truths existentes | Baja | Alto | Los 134 escalares verificados no incluyen `AdBeck` (no estaba en los 15 casos clínicos). Validar manualmente los reportes históricos que lo usaron. |
| El motor tiene caché de baremos | Baja | Medio | Verificar `app/domain/clinical_engine/baremos_loader.py` y forzar recarga tras el cambio. |
| El usuario clínico ya emitió informes con el baremo corrupto | Alta (si se usó) | Medio | Si hay informes firmados, agregar una fe de erratas. Si no, el cambio es transparente. |

---

## 5. Validación post-migración

Una vez aplicado el cambio (F7.2.6):

1. `pytest tests/ -v --tb=short` → 855+ tests deben pasar.
2. `pytest tests/integration/test_casos_ground_truth.py -v` → 134 escalares verificados.
3. Smoke test manual: paciente ficticio 28a, BDI-II = 22, esperar clasificación "Moderado".
4. Smoke test manual: paciente ficticio 35a, BDI-II = 8, esperar "Mínimo".
5. Smoke test manual: paciente ficticio 60a, BDI-II = 35, esperar "Severo".
6. Verificar en la UI que el cambio se refleja sin necesidad de refresh manual.

---

## 6. Referencias

- **Beck, A. T., Steer, R. A., & Brown, G. K. (1996).** *Manual for the Beck Depression Inventory–II.* San Antonio, TX: Psychological Corporation.
- **Bonnett, C., Valencia, M., & Sánchez, R. (2004).** *Adaptación colombiana del BDI-II.* (Pendiente de verificación — buscar en Arango-Lasprilla & Rivera 2017).
- **Lawton, M. P., & Brody, E. M. (1969).** Assessment of older people: Self-maintaining and instrumental activities of daily living. *Gerontologist, 9*, 179-186.
- **Arango-Lasprilla, J. C. & Rivera, D. (Eds.). (2017).** *Neuropsicología en Colombia: Datos normativos, estado actual y retos a futuro.* Universidad de Manizales.
- `docs/AUDITORIA_BAREMOS_DETALLADA.md` — Reporte completo de F7.1.
- `scripts/audit_baremos_18.py` — Script de auditoría read-only.
- `tests/unit/test_audit_baremos.py` — Tests del script de auditoría.
- `tests/unit/test_principios_narrativa.py` — Tests del validador de principios narrativos (F6.2).

---

## 7. Estado actual

**F7.2.1 a F7.2.10 — TODOS PENDIENTES DE APROBACIÓN.**

Este plan NO debe ejecutarse sin:
1. Confirmación explícita del responsable del tratamiento.
2. Backup completo de `data/BD_NEURO_MAESTRA.json` (en disco separado).
3. Smoke test del nuevo baremo con al menos 3 puntuaciones de muestra.

Si el usuario aprueba, se procede F7.2.1 → F7.2.10 secuencialmente. Cualquier fallo en F7.2.7 (regresión de tests) detiene el proceso y se evalúa rollback desde F7.2.5.
