"""
app/presentation/api/v1/patients.py
=====================================
Endpoints RESTful de Pacientes.

Esta capa SOLO habla HTTP: recibe requests, delega a use cases,
devuelve responses. Cero lógica de negocio aquí.

Seguridad (S0.2 del PLAN_MAESTRO):
  - Auth: cada handler exige CurrentUser (Bearer token) — el middleware
    global ya enforza JWT, pero este dependency explicito documenta
    la intencion y permite integrar el `profesional_id` del usuario
    con los filtros de los listados.
  - Ownership: `get_patient_for_user(patient_id, db, user)` carga el
    paciente y valida que `user` puede acceder a el (admin ve todo;
    profesional solo ve pacientes de su profesional_id). El intento
    cross-tenant queda registrado en audit_log como `access_denied`.

Endpoints:
    POST   /patients/             → Registrar paciente
    GET    /patients/age-preview  → Calcular edad en tiempo real (publica)
    GET    /patients/             → Buscar pacientes (filtrado por user)
    GET    /patients/{id}         → Obtener paciente por ID (ownership)
    PATCH  /patients/{id}         → Actualizar datos (ownership)
    DELETE /patients/{id}         → Archivar (soft delete) (ownership)
"""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from app.application.dtos.patient_dtos import (
    AgeResponseDTO,
    PatientCreateDTO,
    PatientResponseDTO,
    PatientUpdateDTO,
)
from app.core.exceptions import (
    ApplicationError,
    PatientAlreadyExistsError,
    PatientNotFoundError,
)
from app.presentation.api.v1.auth import (
    CurrentUser,
    get_patient_for_user,
)
from app.presentation.dependencies import (
    ArchivePatientUC,
    DbSession,
    ExportPatientUC,
    GetPatientUC,
    RegisterPatientUC,
    SearchPatientsUC,
    UpdatePatientUC,
)

router = APIRouter(prefix="/patients", tags=["Pacientes"])


# ──────────────────────────────────────────────────────────────
# Handlers de excepción → HTTP
# ──────────────────────────────────────────────────────────────

def _handle_domain_error(e: Exception):
    if isinstance(e, PatientAlreadyExistsError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.to_dict())
    if isinstance(e, PatientNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.to_dict())
    if isinstance(e, ApplicationError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.to_dict())
    raise e


def _scope_profesional_id(user) -> str | None:
    """
    Devuelve el profesional_id bajo el que el usuario actual puede
    buscar/ver pacientes. Admin -> None (sin filtro, ve todo).
    Profesional / viewer -> su profesional_id.
    """
    if user.role == "admin":
        return None
    return user.profesional_id


# ──────────────────────────────────────────────────────────────
# ENDPOINTS
# ──────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=PatientResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo paciente",
    description=(
        "Crea un nuevo registro de paciente. Equivale al botón 'Guardar' del formulario "
        "'Recepción Usuarios' del sistema VBA. Calcula y devuelve la edad exacta y "
        "la población clínica automáticamente. "
        "El paciente queda asignado al profesional_id del usuario actual; "
        "un admin puede reasignarlo enviando el campo."
    ),
)
def register_patient(
    dto: PatientCreateDTO,
    uc: RegisterPatientUC,
    user=CurrentUser,
) -> PatientResponseDTO:
    # §S0.2: forzar que el paciente quede vinculado al profesional del user
    # (a menos que sea admin y esté reasignando explícitamente).
    if user.role != "admin" and user.profesional_id is not None:
        dto.profesional_id = user.profesional_id
    try:
        return uc.execute(dto)
    except Exception as e:
        _handle_domain_error(e)


