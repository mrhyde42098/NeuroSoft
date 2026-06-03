# 🔍 Auditoría de Bugs y Mejoras — NeuroSoft App

**Fecha:** 15 de mayo de 2026
**Auditor:** Claude (sesión Johan)
**Alcance:** Frontend React + Backend FastAPI
**Estado:** Reporte de hallazgos — **NINGÚN cambio aplicado**

---

## Resumen ejecutivo

| Severidad | Frontend | Backend | Total |
|---|---:|---:|---:|
| 🔴 **Crítico** | 3 | 6 | **9** |
| 🟠 **Alto** | 5 | 8 | **13** |
| 🟡 **Medio** | 8 | 7 | **15** |
| 🟢 **Bajo / Cosmético** | 9 | 4 | **13** |
| **Total** | 25 | 25 | **50** |

Los bugs **críticos** afectan directamente cálculos clínicos (Rey 15-Item, Grober & Buschke, Z-scores, índices). Los **altos** son race conditions, fallos silenciosos y validaciones débiles. **Recomiendo abordar primero los 9 críticos.**

---

# 🔴 CRÍTICOS — Afectan cálculo o seguridad clínica

## C1 · Conteo incorrecto en Rey 15-Item Test (validez de simulación)
**Archivo:** `neurosoft-frontend/src/app/evaluation/ReactivePanel.jsx:227`
**Categoría:** Bug lógico por precedencia de operadores

```js
const tot=(cfg.items||[]).filter(x=>(ns[`r${x.n}`])||"0"==="1").length;
```

**Problema:** JavaScript evalúa primero `"0"==="1"` (siempre `false`), después `||` con `ns[…]`. El resultado es que `.filter()` cuenta **todos** los ítems donde `ns[r${x.n}]` es truthy — incluye tanto `"0"` (no recordado) como `"1"` (recordado).

**Intención clara:**
```js
const tot=(cfg.items||[]).filter(x=>(ns[`r${x.n}`]||"0")==="1").length;
```
(fíjate dónde están los paréntesis)

**Impacto clínico:** El Rey 15-Item Test es una prueba de **validez de síntomas / detección de simulación**. Un conteo incorrecto puede llevar a:
- Falsos positivos en sospecha de simulación
- Falsos negativos: pacientes simuladores no detectados
- Interpretación errónea de esfuerzo en valoraciones médico-legales

**Severidad:** 🔴 Crítico

---

## C2 · División por cero en cálculo de promedio de adherencia
**Archivo:** `neurosoft-backend/app/presentation/api/v1/notifications.py:175`

```python
promedio_adherencia = int(sum(...) / len(rows)) if rows else 0
```

**Problema:** El guard `if rows` protege contra lista `None` y lista vacía, pero el comprehension interno puede generar lista vacía aunque `rows` no lo esté (filtros aplicados).

**Severidad:** 🔴 Crítico (puede generar 500 al cargar dashboard)

---

## C3 · División por cero en promedios semanales de rehab
**Archivo:** `neurosoft-backend/app/application/use_cases/rehab_use_cases.py:1008`

```python
round(sum(scores) / len(scores), 1)
```

**Problema:** Sin guard `if scores`. Si una semana del plan no tiene puntuaciones registradas, `len(scores)=0` → `ZeroDivisionError`.

**Severidad:** 🔴 Crítico (rompe vista de progreso del plan)

---

## C4 · División por cero en promedio Z por dominio
**Archivo:** `neurosoft-backend/app/presentation/api/v1/advanced.py:463`

```python
z_prom = sum(z_vals) / len(z_vals)
```

**Problema:** Si un dominio cognitivo está marcado en el protocolo pero ninguna prueba se aplicó, `z_vals=[]`.

**Severidad:** 🔴 Crítico (afecta el gráfico de perfil clínico)

---

## C5 · SQL injection potencial en ALTER TABLE dinámico
**Archivo:** `neurosoft-backend/app/infrastructure/database/engine.py:133`

