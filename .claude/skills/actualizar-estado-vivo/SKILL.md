---
name: actualizar-estado-vivo
description: Actualiza docs/ESTADO_VIVO.md (y una línea en PUNTO_INFLEXION si aplica) al cerrar sprints, roadmaps o tareas significativas. Usar al terminar implementación de QW/M/N/P, fixes de auditoría, o cuando cualquier IA complete trabajo de la lista pendiente. NO reescribe CLAUDE.md completo.
---

# Actualizar estado vivo

## Objetivo

Mantener **una sola fuente de verdad** (`docs/ESTADO_VIVO.md`) sin gastar tokens reescribiendo todo el contexto IA.

## Cuándo activarte

- Usuario escribió `/actualizar-estado-vivo`
- Acabas de implementar un item de roadmap (QW-*, M-*, N*, P*, sprint V*)
- Cerraste un fix de `docs/historico/audits/AUDIT_*.md`
- Johan dice "marca como hecho" o "cierra el sprint"

## Protocolo (mínimo, enfocado)

### 1. Leer estado actual

```
docs/ESTADO_VIVO.md
```

### 2. Verificar en código (no confiar en memoria)

- Si marcas ✅: confirma que el código/tests existen (grep, pytest puntual, o archivo modificado en la sesión).
- Si marcas ❌: deja razón breve en la fila o en "Pendiente real".

### 3. Editar ESTADO_VIVO.md

Actualizar **solo** las secciones afectadas:

| Campo | Qué poner |
|---|---|
| Fecha cabecera | `Última actualización: DD mes YYYY` |
| Métricas | Solo si cambiaron (tests count, build, etc.) |
| Tabla sprint/roadmap | Cambiar estado ✅ ⚠️ ❌ |
| Pendiente real | Mover items completados fuera de `[ ]` |

Formato de estado: `✅` hecho · `⚠️` parcial · `❌` pendiente

### 4. PUNTO_INFLEXION (solo si aplica)

Si el cambio es **relevante para retomar en otro chat** (nuevo sprint cerrado, bug crítico, cambio de arquitectura):

Añadir **3-5 líneas** al final de `docs/PUNTO_INFLEXION_2026-06-05.md` bajo `## Actualizaciones`:

```markdown
### DD mes YYYY — [título corto]
- Qué se hizo
- Archivos clave
- Qué sigue
```

**No** reescribir el documento entero.

### 5. NO hacer (ahorro de tokens)

- No reescribir `CLAUDE.md` → usar `/actualizar-contexto-ia` si Johan lo pide
- No duplicar info en `docs/planning/ROADMAP_2026.md`
- No crear nuevo AUDIT en raíz

## Salida al usuario

Resumen de 3-5 bullets: qué filas cambiaron en ESTADO_VIVO y si se tocó PUNTO_INFLEXION.
