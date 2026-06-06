"""
app/presentation/api/v1/evaluations.py
=========================================
Endpoints para historial y detalle de evaluaciones.

Rutas:
    GET  /api/v1/evaluations/{patient_id}         — historial completo
    GET  /api/v1/evaluations/{patient_id}/latest  — última por protocolo
    GET  /api/v1/evaluations/detail/{eval_id}     — detalle con resultados
    GET  /api/v1/evaluations/{patient_id}/compare — comparación pre-post
    DELETE /api/v1/evaluations/detail/{eval_id}   — eliminar una evaluación
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from app.application.dtos.scoring_dtos import (
    EvaluationDetailDTO,
    PatientEvaluationsDTO,
    SignatureStatusDTO,
    SignEvaluationDTO,
)
from app.presentation.dependencies import (
    DbSession,
    EvaluationRepo,
    GetEvalDetailUC,
    GetEvalHistoryUC,
    GetSignatureUC,
    SignEvalUC,
)

evaluations_router = APIRouter(prefix="/evaluations", tags=["Evaluaciones"])


@evaluations_router.get(
    "/trend",
    summary="Tendencia mensual de evaluaciones (dashboard)",
    description=(
        "Devuelve el conteo de evaluaciones agrupado por mes durante los "
        "últimos N meses (default 6, máx 24). Útil para el gráfico de "
        "tendencia del dashboard."
    ),
)
def get_evaluations_trend(
    db: DbSession,
    meses: int = Query(6, ge=1, le=24, description="Número de meses hacia atrás (1-24)."),
):
    """
    Respuesta:
        [
          {"mes": "dic", "anio": 2025, "ym": "2025-12", "val": 16},
          {"mes": "ene", "anio": 2026, "ym": "2026-01", "val": 19},
          ...
        ]
    Garantiza que aparezcan los `meses` puntos consecutivos aunque el
    conteo del mes sea cero (sin huecos en el eje X).
    """
    from datetime import date

    from sqlalchemy import func

    from app.infrastructure.database.orm_models import EvaluationORM

    today = date.today()
    # Inicio = primer día del mes (today.month - meses + 1)
    start_year = today.year
    start_month = today.month - meses + 1
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    start = date(start_year, start_month, 1)

    rows = (
        db.query(
            func.strftime("%Y-%m", EvaluationORM.fecha).label("ym"),
            func.count(EvaluationORM.id).label("n"),
        )
        .filter(EvaluationORM.fecha >= start)
        .group_by("ym")
        .all()
    )
    counts = {ym: int(n) for ym, n in rows}

    _MES_ABBR = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

    out = []
    y, m = start_year, start_month
    for _ in range(meses):
        ym = f"{y:04d}-{m:02d}"
        out.append(
            {
                "mes": _MES_ABBR[m - 1],
                "anio": y,
                "ym": ym,
                "val": counts.get(ym, 0),
            }
        )
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


@evaluations_router.get(
    "/{patient_id}",
    response_model=PatientEvaluationsDTO,
    summary="Historial completo de evaluaciones de un paciente",
    description=(
        "Retorna todas las evaluaciones guardadas para el paciente, "
        "incluyendo versiones anteriores del mismo protocolo. "
        "Ordenadas por fecha descendente."
    ),
)
def get_evaluation_history(
    patient_id: str,
    uc: GetEvalHistoryUC,
):
    return uc.get_all(patient_id)


@evaluations_router.get(
    "/{patient_id}/latest",
    response_model=PatientEvaluationsDTO,
    summary="Última evaluación por protocolo",
    description=(
        "Retorna solo la evaluación más reciente de cada protocolo. Útil para el panel principal del paciente."
    ),
)
def get_latest_evaluations(
    patient_id: str,
    uc: GetEvalHistoryUC,
):
    return uc.get_latest(patient_id)


@evaluations_router.get(
    "/detail/{eval_id}",
    response_model=EvaluationDetailDTO,
    summary="Detalle completo de una evaluación",
    description=("Retorna todos los resultados calculados y puntajes brutos de una evaluación específica por su ID."),
)
def get_evaluation_detail(
    eval_id: str,
    uc: GetEvalDetailUC,
):
    return uc.execute(eval_id)


@evaluations_router.delete(
    "/detail/{eval_id}",
    status_code=204,
    summary="Eliminar una evaluación",
    description=(
        "Elimina una evaluación. **No aplica a evaluaciones firmadas**: una "
        "evaluación con firma digital (Res. 2654 MinSalud) no puede eliminarse "
        "— solo superponer con una nueva evaluación del mismo protocolo."
    ),
)
def delete_evaluation(
    eval_id: str,
    eval_repo: EvaluationRepo,
    db: DbSession,
):
    from app.core.exceptions import EvaluationAlreadySignedError
    from app.infrastructure.database.orm_models import EvaluationORM

    # Blindaje: no permitir borrar una evaluación firmada.
    orm = db.get(EvaluationORM, eval_id)
    if orm is not None and orm.signed_at is not None:
        raise HTTPException(
            status_code=409,
            detail=EvaluationAlreadySignedError(
                eval_id,
                signed_at=orm.signed_at.isoformat(),
            ).to_dict(),
        )
    eval_repo.delete(eval_id)


# ═══════════════════════════════════════════════════════════════
# WORKFLOW DE FIRMA CLÍNICA (Res. 2654 MinSalud)
# ═══════════════════════════════════════════════════════════════


@evaluations_router.post(
    "/detail/{eval_id}/sign",
    response_model=SignatureStatusDTO,
    summary="Firmar digitalmente una evaluación",
    description=(
        "Cierra la evaluación y la deja inmutable. Tras firmar, el hash SHA-256 "
        "del payload clínico queda registrado — si alguien altera la BD a mano "
        "el hash recalculado no coincide y la validación posterior (GET /signature) "
        "marca la firma como inválida. "
        "Requiere autenticación (el identificador del clínico se toma del JWT)."
    ),
)
def sign_evaluation(
    eval_id: str,
    body: SignEvaluationDTO,
    request: Request,
    uc: SignEvalUC,
):
    from app.core.exceptions import (
        EvaluationAlreadySignedError,
        EvaluationNotFoundError,
    )

    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail="Debe confirmar la firma con `confirm: true`.",
        )

    actor_id = getattr(request.state, "user_id", None)
    actor_label = getattr(request.state, "user_label", None)

    try:
        return uc.execute(
            evaluation_id=eval_id,
            actor_id=actor_id,
            actor_label=actor_label,
            note=body.note,
        )
    except EvaluationAlreadySignedError as e:
        raise HTTPException(status_code=409, detail=e.to_dict())
    except EvaluationNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())


@evaluations_router.get(
    "/detail/{eval_id}/signature",
    response_model=SignatureStatusDTO,
    summary="Estado de firma de una evaluación",
    description=(
        "Retorna si la evaluación está firmada, por quién y cuándo, y si el "
        "hash recalculado coincide con el almacenado (`valid: true/false`). "
        "Si `valid: false`, alguien alteró la BD y la firma ya no es confiable."
    ),
)
def get_signature_status(
    eval_id: str,
    uc: GetSignatureUC,
):
    from app.core.exceptions import EvaluationNotFoundError

    try:
        return uc.execute(eval_id)
    except EvaluationNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())


# ═══════════════════════════════════════════════════════════════
# COMPARACIÓN PRE–POST
# ═══════════════════════════════════════════════════════════════


@evaluations_router.get(
    "/{patient_id}/compare",
    summary="Comparación pre–post entre dos evaluaciones",
    description=(
        "Empareja los resultados de dos evaluaciones del mismo paciente y "
        "devuelve, por cada prueba presente en ambas, los puntajes PD, Z "
        "e interpretación, más la diferencia (delta_z, delta_pd). "
        "Útil para medir evolución clínica tras terapia."
    ),
)
def compare_evaluations(
    patient_id: str,
    eval_repo: EvaluationRepo,
    pre: str = Query(..., description="evaluation_id de la evaluación PRE"),
    post: str = Query(..., description="evaluation_id de la evaluación POST"),
):
    try:
        ev_pre = eval_repo.find_by_id(pre)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Evaluación PRE '{pre}' no encontrada.")
    try:
        ev_post = eval_repo.find_by_id(post)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Evaluación POST '{post}' no encontrada.")

    # Seguridad: ambas deben pertenecer al mismo paciente del path
    if ev_pre.patient_id != patient_id or ev_post.patient_id != patient_id:
        raise HTTPException(
            status_code=400,
            detail="Las evaluaciones no pertenecen al paciente indicado.",
        )

    def _index(ev) -> dict[str, dict[str, Any]]:
        idx: dict[str, dict[str, Any]] = {}
        for r in getattr(ev, "resultados", []) or []:
            # Puede venir como dict o como objeto; normalizamos
            if hasattr(r, "model_dump"):
                r = r.model_dump()
            elif not isinstance(r, dict):
                r = r.__dict__
            tid = r.get("test_id")
            if tid:
                idx[tid] = r
        return idx

    idx_pre = _index(ev_pre)
    idx_post = _index(ev_post)

    comunes = sorted(set(idx_pre.keys()) & set(idx_post.keys()))
    solo_pre = sorted(set(idx_pre.keys()) - set(idx_post.keys()))
    solo_post = sorted(set(idx_post.keys()) - set(idx_pre.keys()))

    def _fnum(x) -> float | None:
        if x is None or x == "":
            return None
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    tests: list[dict[str, Any]] = []
    for tid in comunes:
        a = idx_pre[tid]
        b = idx_post[tid]
        z_pre = _fnum(a.get("z_equivalente"))
        z_post = _fnum(b.get("z_equivalente"))
        pd_pre = _fnum(a.get("puntaje_bruto"))
        pd_post = _fnum(b.get("puntaje_bruto"))
        delta_z = (z_post - z_pre) if (z_pre is not None and z_post is not None) else None
        delta_pd = (pd_post - pd_pre) if (pd_pre is not None and pd_post is not None) else None

        # Etiqueta de cambio clínicamente relevante (>=0.5 z)
        if delta_z is None:
            cambio = "sin_dato"
        elif delta_z >= 0.5:
            cambio = "mejora"
        elif delta_z <= -0.5:
            cambio = "deterioro"
        else:
            cambio = "estable"

        tests.append(
            {
                "test_id": tid,
                "test_nombre": a.get("test_nombre") or b.get("test_nombre") or tid,
                "dominio_cognitivo": a.get("dominio_cognitivo") or b.get("dominio_cognitivo") or "",
                "pre": {
                    "puntaje_bruto": pd_pre,
                    "puntaje_escalar": _fnum(a.get("puntaje_escalar")),
                    "z": z_pre,
                    "interpretacion": a.get("interpretacion") or "",
                },
                "post": {
                    "puntaje_bruto": pd_post,
                    "puntaje_escalar": _fnum(b.get("puntaje_escalar")),
                    "z": z_post,
                    "interpretacion": b.get("interpretacion") or "",
                },
                "delta_z": round(delta_z, 3) if delta_z is not None else None,
                "delta_pd": round(delta_pd, 3) if delta_pd is not None else None,
                "cambio": cambio,
            }
        )

    # Ordenar por delta_z descendente (mejoras primero, deterioros al final)
    tests.sort(
        key=lambda t: (t["delta_z"] is None, -(t["delta_z"] or 0)),
    )

    # Agrupar por dominio para resumen
    dominios: dict[str, dict[str, int]] = {}
    for t in tests:
        dom = t["dominio_cognitivo"] or "Sin dominio"
        d = dominios.setdefault(dom, {"total": 0, "mejora": 0, "estable": 0, "deterioro": 0, "sin_dato": 0})
        d["total"] += 1
        d[t["cambio"]] += 1

    # Resumen general
    resumen = {
        "tests_comunes": len(comunes),
        "mejora": sum(1 for t in tests if t["cambio"] == "mejora"),
        "estable": sum(1 for t in tests if t["cambio"] == "estable"),
        "deterioro": sum(1 for t in tests if t["cambio"] == "deterioro"),
        "sin_dato": sum(1 for t in tests if t["cambio"] == "sin_dato"),
    }

    return {
        "patient_id": patient_id,
        "pre": {
            "evaluation_id": pre,
            "protocolo": getattr(ev_pre, "protocolo", None),
            "fecha": ev_pre.fecha.isoformat() if getattr(ev_pre, "fecha", None) else None,
            "edad_display": getattr(ev_pre, "edad_display", None),
            "pruebas_realizadas": len(idx_pre),
        },
        "post": {
            "evaluation_id": post,
            "protocolo": getattr(ev_post, "protocolo", None),
            "fecha": ev_post.fecha.isoformat() if getattr(ev_post, "fecha", None) else None,
            "edad_display": getattr(ev_post, "edad_display", None),
            "pruebas_realizadas": len(idx_post),
        },
        "solo_pre": solo_pre,
        "solo_post": solo_post,
        "resumen": resumen,
        "dominios": [{"nombre": k, **v} for k, v in dominios.items()],
        "tests": tests,
    }
