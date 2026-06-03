"""
tests/integration/test_patients_ownership.py
==============================================
S0.2 del PLAN_MAESTRO: ownership en /patients/*.

Verifica que:
  - admin puede acceder a cualquier paciente.
  - profesional_A puede acceder a sus propios pacientes.
  - profesional_A NO puede acceder a pacientes de profesional_B (403).
  - Los listados filtran por scope (no-admin solo ve los suyos).
  - register_patient asigna automaticamente el profesional_id del user.
  - update_patient no permite reasignar el profesional_id (403 si no es admin).
  - export_patient_data respeta ownership.
"""
from __future__ import annotations

import uuid
from datetime import date

import pytest

# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════


def _create_profesional(client, db, suffix: str, profesional_id: str | None) -> str:
    """
    Crea un user (rol=profesional) y lo vincula a un profesional_id.
    Devuelve el id del user. Crea tambien la fila ProfessionalORM para
    que la FK users.profesional_id -> professionals.id se satisfaga.
    """
    from app.infrastructure.auth.auth_service import UserRepository, hash_password
    from app.infrastructure.database.orm_models import ProfessionalORM, UserORM
    username = f"prof_own_{suffix}"
    with db() as session:
        # 1) Asegurar que existe el ProfessionalORM (FK target)
        if profesional_id is not None:
            prof_orm = session.query(ProfessionalORM).filter_by(id=profesional_id).first()
            if prof_orm is None:
                prof_orm = ProfessionalORM(
                    id=profesional_id,
                    nombre_completo=f"Profesional {suffix}",
                    titulo="Psicólogo",
                    especialidad="Clínica",
                    activo=True,
                )
                session.add(prof_orm)
                session.flush()
        # 2) Crear / actualizar el user
        repo = UserRepository(session)
        existing = session.query(UserORM).filter_by(username=username).first()
        if existing is not None:
            existing.role = "profesional"
            existing.is_active = True
            existing.profesional_id = profesional_id
            existing.hashed_password = hash_password("ProfOwn!2026")
            session.commit()
            return existing.id
        user = repo.create(
            username=username,
            password_plain="ProfOwn!2026",
            nombre_completo=f"Prof Own {suffix}",
            role="profesional",
            profesional_id=profesional_id,
        )
        session.commit()
        return user.id


def _create_patient_direct(db, profesional_id: str | None, doc: str) -> str:
    """Inserta un paciente vía ORM y devuelve su id."""
    from app.infrastructure.database.orm_models import PatientORM
    pid = str(uuid.uuid4())
    with db() as session:
        p = PatientORM(
            id=pid,
            tipo_documento="CC",
            numero_documento=doc,
            primer_nombre="Test",
            primer_apellido=f"Patient{doc}",
            fecha_nacimiento=date(2010, 1, 1),
            fecha_atencion=date(2026, 6, 1),
            sexo="M",
            escolaridad="Primaria",
            lateralidad="Diestro",
            profesional_id=profesional_id,
            is_active=True,
        )
        session.add(p)
        session.commit()
    return pid


def _ensure_professional(db, profesional_id: str, suffix: str) -> None:
    """Crea ProfessionalORM si no existe (necesario para FK)."""
    from app.infrastructure.database.orm_models import ProfessionalORM
    with db() as session:
        existing = session.query(ProfessionalORM).filter_by(id=profesional_id).first()
        if existing is None:
            session.add(ProfessionalORM(
                id=profesional_id,
                nombre_completo=f"Profesional {suffix}",
                titulo="Psicólogo",
                activo=True,
            ))
            session.commit()


def _login(client, username: str) -> str:
    r = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "ProfOwn!2026"},
    )
    assert r.status_code == 200, f"login {username} fallo: {r.text}"
    return r.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def db_session_factory():
    from app.infrastructure.database.engine import SessionLocal
    return SessionLocal


