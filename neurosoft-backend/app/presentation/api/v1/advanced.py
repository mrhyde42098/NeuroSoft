"""
app/presentation/api/v1/advanced.py
======================================
Funcionalidades avanzadas:

  GET  /advanced/hc/search          → Búsqueda dentro de Historias Clínicas
  GET  /advanced/hc/{pid}/versions  → Versiones históricas de una HC
  GET  /advanced/export/patients    → Exportar pacientes a CSV
  GET  /advanced/export/evaluations → Exportar evaluaciones a CSV
  POST /advanced/templates/suggest  → Sugerir texto para observaciones (IDx, recomendaciones)
  POST /advanced/config/profesionales/{id}/firma → Subir firma base64
"""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from app.application.dtos.clinical_history_dtos import SignatureUploadDTO
from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession

logger = logging.getLogger(__name__)
advanced_router = APIRouter(prefix="/advanced", tags=["Funcionalidades Avanzadas"])


# ─────────────────────────────────────────────────────────────
# 1. BÚSQUEDA EN HISTORIA CLÍNICA
# ─────────────────────────────────────────────────────────────

@advanced_router.get(
    "/hc/search",
    summary="Búsqueda avanzada en Historias Clínicas",
    description=(
        "Busca texto libre dentro de los campos de la Historia Clínica. "
        "Permite encontrar 'todos los pacientes con diagnóstico F84', "
        "'medicación risperidona', etc.\n\n"
        "**Campos buscados:** motivo_consulta, patologicos_medicos, psiquiatricos, "
        "farmacologicos, obs_impresion_dx, obs_recomendaciones, codigo_cie10, cualquier campo de texto."
    ),
)
def search_clinical_histories(
    q: str = Query(..., min_length=2, description="Texto a buscar"),
    campo: str | None = Query(
        default=None,
        description="Campo específico. Ej: farmacologicos, codigo_cie10. Vacío = todos."
    ),
    limit: int = Query(default=25, ge=1, le=100),
    db: DbSession = None,
):
    from sqlalchemy import or_

    from app.infrastructure.database.orm_models import ClinicalHistoryORM, PatientORM

    # Campos de texto que se buscarán
    TEXT_FIELDS = [
        "motivo_consulta", "patologicos_medicos", "sensoriales_motores",
        "psiquiatricos", "farmacologicos", "traumaticos", "quirurgicos",
        "toxicos", "alergicos", "terapeuticos", "paraclinicos", "familiares",
        "vive_con", "abc", "escolar_laboral", "cognitivo", "comportamiento_animo",
        "patron_sueno", "patron_alimentacion", "plan_atencion", "impresion_diagnostica_hc",
        "obs_clinica_general", "obs_atencion", "obs_memoria", "obs_praxias_gnosias",
        "obs_lenguaje", "obs_funciones_ejecutivas", "obs_emociones", "obs_ci",
        "obs_impresion_dx", "obs_funcionalidad", "obs_recomendaciones", "codigo_cie10",
    ]

    like = f"%{q}%"

    if campo and campo in TEXT_FIELDS:
        # Buscar en campo específico
        col = getattr(ClinicalHistoryORM, campo)
        hcs = db.query(ClinicalHistoryORM).filter(col.ilike(like)).limit(limit).all()
    else:
        # Buscar en todos los campos
        conditions = [
            getattr(ClinicalHistoryORM, f).ilike(like)
            for f in TEXT_FIELDS
        ]
        hcs = db.query(ClinicalHistoryORM).filter(or_(*conditions)).limit(limit).all()

    results = []
    for hc in hcs:
        patient = db.get(PatientORM, hc.patient_id)
        nombre = ""
        if patient:
            nombre = f"{patient.primer_nombre or ''} {patient.primer_apellido or ''}".strip()

        # Encontrar en qué campos aparece el término
        coincidencias = {}
        term_lower = q.lower()
        for f in TEXT_FIELDS:
            val = getattr(hc, f, "") or ""
            if term_lower in str(val).lower():
                # Extracto de contexto (50 chars antes y después)
                val_str = str(val)
                idx = val_str.lower().find(term_lower)
                start = max(0, idx - 40)
                end = min(len(val_str), idx + len(q) + 40)
                extracto = ("..." if start > 0 else "") + val_str[start:end] + ("..." if end < len(val_str) else "")
                coincidencias[f] = extracto

        results.append({
            "hc_id": hc.id,
            "patient_id": hc.patient_id,
            "nombre_paciente": nombre,
            "numero_documento": hc.numero_documento,
            "fecha_atencion": hc.fecha_atencion.isoformat() if hc.fecha_atencion else None,
            "codigo_cie10": hc.codigo_cie10,
            "coincidencias": coincidencias,
            "total_coincidencias": len(coincidencias),
        })

    return {
        "query": q,
        "campo_filtrado": campo,
        "total_resultados": len(results),
        "resultados": results,
    }


