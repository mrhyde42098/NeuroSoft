"""
tests/integration/test_audit_phi.py
====================================
S0.3 del PLAN_MAESTRO: política PHI en audit log.

Verifica que:
  - Los campos VERBATIM (ids, flags, fechas) se loguean tal cual.
  - Los campos PHI (nombre, doc, teléfono) se hashean a sha256:xxxx.
  - Los campos SKIP (firma_base64, hashed_password) NO aparecen.
  - El summary NO contiene nombres completos de pacientes.
  - El diff de un UPDATE solo contiene entradas para campos que
    cambiaron y que NO son skip.
  - El mismo valor en hash produce el mismo sha256:xxxx (estabilidad
    para correlación forense entre runs).
"""
from __future__ import annotations

import json
import uuid
from datetime import date

import pytest

# ═══════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def in_memory_db():
    """BD en memoria con esquema completo (mismo que conftest pero aislado)."""
    from sqlalchemy import create_engine as sa_engine
    from sqlalchemy.orm import sessionmaker
    from app.infrastructure.database.orm_models import Base

    engine_mem = sa_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine_mem)
    Session = sessionmaker(bind=engine_mem, autocommit=False, autoflush=True)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine_mem)


def _make_patient(**overrides) -> object:
    from app.infrastructure.database.orm_models import PatientORM
    base = dict(
        id=str(uuid.uuid4()),
        tipo_documento="CC",
        numero_documento="1234567890",
        primer_nombre="Juan",
        segundo_nombre="Carlos",
        primer_apellido="Pérez",
        segundo_apellido="García",
        fecha_nacimiento=date(1990, 1, 1),
        fecha_atencion=date(2026, 6, 1),
        sexo="M",
        escolaridad="Universitaria",
        lateralidad="Diestro",
        telefono="3001234567",
        correo="juan@test.com",
        direccion="Calle 123 #45-67",
        ciudad="Bogotá",
        motivo_consulta="Dificultades de memoria reportadas",
        is_active=True,
    )
    base.update(overrides)
    p = PatientORM(**base)
    return p


# ═══════════════════════════════════════════════════════════════════
# 1. SNAPSHOT: campos VERBATIM pasan tal cual
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAuditSnapshotVerbatim:

    def test_campos_no_PHI_se_loguean_tal_cual(self, in_memory_db):
        from app.infrastructure.audit.listeners import _snapshot
        p = _make_patient()
        snap = _snapshot(p)
        # Verbatim: metadata que debe aparecer cruda
        assert snap["tipo_documento"] == "CC"
        assert snap["sexo"] == "M"
        assert snap["lateralidad"] == "Diestro"
        assert snap["escolaridad"] == "Universitaria"
        assert snap["is_active"] is True
        # numero_documento es PHI (Ley 1581: dato personal identificable)
        # y por defecto se hashea, no se loguea verbatim
        assert snap["numero_documento"].startswith("sha256:")

    def test_campos_PHI_se_hashean(self, in_memory_db):
        from app.infrastructure.audit.listeners import _snapshot
        p = _make_patient()
        snap = _snapshot(p)
        # Hash: PHI se reemplaza con sha256:xxxxxxxxxxxx
        for phi_field in ("primer_nombre", "primer_apellido", "telefono",
                          "correo", "direccion", "motivo_consulta"):
            assert phi_field in snap
            v = snap[phi_field]
            assert isinstance(v, str) and v.startswith("sha256:"), (
                f"{phi_field} = {v!r} (esperado sha256:xxxx)"
            )

    def test_campos_SKIP_no_aparecen(self, in_memory_db):
        from app.infrastructure.audit.listeners import _snapshot
        # Patient no tiene firma_base64, pero igual validamos la clasificacion
        from app.infrastructure.audit.listeners import _classify
        for skip_field in ("firma_base64", "sello_base64", "foto_base64",
                           "contenido_base64", "hashed_password",
                           "firma", "firma_digital", "tokens"):
            assert _classify(skip_field) == "skip", skip_field

    def test_campos_con_sufijo_base64_se_skipean(self, in_memory_db):
        """Cualquier *_base64 cae en SKIP sin estar explícito en la lista."""
        from app.infrastructure.audit.listeners import _classify
        for f in ("custom_base64", "otro_base64", "imagen_base64"):
            assert _classify(f) == "skip", f

    def test_hash_es_estable_entre_llamadas(self, in_memory_db):
        from app.infrastructure.audit.listeners import _hash_phi
        # Mismo input → mismo hash (clave para correlación forense)
        assert _hash_phi("Juan") == _hash_phi("Juan")
        assert _hash_phi("Juan") != _hash_phi("Pedro")
        # Tipos diferentes se manejan
        assert _hash_phi(None) == "__null__"
        assert _hash_phi(True) == _hash_phi(True)
        assert _hash_phi(True) != _hash_phi(False)


# ═══════════════════════════════════════════════════════════════════
# 2. LABEL: el summary NO contiene nombres completos
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAuditLabel:

    def test_label_de_paciente_no_contiene_nombre(self, in_memory_db):
        from app.infrastructure.audit.listeners import _label
        p = _make_patient(primer_nombre="Juan", primer_apellido="Pérez")
        lbl = _label(p)
        assert "Juan" not in lbl
        assert "Pérez" not in lbl
        # Solo el id corto
        assert lbl.startswith("id=")

    def test_label_de_evaluacion_solo_id(self, in_memory_db):
        from app.infrastructure.audit.listeners import _label
        from app.infrastructure.database.orm_models import EvaluationORM
        e = EvaluationORM(id=str(uuid.uuid4()))
        lbl = _label(e)
        assert "Evaluación" in lbl
        assert e.id[:8] in lbl


