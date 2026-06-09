"""
app/core/config.py
==================
Gestión centralizada de configuración mediante variables de entorno.

Usa pydantic-settings para validar y tipificar cada parámetro de la
aplicación. Un único objeto `settings` importable desde cualquier módulo.

Patrón: Singleton lazy — la instancia se crea una sola vez al importar.

Variables de entorno soportadas (.env o shell):
    NEUROSOFT_ENV                development | production | testing
    NEUROSOFT_SECRET_KEY         (OBLIGATORIA en producción) clave JWT
    NEUROSOFT_ADMIN_PASSWORD     (OBLIGATORIA en producción) contraseña admin inicial
    NEUROSOFT_DB_PATH            ruta al archivo SQLite  (default: data/neurosoft.db)
    NEUROSOFT_BAREMO_PATH        ruta al JSON de baremos (default: data/BD_NEURO_MAESTRA.json)
    NEUROSOFT_REPORTS_DIR        directorio de informes  (default: reports/)
    NEUROSOFT_LOG_LEVEL          DEBUG | INFO | WARNING  (default: INFO)
    NEUROSOFT_CORS_ORIGINS       JSON list de orígenes   (default: ["*"] en dev)
    NEUROSOFT_API_VERSION        versión de la API       (default: "2.0.1")
    NEUROSOFT_CLINICAL_BRAND     nombre de la marca clínica mostrada en informes
    NEUROSOFT_EXPOSE_DOCS        1|0   habilitar /docs y /redoc (default: 1 en dev, 0 en prod)
    NEUROSOFT_RATE_LIMIT_PER_MIN límite global de peticiones por IP (0 = desactivado)

Modos estrictos:
    En env=production, el arranque aborta si:
        • NEUROSOFT_SECRET_KEY no está seteada o conserva el valor por defecto
        • NEUROSOFT_ADMIN_PASSWORD no está seteada
        • cors_origins contiene "*" con allow_credentials=True (inseguro)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

try:
    from pydantic import Field, field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

# Raíz del proyecto (dos niveles arriba de este archivo)
_PROJECT_ROOT = Path(__file__).parent.parent.parent


def _user_data_dir() -> Path:
    """
    Directorio para persistir datos del usuario (BD + backups + logs).

    - Modo desarrollo: project_root/data
    - Modo empaquetado (PyInstaller): %APPDATA%/NeuroSoft en Windows
                                      ~/Library/Application Support/NeuroSoft en macOS
                                      ~/.local/share/NeuroSoft en Linux

    La variable NEUROSOFT_DATA_DIR puede forzar una ruta específica
    (modo portable: colocar junto al .exe).
    """
    forced = os.getenv("NEUROSOFT_DATA_DIR")
    if forced:
        base = Path(forced)
    elif getattr(sys, "frozen", False):
        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA", Path.home())) / "NeuroSoft"
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support" / "NeuroSoft"
        else:
            base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "NeuroSoft"
    else:
        base = _PROJECT_ROOT / "data"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return base


_DATA_ROOT = _user_data_dir()


if HAS_PYDANTIC:

    class Settings(BaseSettings):
        """
        Configuración completa de NeuroSoft.

        Todos los campos tienen valores por defecto seguros para
        desarrollo local. En producción, sobreescribir con variables
        de entorno o un archivo `.env` en la raíz del proyecto.
        """

        model_config = SettingsConfigDict(
            env_prefix="NEUROSOFT_",
            env_file=str(_PROJECT_ROOT / ".env"),
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

        # ── Entorno ──────────────────────────────────────────────────
        env: Literal["development", "production", "testing"] = Field(
            default="development",
            description="Entorno de ejecución.",
        )

        # ── Rutas de datos ───────────────────────────────────────────
        db_path: Path = Field(
            default=_DATA_ROOT / "neurosoft.db",
            description="Ruta al archivo SQLite. Se crea automáticamente.",
        )
        backup_dir: Path = Field(
            default=_DATA_ROOT / "backups",
            description="Directorio para backups cifrados automáticos (S4.3).",
        )
        baremo_path: Path = Field(
            default=_DATA_ROOT / "BD_NEURO_MAESTRA.json",
            description="Ruta al JSON de baremos normativos.",
        )
        reports_dir: Path = Field(
            default=_DATA_ROOT / "reports",
            description="Directorio donde se guardan los informes generados.",
        )

        # ── API ──────────────────────────────────────────────────────
        api_version: str = Field(default="2.0.1")
        api_title: str = Field(default="NeuroSoft API")
        api_description: str = Field(
            default=("Motor de calificación neuropsicológica. 152 variables clínicas · 15 strategies · Colombia.")
        )

        # ── Logging ──────────────────────────────────────────────────
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

        # ── CORS ─────────────────────────────────────────────────────
        cors_origins: list[str] = Field(
            default=[
                # §M6-fix: default restrictivo. Antes era ["*"] — funcionaba con
                # `allow_credentials=False` por degradación en main.py, pero un
                # default permisivo es mala higiene. Si el operador necesita
                # otros orígenes, los declara explícitamente en .env vía
                # NEUROSOFT_CORS_ORIGINS='["https://mi-dominio.com"]'.
                "http://localhost:5173",  # Vite dev server
                "http://localhost:8000",  # backend dev directo
                "http://localhost:8765",  # launcher pywebview
                "http://127.0.0.1:5173",
                "http://127.0.0.1:8000",
                "http://127.0.0.1:8765",
            ],
            description=(
                "Lista JSON de orígenes permitidos. Default: localhost dev/8765. "
                "Producción: declara explícitamente los dominios externos. "
                '"*" desactiva credenciales (cookies/Authorization no se envían).'
            ),
        )

        # ── Seguridad ────────────────────────────────────────────────
        secret_key: str = Field(
            default="",
            description="Clave JWT. OBLIGATORIA en producción (>= 32 chars).",
        )
        admin_password: str = Field(
            default="",
            description="Contraseña inicial del usuario admin. OBLIGATORIA en producción.",
        )
        expose_docs: bool = Field(
            default=True,
            description="Exponer /docs y /redoc. En producción debería ser False.",
        )
        rate_limit_per_min: int = Field(
            default=120,
            description="Rate limit global por IP. 0 = desactivado.",
        )
        # §S0.4 — ELIMINADO `disable_auth`: era un kill-switch crítico
        # que dejaba toda la API sin auth. Si necesitas bypass para tests,
        # usa un JWT válido de corta duración en un entorno aislado.

        # ── Marca clínica (neutralizable al compartir el software) ──
        clinical_brand: str = Field(
            default="NeuroSoft",
            description="Nombre mostrado en informes y mensajes clínicos.",
        )
        clinical_brand_subtitle: str = Field(
            default="Plataforma de evaluación neuropsicológica",
            description="Subtítulo/descripción corta de la marca clínica.",
        )

        # ── Feature flags ────────────────────────────────────────────
        enable_reports: bool = Field(
            default=True,
            description="Habilitar generación de reportes PDF/Word.",
        )

        # ── Límites de uploads (defensa contra DoS / contenido malicioso) ──
        # Los tres endpoints que aceptan archivos (restore backup, import
        # legacy xlsm, firma de profesional) validan MIME por magic bytes
        # y rechazan payloads fuera de rango. Estos defaults son
        # razonables para el caso de uso clínico.
        max_upload_backup_mb: int = Field(
            default=200,
            description="Tamaño máximo del archivo .db al restaurar (MB).",
        )
        max_upload_xlsm_mb: int = Field(
            default=50,
            description="Tamaño máximo del archivo .xlsm legacy (MB).",
        )
        max_firma_kb: int = Field(
            default=512,
            description="Tamaño máximo de la firma (imagen base64, KB).",
        )

        # ── SMTP (envío de correos con log) ──────────────────────────
        smtp_host: str = Field(
            default="",
            description="Servidor SMTP. Ej: smtp.office365.com, smtp.gmail.com. Vacío → feature deshabilitada.",
        )
        smtp_port: int = Field(default=587, description="Puerto SMTP (587 STARTTLS, 465 SSL).")
        smtp_user: str = Field(default="", description="Usuario SMTP.")
        smtp_password: str = Field(default="", description="Contraseña o App Password SMTP.")
        smtp_from: str = Field(default="", description="Dirección FROM (si vacía, usa smtp_user).")
        smtp_from_name: str = Field(default="NeuroSoft", description="Display name del remitente.")
        smtp_use_tls: bool = Field(default=True, description="STARTTLS (puerto 587).")
        smtp_use_ssl: bool = Field(default=False, description="SSL directo (puerto 465).")
        smtp_timeout: int = Field(default=30, description="Timeout SMTP en segundos.")

        # ── Propiedades derivadas ────────────────────────────────────
        @property
        def is_development(self) -> bool:
            return self.env == "development"

        @property
        def is_testing(self) -> bool:
            return self.env == "testing"

        @property
        def sqlalchemy_url(self) -> str:
            """URL de conexión SQLAlchemy para SQLite."""
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{self.db_path}"

        @field_validator("baremo_path", mode="before")
        @classmethod
        def validate_baremo_exists_warn(cls, v):
            """No bloquea el arranque, pero advierte si el JSON no existe."""
            path = Path(v)
            if not path.exists():
                import warnings

                warnings.warn(
                    f"BD_NEURO_MAESTRA.json no encontrado en: {path}. "
                    "El motor de baremos no estará disponible hasta copiarlo.",
                    stacklevel=2,
                )
            return path

        # ── Hooks de validación por entorno ──────────────────────────
        def enforce_production_invariants(self) -> list[str]:
            """
            Verifica que en producción estén seteadas las variables críticas.
            Devuelve la lista de problemas encontrados (vacía si todo bien).
            """
            problems: list[str] = []
            if self.env != "production":
                return problems

            _DEFAULT_SECRET = "neurosoft-dev-secret-key-change-in-production-32chars-min"
            if not self.secret_key or self.secret_key == _DEFAULT_SECRET:
                problems.append(
                    "NEUROSOFT_SECRET_KEY no configurada (o usa el valor de desarrollo). "
                    'Genera una con: python -c "import secrets; print(secrets.token_urlsafe(48))"'
                )
            elif len(self.secret_key) < 32:
                problems.append(
                    f"NEUROSOFT_SECRET_KEY es demasiado corta ({len(self.secret_key)} chars); se requieren al menos 32."
                )
            if not self.admin_password:
                problems.append(
                    "NEUROSOFT_ADMIN_PASSWORD no configurada. "
                    "Define una contraseña inicial fuerte para el usuario admin."
                )
            elif len(self.admin_password) < 8:
                problems.append("NEUROSOFT_ADMIN_PASSWORD demasiado corta (mínimo 8 caracteres).")
            if "*" in self.cors_origins:
                problems.append(
                    "cors_origins contiene '*' pero allow_credentials=True: combinación rechazada "
                    "por el navegador y riesgosa. Lista dominios específicos en "
                    "NEUROSOFT_CORS_ORIGINS."
                )
            return problems

        def effective_expose_docs(self) -> bool:
            """Docs visibles salvo que se pida lo contrario o se esté en producción."""
            if self.env == "production":
                # En producción, solo si se pidió explícitamente
                return bool(os.getenv("NEUROSOFT_EXPOSE_DOCS")) and self.expose_docs
            return self.expose_docs

else:
    # Fallback mínimo sin pydantic-settings (para entornos sin dependencias)
    class Settings:  # type: ignore
        env = "development"
        db_path = _DATA_ROOT / "neurosoft.db"
        baremo_path = _DATA_ROOT / "BD_NEURO_MAESTRA.json"
        reports_dir = _DATA_ROOT / "reports"
        api_version = "2.0.1"
        api_title = "NeuroSoft API"
        api_description = "Motor de calificación neuropsicológica."
        log_level = "INFO"
        cors_origins = [
            "http://localhost:5173",
            "http://localhost:8000",
            "http://localhost:8765",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8765",
        ]
        enable_reports = True
        secret_key = ""
        admin_password = ""
        expose_docs = True
        rate_limit_per_min = 120
        clinical_brand = "NeuroSoft"
        clinical_brand_subtitle = "Plataforma de evaluación neuropsicológica"
        smtp_host = ""
        smtp_port = 587
        smtp_user = ""
        smtp_password = ""
        smtp_from = ""
        smtp_from_name = "NeuroSoft"
        smtp_use_tls = True
        smtp_use_ssl = False
        smtp_timeout = 30
        max_upload_backup_mb = 200
        max_upload_xlsm_mb = 50
        max_firma_kb = 512
        is_development = True
        is_testing = False
        sqlalchemy_url = f"sqlite:///{_DATA_ROOT / 'neurosoft.db'}"

        def enforce_production_invariants(self) -> list:
            return []

        def effective_expose_docs(self) -> bool:
            return bool(self.expose_docs)


# Instancia singleton — importar desde cualquier módulo:
#   from app.core.config import settings
settings = Settings()