# ─────────────────────────────────────────────────────────────
# 2. VERSIONES HISTÓRICAS DE UNA HC
# ─────────────────────────────────────────────────────────────

@advanced_router.get(
    "/hc/{patient_id}/versions",
    summary="Historial de versiones de la Historia Clínica",
    description="Retorna todas las versiones guardadas de la HC, con fecha y quién la modificó.",
)
def get_hc_versions(patient_id: str, db: DbSession):
    from sqlalchemy import desc

    from app.infrastructure.database.orm_models import ClinicalHistoryORM, ClinicalHistoryVersionORM

    hc = (
        db.query(ClinicalHistoryORM)
        .filter_by(patient_id=patient_id)
        .first()
    )
    if hc is None:
        return {"patient_id": patient_id, "versiones": [], "version_actual": 0}

    versions = (
        db.query(ClinicalHistoryVersionORM)
        .filter_by(hc_id=hc.id)
        .order_by(desc(ClinicalHistoryVersionORM.version_num))
        .all()
    )

    return {
        "patient_id": patient_id,
        "hc_id": hc.id,
        "version_actual": getattr(hc, "row_version", 1),
        "versiones": [
            {
                "version_num": v.version_num,
                "saved_at": v.saved_at.isoformat() if v.saved_at else None,
                "saved_by": v.saved_by or "desconocido",
                "snapshot_disponible": bool(v.snapshot_json),
            }
            for v in versions
        ],
    }


@advanced_router.get(
    "/hc/{patient_id}/versions/{version_num}",
    summary="Ver snapshot de una versión específica de la HC",
)
def get_hc_version_snapshot(patient_id: str, version_num: int, db: DbSession):
    from app.infrastructure.database.orm_models import ClinicalHistoryORM, ClinicalHistoryVersionORM

    hc = db.query(ClinicalHistoryORM).filter_by(patient_id=patient_id).first()
    if hc is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="HC no encontrada.")

    ver = (
        db.query(ClinicalHistoryVersionORM)
        .filter_by(hc_id=hc.id, version_num=version_num)
        .first()
    )
    if ver is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Versión {version_num} no encontrada.")

    try:
        snapshot = json.loads(ver.snapshot_json)
    except Exception:
        snapshot = {}

    return {
        "hc_id": hc.id,
        "patient_id": patient_id,
        "version_num": ver.version_num,
        "saved_at": ver.saved_at.isoformat() if ver.saved_at else None,
        "saved_by": ver.saved_by,
        "snapshot": snapshot,
    }


# ─────────────────────────────────────────────────────────────
# 3. EXPORTAR A CSV
# ─────────────────────────────────────────────────────────────

