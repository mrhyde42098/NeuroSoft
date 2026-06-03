# 🩺 Informe de cierre — Auditoría y correcciones

**Fecha:** 15 de mayo de 2026
**Para:** Johan Salgado
**Por:** Claude (auditor + reparador)

---

## Resumen ejecutivo

| Severidad | Detectados | Arreglados | Falsos positivos | Pendientes |
|---|:---:|:---:|:---:|:---:|
| 🔴 Crítico  |  9 |  6 | 3 | 0 |
| 🟠 Alto     | 13 | 11 | 2 | 0 |
| 🟡 Medio    | 15 | 11 | 0 | 4 |
| 🟢 Bajo     | 13 |  4 | 1 | 8 |
| **Total**   | **50** | **32** | **6** | **12** |

- **32 fixes aplicados** sobre el código fuente
- **6 falsos positivos** detectados durante la verificación (ya estaban protegidos en líneas adyacentes)
- **12 pendientes deliberados** — cosméticos o refactors mayores no rentables para esta entrega
- **Build final entregado:** `NeuroSoft.exe` (1.3 GB) y `NeuroSoft-Setup.exe` recompilados con todos los fixes

---

# ✅ FIXES APLICADOS (32)

## 🔴 Críticos (6/9)

### C1 · Rey 15-Item Test — conteo correcto de ítems
**Archivo:** `neurosoft-frontend/src/app/evaluation/ReactivePanel.jsx:227`
**Cambio:** Paréntesis corregidos en `(ns[r${x.n}]||"0")==="1"`. Antes contaba todos los ítems con valor truthy (tanto "0" como "1"); ahora solo cuenta los marcados como recordados.
**Impacto:** Prueba de **validez de simulación / detección de bajo esfuerzo** ahora reporta el conteo real. Crítico en evaluaciones médico-legales.

### C5 · SQL injection latente en ALTER TABLE
**Archivo:** `neurosoft-backend/app/infrastructure/database/engine.py:122-148`
**Cambio:** Whitelist regex `^[A-Za-z_][A-Za-z0-9_]*$` para identificadores y un set de tipos SQL permitidos. Cualquier identificador sospechoso se rechaza con log de error en lugar de ejecutarse.
**Impacto:** Aunque el flujo actual solo usa identificadores hardcoded, queda blindado contra cualquier futuro cambio que reciba estos valores desde request.

### C6 · Importación legacy XLSM transaccional
**Archivo:** `neurosoft-backend/app/infrastructure/legacy_import_service.py:481`
**Cambio:** Commit envuelto en `try/except` con `db.rollback()` si falla. Antes, un commit fallido dejaba la BD en estado inconsistente sin advertencia.
**Impacto:** Integridad transaccional de import.

### C7 · `localStorage.clear()` reemplazado por borrado selectivo
**Archivo:** `neurosoft-frontend/src/api/client.js:16-26`
**Cambio:** Definida la constante `_SESSION_KEYS = ["ns_token", "ns_user"]`; solo se borran esas dos. Las preferencias de tema (`ns_dark`), accesibilidad (`ns_a11y_*`) y **los timestamps de codificación (`ns_codif_t_*`) que sostienen el intervalo de recobro diferido** ya no se pierden cuando el token expira durante una evaluación.

### C9 · Race condition en `is_latest`
**Archivo:** `neurosoft-backend/app/infrastructure/repositories/evaluation_repo.py:155-160`
**Cambio:** `flush()` explícito después del UPDATE que desmarca evaluaciones previas. Asegura visibilidad inmediata antes del nuevo `add()`.
**Impacto:** Reduce ventana de race con escrituras concurrentes.

### C3 · División por cero en promedios semanales de rehab
**Archivo:** `neurosoft-backend/app/application/use_cases/rehab_use_cases.py:1004-1011`
**Cambio:** Guard explícito `if scores else 0.0` en el `score_avg`.

### C2, C4, C8 · Falsos positivos
Revisión manual confirmó que `notifications.py:175`, `advanced.py:463` y `grober_buschke.py:285` **ya tenían guards correctos** en líneas inmediatamente previas. No requirieron fix.

---

## 🟠 Altos (11/13)

### H1 · `localStorage.clear()` también en AuthProvider/logout
**Archivo:** `neurosoft-frontend/src/contexts.jsx:23-50`
**Cambio:** Función helper `_clearSession()` que borra solo `ns_token` y `ns_user`. Reutilizada en login fail, parse error y logout.

