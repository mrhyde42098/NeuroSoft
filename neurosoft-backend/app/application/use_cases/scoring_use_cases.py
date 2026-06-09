"""
app/application/use_cases/scoring_use_cases.py
================================================
Casos de uso: Calificación, Observaciones y Reportes.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.application.dtos.scoring_dtos import (
    EvaluationDetailDTO,
    EvaluationSummaryDTO,
    ObservationResponseDTO,
    ObservationsCompleteDTO,
    ObservationUpsertDTO,
    PatientEvaluationsDTO,
    PatientInfoScoringDTO,
    ResultadoPruebaDTO,
    ScoringRequestDTO,
    ScoringResponseDTO,
    SignatureStatusDTO,
    SingleScoreRequestDTO,
    TestInfoDTO,
)
from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext
from app.infrastructure.repositories.patient_repo import PatientRepository

logger = logging.getLogger(__name__)

# Dominios clínicos válidos para observaciones
DOMINIOS_VALIDOS = {
    "apariencia_conducta",
    "lenguaje",
    "atencion_concentracion",
    "memoria",
    "funciones_ejecutivas",
    "habilidades_visoespaciales",
    "habilidades_motoras",
    "socio_emocional",
    "impresion_diagnostica",
    "recomendaciones",
    "antecedentes",
    "motivo_consulta",
}


# ─────────────────────────────────────────────────────────────
# 1. CALIFICAR EVALUACIÓN
# ─────────────────────────────────────────────────────────────


class ScoreEvaluationUseCase:
    """
    Aplica el motor de baremos a los puntajes brutos de un paciente.

    Flujo:
        1. Recuperar paciente de BD.
        2. Construir PatientContext (edad, sexo, escolaridad, población).
        3. Ejecutar ClinicalEngine.score().
        4. Persistir resultados en tabla evaluations.
        5. Retornar ScoringResponseDTO.
    """

    def __init__(
        self,
        patient_repo: PatientRepository,
        engine: ClinicalEngine,
        evaluation_repo=None,
    ):
        self._patient_repo = patient_repo
        self._engine = engine
        self._eval_repo = evaluation_repo

    def execute(self, dto: ScoringRequestDTO) -> ScoringResponseDTO:
        from app.infrastructure.repositories.evaluation_repo import SaveEvaluationCommand

        # 1. Cargar paciente
        paciente = self._patient_repo.find_by_id(dto.patient_id)

        # 2. Construir contexto demográfico
        ctx = PatientContext.from_demographics(
            birth_date=paciente.fecha_nacimiento,
            evaluation_date=paciente.fecha_atencion,
            sexo=paciente.sexo,
            escolaridad=paciente.escolaridad,
        )

        # 3. Motor de calificación
        engine_result = self._engine.score(
            paciente_id=dto.patient_id,
            puntajes=dto.puntajes,
            patient_context=ctx,
            protocolo=dto.protocolo,
        )

        # 4. Construir response DTOs
        resultados_dto = [
            ResultadoPruebaDTO(
                test_id=r.test_id,
                test_nombre=r.test_nombre,
                dominio_cognitivo=r.dominio_cognitivo,
                puntaje_bruto=r.puntaje_bruto,
                puntaje_escalar=r.puntaje_escalar,
                tipo_metrica=r.tipo_metrica,
                interpretacion=r.interpretacion,
                z_equivalente=r.z_equivalente,
                llave_baremo=r.llave_baremo_usada,
                metadata=r.metadata,
            )
            for r in engine_result.resultados
        ]

        response = ScoringResponseDTO(
            patient_id=dto.patient_id,
            protocolo=dto.protocolo,
            poblacion=engine_result.poblacion,
            edad_display=engine_result.edad_display,
            patient_info=PatientInfoScoringDTO(
                nombre=paciente.nombre_completo,
                fecha_nacimiento=paciente.fecha_nacimiento,
                edad_anios=ctx.age.years,
                escolaridad=paciente.escolaridad,
                motivo_consulta=paciente.motivo_consulta,
            ),
            fecha_calculo=datetime.now(UTC).isoformat(),
            resultados=resultados_dto,
            total_pruebas=engine_result.total_pruebas,
            pruebas_realizadas=engine_result.pruebas_realizadas,
            pruebas_sin_dato=engine_result.pruebas_sin_dato,
            advertencias=engine_result.advertencias,
            puntos_debiles=[r.test_nombre for r in engine_result.puntos_debiles],
            puntos_fuertes=[r.test_nombre for r in engine_result.puntos_fuertes],
        )

        # 5. Persistir en BD (si el repo está conectado)
        if self._eval_repo is not None:
            cmd = SaveEvaluationCommand(
                patient_id=dto.patient_id,
                protocolo=dto.protocolo,
                fecha=paciente.fecha_atencion,
                puntajes_brutos=dto.puntajes,
                resultados=[r.model_dump() for r in resultados_dto],
                poblacion=engine_result.poblacion,
                edad_display=engine_result.edad_display,
                pruebas_realizadas=engine_result.pruebas_realizadas,
                pruebas_sin_dato=engine_result.pruebas_sin_dato,
                advertencias=engine_result.advertencias,
                puntos_debiles=[r.test_nombre for r in engine_result.puntos_debiles],
                puntos_fuertes=[r.test_nombre for r in engine_result.puntos_fuertes],
            )
            saved = self._eval_repo.save(cmd)
            response.evaluation_id = saved.id

        return response


# ─────────────────────────────────────────────────────────────
# 2. CALIFICACIÓN RÁPIDA (preview de una prueba)
# ─────────────────────────────────────────────────────────────


class ScorePreviewUseCase:
    """Califica una sola prueba sin persistir. Para el frontend reactivo."""

    def __init__(self, patient_repo: PatientRepository, engine: ClinicalEngine):
        self._patient_repo = patient_repo
        self._engine = engine

    def execute(self, dto: SingleScoreRequestDTO) -> ResultadoPruebaDTO | None:
        paciente = self._patient_repo.find_by_id(dto.patient_id)
        ctx = PatientContext.from_demographics(
            birth_date=paciente.fecha_nacimiento,
            evaluation_date=paciente.fecha_atencion,
            sexo=paciente.sexo,
            escolaridad=paciente.escolaridad,
        )
        resultado = self._engine.score_single(dto.test_id, dto.puntaje_bruto, ctx)
        if resultado is None:
            return None
        return ResultadoPruebaDTO(
            test_id=resultado.test_id,
            test_nombre=resultado.test_nombre,
            dominio_cognitivo=resultado.dominio_cognitivo,
            puntaje_bruto=resultado.puntaje_bruto,
            puntaje_escalar=resultado.puntaje_escalar,
            tipo_metrica=resultado.tipo_metrica,
            interpretacion=resultado.interpretacion,
            z_equivalente=resultado.z_equivalente,
            llave_baremo=resultado.llave_baremo_usada,
            metadata=resultado.metadata,
        )


# ─────────────────────────────────────────────────────────────
# 3. LISTAR PRUEBAS DISPONIBLES
# ─────────────────────────────────────────────────────────────


class ListTestsUseCase:
    """Devuelve el catálogo de pruebas, filtrable por población."""

    def __init__(self, loader: BaremosLoader):
        self._loader = loader

    def execute(self, poblacion: str | None = None) -> list[TestInfoDTO]:
        if poblacion:
            tests = self._loader.get_pruebas_por_poblacion(poblacion)
        else:
            tests = {tid: self._loader.get_prueba(tid) for tid in self._loader.all_test_ids}

        return [
            TestInfoDTO(
                test_id=p.id,
                nombre=p.nombre,
                tipo_calculo=p.tipo_calculo,
                tipo_metrica=p.tipo_metrica,
                poblacion=p.poblacion,
            )
            for p in tests.values()
        ]


# ─────────────────────────────────────────────────────────────
# 4. OBSERVACIONES CLÍNICAS
# ─────────────────────────────────────────────────────────────


class UpsertObservationUseCase:
    """Guarda o actualiza la observación de un dominio clínico."""

    def __init__(self, session):
        self._session = session

    def execute(self, dto: ObservationUpsertDTO) -> ObservationResponseDTO:
        from app.infrastructure.database.orm_models import ObservationORM

        if dto.dominio not in DOMINIOS_VALIDOS:
            from app.core.exceptions import ApplicationError

            raise ApplicationError(
                f"Dominio '{dto.dominio}' no reconocido. Válidos: {sorted(DOMINIOS_VALIDOS)}",
                code="INVALID_DOMAIN",
            )

        # Buscar existente
        existing = (
            self._session.query(ObservationORM)
            .filter_by(
                patient_id=dto.patient_id,
                dominio=dto.dominio,
                evaluation_id=dto.evaluation_id,
            )
            .first()
        )
        now = datetime.now(UTC).isoformat()

        if existing:
            existing.texto = dto.texto
            existing.updated_at = now
            obs_id = existing.id
        else:
            obs_id = str(uuid.uuid4())
            obs = ObservationORM(
                id=obs_id,
                patient_id=dto.patient_id,
                evaluation_id=dto.evaluation_id,
                dominio=dto.dominio,
                texto=dto.texto,
                created_at=now,
                updated_at=now,
            )
            self._session.add(obs)

        return ObservationResponseDTO(
            id=obs_id,
            patient_id=dto.patient_id,
            evaluation_id=dto.evaluation_id,
            dominio=dto.dominio,
            texto=dto.texto,
            updated_at=now,
        )


class GetObservationsUseCase:
    """Retorna todas las observaciones de un paciente agrupadas por dominio."""

    def __init__(self, session):
        self._session = session

    def execute(self, patient_id: str, evaluation_id: str | None = None) -> ObservationsCompleteDTO:
        from app.infrastructure.database.orm_models import ObservationORM

        q = self._session.query(ObservationORM).filter_by(patient_id=patient_id)
        if evaluation_id:
            q = q.filter_by(evaluation_id=evaluation_id)
        obs_list = q.all()
        return ObservationsCompleteDTO(
            patient_id=patient_id,
            evaluation_id=evaluation_id,
            observaciones={o.dominio: o.texto for o in obs_list},
        )


# ─────────────────────────────────────────────────────────────
# 4. HISTORIAL DE EVALUACIONES
# ─────────────────────────────────────────────────────────────


class GetEvaluationHistoryUseCase:
    """
    Recupera el historial de evaluaciones de un paciente.
    Requiere que EvaluationRepository esté conectado.
    """

    def __init__(self, evaluation_repo, patient_repo: PatientRepository):
        self._eval_repo = evaluation_repo
        self._patient_repo = patient_repo

    def get_all(self, patient_id: str) -> PatientEvaluationsDTO:
        from app.application.dtos.scoring_dtos import PatientEvaluationsDTO

        # Verificar que el paciente existe
        self._patient_repo.find_by_id(patient_id)

        records = self._eval_repo.find_all_by_patient(patient_id)
        summaries = [_record_to_summary(r) for r in records]
        return PatientEvaluationsDTO(
            patient_id=patient_id,
            total_evaluaciones=len(summaries),
            evaluaciones=summaries,
        )

    def get_latest(self, patient_id: str) -> PatientEvaluationsDTO:
        """Solo la última evaluación por protocolo."""
        from app.application.dtos.scoring_dtos import PatientEvaluationsDTO

        self._patient_repo.find_by_id(patient_id)
        records = self._eval_repo.find_latest_by_patient(patient_id)
        summaries = [_record_to_summary(r) for r in records]
        return PatientEvaluationsDTO(
            patient_id=patient_id,
            total_evaluaciones=len(summaries),
            evaluaciones=summaries,
        )


class GetEvaluationDetailUseCase:
    """Recupera el detalle completo de una evaluación por ID."""

    def __init__(self, evaluation_repo):
        self._eval_repo = evaluation_repo

    def execute(self, eval_id: str) -> EvaluationDetailDTO:
        from app.application.dtos.scoring_dtos import EvaluationDetailDTO, ResultadoPruebaDTO

        record = self._eval_repo.find_by_id(eval_id)
        summary = _record_to_summary(record)

        resultados_dto = []
        for r in record.resultados:
            try:
                resultados_dto.append(ResultadoPruebaDTO(**r))
            except (TypeError, ValueError) as _skip_exc:
                # Un resultado histórico con esquema obsoleto no debe tumbar
                # el endpoint; se deja fuera del DTO y se registra para
                # que el administrador pueda depurar la data sucia.
                logger.warning(
                    "get_evaluation_detail: resultado descartado (%s: %s); raw=%.200r",
                    type(_skip_exc).__name__,
                    _skip_exc,
                    r,
                )

        return EvaluationDetailDTO(
            **summary.model_dump(),
            patient_id=record.patient_id,
            puntajes_brutos=record.puntajes_brutos,
            resultados=resultados_dto,
        )


# ─────────────────────────────────────────────────────────────
# 5. WORKFLOW DE FIRMA (Res. 2654 MinSalud)
# ─────────────────────────────────────────────────────────────


def _canonical_payload_for_signature(orm) -> str:
    """
    Serializa de forma determinística los campos inmutables de una
    evaluación para producir el hash de firma.

    La clave del diseño: solo se incluyen datos CLÍNICOS (puntajes y
    resultados); NO incluye `signed_at`, `signed_by`, ni timestamps
    volátiles — así el hash solo cambia si alguien altera los datos
    clínicos (evidencia de tampering).
    """
    import json as _json

    payload = {
        "id": orm.id,
        "patient_id": orm.patient_id,
        "protocolo": orm.protocolo,
        "fecha": orm.fecha.isoformat() if orm.fecha else None,
        "puntajes_brutos_json": orm.puntajes_brutos_json or "",
        "resultados_json": orm.resultados_json or "",
        "baremo_version": getattr(orm, "baremo_version", None),
        "baremo_checksum": getattr(orm, "baremo_checksum", None),
    }
    # sort_keys=True para que el orden sea estable
    return _json.dumps(payload, sort_keys=True, ensure_ascii=False)


def _compute_signature_hash(orm) -> str:
    """SHA-256 del payload canónico — usado como prueba de integridad."""
    import hashlib as _hashlib

    return _hashlib.sha256(_canonical_payload_for_signature(orm).encode("utf-8")).hexdigest()


class SignEvaluationUseCase:
    """
    Firma digitalmente una evaluación.

    Efectos:
      1. Escribe `signed_at`, `signed_by`, `signed_by_label`, `signature_sha256`.
      2. Registra un evento de auditoría `action=sign`.
      3. Tras firmar, `ScoreEvaluationUseCase` de esa misma evaluación
         debe rechazar actualizaciones con `EvaluationAlreadySignedError`.

    Idempotencia: si ya está firmada, lanza `EvaluationAlreadySignedError`
    — el frontend debe preguntar al clínico antes de pedir firma.
    """

    def __init__(self, session):
        self._session = session

    def execute(
        self,
        evaluation_id: str,
        actor_id: str | None,
        actor_label: str | None,
        note: str | None = None,
    ) -> SignatureStatusDTO:
        from app.application.dtos.scoring_dtos import SignatureStatusDTO
        from app.core.exceptions import (
            EvaluationAlreadySignedError,
            EvaluationNotFoundError,
        )
        from app.infrastructure.audit import record_event
        from app.infrastructure.database.orm_models import EvaluationORM

        orm = self._session.get(EvaluationORM, evaluation_id)
        if orm is None:
            raise EvaluationNotFoundError(evaluation_id)

        if orm.signed_at is not None:
            raise EvaluationAlreadySignedError(
                evaluation_id,
                signed_at=orm.signed_at.isoformat() if orm.signed_at else None,
            )

        # Calcular hash ANTES de modificar el ORM (deterministic payload).
        sha = _compute_signature_hash(orm)
        now = datetime.now(UTC)

        orm.signed_at = now
        orm.signed_by = actor_id
        orm.signed_by_label = (actor_label or "")[:150] or None
        orm.signature_sha256 = sha

        self._session.flush()

        record_event(
            self._session,
            action="sign",
            entity_type="evaluation",
            entity_id=evaluation_id,
            actor_id=actor_id,
            actor_label=actor_label,
            summary=(note or "Firma clínica de evaluación")[:300],
            commit=False,
        )

        logger.info(
            "Evaluación firmada: id=%s by=%s sha=%s",
            evaluation_id,
            actor_id,
            sha[:12],
        )
        return SignatureStatusDTO(
            evaluation_id=evaluation_id,
            signed=True,
            signed_at=now.isoformat(),
            signed_by=actor_id,
            signed_by_label=orm.signed_by_label,
            signature_sha256=sha,
            valid=True,
            note=note,
        )


class GetSignatureStatusUseCase:
    """
    Retorna el estado de firma de una evaluación + validación del hash.

    Si alguien alteró la BD directamente (SQL injection, manipulación
    manual del .db), el hash recalculado no coincide con el guardado y
    `valid=False`. El frontend debe mostrar un banner rojo de alerta.
    """

    def __init__(self, session):
        self._session = session

    def execute(self, evaluation_id: str) -> SignatureStatusDTO:
        from app.application.dtos.scoring_dtos import SignatureStatusDTO
        from app.core.exceptions import EvaluationNotFoundError
        from app.infrastructure.database.orm_models import EvaluationORM

        orm = self._session.get(EvaluationORM, evaluation_id)
        if orm is None:
            raise EvaluationNotFoundError(evaluation_id)

        signed = orm.signed_at is not None
        valid: bool | None = None
        if signed and orm.signature_sha256:
            recomputed = _compute_signature_hash(orm)
            valid = recomputed == orm.signature_sha256
            if not valid:
                logger.warning(
                    "Signature MISMATCH para evaluación %s: stored=%s recomputed=%s",
                    evaluation_id,
                    (orm.signature_sha256 or "")[:12],
                    recomputed[:12],
                )

        return SignatureStatusDTO(
            evaluation_id=evaluation_id,
            signed=signed,
            signed_at=orm.signed_at.isoformat() if orm.signed_at else None,
            signed_by=orm.signed_by,
            signed_by_label=orm.signed_by_label,
            signature_sha256=orm.signature_sha256,
            valid=valid,
        )


# Helper interno
def _record_to_summary(record) -> EvaluationSummaryDTO:
    from app.application.dtos.scoring_dtos import EvaluationSummaryDTO

    signed_at = getattr(record, "signed_at", None)
    return EvaluationSummaryDTO(
        evaluation_id=record.id,
        protocolo=record.protocolo,
        fecha=record.fecha.isoformat() if record.fecha else "",
        poblacion=record.poblacion,
        edad_display=record.edad_display,
        pruebas_realizadas=record.pruebas_realizadas,
        pruebas_sin_dato=record.pruebas_sin_dato,
        is_latest=record.is_latest,
        created_at=record.created_at.isoformat() if record.created_at else "",
        puntos_debiles=record.puntos_debiles or [],
        puntos_fuertes=record.puntos_fuertes or [],
        advertencias=record.advertencias or [],
        signed_at=signed_at.isoformat() if signed_at else None,
        signed_by=getattr(record, "signed_by", None),
        signed_by_label=getattr(record, "signed_by_label", None),
        signature_sha256=getattr(record, "signature_sha256", None),
    )
