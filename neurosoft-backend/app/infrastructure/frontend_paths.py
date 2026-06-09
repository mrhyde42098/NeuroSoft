"""
app/infrastructure/frontend_paths.py
=====================================
Rutas del frontend estático en desarrollo y en el .exe empaquetado.

En producción las actualizaciones .nsupdate escriben en
%APPDATA%/NeuroSoft/static/ (overlay escribible). El bundle embebido
en PyInstaller es de solo lectura.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _user_data_dir() -> Path:
    try:
        from app.core.config import settings

        base = Path(settings.db_path).parent
    except Exception:
        base = Path(os.getenv("APPDATA", Path.home())) / "NeuroSoft"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parents[2]


def bundled_static_dir() -> Path | None:
    """Directorio static/ dentro del bundle PyInstaller (solo lectura)."""
    candidate = _bundle_root() / "static"
    if candidate.is_dir() and (candidate / "index.html").is_file():
        return candidate
    return None


def overlay_static_dir() -> Path:
    """Directorio escribible para actualizaciones de frontend."""
    d = _user_data_dir() / "static"
    d.mkdir(parents=True, exist_ok=True)
    return d


def dev_static_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "neurosoft-frontend" / "dist"


def ensure_overlay_bootstrapped() -> Path:
    """
    Garantiza que el overlay tenga index.html (copia desde bundle la primera vez).
    Retorna el directorio escribible donde aplicar .nsupdate.
    """
    overlay = overlay_static_dir()
    if (overlay / "index.html").is_file():
        return overlay
    bundled = bundled_static_dir()
    if bundled is not None:
        shutil.copytree(bundled, overlay, dirs_exist_ok=True)
    return overlay


def served_static_dir() -> Path | None:
    """
    Directorio que FastAPI StaticFiles debe servir.
    Prioridad: overlay (actualizado) > bundle > dev dist.
    """
    if getattr(sys, "frozen", False):
        overlay = overlay_static_dir()
        if (overlay / "index.html").is_file():
            return overlay
        bundled = bundled_static_dir()
        if bundled is not None:
            return bundled
        return None

    dev = dev_static_dir()
    if dev.is_dir() and (dev / "index.html").is_file():
        return dev
    return None


def writable_frontend_dir() -> Path:
    """Destino de extracción para POST /system/update."""
    if getattr(sys, "frozen", False):
        return ensure_overlay_bootstrapped()
    dest = dev_static_dir()
    dest.mkdir(parents=True, exist_ok=True)
    return dest
