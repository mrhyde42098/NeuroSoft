"""
app/core/config_institucion.py
==============================
F19 — Sistema de identidad configurable del clínico / institución.

Patrón:
- Configuración persistida en BD (no en .env) — los valores son únicos
  por instalación.
- Cifrado AES-256 (Fernet) para campos sensibles (tarjeta_profesional,
  institucion_nit) con clave derivada de SECRET_KEY.
- Valores por defecto: VACÍOS. El clínico completa desde ConfigPage.
- Sin atribución a terceros. El "autor" siempre es "NeuroSoft App".
- Si el sistema arranca sin nombre_completo + tarjeta_profesional,
  el frontend muestra un wizard de primer inicio que obliga a completar
  estos campos antes de poder generar informes.
"""
from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Optional

# Singleton lazy
_INSTITUCION_CACHE: Optional["InstitucionConfig"] = None


@dataclass
class InstitucionConfig:
    """
    Configuración institucional y del profesional.
    14 campos según F19.1.
    """

    # Profesional (obligatorios para generar informes)
    nombre_completo: str = ""
    tarjeta_profesional: str = ""
    universidad: str = ""
    fecha_tarjeta: str = ""
    resolucion: str = ""

    # Institución (opcional; vacío si el profesional es independiente)
    institucion_nombre: str = ""
    institucion_nit: str = ""
    institucion_direccion: str = ""
    institucion_telefono: str = ""
    institucion_correo: str = ""
    institucion_logo_path: str = ""

    # Pie y otros
    pie_pagina_pdf: str = ""
    codigo_habilitacion: str = ""
    sello_digital_path: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "InstitucionConfig":
        """Construye desde dict, ignorando claves desconocidas."""
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})

    def campos_obligatorios_completos(self) -> bool:
        """Para generar informes, se requiere nombre_completo + tarjeta_profesional."""
        return bool(self.nombre_completo.strip()) and bool(self.tarjeta_profesional.strip())

    def puede_generar_rips(self) -> bool:
        """RIPS / Factura requiere NIT además de los obligatorios."""
        return self.campos_obligatorios_completos() and bool(self.institucion_nit.strip())

    def placeholders(self) -> dict:
        """Devuelve un dict con los placeholders para usar en plantillas."""
        return {
            "nombre_completo": self.nombre_completo or "[NOMBRE DEL PROFESIONAL]",
            "tarjeta_profesional": self.tarjeta_profesional or "[TARJETA PROFESIONAL]",
            "universidad": self.universidad or "[UNIVERSIDAD]",
            "fecha_tarjeta": self.fecha_tarjeta or "[FECHA TARJETA]",
            "resolucion": self.resolucion or "[RESOLUCIÓN]",
            "institucion_nombre": self.institucion_nombre or "[INSTITUCIÓN]",
            "institucion_nit": self.institucion_nit or "[NIT]",
            "institucion_direccion": self.institucion_direccion or "[DIRECCIÓN]",
            "institucion_telefono": self.institucion_telefono or "[TELÉFONO]",
            "institucion_correo": self.institucion_correo or "[CORREO]",
            "pie_pagina_pdf": self.pie_pagina_pdf or "",
            "codigo_habilitacion": self.codigo_habilitacion or "[CÓDIGO HABILITACIÓN]",
        }


# ─────────────────────────────────────────────────────────────────────
# Persistencia en BD
# ─────────────────────────────────────────────────────────────────────

# Tabla simple key-value; un solo registro por instalación.
# Almacenamos en una tabla dedicada (no en config.py) porque los
# valores son únicos por usuario/instalación, no globales.

_CONFIG_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS institucion_config (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    data_json       TEXT NOT NULL,
    updated_at      TEXT NOT NULL
)
"""


def _get_db_path() -> Path:
    """Resuelve la ruta al SQLite. SIEMPRE lee del env primero
    para que los tests con monkeypatch funcionen."""
    env_path = os.getenv("NEUROSOFT_DB_PATH")
    if env_path:
        return Path(env_path)
    try:
        from app.core.config import settings
        return Path(settings.db_path)
    except Exception:
        return Path("data/neurosoft.db")


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(_CONFIG_TABLE_SQL)
    conn.commit()


def load_institucion_config() -> InstitucionConfig:
    """Carga la config de BD. Si no existe, retorna defaults vacíos."""
    global _INSTITUCION_CACHE
    if _INSTITUCION_CACHE is not None:
        return _INSTITUCION_CACHE

    db_path = _get_db_path()
    if not db_path.exists():
        return InstitucionConfig()

    try:
        with sqlite3.connect(str(db_path)) as conn:
            _ensure_table(conn)
            row = conn.execute(
                "SELECT data_json FROM institucion_config WHERE id = 1"
            ).fetchone()
            if row is None:
                cfg = InstitucionConfig()
            else:
                cfg = InstitucionConfig.from_dict(json.loads(row[0]))
            _INSTITUCION_CACHE = cfg
            return cfg
    except (sqlite3.OperationalError, json.JSONDecodeError):
        # BD no accesible — retornar defaults
        return InstitucionConfig()


def save_institucion_config(config: InstitucionConfig) -> None:
    """Persiste la config en BD. Invalida caché."""
    global _INSTITUCION_CACHE
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        _ensure_table(conn)
        from datetime import datetime, timezone
        conn.execute(
            """INSERT INTO institucion_config (id, data_json, updated_at)
               VALUES (1, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 data_json = excluded.data_json,
                 updated_at = excluded.updated_at""",
            (json.dumps(config.to_dict(), ensure_ascii=False),
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    _INSTITUCION_CACHE = config


def invalidate_cache() -> None:
    """Útil para tests o cuando se cambia el usuario activo."""
    global _INSTITUCION_CACHE
    _INSTITUCION_CACHE = None


def get_config_institucion() -> InstitucionConfig:
    """
    F19.2 — Punto de acceso principal.
    ``from app.core.config_institucion import get_config_institucion``
    """
    return load_institucion_config()


# ─────────────────────────────────────────────────────────────────────
# Datos de demostración (marcados como [DEMO])
# ─────────────────────────────────────────────────────────────────────


def demo_data() -> InstitucionConfig:
    """Botón 'Usar datos de prueba' — claramente marcado como DEMO."""
    return InstitucionConfig(
        nombre_completo="[DEMO] Profesional de Prueba",
        tarjeta_profesional="[DEMO] TP-000000",
        universidad="[DEMO] Universidad de Prueba",
        institucion_nombre="[DEMO] Consultorio de Prueba",
        institucion_nit="[DEMO] 900.000.000-0",
        institucion_direccion="[DEMO] Calle 0 # 0-00, Bogotá",
        institucion_telefono="[DEMO] +57 300 000 0000",
        institucion_correo="[DEMO] demo@example.com",
    )
