"""
tests/unit/core/test_upload_validation.py
==========================================
Pruebas del validador centralizado de uploads.

Cubre:
    • `validate_upload_bytes` con tamaños dentro y fuera de rango.
    • Validación de extensiones (.db, .xlsx, .xlsm).
    • Validación de magic bytes (SQLite, OOXML, imágenes).
    • `validate_firma_base64` con PNG/JPEG/GIF/SVG/corrupto.
    • `sanitize_filename` contra path traversal.
"""

from __future__ import annotations

import base64

import pytest

from app.core.upload_validation import (
    OOXML_SIGNATURES,
    SIG_SQLITE3,
    UploadInvalidError,
    UploadTooLargeError,
    sanitize_filename,
    validate_firma_base64,
    validate_upload_bytes,
)

# ─────────────────────────────────────────────────────────────
# sanitize_filename
# ─────────────────────────────────────────────────────────────


class TestSanitizeFilename:
    def test_basic_filename(self):
        assert sanitize_filename("archivo.db") == "archivo.db"

    def test_path_traversal_rejected(self):
        # `Path(...).name` ya strippea los componentes de ruta, así que
        # el ataque de path traversal queda neutralizado: sólo queda el
        # basename, sin `..` ni separadores.
        result = sanitize_filename("../../etc/passwd")
        assert "/" not in result and "\\" not in result
        assert ".." not in result
        assert result == "passwd"

    def test_absolute_path_stripped(self):
        assert sanitize_filename("/etc/passwd") == "passwd"

    def test_windows_path_stripped(self):
        assert sanitize_filename(r"C:\Users\evil\file.db") == "file.db"

    def test_empty_returns_default(self):
        assert sanitize_filename("") == "archivo"
        assert sanitize_filename(None) == "archivo"

    def test_hidden_file_rejected(self):
        assert sanitize_filename(".hidden") == "archivo"

    def test_none_handled(self):
        assert sanitize_filename(None) == "archivo"


# ─────────────────────────────────────────────────────────────
# validate_upload_bytes
# ─────────────────────────────────────────────────────────────


class TestValidateUploadBytes:
    def test_happy_path_db(self):
        data = b"SQLite format 3\x00" + b"\x00" * 2000
        # No debe levantar
        validate_upload_bytes(
            data,
            max_bytes=10 * 1024 * 1024,
            min_bytes=1024,
            allowed_extensions=[".db"],
            allowed_signatures=[SIG_SQLITE3],
            filename="backup.db",
            label="backup",
        )

    def test_too_large(self):
        data = b"\x00" * (2 * 1024 * 1024)
        with pytest.raises(UploadTooLargeError):
            validate_upload_bytes(
                data,
                max_bytes=1 * 1024 * 1024,
                filename="x.db",
                label="backup",
            )

    def test_too_small(self):
        with pytest.raises(UploadInvalidError, match="vacío"):
            validate_upload_bytes(
                b"",
                max_bytes=1024,
                min_bytes=1,
                label="backup",
            )

    def test_extension_rejected(self):
        data = b"SQLite format 3\x00" + b"\x00" * 2000
        with pytest.raises(UploadInvalidError, match="Extensión"):
            validate_upload_bytes(
                data,
                max_bytes=1024 * 1024,
                allowed_extensions=[".db"],
                filename="malicious.exe",
                label="backup",
            )

    def test_signature_rejected(self):
        data = b"NOT_SQLITE_AT_ALL" + b"\x00" * 2000
        with pytest.raises(UploadInvalidError, match="formato"):
            validate_upload_bytes(
                data,
                max_bytes=1024 * 1024,
                allowed_signatures=[SIG_SQLITE3],
                filename="fake.db",
                label="backup",
            )

    def test_ooxml_accepted(self):
        # OOXML/XLSX empieza con PK (ZIP)
        data = b"PK\x03\x04" + b"\x00" * 2000
        validate_upload_bytes(
            data,
            max_bytes=10 * 1024 * 1024,
            allowed_extensions=[".xlsx", ".xlsm"],
            allowed_signatures=list(OOXML_SIGNATURES),
            filename="legacy.xlsm",
            label="xlsm",
        )

    def test_http_status_codes(self):
        """Los errores tienen HTTP status apropiado."""
        err_too_big = UploadTooLargeError("x")
        err_invalid = UploadInvalidError("x")
        assert err_too_big.status_code == 413
        assert err_invalid.status_code == 422


# ─────────────────────────────────────────────────────────────
# validate_firma_base64
# ─────────────────────────────────────────────────────────────

# Imagen PNG 1x1 mínima (usada en muchos test frameworks).
_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00"
    b"\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx"
    b"\x9cc\xfc\xff\xff?\x03\x00\x05\xfe\x02\xfe\xa7\xac\xb8\xee\x00"
    b"\x00\x00\x00IEND\xaeB`\x82"
)

_JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 80


class TestValidateFirmaBase64:
    def test_valid_png(self):
        payload = base64.b64encode(_PNG_BYTES).decode("ascii")
        raw = validate_firma_base64(payload, max_bytes=1024)
        assert raw == _PNG_BYTES

    def test_valid_png_with_data_uri(self):
        payload = "data:image/png;base64," + base64.b64encode(_PNG_BYTES).decode("ascii")
        raw = validate_firma_base64(payload, max_bytes=1024)
        assert raw == _PNG_BYTES

    def test_valid_jpeg(self):
        payload = base64.b64encode(_JPEG_BYTES).decode("ascii")
        raw = validate_firma_base64(payload, max_bytes=1024)
        assert raw == _JPEG_BYTES

    def test_empty_rejected(self):
        with pytest.raises(UploadInvalidError):
            validate_firma_base64("", max_bytes=1024)

    def test_invalid_base64(self):
        with pytest.raises(UploadInvalidError, match="base64"):
            validate_firma_base64("not-base64!!!", max_bytes=1024)

    def test_svg_rejected_upfront(self):
        # Incluso sin llegar a decodificar, el filtro textual rechaza SVG
        with pytest.raises(UploadInvalidError, match="SVG"):
            validate_firma_base64(
                "data:image/svg+xml;base64,PHN2ZyB4bWxucz0...",
                max_bytes=1024,
            )

    def test_unknown_format_rejected(self):
        # bytes que no son PNG/JPEG/GIF
        bad = b"HELLO_WORLD_NOT_AN_IMAGE" + b"\x00" * 80
        payload = base64.b64encode(bad).decode("ascii")
        with pytest.raises(UploadInvalidError, match="PNG, JPEG o GIF"):
            validate_firma_base64(payload, max_bytes=1024)

    def test_too_large(self):
        big = _PNG_BYTES + b"\x00" * 2000
        payload = base64.b64encode(big).decode("ascii")
        with pytest.raises(UploadTooLargeError):
            validate_firma_base64(payload, max_bytes=256)

    def test_too_small(self):
        tiny = b"\x89PN"  # 4 bytes
        payload = base64.b64encode(tiny).decode("ascii")
        with pytest.raises(UploadInvalidError, match="vacía|corrupta"):
            validate_firma_base64(payload, max_bytes=1024)
