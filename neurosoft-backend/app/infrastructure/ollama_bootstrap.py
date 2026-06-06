"""
app/infrastructure/ollama_bootstrap.py
========================================
Auto-instalación silenciosa de Ollama al primer arranque del .exe.

Estrategia:
    1. Esperar 8 segundos tras el startup (la app debe estar lista para que
       el usuario haga login).
    2. Verificar si Ollama ya responde en http://127.0.0.1:11434.
       Si responde → no hace nada (ya instalado y corriendo).
    3. Si NO responde, buscar OllamaSetup.exe bundleado en
       sys._MEIPASS/vendor/ollama/.
    4. Si existe, lanzarlo con /SILENT /NORESTART en background.
    5. Esperar hasta 3 minutos a que el servicio levante.
    6. Si el servicio respondió: marcar bootstrap completo y configurar al
       usuario admin con provider="ollama" por defecto (sólo si su config
       AI está vacía — no sobrescribimos elecciones del usuario).

Idempotente: deja un flag `.ollama_install_attempted` en data_dir para
NO reintentar en arranques sucesivos (el usuario puede borrarlo si quiere
forzar otro intento).
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import sys
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_HEALTH_ENDPOINT = OLLAMA_URL + "/api/tags"
WAIT_AFTER_STARTUP_S = 8
WAIT_FOR_SERVICE_TOTAL_S = 180  # 3 minutos
WAIT_FOR_SERVICE_INTERVAL_S = 4


def _bundled_installer_path() -> Path | None:
    """
    Localiza OllamaSetup.exe. §ollama-fix: ya no se bundlea dentro del exe;
    se distribuye junto al ejecutable principal (instalado vía Inno Setup).
    """
    candidates = []
    # 1. Junto al .exe instalado (modo producción frozen)
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "vendor" / "ollama" / "OllamaSetup.exe")
        candidates.append(exe_dir / "OllamaSetup.exe")
    # 2. Legacy: dentro del bundle de PyInstaller (por compatibilidad)
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
    candidates.append(base / "vendor" / "ollama" / "OllamaSetup.exe")
    # 3. Desarrollo: relativo al checkout
    candidates.append(Path(__file__).resolve().parents[3] / "vendor" / "ollama" / "OllamaSetup.exe")
    for c in candidates:
        try:
            if c.exists():
                return c
        except Exception as _exc:
            # §B6-fix: candidatos con paths inválidos (permisos, símbolos raros).
            # No bloqueante — solo seguimos buscando.
            logger.debug("Path candidato no accesible (%s): %s", c, _exc)
            continue
    return None


def _flag_path() -> Path | None:
    """Ruta al flag de 'ya intentamos auto-instalar' en data_dir."""
    try:
        from app.core.config import settings

        d = Path(settings.data_dir if hasattr(settings, "data_dir") else settings.db_path).parent
        d.mkdir(parents=True, exist_ok=True)
        return d / ".ollama_install_attempted"
    except Exception as _exc:
        # §B6-fix: sin acceso a data_dir, omitimos el flag (reintentaremos
        # en próximos arranques pero no rompe nada).
        logger.debug("No se pudo resolver flag_path: %s", _exc)
        return None


async def _ollama_responding(timeout: float = 3.0) -> bool:
    """¿Está Ollama respondiendo en el puerto estándar?"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(OLLAMA_HEALTH_ENDPOINT)
            return r.status_code < 400
    except Exception as _exc:
        # §B6-fix: timeout, connection refused, DNS — todo es "no responde".
        # Loggeamos en debug para diagnóstico sin spamear el log normal.
        logger.debug("Ollama no responde en %s: %s", OLLAMA_HEALTH_ENDPOINT, _exc)
        return False


