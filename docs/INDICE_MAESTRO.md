# Índice maestro — NeuroSoft App
**Para humanos e IAs.** Empieza aquí si no sabes qué archivo leer.

---

## 1. Lectura obligatoria (orden)

| # | Archivo | Para qué |
|---|---|---|
| 1 | [`PUNTO_INFLEXION_2026-06-05.md`](PUNTO_INFLEXION_2026-06-05.md) | Traspaso completo: qué es el proyecto, qué se hizo, build, restricciones |
| 2 | [`ESTADO_VIVO.md`](ESTADO_VIVO.md) | Qué está ✅ hecho vs ❌ pendiente (actualizar cada sprint) |
| 3 | [`../CLAUDE.md`](../CLAUDE.md) | Reglas para IA: qué NO recomendar, skills, stack cerrado |
| 4 | [`ARQUITECTURA.md`](ARQUITECTURA.md) | Arquitectura técnica monorepo |
| 5 | [`../neurosoft-backend/CLAUDE.md`](../neurosoft-backend/CLAUDE.md) | Motor clínico, baremos, casos ground truth |
| 6 | [`../neurosoft-frontend/CLAUDE.md`](../neurosoft-frontend/CLAUDE.md) | React, REACTIVOS, flujo evaluación |

---

## 2. Sprint activo — REACTIVOS

| Archivo | Tipo |
|---|---|
| [`VERIFICACION_INS_PDF_2026-06-05.md`](VERIFICACION_INS_PDF_2026-06-05.md) | PDF IN&S vs JSON vs clinical.js — veredicto ✅ JSON |
| [`REACTIVOS_WISC_WAIS_PLAN.md`](REACTIVOS_WISC_WAIS_PLAN.md) | Plan P0: gap analysis WISC/WAIS → clinical.js |
| `Capacitaciones Clínicas/protocolos/*.json` | Fuente clínica autoritativa |
| `docs/scripts/audit_reactivos_gap.py` | Script inventario placeholders |

## 3. Organización del repo

| Archivo | Tipo |
|---|---|
| [`AUDITORIA_DE_AUDITORIAS_2026-06-05.md`](AUDITORIA_DE_AUDITORIAS_2026-06-05.md) | Limpieza jun 2026 — qué se movió y por qué |
| [`historico/CARPETAS_RAIZ.md`](historico/CARPETAS_RAIZ.md) | Mapa de cada carpeta en raíz |

| [`infra/BUILD_Y_DISTRIBUCION.md`](infra/BUILD_Y_DISTRIBUCION.md) | vendor, installer, mcp, scripts .py raíz |

## 4. Auditorías

| Archivo | Tipo |
|---|---|
| [`historico/audits/AUDIT_2026-06-05.md`](historico/audits/AUDIT_2026-06-05.md) | **Más reciente** — integral post V6 |
| [`historico/audits/`](historico/audits/) | Auditorías 26-may → 5-jun 2026 |
| [`audits/`](audits/) | Auditorías mayo 2025 (bugs, backend v2) |
| [`AUDITORIA_PDFs.md`](AUDITORIA_PDFs.md) | Sprint V1–V5 PDF + reactivos (23 fixes) |
| [`REFERENCIAS_INFORMES_NPS.md`](REFERENCIAS_INFORMES_NPS.md) | **Estándar visual informes** IN&S+Pro, muestras mínimas, prompt maestro |
| [`casos-clinicos/AUDITORIA_EXCEL_VS_MOTOR.md`](casos-clinicos/AUDITORIA_EXCEL_VS_MOTOR.md) | Baremos vs Excel VBA |
| [`casos-clinicos/AUDITORIA_55_TESTS_SOLO_MOTOR.md`](casos-clinicos/AUDITORIA_55_TESTS_SOLO_MOTOR.md) | Fuentes clínicas 52 tests |

---

## 3. Roadmaps y planning

| Archivo | Nota |
|---|---|
| [`planning/ROADMAP_2026.md`](planning/ROADMAP_2026.md) | Plan original QW/M/L — **ver ESTADO_VIVO para estado real** |
| [`planning/CLINICAL_ROADMAP.md`](planning/CLINICAL_ROADMAP.md) | Roadmap clínico detallado |
| [`planning/ROADMAP_EXPANSION.md`](planning/ROADMAP_EXPANSION.md) | Expansión producto |
| [`historico/sprints/`](historico/sprints/) | Planes sprint estética UI |

---

## 4. Clínico

| Archivo | Contenido |
|---|---|
| [`casos-clinicos/CASOS_GROUND_TRUTH.md`](casos-clinicos/CASOS_GROUND_TRUTH.md) | 15 casos validados motor |
| [`Capacitaciones Clínicas/protocolos/`](../Capacitaciones%20Clínicas/protocolos/) | Protocolos fuente (no editar baremos) |
| `neurosoft-frontend/src/data/clinical.js` | REACTIVOS captura UI |

---

## 5. Seguridad y legal

| Archivo |
|---|
| [`seguridad/MODELO_AMENAZAS.md`](seguridad/MODELO_AMENAZAS.md) |
| [`legal/HABEAS_DATA.md`](legal/HABEAS_DATA.md) |
| [`legal/GUIA_REGISTRO_INVIMA_SaMD.md`](legal/GUIA_REGISTRO_INVIMA_SaMD.md) |

---

## 6. Beta y build

| Archivo |
|---|
| [`beta/INSTRUCCIONES_BETA_TESTER.md`](beta/INSTRUCCIONES_BETA_TESTER.md) |
| `.claude/skills/build-beta-tester/SKILL.md` |
| `dist/NeuroSoft-Setup.exe` (generado, no en git) |

---

## 7. Skills y agentes (`.claude/`)

| Recurso | Uso |
|---|---|
| `skills/audit-completo` | QA bugs por severidad |
| `skills/build-beta-tester` | Pipeline empaquetado |
| `skills/investigar-clinica` | Papers 2022–2026 |
| `skills/exportar-sesion` | Resumen para otro chat |
| `agents/clinical-engine-reviewer.md` | Revisar cambios motor |

---

## 8. Carpetas raíz — mapa rápido

Ver [`historico/CARPETAS_RAIZ.md`](historico/CARPETAS_RAIZ.md) para descripción de cada carpeta del monorepo.

---

## 9. Duplicados conocidos (no consolidar sin revisar)

- `neurosoft-backend/docs/AUDITORIA_BAREMOS_DETALLADA.md` ≈ copia de `docs/AUDITORIA_BAREMOS_DETALLADA.md`
- `neurosoft-backend/docs/RESUMEN_*.md` — resúmenes históricos backend; archivar eventualmente