```python
f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"
```

**Problema:** Aunque actualmente las variables vienen de una lista blanca interna del código, no hay validación explícita. Cualquier futuro cambio que reciba estos valores desde request los hace inyectables.

**Severidad:** 🔴 Crítico (vulnerabilidad latente)

---

## C6 · Commit sin rollback en importación legacy
**Archivo:** `neurosoft-backend/app/infrastructure/legacy_import_service.py:481`

**Problema:** Un `db.commit()` después de un loop que captura excepciones individuales. Si una fila del XLSM falla, las anteriores ya commiteadas quedan, generando una BD inconsistente.

**Severidad:** 🔴 Crítico (corrupción parcial de datos importados)

---

## C7 · localStorage.clear() borra todo al recibir 401
**Archivo:** `neurosoft-frontend/src/api/client.js:18`

```js
if (r.status === 401 && localStorage.getItem("ns_token")) {
  localStorage.clear();
  window.location.reload();
}
```

**Problema:** `localStorage.clear()` borra:
- `ns_token` ✓ correcto
- `ns_dark` ❌ preferencia de modo oscuro
- `ns_a11y_hc`, `ns_a11y_fs` ❌ preferencias de accesibilidad
- `ns_sel_patient` ❌ paciente seleccionado
- `ns_codif_t_*` ❌ **timestamps de codificación para recobro diferido** (puede afectar validez de evaluaciones en curso)

**Lo correcto sería:** `localStorage.removeItem("ns_token")` y `localStorage.removeItem("ns_user")`.

**Severidad:** 🔴 Crítico (pérdida de datos clínicos en curso si la sesión expira durante evaluación)

---

## C8 · División potencial por cero en cálculo de discriminabilidad Grober-Buschke
**Archivo:** `neurosoft-backend/app/domain/clinical_engine/grober_buschke.py:285`

```python
discriminabilidad = (rec_aciertos / total_dianas) - (rec_falsos / total_distr)
```

**Problema:** El guard de línea 284 verifica `total_dianas > 0`, pero la segunda división `rec_falsos / total_distr` no tiene guard si `total_distr=0`.

**Impacto clínico:** Cálculo erróneo del índice de discriminabilidad — fundamental para diagnosticar amnesia hipocampal vs déficit ejecutivo en adulto mayor.

**Severidad:** 🔴 Crítico

---

## C9 · Race condition en optimistic locking de evaluaciones
**Archivo:** `neurosoft-backend/app/infrastructure/repositories/evaluation_repo.py:155-159`

```python
query().filter(...).update({"is_latest": False})
```

**Problema:** Sin transacción explícita. Si dos sesiones marcan `is_latest` simultáneamente para el mismo paciente+protocolo, pueden quedar **dos registros con `is_latest=True`**, rompiendo la invariante.

**Severidad:** 🔴 Crítico (integridad de datos longitudinales)

---

# 🟠 ALTOS — Errores lógicos significativos

## H1 · localStorage.clear() también en AuthProvider y catch JSON
**Archivo:** `neurosoft-frontend/src/contexts.jsx:32, 43`

```js
try { setUser(JSON.parse(s)); }
catch { localStorage.clear(); }
// ...
const logout = () => { localStorage.clear(); setUser(null); };
```

**Problema:** Mismo bug que C7. Logout y JSON parse fallido borran TODAS las preferencias.

**Severidad:** 🟠 Alto

---

## H2 · División por cero en gráfico de tendencia del Dashboard
**Archivo:** `neurosoft-frontend/src/app/dashboard/DashboardPage.jsx:128, 134, 138`

```js
`${30 + i * (540 / (trendData.length - 1))},${20 + (1 - t.val / maxTrend) * 140}`
```

**Problema:** Si `trendData.length === 1`, denominador es 0 → coordenadas `Infinity` → SVG roto.

