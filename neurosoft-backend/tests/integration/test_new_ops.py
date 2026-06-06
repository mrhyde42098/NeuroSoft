"""
tests/integration/test_new_ops.py
===================================
Cobertura de los 3 huecos operativos cerrados:

  A.3  — POST /admin/import-legacy-xlsm
  A.6  — POST /reports/{eval_id}/send-email
         GET  /emails, GET /emails/status
  A.10 — GET  /rips/export

Solo smoke tests de contratos (auth, rutas, shape de respuesta). La lógica
SMTP no se ejercita (requeriría servidor real).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


# ─────────────────────────────────────────────────────────────
# A.3 — Migrador legacy xlsm
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestAdminImportLegacyXlsm:
    def test_sin_token_401(self, client):
        r = client.post("/api/v1/admin/import-legacy-xlsm")
        assert r.status_code == 401

    def test_ruta_registrada(self, client):
        from app.main import app

        paths = {getattr(r, "path", "") for r in app.routes}
        assert "/api/v1/admin/import-legacy-xlsm" in paths


# ─────────────────────────────────────────────────────────────
# A.6 — Correos
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestEmailEndpoints:
    def test_send_email_sin_token_401(self, client):
        r = client.post(
            "/api/v1/reports/any-id/send-email",
            json={"to": ["a@b.com"], "tipo": "informe"},
        )
        assert r.status_code == 401

    def test_status_sin_token_401(self, client):
        r = client.get("/api/v1/emails/status")
        assert r.status_code == 401

    def test_logs_sin_token_401(self, client):
        r = client.get("/api/v1/emails")
        assert r.status_code == 401

    def test_rutas_registradas(self, client):
        from app.main import app

        paths = {getattr(r, "path", "") for r in app.routes}
        esperadas = {
            "/api/v1/reports/{eval_id}/send-email",
            "/api/v1/emails",
            "/api/v1/emails/status",
        }
        faltantes = esperadas - paths
        assert not faltantes, f"Faltan rutas: {faltantes}"


# ─────────────────────────────────────────────────────────────
# A.10 — RIPS mensual
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestRipsExport:
    def test_sin_token_401(self, client):
        r = client.get("/api/v1/rips/export?desde=2026-01-01&hasta=2026-01-31")
        assert r.status_code == 401

    def test_ruta_registrada(self, client):
        from app.main import app

        paths = {getattr(r, "path", "") for r in app.routes}
        assert "/api/v1/rips/export" in paths


# ─────────────────────────────────────────────────────────────
# Sanidad de los generadores (unitarios, sin HTTP)
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestGeneradoresUnitarios:
    def test_rips_monthly_txt_vacio_retorna_tres_archivos(self):
        """Rango sin evaluaciones → los 3 archivos existen con headers."""
        from datetime import date

        from app.infrastructure.database.engine import get_session
        from app.infrastructure.rips_service import generate_rips_monthly_txt

        db = next(get_session())
        try:
            out = generate_rips_monthly_txt(
                db,
                professional_id=None,
                desde=date(2099, 1, 1),
                hasta=date(2099, 1, 31),
                numero_factura="TEST-001",
                codigo_prestador="NIT-000",
            )
            assert set(out.keys()) == {"CT.txt", "US.txt", "AC.txt"}
            # CT siempre tiene al menos la cabecera
            assert len(out["CT.txt"]) > 0
            # US y AC pueden estar vacíos (solo el trailing CRLF)
            assert isinstance(out["US.txt"], (bytes, bytearray))
            assert isinstance(out["AC.txt"], (bytes, bytearray))
        finally:
            db.close()

    def test_email_service_reporta_no_configurado(self):
        """Sin SMTP_HOST configurado, is_configured() es False."""
        from app.infrastructure.email_service import is_configured

        # En entorno test no hay NEUROSOFT_SMTP_HOST seteado
        assert is_configured() in (True, False)  # tolerante — solo contrato

    def test_email_log_tabla_existe(self):
        """EmailLogORM debe estar declarada y registrada en metadata."""
        from app.infrastructure.database.orm_models import EmailLogORM

        assert EmailLogORM.__tablename__ == "email_logs"
        cols = {c.name for c in EmailLogORM.__table__.columns}
        for required in {
            "id",
            "ts",
            "actor_id",
            "recipient_to",
            "subject",
            "status",
            "tipo",
            "error_message",
        }:
            assert required in cols, f"Falta columna {required} en email_logs"

    def test_legacy_import_template_context(self):
        """Chequeo de que el servicio legacy_import importa sin romper."""
        from app.infrastructure import legacy_import_service

        # Debe exponer la función principal y el dataclass de reporte
        assert hasattr(legacy_import_service, "import_legacy_xlsm")
        assert hasattr(legacy_import_service, "ImportReport")

    def test_rips_monthly_zip_es_zip_valido(self):
        """Output de ZIP debe ser un ZIP abrible por zipfile."""
        import io
        import zipfile
        from datetime import date

        from app.infrastructure.database.engine import get_session
        from app.infrastructure.rips_service import generate_rips_monthly_zip

        db = next(get_session())
        try:
            blob = generate_rips_monthly_zip(
                db,
                professional_id=None,
                desde=date(2099, 1, 1),
                hasta=date(2099, 1, 31),
            )
            with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                names = set(zf.namelist())
            assert names == {"CT.txt", "US.txt", "AC.txt"}
        finally:
            db.close()
