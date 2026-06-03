# docs/ — Documentación del proyecto NeuroSoft

Esta carpeta agrupa documentación histórica, planning, samples y scripts auxiliares. El código fuente y los entregables del build NO viven aquí.

## Estructura

| Carpeta | Contenido | Cuándo consultar |
|---|---|---|
| `audits/` | Auditorías de código históricas (bugs, refactor, seguridad) | Buscar el origen de un fix o un regresión histórica |
| `beta/` | Guías y manuales del beta tester (PDF + MD) | Cuando se prepara un release a beta tester |
| `historic-prompts/` | Prompts antiguos para sesiones de Claude / diseño | Solo si hace falta retomar contexto de una sesión vieja |
| `legal/` | Habeas Data, registro INVIMA, marco normativo Colombia | Antes de tocar manejo de datos sensibles o lanzar comercial |
| `planning/` | Roadmaps clínicos, investigación, plan de implementación | Para decidir prioridades de feature o cambios mayores |
| `samples/` | PDFs de muestra de informes (todas las variantes Pro) | Mostrar al beta tester o documentar diseño actual |
| `scripts/` | Scripts auxiliares para generar PDFs (manual, brochure, dossier) | Para regenerar entregables después de cambios visuales |

## Reglas

1. **Raíz del proyecto**: solo `README.md` + `CLAUDE.md`. Cualquier otro `.md` debería terminar aquí.
2. **`dist/`**: solo `NeuroSoft.exe`, `NeuroSoft-Setup.exe` y `MANUAL_BETA_TESTER.pdf` (el que el instalador empaqueta).
3. **Auditorías**: archivar con fecha (`AUDIT_YYYY-MM-DD.md`). Nunca borrar — son histórico de decisiones.

## Genéricos a tener a la mano

- **CLAUDE.md raíz** — instrucciones para sesiones de Claude Code (qué ya existe, qué NO recomendar).
- **`docs/planning/CLINICAL_ROADMAP.md`** — estado vivo del roadmap clínico.
- **`docs/legal/HABEAS_DATA.md`** — política de manejo de datos clínicos.
