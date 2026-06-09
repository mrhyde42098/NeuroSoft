# NeuroSoft V2 — Convenciones anti-vibecode

Guía de estilo arquitectónico para evitar deuda orgánica al añadir features.

## Frontend

| Carpeta | Permite | Prohibido |
|---------|---------|-----------|
| `src/app/{feature}/` | Page shell + tabs | Fetch directo si existe hook compartido |
| `src/app/{feature}/components/` | Sub-componentes del feature | Lógica clínica pesada |
| `src/ui/` | Componentes visuales puros | `useState` de dominio clínico |
| `src/ui/forms/` | Campos reutilizables | Lógica de página completa |
| `src/hooks/` | Estado/fetch compartido | JSX |
| `src/data/` | Datos estáticos | JSX |

**Límite:** páginas `.jsx` ≤ 300 líneas sin justificación en PR.

### Estado React

- 2+ páginas → `hooks/` o `contexts.jsx`
- Formulario → `useFormState` o `useReducer` (no 5+ `useState` sueltos)
- Selector paciente → `PatientSelector` + `usePatientsPanel`

### Formularios (checklist)

1. `FormField` / `FieldBlock`
2. Paciente → `PatientSelector`
3. EPS/CUPS → `ColombiaBillingFields`
4. 8+ keys de estado → `useFormState`

## Backend

| Capa | Puede importar | No puede importar |
|------|----------------|-------------------|
| `presentation/api/v1/` | use_cases, dtos, dependencies | `orm_models` directo |
| `application/use_cases/` | domain, repos, dtos | FastAPI, HTTPException |
| `infrastructure/repositories/` | orm_models | FastAPI |
| `domain/` | nada externo | SQLAlchemy, FastAPI |

**Límite:** routes ≤ 150 líneas; use_cases ≤ 400 líneas.

### Endpoint nuevo (checklist)

1. DTO en `application/dtos/`
2. Lógica en use case
3. Persistencia en repository
4. Errores de dominio (`ApplicationError`), no strings sueltos
5. DI en `dependencies.py`
6. Test de integración mínimo
7. Un solo router por prefijo (`/backup/` → `documents.backup_router_new` únicamente)

## Errores

API: `{ "code": "...", "message": "...", "details": {} }`

Frontend: `api/client.js` mapea códigos; `RouteErrorBoundary` por feature.

## Reglas STOP para IAs

- **STOP:** no añadir a monolitos > 300 líneas — extraer primero
- **STOP:** no duplicar `patients/panel` — usar `usePatientsPanel`
- **STOP:** no Pydantic inline en routes
- **STOP:** no algoritmos clínicos en JSX
- **ASK:** cambios en scoring/baremos → ejecutar tests ground-truth

## CI guards

Ejecutados en GitHub Actions (`backend-ci.yml`, `frontend-ci.yml`) y vía `python tools/run_quality_gates.py`:

- `python tools/check_v2_guards.py` — alerta `.jsx` en `src/app/` > 400 líneas; routes con `db.query` / `db.add` directo
- `python tools/api_manifest_check.py` — alineación métodos HTTP frontend↔backend (baseline en `tools/api_manifest_baseline.json`)
