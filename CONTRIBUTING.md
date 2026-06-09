# Contribuir a NeuroSoft

Gracias por interesar en NeuroSoft. Este proyecto es software de apoyo
neuropsicológico con baremos normativos colombianos; los cambios en el
motor clínico tienen impacto directo en diagnósticos.

**Maintainer principal:** Johan Sebastián Salgado Sarmiento ([@mrhyde42098](https://github.com/mrhyde42098))

## Antes de abrir un PR

1. **Gates unificados:** `python tools/run_quality_gates.py --with-build` (desde la raíz)
2. **Backend:** `cd neurosoft-backend && pytest tests/`
3. **Frontend:** `cd neurosoft-frontend && npm run lint && npm run build`
4. **Arquitectura V2:** `python tools/check_v2_guards.py` y `python tools/api_manifest_check.py`
5. Si tocas `strategies.py`, `baremos_loader.py` o `engine.py`, el agente
   `clinical-engine-reviewer` debe pasar (ver `.claude/agents/`).

### Cuándo usar Inspector General vs otros agentes

| Situación | Herramienta |
|-----------|-------------|
| Antes de release beta o build amplio | `/inspector-general` (skill en `.claude/skills/inspector-general/`) |
| Bug puntual en un archivo | `/audit-completo <archivo>` |
| Cambio en motor de scoring | `clinical-engine-reviewer` |
| Cambios API frontend/backend | `api-alignment-reviewer` |
| Cerrar sprint y actualizar backlog | `/actualizar-estado-vivo` |

## Qué no modificar sin aprobación del maintainer

- Valores numéricos en `neurosoft-backend/data/BD_NEURO_MAESTRA.json`
- Cambios de plataforma (Electron, PostgreSQL, TypeScript, etc.)

## Material protegido (no subir al repo)

| Archivo / carpeta | Motivo |
|---|---|
| `reactivosPearson.generated.js` con claves | Tras `sync_reactivos_from_protocol.py` — usar stub OSS en git |
| `docs/generated/*_extract.txt`, `wisc_*.txt`, `wais_*.txt` | Texto verbatim Pearson |
| `neurosoft-backend/data/baremos_shards/` | Regenerable en build |
| `licenses_*.csv`, `license_history.json` | Claves de licencia beta |
| `dist/`, `vendor/`, `.env` | Binarios y secretos |

El repo público incluye **stub vacío** de reactivos Pearson. Clones OSS compilan;
la evaluación interactiva WISC/WAIS requiere generar reactivos en local con licencia.

## Estructura del monorepo

| Carpeta | Rol |
|---------|-----|
| `neurosoft-backend/` | FastAPI, motor clínico, PDF, API REST |
| `neurosoft-frontend/` | React 18 + Vite (JSX) |
| `docs/` | Arquitectura, estado vivo, casos clínicos |
| `.github/workflows/` | CI backend + frontend |

## Issues abiertos (roadmap público)

Ver [Issues](https://github.com/mrhyde42098/NeuroSoft/issues) o `docs/ESTADO_VIVO.md`
para el estado actual. Temas bienvenidos:

- Regresiones del motor de baremos
- Accesibilidad y modo oscuro en UI
- Documentación de API y despliegue
- Tests E2E del flujo paciente → evaluación → informe PDF

## Seguridad

No abrir issues públicos con datos de pacientes reales. Para vulnerabilidades,
describe el impacto sin PHI y referencia archivos concretos.

## Licencia

Al contribuir, aceptas que tu código se licencie bajo Apache 2.0 (ver `LICENSE`).
