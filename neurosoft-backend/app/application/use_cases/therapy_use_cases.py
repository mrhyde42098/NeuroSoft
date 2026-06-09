"""Casos de uso del módulo de psicología clínica."""

from __future__ import annotations

from app.application.dtos.therapy_dtos import (
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
from app.domain.clinical_engine.cie_mapping_service import resolve_cie11_code
from app.infrastructure.repositories.therapy_repo import TherapyRepository


class ListTherapyPlansUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, patient_id: str) -> list[TherapyPlanResponseDTO]:
        return self._repo.list_plans(patient_id)


class CreateTherapyPlanUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(
        self,
        dto: TherapyPlanCreateDTO,
        *,
        profesional_id: str | None,
    ) -> TherapyPlanResponseDTO:
        cie11 = dto.codigo_cie11 or resolve_cie11_code(dto.diagnostico_principal)
        return self._repo.create_plan(dto, profesional_id=profesional_id, cie11=cie11)


class GetTherapyPlanUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, plan_id: str) -> TherapyPlanResponseDTO:
        return self._repo.get_plan(plan_id)


class UpdateTherapyPlanUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, plan_id: str, dto: TherapyPlanUpdateDTO) -> TherapyPlanResponseDTO:
        return self._repo.update_plan(plan_id, dto)


class ListTherapySessionsUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, patient_id: str, plan_id: str | None = None) -> list[TherapySessionResponseDTO]:
        return self._repo.list_sessions(patient_id, plan_id)


class CreateTherapySessionUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, dto: TherapySessionCreateDTO, *, profesional_id: str | None) -> TherapySessionResponseDTO:
        return self._repo.create_session(dto, profesional_id=profesional_id)


class GetTherapySessionUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, session_id: str) -> TherapySessionResponseDTO:
        return self._repo.get_session(session_id)


class UpdateTherapySessionUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, session_id: str, dto: TherapySessionUpdateDTO) -> TherapySessionResponseDTO:
        return self._repo.update_session(session_id, dto)


class LockTherapySessionUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, session_id: str, *, user_id: str) -> TherapySessionResponseDTO:
        return self._repo.lock_session(session_id, user_id=user_id)


class CreateRiskAssessmentUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, dto: RiskAssessmentCreateDTO, *, profesional_id: str | None) -> RiskAssessmentResponseDTO:
        return self._repo.create_risk_assessment(dto, profesional_id=profesional_id)


class ListRiskAssessmentsUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, patient_id: str) -> list[RiskAssessmentResponseDTO]:
        return self._repo.list_risk_assessments(patient_id)


class CreateTherapyTaskUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, dto: TherapyTaskCreateDTO) -> TherapyTaskResponseDTO:
        return self._repo.create_task(dto)


class ListTherapyTasksUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(
        self,
        patient_id: str,
        *,
        estado: str | None = None,
        plan_id: str | None = None,
        session_id: str | None = None,
        incluir_archivadas: bool = False,
    ) -> list[TherapyTaskResponseDTO]:
        return self._repo.list_tasks(
            patient_id,
            estado=estado,
            plan_id=plan_id,
            session_id=session_id,
            incluir_archivadas=incluir_archivadas,
        )


class GetTherapyTaskUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, task_id: str) -> TherapyTaskResponseDTO:
        return self._repo.get_task(task_id)


class UpdateTherapyTaskUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, task_id: str, dto: TherapyTaskUpdateDTO) -> TherapyTaskResponseDTO:
        return self._repo.update_task(task_id, dto)


class ArchiveTherapyTaskUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, task_id: str) -> None:
        self._repo.archive_task(task_id)


class TherapyTaskSummaryUseCase:
    def __init__(self, repo: TherapyRepository):
        self._repo = repo

    def execute(self, patient_id: str) -> dict:
        return self._repo.task_summary(patient_id)
