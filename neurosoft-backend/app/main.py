"""
app/main.py
============
Punto de entrada de NeuroSoft Backend v2.0.

Instancia FastAPI, registra middlewares, conecta routers y
gestiona el ciclo de vida (startup / shutdown).

Para ejecutar:
    uvicorn app.main:app --reload --port 8000

Documentación:
    http://localhost:8000/docs   (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import (
    ApplicationError,
    DomainError,
    InfrastructureError,
)

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    # `%(rid)s` lo inyecta el PIIRedactor (ver core/logging_redactor.py).
    # Vale "-" cuando no hay request en curso (startup, scheduler, etc.).
    format="%(asctime)s | %(levelname)-8s | rid=%(rid)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("neurosoft")

# Instalar redactor de PII (Habeas Data / Ley 1581). Debe hacerse
# DESPUÉS de basicConfig para que el filtro alcance los handlers
# creados por éste. Ver app/core/logging_redactor.py para el listado
# de patrones cubiertos.
from app.core.logging_redactor import install_pii_redactor  # noqa: E402

install_pii_redactor()


# ─────────────────────────────────────────────────────────────
# Helpers de empaquetado (PyInstaller + frontend estático)
# ─────────────────────────────────────────────────────────────

def _get_static_dir() -> Path | None:
    """
    Devuelve el directorio del frontend compilado si existe.

    - En modo desarrollo: neurosoft-frontend/dist (ignorado si no está compilado).
    - En modo empaquetado (PyInstaller): <bundle>/static.
    """
    if getattr(sys, "frozen", False):
        bundle = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        candidate = bundle / "static"
    else:
        candidate = Path(__file__).parent.parent.parent / "neurosoft-frontend" / "dist"
    return candidate if candidate.exists() and (candidate / "index.html").exists() else None


def _get_bundled_asset(rel: str) -> Path | None:
    """Localiza un asset incluido en el bundle (baremos, icono, etc.)."""
    if getattr(sys, "frozen", False):
        bundle = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        bundle = Path(__file__).parent.parent.parent
    candidate = bundle / rel
    return candidate if candidate.exists() else None


def _bootstrap_default_assets() -> None:
    """
    Si es la primera vez que se ejecuta (datos del usuario vacíos),
    copia el JSON de baremos empaquetado al directorio de datos.
    """
    try:
        # BD_NEURO_MAESTRA.json
        if not settings.baremo_path.exists():
            for candidate_rel in ("data/BD_NEURO_MAESTRA.json",
                                  "neurosoft-backend/data/BD_NEURO_MAESTRA.json"):
                src = _get_bundled_asset(candidate_rel)
                if src:
                    settings.baremo_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, settings.baremo_path)
                    logger.info("📦 Baremo inicial copiado a: %s", settings.baremo_path)
                    break
    except Exception as e:
        logger.warning("⚠️  Bootstrap de assets falló: %s", e)


# ─────────────────────────────────────────────────────────────
# Ciclo de vida
# ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:
        1. Inicializar BD SQLite (crear tablas).
        2. Cargar BD_NEURO_MAESTRA.json en memoria.
    Shutdown:
        (Sin cleanup necesario — SQLite cierra las conexiones solo)
    """
    # ── STARTUP ──────────────────────────────────────────────
    import time as _t
    app.state.started_at = _t.time()
    logger.info("=" * 55)
    logger.info("  NeuroSoft API v%s — Iniciando...", settings.api_version)
    logger.info("  Entorno: %s", settings.env)
    logger.info("  Datos: %s", settings.db_path.parent)
    logger.info("=" * 55)

    # 0.a. Verificar invariantes de producción (secretos, CORS, etc.)
    try:
        problems = settings.enforce_production_invariants()
    except Exception:  # §H6-fix: loggear el traceback en vez de tragarlo
        logger.exception("Error al evaluar invariantes de producción")
        problems = []
    if problems:
        logger.error("❌ Invariantes de producción violados:")
        for p in problems:
            logger.error("   • %s", p)
        raise RuntimeError(
            "Configuración insegura para producción: "
            + "; ".join(problems)
        )

    # 0.b. Bootstrap: copiar baremo por defecto si no existe (modo empaquetado)
    _bootstrap_default_assets()

    # 1. Inicializar base de datos
    from app.infrastructure.database.engine import init_database
    init_database()

    # 1.b. Registrar listeners de auditoría sobre Session
    try:
        from app.infrastructure.audit import register_audit_listeners
        register_audit_listeners()
        logger.info("✅ Audit listeners activos (trazabilidad Resolución 1995)")
    except Exception as e:
        logger.warning("⚠️  No se pudieron registrar audit listeners: %s", e)

    # 2. Cargar baremos en memoria
    from app.domain.clinical_engine.baremos_loader import BaremosLoader
    try:
        loader = BaremosLoader.load(settings.baremo_path)
        app.state.baremo_loaded = True
        app.state.baremo_loader = loader
        logger.info("✅ Baremos cargados: %d pruebas", loader.total_pruebas)
    except Exception as e:
        app.state.baremo_loaded = False
        app.state.baremo_loader = None
        logger.warning("⚠️  Baremos no disponibles: %s", e)
        logger.warning("   Copia BD_NEURO_MAESTRA.json a data/ para habilitar calificación.")

    # 2.b. Seed del catálogo de actividades de rehabilitación (idempotente)
    try:
        from app.application.use_cases.rehab_use_cases import seed_activity_catalog
        from app.infrastructure.database.engine import get_session
        _db = next(get_session())
        try:
            seed_activity_catalog(_db)
        finally:
            _db.close()
    except Exception as e:
        logger.warning("⚠️  No se pudo sembrar el catálogo de rehabilitación: %s", e)

    # 3. Crear usuario admin por defecto si no existe ningún usuario
    try:
        from app.infrastructure.auth.auth_service import UserRepository
        from app.infrastructure.database.engine import get_session
        db = next(get_session())
        repo = UserRepository(db)
        # Dejar que ensure_admin_exists resuelva la contraseña según el entorno
        repo.ensure_admin_exists()
        repo.ensure_beta_tester_exists()
        db.close()
    except RuntimeError:
        # En producción, una contraseña insegura debe abortar el arranque
        raise
    except Exception as e:
        logger.warning("⚠️  No se pudo verificar usuario admin: %s", e)

    logger.info("✅ NeuroSoft listo en http://localhost:8000")

    # 4. Iniciar scheduler de tareas programadas
    from app.infrastructure.scheduler_service import start_scheduler
    start_scheduler()

    # 5. Auto-instalar Ollama al PRIMER arranque (solo Windows, solo si bundled).
    #    Esto se hace en background para no bloquear el inicio del backend.
    #    Si Ollama ya está corriendo, no hace nada. Se ejecuta una sola vez
    #    (deja un flag en settings.data_dir/.ollama_install_attempted).
    try:
        import asyncio as _asyncio

        from app.infrastructure.ollama_bootstrap import auto_install_ollama_first_run
        _asyncio.create_task(auto_install_ollama_first_run())
    except Exception as e:
        logger.debug("Auto-install Ollama no disponible: %s", e)

    # Estímulos PDF masivos: limpieza en background (no bloquea /health del .exe)
    try:
        import asyncio

        async def _stimuli_cleanup_bg() -> None:
            try:
                from app.infrastructure.database.engine import get_session
                from app.infrastructure.stimuli_bootstrap import bootstrap_stimuli

                db = next(get_session())
                try:
                    bootstrap_stimuli(settings.db_path.parent, db)
                finally:
                    db.close()
            except Exception as exc:
                logger.warning("Bootstrap estímulos (background): %s", exc)

        asyncio.create_task(_stimuli_cleanup_bg())
    except Exception as e:
        logger.debug("No se programó limpieza de estímulos: %s", e)

    yield  # ── La app corre aquí ──

    # ── SHUTDOWN ─────────────────────────────────────────────
    from app.infrastructure.scheduler_service import stop_scheduler
    stop_scheduler()
    logger.info("NeuroSoft detenido.")


