# Mejoras sugeridas post-upgrade (jun 2026)

Tras migrar a **FastAPI 0.136**, **React 19** y **Vite 6**.

## Backend (FastAPI / Pydantic 2.10)

| Área | Mejora | Prioridad |
|------|--------|-----------|
| OpenAPI | Test `tests/unit/test_openapi_schema.py` + revisar `/docs` | ✅ |
| Lifespan | Consolidado en `lifespan` async (`main.py`) | ✅ |
| Dependencies | `CurrentUser` / `AdminUser` como `Annotated[..., Depends]` | ✅ |
| Tests CI | Pin `fastapi==0.136.3` en `requirements.txt` | ✅ |

## Frontend (React 19 / Vite 6)

| Área | Mejora | Prioridad |
|------|--------|-----------|
| Bundle | `LazyRoute` + `use()`, `AIFloatingChat` lazy, `DomainAnalysisLazy`, chunk `therapy` | ✅ |
| React 19 | Rutas con `use()` vía `src/ui/LazyRoute.jsx` | ✅ |
| Strict Mode | Timers en `EvalApplyPage` con cleanup explícito | ✅ |
| ESLint | `eslint-plugin-react-hooks` ^5.2.0 | ✅ |

## Baremos

| Área | Mejora | Prioridad |
|------|--------|-----------|
| Lazy load | Materialización por `test_id` en `baremos_loader.py` | ✅ |
| Shards | `docs/scripts/split_baremos_poblacion.py` + loader modo `baremos_shards/` | ✅ |

## Herramientas titular

| Herramienta | Uso |
|-------------|-----|
| `dist/NeuroSoft-LicenseAdmin.exe` | Generar claves NSFT (GUI) |
| `python admin_license_app.py` | Mismo panel desde código |
| `docs/GUIA_PROTECCION_Y_LICENCIAS.md` | Flujo completo IP + beta |

## Regenerar shards (opcional, reduce RAM cold start)

```bash
python docs/scripts/split_baremos_poblacion.py
```

El loader detecta automáticamente `data/baremos_shards/manifest.json` junto al JSON maestro.

## Integración Inspector General (7 jun 2026)

| Área | Estado |
|------|--------|
| pytest suite | 1034+ passed |
| ESLint | 0 errors (build gate OK) |
| QW-6 etiquetas | ✅ backend + PatientsPage |
| QW-8 backup schedule | ✅ migración 011 + BackupTab + scheduler + router único |
| Alineación API jun-2026 | ✅ therapy PATCH, backup body, agenda mes + profesional_id |
| InformesPage glosario | ✅ GlossaryLegend |
| Build desktop | ✅ exe ~48 MB + Setup ~1.3 GB |
