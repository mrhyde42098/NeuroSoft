"""
tests/integration/test_soft_delete.py
======================================
Cumplimiento de la Resolución 1995 de 1999 (Colombia): la historia
clínica y los datos asociados NO se pueden borrar físicamente.

Estos tests verifican que `soft_delete` / `archive`:
  - Marcan el paciente como inactivo pero NO eliminan evaluaciones, HC
    ni evolución terapia.
  - Pueblan `archived_at`, `archived_by`, `archived_reason` para trazabilidad.
  - Hacen que `find_by_id` devuelva PatientNotFoundError (el paciente
    no aparece en el flujo clínico pero los datos persisten en la BD).

También valida el soft-delete de sesiones de evolución terapéutica:
  - `archived_at` se puebla, la sesión desaparece del listado por paciente,
    pero la fila sigue en la BD para la auditoría.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import pytest


def _make_patient_orm(db, doc="SD001"):
    from app.infrastructure.database.orm_models import PatientORM

    orm = PatientORM(
        id=str(uuid.uuid4()),
        numero_documento=doc,
        tipo_documento="CC",
        primer_nombre="SoftDelete",
        primer_apellido="Test",
        fecha_nacimiento=date(2010, 1, 1),
        sexo="H",
        escolaridad="Primaria Incompleta",
        lateralidad="Diestro",
        fecha_atencion=date(2026, 3, 20),
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db.add(orm)
    db.flush()
    return orm


def _make_hc(db, patient_id):
    from app.infrastructure.database.orm_models import ClinicalHistoryORM

    hc = ClinicalHistoryORM(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        numero_documento="SD001",
        fecha_atencion=date(2026, 3, 20),
        codigo_cie10="F809",
    )
    db.add(hc)
    db.flush()
    return hc


def _make_evaluation(db, patient_id):
    from app.infrastructure.database.orm_models import EvaluationORM

    ev = EvaluationORM(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        protocolo="WISC-IV",
        fecha=date(2026, 3, 20),
        puntajes_brutos_json='{"TEST_A": 10}',
        resultados_json="[]",
        is_latest=True,
        created_at=datetime.now(UTC),
    )
    db.add(ev)
    db.flush()
    return ev


def _make_evolucion(db, patient_id, numero="1"):
    from app.infrastructure.database.orm_models import EvolTerapiaORM

    ev = EvolTerapiaORM(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        numero_documento="SD001",
        fecha_sesion=date(2026, 3, 20),
        numero_sesion=numero,
        objetivos="Objetivo test",
        actividades="Actividad test",
        plan_trabajo="Plan test",
    )
    db.add(ev)
    db.flush()
    return ev


# ═══════════════════════════════════════════════════════════════
# SOFT-DELETE DE PACIENTE (Res. 1995)
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestSoftDeletePaciente:
    def test_archive_no_borra_evaluaciones(self, in_memory_db):
        """Res. 1995: al archivar un paciente, sus evaluaciones se preservan."""
        from app.infrastructure.database.orm_models import EvaluationORM
        from app.infrastructure.repositories.patient_repo import PatientRepository

        p = _make_patient_orm(in_memory_db)
        _make_evaluation(in_memory_db, p.id)
        in_memory_db.commit()

        assert in_memory_db.query(EvaluationORM).filter_by(patient_id=p.id).count() == 1

        repo = PatientRepository(in_memory_db)
        assert repo.archive(p.id, actor_id="tester", reason="fin de tratamiento") is True
        in_memory_db.commit()

        # Las evaluaciones SIGUEN EXISTIENDO — no se cascadeó el delete.
        assert in_memory_db.query(EvaluationORM).filter_by(patient_id=p.id).count() == 1

    def test_archive_no_borra_historia_clinica(self, in_memory_db):
        from app.infrastructure.database.orm_models import ClinicalHistoryORM
        from app.infrastructure.repositories.patient_repo import PatientRepository

        p = _make_patient_orm(in_memory_db, doc="SD002")
        _make_hc(in_memory_db, p.id)
        in_memory_db.commit()

        PatientRepository(in_memory_db).archive(p.id, reason="alta")
        in_memory_db.commit()

        # HC intacta — consulta directa al ORM (bypassa filtros de paciente activo).
        hc = in_memory_db.query(ClinicalHistoryORM).filter_by(patient_id=p.id).first()
        assert hc is not None

    def test_archive_no_borra_evolucion_terapeutica(self, in_memory_db):
        from app.infrastructure.database.orm_models import EvolTerapiaORM
        from app.infrastructure.repositories.patient_repo import PatientRepository

        p = _make_patient_orm(in_memory_db, doc="SD003")
        _make_evolucion(in_memory_db, p.id, numero="1")
        _make_evolucion(in_memory_db, p.id, numero="2")
        in_memory_db.commit()

        PatientRepository(in_memory_db).archive(p.id, reason="cambio de profesional")
        in_memory_db.commit()

        # Las dos sesiones persisten físicamente.
        assert in_memory_db.query(EvolTerapiaORM).filter_by(patient_id=p.id).count() == 2

    def test_archive_puebla_campos_auditoria(self, in_memory_db):
        """archived_at / archived_by / archived_reason deben quedar registrados."""
        from app.infrastructure.database.orm_models import PatientORM
        from app.infrastructure.repositories.patient_repo import PatientRepository

        p = _make_patient_orm(in_memory_db, doc="SD004")
        in_memory_db.commit()

        repo = PatientRepository(in_memory_db)
        repo.archive(p.id, actor_id="prof-uuid-42", reason="solicitud del paciente (art. 8 Ley 1581)")
        in_memory_db.commit()

        orm = in_memory_db.query(PatientORM).filter_by(id=p.id).first()
        assert orm is not None
        assert orm.is_active is False
        assert orm.archived_at is not None
        assert orm.archived_by == "prof-uuid-42"
        assert "Ley 1581" in (orm.archived_reason or "")

    def test_paciente_archivado_no_aparece_en_find_by_id(self, in_memory_db):
        from app.core.exceptions import PatientNotFoundError
        from app.infrastructure.repositories.patient_repo import PatientRepository

        p = _make_patient_orm(in_memory_db, doc="SD005")
        in_memory_db.commit()

        repo = PatientRepository(in_memory_db)
        repo.archive(p.id, reason="test")
        in_memory_db.commit()

        with pytest.raises(PatientNotFoundError):
            repo.find_by_id(p.id)


# ═══════════════════════════════════════════════════════════════
# SOFT-DELETE DE SESIÓN DE EVOLUCIÓN
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestSoftDeleteEvolucion:
    def test_sesion_archivada_persiste_en_bd(self, in_memory_db):
        """Al archivar una sesión, la fila NO se borra de la BD."""
        from app.infrastructure.database.orm_models import EvolTerapiaORM

        p = _make_patient_orm(in_memory_db, doc="SDE001")
        s = _make_evolucion(in_memory_db, p.id)
        in_memory_db.commit()

        # Simular lo que hace el endpoint delete_evolucion
        s.archived_at = datetime.utcnow()
        s.archived_by = "prof-xyz"
        s.archived_reason = "duplicada por error"
        in_memory_db.commit()

        total = in_memory_db.query(EvolTerapiaORM).filter_by(patient_id=p.id).count()
        assert total == 1, "La sesión archivada debe seguir en la BD para auditoría."

    def test_sesion_archivada_no_aparece_en_listing(self, in_memory_db):
        """`GetEvolTerapiaUseCase.by_patient` filtra las archivadas."""
        from app.application.use_cases.clinical_history_use_cases import GetEvolTerapiaUseCase

        p = _make_patient_orm(in_memory_db, doc="SDE002")
        s1 = _make_evolucion(in_memory_db, p.id, numero="1")
        s2 = _make_evolucion(in_memory_db, p.id, numero="2")
        in_memory_db.commit()

        # Archivar la primera
        s1.archived_at = datetime.utcnow()
        s1.archived_by = "prof"
        s1.archived_reason = "test"
        in_memory_db.commit()

        resultados = GetEvolTerapiaUseCase(in_memory_db).by_patient(p.id)
        ids = [r.id for r in resultados]
        assert s1.id not in ids
        assert s2.id in ids
        assert len(resultados) == 1
