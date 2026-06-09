# Estado vivo — NeuroSoft App
**Última actualización:** 9 de junio de 2026 (Sprint REACTIVOS láminas ejemplo + tests) 
**Fuente de verdad** para saber qué está hecho vs qué falta. 
**Regla IA:** al cerrar sprint/roadmap → skill `/actualizar-estado-vivo`. Sync contexto completo solo con `/actualizar-contexto-ia`.

---

## Métricas actuales (verificadas)

| Métrica | Valor |
|---|---|
| Tests pytest | **1052 passed** (3 skipped) |
| ESLint frontend | **0 errors** · 42 warnings legacy (`npm run lint`) |
| Baremos | 173 pruebas, ~114.586 claves (`BD_NEURO_MAESTRA.json`) |
| Build exe | **~48 MB** · Setup ~1.3 GB · LicenseAdmin exe |
| Bundle index | **~337 KB** (gzip ~100 KB) · lazy routes React 19 |
| Stack | FastAPI 0.136 · React 19 · Vite 6 · Pydantic 2.10 |
| CI workflows | `.github/workflows/backend-ci.yml`, `frontend-ci.yml` |
| GitHub OSS | https://github.com/mrhyde42098/NeuroSoft · Codex OSS enviado |

---

## Sprints cerrados

| Sprint | Tema | Doc |
|---|---|---|
| V0 | Sanitización de referencias comerciales en código | `docs/historico/sprints/AUDITORIA_PDFs.md` §V0 |
| V1–V3 | PDF charts + estímulos + gráficas | `docs/AUDITORIA_PDFs.md` |
| V4 | REACTIVOS WISC/WAIS fidelidad | idem |
| V5 | Validación edad, typos BD | idem |
| V6 | Hotfix `cfg.scoring` ReactivePanel | `docs/PUNTO_INFLEXION_2026-06-05.md` |
| Audit 5 jun | IDOR fixes, advertencias motor | `docs/historico/audits/AUDIT_2026-06-05.md` |
| PLAN_MAESTRO UI | Dashboard, pacientes, agenda, eval, RIPS, DS editorial | `PLAN_MAESTRO_DESARROLLO.md` |

### PLAN_MAESTRO_DESARROLLO — estado (5 jun 2026)

| Sprint | Tema | Estado |
|---|---|---|
| S0 | Sistema diseño (StatTile, SectionCard, tokens) | ✅ |
| S1 | Dashboard 3 zonas + Estadísticas + sidebar | ✅ |
| S2 | Register vía_atención + HC CIE-11 dual + HC 4 pasos (screening aparte) | ✅ |
| S3 | Agenda EPS/CUPS/autorización | ✅ |
| S4 | EvalApply FloatingTimer/SegmentedNav/portada | ✅ |
| S5 | Screening dedup + layout vertical 2 cols | ✅ |
| S6 | RipsPage preflight + export | ✅ |
| S7 | Terapia Meet/Zoom SOAP + PanelIA pulls | ✅ |
| S8 | AprenderHub tabs + Config pruebas embebidas | ✅ |
| CONS | Consentimiento PDF + email SMTP + firma digital | ✅ (OTP SMS opcional P2) |
| OSS | Repo público, CONTRIBUTING, issues, sin material de capacitación en git | ✅ |
| PDF Pro | Resumen para la Familia en variante `pro` | ✅ (6 jun 2026) |

---

## Roadmap QW (Quick Wins) — `docs/planning/ROADMAP_2026.md`

| ID | Feature | Estado |
|---|---|---|
| QW-1 | Informes: imprimir, email, guardar como | ✅ |
| QW-2 | Config SMTP UI + Fernet | ✅ |
| QW-3 | Plantillas email editables | ✅ |
| QW-4 | PDF HC sola | ✅ |
| QW-5 | Compartir con PIN | ⚠️ Parcial (share link + password, no PIN 6 dígitos SMS) |
| QW-6 | Etiquetas pacientes | ✅ (PatientsPage + PATCH + migración 010) |
| QW-7 | Recordatorios citas 18:00 | ✅ |
| QW-8 | Backup automático configurable | ✅ (BackupTab + schedule API + migración 011) |

