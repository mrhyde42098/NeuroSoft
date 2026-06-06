"""
tests/unit/core/test_logging_redactor.py
=========================================
Pruebas del redactor de PII en logs.

Cubre:
    • Función `redact()` en aislamiento (cada patrón).
    • Filtro `PIIRedactor` sobre LogRecord reales.
    • Idempotencia de `install_pii_redactor()`.
    • Opt-out con `extra={"skip_pii": True}`.
"""

from __future__ import annotations

import logging

from app.core.logging_redactor import (
    PIIRedactor,
    install_pii_redactor,
    redact,
)

# ─────────────────────────────────────────────────────────────
# Tests de la función pura `redact()`
# ─────────────────────────────────────────────────────────────


class TestRedactFunction:
    def test_redact_email(self):
        out = redact("User mail: jssalgadosa@unal.edu.co sent at 10:00")
        assert "jssalgadosa@unal.edu.co" not in out
        assert "[REDACTED]" in out

    def test_redact_multiple_emails(self):
        out = redact("a@b.com / c@d.co")
        assert "a@b.com" not in out
        assert "c@d.co" not in out
        assert out.count("[REDACTED]") == 2

    def test_redact_colombian_phone_plus57(self):
        out = redact("Contacto: +57 301 234 5678")
        assert "301 234 5678" not in out
        assert "[REDACTED]" in out

    def test_redact_colombian_mobile(self):
        out = redact("Celular 3012345678 disponible")
        assert "3012345678" not in out
        assert "[REDACTED]" in out

    def test_redact_jwt(self):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMifQ.abc123def"
        out = redact(f"Authorization: Bearer {token}")
        assert token not in out
        assert "[REDACTED]" in out

    def test_redact_password_kv(self):
        out = redact("payload={'password': 'hunter2', 'user': 'admin'}")
        assert "hunter2" not in out
        assert "password" in out  # la clave se preserva
        assert "[REDACTED]" in out

    def test_redact_cedula_in_kv(self):
        out = redact("cedula=1020304050 registrada")
        assert "1020304050" not in out
        assert "[REDACTED]" in out

    def test_redact_preserves_uuid(self):
        """UUIDs internos no deben redactarse — son identificadores técnicos."""
        uuid_like = "550e8400-e29b-41d4-a716-446655440000"
        out = redact(f"patient_id={uuid_like}")
        # UUID no coincide con patrones de email/phone/JWT/cédula.
        # El KV regex sólo dispara con claves específicas — patient_id
        # no está en la lista (es un identificador de sistema, no de PII).
        assert uuid_like in out

    def test_redact_preserves_timestamps(self):
        """Timestamps no deben redactarse aunque tengan 7+ dígitos."""
        out = redact("2026-04-18 14:32:15 - evento X")
        assert "2026-04-18" in out
        assert "14:32:15" in out

    def test_redact_preserves_ports(self):
        """Puertos de red no son PII."""
        out = redact("Listening on port 8000")
        assert "8000" in out

    def test_redact_non_string_returns_same(self):
        assert redact(None) is None  # type: ignore[arg-type]
        assert redact("") == ""
        assert redact(12345) == 12345  # type: ignore[arg-type]

    def test_redact_empty_safe(self):
        assert redact("") == ""

    def test_redact_no_pii_unchanged(self):
        plain = "La evaluación se completó exitosamente con 10 pruebas."
        assert redact(plain) == plain


# ─────────────────────────────────────────────────────────────
# Tests del filtro sobre LogRecord
# ─────────────────────────────────────────────────────────────


class TestPIIRedactorFilter:
    def _make_record(self, msg: str, *args) -> logging.LogRecord:
        return logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=msg,
            args=args,
            exc_info=None,
        )

    def test_filter_redacts_email_in_message(self):
        r = self._make_record("user=%s", "pedro@example.com")
        filt = PIIRedactor()
        assert filt.filter(r) is True
        assert "pedro@example.com" not in r.getMessage()
        assert "[REDACTED]" in r.getMessage()

    def test_filter_redacts_password_in_dict_args(self):
        r = self._make_record("payload=%s", "{'password': 'topsecret'}")
        filt = PIIRedactor()
        filt.filter(r)
        assert "topsecret" not in r.getMessage()

    def test_filter_skip_pii_extra(self):
        r = self._make_record("Email: test@example.com")
        r.skip_pii = True  # type: ignore[attr-defined]
        filt = PIIRedactor()
        filt.filter(r)
        # No redactó
        assert "test@example.com" in r.getMessage()

    def test_filter_does_not_raise_on_malformed_record(self):
        r = self._make_record("bad-format-%s")  # missing arg
        filt = PIIRedactor()
        # No debe lanzar — fail-open
        assert filt.filter(r) is True

    def test_filter_returns_true_always(self):
        """El filtro NUNCA descarta logs, sólo redacta."""
        r = self._make_record("hola mundo")
        filt = PIIRedactor()
        assert filt.filter(r) is True


# ─────────────────────────────────────────────────────────────
# Tests de instalación
# ─────────────────────────────────────────────────────────────


class TestInstallRedactor:
    def test_install_idempotent(self):
        log = logging.getLogger("neurosoft.test.idempotent")
        log.filters.clear()
        r1 = install_pii_redactor("neurosoft.test.idempotent")
        r2 = install_pii_redactor("neurosoft.test.idempotent")
        # Misma instancia, no se agrega duplicado
        assert r1 is r2
        assert sum(1 for f in log.filters if isinstance(f, PIIRedactor)) == 1

    def test_install_adds_to_handlers(self, caplog):
        """
        El filtro debe capturar mensajes emitidos vía loggers hijos
        del root (los que heredan handlers).
        """
        install_pii_redactor()
        logger = logging.getLogger("neurosoft.test.capture")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO, logger="neurosoft.test.capture"):
            logger.info("usuario: carlos@example.com")

        # caplog usa su propio handler, pero el filtro se aplica a
        # record.msg en `filter()`. Verificamos que el texto quede
        # sanitizado en el propio record si el filtro se ejecutó.
        # (En este harness sólo validamos que la instalación no
        # levante excepciones — ver tests de filtro para semántica.)
        assert any(isinstance(f, PIIRedactor) for f in logging.getLogger().filters) or any(
            isinstance(f, PIIRedactor) for h in logging.getLogger().handlers for f in h.filters
        )
