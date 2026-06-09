# CLAUDE.md — NeuroSoft (raíz del proyecto)

> **Actualizado:** 5 jun 2026 · Refs clínicas + skills estado vivo + prep reactivos WISC/WAIS

## Punto de entrada IA (leer en este orden)

1. **`docs/PUNTO_INFLEXION_2026-06-05.md`** — traspaso completo para retomar en otro chat
2. **`docs/ESTADO_VIVO.md`** — qué está ✅ hecho vs ❌ pendiente (fuente de verdad)
3. **`docs/INDICE_MAESTRO.md`** — mapa de toda la documentación
4. **`docs/historico/CARPETAS_RAIZ.md`** — qué hace cada carpeta del monorepo
5. Este archivo (`CLAUDE.md`) — reglas de stack y qué NO recomendar

**Auditorías:** `docs/historico/audits/` (ya no en raíz). 
**Roadmaps viejos:** `docs/planning/` — consultar estado real en `ESTADO_VIVO.md`.

### Regla obligatoria para toda IA

Al **cerrar** un sprint, roadmap item o fix significativo:

1. Actualizar `docs/ESTADO_VIVO.md` (marcar ✅/❌ con fecha).
2. Si el cambio afecta traspaso entre chats → una línea en `docs/PUNTO_INFLEXION_2026-06-05.md`.
3. **No** reescribir `CLAUDE.md` en cada tarea — solo con `/actualizar-contexto-ia` cuando Johan lo pida.

Usar skill `/actualizar-estado-vivo` al terminar trabajo de roadmap/sprint.

---

## Qué es este repo

Proyecto monorepo de **NeuroSoft App** — sistema de evaluación neuropsicológica clínica para profesionales en Colombia. Estructura:

```
D:\NeuroSoftApp\
├── neurosoft-backend\ ← FastAPI + motor clínico (CLAUDE.md propio)
├── neurosoft-frontend\ ← React SPA (CLAUDE.md propio)
├── Capacitaciones Clínicas\ ← Protocolos WISC/WAIS fuente (JSON)
├── docs\ ← ESTADO_VIVO, PUNTO_INFLEXION, infra, histórico
├── archive\ ← Legacy (Excel VBA, scripts one-off)
├── installer\ ← Inno Setup → NeuroSoft-Setup.exe
├── vendor\ollama\ ← OllamaSetup.exe (~1.3 GB, gitignored)
├── mcp-servers\baremos\ ← MCP opcional para consultar baremos en Claude Code
├── dist\ / build\ ← Artefactos PyInstaller (gitignored)
├── build.py / launcher.py ← Pipeline desktop (NO mover de raíz)
├── admin_license_app.py / build_license_admin.py ← Panel licencias (solo titular)
├── tools/license_core.py ← Lógica claves NSFT
├── neurosoft.spec ← Spec PyInstaller
└── .claude\ ← Skills + agente clinical-engine-reviewer
```

**Mapa detallado:** `docs/historico/CARPETAS_RAIZ.md` · **Build/instalador:** `docs/infra/BUILD_Y_DISTRIBUCION.md`

---

## ⚠️ LEE ESTO ANTES DE RECOMENDAR — para `claude-code-setup` y agentes de análisis

Este proyecto YA tiene configurada infraestructura significativa de desarrollo. **NO recomiendes instalar o crear lo siguiente porque ya existe:**