---

## Roadmap M (Medio plazo)

| ID | Feature | Estado |
|---|---|---|
| M-1 | Módulo terapias enriquecido (18 enfoques) | ✅ |
| M-2 | Aprender (glosario 120, rutas, API, biblioteca fav) | ✅ P2 cerrado 6 jun |
| M-3 | C-SSRS riesgo suicida | ✅ |
| M-4 | Telepsicología Jitsi | ✅ |
| M-5 | Completitud informe + bloqueo descarga | ✅ |
| M-6 | Orden clínico evaluación + timer Grober | ✅ |
| M-7 | Acompañantes entidad | ✅ |
| M-8 | Bandeja escalas sugeridas | ✅ |

---

## Sub-sprints N / P (mayo–jun 2026)

| ID | Feature | Estado |
|---|---|---|
| N1 | Simulador casos clínicos | ✅ |
| N2 | Glosario tooltips InformesPage | ✅ (`GlossaryLegend` en preview infantil) |
| N3 | Tests GADS-CTAs / NiCDI | ✅ |
| P1 | aprenderContent expandido | ✅ (parcial vs meta 80 términos) |
| P2 | Ground truth 15 fixtures CI | ✅ |
| P3 | Telepsicología | ✅ |
| P4 | GlossaryTerm component | ✅ |
| P5 | Cleanup duplicados motor | ✅ |

---

## Pendiente real (priorizado)

### P0 — antes de beta amplia
- [x] **Sprint REACTIVOS WISC/WAIS** — verbal ✅ · láminas ejemplo en SQLite (170 ítems: Matrices, Conceptos, FigInc, Voc 1-4, AdMatr, AdWAISFI, AdWAISCC cubos) · `seed_pearson_ejemplo_laminas.py`
- [ ] Sustituir láminas ejemplo por escaneo cuadernillo Pearson (`map_pearson_visual_stimuli.py --wisc-pdf ...`)
- [ ] E2E manual UI: paciente → WISC → PDF pro (checklist `PUNTO_INFLEXION` §17; API automatizada ✅ + test estimulos NiWiscMat)

### Hecho reciente (8 jun 2026 — Inspector General ejecución + P1)
- [x] **Infraestructura** `/inspector-general` + gates CI + informe `docs/audits/INFORME_MAESTRO_2026-06-08.md`
- [x] **P0 API:** `api.blob` GET en HC PDF y consentimientos
- [x] **P1 UI firma evaluación** — `EvalResultsPage` POST sign + badge integridad
- [x] **P1 therapy_closure** — selector `therapy_plan_id` en `EvalResultsPage` + `InformesPage`
- [x] **P1 tests HTTP** — `test_therapy_agenda_http.py`, `test_consent_tele.py`
- [x] **P1 RIPS** — preflight sin límite 100 pacientes + `numero_factura` / `codigo_prestador`
- [x] **P1 tele-consent** — `telepsicologia` obligatorio si `via_atencion` o cita/sesión tele
- [x] **E2E API** — `e2e/wisc-pdf-pro.spec.js` en CI (`clinical-api` project)

### Hecho reciente (7 jun 2026 — alineación API frontend↔backend)
- [x] **Therapy sessions:** `TherapySessionUpdateDTO` + PATCH UI incluyen `modalidad` y `duracion_min`
- [x] **Backup QW-8:** router legado `/backup/` eliminado; `POST` único con body `BackupRequestDTO` (notas en JSON)
- [x] **Agenda:** vista mes usa `GET /agenda/?fecha_desde&fecha_hasta`; citas asignan `profesional_id` del JWT al crear
- [x] **Tests:** `tests/integration/test_api_alignment_jun2026.py`
- [x] **Build 2.0.1:** frontend OK · `NeuroSoft.exe` 11.6 MB (onedir) · Setup 29.9 MB · manual PDF · ZIP/nsupdate v2.0.1

