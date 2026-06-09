# Informe Maestro Inspector General — NeuroSoft App

**Fecha:** 8 de junio de 2026  
**Inspector:** Cursor Agent (skill `/inspector-general` — primera ejecución completa)  
**Baseline:** `docs/ESTADO_VIVO.md` · gates `docs/audits/gates_2026-06-08.json`

---

## 1. Resumen ejecutivo

| Eje | Semáforo | Nota breve |
|-----|----------|------------|
| Clínico | 🟡 | P0 REACTIVOS WISC/WAIS + E2E manual WISC→PDF pendientes |
| Seguridad | 🟢 | IDOR corregido jun-2026; JWT + ownership en HC |
| API | 🟢 | **P0 cerrado hoy:** fix `api.blob` GET HC + consentimientos; 0 METHOD_MISMATCH |
| Arquitectura V2 | 🟡 | Strict modules limpios; 26 ítems legacy debt |
| Normativa CO | 🟡 | RIPS/CIE-11 OK; OTP Ley 527 y tele-consent P1 |
| UX / Producto | 🟢 | S0–S8 cerrados; Aprender P2 operativo |
| Build / CI | 🟢 | **1036 pytest** · ESLint 0 errors · gates OK |

**Veredicto:** Sistema **listo para beta controlada** tras checklist E2E manual y sync Pearson local; beta amplia bloqueada por reactivos visuales y validación clínica.

---

## 2. Gates automáticos

Fuente: `docs/audits/gates_2026-06-08.json`

| Gate | Estado | Detalle |
|------|--------|---------|
| pytest | ✅ | 1036 passed, 3 skipped (~57s) |
| eslint | ✅ | 0 errors, 42 warnings legacy |
| v2_guards | ✅ | Strict `therapy.py` + `appointments.py` clean; 26 WARN legacy |
| api_manifest | ✅ | 221 rutas BE / 139 llamadas FE; 0 critical new |

**Acción ejecutada en esta sesión:** corrección P0 `api.blob(..., "GET")` en `ClinicalHistoryPage.jsx` y `ConsentModal.jsx`; baseline actualizado.

---

## 3. Reconciliación de auditorías previas

| ID | Hallazgo (fuente) | Estado | Evidencia |
|----|-------------------|--------|-----------|
| C1 | IDOR HC (`AUDIT_2026-06-05`) | ✅ Resuelto | `get_patient_for_user` en `clinical_history.py` |
| A2 | OTP Ley 527 consentimiento | ❌ Abierto P1 | Solo `firma_base64` + email |
| A3 | RIPS CIE-10 only | ✅ Correcto | Norma vigente |
| FULL-P0-4 | Módulo validez medicolegal | ✅ Resuelto | `validez.py` + tests integration |
| API-1 | `api.blob` GET HC PDF | ✅ **Resuelto 8 jun** | `ClinicalHistoryPage.jsx` |
| API-2 | `api.blob` GET consent PDF | ✅ **Resuelto 8 jun** | `ConsentModal.jsx` abrirPdf |
| API-3 | Firma evaluación sin UI | ❌ Abierto P1 | BE + tests; sin FE |
| Therapy | `therapy_plan_id` en closure | ❌ Abierto P1 | BE acepta param; FE no envía |
| QW-5 | Compartir con PIN SMS | ⚠️ Parcial | Link + password |
| P0 Reactivos | WISC/WAIS láminas PNG | ❌ Abierto P0 | `REACTIVOS_WISC_WAIS_PLAN.md` |
| P0 E2E | paciente→WISC→PDF pro | ❌ Abierto P0 | Checklist `PUNTO_INFLEXION` §17 |

---

## 4. Hallazgos nuevos

### Críticos

_Ninguno tras fix P0 API (8 jun 2026)._

### Altos

| ID | Archivo | Problema | Sugerencia |
|----|---------|----------|------------|
| A-V2-1 | `PanelIA.jsx` (1265 L) | Monolito FE máximo | Extraer hooks/sub-componentes |
| A-V2-2 | `emails.py` (20 db hits) | DB directo en route | Migrar a repository |
| A-API-1 | `EvalResultsPage.jsx` | Sin UI firma evaluación | Cablear POST `/sign` + badge |
| A-CL-1 | `reactivosPearson.generated.js` | Stub vacío en OSS | Sync local con licencia |