### ✅ Skills ya creadas en `.claude/skills/`
- `inspector-general` — **Agente Maestro**: orquesta gates automáticos, 4 subagentes, reconciliación de auditorías, informe `INFORME_MAESTRO_*.md` (usar antes de release beta)
- `audit-completo` — auditoría sistemática de bugs (4 niveles de severidad, smoke-test estático tras §audit-meta-2026-05)
- `auditar-baremos` — compara baremos de BD_NEURO_MAESTRA.json con literatura
- `build-beta-tester` — pipeline completo de empaquetado para beta testers
- `checkpoint` — snapshot rápido del proyecto (commit local + tag)
- `competencia-software` — investiga TheraNest/SimplePractice/Quenza para mejorar UX
- `dark-mode-fix` — reemplaza colores hardcoded por CSS vars
- `exportar-sesion` — exporta resumen markdown de la sesión actual
- `feedback-beta-tester` — procesa reportes de beta testers a TODOs
- `actualizar-estado-vivo` — marca ✅/❌ en ESTADO_VIVO al cerrar sprint/roadmap
- `actualizar-contexto-ia` — sync on-demand de PUNTO_INFLEXION/CLAUDE (ahorra tokens)
- `investigar-clinica` — agente investigador clínico (papers 2022-2026)
- `investigar-terapia` — investigador específico de psicoterapia
- `mejorar-informe-pdf` — plan para rediseñar el informe PDF
- `redisenar-informes` — **ejecuta** el estándar visual NPS+Pro (Composer/Opus 4.8 mínimo)
- `snapshot-paciente` — genera fixtures JSON para tests de regresión clínica

**Cualquier "agente de análisis de baremos / investigación / build / refactor" propuesto YA existe como skill. Verifícalo antes.**

### NeuroSoft V2 — reglas anti-vibecode (jun 2026)

Ver **`docs/CONVENCIONES_V2.md`** completo. Resumen para IAs:

- **STOP:** no añadir código a páginas/routes monolíticos (>300 líneas) — extraer sub-componente o use case primero
- **STOP:** no duplicar `api.get("/patients/panel")` — usar `usePatientsPanel` + `PatientSelector`
- **STOP:** no definir DTOs Pydantic dentro de `presentation/api/v1/*.py`
- **STOP:** no `db.query` / `db.commit` en routes — usar repository + use case + `dependencies.py`
- **STOP:** no mezclar algoritmos clínicos con JSX
- **ASK:** cambios en `domain/clinical_engine/` → ejecutar tests ground-truth antes de merge
- **CI guards:** `python tools/check_v2_guards.py` + `python tools/api_manifest_check.py` (en GitHub Actions)
- **Inspector General:** `python tools/run_quality_gates.py` — runner unificado para `/inspector-general`

### ✅ Linting + quality gates ya configurados
- **ESLint v9 flat config** en `neurosoft-frontend/eslint.config.js`
 - `no-undef: error`, `react/jsx-no-undef: error`, `no-dupe-keys: error`, `no-const-assign: error`
 - `no-empty: warn` con `allowEmptyCatch: true` (patrón intencional)
 - `react-hooks/rules-of-hooks: error`
- **Build pipeline con lint-gate**: `npm run build` ejecuta `npm run lint && vite build` — si lint falla, no se construye. NO recomiendes añadir esto.
- **`py_compile` check** en `/build-beta-tester` antes de PyInstaller.

### ✅ Testing ya configurado
- **pytest** en `neurosoft-backend/tests/` — **1011 tests** pasan (jun 2026)
- **Playwright E2E** en `neurosoft-frontend/e2e/` (`smoke.spec.js`)
- Casos clínicos verificados (Caso 1 y 2 en `neurosoft-backend/CLAUDE.md`)
- **NO recomendar** Jest, Vitest, Cypress, Mocha — usamos Playwright.

### ✅ IA — Asistente clínico ya integrado
- **Backend**: `app/domain/clinical_engine/ai_prompts.py` con **6 prompts especializados curados**:
 `mejorar_observacion_clinica`, `sugerir_dx_dsm5`, `explicar_discrepancia`, `redactar_recomendaciones`, `narrativa_integradora`, `revisar_pediatrico`.
- **Endpoint**: `GET /api/v1/ai/prompts` y `POST /api/v1/ai/specialized`.
- **Log de trazabilidad**: tabla `ai_logs` (ORM `AILogORM`, migración Alembic 006) — guarda metadata (provider, model, tokens, duración, applied_to_report) **sin contenido PHI**.
- **Sanitización PHI**: `sanitize_clinical_input()` en `ai.py` quita documentos, fechas, emails, teléfonos antes de salir al cloud.
- **Frontend**: componente `AIAsistente.jsx` con dropdown de los 6 prompts + integración en `EvalResultsPage`.
- **Proveedores soportados**: Gemini, Claude (Anthropic), OpenAI, Ollama local.
- **NO sugerir** Langchain / LlamaIndex / agentes ReAct — la app es desktop offline-friendly, no quiere dependencias pesadas en el frontend ni servicios externos obligatorios.

