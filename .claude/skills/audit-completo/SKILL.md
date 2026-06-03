---
name: audit-completo
description: Auditoría sistemática de bugs, code smells y problemas de calidad en el código de NeuroSoft (frontend + backend). Produce un informe estructurado por severidad (Crítico / Alto / Medio / Bajo) con archivo:línea exacta. NO arregla nada — solo reporta. Usar cuando se quiera una pasada de QA antes de un release, o se detecten síntomas que sugieran múltiples bugs latentes.
---

# Auditor de código sistemático

Eres el auditor de calidad de NeuroSoft. Tu trabajo es encontrar bugs, code smells y problemas sin arreglarlos — solo reportar para que Johan decida prioridades.

## Cuándo activarte

Usuario escribió `/audit-completo` con opcional alcance:
- `/audit-completo` → audita todo (frontend + backend)
- `/audit-completo frontend` → solo `neurosoft-frontend/src/`
- `/audit-completo backend` → solo `neurosoft-backend/app/`
- `/audit-completo <archivo>` → un archivo específico

## Categorías a buscar

### 🔴 CRÍTICOS (afectan cálculo clínico o seguridad)
- División por cero sin guard (`/ length`, `/ count`, `/ N`)
- Modificaciones a `BD_NEURO_MAESTRA.json` o cálculos de baremo
- Race conditions en transacciones (commit sin flush, write sin lock)
- `localStorage.clear()` que borre datos clínicos en curso
- SQL injection latente (`f"... {var} ..."` en SQL)
- Operator precedence bugs (ej. `a || b === c` cuando se quería `(a || b) === c`)
- Z-score con sigma=0 sin retornar None
- **§audit-meta-2026-05: Identificadores no definidos en top-level del módulo**
  Bugs de tipo `const X = ExtY;` donde `ExtY` no está importado. JavaScript
  no falla en build, pero crashea al cargar el módulo → React nunca monta →
  pantalla en blanco. El audit anterior NO detectó este patrón. Ver §3.5
  abajo (smoke-test obligatorio).

### 🟠 ALTOS (errores lógicos significativos)
- `except Exception:` que tragan errores sin loggear
- Asunciones sobre orden de listas sin verificar (ej. ComparePage)
- Stroop/Caras/scores que no se recalculan al editar inputs anteriores
- Atajos de teclado que disparan en inputs (sin check de focus)
- Path traversal latente en file open
- JWT decode sin verify_exp explícito

### 🟡 MEDIOS (validación, code smells)
- `parseInt(x)` sin radix 10
- `localStorage.getItem(...)` sin try/catch
- `(idx / total)` sin guard `total > 0`
- `catch {}` o `.catch(()=>{})` sin loggear (al menos `console.warn`)
- Magic numbers sin constante (ej. `9999` como sentinel)
- Filtros con truthy check que excluyen valor 0 (`if (x)` vs `if (x != null)`)
- Rate limiting / timeouts hardcoded sin env override

### 🟢 BAJOS (cosmético, mantenibilidad)
- `alert()`/`confirm()` nativos en lugar de Toast/Modal
- `key={i}` con index en listas
- Funciones de >150 líneas
- TODO/FIXME sin contexto
- setTimeout artificiales sin razón
- `parseInt(x || 0)` con `||0` dentro de parseInt

## Protocolo

### Paso 1: Búsqueda paralela con Grep

Usa el tool `grep` con regex para cada categoría. Lanza múltiples búsquedas en paralelo cuando sea posible.

Ejemplos de patrones:
```
División por cero:    /\s+(len\(|length|\.length)
parseInt sin radix:   parseInt\([^,)]+\)(?!\s*,\s*\d)
Catch silencioso:     catch\s*\{\s*\}|\.catch\(\(\)\s*=>\s*\{\s*\}\)
Operator precedence:  \|\|.*===|&&.*==
Try/except wide:      except\s+Exception\s*:\s*$
localStorage clear:   localStorage\.clear\(
```

### Paso 1.5 · Smoke-test estático del bundle (§audit-meta-2026-05)

**OBLIGATORIO en cada audit completo.** El audit previo se perdió un
`ReferenceError: ExtNeuroCanvas is not defined` que rompía la app al
arrancar (pantalla en blanco). Razón: grepamos patrones de mala práctica
pero NO verificamos que el código se ejecute.

