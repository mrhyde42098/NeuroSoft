# Punto de inflexión — NeuroSoft App
## Informe de traspaso para continuidad en otra sesión de IA

**Fecha:** 5 de junio de 2026 
**Autor del software:** Johan Sebastián Salgado Sarmiento (propietario único) 
**Sesión origen:** Auditoría integral post-sprint V0–V6 + implementación de fixes + build completo 
**Documentos relacionados:** `AUDIT_2026-06-05.md`, `docs/AUDITORIA_PDFs.md`, `CLAUDE.md`, `docs/ARQUITECTURA.md`

---

## 0. Cómo usar este documento

Este archivo es el **punto de inflexión** entre dos chats de IA. Léelo completo antes de tocar código. Resume:

1. Qué es NeuroSoft y qué contiene.
2. Qué pidió Johan en esta sesión.
3. Qué se auditó, qué se implementó y qué quedó pendiente.
4. Estado actual verificado (tests, build, artefactos).
5. Reglas inviolables y próximos pasos priorizados.

**No modificar sin aprobación explícita de Johan:**
- `neurosoft-backend/data/BD_NEURO_MAESTRA.json` (valores numéricos de baremos)
- `Capacitaciones Clínicas/protocolos/*.json` (fuente clínica; solo nombres cosméticos ya sanitizados)
- No sugerir migrar a TypeScript, Electron, PostgreSQL, pywebview→Electron, Langchain, etc.

---

## 1. Identidad del proyecto

**NeuroSoft App** es software médico real de evaluación neuropsicológica para profesionales en Colombia. Genera informes clínicos con baremos colombianos. Un error silencioso en un CI puede alterar un diagnóstico — el rigor del motor clínico no es negociable.

| Atributo | Valor |
|---|---|
| Propietario | Johan Sebastián Salgado Sarmiento |
| Idioma UI/docs | Español colombiano neutro |
| Versión visible al usuario | **Ninguna** (producto = "NeuroSoft App") |
| Modo de entrega | Desktop Windows offline-first (pywebview + PyInstaller + Inno Setup) |
| Datos clínicos | SQLite local en `%APPDATA%/NeuroSoft` |
| Baremos | `BD_NEURO_MAESTRA.json` — 173 pruebas, ~114.586 claves (fuente única de verdad) |

### Stack técnico (cerrado — no proponer cambios de plataforma)

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11, FastAPI 0.115, SQLAlchemy 2.0, SQLite, Pydantic 2.7, ReportLab 4.2, pytest, Alembic |
| Frontend | React 18, Vite 5, Tailwind 3, **JSX puro** (no TypeScript), ESLint v9 flat config, Playwright E2E |
| Desktop | PyInstaller → `NeuroSoft.exe` + Inno Setup → `NeuroSoft-Setup.exe` |
| IA opcional | Ollama local / Gemini / Claude / OpenAI — sanitización PHI antes de cloud |

---

## 2. Estructura del monorepo

```
D:\NeuroSoftApp\
├── neurosoft-backend/ FastAPI + motor clínico + PDF + API
│ ├── app/domain/clinical_engine/ ← NÚCLEO (engine, strategies, baremos_loader)
│ ├── app/application/use_cases/ ← Orquestación
│ ├── app/infrastructure/ ← BD, auth, report_pro, scheduler, audit
│ ├── app/presentation/api/v1/ ← ~37 routers REST
│ ├── data/BD_NEURO_MAESTRA.json ← INTOCABLE (valores numéricos)
│ └── tests/ ← 1011 tests pytest
├── neurosoft-frontend/ React SPA
│ ├── src/data/clinical.js ← REACTIVOS, INSTRUCCIONES, CONDUCTAS
│ ├── src/app/evaluation/ ← Flujo de evaluación (núcleo UX)
│ └── dist/ ← Build Vite (generado)
├── installer/NeuroSoft.iss Inno Setup
├── vendor/ollama/OllamaSetup.exe (~1.3 GB, gitignored)
├── dist/ Artefactos de build
├── build.py Pipeline PyInstaller
├── .claude/skills/ Skills del proyecto (/audit-completo, /build-beta-tester, etc.)
└── docs/ Documentación + casos clínicos + este informe
```