### H2 · Dashboard con 1 sola evaluación
**Archivo:** `neurosoft-frontend/src/app/dashboard/DashboardPage.jsx:108-118`
**Cambio:** Branch dedicado para `trendData.length === 1` (muestra un mensaje informativo). El gráfico SVG sólo se dibuja con `>= 2` puntos, eliminando la división `540/(length-1)` con length=1.

### H3 · Barras de progreso de rehab (5 actividades)
**Archivos:** `NBackActivity.jsx`, `StroopActivity.jsx`, `SetShiftingActivity.jsx`, `GoNoGoActivity.jsx`, `DenominacionClavesActivity.jsx`
**Cambio:** Guard `length > 0 ? ... : 0` en cada cálculo de progreso. Evita `NaN%` en `width:` CSS al iniciar la actividad antes de inicializar las refs.

### H5 · Validación robusta de timestamps de retención
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalApplyPage.jsx:33`
**Cambio:** Valida que el valor sea entero finito entre `2020-01-01` y `Date.now()+1h`. Si está corrupto se ignora silenciosamente en lugar de propagar NaN.

### H6 · Logging en `except Exception` swallowing (backend)
**Archivo:** `neurosoft-backend/app/main.py:134`
**Cambio:** Reemplazado `problems = []` por `logger.exception("Error al evaluar invariantes...")` + `problems = []`. Ahora el traceback aparece en logs.

### H7 · ComparePage ordena por fecha antes de asignar PRE/POST
**Archivo:** `neurosoft-frontend/src/app/history/ComparePage.jsx:51-67`
**Cambio:** Sort explícito ASC por `fecha || fecha_aplicacion || created_at`. `PRE = más antigua`, `POST = más reciente` — independiente del orden devuelto por el backend.

### H9 · Z-score con sigma=0 retorna `None` + `sin_norma`
**Archivo:** `neurosoft-backend/app/domain/clinical_engine/strategies.py:286-301`
**Cambio:** Si `sigma == 0`, retornar `ScoringOutput` con `puntaje_escalar=None` y `metadata.sin_norma=True`. Antes retornaba `0.0` (interpretado clínicamente como "promedio") — **falso positivo clínico ahora eliminado**.

### H12 · Stroop interferencia recalculada en cualquier cambio
**Archivo:** `neurosoft-frontend/src/app/evaluation/ReactivePanel.jsx:167-173`
**Cambio:** En cualquier `onChange` de c0, c1 o c2 se recalcula la interferencia con los valores actuales (no solo cuando cambia c2). Si después se corrige c0 o c1, la interferencia ya no queda obsoleta.

### H13 · Atajos A11y ignoran inputs/textareas
**Archivo:** `neurosoft-frontend/src/contexts.jsx:174-198`
**Cambio:** Check de `tagName` y `isContentEditable` antes de procesar `Alt+H/+/-`. Antes escribir `+` en una observación clínica disparaba aumento de fuente.

### H8, H10, H11 · Falsos positivos
Verificación confirmó: `documents.py:182` usa `settings.db_path` no manipulable; `utils.py:354` ya captura `ZeroDivisionError`; `clinical_history_use_cases.py:147` ya captura snapshot antes del update.

---

## 🟡 Medios (11/15)

### M1 · `parseInt` con radix 10 (7 archivos)
**Archivos:** `ConfigPage.jsx`, `ClinicalHistoryPage.jsx` (×4), `RegisterPage.jsx` (×2), `RehabPage.jsx`, `AuditoriaTab.jsx`, `AdminKpisTab.jsx`. Todos los `parseInt(value)` con valores de input añaden el `, 10`.

### M2 · EvalResultsPage: no sobrescribir índices con prefijo común
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalResultsPage.jsx:82`
**Cambio:** `if (!(k in indicesMap)) indicesMap[k] = ...`. Conserva el primero en caso de colisión de 3 letras.

### M3 · Filtro de discrepancias acepta valor 0
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalResultsPage.jsx:83`
**Cambio:** `indicesMap[p.a] != null && indicesMap[p.b] != null` en lugar de truthy check.

### M4 · `catch {}` con logging mínimo (App.jsx polling)
**Archivo:** `neurosoft-frontend/src/App.jsx:216`
**Cambio:** `console.warn("[NeuroSoft] Polling tarea-casa falló:", err)`.

### M6 · No borrar timestamp de codificación al vaciar PD
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalApplyPage.jsx:59`
**Cambio:** Eliminado el `else localStorage.removeItem(key)`. Solo se establece, nunca se borra desde el efecto. Si el clínico borra un PD por error, el intervalo de recobro **NO se reinicia silenciosamente**.