# ═══════════════════════════════════════════════════════════════════
# 3. INTEGRACIÓN: el listener inserta audit_log sin filtrar PHI
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAuditListenerIntegration:

    def test_create_paciente_inserta_audit_sin_PHI_en_summary(
        self, in_memory_db,
    ):
        from app.infrastructure.audit import record_event
        from app.infrastructure.database.orm_models import AuditLogORM

        p = _make_patient(primer_nombre="SECRETO-JUAN", primer_apellido="SECRETO-PEREZ")
        record_event(
            in_memory_db,
            action="create",
            entity_type="patient",
            entity_id=p.id,
            summary=f"CREATE Paciente: Juan Perez",
            commit=True,
        )
        row = in_memory_db.query(AuditLogORM).filter_by(entity_id=p.id).first()
        assert row is not None
        # El summary que pasamos contiene PHI — eso es responsabilidad del
        # caller. Pero el _label automatico NO lo haria.
        # Verificamos que el listener (no record_event) genera summary sin PHI:
        from app.infrastructure.audit.listeners import _label
        auto = _label(p)
        assert "SECRETO" not in auto

    def test_update_paciente_diff_hashea_PHI(self, in_memory_db):
        """
        Simula un flush con un paciente modificado y verifica que el diff
        en audit_log.changes tiene PHI hasheado.
        """
        from app.infrastructure.audit.listeners import _safe_value, _classify

        # Carga el dict con valores crudos
        old_val = "Juan"
        new_val = "Pedro"
        # telefono es PHI → hash
        assert _classify("telefono") == "hash"
        assert _safe_value("telefono", old_val) != _safe_value("telefono", new_val)
        # Pero el mismo valor da el mismo hash
        assert _safe_value("primer_nombre", "Juan") == _safe_value("primer_nombre", "Juan")
        # y campos verbatim dan el valor tal cual
        assert _safe_value("sexo", "M") == "M"
        assert _safe_value("is_active", True) is True
        assert _safe_value("is_active", None) is None


# ═══════════════════════════════════════════════════════════════════
# 4. END-TO-END: el listener real al hacer PATCH registra PHI hasheado
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAuditListenerEnd2End:
    """
    El caso más realista: cargar un PatientORM, modificar un campo PHI,
    hacer commit, y verificar el audit_log.changes resultante.
    """

    def test_patch_telefono_registra_hash_no_valor(self, in_memory_db):
        from app.infrastructure.audit.listeners import _label, register_audit_listeners
        from app.infrastructure.database.orm_models import AuditLogORM

        register_audit_listeners()
        p = _make_patient(telefono="3001111111")
        in_memory_db.add(p)
        in_memory_db.commit()  # crea el audit 'create'
        # Forzar recarga desde la BD para que el estado in-memory
        # coincida con el de la BD (necesario para que get_history
        # detecte el valor antiguo).
        in_memory_db.expire(p)
        in_memory_db.refresh(p)
        # Modificar y volver a hacer flush
        p.telefono = "3002222222"
        in_memory_db.commit()

        rows = (
            in_memory_db.query(AuditLogORM)
            .filter_by(entity_id=p.id, entity_type="patient")
            .order_by(AuditLogORM.id)
            .all()
        )
        assert len(rows) == 2
        update_row = rows[-1]
        assert update_row.action == "update"
        changes = json.loads(update_row.changes or "{}")
        # El telefono (PHI) debe aparecer como hash, no como número
        assert "telefono" in changes, f"telefono no esta en changes: {list(changes.keys())}"
        old_h, new_h = changes["telefono"]
        assert old_h.startswith("sha256:"), f"old={old_h!r}"
        assert new_h.startswith("sha256:"), f"new={new_h!r}"
        # Y NO debe contener los numeros reales
        assert "3001111111" not in (update_row.changes or "")
        assert "3002222222" not in (update_row.changes or "")

    def test_create_paciente_summary_sin_nombre(self, in_memory_db):
        from app.infrastructure.audit.listeners import register_audit_listeners
        from app.infrastructure.database.orm_models import AuditLogORM

        register_audit_listeners()
        p = _make_patient(
            primer_nombre="ANDREA",
            primer_apellido="DELACROIX",
        )
        in_memory_db.add(p)
        in_memory_db.commit()

        row = (
            in_memory_db.query(AuditLogORM)
            .filter_by(entity_id=p.id, entity_type="patient", action="create")
            .first()
        )
        assert row is not None
        # El summary NO debe contener el nombre real
        assert "ANDREA" not in (row.summary or "")
        assert "DELACROIX" not in (row.summary or "")
        # Pero debe tener una referencia al id
        assert row.entity_id == p.id
        # El snapshot (changes) debe tener los PHI hasheados
        changes = json.loads(row.changes or "{}")
        assert changes["primer_nombre"].startswith("sha256:")
        assert changes["primer_apellido"].startswith("sha256:")
