# Inspector General — Matriz de reconciliación

Checklist para Fase 3. Marcar cada fila: ✅ Resuelto · ❌ Abierto · ⚠️ Regresión

## Auditoría 2026-06-05 (seguridad + motor)

| ID | Hallazgo | Archivo clave | Verificación |
|----|----------|---------------|--------------|
| C1 | IDOR historia clínica | `clinical_history.py` | `get_patient_for_user` en GET/PATCH |
| C2 | Baremos monolítico sin versionado | `BD_NEURO_MAESTRA.json` | Política: no modificar sin aprobación |
| A1 | `except Exception` amplio en API | `emails.py`, `main.py` | Grep + log estructurado |
| A2 | Consentimiento sin OTP Ley 527 | `consentimientos.py` | Solo firma_base64 + email |
| A3 | RIPS export CIE-10 only | `rips_service.py` | Correcto por norma vigente |
| A4 | TOMM sin estímulos por ítem | `clinical.js`, `ReactivePanel` | Protocolo validez + ItemStimulus |
| A5 | Test backup flaky | `test_backup.py` | pytest aislado |

## Auditoría 2026-06-06 FULL (7 capas)

| ID | Hallazgo | Verificación |
|----|----------|--------------|
| FULL-P0-1 | Estímulos PDF + UI | `ItemStimulus.jsx`, `data/stimuli_assets/` |
| FULL-P0-2 | IFS Colombia corte 17.5 | `clinical.js` screening |
| FULL-P0-3 | CIE-11 complementario HC | `ClinicalHistoryPage` picker dual |
| FULL-P0-4 | Módulo validez medicolegal | `report_pro/validez.py`, template medicolegal |
| FULL-P1-1 | OTP consentimiento | Pendiente P1 |
| FULL-P1-2 | FIT SRS/ORS terapia | Pendiente P1 |
| FULL-P2-1 | Conners 4 / BANFE-2 / ADOS-2 | Gate licencia |

## Alineación API jun-2026 (fixes verificados)

| Item | Estado esperado | Evidencia |
|------|-----------------|-----------|
| Therapy PATCH `modalidad`/`duracion_min` | ✅ | `TherapySessionUpdateDTO`, `SesionSOAPForm.jsx` |
| Backup POST único con body JSON | ✅ | `backup_router_new`, sin router legado |
| Agenda mes `fecha_desde`/`fecha_hasta` | ✅ | `AgendaPage.jsx` |
| Citas `profesional_id` desde JWT | ✅ | `appointments.py` create |

## Gaps API conocidos

| Ruta | Estado | Nota |
|------|--------|------|
| `/api/v1/clinical-history/{id}/pdf` | ✅ Resuelto 8 jun 2026 | `api.blob(..., "GET")` |
| `/api/v1/consentimientos/{id}/pdf` | ✅ Resuelto 8 jun 2026 | `abrirPdf` → GET |
| `/api/v1/evaluations/detail/{id}/sign` | ❌ P1 | Backend sin UI |

## P0 beta — checklist fijo

- [ ] Sprint REACTIVOS WISC/WAIS — `docs/REACTIVOS_WISC_WAIS_PLAN.md`
- [ ] E2E manual paciente → WISC → PDF pro — `PUNTO_INFLEXION` §17
- [x] Fix `api.blob` GET en HC y consentimientos (8 jun 2026)

## P1 calidad — checklist fijo

- [x] UI firma evaluación (`/evaluations/detail/{id}/sign`) — 8 jun 2026
- [x] `therapy_plan_id` en informe `therapy_closure` — 8 jun 2026
- [x] Tests HTTP therapy + agenda — 8 jun 2026
- [ ] OTP consentimiento Ley 527

## P2 visión 12 meses — checklist fijo

- [ ] HL7 FHIR / Res. 1888 IHCE
- [ ] RIPS XML automático + E2E billing→RIPS
- [ ] FIT SRS/ORS módulo terapia
- [ ] Portal paciente PWA
- [ ] Conners 4, BANFE-2, ADOS-2 (gates licencia)

## Fuentes de auditoría (grep paths)

```text
docs/historico/audits/AUDIT_2026-06-05.md      ← referencia principal
docs/historico/audits/AUDIT_2026-06-06_FULL.md ← backlog P0-P2
docs/AUDITORIA_PDFs.md                         ← sprint PDF V1-V5
docs/AUDITORIA_DE_AUDITORIAS_2026-06-05.md     ← meta-auditoría docs
```

## Subagentes — delegación

| Fase | Subagente | Cuándo omitir |
|------|-----------|---------------|
| 2 | api-alignment-reviewer | Nunca en auditoría completa |
| 2 | architecture-v2-reviewer | Nunca en auditoría completa |
| 2 | normativa-colombia-reviewer | Solo si `/inspector-general api` |
| 2 | clinical-fidelity-reviewer | Si no hubo cambios clínicos recientes |
| 2 | clinical-engine-reviewer | Solo si motor tocado en git log |