# ─────────────────────────────────────────────────────────────
# Instancia FastAPI
# ─────────────────────────────────────────────────────────────

_EXPOSE_DOCS = (
    settings.effective_expose_docs()
    if hasattr(settings, "effective_expose_docs")
    else True
)

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs" if _EXPOSE_DOCS else None,
    redoc_url="/redoc" if _EXPOSE_DOCS else None,
    openapi_url="/openapi.json" if _EXPOSE_DOCS else None,
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────────
# Auth Middleware — protege todas las rutas excepto las públicas
# ─────────────────────────────────────────────────────────────

# Rutas que NO requieren autenticación
_PUBLIC_PATHS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
}

# Prefijos públicos (para rutas con token dinámico, ej. telemedicina,
# vista pública de informes, viewer de actividades de rehabilitación
# que el paciente abre desde su casa).
_PUBLIC_PREFIXES = (
    "/api/v1/shared/view/",
    "/api/v1/public/rehab/",
)

# ─────────────────────────────────────────────────────────────
# Rate limiter global (sliding window in-memory, por IP)
# ─────────────────────────────────────────────────────────────

import time as _time
from collections import deque
from threading import Lock as _Lock

_RL_LOCK = _Lock()
_RL_BUCKETS: dict[str, deque[float]] = {}
_RL_WINDOW = 60.0  # 1 minuto