@advanced_router.get(
    "/export/patients",
    response_class=Response,
    summary="Exportar listado de pacientes a CSV",
    responses={200: {"content": {"text/csv": {}}}},
)
def export_patients_csv(
    sexo: str | None = Query(default=None),
    poblacion: str | None = Query(default=None),
    fecha_desde: str | None = Query(default=None),
    fecha_hasta: str | None = Query(default=None),
    db: DbSession = None,
):
    from sqlalchemy import func

    from app.infrastructure.database.orm_models import EvaluationORM, PatientORM

    q = db.query(PatientORM).filter(PatientORM.is_active.is_(True))
    if sexo: q = q.filter(PatientORM.sexo == sexo)
    if fecha_desde: q = q.filter(PatientORM.fecha_atencion >= date.fromisoformat(fecha_desde))
    if fecha_hasta: q = q.filter(PatientORM.fecha_atencion <= date.fromisoformat(fecha_hasta))

    # Filtro por población (edad calculada)
    if poblacion:
        hoy = date.today()
        if poblacion == "infantil":
            q = q.filter(PatientORM.fecha_nacimiento > date(hoy.year-18, hoy.month, hoy.day))
        elif poblacion == "adulto_joven":
            q = q.filter(
                PatientORM.fecha_nacimiento <= date(hoy.year-18, hoy.month, hoy.day),
                PatientORM.fecha_nacimiento > date(hoy.year-50, hoy.month, hoy.day),
            )
        elif poblacion == "adulto_mayor":
            q = q.filter(PatientORM.fecha_nacimiento <= date(hoy.year-50, hoy.month, hoy.day))

    patients = q.order_by(PatientORM.primer_apellido, PatientORM.primer_nombre).all()

    # Conteo de evaluaciones por paciente
    eval_counts = {
        row[0]: row[1]
        for row in db.query(EvaluationORM.patient_id, func.count(EvaluationORM.id))
        .filter(EvaluationORM.patient_id.in_([p.id for p in patients]))
        .group_by(EvaluationORM.patient_id)
        .all()
    }

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Documento", "Tipo_Doc", "Nombre", "Apellido",
        "Fecha_Nacimiento", "Sexo", "Escolaridad", "Lateralidad",
        "Ciudad", "EPS", "Remite", "Fecha_Atencion", "Protocolo",
        "Evaluaciones", "Motivo_Consulta",
    ])

    for p in patients:
        writer.writerow([
            p.id, p.numero_documento, p.tipo_documento,
            f"{p.primer_nombre or ''} {p.segundo_nombre or ''}".strip(),
            f"{p.primer_apellido or ''} {p.segundo_apellido or ''}".strip(),
            p.fecha_nacimiento.isoformat() if p.fecha_nacimiento else "",
            "Masculino" if p.sexo == "H" else "Femenino",
            p.escolaridad or "",
            p.lateralidad or "",
            p.ciudad or "",
            p.eps or "",
            p.remite or "",
            p.fecha_atencion.isoformat() if p.fecha_atencion else "",
            p.protocolo or "",
            eval_counts.get(p.id, 0),
            (p.motivo_consulta or "")[:200],
        ])

    csv_bytes = output.getvalue().encode("utf-8-sig")  # BOM para Excel en Windows
    filename = f"neurosoft_pacientes_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@advanced_router.get(
    "/export/evaluations",
    response_class=Response,
    summary="Exportar resultados de evaluaciones a CSV",
    description="Incluye todos los escalares, Z-scores e interpretaciones de todas las evaluaciones.",
    responses={200: {"content": {"text/csv": {}}}},
)
def export_evaluations_csv(
    patient_id: str | None = Query(default=None, description="Filtrar por paciente"),
    protocolo: str | None = Query(default=None),
    fecha_desde: str | None = Query(default=None),
    fecha_hasta: str | None = Query(default=None),
    db: DbSession = None,
):
    from app.infrastructure.database.orm_models import EvaluationORM, PatientORM

    q = db.query(EvaluationORM).filter(EvaluationORM.is_latest.is_(True))
    if patient_id: q = q.filter(EvaluationORM.patient_id == patient_id)
    if protocolo:  q = q.filter(EvaluationORM.protocolo == protocolo)
    if fecha_desde: q = q.filter(EvaluationORM.fecha >= date.fromisoformat(fecha_desde))
    if fecha_hasta: q = q.filter(EvaluationORM.fecha <= date.fromisoformat(fecha_hasta))

    evals = q.order_by(EvaluationORM.fecha.desc()).all()

    # Collect all test IDs across all evaluations for column headers
    all_test_ids: list = []
    eval_data = []
    for ev in evals:
        try:
            resultados = json.loads(ev.resultados_json or "[]")
        except Exception:
            resultados = []
        for r in resultados:
            tid = r.get("test_id", "")
            if tid and tid not in all_test_ids:
                all_test_ids.append(tid)
        eval_data.append((ev, resultados))

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    base_cols = [
        "Eval_ID", "Patient_ID", "Documento", "Nombre_Paciente",
        "Fecha", "Protocolo", "Poblacion", "Edad_Display",
        "Pruebas_Realizadas",
    ]
    # For each test: PD, Escalar, Z, Interpretacion
    test_cols = []
    for tid in all_test_ids:
        test_cols += [f"{tid}_PD", f"{tid}_ES", f"{tid}_Z", f"{tid}_Nivel"]

    writer.writerow(base_cols + test_cols)

    # Data rows
    for ev, resultados in eval_data:
        patient = db.get(PatientORM, ev.patient_id)
        nombre = ""
        doc = ""
        if patient:
            nombre = f"{patient.primer_nombre or ''} {patient.primer_apellido or ''}".strip()
            doc = patient.numero_documento or ""

        # Index results by test_id
        res_by_id = {r.get("test_id"): r for r in resultados}

        base = [
            ev.id, ev.patient_id, doc, nombre,
            ev.fecha.isoformat() if ev.fecha else "",
            ev.protocolo or "",
            ev.poblacion or "",
            ev.edad_display or "",
            ev.pruebas_realizadas or 0,
        ]

        test_values = []
        for tid in all_test_ids:
            r = res_by_id.get(tid, {})
            pd_v = r.get("puntaje_bruto", "")
            es_v = r.get("puntaje_escalar", "")
            z_v  = r.get("z_equivalente", "")
            ni_v = r.get("interpretacion", "")
            # Don't export 9999 as PD
            if pd_v == 9999 or pd_v == 9999.0:
                pd_v = ""
            test_values += [pd_v, es_v, z_v, ni_v]

        writer.writerow(base + test_values)

    csv_bytes = output.getvalue().encode("utf-8-sig")
    filename = f"neurosoft_evaluaciones_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─────────────────────────────────────────────────────────────