---

## 3. Qué pidió Johan en esta sesión

### Fase A — Auditoría integral (prompt extenso)

1. Leer contexto: `CLAUDE.md`, `AUDITORIA_PDFs.md`, ground truth, motor, PDF, REACTIVOS.
2. Auditoría estática backend + frontend + integración + PDF.
3. Tests dinámicos: pytest, ESLint, build (sin E2E manual completo).
4. Verificar 13 bugs históricos de regresión (§5 del prompt).
5. Plan integral en **4 ejes**: clínico, técnico, UX/producto, normativo Colombia 2026.
6. Entregar reporte en formato §7 → generado como `AUDIT_2026-06-05.md`.

### Fase B — Implementación ("Realízalo todo")

Implementar los hallazgos prioritarios del audit (IDOR, advertencias motor, hardening strategies, frontend guards, sanitización de referencias comerciales, etc.).

### Fase C — Build + informe de traspaso (este mensaje)

- **Build completo SIN regeneración de PDFs** (no ejecutar `regenerar_samples_v5.py`).
- Informe punto de inflexión para otra IA.

---

## 4. Historial reciente de sprints (contexto clínico)

| Sprint | Tema | Estado |
|---|---|---|
| V0 | Sanitización referencias comerciales explícitas en código | ✅ |
| V1 | Bugs visuales PDF (charts.py, base.py, strikethrough) | ✅ |
| V2 | Estímulos FCRO + disclaimer Cubos | ✅ |
| V3 | Gráficas rediseñadas (Z, radar, campana, KPI) | ✅ |
| V4 | REACTIVOS WISC/WAIS fidelidad (Sem, Voc, Com, LN, Reg, BNT) | ✅ |
| V5 | Validación edad warning, typos BD, docstring 173 pruebas | ✅ |
| V6 HOTFIX | `cfg.scoring` undefined → crash ReactivePanel | ✅ |

**Informe consolidado V1–V5:** `docs/AUDITORIA_PDFs.md` (23 hallazgos corregidos).

**Caso ground truth:** `docs/casos-clinicos/CASOS_GROUND_TRUTH.md` — 15 casos + 134 escalares en CI (`tests/integration/test_casos_ground_truth.py`).

---

## 5. Funcionalidades del software (mapa completo)

### 5.1 Núcleo clínico — Evaluación neuropsicológica

- **Registro de pacientes** (sociodemografía, escolaridad, EPS, CIE-10).
- **Historia clínica** (4 pestañas + observaciones por dominio cognitivo).
- **Aplicación de batería** por protocolo (infantil / adulto joven / adulto mayor).
- **Captura reactiva** ítem-por-ítem (`ReactivePanel.jsx` + `clinical.js` REACTIVOS).
- **Motor de baremos** (`ClinicalEngine` + 15 strategies) → PE, CI, T, Z, interpretación.
- **Resultados** con perfil Z, discrepancias WISC/WAIS, fortalezas/debiles, advertencias.
- **Informes PDF** — 7 variantes: `estandar`, `pro`, `pediatrico`, `medicolegal`, `junta_medica`, `inconcluso`, `paciente`.
- **Exportación** DOCX, XLSX, comparativo pre–post (RCI).
- **Firma irreversible** de evaluación (hash + trazabilidad Res. 1995).

### 5.2 Tamizaje y escalas

- `screening.js` — PHQ-9, GAD-7, GDS-15, SNAP-IV, MoCA, PCL-5, etc.
- `screeningSugerencias.js` — 14 reglas data-driven (edad + MC → escala sugerida).
- C-SSRS riesgo suicida en módulo terapia.