def _rate_limit_check(client_ip: str) -> bool:
    """Devuelve True si la petición se acepta, False si excede el límite."""
    limit = int(getattr(settings, "rate_limit_per_min", 0) or 0)
    if limit <= 0:
        return True
    now = _time.time()
    with _RL_LOCK:
        dq = _RL_BUCKETS.setdefault(client_ip, deque())
        # Purga eventos fuera de la ventana
        cutoff = now - _RL_WINDOW
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= limit:
            return False
        dq.append(now)
    return True


import uuid as _uuid

from app.core.request_context import current_request_id as _current_rid


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """
    Asigna un identificador único por request (UUID4) y lo expone como
    header `X-Request-ID` en la respuesta. Permite correlacionar logs +
    eventos de auditoría + reportes de error de un mismo request.

    Si el cliente envía su propio `X-Request-ID`, lo respetamos (útil
    para trazabilidad end-to-end con un balanceador o gateway).

    También setea la ContextVar global `current_request_id` para que
    el filtro de logging y el servicio de auditoría puedan recuperarlo
    sin tener que pasar `request` por cada capa.
    """
    raw = request.headers.get("X-Request-ID") or _uuid.uuid4().hex
    # Sanitizar — el header viene del cliente. Caracteres no imprimibles
    # podrían inyectar secuencias de control en los logs (log forging).
    rid = "".join(ch for ch in raw if ch.isalnum() or ch in "-_")[:64] or _uuid.uuid4().hex
    request.state.request_id = rid
    rid_token = _current_rid.set(rid)
    try:
        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", rid)
        return response
    finally:
        _current_rid.reset(rid_token)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Limita globalmente las peticiones por IP en una ventana deslizante."""
    # No limitar preflight CORS ni rutas estáticas
    if request.method == "OPTIONS" or not request.url.path.startswith("/api/"):
        return await call_next(request)
    client_ip = request.client.host if request.client else "unknown"
    if not _rate_limit_check(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Demasiadas solicitudes. Espera un momento antes de reintentar.",
                "code": "RATE_LIMIT_EXCEEDED",
            },
            headers={"Retry-After": "60"},
        )
    return await call_next(request)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """
    Valida el Bearer token en todas las rutas protegidas.
    Las rutas públicas (_PUBLIC_PATHS) se dejan pasar sin token.
    En modo desarrollo (settings.env == 'dev') se puede deshabilitar
    poniendo NEUROSOFT_DISABLE_AUTH=1 en el .env.
    """
    path = request.url.path

    # Permitir rutas públicas y preflight CORS
    if request.method == "OPTIONS" or path in _PUBLIC_PATHS:
        return await call_next(request)
    if any(path.startswith(p) for p in _PUBLIC_PREFIXES):
        return await call_next(request)

    # Permitir assets estáticos del SPA (JS, CSS, imágenes, fuentes, favicon...)
    # Solo los endpoints /api requieren autenticación.
    if not path.startswith("/api/"):
        return await call_next(request)

    # §S0.4 — ELIMINADO el kill-switch NEUROSOFT_DISABLE_AUTH / disable_auth.
    # Era un riesgo crítico: con esa flag, TODA la API quedaba sin auth,
    # incluyendo endpoints sensibles (update.py, patients.py). Los devs
    # ahora deben usar un JWT válido siempre.
    # Si necesitas un bypass para tests E2E automatizados, hazlo en un
    # entorno aislado y con tokens de corta duración generados ad-hoc.
    _disable_auth_env = os.getenv("NEUROSOFT_DISABLE_AUTH", "0") == "1"
    if _disable_auth_env:
        logger.warning(
            "NEUROSOFT_DISABLE_AUTH está activa pero es IGNORADA "
            "(eliminado en Sprint 0, S0.4). Todas las rutas /api/* "
            "requieren Bearer token válido."
        )

    # Verificar token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=401,
            content={"detail": "Token de autenticación requerido.", "code": "UNAUTHORIZED"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", 1)[1]
    try:
        from app.infrastructure.auth.auth_service import decode_access_token
        payload = decode_access_token(token)
        # Adjuntar datos del usuario al request state para los endpoints
        request.state.user_id    = payload["sub"]
        request.state.user_role  = payload.get("role", "profesional")
        request.state.user_label = payload.get("username") or payload["sub"][:8]
        request.state.token_jti  = payload.get("jti", "")
    except ValueError as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=401,
            content={"detail": str(e), "code": "TOKEN_INVALID"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Bloqueo por lista negra: si el token fue revocado (logout / admin),
    # aunque siga siendo criptográficamente válido debe rechazarse.
    jti = payload.get("jti")
    user_id = payload.get("sub", "")
    iat = payload.get("iat")
    if jti or user_id:
        try:
            from app.infrastructure.auth.auth_service import (
                is_token_revoked,
                is_user_session_revoked,
            )
            from app.infrastructure.database.engine import SessionLocal
            _check_db = SessionLocal()
            try:
                if jti and is_token_revoked(_check_db, jti):
                    return JSONResponse(
                        status_code=401,
                        content={
                            "detail": "Token revocado (sesión cerrada).",
                            "code": "TOKEN_REVOKED",
                        },
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                if user_id and is_user_session_revoked(_check_db, user_id, iat):
                    return JSONResponse(
                        status_code=401,
                        content={
                            "detail": (
                                "Sesión invalidada (cambio de contraseña "
                                "o revocación administrativa)."
                            ),
                            "code": "SESSION_INVALIDATED",
                        },
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            finally:
                _check_db.close()
        except Exception as _exc:  # noqa: BLE001
            from app.core.config import settings

            if settings.env == "production":
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": "No se pudo validar la sesión. Intente de nuevo.",
                        "code": "SESSION_CHECK_UNAVAILABLE",
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
            logger.warning(
                "No se pudo consultar la blacklist (%s). Continuando (dev).",
                _exc,
            )

    # Propagar actor al ContextVar de auditoría para los listeners ORM
    try:
        from app.infrastructure.audit import current_actor_id, current_actor_label, current_ip
        actor_tok = current_actor_id.set(request.state.user_id)
        ip_tok = current_ip.set(request.client.host if request.client else None)
        label_tok = current_actor_label.set(payload.get("username") or request.state.user_id[:8])
        try:
            return await call_next(request)
        finally:
            current_actor_id.reset(actor_tok)
            current_actor_label.reset(label_tok)
            current_ip.reset(ip_tok)
    except Exception:
        return await call_next(request)

# ─────────────────────────────────────────────────────────────
# Security Headers Middleware — defensas básicas contra ataques
# comunes (XSS, clickjacking, MIME sniffing, fuga de Referer, etc.)
# ─────────────────────────────────────────────────────────────

# Encabezados que se añaden a TODA respuesta servida por la API.
# - X-Content-Type-Options: nosniff       → desactiva MIME sniffing del browser
# - X-Frame-Options: DENY                 → bloquea iframing (clickjacking)
# - Referrer-Policy: strict-origin-when-cross-origin → no filtrar URLs sensibles
# - Permissions-Policy: bloquea APIs del navegador no usadas (geo, mic, etc.)
# - Strict-Transport-Security (solo en producción HTTPS): fuerza TLS 1 año
# - X-Permitted-Cross-Domain-Policies: none → bloquea Adobe legacy
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": (
        "geolocation=(), microphone=(), camera=(), "
        "payment=(), usb=(), magnetometer=(), accelerometer=()"
    ),
    "X-Permitted-Cross-Domain-Policies": "none",
}


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """
    Inyecta encabezados de seguridad en cada respuesta. Cumple con
    OWASP Secure Headers + buenas prácticas para apps clínicas.

    S4.2: también cuenta requests en el sistema de métricas opt-in.
    """
    import time as _t
    t0 = _t.perf_counter()
    response = await call_next(request)
    elapsed_ms = (_t.perf_counter() - t0) * 1000.0
    for k, v in _SECURITY_HEADERS.items():
        # No sobreescribir si el endpoint ya puso uno explícito
        response.headers.setdefault(k, v)
    # HSTS solo en producción — evita que el browser cachee HTTPS-only
    # cuando el dev arranca con http://localhost.
    if settings.env == "production":
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    # Métricas opt-in (S4.2): nunca envía PHI
    from app.infrastructure.observability import metrics
    if metrics._is_enabled():
        path = request.url.path
        # Sanitizar paths con IDs
        if path.startswith("/api/"):
            method = request.method
            status = response.status_code
            metrics.counter_inc(f"http_requests_total{{method={method}}}")
            metrics.histogram_observe("http_request_duration_ms", elapsed_ms)
            metrics.counter_inc(f"http_responses_total{{status={status}}}")
    return response


# ─────────────────────────────────────────────────────────────
# CORS Middleware — DEBE registrarse DESPUÉS del auth middleware
# para que sea el middleware más externo y añada headers CORS
# a TODAS las respuestas (incluidas las 401 del auth).
# ─────────────────────────────────────────────────────────────

# Si los orígenes están en wildcard ["*"], no se pueden mezclar con
# allow_credentials=True (el navegador rechaza la respuesta). Desactivamos
# credenciales en ese caso para no romper silenciosamente las llamadas.
_cors_origins = list(settings.cors_origins or [])
_allow_credentials = True
if "*" in _cors_origins:
    _allow_credentials = False
    if settings.env != "development":
        logger.warning(
            "⚠️  CORS con '*' y allow_credentials desactivado. "
            "Configura NEUROSOFT_CORS_ORIGINS con dominios específicos."
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Exception Handlers globales
# Convierten excepciones de dominio en respuestas HTTP coherentes
# ─────────────────────────────────────────────────────────────

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=422, content=exc.to_dict())


@app.exception_handler(ApplicationError)
async def application_error_handler(request: Request, exc: ApplicationError):
    status_map = {
        "PATIENT_ALREADY_EXISTS": 409,
        "PATIENT_NOT_FOUND": 404,
        "EVALUATION_NOT_FOUND": 404,
        "INVALID_PROTOCOL": 422,
    }
    code = status_map.get(exc.code, 422)
    return JSONResponse(status_code=code, content=exc.to_dict())


@app.exception_handler(InfrastructureError)
async def infrastructure_error_handler(request: Request, exc: InfrastructureError):
    status_map = {
        "BAREMO_DB_NOT_LOADED": 503,
        "DATABASE_ERROR": 503,
        "REPORT_GENERATION_ERROR": 500,
    }
    code = status_map.get(exc.code, 500)
    return JSONResponse(status_code=code, content=exc.to_dict())


# ─────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────

from datetime import UTC

from app.presentation.api.router import api_v1_router  # noqa: E402
from app.presentation.api.v1 import observability as _obs_router  # noqa: E402

app.include_router(api_v1_router)
app.include_router(_obs_router.router)


# ─────────────────────────────────────────────────────────────
# Endpoints del sistema
# ─────────────────────────────────────────────────────────────

_STATIC_DIR = _get_static_dir()


@app.get("/", tags=["Sistema"], include_in_schema=False)
def root():
    """
    Raíz de la aplicación:
    - Si el frontend compilado existe → sirve index.html (modo empaquetado).
    - En desarrollo puro (sin `npm run build`) → devuelve metadatos JSON.

    §pywebview-fix (2026-05-18): WebView2 cachea agresivamente el HTML raíz
    entre lanzamientos del .exe. Forzamos headers no-cache para que el HTML
    SIEMPRE se sirva fresco al arrancar. Los assets hasheados (/assets/*.js)
    sí se pueden cachear porque su nombre cambia con cada build.
    """
    no_cache_headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    if _STATIC_DIR:
        return FileResponse(_STATIC_DIR / "index.html", headers=no_cache_headers)
    return JSONResponse({
        "sistema": "NeuroSoft API",
        "version": settings.api_version,
        "estado": "operativo",
        "docs": "/docs",
        "redoc": "/redoc",
    }, headers=no_cache_headers)


@app.get("/index.html", tags=["Sistema"], include_in_schema=False)
def root_index_html():
    """Alias explícito para /index.html con los mismos headers no-cache."""
    return root()


@app.get("/sw.js", tags=["Sistema"], include_in_schema=False)
def service_worker_js():
    """
    §pywebview-fix: el Service Worker antiguo debe poder ser desplazado
    al primer arranque tras una actualización. Servimos sw.js sin caché
    Y NEUTRALIZADO en pywebview — un SW vacío que sólo se desregistra a
    sí mismo cuando se activa.
    """
    no_cache_headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "Content-Type": "application/javascript; charset=utf-8",
        # Permite que el SW controle la raíz aunque viva en otro path.
        "Service-Worker-Allowed": "/",
    }
    # SW kill-switch: cualquier registro previo se desregistra sí mismo.
    # Esto neutraliza el SW v3/v4 viejo que pueda quedar en WebView2.
    kill_switch_js = (
        "/* NeuroSoft SW kill-switch — desregistra cualquier SW residual. */\n"
        "self.addEventListener('install', () => { self.skipWaiting(); });\n"
        "self.addEventListener('activate', (e) => {\n"
        "  e.waitUntil((async () => {\n"
        "    try {\n"
        "      const keys = await caches.keys();\n"
        "      await Promise.all(keys.map(k => caches.delete(k)));\n"
        "    } catch (e) {}\n"
        "    try { await self.registration.unregister(); } catch (e) {}\n"
        "    try {\n"
        "      const cs = await self.clients.matchAll();\n"
        "      cs.forEach(c => c.navigate(c.url));\n"
        "    } catch (e) {}\n"
        "  })());\n"
        "});\n"
    )
    from fastapi.responses import Response
    return Response(content=kill_switch_js, headers=no_cache_headers)


