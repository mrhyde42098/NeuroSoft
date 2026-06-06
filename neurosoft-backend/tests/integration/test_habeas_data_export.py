"""
tests/integration/test_habeas_data_export.py
==============================================
Derecho de acceso Habeas Data (Ley 1581/2012, Art. 8).

El paciente puede pedir copia íntegra de TODOS los datos personales que
el sistema tiene sobre él. Esta suite verifica que `ExportPatientDataUseCase`:

  1. Devuelve un dump auto-contenido con schema_version y exported_at.
  2. Incluye paciente, historia clínica + versiones, evaluaciones,
     evoluciones, observaciones, citas, consentimientos, documentos
     y emails.
  3. Respeta el aislamiento entre pacientes — datos de otros pacientes
     NO se filtran.
  4. Lanza PatientNotFoundError para IDs inexistentes.
  5. Parsea correctamente los campos JSON (puntajes, resultados, etc.).
  6. Omite la firma base64 de los consentimientos (datos pesados).
  7. Marca un evento `export` en la auditoría cuando se accede al endpoint.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import pytest

# ─────────────────────────────────────────────────────────────
# Fixtures de datos
# ─────────────────────────────────────────────────────────────


def _new_patient(db, doc="EXP001"):
    from app.infrastructure.database.orm_models import PatientORM

    p = PatientORM(
        id=str(uuid.uuid4()),
        numero_documento=doc,
        tipo_documento="CC",
        primer_nombre="Habeas",
        segundo_nombre="Data",
        primer_apellido="Test",
        fecha_nacimiento=date(2010, 5, 15),
        sexo="H",
        escolaridad="Primaria Incompleta",
        lateralidad="Diestro",
        fecha_atencion=date(2026, 3, 20),
        is_active=True,
        created_at=datetime.now(UTC),
        telefono="3001234567",
        correo="paciente@example.com",
    )
    db.add(p)
    db.flush()
    return p


def _new_evaluation(db, patient_id, protocolo="WISC-IV"):
    from app.infrastructure.database.orm_models import EvaluationORM

    e = EvaluationORM(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        protocolo=protocolo,
        fecha=date(2026, 3, 20),
        puntajes_brutos_json='{"NiWiscDC": 42}',
        resultados_json='[{"test_id":"NiWiscDC","puntaje_escalar":11}]',
        advertencias_json='["Aviso 1"]',
        poblacion="infantil",
        edad_display="15a",
        pruebas_realizadas=1,
        pruebas_sin_dato=0,
        is_latest=True,
        baremo_version="BD-2025",
        baremo_checksum="abc123",
        created_at=datetime.now(UTC),
    )
    db.add(e)
    db.flush()
    return e


def _new_clinical_history(db, patient_id, doc="EXP001"):
    from app.infrastructure.database.orm_models import ClinicalHistoryORM

    hc = ClinicalHistoryORM(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        numero_documento=doc,
        fecha_atencion=date(2026, 3, 20),
        codigo_cie10="F809",
        motivo_consulta="Evaluación clínica",
        created_at=datetime.now(UTC),
    )
    db.add(hc)
    db.flush()
    return hc


# ═══════════════════════════════════════════════════════════════
# 1. ESTRUCTURA DEL EXPORT
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestExportEstructura:
    def test_paciente_inexistente_lanza(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )
        from app.core.exceptions import PatientNotFoundError

        with pytest.raises(PatientNotFoundError):
            ExportPatientDataUseCase(in_memory_db).execute("no-existe")

    def test_export_devuelve_schema_version(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )

        p = _new_patient(in_memory_db)
        in_memory_db.commit()

        out = ExportPatientDataUseCase(in_memory_db).execute(p.id)
        assert out["schema_version"] == "1.0"
        assert "exported_at" in out
        assert out["patient_id"] == p.id
        assert "Ley 1581" in out["legal_basis"]

    def test_export_minimal_paciente_solo(self, in_memory_db):
        """Un paciente sin HC ni evaluaciones devuelve listas vacías, no errores."""
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )

        p = _new_patient(in_memory_db, doc="MIN001")
        in_memory_db.commit()

        out = ExportPatientDataUseCase(in_memory_db).execute(p.id)
        assert out["paciente"]["id"] == p.id
        assert out["paciente"]["numero_documento"] == "MIN001"
        assert out["historia_clinica"] is None
        assert out["evaluaciones"] == []
        assert out["evoluciones_terapia"] == []
        assert out["observaciones"] == []
        assert out["consentimientos"] == []
        assert out["citas"] == []
        assert out["documentos_emitidos"] == []
        assert out["emails_enviados"] == []
        assert out["totales"]["evaluaciones"] == 0


# ═══════════════════════════════════════════════════════════════
# 2. CAMPOS JSON SE PARSEAN
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestExportParsing:
    def test_evaluacion_devuelve_puntajes_como_dict(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )

        p = _new_patient(in_memory_db, doc="PARSE001")
        e = _new_evaluation(in_memory_db, p.id)
        in_memory_db.commit()

        out = ExportPatientDataUseCase(in_memory_db).execute(p.id)
        assert len(out["evaluaciones"]) == 1
        ev = out["evaluaciones"][0]
        assert ev["id"] == e.id
        # puntajes_brutos_json debió expandirse a dict
        assert isinstance(ev["puntajes_brutos"], dict)
        assert ev["puntajes_brutos"]["NiWiscDC"] == 42
        # resultados_json debió expandirse a list
        assert isinstance(ev["resultados"], list)
        assert ev["resultados"][0]["test_id"] == "NiWiscDC"
        # advertencias también
        assert ev["advertencias"] == ["Aviso 1"]
        # los campos crudos *_json deben estar AUSENTES en el dump (limpieza)
        for k in ("puntajes_brutos_json", "resultados_json", "advertencias_json"):
            assert k not in ev, f"Campo crudo '{k}' no debería aparecer"

    def test_dates_serializadas_iso(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )

        p = _new_patient(in_memory_db, doc="DATE001")
        in_memory_db.commit()

        out = ExportPatientDataUseCase(in_memory_db).execute(p.id)
        # Las fechas se serializan en ISO 8601
        assert out["paciente"]["fecha_nacimiento"] == "2010-05-15"
        assert out["paciente"]["fecha_atencion"] == "2026-03-20"


# ═══════════════════════════════════════════════════════════════
# 3. AISLAMIENTO ENTRE PACIENTES
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestExportAislamiento:
    def test_no_filtra_evaluaciones_de_otros(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )

        alice = _new_patient(in_memory_db, doc="ALICE")
        bob = _new_patient(in_memory_db, doc="BOB")
        _new_evaluation(in_memory_db, alice.id, protocolo="WISC-IV")
        _new_evaluation(in_memory_db, bob.id, protocolo="WAIS-IV")
        _new_evaluation(in_memory_db, bob.id, protocolo="WMS-IV")
        in_memory_db.commit()

        export_alice = ExportPatientDataUseCase(in_memory_db).execute(alice.id)
        export_bob = ExportPatientDataUseCase(in_memory_db).execute(bob.id)

        assert len(export_alice["evaluaciones"]) == 1
        assert len(export_bob["evaluaciones"]) == 2
        # Confirmar que cada paciente solo ve sus propios protocolos
        protos_alice = {e["protocolo"] for e in export_alice["evaluaciones"]}
        protos_bob = {e["protocolo"] for e in export_bob["evaluaciones"]}
        assert protos_alice == {"WISC-IV"}
        assert protos_bob == {"WAIS-IV", "WMS-IV"}

    def test_no_filtra_observaciones_ni_citas_ajenas(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )
        from app.infrastructure.database.orm_models import (
            AppointmentORM,
            ObservationORM,
        )

        alice = _new_patient(in_memory_db, doc="A1")
        bob = _new_patient(in_memory_db, doc="B1")

        in_memory_db.add_all(
            [
                ObservationORM(
                    id=str(uuid.uuid4()),
                    patient_id=alice.id,
                    dominio="Atención",
                    texto="Atención preservada",
                    created_at="2026-03-20T10:00:00",
                    updated_at="2026-03-20T10:00:00",
                ),
                ObservationORM(
                    id=str(uuid.uuid4()),
                    patient_id=bob.id,
                    dominio="Memoria",
                    texto="Memoria afectada",
                    created_at="2026-03-20T10:00:00",
                    updated_at="2026-03-20T10:00:00",
                ),
                AppointmentORM(
                    id=str(uuid.uuid4()),
                    patient_id=alice.id,
                    fecha=date(2026, 4, 1),
                    hora_inicio="10:00",
                    tipo_cita="evaluacion",
                ),
            ]
        )
        in_memory_db.commit()

        e_alice = ExportPatientDataUseCase(in_memory_db).execute(alice.id)
        e_bob = ExportPatientDataUseCase(in_memory_db).execute(bob.id)

        assert len(e_alice["observaciones"]) == 1
        assert e_alice["observaciones"][0]["dominio"] == "Atención"
        assert len(e_bob["observaciones"]) == 1
        assert e_bob["observaciones"][0]["dominio"] == "Memoria"
        assert len(e_alice["citas"]) == 1
        assert len(e_bob["citas"]) == 0


# ═══════════════════════════════════════════════════════════════
# 4. PRIVACY — datos pesados se omiten
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestExportPrivacy:
    def test_firma_consentimiento_se_omite(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )
        from app.infrastructure.database.orm_models import ConsentimientoORM

        p = _new_patient(in_memory_db, doc="CONS001")
        in_memory_db.add(
            ConsentimientoORM(
                id=str(uuid.uuid4()),
                patient_id=p.id,
                tipo="habeas_data",
                version_texto="1.0",
                texto_completo="Texto del consentimiento",
                aceptado=True,
                firma_base64="UNA_IMAGEN_BASE64_MUY_LARGA" * 100,
                fecha_firma=datetime.now(UTC),
                created_at=datetime.now(UTC),
            )
        )
        in_memory_db.commit()

        out = ExportPatientDataUseCase(in_memory_db).execute(p.id)
        assert len(out["consentimientos"]) == 1
        cons = out["consentimientos"][0]
        # La firma base64 se reemplaza por una nota
        assert "imagen omitida" in cons["firma_base64"].lower()
        # El resto de campos sigue ahí
        assert cons["tipo"] == "habeas_data"
        assert cons["aceptado"] is True


# ═══════════════════════════════════════════════════════════════
# 5. HISTORIA CLÍNICA + VERSIONES
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestExportHistoriaClinica:
    def test_hc_y_versiones_se_incluyen(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )
        from app.infrastructure.database.orm_models import (
            ClinicalHistoryVersionORM,
        )

        p = _new_patient(in_memory_db, doc="HC001")
        hc = _new_clinical_history(in_memory_db, p.id, doc="HC001")
        in_memory_db.add_all(
            [
                ClinicalHistoryVersionORM(
                    id=str(uuid.uuid4()),
                    hc_id=hc.id,
                    patient_id=p.id,
                    version_num=1,
                    snapshot_json='{"motivo_consulta": "viejo"}',
                    saved_by="user1",
                ),
                ClinicalHistoryVersionORM(
                    id=str(uuid.uuid4()),
                    hc_id=hc.id,
                    patient_id=p.id,
                    version_num=2,
                    snapshot_json='{"motivo_consulta": "nuevo"}',
                    saved_by="user1",
                ),
            ]
        )
        in_memory_db.commit()

        out = ExportPatientDataUseCase(in_memory_db).execute(p.id)
        assert out["historia_clinica"] is not None
        assert out["historia_clinica"]["codigo_cie10"] == "F809"
        # Versiones presentes y ordenadas por version_num ascendente
        versiones = out["historia_clinica_versiones"]
        assert len(versiones) == 2
        assert versiones[0]["version_num"] == 1
        assert versiones[1]["version_num"] == 2
        # snapshot_json crudo se reemplaza por el dict parseado
        assert versiones[0]["snapshot"] == {"motivo_consulta": "viejo"}
        assert "snapshot_json" not in versiones[0]


# ═══════════════════════════════════════════════════════════════
# 6. TOTALES
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestExportTotales:
    def test_totales_coinciden_con_listas(self, in_memory_db):
        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )

        p = _new_patient(in_memory_db, doc="TOT001")
        _new_evaluation(in_memory_db, p.id, protocolo="WISC-IV")
        _new_evaluation(in_memory_db, p.id, protocolo="WAIS-IV")
        _new_clinical_history(in_memory_db, p.id, doc="TOT001")
        in_memory_db.commit()

        out = ExportPatientDataUseCase(in_memory_db).execute(p.id)
        assert out["totales"]["evaluaciones"] == len(out["evaluaciones"]) == 2
        assert out["totales"]["consentimientos"] == 0
        assert out["totales"]["evoluciones_terapia"] == 0


# ═══════════════════════════════════════════════════════════════
# 7. INTEGRACIÓN — endpoint completo (función directa)
# ═══════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestExportEndpoint:
    """
    Prueba la función `export_patient_data` sin TestClient.
    Comprueba que se registra el evento `export` en auditoría.
    """

    def test_endpoint_genera_evento_de_auditoria(self, in_memory_db):
        from unittest.mock import MagicMock

        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )
        from app.infrastructure.database.orm_models import AuditLogORM
        from app.presentation.api.v1.patients import export_patient_data

        p = _new_patient(in_memory_db, doc="AUDIT001")
        _new_evaluation(in_memory_db, p.id)
        in_memory_db.commit()

        # Simular FastAPI: mock request + UC inyectado
        req = MagicMock()
        req.state = MagicMock(user_id="prof-99", user_label="Dra. Test")
        req.client = MagicMock(host="127.0.0.1")
        req.headers = {}

        # §S0.2: user mockeado con los atributos que get_patient_for_user
        # espera (admin, sin profesional_id para acceso total)
        user_mock = MagicMock()
        user_mock.role = "admin"
        user_mock.profesional_id = None
        user_mock.id = "prof-99"
        user_mock.username = "Dra. Test"

        uc = ExportPatientDataUseCase(in_memory_db)
        resp = export_patient_data(
            patient_id=p.id,
            request=req,
            uc=uc,
            db=in_memory_db,
            user=user_mock,
        )
        in_memory_db.commit()

        # JSONResponse con Content-Disposition de descarga
        assert resp.status_code == 200
        cd = resp.headers.get("content-disposition", "")
        assert "attachment" in cd
        assert p.id in cd

        # Auditoría
        logs = (
            in_memory_db.query(AuditLogORM).filter(AuditLogORM.action == "export", AuditLogORM.entity_id == p.id).all()
        )
        assert len(logs) == 1
        assert logs[0].actor_id == "prof-99"
        assert "Habeas Data" in (logs[0].summary or "")

    def test_endpoint_404_si_no_existe(self, in_memory_db):
        from unittest.mock import MagicMock

        from fastapi import HTTPException

        from app.application.use_cases.export_use_cases import (
            ExportPatientDataUseCase,
        )
        from app.presentation.api.v1.patients import export_patient_data

        req = MagicMock()
        req.state = MagicMock(user_id="prof-99", user_label="Dra. Test")
        req.client = MagicMock(host="127.0.0.1")
        req.headers = {}
        user_mock = MagicMock()
        user_mock.role = "admin"
        user_mock.profesional_id = None
        user_mock.id = "prof-99"
        user_mock.username = "Dra. Test"
        uc = ExportPatientDataUseCase(in_memory_db)

        with pytest.raises(HTTPException) as exc_info:
            export_patient_data(
                patient_id="no-existe-uid",
                request=req,
                uc=uc,
                db=in_memory_db,
                user=user_mock,
            )
        assert exc_info.value.status_code == 404
