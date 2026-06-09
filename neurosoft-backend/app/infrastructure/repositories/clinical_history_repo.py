"""Repositorio de Historia Clínica."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.application.dtos.clinical_history_dtos import (
    ClinicalHistoryResponseDTO,
    ClinicalHistoryUpsertDTO,
)
from app.core.exceptions import PatientNotFoundError
from app.domain.clinical_engine.cie_mapping_service import resolve_cie11_code

logger = logging.getLogger(__name__)


def hc_to_response(orm) -> ClinicalHistoryResponseDTO:
    fields = [
        "id",
        "patient_id",
        "numero_documento",
        "fecha_atencion",
        "codigo_cie10",
        "codigo_cie11",
        "motivo_consulta",
        "edad_materna",
        "no_gestacion",
        "riesgos",
        "cual_riesgo",
        "estres_prenatal",
        "gestacion",
        "semanas",
        "tipo_parto",
        "peso_gr",
        "talla_cm",
        "condiciones_neonatales",
        "incubadora",
        "sosten_cefalico",
        "sedestacion",
        "gateo",
        "marcha",
        "balbuceo",
        "primeras_palabras",
        "habla_claro",
        "control_anual",
        "control_vesical",
        "tipo_estres_prenatal",
        "ucin",
        "patologicos_medicos",
        "sensoriales_motores",
        "psiquiatricos",
        "farmacologicos",
        "traumaticos",
        "quirurgicos",
        "toxicos",
        "alergicos",
        "terapeuticos",
        "paraclinicos",
        "familiares",
        "vive_con",
        "abc",
        "escolar_laboral",
        "cognitivo",
        "comportamiento_animo",
        "patron_sueno",
        "patron_alimentacion",
        "plan_atencion",
        "impresion_diagnostica_hc",
        "hipotesis_pre_eval",
        "obs_clinica_general",
        "obs_atencion",
        "obs_memoria",
        "obs_praxias_gnosias",
        "obs_lenguaje",
        "obs_funciones_ejecutivas",
        "obs_emociones",
        "obs_ci",
        "obs_impresion_dx",
        "obs_funcionalidad",
        "obs_recomendaciones",
    ]
    return ClinicalHistoryResponseDTO(
        **{f: getattr(orm, f) for f in fields},
        row_version=getattr(orm, "row_version", 1) or 1,
    )


class ClinicalHistoryRepository:
    def __init__(self, session: Session):
        self._db = session

    def get_by_patient(self, patient_id: str) -> ClinicalHistoryResponseDTO | None:
        from app.infrastructure.database.orm_models import ClinicalHistoryORM

        hc = self._db.query(ClinicalHistoryORM).filter_by(patient_id=patient_id).first()
        return hc_to_response(hc) if hc else None

    def get_by_id(self, hc_id: str) -> ClinicalHistoryResponseDTO | None:
        from app.infrastructure.database.orm_models import ClinicalHistoryORM

        hc = self._db.query(ClinicalHistoryORM).filter_by(id=hc_id).first()
        return hc_to_response(hc) if hc else None

    def upsert(self, dto: ClinicalHistoryUpsertDTO) -> ClinicalHistoryResponseDTO:
        from app.infrastructure.database.orm_models import ClinicalHistoryORM, ClinicalHistoryVersionORM, PatientORM

        patient = self._db.query(PatientORM).filter_by(id=dto.patient_id, is_active=True).first()
        if not patient:
            raise PatientNotFoundError(dto.patient_id)

        existing = (
            self._db.query(ClinicalHistoryORM)
            .filter_by(patient_id=dto.patient_id, fecha_atencion=dto.fecha_atencion)
            .first()
        )

        d, a, f, p, o = dto.desarrollo, dto.antecedentes, dto.familiar, dto.plan_atencion, dto.observaciones
        cie11 = dto.codigo_cie11 or resolve_cie11_code(dto.codigo_cie10)

        fields = dict(
            patient_id=dto.patient_id,
            numero_documento=patient.numero_documento,
            fecha_atencion=dto.fecha_atencion,
            codigo_cie10=dto.codigo_cie10,
            codigo_cie11=cie11,
            motivo_consulta=d.motivo_consulta,
            edad_materna=d.edad_materna,
            no_gestacion=d.no_gestacion,
            riesgos=d.riesgos,
            cual_riesgo=d.cual_riesgo,
            estres_prenatal=d.estres_prenatal,
            gestacion=d.gestacion,
            semanas=d.semanas,
            tipo_parto=d.tipo_parto,
            peso_gr=d.peso_gr,
            talla_cm=d.talla_cm,
            condiciones_neonatales=d.condiciones_neonatales,
            incubadora=d.incubadora,
            sosten_cefalico=d.sosten_cefalico,
            sedestacion=d.sedestacion,
            gateo=d.gateo,
            marcha=d.marcha,
            balbuceo=d.balbuceo,
            primeras_palabras=d.primeras_palabras,
            habla_claro=d.habla_claro,
            control_anual=d.control_anual,
            control_vesical=d.control_vesical,
            tipo_estres_prenatal=d.tipo_estres_prenatal,
            ucin=d.ucin,
            patologicos_medicos=a.patologicos_medicos,
            sensoriales_motores=a.sensoriales_motores,
            psiquiatricos=a.psiquiatricos,
            farmacologicos=a.farmacologicos,
            traumaticos=a.traumaticos,
            quirurgicos=a.quirurgicos,
            toxicos=a.toxicos,
            alergicos=a.alergicos,
            terapeuticos=a.terapeuticos,
            paraclinicos=a.paraclinicos,
            familiares=a.familiares,
            vive_con=f.vive_con,
            abc=f.abc,
            escolar_laboral=f.escolar_laboral,
            cognitivo=f.cognitivo,
            comportamiento_animo=f.comportamiento_animo,
            patron_sueno=f.patron_sueno,
            patron_alimentacion=f.patron_alimentacion,
            plan_atencion=p.plan_atencion,
            impresion_diagnostica_hc=p.impresion_diagnostica_hc,
            hipotesis_pre_eval=p.hipotesis_pre_eval,
            obs_clinica_general=o.obs_clinica_general,
            obs_atencion=o.obs_atencion,
            obs_memoria=o.obs_memoria,
            obs_praxias_gnosias=o.obs_praxias_gnosias,
            obs_lenguaje=o.obs_lenguaje,
            obs_funciones_ejecutivas=o.obs_funciones_ejecutivas,
            obs_emociones=o.obs_emociones,
            obs_ci=o.obs_ci,
            obs_impresion_dx=o.obs_impresion_dx,
            obs_funcionalidad=o.obs_funcionalidad,
            obs_recomendaciones=o.obs_recomendaciones,
        )

        if existing:
            if dto.row_version is not None and dto.row_version > 0:
                current_version = getattr(existing, "row_version", 1) or 1
                if dto.row_version != current_version:
                    from app.core.exceptions import ConcurrencyError

                    raise ConcurrencyError(
                        resource="Historia Clínica",
                        client_version=dto.row_version,
                        server_version=current_version,
                    )
            try:
                snapshot = {k: str(getattr(existing, k, "")) for k in fields}
                ver_snapshot = ClinicalHistoryVersionORM(
                    id=str(uuid.uuid4()),
                    hc_id=existing.id,
                    patient_id=existing.patient_id,
                    version_num=getattr(existing, "row_version", 1) or 1,
                    snapshot_json=json.dumps(snapshot, ensure_ascii=False, default=str),
                    saved_at=datetime.now(UTC),
                )
                self._db.add(ver_snapshot)
            except Exception as snap_err:
                logger.warning("Error guardando snapshot HC: %s", snap_err)
            for k, v in fields.items():
                setattr(existing, k, v)
            existing.updated_at = datetime.now(UTC)
            existing.row_version = (getattr(existing, "row_version", 1) or 1) + 1
            return hc_to_response(existing)

        hc = ClinicalHistoryORM(id=str(uuid.uuid4()), row_version=1, **fields)
        self._db.add(hc)
        return hc_to_response(hc)
