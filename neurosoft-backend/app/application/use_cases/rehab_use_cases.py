"""
app/application/use_cases/rehab_use_cases.py
================================================
Casos de uso del módulo de rehabilitación neuropsicológica.

Cubre:
  • CRUD del plan de intervención (con firma SHA-256, igual que evaluación)
  • Listar / consultar el catálogo de actividades
  • Registrar sesiones (clínico o paciente vía link público)
  • Generar y validar links públicos para tarea-casa
"""
from __future__ import annotations

import hashlib
import json
import logging
import secrets
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _parse_json(raw: str | None) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _canonical_plan_payload(orm) -> str:
    """Payload determinístico para el hash de firma del plan."""
    payload = {
        "id":                  orm.id,
        "patient_id":          orm.patient_id,
        "evaluation_id":       orm.evaluation_id,
        "fecha_inicio":        orm.fecha_inicio.isoformat() if orm.fecha_inicio else None,
        "fecha_fin_estimada":  orm.fecha_fin_estimada.isoformat() if orm.fecha_fin_estimada else None,
        "frecuencia_semanal":  orm.frecuencia_semanal,
        "objetivos":           orm.objetivos or "",
        "dominios_json":       orm.dominios_json or "",
        "actividades_json":    orm.actividades_json or "",
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def _compute_plan_hash(orm) -> str:
    return hashlib.sha256(
        _canonical_plan_payload(orm).encode("utf-8")
    ).hexdigest()


def _orm_to_response(orm) -> dict[str, Any]:
    return {
        "id":                 orm.id,
        "patient_id":         orm.patient_id,
        "evaluation_id":      orm.evaluation_id,
        "profesional_id":     orm.profesional_id,
        "fecha_inicio":       orm.fecha_inicio,
        "fecha_fin_estimada": orm.fecha_fin_estimada,
        "frecuencia_semanal": orm.frecuencia_semanal,
        "objetivos":          orm.objetivos,
        "dominios":           _parse_json(orm.dominios_json) or [],
        "actividades":        _parse_json(orm.actividades_json) or [],
        "notas":              orm.notas,
        "estado":             orm.estado,
        "created_at":         orm.created_at,
        "updated_at":         orm.updated_at,
        "signed_at":          orm.signed_at,
        "signed_by":          orm.signed_by,
        "signed_by_label":    orm.signed_by_label,
        "signature_sha256":   orm.signature_sha256,
    }


def _session_to_response(orm) -> dict[str, Any]:
    return {
        "id":            orm.id,
        "plan_id":       orm.plan_id,
        "activity_id":   orm.activity_id,
        "activity_slug": orm.activity_slug,
        "patient_id":    orm.patient_id,
        "ts_inicio":     orm.ts_inicio,
        "ts_fin":        orm.ts_fin,
        "duracion_seg":  orm.duracion_seg,
        "score":         orm.score,
        "aciertos":      orm.aciertos,
        "errores":       orm.errores,
        "parametros":    _parse_json(orm.parametros_json),
        "resultado":     _parse_json(orm.resultado_json),
        "modo":          orm.modo,
        "origen_token":  orm.origen_token,
    }


# ═══════════════════════════════════════════════════════════════
# CATÁLOGO DE ACTIVIDADES
# ═══════════════════════════════════════════════════════════════

class ListActivitiesUseCase:
    def __init__(self, session):
        self._db = session

    def execute(
        self,
        dominio: str | None = None,
        only_active: bool = True,
    ) -> list[dict[str, Any]]:
        from app.infrastructure.database.orm_models import RehabActivityCatalogORM

        q = self._db.query(RehabActivityCatalogORM)
        if dominio:
            q = q.filter(RehabActivityCatalogORM.dominio == dominio)
        if only_active:
            q = q.filter(RehabActivityCatalogORM.activo.is_(True))
        items = q.order_by(
            RehabActivityCatalogORM.orden.asc(),
            RehabActivityCatalogORM.nombre.asc(),
        ).all()
        return [{
            "id":                 a.id,
            "slug":               a.slug,
            "nombre":             a.nombre,
            "dominio":            a.dominio,
            "dificultad_default": a.dificultad_default,
            "duracion_min":       a.duracion_min,
            "descripcion":        a.descripcion,
            "instrucciones":      a.instrucciones,
            "parametros_default": _parse_json(a.parametros_json),
            "provider":           a.provider,
            "external_url":       a.external_url,
            "activo":             a.activo,
            "orden":              a.orden,
        } for a in items]


# ═══════════════════════════════════════════════════════════════
# PLAN DE INTERVENCIÓN
# ═══════════════════════════════════════════════════════════════

class CreateRehabPlanUseCase:
    def __init__(self, session):
        self._db = session

    def execute(self, dto) -> dict[str, Any]:
        from app.core.exceptions import PatientNotFoundError
        from app.infrastructure.database.orm_models import (
            PatientORM,
            RehabPlanORM,
        )

        if self._db.get(PatientORM, dto.patient_id) is None:
            raise PatientNotFoundError(dto.patient_id)

        orm = RehabPlanORM(
            id=str(uuid.uuid4()),
            patient_id=dto.patient_id,
            evaluation_id=dto.evaluation_id,
            profesional_id=dto.profesional_id,
            fecha_inicio=dto.fecha_inicio,
            fecha_fin_estimada=dto.fecha_fin_estimada,
            frecuencia_semanal=dto.frecuencia_semanal,
            objetivos=dto.objetivos,
            dominios_json=json.dumps(dto.dominios or [], ensure_ascii=False),
            actividades_json=json.dumps(dto.actividades or [], ensure_ascii=False),
            notas=dto.notas,
            estado="borrador",
        )
        self._db.add(orm)
        self._db.flush()
        return _orm_to_response(orm)


class GetRehabPlanUseCase:
    def __init__(self, session):
        self._db = session

    def by_id(self, plan_id: str) -> dict[str, Any]:
        from app.infrastructure.database.orm_models import RehabPlanORM
        orm = self._db.get(RehabPlanORM, plan_id)
        if orm is None:
            from app.core.exceptions import ApplicationError
            raise ApplicationError(
                message=f"Plan '{plan_id}' no encontrado.",
                code="REHAB_PLAN_NOT_FOUND",
                http_status=404,
            )
        return _orm_to_response(orm)

    def by_patient(self, patient_id: str, include_archived: bool = False):
        from app.infrastructure.database.orm_models import RehabPlanORM
        q = self._db.query(RehabPlanORM).filter_by(patient_id=patient_id)
        if not include_archived:
            q = q.filter(RehabPlanORM.archived_at.is_(None))
        return [_orm_to_response(o) for o in
                q.order_by(RehabPlanORM.created_at.desc()).all()]


class UpdateRehabPlanUseCase:
    def __init__(self, session):
        self._db = session

    def execute(self, plan_id: str, dto) -> dict[str, Any]:
        from app.core.exceptions import (
            ApplicationError,
            EvaluationAlreadySignedError,
        )
        from app.infrastructure.database.orm_models import RehabPlanORM

        orm = self._db.get(RehabPlanORM, plan_id)
        if orm is None:
            raise ApplicationError(
                message=f"Plan '{plan_id}' no encontrado.",
                code="REHAB_PLAN_NOT_FOUND",
                http_status=404,
            )
        # Mientras esté firmado: solo se puede cambiar `estado`
        is_signed = orm.signed_at is not None
        data = dto.model_dump(exclude_none=True)
        if is_signed:
            non_state = {k: v for k, v in data.items() if k != "estado"}
            if non_state:
                raise EvaluationAlreadySignedError(
                    plan_id, signed_at=orm.signed_at.isoformat(),
                )

        if "fecha_fin_estimada" in data:
            orm.fecha_fin_estimada = data["fecha_fin_estimada"]
        if "frecuencia_semanal" in data:
            orm.frecuencia_semanal = data["frecuencia_semanal"]
        if "objetivos" in data:
            orm.objetivos = data["objetivos"]
        if "dominios" in data:
            orm.dominios_json = json.dumps(data["dominios"], ensure_ascii=False)
        if "actividades" in data:
            orm.actividades_json = json.dumps(data["actividades"], ensure_ascii=False)
        if "notas" in data:
            orm.notas = data["notas"]
        if "estado" in data:
            valid = {"borrador", "activo", "pausado", "finalizado", "archivado"}
            if data["estado"] not in valid:
                raise ApplicationError(
                    message=f"Estado inválido. Válidos: {valid}",
                    code="INVALID_STATE",
                    http_status=422,
                )
            orm.estado = data["estado"]

        self._db.flush()
        return _orm_to_response(orm)


class SignRehabPlanUseCase:
    """Firma del plan — cierre clínico análogo a `SignEvaluationUseCase`."""

    def __init__(self, session):
        self._db = session

    def execute(
        self,
        plan_id: str,
        actor_id: str | None,
        actor_label: str | None,
        note: str | None = None,
    ) -> dict[str, Any]:
        from app.core.exceptions import (
            ApplicationError,
            EvaluationAlreadySignedError,
        )
        from app.infrastructure.audit import record_event
        from app.infrastructure.database.orm_models import RehabPlanORM

        orm = self._db.get(RehabPlanORM, plan_id)
        if orm is None:
            raise ApplicationError(
                message=f"Plan '{plan_id}' no encontrado.",
                code="REHAB_PLAN_NOT_FOUND",
                http_status=404,
            )
        if orm.signed_at is not None:
            raise EvaluationAlreadySignedError(
                plan_id, signed_at=orm.signed_at.isoformat(),
            )

        orm.signed_at = datetime.now(UTC)
        orm.signed_by = actor_id
        orm.signed_by_label = actor_label
        orm.signature_sha256 = _compute_plan_hash(orm)
        if orm.estado == "borrador":
            orm.estado = "activo"
        self._db.flush()

        record_event(
            self._db,
            action="sign",
            entity_type="rehab_plan",
            entity_id=plan_id,
            actor_id=actor_id,
            actor_label=actor_label,
            summary=f"Plan de rehabilitación firmado{' — ' + note if note else ''}",
            commit=False,
        )
        return _orm_to_response(orm)


# ═══════════════════════════════════════════════════════════════
# SESIONES
# ═══════════════════════════════════════════════════════════════

class CreateRehabSessionUseCase:
    def __init__(self, session):
        self._db = session

    def execute(
        self,
        dto,
        origen_token: str | None = None,
    ) -> dict[str, Any]:
        from app.core.exceptions import ApplicationError, PatientNotFoundError
        from app.infrastructure.database.orm_models import (
            PatientORM,
            RehabActivityCatalogORM,
            RehabSessionORM,
        )

        if self._db.get(PatientORM, dto.patient_id) is None:
            raise PatientNotFoundError(dto.patient_id)

        activity = (
            self._db.query(RehabActivityCatalogORM)
            .filter_by(slug=dto.activity_slug, activo=True)
            .first()
        )
        if activity is None:
            raise ApplicationError(
                message=f"Actividad '{dto.activity_slug}' no existe o está inactiva.",
                code="ACTIVITY_NOT_FOUND",
                http_status=404,
            )

        # Métricas mínimas extraídas del resultado (si existen)
        score = dto.resultado.get("score")
        aciertos = dto.resultado.get("aciertos") or dto.resultado.get("hits")
        errores = dto.resultado.get("errores") or dto.resultado.get("errors")

        ts_inicio = datetime.now(UTC)
        ts_fin = ts_inicio
        if dto.duracion_seg:
            ts_inicio = ts_fin - timedelta(seconds=dto.duracion_seg)

        orm = RehabSessionORM(
            id=str(uuid.uuid4()),
            plan_id=dto.plan_id,
            activity_id=activity.id,
            activity_slug=dto.activity_slug,
            patient_id=dto.patient_id,
            ts_inicio=ts_inicio,
            ts_fin=ts_fin,
            duracion_seg=dto.duracion_seg,
            parametros_json=json.dumps(dto.parametros or {}, ensure_ascii=False),
            resultado_json=json.dumps(dto.resultado, ensure_ascii=False),
            score=int(score) if isinstance(score, (int, float)) else None,
            aciertos=int(aciertos) if isinstance(aciertos, (int, float)) else None,
            errores=int(errores) if isinstance(errores, (int, float)) else None,
            modo=dto.modo or "en_consulta",
            origen_token=origen_token,
            notas_clinico=dto.notas_clinico,
        )
        self._db.add(orm)
        self._db.flush()
        return _session_to_response(orm)


class ListRehabSessionsUseCase:
    def __init__(self, session):
        self._db = session

    def by_patient(
        self,
        patient_id: str,
        plan_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        from app.infrastructure.database.orm_models import RehabSessionORM
        q = self._db.query(RehabSessionORM).filter_by(patient_id=patient_id)
        if plan_id:
            q = q.filter_by(plan_id=plan_id)
        rows = q.order_by(RehabSessionORM.ts_inicio.desc()).limit(limit).all()
        return [_session_to_response(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
# LINKS PÚBLICOS PARA TAREA-CASA
# ═══════════════════════════════════════════════════════════════

class CreateRehabShareUseCase:
    def __init__(self, session):
        self._db = session

    def execute(self, dto, created_by: str) -> dict[str, Any]:
        from app.core.exceptions import ApplicationError
        from app.infrastructure.database.orm_models import (
            RehabPlanORM,
            RehabShareLinkORM,
        )

        plan = self._db.get(RehabPlanORM, dto.plan_id)
        if plan is None:
            raise ApplicationError(
                message=f"Plan '{dto.plan_id}' no encontrado.",
                code="REHAB_PLAN_NOT_FOUND",
                http_status=404,
            )
        if plan.signed_at is None:
            raise ApplicationError(
                message="Solo se pueden compartir planes firmados.",
                code="REHAB_PLAN_NOT_SIGNED",
                http_status=409,
            )

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(
            days=dto.expires_in_days,
        )
        link = RehabShareLinkORM(
            id=str(uuid.uuid4()),
            token=token,
            plan_id=plan.id,
            patient_id=plan.patient_id,
            created_by=created_by,
            expires_at=expires_at,
            revoked=False,
        )
        self._db.add(link)
        self._db.flush()
        return {
            "id":             link.id,
            "token":          link.token,
            "plan_id":        link.plan_id,
            "patient_id":     link.patient_id,
            "expires_at":     link.expires_at,
            "revoked":        link.revoked,
            "sessions_count": link.sessions_count,
            "public_url":     f"/shared/rehab/{link.token}",
        }


class GetPublicRehabPlanUseCase:
    """Lo que ve el paciente al abrir un link público."""

    def __init__(self, session):
        self._db = session

    def execute(self, token: str) -> dict[str, Any]:
        from app.core.exceptions import ApplicationError
        from app.infrastructure.database.orm_models import (
            PatientORM,
            RehabPlanORM,
            RehabShareLinkORM,
        )

        link = (
            self._db.query(RehabShareLinkORM)
            .filter_by(token=token, revoked=False)
            .first()
        )
        if link is None:
            raise ApplicationError(
                message="Link inválido o revocado.",
                code="REHAB_LINK_NOT_FOUND",
                http_status=404,
            )
        # Comparar expiración
        now = datetime.now(UTC)
        exp = link.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)
        if exp < now:
            raise ApplicationError(
                message="Link expirado.",
                code="REHAB_LINK_EXPIRED",
                http_status=410,
            )

        plan = self._db.get(RehabPlanORM, link.plan_id)
        if plan is None or plan.estado in ("archivado", "finalizado"):
            raise ApplicationError(
                message="Plan no disponible.",
                code="REHAB_PLAN_UNAVAILABLE",
                http_status=410,
            )

        patient = self._db.get(PatientORM, link.patient_id)
        first_name = patient.primer_nombre if patient else None

        return {
            "plan_id":            plan.id,
            "patient_first_name": first_name,
            "actividades":        _parse_json(plan.actividades_json) or [],
            "expires_at":         link.expires_at,
        }


class SubmitPublicRehabResultUseCase:
    """El paciente envía el resultado de una actividad desde el viewer público."""

    def __init__(self, session):
        self._db = session

    def execute(self, token: str, dto) -> dict[str, Any]:
        from app.core.exceptions import ApplicationError
        from app.infrastructure.database.orm_models import (
            RehabActivityCatalogORM,
            RehabSessionORM,
            RehabShareLinkORM,
        )

        link = (
            self._db.query(RehabShareLinkORM)
            .filter_by(token=token, revoked=False)
            .first()
        )
        if link is None:
            raise ApplicationError(
                message="Link inválido o revocado.",
                code="REHAB_LINK_NOT_FOUND",
                http_status=404,
            )
        now = datetime.now(UTC)
        exp = link.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)
        if exp < now:
            raise ApplicationError(
                message="Link expirado.",
                code="REHAB_LINK_EXPIRED",
                http_status=410,
            )

        activity = (
            self._db.query(RehabActivityCatalogORM)
            .filter_by(slug=dto.activity_slug, activo=True)
            .first()
        )
        if activity is None:
            raise ApplicationError(
                message=f"Actividad '{dto.activity_slug}' no existe.",
                code="ACTIVITY_NOT_FOUND",
                http_status=404,
            )

        score = dto.resultado.get("score")
        aciertos = dto.resultado.get("aciertos") or dto.resultado.get("hits")
        errores = dto.resultado.get("errores") or dto.resultado.get("errors")

        ts_fin = datetime.now(UTC)
        ts_inicio = ts_fin
        if dto.duracion_seg:
            ts_inicio = ts_fin - timedelta(seconds=dto.duracion_seg)

        orm = RehabSessionORM(
            id=str(uuid.uuid4()),
            plan_id=link.plan_id,
            activity_id=activity.id,
            activity_slug=dto.activity_slug,
            patient_id=link.patient_id,
            ts_inicio=ts_inicio,
            ts_fin=ts_fin,
            duracion_seg=dto.duracion_seg,
            parametros_json=json.dumps(dto.parametros or {}, ensure_ascii=False),
            resultado_json=json.dumps(dto.resultado, ensure_ascii=False),
            score=int(score) if isinstance(score, (int, float)) else None,
            aciertos=int(aciertos) if isinstance(aciertos, (int, float)) else None,
            errores=int(errores) if isinstance(errores, (int, float)) else None,
            modo="tarea_casa",
            origen_token=token,
        )
        self._db.add(orm)
        # Actualizar contador y last_used_at del link
        link.sessions_count = (link.sessions_count or 0) + 1
        link.last_used_at = ts_fin
        self._db.flush()
        return _session_to_response(orm)


# ═══════════════════════════════════════════════════════════════
# SEED del catálogo (idempotente, se llama en lifespan)
# ═══════════════════════════════════════════════════════════════

DEFAULT_ACTIVITIES = [
    {
        "slug":               "stroop",
        "nombre":             "Stroop — Inhibición e interferencia",
        "dominio":            "funciones_ejecutivas",
        "dificultad_default": 2,
        "duracion_min":       5,
        "descripcion": (
            "Tarea clásica de Stroop: el paciente debe nombrar el COLOR "
            "de la tinta en que está escrita una palabra (ROJO, AZUL, "
            "VERDE, AMARILLO), ignorando el significado. Mide control "
            "inhibitorio y resistencia a la interferencia."
        ),
        "instrucciones": (
            "Verás palabras en distintos colores. Indica el COLOR de la "
            "tinta, NO la palabra escrita. Tan rápido como puedas, "
            "minimizando errores."
        ),
        "parametros_default": {"trials": 30, "isi_ms": 1500, "congruency_ratio": 0.5},
        "provider":           "internal",
        "orden":              1,
    },
    {
        "slug":               "n_back",
        "nombre":             "N-back visuoespacial",
        "dominio":            "memoria_trabajo",
        "dificultad_default": 2,
        "duracion_min":       6,
        "descripcion": (
            "Aparecerán cuadros iluminados en una grilla 3×3. El paciente "
            "debe presionar cuando la posición actual coincida con la "
            "que apareció N pasos atrás (1-back, 2-back, 3-back)."
        ),
        "instrucciones": (
            "Presiona ESPACIO si la posición actual es la misma que "
            "apareció hace N pasos. Empezamos en N=1; subiremos según "
            "tu desempeño."
        ),
        "parametros_default": {"n": 1, "trials": 20, "isi_ms": 2000},
        "provider":           "internal",
        "orden":              2,
    },
    {
        "slug":               "fluency_verbal",
        "nombre":             "Fluencia verbal cronometrada",
        "dominio":            "lenguaje",
        "dificultad_default": 1,
        "duracion_min":       3,
        "descripcion": (
            "El paciente escribe la mayor cantidad posible de palabras "
            "que cumplan un criterio (categoría semántica o letra inicial) "
            "en 60 segundos. Mide acceso lexical y flexibilidad."
        ),
        "instrucciones": (
            "Escribe en el cuadro tantas palabras como puedas que "
            "cumplan el criterio, separadas por enter. Tienes 60 segundos."
        ),
        "parametros_default": {"duration_sec": 60, "criterio": "animales"},
        "provider":           "internal",
        "orden":              3,
    },
    {
        "slug":               "tachado",
        "nombre":             "Tachado / Cancelación",
        "dominio":            "atencion",
        "dificultad_default": 1,
        "duracion_min":       4,
        "descripcion": (
            "El paciente debe identificar y marcar todos los estímulos "
            "objetivo (p. ej. la letra 'A') entre distractores en una "
            "matriz. Mide atención sostenida y selectiva."
        ),
        "instrucciones": (
            "Haz clic sobre cada letra A que veas. Trabaja de izquierda "
            "a derecha y de arriba abajo, sin saltarte ninguna."
        ),
        "parametros_default": {"target": "A", "rows": 10, "cols": 15},
        "provider":           "internal",
        "orden":              4,
    },
    {
        "slug":               "corsi_forward",
        "nombre":             "Cubos de Corsi — Directo",
        "dominio":            "memoria_trabajo",
        "dificultad_default": 2,
        "duracion_min":       5,
        "descripcion": (
            "Test clásico de Corsi (1972) para memoria de trabajo "
            "visoespacial. Se iluminan cubos en secuencia y el paciente "
            "debe reproducir el mismo orden. La longitud crece hasta que "
            "falla dos veces consecutivas. Score = span Corsi."
        ),
        "instrucciones": (
            "Observa la secuencia de cubos que se iluminan. Cuando termine, "
            "reproduce el mismo orden haciendo clic sobre cada cubo. "
            "La secuencia comenzará con 2 cubos."
        ),
        "parametros_default": {"mode": "forward", "maxLen": 9},
        "provider":           "internal",
        "orden":              5,
    },
    {
        "slug":               "corsi_backward",
        "nombre":             "Cubos de Corsi — Inverso",
        "dominio":            "memoria_trabajo",
        "dificultad_default": 3,
        "duracion_min":       5,
        "descripcion": (
            "Variante inversa del Corsi: el paciente reproduce la "
            "secuencia en ORDEN INVERSO. Mide manipulación activa en "
            "memoria de trabajo visoespacial (mayor demanda ejecutiva)."
        ),
        "instrucciones": (
            "Observa la secuencia de cubos. Al terminar, reproduce la "
            "secuencia en ORDEN INVERSO (del último al primero)."
        ),
        "parametros_default": {"mode": "backward", "maxLen": 9},
        "provider":           "internal",
        "orden":              6,
    },
    {
        "slug":               "mental_rotation",
        "nombre":             "Rotación Mental (visoespacial)",
        "dominio":            "visoespacial",
        "dificultad_default": 2,
        "duracion_min":       5,
        "descripcion": (
            "Tarea de Shepard & Metzler (1971). El paciente debe "
            "identificar cuál de dos figuras es la misma rotada (vs su "
            "imagen espejo). Mide y entrena rotación mental."
        ),
        "instrucciones": (
            "Verá una figura modelo y dos opciones. Una es la misma "
            "figura rotada; la otra es su espejo (imposible de igualar "
            "rotando). Escoja la igualada por rotación."
        ),
        "parametros_default": {"trials": 12},
        "provider":           "internal",
        "orden":              8,
    },
    {
        "slug":               "ekman_recognition",
        "nombre":             "Reconocimiento de Emociones (Ekman)",
        "dominio":            "cognicion_social",
        "dificultad_default": 1,
        "duracion_min":       4,
        "descripcion": (
            "Entrenamiento de cognición social. Se presenta una cara "
            "esquemática con una de las 6 emociones básicas (Ekman) y "
            "el paciente elige la etiqueta correcta. Útil en rehab. de "
            "TEA, TCE frontal y esquizofrenia."
        ),
        "instrucciones": (
            "Verá una cara con una expresión. Identifique la emoción "
            "entre las 6 opciones (Alegría, Tristeza, Ira, Miedo, "
            "Sorpresa, Asco)."
        ),
        "parametros_default": {"trials": 12},
        "provider":           "internal",
        "orden":              9,
    },
    {
        "slug":               "spaced_retrieval",
        "nombre":             "Recobro Espaciado (SRT)",
        "dominio":            "memoria",
        "dificultad_default": 2,
        "duracion_min":       15,
        "descripcion": (
            "Spaced Retrieval Training (Bourgeois 1990) — gold standard "
            "para rehabilitación de memoria en demencia leve y TCL "
            "amnésico. El clínico define un par pregunta→respuesta y se "
            "practica con intervalos crecientes (30s, 1m, 2m, 4m, 8m, "
            "16m). Errorless: si falla, baja al último intervalo correcto."
        ),
        "instrucciones": (
            "El clínico ingresa una pregunta y su respuesta. Tras un "
            "tiempo creciente entre prácticas, se le pregunta al "
            "paciente. Si responde bien, sube de intervalo; si falla, "
            "baja al previo correcto."
        ),
        "parametros_default": {"max_interval_min": 16},
        "provider":           "internal",
        "orden":              7,
    },
    {
        "slug":               "cpt",
        "nombre":             "CPT — Atención Sostenida",
        "dominio":            "atencion",
        "dificultad_default": 2,
        "duracion_min":       5,
        "descripcion": (
            "Continuous Performance Task (CPT): letras aparecen a ritmo "
            "fijo y el paciente presiona solo cuando aparece la letra "
            "objetivo (X por defecto). Mide atención sostenida, "
            "omisiones (falta de vigilancia) y falsos positivos "
            "(impulsividad). Registra tiempo de reacción medio."
        ),
        "instrucciones": (
            "Aparecerán letras, una a la vez. Presiona el botón (o "
            "Espacio) SOLO cuando aparezca la letra X. "
            "Mantén la atención durante toda la tarea."
        ),
        "parametros_default": {"trials": 30, "isi_ms": 1500, "target": "X", "target_ratio": 0.25},
        "provider":           "internal",
        "orden":              10,
    },
    {
        "slug":               "go_no_go",
        "nombre":             "Go / No-Go Progresivo",
        "dominio":            "atencion",
        "dificultad_default": 2,
        "duracion_min":       6,
        "descripcion": (
            "Tarea clásica de inhibición de respuesta. Círculo verde → "
            "presionar (GO); círculo rojo → inhibir (NO-GO). "
            "3 bloques con dificultad creciente: velocidad aumenta y "
            "se incrementa la proporción de estímulos No-Go. "
            "Registra aciertos GO, omisiones y comisiones."
        ),
        "instrucciones": (
            "Círculo VERDE: presiona rápido. "
            "Círculo ROJO: no presiones. "
            "La velocidad aumenta en cada bloque."
        ),
        "parametros_default": {"trials_per_block": 20},
        "provider":           "internal",
        "orden":              11,
    },
    {
        "slug":               "set_shifting",
        "nombre":             "Clasificación flexible — WCST simple",
        "dominio":            "funciones_ejecutivas",
        "dificultad_default": 3,
        "duracion_min":       10,
        "descripcion": (
            "Versión simplificada del Wisconsin Card Sorting Test (WCST). "
            "El paciente clasifica cartas por COLOR, FORMA o NÚMERO; la "
            "regla cambia silenciosamente tras un número de aciertos "
            "consecutivos. Mide flexibilidad cognitiva y detecta "
            "perseveraciones (errores por regla anterior)."
        ),
        "instrucciones": (
            "Coloca cada carta en la pila que corresponda. "
            "La regla puede cambiar — usa el feedback para adaptarte. "
            "Clasifica por color, forma o cantidad de símbolos."
        ),
        "parametros_default": {"total_trials": 48, "trials_per_rule": 10},
        "provider":           "internal",
        "orden":              12,
    },
    {
        "slug":               "denominacion_claves",
        "nombre":             "Denominación con jerarquía de claves",
        "dominio":            "lenguaje",
        "dificultad_default": 2,
        "duracion_min":       8,
        "descripcion": (
            "Tarea de denominación confrontacional con sistema jerárquico "
            "de ayudas. Se presenta el estímulo y el clínico registra si "
            "la denominación fue espontánea (nivel 0), con clave "
            "semántica (nivel 1), con clave fonémica (nivel 2) o no "
            "evocada (nivel 3). Útil en afasia, TCE y demencia."
        ),
        "instrucciones": (
            "Se mostrará el concepto. Intente nombrarlo sin ayuda. "
            "Si no recuerda, el clínico dará una pista semántica "
            "y luego fonémica. Se registra el nivel de ayuda requerido."
        ),
        "parametros_default": {"items": []},
        "provider":           "internal",
        "orden":              13,
    },
    {
        "slug":               "tower_of_london",
        "nombre":             "Torre de Londres — Planificación ejecutiva",
        "dominio":            "ejecutiva",
        "dificultad_default": 2,
        "duracion_min":       10,
        "descripcion": (
            "Tarea clásica de planificación ejecutiva y resolución de problemas. "
            "El paciente mueve discos entre tres postes para replicar un estado "
            "objetivo en el menor número de movimientos posible. Evalúa "
            "planificación prospectiva, control inhibitorio y memoria de trabajo."
        ),
        "instrucciones": (
            "Verá tres postes con discos de colores. Debe mover los discos "
            "uno a uno hasta copiar la configuración objetivo. Un disco grande "
            "nunca puede colocarse encima de uno pequeño. Use el mínimo de "
            "movimientos posible."
        ),
        "parametros_default": {"levels": 5},
        "provider":           "internal",
        "orden":              14,
    },
    {
        "slug":               "mente_ojos",
        "nombre":             "Reading the Mind in the Eyes — Cognición social",
        "dominio":            "cognicion_social",
        "dificultad_default": 2,
        "duracion_min":       10,
        "descripcion": (
            "Versión rehabilitación del paradigma de Baron-Cohen et al. (2001). "
            "El paciente observa imágenes de la región ocular y elige el estado "
            "mental que mejor describe a la persona. Trabaja teoría de la mente, "
            "reconocimiento de emociones complejas y empatía cognitiva."
        ),
        "instrucciones": (
            "Verá los ojos de diferentes personas. Elija la palabra que mejor "
            "describa lo que esa persona siente o piensa en ese momento. "
            "No hay tiempo límite. Recibirá retroalimentación educativa."
        ),
        "parametros_default": {"n_items": 8},
        "provider":           "internal",
        "orden":              15,
    },
    {
        "slug":               "avd_dinero",
        "nombre":             "Manejo de dinero — AVD cognitiva",
        "dominio":            "avd",
        "dificultad_default": 2,
        "duracion_min":       10,
        "descripcion": (
            "Actividad de transferencia ecológica: situaciones reales de "
            "manejo de dinero (calcular vuelto, comparar precios y planificar "
            "presupuesto). Indicada en TCE, demencia leve y rehabilitación "
            "de funciones instrumentales de la vida diaria."
        ),
        "instrucciones": (
            "Resolverá situaciones cotidianas de compras y presupuesto. "
            "Lea con atención cada situación y responda. "
            "Se le dará retroalimentación al finalizar."
        ),
        "parametros_default": {"scenarios": 5},
        "provider":           "internal",
        "orden":              16,
    },
]


# ═══════════════════════════════════════════════════════════════
# EVOLUCIÓN LONGITUDINAL — gráfica por dominio cognitivo
# ═══════════════════════════════════════════════════════════════

class GetEvolutionUseCase:
    """
    Cruza `rehab_sessions` con el catálogo (dominio cognitivo) y devuelve
    una serie temporal por dominio, agrupada por semana ISO.

    Estructura de retorno:
      {
        "dominios": [
          {
            "dominio": "funciones_ejecutivas",
            "puntos": [
              {"semana": "2026-W14", "score_avg": 78, "n": 4},
              {"semana": "2026-W15", "score_avg": 82, "n": 5},
              ...
            ]
          },
          ...
        ],
        "total_sesiones": 27,
        "rango": {"desde": "2026-04-01", "hasta": "2026-05-15"}
      }
    """

    def __init__(self, session):
        self._db = session

    def execute(
        self,
        patient_id: str,
        plan_id: str | None = None,
    ) -> dict[str, Any]:
        from collections import defaultdict

        from app.infrastructure.database.orm_models import (
            RehabActivityCatalogORM,
            RehabSessionORM,
        )

        q = (
            self._db.query(
                RehabSessionORM.ts_inicio,
                RehabSessionORM.score,
                RehabActivityCatalogORM.dominio,
            )
            .join(
                RehabActivityCatalogORM,
                RehabSessionORM.activity_id == RehabActivityCatalogORM.id,
            )
            .filter(RehabSessionORM.patient_id == patient_id)
            .filter(RehabSessionORM.score.isnot(None))
        )
        if plan_id:
            q = q.filter(RehabSessionORM.plan_id == plan_id)
        q = q.order_by(RehabSessionORM.ts_inicio.asc())

        rows = q.all()
        if not rows:
            return {
                "dominios": [],
                "total_sesiones": 0,
                "rango": {"desde": None, "hasta": None},
            }

        # Agrupar por (dominio, semana ISO)
        by_dom_week: dict[str, dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )
        for ts_ini, score, dominio in rows:
            iso_year, iso_week, _ = ts_ini.isocalendar()
            key = f"{iso_year}-W{iso_week:02d}"
            by_dom_week[dominio][key].append(int(score))

        out = []
        for dominio, weeks in by_dom_week.items():
            puntos = []
            for week_key in sorted(weeks.keys()):
                scores = weeks[week_key]
                # §C3-fix: guard explícito contra división por cero
                avg = round(sum(scores) / len(scores), 1) if scores else 0.0
                puntos.append({
                    "semana": week_key,
                    "score_avg": avg,
                    "n": len(scores),
                })
            out.append({"dominio": dominio, "puntos": puntos})

        return {
            "dominios": sorted(out, key=lambda d: d["dominio"]),
            "total_sesiones": len(rows),
            "rango": {
                "desde": rows[0][0].date().isoformat(),
                "hasta": rows[-1][0].date().isoformat(),
            },
        }


# ═══════════════════════════════════════════════════════════════
# ADHERENCIA — sesiones realizadas vs. esperadas
# ═══════════════════════════════════════════════════════════════

class GetAdherenceUseCase:
    """
    Calcula adherencia al plan de rehabilitación de un paciente.

    Fórmula:
      esperadas  = frecuencia_semanal × semanas_transcurridas
      realizadas = sesiones registradas en el rango [fecha_inicio, hoy]
      adherencia = realizadas / esperadas (clip 0..1.5)

    Devuelve también las cifras de la última semana ISO para el dashboard.
    """

    def __init__(self, session):
        self._db = session

    def execute(self, patient_id: str) -> dict[str, Any]:
        from app.infrastructure.database.orm_models import (
            RehabPlanORM,
            RehabSessionORM,
        )

        plan = (
            self._db.query(RehabPlanORM)
            .filter_by(patient_id=patient_id)
            .filter(RehabPlanORM.archived_at.is_(None))
            .filter(RehabPlanORM.estado.in_(("activo", "borrador", "pausado")))
            .order_by(RehabPlanORM.created_at.desc())
            .first()
        )
        if plan is None:
            return {
                "has_plan":           False,
                "patient_id":         patient_id,
                "plan_id":            None,
                "frecuencia_semanal": 0,
                "semanas_activas":    0,
                "sesiones_esperadas": 0,
                "sesiones_realizadas": 0,
                "adherencia_pct":     0,
                "esta_semana": {"realizadas": 0, "esperadas": 0},
            }

        today = date.today()
        start = plan.fecha_inicio
        days = max((today - start).days, 0)
        weeks = max(days // 7, 0) + (1 if days % 7 else 0)
        # Mínimo 1 semana para que el plan recién creado no devuelva 0
        if weeks == 0:
            weeks = 1
        expected = plan.frecuencia_semanal * weeks

        # Sesiones realizadas en el rango
        from sqlalchemy import func as _f
        done = (
            self._db.query(_f.count(RehabSessionORM.id))
            .filter(RehabSessionORM.patient_id == patient_id)
            .filter(RehabSessionORM.plan_id == plan.id)
            .scalar()
            or 0
        )
        adherence = min(1.5, done / expected) if expected else 0
        adherence_pct = int(round(adherence * 100))

        # Esta semana ISO: usamos rango de fechas (lunes 00:00 → ahora)
        # en lugar de strftime, porque el formato de SQLite (%W) y el
        # ISO week de Python pueden diferir en los bordes de año.
        from datetime import datetime as _dt
        from datetime import time as _time
        monday = today - timedelta(days=today.weekday())
        monday_dt = _dt.combine(monday, _time.min)
        this_week = (
            self._db.query(_f.count(RehabSessionORM.id))
            .filter(RehabSessionORM.patient_id == patient_id)
            .filter(RehabSessionORM.plan_id == plan.id)
            .filter(RehabSessionORM.ts_inicio >= monday_dt)
            .scalar()
            or 0
        )

        return {
            "has_plan":            True,
            "patient_id":          patient_id,
            "plan_id":             plan.id,
            "frecuencia_semanal":  plan.frecuencia_semanal,
            "semanas_activas":     weeks,
            "sesiones_esperadas":  expected,
            "sesiones_realizadas": int(done),
            "adherencia_pct":      adherence_pct,
            "esta_semana": {
                "realizadas": int(this_week),
                "esperadas":  plan.frecuencia_semanal,
            },
        }


# ═══════════════════════════════════════════════════════════════
# SUGERENCIA DE PLAN A PARTIR DE EVALUACIÓN
# ═══════════════════════════════════════════════════════════════

# Mapeo "test_id incluye → dominio cognitivo del catálogo".
# Heurística simple para una primera versión; el clínico puede editar.
_TEST_TO_DOMAIN = (
    # (substring del test_id, dominio)
    ("Aten",        "atencion"),
    ("Span",        "memoria_trabajo"),
    ("RDD",         "memoria_trabajo"),
    ("LN",          "memoria_trabajo"),
    ("Mem",         "memoria"),
    ("Recuer",      "memoria"),
    ("Voc",         "lenguaje"),
    ("Sem",         "lenguaje"),
    ("Lenguaje",    "lenguaje"),
    ("Cubo",        "visoespacial"),
    ("Mat",         "visoespacial"),
    ("FigInc",      "visoespacial"),
    ("Cl",          "velocidad_procesamiento"),
    ("BusSim",      "velocidad_procesamiento"),
    ("Reg",         "velocidad_procesamiento"),
    ("Com",         "funciones_ejecutivas"),
    ("ConD",        "funciones_ejecutivas"),
    ("Fluid",       "funciones_ejecutivas"),
)


def _test_to_domain(test_id: str) -> str | None:
    if not test_id:
        return None
    for substr, dom in _TEST_TO_DOMAIN:
        if substr.lower() in test_id.lower():
            return dom
    return None


class SuggestPlanFromEvaluationUseCase:
    """
    A partir de una evaluación firmada (o no), identifica los dominios
    con desempeño bajo (Z ≤ -1 o interpretación 'bajo'/'deficitario') y
    sugiere un plan inicial: dominios objetivo + actividades del catálogo
    cuyo dominio coincida.

    NO crea el plan automáticamente — lo devuelve para que el clínico lo
    revise, edite y guarde.
    """

    def __init__(self, session):
        self._db = session

    def execute(self, evaluation_id: str) -> dict[str, Any]:
        from collections import Counter

        from app.core.exceptions import EvaluationNotFoundError
        from app.infrastructure.database.orm_models import (
            EvaluationORM,
            RehabActivityCatalogORM,
        )

        ev = self._db.get(EvaluationORM, evaluation_id)
        if ev is None:
            raise EvaluationNotFoundError(evaluation_id)

        resultados = _parse_json(ev.resultados_json) or []
        # Identificar tests con desempeño bajo
        bajos = []
        for r in resultados:
            interp = (r.get("interpretacion") or "").lower()
            z = r.get("z_equivalente")
            try:
                z_num = float(z) if z is not None else None
            except (TypeError, ValueError):
                z_num = None
            es_bajo = (
                interp in ("bajo", "deficitario", "muy bajo", "limite")
                or (z_num is not None and z_num <= -1)
            )
            if es_bajo:
                bajos.append(r)

        # Sumar dominios afectados (los más frecuentes primero)
        dom_counts = Counter()
        for r in bajos:
            dom = _test_to_domain(r.get("test_id") or "")
            if dom:
                dom_counts[dom] += 1
        dominios_sugeridos = [d for d, _ in dom_counts.most_common()]

        # Buscar actividades del catálogo cuyo dominio esté en la lista
        actividades = []
        if dominios_sugeridos:
            cat = (
                self._db.query(RehabActivityCatalogORM)
                .filter(RehabActivityCatalogORM.dominio.in_(dominios_sugeridos))
                .filter(RehabActivityCatalogORM.activo.is_(True))
                .order_by(RehabActivityCatalogORM.orden.asc())
                .all()
            )
            for a in cat:
                actividades.append({
                    "slug":       a.slug,
                    "nombre":     a.nombre,
                    "dominio":    a.dominio,
                    "dificultad": a.dificultad_default,
                    "parametros": _parse_json(a.parametros_json) or {},
                })

        return {
            "evaluation_id":      evaluation_id,
            "patient_id":         ev.patient_id,
            "tests_bajos":        len(bajos),
            "dominios_sugeridos": dominios_sugeridos,
            "actividades":        actividades,
            "frecuencia_semanal_sugerida": 2 if not dominios_sugeridos else 3,
            "objetivos_sugerencia": _build_default_objectives(dominios_sugeridos),
        }


def _build_default_objectives(dominios: list[str]) -> str:
    """Texto editable por defecto para los objetivos del plan."""
    if not dominios:
        return ""
    labels = {
        "atencion":                "atención sostenida y selectiva",
        "memoria":                 "memoria episódica verbal y visual",
        "memoria_trabajo":         "memoria de trabajo y span atencional",
        "funciones_ejecutivas":    "control inhibitorio, flexibilidad y planificación",
        "lenguaje":                "fluidez y acceso lexical",
        "visoespacial":            "análisis y síntesis visoperceptual",
        "velocidad_procesamiento": "velocidad de procesamiento",
    }
    bullets = "; ".join(labels.get(d, d) for d in dominios)
    return (
        f"Intervención focalizada en {bullets}. "
        f"Trabajo combinado en consulta y tarea-casa, con "
        f"reevaluación a las 8 sesiones."
    )


def seed_activity_catalog(session) -> int:
    """
    Inserta las actividades por defecto si no existen. Idempotente.
    Devuelve cuántas actividades nuevas se insertaron.
    """
    from app.infrastructure.database.orm_models import RehabActivityCatalogORM

    inserted = 0
    for spec in DEFAULT_ACTIVITIES:
        exists = (
            session.query(RehabActivityCatalogORM)
            .filter_by(slug=spec["slug"])
            .first()
        )
        if exists:
            continue
        session.add(RehabActivityCatalogORM(
            id=str(uuid.uuid4()),
            slug=spec["slug"],
            nombre=spec["nombre"],
            dominio=spec["dominio"],
            dificultad_default=spec["dificultad_default"],
            duracion_min=spec["duracion_min"],
            descripcion=spec["descripcion"],
            instrucciones=spec["instrucciones"],
            parametros_json=json.dumps(spec["parametros_default"], ensure_ascii=False),
            provider=spec["provider"],
            external_url=None,
            activo=True,
            orden=spec["orden"],
        ))
        inserted += 1
    if inserted > 0:
        session.commit()
        logger.info("Catálogo de rehabilitación: %d actividades nuevas insertadas", inserted)
    return inserted
