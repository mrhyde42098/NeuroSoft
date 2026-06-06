# docs/ — Documentación NeuroSoft App

## Empieza aquí

| Prioridad | Archivo |
|---|---|
| 🟢 | [`INDICE_MAESTRO.md`](INDICE_MAESTRO.md) |
| 🟢 | [`ESTADO_VIVO.md`](ESTADO_VIVO.md) |
| 🟢 | [`PUNTO_INFLEXION_2026-06-05.md`](PUNTO_INFLEXION_2026-06-05.md) |

## Estructura (jun 2026)

| Carpeta | Contenido |
|---|---|
| `historico/` | Auditorías archivadas, prompts viejos, mapa carpetas raíz |
| `audits/` | Auditorías mayo 2025 |
| `planning/` | Roadmaps originales — **estado real en ESTADO_VIVO** |
| `casos-clinicos/` | Ground truth, validación baremos |
| `beta/` | Guías beta tester |
| `legal/` | Habeas Data, INVIMA |
| `seguridad/` | Modelo de amenazas |
| `arquitectura/` | Flujo datos, mapa módulos |

## Reglas de organización

1. **Raíz del repo:** solo `README.md` + `CLAUDE.md` + archivos de build. Los `AUDIT_*.md` van a `docs/historico/audits/`.
2. **No borrar** auditorías ni roadmaps — archivar en `historico/`.
3. **Actualizar** `ESTADO_VIVO.md` al cerrar cada sprint.
4. **`dist/`:** artefactos de build (gitignored).

Ver [`historico/CARPETAS_RAIZ.md`](historico/CARPETAS_RAIZ.md) para el mapa completo del monorepo.