@router.get(
    "/age-preview",
    response_model=AgeResponseDTO,
    summary="Calcular edad cronológica exacta",
    description=(
        "Calcula la edad sin guardar ningún dato. "
        "Diseñado para llamarse mientras el usuario escribe la fecha de nacimiento "
        "(UX reactivo del formulario). Sin auth: es un calculo puro."
    ),
)
def age_preview(
    fecha_nacimiento: date = Query(..., description="YYYY-MM-DD"),
    fecha_referencia: date | None = Query(default=None, description="Default: hoy"),
) -> AgeResponseDTO:
    from app.application.use_cases.patient_use_cases import CalculateAgeUseCase
    try:
        return CalculateAgeUseCase.execute(fecha_nacimiento, fecha_referencia)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/",
    response_model=list[PatientResponseDTO],
    summary="Buscar pacientes (filtrado por scope del usuario)",
    description=(
        "Búsqueda flexible por documento o nombre. Réplica del botón 'Buscar' del VBA. "
        "Los profesionales solo ven pacientes asignados a su profesional_id; "
        "los admins ven todos."
    ),
)
def search_patients(
    documento: str | None = Query(default=None),
    nombre: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    uc: SearchPatientsUC = ...,
    user=CurrentUser,
) -> list[PatientResponseDTO]:
    # §S0.2: si no es admin, filtra por su profesional_id
    scope = _scope_profesional_id(user)
    return uc.execute(
        documento=documento,
        nombre=nombre,
        limit=limit,
        offset=offset,
        profesional_id=scope,
    )


# ── PANEL Y ESTADÍSTICAS (MUST be before /{patient_id}) ──────

from app.application.dtos.patient_dtos import (
    PatientPanelResponseDTO,
    PatientStatsDTO,
)
from app.presentation.dependencies import PatientPanelUC, PatientStatsUC


@router.get(
    "/panel",
    response_model=PatientPanelResponseDTO,
    summary="Panel de pacientes con filtros y paginación",
    description=(
        "Búsqueda avanzada con filtros de texto, sexo, población etaria, "
        "profesional asignado y rango de fechas de atención. "
        "Cada resultado incluye el conteo de evaluaciones y la última evaluación realizada. "
        "Paginación con `pagina` y `por_pagina`. "
        "Los profesionales solo ven pacientes de su profesional_id; "
        "los admins pueden pasar `profesional_id` arbitrario para filtrar."
    ),
)
def get_patient_panel(
    uc: PatientPanelUC,
    user=CurrentUser,
    q: str | None = Query(default=None, description="Buscar por nombre o documento"),
    sexo: str | None = Query(default=None, description="H=Masculino, M=Femenino"),
    poblacion: str | None = Query(default=None, description="infantil | adulto_joven | adulto_mayor"),
    profesional_id: str | None = Query(default=None, description="UUID del profesional (solo admin)"),
    fecha_desde: str | None = Query(default=None, description="YYYY-MM-DD"),
    fecha_hasta: str | None = Query(default=None, description="YYYY-MM-DD"),
    pagina: int = Query(default=1, ge=1, description="Número de página"),
    por_pagina: int = Query(default=25, ge=1, le=100, description="Resultados por página"),
) -> PatientPanelResponseDTO:
    from datetime import date
    fd = date.fromisoformat(fecha_desde) if fecha_desde else None
    fh = date.fromisoformat(fecha_hasta) if fecha_hasta else None
    # §S0.2: para no-admin, ignorar el `profesional_id` que mande el cliente
    # y forzar el suyo propio.
    scope = _scope_profesional_id(user)
    return uc.execute(
        q=q, sexo=sexo, poblacion=poblacion,
        profesional_id=scope,
        fecha_desde=fd, fecha_hasta=fh,
        pagina=pagina, por_pagina=por_pagina,
    )


@router.get(
    "/stats",
    response_model=PatientStatsDTO,
    summary="Estadísticas globales para el dashboard",
    description=(
        "Total de pacientes, distribución por sexo, atendidos este mes y este año. "
        "Admin ve el agregado global; profesional / viewer ven solo el subset "
        "de su profesional_id."
    ),
)
def get_patient_stats(uc: PatientStatsUC, user=CurrentUser) -> PatientStatsDTO:
    scope = _scope_profesional_id(user)
    return uc.execute(profesional_id=scope)