### ✅ Migraciones Alembic activas
- `001` initial schema · `002` row_version HC · `003` patient archive · `004` acompañante + inconcluso · `005` therapy_tasks · `006` ai_logs.
- `Base.metadata.create_all()` también corre al startup como fallback. NO sugerir migrate scripts manuales.

### ✅ Seguridad / cumplimiento ya implementado
- **JWT con verify_exp explícito** (auth_service.py)
- **Rate limiting** in-memory por IP (configurable vía `NEUROSOFT_RATE_LIMIT_PER_MIN`)
- **Security headers**: X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, HSTS en prod
- **Audit log listeners** sobre Session ORM (Resolución 1995 trazabilidad)
- **Token blacklist** para logout real
- **PII redactor** en logs (`core/logging_redactor.py`)
- **safeLS helper** (frontend) para localStorage tolerante a modo privado / cuota llena
- **ConfirmProvider** + `useConfirm` reemplazan `window.confirm()` nativo
- **NO sugerir** Helmet, express-rate-limit, etc. — el stack es FastAPI, ya está cubierto a su nivel.

### ✅ PWA / offline strategy
- Service Worker **deliberadamente deshabilitado en pywebview** (`isPyWebView` check en `index.html`). Causaba pantalla en blanco con caché obsoleta. El SW solo se registra si la app se sirve vía web real.
- **NO sugerir** Workbox / vite-plugin-pwa — ya se intentó y fue contraproducente para el modo desktop.

### ✅ Empaquetado desktop
- **PyInstaller + Inno Setup** (no Electron, no Tauri).
- WebView2 via pywebview con `WEBVIEW2_USER_DATA_FOLDER` aislado y purga al cambiar bundle hash.
- `NeuroSoft.exe` ~42 MB · `NeuroSoft-Setup.exe` ~1.4 GB (incluye OllamaSetup.exe separado).
- **NO sugerir** migrar a Electron o Tauri.

### ✅ Subagentes en `.claude/agents/`
- `clinical-engine-reviewer` — se invoca cuando se toca `strategies.py`, `engine.py` o `baremos_loader.py`. Corre los 27 tests del engine y verifica los casos ground-truth (Caso 1 y 2 del CLAUDE.md backend).

### ✅ Hook pre-commit ya configurado
- En `.claude/settings.local.json` → PreToolUse en Bash: `.claude/hooks/pre-commit-check.js`.
- Bloquea `git commit` si `npm run lint --max-warnings 0` falla en el frontend o si `python -m py_compile` falla en cualquier `.py` staged (excluye tests).

### ✅ Type checking frontend
- `neurosoft-frontend/jsconfig.json` con `checkJs: true` y paths alias `@/*`.
- No requiere TypeScript — el IDE/LSP usa jsconfig para inferencia y navegación.

### ✅ RTK (Rust Token Killer) instalado
- Binario en `C:\Users\DESKTOP\.local\bin\rtk.exe` (v0.40.0).
- Hook global en `~/.claude/settings.json` → `rtk hook claude` intercepta comandos Bash.
- Instrucciones de uso en `~/.claude/RTK.md` (cargado via `@RTK.md` en `~/.claude/CLAUDE.md`).
- Usar explícitamente: `rtk pytest`, `rtk git status`, `rtk git diff`, `rtk playwright test`.
- **Nota Windows**: auto-rewrite de comandos no disponible en Windows nativo (solo en WSL/Linux/macOS). Usar prefijo `rtk` manualmente o via Bash.

### ⚡ RTK — reglas de uso automático (Windows)

**En Windows el rewrite automático no existe. Claude DEBE usar los wrappers manuales.**
Reglas que aplican en TODO momento sin que Johan lo pida:

