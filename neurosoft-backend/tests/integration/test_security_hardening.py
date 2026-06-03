"""
tests/integration/test_security_hardening.py
==============================================
Conjunto de mejoras de seguridad/observabilidad incrementales:

  1. Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
  2. X-Request-ID en cada respuesta + propagación al audit log
  3. Cambio de contraseña invalida sesiones anteriores
  4. Endpoint admin POST /auth/users/{id}/revoke-tokens

Las pruebas que requieren TestClient comparten una BD real ad-hoc creada
por la `lifespan` de FastAPI; las que prueban lógica interna (revocación,
sentinels) usan la fixture `in_memory_db` aislada.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

# ═══════════════════════════════════════════════════════════════
# 1. SECURITY HEADERS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestSecurityHeaders:
    """
    Cualquier respuesta del backend debe incluir un set mínimo de
    encabezados defensivos. Lo verificamos contra el endpoint público
    `/health` para no requerir token.
    """

    @pytest.fixture(scope="class")
    def client(self):
        from fastapi.testclient import TestClient

        from app.main import app
        with TestClient(app) as c:
            yield c

    def test_health_incluye_x_content_type_options(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.headers.get("x-content-type-options") == "nosniff"

    def test_health_incluye_x_frame_options(self, client):
        r = client.get("/health")
        assert r.headers.get("x-frame-options") == "DENY"

    def test_health_incluye_referrer_policy(self, client):
        r = client.get("/health")
        rp = r.headers.get("referrer-policy", "").lower()
        assert "strict-origin" in rp

    def test_health_incluye_permissions_policy(self, client):
        r = client.get("/health")
        pp = r.headers.get("permissions-policy", "")
        # debe denegar APIs sensibles
        assert "geolocation=()" in pp
        assert "camera=()" in pp
        assert "microphone=()" in pp

    def test_health_incluye_x_permitted_cross_domain_policies(self, client):
        r = client.get("/health")
        assert r.headers.get("x-permitted-cross-domain-policies") == "none"

    def test_hsts_solo_en_produccion(self, client):
        """En desarrollo NO emitimos HSTS para no envenenar browsers locales."""
        r = client.get("/health")
        # En el entorno de tests env=development, no debería estar.
        from app.core.config import settings
        if settings.env != "production":
            assert "strict-transport-security" not in {
                k.lower() for k in r.headers.keys()
            }


# ═══════════════════════════════════════════════════════════════
# 2. X-Request-ID
# ═══════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestHealthOperational:
    """`/health` debe exponer métricas operativas para monitoreo."""

    @pytest.fixture(scope="class")
    def client(self):
        from fastapi.testclient import TestClient

        from app.main import app
        with TestClient(app) as c:
            yield c

    def test_health_devuelve_seccion_operational(self, client):
        r = client.get("/health")
        body = r.json()
        assert "operational" in body
        op = body["operational"]
        # Si no hubo error infra, deben venir las métricas
        if "error" not in op:
            assert "audit_log_count" in op
            assert "token_blacklist_count" in op
            assert "last_backup" in op
            assert isinstance(op["audit_log_count"], int)
            assert isinstance(op["token_blacklist_count"], int)
            assert op["audit_log_count"] >= 0
            assert op["token_blacklist_count"] >= 0


@pytest.mark.integration
class TestRequestId:

    @pytest.fixture(scope="class")
    def client(self):
        from fastapi.testclient import TestClient

        from app.main import app
        with TestClient(app) as c:
            yield c

    def test_response_incluye_x_request_id_autogenerado(self, client):
        r = client.get("/health")
        rid = r.headers.get("x-request-id")
        assert rid is not None
        assert len(rid) >= 8

    def test_response_respeta_x_request_id_del_cliente(self, client):
        r = client.get("/health", headers={"X-Request-ID": "miRequestId-001"})
        # debe devolverlo tal cual (sanitizado)
        assert r.headers.get("x-request-id") == "miRequestId-001"

    def test_x_request_id_se_sanitiza(self, client):
        """Caracteres no imprimibles no deben llegar a los logs (log forging)."""
        r = client.get("/health", headers={"X-Request-ID": "abc\r\n[FAKE-LOG]"})
        rid = r.headers.get("x-request-id", "")
        assert "\r" not in rid
        assert "\n" not in rid
        # los corchetes y otros símbolos no alfanuméricos también se descartan
        assert "[" not in rid

    def test_two_requests_tienen_rids_distintos(self, client):
        r1 = client.get("/health")
        r2 = client.get("/health")
        assert r1.headers.get("x-request-id") != r2.headers.get("x-request-id")


@pytest.mark.integration
class TestRequestIdPropagaAuditoria:
    """
    El asiento de auditoría debe llevar el mismo X-Request-ID del request
    que lo generó — así se correlaciona con los logs del proceso.
    """

    def test_record_event_persiste_request_id(self, in_memory_db):
        from unittest.mock import MagicMock

        from app.infrastructure.audit import record_event
        from app.infrastructure.database.orm_models import AuditLogORM

        # Mock request con request_id en state
        req = MagicMock()
        req.state = MagicMock(request_id="abcdef0123456789")
        req.client = MagicMock(host="127.0.0.1")
        req.headers = {"user-agent": "pytest"}

        record_event(
            in_memory_db,
            action="test",
            entity_type="auth",
            entity_id="u1",
            actor_id="u1",
            actor_label="tester",
            summary="prueba rid",
            request=req,
            commit=False,
        )
        in_memory_db.commit()

        log = (
            in_memory_db.query(AuditLogORM)
            .filter(AuditLogORM.action == "test")
            .one()
        )
        assert log.request_id == "abcdef0123456789"

    def test_record_event_usa_contextvar_si_no_hay_request(self, in_memory_db):
        from app.core.request_context import current_request_id
        from app.infrastructure.audit import record_event
        from app.infrastructure.database.orm_models import AuditLogORM

        tok = current_request_id.set("ctx-rid-xyz")
        try:
            record_event(
                in_memory_db,
                action="test_ctx",
                entity_type="auth",
                actor_id="u1",
                actor_label="tester",
                summary="sin request",
                commit=False,
            )
            in_memory_db.commit()
        finally:
            current_request_id.reset(tok)

        log = (
            in_memory_db.query(AuditLogORM)
            .filter(AuditLogORM.action == "test_ctx")
            .one()
        )
        assert log.request_id == "ctx-rid-xyz"


# ═══════════════════════════════════════════════════════════════
# 3. CAMBIO DE CONTRASEÑA REVOCA SESIONES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestRevokeAllUserTokens:

    def _make_user(self, db):
        from app.infrastructure.auth.auth_service import UserRepository
        repo = UserRepository(db)
        u = repo.create(
            username="multi_session",
            password_plain="segura1234",
            nombre_completo="Multi Session",
            role="profesional",
        )
        db.commit()
        return u

    def test_revoke_all_inserta_sentinel(self, in_memory_db):
        from app.infrastructure.auth.auth_service import revoke_all_user_tokens
        from app.infrastructure.database.orm_models import TokenBlacklistORM

        user = self._make_user(in_memory_db)
        revoke_all_user_tokens(in_memory_db, user.id, reason="password_change")
        in_memory_db.commit()

        sentinel = (
            in_memory_db.query(TokenBlacklistORM)
            .filter_by(jti=f"user:{user.id}")
            .one()
        )
        assert sentinel.user_id == user.id
        assert sentinel.reason == "password_change"

    def test_revoke_all_es_idempotente(self, in_memory_db):
        """Llamar 2× actualiza la sentinel pero no duplica filas."""
        from app.infrastructure.auth.auth_service import revoke_all_user_tokens
        from app.infrastructure.database.orm_models import TokenBlacklistORM

        user = self._make_user(in_memory_db)
        revoke_all_user_tokens(in_memory_db, user.id, "password_change")
        in_memory_db.commit()
        revoke_all_user_tokens(in_memory_db, user.id, "admin_revoked")
        in_memory_db.commit()

        rows = (
            in_memory_db.query(TokenBlacklistORM)
            .filter_by(jti=f"user:{user.id}")
            .all()
        )
        assert len(rows) == 1
        assert rows[0].reason == "admin_revoked"

    def test_token_emitido_antes_se_invalida(self, in_memory_db):
        """
        Token emitido a t0, sentinel insertada a t1 > t0 → token rechazado
        por `is_user_session_revoked`.
        """
        from app.infrastructure.auth.auth_service import (
            create_access_token,
            decode_access_token,
            is_user_session_revoked,
            revoke_all_user_tokens,
        )

        user = self._make_user(in_memory_db)
        # Emitir token con iat 1h en el pasado
        tok = create_access_token(user.id, user.role)
        _payload = decode_access_token(tok)
        # Forzar iat al pasado para la prueba
        old_iat = int(
            (datetime.now(UTC) - timedelta(hours=1)).timestamp()
        )

        # Antes de la sentinel
        assert is_user_session_revoked(in_memory_db, user.id, old_iat) is False

        # Insertar sentinel ahora
        revoke_all_user_tokens(in_memory_db, user.id, reason="password_change")
        in_memory_db.commit()

        # Token "viejo" ya no vale
        assert is_user_session_revoked(in_memory_db, user.id, old_iat) is True

    def test_token_emitido_despues_sigue_valido(self, in_memory_db):
        """
        Si el usuario hace login DESPUÉS de la revocación, su nuevo token
        debe seguir funcionando.
        """
        from app.infrastructure.auth.auth_service import (
            is_user_session_revoked,
            revoke_all_user_tokens,
        )

        user = self._make_user(in_memory_db)
        revoke_all_user_tokens(in_memory_db, user.id, reason="admin_revoked")
        in_memory_db.commit()

        # Token nuevo: iat = ahora + 1s (claramente posterior a la sentinel)
        future_iat = int(
            (datetime.now(UTC) + timedelta(seconds=1)).timestamp()
        )
        assert is_user_session_revoked(in_memory_db, user.id, future_iat) is False

    def test_get_current_user_rechaza_token_pre_revocacion(self, in_memory_db):
        from datetime import datetime as _dt
        from datetime import timedelta as _td

        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials
        from jose import jwt as _jwt

        from app.infrastructure.auth.auth_service import (
            ALGORITHM,
            SECRET_KEY,
            revoke_all_user_tokens,
        )
        from app.presentation.api.v1.auth import get_current_user

        user = self._make_user(in_memory_db)

        # Construir un token con iat en el pasado (no usar create_access_token
        # porque pone iat=ahora). Aún así el JWT es válido criptográficamente.
        old_iat = _dt.now(UTC) - _td(hours=1)
        payload = {
            "sub": user.id,
            "role": user.role,
            "type": "access",
            "jti": "vieja-jti",
            "iat": int(old_iat.timestamp()),
            "exp": _dt.now(UTC) + _td(hours=1),
            "username": user.username,
        }
        old_token = _jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Revocar todas las sesiones AHORA
        revoke_all_user_tokens(in_memory_db, user.id, reason="password_change")
        in_memory_db.commit()

        # El dependency rechaza
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(
                credentials=HTTPAuthorizationCredentials(
                    scheme="Bearer", credentials=old_token,
                ),
                db=in_memory_db,
            )
        assert exc_info.value.status_code == 401
        assert "invalidad" in str(exc_info.value.detail).lower()


# ═══════════════════════════════════════════════════════════════
# 4. ENDPOINT ADMIN — REVOKE TOKENS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestAdminRevokeEndpoint:
    """Prueba directa de la función `admin_revoke_user_tokens`."""

    def _make_admin_and_user(self, db):
        from app.infrastructure.auth.auth_service import UserRepository
        repo = UserRepository(db)
        admin = repo.create(
            username="admin42",
            password_plain="admin1234",
            nombre_completo="Admin",
            role="admin",
        )
        target = repo.create(
            username="target",
            password_plain="target1234",
            nombre_completo="Target",
            role="profesional",
        )
        db.commit()
        return admin, target

    def test_admin_revoke_inserta_sentinel_y_audita(self, in_memory_db):
        from unittest.mock import MagicMock

        from app.infrastructure.database.orm_models import (
            AuditLogORM,
            TokenBlacklistORM,
        )
        from app.presentation.api.v1.auth import admin_revoke_user_tokens

        admin, target = self._make_admin_and_user(in_memory_db)

        req = MagicMock()
        req.state = MagicMock(user_id=admin.id, request_id="rid-xyz")
        req.client = MagicMock(host="10.0.0.1")
        req.headers = {}

        admin_revoke_user_tokens(
            user_id=target.id,
            request=req,
            db=in_memory_db,
            admin=admin,
        )
        in_memory_db.commit()

        # Sentinel creada
        sentinel = (
            in_memory_db.query(TokenBlacklistORM)
            .filter_by(jti=f"user:{target.id}")
            .one()
        )
        assert sentinel.reason == "admin_revoked"
        assert sentinel.user_id == target.id

        # Auditoría
        log = (
            in_memory_db.query(AuditLogORM)
            .filter(
                AuditLogORM.action == "admin_revoke_tokens",
                AuditLogORM.entity_id == target.id,
            )
            .one()
        )
        assert log.actor_id == admin.id
        assert "target" in (log.summary or "")

    def test_admin_revoke_404_si_usuario_inexistente(self, in_memory_db):
        from unittest.mock import MagicMock

        from fastapi import HTTPException

        from app.presentation.api.v1.auth import admin_revoke_user_tokens

        admin, _ = self._make_admin_and_user(in_memory_db)
        req = MagicMock()
        req.state = MagicMock(user_id=admin.id, request_id="rid-xyz")
        req.client = MagicMock(host="10.0.0.1")
        req.headers = {}

        with pytest.raises(HTTPException) as exc_info:
            admin_revoke_user_tokens(
                user_id="no-existe",
                request=req,
                db=in_memory_db,
                admin=admin,
            )
        assert exc_info.value.status_code == 404