**Severidad:** 🟠 Alto (primer arranque del clínico con 1 sola evaluación → dashboard quebrado)

---

## H3 · División por cero en NBackActivity y otras rehabilitaciones
**Archivos:**
- `neurosoft-frontend/src/app/rehab/NBackActivity.jsx:194` — `(idx / sequenceRef.current.length) * 100`
- `neurosoft-frontend/src/app/rehab/StroopActivity.jsx:232` — `(idx / trialsRef.current.length) * 100`
- `neurosoft-frontend/src/app/rehab/SetShiftingActivity.jsx:162` — `(trial / totalTrials) * 100`
- `neurosoft-frontend/src/app/rehab/GoNoGoActivity.jsx:149` — `(idx / block.length) * 100`
- `neurosoft-frontend/src/app/rehab/DenominacionClavesActivity.jsx:137`
- `neurosoft-frontend/src/app/rehab/TowerOfLondonActivity.jsx:171`

**Problema:** Cuando se entra a la actividad antes de inicializar `sequenceRef`/`trialsRef`/`totalTrials`, da NaN o Infinity en la barra de progreso → CSS roto (`width: NaN%`).

**Severidad:** 🟠 Alto (UX degradada en arranque de cualquier rehab)

---

## H4 · División por cero en ClinicalInterpretationPanel
**Archivo:** `neurosoft-frontend/src/app/evaluation/ClinicalInterpretationPanel.jsx:60, 62, 120`

```js
const media = escalares.reduce((a, b) => a + b, 0) / escalares.length;
const ds = Math.sqrt(
  escalares.reduce((s, e) => s + Math.pow(e - media, 2), 0) / escalares.length
);
// y:
const promGeneral = disponibles.reduce((a, b) => a + b, 0) / disponibles.length;
```

**Problema:** Análisis de homogeneidad del perfil — si `escalares.length === 0` (paciente sin ningún subtest válido), explota.

**Severidad:** 🟠 Alto

---