### Hecho reciente (7 jun 2026 — entrega beta lista)
- [x] **Build completo:** frontend + baremos shards + exe onedir + manual PDF + Setup 1.36 GB (con Ollama)
- [x] **Manual beta PDF** pulido (14 páginas, sin desborde pág. 2–3, credenciales genéricas)
- [x] **Fix instalador:** empaqueta `dist/NeuroSoft/` onedir (no onefile legacy)
- [x] **LicenseAdmin** regenerado (`NeuroSoft-LicenseAdmin.exe` 15.6 MB)
- [x] **1034 tests** pytest · ESLint 0 errors · `update.json` + `.nsupdate` + ZIP onedir

### Hecho reciente (7 jun 2026 — Integración Inspector General)
- [x] **1034 tests pytest** en verde; fix flaky `test_backup.py` (aislamiento `_directorio_backups`)
- [x] **ESLint 0 errors:** `RegisterPage` (`setValues`, `useCupsPsicologia`), `RehabPlanTab` (`safeLS`)
- [x] **QW-6/QW-8** verificados end-to-end: etiquetas paciente + backup programado (API + BackupTab)
- [x] **Reactivos visuales Fase 1:** Matrices/Conceptos en `clinical.js` + `ReactivePanel` + sync Pearson
- [x] **InformesPage:** `GlossaryLegend` con 120 términos en preview pediátrico
- [x] **Build certificado:** `NeuroSoft.exe` 47.6 MB · `NeuroSoft-Setup.exe` 1.3 GB · bundle 337 KB
- [x] **PDF Pro:** 31 tests reports/enrichment pasando; Resumen Familia sin regresión

### Hecho reciente (6 jun 2026)
- [x] **Centro Aprender P2:** 120 términos glosario, 11 artículos, 4 rutas guiadas, favoritos biblioteca, API `/api/v1/aprender/`
- [x] **Centro Aprender P0/P1:** 6 quizzes, 11 casos simulador, 6 protocolos, `ProtocolosPage`, hub con progreso
- [x] **Build automático:** `build.py` regenera shards + PDF + Inno Setup sin pasos manuales
- [x] **Post-upgrade:** OpenAPI tests, `Annotated` auth, lazy routes React 19, bundle ~336 KB
- [x] FastAPI 0.136 + React 19 + Vite 6 + baremos shards por población
- [x] Acuerdo legal v2.0.0 (una vez por PC; skip admin/master)
- [x] `admin_license_app.py` + `NeuroSoft-LicenseAdmin.exe`
- [x] Manual beta PDF regenerado con sección Aprender (genérico, sin credenciales personales)
- [x] Terapias: botón Cerrar en vista previa catálogo

### Hecho reciente (9 jun 2026 — láminas Pearson ejemplo)
- [x] `seed_pearson_ejemplo_laminas.py` — 170 láminas + manifest depurado
- [x] `map_pearson_visual_stimuli.py` — pipeline cuadernillo escaneado
- [x] Tests `test_estimulos_pearson.py` (6) + E2E API láminas en `wisc-pdf-pro.spec.js`
- [x] ReactivePanel: label `imagen`, guía `guia`, hint vocab ilustrado

### P1 — calidad clínica/UX
- [ ] Consentimiento OTP SMS (opcional; email+PDF ya implementado)
- [ ] Láminas PNG definitivas del cuadernillo físico (reemplazar tarjetas ejemplo)
- [x] Firma evaluación UI + tests HTTP sign/signature (8 jun 2026)
- [x] Informe `therapy_closure` con selector de plan (8 jun 2026)

### P2 — largo plazo (no urgente)
- [ ] HL7 FHIR / Res. 1888 IHCE (solo si integración EPS)
- [ ] RIPS XML automático
- [ ] Multi-profesional granular
- [ ] App móvil paciente PWA

---

## Documentos que NO tocar (histórico)

Los roadmaps en `docs/planning/` son **planes originales** — no borrar. 
El estado real está **aquí** (`ESTADO_VIVO.md`), no en los roadmaps viejos.

Auditorías archivadas: `docs/historico/audits/`
