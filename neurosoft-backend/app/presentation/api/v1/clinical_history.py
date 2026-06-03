"""
app/presentation/api/v1/clinical_history.py
=============================================
Endpoints: Historia Clínica, Observaciones, Evolución Terapia,
Configuración, Documentos, Backup, Guía de Pruebas, CIE-10.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.dtos.clinical_history_dtos import (
    BackupRequestDTO,
    BackupResponseDTO,
    ClinicalHistoryResponseDTO,
    ClinicalHistoryUpsertDTO,
    ComprobanteAsistenciaDTO,
    ConfigCompleteResponseDTO,
    ConfigInstitucionDTO,
    ConfigPrefsInformeDTO,
    DocumentoResponseDTO,
    EvolTerapiaCreateDTO,
    EvolTerapiaResponseDTO,
    ProfessionalCreateDTO,
    ProfessionalResponseDTO,
    RemisionDTO,
)
from app.application.use_cases.clinical_history_use_cases import (
    BackupUseCase,
    CreateEvolTerapiaUseCase,
    GenerateDocumentUseCase,
    GetClinicalHistoryUseCase,
    GetConfigUseCase,
    GetEvolTerapiaUseCase,
    GetInterpretationSuggestionsUseCase,
    ManageProfessionalUseCase,
    UpdateConfigInstitucionUseCase,
    UpdateConfigPrefsUseCase,
    UpsertClinicalHistoryUseCase,
)
from app.core.exceptions import ApplicationError, PatientNotFoundError
from app.domain.clinical_engine.test_guide import (
    PROTOCOLOS_DISPONIBLES,
    TEST_GUIDE,
    get_protocol_tests,
)
from app.domain.entities.configuration import (
    CIE10_NEUROPSICOLOGIA,
    get_cie10_categorias,
)
from app.infrastructure.database.engine import get_session
from app.presentation.api.v1.auth import require_admin


def _db():
    yield from get_session()


def _handle(e: Exception):
    if isinstance(e, PatientNotFoundError):
        raise HTTPException(404, detail=e.to_dict())
    if isinstance(e, ApplicationError):
        raise HTTPException(422, detail=e.to_dict())
    raise e


# ═══════════════════════════════════════════════════════════════
# HISTORIA CLÍNICA
# ═══════════════════════════════════════════════════════════════

hc_router = APIRouter(prefix="/clinical-history", tags=["Historia Clínica"])


@hc_router.post("/", response_model=ClinicalHistoryResponseDTO,
                status_code=status.HTTP_201_CREATED,
                summary="Crear o actualizar Historia Clínica",
                description="Upsert completo de la HC. Las 4 pestañas + observaciones clínicas.")
def upsert_clinical_history(
    dto: ClinicalHistoryUpsertDTO,
    db: Session = Depends(get_session),
):
    try:
        return UpsertClinicalHistoryUseCase(db).execute(dto)
    except Exception as e:
        _handle(e)


@hc_router.get("/{patient_id}", response_model=Optional[ClinicalHistoryResponseDTO],
               summary="Obtener Historia Clínica de un paciente")
def get_clinical_history(patient_id: str, db: Session = Depends(get_session)):
    return GetClinicalHistoryUseCase(db).by_patient(patient_id)


@hc_router.get("/{patient_id}/pdf",
               summary="§QW-4 Generar PDF de la Historia Clínica completa",
               description=(
                   "Genera un PDF imprimible con la HC + datos sociodemográficos del paciente. "
                   "No requiere evaluación previa — útil para EPS/IPS que piden HC sola."
               ))
def generate_hc_pdf(patient_id: str, db: Session = Depends(get_session)):
    """§QW-4: PDF de HC sola (sin evaluación). ReportLab inline."""
    from fastapi.responses import Response

    from app.infrastructure.database.orm_models import (
        ClinicalHistoryORM,
        ConfigInstitucionORM,
        PatientORM,
        ProfessionalORM,
    )
    from app.infrastructure.hc_pdf_service import generate_clinical_history_pdf

    pat = db.get(PatientORM, patient_id)
    if not pat:
        raise HTTPException(404, detail="Paciente no encontrado.")
    hc = (db.query(ClinicalHistoryORM)
          .filter(ClinicalHistoryORM.patient_id == patient_id)
          .order_by(ClinicalHistoryORM.fecha_atencion.desc())
          .first())
    inst = db.query(ConfigInstitucionORM).first()
    prof = db.get(ProfessionalORM, pat.profesional_id) if pat.profesional_id else None

    pdf_bytes = generate_clinical_history_pdf(
        patient=pat, clinical_history=hc, institucion=inst, profesional=prof,
    )
    filename = (
        f"HistoriaClinica_{(pat.primer_apellido or '').strip()}"
        f"_{pat.numero_documento or patient_id[:8]}.pdf"
    ).replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@hc_router.get("/{patient_id}/interpretation",
               summary="Sugerencias de interpretación por dominio cognitivo",
               description=(
                   "Analiza los resultados de la última evaluación y devuelve: "
                   "perfiles por dominio, texto sugerido, datos de la gráfica Z y resumen de CI."
               ))
def get_interpretation_suggestions(
    patient_id: str,
    evaluation_id: str | None = Query(default=None),
    db: Session = Depends(get_session),
):
    from app.infrastructure.database.orm_models import EvaluationORM

    if not evaluation_id:
        ev = (db.query(EvaluationORM)
              .filter_by(patient_id=patient_id)
              .order_by(EvaluationORM.created_at.desc())
              .first())
        if not ev:
            return {"profiles": [], "z_chart": [], "ci_summary": None}
        evaluation_id = ev.id

    return GetInterpretationSuggestionsUseCase(db).execute(evaluation_id)


# ═══════════════════════════════════════════════════════════════
# EVOLUCIÓN TERAPIA NPS
# ═══════════════════════════════════════════════════════════════

evol_router = APIRouter(prefix="/evolucion", tags=["Evolución Terapia NPs"])


@evol_router.post("/", response_model=EvolTerapiaResponseDTO,
                  status_code=201,
                  summary="Registrar sesión de evolución terapéutica")
def create_evolucion(dto: EvolTerapiaCreateDTO, db: Session = Depends(get_session)):
    try:
        return CreateEvolTerapiaUseCase(db).execute(dto)
    except Exception as e:
        _handle(e)


@evol_router.get("/{patient_id}", response_model=list[EvolTerapiaResponseDTO],
                 summary="Historial de sesiones de un paciente")
def get_evolucion(patient_id: str, db: Session = Depends(get_session)):
    return GetEvolTerapiaUseCase(db).by_patient(patient_id)


# ═══════════════════════════════════════════════════════════════
# GUÍA DE ADMINISTRACIÓN DE PRUEBAS
# ═══════════════════════════════════════════════════════════════

guide_router = APIRouter(prefix="/test-guide", tags=["Guía de Pruebas"])


@guide_router.get("/protocols",
                  summary="Protocolos clínicos disponibles",
                  description="Lista los 19 protocolos del sistema con sus pruebas asociadas.")
def list_protocols():
    return PROTOCOLOS_DISPONIBLES


@guide_router.get("/protocols/{protocol_id}",
                  summary="Pruebas de un protocolo en orden de administración")
def get_protocol(
    protocol_id: str,
    include_optional: bool = Query(default=False),
):
    protocol_names = {p["id"]: p["nombre"] for p in PROTOCOLOS_DISPONIBLES}
    if protocol_id not in protocol_names:
        raise HTTPException(404, detail=f"Protocolo '{protocol_id}' no encontrado.")

    # Map protocol id to protocol_principal name
    id_to_name = {
        "wisc_ci": "WISC-IV", "wisc_perfil": "WISC-IV", "wisc_tea": "WISC-IV",
        "kabc_ci": "KABC-II", "ead": "EAD",
        "wais_ci": "WAIS-III", "wais_perfil_adulto": "WAIS-III",
        "adulto_mayor": "Adulto Mayor",
    }
    protocol_name = id_to_name.get(protocol_id, "WISC-IV")
    tests = get_protocol_tests(protocol_name, include_optional)

    return {
        "id": protocol_id,
        "nombre": protocol_names[protocol_id],
        "pruebas": [
            {
                "test_id": t.test_id,
                "nombre": t.nombre_display,
                "nombre_completo": t.nombre_prueba_completa,
                "dominio": t.dominio,
                "orden": t.orden_protocolo,
                "tiempo_limite_seg": t.tiempo_limite_seg,
                "max_pd": t.max_pd,
                "min_pd": t.min_pd,
                "tipo_respuesta": t.tipo_respuesta,
                "instruccion_corta": t.instruccion_corta,
                "tips_clinicos": t.tips_clinicos,
                "materiales": t.materiales,
                "criterios_discontinuacion": t.criterios_discontinuacion,
                "es_opcional": t.es_opcional,
            }
            for t in tests
        ]
    }


@guide_router.get("/tests/{test_id}",
                  summary="Información de administración de una prueba")
def get_test_info(test_id: str):
    info = TEST_GUIDE.get(test_id)
    if not info:
        return {"test_id": test_id, "info": "No disponible en guía"}
    return {
        "test_id": info.test_id,
        "nombre": info.nombre_display,
        "dominio": info.dominio,
        "tiempo_limite_seg": info.tiempo_limite_seg,
        "max_pd": info.max_pd,
        "instruccion_corta": info.instruccion_corta,
        "tips_clinicos": info.tips_clinicos,
        "materiales": info.materiales,
        "criterios_discontinuacion": info.criterios_discontinuacion,
    }


# ═══════════════════════════════════════════════════════════════
# CIE-10
# ═══════════════════════════════════════════════════════════════

cie10_router = APIRouter(prefix="/cie10", tags=["CIE-10"])


@cie10_router.get("/",
                  summary="Catálogo CIE-10 neuropsicología",
                  description="Todos los códigos CIE-10 relevantes para neuropsicología.")
def list_cie10(
    buscar: str | None = Query(default=None, description="Filtrar por código o descripción"),
    categoria: str | None = Query(default=None, description="Filtrar por rango (ej. F00-F09, F80-F89, G30-G32)"),
    limit: int = Query(default=200, ge=1, le=1000, description="Máximo de resultados"),
):
    data = CIE10_NEUROPSICOLOGIA
    if categoria:
        cat = categoria.strip().upper()
        data = [c for c in data if str(c.get("categoria", "")).upper() == cat]
    if buscar:
        b = buscar.strip().upper()
        data = [
            c for c in data
            if b in c["codigo"].upper() or b in c["descripcion"].upper()
        ]
    # Ordenar por código (estable y predecible)
    data = sorted(data, key=lambda c: c["codigo"])
    return data[:limit]


@cie10_router.get("/categorias",
                  summary="Categorías/rangos CIE-10",
                  description="Agrupaciones CIE-10 (ej. F00-F09 → Trastornos orgánicos…)")
def list_cie10_categorias():
    cats = get_cie10_categorias()
    return [{"rango": k, "nombre": v} for k, v in cats.items()]


# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

config_router = APIRouter(prefix="/config", tags=["Configuración"])


@config_router.get("/", response_model=ConfigCompleteResponseDTO,
                   summary="Obtener configuración completa del sistema")
def get_config(db: Session = Depends(get_session)):
    return GetConfigUseCase(db).execute()


@config_router.put("/institucion", response_model=ConfigInstitucionDTO,
                   summary="Actualizar datos de la institución")
def update_institucion(
    dto: ConfigInstitucionDTO,
    db: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    return UpdateConfigInstitucionUseCase(db).execute(dto)


@config_router.put("/prefs-informe", response_model=ConfigPrefsInformeDTO,
                   summary="Actualizar preferencias visuales del informe")
def update_prefs(
    dto: ConfigPrefsInformeDTO,
    db: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    return UpdateConfigPrefsUseCase(db).execute(dto)


@config_router.get("/profesionales", response_model=list[ProfessionalResponseDTO],
                   summary="Listar todos los profesionales")
def list_professionals(db: Session = Depends(get_session)):
    return ManageProfessionalUseCase(db).list_all()


@config_router.post("/profesionales", response_model=ProfessionalResponseDTO,
                    status_code=201, summary="Agregar profesional")
def create_professional(
    dto: ProfessionalCreateDTO,
    db: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    return ManageProfessionalUseCase(db).create(dto)


@config_router.put("/profesionales/{prof_id}", response_model=ProfessionalResponseDTO,
                   summary="Actualizar datos de un profesional (incl. firma)")
def update_professional(
    prof_id: str,
    dto: ProfessionalCreateDTO,
    db: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    try:
        return ManageProfessionalUseCase(db).update(prof_id, dto)
    except ApplicationError as e:
        raise HTTPException(404, detail=e.to_dict())


@config_router.delete("/profesionales/{prof_id}", status_code=204,
                       summary="Desactivar profesional")
def deactivate_professional(
    prof_id: str,
    db: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    ManageProfessionalUseCase(db).deactivate(prof_id)


# ═══════════════════════════════════════════════════════════════
# BACKUP
# ═══════════════════════════════════════════════════════════════

backup_router = APIRouter(prefix="/backup", tags=["Backup"])


@backup_router.post("/", response_model=BackupResponseDTO,
                    summary="Generar backup manual de la base de datos",
                    description="Copia el archivo SQLite a un directorio de backup. "
                                "Equivalente al botón BackUp del sistema VBA.")
def create_backup(
    dto: BackupRequestDTO,
    db: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    try:
        return BackupUseCase(db).create_backup(dto)
    except ApplicationError as e:
        raise HTTPException(500, detail=e.to_dict())


@backup_router.get("/", response_model=list[BackupResponseDTO],
                   summary="Historial de backups")
def list_backups(
    db: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    return BackupUseCase(db).list_backups()


# ═══════════════════════════════════════════════════════════════
# DOCUMENTOS — Comprobantes, Remisiones
# ═══════════════════════════════════════════════════════════════

docs_router = APIRouter(prefix="/documents", tags=["Documentos"])


@docs_router.post("/comprobante-asistencia", response_model=DocumentoResponseDTO,
                  status_code=201,
                  summary="Generar comprobante de asistencia a cita")
def comprobante_asistencia(dto: ComprobanteAsistenciaDTO, db: Session = Depends(get_session)):
    try:
        return GenerateDocumentUseCase(db).comprobante_asistencia(dto)
    except Exception as e:
        _handle(e)


@docs_router.post("/remision", response_model=DocumentoResponseDTO,
                  status_code=201,
                  summary="Generar formulario de remisión/interconsulta")
def remision(dto: RemisionDTO, db: Session = Depends(get_session)):
    try:
        return GenerateDocumentUseCase(db).remision(dto)
    except Exception as e:
        _handle(e)


@docs_router.get("/{patient_id}",
                 summary="Documentos generados para un paciente")
def list_documents(patient_id: str, db: Session = Depends(get_session)):
    from app.infrastructure.database.orm_models import DocumentoEmitidoORM
    docs = (db.query(DocumentoEmitidoORM)
            .filter_by(patient_id=patient_id)
            .order_by(DocumentoEmitidoORM.fecha_emision.desc())
            .all())
    return [
        {"id": d.id, "tipo": d.tipo_documento, "titulo": d.titulo,
         "formato": d.formato, "fecha": d.fecha_emision.isoformat()}
        for d in docs
    ]
