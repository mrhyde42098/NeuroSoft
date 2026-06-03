# NeuroSoft

Plataforma de evaluación neuropsicológica para uso clínico.

NeuroSoft automatiza la calificación de baterías neuropsicológicas usando
baremos normativos colombianos, genera informes PDF/Word listos para la
historia clínica, y administra el ciclo completo del paciente: recepción,
anamnesis, calificación, evolución terapéutica y reportes RIPS
(Resolución 2275/2023).

| Módulo | Stack |
|---|---|
| Backend | FastAPI · SQLAlchemy · SQLite (WAL) · Python 3.11+ |
| Frontend | React · Vite · TypeScript |
| Motor | 15 strategies de calificación · 152 pruebas normadas |
| Empaquetado | Docker · PyInstaller (desktop) |

---

## Inicio rápido (Docker)

```bash
git clone <repo>
cd NeuroSoftApp/neurosoft-backend
cp .env.example .env           # editar secretos
docker compose up -d --build
curl http://localhost:8000/api/v1/health
```

Primer login: `admin` / valor de `NEUROSOFT_ADMIN_PASSWORD` del `.env`.
**Cambiar esa contraseña inmediatamente tras el primer login.**

---

## Desarrollo local (sin Docker)

```bash
cd neurosoft-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Variables mínimas de desarrollo
export NEUROSOFT_ENV=development
export NEUROSOFT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")

uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd neurosoft-frontend
npm install
npm run dev
```

---

## Arquitectura

```
neurosoft-backend/
├── app/
│   ├── core/                   # config, excepciones, branding, upload validation, PII redactor
│   ├── domain/                 # entidades puras, motor de calificación (Strategy pattern)
│   │   ├── entities/
│   │   └── clinical_engine/    # loader de baremos, 15 strategies, ClinicalEngine
│   ├── application/            # use cases, DTOs (Pydantic)
│   ├── infrastructure/         # SQLAlchemy, repositorios, auth, email, PDF, RIPS
│   │   ├── database/
│   │   ├── repositories/
│   │   └── auth/
│   └── presentation/           # FastAPI routers y dependencias
│       └── api/v1/
├── alembic/                    # migraciones de BD
├── tests/                      # unit + integration
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

Separación de capas según Clean Architecture + DDD. El dominio no depende
de FastAPI ni de SQLAlchemy; esas son inyecciones de la capa de
infraestructura.

---

## Seguridad

El sistema asume despliegue on-premise en una clínica pequeña/mediana y
aplica defensas apropiadas para ese contexto:

- **JWT con SECRET_KEY obligatoria en producción** (≥ 32 caracteres; el
  arranque aborta si no está o si conserva el valor de desarrollo).
- **Contraseña admin obligatoria** en producción (≥ 8 caracteres, no puede
  quedar vacía ni valer el default).
- **Hashing de contraseñas con bcrypt** (cost 12 por defecto; compatibilidad
  retroactiva con hashes SHA-256 legacy para no romper sesiones existentes).
- **Rate limiting global** por IP (configurable; 120 req/min por defecto).
- **CORS estricto** en producción — rechaza `"*"` cuando `allow_credentials=True`.
- **Docs deshabilitadas** en producción salvo opt-in explícito
  (`NEUROSOFT_EXPOSE_DOCS=1`).
- **Redactor de PII en logs** (ver `app/core/logging_redactor.py`) que
  intercepta emails, teléfonos, JWT, cédulas y pares clave=valor sensibles
  antes de que lleguen al handler.
- **Validación estructural de uploads**: magic bytes + extensión + tamaño
  máximo configurable. SVG rechazado explícitamente (XSS).
- **Soft-delete de pacientes** (Resolución 1995 de 1999 — las historias
  clínicas no se borran, se archivan con `archived_at/by/reason`).
- **Versionado de baremos**: cada evaluación guarda `baremo_version` y
  `baremo_checksum` (SHA-256) para trazabilidad clínica.

Revisar [`docs/legal/HABEAS_DATA.md`](docs/legal/HABEAS_DATA.md) para las
obligaciones del operador bajo la Ley 1581 de 2012.

---

## Testing

```bash
cd neurosoft-backend
pytest tests/                         # todos
pytest tests/unit/ -q                 # solo unit
pytest tests/integration/ -q          # solo integration
pytest --cov=app --cov-report=html    # cobertura
```

CI: ver `.github/workflows/backend-ci.yml` (lint + tests + docker build + scans).

---

## Migraciones de base de datos

```bash
cd neurosoft-backend
alembic upgrade head                  # aplicar migraciones
alembic revision -m "mi cambio"       # crear nueva
alembic downgrade -1                  # revertir una
```

En desarrollo, la app también aplica *patches aditivos* automáticos al
arrancar (ver `app/infrastructure/database/engine.py::_apply_additive_schema_patches`)
para añadir columnas nuevas en bases que ya existían, sin forzar al
operador a correr Alembic manualmente.

---

## Licencia

Apache License 2.0 con adenda clínica — ver `LICENSE`.

Este software es una herramienta de apoyo profesional; **no reemplaza
el juicio clínico** y **no está certificado como dispositivo médico**.
El uso es responsabilidad exclusiva del profesional calificado.

---

## Contribuciones

Issues y PRs bienvenidos. Antes de abrir un PR:

1. `pytest tests/` debe pasar.
2. `ruff check app tests` debe pasar (cuando salga del modo "no bloqueante").
3. Si el cambio toca datos clínicos o auditables, describir impacto
   regulatorio en el PR (Ley 1581, Resolución 2275, Resolución 1995).