# 4. PLANTILLAS DE OBSERVACIONES (sugerencia automática)
# ─────────────────────────────────────────────────────────────

@advanced_router.post(
    "/templates/suggest",
    summary="Sugerir texto para observaciones clínicas",
    description=(
        "Genera texto sugerido para los campos de observaciones clínicas "
        "basándose en el perfil Z de la última evaluación del paciente.\n\n"
        "Usa los `prompts_bajo`, `prompts_promedio` y `prompts_superior` "
        "definidos en `DOMAIN_DESCRIPTIONS` del motor clínico.\n\n"
        "El clínico puede usar estas sugerencias como punto de partida y editarlas."
    ),
)
def suggest_observation_text(
    patient_id: str,
    eval_id: str | None = None,
    db: DbSession = None,
):
    import json

    from sqlalchemy import desc

    from app.domain.clinical_engine.interpretation_engine import (
        DOMAIN_DESCRIPTIONS,
    )
    from app.infrastructure.database.orm_models import EvaluationORM

    # Buscar evaluación
    if eval_id:
        ev = db.get(EvaluationORM, eval_id)
    else:
        ev = (
            db.query(EvaluationORM)
            .filter(
                EvaluationORM.patient_id == patient_id,
                EvaluationORM.is_latest.is_(True),
            )
            .order_by(desc(EvaluationORM.fecha))
            .first()
        )

    if ev is None:
        return {
            "patient_id": patient_id,
            "eval_id": None,
            "sugerencias": {},
            "nota": "No se encontró evaluación. Las sugerencias requieren resultados previos.",
        }

    # Parsear resultados
    try:
        resultados = json.loads(ev.resultados_json or "[]")
    except Exception:
        resultados = []

    # Agrupar por dominio cognitivo
    dominios: dict = {}
    for r in resultados:
        if not r.get("fue_realizada", True):
            continue
        dominio = r.get("dominio_cognitivo", "")
        z = r.get("z_equivalente")
        if z is None:
            continue
        if dominio not in dominios:
            dominios[dominio] = []
        dominios[dominio].append(z)

    # Calcular Z promedio por dominio y seleccionar texto
    sugerencias = {}
    for dominio, z_vals in dominios.items():
        if not z_vals:
            continue
        z_prom = sum(z_vals) / len(z_vals)

        # Buscar en DOMAIN_DESCRIPTIONS
        desc_info = DOMAIN_DESCRIPTIONS.get(dominio, {})
        if not desc_info:
            # Buscar parcialmente
            for key in DOMAIN_DESCRIPTIONS:
                if any(word in dominio for word in key.split()):
                    desc_info = DOMAIN_DESCRIPTIONS[key]
                    break

        if not desc_info:
            continue

        if z_prom <= -1.0:
            texto = desc_info.get("prompts_bajo", "")
            nivel = "bajo"
        elif z_prom >= 1.0:
            texto = desc_info.get("prompts_superior", "")
            nivel = "superior"
        else:
            texto = desc_info.get("prompts_promedio", "")
            nivel = "promedio"

        if texto:
            sugerencias[dominio] = {
                "nivel": nivel,
                "z_promedio": round(z_prom, 2),
                "texto_sugerido": texto,
                "icono": desc_info.get("icono", "🧠"),
                "pruebas_representativas": desc_info.get("pruebas_representativas", []),
                "n_pruebas": len(z_vals),
            }

    # Generar texto de impresión diagnóstica compilado
    textos_bajos = [v["texto_sugerido"] for v in sugerencias.values() if v["nivel"] == "bajo"]
    textos_promedio = [v["texto_sugerido"] for v in sugerencias.values() if v["nivel"] == "promedio"]
    _textos_superiores = [v["texto_sugerido"] for v in sugerencias.values() if v["nivel"] == "superior"]

    impresion_compilada = ""
    if textos_bajos:
        impresion_compilada += " ".join(textos_bajos[:3])
    if textos_promedio:
        if impresion_compilada:
            impresion_compilada += " En los demás dominios, "
        impresion_compilada += textos_promedio[0]

    return {
        "patient_id": patient_id,
        "eval_id": ev.id,
        "protocolo": ev.protocolo,
        "fecha": ev.fecha.isoformat() if ev.fecha else None,
        "sugerencias_por_dominio": sugerencias,
        "impresion_dx_sugerida": impresion_compilada,
        "nota": (
            "Estos textos son sugerencias basadas en el perfil Z del paciente. "
            "El psicólogo debe revisarlos y personalizarlos según el caso clínico."
        ),
    }