async def auto_install_ollama_first_run() -> None:
    """
    Tarea background que se ejecuta al startup. Auto-instala Ollama si:
        • Plataforma == Windows
        • OllamaSetup.exe está bundleado
        • Ollama NO está ya corriendo
        • No hemos intentado antes (flag inexistente)

    No bloquea, no muestra UI. Loguea progreso.
    """
    if sys.platform != "win32":
        return

    await asyncio.sleep(WAIT_AFTER_STARTUP_S)

    flag = _flag_path()
    if flag and flag.exists():
        logger.debug("Ollama auto-install: ya intentado anteriormente, omitiendo.")
        return

    # Si Ollama ya está corriendo, simplemente marcar flag y salir.
    if await _ollama_responding():
        logger.info("Ollama ya estaba corriendo — no requiere auto-install.")
        if flag:
            try:
                flag.write_text("ollama_already_running\n", encoding="utf-8")
            except Exception as _exc:
                # §B6-fix: no es bloqueante; solo significa que se reintentará.
                logger.debug("No se pudo escribir flag de Ollama: %s", _exc)
        return

    installer = _bundled_installer_path()
    if not installer:
        logger.info("Ollama no está corriendo y el installer no está bundleado — omitiendo auto-install.")
        return

    logger.info("Auto-install Ollama: lanzando %s en modo silencioso…", installer)
    try:
        subprocess.Popen(
            [str(installer), "/SILENT", "/NORESTART"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=0x00000008,  # DETACHED_PROCESS
        )
    except Exception as e:
        logger.warning("No se pudo lanzar OllamaSetup.exe: %s", e)
        return

    # Esperar a que Ollama empiece a responder
    elapsed = 0
    running = False
    while elapsed < WAIT_FOR_SERVICE_TOTAL_S:
        await asyncio.sleep(WAIT_FOR_SERVICE_INTERVAL_S)
        elapsed += WAIT_FOR_SERVICE_INTERVAL_S
        if await _ollama_responding():
            running = True
            break

    if running:
        logger.info("✅ Ollama instalado y corriendo (%ds desde el lanzamiento del installer).", elapsed)
        # Configurar al admin con provider="ollama" si su config IA está vacía.
        await _set_default_provider_ollama_if_empty()
    else:
        logger.warning("Ollama no respondió en %ds. El usuario puede activarlo manualmente.", WAIT_FOR_SERVICE_TOTAL_S)

    # Marcamos el flag para no reintentar en próximos arranques
    if flag:
        try:
            flag.write_text(("running\n" if running else "launched_but_not_ready\n"), encoding="utf-8")
        except Exception as _exc:
            # §B6-fix: reintentaremos en próximo arranque — no es crítico.
            logger.debug("No se pudo escribir flag final de Ollama: %s", _exc)


async def _set_default_provider_ollama_if_empty() -> None:
    """
    Si la config AI del usuario admin está vacía (sin provider seleccionado),
    establecer Ollama como provider por defecto. No sobrescribe si el usuario
    ya eligió otro proveedor.
    """
    try:
        from app.infrastructure.database.engine import get_session
        from app.infrastructure.database.orm_models import AIConfigORM, UserORM
    except Exception as e:
        logger.debug("No se pudo importar ORM AI: %s", e)
        return
    db = next(get_session())
    try:
        admin = db.query(UserORM).filter_by(role="admin").first()
        if not admin:
            return
        cfg = db.query(AIConfigORM).filter_by(user_id=admin.id).first()
        if cfg is None:
            cfg = AIConfigORM(
                user_id=admin.id,
                provider="ollama",
                model="llama3.1:8b",
                ollama_url=OLLAMA_URL,
            )
            db.add(cfg)
            db.commit()
            logger.info("Config AI default: provider=ollama para admin (auto).")
        elif not cfg.provider or cfg.provider == "auto":
            cfg.provider = "ollama"
            if not cfg.ollama_url:
                cfg.ollama_url = OLLAMA_URL
            if not cfg.model:
                cfg.model = "llama3.1:8b"
            db.commit()
            logger.info("Config AI actualizada a provider=ollama para admin.")
    except Exception as e:
        logger.debug("No se pudo configurar provider Ollama por defecto: %s", e)
    finally:
        db.close()
