# Plan sprint REACTIVOS — WISC-IV y WAIS-III

**Fecha:** 5 jun 2026 
**Prioridad:** P0 — error clínico crítico 
**Fuente clínica autoritativa:** `Capacitaciones Clínicas/protocolos/wisc_iv_protocolo.json` y `wais_iii_protocolo.json` 
**Verificación PDF de protocolo:** `docs/VERIFICACION_PROTOCOLO_PDF_2026-06-05.md` (WISC/WAIS drive-download confirmados ✅) 
**Destino UI:** `neurosoft-frontend/src/data/clinical.js` → `export const REACTIVOS` 
**Protección copyright:** `pearsonProtected.js` (consentimiento + audit log)

---

## Resumen ejecutivo

| Métrica | Valor |
|---|---|
| Tests con `requires_protocol_text:true` (placeholder) | **16** |
| Tests WISC/WAIS con texto real parcial | **~12** |
| Tests con **discrepancia** texto actual vs protocolo fuente | **≥4** (Semejanzas WISC/WAIS, Vocabulario WISC, LN WISC) |
| Ítems listos en JSON Capacitaciones (verbales) | **~200+** |
| Ítems solo visuales (Matrices, Conceptos) | **63** — requieren cuadernillo, no texto inline |

**Veredicto:** El clínico ve "Reactivo N — ver protocolo" en la mitad de subpruebas Pearson. Además, varios subtests que *sí* tienen texto están **desalineados** con el protocolo fuente.

---

## Mapa de archivos

```
Capacitaciones Clínicas/protocolos/ ← FUENTE (editar aquí primero)
 wisc_iv_protocolo.json
 wais_iii_protocolo.json
 ↓ sync (script a crear)
neurosoft-frontend/src/data/
 clinical.js ← REACTIVOS (UI evaluación)
 protocols/wisc_iv_protocolo.json ← espejo parcial (routing)
 pearsonProtected.js ← TESTS_VERBATIM + metadatos ISBN
```

Script de auditoría: `docs/scripts/audit_reactivos_gap.py`

---

## Inventario por subtest — WISC-IV

| test_id | Nombre | Estado en `clinical.js` | Ítems protocolo | Acción |
|---|---|---|---|---|
| `NiWiscDC` | Diseño con Cubos | ✅ Estructura (desc genérica, no verbatim) | 14 | Mantener; estímulos visuales en cuadernillo |
| `NiWiscSem` | Semejanzas | ⚠️ **Pares incorrectos** vs fuente | 24 (M+1-23) | **Reemplazar** desde protocolo |
| `NiWiscVoc` | Vocabulario | ⚠️ 32 palabras, orden distinto; faltan 4 | 36 | **Reemplazar** lista completa |
| `NiWiscCom` | Comprensión | ⚠️ 18 preguntas; protocolo tiene 21 | 21 | Verificar manual §18 oficiales; alinear |
| `NiWiscRDD` | Retención Dígitos | ✅ Secuencias OK | OD 8 + OI 8 | Revisar OI ítem 1 (protocolo: 2-1/1-3) |
| `NiWiscLN` | Letras y Números | ⚠️ Secuencias placeholder | 10 niveles × 3 trials | **Reemplazar** desde `ensayos_secuencias` |
| `NiWiscMat` | Matrices | ❌ Placeholder ×35 | 35 (solo claves respuesta) | UI: lámina + opciones; importar `respuestas_correctas` |
| `NiWiscConD` | Conceptos con Dibujos | ❌ Placeholder ×28 | 0 texto (visual) | UI: referencia cuadernillo + captura 0/1 |
| `NiWiscCl` | Claves | ✅ timed_count | — | OK |
| `NiWiscBusSim` | Búsqueda Símbolos | ✅ timed_count | — | OK |
| `NiWiscAri` | Aritmética | ❌ Placeholder ×34 | **34 preguntas completas** | **Importar** texto + tiempo |
| `NiWisFigInc` | Figuras Incompletas | ❌ Placeholder ×38 | **38 ítems** (imagen+resp) | Importar pregunta/respuesta guía |
| `NiWisInf` | Información | ❌ Placeholder ×33 | **33 preguntas** | **Importar** |
| `NiWisPalCon` | Palabras en Contexto | ❌ Placeholder ×24 | **24 ítems con pistas** | **Importar** |
| `NiWisReg` | Registro | ✅ 5 series | — | OK estructura |

### Discrepancias críticas detectadas

**NiWiscSem** — `clinical.js` empieza con `Rueda — Pelota`; protocolo fuente:

- M (muestra): `Rojo — Azul`
- 1: `Leche — Agua`
- 2: `Esfero — Lápiz`
- … hasta 23: `Espacio — Tiempo`

**NiWiscVoc** — protocolo tiene 36 palabras (ej. ítem 6 `Sombrilla`, 11 `Obedecer`); `clinical.js` usa lista distinta (ej. `Vaca` en n:6, `Alfabeto` en n:11).

**NiWiscLN** — protocolo define secuencias reales por nivel; `clinical.js` repite `L-N-3` en niveles 7-8.

---

## Inventario por subtest — WAIS-III