| Si vas a correr… | Usa en cambio |
|---|---|
| `python -m pytest ... -v` | `rtk test python -m pytest ... -v` |
| `npx playwright test` | `rtk test npx playwright test` |
| `npx eslint src` / `npm run lint` | `rtk lint npx eslint src` |
| `git diff` (diffs grandes) | `rtk git diff` |
| `git log` | `rtk git log` |

No usar RTK en: `git add`, `git commit`, `python -m py_compile`, `npm install`, lectura de archivos.

### ✅ Sprint mayo 2026 — features completadas

Auditoría completa Excel → motor + sprint de mejoras clínicas:

- **Auditoría baremos:** 97/102 tests match 100% con Excel original (Sistema VBA histórico). 10 Grober legacy eliminados + bug `AdFCRO_Rey` corregido. Backup en `data/BD_NEURO_MAESTRA.backup-pre-auditoria-excel.json`. Reporte: `docs/casos-clinicos/AUDITORIA_EXCEL_VS_MOTOR.md`.
- **QW-1 Informes:** botones Imprimir, Guardar como, Enviar correo + modal email completo. Bloqueo descarga si secciones críticas faltan.
- **QW-2 Config SMTP UI:** tab "Comunicaciones" en `ConfigPage`. Password cifrada en BD con Fernet (helper `infrastructure/crypto.py`).
- **QW-3 Plantillas email editables:** 6 tipos (informe/remision/evolucion/rips/recordatorio/otro) override de defaults.
- **QW-4 PDF de HC sola:** botón "Imprimir HC" en `ClinicalHistoryPage`. Sin necesidad de evaluación.
- **QW-7 Recordatorios automáticos:** APScheduler job 18:00 envía email a citas de mañana.
- **M-1 Módulo académico terapias:** `EnfoqueDetalle.jsx` con 7 tabs (resumen/aplicación/técnicas/videos/bibliografía/casos/recursos). 3 enfoques piloto: CBT, ACT, EMDR.
- **M-3 C-SSRS riesgo suicida:** form completo con cálculo automático de nivel + plan de seguridad + banner persistente en `TherapyPage`.
- **M-5 Completitud informe:** indicador visual por sección + lista de bloqueos en `InformesPage`. Botón descarga deshabilitado si CRÍTICO falta.
- **M-6 Orden clínico evaluación:** `OrdenClinicoBanner.jsx` con siguiente test recomendado + timer de recobro (≥20 min entre codificación y recobro Grober). Catálogo: `data/protocolosOrden.js`.
- **M-7 Acompañantes como entidad:** `CompanionORM` + CRUD + UI en HC con autorizaciones (responder escalas proxy, recibir recordatorios).
- **M-8 Bandeja escalas sugeridas:** `screeningSugerencias.js` con 14 reglas data-driven (MC + edad + población → SNAP-IV, PHQ-9, GDS-15, MoCA, PCL-5, etc.).

### ✅ Sprint mayo 2026 — segunda mitad (continuación)

- **Auditoría 52 tests "solo motor":** fuentes clínicas oficiales identificadas para 40/52 tests (Folstein MMSE, Yesavage GDS-15, Beck BDI-II, Lawton IADL, Kertesz FBI, Torralva INECO FS, Arango-Lasprilla 2017 Neuronorma Colombia, Wechsler WISC-IV, etc.). 12 candidatos a revisión clínica menor (consolidación de duplicados ORD/SDMT/TMT, verificación de cobertura ViMRemRec). Reporte: `docs/casos-clinicos/AUDITORIA_55_TESTS_SOLO_MOTOR.md`.

- **Enriquecimiento 13 enfoques terapéuticos restantes (agente Haiku):** DBT, MBCT, TF-CBT, IPT, Esquemas, Gottman, EFT Pareja, Sistémica Estructural, CBT-E Alimentaria, Entrevista Motivacional, TCC Niños, Humanística, CFT Compasión. Generado en `src/data/enfoquesExtendidos.js`, aplicado runtime vía spread en `enfoquesTerapeuticos.js`. Cada uno con descripcion_extendida + efecto_tamano + fases + técnicas + videos + bibliografía + casos + recursos.

