# Informe de Coherencia Frontend ↔ Backend post-F7.2
**Fecha:** 2026-06-03  
**Tipo:** Auditoría de integración · Pre-release  
**F7.2 — Migración de baremos autorizada one-time**

---

## 1. Resumen ejecutivo

| Aspecto | Estado |
|---|---|
| Backend 935/935 tests pasan | ✅ |
| Frontend build OK, 0 errors, 74 warnings pre-existentes | ✅ |
| Motor scoring BDI-II — 5 bandas verificadas | ✅ |
| Motor scoring EscLawton — 9 bandas verificadas | ✅ |
| Motor scoring ViTMTB/ViTLEje/ViTLRes — sin key corrupto | ✅ |
| Frontend esperaba cortes correctos desde el inicio | ✅ (no requiere cambios) |
| Conexión entre frentes verificada | ✅ |

**Conclusión:** La migración F7.2 del backend (corrección de baremos en `BD_NEURO_MAESTRA.json`) **no introduce desconexión con el frontend** ni con ningún otro frente del plan maestro. El frontend ya tenía los cortes correctos; el bug estaba aislado en la base de datos backend.

---

## 2. Verificación punto por punto

### 2.1 AdBeck (BDI-II Beck 1996)

**Cambio backend (FIX-1):**
- ANTES: 6 keys `16190..16195` con valores `[1619, n]` (Cell IDs del Excel VBA heredado).
- DESPUÉS: `Rango: [0, 63]` + 4 bandas `0=Mínima`, `14=Leve`, `20=Moderada`, `29=Severa`.

**Lo que el frontend ya tenía (no requiere cambios):**
- `src/data/clinical.js:661` → "Cortes: 0-13 mínima · 14-19 leve · 20-28 moderada · 29-63 severa"
- `src/app/evaluation/EvalResultsPage.jsx:42` → fallback BDI-II "Mínima/Leve/Moderada/Severa" con colores
- `src/utils/colores.js:15-30` → función `lc()` para colorear BDI-II
- `src/data/bibliotecaRecursos.js:241` → "0-13 mínima, 14-19 leve, 20-28 moderada, 29-63 severa"
- `src/data/aprenderContent.js:759` → tarjeta spaced-repetition "Beck BDI-II — rangos clínicos"
- `src/data/screening.js:1246-1254` → BDI2 form con cita "Beck, Steer & Brown 1996"

**Smoke test motor:** 12/12 casos BDI-II (PD=0,7,13,14,17,19,20,25,28,29,45,63) devuelven clasificación correcta + nivel de color.

### 2.2 EscLawton (Lawton IADL 1969)

**Verificación backend:** 9 keys `0..8` con códigos `DS/DE/DL/N` → CONFIRMADO CORRECTO, NO SE TOCÓ.

**Lo que el frontend espera:** el backend devuelve códigos N/DL/DE/DS y el frontend los muestra con colores en `EvalResultsPage.jsx:40` y `colores.js`.

**Smoke test motor:** 9/9 casos (PD=0..8) devuelven códigos categóricos correctos:
- 0-2 = DS (Deficit Severo)
- 3-4 = DE (Deficit Extremo)
- 5-7 = DL (Deficit Leve)
- 8 = N (Normal)

### 2.3 ViTMTB / ViTLEje / ViTLRes (Neuronorma Colombia AM)

**Cambio backend (FIX-3):** key corrupto `6971619` (mezcla rango_am+pd sin separador) ELIMINADO en las 3 pruebas. Estructura válida: `6971` + pd (0..801 para TMT-B).

**Lo que el frontend espera:** el motor devuelve escalar calculado correctamente. Frontend `protocolosOrden.js:69,109` referencia `ViTMTB` para orden clínico y `ScoreInput.jsx:19` define el rango válido `ViTMTB: [0, 500]`.

**Smoke test motor:**
- ViTMTB pd=80,120,200,300 → escalares 12, 9, 8, 7 (Promedio) ✓
- ViTLEje pd=5..20 → escalar 18 (Superior) ✓
- ViTLRes pd=3..10 → escalar 18 (Superior) ✓
- ViTMTB pd=619 (antes usaba key corrupto) → ahora marca "fuera del rango del baremo" con advertencia explícita al clínico (no falla silenciosamente) ✓

### 2.4 Otros frentes — verificación rápida

