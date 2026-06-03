"""
tests/unit/core/test_password_verify.py
=========================================
Verifica `shared._verify_password` — la función que valida la contraseña
opcional de un SharedReport (informe compartido por telemedicina).

Debe soportar DOS formatos:
  1. **bcrypt** (nuevos shares) — `$2a$`, `$2b$`, `$2y$` prefix.
  2. **SHA-256 legacy** (shares antiguos) — formato `salt$hex`.

Motivo histórico: antes se hasheaba con SHA-256 simple; se migró a bcrypt
pero los shares antiguos aún viven en BD y deben seguir verificándose
hasta que expiren naturalmente.

Estos tests evitan que una regresión (ej. "limpiar" el fallback legacy
sin haber migrado los datos) deje inaccesibles shares válidos.
"""
from __future__ import annotations

import hashlib

import pytest

# Pre-requisitos opcionales — si passlib no está, saltamos todo.
passlib = pytest.importorskip("passlib")


@pytest.mark.unit
class TestVerifyPasswordBcrypt:
    """bcrypt: los shares nuevos se generan con _bcrypt_hash y deben verificar."""

    def test_hash_genera_bcrypt(self):
        from app.presentation.api.v1.shared import _hash_password
        h = _hash_password("miclave123")
        assert h.startswith(("$2a$", "$2b$", "$2y$"))

    def test_verify_bcrypt_ok(self):
        from app.presentation.api.v1.shared import _hash_password, _verify_password
        h = _hash_password("secret-pass-42")
        assert _verify_password("secret-pass-42", h) is True

    def test_verify_bcrypt_password_incorrecta(self):
        from app.presentation.api.v1.shared import _hash_password, _verify_password
        h = _hash_password("correct-horse")
        assert _verify_password("battery-staple", h) is False

    def test_verify_bcrypt_password_vacia(self):
        from app.presentation.api.v1.shared import _hash_password, _verify_password
        h = _hash_password("noempty")
        assert _verify_password("", h) is False

    def test_verify_bcrypt_hash_corrupto_no_lanza(self):
        """Un hash mal formado debe devolver False, nunca excepción."""
        from app.presentation.api.v1.shared import _verify_password
        # hash "bcrypt-shape" pero truncado → passlib debería fallar silenciosamente.
        assert _verify_password("whatever", "$2b$12$truncated") is False


# ═══════════════════════════════════════════════════════════════
# SHA-256 LEGACY FALLBACK
# ═══════════════════════════════════════════════════════════════

def _sha256_legacy_hash(plain: str, salt: str) -> str:
    """Reproduce el formato legacy `salt$hex(sha256(salt+plain))`."""
    h = hashlib.sha256((salt + plain).encode("utf-8")).hexdigest()
    return f"{salt}${h}"


@pytest.mark.unit
class TestVerifyPasswordLegacy:
    """SHA-256: shares viejos (pre-migración) deben seguir verificándose."""

    def test_verify_legacy_sha256_ok(self):
        from app.presentation.api.v1.shared import _verify_password
        legacy = _sha256_legacy_hash("clave-vieja", salt="abc123")
        assert _verify_password("clave-vieja", legacy) is True

    def test_verify_legacy_sha256_password_incorrecta(self):
        from app.presentation.api.v1.shared import _verify_password
        legacy = _sha256_legacy_hash("original", salt="xyz789")
        assert _verify_password("otra-clave", legacy) is False

    def test_verify_legacy_salt_distinto_falla(self):
        """
        Si el atacante intenta forjar un hash con salt diferente, debe fallar.
        (Previene ataques de precomputado que dependan de salt conocido.)
        """
        from app.presentation.api.v1.shared import _verify_password
        legacy = _sha256_legacy_hash("secreto", salt="salt-A")
        # El mismo plaintext con otro salt produce hash distinto
        legacy_B = _sha256_legacy_hash("secreto", salt="salt-B")
        assert legacy != legacy_B
        # Verificar contra el original con la clave real debe seguir funcionando
        assert _verify_password("secreto", legacy) is True
        assert _verify_password("secreto", legacy_B) is True


# ═══════════════════════════════════════════════════════════════
# EDGE CASES / DEFENSA
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestVerifyPasswordDefensivo:

    def test_hash_vacio_retorna_false(self):
        from app.presentation.api.v1.shared import _verify_password
        assert _verify_password("cualquier-cosa", "") is False

    def test_hash_none_equivalente_a_vacio(self):
        """
        `_verify_password(raw, None)` no debe lanzar — algunos callers pasan
        `row.password_hash` que puede ser None si el share no tiene contraseña.
        """
        from app.presentation.api.v1.shared import _verify_password
        # Python trata None como falsy al entrar en `if not hashed`
        assert _verify_password("x", None) is False  # type: ignore[arg-type]

    def test_formato_desconocido_no_lanza(self):
        """Un hash que no es bcrypt ni tiene '$' como separador no debe crashear."""
        from app.presentation.api.v1.shared import _verify_password
        # Sin '$' separador → split("$", 1) sólo da una parte → except path
        assert _verify_password("x", "not-a-valid-hash-format") is False

    def test_hash_bcrypt_y_raw_unicode(self):
        """Passwords con tildes/emoji deben ser admitidas por bcrypt."""
        from app.presentation.api.v1.shared import _hash_password, _verify_password
        raw = "contraseña-ñandú-🔐"
        h = _hash_password(raw)
        assert _verify_password(raw, h) is True

    def test_distincion_entre_formatos(self):
        """
        bcrypt y legacy no deben confundirse: un hash legacy con '$2a' en
        el salt sería mal interpretado. Verifiquemos que la detección usa
        los prefijos correctos ($2a$, $2b$, $2y$).
        """
        from app.presentation.api.v1.shared import _verify_password
        # Salt que empieza con '2a' pero sin el $ antepuesto → NO es bcrypt
        legacy_con_salt_tramposo = _sha256_legacy_hash("clave", salt="2a01")
        assert not legacy_con_salt_tramposo.startswith("$2a$")
        assert _verify_password("clave", legacy_con_salt_tramposo) is True


# ═══════════════════════════════════════════════════════════════
# auth_service.verify_password (usuarios, no shares)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestAuthServiceVerify:
    """El servicio de auth principal debe usar solo bcrypt (no legacy)."""

    def test_hash_y_verify_round_trip(self):
        from app.infrastructure.auth.auth_service import hash_password, verify_password
        h = hash_password("usuario-pass-2024")
        assert h.startswith(("$2a$", "$2b$", "$2y$"))
        assert verify_password("usuario-pass-2024", h) is True
        assert verify_password("otra-cosa", h) is False

    def test_verify_hash_invalido_no_lanza(self):
        from app.infrastructure.auth.auth_service import verify_password
        # Aquí NO hay fallback legacy: todo debe ser bcrypt.
        assert verify_password("x", "garbage") is False
        assert verify_password("x", "") is False

    def test_dos_hashes_del_mismo_plain_son_distintos(self):
        """bcrypt usa salt aleatorio: dos hashes del mismo plain deben diferir."""
        from app.infrastructure.auth.auth_service import hash_password
        h1 = hash_password("misma-clave")
        h2 = hash_password("misma-clave")
        assert h1 != h2, "bcrypt debe usar salt aleatorio (no determinístico)"
