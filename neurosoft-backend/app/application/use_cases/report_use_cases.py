"""Orquestación de generación de informes (PDF, DOCX, XLSX)."""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.exceptions import EvaluationNotFoundError
from app.infrastructure.database.orm_models import (
    ClinicalHistoryORM,
    ObservationORM,
    PatientORM,
    ProfessionalORM,
)
from app.infrastructure.repositories.evaluation_repo import EvaluationRepository

logger = logging.getLogger(__name__)

ReportTemplate = Literal[
    "estandar",
    "pro",
    "pediatrico",
    "medicolegal",
    "junta_medica",
    "inconcluso",
    "therapy_closure",
    "paciente",
]


def get_or_default_institucion(db: Session):
    try:
        from app.infrastructure.database.orm_models import ConfigInstitucionORM

        inst = db.query(ConfigInstitucionORM).first()
        if inst:
            return inst
    except (ImportError, AttributeError) as exc:
        logger.debug("ConfigInstitucionORM no disponible: %s", exc)

    class _DefaultInstitucion:
        nombre = "Consultorio Neuropsicológico"
        nit = ""
        direccion = ""
        telefono = ""
        email = ""
        logo_base64 = None

    return _DefaultInstitucion()


class GenerateReportUseCase:
    def __init__(self, session: Session, eval_repo: EvaluationRepository):
        self._db = session
        self._eval_repo = eval_repo

    def _find_evaluation(self, eval_id: str):
        try:
            return self._eval_repo.find_by_id(eval_id)
        except EvaluationNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluación '{eval_id}' no encontrada.",
            ) from None

    def build_report_data(
        self,
        eval_id: str,
        *,
        therapy_plan_id: str | None = None,
        include_therapy: bool = False,
    ):
        from app.infrastructure.report_service import build_report_data_from_db

        ev = self._find_evaluation(eval_id)
        patient_orm = self._db.get(PatientORM, ev.patient_id)
        if patient_orm is None:
            raise HTTPException(status_code=404, detail="Paciente no encontrado.")

        hc = (
            self._db.query(ClinicalHistoryORM)
            .filter(ClinicalHistoryORM.patient_id == ev.patient_id)
            .order_by(ClinicalHistoryORM.fecha_atencion.desc())
            .first()
        )

        obs_list = self._db.query(ObservationORM).filter_by(patient_id=ev.patient_id, evaluation_id=eval_id).all()
        observations_dict = {o.dominio: o.texto for o in obs_list} if obs_list else {}

        institucion = get_or_default_institucion(self._db)

        profesional = None
        if patient_orm.profesional_id:
            profesional = self._db.get(ProfessionalORM, patient_orm.profesional_id)

        return (
            build_report_data_from_db(
                patient=patient_orm,
                clinical_history=hc,
                evaluation_record=ev,
                institucion=institucion,
                profesional=profesional,
                observations=observations_dict,
                db=self._db,
                therapy_plan_id=therapy_plan_id,
                include_therapy=include_therapy,
            ),
            ev,
            patient_orm,
        )

    def execute_pdf(
        self,
        eval_id: str,
        *,
        template: ReportTemplate = "pro",
        therapy_plan_id: str | None = None,
    ) -> tuple[bytes, str]:
        from app.infrastructure.report_service import generate_report_pdf

        report_data, _ev, patient_orm = self.build_report_data(
            eval_id,
            therapy_plan_id=therapy_plan_id,
            include_therapy=(template == "therapy_closure"),
        )

        try:
            pdf_bytes = generate_report_pdf(report_data, template=template)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        except Exception as e:
            logger.exception("Error generando PDF para eval_id=%s template=%s", eval_id, template)
            raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}") from e

        nombre = (
            f"InformeNPS_{patient_orm.primer_apellido or ''}"
            f"_{patient_orm.numero_documento}"
            f"_{patient_orm.fecha_atencion.strftime('%Y%m%d') if patient_orm.fecha_atencion else 'sin_fecha'}"
            ".pdf"
        )
        return pdf_bytes, nombre

    def execute_docx(self, eval_id: str) -> tuple[bytes, str]:
        from app.infrastructure.export_service import generate_report_docx

        report_data, ev, patient_orm = self.build_report_data(eval_id)

        try:
            docx_bytes = generate_report_docx(report_data)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        except Exception as e:
            logger.exception("Error generando DOCX para eval_id=%s", eval_id)
            raise HTTPException(status_code=500, detail=f"Error generando DOCX: {e}") from e

        nombre = (
            f"InformeNPS_{patient_orm.primer_apellido or ''}"
            f"_{patient_orm.numero_documento}"
            f"_{ev.fecha.strftime('%Y%m%d') if getattr(ev, 'fecha', None) else 'sin_fecha'}"
            ".docx"
        )
        return docx_bytes, nombre

    def execute_xlsx(self, eval_id: str) -> tuple[bytes, str]:
        from app.infrastructure.export_service import generate_evaluation_xlsx

        report_data, ev, patient_orm = self.build_report_data(eval_id)

        try:
            xlsx_bytes = generate_evaluation_xlsx(report_data)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        except Exception as e:
            logger.exception("Error generando XLSX para eval_id=%s", eval_id)
            raise HTTPException(status_code=500, detail=f"Error generando XLSX: {e}") from e

        nombre = (
            f"Puntajes_{patient_orm.primer_apellido or ''}"
            f"_{patient_orm.numero_documento}"
            f"_{ev.fecha.strftime('%Y%m%d') if getattr(ev, 'fecha', None) else 'sin_fecha'}"
            ".xlsx"
        )
        return xlsx_bytes, nombre