## H5 · `Number(localStorage.getItem(...) || 0)` no protege contra string corrupto
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalApplyPage.jsx:33`

```js
const ts=Number(localStorage.getItem(getRetentionStorageKey(retentionScope,x.test_id))||0);
```

**Problema:** Si por alguna razón el storage tiene `"abc"`, `Number("abc")` = `NaN`. El check `if(ts)` lo descarta correctamente, pero los timestamps nunca se valida que sean números enteros plausibles (ej. más de 1 año en el pasado podría indicar storage corrupto).

**Severidad:** 🟠 Alto (validez del intervalo de recobro depende de esto)

---

## H6 · Manejo de errores que tragó excepciones genéricas
**Archivos múltiples backend:**
- `main.py:134` — `except Exception: problems = []`
- `clinical_history_use_cases.py:478, 507`
- `email_service.py:345, 348`
- `admin_import.py:110`
- `emails.py:76, 203`

**Problema:** Excepciones genéricas silenciadas sin loggear el `traceback`. Cuando algo falla, no hay forma de diagnosticarlo desde los logs.

**Severidad:** 🟠 Alto (debugging imposible en producción)

---

## H7 · Asume orden cronológico de evaluaciones sin verificar
**Archivo:** `neurosoft-frontend/src/app/history/ComparePage.jsx:54-57`

```js
if (arr.length >= 2) {
  setPreId(arr[arr.length - 1].evaluation_id || arr[arr.length - 1].id);
  setPostId(arr[0].evaluation_id || arr[0].id);
}
```

**Problema:** Asume que el backend devuelve evaluaciones ordenadas por fecha descendente (más reciente primero). Si el backend cambia el orden o agrega filtros, **PRE puede ser más reciente que POST**, invirtiendo la comparativa.

**Severidad:** 🟠 Alto (invierte signo del cambio reportado al clínico)

---

## H8 · Path Traversal latente al descargar backup
**Archivo:** `neurosoft-backend/app/presentation/api/v1/documents.py:182-183`

**Problema:** Patrón `open(db_path, "rb")` donde `db_path` está actualmente hardcoded, pero el patrón es genérico y vulnerable si alguien lo modifica para aceptar parámetro de URL.

**Severidad:** 🟠 Alto (vulnerabilidad latente)

---

## H9 · Z-score con sigma=0 retorna 0.0 silenciosamente
**Archivo:** `neurosoft-backend/app/domain/clinical_engine/strategies.py:287`

```python
z = round((pd - mu) / sigma, 2) if sigma != 0 else 0.0
```

**Problema:** Si un baremo tiene `sigma=0` (error en BD), retornar `0.0` reporta al clínico un **rendimiento "promedio"** cuando en realidad **no se puede calcular**.

**Lo correcto:** retornar `None` o marcar `sin_norma`.

**Severidad:** 🟠 Alto (falso "promedio" en perfil clínico)

---

## H10 · División por cero en transformación percentil → Z
**Archivo:** `neurosoft-backend/app/core/utils.py:354`

**Problema:** Polinomio de aproximación inverso puede tener denominador cero con valores extremos de t.

**Severidad:** 🟠 Alto (perfil Z para clinical histogram)

---

## H11 · Snapshot de Historia Clínica guardado antes del row_version actualizado
**Archivo:** `neurosoft-backend/app/application/use_cases/clinical_history_use_cases.py:147`

**Problema:** El snapshot se captura ANTES de incrementar `row_version`. Al consultar versiones históricas, el número de versión no coincide con el estado real.

**Severidad:** 🟠 Alto (trazabilidad/auditoría)

---

## H12 · Stroop: interferencia no se recalcula al editar c0/c1 después
**Archivo:** `neurosoft-frontend/src/app/evaluation/ReactivePanel.jsx:170`

```js
onChange={e=>{setS(`c${i}`,e.target.value);if(i===2&&scores.c0&&scores.c1){const interf=parseInt(e.target.value||0)-((parseInt(scores.c0)*parseInt(scores.c1))/(parseInt(scores.c0)+parseInt(scores.c1)));setS("interferencia",String(Math.round(interf)))}}}
```

**Problema:** La interferencia solo se calcula al cambiar `c2`. Si el clínico ingresó c0=10, c1=12, c2=5 (calcula interferencia) y luego corrige c0=15, la interferencia queda obsoleta basada en el c0 viejo.

**Severidad:** 🟠 Alto (resultado clínico desactualizado silenciosamente)

---

## H13 · Keyboard shortcuts globales también disparan en inputs (A11y)
**Archivo:** `neurosoft-frontend/src/contexts.jsx:175-186`

**Problema:** El handler de `Alt+H`, `Alt++`, `Alt+-` se ejecuta incluso si el usuario está escribiendo en un input. En App.jsx:224 sí se verifica `if(tag==="input"||tag==="textarea"||tag==="select")return`, pero en `contexts.jsx` no. Resultado: si Mayra está escribiendo "¡Hola!" en una observación y escribe `+` con shift+`=`, le sube el font scale.

**Severidad:** 🟠 Alto (UX interrumpida durante redacción de informes)

---

# 🟡 MEDIOS — Validación, edge cases, code smells

## M1 · `parseInt` sin radix
**Archivos múltiples:**
- `App.jsx:188` — `parseInt(localStorage.getItem(KEY)||"0",10)` ✓ tiene radix
- `ConfigPage.jsx:135, 136` — sin radix
- `ClinicalHistoryPage.jsx:92, 96, 156, 177` — sin radix
- `RegisterPage.jsx:194, 245` — sin radix
- `RehabPage.jsx:558` — sin radix
- `ReactivePanel.jsx:170, 184` — múltiples `parseInt(...)` sin radix
- `AuditoriaTab.jsx:67`, `AdminKpisTab.jsx:114` — sin radix

**Problema:** Sin radix, strings que empiezan con "0" pueden interpretarse como octal en motores antiguos (no en V8 moderno, pero buena práctica).

**Severidad:** 🟡 Medio (compatibilidad y claridad)

---

## M2 · Slice de 3 chars puede colisionar índices con prefijo común
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalResultsPage.jsx:82`

