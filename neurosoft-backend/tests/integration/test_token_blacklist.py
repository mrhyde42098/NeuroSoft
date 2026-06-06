"""
tests/integration/test_token_blacklist.py
============================================
Revocación explícita de JWTs (logout real).

Un JWT sin blacklist es imposible de invalidar antes de su `exp`. Esta suite
valida que:

  1. `create_access_token` incluye un `jti` único por token.
  2. `revoke_token` es idempotente (insertar 2× no lanza).
  3. `is_token_revoked` distingue tokens revocados y no revocados.
  4. `purge_expired_blacklist_entries` borra solo lo caducado.
  5. El dependency `get_current_user` rechaza un token revocado con 401
     aunque el JWT siga criptográficamente válido.
  6. Dos sesiones del mismo usuario (dos logins) tienen jtis distintos:
     revocar una no debe afectar la otra.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

# ═══════════════════════════════════════════════════════════════
# 1. JTI EN EL TOKEN
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAccessTokenHasJti:
    def test_create_access_token_incluye_jti(self):
        from app.infrastructure.auth.auth_service import (
            create_access_token,
            decode_access_token,
        )

        tok = create_access_token("user-1", "admin", username="alice")
        payload = decode_access_token(tok)
        assert "jti" in payload
        assert isinstance(payload["jti"], str)
        assert len(payload["jti"]) >= 32  # uuid4 canónico

    def test_dos_tokens_tienen_jti_distintos(self):
        from app.infrastructure.auth.auth_service import (
            create_access_token,
            decode_access_token,
        )

        t1 = create_access_token("user-1", "admin")
        t2 = create_access_token("user-1", "admin")
        p1 = decode_access_token(t1)
        p2 = decode_access_token(t2)
        assert p1["jti"] != p2["jti"]

    def test_username_se_propaga_al_payload(self):
        from app.infrastructure.auth.auth_service import (
            create_access_token,
            decode_access_token,
        )

        tok = create_access_token("user-1", "profesional", username="bob")
        payload = decode_access_token(tok)
        assert payload.get("username") == "bob"

    def test_create_access_token_sin_username_funciona(self):
        """Retrocompat: llamar sin username (como antes del feature) debe seguir OK."""
        from app.infrastructure.auth.auth_service import (
            create_access_token,
            decode_access_token,
        )

        tok = create_access_token("user-9", "viewer")
        payload = decode_access_token(tok)
        assert payload["sub"] == "user-9"
        assert "username" not in payload  # no obligatorio


# ═══════════════════════════════════════════════════════════════
# 2. REVOCACIÓN — capa de persistencia
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestRevokeToken:
    def test_revoke_inserta_en_blacklist(self, in_memory_db):
        from app.infrastructure.auth.auth_service import (
            is_token_revoked,
            revoke_token,
        )

        jti = "jti-test-001"
        assert is_token_revoked(in_memory_db, jti) is False

        revoke_token(
            in_memory_db,
            jti=jti,
            user_id="user-abc",
            expires_at=datetime.now(UTC) + timedelta(hours=8),
            reason="logout",
        )
        in_memory_db.commit()

        assert is_token_revoked(in_memory_db, jti) is True

    def test_revoke_dos_veces_es_idempotente(self, in_memory_db):
        """No lanza y no crea duplicados."""
        from app.infrastructure.auth.auth_service import revoke_token
        from app.infrastructure.database.orm_models import TokenBlacklistORM

        jti = "jti-duplicado"
        exp = datetime.now(UTC) + timedelta(hours=1)
        revoke_token(in_memory_db, jti, "u1", exp, "logout")
        in_memory_db.commit()
        revoke_token(in_memory_db, jti, "u1", exp, "logout")  # repetir
        in_memory_db.commit()

        n = in_memory_db.query(TokenBlacklistORM).filter_by(jti=jti).count()
        assert n == 1

    def test_is_revoked_con_jti_vacio_retorna_false(self, in_memory_db):
        """Tokens legacy emitidos antes del feature no deben romperse."""
        from app.infrastructure.auth.auth_service import is_token_revoked

        assert is_token_revoked(in_memory_db, "") is False
        assert is_token_revoked(in_memory_db, None) is False  # type: ignore[arg-type]

    def test_purge_elimina_solo_caducados(self, in_memory_db):
        from app.infrastructure.auth.auth_service import (
            purge_expired_blacklist_entries,
            revoke_token,
        )
        from app.infrastructure.database.orm_models import TokenBlacklistORM

        now = datetime.now(UTC)
        # Uno caducado hace 1h, otro vigente por 1h
        revoke_token(in_memory_db, "expirado", "u1", now - timedelta(hours=1), "logout")
        revoke_token(in_memory_db, "vigente", "u2", now + timedelta(hours=1), "logout")
        in_memory_db.commit()

        deleted = purge_expired_blacklist_entries(in_memory_db)
        in_memory_db.commit()

        assert deleted == 1
        remaining = {x.jti for x in in_memory_db.query(TokenBlacklistORM).all()}
        assert remaining == {"vigente"}

    def test_revoke_guarda_motivo(self, in_memory_db):
        """El campo `reason` permite distinguir logout voluntario vs. revocación admin."""
        from app.infrastructure.auth.auth_service import revoke_token
        from app.infrastructure.database.orm_models import TokenBlacklistORM

        exp = datetime.now(UTC) + timedelta(hours=1)
        revoke_token(in_memory_db, "jti-admin", "u1", exp, reason="admin_revoked")
        in_memory_db.commit()

        entry = in_memory_db.query(TokenBlacklistORM).filter_by(jti="jti-admin").one()
        assert entry.reason == "admin_revoked"


# ═══════════════════════════════════════════════════════════════
# 3. GET_CURRENT_USER — rechaza tokens revocados
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestGetCurrentUserRejectsRevokedTokens:
    """
    Prueba el dependency `get_current_user` sin levantar toda la app:
    es la misma lógica que usan todos los endpoints protegidos.
    """

    def _make_user(self, db):
        from app.infrastructure.auth.auth_service import UserRepository

        repo = UserRepository(db)
        user = repo.create(
            username="revoker",
            password_plain="segura1234",
            nombre_completo="Revoker Test",
            role="profesional",
        )
        db.commit()
        return user

    def test_token_valido_retorna_usuario(self, in_memory_db):
        from fastapi.security import HTTPAuthorizationCredentials

        from app.infrastructure.auth.auth_service import create_access_token
        from app.presentation.api.v1.auth import get_current_user

        user = self._make_user(in_memory_db)
        tok = create_access_token(user.id, user.role, username=user.username)
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok)

        result = get_current_user(credentials=creds, db=in_memory_db)
        assert result.id == user.id

    def test_token_revocado_lanza_401(self, in_memory_db):
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        from app.infrastructure.auth.auth_service import (
            create_access_token,
            decode_access_token,
            revoke_token,
        )
        from app.presentation.api.v1.auth import get_current_user

        user = self._make_user(in_memory_db)
        tok = create_access_token(user.id, user.role, username=user.username)
        payload = decode_access_token(tok)

        # Revocar ese jti
        revoke_token(
            in_memory_db,
            jti=payload["jti"],
            user_id=user.id,
            expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
            reason="logout",
        )
        in_memory_db.commit()

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=creds, db=in_memory_db)
        assert exc_info.value.status_code == 401
        assert "revoc" in str(exc_info.value.detail).lower()

    def test_dos_sesiones_independientes_revocacion_no_se_contagia(self, in_memory_db):
        """
        Dos logins del mismo usuario → dos jtis. Revocar uno no afecta al otro.
        """
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        from app.infrastructure.auth.auth_service import (
            create_access_token,
            decode_access_token,
            revoke_token,
        )
        from app.presentation.api.v1.auth import get_current_user

        user = self._make_user(in_memory_db)
        tok1 = create_access_token(user.id, user.role, username=user.username)
        tok2 = create_access_token(user.id, user.role, username=user.username)
        p1 = decode_access_token(tok1)
        p2 = decode_access_token(tok2)
        assert p1["jti"] != p2["jti"]

        # Revocar solo el primero
        revoke_token(
            in_memory_db,
            jti=p1["jti"],
            user_id=user.id,
            expires_at=datetime.fromtimestamp(p1["exp"], tz=UTC),
            reason="logout",
        )
        in_memory_db.commit()

        # El primero falla
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(
                credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok1),
                db=in_memory_db,
            )
        assert exc_info.value.status_code == 401

        # El segundo sigue funcionando
        result = get_current_user(
            credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok2),
            db=in_memory_db,
        )
        assert result.id == user.id

    def test_token_de_usuario_inactivo_401(self, in_memory_db):
        """Regression: si el usuario está inactivo, no debe poder autenticarse."""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        from app.infrastructure.auth.auth_service import (
            UserRepository,
            create_access_token,
        )
        from app.presentation.api.v1.auth import get_current_user

        user = self._make_user(in_memory_db)
        tok = create_access_token(user.id, user.role, username=user.username)

        # Desactivarlo
        UserRepository(in_memory_db).deactivate(user.id)
        in_memory_db.commit()

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=creds, db=in_memory_db)
        assert exc_info.value.status_code == 401


# ═══════════════════════════════════════════════════════════════
# 4. ENDPOINT LOGOUT — test directo de la función
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestLogoutEndpointFunction:
    """
    Prueba la función `logout` sin TestClient. Simula lo que FastAPI
    inyectaría y verifica los efectos colaterales (blacklist + auditoría).
    """

    def _make_user_and_token(self, db):
        from app.infrastructure.auth.auth_service import (
            UserRepository,
            create_access_token,
        )

        repo = UserRepository(db)
        user = repo.create(
            username="logouttest",
            password_plain="segura1234",
            nombre_completo="Logout Test",
            role="profesional",
        )
        db.commit()
        tok = create_access_token(user.id, user.role, username=user.username)
        return user, tok

    def test_logout_inserta_jti_en_blacklist(self, in_memory_db):
        from unittest.mock import MagicMock

        from fastapi.security import HTTPAuthorizationCredentials

        from app.infrastructure.auth.auth_service import (
            decode_access_token,
            is_token_revoked,
        )
        from app.infrastructure.database.orm_models import TokenBlacklistORM
        from app.presentation.api.v1.auth import logout

        user, tok = self._make_user_and_token(in_memory_db)
        payload = decode_access_token(tok)
        assert is_token_revoked(in_memory_db, payload["jti"]) is False

        # Simular FastAPI: request mock + credenciales + current_user
        req = MagicMock()
        req.client = MagicMock(host="127.0.0.1")
        req.headers = {}

        logout(
            request=req,
            db=in_memory_db,
            credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok),
            current_user=user,
        )
        in_memory_db.commit()

        assert is_token_revoked(in_memory_db, payload["jti"]) is True
        entry = in_memory_db.query(TokenBlacklistORM).filter_by(jti=payload["jti"]).one()
        assert entry.user_id == user.id
        assert entry.reason == "logout"

    def test_logout_registra_auditoria(self, in_memory_db):
        from unittest.mock import MagicMock

        from fastapi.security import HTTPAuthorizationCredentials

        from app.infrastructure.database.orm_models import AuditLogORM
        from app.presentation.api.v1.auth import logout

        user, tok = self._make_user_and_token(in_memory_db)
        req = MagicMock()
        req.client = MagicMock(host="127.0.0.1")
        req.headers = {}

        logout(
            request=req,
            db=in_memory_db,
            credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok),
            current_user=user,
        )
        in_memory_db.commit()

        logs = (
            in_memory_db.query(AuditLogORM)
            .filter(AuditLogORM.action == "logout", AuditLogORM.entity_id == user.id)
            .all()
        )
        assert len(logs) >= 1

    def test_logout_idempotente(self, in_memory_db):
        """Llamar logout 2× con el mismo token no lanza; el jti sigue revocado."""
        from unittest.mock import MagicMock

        from fastapi.security import HTTPAuthorizationCredentials

        from app.infrastructure.auth.auth_service import decode_access_token, is_token_revoked
        from app.presentation.api.v1.auth import logout

        user, tok = self._make_user_and_token(in_memory_db)
        req = MagicMock()
        req.client = MagicMock(host="127.0.0.1")
        req.headers = {}
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok)

        logout(request=req, db=in_memory_db, credentials=creds, current_user=user)
        logout(request=req, db=in_memory_db, credentials=creds, current_user=user)
        in_memory_db.commit()

        jti = decode_access_token(tok)["jti"]
        assert is_token_revoked(in_memory_db, jti) is True