### Medios

- `advanced.py` (679 L, 15 db hits) — deuda V2
- `rehab_use_cases.py` (1307 L) — particionar
- RIPS preflight limitado a 100 pacientes
- Mapeo CIE-10↔11 parcial (~22 códigos)
- Consentimiento telepsicología no obligatorio por modalidad

---

## 5. Subagentes — síntesis

### API Alignment

- 0 `MISSING_BACKEND`; 0 `METHOD_MISMATCH` post-fix
- 109 `ORPHAN_BACKEND` (mayoría admin/IA vía `fetch`, no `api.*`)
- P1: UI firma evaluación; selector `therapy_plan_id` para informe cierre

### Architecture V2

- Strict modules PASS; 14 páginas FE >300 L; 24 routes >150 L
- Prioridad refactor: `PanelIA.jsx`, `emails.py`/`advanced.py`, `rehab_use_cases.py`

### Normativa Colombia

- RIPS Res. 2275 operativo (CIE-10); CIE-11 complementario en HC
- Ley 1581 consentimientos con PDF/email; sin OTP Ley 527
- P2: FHIR/Res. 1888, portal ARCO, RIPS XML E2E

### Fidelidad clínica

- Verbal WISC/WAIS Fase 1 ✅; visuales cuadernillo parcial
- Validez PDF: 8 tests (unit + integration) ✅
- Sin Playwright paciente→WISC→PDF Pro

---

## 6. Backlog unificado

### P0 — antes de beta amplia

- [ ] Sprint REACTIVOS WISC/WAIS — láminas PNG Pearson (`docs/REACTIVOS_WISC_WAIS_PLAN.md`)
- [ ] E2E manual: paciente → WISC → PDF pro (`PUNTO_INFLEXION` §17)
- [x] Fix `api.blob` GET en HC y consentimientos — **hecho 8 jun 2026**

### P1 — calidad post-beta

- [ ] UI firma evaluación (`POST /evaluations/detail/{id}/sign`)
- [ ] `therapy_plan_id` en informe `therapy_closure`
- [ ] Tests HTTP therapy + agenda (más allá de DTO test)
- [ ] OTP consentimiento Ley 527
- [ ] Refactor `PanelIA.jsx` + `emails.py` (V2)

### P2 — visión 12 meses

- [ ] HL7 FHIR / Res. 1888 IHCE
- [ ] RIPS XML automático + E2E billing→RIPS
- [ ] FIT SRS/ORS módulo terapia
- [ ] Portal paciente PWA
- [ ] Conners 4 / BANFE-2 / ADOS-2 (gates licencia)

---

## 7. Recomendaciones de elevación

### Competitivo / producto

1. Cerrar flujo E2E clínico documentado antes de comparar con TheraNest/SimplePractice
2. FIT SRS/ORS en terapia — diferenciador outcome measurement Colombia
3. Portal paciente PWA para tareas terapéuticas y consentimientos

### Normativo / legal

1. OTP o proveedor firma electrónica para consentimientos institucionales
2. Completar tabla CIE-10↔11 antes transición 2027
3. Dictamen INVIMA antes de posicionamiento SaMD

### Arquitectura / técnico

1. Bajar umbral `check_v2_guards` de 400→300 L alineado con CONVENCIONES
2. Playwright spec `wisc-to-pdf-pro.spec.js` en CI
3. Expandir `api_manifest_check` para detectar `fetch(${API}/...)`

### Clínico / baremos

1. Sync Pearson en build licenciado (no stub OSS vacío)
2. Playwright + ground-truth para Semejanzas verbatim en UI
3. Automatizar índices CVLT/Grober en informe medicolegal

---

## 8. Próxima ejecución

| Cuándo | Acción |
|--------|--------|
| Antes del próximo build beta | `/inspector-general` completo |
| Tras cerrar P0 reactivos | `clinical-fidelity-reviewer` |
| Si toca `client.js` o API | `api-alignment-reviewer` |
| Al cerrar items P0/P1 | `/actualizar-estado-vivo` |

---

*Generado por Inspector General · Infraestructura en `.claude/skills/inspector-general/` · No sustituye revisión humana clínica.*
