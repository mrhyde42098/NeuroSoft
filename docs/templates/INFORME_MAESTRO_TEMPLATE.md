# Informe Maestro Inspector General — NeuroSoft App

**Fecha:** {{FECHA}}  
**Inspector:** Claude (skill `/inspector-general`)  
**Baseline:** `docs/ESTADO_VIVO.md` · último commit `{{GIT_SHA}}`

---

## 1. Resumen ejecutivo

| Eje | Semáforo | Nota breve |
|-----|----------|------------|
| Clínico | {{SEM_CLINICO}} | |
| Seguridad | {{SEM_SEGURIDAD}} | |
| API | {{SEM_API}} | |
| Arquitectura V2 | {{SEM_ARQ}} | |
| Normativa CO | {{SEM_NORM}} | |
| UX / Producto | {{SEM_UX}} | |
| Build / CI | {{SEM_BUILD}} | |

**Veredicto:** {{VEREDICTO_UNA_LINEA}}

---

## 2. Gates automáticos

Fuente: `docs/audits/gates_{{FECHA}}.json`

| Gate | Estado | Detalle |
|------|--------|---------|
| pytest | {{GATE_PYTEST}} | {{PYTEST_COUNT}} |
| eslint | {{GATE_ESLINT}} | |
| v2_guards | {{GATE_V2}} | |
| api_manifest | {{GATE_API}} | |

---

## 3. Reconciliación de auditorías previas

| ID | Hallazgo (fuente) | Estado | Evidencia |
|----|-------------------|--------|-----------|
| C1 | IDOR HC (`AUDIT_2026-06-05`) | | |
| A2 | OTP Ley 527 consentimiento | | |
| FULL-P0-1 | Reactivos WISC/WAIS | | |
| API-1 | `api.blob` GET HC PDF | | |
| API-2 | `api.blob` GET consent PDF | | |
| API-3 | Firma evaluación sin UI | | |

_Ver matriz completa en `.claude/skills/inspector-general/reference.md`_

---

## 4. Hallazgos nuevos

### Críticos

| ID | Archivo | Problema | Impacto |
|----|---------|----------|---------|
| | | | |

### Altos

| ID | Archivo | Problema | Sugerencia |
|----|---------|----------|------------|
| | | | |

### Medios / Bajos

_(máx. 10 items)_

---

## 5. Subagentes — síntesis

### API Alignment
{{RESUMEN_API_ALIGNMENT}}

### Architecture V2
{{RESUMEN_ARQ_V2}}

### Normativa Colombia
{{RESUMEN_NORMATIVA}}

### Fidelidad clínica
{{RESUMEN_CLINICO}}

### Audit-completo (código)
{{RESUMEN_AUDIT_COMPLETO}}

---

## 6. Backlog unificado

### P0 — antes de beta amplia

- [ ] Sprint REACTIVOS WISC/WAIS (`docs/REACTIVOS_WISC_WAIS_PLAN.md`)
- [ ] E2E manual: paciente → WISC → PDF pro
- [ ] Fix `api.blob` GET en HC y consentimientos
- [ ] _{{P0_EXTRA}}_

### P1 — calidad post-beta

- [ ] UI firma evaluación (`POST /evaluations/detail/{id}/sign`)
- [ ] `therapy_plan_id` en informe `therapy_closure`
- [ ] Tests HTTP therapy + agenda
- [ ] OTP consentimiento Ley 527
- [ ] _{{P1_EXTRA}}_

### P2 — visión 12 meses

- [ ] HL7 FHIR / Res. 1888 IHCE
- [ ] RIPS XML automático + E2E billing→RIPS
- [ ] FIT SRS/ORS módulo terapia
- [ ] Portal paciente PWA
- [ ] Conners 4 / BANFE-2 / ADOS-2 (gates licencia)
- [ ] _{{P2_EXTRA}}_

---

## 7. Recomendaciones de elevación

### Competitivo / producto
1.

### Normativo / legal
1.

### Arquitectura / técnico
1.

### Clínico / baremos
1.

---

## 8. Próxima ejecución

| Cuándo | Acción |
|--------|--------|
| Antes del próximo build beta | `/inspector-general` completo |
| Si toca motor clínico | `clinical-engine-reviewer` |
| Si toca solo un módulo | `/audit-completo <archivo>` |
| Al cerrar items P0/P1 | `/actualizar-estado-vivo` |

---

*Generado por Inspector General. No sustituye revisión humana ni validación clínica con pacientes reales.*
