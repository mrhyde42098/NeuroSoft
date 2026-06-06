"""
app/presentation/api/v1/reports.py
=====================================
Endpoint de generación de informe PDF.

POST /api/v1/reports/pdf/{eval_id}
    Genera el PDF completo a partir de una evaluación guardada.
    Combina: paciente + historia clínica + resultados + config institucional.
    Retorna el archivo PDF directamente (Content-Type: application/pdf).

GET /api/v1/reports/preview/{eval_id}
    Devuelve la data estructurada del informe (sin generar PDF).
    Útil para el frontend antes de descargar.
"""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.core.exceptions import EvaluationNotFoundError
from app.presentation.api.v1.auth import CurrentUser, get_evaluation_for_user
from app.presentation.dependencies import (
    DbSession,
    EvaluationRepo,
    PatientRepo,
)

logger = logging.getLogger(__name__)


def _find_evaluation(eval_repo: EvaluationRepo, eval_id: str):
    try:
        return eval_repo.find_by_id(eval_id)
    except EvaluationNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluación '{eval_id}' no encontrada.",
        ) from None

reports_router = APIRouter(prefix="/reports", tags=["Informes PDF"])


@reports_router.post(
    "/pdf/{eval_id}",
    response_class=Response,
    summary="Generar informe PDF de una evaluación",
    description=(
        "Genera el informe de evaluación neuropsicológica en PDF. "
        "Combina datos del paciente, historia clínica, observaciones clínicas "
        "y resultados de la evaluación especificada.\n\n"
        "**Requiere:** `reportlab` instalado (`pip install reportlab`).\n\n"
        "Retorna el archivo PDF directamente para descarga."
    ),
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF del informe generado exitosamente.",
        },
        404: {"description": "Evaluación o paciente no encontrado."},
        500: {"description": "Error generando el PDF (reportlab no instalado?)."},
    },
)
def generate_pdf(
    eval_id: str,
    eval_repo: EvaluationRepo,
    patient_repo: PatientRepo,
    db: DbSession,
    user=CurrentUser,
    template: Literal[
        "estandar", "pro", "pediatrico",
        "medicolegal", "junta_medica", "inconcluso",
        "therapy_closure", "paciente",
    ] = Query(
        "pro",
        description=(
            "Variante de plantilla del informe: 'pro' (estándar IN&S+Pro), "
            "'estandar' (legacy histórica), 'pediatrico', 'medicolegal', "
            "'junta_medica' (2 págs), 'inconcluso', "
            "'therapy_closure' (cierre de proceso terapéutico), "
            "'paciente' (lenguaje claro para el paciente y su familia)."
        ),
    ),
    therapy_plan_id: str | None = Query(
        default=None,
        description="UUID del plan terapéutico (solo template therapy_closure)",
    ),
):
    from app.infrastructure.database.orm_models import (
        ClinicalHistoryORM,
        ObservationORM,
        PatientORM,
        ProfessionalORM,
    )
    from app.infrastructure.report_service import (
        build_report_data_from_db,
        generate_report_pdf,
    )

    get_evaluation_for_user(eval_id, db, user)
    ev = _find_evaluation(eval_repo, eval_id)

    # 2. Paciente (ORM directo para tener todos los campos)
    patient_orm = db.get(PatientORM, ev.patient_id)
    if patient_orm is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    # 3. Historia clínica (opcional)
    hc = (
        db.query(ClinicalHistoryORM)
        .filter(ClinicalHistoryORM.patient_id == ev.patient_id)
        .order_by(ClinicalHistoryORM.fecha_atencion.desc())
        .first()
    )

    # 4. Observaciones de la tabla observations (complementa HC si vacía)
    obs_list = (
        db.query(ObservationORM)
        .filter_by(patient_id=ev.patient_id, evaluation_id=eval_id)
        .all()
    )
    observations_dict = {o.dominio: o.texto for o in obs_list} if obs_list else {}

    # 5. Configuración institucional (singleton)
    institucion = _get_or_default_institucion(db)

    # 6. Profesional asignado al paciente
    profesional = None
    if patient_orm.profesional_id:
        profesional = db.get(ProfessionalORM, patient_orm.profesional_id)

    # 7. Construir ReportData
    report_data = build_report_data_from_db(
        patient=patient_orm,
        clinical_history=hc,
        evaluation_record=ev,
        institucion=institucion,
        profesional=profesional,
        observations=observations_dict,
        db=db,
        therapy_plan_id=therapy_plan_id,
        include_therapy=(template == "therapy_closure"),
    )

    # 7. Generar PDF (con plantilla seleccionada)
    try:
        pdf_bytes = generate_report_pdf(report_data, template=template)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(
            "Error generando PDF para eval_id=%s con template=%s", eval_id, template,
        )
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}")

    # 8. Nombre del archivo
    nombre = (
        f"InformeNPS_{patient_orm.primer_apellido or ''}"
        f"_{patient_orm.numero_documento}"
        f"_{patient_orm.fecha_atencion.strftime('%Y%m%d') if patient_orm.fecha_atencion else 'sin_fecha'}"
        ".pdf"
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@reports_router.post(
    "/docx/{eval_id}",
    response_class=Response,
    summary="Generar informe DOCX editable",
    description=(
        "Genera el informe de evaluación neuropsicológica en formato Word "
        "(.docx) editable por el profesional antes de firmarlo/imprimirlo.\n\n"
        "**Requiere:** `python-docx` instalado (`pip install python-docx`)."
    ),
)
def generate_docx(
    eval_id: str,
    eval_repo: EvaluationRepo,
    patient_repo: PatientRepo,
    db: DbSession,
    user=CurrentUser,
):
    from app.infrastructure.database.orm_models import (
        ClinicalHistoryORM,
        ObservationORM,
        PatientORM,
        ProfessionalORM,
    )
    from app.infrastructure.export_service import generate_report_docx
    from app.infrastructure.report_service import build_report_data_from_db

    get_evaluation_for_user(eval_id, db, user)
    ev = _find_evaluation(eval_repo, eval_id)

    patient_orm = db.get(PatientORM, ev.patient_id)
    if patient_orm is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    hc = (
        db.query(ClinicalHistoryORM)
        .filter(ClinicalHistoryORM.patient_id == ev.patient_id)
        .order_by(ClinicalHistoryORM.fecha_atencion.desc())
        .first()
    )

    obs_list = (
        db.query(ObservationORM)
        .filter_by(patient_id=ev.patient_id, evaluation_id=eval_id)
        .all()
    )
    observations_dict = {o.dominio: o.texto for o in obs_list} if obs_list else {}

    institucion = _get_or_default_institucion(db)

    profesional = None
    if patient_orm.profesional_id:
        profesional = db.get(ProfessionalORM, patient_orm.profesional_id)

    report_data = build_report_data_from_db(
        patient=patient_orm,
        clinical_history=hc,
        evaluation_record=ev,
        institucion=institucion,
        profesional=profesional,
        observations=observations_dict,
    )

    try:
        docx_bytes = generate_report_docx(report_data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Error generando DOCX para eval_id=%s", eval_id)
        raise HTTPException(status_code=500, detail=f"Error generando DOCX: {e}")

    nombre = (
        f"InformeNPS_{patient_orm.primer_apellido or ''}"
        f"_{patient_orm.numero_documento}"
        f"_{ev.fecha.strftime('%Y%m%d') if getattr(ev, 'fecha', None) else 'sin_fecha'}"
        ".docx"
    )

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Content-Length": str(len(docx_bytes)),
        },
    )