### 5.3 Terapia y sesiones clínicas

- Planes terapéuticos (CBT, ACT, EMDR + 13 enfoques extendidos).
- Sesiones SOAP, tareas terapéuticas, telepsicología (Jitsi determinístico).
- Módulo académico: `EnfoqueDetalle.jsx` (7 tabs por enfoque).

### 5.4 Módulo "Aprender" (educativo)

- Glosario, spaced repetition (Leitner), quiz, artículos, biblioteca.
- Simulador de casos clínicos con perfiles reales del motor.
- `aprenderContent.js` — 60+ términos, quizzes, artículos.

### 5.5 Rehabilitación cognitiva

- Actividades: CPT, Go/No-Go, memoria, AVD dinero, etc.
- Viewer público de rehab vía link.

### 5.6 Operaciones de consultorio

- Agenda / citas + recordatorios email (APScheduler 18:00).
- SMTP configurable (Fernet), plantillas email editables.
- Backup/restauración, importación admin, KPIs.
- Compartir informes (link público con token + scope + password opcional).
- OTA updates (HMAC), licencia, consentimientos, acompañantes.

### 5.7 IA clínica (opcional, con PHI scrub)

- 6 prompts curados: observación, DSM-5, discrepancia, recomendaciones, narrativa, pediátrico.
- `AIAsistente.jsx` en resultados; log `ai_logs` sin contenido PHI.
- Ollama local para modo offline.

### 5.8 Seguridad y cumplimiento (implementado)

- JWT `verify_exp` explícito, rate limit, security headers.
- Audit log ORM (Res. 1995), token blacklist, PII redactor en logs.
- Ley 1090 / 1581 / 1995 en bloque legal PDF.
- `MODELO_AMENAZAS.md` en `docs/seguridad/`.

---

## 6. Motor clínico — referencia rápida

**Archivos críticos:**
- `engine.py` — orquestador, validación edad, acumulación advertencias
- `strategies.py` — 15 strategies (`rango_puntaje`, `wais_range`, `z_score`, `suma_a_indice`, etc.)
- `baremos_loader.py` — singleton BD_NEURO en memoria
- Sentinel `PD=9999` → `sin_dato`; `out_of_baremo` → advertencia visible

**Comando de verificación:**
```powershell
cd D:\NeuroSoftApp\neurosoft-backend
python -m pytest tests/ -q
```

**Subagente obligatorio** si tocas engine/strategies/baremos: `clinical-engine-reviewer` (27+ tests ground truth).

---

## 7. Frontend — referencia rápida

**Archivos críticos:**
- `src/data/clinical.js` — REACTIVOS (captura), INSTRUCCIONES (guía lateral), CONDUCTAS
- `ReactivePanel.jsx` — captura ítem-por-ítem; hotfix V6: `Array.isArray(cfg.scoring)`
- `PatronFCRO.jsx` / `PatronesCubos.jsx` — estímulos SVG
- `EvalApplyPage.jsx` / `EvalResultsPage.jsx` / `InformesPage.jsx` — flujo principal

**Comandos:**
```powershell
cd D:\NeuroSoftApp\neurosoft-frontend
npm run lint # gate pre-build
npm run build # lint + vite
npm run dev # puerto 5173, API en 8000
```

---

## 8. Qué se hizo en la sesión de auditoría + fixes

### 8.1 Auditoría (`AUDIT_2026-06-05.md`)

- 24 hallazgos nuevos identificados (2 críticos, 8 altos, 9 medios, 5 bajos).
- pytest inicial: **1010/1010 passed**.
- ESLint: **0 warnings**.
- Plan integral 4 ejes documentado.

### 8.2 Implementación realizada (esta sesión)