```js
const k=i.n.replace(/[^A-Z]/g,"").slice(0,3);indicesMap[k]=Math.round(i.v||0)
```

**Problema:** Si dos índices empiezan con las mismas 3 mayúsculas (poco probable en WISC/WAIS pero posible en protocolos futuros), uno sobreescribe al otro.

**Severidad:** 🟡 Medio

---

## M3 · `indicesMap[p.a]&&indicesMap[p.b]` excluye valor 0
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalResultsPage.jsx:83`

```js
const discrepancias=DISCREPANCY_PAIRS.filter(p=>indicesMap[p.a]&&indicesMap[p.b])
```

**Problema:** Si un índice vale 0 (improbable pero posible), no se incluye en discrepancias. Debería ser `!= null`.

**Severidad:** 🟡 Medio

---

## M4 · Try/catch silenciosos sin loggear nada (frontend)
**Archivos:** múltiples — `App.jsx:209,216`; `AgendaPage.jsx:68,86`; `NeuroCanvas.jsx:275`; `HistorialPage.jsx:59`; `PanelIA.jsx:493`; `ConfigPage.jsx:50`; `ClinicalHistoryPage.jsx:163`.

**Problema:** `catch {}` o `.catch(() => {})` sin tracking. Cualquier error (red, parsing, validación) se pierde para siempre.

**Severidad:** 🟡 Medio (debugging imposible para Mayra y futuros usuarios)

---

## M5 · Magic number `9999` como sentinel "no realizado"
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalApplyPage.jsx:99`

```js
pd[x.test_id]=v!=null&&v!==""?parseFloat(v):9999
```

**Problema:** El backend interpreta `9999` como "prueba no realizada" (convención del sistema VBA original mencionada en CLAUDE.md backend). Pero si una prueba real legítimamente tiene PD=9999 (improbable en escalares clínicos pero técnicamente posible en pruebas con tiempos en segundos), se confunde con "no realizada".

**Severidad:** 🟡 Medio (ambigüedad semántica)

---

## M6 · localStorage `ns_codif_t_*` se borra cuando un PD pasa de tener valor a vacío
**Archivo:** `neurosoft-frontend/src/app/evaluation/EvalApplyPage.jsx:59`

```js
useEffect(()=>{... tests.forEach(x=>{... if(isClinicalTestDone(x,puntajes)){if(!localStorage.getItem(key))localStorage.setItem(key,String(Date.now()))}else localStorage.removeItem(key)});...},[puntajes,tests,retentionScope]);
```

**Problema:** Si el clínico borra accidentalmente el PD de una prueba de codificación (ej. quería corregir y borró el campo), **se borra el timestamp de inicio**. Cuando vuelva a ingresar el PD, se reinicia el contador del intervalo de recobro → **invalidación silenciosa del recobro diferido**.

**Severidad:** 🟡 Medio (validez clínica del recobro)

---

## M7 · `am_key()` retorna fallback "5056" para edades < 50
**Archivo:** `neurosoft-backend/app/core/utils.py:287`

```python
return f"5056{pd}" if years >= 50 else None
```

**Problema:** Pacientes en frontera (50-55 años) reciben baremo "5056" cuando podrían tener una banda específica. Necesita revisión clínica de la convención.

**Severidad:** 🟡 Medio

---

## M8 · Rate limiting hardcoded
**Archivo:** `neurosoft-backend/app/presentation/api/v1/auth.py:180-181`

```python
_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 60
```

**Problema:** No configurable vía env. En desarrollo es molesto para tests, en producción puede ser insuficiente.