@reports_router.post(
    "/xlsx/{eval_id}",
    response_class=Response,
    summary="Generar matriz de puntajes en Excel",
    description=(
        "Genera un XLSX con dos hojas:\n"
        "- Resumen: datos del paciente y protocolo.\n"
        "- Puntajes: una fila por prueba con PD, PE, Z e interpretación.\n\n"
        "**Requiere:** `openpyxl` instalado."
    ),
)
def generate_xlsx(
    eval_id: str,
    eval_repo: EvaluationRepo,
    patient_repo: PatientRepo,
    db: DbSession,
    user=CurrentUser,
):
    from app.infrastructure.database.orm_models import (
        ClinicalHistoryORM,
        ObservationORM,
        PatientORM,
        ProfessionalORM,
    )
    from app.infrastructure.export_service import generate_evaluation_xlsx
    from app.infrastructure.report_service import build_report_data_from_db

    get_evaluation_for_user(eval_id, db, user)
    ev = _find_evaluation(eval_repo, eval_id)

    patient_orm = db.get(PatientORM, ev.patient_id)
    if patient_orm is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    hc = (
        db.query(ClinicalHistoryORM)
        .filter(ClinicalHistoryORM.patient_id == ev.patient_id)
        .order_by(ClinicalHistoryORM.fecha_atencion.desc())
        .first()
    )

    obs_list = (
        db.query(ObservationORM)
        .filter_by(patient_id=ev.patient_id, evaluation_id=eval_id)
        .all()
    )
    observations_dict = {o.dominio: o.texto for o in obs_list} if obs_list else {}

    institucion = _get_or_default_institucion(db)

    profesional = None
    if patient_orm.profesional_id:
        profesional = db.get(ProfessionalORM, patient_orm.profesional_id)

    report_data = build_report_data_from_db(
        patient=patient_orm,
        clinical_history=hc,
        evaluation_record=ev,
        institucion=institucion,
        profesional=profesional,
        observations=observations_dict,
    )

    try:
        xlsx_bytes = generate_evaluation_xlsx(report_data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Error generando XLSX para eval_id=%s", eval_id)
        raise HTTPException(status_code=500, detail=f"Error generando XLSX: {e}")

    nombre = (
        f"Puntajes_{patient_orm.primer_apellido or ''}"
        f"_{patient_orm.numero_documento}"
        f"_{ev.fecha.strftime('%Y%m%d') if getattr(ev, 'fecha', None) else 'sin_fecha'}"
        ".xlsx"
    )

    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Content-Length": str(len(xlsx_bytes)),
        },
    )