| Área | Cambio |
|---|---|
| **IDOR seguridad** | `get_patient_for_user` en HC, PDF, evolución, documentos, scoring, observaciones, Grober, reports (PDF/DOCX/XLSX/preview/enrichment), shares |
| **IDOR helper** | `get_evaluation_for_user()` en `auth.py` |
| **Motor clínico** | Advertencias acumulativas (edad + fuera de baremo ya no se pisan) |
| **Strategies** | ComparativoStrategy sin Z=0 falso; BaremoPE lista vacía; PuntajeDobl sin PE=0 default |
| **baremos_loader** | try/except JSON corrupto al startup |
| **JWT blacklist** | fail-closed en `production` |
| **reports.py** | Solo `EvaluationNotFoundError` → 404 |
| **shared.py** | `_safe_json_list` para JSON corrupto en vista pública |
| **PDF** | Tabla pruebas con ≥1 resultado (antes ≥2) |
| **reservorio.py** | `path` solo en dev |
| **Frontend** | ReactivePanel guards `items`/`elements`; AdBusSim/ViBusSim separados en INSTRUCCIONES |
| **Protocolos** | 7 JSON sin "", mojibake `Niños` corregido (frontend + Capacitaciones Clínicas) |
| **Test nuevo** | `test_engine_advertencias.py` — regresión advertencias coexisten |

### 8.3 Bugs históricos §5 — estado post-fix

| Bug | Estado |
|---|---|
| cfg.scoring undefined (V6) | ✅ |
| FCRO 3/8/18 | ✅ |
| PDF doble header / strikethrough | ✅ |
| Rivalidad duplicado | ✅ |
| NiWiscCom 18 / Voc 32 / Sem 23 | ✅ |
| BNT requires_license | ✅ |
| AdBusSim + ViBusSim en REACTIVOS | ✅ |
| AdBusSim + ViBusSim en INSTRUCCIONES | ✅ (separados) |
| marcas comerciales en protocolos JSON | ✅ (nombres sanitizados) |
| Typos BD COMRENSIÓN/ORGNIZACIÓN | ✅ |

---

## 9. Build completo ejecutado (5 jun 2026)

**Sin regeneración de PDFs** (no se ejecutó `regenerar_samples_v5.py` ni `generate_manual_pdf.py`).

| Paso | Resultado |
|---|---|
| `Stop-Process NeuroSoft` | OK |
| `npm run build` (lint + vite) | ✅ built in 18.97s |
| `python -m py_compile app/main.py` | OK |
| `python build.py --skip-frontend --skip-ollama` | ✅ 87.4s |
| Inno Setup `NeuroSoft.iss` | ✅ Successful compile (153s) |

### Artefactos finales

| Archivo | Tamaño | Ruta |
|---|---|---|
| `NeuroSoft.exe` | **47.05 MB** | `D:\NeuroSoftApp\dist\NeuroSoft.exe` |
| `NeuroSoft-Setup.exe` | **1376.79 MB (~1.4 GB)** | `D:\NeuroSoftApp\dist\NeuroSoft-Setup.exe` |

Verificaciones post-build:
- ✅ exe < 100 MB (Ollama NO bundleado dentro del exe)
- ✅ Setup ~1.4 GB (incluye OllamaSetup.exe separado en instalador)

### Tests al cierre de fixes

- **1011 passed** (incluye `test_engine_advertencias.py`)
- 1 flaky: `test_listar_backups_detecta_archivos` (temp del sistema, no relacionado con cambios)

---

## 10. Pendiente / no hecho en esta sesión

| Item | Prioridad | Notas |
|---|---|---|
| Regenerar 17 PDFs muestra | Baja | Johan pidió explícitamente NO hacerlo |
| E2E manual (paciente → WISC → PDF × 7) | Media | Checklist en prompt §6 |
| Dark mode masivo en `evaluation/` | Baja | Skill `/dark-mode-fix` |
| Rate limit `/errors` endpoint | Baja | |
| Fix test backup flaky | Baja | `tests/unit/infrastructure/test_backup.py:44` |
| Glosario tooltips en `InformesPage` | Media | Ya en EvalResultsPage |
| Completar placeholders REACTIVOS (Matrices, Información, etc.) | Media | 16 bloques con `requires_protocol_text:true` |
| GitHub Actions CI en remoto | Media | Workflows existen en `.github/workflows/` |
| FHIR/RDA Res. 1888/2025 | Largo plazo | Solo si integración EPS |