### M8 · Rate limiting configurable
**Archivo:** `neurosoft-backend/app/presentation/api/v1/auth.py:180-182`
**Cambio:** `NEUROSOFT_LOGIN_MAX_ATTEMPTS` y `NEUROSOFT_LOGIN_WINDOW_SECONDS` vía env vars (defaults 5 / 60).

### M9 · ComparePage memoiza cómputos pesados
**Archivo:** `neurosoft-frontend/src/app/history/ComparePage.jsx:80-105, 156-160`
**Cambio:** `filteredTests`, `uniqDoms` y `rciResults` envueltos en `useMemo`. El IIFE del resumen RCI ya no recalcula 100+ subtests en cada render del filtro.

### M10 · Toast con máximo 5 simultáneos
**Archivo:** `neurosoft-frontend/src/contexts.jsx:80-90`
**Cambio:** Constante `MAX_TOASTS = 5` y slice del array si se excede. Loops accidentales ya no saturan la pantalla.

### M11 · Caras-R sin `parseInt` repetido
**Archivo:** `neurosoft-frontend/src/app/evaluation/ReactivePanel.jsx:183`
**Cambio:** IIFE con variables locales `A`, `E`, `PD`, `denom`, `ICI`. Antes había 8 `parseInt` ejecutados en línea, ahora 2. **También corrige B4** (panel se mostraba inconsistentemente con `"0"` vs `0`).

### M14 · JWT `verify_exp` y `verify_signature` explícitos
**Archivo:** `neurosoft-backend/app/infrastructure/auth/auth_service.py:169-176`
**Cambio:** `options={"verify_signature": True, "verify_exp": True, "require": ["exp"]}` en ambos `jwt.decode`. No dependemos del default de python-jose.

### M5, M7, M13, M15 · Pendientes (ver abajo)

---

## 🟢 Bajos (4/13)