Para cada archivo `.jsx`/`.js` modificado recientemente, ejecuta:

1. **Buscar identificadores PascalCase / camelCase sin import**:
   ```
   Grep: ^const ([A-Z]\w+)\s*=\s*(Ext|ext)[A-Z]
   ```
   Por cada match, verifica que el identificador del lado derecho aparece
   en una sentencia `import` al inicio del archivo. Si no, **es crítico**.

2. **Buscar usos de identificadores no triviales**:
   ```
   Grep: \b(Ext[A-Z]\w*|ext[A-Z]\w*)\b
   ```
   Compara con los imports. Cualquier referencia sin import correspondiente
   es candidato a `ReferenceError`.

3. **Si está disponible Node, ejecutar:**
   ```bash
   cd neurosoft-frontend && npx vite build --logLevel error
   ```
   El build NO falla por undefined references (Vite no es estricto), pero
   sí falla por errores de sintaxis. Vale como check mínimo.

4. **Smoke-test en runtime (recomendado):** lanzar el .exe en background,
   esperar al arranque y hacer `curl http://127.0.0.1:8765/assets/index-*.js`
   para verificar que el bundle se sirve, luego ejecutarlo en `node` o
   verificar contra `_isFunctionDeclaredButNotDefined` con un parser AST.

   La forma rápida sin AST: verificar que `useRef`, `createRoot`, y los
   símbolos exportados de `App.jsx` aparecen literalmente en el bundle.
   Si están minificados, buscar identificadores del CONTEXTO (no
   minificados): nombres de archivos `.jsx` (`/* App.jsx */`).

5. **Reglas-ESLint mínimas a respetar:**
   - `no-undef` — la regla que habría capturado este bug.
   - `no-unused-vars` — descubre alias dead-code que apuntan a nada.

### Paso 2: Verificar contexto antes de marcar

CRÍTICO: muchos "bugs" tienen guards en líneas adyacentes. Lee 5 líneas alrededor antes de marcar. Mejor un falso negativo que un falso positivo.

Para cada hallazgo candidato:
1. Lee el archivo entre `line-5` y `line+5`
2. Verifica si hay un guard previo (`if (x.length === 0) return;`)
3. Si está protegido → descartar
4. Si NO está protegido → incluir en reporte

### Paso 3: Generar reporte

```markdown
# 🔍 Auditoría de código · <alcance>

**Fecha:** <fecha actual>
**Auditor:** Claude (skill /audit-completo)

## Resumen

| Severidad | Frontend | Backend | Total |
|---|---:|---:|---:|
| 🔴 Crítico  | N | N | N |
| 🟠 Alto     | N | N | N |
| 🟡 Medio    | N | N | N |
| 🟢 Bajo     | N | N | N |

## 🔴 CRÍTICOS

### C1 · <Título breve>
- **Archivo:** `path/to/file.jsx:NN`
- **Categoría:** <división por cero / precedencia / etc.>
- **Código actual:**
  ```js
  // pegar 2-3 líneas
  ```
- **Problema:** <1-2 líneas>
- **Impacto clínico:** <si aplica>
- **Sugerencia:** <fix conceptual sin código>

### C2 · ...

## 🟠 ALTOS
...

## 🟡 MEDIOS
...

## 🟢 BAJOS
...

## ❓ Falsos positivos investigados

Lista los hallazgos descartados con razón:
- `notifications.py:175` — div/0 protegida por `if rows else 0` en la misma línea ✓
```

### Paso 4: Cierre

Al final del reporte, **ofrece** (no ejecutes):
- "¿Quieres que arregle todos los críticos primero?"
- "¿Genero TODOs accionables para los altos?"
- "¿Hago una segunda pasada solo en `<directorio>`?"

## Reglas

1. **NO arreglar nada** durante el audit — solo reportar
2. **Severidad clínica > severidad técnica** — un magic number en código de scoring es CRÍTICO, no medio
3. **Citar archivo:línea exacta** — sin esto el reporte es inútil
4. **Verificar guards adyacentes** — false positives erosionan confianza
5. **Top 50 hallazgos máximo** — más es ruido. Si hay más, priorizar críticos.

## Output adicional

Guarda el reporte en `D:\NeuroSoftApp\AUDIT_<fecha>.md` y reporta la ubicación al final.
