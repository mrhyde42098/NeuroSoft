# Mapa de Módulos — NeuroSoft App

**Versión:** 2.0 · **Última actualización:** 2026-06-03 · **Estado:** Producción

Este documento describe la arquitectura de NeuroSoft App con énfasis en la separación de capas, dependencias y reglas de evolución.

---

## 1. Visión general

NeuroSoft es un **sistema monolítico modular** estructurado en Clean Architecture con dos aplicaciones:

| Aplicación | Stack | Propósito |
|---|---|---|
| `neurosoft-backend` | Python 3.11 + FastAPI + SQLAlchemy 2.0 + SQLite | API REST, motor clínico, generador de PDF, scheduler |
| `neurosoft-frontend` | JavaScript ES2022 + React 18 + Vite 5 + Tailwind 3 | SPA (Single Page Application) + UI clínica |

Ambas se empaquetan en un solo `.exe` con PyInstaller + Inno Setup (ver `installer/NeuroSoft.iss`).

---

## 2. Backend — capas Clean Architecture

```
neurosoft-backend/
├── app/
│   ├── domain/                    ← NÚCLEO. Sin dependencias de framework.
│   │   ├── clinical_engine/       ← Motor de cálculo neuropsicológico
│   │   │   ├── strategies.py      ← 15 estrategias de scoring
│   │   │   ├── engine.py          ← ClinicalEngine (orquestador)
│   │   │   ├── baremos_loader.py  ← Carga BD_NEURO_MAESTRA.json
│   │   │   ├── factory.py         ← tipo_calculo → Strategy
│   │   │   ├── interpretation_engine.py  ← Textos por dominio
│   │   │   ├── ai_prompts.py      ← 6 prompts clínicos especializados
│   │   │   └── narrative.py       ← Generador de narrativa (F9 + S2.5)
│   │   └── ...
│   ├── application/               ← Use cases. Orquestan dominio + repos.
│   │   └── use_cases/             ← Lógica de aplicación
│   ├── infrastructure/            ← Adaptadores (BD, PDF, auth, scheduler)
│   │   ├── auth/                  ← JWT, password hashing, token blacklist
│   │   ├── audit/                 ← Listeners SQLAlchemy (Res. 1995 trazabilidad)
│   │   ├── database/              ← ORM, sesión, migraciones Alembic
│   │   ├── repositories/          ← Persistencia
│   │   ├── report_pro/            ← Generador PDF Pro + 7 variantes
│   │   ├── report_service.py      ← Generador PDF estándar (legacy)
│   │   ├── email_service.py       ← SMTP + plantillas (QW-2, QW-3)
│   │   ├── scheduler_service.py   ← APScheduler (QW-7 recordatorios)
│   │   ├── crypto.py              ← Fernet AES-128-CBC + HMAC-SHA256
│   │   ├── hc_pdf_service.py      ← PDF de HC sola (QW-4)
│   │   ├── retencion.py           ← F5.2 cálculo fechas críticas
│   │   └── ...
│   ├── presentation/              ← HTTP. CERO lógica de negocio.
│   │   └── api/v1/                ← Endpoints REST FastAPI
│   │       ├── auth.py            ← Login, refresh, logout, change-password
│   │       ├── patients.py        ← CRUD pacientes (con ownership)
│   │       ├── evaluations.py     ← Evaluaciones + scoring
│   │       ├── reports.py         ← Generación de PDF
│   │       ├── clinical_history.py← Historia clínica
│   │       ├── therapy.py         ← Sesiones + notas SOAP + C-SSRS
│   │       ├── companions.py      ← Acompañantes (M-7)
│   │       ├── config.py          ← SMTP, plantillas email (QW-2/QW-3)
│   │       ├── retencion.py       ← F5.2 endpoint admin
│   │       ├── ai.py              ← Asistente IA con sanitización PHI
│   │       └── update.py          ← Auto-update con HMAC (S0.1)
│   ├── core/                      ← Config, logging, middleware
│   └── main.py                    ← App FastAPI + middleware auth global
├── data/                          ← BD SQLite + baremos JSON (INTOCABLE)
├── alembic/                       ← Migraciones (001-006)
├── tests/                         ← 910 tests (855 previos + 55 nuevos)
└── scripts/                       ← Utilidades (audit_baremos_18.py)
```

---

## 3. Frontend — estructura por dominio

