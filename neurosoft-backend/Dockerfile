# syntax=docker/dockerfile:1.7
# ===============================================================
# NeuroSoft Backend — imagen de producción (multi-stage)
# ===============================================================
# Objetivos:
#   • Imagen final pequeña y sin toolchain de compilación.
#   • Usuario no-root para reducir impacto de posibles escapes.
#   • Cache de pip entre builds usando BuildKit.
#   • Listo para Compose (expone 8000, respeta variables NEUROSOFT_*).
#
# Build:
#     docker build -t neurosoft-backend:latest .
#
# Run:
#     docker run -d --name neurosoft \
#         -p 8000:8000 \
#         --env-file .env \
#         -v neurosoft_data:/app/data \
#         neurosoft-backend:latest
#
# Health:
#     curl -f http://localhost:8000/api/v1/health || exit 1

# ───────────────────────────────────────────────────────────────
# STAGE 1 — builder: instala deps en un entorno aislado
# ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /build

# Dependencias de sistema necesarias para compilar wheels
# (bcrypt, cryptography). Se descartan en el stage final.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalamos las deps en un prefijo propio para copiarlas luego.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt


# ───────────────────────────────────────────────────────────────
# STAGE 2 — runtime: imagen final
# ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NEUROSOFT_ENV=production \
    NEUROSOFT_DATA_DIR=/app/data \
    NEUROSOFT_LOG_LEVEL=INFO

# Instalamos solo runtime libs: libssl3 y libffi (cryptography las usa).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libssl3 \
        libffi8 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home --uid 1001 neurosoft

# Copiamos los paquetes Python desde el builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copiamos el código y el baremo
COPY --chown=neurosoft:neurosoft app ./app
COPY --chown=neurosoft:neurosoft alembic ./alembic
COPY --chown=neurosoft:neurosoft alembic.ini ./alembic.ini

# Directorio de datos (BD, backups, reports) persistible como volumen
RUN mkdir -p /app/data /app/data/backups /app/data/reports \
    && chown -R neurosoft:neurosoft /app/data

USER neurosoft

EXPOSE 8000

# Health-check simple contra el endpoint /api/v1/health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