@reports_router.get(
    "/preview/{eval_id}",
    summary="Vista previa de datos del informe (sin generar PDF)",
    description="Retorna la estructura de datos que se usará para generar el informe.",
)
def preview_report_data(
    eval_id: str,
    eval_repo: EvaluationRepo,
    patient_repo: PatientRepo,
    db: DbSession,
    user=CurrentUser,
):
    from app.infrastructure.database.orm_models import (
        ClinicalHistoryORM,
        ObservationORM,
        PatientORM,
        ProfessionalORM,
    )

    get_evaluation_for_user(eval_id, db, user)
    ev = _find_evaluation(eval_repo, eval_id)

    patient_orm = db.get(PatientORM, ev.patient_id)
    if not patient_orm:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    hc = (
        db.query(ClinicalHistoryORM)
        .filter(ClinicalHistoryORM.patient_id == ev.patient_id)
        .first()
    )

    # Profesional asignado → firma disponible?
    tiene_firma = False
    if patient_orm.profesional_id:
        prof = db.get(ProfessionalORM, patient_orm.profesional_id)
        tiene_firma = bool(prof and prof.firma_base64 and prof.firma_base64.strip())

    # §M-5: cálculo detallado de completitud por sección
    tiene_hc = hc is not None
    tiene_motivo = bool(hc and (hc.motivo_consulta or "").strip())
    tiene_antecedentes = bool(hc and any((getattr(hc, f, "") or "").strip() for f in [
        "antecedentes_personales", "antecedentes_familiares",
        "antecedentes_psiquiatricos", "farmacos_actuales",
    ]))
    tiene_obs = bool(
        (hc and hc.obs_clinica_general not in (None, "", "N/A"))
        or db.query(ObservationORM.id).filter(ObservationORM.patient_id == ev.patient_id).first()
    )

    # Conteo de observaciones por dominio cognitivo (de las pruebas aplicadas).
    obs_por_dominio = (
        db.query(ObservationORM.dominio_cognitivo)
        .filter(ObservationORM.patient_id == ev.patient_id)
        .distinct().all()
    )
    dominios_con_obs = {d[0] for d in obs_por_dominio if d[0]}
    dominios_evaluados = {r.dominio_cognitivo for r in (ev.resultados or []) if r.dominio_cognitivo}
    dominios_sin_obs = dominios_evaluados - dominios_con_obs

    # Reglas de bloqueo (CRÍTICO no puede faltar para descargar)
    bloqueos = []
    if not tiene_hc: bloqueos.append("Falta Historia Clínica")
    if not ev.resultados or len(ev.resultados) == 0:
        bloqueos.append("La evaluación no tiene resultados registrados")
    if not tiene_firma:
        bloqueos.append("Profesional sin firma cargada (Ajustes → Profesionales)")

    # Reglas de advertencia (no bloquean pero se muestran)
    advertencias_completitud = []
    if not tiene_motivo: advertencias_completitud.append("HC sin motivo de consulta")
    if not tiene_antecedentes: advertencias_completitud.append("HC sin antecedentes")
    if not tiene_obs: advertencias_completitud.append("Sin observaciones clínicas")
    if dominios_sin_obs:
        advertencias_completitud.append(
            f"{len(dominios_sin_obs)} dominios sin observación: {', '.join(sorted(dominios_sin_obs))[:120]}"
        )

    secciones = [
        {"id": "hc", "label": "Historia clínica", "ok": tiene_hc, "critico": True},
        {"id": "motivo", "label": "Motivo de consulta", "ok": tiene_motivo, "critico": False},
        {"id": "antecedentes", "label": "Antecedentes", "ok": tiene_antecedentes, "critico": False},
        {"id": "resultados", "label": f"Resultados ({len(ev.resultados or [])})", "ok": bool(ev.resultados), "critico": True},
        {"id": "observaciones", "label": "Observaciones clínicas",
         "ok": tiene_obs, "critico": False,
         "detalle": f"{len(dominios_con_obs)}/{len(dominios_evaluados)} dominios" if dominios_evaluados else None},
        {"id": "firma", "label": "Firma del profesional", "ok": tiene_firma, "critico": True},
    ]
    completitud_pct = round(100 * sum(1 for s in secciones if s["ok"]) / len(secciones))

    return {
        "eval_id": eval_id,
        "patient_id": ev.patient_id,
        "nombre_completo": f"{patient_orm.primer_nombre} {patient_orm.primer_apellido}",
        "protocolo": ev.protocolo,
        "fecha": ev.fecha.isoformat() if ev.fecha else None,
        "poblacion": ev.poblacion,
        "pruebas_realizadas": ev.pruebas_realizadas,
        "tiene_historia_clinica": tiene_hc,
        "tiene_observaciones": tiene_obs,
        "tiene_firma": tiene_firma,
        "resultados_count": len(ev.resultados),
        "puntos_debiles": ev.puntos_debiles,
        "puntos_fuertes": ev.puntos_fuertes,
        "advertencias": ev.advertencias,
        # §M-5: nuevos campos de completitud
        "secciones": secciones,
        "completitud_pct": completitud_pct,
        "bloqueos": bloqueos,           # impiden descargar (a menos que se use plantilla 'inconcluso')
        "puede_descargar": len(bloqueos) == 0,
        "advertencias_completitud": advertencias_completitud,
        "dominios_evaluados": sorted(dominios_evaluados),
        "dominios_con_obs": sorted(dominios_con_obs),
        "dominios_sin_obs": sorted(dominios_sin_obs),
    }


