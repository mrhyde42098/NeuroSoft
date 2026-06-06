"""
tests/integration/test_auth_service.py
========================================
Tests de integración para el servicio de autenticación.
"""

from __future__ import annotations

import pytest


@pytest.mark.integration
class TestAuthService:
    def test_create_user_and_authenticate(self, in_memory_db):
        from app.infrastructure.auth.auth_service import UserRepository

        repo = UserRepository(in_memory_db)

        user = repo.create(
            username="testuser",
            password_plain="miPassword123",
            nombre_completo="Test User",
            role="profesional",
        )
        in_memory_db.commit()

        assert user.username == "testuser"
        assert user.is_active is True

        # Authenticate con password correcta
        auth_ok = repo.authenticate("testuser", "miPassword123")
        assert auth_ok is not None
        assert auth_ok.username == "testuser"

    def test_authenticate_wrong_password(self, in_memory_db):
        from app.infrastructure.auth.auth_service import UserRepository

        repo = UserRepository(in_memory_db)

        repo.create(
            username="wrongpw",
            password_plain="correcta1234",
            nombre_completo="Wrong PW",
        )
        in_memory_db.commit()

        result = repo.authenticate("wrongpw", "incorrecta")
        assert result is None

    def test_authenticate_nonexistent_user(self, in_memory_db):
        from app.infrastructure.auth.auth_service import UserRepository

        repo = UserRepository(in_memory_db)
        result = repo.authenticate("noexisto", "pass1234")
        assert result is None

    def test_hash_is_bcrypt(self, in_memory_db):
        from app.infrastructure.auth.auth_service import UserRepository

        repo = UserRepository(in_memory_db)
        user = repo.create(
            username="hashtest",
            password_plain="segura123",
            nombre_completo="Hash Test",
        )
        in_memory_db.commit()

        # bcrypt hashes start with $2b$ or $2a$
        assert user.hashed_password.startswith("$2"), f"Hash no parece bcrypt: {user.hashed_password[:10]}"

    def test_duplicate_user_raises(self, in_memory_db):
        from app.infrastructure.auth.auth_service import UserRepository

        repo = UserRepository(in_memory_db)

        repo.create(username="dupl", password_plain="pass1234", nombre_completo="Dup")
        in_memory_db.commit()

        with pytest.raises(ValueError, match="ya existe"):
            repo.create(username="dupl", password_plain="pass5678", nombre_completo="Dup2")

    def test_update_password(self, in_memory_db):
        from app.infrastructure.auth.auth_service import UserRepository

        repo = UserRepository(in_memory_db)

        user = repo.create(
            username="updpw",
            password_plain="original123",
            nombre_completo="Update PW",
        )
        in_memory_db.commit()

        repo.update_password(user.id, "nuevaPass456")
        in_memory_db.commit()

        # Old password fails
        assert repo.authenticate("updpw", "original123") is None
        # New password works
        assert repo.authenticate("updpw", "nuevaPass456") is not None

    def test_deactivate_user(self, in_memory_db):
        from app.infrastructure.auth.auth_service import UserRepository

        repo = UserRepository(in_memory_db)

        user = repo.create(
            username="deact",
            password_plain="pass1234",
            nombre_completo="Deactivate Me",
        )
        in_memory_db.commit()

        repo.deactivate(user.id)
        in_memory_db.commit()

        # Deactivated user can't authenticate
        assert repo.authenticate("deact", "pass1234") is None