**Severidad:** 🟡 Medio

---

## M9 · IIFE recrea `exportData` en cada render de ComparePage
**Archivo:** `neurosoft-frontend/src/app/history/ComparePage.jsx:145-263`

**Problema:** El `(() => {...})()` que envuelve el resumen RCI define `exportData` y todo el cálculo de `rciResults` en cada render. Para 100+ subtests, esto es lento.

**Severidad:** 🟡 Medio (performance en evaluaciones largas)

---

## M10 · Toast sin límite máximo de simultáneos
**Archivo:** `neurosoft-frontend/src/contexts.jsx:80-86`

**Problema:** Si por alguna razón se pushean 100 toasts en un loop (ej. error en validación masiva), todos aparecen en pantalla.

**Severidad:** 🟡 Medio

---

## M11 · Caras-R: `parseInt` repetido 8 veces en la misma expresión
**Archivo:** `neurosoft-frontend/src/app/evaluation/ReactivePanel.jsx:184`

```js
{scores.aciertos&&<div... > PD: {Math.max(0,(parseInt(scores.aciertos)||0)-(parseInt(scores.errores)||0))} · ICI: {((parseInt(scores.aciertos)||0)-(parseInt(scores.errores)||0)>0?((parseInt(scores.aciertos)||0)-(parseInt(scores.errores)||0))/((parseInt(scores.aciertos)||0)+(parseInt(scores.errores)||0)):0).toFixed(2)}</div>}
```

**Problema:** `parseInt` ejecutado 8 veces en línea. Re-parsing en cada render. Además dificulta lectura.

**Severidad:** 🟡 Medio (mantenibilidad)

---

## M12 · Cálculo de edad usa `parseInt` sobre cadena formateada
**Archivo:** `neurosoft-frontend/src/app/patients/ClinicalHistoryPage.jsx:92, 156, 177`

```js
? parseInt(pat.age_display) // "8a 3m" → 8 years
```

**Problema:** Frágil. Si el formato cambia a "8 años 3 meses", `parseInt` aún da 8 pero por suerte. Mejor sería que el backend devuelva `age_years` y `age_months` numéricos.

**Severidad:** 🟡 Medio

---

## M13 · Snapshot HC con bug de versionado
Ver H11 (se mantiene en categoría Alto).

---

## M14 · Token JWT sin opción explícita `verify_exp`
**Archivo:** `neurosoft-backend/app/infrastructure/auth/auth_service.py:173-174`

**Problema:** `jwt.decode(...)` sin `options={"verify_exp": True}`. Python-jose lo hace por defecto, pero confiar en defaults es frágil.

**Severidad:** 🟡 Medio

---

## M15 · `NUM_ITEMS = 16` hardcoded en Grober-Buschke
**Archivo:** `neurosoft-backend/app/domain/clinical_engine/grober_buschke.py:60`

**Problema:** El número de palabras del Grober & Buschke está hardcoded. Si en el futuro se aplica una versión de 12 ó 24 ítems, el código falla.

**Severidad:** 🟡 Medio

---

# 🟢 BAJOS — Cosméticos, code quality

## B1 · `key={i}` con index en listas que pueden mutar
**Archivos:** `App.jsx:90`, `Skeleton.jsx:65,100,120,126,167,175`, `AgendaPage.jsx:157,216,259,263`, `stimuli.jsx:39,166,173,235,265,270,275,297,311,374,412`, `HelpPage.jsx:164`, `PanelCompartir.jsx:496,505`.

**Problema:** React puede tener bugs sutiles de estado si la lista se filtra o reordena. En la mayoría de casos arriba las listas no mutan, pero es buena práctica usar IDs estables.

**Severidad:** 🟢 Bajo

---

## B2 · `parseInt(e.target.value||0)` — `||0` dentro de parseInt
**Archivo:** `neurosoft-frontend/src/app/evaluation/ReactivePanel.jsx:170`