---

## 11. Plan integral 4 ejes (resumen para continuidad)

### Clínico
- **P0:** Mantener baremos congelados; re-validar con `validar_casos.py` ante cualquier cambio motor.
- **P1:** Textos reales en subtests WISC/WAIS pendientes (sin copiar estímulos con copyright Pearson).
- **P2:** Revisar gaps `AUDITORIA_55_TESTS_SOLO_MOTOR.md`.

### Técnico
- **P0:** IDOR cerrado en esta sesión — verificar con tests de integración auth si se expone en red.
- **P1:** CI en GitHub; health check baremos cargados.
- **No:** PostgreSQL, TypeScript, Electron.

### UX / Producto
- **P1:** Guards defensivos ReactivePanel (hecho); extender ErrorBoundary mensajes amigables.
- **P2:** Inspiración NovoPsych (baterías sugeridas — ya existe screeningSugerencias).

### Normativo Colombia 2026
- **P0:** IDOR = Ley 1581 (hecho).
- **P2:** Res. 1888 IHCE/FHIR — relevante solo si integración con EPS.

---

## 12. Comandos de desarrollo diario

```powershell
# Backend
cd D:\NeuroSoftApp\neurosoft-backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Frontend (otra terminal)
cd D:\NeuroSoftApp\neurosoft-frontend
npm run dev

# Tests completos
cd D:\NeuroSoftApp\neurosoft-backend
python -m pytest tests/ -q

# Build completo (sin PDFs)
Stop-Process -Name "NeuroSoft" -Force -ErrorAction SilentlyContinue
cd D:\NeuroSoftApp\neurosoft-frontend; npm run build
cd D:\NeuroSoftApp; python build.py --skip-frontend --skip-ollama
& "C:\Users\DESKTOP\AppData\Local\Programs\Inno Setup 6\ISCC.exe" "D:\NeuroSoftApp\installer\NeuroSoft.iss"
```

---

## 13. Skills y comandos slash del proyecto

| Comando | Uso |
|---|---|
| `/audit-completo` | Auditoría bugs por severidad |
| `/build-beta-tester` | Pipeline empaquetado |
| `/investigar-clinica <tema>` | Papers 2022-2026 Colombia/LATAM |
| `/auditar-baremos <test_id>` | Comparar baremo vs literatura |
| `/checkpoint` | Snapshot git local antes de cambios grandes |
| `/exportar-sesion` | Resumen md para retomar en otro chat |
| `/mejorar-informe-pdf` | Plan rediseño PDF |

