---
name: organizar-repo
description: Auditoría de auditorías — ordena carpetas, archiva docs viejos, actualiza ESTADO_VIVO y CLAUDE.md. Usar cuando la carpeta del proyecto esté desordenada, haya AUDIT_*.md en la raíz, o Johan pida limpiar/organizar el monorepo sin borrar historial.
---

# Organizar repositorio NeuroSoft

## Objetivo

Mantener `D:\NeuroSoftApp` legible para humanos e IAs sin perder historial.

## Protocolo

### 1. Inventario raíz

Listar carpetas/archivos en raíz. Solo deben quedar como `.md` activos:
- `README.md`
- `CLAUDE.md`

Los `AUDIT_YYYY-MM-DD.md` → mover a `docs/historico/audits/`.

### 2. Verificar estado real vs docs viejos

Leer `docs/ESTADO_VIVO.md` y contrastar con:
- `docs/planning/ROADMAP_2026.md`
- Último `docs/historico/audits/AUDIT_*.md`

Actualizar `ESTADO_VIVO.md` si hay discrepancia.

### 3. Archivar sin borrar

| Tipo | Destino |
|---|---|
| Audits raíz | `docs/historico/audits/` |
| Prompts viejos | `docs/historico/prompts/` |
| Excel VBA / build scripts obsoletos | `archive/legacy/` |
| Scripts one-off | `archive/scripts-oneoff/` |

### 4. Skills de mantenimiento

- `/actualizar-estado-vivo` — al cerrar sprints (obligatorio para IAs)
- `/actualizar-contexto-ia` — solo on-demand (ahorra tokens)

### 5. Actualizar punteros IA

- `CLAUDE.md` — sección "Punto de entrada IA"
- `docs/INDICE_MAESTRO.md`
- `docs/historico/CARPETAS_RAIZ.md`

### 5. NO hacer

- Borrar `BD_NEURO_MAESTRA.json` ni protocolos clínicos
- Borrar auditorías (solo mover)
- Sugerir migrar stack (TS, Electron, PostgreSQL)

## Entregable

Breve resumen: qué se movió, qué quedó pendiente, enlaces a `ESTADO_VIVO.md`.
