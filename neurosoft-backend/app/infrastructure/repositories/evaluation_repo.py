"""
app/infrastructure/repositories/evaluation_repo.py
=====================================================
Repositorio de evaluaciones neuropsicológicas.

Persiste y recupera sesiones de calificación completas:
    - Puntajes brutos ingresados por el profesional
    - Resultados calculados por el engine (escalares, Z, interpretaciones)
    - Metadata de la sesión (protocolo, fecha, advertencias)

Una misma evaluación puede tener múltiples intentos/re-calificaciones;
cada POST a /scores/ crea un nuevo registro con is_latest=True
y marca el anterior como is_latest=False para ese paciente+protocolo.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, date, datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.exceptions import EvaluationNotFoundError
from app.infrastructure.database.orm_models import EvaluationORM

logger = logging.getLogger(__name__)

# Re-exportado para compatibilidad con importaciones existentes:
# `from app.infrastructure.repositories.evaluation_repo import EvaluationNotFoundError`
# La clase canónica vive en app.core.exceptions — antes había una versión
# duplicada local con código distinto ("EVAL_NOT_FOUND" vs "EVALUATION_NOT_FOUND")
# que impedía que los `except` del endpoint capturaran la excepción del repo.
__all__ = ["EvaluationNotFoundError", "EvaluationRecord", "SaveEvaluationCommand", "EvaluationRepository"]


# ─────────────────────────────────────────────────────────────
# Data Transfer Objects (interno al repositorio)
# ─────────────────────────────────────────────────────────────


class EvaluationRecord:
    """Representación plana de una evaluación guardada."""

    def __init__(
        self,
        id: str,
        patient_id: str,
        protocolo: str | None,
        fecha: date,
        puntajes_brutos: dict,
        resultados: list,
        poblacion: str | None,
        edad_display: str | None,
        pruebas_realizadas: int,
        pruebas_sin_dato: int,
        advertencias: list,
        puntos_debiles: list,
        puntos_fuertes: list,
        is_latest: bool,
        created_at: datetime,
        signed_at: datetime | None = None,
        signed_by: str | None = None,
        signed_by_label: str | None = None,
        signature_sha256: str | None = None,
    ):
        self.id = id
        self.patient_id = patient_id
        self.protocolo = protocolo
        self.fecha = fecha
        self.puntajes_brutos = puntajes_brutos
        self.resultados = resultados
        self.poblacion = poblacion
        self.edad_display = edad_display
        self.pruebas_realizadas = pruebas_realizadas
        self.pruebas_sin_dato = pruebas_sin_dato
        self.advertencias = advertencias
        self.puntos_debiles = puntos_debiles
        self.puntos_fuertes = puntos_fuertes
        self.is_latest = is_latest
        self.created_at = created_at
        # Workflow de firma
        self.signed_at = signed_at
        self.signed_by = signed_by
        self.signed_by_label = signed_by_label
        self.signature_sha256 = signature_sha256


class SaveEvaluationCommand:
    """Input para guardar una evaluación nueva."""

    def __init__(
        self,
        patient_id: str,
        protocolo: str | None,
        fecha: date,
        puntajes_brutos: dict,
        resultados: list,  # List[ResultadoPruebaDTO dict]
        poblacion: str | None,
        edad_display: str | None,
        pruebas_realizadas: int,
        pruebas_sin_dato: int,
        advertencias: list,
        puntos_debiles: list,
        puntos_fuertes: list,
    ):
        self.patient_id = patient_id
        self.protocolo = protocolo
        self.fecha = fecha
        self.puntajes_brutos = puntajes_brutos
        self.resultados = resultados
        self.poblacion = poblacion
        self.edad_display = edad_display
        self.pruebas_realizadas = pruebas_realizadas
        self.pruebas_sin_dato = pruebas_sin_dato
        self.advertencias = advertencias
        self.puntos_debiles = puntos_debiles
        self.puntos_fuertes = puntos_fuertes


# ─────────────────────────────────────────────────────────────
# Repositorio
# ─────────────────────────────────────────────────────────────


class EvaluationRepository:
    """
    CRUD completo para evaluaciones neuropsicológicas.

    Reglas de negocio:
        - Por cada (patient_id, protocolo) solo hay UN registro con is_latest=True.
          Al guardar una nueva evaluación del mismo protocolo, el anterior queda
          como histórico (is_latest=False).
        - Los puntajes y resultados se serializan a JSON en la BD.
          Se deserializan al leer.
    """

    def __init__(self, session: Session):
        self._session = session

    # ──────────────────────────────────────────────────────────
    # ESCRITURA
    # ──────────────────────────────────────────────────────────

    def save(self, cmd: SaveEvaluationCommand) -> EvaluationRecord:
        """
        Persiste una sesión de evaluación nueva.

        Marca el registro anterior del mismo protocolo como is_latest=False
        antes de guardar el nuevo.
        """
        # §C9-fix: flush + bloqueo de fila para reducir race con escrituras
        # concurrentes que marquen is_latest=True simultáneamente.
        # En SQLite (modo WAL) los UPDATE serializan a nivel de archivo,
        # pero hacemos flush explícito para asegurar visibilidad inmediata
        # entre operaciones de la misma sesión.
        if cmd.protocolo:
            self._session.query(EvaluationORM).filter(
                EvaluationORM.patient_id == cmd.patient_id,
                EvaluationORM.protocolo == cmd.protocolo,
                EvaluationORM.is_latest.is_(True),
            ).update({"is_latest": False}, synchronize_session=False)
            self._session.flush()

        # Intentar capturar versión del baremo cargado en memoria para
        # trazabilidad — no rompe si el loader aún no está disponible.
        baremo_version = None
        baremo_checksum = None
        try:
            from app.domain.clinical_engine.baremos_loader import BaremosLoader

            _loader = BaremosLoader.instance()
            baremo_version = _loader.baremo_version
            baremo_checksum = _loader.baremo_checksum
        except Exception as exc:
            # Loader puede no estar disponible en tests aislados.
            # No es critico — la evaluacion se guarda sin trazabilidad de baremo.
            logger.debug("BaremosLoader no disponible al guardar eval: %s", exc)

        orm = EvaluationORM(
            id=str(uuid.uuid4()),
            patient_id=cmd.patient_id,
            protocolo=cmd.protocolo,
            fecha=cmd.fecha,
            puntajes_brutos_json=json.dumps(cmd.puntajes_brutos, ensure_ascii=False),
            resultados_json=json.dumps(cmd.resultados, ensure_ascii=False, default=str),
            poblacion=cmd.poblacion,
            edad_display=cmd.edad_display,
            pruebas_realizadas=cmd.pruebas_realizadas,
            pruebas_sin_dato=cmd.pruebas_sin_dato,
            advertencias_json=json.dumps(cmd.advertencias, ensure_ascii=False),
            puntos_debiles_json=json.dumps(cmd.puntos_debiles, ensure_ascii=False),
            puntos_fuertes_json=json.dumps(cmd.puntos_fuertes, ensure_ascii=False),
            baremo_version=baremo_version,
            baremo_checksum=baremo_checksum,
            is_latest=True,
            created_at=datetime.now(UTC),
        )
        self._session.add(orm)
        self._session.flush()
        self._session.refresh(orm)

        logger.info(
            "Evaluación guardada: id=%s patient=%s protocolo=%s",
            orm.id,
            cmd.patient_id,
            cmd.protocolo,
        )
        return self._to_record(orm)

    # ──────────────────────────────────────────────────────────
    # LECTURA
    # ──────────────────────────────────────────────────────────

    def find_by_id(self, eval_id: str) -> EvaluationRecord:
        """Retorna una evaluación por ID. Lanza EvaluationNotFoundError si no existe."""
        orm = self._session.get(EvaluationORM, eval_id)
        if orm is None:
            raise EvaluationNotFoundError(eval_id)
        return self._to_record(orm)

    def find_latest_by_patient(self, patient_id: str) -> list[EvaluationRecord]:
        """
        Retorna la última evaluación de cada protocolo para un paciente.
        Ordenadas por fecha desc.
        """
        rows = (
            self._session.query(EvaluationORM)
            .filter(
                EvaluationORM.patient_id == patient_id,
                EvaluationORM.is_latest.is_(True),
            )
            .order_by(desc(EvaluationORM.fecha), desc(EvaluationORM.created_at))
            .all()
        )
        return [self._to_record(r) for r in rows]

    def find_all_by_patient(self, patient_id: str) -> list[EvaluationRecord]:
        """
        Retorna todo el historial de evaluaciones de un paciente,
        incluyendo versiones anteriores. Ordenadas por fecha desc.
        """
        rows = (
            self._session.query(EvaluationORM)
            .filter(EvaluationORM.patient_id == patient_id)
            .order_by(desc(EvaluationORM.fecha), desc(EvaluationORM.created_at))
            .all()
        )
        return [self._to_record(r) for r in rows]

    def find_latest_by_patient_and_protocolo(self, patient_id: str, protocolo: str) -> EvaluationRecord | None:
        """Retorna la última evaluación de un protocolo específico, o None."""
        orm = (
            self._session.query(EvaluationORM)
            .filter(
                EvaluationORM.patient_id == patient_id,
                EvaluationORM.protocolo == protocolo,
                EvaluationORM.is_latest.is_(True),
            )
            .first()
        )
        return self._to_record(orm) if orm else None

    def count_by_patient(self, patient_id: str) -> int:
        """Cuenta el total de evaluaciones (todas las versiones) de un paciente."""
        return self._session.query(EvaluationORM).filter(EvaluationORM.patient_id == patient_id).count()

    def delete(self, eval_id: str) -> None:
        """Elimina una evaluación por ID."""
        orm = self._session.get(EvaluationORM, eval_id)
        if orm is None:
            raise EvaluationNotFoundError(eval_id)
        self._session.delete(orm)
        logger.info("Evaluación eliminada: id=%s", eval_id)

    # ──────────────────────────────────────────────────────────
    # CONVERSIÓN ORM ↔ Record
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _to_record(orm: EvaluationORM) -> EvaluationRecord:
        def _parse(field) -> list | dict:
            if not field:
                return []
            try:
                return json.loads(field)
            except (json.JSONDecodeError, TypeError):
                return []

        return EvaluationRecord(
            id=orm.id,
            patient_id=orm.patient_id,
            protocolo=orm.protocolo,
            fecha=orm.fecha,
            puntajes_brutos=_parse(orm.puntajes_brutos_json) or {},
            resultados=_parse(orm.resultados_json),
            poblacion=getattr(orm, "poblacion", None),
            edad_display=getattr(orm, "edad_display", None),
            pruebas_realizadas=getattr(orm, "pruebas_realizadas", 0) or 0,
            pruebas_sin_dato=getattr(orm, "pruebas_sin_dato", 0) or 0,
            advertencias=_parse(getattr(orm, "advertencias_json", None)),
            puntos_debiles=_parse(getattr(orm, "puntos_debiles_json", None)),
            puntos_fuertes=_parse(getattr(orm, "puntos_fuertes_json", None)),
            is_latest=getattr(orm, "is_latest", True),
            created_at=orm.created_at,
            signed_at=getattr(orm, "signed_at", None),
            signed_by=getattr(orm, "signed_by", None),
            signed_by_label=getattr(orm, "signed_by_label", None),
            signature_sha256=getattr(orm, "signature_sha256", None),
        )
