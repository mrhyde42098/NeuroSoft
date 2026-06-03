"""
tests/integration/test_repositories.py
=========================================
Tests de integración: repositorios, concurrencia (optimistic locking),
agenda, evaluaciones.
"""
from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import pytest

# ═══════════════════════════════════════════════════════════════
# PATIENT REPOSITORY
# ═══════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestPatientRepository:

    def _make_patient(self, doc="12345678"):
        from app.domain.entities.models import Paciente, PacienteId
        return Paciente(
            id=PacienteId.generate(),
            numero_documento=doc,
            tipo_documento="CC",
            primer_nombre="Juan",
            segundo_nombre=None,
            primer_apellido="Pérez",
            segundo_apellido="García",
            fecha_nacimiento=date(1995, 6, 15),
            sexo="H",
            escolaridad="Universitaria",
            lateralidad="Diestro",
            fecha_atencion=date(2026, 3, 20),
        )

    def test_save_and_find_by_id(self, in_memory_db):
        from app.infrastructure.repositories.patient_repo import PatientRepository
        repo = PatientRepository(in_memory_db)
        p = self._make_patient("99999")
        repo.save(p)
        in_memory_db.commit()

        found = repo.find_by_id(str(p.id))
        assert found.numero_documento == "99999"
        assert found.primer_nombre == "Juan"

    def test_find_not_found_raises(self, in_memory_db):
        from app.core.exceptions import PatientNotFoundError
        from app.infrastructure.repositories.patient_repo import PatientRepository
        repo = PatientRepository(in_memory_db)
        with pytest.raises(PatientNotFoundError):
            repo.find_by_id("non-existent-uuid-1234")

    def test_soft_delete(self, in_memory_db):
        from app.core.exceptions import PatientNotFoundError
        from app.infrastructure.repositories.patient_repo import PatientRepository
        repo = PatientRepository(in_memory_db)
        p = self._make_patient("77777")
        repo.save(p)
        in_memory_db.commit()

        repo.soft_delete(str(p.id))
        in_memory_db.commit()

        with pytest.raises(PatientNotFoundError):
            repo.find_by_id(str(p.id))

    def test_search_by_nombre(self, in_memory_db):
        from app.infrastructure.repositories.patient_repo import PatientRepository
        repo = PatientRepository(in_memory_db)
        for doc in ["11111", "22222", "33333"]:
            repo.save(self._make_patient(doc))
        in_memory_db.commit()

        results = repo.search(nombre="Juan")
        assert len(results) == 3

    def test_search_by_documento(self, in_memory_db):
        from app.infrastructure.repositories.patient_repo import PatientRepository
        repo = PatientRepository(in_memory_db)
        repo.save(self._make_patient("ÚNICO123"))
        in_memory_db.commit()

        results = repo.search(documento="ÚNICO123")
        assert len(results) == 1
        assert results[0].numero_documento == "ÚNICO123"

    def test_get_stats(self, in_memory_db):
        from app.infrastructure.repositories.patient_repo import PatientRepository
        repo = PatientRepository(in_memory_db)
        for i, sexo in enumerate(["H", "H", "M"]):
            from app.domain.entities.models import Paciente, PacienteId
            p = Paciente(
                id=PacienteId.generate(), numero_documento=f"STAT{i}",
                tipo_documento="CC", primer_nombre="Test",
                primer_apellido="Prueba", fecha_nacimiento=date(1990, 1, 1),
                sexo=sexo, escolaridad="Universitaria",
                lateralidad="Diestro", fecha_atencion=date.today(),
            )
            repo.save(p)
        in_memory_db.commit()

        stats = repo.get_stats()
        assert stats["masculino"] >= 2
        assert stats["femenino"] >= 1
        assert stats["total_pacientes"] >= 3