# ── PACIENTE POR ID (parameterized — must be AFTER /panel /stats) ──

@router.get(
    "/{patient_id}",
    response_model=PatientResponseDTO,
    summary="Obtener paciente por ID (verifica ownership)",
)
def get_patient(
    patient_id: str,
    uc: GetPatientUC,
    db: DbSession,
    user=CurrentUser,
) -> PatientResponseDTO:
    # §S0.2: verificar ownership antes de delegar al use case
    get_patient_for_user(patient_id, db, user)
    try:
        return uc.by_id(patient_id)
    except Exception as e:
        _handle_domain_error(e)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponseDTO,
    summary="Actualizar datos del paciente (verifica ownership)",
)
def update_patient(
    patient_id: str,
    dto: PatientUpdateDTO,
    uc: UpdatePatientUC,
    db: DbSession,
    user=CurrentUser,
) -> PatientResponseDTO:
    # §S0.2: el DTO PatientUpdateDTO no expone `profesional_id` por diseño,
    # así que un no-admin no puede reasignarse un paciente vía PATCH. El
    # check de ownership aquí es la segunda línea de defensa.
    get_patient_for_user(patient_id, db, user)
    try:
        return uc.execute(patient_id, dto)
    except Exception as e:
        _handle_domain_error(e)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archivar paciente (soft delete, verifica ownership)",
    description="No borra físicamente. Marca el registro como inactivo.",
)
def archive_patient(
    patient_id: str,
    uc: ArchivePatientUC,
    db: DbSession,
    user=CurrentUser,
):
    get_patient_for_user(patient_id, db, user)
    try:
        uc.execute(patient_id)
    except Exception as e:
        _handle_domain_error(e)


# ──────────────────────────────────────────────────────────────
# HABEAS DATA — Derecho de acceso (Ley 1581/2012, Art. 8)
# ──────────────────────────────────────────────────────────────

@router.get(
    "/{patient_id}/export",
    summary="Exportar TODOS los datos del paciente (Habeas Data, verifica ownership)",
    description=(
        "Genera un dump JSON con la información completa que el sistema "
        "tiene sobre el paciente: datos demográficos, historia clínica, "
        "evaluaciones, sesiones de terapia, observaciones, citas, "
        "consentimientos, documentos emitidos y bitácora de correos. "
        "Cumple el derecho de acceso del titular del dato (Ley 1581/2012). "
        "El acto se registra en la auditoría como `export`. "
        "S0.2: la exportación se restringe a pacientes del profesional "
        "asignado (admin ve todos)."
    ),
    responses={
        200: {
            "description": "Dump JSON con esquema documentado por `schema_version`.",
            "content": {"application/json": {}},
        },
        404: {"description": "Paciente no encontrado."},
        403: {"description": "El usuario no tiene acceso a este paciente."},
    },
)
def export_patient_data(
    patient_id: str,
    request: Request,
    uc: ExportPatientUC,
    db: DbSession,
    user=CurrentUser,
):
    from app.infrastructure.audit import record_event

    # §S0.2: ownership check antes de exportar
    get_patient_for_user(patient_id, db, user)

    try:
        data = uc.execute(patient_id)
    except PatientNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())

    # Auditoría: dejar trazabilidad de quién, cuándo y para qué paciente
    # se exportaron los datos (Res. 1995/99 + Ley 1581).
    record_event(
        db,
        action="export",
        entity_type="patient",
        entity_id=patient_id,
        actor_id=user.id,
        actor_label=user.username,
        summary=(
            f"Exportación Habeas Data — "
            f"{data['totales']['evaluaciones']} evaluaciones, "
            f"{data['totales']['evoluciones_terapia']} sesiones de terapia"
        ),
        request=request,
    )

    # Devolvemos un Content-Disposition para que el navegador ofrezca
    # descargar el archivo (paquete autocontenido).
    filename = f"habeas_data_{patient_id}.json"
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
