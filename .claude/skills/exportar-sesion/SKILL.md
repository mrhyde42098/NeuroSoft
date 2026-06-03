---
name: exportar-sesion
description: Exporta un resumen markdown del trabajo realizado en la sesión actual de Claude Code — archivos modificados, decisiones tomadas, build artifacts generados, y "para la próxima". Útil porque Johan trabaja en múltiples chats simultáneos por límites de tokens y necesita poder retomar en otro chat con contexto completo.
---

# Exportador de resumen de sesión

Genera un archivo markdown que sintetiza el trabajo de la sesión actual para poder retomarlo en otra ventana de chat con todo el contexto.

## Cuándo activarte

Usuario escribió `/exportar-sesion` con opcional título:
- `/exportar-sesion` → usa timestamp como título
- `/exportar-sesion mejoras informe PDF` → usa el título

## Protocolo

### Paso 1: Determinar el alcance

Reúne información sobre lo que cambió en la sesión:

```bash
cd D:\NeuroSoftApp
git status --short
git diff --stat
git log --oneline -20
```

### Paso 2: Identificar artefactos

Verifica si hay nuevos en `dist/`:
```bash
ls -lah dist/ | head
```

Si el `NeuroSoft-Setup.exe` fue actualizado en esta sesión (mtime < 1 hora), apuntarlo.

### Paso 3: Generar el resumen

Escribe el archivo en `D:\NeuroSoftApp\session_logs\YYYY-MM-DD_<titulo-slug>.md`:

```markdown
# 📋 Sesión: <título>

**Fecha:** <ISO timestamp>
**Rama:** <branch>
**Duración aprox:** <si se puede inferir del git log>

## 🎯 Objetivo principal de la sesión

<1-2 líneas que resuman qué se intentaba lograr>

## ✅ Lo que se completó

- ✓ Cambio 1 (archivo:línea) — descripción
- ✓ Cambio 2 (archivo:línea) — descripción
- ✓ Build generado (NeuroSoft-Setup.exe N MB)

## 📂 Archivos modificados (N)

```
M  neurosoft-frontend/src/app/...
M  neurosoft-backend/app/...
A  .claude/skills/.../SKILL.md
```

## 🔍 Decisiones técnicas tomadas

- **Decisión 1**: hicimos X en lugar de Y porque Z
- **Decisión 2**: ...

## ⚠ Cosas que quedaron pendientes / a revisar

- [ ] Pendiente 1 (alta prioridad — afecta al beta tester)
- [ ] Pendiente 2 (media)
- [ ] Idea para futuro: ___

## 🚀 Para la próxima sesión

**Si retomas el trabajo desde otro chat, dile:**

> "Continúa desde la sesión anterior. Lee `D:\NeuroSoftApp\session_logs\<este-archivo>.md`
> para contexto. La prioridad inmediata es: <prioridad>.
> Antes de modificar nada, considera: <warnings>."

## 📌 Comandos clave usados en esta sesión

```
# (lista los 3-5 comandos más relevantes corridos)
npm run build
python build.py --skip-frontend --skip-ollama
& "...\ISCC.exe" installer/NeuroSoft.iss
```

## 🔗 Referencias técnicas tocadas

- Archivos clave: `path/to/file.jsx`
- Funciones tocadas: `funcName()`
- Tests creados/modificados: `tests/.../test_X.py`
```

### Paso 4: Reportar al usuario

```
✅ Sesión exportada
📁 D:\NeuroSoftApp\session_logs\2026-05-15_mejoras-pdf.md

Para retomar desde otro chat:
> "Lee D:\NeuroSoftApp\session_logs\2026-05-15_mejoras-pdf.md
>  y continuamos desde la sección 'Para la próxima sesión'."
```

## Reglas

1. **No incluir credenciales** ni paths secretos (tokens, passwords de beta testers, etc.)
2. **No copiar código completo** — solo referencias archivo:línea
3. **El archivo se guarda LOCAL** — `session_logs/` ya está en `.gitignore` (o agregarlo)
4. **Máximo 200 líneas por export** — si es más, sintetizar

## Setup adicional (primera vez)

Agregar `session_logs/` al `.gitignore` del proyecto (verificar):
```bash
grep -q "session_logs" /d/NeuroSoftApp/.gitignore || echo "session_logs/" >> /d/NeuroSoftApp/.gitignore
mkdir -p /d/NeuroSoftApp/session_logs
```

## Variantes

- `/exportar-sesion completo` — incluye también git diff resumido
- `/exportar-sesion breve` — solo 5 bullets sin detalle
