"""Repositorio de planes, sesiones, riesgo y tareas terapéuticas."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.application.dtos.therapy_dtos import (
    ObjectiveResponseDTO,
    RiskAssessmentCreateDTO,
    RiskAssessmentResponseDTO,
    TherapyPlanCreateDTO,
    TherapyPlanResponseDTO,
    TherapyPlanUpdateDTO,
    TherapySessionCreateDTO,
    TherapySessionResponseDTO,
    TherapySessionUpdateDTO,
    TherapyTaskCreateDTO,
    TherapyTaskResponseDTO,
    TherapyTaskUpdateDTO,
)
from app.infrastructure.database.orm_models import (
    RiskAssessmentORM,
    TherapyObjectiveORM,
    TherapyPlanORM,
    TherapySessionORM,
    TherapyTaskORM,
)


def plan_to_dto(orm: TherapyPlanORM, objetivos: list[TherapyObjectiveORM]) -> TherapyPlanResponseDTO:
    return TherapyPlanResponseDTO(
        id=orm.id,
        patient_id=orm.patient_id,
        profesional_id=orm.profesional_id,
        enfoque_principal=orm.enfoque_principal,
        diagnostico_principal=orm.diagnostico_principal,
        diagnostico_secundario=orm.diagnostico_secundario,
        codigo_cie11=getattr(orm, "codigo_cie11", None),
        motivo_consulta=orm.motivo_consulta,
        duracion_estimada_sesiones=orm.duracion_estimada_sesiones,
        fecha_inicio=orm.fecha_inicio,
        fecha_revision=orm.fecha_revision,
        fecha_cierre=orm.fecha_cierre,
        motivo_cierre=orm.motivo_cierre,
        estado=orm.estado,
        objetivos=[
            ObjectiveResponseDTO(
                id=o.id,
                plan_id=o.plan_id,
                descripcion=o.descripcion,
                criterios_medibles=o.criterios_medibles,
                fecha_inicio=o.fecha_inicio,
                fecha_meta=o.fecha_meta,
                estado=o.estado,
                progreso_pct=o.progreso_pct or 0,
                orden=o.orden or 0,
            )
            for o in objetivos
        ],
    )


def session_to_dto(orm: TherapySessionORM) -> TherapySessionResponseDTO:
    return TherapySessionResponseDTO(
        **{
            c.name: getattr(orm, c.name)
            for c in orm.__table__.columns
            if c.name not in ("signature_sha256", "archived_at", "archived_reason")
        }
    )


def task_to_dto(orm: TherapyTaskORM) -> TherapyTaskResponseDTO:
    return TherapyTaskResponseDTO(**{c.name: getattr(orm, c.name) for c in orm.__table__.columns})


def risk_to_dto(orm: RiskAssessmentORM) -> RiskAssessmentResponseDTO:
    return RiskAssessmentResponseDTO(**{c.name: getattr(orm, c.name) for c in orm.__table__.columns})


class TherapyRepository:
    def __init__(self, session: Session):
        self._db = session

    def list_plans(self, patient_id: str) -> list[TherapyPlanResponseDTO]:
        plans = (
            self._db.query(TherapyPlanORM)
            .filter_by(patient_id=patient_id)
            .order_by(TherapyPlanORM.fecha_inicio.desc())
            .all()
        )
        result = []
        for plan in plans:
            objs = (
                self._db.query(TherapyObjectiveORM)
                .filter_by(plan_id=plan.id)
                .order_by(TherapyObjectiveORM.orden, TherapyObjectiveORM.created_at)
                .all()
            )
            result.append(plan_to_dto(plan, objs))
        return result

    def create_plan(
        self, dto: TherapyPlanCreateDTO, *, profesional_id: str | None, cie11: str | None
    ) -> TherapyPlanResponseDTO:
        plan = TherapyPlanORM(
            id=str(uuid.uuid4()),
            patient_id=dto.patient_id,
            profesional_id=dto.profesional_id or profesional_id,
            enfoque_principal=dto.enfoque_principal,
            diagnostico_principal=dto.diagnostico_principal,
            diagnostico_secundario=dto.diagnostico_secundario,
            codigo_cie11=cie11,
            motivo_consulta=dto.motivo_consulta,
            duracion_estimada_sesiones=dto.duracion_estimada_sesiones,
            fecha_revision=dto.fecha_revision,
            estado="activo",
        )
        self._db.add(plan)
        self._db.flush()
        objs: list[TherapyObjectiveORM] = []
        for o_dto in dto.objetivos:
            obj = TherapyObjectiveORM(
                id=str(uuid.uuid4()),
                plan_id=plan.id,
                descripcion=o_dto.descripcion,
                criterios_medibles=o_dto.criterios_medibles,
                fecha_meta=o_dto.fecha_meta,
                orden=o_dto.orden,
                estado="activo",
                progreso_pct=0,
            )
            self._db.add(obj)
            objs.append(obj)
        self._db.commit()
        return plan_to_dto(plan, objs)

    def get_plan(self, plan_id: str) -> TherapyPlanResponseDTO:
        plan = self._db.query(TherapyPlanORM).filter_by(id=plan_id).first()
        if not plan:
            raise HTTPException(404, "Plan no encontrado.")
        objs = (
            self._db.query(TherapyObjectiveORM)
            .filter_by(plan_id=plan_id)
            .order_by(TherapyObjectiveORM.orden, TherapyObjectiveORM.created_at)
            .all()
        )
        return plan_to_dto(plan, objs)

    def update_plan(self, plan_id: str, dto: TherapyPlanUpdateDTO) -> TherapyPlanResponseDTO:
        plan = self._db.query(TherapyPlanORM).filter_by(id=plan_id).first()
        if not plan:
            raise HTTPException(404, "Plan no encontrado.")
        for field, value in dto.model_dump(exclude_none=True).items():
            setattr(plan, field, value)
        self._db.commit()
        objs = self._db.query(TherapyObjectiveORM).filter_by(plan_id=plan_id).order_by(TherapyObjectiveORM.orden).all()
        return plan_to_dto(plan, objs)

    def list_sessions(self, patient_id: str, plan_id: str | None = None) -> list[TherapySessionResponseDTO]:
        q = self._db.query(TherapySessionORM).filter_by(patient_id=patient_id)
        if plan_id:
            q = q.filter_by(plan_id=plan_id)
        return [session_to_dto(s) for s in q.order_by(TherapySessionORM.fecha.desc()).all()]

    def create_session(self, dto: TherapySessionCreateDTO, *, profesional_id: str | None) -> TherapySessionResponseDTO:
        sess = TherapySessionORM(
            id=str(uuid.uuid4()),
            plan_id=dto.plan_id,
            patient_id=dto.patient_id,
            profesional_id=dto.profesional_id or profesional_id,
            fecha=dto.fecha or datetime.now(UTC),
            duracion_min=dto.duracion_min,
            modalidad=dto.modalidad,
            enfoque_sesion=dto.enfoque_sesion,
            soap_subjetivo=dto.soap_subjetivo,
            soap_objetivo=dto.soap_objetivo,
            soap_analisis=dto.soap_analisis,
            soap_plan=dto.soap_plan,
            objetivos_trabajados=dto.objetivos_trabajados,
            tareas_asignadas=dto.tareas_asignadas,
            medicacion_actual=dto.medicacion_actual,
            riesgo_suicida=dto.riesgo_suicida,
            riesgo_observaciones=dto.riesgo_observaciones,
            alianza_terapeutica=dto.alianza_terapeutica,
            estado_emocional_ini=dto.estado_emocional_ini,
            estado_emocional_fin=dto.estado_emocional_fin,
        )
        self._db.add(sess)
        self._db.commit()
        return session_to_dto(sess)

    def get_session(self, session_id: str) -> TherapySessionResponseDTO:
        sess = self._db.query(TherapySessionORM).filter_by(id=session_id).first()
        if not sess:
            raise HTTPException(404, "Sesión no encontrada.")
        return session_to_dto(sess)

    def update_session(self, session_id: str, dto: TherapySessionUpdateDTO) -> TherapySessionResponseDTO:
        sess = self._db.query(TherapySessionORM).filter_by(id=session_id).first()
        if not sess:
            raise HTTPException(404, "Sesión no encontrada.")
        if sess.locked_at:
            raise HTTPException(409, "Sesión firmada — no se puede modificar.")
        for field, value in dto.model_dump(exclude_none=True).items():
            setattr(sess, field, value)
        self._db.commit()
        return session_to_dto(sess)

    def lock_session(self, session_id: str, *, user_id: str) -> TherapySessionResponseDTO:
        sess = self._db.query(TherapySessionORM).filter_by(id=session_id).first()
        if not sess:
            raise HTTPException(404, "Sesión no encontrada.")
        if sess.locked_at:
            return session_to_dto(sess)
        content = "|".join(
            [
                sess.soap_subjetivo or "",
                sess.soap_objetivo or "",
                sess.soap_analisis or "",
                sess.soap_plan or "",
                str(sess.riesgo_suicida or ""),
            ]
        )
        sess.locked_at = datetime.now(UTC)
        sess.locked_by = user_id
        sess.signature_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        self._db.commit()
        return session_to_dto(sess)

    def create_risk_assessment(
        self, dto: RiskAssessmentCreateDTO, *, profesional_id: str | None
    ) -> RiskAssessmentResponseDTO:
        ra = RiskAssessmentORM(
            id=str(uuid.uuid4()),
            patient_id=dto.patient_id,
            session_id=dto.session_id,
            profesional_id=dto.profesional_id or profesional_id,
            instrumento=dto.instrumento,
            nivel=dto.nivel,
            ideacion_suicida=dto.ideacion_suicida,
            ideacion_con_plan=dto.ideacion_con_plan,
            intento_previo=dto.intento_previo,
            intento_reciente_30d=dto.intento_reciente_30d,
            factores_protectores=dto.factores_protectores,
            factores_riesgo=dto.factores_riesgo,
            plan_seguridad=dto.plan_seguridad,
            derivacion_emergencia=dto.derivacion_emergencia,
            nota_clinica=dto.nota_clinica,
        )
        self._db.add(ra)
        self._db.commit()
        return risk_to_dto(ra)

    def list_risk_assessments(self, patient_id: str) -> list[RiskAssessmentResponseDTO]:
        rows = (
            self._db.query(RiskAssessmentORM)
            .filter_by(patient_id=patient_id)
            .order_by(RiskAssessmentORM.fecha.desc())
            .all()
        )
        return [risk_to_dto(a) for a in rows]

    def create_task(self, dto: TherapyTaskCreateDTO) -> TherapyTaskResponseDTO:
        task = TherapyTaskORM(
            id=str(uuid.uuid4()),
            patient_id=dto.patient_id,
            plan_id=dto.plan_id,
            session_id=dto.session_id,
            profesional_id=dto.profesional_id,
            objetivo_id=dto.objetivo_id,
            tipo=dto.tipo,
            titulo=dto.titulo.strip(),
            descripcion=dto.descripcion,
            fecha_limite=dto.fecha_limite,
            frecuencia=dto.frecuencia,
            estado="pendiente",
        )
        self._db.add(task)
        self._db.commit()
        return task_to_dto(task)

    def list_tasks(
        self,
        patient_id: str,
        *,
        estado: str | None = None,
        plan_id: str | None = None,
        session_id: str | None = None,
        incluir_archivadas: bool = False,
    ) -> list[TherapyTaskResponseDTO]:
        q = self._db.query(TherapyTaskORM).filter_by(patient_id=patient_id)
        if estado:
            q = q.filter(TherapyTaskORM.estado == estado)
        if plan_id:
            q = q.filter(TherapyTaskORM.plan_id == plan_id)
        if session_id:
            q = q.filter(TherapyTaskORM.session_id == session_id)
        if not incluir_archivadas:
            q = q.filter(TherapyTaskORM.archived_at.is_(None))
        return [task_to_dto(t) for t in q.order_by(TherapyTaskORM.fecha_asignacion.desc()).all()]

    def get_task(self, task_id: str) -> TherapyTaskResponseDTO:
        task = self._db.query(TherapyTaskORM).filter_by(id=task_id).first()
        if not task:
            raise HTTPException(404, "Tarea no encontrada")
        return task_to_dto(task)

    def update_task(self, task_id: str, dto: TherapyTaskUpdateDTO) -> TherapyTaskResponseDTO:
        task = self._db.query(TherapyTaskORM).filter_by(id=task_id).first()
        if not task:
            raise HTTPException(404, "Tarea no encontrada")
        if task.archived_at is not None:
            raise HTTPException(400, "La tarea está archivada y no admite cambios")

        if dto.estado is not None:
            task.estado = dto.estado
        if dto.respuesta is not None:
            task.respuesta = dto.respuesta
        if dto.adherencia_pct is not None:
            task.adherencia_pct = dto.adherencia_pct
        if dto.dificultad_pct is not None:
            task.dificultad_pct = dto.dificultad_pct
        if dto.utilidad_pct is not None:
            task.utilidad_pct = dto.utilidad_pct
        if dto.nota_clinico is not None:
            task.nota_clinico = dto.nota_clinico

        now = datetime.now(UTC)
        if dto.completar:
            task.estado = "completada"
            task.completada_en = now
        if dto.revisar:
            task.revisada_en = now

        self._db.commit()
        return task_to_dto(task)

    def archive_task(self, task_id: str) -> None:
        task = self._db.query(TherapyTaskORM).filter_by(id=task_id).first()
        if not task:
            raise HTTPException(404, "Tarea no encontrada")
        task.archived_at = datetime.now(UTC)
        self._db.commit()

    def task_summary(self, patient_id: str) -> dict:
        tasks = (
            self._db.query(TherapyTaskORM)
            .filter_by(patient_id=patient_id)
            .filter(TherapyTaskORM.archived_at.is_(None))
            .all()
        )
        total = len(tasks)
        if total == 0:
            return {
                "total": 0,
                "completadas": 0,
                "parciales": 0,
                "pendientes": 0,
                "omitidas": 0,
                "adherencia_global_pct": 0,
                "dificultad_promedio": None,
                "utilidad_promedio": None,
            }
        completadas = sum(1 for t in tasks if t.estado == "completada")
        parciales = sum(1 for t in tasks if t.estado == "parcial")
        pendientes = sum(1 for t in tasks if t.estado in ("pendiente", "en_progreso"))
        omitidas = sum(1 for t in tasks if t.estado == "omitida")
        adherencia = round(((completadas + parciales * 0.5) / total) * 100)
        dificultades = [t.dificultad_pct for t in tasks if t.dificultad_pct is not None]
        utilidades = [t.utilidad_pct for t in tasks if t.utilidad_pct is not None]
        return {
            "total": total,
            "completadas": completadas,
            "parciales": parciales,
            "pendientes": pendientes,
            "omitidas": omitidas,
            "adherencia_global_pct": adherencia,
            "dificultad_promedio": round(sum(dificultades) / len(dificultades)) if dificultades else None,
            "utilidad_promedio": round(sum(utilidades) / len(utilidades)) if utilidades else None,
        }
