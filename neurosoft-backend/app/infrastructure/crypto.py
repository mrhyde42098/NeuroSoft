"""
app/infrastructure/crypto.py
================================
Cifrado/descifrado simétrico para campos sensibles guardados en SQLite.

Caso de uso: contraseña SMTP, credenciales de servicios externos, tokens.
NO sustituye una solución de KMS — pero es muchísimo mejor que plaintext
en BD local. La clave Fernet se deriva del `JWT_SECRET` del backend.

Diseño:
    • Si el campo cifrado se pierde (BD copiada a otra máquina con otro
      JWT_SECRET), `decrypt` devuelve None y el sistema cae a env vars.
    • No lanza excepciones al caller — el código que usa esto debe
      considerar None como "no descifrable / volver a configurar".
"""

from __future__ import annotations

import base64
import hashlib
import logging

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("neurosoft.crypto")

_fernet_cache: Fernet | None = None


def _get_fernet() -> Fernet:
    """Deriva una clave Fernet determinística a partir del secret_key."""
    global _fernet_cache
    if _fernet_cache is not None:
        return _fernet_cache
    from app.core.config import settings

    secret = (settings.secret_key or "neurosoft-default-key-change-me-please").encode("utf-8")
    # Fernet requiere clave 32 bytes urlsafe-b64
    digest = hashlib.sha256(secret).digest()
    key = base64.urlsafe_b64encode(digest)
    _fernet_cache = Fernet(key)
    return _fernet_cache


def encrypt(plaintext: str) -> str:
    """Devuelve token Fernet (string ASCII). Vacío si plaintext es vacío."""
    if not plaintext:
        return ""
    return _get_fernet().encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt(token: str) -> str | None:
    """Devuelve plaintext o None si no se pudo descifrar (clave cambiada, etc.)."""
    if not token:
        return None
    try:
        return _get_fernet().decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError) as e:
        logger.warning("No se pudo descifrar campo: %s", type(e).__name__)
        return None


def reset_cache() -> None:
    """Útil en tests: forzar regenerar Fernet (p.ej. tras cambiar JWT_SECRET)."""
    global _fernet_cache
    _fernet_cache = None
