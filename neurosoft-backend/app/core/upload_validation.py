"""
app/core/upload_validation.py
==============================
Validación centralizada para endpoints que aceptan archivos.

Motivación
----------
Los endpoints de upload son una superficie de ataque clásica:
    1. DoS por tamaño (subir 10 GB agotando memoria y disco).
    2. Suplantación MIME: extensión .xlsm con contenido ejecutable.
    3. XSS almacenado: payloads "image/svg+xml" con <script> incrustado.
    4. Path traversal vía filename (../../etc/passwd).

Este módulo centraliza los chequeos estructurales para que cada
endpoint no reinvente la rueda:
    • `validate_upload_bytes()` — tamaño + magic bytes + extensión.
    • `MagicSignature` — catálogo de firmas de archivo reconocidas.
    • Errores tipados (`UploadTooLargeError`, `UploadInvalidError`).

Detalles importantes
--------------------
- La validación se hace sobre los BYTES ya leídos: esto significa
  que el caller debe limitar la lectura (`await file.read(max)`)
  antes de llamarnos, o aceptar que la primera barrera es el
  tamaño final del buffer en memoria.
- No se hace antivirus scan — eso va en una capa superior
  (integración con ClamAV o similar si el cliente lo exige).
- El nombre de archivo se sanitiza para evitar path traversal
  (sólo se conserva `Path(name).name`).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Excepciones
# ─────────────────────────────────────────────────────────────


class UploadValidationError(Exception):
    """Error genérico de validación de upload. HTTP 422."""

    status_code: int = 422


class UploadTooLargeError(UploadValidationError):
    """El archivo excede el tamaño máximo permitido. HTTP 413."""

    status_code: int = 413


class UploadInvalidError(UploadValidationError):
    """El archivo no pasa las verificaciones de tipo / firma."""

    status_code: int = 422


# ─────────────────────────────────────────────────────────────
# Firmas de archivo (magic bytes)
# ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class MagicSignature:
    """
    Firma binaria reconocida en los primeros N bytes de un archivo.
    `offset` permite verificar firmas que no empiezan en el byte 0
    (raro pero necesario para algunos formatos).
    """

    name: str
    prefix: bytes
    offset: int = 0

    def matches(self, data: bytes) -> bool:
        end = self.offset + len(self.prefix)
        if len(data) < end:
            return False
        return data[self.offset : end] == self.prefix


# Catálogo de firmas para los formatos que aceptamos.
SIG_SQLITE3 = MagicSignature("SQLite 3", b"SQLite format 3\x00")
SIG_ZIP = MagicSignature("ZIP / OOXML", b"PK\x03\x04")
SIG_ZIP_EMPTY = MagicSignature("ZIP vacío", b"PK\x05\x06")
SIG_PNG = MagicSignature("PNG", b"\x89PNG\r\n\x1a\n")
SIG_JPEG = MagicSignature("JPEG", b"\xff\xd8\xff")
SIG_GIF87 = MagicSignature("GIF87a", b"GIF87a")
SIG_GIF89 = MagicSignature("GIF89a", b"GIF89a")
SIG_WEBP_RIFF = MagicSignature("WebP (RIFF)", b"RIFF")

# Las imágenes raster admitidas para firmas digitales: PNG, JPEG,
# GIF. SVG queda FUERA a propósito (XSS storage risk).
IMAGE_SIGNATURES: tuple[MagicSignature, ...] = (
    SIG_PNG,
    SIG_JPEG,
    SIG_GIF87,
    SIG_GIF89,
    # WebP es válido pero necesita verificación extra ("WEBP" en offset 8).
)

# OOXML (.xlsx, .xlsm, .docx) — todos son ZIPs por dentro.
OOXML_SIGNATURES: tuple[MagicSignature, ...] = (SIG_ZIP, SIG_ZIP_EMPTY)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def sanitize_filename(filename: str | None) -> str:
    """
    Devuelve sólo el basename, sin separadores ni `..`. Protege
    contra path traversal si el filename se usa para escribir en
    disco.
    """
    if not filename:
        return "archivo"
    # Rechazamos cualquier ruta relativa o componentes sospechosos
    base = Path(filename).name
    if not base or base.startswith(".") or ".." in base:
        return "archivo"
    return base


def _matches_any(data: bytes, sigs: Iterable[MagicSignature]) -> bool:
    return any(sig.matches(data) for sig in sigs)


# ─────────────────────────────────────────────────────────────
# Validador público
# ─────────────────────────────────────────────────────────────


def validate_upload_bytes(
    data: bytes,
    *,
    max_bytes: int,
    min_bytes: int = 1,
    allowed_extensions: Sequence[str] | None = None,
    allowed_signatures: Sequence[MagicSignature] | None = None,
    filename: str | None = None,
    label: str = "archivo",
) -> None:
    """
    Verifica que `data` cumpla las restricciones del endpoint.

    Args:
        data:                 Bytes ya leídos del upload.
        max_bytes:            Tamaño máximo (levanta UploadTooLargeError).
        min_bytes:            Tamaño mínimo (default 1; evita vacíos).
        allowed_extensions:   Lista blanca de extensiones (p.ej. [".db"]).
                              Case-insensitive. None = no validar extensión.
        allowed_signatures:   Firmas magic aceptadas. None = no validar
                              contenido (solo útil si el endpoint ya hace
                              una verificación más profunda a nivel aplicación).
        filename:             Para mensajes de error y chequeo de extensión.
        label:                Nombre humano del tipo ("backup .db", "firma", ...).

    Raises:
        UploadTooLargeError:  Si len(data) > max_bytes.
        UploadInvalidError:   Si len(data) < min_bytes, la extensión no
                              está en la lista blanca, o ninguna firma
                              coincide.
    """
    size = len(data)

    if size < min_bytes:
        raise UploadInvalidError(f"El {label} parece estar vacío o corrupto ({size} bytes).")
    if size > max_bytes:
        mb = max_bytes / (1024 * 1024)
        raise UploadTooLargeError(f"El {label} excede el tamaño máximo permitido ({mb:.0f} MB).")

    # Extensión
    if allowed_extensions:
        name = (filename or "").lower()
        exts = tuple(e.lower() for e in allowed_extensions)
        if not any(name.endswith(e) for e in exts):
            raise UploadInvalidError(f"Extensión no permitida para {label}. Aceptadas: {', '.join(exts)}.")

    # Magic bytes
    if allowed_signatures:
        if not _matches_any(data, allowed_signatures):
            expected = ", ".join(s.name for s in allowed_signatures)
            raise UploadInvalidError(
                f"El contenido del {label} no coincide con ningún formato válido (esperado: {expected})."
            )


# ─────────────────────────────────────────────────────────────
# Validador específico para firma base64
# ─────────────────────────────────────────────────────────────


def validate_firma_base64(
    b64_payload: str,
    *,
    max_bytes: int,
) -> bytes:
    """
    Valida un payload base64 que se espera sea una imagen PNG/JPEG/GIF.
    Rechaza SVG y cualquier otra cosa (XSS storage).

    Returns:
        Los bytes decodificados listos para persistir.

    Raises:
        UploadInvalidError:   base64 malformado o imagen no permitida.
        UploadTooLargeError:  Excede max_bytes al decodificar.
    """
    import base64

    if not b64_payload:
        raise UploadInvalidError("firma_base64 es requerido.")

    payload = b64_payload.strip()
    # Rechazar explícitamente SVG (aun camuflado como data:image/svg+xml)
    header_lower = payload[:64].lower()
    if "svg" in header_lower:
        raise UploadInvalidError("Firmas en formato SVG no están permitidas por razones de seguridad.")

    # Quitar el prefijo data URI si existe
    if "," in payload and payload.startswith("data:"):
        payload = payload.split(",", 1)[1]

    try:
        raw = base64.b64decode(payload, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise UploadInvalidError("firma_base64 no es base64 válido.") from exc

    if len(raw) < 16:
        raise UploadInvalidError("La firma está vacía o corrupta.")
    if len(raw) > max_bytes:
        kb = max_bytes // 1024
        raise UploadTooLargeError(f"La firma excede el tamaño máximo permitido ({kb} KB).")

    if not _matches_any(raw, IMAGE_SIGNATURES):
        raise UploadInvalidError("La firma debe ser una imagen PNG, JPEG o GIF válida.")

    return raw