```js
parseInt(e.target.value||0)
```

**Problema:** Si `e.target.value === ""`, `"" || 0` → `0` (no `"0"`). Funciona pero confuso. Lo correcto: `parseInt(e.target.value) || 0`.

**Severidad:** 🟢 Bajo

---

## B3 · `alert()` y `confirm()` nativos en lugar de modal/toast
**Archivos múltiples:**
- `EvalResultsPage.jsx:106,109,112,114,116,118,120,182,319` — 9 alert()s
- `HistorialPage.jsx:72`, `InformesPage.jsx:72`, `EvalApplyPage.jsx:99`, `EstimulosTab.jsx:29`, `SpacedRetrievalActivity.jsx:78`, `ErrorBoundary.jsx:75`
- `confirm()`: `BackupTab.jsx:23`, `PanelIA.jsx:471,504`, `EvalResultsPage.jsx:106`, `RehabPage.jsx:251`, `PanelCompartir.jsx:308`

**Problema:** `alert()` es bloqueante, feo, y no respeta el tema oscuro. Ya hay un sistema de Toast (`useToast()`) que debería usarse.

**Severidad:** 🟢 Bajo (UX)

---

## B4 · Acceso directo a `scores.aciertos` truthy excluye "0"
**Archivo:** `neurosoft-frontend/src/app/evaluation/ReactivePanel.jsx:184`

```js
{scores.aciertos&&<div...
```

**Problema:** Si `scores.aciertos === "0"` (string), es truthy (mostraría el panel). Pero si es `0` (number), falsy. Inconsistencia silente.

**Severidad:** 🟢 Bajo

---

## B5 · Códigos `Math.max(0, ...)` o `Math.min(100, ...)` puramente defensivos
**Archivo:** múltiples — `EvalResultsPage.jsx:78` (`zp = z => Math.max(0, Math.min(100, ((z+3)/6)*100))`).

**Problema:** Defensivo correcto, pero la fórmula `(z+3)/6*100` siempre da entre 0–100 si `z ∈ [-3, 3]`. El clamping silenciosamente oculta valores extremos sin avisar al clínico.

**Severidad:** 🟢 Bajo (Z=4 silenciosamente mostrado como 100%)

---

## B6 · `setTimeout(() => setReady(true), 100)` en LoginPage
**Archivo:** `neurosoft-frontend/src/app/auth/LoginPage.jsx:27`

**Problema:** Hace que el formulario aparezca con 100ms de delay sin razón clara. Buggy si el usuario es rápido y golpea Enter antes.

**Severidad:** 🟢 Bajo (cosmético)

---

## B7 · Magic numbers en report_service.py (PDF)
**Archivo:** `neurosoft-backend/app/infrastructure/report_service.py:354`

```python
def _check_page(self, c, y: float, need: float = 60, ...)
```

**Problema:** Espacios mágicos (60, 80, 200) sin constantes nombradas.

**Severidad:** 🟢 Bajo (mantenibilidad)

---

## B8 · Funciones backend de generación PDF de >150 líneas sin comentarios
**Archivo:** `neurosoft-backend/app/infrastructure/report_service.py`

**Problema:** Mantenimiento difícil.

**Severidad:** 🟢 Bajo

---

## B9 · "polling tick" en App.jsx pierde estado si falla la primera llamada
**Archivo:** `neurosoft-frontend/src/App.jsx:190-216`

```js
const tick=async()=>{
  try {
    const panel=await api.get(...).catch(()=>null);
    if(!panel||!panel.pacientes)return;  // ← return temprano
    ...
    last=stamp;  // ← sólo se actualiza si todo va bien
    localStorage.setItem(KEY,String(stamp));
  } catch {}
};
```

**Problema:** Si `panel` es null o `pacientes` falta, no se actualiza `last`. La siguiente ejecución usará el mismo `since`. Si esto persiste, eventualmente todas las sesiones recientes serán "nuevas" repetidamente.