- **§M-2 Módulo "Aprender" (Pilar 3 educativo):** AprenderHub + 5 páginas implementadas — Glosario (búsqueda full-text), Estudiar (spaced repetition Leitner 5 cajas con progreso localStorage), Quiz (feedback inmediato), Artículos (markdown viewer ad-hoc), Biblioteca (existente). Contenido inicial en `src/data/aprenderContent.js`. Sidebar grupo "Aprender" ampliado con 7 entradas.

### ✅ Sub-sprint N1-N3 (mayo 2026 — continuación)

- **N1 Simulador de casos clínicos:** `aprender/SimuladorPage.jsx` + `data/casosSimulador.js` con 3 vignettes (TDAH inf, Alzheimer AM, Depresión postparto) con perfiles cognitivos REALES del motor + interpretación experta paso a paso (perfil, hipótesis, diagnóstico DSM-5+CIE-10, batería complementaria, recomendaciones, referencias). Integrado en `AprenderHub` + Sidebar grupo Aprender.
- **N2 Glosario tooltips en InformesPage:** leyenda interactiva con `<GlossaryTerm>` para ICV/IRP/IMT/IVP/CIT/ICG cuando población = infantil. Hover/click muestra definición + ejemplo + fuente.
- **N3 Tests específicos GADS-CTAs y NiCDI:** 11 tests nuevos en `tests/unit/clinical_engine/test_gads_cdi_strategies.py`. **Bug crítico detectado y corregido**: `PuntajeDoblResultadoStrategy` devolvía `0.0` para NiGADSCTAs porque buscaba clave `"PE"` cuando el baremo usa `"CTAS"`. Fix: ahora prueba múltiples claves (PE/CTAS/T/T_score/Score) con fallback al primer valor numérico no-Percentil.

### ✅ Sub-sprint P1-P5 (mayo 2026 — cierre)

- **P5 Cleanup duplicado motor:** `InstrConfiICO` eliminado (typo de `InstrConflICO`, 4 claves idénticas). Backup en `data/BD_NEURO_MAESTRA.backup-pre-consolidacion-duplicados.json`. Documentado que `OrSD/OrTMTA/OrTMTB` NO son duplicados — son z-score para adulto joven, complementarios al Neuronorma AM.
- **P2 Snapshots ground truth como tests CI:** 15 fixtures JSON en `neurosoft-backend/tests/fixtures/casos_ground_truth/`. Test `tests/integration/test_casos_ground_truth.py` itera con 17 tests (15 casos + 2 meta-tests). **134 escalares verificados automáticamente**. Si algún baremo cambia y rompe regresión, falla con mensaje claro.
- **P4 Glosario tooltips embebidos:** componente `ui/GlossaryTerm.jsx` reutilizable. Hover sobre ICV/IRP/IMT/IVP/ICG en EvalResultsPage abre tooltip con definición + ejemplo + ver-también + fuente. Accesible (Esc cierra, click-outside cierra).
- **P3 M-4 Telepsicología básica:** componente `TelepsicologiaTools` en `SesionSOAPForm` — cuando modalidad="telepsicologia" muestra link Jitsi determinístico por sessionId, botón abrir sala, copiar al portapapeles, recordatorio consentimiento Ley 1090.
- **P1 aprenderContent.js expandido:** 60 términos glosario (12 categorías), 50 tarjetas spaced, 3 quizzes×10 preguntas, 6 artículos extensos (Discrepancia ICV-IRP, TDAH vs Ansiedad, Alzheimer vs Pseudodemencia, RCI cuándo NO usar, Impresión DSM-5+CIE-10, Validez de síntomas medicolegal).

### ✅ Sprint junio 2026 — V0–V6 + hardening (cerrado)