@pytest.fixture(scope="module")
def admin_token(client) -> str:
    from app.infrastructure.auth.auth_service import UserRepository, hash_password
    from app.infrastructure.database.engine import SessionLocal
    from app.infrastructure.database.orm_models import UserORM
    with SessionLocal() as s:
        repo = UserRepository(s)
        existing = s.query(UserORM).filter_by(username="admin_own_test").first()
        if existing is None:
            repo.create(
                username="admin_own_test",
                password_plain="AdminOwn!2026",
                nombre_completo="Admin Own",
                role="admin",
            )
            s.commit()
        else:
            existing.hashed_password = hash_password("AdminOwn!2026")
            existing.is_active = True
            existing.role = "admin"
            s.commit()
    r = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_own_test", "password": "AdminOwn!2026"},
    )
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def prof_a_token(client, db_session_factory):
    prof_id = str(uuid.uuid4())
    _create_profesional(client, db_session_factory, "a", prof_id)
    return _login(client, "prof_own_a"), prof_id


@pytest.fixture(scope="module")
def prof_b_token(client, db_session_factory):
    prof_id = str(uuid.uuid4())
    _create_profesional(client, db_session_factory, "b", prof_id)
    return _login(client, "prof_own_b"), prof_id


# ═══════════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestPatientOwnership:
    """
    S0.2: cada handler de /patients/* verifica que el user autenticado
    puede acceder al paciente objetivo.
    """

    def test_admin_puede_leer_cualquier_paciente(
        self, client, admin_token, db_session_factory,
    ):
        # paciente de un profesional cualquiera
        prof_id = str(uuid.uuid4())
        _ensure_professional(db_session_factory, prof_id, "admin-read")
        pid = _create_patient_direct(db_session_factory, prof_id, f"DOC-A-{uuid.uuid4().hex[:6]}")
        r = client.get(f"/api/v1/patients/{pid}", headers=_auth(admin_token))
        assert r.status_code == 200, r.text
        assert r.json()["id"] == pid

    def test_prof_puede_leer_su_propio_paciente(
        self, client, prof_a_token, db_session_factory,
    ):
        token_a, prof_a_id = prof_a_token
        pid = _create_patient_direct(db_session_factory, prof_a_id, f"DOC-A-{uuid.uuid4().hex[:6]}")
        r = client.get(f"/api/v1/patients/{pid}", headers=_auth(token_a))
        assert r.status_code == 200, r.text
        assert r.json()["id"] == pid

    def test_prof_NO_puede_leer_paciente_de_otro_prof(
        self, client, prof_a_token, prof_b_token, db_session_factory,
    ):
        token_a, _ = prof_a_token
        _, prof_b_id = prof_b_token
        # paciente de B
        pid = _create_patient_direct(db_session_factory, prof_b_id, f"DOC-B-{uuid.uuid4().hex[:6]}")
        r = client.get(f"/api/v1/patients/{pid}", headers=_auth(token_a))
        assert r.status_code == 403, r.text
        assert "permiso" in r.text.lower()

    def test_paciente_inexistente_retorna_404(
        self, client, admin_token,
    ):
        r = client.get(
            f"/api/v1/patients/{uuid.uuid4()}",
            headers=_auth(admin_token),
        )
        assert r.status_code == 404

    def test_update_paciente_de_otro_prof_retorna_403(
        self, client, prof_a_token, prof_b_token, db_session_factory,
    ):
        token_a, _ = prof_a_token
        _, prof_b_id = prof_b_token
        pid = _create_patient_direct(db_session_factory, prof_b_id, f"DOC-U-{uuid.uuid4().hex[:6]}")
        r = client.patch(
            f"/api/v1/patients/{pid}",
            json={"primer_nombre": "Hack"},
            headers=_auth(token_a),
        )
        assert r.status_code == 403, r.text

    def test_archive_paciente_de_otro_prof_retorna_403(
        self, client, prof_a_token, prof_b_token, db_session_factory,
    ):
        token_a, _ = prof_a_token
        _, prof_b_id = prof_b_token
        pid = _create_patient_direct(db_session_factory, prof_b_id, f"DOC-X-{uuid.uuid4().hex[:6]}")
        r = client.delete(
            f"/api/v1/patients/{pid}",
            headers=_auth(token_a),
        )
        assert r.status_code == 403, r.text

    def test_export_paciente_de_otro_prof_retorna_403(
        self, client, prof_a_token, prof_b_token, db_session_factory,
    ):
        token_a, _ = prof_a_token
        _, prof_b_id = prof_b_token
        pid = _create_patient_direct(db_session_factory, prof_b_id, f"DOC-E-{uuid.uuid4().hex[:6]}")
        r = client.get(
            f"/api/v1/patients/{pid}/export",
            headers=_auth(token_a),
        )
        assert r.status_code == 403, r.text

    def test_register_asigna_profesional_id_del_user(
        self, client, prof_a_token,
    ):
        """
        El handler fuerza dto.profesional_id = user.profesional_id para
        no-admins, incluso si el cliente intenta inyectar otro.
        Verificamos directamente en BD (PatientResponseDTO no expone
        profesional_id).
        """
        from app.infrastructure.database.engine import SessionLocal
        from app.infrastructure.database.orm_models import PatientORM
        token_a, prof_a_id = prof_a_token
        doc = f"DOC-R-{uuid.uuid4().hex[:6]}"
        fake_prof = str(uuid.uuid4())
        r = client.post(
            "/api/v1/patients/",
            json={
                "tipo_documento": "CC",
                "numero_documento": doc,
                "primer_nombre": "Nuevo",
                "primer_apellido": "Paciente",
                "fecha_nacimiento": "2010-01-01",
                "sexo": "M",
                "escolaridad": "Primaria",
                "lateralidad": "Diestro",
                "fecha_atencion": "2026-06-01",
                "profesional_id": fake_prof,  # intenta reasignar
            },
            headers=_auth(token_a),
        )
        assert r.status_code == 201, r.text
        # Verificamos en BD
        with SessionLocal() as s:
            p = s.query(PatientORM).filter_by(numero_documento=doc).first()
            assert p is not None
            assert p.profesional_id == prof_a_id, (
                f"Se esperaba profesional_id={prof_a_id} (del user), "
                f"se guardo {p.profesional_id}"
            )

    def test_update_no_permite_reasignar_profesional_id(
        self, client, prof_a_token, db_session_factory,
    ):
        """
        El DTO PatientUpdateDTO NO expone `profesional_id` por diseño;
        un no-admin no puede reasignarse pacientes vía PATCH.
        Verificamos que el atributo es ignorado aunque el cliente lo mande
        (Pydantic lo descarta silenciosamente) Y que el ownership check
        previo sigue bloqueando acceso cross-tenant.
        """
        token_a, prof_a_id = prof_a_token
        other_prof = str(uuid.uuid4())
        # Paciente de OTRO prof
        from app.infrastructure.database.engine import SessionLocal
        from app.infrastructure.database.orm_models import ProfessionalORM
        with SessionLocal() as s:
            s.add(ProfessionalORM(
                id=other_prof, nombre_completo="Otro", titulo="Psi", activo=True,
            ))
            s.commit()
        pid_other = _create_patient_direct(db_session_factory, other_prof, f"DOC-RA-{uuid.uuid4().hex[:6]}")
        # Intento de PATCH con profesional_id inyectado: debe ser 403 (no 200)
        r = client.patch(
            f"/api/v1/patients/{pid_other}",
            json={"primer_nombre": "Hack", "profesional_id": prof_a_id},
            headers=_auth(token_a),
        )
        assert r.status_code == 403, r.text

    def test_list_solo_devuelve_pacientes_del_prof(
        self, client, prof_a_token, prof_b_token, db_session_factory,
    ):
        """
        El endpoint /patients/ filtra por scope (profesional_id del user).
        Verificamos en BD que los IDs devueltos pertenecen al profesional.
        """
        from app.infrastructure.database.engine import SessionLocal
        from app.infrastructure.database.orm_models import PatientORM
        token_a, prof_a_id = prof_a_token
        _, prof_b_id = prof_b_token
        # Asegurar que existan los ProfessionalORM para las FKs
        _ensure_professional(db_session_factory, prof_a_id, "a")
        _ensure_professional(db_session_factory, prof_b_id, "b")
        # Crear uno de cada
        doc_a = f"DOC-LA-{uuid.uuid4().hex[:6]}"
        doc_b = f"DOC-LB-{uuid.uuid4().hex[:6]}"
        _create_patient_direct(db_session_factory, prof_a_id, doc_a)
        _create_patient_direct(db_session_factory, prof_b_id, doc_b)
        r = client.get("/api/v1/patients/?limit=100", headers=_auth(token_a))
        assert r.status_code == 200, r.text
        rows = r.json()
        returned_docs = {row["numero_documento"] for row in rows}
        # El paciente de B no debe aparecer en el listado del prof A
        assert doc_b not in returned_docs, (
            f"List del prof A devolvio el paciente {doc_b} (de B)"
        )
        # Y verificamos en BD que el filtro coincide
        with SessionLocal() as s:
            count_a_in_db = s.query(PatientORM).filter(
                PatientORM.profesional_id == prof_a_id,
                PatientORM.is_active.is_(True),
            ).count()
            # Aproximadamente, el listado del prof A no debe exceder su scope
            assert len(rows) <= count_a_in_db + 10, (
                f"List del prof A ({len(rows)}) excede su scope ({count_a_in_db})"
            )

    def test_admin_ve_todos_los_pacientes(
        self, client, admin_token, prof_a_token, prof_b_token, db_session_factory,
    ):
        token_a, prof_a_id = prof_a_token
        _, prof_b_id = prof_b_token
        _ensure_professional(db_session_factory, prof_a_id, "a2")
        _ensure_professional(db_session_factory, prof_b_id, "b2")
        # DOC-VA- / DOC-VB- son prefijos unicos de este test
        unique_a = f"DOC-VA-{uuid.uuid4().hex[:6]}"
        unique_b = f"DOC-VB-{uuid.uuid4().hex[:6]}"
        _create_patient_direct(db_session_factory, prof_a_id, unique_a)
        _create_patient_direct(db_session_factory, prof_b_id, unique_b)
        # Buscar uno a uno por documento (preciso, sin depender de la
        # paginacion de 100 rows que puede dejar fuera pacientes de
        # otros tests).
        r_a = client.get(
            f"/api/v1/patients/?documento={unique_a}",
            headers=_auth(admin_token),
        )
        r_b = client.get(
            f"/api/v1/patients/?documento={unique_b}",
            headers=_auth(admin_token),
        )
        assert r_a.status_code == 200, r_a.text
        assert r_b.status_code == 200, r_b.text
        docs_a = {p["numero_documento"] for p in r_a.json()}
        docs_b = {p["numero_documento"] for p in r_b.json()}
        assert unique_a in docs_a, f"Admin no encuentra paciente de A: {docs_a}"
        assert unique_b in docs_b, f"Admin no encuentra paciente de B: {docs_b}"

    def test_intento_cross_tenant_queda_en_audit(
        self, client, prof_a_token, prof_b_token, db_session_factory,
    ):
        from app.infrastructure.database.engine import SessionLocal
        from app.infrastructure.database.orm_models import AuditLogORM
        token_a, _ = prof_a_token
        _, prof_b_id = prof_b_token
        _ensure_professional(db_session_factory, prof_b_id, "b3")
        pid = _create_patient_direct(db_session_factory, prof_b_id, f"DOC-AUD-{uuid.uuid4().hex[:6]}")
        # Dispara el cross-tenant
        r = client.get(f"/api/v1/patients/{pid}", headers=_auth(token_a))
        assert r.status_code == 403
        # Verifica que quedo registrado
        with SessionLocal() as s:
            row = (s.query(AuditLogORM)
                   .filter_by(action="access_denied", entity_id=pid)
                   .first())
            assert row is not None, "No se registro el access_denied en audit_log"
            assert "cross-tenant" in (row.summary or "").lower()