Ubicación: `D:\NeuroSoftApp\.claude\skills\`

---

## 14. Restricciones para la próxima IA

### Prohibido sin aprobación
- Modificar valores en `BD_NEURO_MAESTRA.json`
- Sugerir migrar stack (TS, Electron, PostgreSQL, Next.js, Langchain, Workbox)
- Usar placeholders "", "[DEMO]", "Ps. Johan Salgado" como default
- Mostrar versión en UI al usuario
- Mencionar uso de IA al paciente en PDF

### Permitido
- Bugs con archivo:línea exacta
- Refactors con tests
- UX, a11y, dark mode, nuevos tests
- Typos cosméticos en BD (con re-validación ground truth)

---

## 15. Archivos modificados en la sesión de fixes (referencia git)

**Backend:**
- `app/domain/clinical_engine/engine.py`
- `app/domain/clinical_engine/strategies.py`
- `app/domain/clinical_engine/baremos_loader.py`
- `app/presentation/api/v1/auth.py`
- `app/presentation/api/v1/clinical_history.py`
- `app/presentation/api/v1/scores.py`
- `app/presentation/api/v1/reports.py`
- `app/presentation/api/v1/shared.py`
- `app/presentation/api/v1/reservorio.py`
- `app/infrastructure/report_pro/base.py`
- `app/main.py`
- `tests/unit/clinical_engine/test_engine_advertencias.py` (nuevo)

**Frontend:**
- `src/app/evaluation/ReactivePanel.jsx`
- `src/data/clinical.js`
- `src/data/PatronFCRO.jsx`
- `src/data/protocols/*.json` (5 archivos)
- `Capacitaciones Clínicas/protocolos/*.json` (5 archivos)

**Documentación generada:**
- `AUDIT_2026-06-05.md`
- `docs/PUNTO_INFLEXION_2026-06-05.md` (este archivo)

---

## 16. Próximo paso recomendado para Johan

1. **Probar el .exe recién generado:** `D:\NeuroSoftApp\dist\NeuroSoft.exe`
2. **Flujo E2E manual:** crear paciente 12 años → WISC-IV (5 subtests) → resultados → PDF pro
3. **Si todo OK:** distribuir `NeuroSoft-Setup.exe` a beta testers
4. **Si algo falla:** reportar síntoma exacto; el hotfix V6 (`scoring`) y los fixes IDOR están en el build de hoy

---

## Actualizaciones

### 6 jun 2026 — Cierre beta + OSS
- HC 4 pasos; screening/MMSE fuera del wizard. Repo GitHub público; Codex OSS enviado.
- Fix PDF Pro: `Resumen para la Familia` en `base._build_pages`. **1016 tests** OK.
- Build: `dist/NeuroSoft.exe` 47.3 MB · `NeuroSoft-Setup.exe` 1.34 GB.
- Informes: `docs/INFORME_CIERRE_2026-06-06.md`, `ESTADO_VIVO.md` actualizado.

### 6 jun 2026 — UX evaluación + QW-6/QW-8
- Dashboard intro evaluación (sin pantalla en blanco sin paciente).
- Screening: nombres sin duplicar abreviatura. Agenda: alta mínima para cita.
- Videos terapia: embed `youtube-nocookie` + enlace externo. Etiquetas pacientes (migración 010).

---

## 17. Checklist E2E manual — Paciente → WISC → PDF

Ejecutar en build local o `NeuroSoft.exe` antes de cada entrega beta.

| # | Paso | Esperado | ✓ |
|---|---|---|---|
| 1 | Login profesional | Entra al dashboard sin error | ☐ |
| 2 | Registrar paciente ~10 años (o usar existente) | Panel muestra edad/población infantil | ☐ |
| 3 | Evaluación → WISC-IV | Dashboard intro con grilla de subtests (no pantalla vacía) | ☐ |
| 4 | Seleccionar paciente + Comenzar | Abre subtest con reactivos, guía lateral visible (XL) | ☐ |
| 5 | Aplicar ≥5 subtests core (Sem, Voc, Mat, DC, Claves…) | PD guardados; progreso sube | ☐ |
| 6 | Finalizar → Resultados | CI/índices calculados; sin 9999 en core | ☐ |
| 7 | Generar PDF Estándar | Descarga/abre sin error | ☐ |
| 8 | Generar PDF Pro | Gráficas sin superposición; Resumen Familia presente | ☐ |
| 9 | Screening PHQ-9 o GAD-7 | Nombres legibles (sin «PHQ-9 — PHQ-9») | ☐ |
| 10 | Agenda → Nuevo paciente mínimo + cita | Crea paciente y agenda sin ir a registro completo | ☐ |

**Regresión rápida:** `pytest neurosoft-backend/tests` + abrir evaluación sin paciente (debe mostrar dashboard, no blanco).

---

### 6 jun 2026 — Stack + licencias + manual beta
- **Stack:** FastAPI 0.136.3, Pydantic 2.10, React 19, Vite 6, baremos lazy load por prueba.
- **Licencias:** `admin_license_app.py` → `dist/NeuroSoft-LicenseAdmin.exe` (titular). Historial en `%APPDATA%/NeuroSoft/LicenseAdmin/`.
- **Legal UX:** Acuerdo v2.0.0 una vez por PC (`install_agreement.json`); admin/master no lo ven.
- **Docs:** `docs/GUIA_PROTECCION_Y_LICENCIAS.md`, `docs/SEGURIDAD_DATOS_CLINICOS.md` (BitLocker opcional).
- **Manual:** `python docs/scripts/generate_manual_pdf.py` → `dist/MANUAL_BETA_TESTER.pdf`.
- **Mejoras post-upgrade:** ✅ OpenAPI CI, Annotated auth, lazy routes, shards automáticos en build.

---

### 6 jun 2026 (tarde) — Centro Aprender + empaquetado automático
- **Aprender:** `ProtocolosPage.jsx`, 6 quizzes, 11 casos simulador, hub con dashboard progreso, tablas en artículos.
- **Build:** `python build.py --skip-ollama` → frontend + shards + exe + PDF + `NeuroSoft-Setup.exe` (todo en un comando).
- **Manual:** sección 6 Aprender; portada genérica beta (sin credenciales personales).
- **Docs:** `docs/ROADMAP_APRENDER_ENRIQUECIMIENTO.md` cerrado; pendiente P2 = glosario +120 y rutas guiadas.

### 6 jun 2026 (noche) — Aprender P2 cerrado
- **Glosario:** 120 términos (+20 RIPS, CIE-11, ENI-2, SVT/TOMM…).
- **Artículos:** 11 total (+MoCA Colombia, Neuronorma, informe NPS, SVT/TOMM, Res. 1995).
- **Rutas guiadas:** `aprenderPaths.js` — 4 itinerarios con progreso localStorage.
- **Biblioteca:** favoritos y leídos (`ns_biblioteca_fav`, `ns_biblioteca_leidos`).
- **API:** `GET /api/v1/aprender/stats` + `/paths` (público, manifest en `data/aprender/`).
- **Build:** fix `build.py` (`step_pyinstaller` duplicado); manual PDF + Setup regenerados.

### 7 jun 2026 (tarde) — Alineación API jun-2026
- **Fix:** therapy `PATCH` persiste modalidad/duración; backup `POST` único con `BackupRequestDTO` en body; agenda mes con `GET /agenda/` por rango; `profesional_id` en citas desde JWT.
- **Archivos:** `therapy_dtos.py`, `documents.py`, `appointments.py`, `AgendaPage.jsx`, `BackupTab.jsx`, `SesionSOAPForm.jsx`; router sin `backup_router` legado.
- **Tests:** `test_api_alignment_jun2026.py`.
- **Siguiente:** rebuild beta + E2E manual.

### 7 jun 2026 — Inspector General de Integración (build certificado)
- **Tests:** 1034 passed; fix flaky backups (`test_backup.py` autouse `_directorio_backups` aislado).
- **Frontend:** ESLint 0 errors; `RegisterPage` (`setValues`+CUPS hook), `RehabPlanTab` (`safeLS`); bundle index 337 KB.
- **QW-6/QW-8/N2:** etiquetas paciente, backup programado (API+UI), glosario en `InformesPage` vía `GlossaryLegend`.
- **Reactivos:** Matrices/Conceptos Fase 1 en `clinical.js` + `ReactivePanel`; sync Pearson script.
- **Build:** `NeuroSoft.exe` 47.6 MB · Setup 1.3 GB · 31 tests PDF OK.
- **Siguiente:** E2E manual WISC→PDF pro; láminas PNG Pearson reales (copyright).


*Fin del informe de traspaso. NeuroSoft App — software propietario. Sin atribución a terceros.*
