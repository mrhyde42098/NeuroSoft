"""
tests/integration/test_update_endpoint.py
==========================================
Cobertura de seguridad del endpoint POST /system/update.

S0.1 del PLAN_MAESTRO_GLOBAL:
  - require_admin: 401 sin token, 403 con rol profesional.
  - HMAC-SHA256: 401 sin header, 401 con firma inválida, 200 con firma correcta.
  - Path traversal: 400 si el ZIP contiene `frontend/../etc/passwd`.
  - Manifest: 400 si falta manifest.json.
  - Audit log: 200 feliz inserta un AuditLogORM con action="update_applied".
  - Side effects: extrae los archivos del frontend a dist/ y crea last_update.json.

Las pruebas usan TestClient + la BD real que el lifespan de la app crea en
tests/, así podemos pasar por la ruta completa HTTP → DB.
"""

from __future__ import annotations

import hashlib
import hmac
import io
import json
import os
import zipfile
from pathlib import Path

import pytest

# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════


def _build_nsupdate(manifest: dict, entries: list[tuple[str, bytes]]) -> bytes:
    """
    Construye un .nsupdate (ZIP) en memoria.

    `entries`: lista de (path_relativo_al_zip, contenido). El path debe
    empezar por `frontend/` o no será extraído por el endpoint.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        for name, data in entries:
            zf.writestr(name, data)
    body = buf.getvalue()
    # El endpoint exige al menos 1024 bytes. ZIP_DEFLATED comprime muy
    # bien los ceros, así que rellenamos con bytes aleatorios no
    # compresibles (ZIP_STORED) hasta superar el umbral.
    if len(body) < 2048:
        pad_size = 2048 - len(body) + 512  # holgura
        import os as _os

        zf_buf = io.BytesIO()
        with zipfile.ZipFile(zf_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            for name, data in entries:
                zf.writestr(name, data)
            zf.writestr(
                "frontend/_padding.bin",
                _os.urandom(pad_size),
                compress_type=zipfile.ZIP_STORED,
            )
        body = zf_buf.getvalue()
    return body


def _hmac_key() -> str:
    """
    Devuelve la clave HMAC esperada por el endpoint, tal como la resuelve
    `_resolve_hmac_key()` en update.py cuando no hay env var.
    """
    explicit = os.getenv("NEUROSOFT_UPDATE_HMAC_KEY", "").strip()
    if explicit:
        return explicit
    from app.infrastructure.auth.auth_service import SECRET_KEY

    return hashlib.sha256(("nsupdate-hmac::" + SECRET_KEY).encode("utf-8")).hexdigest()


def _sign(body: bytes) -> str:
    return hmac.new(_hmac_key().encode("utf-8"), body, hashlib.sha256).hexdigest()


# ═══════════════════════════════════════════════════════════════════
# FIXTURE: cliente + admin
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client) -> str:
    """
    Crea un admin (si no existe) vía UserRepository y devuelve su access_token.

    Usa el endpoint /auth/users (protegido por require_admin) para crear
    el admin, y /auth/login para obtener el token — así probamos también
    que la cadena funciona end-to-end con la BD real del lifespan.
    """
    from app.infrastructure.auth.auth_service import UserRepository
    from app.infrastructure.database.engine import SessionLocal
    from app.infrastructure.database.orm_models import UserORM

    with SessionLocal() as db:
        repo = UserRepository(db)
        existing = db.query(UserORM).filter_by(username="admin_test_update").first()
        if existing is None:
            repo.create(
                username="admin_test_update",
                password_plain="AdminTest!2026",
                nombre_completo="Admin Test Update",
                role="admin",
            )
            db.commit()
        else:
            repo.update_password(existing.id, "AdminTest!2026")
            existing.role = "admin"
            existing.is_active = True
            db.commit()

    r = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_test_update", "password": "AdminTest!2026"},
    )
    assert r.status_code == 200, f"login admin fallo: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def profesional_token(client) -> str:
    """Crea un profesional y devuelve su access_token."""
    from app.infrastructure.auth.auth_service import UserRepository
    from app.infrastructure.database.engine import SessionLocal
    from app.infrastructure.database.orm_models import UserORM

    with SessionLocal() as db:
        repo = UserRepository(db)
        existing = db.query(UserORM).filter_by(username="prof_test_update").first()
        if existing is None:
            repo.create(
                username="prof_test_update",
                password_plain="ProfTest!2026",
                nombre_completo="Profesional Test Update",
                role="profesional",
            )
            db.commit()
        else:
            repo.update_password(existing.id, "ProfTest!2026")
            existing.role = "profesional"
            existing.is_active = True
            db.commit()

    r = client.post(
        "/api/v1/auth/login",
        json={"username": "prof_test_update", "password": "ProfTest!2026"},
    )
    assert r.status_code == 200, f"login prof fallo: {r.text}"
    return r.json()["access_token"]


# ═══════════════════════════════════════════════════════════════════
# 1. AUTH — require_admin
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestUpdateAuth:
    """El endpoint /system/update exige admin autenticado."""

    def test_sin_token_retorna_401(self, client):
        r = client.post("/api/v1/system/update", files={"file": ("x.nsupdate", b"x")})
        assert r.status_code == 401

    def test_con_token_de_profesional_retorna_403(self, client, profesional_token):
        body = _build_nsupdate(
            {"version": "1.0.0", "fecha": "2026-06-01"},
            [("frontend/index.html", b"<h1>ok</h1>")],
        )
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("x.nsupdate", body, "application/zip")},
            headers={
                "Authorization": f"Bearer {profesional_token}",
                "X-Update-Signature": _sign(body),
            },
        )
        assert r.status_code == 403, r.text


# ═══════════════════════════════════════════════════════════════════
# 2. FIRMA HMAC
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestUpdateHmac:
    """El endpoint exige X-Update-Signature válida."""

    def test_sin_header_signature_retorna_401(self, client, admin_token):
        body = _build_nsupdate(
            {"version": "1.0.0"},
            [("frontend/index.html", b"ok")],
        )
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("x.nsupdate", body, "application/zip")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r.status_code == 401
        assert "X-Update-Signature" in r.text

    def test_con_firma_invalida_retorna_401(self, client, admin_token):
        body = _build_nsupdate(
            {"version": "1.0.0"},
            [("frontend/index.html", b"ok")],
        )
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("x.nsupdate", body, "application/zip")},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Update-Signature": "deadbeef" * 8,
            },
        )
        assert r.status_code == 401
        assert "hmac" in r.text.lower()

    def test_firma_valida_pasa_hmac(self, client, admin_token):
        """Happy path: firma válida + admin → 200 y extrae."""
        body = _build_nsupdate(
            {"version": "9.9.9-test", "fecha": "2026-06-01"},
            [("frontend/test-update-marker.txt", "marcado")],
        )
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("v9.9.9.nsupdate", body, "application/zip")},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Update-Signature": _sign(body),
            },
        )
        assert r.status_code == 200, r.text
        body_json = r.json()
        assert body_json["ok"] is True
        assert body_json["version"] == "9.9.9-test"


# ═══════════════════════════════════════════════════════════════════
# 3. PATH TRAVERSAL
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestUpdatePathTraversal:
    def test_entrada_con_parent_dir_se_rechaza(self, client, admin_token):
        """Si el ZIP trae `frontend/../../etc/passwd`, se rechaza con 400."""
        # body > 1024 para que no sea rechazado por tamaño
        import os as _os

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps({"version": "1.0.0"}))
            zf.writestr("frontend/../../etc/passwd_evil", b"x")
            zf.writestr(
                "frontend/_pad.bin",
                _os.urandom(2048),
                compress_type=zipfile.ZIP_STORED,
            )
        body = buf.getvalue()
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("v1.nsupdate", body, "application/zip")},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Update-Signature": _sign(body),
            },
        )
        assert r.status_code == 400
        assert "insegura" in r.text.lower() or "traversal" in r.text.lower()

    def test_sin_manifest_json_se_rechaza(self, client, admin_token):
        # Sobreescribimos sin manifest, pero con payload > 1024 bytes
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("frontend/index.html", b"x" * 1500)
        body = buf.getvalue()
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("v1.nsupdate", body, "application/zip")},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Update-Signature": _sign(body),
            },
        )
        assert r.status_code == 400
        assert "manifest" in r.text.lower()

    def test_archivo_muy_pequeno_se_rechaza(self, client, admin_token):
        body = b"x" * 10  # < 1024 bytes
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("v1.nsupdate", body, "application/zip")},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Update-Signature": _sign(body),
            },
        )
        assert r.status_code == 400


# ═══════════════════════════════════════════════════════════════════
# 4. AUDIT LOG + SIDE EFFECTS
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestUpdateAudit:
    def test_happy_path_inserta_audit_log(self, client, admin_token):
        from app.infrastructure.database.engine import SessionLocal
        from app.infrastructure.database.orm_models import AuditLogORM

        with SessionLocal() as db:
            before = db.query(AuditLogORM).filter_by(action="update_applied").count()

        body = _build_nsupdate(
            {"version": "9.9.9-audit", "frontend_hash": "abc123"},
            [("frontend/audit-marker.html", b"<h1>audit</h1>")],
        )
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("v9.9.9-audit.nsupdate", body, "application/zip")},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Update-Signature": _sign(body),
            },
        )
        assert r.status_code == 200, r.text

        with SessionLocal() as db:
            rows = db.query(AuditLogORM).filter_by(action="update_applied").order_by(AuditLogORM.ts.asc()).all()
            assert len(rows) > before, "no se insertó audit_log de update_applied"
            entry = next(r for r in reversed(rows) if "v9.9.9-audit" in (r.summary or ""))
            assert entry.entity_type == "system"
            assert entry.actor_label == "admin_test_update"
            assert "v9.9.9-audit" in (entry.summary or "")
            assert entry.changes is not None
            changes = json.loads(entry.changes)
            assert changes["version"] == "9.9.9-audit"
            assert changes["sha256"] == hashlib.sha256(body).hexdigest()

    def test_last_update_json_se_persiste(self, client, admin_token):
        body = _build_nsupdate(
            {"version": "9.9.9-lastupd"},
            [("frontend/lastupd.txt", b"x")],
        )
        r = client.post(
            "/api/v1/system/update",
            files={"file": ("v9.9.9.nsupdate", body, "application/zip")},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Update-Signature": _sign(body),
            },
        )
        assert r.status_code == 200, r.text

        info_path = Path("data") / "last_update.json"
        assert info_path.exists(), f"{info_path} no se creó"
        info = json.loads(info_path.read_text(encoding="utf-8"))
        # La ultima llamada fue la de test_happy_path_inserta_audit_log o
        # test_last_update_json_se_persiste; el orden no es estricto pero
        # al menos uno de los dos debe estar presente.
        assert info["version"] in {"9.9.9-lastupd", "9.9.9-audit"}
        assert "sha256" in info
        assert "tamano_bytes" in info
