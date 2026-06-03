# CLAUDE.md — NeuroSoft (raíz del proyecto)

## Qué es este repo

Proyecto monorepo de **NeuroSoft App** — sistema de evaluación neuropsicológica clínica para profesionales en Colombia. Estructura:

```
D:\NeuroSoftApp\
├── neurosoft-backend\          ← FastAPI + SQLAlchemy + SQLite (tiene su propio CLAUDE.md)
├── neurosoft-frontend\         ← React + Vite + Tailwind (tiene su propio CLAUDE.md)
├── installer\                  ← Inno Setup script (NeuroSoft.iss)
├── vendor\ollama\              ← OllamaSetup.exe (1.3 GB, ignored por git)
├── dist\                       ← artefactos de build (.exe, setup, manual, PDF)
├── build.py                    ← pipeline PyInstaller
├── neurosoft.spec              ← spec de PyInstaller
├── neurosoft.ico               ← icono de la app
└── .claude\                    ← skills, settings, memoria del proyecto
```

---

## ⚠️ LEE ESTO ANTES DE RECOMENDAR — para `claude-code-setup` y agentes de análisis

Este proyecto YA tiene configurada infraestructura significativa de desarrollo. **NO recomiendes instalar o crear lo siguiente porque ya existe:**

### ✅ Skills ya creadas en `.claude/skills/`
- `audit-completo` — auditoría sistemática de bugs (4 niveles de severidad, smoke-test estático tras §audit-meta-2026-05)
- `auditar-baremos` — compara baremos de BD_NEURO_MAESTRA.json con literatura
- `build-mayra` — pipeline completo de empaquetado (alias histórico, renombrado a `build-beta-tester`)
- `checkpoint` — snapshot rápido del proyecto (commit local + tag)
- `competencia-software` — investiga TheraNest/SimplePractice/Quenza para mejorar UX
- `dark-mode-fix` — reemplaza colores hardcoded por CSS vars
- `exportar-sesion` — exporta resumen markdown de la sesión actual
- `feedback-mayra` — procesa reportes de beta testers a TODOs
- `investigar-clinica` — agente investigador clínico (papers 2022-2026)
- `investigar-terapia` — investigador específico de psicoterapia
- `mejorar-informe-pdf` — plan para rediseñar el informe PDF
- `snapshot-paciente` — genera fixtures JSON para tests de regresión clínica

**Cualquier "agente de análisis de baremos / investigación / build / refactor" propuesto YA existe como skill. Verifícalo antes.**

### ✅ Linting + quality gates ya configurados
- **ESLint v9 flat config** en `neurosoft-frontend/eslint.config.js`
  - `no-undef: error`, `react/jsx-no-undef: error`, `no-dupe-keys: error`, `no-const-assign: error`
  - `no-empty: warn` con `allowEmptyCatch: true` (patrón intencional)
  - `react-hooks/rules-of-hooks: error`
- **Build pipeline con lint-gate**: `npm run build` ejecuta `npm run lint && vite build` — si lint falla, no se construye. NO recomiendes añadir esto.
- **`py_compile` check** en `/build-mayra` antes de PyInstaller.

### ✅ Testing ya configurado
- **pytest** en `neurosoft-backend/tests/` — 27 tests del clinical engine pasan
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

### 📋 Lo que SÍ podría faltar (próximo sprint)
- **GitHub Actions / CI** — pipeline automatizado (tests Python + lint frontend + Playwright).
- **Glosario tooltips en InformesPage** (extender de EvalResultsPage al panel de informes).
- **Ampliar `aprenderContent.js`** a 80 términos / 125 tarjetas / 8 quizzes / 10 artículos (parcialmente alcanzado).
- **M-2 Simulador de casos clínicos** (vignettes con baremos reales para que estudiantes practiquen interpretación).
- **GADS-CTAs y NiCDI** — verificar comportamiento con baremos `edad_sexo` y `puntaje_doble_resultado` en tests.

---

## Comandos slash disponibles

Ejecutables con `/nombre` desde Claude Code:

| Comando | Para qué |
|---|---|
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
cd neurosoft-frontend && npm run build       # incluye lint pre-build
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
- **Stack**: React 18 + Vite + Tailwind (frontend) · FastAPI + SQLAlchemy + SQLite (backend) · PyInstaller + Inno Setup (empaquetado) · Ollama (IA local opcional).
- **No publicar uso de IA al paciente**: la cláusula del PDF habla de responsabilidad profesional (Ley 1090), NO menciona explícitamente que se usó IA — eso es decisión editorial intencional del clínico.

---

## Referencias clínicas centrales

- **Arango-Lasprilla, J. C. & Rivera, D. (Eds.). (2017).** *Neuropsicología en Colombia: Datos normativos, estado actual y retos a futuro.* — Fuente principal de los baremos colombianos para 10 pruebas.
- **Jacobson & Truax (1991)** — Reliable Change Index (RCI) usado en Pre–Post.
- **Ley 1090 de 2006** — Código Deontológico del Psicólogo en Colombia (responsabilidad profesional, art. 2 y 36).
- **Ley 1581 de 2012** — Habeas Data Colombia (datos clínicos sensibles).
- **Ley 1616 de 2013** — Ley de Salud Mental.
- **Resolución 1995 de 1999** — Historia clínica (trazabilidad, firma irreversible).

---

## Subprojectos con su propia memoria

- `neurosoft-backend/CLAUDE.md` — arquitectura clean, baremos, estrategias clínicas, casos verificados
- `neurosoft-frontend/CLAUDE.md` — estructura React, sistema de diseño, contextos

Ambos contienen reglas críticas específicas. Consultar siempre antes de modificar código clínico.