# ═══════════════════════════════════════════════════════════════
# EVALUATION REPOSITORY
# ═══════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestEvaluationRepository:

    def _create_patient(self, db, doc="EVA001"):
        from app.infrastructure.database.orm_models import PatientORM
        orm = PatientORM(
            id=str(uuid.uuid4()), numero_documento=doc, tipo_documento="CC",
            primer_nombre="Eva", primer_apellido="Test",
            fecha_nacimiento=date(2010, 1, 1), sexo="H",
            escolaridad="Primaria Incompleta", lateralidad="Diestro",
            fecha_atencion=date(2026, 3, 20), is_active=True,
            created_at=datetime.now(UTC),
        )
        db.add(orm)
        db.flush()
        return orm

    def test_save_and_find(self, in_memory_db):
        from app.infrastructure.repositories.evaluation_repo import (
            EvaluationRepository,
            SaveEvaluationCommand,
        )
        patient = self._create_patient(in_memory_db)
        repo = EvaluationRepository(in_memory_db)

        cmd = SaveEvaluationCommand(
            patient_id=patient.id, protocolo="WISC-IV",
            fecha=date(2026, 3, 20),
            puntajes_brutos={"NiWiscDC": 42},
            resultados=[{"test_id": "NiWiscDC", "puntaje_escalar": 9}],
            poblacion="infantil", edad_display="16a 0m",
            pruebas_realizadas=1, pruebas_sin_dato=0,
            advertencias=[], puntos_debiles=[], puntos_fuertes=[],
        )
        saved = repo.save(cmd)
        in_memory_db.commit()

        found = repo.find_by_id(saved.id)
        assert found.patient_id == patient.id
        assert found.protocolo == "WISC-IV"
        assert found.puntajes_brutos == {"NiWiscDC": 42}
        assert found.pruebas_realizadas == 1
        assert found.is_latest is True

    def test_is_latest_versioning(self, in_memory_db):
        """Guardar una segunda evaluación del mismo protocolo marca la primera como no latest."""
        from app.infrastructure.repositories.evaluation_repo import (
            EvaluationRepository,
            SaveEvaluationCommand,
        )
        patient = self._create_patient(in_memory_db, "EVA002")
        repo = EvaluationRepository(in_memory_db)

        cmd1 = SaveEvaluationCommand(
            patient_id=patient.id, protocolo="WISC-IV",
            fecha=date(2026, 3, 1),
            puntajes_brutos={"NiWiscDC": 30}, resultados=[],
            poblacion="infantil", edad_display="10a",
            pruebas_realizadas=1, pruebas_sin_dato=0,
            advertencias=[], puntos_debiles=[], puntos_fuertes=[],
        )
        ev1 = repo.save(cmd1)
        in_memory_db.commit()

        cmd2 = SaveEvaluationCommand(
            patient_id=patient.id, protocolo="WISC-IV",
            fecha=date(2026, 3, 20),
            puntajes_brutos={"NiWiscDC": 40}, resultados=[],
            poblacion="infantil", edad_display="10a",
            pruebas_realizadas=1, pruebas_sin_dato=0,
            advertencias=[], puntos_debiles=[], puntos_fuertes=[],
        )
        ev2 = repo.save(cmd2)
        in_memory_db.commit()

        # ev2 debe ser latest, ev1 no
        found1 = repo.find_by_id(ev1.id)
        found2 = repo.find_by_id(ev2.id)
        assert found1.is_latest is False
        assert found2.is_latest is True

    def test_find_latest_by_patient(self, in_memory_db):
        from app.infrastructure.repositories.evaluation_repo import (
            EvaluationRepository,
            SaveEvaluationCommand,
        )
        patient = self._create_patient(in_memory_db, "EVA003")
        repo = EvaluationRepository(in_memory_db)

        for proto in ["WISC-IV", "WAIS-III"]:
            cmd = SaveEvaluationCommand(
                patient_id=patient.id, protocolo=proto,
                fecha=date(2026, 3, 20), puntajes_brutos={}, resultados=[],
                poblacion="infantil", edad_display="10a",
                pruebas_realizadas=0, pruebas_sin_dato=0,
                advertencias=[], puntos_debiles=[], puntos_fuertes=[],
            )
            repo.save(cmd)
        in_memory_db.commit()

        latest = repo.find_latest_by_patient(patient.id)
        assert len(latest) == 2
        assert {ev.protocolo for ev in latest} == {"WISC-IV", "WAIS-III"}

    def test_count_by_patient(self, in_memory_db):
        from app.infrastructure.repositories.evaluation_repo import (
            EvaluationRepository,
            SaveEvaluationCommand,
        )
        patient = self._create_patient(in_memory_db, "EVA004")
        repo = EvaluationRepository(in_memory_db)

        for i in range(3):
            cmd = SaveEvaluationCommand(
                patient_id=patient.id, protocolo=f"PROTO-{i}",
                fecha=date(2026, 3, 20), puntajes_brutos={}, resultados=[],
                poblacion="infantil", edad_display="",
                pruebas_realizadas=0, pruebas_sin_dato=0,
                advertencias=[], puntos_debiles=[], puntos_fuertes=[],
            )
            repo.save(cmd)
        in_memory_db.commit()

        assert repo.count_by_patient(patient.id) == 3

    def test_delete(self, in_memory_db):
        from app.infrastructure.repositories.evaluation_repo import (
            EvaluationNotFoundError,
            EvaluationRepository,
            SaveEvaluationCommand,
        )
        patient = self._create_patient(in_memory_db, "EVA005")
        repo = EvaluationRepository(in_memory_db)
        cmd = SaveEvaluationCommand(
            patient_id=patient.id, protocolo="TEST",
            fecha=date(2026, 3, 20), puntajes_brutos={}, resultados=[],
            poblacion="infantil", edad_display="",
            pruebas_realizadas=0, pruebas_sin_dato=0,
            advertencias=[], puntos_debiles=[], puntos_fuertes=[],
        )
        ev = repo.save(cmd)
        in_memory_db.commit()

        repo.delete(ev.id)
        in_memory_db.commit()

        with pytest.raises(EvaluationNotFoundError):
            repo.find_by_id(ev.id)