- **V0–V5:** ver `docs/AUDITORIA_PDFs.md` (23 hallazgos PDF/reactivos/motor).
- **V6:** hotfix `cfg.scoring` en `ReactivePanel.jsx`.
- **Audit 5 jun:** IDOR HC/scores/reports, advertencias etarias acumulativas, strategies edge cases.
- **Build:** `dist/NeuroSoft.exe` 47 MB · `NeuroSoft-Setup.exe` 1.4 GB.

### 📋 Pendiente real (ver `docs/ESTADO_VIVO.md`)

- E2E manual beta · dark mode `evaluation/` · placeholders REACTIVOS · glosario en InformesPage
- QW-6 etiquetas pacientes · QW-8 backup programado · test flaky backups

---

## Comandos slash disponibles

Ejecutables con `/nombre` desde Claude Code:

| Comando | Para qué |
|---|---|
| **`/inspector-general`** | Agente Maestro: gates + subagentes + reconciliación auditorías → `docs/audits/INFORME_MAESTRO_*.md` |
| **`/audit-completo`** | Auditoría sistemática de bugs (crítico/alto/medio/bajo) con archivo:línea |
| **`/investigar-clinica <tema>`** | Agente investigador: papers 2022-2026 con foco Colombia/Latinoamérica |
| **`/investigar-terapia <tema>`** | Como investigar-clinica pero para psicoterapia (no neuropsicología) |
| **`/auditar-baremos <test_id>`** | Compara baremos actuales con literatura reciente |
| **`/build-beta-tester`** | Pipeline completo de empaquetado |
| **`/feedback-beta-tester <texto>`** | Parsea reportes de beta tester → TODOs accionables |
| **`/competencia-software <tema>`** | Investiga TheraNest/SimplePractice/Quenza para inspirar features |
| **`/checkpoint`** | Snapshot rápido (commit local + tag) antes de cambios grandes |
| **`/dark-mode-fix`** | Encuentra colores hardcoded y los reemplaza por CSS vars |
| **`/exportar-sesion`** | Exporta resumen md de la sesión actual para retomar en otro chat |
| **`/snapshot-paciente`** | Crea fixture JSON de un caso clínico para tests de regresión |
| **`/mejorar-informe-pdf`** | Plan estructurado para rediseñar el informe PDF |
| **`/redisenar-informes`** | Implementa/mantiene estándar PDF NPS+Pro — ver `docs/REFERENCIAS_INFORMES_NPS.md` |
| **`/organizar-repo`** | Auditoría de auditorías: ordenar docs, ESTADO_VIVO, limpiar raíz |
| **`/actualizar-estado-vivo`** | Al cerrar sprint/roadmap: actualizar ESTADO_VIVO (+ línea en PUNTO_INFLEXION si aplica) |
| **`/actualizar-contexto-ia`** | Sync on-demand de archivos de lectura IA (solo cuando Johan lo pida) |

### Orquestación Inspector General

```text
/inspector-general
  ├─ tools/run_quality_gates.py (pytest, eslint, v2, api manifest)
  ├─ subagentes: api-alignment · architecture-v2 · normativa-colombia · clinical-fidelity
  ├─ /audit-completo (código, delegado)
  └─ docs/audits/INFORME_MAESTRO_<fecha>.md → /actualizar-estado-vivo
```

**Subagentes** en `.claude/agents/`: `clinical-engine-reviewer` (motor) + 4 revisores del Inspector.

### Cómo crear nuevas skills

Cada skill vive en `.claude/skills/<nombre>/SKILL.md` con frontmatter:
```yaml
---
name: nombre-skill
description: Cuándo se debe activar y qué hace.
---
```

---

## Pipeline de build (manual, sin skill)

```bash
cd neurosoft-frontend && npm run build # incluye lint pre-build
cd .. && python build.py --skip-frontend --skip-ollama
& "C:\Users\DESKTOP\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer\NeuroSoft.iss
```

Output final: `dist\NeuroSoft-Setup.exe` → enviar al beta tester.

### Reglas críticas del build