@reports_router.get(
    "/enrichment/{eval_id}",
    summary="Enriquecimiento clínico del informe",
    description=(
        "Retorna recomendaciones del reservorio institucional, batería alterna "
        "sugerida y advertencias heredadas para una evaluación concreta. "
        "Resuelve automáticamente el grupo etario por fecha de nacimiento y el "
        "cuadro clínico a partir del CIE-10 registrado en paciente o HC."
    ),
)
def get_report_enrichment(
    eval_id: str,
    eval_repo: EvaluationRepo,
    db: DbSession,
    user=CurrentUser,
):
    from app.application.use_cases.report_enrichment import (
        build_report_enrichment,
    )
    from app.infrastructure.database.orm_models import (
        ClinicalHistoryORM,
        PatientORM,
    )

    get_evaluation_for_user(eval_id, db, user)
    ev = _find_evaluation(eval_repo, eval_id)

    patient_orm = db.get(PatientORM, ev.patient_id)
    if not patient_orm:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    hc = (
        db.query(ClinicalHistoryORM)
        .filter(ClinicalHistoryORM.patient_id == ev.patient_id)
        .order_by(ClinicalHistoryORM.fecha_atencion.desc())
        .first()
    )

    # Preferir CIE-10 de HC (más clínico); fallback a codigo_rips del paciente
    cie10 = None
    if hc and hc.codigo_cie10:
        cie10 = hc.codigo_cie10
    elif patient_orm.codigo_rips:
        cie10 = patient_orm.codigo_rips

    # Extraer resultados de pruebas para detección de patrones cognitivos
    resultados_pruebas = None
    try:
        resultados_raw = ev.resultados or []
        if isinstance(resultados_raw, list) and resultados_raw:
            resultados_pruebas = [
                {
                    "nombre_prueba": r.get("nombre_prueba", ""),
                    "test_id":       r.get("test_id", ""),
                    "puntaje_escalar": r.get("puntaje_escalar"),
                }
                for r in resultados_raw
                if isinstance(r, dict)
            ]
    except Exception:
        pass  # No es crítico — el enriquecimiento funciona sin resultados

    result = build_report_enrichment(
        eval_id=eval_id,
        patient_id=ev.patient_id,
        fecha_nacimiento=patient_orm.fecha_nacimiento,
        codigo_cie10=cie10,
        discapacidad=patient_orm.discapacidad,
        advertencias=list(ev.advertencias or []),
        resultados_pruebas=resultados_pruebas,
    )
    return result.as_dict()


# ─────────────────────────────────────────────────────────────
# Helper: configuración institucional con defaults
# ─────────────────────────────────────────────────────────────

def _get_or_default_institucion(db):
    """Retorna la configuración institucional o un objeto con defaults."""
    try:
        from app.infrastructure.database.orm_models import ConfigInstitucionORM
        inst = db.query(ConfigInstitucionORM).first()
        if inst:
            return inst
    except (ImportError, AttributeError) as _cfg_exc:
        # ORM no cargado o BD aún sin tabla — devolvemos defaults sin ruido.
        # SQLAlchemy OperationalError no entra aquí: preferimos que se propague
        # para detectar BDs corruptas en el endpoint que genera informes.
        import logging as _logging
        _logging.getLogger(__name__).debug(
            "ConfigInstitucionORM no disponible: %s", _cfg_exc,
        )

    class _DefaultInstitucion:
        nombre     = "Consultorio Neuropsicológico"
        nit        = ""
        direccion  = ""
        telefono   = ""
        email      = ""
        logo_base64 = None

    return _DefaultInstitucion()
