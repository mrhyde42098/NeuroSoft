---
name: dark-mode-fix
description: Encuentra colores hardcoded en JSX/CSS (style={{background:"#fff..."}}, bg-white, text-gray-700, etc.) y los reemplaza por variables CSS de NeuroSoft (var(--ns-card), var(--ns-text), var(--ns-muted)) para que respeten modo oscuro y alto contraste. Usar cuando un componente se vea mal en dark mode o el usuario reporte falta de contraste.
---

# Dark mode fixer — colores hardcoded → CSS vars

NeuroSoft tiene un sistema de variables CSS (`--ns-*`) que se invierten automáticamente en modo oscuro. Cualquier color hardcoded en JSX rompe este sistema. Tu trabajo es detectar y proponer reemplazos.

## Cuándo activarte

Usuario escribió `/dark-mode-fix` con opcional alcance:
- `/dark-mode-fix` → analiza todo `neurosoft-frontend/src/`
- `/dark-mode-fix <archivo>` → un archivo específico
- `/dark-mode-fix patients` → solo páginas de pacientes

## Mapa de reemplazos (memorizar)

### Inline `style={{...}}`

| Hardcoded | Reemplazar por |
|---|---|
| `background: "#fff"` o `"white"` | `background: "var(--ns-card)"` |
| `background: "#f5f3ef"`, `"#f5f3ff"`, `"#fafafa"` | `background: "var(--ns-subtle)"` |
| `background: "#e4e2de"`, `"#e5e7eb"`, `"#eee"` | `background: "var(--ns-input)"` o `"var(--ns-card-b)"` |
| `color: "#1e293b"`, `"#0f172a"` | `color: "var(--ns-text)"` |
| `color: "#64748b"`, `"#94a3b8"`, `"#6b7280"` | `color: "var(--ns-muted)"` |
| `borderColor: "#e5e7eb"`, `"#e4e2de"` | `borderColor: "var(--ns-card-b)"` |

### Backgrounds semánticos (warnings, errors)

Convertir a `rgba(...)` con opacidad baja para que funcionen en ambos modos:

| Antes | Después |
|---|---|
| `#fef2f2` (red bg) | `rgba(239,68,68,0.08)` |
| `#fef3c7` (amber bg) | `rgba(251,191,36,0.15)` |
| `#fffbeb`, `#fff8e1` | `rgba(245,158,11,0.08)` |
| `#dcfce7`, `#ecfdf5` (green bg) | `rgba(16,185,129,0.08)` |
| `#dbeafe`, `#eff6ff` (blue bg) | `rgba(59,130,246,0.08)` |

### Tailwind classes

| Hardcoded | Mejor pattern |
|---|---|
| `bg-white` | Ya manejado en `index.css` via `.dark-mode .bg-white {background: var(--ns-card)}` |
| `text-gray-700`, `text-gray-800` | Ya manejado en index.css |
| `text-gray-500`, `text-gray-400` | Ya manejado |
| `bg-gray-50`, `bg-gray-100` | Ya manejado |

**Pero** si el color va con un fondo de marca (TEAL gradient, etc.) y el texto debe seguir siendo legible siempre, dejar `text-white` o `text-gray-300` literal.

## Protocolo

### Paso 1: Búsqueda

Usar `grep` para encontrar candidatos en `neurosoft-frontend/src/`:

```regex
style=\{\{[^}]*background:\s*["']#[0-9a-fA-F]+["']
style=\{\{[^}]*color:\s*["']#(?:fff|1e|0f|64|94|6b)[0-9a-fA-F]+
```

Limita a 50 hits por sesión para mantener foco.

### Paso 2: Análisis por archivo

Para cada archivo afectado:
1. Lee el archivo completo
2. Identifica cada hardcoded
3. Determina si:
   - Es semántico (warning, error, success) → usar rgba con opacidad
   - Es estructural (fondo de card, texto principal) → usar `var(--ns-*)`
   - Es del sistema de marca (gradient TEAL→NAVY) → dejar literal

### Paso 3: Aplicar fixes

Usa `edit` con `replace_all: false` (un cambio a la vez). Agrupa cambios del mismo archivo en bloque para legibilidad. Agrega comentario `/* §dark-mode-fix */` en la primera línea modificada de cada archivo para tracking futuro.

### Paso 4: Verificar build

Al terminar, correr:
```bash
cd D:\NeuroSoftApp\neurosoft-frontend && npm run build
```

Si falla, revertir el último archivo modificado.

### Paso 5: Reporte

```markdown
# 🌓 Dark mode fix

## Archivos modificados (N)

### `src/app/.../File.jsx`
- 3 hardcoded backgrounds → `var(--ns-card)` / `var(--ns-subtle)`
- 2 colores de texto → `var(--ns-text)` / `var(--ns-muted)`
- 1 banner amber → `rgba(251,191,36,0.15)`

## Cambios NO aplicados (revisar manualmente)
- `XxxPage.jsx:NN` — color usado en gradient de marca; conservar literal
```

## Reglas

1. **No tocar `tokens.js` ni `index.css`** — son fuente de verdad de los colores
2. **No quitar `text-white`** en botones con fondo TEAL — son intencionales
3. **Conservar colores de estados clínicos** (`#ba1a1a` para Bajo, etc.) — son semánticos clínicos en `utils/colores.js`
4. **Verificar build después** — un typo en CSS rompe todo

## Variables CSS disponibles (de `index.css`)

```
--ns-bg          fondo de página
--ns-card        fondo de tarjeta
--ns-card-b      borde de tarjeta
--ns-input       fondo de inputs
--ns-text        texto principal
--ns-muted       texto secundario
--ns-sidebar     fondo de sidebar
--ns-topbar      fondo de topbar
--ns-subtle      fondo sutil (separadores)
--ns-hover       hover de botones
```

Cualquier cosa fuera de esta paleta requiere justificación.