@app.get("/health", tags=["Sistema"], summary="Health check")
def health():
    """
    Estado del sistema. Usado por monitoreo y el frontend demo.

    Incluye:
    - **db**: ping real a SQLite (`SELECT 1`). Si falla → status=unhealthy (HTTP 200 aún,
      los orquestadores leen el campo `status`).
    - **baremo**: si está cargado, reporta checksum y cantidad de pruebas.
    - **disk**: espacio libre en el directorio de datos (alerta si < 500 MB).
    - **uptime_seconds**: segundos desde el arranque del proceso.
    """
    import shutil
    import time as _t

    from sqlalchemy import text

    from app.infrastructure.database.engine import _engine  # type: ignore

    # ─── DB ping ────────────────────────────────────────────
    db_status: dict[str, object] = {"ok": False}
    try:
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1")).scalar()
        db_status["ok"] = True
    except Exception as exc:  # noqa: BLE001
        db_status["error"] = type(exc).__name__

    # ─── Baremo ─────────────────────────────────────────────
    baremo_info: dict[str, object] = {
        "loaded": bool(getattr(app.state, "baremo_loaded", False)),
    }
    loader = getattr(app.state, "baremo_loader", None)
    if loader is not None:
        try:
            baremo_info["total_pruebas"] = loader.total_pruebas
            baremo_info["version"] = loader.baremo_version
            checksum = loader.baremo_checksum
            # Solo los primeros 12 chars del checksum — suficiente para detectar
            # cambios, no expone el hash completo en el healthcheck público.
            baremo_info["checksum"] = checksum[:12] if checksum else None
        except Exception:  # noqa: BLE001
            pass

    # ─── Disk ───────────────────────────────────────────────
    disk_info: dict[str, object] = {}
    try:
        usage = shutil.disk_usage(settings.db_path.parent)
        free_mb = usage.free // (1024 * 1024)
        disk_info = {
            "free_mb": int(free_mb),
            "total_mb": int(usage.total // (1024 * 1024)),
            "low": free_mb < 500,
        }
    except Exception as exc:  # noqa: BLE001
        disk_info = {"error": type(exc).__name__}

    # ─── Uptime ─────────────────────────────────────────────
    started_at = getattr(app.state, "started_at", None)
    uptime = None
    if started_at:
        uptime = round(_t.time() - started_at, 1)

    # ─── Métricas operativas (auditoría, blacklist, último backup) ───
    # Se devuelven para que un panel de monitoreo (o el frontend admin)
    # pueda alertar sobre tablas que crecen sin control o backups
    # que llevan días sin correr.
    operational: dict[str, object] = {}
    try:
        from sqlalchemy import func as _func

        from app.infrastructure.database.engine import SessionLocal as _SL
        from app.infrastructure.database.orm_models import (
            AuditLogORM as _Audit,
        )
        from app.infrastructure.database.orm_models import (
            BackupRegistroORM as _Backup,
        )
        from app.infrastructure.database.orm_models import (
            TokenBlacklistORM as _Bl,
        )
        _check = _SL()
        try:
            audit_count = _check.query(_func.count(_Audit.id)).scalar() or 0
            blacklist_count = _check.query(_func.count(_Bl.jti)).scalar() or 0
            last_backup_orm = (
                _check.query(_Backup)
                .order_by(_Backup.fecha.desc())
                .first()
            )
            operational["audit_log_count"] = int(audit_count)
            operational["token_blacklist_count"] = int(blacklist_count)
            if last_backup_orm is not None:
                operational["last_backup"] = {
                    "fecha": last_backup_orm.fecha.isoformat()
                    if last_backup_orm.fecha else None,
                    "exitoso": bool(last_backup_orm.exitoso),
                    "tamano_bytes": int(last_backup_orm.tamano_bytes or 0),
                    "tipo": last_backup_orm.tipo,
                }
                # Avisar si el último backup tiene > 36h
                from datetime import datetime as _dt
                fecha = last_backup_orm.fecha
                if fecha is not None:
                    if fecha.tzinfo is None:
                        fecha = fecha.replace(tzinfo=UTC)
                    age_h = (_dt.now(UTC) - fecha).total_seconds() / 3600
                    operational["last_backup"]["age_hours"] = round(age_h, 1)
                    operational["last_backup"]["stale"] = age_h > 36
            else:
                operational["last_backup"] = None
        finally:
            _check.close()
    except Exception as exc:  # noqa: BLE001
        operational["error"] = type(exc).__name__

    status = "healthy" if db_status["ok"] else "unhealthy"
    if disk_info.get("low"):
        status = "degraded"
    last_bk = operational.get("last_backup")
    if isinstance(last_bk, dict) and last_bk.get("stale"):
        status = "degraded"

    return {
        "status": status,
        "version": settings.api_version,
        "env": settings.env,
        "db_path": str(settings.db_path),
        "db": db_status,
        "baremo": baremo_info,
        "baremo_cargado": baremo_info["loaded"],  # retrocompatibilidad
        "disk": disk_info,
        "uptime_seconds": uptime,
        "operational": operational,
    }


# ─────────────────────────────────────────────────────────────
# Static files — frontend compilado (modo empaquetado)
# Se monta AL FINAL para que todos los routers /api tengan precedencia.
# ─────────────────────────────────────────────────────────────

if _STATIC_DIR:
    # SPA fallback para rutas conocidas del frontend que no existen como
    # archivos (p.ej. /shared/view/{token} — página pública de telemedicina).
    # Debe registrarse ANTES del mount StaticFiles.
    @app.get("/shared/view/{token}", include_in_schema=False)
    def _shared_viewer_spa(token: str):
        return FileResponse(_STATIC_DIR / "index.html")

    # StaticFiles con html=True sirve index.html para rutas del SPA.
    # La autenticación sólo aplica a /api/*; los assets pasan por el middleware.
    app.mount(
        "/",
        StaticFiles(directory=str(_STATIC_DIR), html=True),
        name="frontend",
    )
    logger.info("🎨 Frontend estático montado desde: %s", _STATIC_DIR)