# ═══════════════════════════════════════════════════════════════
# OPTIMISTIC LOCKING — CONCURRENCIA
# ═══════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestClinicalHistoryConcurrency:
    """
    Simula dos usuarios guardando la HC al mismo tiempo.
    El segundo save debe detectar el conflicto y lanzar error.
    """

    def _create_patient(self, db):
        from app.infrastructure.database.orm_models import PatientORM
        orm = PatientORM(
            id=str(uuid.uuid4()), numero_documento="CONC001",
            tipo_documento="CC", primer_nombre="Conc", primer_apellido="Test",
            fecha_nacimiento=date(2010, 1, 1), sexo="H",
            escolaridad="Primaria Incompleta", lateralidad="Diestro",
            fecha_atencion=date(2026, 3, 20), is_active=True,
            created_at=datetime.now(UTC),
        )
        db.add(orm)
        db.flush()
        return orm

    def test_primer_save_sin_version_ok(self, in_memory_db):
        from app.infrastructure.database.orm_models import ClinicalHistoryORM
        patient = self._create_patient(in_memory_db)

        hc = ClinicalHistoryORM(
            id=str(uuid.uuid4()), patient_id=patient.id,
            numero_documento="CONC001",
            fecha_atencion=date(2026, 3, 20),
            row_version=1,
        )
        in_memory_db.add(hc)
        in_memory_db.commit()

        # Leer versión guardada
        found = in_memory_db.get(ClinicalHistoryORM, hc.id)
        assert found.row_version == 1

    def test_update_incrementa_version(self, in_memory_db):
        from app.infrastructure.database.orm_models import ClinicalHistoryORM
        patient = self._create_patient(in_memory_db)

        hc = ClinicalHistoryORM(
            id=str(uuid.uuid4()), patient_id=patient.id,
            numero_documento="CONC002", fecha_atencion=date(2026, 3, 20),
            row_version=1,
        )
        in_memory_db.add(hc)
        in_memory_db.commit()

        # Simular save válido (versión correcta)
        found = in_memory_db.get(ClinicalHistoryORM, hc.id)
        assert found.row_version == 1
        found.row_version = 2
        found.motivo_consulta = "Evaluación actualizada"
        in_memory_db.commit()

        refreshed = in_memory_db.get(ClinicalHistoryORM, hc.id)
        assert refreshed.row_version == 2

    def test_stale_version_detectada_por_use_case(self, in_memory_db):
        """UpsertClinicalHistoryUseCase rechaza update con versión obsoleta."""
        from app.core.exceptions import ConcurrencyError
        from app.infrastructure.database.orm_models import ClinicalHistoryORM

        patient = self._create_patient(in_memory_db)

        hc = ClinicalHistoryORM(
            id=str(uuid.uuid4()), patient_id=patient.id,
            numero_documento="CONC003", fecha_atencion=date(2026, 3, 20),
            row_version=5,
        )
        in_memory_db.add(hc)
        in_memory_db.commit()

        # Intentar guardar con versión obsoleta (3 en vez de 5)
        from app.application.dtos.clinical_history_dtos import (
            ClinicalHistoryUpsertDTO,
            HCAntecedentesDTO,
            HCDesarrolloDTO,
            HCFamiliarDTO,
            HCObservacionesDTO,
            HCPlanAtencionDTO,
        )
        from app.application.use_cases.clinical_history_use_cases import UpsertClinicalHistoryUseCase
        dto = ClinicalHistoryUpsertDTO(
            patient_id=patient.id,
            fecha_atencion=date(2026, 3, 20),
            row_version=3,  # OBSOLETA — debe fallar
            desarrollo=HCDesarrolloDTO(motivo_consulta="Update con versión obsoleta"),
            antecedentes=HCAntecedentesDTO(),
            familiar=HCFamiliarDTO(),
            plan_atencion=HCPlanAtencionDTO(),
            observaciones=HCObservacionesDTO(),
        )

        with pytest.raises(ConcurrencyError):
            UpsertClinicalHistoryUseCase(in_memory_db).execute(dto)