# ─────────────────────────────────────────────────────────────
# 5. SUBIR FIRMA DEL PROFESIONAL (base64)
# ─────────────────────────────────────────────────────────────

@advanced_router.post(
    "/config/profesionales/{prof_id}/firma",
    summary="Subir imagen de firma digital del profesional",
    description=(
        "Guarda la firma del profesional como base64. "
        "El frontend convierte la imagen a base64 antes de enviarla. "
        "La firma aparece automáticamente en todos los informes PDF generados."
    ),
)
def upload_firma(
    prof_id: str,
    body: SignatureUploadDTO,
    request: Request,
    db: DbSession,
    admin=Depends(require_admin),
):
    """
    Guarda la firma del profesional.

    Sólo se aceptan imágenes raster (PNG, JPEG, GIF). SVG queda
    rechazado por riesgo de XSS almacenado. El tamaño máximo se
    controla con `settings.max_firma_kb`.
    """
    from app.core.config import settings
    from app.core.upload_validation import (
        UploadValidationError,
        validate_firma_base64,
    )
    from app.infrastructure.audit import record_event
    from app.infrastructure.database.orm_models import ProfessionalORM

    prof = db.get(ProfessionalORM, prof_id)
    if prof is None:
        raise HTTPException(status_code=404, detail="Profesional no encontrado.")

    try:
        raw = validate_firma_base64(
            body.firma_base64,
            max_bytes=settings.max_firma_kb * 1024,
        )
    except UploadValidationError as exc:
        raise HTTPException(exc.status_code, str(exc))

    # Persistimos la representación base64 "limpia" (sin prefijo data:)
    # para que el PDF la pueda incrustar sin tener que re-parsear.
    import base64 as _b64
    clean_b64 = _b64.b64encode(raw).decode("ascii")
    previous_present = bool(prof.firma_base64)

    prof.firma_base64 = clean_b64
    db.flush()

    actor_id = getattr(request.state, "user_id", None)
    record_event(
        db,
        action="update",
        entity_type="professional.firma",
        entity_id=prof_id,
        actor_id=actor_id,
        summary=(
            f"Firma actualizada ({len(raw)} bytes); "
            f"{'reemplaza firma previa' if previous_present else 'primera firma cargada'}"
        ),
        request=request,
        commit=False,
    )

    return {
        "id": prof.id,
        "nombre_completo": prof.nombre_completo,
        "firma_guardada": True,
        "tamaño_bytes": len(raw),
    }


@advanced_router.delete(
    "/config/profesionales/{prof_id}/firma",
    status_code=204,
    summary="Eliminar firma del profesional",
)
def delete_firma(prof_id: str, db: DbSession, admin=Depends(require_admin)):
    from fastapi import HTTPException

    from app.infrastructure.database.orm_models import ProfessionalORM
    prof = db.get(ProfessionalORM, prof_id)
    if prof is None:
        raise HTTPException(status_code=404, detail="Profesional no encontrado.")
    prof.firma_base64 = None
    db.flush()
