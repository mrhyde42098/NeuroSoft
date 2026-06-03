# Arquitectura de NeuroSoft

Documento técnico de alto nivel para ingenieros, auditores y beta testers
avanzados. Cubre el **monorepo NeuroSoft App** completo: backend,
frontend, empaquetado desktop, motor clínico y cumplimiento normativo
colombiano.

> **Última revisión:** junio 2026 (Sprint 0-3).
> **Versión del sistema:** 2.0.0
> **Software propiedad de:** Johan Sebastián Salgado Sarmiento.

---

## 1. Visión general

NeuroSoft App es un sistema **offline-first** de evaluación neuropsicológica
clínica para consultorios pequeños (2-5 psicólogos) en Colombia. Se entrega
como **aplicación de escritorio** (Windows) que embebe:

- **Backend**: FastAPI + SQLAlchemy + SQLite (motor clínico + API).
- **Frontend**: React 18 + Vite + Tailwind (UI clínica).
- **Empaquetado**: PyInstaller (binario) + Inno Setup (instalador).
- **IA opcional**: Ollama local (privacidad por defecto) o Gemini/Claude/OpenAI
  en la nube con sanitización PHI.

**NO** usa Electron, Tauri ni frameworks pesados. El bundle pesa ~42 MB
(`NeuroSoft.exe`) y el instalador ~1.4 GB (incluye `OllamaSetup.exe`
como dependencia opcional separada).

---

## 2. Estructura del monorepo

```
D:\NeuroSoftApp\
├── neurosoft-backend/          ← FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── domain/             ← Núcleo: motor clínico, estrategias
│   │   ├── application/        ← Casos de uso (orquestación)
│   │   ├── infrastructure/     ← BD, auth, audit, scheduler, reports
│   │   └── presentation/       ← API REST (FastAPI routers)
│   ├── tests/                  ← 814+ tests pytest
│   ├── alembic/                ← Migraciones BD
│   └── data/                   ← BD_NEURO_MAESTRA.json (168 pruebas)
│
├── neurosoft-frontend/         ← React 18 + Vite + Tailwind
│   ├── src/
│   │   ├── app/                ← Páginas por dominio
│   │   ├── data/               ← Datos clínicos estáticos
│   │   ├── ui/                 ← Sistema de diseño (tokens + primitives)
│   │   ├── contexts.jsx        ← Auth, Dark, Toast, A11y providers
│   │   ├── api/                ← Cliente HTTP
│   │   └── utils/              ← Helpers puros
│   ├── e2e/                    ← Tests Playwright
│   └── dist/                   ← Build artifacts
│
├── installer/                  ← Inno Setup script (NeuroSoft.iss)
├── vendor/ollama/              ← OllamaSetup.exe (1.3 GB, gitignored)
├── dist/                       ← Artefactos de build (.exe, setup, manual)
│
├── .claude/                    ← Skills, settings, memoria del proyecto
├── .github/workflows/          ← CI: backend-ci.yml, frontend-ci.yml
└── docs/                       ← Documentación técnica
```

---

## 3. Backend — Clean Architecture

```
app/
├── domain/                ← REGLAS DE NEGOCIO (no sabe de HTTP/BD)
│   └── clinical_engine/
│       ├── strategies.py          ← 15 estrategias de scoring
│       ├── engine.py              ← Orquestador (ClinicalEngine)
│       ├── baremos_loader.py      ← Carga BD_NEURO_MAESTRA.json
│       ├── factory.py             ← Mapea tipo_calculo → Strategy
│       └── interpretation_engine.py ← Textos clínicos por dominio
│
├── application/           ← CASOS DE USO
│   └── use_cases/        ← Orquestan dominio + repositorios
│
├── infrastructure/        ← ADAPTADORES (BD, IO, servicios externos)
│   ├── database/         ← SQLAlchemy ORM + Alembic migrations
│   ├── auth/             ← JWT + bcrypt + rate limit
│   ├── audit/            ← Listeners PHI + record_event
│   ├── report_pro/       ← Generador PDF premium (6 variantes)
│   ├── scheduler/        ← APScheduler (recordatorios, limpieza)
│   └── observability/    ← Logging + redactor PHI
│
└── presentation/          ← INTERFAZ HTTP (FastAPI)
    └── api/v1/           ← Routers (patients, evaluations, reports…)
```

