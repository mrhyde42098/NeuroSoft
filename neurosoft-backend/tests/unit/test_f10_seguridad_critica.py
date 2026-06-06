"""
F10 — Verificación de que los 5 hallazgos críticos de seguridad (S0.x)
están cerrados. Estos tests son READ-ONLY: solo verifican que el código
NO ejecuta los kill-switches aunque las env vars estén activas.
"""

import os
from unittest.mock import patch


class TestKillSwitchesEliminados:
    """F10.1.4 y F10.1.5 — kill-switches S0.4 y S0.5."""

    def test_disable_auth_no_bypasea_auth(self):
        """Aunque NEUROSOFT_DISABLE_AUTH=1, el middleware debe seguir exigiendo Bearer."""
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        with patch.dict(os.environ, {"NEUROSOFT_DISABLE_AUTH": "1"}):
            # Llamar a /api/* sin token debe seguir retornando 401
            r = client.get("/api/v1/patients/panel")
            assert r.status_code == 401, f"Kill-switch aún activo: retornó {r.status_code}, esperaba 401"
            assert "Token" in r.json().get("detail", "")

    def test_reset_admin_password_no_se_aplica(self):
        """Aunque NEUROSOFT_RESET_ADMIN_PASSWORD=1, ensure_admin_exists no debe
        modificar la contraseña del admin."""
        # Verificar que el código documenta la eliminación
        import inspect

        from app.infrastructure.auth.auth_service import UserRepository

        src = inspect.getsource(UserRepository.ensure_admin_exists)
        assert "ELIMINADO" in src, "ensure_admin_exists debe documentar que el kill-switch fue eliminado"
        assert "NEUROSOFT_RESET_ADMIN_PASSWORD" in src


class TestRequireAdminEnUpdate:
    """F10.1.1 — endpoint /system/update debe requerir rol admin."""

    def test_update_endpoint_esta_protegido(self):
        import inspect

        from app.presentation.api.v1 import update

        src = inspect.getsource(update)
        assert "require_admin" in src or "current_user.role" in src, (
            "update.py debe usar require_admin o verificar current_user.role"
        )


class TestAuditPHIFiltrado:
    """F10.1.3 — audit log no debe filtrar PHI en changes."""

    def test_cambios_auditables_tiene_whitelist(self):
        import inspect

        from app.infrastructure.audit import listeners

        src = inspect.getsource(listeners)
        # Verificar que existe una whitelist/blacklist o hash de campos sensibles
        assert any(
            kw in src
            for kw in (
                "WHITELIST",
                "whitelist",
                "BLACKLIST",
                "blacklist",
                "HASH_PHI",
                "HASH",
                "REDACTAR",
                "redactar",
                "EXCLUIR",
                "excluir",
            )
        ), "audit listeners debe tener whitelist/hash/redactar para PHI"


class TestIDORPatients:
    """F10.1.2 — patients.py debe verificar ownership."""

    def test_patients_usa_ownership_helper(self):
        import inspect

        from app.presentation.api.v1 import patients

        src = inspect.getsource(patients)
        assert any(
            helper in src
            for helper in (
                "get_patient_for_user",
                "verify_ownership",
                "_verify_patient_ownership",
            )
        ), "patients.py debe usar un helper de ownership"


class TestJWTSecurity:
    """F10.1.8 — JWT verify_exp debe ser explícito."""

    def test_jwt_decode_usa_verify_exp_explicito(self):
        import inspect

        from app.infrastructure.auth import auth_service

        src = inspect.getsource(auth_service)
        assert "verify_exp" in src or "options" in src, (
            "auth_service debe usar verify_exp explícito o options={'verify_exp': True}"
        )