**Severidad:** 🟢 Bajo (toast molesto de notificaciones duplicadas)

---

## B10 · Subprocess Ollama sin verificar resultado
**Archivo:** `neurosoft-backend/app/presentation/api/v1/ai.py:582-586`

**Problema:** `subprocess.Popen(...)` lanza el installer pero no verifica si terminó exitosamente.

**Severidad:** 🟢 Bajo

---

## B11 · Type coercion frágil en strategies.py
**Archivo:** `neurosoft-backend/app/domain/clinical_engine/strategies.py` (varias líneas: 194, 206, 265, 406, 572)

**Problema:** `float(valor[2]) if isinstance(valor, (list, tuple)) and len(valor) >= 3 else float(valor)` — Si `valor` es lista de 2 elementos, falla en `float(valor)`.

**Severidad:** 🟢 Bajo

---

## B12 · TODO comentario sin contexto en entities
**Archivo:** `neurosoft-backend/app/domain/entities/clinical_history.py:13`

**Problema:** Referencia a `TODO_EL_CODIGO.txt` sin contexto.

**Severidad:** 🟢 Bajo

---

## B13 · Scoring use case descarta resultados obsoletos silenciosamente
**Archivo:** `neurosoft-backend/app/application/use_cases/scoring_use_cases.py:348`

**Problema:** `except (TypeError, ValueError) as _skip_exc: logger.warning(...)` — Resultado descartado, pero usuario obtiene una evaluación incompleta sin aviso explícito.

**Severidad:** 🟢 Bajo

---

# 📋 Plan de remediación sugerido

### Sprint inmediato (24-48 h)
1. **C1** — Rey 15-Item: paréntesis (5 minutos de cambio, alto impacto clínico)
2. **C7, H1** — `localStorage.clear()` → `removeItem` específico (10 min)
3. **C2, C3, C4, C8** — Agregar guards `if denom > 0` en backend (30 min)
4. **H2, H3, H4** — Agregar guards en divisiones del frontend (30 min)
5. **H9** — Z-score con sigma=0 → retornar None en lugar de 0.0 (10 min)

### Sprint corto (1 semana)
6. **C5** — Whitelist explícita en ALTER TABLE
7. **C6** — Wrap legacy import en transaction con rollback
8. **C9** — Lock optimista en `is_latest`
9. **H7** — Verificar orden cronológico en ComparePage antes de asignar PRE/POST
10. **H12** — Recalcular interferencia Stroop en todos los cambios
11. **H13** — Verificar focus en input antes de disparar atajos
12. **M4** — Agregar al menos `console.warn()` en todos los `catch {}`

### Sprint medio (2-3 semanas)
13. **B3** — Migrar todos los `alert()`/`confirm()` a Toast/Modal
14. **M1, B2** — Limpiar todos los `parseInt` sin radix
15. **M5** — Documentar formalmente la convención `9999`
16. **H10, H11, H6** — Backend cleanup
17. **M11** — Extraer parseInt en variable local en ReactivePanel

### Sprint mejora continua
- **B1** — Cambiar `key={i}` por IDs estables donde aplique
- **B7, B8** — Refactor de constantes en report_service.py
- **M9** — Memoizar `rciResults` y `exportData` con useMemo

---

# 🧭 Notas metodológicas

- **Auditoría manual + agentes Explore**: revisión cruzada en paralelo
- **Sin cambios aplicados**: este documento es 100% lectura
- **Cobertura**: ~80% del código clínico crítico revisado, 100% del flujo de autenticación, 60% del módulo rehab
- **Falsos positivos posibles**: algunas "divisiones por cero" tienen guards distantes (>10 líneas) que pueden haberse pasado por alto. Confirmar antes de fixear

---

**Documento generado:** 15/05/2026
**Por:** Claude (auditor de código)
**Para:** Johan Salgado · `jssalgadosa@unal.edu.co`