```
neurosoft-frontend/
├── src/
│   ├── api/
│   │   └── client.js              ← HTTP client con JWT + safeLS
│   ├── app/                       ← Páginas por dominio
│   │   ├── auth/                  ← Login
│   │   ├── patients/              ← HC, consentimientos, acompañantes
│   │   ├── evaluation/            ← Aplicación + scoring + screening
│   │   │   ├── ScreeningPage.jsx
│   │   │   ├── ScreeningWizard.jsx  ← F8.2 nuevo
│   │   │   ├── EvalApplyPage.jsx
│   │   │   ├── EvalResultsPage.jsx
│   │   │   └── StimulusDisplay.jsx   ← S5.x Pearson verbatim
│   │   ├── reports/               ← Informes generados
│   │   ├── therapy/               ← Sesiones, SOAP, C-SSRS, enfoques
│   │   ├── rehab/                 ← 15 actividades cognitivas
│   │   ├── ia/                    ← Panel IA + chat
│   │   ├── config/                ← SMTP, comunicaciones, accesibilidad
│   │   ├── agenda/                ← Citas
│   │   ├── dashboard/             ← KPIs clínicos
│   │   ├── history/               ← Comparativo longitudinal
│   │   ├── aprender/              ← Módulo educativo (Pilar 3)
│   │   └── layout/                ← Sidebar, TopBar
│   ├── data/                      ← Datos clínicos estáticos
│   │   ├── clinical.js            ← REACTIVOS, INSTRUCCIONES, OBS_TEMPLATES
│   │   ├── screening.js           ← 28 escalas + CONSTRUCTOS (F8.1)
│   │   ├── screeningSugerencias.js← 14 reglas data-driven
│   │   ├── protocolosOrden.js     ← 3 protocolos con recobro
│   │   ├── datosClinicos.js       ← RECOMMENDATIONS_LIB, DSM5
│   │   ├── protocolLoader.js      ← sugerenciaProtocolo + queja memoria
│   │   ├── plantillasDocumentales.js ← 17 plantillas (F5.1)
│   │   ├── enfoqueTerapeuticos.js ← 16 enfoques + extended
│   │   ├── aprenderContent.js     ← 60 glosario, 50 tarjetas, 3 quizzes
│   │   ├── casosSimulador.js      ← 3 vignettes (N1)
│   │   ├── pearsonProtected.js    ← S5.x verbatim one-time
│   │   └── ui.js                  ← REPORT_TEMPLATES, SHORTCUTS
│   ├── contexts.jsx               ← AuthProvider, DarkProvider, Toast, A11y
│   ├── ui/                        ← Sistema de diseño (sin lógica)
│   │   ├── primitives.jsx         ← Btn, Card, Input, Sel, etc.
│   │   ├── tokens.js              ← TEAL, NAVY, COLORS, SIZES
│   │   ├── PearsonConsentDialog.jsx ← S5.x
│   │   ├── SelloProtegidoBadge.jsx   ← S5.x
│   │   ├── ApoyoClinicoPanel.jsx     ← S5.x
│   │   └── GlossaryTerm.jsx          ← P4
│   ├── utils/                     ← Helpers puros
│   └── hooks/                     ← Hooks React (usePearsonConsent)
└── e2e/                           ← Playwright
    ├── smoke.spec.js
    ├── a11y.spec.js
    └── pearsonConsent.spec.js     ← S5.x
```

---

## 4. Flujo de una evaluación (alto nivel)

```
[Frontend: EvalApplyPage]
  ↓ POST /api/v1/evaluaciones
[Backend: application/use_cases]
  ↓
[Engine: ClinicalEngine.score]
  ├─ Para cada test (test_id, pd):
  │   ├─ baremos_loader.get_prueba(test_id)
  │   ├─ factory.get(tipo_calculo) → Strategy
  │   └─ strategy.calculate(...)
  └─ Resultado agregado: EngineResult
  ↓
[Frontend: EvalResultsPage]
  ├─ Integración cuantitativa-cualitativa
  ├─ Validación contra 7 principios narrativos (F6.2 + F9.2)
  └─ Redacción libre del clínico
  ↓ POST /api/v1/reports/pdf/{eval_id}
[Backend: report_pro]
  ├─ Genera PDF con metadatos PDF/A (F9.3)
  ├─ Inyecta bloque legal del encabezado (F9.3)
  └─ Footer con normograma 2026.06 (F5.3)
```

---

## 5. Reglas de evolución

| Regla | Razón |
|---|---|
| **No modificar `data/BD_NEURO_MAESTRA.json` sin consulta** | Fuente de verdad clínica. Toda divergencia debe documentarse en `docs/PLAN_MIGRACION_BAREMOS.md` (F7.2). |
| **Cambios en `domain/clinical_engine/` requieren correr 27 tests del engine** | Escalares clínicos reales. Una falla silenciosa = diagnóstico incorrecto. |
| **Ningún cambio de prompt IA en `ai_prompts.py` sin actualizar `ai_logs` schema** | Trazabilidad de uso de IA en informes (Res. 1995/1999). |
| **Las variantes PDF heredan de `NeuroPDFGeneratorPro`** | No duplicar lógica. Usar `VARIANT_LABEL`, `USE_COVER`, `INCLUDE_ANNEX`. |
| **Endpoints en `presentation/api/v1/` son HTTP-only** | Cero lógica de negocio. Use cases en `application/`. |
| **Auth global en `main.py:355`** | Todas las rutas `/api/*` requieren Bearer. Auth por ruta individual = riesgo. |
| **Conftest autouse reset DOBLE rate limiter** | Evita flakes por colisión de timestamps en suite completa. |

---

## 6. Métricas (Junio 2026)

| Métrica | Valor |
|---|---|
| Líneas de código Python backend | ~13,500 |
| Líneas de código JS frontend | ~16,200 |
| Tests backend | 910+ (855 previos + 55 nuevos Frentes 5-9) |
| Tests frontend (Node sanity) | 10 (F8.1) |
| E2E Playwright | 6 specs |
| Tablas BD (SQLAlchemy) | 14 |
| Endpoints API REST | ~50 |
| Variantes PDF | 7 (estandar, pro, pediatrico, medicolegal, junta_medica, inconcluso, paciente) |
| Pruebas baremos | 168 (102 OK + 22 validados + 3 anomalías) |
| Plantillas documentales | 17 (12 base + 5 F5.1) |
| Normas colombianas referenciadas | 17 (Bloque Legal) |

---

## 7. Referencias

- `docs/ARQUITECTURA.md` — Más detalle sobre decisiones técnicas.
- `docs/DRP.md` — Plan de recuperación ante desastres.
- `docs/seguridad/MODELO_AMENAZAS.md` — Análisis STRIDE (F10.1.13).
- `neurosoft-backend/CLAUDE.md` — Reglas críticas del backend.
- `neurosoft-frontend/CLAUDE.md` — Reglas críticas del frontend.
- `CLAUDE.md` (raíz) — Memoria del proyecto.
