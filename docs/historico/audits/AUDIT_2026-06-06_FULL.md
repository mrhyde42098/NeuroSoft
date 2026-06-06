# Auditoría integral FULL — NeuroSoft App · 6 de junio de 2026

**Entregable:** Informe maestro único (metodología 7 capas).  
**Baseline tests:** 1010 passed, 1 failed (`test_backup.py` — entorno local, no clínico).  
**Cobertura inventariada:** ver `audit_coverage_2026-06-06.json` — **450 archivos / 140 491 líneas** en dominios productivos (backend app, tests, frontend src, docs, protocolos).

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Hallazgos por severidad](#2-hallazgos-por-severidad)
3. [Regresiones vs AUDIT_2026-06-05](#3-regresiones-vs-audit_2026-06-05)
4. [REACTIVOS / protocolos / estímulos](#4-reactivos--protocolos--estímulos)
5. [Motor clínico y baremos](#5-motor-clínico-y-baremos)
6. [Seguridad y multi-tenant](#6-seguridad-y-multi-tenant)
7. [PDF e informes](#7-pdf-e-informes)
8. [Gap clínico verificado](#8-gap-clínico-verificado)
9. [Gap normativo Colombia 2026](#9-gap-normativo-colombia-2026)
10. [Gap técnico](#10-gap-técnico)
11. [Gap UX / producto](#11-gap-ux--producto)
12. [Backlog unificado P0–P2](#12-backlog-unificado-p0p2)

---

## 1. Resumen ejecutivo

| Métrica | Resultado |
|---------|-----------|
| Archivos productivos inventariados | 450 |
| Líneas revisadas (dominios clave) | ~140k |
| pytest | **1010 OK**, 1 fallo backup |
| ESLint frontend | Pendiente en build (`npm run build`) |
| IDOR HC | **Corregido** — `get_patient_for_user` en `clinical_history.py` |
| Estímulos PDF | **402 imágenes** extraídas → `data/stimuli_assets/` |
| Implementación sprint | Estímulos por ítem, IFS, cortes CO, CIE-11 ref., validez P0 |

---

## 2. Hallazgos por severidad

### Críticos

| ID | Hallazgo | Archivo | Estado |
|----|----------|---------|--------|
| C1 | ~~IDOR historia clínica sin ownership~~ | `clinical_history.py` | **Resuelto** — líneas 88-102 usan `CurrentUser` + `get_patient_for_user` |
| C2 | Baremos en JSON monolítico sin versionado por edición | `BD_NEURO_MAESTRA.json` | Abierto — no modificado en este sprint (política usuario) |

### Altos

| ID | Hallazgo | Archivo | Recomendación |
|----|----------|---------|---------------|
| A1 | `except Exception` amplio en rutas API | `emails.py`, `main.py`, `evaluations.py` | Loggear + re-lanzar o HTTP 500 estructurado |
| A2 | Consentimiento solo `firma_base64` (sin OTP Ley 527) | `consentimientos.py` | P1 — OTP + auditoría |
| A3 | RIPS export solo CIE-10 | `rips_service.py:59` | Correcto por norma vigente; CIE-11 no enviar hasta circular MinSalud |
| A4 | TOMM sin estímulos visuales por ítem en captura | `clinical.js` + UI | Parcialmente resuelto — protocolo validez + extracción PDF |
| A5 | Test backup flaky en CI local | `test_backup.py` | Revisar rutas temporales Windows |

### Medios

| ID | Hallazgo | Notas |
|----|----------|-------|
| M1 | PHQ-9 corte internacional 10 por defecto en comentarios | **Resuelto** — selector AP Colombia ≥7 |
| M2 | MoCA corte único 26 | **Resuelto** — perfiles Pineros 2018 en screening |
| M3 | ACE-III corte 82 internacional | **Resuelto** — perfil Colombia 87 por defecto |
| M4 | `AdBusSim + ViBusSim` en INSTRUCCIONES | Inconsistencia cosmética `clinical.js` |
| M5 | 402 PNG de estímulos no deben ir a git remoto completo | `.gitignore` recomendado para `stimuli_assets/**/*.png` |

### Bajos

| ID | Hallazgo |
|----|----------|
| B1 | Falta E2E Playwright en esta pasada |
| B2 | Conners 4 / BANFE-2 / ADOS-2 — solo backlog con gate licencia |

---

## 3. Regresiones vs AUDIT_2026-06-05

| Bug histórico | Estado jun-06 |
|---------------|---------------|
| IDOR HC | Corregido |
| WISC/WAIS placeholders | Corregido (commit `c28e78a`) |
| FCRO patrones | OK |
| cfg.scoring undefined | OK |
| IN&S en nombres protocolo | Limpiado en sync; scripts docs aún mencionan IN&S |
| Estímulos por ítem | **Nuevo** — ItemStimulus + PresentationOverlay |

---

## 4. REACTIVOS / protocolos / estímulos

- Inventario: [`docs/stimuli/STIMULI_INVENTORY.md`](../../stimuli/STIMULI_INVENTORY.md)
- Scripts: `extract_stimuli_from_pdfs.py`, `seed_estimulos_from_manifest.py`
- UI: `ItemStimulus.jsx`, `PresentationOverlay.jsx`, integración `ReactivePanel.jsx`
- API existente: `/api/v1/estimulos/por_test/{test_id}` con `item_id`
- Manifest: 402 entradas desde PDFs en `Capacitaciones Clínicas/drive-download-...`

---

## 5. Motor clínico y baremos

- `engine.py` / `strategies.py` — sin cambios en este sprint
- 1010 tests motor + integración pasan
- Grober discriminabilidad en `grober_buschke.py` — usable para flags validez CVLT (P1 automatizar en informe)

---

## 6. Seguridad y multi-tenant

- JWT + `get_patient_for_user` patrón estándar en pacientes y HC
- `ai_logs` + `sanitize_clinical_input` — revisar en despliegue red (no solo desktop)
- Fernet / cifrado — sin regresión detectada en lectura focal

---

## 7. PDF e informes

- Variantes report_pro — ver `docs/AUDITORIA_PDFs.md`
- Codificación dual CIE-11 en texto de impresión diagnóstica (frontend) — **implementado**
- RIPS PDF sigue CIE-10 en `codigo_dx`

---

## 8. Gap clínico verificado

| Prueba / tema | En NeuroSoft | Acción sprint |
|---------------|--------------|---------------|
| ACE-III | `ACE3` screening | Cortes CO 87 |
| IFS Colombia | No existía | **Añadido** corte 17.5 |
| TOMM / Rey15 | `clinical.js` | Protocolo `validez` + panel Slick |
| PHQ-9 CO | PHQ9 | Corte AP ≥7 |
| MoCA escolaridad | MoCA | Perfiles Pineros |
| HVLT-R | Protocolos JSON | P1 motor completo |
| Conners 4 | Conners-3 abr. | P2 + licencia MHS |

---

## 9. Gap normativo Colombia 2026

| Norma | Impacto NeuroSoft | Decisión |
|-------|-------------------|----------|
| Res. 1442/2024 + 1657/2025 CIE-11 | Transición ~ago 2027 | CIE-11 **complementario** en HC/informe |
| RIPS | CIE-10 obligatorio hoy | **No** cambiar export |
| Ley 527 consentimiento | OTP pendiente | P1 |
| Res. 2654 telepsicología | Jitsi OK; consent específico | P1 |
| Ley 1581 | Habeas data — consent separado parcial | P2 panel paciente |

---

## 10. Gap técnico

| Área | Versión actual | Nota |
|------|----------------|------|
| FastAPI | 0.115.0 | Estable; evaluar 0.116+ en sprint deps |
| Pydantic | 2.7.0 | OK |
| React | 18.2 | OK — no migrar 19 sin plan |
| Vite | 5.0.8 | OK |
| SQLite | SQLAlchemy 2.0 | WAL — verificar en `engine.py` P1 |
| Observabilidad | logs básicos | Sentry/OTel P2 desktop |

---

## 11. Gap UX / producto

- Fortalezas: evaluación ítem a ítem, 7 PDFs, Aprender, screening data-driven, Ollama offline
- vs SimplePractice/TheraNest: facturación US — NeuroSoft tiene RIPS CO
- Pendiente: FIT SRS/ORS (P1), portal paciente (P2), onboarding joyride (P2)

---

## 12. Backlog unificado P0–P2

### P0 (implementado en este sprint)

1. Estímulos PDF + UI miniatura/fullscreen  
2. IFS Colombia + cortes ACE/MoCA/PHQ  
3. CIE-11 complementario en picker  
4. Módulo validez (Slick + protocolo REY15/TOMM)  
5. Auditoría FULL (este documento)

### P1

- OTP consentimiento Ley 527  
- FIT SRS/ORS terapia  
- Seed automático estímulos en instalador  
- Mapeo CIE-10↔11 completo OMS en JSON  
- CVLT índices simulación en informe medicolegal  

### P2

- Conners 4, BANFE-2, ADOS-2 (licencias)  
- HVLT-R/BVMT-R baremos LATAM  
- INVIMA / FHIR — dictamen legal  

---

*Generado en implementación del plan «Estímulos PDF + auditoría integral». No sustituye revisión humana línea a línea de los 33k archivos del árbol completo del repo (incl. node_modules excluidos).*