1. **NO bundlear `OllamaSetup.exe` dentro del .exe principal** (causa "The setup files are corrupted"). Se distribuye separado dentro del instalador Inno Setup → carpeta `{app}\vendor\ollama\` al instalar.
2. **`NeuroSoft.exe` debe pesar <100 MB**. Si pesa >1 GB, Ollama se bundleó por accidente.
3. **`NeuroSoft-Setup.exe` debe pesar ~1.4 GB**.
4. Antes del build: `Stop-Process -Name "NeuroSoft" -Force -ErrorAction SilentlyContinue` (libera el .exe en uso).

---

## Configuración (`.claude/settings.local.json`)

Whitelist de comandos recurrentes para reducir prompts. No se commitea (está en `.gitignore`).

Comandos pre-aprobados:
- `npm run build`, `npm install`, `pytest` (Bash y PowerShell), `npx eslint …`
- `python build.py …`, `python -m py_compile …`, `python docs/scripts/generate_manual_pdf.py …`
- `Stop-Process -Name "NeuroSoft" …`
- `ISCC.exe …`
- `WebSearch`, `WebFetch`
- Comandos de lectura git (`git status`, `git diff`, `git log`)
- `rtk …` (Bash y PowerShell) — wrappers RTK optimizados para tokens

Comandos **denegados**:
- `rm -rf`, `git push --force`, `git reset --hard`, `Remove-Item -Recurse -Force C:\*`

---

## Memoria persistente

- **Usuario**: Johan Sebastián Salgado Sarmiento, psicólogo + creador de NeuroSoft App. Email `jssalgadosa@unal.edu.co`.
- **Beta tester**: credenciales pre-configuradas en el .exe: `beta / BetaTester2026!` (defaults). Override vía `NEUROSOFT_BETA_USERNAME` / `NEUROSOFT_BETA_PASSWORD`. Installs históricos que tengan otros usuarios beta siguen funcionando.
- **Branding**: producto se llama **"NeuroSoft App"** — sin números de versión visibles al usuario.
- **Idioma**: todo en español colombiano neutro.
- **Stack**: React 19 + Vite 6 + Tailwind (frontend) · FastAPI 0.136 + Pydantic 2.10 + SQLAlchemy + SQLite (backend) · PyInstaller + Inno Setup · Ollama (IA local opcional).
- **No publicar uso de IA al paciente**: la cláusula del PDF habla de responsabilidad profesional (Ley 1090), NO menciona explícitamente que se usó IA — eso es decisión editorial intencional del clínico.

---

## Referencias clínicas centrales

> Fuentes **documentadas en el repo** — no inventar DOI/ISBN. Detalle por prueba: `docs/casos-clinicos/AUDITORIA_55_TESTS_SOLO_MOTOR.md`, `docs/casos-clinicos/AUDITORIA_EXCEL_VS_MOTOR.md`, `docs/manuales-ocr/EXTRACCION_WISC-IV_WAIS-III.md`.

### Baremos Colombia (Neuronorma / motor)

| Fuente | Uso en NeuroSoft | Doc interno |
|---|---|---|
| **Arango-Lasprilla, J. C. & Rivera, D. (Eds.). (2017).** *Neuropsicología en Colombia: Datos normativos, estado actual y retos a futuro.* UAM, Manizales. | TMT AM, FCRO AM, FluidP/Anim, ViDeno/ViSem, Stroop AM, SDMT, WAIS-III AM | `AUDITORIA_55_TESTS` §4 |
| **Peña-Casanova et al. (2009).** Neuronorma (España) → adaptación Colombia en Arango-Lasprilla (2017) | Grober AM, varios z-score AM | `AUDITORIA_55_TESTS` §5 |
| **Arango-Lasprilla et al. (2015).** Validación adulto joven | `AdTMT_AB`, `AdFCRO_Rey`, `AdStroop_Corr`, `AdCVLT` | `AUDITORIA_EXCEL_VS_MOTOR` |
| **Excel histórico** `MISISTEMAV1.xlsm` (archivado en `archive/legacy/`) | 97/102 tests match 100% con motor | `AUDITORIA_EXCEL_VS_MOTOR` |

### WISC-IV / WAIS-III (Pearson / Manual Moderno — copyright)

| Fuente | ISBN (en `pearsonProtected.js`) | Protocolo JSON |
|---|---|---|
| **Wechsler (2007). WISC-IV Manual de Aplicación** | 978-968-426-987-0 | `Capacitaciones Clínicas/protocolos/wisc_iv_protocolo.json` |
| **Wechsler (1997). WAIS-III Manual de Aplicación** | 978-968-426-984-9 | `Capacitaciones Clínicas/protocolos/wais_iii_protocolo.json` |
| OCR manuales aplicación | — | `docs/manuales-ocr/EXTRACCION_WISC-IV_WAIS-III.md` |

Ítems verbatim protegidos por `pearsonProtected.js` + consentimiento único al instalar.

### Escalas clínicas frecuentes (solo motor, post-Excel)

| Test ID | Fuente original (auditada) |
|---|---|
| `MMSE` | Folstein, Folstein & McHugh (1975). *J Psychiatr Res*, 12(3), 189-198. Validación CO: Rosselli et al. (2000) |
| `EscYesavage` | Yesavage et al. (1983). *J Psychiatr Res*, 17(1), 37-49. CO: Pedraza et al. (2014) |
| `AdBeck` / `EscBeck` | Beck, Steer & Brown (1996). BDI-II. CO: Posada-Villa et al. (2008) |
| `EscLawton` | Lawton & Brody (1969). *The Gerontologist*, 9(3), 179-186 |
| `EscKertesz` | Kertesz, Davidson & Fox (1997). FBI. CO: Henao-Arboleda et al. (2010) |
| `GoNoGoICO`…`RefranesICO` | Torralva et al. (2009). INECO Frontal Screening. *JINS*, 15(5), 777-786 |
| `Denom48` | Boston Naming Test. CO: Allegri et al. (1997), Pedraza et al. (2012) |
| `NiCDI` | Kovacs (1992). CDI. CO: Aguirre-Acevedo et al. (2008) |
| `NiGADSCTAs` | Gilliam (2001). GADS |
| `NiEniE1+E2+E3+E4` | Matute, Rosselli, Ardila & Ostrosky-Solís (2014). ENI-2 |
| `ViGrober*` / `GBTotal` | Grober & Buschke (1987). *Dev Neuropsychol*, 3(1), 13-36 |
| `NiFCROCop` / `NiFCRORec` | Rey (1941); adaptación infantil Bernstein & Waber (1996); CO: Rosselli et al. (2004) |
| `SDMT` | Smith (1982). WPS. CO: Arango-Lasprilla et al. (2015) |
| `NiSt_*` | Golden (1978). Stroop. CO: Matute et al. (2007) |

### Métodos estadísticos y normativo

| Referencia | Uso |
|---|---|
| **Jacobson & Truax (1991).** RCI | Pre–Post, cambio confiable |
| **Ley 1090 de 2006** | Deontología psicólogo CO (PDF informe) |
| **Ley 1581 de 2012** | Habeas Data — `docs/legal/HABEAS_DATA.md` |
| **Ley 1616 de 2013** | Salud mental |
| **Resolución 1995 de 1999** | HC — audit log ORM — `docs/MONITOREO_AUDIT_LOG.md` |
| **Resolución 1888 de 2025** | IHCE (futuro, no implementado) — `docs/planning/ROADMAP_2026.md` |

### Casos ground-truth verificados

- **Caso 1 (Jesús, 16a11m WISC-IV):** `neurosoft-backend/CLAUDE.md` + fixtures `tests/fixtures/casos_ground_truth/`
- **Caso 2 (María Elena, AM):** idem — 134 escalares en CI
- Reporte: `docs/casos-clinicos/CASOS_GROUND_TRUTH.md`

---

## Subprojectos con su propia memoria

- `neurosoft-backend/CLAUDE.md` — arquitectura clean, baremos, estrategias clínicas, casos verificados
- `neurosoft-frontend/CLAUDE.md` — estructura React, sistema de diseño, contextos

Ambos contienen reglas críticas específicas. Consultar siempre antes de modificar código clínico.