# ═══════════════════════════════════════════════════════════════
# APPOINTMENTS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestAppointments:

    def _create_patient(self, db, doc="APT001"):
        from app.infrastructure.database.orm_models import PatientORM
        orm = PatientORM(
            id=str(uuid.uuid4()), numero_documento=doc,
            tipo_documento="CC", primer_nombre="Agenda",
            primer_apellido="Test", fecha_nacimiento=date(2010, 1, 1),
            sexo="H", escolaridad="Primaria Incompleta",
            lateralidad="Diestro", fecha_atencion=date(2026, 3, 20),
            is_active=True, created_at=datetime.now(UTC),
        )
        db.add(orm)
        db.flush()
        return orm

    def test_create_appointment(self, in_memory_db):
        from app.infrastructure.database.orm_models import AppointmentORM
        patient = self._create_patient(in_memory_db)

        cita = AppointmentORM(
            id=str(uuid.uuid4()), patient_id=patient.id,
            fecha=date(2026, 4, 10), hora_inicio="09:00", hora_fin="10:00",
            tipo_cita="evaluacion", estado="programada",
            created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
        )
        in_memory_db.add(cita)
        in_memory_db.commit()

        found = in_memory_db.get(AppointmentORM, cita.id)
        assert found.estado == "programada"
        assert found.tipo_cita == "evaluacion"

    def test_update_estado(self, in_memory_db):
        from app.infrastructure.database.orm_models import AppointmentORM
        patient = self._create_patient(in_memory_db, "APT002")

        cita = AppointmentORM(
            id=str(uuid.uuid4()), patient_id=patient.id,
            fecha=date(2026, 4, 10), hora_inicio="09:00",
            tipo_cita="terapia", estado="programada",
            created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
        )
        in_memory_db.add(cita)
        in_memory_db.commit()

        found = in_memory_db.get(AppointmentORM, cita.id)
        found.estado = "atendida"
        in_memory_db.commit()

        updated = in_memory_db.get(AppointmentORM, cita.id)
        assert updated.estado == "atendida"

    def test_query_by_date(self, in_memory_db):
        from app.infrastructure.database.orm_models import AppointmentORM
        patient = self._create_patient(in_memory_db, "APT003")
        target_date = date(2026, 4, 15)

        for i, d in enumerate([target_date, date(2026, 4, 16), date(2026, 4, 17)]):
            cita = AppointmentORM(
                id=str(uuid.uuid4()), patient_id=patient.id,
                fecha=d, hora_inicio=f"0{8+i}:00",
                tipo_cita="evaluacion", estado="programada",
                created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
            )
            in_memory_db.add(cita)
        in_memory_db.commit()

        citas_del_dia = (
            in_memory_db.query(AppointmentORM)
            .filter(AppointmentORM.fecha == target_date)
            .all()
        )
        assert len(citas_del_dia) == 1
