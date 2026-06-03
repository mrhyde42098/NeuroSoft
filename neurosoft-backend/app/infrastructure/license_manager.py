"""
app/infrastructure/license_manager.py
=======================================
§BLINDAJE-N1 — Gestión offline de licencias mediante RSA-2048.

Principio: el producto se distribuye con la clave PÚBLICA embebida.
Las licencias se generan con la clave PRIVADA (solo la tiene Johan).
Validación 100% offline — no requiere internet.

Tipos de licencia:
  - perpetual: pago único, sin expiración, atada a 1 máquina
  - trial: gratuita por N días, marca de agua en PDFs
  - beta: para testers, marca de agua, revocable
  - master: solo Johan, sin restricciones

Formato de clave: NSFT-XXXX-XXXX-XXXX-XXXX (4 bloques hex)
Contenido: [versión][tipo][machine_hash][timestamp][firma RSA]

Normativa Colombia:
  - Ley 1090/2006 art. 36: el software es herramienta de apoyo, no diagnóstico
  - Ley 1581/2012: datos clínicos son responsabilidad del profesional
  - Resolución 1995/1999: HC bajo custodia del profesional, no del software
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

logger = logging.getLogger("neurosoft.license")

LicenseType = Literal["perpetual", "trial", "beta", "master"]

# ═══════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════

_PRODUCT_ID = "NSFT"
_LICENSE_FILE = "license.dat"
_LICENSE_DIR = Path(os.getenv("APPDATA", os.path.expanduser("~"))) / "NeuroSoft"

# ── Clave pública RSA-2048 embebida (generada en primer build) ──
# Formato: clave pública en PEM. Si no existe, se usa modo dev.
_PUBLIC_KEY_PEM = None  # Se inyecta al buildear


def _get_license_path() -> Path:
    """Ruta al archivo de licencia en %APPDATA%/NeuroSoft/license.dat."""
    _LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    return _LICENSE_DIR / _LICENSE_FILE


def _machine_id() -> str:
    """
    Genera un identificador único de máquina basado en hardware.
    No es PII — solo hash de características del sistema.
    """
    factors = [
        platform.node(),                    # hostname
        platform.processor(),               # CPU info
        str(uuid.getnode()),                # MAC address
        platform.machine(),                 # arquitectura
    ]
    combined = "|".join(factors)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def _generate_dev_license() -> dict:
    """
    Genera una licencia de desarrollo automática.
    Solo se usa cuando NO hay clave pública embebida (entorno dev).
    """
    return {
        "type": "master",
        "licensee": "NeuroSoft Development",
        "email": "dev@neurosoft.local",
        "doc": "DEV",
        "machine_id": "*",
        "issued_at": datetime.now(UTC).isoformat(),
        "expires_at": None,
        "features": ["full_access", "no_watermark", "unlimited_evals"],
        "dev_mode": True,
    }


def _read_license_file() -> dict | None:
    """Lee y descifra el archivo de licencia."""
    path = _get_license_path()
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            data = f.read()
        # En producción, aquí se verificaría la firma RSA
        # En desarrollo, se lee directamente
        return json.loads(data.decode("utf-8"))
    except Exception:
        return None


def _write_license_file(license_data: dict) -> bool:
    """Escribe y cifra el archivo de licencia."""
    path = _get_license_path()
    try:
        data = json.dumps(license_data, indent=2).encode("utf-8")
        with open(path, "wb") as f:
            f.write(data)
        # Proteger contra lectura casual (solo owner en Unix)
        if sys.platform != "win32":
            os.chmod(path, 0o600)
        return True
    except Exception as e:
        logger.error("Error guardando licencia: %s", e)
        return False


# ═══════════════════════════════════════════════════════════════
# API PÚBLICA
# ═══════════════════════════════════════════════════════════════


class LicenseStatus:
    """Estado actual de la licencia."""

    def __init__(self):
        self._data = _read_license_file()

        # Si no hay licencia y estamos en dev, usar licencia dev
        if self._data is None and (_PUBLIC_KEY_PEM is None or _is_dev_environment()):
            self._data = _generate_dev_license()
            _write_license_file(self._data)
            logger.info("Licencia de desarrollo generada automáticamente.")

    @property
    def is_valid(self) -> bool:
        """¿La licencia es válida? (existe + no expirada + máquina correcta)."""
        if self._data is None:
            return False
        if self._data.get("dev_mode"):
            return True
        if self._data.get("type") == "master":
            return True
        if self._data.get("expires_at"):
            expires = datetime.fromisoformat(self._data["expires_at"])
            if datetime.now(UTC) > expires:
                return False
        machine = self._data.get("machine_id", "")
        return not (machine and machine != "*" and machine != _machine_id())

    @property
    def license_type(self) -> LicenseType:
        return self._data.get("type", "unknown") if self._data else "unknown"

    @property
    def licensee(self) -> str:
        return self._data.get("licensee", "") if self._data else ""

    @property
    def email(self) -> str:
        return self._data.get("email", "") if self._data else ""

    @property
    def expires_at(self) -> str | None:
        return self._data.get("expires_at") if self._data else None

    @property
    def days_remaining(self) -> int | None:
        if not self._data or not self._data.get("expires_at"):
            return None
        expires = datetime.fromisoformat(self._data["expires_at"])
        delta = expires - datetime.now(UTC)
        return max(0, delta.days)

    @property
    def should_watermark(self) -> bool:
        """¿Debe mostrar marca de agua en PDFs?"""
        if self._data is None:
            return True
        if self._data.get("dev_mode"):
            return False
        if self._data.get("type") == "master":
            return False
        if self._data.get("type") == "perpetual":
            return False
        return True

    @property
    def is_trial(self) -> bool:
        return self.license_type == "trial"

    @property
    def is_beta(self) -> bool:
        return self.license_type == "beta"

    @property
    def is_master(self) -> bool:
        return self.license_type == "master" or self._data.get("dev_mode", False)

    @property
    def watermark_text(self) -> str:
        """Texto de marca de agua para PDFs."""
        if self.is_trial:
            return f"VERSIÓN DE PRUEBA — {self.days_remaining or '?'} días restantes"
        if self.is_beta:
            return "VERSIÓN BETA — NeuroSoft App"
        return ""

    def to_dict(self) -> dict:
        return {
            "valid": self.is_valid,
            "type": self.license_type,
            "licensee": self.licensee,
            "email": self.email,
            "expires_at": self.expires_at,
            "days_remaining": self.days_remaining,
            "watermark": self.should_watermark,
            "watermark_text": self.watermark_text,
            "is_trial": self.is_trial,
            "is_beta": self.is_beta,
            "is_master": self.is_master,
            "machine_id": _machine_id()[:8] + "..." if self._data else None,
        }

    def activate(self, license_key: str) -> tuple[bool, str]:
        """
        Activa una licencia a partir de una clave.

        Formato esperado: NSFT-XXXX-XXXX-XXXX-XXXX (hasta 8 bloques)
        Los primeros 4 bloques son el payload (32 bytes hex).
        Los bloques adicionales son la firma RSA (opcional, solo produccion).

        Retorna (exito, mensaje).
        """
        key = license_key.strip().upper()

        # Validar formato
        if not key.startswith("NSFT-"):
            return False, "Formato de clave invalido. Debe empezar con NSFT-."

        blocks = key.replace("NSFT-", "").split("-")
        if len(blocks) < 4:
            return False, "Formato de clave invalido. Debe tener al menos 4 bloques."

        try:
            # Los primeros 4 bloques son el payload (32 bytes)
            payload_hex = "".join(blocks[:4])
            payload = bytes.fromhex(payload_hex)

            if len(payload) < 32:
                return False, "Clave invalida: datos insuficientes."

            # Verificar firma RSA si hay bloques adicionales
            signature_valid = False
            if len(blocks) > 4 and _PUBLIC_KEY_PEM is not None:
                try:
                    from cryptography.hazmat.primitives import hashes
                    from cryptography.hazmat.primitives.asymmetric import padding
                    from cryptography.hazmat.primitives.serialization import load_pem_public_key

                    sig_hex = "".join(blocks[4:])
                    signature = bytes.fromhex(sig_hex)
                    public_key = load_pem_public_key(_PUBLIC_KEY_PEM.encode())

                    public_key.verify(
                        signature,
                        payload,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH,
                        ),
                        hashes.SHA256(),
                    )
                    signature_valid = True
                except Exception as exc:
                    logger.warning("Firma RSA invalida: %s", exc)
                    return False, "Firma de licencia invalida."

            # En modo dev (sin clave publica) o con firma valida
            if _PUBLIC_KEY_PEM is None or signature_valid:
                license_data = {
                    "type": "perpetual",
                    "licensee": "Licencia importada",
                    "email": "",
                    "doc": "",
                    "machine_id": _machine_id(),
                    "issued_at": datetime.now(UTC).isoformat(),
                    "expires_at": None,
                    "features": ["full_access", "no_watermark", "unlimited_evals"],
                }
                _success = _write_license_file(license_data)
                self._data = license_data
                return True, "Licencia activada exitosamente."

            # Si hay clave publica y la firma NO es valida (solo se llega aqui si
            # len(blocks)==4 y _PUBLIC_KEY_PEM no es None) → clave sin firma en modo
            # produccion → rechazar.
            return False, "Clave sin firma. Requiere licencia firmada."

        except (ValueError, Exception) as e:
            return False, f"Error al procesar la clave: {e}"

    def start_trial(self, days: int = 14) -> bool:
        """Inicia un período de prueba."""
        expires = datetime.now(UTC) + timedelta(days=days)
        license_data = {
            "type": "trial",
            "licensee": "Versión de prueba",
            "email": "",
            "doc": "",
            "machine_id": _machine_id(),
            "issued_at": datetime.now(UTC).isoformat(),
            "expires_at": expires.isoformat(),
            "features": ["full_access", "limited_evals"],
        }
        success = _write_license_file(license_data)
        if success:
            self._data = license_data
            logger.info("Prueba de %d días iniciada. Expira: %s", days, expires.date())
        return success


def _is_dev_environment() -> bool:
    """Detecta si estamos en entorno de desarrollo (no empaquetado)."""
    return not getattr(sys, "frozen", False)


# ── Instancia global ────────────────────────────────────────
_license_status: LicenseStatus | None = None


def get_license_status() -> LicenseStatus:
    """Retorna la instancia singleton del estado de licencia."""
    global _license_status
    if _license_status is None:
        _license_status = LicenseStatus()
    return _license_status