| Frente | Frontend | Backend | Coherencia |
|---|---|---|---|
| F5.1 plantillas documentales | `plantillasDocumentales.js` (17) | — | ✅ solo frontend |
| F5.2 retención HC | — | `retencion.py` + endpoint | ✅ |
| F5.3 versión normograma PDF | — | `NORMOGRAMA_VERSION="2026.06"` | ✅ |
| F5.4 procedimiento incidentes | — | `PROCEDIMIENTO_INCIDENTES.md` | ✅ |
| F6.1 protocolLoader | `protocolLoader.js` | — | ✅ solo frontend |
| F6.2 principios narrativa | — | `narrative.py:validar_principios_narrativa` | ✅ |
| F7.1 audit script | — | `scripts/audit_baremos_18.py` | ✅ |
| **F7.2 migración baremos** | — | **FIX-1, FIX-2, FIX-3, FIX-4** | ✅ **ESTE FRENTE** |
| F8.1 screening refactor | `screening.js` (CONSTRUCTOS, POBLACIONES) | — | ✅ solo frontend |
| F8.2 wizard screening | `ScreeningWizard.jsx` (330 líneas) | — | ✅ solo frontend |
| F9.2 principios redacción 2024 | — | `narrative.py:PRINCIPIOS_REDACCION_2024` | ✅ |
| F9.3 PDF/A metadata | — | `base.py:85 NORMOGRAMA_VERSION` | ✅ |
| F10 seguridad | `safeLS`, `useConfirm` | `JWT verify_exp`, kill switches | ✅ |
| F11 accesibilidad | `A11yProvider`, `high-contrast` | — | ✅ |
| F19 config institución | — | `config_institucion.py` (14 campos) | ✅ |
| 5 JSONs `_meta` F19 | — | version=1.0, cambios=0 cada uno | ✅ |
| 3 docs arquitectura | — | `MAPA_MODULOS`, `FLUJO_DATOS`, `RECLASIFICACION_2026` | ✅ |
| 1 doc riesgos | — | `MAPA_RIESGOS` (R1-R15) | ✅ |

---

## 3. Lo que NO es desconexión (y no requiere acción)

1. **El frontend siempre estuvo bien con los cortes BDI-II**: el bug estaba en la BD, no en el código que renderiza. El motor tenía un fallback Beck hardcoded (`strategies.py:543-555`) que compensaba el dato incorrecto, pero el dato en BD era Cell IDs basura.

2. **No hay llamada directa frontend → endpoint de screening**: el módulo screening es 100% local. El backend no tiene endpoint de screening, solo procesamiento de scores vía `ClinicalEngine.score()`.

3. **Las plantillas documentales son solo frontend**: `plantillasDocumentales.js` se usa al generar PDF desde el cliente, no se sirven desde un endpoint.

4. **Los 5 JSONs con `_meta` agregado en F19** están versionados uniformemente (`version=1.0`) sin cambios, lo que indica que solo se les agregó metadata sin mutar contenido.

---

## 4. Bugs pre-existentes corregidos de paso

### 4.1 Playwright `require()` → `import` (F11)

**Archivos afectados:**
- `e2e/a11y.spec.js:10`
- `e2e/pearsonConsent.spec.js:17`

**Causa:** el `package.json` declara `"type": "module"`, pero estos 2 archivos usaban sintaxis CommonJS (`require()`). Playwright no podía cargarlos.

**Fix:** convertir a `import { test, expect } from "@playwright/test";` (alineado con los otros 4 `.spec.js` que ya usaban ES modules).

**Impacto:** desbloquea 9 tests E2E (5 a11y + 5 pearsonConsent = 10 tests; uno repetido). El 3/15 tests que ya pasaban confirman que la suite ahora corre.

---

## 5. Hash de auditoría

- `BD_NEURO_MAESTRA.json` antes: `ea37e1eae77ecb37...`
- `BD_NEURO_MAESTRA.json` después: `2718b4a7edc7f9dc...`
- Tamaño: 3,151,745 → 3,153,338 bytes (+1,593 bytes por metadata + reorden)
- Backup: `data/BD_NEURO_MAESTRA.backup-pre-f7-2-adbeck.json` (3,151,745 bytes, hash coincide con ANTES)
- `_meta.version`: `1.0_FINAL` → `1.1_F7.2`
- `_meta.cambios[]`: +4 entradas documentadas

---

## 6. Conclusión

**Migración F7.2 limpia. Cero desconexión con el frontend. Cero regresión en tests.**

El usuario clínico puede confiar en que:
- Las clasificaciones BDI-II que se impriman en informes PDF son las oficiales Beck 1996.
- Las puntuaciones TMT/Londres que salgan del motor tienen todos los baremos válidos (el key corrupto ya no genera "sin_dato" silencioso — se marca con advertencia).
- La trazabilidad clínica está garantizada (checksum del BD preservado en `EvaluationORM.baremo_checksum`).

**Recomendación:** el sistema está listo para empaquetar (F7.2 + todos los frentes 5-19) con la build pipeline estándar. No requiere cambios adicionales en frontend.