**Regla absoluta:** el motor clínico (`strategies.py`, `engine.py`) NO
conoce FastAPI ni SQLAlchemy. Es código puro testeable.

### 3.1 Motor clínico

15 estrategias de scoring (`tipo_calculo`):

| Estrategia | Pruebas | Método |
|---|---|---|
| `rango_puntaje` | 65 (WISC-IV, ENI-2, K-ABC) | Tabla de baremo por edad |
| `wais_range` | 20 (WAIS-III) | Tabla por rango de edad |
| `desconocido` | 33 (Neuronorma AM) | Ajuste escolaridad + tabla |
| `z_score` | 10 | (PD - media) / sd |
| `suma_a_indice` | 14 (índices compuestos) | Suma de PE → CI |
| `escolaridad_pc50` | 5 | Tabla por edad × escolaridad |
| `puntaje_directo_a_t` | 8 | Tabla PD → T-score |
| `puntaje_doble_resultado` | 9 | Tabla → [PE, Percentil] |
| `clasificacion_fija` | 4 | Tabla → clasificación |
| `edad_sexo` | 4 | Tabla → [sexo, media, sd] |
| Otras | 6 | Cálculos específicos |

**Datos clínicos** (`data/BD_NEURO_MAESTRA.json`): 168 pruebas, 112.643
claves de baremo. **NO MODIFICAR sin consulta previa** al autor (regla
del repo).

### 3.2 Seguridad (S0.x)

- **JWT con `verify_exp` explícito** (auth_service.py)
- **Rate limiting** in-memory por IP (configurable vía env)
- **Security headers**: CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy
- **Audit log** sobre Session ORM (Resolución 1995 trazabilidad)
- **Token blacklist** para logout real + sentinel "revoke all"
- **PII redactor** en logs (nunca se loguea PHI)
- **PHI policy** en audit listeners: VERBATIM / HASH (SHA-256:xxxx[:12]) / SKIP
- **Kill switches ELIMINADOS** (no solo ignorados):
  `NEUROSOFT_DISABLE_AUTH`, `NEUROSOFT_RESET_ADMIN_PASSWORD`, etc.

### 3.3 Multi-tenant (S0.2)

- `get_patient_for_user(patient_id, db, user)` helper centraliza ownership.
- 9 handlers de `patients.py` refactorizados con `CurrentUser` + ownership.
- Cross-tenant → 403 + audit log.
- Admin ve todos; profesional solo lo suyo.

---

## 4. Frontend — React + Vite

### 4.1 Sistema de diseño

- **Tokens** centralizados en `ui/tokens.js` (TEAL, NAVY, CREAM, COLORS, SIZES).
- **CSS variables** (`--ns-*`) con inversión automática en `.dark-mode`.
- **Primitivos** en `ui/primitives.jsx` (Card, Btn, Input, Sel, Txta…).
- **Iconos**: Material Symbols Outlined.
- **Modo oscuro**: toggle global, persistido en `localStorage` (`ns_dark`).
- **Alto contraste**: clase `.high-contrast` en `<html>` (A11y).

### 4.2 Contextos globales

| Hook | Proveedor |
|---|---|
| `useAuth()` | `AuthProvider` |
| `useDark()` | `DarkProvider` |
| `useToast()` | `ToastProvider` |
| `useA11y()` | `A11yProvider` |

### 4.3 Accesibilidad (S3.3)

- `<SkipToMain>` link para lectores de pantalla.
- `aria-current="page"` en Sidebar activo.
- `aria-label` en todos los botones de ícono.
- `useFocusTrap` + `useEscape` hooks para modales.
- `useAnnounce` para anuncios a lectores de pantalla.
- `usePrefersReducedMotion` respeta preferencias del SO.
- `<main id="ns-main-content">` con `tabIndex=-1` para foco programático.

---

## 5. Empaquetado desktop

```
build.py  (PyInstaller)           →  NeuroSoft.exe  (~42 MB)
installer/NeuroSoft.iss           →  NeuroSoft-Setup.exe  (~1.4 GB)
```

**Reglas críticas:**

1. **NO bundlear `OllamaSetup.exe` dentro del .exe principal** (causa
   "The setup files are corrupted"). Se distribuye separado.
2. **`NeuroSoft.exe` debe pesar <100 MB**. Si pesa >1 GB, Ollama se
   bundleó por accidente.
