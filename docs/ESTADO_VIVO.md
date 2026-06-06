# Estado vivo — NeuroSoft App
**Última actualización:** 5 de junio de 2026 (PLAN_MAESTRO UI sprint)  
**Fuente de verdad** para saber qué está hecho vs qué falta.  
**Regla IA:** al cerrar sprint/roadmap → skill `/actualizar-estado-vivo`. Sync contexto completo solo con `/actualizar-contexto-ia`.

---

## Métricas actuales (verificadas)

| Métrica | Valor |
|---|---|
| Tests pytest | **1011 passed** (1 flaky backup no relacionado) |
| ESLint frontend | 0 warnings (`npm run lint`) |
| Baremos | 173 pruebas, ~114.586 claves (`BD_NEURO_MAESTRA.json`) |
| Build exe | ~47 MB · Setup ~1.4 GB (regenerado 5 jun 2026 post-PLAN_MAESTRO) |
| CI workflows | `.github/workflows/backend-ci.yml`, `frontend-ci.yml` |

---

## Sprints cerrados

| Sprint | Tema | Doc |
|---|---|---|
| V0 | Sanitización IN&S en código | `docs/historico/sprints/AUDITORIA_PDFs.md` §V0 |
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
| S2 | Register vía_atención + HC CIE-11 dual + wizard 7 pasos | ✅ |
| S3 | Agenda EPS/CUPS/autorización | ✅ |
| S4 | EvalApply FloatingTimer/SegmentedNav/portada | ✅ |
| S5 | Screening dedup + layout vertical 2 cols | ✅ |
| S6 | RipsPage preflight + export | ✅ |
| S7 | Terapia Meet/Zoom SOAP + PanelIA pulls | ✅ |
| S8 | AprenderHub tabs + Config pruebas embebidas | ✅ |
| CONS | Consentimiento PDF + email SMTP + firma digital | ✅ (OTP SMS opcional P2) |

---

## Roadmap QW (Quick Wins) — `docs/planning/ROADMAP_2026.md`

| ID | Feature | Estado |
|---|---|---|
| QW-1 | Informes: imprimir, email, guardar como | ✅ |
| QW-2 | Config SMTP UI + Fernet | ✅ |
| QW-3 | Plantillas email editables | ✅ |
| QW-4 | PDF HC sola | ✅ |
| QW-5 | Compartir con PIN | ⚠️ Parcial (share link + password, no PIN 6 dígitos SMS) |
| QW-6 | Etiquetas pacientes | ❌ Pendiente |
| QW-7 | Recordatorios citas 18:00 | ✅ |
| QW-8 | Backup automático configurable | ⚠️ Parcial (BackupTab existe, sin schedule UI) |

---

## Roadmap M (Medio plazo)

| ID | Feature | Estado |
|---|---|---|
| M-1 | Módulo terapias enriquecido (18 enfoques) | ✅ |
| M-2 | Aprender (glosario, estudiar, quiz, simulador) | ✅ |
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
| N2 | Glosario tooltips InformesPage | ⚠️ EvalResultsPage sí; InformesPage parcial |
| N3 | Tests GADS-CTAs / NiCDI | ✅ |
| P1 | aprenderContent expandido | ✅ (parcial vs meta 80 términos) |
| P2 | Ground truth 15 fixtures CI | ✅ |
| P3 | Telepsicología | ✅ |
| P4 | GlossaryTerm component | ✅ |
| P5 | Cleanup duplicados motor | ✅ |

---

## Pendiente real (priorizado)

### P0 — antes de beta amplia
- [ ] **Sprint REACTIVOS WISC/WAIS** — ver `docs/REACTIVOS_WISC_WAIS_PLAN.md` (16 placeholders + Sem/Voc desalineados)
- [ ] E2E manual: paciente → WISC → PDF pro (checklist en `PUNTO_INFLEXION`)
- [ ] Fix test flaky `test_listar_backups_detecta_archivos`
- [ ] Dark mode en `evaluation/` (skill `/dark-mode-fix`)

### P1 — calidad clínica/UX
- [ ] Consentimiento OTP SMS (opcional; email+PDF ya implementado)
- [ ] Placeholders REACTIVOS restantes (Matrices/Conceptos visuales) tras Fase 1 verbal
- [ ] Glosario tooltips en `InformesPage` (extender desde EvalResultsPage)
- [ ] QW-6 etiquetas pacientes
- [ ] QW-8 backup programado

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
