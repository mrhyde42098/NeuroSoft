---
name: actualizar-contexto-ia
description: Sincroniza on-demand los archivos de lectura para IAs (PUNTO_INFLEXION, CLAUDE.md, INDICE_MAESTRO) sin hacerlo en cada tarea. Usar SOLO cuando Johan pida actualizar contexto, cerrar sesión importante, o antes de empaquetar para otra IA. Diseñado para ahorrar tokens.
---

# Actualizar contexto IA (on-demand)

## Objetivo

Refrescar los **punteros de lectura** para humanos e IAs sin reescribir documentación histórica.

## Cuándo activarte

- Usuario escribió `/actualizar-contexto-ia`
- Johan dice "actualiza el contexto para la próxima IA"
- Antes de `/exportar-sesion` en sesiones largas
- **NO** activar automáticamente al cerrar cada tarea pequeña → usar `/actualizar-estado-vivo` en su lugar

## Orden de trabajo (eficiente en tokens)

### 1. Fuente de verdad

Leer solo:
- `docs/ESTADO_VIVO.md` (estado actual)
- Cambios de la sesión (git diff o lista del usuario)

### 2. Actualizar PUNTO_INFLEXION (si sesión significativa)

Archivo: `docs/PUNTO_INFLEXION_2026-06-05.md`

Añadir sección `## Actualizaciones` con:
- Fecha
- Trabajo de la sesión (máx. 15 líneas)
- Archivos modificados (lista corta)
- Pendiente inmediato (3 items máx.)
- Comandos útiles si cambiaron

**No** regenerar las secciones históricas V0–V6.

### 3. Parche CLAUDE.md (mínimo)

Archivo: `CLAUDE.md`

Solo actualizar si cambió:
- Conteo de tests (`pytest` último run)
- Skills nuevas (lista en §Skills)
- Fecha en cabecera `> **Actualizado:**`
- Sección "Pendiente real" → puntero a ESTADO_VIVO (no duplicar lista larga)
- Métricas build si hubo release

**No** reescribir referencias clínicas ni historial de sprints completos.

### 4. INDICE_MAESTRO (solo si hay docs nuevos)

Si se creó/movió documentación en la sesión, añadir **una fila** en `docs/INDICE_MAESTRO.md`.

### 5. Opcional: neurosoft-backend/CLAUDE.md

Solo si se tocó motor clínico: actualizar conteos de pruebas o casos ground-truth.

## Checklist de salida

```
[ ] ESTADO_VIVO.md ya estaba actualizado (o se actualizó con /actualizar-estado-vivo)
[ ] PUNTO_INFLEXION tiene bloque de actualización con fecha de hoy
[ ] CLAUDE.md cabecera + métricas si aplica
[ ] INDICE_MAESTRO si hay doc nuevo
```

## Salida al usuario

Indicar qué archivos se tocaron y el **orden de lectura** recomendado para la próxima IA (4 líneas máx.).
