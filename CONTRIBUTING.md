# Contribuir a NeuroSoft

Gracias por interesar en NeuroSoft. Este proyecto es software de apoyo
neuropsicológico con baremos normativos colombianos; los cambios en el
motor clínico tienen impacto directo en diagnósticos.

**Maintainer principal:** Johan Sebastián Salgado Sarmiento ([@mrhyde42098](https://github.com/mrhyde42098))

## Antes de abrir un PR

1. **Backend:** `cd neurosoft-backend && pytest tests/`
2. **Frontend:** `cd neurosoft-frontend && npm run lint && npm run build`
3. Si tocas `strategies.py`, `baremos_loader.py` o `engine.py`, el agente
   `clinical-engine-reviewer` debe pasar (ver `.claude/agents/`).

## Qué no modificar sin aprobación del maintainer

- Valores numéricos en `neurosoft-backend/data/BD_NEURO_MAESTRA.json`
- Cambios de plataforma (Electron, PostgreSQL, TypeScript, etc.)

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