| test_id | Nombre | Estado en `clinical.js` | Ítems protocolo | Acción |
|---|---|---|---|---|
| `AdWAISCC` | Cubos | ✅ Estructura | 14 | OK (visual) |
| `AdSemWais` | Semejanzas | ⚠️ 19 pares **inventados/incorrectos** | 19 oficiales | **Reemplazar** (ej. n:1 debe ser `Naranja — Pera`) |
| `AdWAISV` | Vocabulario | ❌ Placeholder ×33 | **33 palabras + criterios 0/1/2** | **Importar** |
| `AdWAISI` | Información | ❌ Placeholder ×28 | **28 preguntas** | **Importar** |
| `AdWAISC` | Comprensión | ❌ Placeholder ×18 | **18 situaciones** | **Importar** |
| `AdWAISA` | Aritmética | ❌ Placeholder ×20 | **20 problemas** | **Importar** |
| `AdMatr` | Matrices | ❌ Placeholder ×26 | 26 (clave A-Z + 1-26) | UI visual + `respuestas_correctas` |
| `AdWAISFI` | Figuras Incompletas | ❌ Placeholder ×25 | **25 láminas** | **Importar** imagen+respuesta |
| `AdDDir` | Dígitos | ✅ Secuencias | OD 8 + OI 7 | OK |
| `AdWAISL` | Letras y Números | ❌ Placeholder ×21 | **7 niveles × 3 intentos** | **Importar** estructura `ensayos_secuencias` |
| `AdSDWais` | Clave de Números | ✅ timed_count | — | OK |
| `AdBusSim` | Búsqueda Símbolos | ✅ timed_count | — | OK |

---

## Encoding y calidad del JSON fuente

Los archivos en `Capacitaciones Clínicas/protocolos/` tienen **mojibake** (`Ã±`, `â€"`, etc.) por encoding UTF-8 mal interpretado. **Paso 0 del sprint:**

1. Re-guardar como UTF-8 sin BOM.
2. Sincronizar copia a `neurosoft-frontend/src/data/protocols/`.
3. Validar con `json.loads(..., encoding='utf-8-sig')`.

---

## Estrategia de implementación (4 fases)

### Fase 0 — Preparación (esta sesión) ✅

- [x] Inventario gap (`audit_reactivos_gap.py`)
- [x] Este documento de plan
- [x] Verificación PDF de protocolo vs JSON (`VERIFICACION_PROTOCOLO_PDF_2026-06-05.md`)
- [ ] Johan valida que protocolos JSON reflejan su manual físico

### Fase 1 — Verbales con texto completo en JSON ✅ (6 jun 2026)

Generador: `docs/scripts/sync_reactivos_from_protocol.py` → `reactivosPearson.generated.js`

| Prioridad | test_ids |
|---|---|
| P0 | `NiWiscSem`, `NiWiscVoc`, `AdSemWais`, `NiWisInf`, `NiWiscAri`, `AdWAISV`, `AdWAISI`, `AdWAISC`, `AdWAISA` |
| P1 | `NiWisFigInc`, `AdWAISFI`, `NiWisPalCon`, `NiWiscLN`, `AdWAISL` |

Mapeo tipo protocolo → `clinical.js`:

| `tipo` en JSON | `type` en REACTIVOS |
|---|---|
| `verbal_con_respuestas` + `par` | `scored_items` + `pair` |
| `verbal_con_respuestas` + `palabra` | `scored_items` + `word` |
| `verbal_con_respuestas` + `pregunta` | `scored_items` + `q` |
| `verbal_con_tiempo` | `scored_items` + `q` + `tiempo_seg` |
| `visual_con_tiempo` | `scored_items` + `imagen` + `respuesta` |
| `ensayos_secuencias` | `items` con `secuencia`/`trials` |
| `ensayos_digitos` | ya existe `type:"digits"` |
| `seleccion_multiple` | nuevo tipo o scored_items con `opciones:5` |

Incluir `resp_2pt`/`resp_1pt`/`resp_0pt` en campo `guia` (solo visible con licencia Pearson aceptada).

### Fase 2 — Visuales (Matrices, Conceptos) ✅ parcial (6 jun 2026)

- No poner texto verbatim de estímulos gráficos en bundle público.
- UI: `visual_cuadernillo` en `ReactivePanel.jsx` → banner cuadernillo licenciado + captura 0/1.
- Claves `respuestas_correctas` visibles solo con consentimiento Pearson (`pearsonProtected.js`).
- **Pendiente:** subir láminas escaneadas (propias) vía Config → Estímulos con `item_id` por número de ítem.

### Fase 3 — Tests y regresión ✅ (6 jun 2026)

- `neurosoft-backend/tests/unit/test_reactivos_sync.py` (4 tests).
- NiWiscSem par[1] == `Leche — Agua` verificado.
- E2E Playwright: abrir evaluación WISC → Semejanzas muestra par real.
- **No tocar** `BD_NEURO_MAESTRA.json`.

### Fase 4 — Documentación

- `/actualizar-estado-vivo` → marcar placeholders como ✅
- Actualizar `docs/AUDITORIA_PDFs.md` §reactivos
- `/actualizar-contexto-ia` si Johan retoma en otro chat

---

## Componentes UI a revisar

| Archivo | Rol |
|---|---|
| `ReactivePanel.jsx` | Render por `cfg.type` y `cfg.scoring` |
| `pearsonProtected.js` | Gate verbatim + metadatos manual |
| `ApoyoClinicoPanel.jsx` | Instrucciones resumidas (pueden desactualizarse) |

Verificar que `requires_protocol_text` muestre banner "consulte manual" **hasta** Fase 1 complete el test.

---

## Riesgos legales

- Ítems WISC/WAIS son **copyright Pearson / Manual Moderno**.
- Flujo actual: consentimiento único + audit log + no redistribución.
- **No** exportar reactivos a PDF público ni repo externo.
- Matrices/Conceptos: mostrar referencia al cuadernillo físico del clínico licenciado.

---

## Comando para retomar

```
Lee docs/REACTIVOS_WISC_WAIS_PLAN.md
Lee Capacitaciones Clínicas/protocolos/wisc_iv_protocolo.json
Implementa Fase 1 empezando por NiWiscSem y NiWiscVoc
Usa /actualizar-estado-vivo al cerrar cada subtest
```

---

*Preparado para sprint REACTIVOS · NeuroSoft App*