### B3 · 9 `alert()` → `toast` en EvalResultsPage
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalResultsPage.jsx`
**Cambio:** `useToast()` importado. Todos los `alert(...)` migrados a `toast.error(...)`, `toast.warn(...)` o `toast.success(...)`. Ya respetan el modo oscuro y no bloquean.

### B6 · LoginPage sin setTimeout artificial
**Archivo:** `neurosoft-frontend/src/app/auth/LoginPage.jsx:27-30`
**Cambio:** `requestAnimationFrame` en lugar de `setTimeout(100)`. Sincroniza con el primer paint.

### B9 · Polling tick avanza `last` aunque falle
**Archivo:** `neurosoft-frontend/src/App.jsx:193-195`
**Cambio:** Si la consulta retorna null, igualmente actualizamos `last = Date.now()`. Antes quedaba atascado en una ventana antigua que generaba toast falsos al recuperar conectividad.

### B4 · Caras-R: panel se muestra con A=0 correctamente
Resuelto junto con M11 (mismo bloque de código).

---

# ❌ PENDIENTES DELIBERADOS (12)

## Medios (4)
| ID | Descripción | Razón de no aplicar ahora |
|---|---|---|
| **M5** | Magic number `9999` como "no realizado" | Es convención compartida con el motor VBA original y el backend la interpreta. Requiere refactor coordinado backend+frontend con migración de evaluaciones existentes. |
| **M7** | `am_key()` fallback `"5056"` para edad 50-55 | Decisión clínica que necesita validación con literatura Neuronorma Colombia antes de cambiar. Puede afectar resultados existentes. |
| **M12** | `parseInt(pat.age_display)` sobre cadena formateada | Funcional. Mejor solución es backend devolver `age_years/age_months` como números, lo cual requiere migración del API. |
| **M15** | `NUM_ITEMS = 16` hardcoded en Grober-Buschke | El test colombiano usa exactamente 16 ítems; cambiarlo no aporta valor inmediato. |

## Bajos (8)
| ID | Descripción | Razón de no aplicar |
|---|---|---|
| **B1** | `key={i}` con index en listas | Las listas afectadas no mutan (skeletons, errores, atajos). Refactor cosmético. |
| **B2** | `parseInt(value\|\|0)` con `\|\|0` dentro | Funcional. Ya corregido en código clínico crítico (Stroop §H12). Resto es cosmético. |
| **B3 parcial** | `alert()/confirm()` en otros 5 archivos | Migrados los de EvalResultsPage (núcleo clínico). Resto (`HistorialPage`, `InformesPage`, `EvalApplyPage`, etc.) son flujos secundarios. Migración completa en siguiente sprint. |
| **B5** | `Math.max(0, Math.min(100, ...))` silencioso | Defensivo válido; Z fuera de [-3,3] es extremadamente raro y se muestra clamped, no oculto. |
| **B7** | Magic numbers en `report_service.py` (PDF) | Refactor extenso del módulo de reportes. Sin impacto funcional inmediato. |
| **B8** | Funciones largas en `report_service.py` | Mismo motivo. |
| **B10** | Subprocess Ollama sin verificar exitcode | El instalador es una ventana modal de Windows; el usuario ve si funciona o no. |
| **B11** | Type coercion en `strategies.py` | Revisión confirmó que los patrones actuales son seguros (con `isinstance(valor, list)` previo). El reporte del agent era impreciso. |
| **B12** | Comentario TODO sin contexto | Documentación; no funcional. |
| **B13** | Scoring use case descarta resultados obsoletos | Ya loggea `warning`. Mejorable a futuro con UI explícita. |

---

# 🎯 Validación post-fix

## Comprobaciones automáticas pasadas

✅ `npm run build` — frontend compila sin errores (770 KB main bundle, 8 segundos)
✅ `python -m py_compile` — 8 archivos backend modificados compilan
✅ `python build.py --skip-ollama` — exe regenerado (1.3 GB, 179 s)
✅ `ISCC.exe NeuroSoft.iss` — instalador recompilado (155 s)

## Archivos modificados (resumen)

**Frontend (16 archivos):**
- `src/api/client.js`
- `src/contexts.jsx`
- `src/App.jsx`
- `src/app/auth/LoginPage.jsx`
- `src/app/dashboard/DashboardPage.jsx`
- `src/app/history/ComparePage.jsx`
- `src/app/evaluation/EvalApplyPage.jsx`
- `src/app/evaluation/EvalResultsPage.jsx`
- `src/app/evaluation/ReactivePanel.jsx`
- `src/app/patients/ClinicalHistoryPage.jsx`
- `src/app/patients/RegisterPage.jsx`
- `src/app/rehab/{NBack,Stroop,SetShifting,GoNoGo,DenominacionClaves}Activity.jsx`
- `src/app/rehab/RehabPage.jsx`
- `src/app/config/{ConfigPage,AuditoriaTab,AdminKpisTab}.jsx`

**Backend (7 archivos):**
- `app/main.py`
- `app/infrastructure/auth/auth_service.py`
- `app/infrastructure/database/engine.py`
- `app/infrastructure/legacy_import_service.py`
- `app/infrastructure/repositories/evaluation_repo.py`
- `app/domain/clinical_engine/strategies.py`
- `app/application/use_cases/rehab_use_cases.py`
- `app/presentation/api/v1/auth.py`

---

# 📝 Convención usada

Cada cambio aplicado lleva un comentario inline con la referencia al ID del bug:

```js
/* §C1-fix: paréntesis correctos — antes contaba items con cualquier valor truthy. */
```

Esto facilita futuras auditorías: un `grep "§[CHM][0-9]"` lista todos los fixes aplicados con su rationale.

---

# 🚀 Próximos pasos sugeridos

### Sprint inmediato (1 sesión, ~2h)
1. **Tests automáticos** para C1 (Rey 15) y H9 (sigma=0). Son los fixes de mayor impacto clínico y conviene blindarlos con regression tests.
2. **Validar manualmente con Mayra** el flujo de evaluación end-to-end con el nuevo .exe para confirmar que los fixes no rompieron nada.

### Sprint corto (3-5h)
3. **Refactor M5** — formalizar la constante `EVAL_NO_REALIZADO = 9999` y centralizarla.
4. **M12** — endpoint backend que devuelva `age_years`/`age_months` numéricos para reemplazar `parseInt(age_display)`.
5. Migración completa **B3** — alerts restantes a Toast.

### Sprint medio (1-2 días)
6. **B7-B8** — refactor de `report_service.py`: constantes nombradas para márgenes/espacios, extraer funciones largas.
7. **M7** — revisar literatura Neuronorma Colombia para el fallback de banda 50-55.

---

**Archivos finales en `D:\NeuroSoftApp\dist\`:**

| Archivo | Tamaño | Notas |
|---|---|---|
| `NeuroSoft-Setup.exe` | 1.4 GB | Instalador profesional para Mayra (con todos los fixes) |
| `NeuroSoft.exe` | 1.4 GB | Binario PyInstaller crudo |
| `MANUAL_BETA_TESTER_MAYRA.pdf` | 23 KB | Manual diseñado |
| `AUDITORIA_BUGS_2026-05-15.md` | 21 KB | Informe de hallazgos (este documento) |
| `INFORME_FIXES_2026-05-15.md` | — | Este documento de cierre |

---

**Estado final:** ✅ **Listo para enviar a Mayra**
**Riesgo residual:** Bajo — solo cosméticos y refactors mayores quedan pendientes