3. Antes del build: `Stop-Process -Name "NeuroSoft" -Force`.

WebView2 via pywebview con `WEBVIEW2_USER_DATA_FOLDER` aislado y purga
al cambiar bundle hash.

---

## 6. Datos clínicos

### 6.1 Baremos

- **WISC-IV, WAIS-III, ENI-2, K-ABC, K-BIT, Neuropsi, BANFE, BNT, Test
  Barcelona**: baremos del manual original o normas colombianas
  (Neuronorma 2017).
- **TOTAL**: 168 pruebas, 112.643 claves.
- **Backup defensivo**: `data/BD_NEURO_MAESTRA.backup-pre-*.json` antes
  de cada cambio mayor.
- **Modificación**: SIEMPRE consultar primero.

### 6.2 Tests ground-truth

- 15 fixtures JSON en `tests/fixtures/casos_ground_truth/`.
- 17 tests parametrizados en `tests/integration/test_casos_ground_truth.py`.
- **134 escalares verificados** automáticamente.

---

## 7. Cumplimiento normativo colombiano

| Norma | Aplica a | Implementación |
|---|---|---|
| Ley 1090/2006 | Informes, firma profesional | Cláusula legal + responsabilidad |
| Ley 1581/2012 | Datos personales, habeas data | PII redactor + endpoint export |
| Ley 1616/2013 | Salud mental | C-SSRS (riesgo suicida) + screening |
| Resolución 1995/1999 | Historia clínica | Audit log + versionado + firma |

### 7.1 Auditoría y logs

- `audit_logs` table con metadata (sin PHI).
- `ai_logs` table (migración 006) para trazabilidad de IA.
- `clinical_access` table (S2.6) para ítems verbatim Pearson.
- Endpoint `GET /api/v1/audit` con paginación.

---

## 8. CI/CD

### 8.1 Backend (`backend-ci.yml`)

- Python 3.11 + 3.12 matrix.
- `ruff check` + `ruff format --check`.
- `mypy app` (no bloqueante aún).
- `pytest tests/ --cov=app` con cobertura.
- `pip-audit` (CVEs).
- `gitleaks` (secretos en el repo).
- Docker build smoke (sin push).

### 8.2 Frontend (`frontend-ci.yml`)

- Node 20.
- `npm run lint` (ESLint v9).
- `npm run build` (Vite).
- `playwright test e2e/smoke.spec.js e2e/a11y.spec.js`.

---

## 9. Testing

| Capa | Framework | Cobertura |
|---|---|---|
| Backend unit | pytest | 33 tests motor + 50+ helpers |
| Backend integration | pytest | 250+ tests BD + endpoints |
| Backend ground-truth | pytest fixtures | 134 escalares |
| Frontend E2E | Playwright | smoke + scoring + a11y |
| Frontend manual | Manual | 5 beta testers activos |

**Total**: 814+ tests pasando (verificado mayo 2026).

---

## 10. Decisiones arquitectónicas clave

1. **Offline-first**: la app DEBE funcionar sin internet.
2. **SQLite + Alembic**: BD embebida, sin servidor externo.
3. **WebView2 + pywebview**: nativo Windows, sin Electron.
4. **Multi-tenant por profesional**: un consultorio, varios profesionales.
5. **IA opcional y desconectable**: Ollama local por defecto.
6. **Privacidad por diseño**: PHI nunca sale al log, IA cloud sanitiza.
7. **6 variantes PDF** según audiencia (pro, pediátrico, médico-legal,
   junta médica, inconcluso, paciente).

---

## 11. Roadmap (Sprint 0-4)

- ✅ **Sprint 0** (3 días): seguridad, multi-tenant, kill switches.
- ✅ **Sprint 1**: motor clínico (edge cases, reclasificación, CIE-10).
- ✅ **Sprint 2**: scrub IN&S, plantillas, screening, narrativa,
  capa protegida Pearson.
- ✅ **Sprint 3** (este documento): UX versión paciente, dark mode,
  A11y, CI/CD.
- ⏳ **Sprint 4**: baremos adicionales, Sentry, backups AES-256, DRP.

---

## 12. Contacto

- **Autor / propietario**: Johan Sebastián Salgado Sarmiento
- **Email**: jssalgadosa@unal.edu.co
- **Documentación**: `docs/` + este archivo
- **Issues**: contactar vía email (no hay GitHub público)
