"""
app/presentation/api/v1/therapy.py
====================================
Endpoints del módulo de psicología clínica (sesiones terapéuticas).

Coexiste con `/api/v1/evaluations/` (evaluación neuropsicológica). Comparte
paciente, profesional y agenda, pero los modelos viven en
``therapy_plans``, ``therapy_sessions`` y ``risk_assessments``.

Endpoints:
  GET    /therapy/plans?patient_id=<id>         lista de planes del paciente
  POST   /therapy/plans                          crea un plan
  GET    /therapy/plans/{plan_id}                detalle del plan + objetivos
  PATCH  /therapy/plans/{plan_id}                actualizar (cerrar, cambiar estado)

  GET    /therapy/sessions?patient_id=<id>      sesiones del paciente
  POST   /therapy/sessions                       crea una sesión nueva (SOAP)
  GET    /therapy/sessions/{session_id}          detalle
  PATCH  /therapy/sessions/{session_id}          actualizar (mientras no esté lockeada)
  POST   /therapy/sessions/{session_id}/lock     firma irreversible

  POST   /therapy/risk-assessments               registra evaluación de riesgo
  GET    /therapy/risk-assessments?patient_id    listado por paciente

Esta es la primera versión MVP del módulo. Próximas iteraciones (ver
``ROADMAP_EXPANSION.md`` Pilar 2): C-SSRS embebido, telepsicología,
tareas terapéuticas, informes de alta.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.infrastructure.database.orm_models import (
    RiskAssessmentORM,
    TherapyObjectiveORM,
    TherapyPlanORM,
    TherapySessionORM,
    TherapyTaskORM,
)
from app.presentation.api.v1.auth import CurrentUser
from app.presentation.dependencies import DbSession

therapy_router = APIRouter(prefix="/therapy", tags=["💚 Psicología Clínica"])


# ═════════════════════════════════════════════════════════════
# DTOs — Plan terapéutico
# ═════════════════════════════════════════════════════════════

class ObjectiveCreateDTO(BaseModel):
    descripcion: str = Field(..., min_length=3)
    criterios_medibles: str | None = None
    fecha_meta: datetime | None = None
    orden: int = 0


class ObjectiveResponseDTO(BaseModel):
    id: str
    plan_id: str
    descripcion: str
    criterios_medibles: str | None
    fecha_inicio: datetime
    fecha_meta: datetime | None
    estado: str
    progreso_pct: int
    orden: int


class TherapyPlanCreateDTO(BaseModel):
    patient_id: str
    profesional_id: str | None = None
    enfoque_principal: str | None = None
    diagnostico_principal: str | None = None
    diagnostico_secundario: str | None = None
    codigo_cie11: str | None = None
    motivo_consulta: str | None = None
    duracion_estimada_sesiones: int | None = None
    fecha_revision: datetime | None = None
    objetivos: list[ObjectiveCreateDTO] = []


class TherapyPlanResponseDTO(BaseModel):
    id: str
    patient_id: str
    profesional_id: str | None
    enfoque_principal: str | None
    diagnostico_principal: str | None
    diagnostico_secundario: str | None
    codigo_cie11: str | None = None
    motivo_consulta: str | None
    duracion_estimada_sesiones: int | None
    fecha_inicio: datetime
    fecha_revision: datetime | None
    fecha_cierre: datetime | None
    motivo_cierre: str | None
    estado: str
    objetivos: list[ObjectiveResponseDTO] = []


class TherapyPlanUpdateDTO(BaseModel):
    """Solo campos modificables después de creado."""
    fecha_revision: datetime | None = None
    fecha_cierre: datetime | None = None
    motivo_cierre: Literal["alta", "abandono", "derivacion", "cambio_terapeuta"] | None = None
    nota_cierre: str | None = None
    estado: Literal["activo", "pausado", "cerrado"] | None = None
    duracion_estimada_sesiones: int | None = None


# ═════════════════════════════════════════════════════════════
# DTOs — Sesión terapéutica
# ═════════════════════════════════════════════════════════════

class TherapySessionCreateDTO(BaseModel):
    patient_id: str
    plan_id: str | None = None
    profesional_id: str | None = None
    fecha: datetime | None = None
    duracion_min: int = 50
    modalidad: Literal["presencial", "telepsicologia", "telefonica"] = "presencial"
    enfoque_sesion: str | None = None
    soap_subjetivo: str | None = None
    soap_objetivo: str | None = None
    soap_analisis: str | None = None
    soap_plan: str | None = None
    objetivos_trabajados: str | None = None   # JSON list[obj_id] como str
    tareas_asignadas: str | None = None
    medicacion_actual: str | None = None
    riesgo_suicida: Literal[
        "ninguno", "ideacion_pasiva", "ideacion_activa", "plan", "intento_reciente"
    ] = "ninguno"
    riesgo_observaciones: str | None = None
    alianza_terapeutica: int | None = Field(None, ge=1, le=5)
    estado_emocional_ini: int | None = Field(None, ge=0, le=10)
    estado_emocional_fin: int | None = Field(None, ge=0, le=10)


class TherapySessionResponseDTO(BaseModel):
    id: str
    plan_id: str | None
    patient_id: str
    profesional_id: str | None
    fecha: datetime
    duracion_min: int
    modalidad: str
    enfoque_sesion: str | None
    soap_subjetivo: str | None
    soap_objetivo: str | None
    soap_analisis: str | None
    soap_plan: str | None
    objetivos_trabajados: str | None
    tareas_asignadas: str | None
    medicacion_actual: str | None
    riesgo_suicida: str
    riesgo_observaciones: str | None
    alianza_terapeutica: int | None
    estado_emocional_ini: int | None
    estado_emocional_fin: int | None
    locked_at: datetime | None
    locked_by: str | None
    created_at: datetime
    updated_at: datetime


class TherapySessionUpdateDTO(BaseModel):
    """Campos modificables mientras la sesión NO esté lockeada."""
    soap_subjetivo: str | None = None
    soap_objetivo: str | None = None
    soap_analisis: str | None = None
    soap_plan: str | None = None
    objetivos_trabajados: str | None = None
    tareas_asignadas: str | None = None
    medicacion_actual: str | None = None
    riesgo_suicida: str | None = None
    riesgo_observaciones: str | None = None
    alianza_terapeutica: int | None = Field(None, ge=1, le=5)
    estado_emocional_ini: int | None = Field(None, ge=0, le=10)
    estado_emocional_fin: int | None = Field(None, ge=0, le=10)


# ═════════════════════════════════════════════════════════════
# DTOs — Evaluación de riesgo
# ═════════════════════════════════════════════════════════════

class RiskAssessmentCreateDTO(BaseModel):
    patient_id: str
    session_id: str | None = None
    profesional_id: str | None = None
    instrumento: str = "c_ssrs"
    nivel: Literal["ninguno", "leve", "moderado", "alto", "inminente"]
    ideacion_suicida: bool = False
    ideacion_con_plan: bool = False
    intento_previo: bool = False
    intento_reciente_30d: bool = False
    factores_protectores: str | None = None
    factores_riesgo: str | None = None
    plan_seguridad: str | None = None
    derivacion_emergencia: bool = False
    nota_clinica: str | None = None


class RiskAssessmentResponseDTO(BaseModel):
    id: str
    patient_id: str
    session_id: str | None
    profesional_id: str | None
    fecha: datetime
    instrumento: str
    nivel: str
    ideacion_suicida: bool
    ideacion_con_plan: bool
    intento_previo: bool
    intento_reciente_30d: bool
    factores_protectores: str | None
    factores_riesgo: str | None
    plan_seguridad: str | None
    derivacion_emergencia: bool
    nota_clinica: str | None


# ═════════════════════════════════════════════════════════════
# Endpoints — Planes
# ═════════════════════════════════════════════════════════════

def _plan_to_dto(orm: TherapyPlanORM, objetivos: list[TherapyObjectiveORM]) -> TherapyPlanResponseDTO:
    return TherapyPlanResponseDTO(
        id=orm.id, patient_id=orm.patient_id, profesional_id=orm.profesional_id,
        enfoque_principal=orm.enfoque_principal,
        diagnostico_principal=orm.diagnostico_principal,
        diagnostico_secundario=orm.diagnostico_secundario,
        codigo_cie11=getattr(orm, "codigo_cie11", None),
        motivo_consulta=orm.motivo_consulta,
        duracion_estimada_sesiones=orm.duracion_estimada_sesiones,
        fecha_inicio=orm.fecha_inicio, fecha_revision=orm.fecha_revision,
        fecha_cierre=orm.fecha_cierre, motivo_cierre=orm.motivo_cierre,
        estado=orm.estado,
        objetivos=[ObjectiveResponseDTO(
            id=o.id, plan_id=o.plan_id, descripcion=o.descripcion,
            criterios_medibles=o.criterios_medibles, fecha_inicio=o.fecha_inicio,
            fecha_meta=o.fecha_meta, estado=o.estado,
            progreso_pct=o.progreso_pct or 0, orden=o.orden or 0,
        ) for o in objetivos],
    )


@therapy_router.get("/plans", response_model=list[TherapyPlanResponseDTO],
                    summary="Listar planes terapéuticos de un paciente")
def list_plans(
    patient_id: str = Query(..., description="UUID del paciente"),
    db: DbSession = None, _u=CurrentUser,
):
    plans = (db.query(TherapyPlanORM)
             .filter_by(patient_id=patient_id)
             .order_by(TherapyPlanORM.fecha_inicio.desc())
             .all())
    result = []
    for p in plans:
        objs = (db.query(TherapyObjectiveORM)
                .filter_by(plan_id=p.id)
                .order_by(TherapyObjectiveORM.orden, TherapyObjectiveORM.created_at)
                .all())
        result.append(_plan_to_dto(p, objs))
    return result


@therapy_router.post("/plans", response_model=TherapyPlanResponseDTO, status_code=201,
                     summary="Crear plan terapéutico (con objetivos opcionales)")
def create_plan(dto: TherapyPlanCreateDTO, db: DbSession, user=CurrentUser):
    from app.domain.clinical_engine.cie_mapping_service import resolve_cie11_code

    cie11 = dto.codigo_cie11 or resolve_cie11_code(dto.diagnostico_principal)

    plan = TherapyPlanORM(
        id=str(uuid.uuid4()),
        patient_id=dto.patient_id,
        profesional_id=dto.profesional_id or user.profesional_id,
        enfoque_principal=dto.enfoque_principal,
        diagnostico_principal=dto.diagnostico_principal,
        diagnostico_secundario=dto.diagnostico_secundario,
        codigo_cie11=cie11,
        motivo_consulta=dto.motivo_consulta,
        duracion_estimada_sesiones=dto.duracion_estimada_sesiones,
        fecha_revision=dto.fecha_revision,
        estado="activo",
    )
    db.add(plan)
    db.flush()
    objs: list[TherapyObjectiveORM] = []
    for o_dto in dto.objetivos:
        obj = TherapyObjectiveORM(
            id=str(uuid.uuid4()), plan_id=plan.id,
            descripcion=o_dto.descripcion, criterios_medibles=o_dto.criterios_medibles,
            fecha_meta=o_dto.fecha_meta, orden=o_dto.orden, estado="activo",
            progreso_pct=0,
        )
        db.add(obj)
        objs.append(obj)
    db.commit()
    return _plan_to_dto(plan, objs)


@therapy_router.get("/plans/{plan_id}", response_model=TherapyPlanResponseDTO,
                    summary="Detalle de un plan terapéutico")
def get_plan(plan_id: str, db: DbSession, _u=CurrentUser):
    plan = db.query(TherapyPlanORM).filter_by(id=plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan no encontrado.")
    objs = (db.query(TherapyObjectiveORM).filter_by(plan_id=plan_id)
            .order_by(TherapyObjectiveORM.orden, TherapyObjectiveORM.created_at).all())
    return _plan_to_dto(plan, objs)


@therapy_router.patch("/plans/{plan_id}", response_model=TherapyPlanResponseDTO,
                      summary="Actualizar plan (cerrar, cambiar estado, etc.)")
def update_plan(plan_id: str, dto: TherapyPlanUpdateDTO, db: DbSession, _u=CurrentUser):
    plan = db.query(TherapyPlanORM).filter_by(id=plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan no encontrado.")
    for field, value in dto.model_dump(exclude_none=True).items():
        setattr(plan, field, value)
    db.commit()
    objs = (db.query(TherapyObjectiveORM).filter_by(plan_id=plan_id)
            .order_by(TherapyObjectiveORM.orden).all())
    return _plan_to_dto(plan, objs)


# ═════════════════════════════════════════════════════════════
# Endpoints — Sesiones
# ═════════════════════════════════════════════════════════════

def _session_to_dto(orm: TherapySessionORM) -> TherapySessionResponseDTO:
    return TherapySessionResponseDTO(**{c.name: getattr(orm, c.name) for c in orm.__table__.columns
                                        if c.name not in ("signature_sha256", "archived_at", "archived_reason")})


@therapy_router.get("/sessions", response_model=list[TherapySessionResponseDTO],
                    summary="Listar sesiones terapéuticas de un paciente")
def list_sessions(
    patient_id: str = Query(...),
    plan_id: str | None = Query(None),
    db: DbSession = None, _u=CurrentUser,
):
    q = db.query(TherapySessionORM).filter_by(patient_id=patient_id)
    if plan_id:
        q = q.filter_by(plan_id=plan_id)
    sesiones = q.order_by(TherapySessionORM.fecha.desc()).all()
    return [_session_to_dto(s) for s in sesiones]


@therapy_router.post("/sessions", response_model=TherapySessionResponseDTO, status_code=201,
                     summary="Crear sesión terapéutica (notas SOAP)")
def create_session(dto: TherapySessionCreateDTO, db: DbSession, user=CurrentUser):
    sess = TherapySessionORM(
        id=str(uuid.uuid4()),
        plan_id=dto.plan_id, patient_id=dto.patient_id,
        profesional_id=dto.profesional_id or user.profesional_id,
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
    db.add(sess)
    db.commit()
    return _session_to_dto(sess)


@therapy_router.get("/sessions/{session_id}", response_model=TherapySessionResponseDTO,
                    summary="Detalle de una sesión terapéutica")
def get_session_detail(session_id: str, db: DbSession, _u=CurrentUser):
    sess = db.query(TherapySessionORM).filter_by(id=session_id).first()
    if not sess:
        raise HTTPException(404, "Sesión no encontrada.")
    return _session_to_dto(sess)


@therapy_router.patch("/sessions/{session_id}", response_model=TherapySessionResponseDTO,
                      summary="Actualizar sesión (solo si NO está lockeada)")
def update_session(session_id: str, dto: TherapySessionUpdateDTO, db: DbSession, _u=CurrentUser):
    sess = db.query(TherapySessionORM).filter_by(id=session_id).first()
    if not sess:
        raise HTTPException(404, "Sesión no encontrada.")
    if sess.locked_at:
        raise HTTPException(409, "Sesión firmada — no se puede modificar.")
    for field, value in dto.model_dump(exclude_none=True).items():
        setattr(sess, field, value)
    db.commit()
    return _session_to_dto(sess)


@therapy_router.post("/sessions/{session_id}/lock", response_model=TherapySessionResponseDTO,
                     summary="Firmar (lockear) sesión — irreversible")
def lock_session(session_id: str, db: DbSession, user=CurrentUser):
    sess = db.query(TherapySessionORM).filter_by(id=session_id).first()
    if not sess:
        raise HTTPException(404, "Sesión no encontrada.")
    if sess.locked_at:
        return _session_to_dto(sess)  # idempotente
    import hashlib
    content = "|".join([
        sess.soap_subjetivo or "",
        sess.soap_objetivo or "",
        sess.soap_analisis or "",
        sess.soap_plan or "",
        str(sess.riesgo_suicida or ""),
    ])
    sess.locked_at = datetime.now(UTC)
    sess.locked_by = user.id
    sess.signature_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    db.commit()
    return _session_to_dto(sess)


# ═════════════════════════════════════════════════════════════
# Endpoints — Evaluación de riesgo
# ═════════════════════════════════════════════════════════════

@therapy_router.post("/risk-assessments", response_model=RiskAssessmentResponseDTO, status_code=201,
                     summary="Registrar evaluación de riesgo suicida")
def create_risk_assessment(dto: RiskAssessmentCreateDTO, db: DbSession, user=CurrentUser):
    ra = RiskAssessmentORM(
        id=str(uuid.uuid4()),
        patient_id=dto.patient_id,
        session_id=dto.session_id,
        profesional_id=dto.profesional_id or user.profesional_id,
        instrumento=dto.instrumento, nivel=dto.nivel,
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
    db.add(ra)
    db.commit()
    return RiskAssessmentResponseDTO(**{c.name: getattr(ra, c.name) for c in ra.__table__.columns})


@therapy_router.get("/risk-assessments", response_model=list[RiskAssessmentResponseDTO],
                    summary="Historial de evaluaciones de riesgo de un paciente")
def list_risk_assessments(
    patient_id: str = Query(...),
    db: DbSession = None, _u=CurrentUser,
):
    assessments = (db.query(RiskAssessmentORM)
                   .filter_by(patient_id=patient_id)
                   .order_by(RiskAssessmentORM.fecha.desc())
                   .all())
    return [RiskAssessmentResponseDTO(**{c.name: getattr(a, c.name) for c in a.__table__.columns})
            for a in assessments]


# ═════════════════════════════════════════════════════════════
# DTOs — Tareas terapéuticas (tarea-casa entre sesiones)
# ═════════════════════════════════════════════════════════════

TASK_TIPOS = Literal[
    "registro_pensamientos", "registro_emocional", "autorregistro_conducta",
    "exposicion", "activacion_conductual", "habilidades_DBT",
    "psicoeducacion", "libre",
]
TASK_ESTADOS = Literal["pendiente", "en_progreso", "completada", "parcial", "omitida"]
TASK_FRECUENCIAS = Literal["diaria", "varias_semana", "semanal", "unica"]


class TherapyTaskCreateDTO(BaseModel):
    patient_id: str
    plan_id: str | None = None
    session_id: str | None = None
    profesional_id: str | None = None
    objetivo_id: str | None = None
    tipo: TASK_TIPOS = "libre"
    titulo: str = Field(..., min_length=3, max_length=120)
    descripcion: str | None = None
    fecha_limite: datetime | None = None
    frecuencia: TASK_FRECUENCIAS | None = None


class TherapyTaskUpdateDTO(BaseModel):
    """Para que el clínico revise o el sistema marque estado."""
    estado: TASK_ESTADOS | None = None
    respuesta: str | None = None
    adherencia_pct: int | None = Field(None, ge=0, le=100)
    dificultad_pct: int | None = Field(None, ge=0, le=100)
    utilidad_pct: int | None = Field(None, ge=0, le=100)
    nota_clinico: str | None = None
    revisar: bool = False  # si True, marca revisada_en = now
    completar: bool = False  # si True, marca completada_en = now + estado=completada


class TherapyTaskResponseDTO(BaseModel):
    id: str
    patient_id: str
    plan_id: str | None
    session_id: str | None
    profesional_id: str | None
    objetivo_id: str | None
    tipo: str
    titulo: str
    descripcion: str | None
    fecha_asignacion: datetime
    fecha_limite: datetime | None
    frecuencia: str | None
    estado: str
    completada_en: datetime | None
    respuesta: str | None
    adherencia_pct: int | None
    dificultad_pct: int | None
    utilidad_pct: int | None
    revisada_en: datetime | None
    nota_clinico: str | None
    created_at: datetime
    updated_at: datetime | None


# ═════════════════════════════════════════════════════════════
# Endpoints — Tareas terapéuticas
# ═════════════════════════════════════════════════════════════

@therapy_router.post("/tasks", response_model=TherapyTaskResponseDTO, status_code=201,
                     summary="Asigna una tarea terapéutica al paciente")
def create_task(
    dto: TherapyTaskCreateDTO,
    db: DbSession = None, _u=CurrentUser,
):
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
    db.add(task)
    db.commit()
    return TherapyTaskResponseDTO(**{c.name: getattr(task, c.name) for c in task.__table__.columns})


@therapy_router.get("/tasks", response_model=list[TherapyTaskResponseDTO],
                    summary="Lista tareas de un paciente (opcionalmente filtradas)")
def list_tasks(
    patient_id: str = Query(...),
    estado: str | None = Query(None, description="Filtrar por estado"),
    plan_id: str | None = Query(None),
    session_id: str | None = Query(None),
    incluir_archivadas: bool = Query(False),
    db: DbSession = None, _u=CurrentUser,
):
    q = db.query(TherapyTaskORM).filter_by(patient_id=patient_id)
    if estado:
        q = q.filter(TherapyTaskORM.estado == estado)
    if plan_id:
        q = q.filter(TherapyTaskORM.plan_id == plan_id)
    if session_id:
        q = q.filter(TherapyTaskORM.session_id == session_id)
    if not incluir_archivadas:
        q = q.filter(TherapyTaskORM.archived_at.is_(None))
    tasks = q.order_by(TherapyTaskORM.fecha_asignacion.desc()).all()
    return [TherapyTaskResponseDTO(**{c.name: getattr(t, c.name) for c in t.__table__.columns})
            for t in tasks]


@therapy_router.get("/tasks/{task_id}", response_model=TherapyTaskResponseDTO,
                    summary="Detalle de una tarea terapéutica")
def get_task(task_id: str, db: DbSession = None, _u=CurrentUser):
    task = db.query(TherapyTaskORM).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(404, "Tarea no encontrada")
    return TherapyTaskResponseDTO(**{c.name: getattr(task, c.name) for c in task.__table__.columns})


@therapy_router.patch("/tasks/{task_id}", response_model=TherapyTaskResponseDTO,
                      summary="Actualiza estado / respuesta / revisión clínica de una tarea")
def update_task(
    task_id: str,
    dto: TherapyTaskUpdateDTO,
    db: DbSession = None, _u=CurrentUser,
):
    task = db.query(TherapyTaskORM).filter_by(id=task_id).first()
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

    db.commit()
    return TherapyTaskResponseDTO(**{c.name: getattr(task, c.name) for c in task.__table__.columns})


@therapy_router.delete("/tasks/{task_id}", status_code=204,
                       summary="Archiva una tarea (soft-delete)")
def archive_task(task_id: str, db: DbSession = None, _u=CurrentUser):
    task = db.query(TherapyTaskORM).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(404, "Tarea no encontrada")
    task.archived_at = datetime.now(UTC)
    db.commit()
    return None


@therapy_router.get("/tasks/{patient_id}/summary",
                    summary="Resumen de adherencia a tareas terapéuticas")
def task_summary(patient_id: str, db: DbSession = None, _u=CurrentUser):
    """
    Resumen de cumplimiento de tareas para un paciente. Útil para mostrar
    en el panel principal de psicoterapia y como insumo para el informe
    de cierre terapéutico.
    """
    tasks = (db.query(TherapyTaskORM)
             .filter_by(patient_id=patient_id)
             .filter(TherapyTaskORM.archived_at.is_(None))
             .all())
    total = len(tasks)
    if total == 0:
        return {
            "total": 0, "completadas": 0, "parciales": 0, "pendientes": 0,
            "omitidas": 0, "adherencia_global_pct": 0,
            "dificultad_promedio": None, "utilidad_promedio": None,
        }
    completadas = sum(1 for t in tasks if t.estado == "completada")
    parciales = sum(1 for t in tasks if t.estado == "parcial")
    pendientes = sum(1 for t in tasks if t.estado in ("pendiente", "en_progreso"))
    omitidas = sum(1 for t in tasks if t.estado == "omitida")
    # Adherencia global: cuántas se completaron (parciales cuentan 50%)
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
