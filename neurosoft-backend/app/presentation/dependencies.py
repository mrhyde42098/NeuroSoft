"""
app/presentation/dependencies.py
==================================
Contenedor de Inyección de Dependencias de FastAPI.

Este archivo es el "pegamento" de la arquitectura: conecta todas las
capas sin acoplarlas entre sí. Los endpoints solo conocen los use cases;
los use cases solo conocen repositorios y el engine; los repositorios
solo conocen el ORM.

Patrón: Provider Functions con FastAPI Depends().

Cada proveedor es una función generadora que:
    1. Crea la dependencia (sesión BD, repositorio, use case).
    2. La yield al endpoint.
    3. Hace cleanup en el finally (cierre de sesión).

Tests: sobreescribir con `app.dependency_overrides[fn] = mock_fn`.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.appointment_use_cases import (
    CreateAppointmentUseCase,
    DeleteAppointmentUseCase,
    GetAgendaStatsUseCase,
    GetAppointmentUseCase,
    GetTodayAppointmentsUseCase,
    GetWeekAppointmentsUseCase,
    ListAppointmentsUseCase,
    ListPatientAppointmentsUseCase,
    UpdateAppointmentUseCase,
)
from app.application.use_cases.patient_use_cases import (
    ArchivePatientUseCase,
    GetPatientUseCase,
    RegisterPatientUseCase,
    SearchPatientsUseCase,
    UpdatePatientUseCase,
)
from app.application.use_cases.report_use_cases import GenerateReportUseCase
from app.application.use_cases.scoring_use_cases import (
    GetEvaluationDetailUseCase,
    GetEvaluationHistoryUseCase,
    GetObservationsUseCase,
    GetSignatureStatusUseCase,
    ListTestsUseCase,
    ScoreEvaluationUseCase,
    ScorePreviewUseCase,
    SignEvaluationUseCase,
    UpsertObservationUseCase,
)
from app.application.use_cases.therapy_use_cases import (
    ArchiveTherapyTaskUseCase,
    CreateRiskAssessmentUseCase,
    CreateTherapyPlanUseCase,
    CreateTherapySessionUseCase,
    CreateTherapyTaskUseCase,
    GetTherapyPlanUseCase,
    GetTherapySessionUseCase,
    GetTherapyTaskUseCase,
    ListRiskAssessmentsUseCase,
    ListTherapyPlansUseCase,
    ListTherapySessionsUseCase,
    ListTherapyTasksUseCase,
    LockTherapySessionUseCase,
    TherapyTaskSummaryUseCase,
    UpdateTherapyPlanUseCase,
    UpdateTherapySessionUseCase,
    UpdateTherapyTaskUseCase,
)
from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.engine import ClinicalEngine
from app.infrastructure.database.engine import get_session
from app.infrastructure.repositories.appointment_repo import AppointmentRepository
from app.infrastructure.repositories.evaluation_repo import EvaluationRepository
from app.infrastructure.repositories.patient_repo import PatientRepository
from app.infrastructure.repositories.therapy_repo import TherapyRepository

# ─────────────────────────────────────────────────────────────
# CAPA 1: Sesión de BD
# ─────────────────────────────────────────────────────────────


def db_session() -> Generator[Session, None, None]:
    """Sesión SQLAlchemy. Se crea y cierra por request."""
    yield from get_session()


DbSession = Annotated[Session, Depends(db_session)]


# ─────────────────────────────────────────────────────────────
# CAPA 2: Repositorios
# ─────────────────────────────────────────────────────────────


def patient_repository(db: DbSession) -> PatientRepository:
    return PatientRepository(session=db)


def evaluation_repository(db: DbSession) -> EvaluationRepository:
    return EvaluationRepository(session=db)


PatientRepo = Annotated[PatientRepository, Depends(patient_repository)]
EvaluationRepo = Annotated[EvaluationRepository, Depends(evaluation_repository)]


def therapy_repository(db: DbSession) -> TherapyRepository:
    return TherapyRepository(session=db)


TherapyRepo = Annotated[TherapyRepository, Depends(therapy_repository)]


def appointment_repository(db: DbSession) -> AppointmentRepository:
    return AppointmentRepository(session=db)


AppointmentRepo = Annotated[AppointmentRepository, Depends(appointment_repository)]


# ─────────────────────────────────────────────────────────────
# CAPA 3: Motor clínico (Singleton compartido entre requests)
# ─────────────────────────────────────────────────────────────


def clinical_engine() -> ClinicalEngine:
    loader = BaremosLoader.instance()
    return ClinicalEngine(loader=loader)


def baremos_loader() -> BaremosLoader:
    return BaremosLoader.instance()


ClinicalEngineInstance = Annotated[ClinicalEngine, Depends(clinical_engine)]
BaremosLoaderInstance = Annotated[BaremosLoader, Depends(baremos_loader)]


# ─────────────────────────────────────────────────────────────
# CAPA 4: Use Cases
# ─────────────────────────────────────────────────────────────

# --- Pacientes ---


def register_patient_uc(repo: PatientRepo) -> RegisterPatientUseCase:
    return RegisterPatientUseCase(repo=repo)


def update_patient_uc(repo: PatientRepo) -> UpdatePatientUseCase:
    return UpdatePatientUseCase(repo=repo)


def get_patient_uc(repo: PatientRepo) -> GetPatientUseCase:
    return GetPatientUseCase(repo=repo)


def search_patients_uc(repo: PatientRepo) -> SearchPatientsUseCase:
    return SearchPatientsUseCase(repo=repo)


def archive_patient_uc(repo: PatientRepo) -> ArchivePatientUseCase:
    return ArchivePatientUseCase(repo=repo)


# --- Scoring ---


def score_evaluation_uc(
    repo: PatientRepo,
    eval_repo: EvaluationRepo,
    engine: ClinicalEngineInstance,
) -> ScoreEvaluationUseCase:
    return ScoreEvaluationUseCase(
        patient_repo=repo,
        engine=engine,
        evaluation_repo=eval_repo,  # ← ahora sí conectado
    )


def score_preview_uc(
    repo: PatientRepo,
    engine: ClinicalEngineInstance,
) -> ScorePreviewUseCase:
    return ScorePreviewUseCase(patient_repo=repo, engine=engine)


def list_tests_uc(loader: BaremosLoaderInstance) -> ListTestsUseCase:
    return ListTestsUseCase(loader=loader)


# --- Evaluaciones (historial) ---


def get_eval_history_uc(
    eval_repo: EvaluationRepo,
    repo: PatientRepo,
) -> GetEvaluationHistoryUseCase:
    return GetEvaluationHistoryUseCase(evaluation_repo=eval_repo, patient_repo=repo)


def get_eval_detail_uc(eval_repo: EvaluationRepo) -> GetEvaluationDetailUseCase:
    return GetEvaluationDetailUseCase(evaluation_repo=eval_repo)


def sign_evaluation_uc(db: DbSession) -> SignEvaluationUseCase:
    return SignEvaluationUseCase(session=db)


def get_signature_status_uc(db: DbSession) -> GetSignatureStatusUseCase:
    return GetSignatureStatusUseCase(session=db)


# --- Observaciones ---


def upsert_observation_uc(db: DbSession) -> UpsertObservationUseCase:
    return UpsertObservationUseCase(session=db)


def get_observations_uc(db: DbSession) -> GetObservationsUseCase:
    return GetObservationsUseCase(session=db)


# --- Terapia ---


def list_therapy_plans_uc(repo: TherapyRepo) -> ListTherapyPlansUseCase:
    return ListTherapyPlansUseCase(repo=repo)


def create_therapy_plan_uc(repo: TherapyRepo) -> CreateTherapyPlanUseCase:
    return CreateTherapyPlanUseCase(repo=repo)


def get_therapy_plan_uc(repo: TherapyRepo) -> GetTherapyPlanUseCase:
    return GetTherapyPlanUseCase(repo=repo)


def update_therapy_plan_uc(repo: TherapyRepo) -> UpdateTherapyPlanUseCase:
    return UpdateTherapyPlanUseCase(repo=repo)


def list_therapy_sessions_uc(repo: TherapyRepo) -> ListTherapySessionsUseCase:
    return ListTherapySessionsUseCase(repo=repo)


def create_therapy_session_uc(repo: TherapyRepo) -> CreateTherapySessionUseCase:
    return CreateTherapySessionUseCase(repo=repo)


def get_therapy_session_uc(repo: TherapyRepo) -> GetTherapySessionUseCase:
    return GetTherapySessionUseCase(repo=repo)


def update_therapy_session_uc(repo: TherapyRepo) -> UpdateTherapySessionUseCase:
    return UpdateTherapySessionUseCase(repo=repo)


def lock_therapy_session_uc(repo: TherapyRepo) -> LockTherapySessionUseCase:
    return LockTherapySessionUseCase(repo=repo)


def create_risk_assessment_uc(repo: TherapyRepo) -> CreateRiskAssessmentUseCase:
    return CreateRiskAssessmentUseCase(repo=repo)


def list_risk_assessments_uc(repo: TherapyRepo) -> ListRiskAssessmentsUseCase:
    return ListRiskAssessmentsUseCase(repo=repo)


def create_therapy_task_uc(repo: TherapyRepo) -> CreateTherapyTaskUseCase:
    return CreateTherapyTaskUseCase(repo=repo)


def list_therapy_tasks_uc(repo: TherapyRepo) -> ListTherapyTasksUseCase:
    return ListTherapyTasksUseCase(repo=repo)


def get_therapy_task_uc(repo: TherapyRepo) -> GetTherapyTaskUseCase:
    return GetTherapyTaskUseCase(repo=repo)


def update_therapy_task_uc(repo: TherapyRepo) -> UpdateTherapyTaskUseCase:
    return UpdateTherapyTaskUseCase(repo=repo)


def archive_therapy_task_uc(repo: TherapyRepo) -> ArchiveTherapyTaskUseCase:
    return ArchiveTherapyTaskUseCase(repo=repo)


def therapy_task_summary_uc(repo: TherapyRepo) -> TherapyTaskSummaryUseCase:
    return TherapyTaskSummaryUseCase(repo=repo)


# --- Informes ---


def generate_report_uc(db: DbSession, eval_repo: EvaluationRepo) -> GenerateReportUseCase:
    return GenerateReportUseCase(session=db, eval_repo=eval_repo)


# --- Agenda ---


def create_appointment_uc(repo: AppointmentRepo) -> CreateAppointmentUseCase:
    return CreateAppointmentUseCase(repo=repo)


def get_today_appointments_uc(repo: AppointmentRepo) -> GetTodayAppointmentsUseCase:
    return GetTodayAppointmentsUseCase(repo=repo)


def get_week_appointments_uc(repo: AppointmentRepo) -> GetWeekAppointmentsUseCase:
    return GetWeekAppointmentsUseCase(repo=repo)


def get_agenda_stats_uc(repo: AppointmentRepo) -> GetAgendaStatsUseCase:
    return GetAgendaStatsUseCase(repo=repo)


def list_appointments_uc(repo: AppointmentRepo) -> ListAppointmentsUseCase:
    return ListAppointmentsUseCase(repo=repo)


def list_patient_appointments_uc(repo: AppointmentRepo) -> ListPatientAppointmentsUseCase:
    return ListPatientAppointmentsUseCase(repo=repo)


def get_appointment_uc(repo: AppointmentRepo) -> GetAppointmentUseCase:
    return GetAppointmentUseCase(repo=repo)


def update_appointment_uc(repo: AppointmentRepo) -> UpdateAppointmentUseCase:
    return UpdateAppointmentUseCase(repo=repo)


def delete_appointment_uc(repo: AppointmentRepo) -> DeleteAppointmentUseCase:
    return DeleteAppointmentUseCase(repo=repo)


# ─────────────────────────────────────────────────────────────
# Anotaciones tipadas listas para usar en endpoints
# ─────────────────────────────────────────────────────────────

RegisterPatientUC = Annotated[RegisterPatientUseCase, Depends(register_patient_uc)]
UpdatePatientUC = Annotated[UpdatePatientUseCase, Depends(update_patient_uc)]
GetPatientUC = Annotated[GetPatientUseCase, Depends(get_patient_uc)]
SearchPatientsUC = Annotated[SearchPatientsUseCase, Depends(search_patients_uc)]
ArchivePatientUC = Annotated[ArchivePatientUseCase, Depends(archive_patient_uc)]
ScoreEvalUC = Annotated[ScoreEvaluationUseCase, Depends(score_evaluation_uc)]
ScorePreviewUC = Annotated[ScorePreviewUseCase, Depends(score_preview_uc)]
ListTestsUC = Annotated[ListTestsUseCase, Depends(list_tests_uc)]
GetEvalHistoryUC = Annotated[GetEvaluationHistoryUseCase, Depends(get_eval_history_uc)]
GetEvalDetailUC = Annotated[GetEvaluationDetailUseCase, Depends(get_eval_detail_uc)]
UpsertObsUC = Annotated[UpsertObservationUseCase, Depends(upsert_observation_uc)]
GetObsUC = Annotated[GetObservationsUseCase, Depends(get_observations_uc)]
SignEvalUC = Annotated[SignEvaluationUseCase, Depends(sign_evaluation_uc)]
GetSignatureUC = Annotated[GetSignatureStatusUseCase, Depends(get_signature_status_uc)]
ListTherapyPlansUC = Annotated[ListTherapyPlansUseCase, Depends(list_therapy_plans_uc)]
CreateTherapyPlanUC = Annotated[CreateTherapyPlanUseCase, Depends(create_therapy_plan_uc)]
GetTherapyPlanUC = Annotated[GetTherapyPlanUseCase, Depends(get_therapy_plan_uc)]
UpdateTherapyPlanUC = Annotated[UpdateTherapyPlanUseCase, Depends(update_therapy_plan_uc)]
ListTherapySessionsUC = Annotated[ListTherapySessionsUseCase, Depends(list_therapy_sessions_uc)]
CreateTherapySessionUC = Annotated[CreateTherapySessionUseCase, Depends(create_therapy_session_uc)]
GetTherapySessionUC = Annotated[GetTherapySessionUseCase, Depends(get_therapy_session_uc)]
UpdateTherapySessionUC = Annotated[UpdateTherapySessionUseCase, Depends(update_therapy_session_uc)]
LockTherapySessionUC = Annotated[LockTherapySessionUseCase, Depends(lock_therapy_session_uc)]
CreateRiskAssessmentUC = Annotated[CreateRiskAssessmentUseCase, Depends(create_risk_assessment_uc)]
ListRiskAssessmentsUC = Annotated[ListRiskAssessmentsUseCase, Depends(list_risk_assessments_uc)]
CreateTherapyTaskUC = Annotated[CreateTherapyTaskUseCase, Depends(create_therapy_task_uc)]
ListTherapyTasksUC = Annotated[ListTherapyTasksUseCase, Depends(list_therapy_tasks_uc)]
GetTherapyTaskUC = Annotated[GetTherapyTaskUseCase, Depends(get_therapy_task_uc)]
UpdateTherapyTaskUC = Annotated[UpdateTherapyTaskUseCase, Depends(update_therapy_task_uc)]
ArchiveTherapyTaskUC = Annotated[ArchiveTherapyTaskUseCase, Depends(archive_therapy_task_uc)]
TherapyTaskSummaryUC = Annotated[TherapyTaskSummaryUseCase, Depends(therapy_task_summary_uc)]
GenerateReportUC = Annotated[GenerateReportUseCase, Depends(generate_report_uc)]
CreateAppointmentUC = Annotated[CreateAppointmentUseCase, Depends(create_appointment_uc)]
GetTodayAppointmentsUC = Annotated[GetTodayAppointmentsUseCase, Depends(get_today_appointments_uc)]
GetWeekAppointmentsUC = Annotated[GetWeekAppointmentsUseCase, Depends(get_week_appointments_uc)]
GetAgendaStatsUC = Annotated[GetAgendaStatsUseCase, Depends(get_agenda_stats_uc)]
ListAppointmentsUC = Annotated[ListAppointmentsUseCase, Depends(list_appointments_uc)]
ListPatientAppointmentsUC = Annotated[ListPatientAppointmentsUseCase, Depends(list_patient_appointments_uc)]
GetAppointmentUC = Annotated[GetAppointmentUseCase, Depends(get_appointment_uc)]
UpdateAppointmentUC = Annotated[UpdateAppointmentUseCase, Depends(update_appointment_uc)]
DeleteAppointmentUC = Annotated[DeleteAppointmentUseCase, Depends(delete_appointment_uc)]


# ─────────────────────────────────────────────────────────────
# CAPA 4b: Patient Panel / Stats
# ─────────────────────────────────────────────────────────────

from app.application.use_cases.patient_use_cases import (
    PatientPanelUseCase,
    PatientStatsUseCase,
)


def patient_panel_uc(repo: PatientRepo, db: DbSession) -> PatientPanelUseCase:
    return PatientPanelUseCase(repo=repo, db=db)


def patient_stats_uc(repo: PatientRepo, db: DbSession) -> PatientStatsUseCase:
    return PatientStatsUseCase(repo=repo, db=db)


PatientPanelUC = Annotated[PatientPanelUseCase, Depends(patient_panel_uc)]
PatientStatsUC = Annotated[PatientStatsUseCase, Depends(patient_stats_uc)]


# ─────────────────────────────────────────────────────────────
# Habeas Data — exportación de datos (Ley 1581/12 Art. 8)
# ─────────────────────────────────────────────────────────────

from app.application.use_cases.export_use_cases import ExportPatientDataUseCase


def export_patient_uc(db: DbSession) -> ExportPatientDataUseCase:
    return ExportPatientDataUseCase(session=db)


ExportPatientUC = Annotated[ExportPatientDataUseCase, Depends(export_patient_uc)]
