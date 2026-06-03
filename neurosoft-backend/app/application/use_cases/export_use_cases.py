"""
app/application/use_cases/export_use_cases.py
================================================
Casos de uso de **exportación de datos personales** — Habeas Data.

Ley 1581 de 2012 (Régimen General de Protección de Datos Personales,
Colombia) y su decreto reglamentario 1377/2013 reconocen al titular
del dato (paciente) los siguientes derechos:

  • Conocer, actualizar y rectificar sus datos personales (Art. 8 lit. a).
  • **Solicitar prueba de la autorización otorgada al responsable** (lit. b).
  • Ser informado sobre el uso que se ha dado a sus datos (lit. c).

Este módulo concentra la generación del paquete completo de datos
asociados al paciente — historia clínica, evaluaciones, evoluciones,
observaciones, citas, consentimientos, documentos emitidos y bitácora
de envío de correos. El paquete se entrega como un único JSON
auto-contenido para que el paciente (o su apoderado) pueda
auditar absolutamente todo lo que el sistema sabe de él.

Lo que NO se incluye:
  - Hashes de contraseñas (no son datos del paciente).
  - Auditoría que afecte a terceros (otros pacientes).
  - Datos clínicos de otros pacientes que pudieran aparecer
    transversalmente en el sistema.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


def _row_to_dict(orm) -> dict[str, Any]:
    """
    Serializa un ORM SQLAlchemy a dict, convirtiendo tipos no-JSON.
    Sólo lee columnas mapeadas — no toca relaciones (las cargamos a mano
    para tener control fino del scope).
    """
    from sqlalchemy import inspect as _inspect
    out: dict[str, Any] = {}
    insp = _inspect(orm)
    for col in insp.mapper.column_attrs:
        val = getattr(orm, col.key, None)
        if val is None:
            out[col.key] = None
            continue
        # Datetimes / dates → ISO 8601
        if hasattr(val, "isoformat"):
            out[col.key] = val.isoformat()
        elif isinstance(val, (str, int, float, bool)):
            out[col.key] = val
        else:
            out[col.key] = str(val)
    return out


def _parse_json_field(raw: str | None) -> Any:
    """Convierte un campo JSON crudo en su estructura. None si no es JSON."""
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return raw  # devolver como string si no parsea


class ExportPatientDataUseCase:
    """
    Genera un dump completo de los datos de un paciente, listo para
    entregar al titular en cumplimiento del derecho de acceso (Ley 1581).

    Estrategia: una sola sesión, varias queries explícitas. NO usamos las
    relaciones SQLAlchemy lazy-loaded para evitar que el `to_dict` arrastre
    objetos huérfanos o N+1.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(self, session):
        self._db = session

    def execute(self, patient_id: str) -> dict[str, Any]:
        from app.core.exceptions import PatientNotFoundError
        from app.infrastructure.database.orm_models import (
            AppointmentORM,
            ClinicalHistoryORM,
            ClinicalHistoryVersionORM,
            ConsentimientoORM,
            DocumentoEmitidoORM,
            EmailLogORM,
            EvaluationORM,
            EvolTerapiaORM,
            ObservationORM,
            PatientORM,
            ProfessionalORM,
        )

        patient = self._db.get(PatientORM, patient_id)
        if patient is None:
            raise PatientNotFoundError(patient_id)

        # ── Datos básicos del paciente
        paciente_dict = _row_to_dict(patient)

        # ── Profesional asignado (sólo nombre, no datos sensibles)
        profesional_info: dict[str, Any] | None = None
        if patient.profesional_id:
            pro = self._db.get(ProfessionalORM, patient.profesional_id)
            if pro is not None:
                profesional_info = {
                    "id": pro.id,
                    "nombre_completo": pro.nombre_completo,
                    "titulo": pro.titulo,
                    "especialidad": pro.especialidad,
                    "registro_profesional": pro.registro_profesional,
                }

        # ── Historia clínica + versiones
        hc_orm = (
            self._db.query(ClinicalHistoryORM)
            .filter_by(patient_id=patient_id)
            .first()
        )
        clinical_history = _row_to_dict(hc_orm) if hc_orm else None
        hc_versions: list[dict[str, Any]] = []
        if hc_orm is not None:
            for v in (
                self._db.query(ClinicalHistoryVersionORM)
                .filter_by(hc_id=hc_orm.id)
                .order_by(ClinicalHistoryVersionORM.version_num.asc())
                .all()
            ):
                row = _row_to_dict(v)
                # snapshot_json es un blob JSON: parsear para que el JSON
                # final no contenga strings con JSON anidado.
                row["snapshot"] = _parse_json_field(v.snapshot_json)
                row.pop("snapshot_json", None)
                hc_versions.append(row)

        # ── Evaluaciones
        evaluaciones: list[dict[str, Any]] = []
        for ev in (
            self._db.query(EvaluationORM)
            .filter_by(patient_id=patient_id)
            .order_by(EvaluationORM.fecha.desc())
            .all()
        ):
            row = _row_to_dict(ev)
            row["puntajes_brutos"] = _parse_json_field(ev.puntajes_brutos_json)
            row["resultados"] = _parse_json_field(ev.resultados_json)
            row["advertencias"] = _parse_json_field(ev.advertencias_json)
            row["puntos_debiles"] = _parse_json_field(ev.puntos_debiles_json)
            row["puntos_fuertes"] = _parse_json_field(ev.puntos_fuertes_json)
            for k in (
                "puntajes_brutos_json", "resultados_json",
                "advertencias_json", "puntos_debiles_json", "puntos_fuertes_json",
            ):
                row.pop(k, None)
            evaluaciones.append(row)

        # ── Sesiones de terapia
        evoluciones = [
            _row_to_dict(e)
            for e in (
                self._db.query(EvolTerapiaORM)
                .filter_by(patient_id=patient_id)
                .order_by(EvolTerapiaORM.fecha_sesion.asc())
                .all()
            )
        ]

        # ── Observaciones por dominio
        observaciones = [
            _row_to_dict(o)
            for o in (
                self._db.query(ObservationORM)
                .filter_by(patient_id=patient_id)
                .order_by(ObservationORM.created_at.asc())
                .all()
            )
        ]

        # ── Consentimientos firmados (Habeas Data + clínicos)
        consentimientos = []
        for c in (
            self._db.query(ConsentimientoORM)
            .filter_by(patient_id=patient_id)
            .order_by(ConsentimientoORM.fecha_firma.asc())
            .all()
        ):
            row = _row_to_dict(c)
            # Eliminamos la imagen base64 de la firma — pesa demasiado
            # para un dump operativo. El paciente puede pedirla aparte.
            if row.get("firma_base64"):
                row["firma_base64"] = "[imagen omitida — solicítela aparte]"
            consentimientos.append(row)

        # ── Citas
        citas = [
            _row_to_dict(a)
            for a in (
                self._db.query(AppointmentORM)
                .filter_by(patient_id=patient_id)
                .order_by(AppointmentORM.fecha.asc())
                .all()
            )
        ]

        # ── Documentos emitidos (informes, certificados, etc.)
        documentos = []
        for d in (
            self._db.query(DocumentoEmitidoORM)
            .filter_by(patient_id=patient_id)
            .order_by(DocumentoEmitidoORM.fecha_emision.desc())
            .all()
        ):
            row = _row_to_dict(d)
            row["contenido"] = _parse_json_field(d.contenido_json)
            row.pop("contenido_json", None)
            documentos.append(row)

        # ── Correos enviados al paciente
        emails_enviados = []
        for em in (
            self._db.query(EmailLogORM)
            .filter_by(patient_id=patient_id)
            .order_by(EmailLogORM.ts.desc())
            .all()
        ):
            row = _row_to_dict(em)
            row["adjuntos"] = _parse_json_field(em.attachments_json)
            row.pop("attachments_json", None)
            emails_enviados.append(row)

        # ── Empaquetado final
        return {
            "schema_version": self.SCHEMA_VERSION,
            "exported_at": datetime.now(UTC).isoformat(),
            "legal_basis": (
                "Ley 1581 de 2012, Art. 8 (derechos del titular: conocer, "
                "actualizar y rectificar sus datos personales). "
                "Decreto 1377 de 2013."
            ),
            "patient_id": patient_id,
            "paciente": paciente_dict,
            "profesional_asignado": profesional_info,
            "historia_clinica": clinical_history,
            "historia_clinica_versiones": hc_versions,
            "evaluaciones": evaluaciones,
            "evoluciones_terapia": evoluciones,
            "observaciones": observaciones,
            "consentimientos": consentimientos,
            "citas": citas,
            "documentos_emitidos": documentos,
            "emails_enviados": emails_enviados,
            "totales": {
                "evaluaciones": len(evaluaciones),
                "evoluciones_terapia": len(evoluciones),
                "observaciones": len(observaciones),
                "consentimientos": len(consentimientos),
                "citas": len(citas),
                "documentos_emitidos": len(documentos),
                "emails_enviados": len(emails_enviados),
                "hc_versiones": len(hc_versions),
            },
        }
