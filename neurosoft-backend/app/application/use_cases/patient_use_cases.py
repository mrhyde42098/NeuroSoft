"""
app/application/use_cases/patient_use_cases.py
================================================
Casos de uso de Pacientes.

Un caso de uso = una acción concreta que el sistema puede realizar.
Orquesta entidades, repositorios y utilidades sin saber nada de HTTP.

Casos:
    RegisterPatientUseCase       → Alta de nuevo paciente
    UpdatePatientUseCase         → Edición de datos
    GetPatientUseCase            → Consulta por ID o documento
    SearchPatientsUseCase        → Búsqueda flexible
    CalculateAgePreviewUseCase   → Vista previa de edad (UX del formulario)
    ArchivePatientUseCase        → Soft delete
"""

from __future__ import annotations

import logging
from datetime import date

from app.application.dtos.patient_dtos import (
    AgeResponseDTO,
    PatientCreateDTO,
    PatientResponseDTO,
    PatientUpdateDTO,
)
from app.core.exceptions import (
    PatientAlreadyExistsError,
)
from app.core.utils import AgeCalculator
from app.domain.entities.models import Paciente, PacienteId
from app.infrastructure.repositories.patient_repo import PatientRepository

logger = logging.getLogger(__name__)


def _to_response(paciente: Paciente) -> PatientResponseDTO:
    """Convierte Paciente → PatientResponseDTO con edad calculada."""
    age = AgeCalculator.calculate(paciente.fecha_nacimiento, paciente.fecha_atencion)
    years = age.years
    poblacion = (
        "infantil" if years < 18
        else "adulto_joven" if years < 50
        else "adulto_mayor"
    )
    return PatientResponseDTO(
        id=str(paciente.id),
        numero_documento=paciente.numero_documento,
        tipo_documento=paciente.tipo_documento,
        nombre_completo=paciente.nombre_completo,
        fecha_nacimiento=paciente.fecha_nacimiento,
        fecha_atencion=paciente.fecha_atencion,
        sexo=paciente.sexo,
        escolaridad=paciente.escolaridad,
        lateralidad=paciente.lateralidad,
        ciudad=paciente.ciudad,
        motivo_consulta=paciente.motivo_consulta,
        codigo_rips=paciente.codigo_rips,
        eps=paciente.eps,
        age_years=age.years,
        age_months=age.months,
        age_display=age.display,
        poblacion=poblacion,
    )


# ─────────────────────────────────────────────────────────────
# 1. REGISTRAR PACIENTE
# ─────────────────────────────────────────────────────────────

class RegisterPatientUseCase:
    """
    Registra un nuevo paciente.

    Reglas:
        - No puede existir otro con mismo doc + fecha_atencion.
        - Calcula la edad y valida que sea ≥ 2 años.
    """

    def __init__(self, repo: PatientRepository):
        self._repo = repo

    def execute(self, dto: PatientCreateDTO) -> PatientResponseDTO:
        # Verificar duplicado
        existing = self._repo.find_by_document_and_date(
            dto.numero_documento, dto.fecha_atencion
        )
        if existing:
            raise PatientAlreadyExistsError(dto.numero_documento, str(dto.fecha_atencion))

        # Construir entidad
        paciente = Paciente(
            id=PacienteId.generate(),
            numero_documento=dto.numero_documento,
            tipo_documento=dto.tipo_documento,
            primer_nombre=dto.primer_nombre,
            segundo_nombre=dto.segundo_nombre,
            primer_apellido=dto.primer_apellido,
            segundo_apellido=dto.segundo_apellido,
            fecha_nacimiento=dto.fecha_nacimiento,
            sexo=dto.sexo,
            escolaridad=dto.escolaridad,
            lateralidad=dto.lateralidad,
            fecha_atencion=dto.fecha_atencion,
            telefono=dto.telefono,
            correo=dto.correo,
            direccion=dto.direccion,
            ciudad=dto.ciudad,
            localidad=dto.localidad,
            estrato=dto.estrato,
            estado_civil=dto.estado_civil,
            lugar_nacimiento=dto.lugar_nacimiento,
            ocupacion=dto.ocupacion,
            acompanante=dto.acompanante,
            acompanante_relacion=dto.acompanante_relacion,
            acompanante_telefono=dto.acompanante_telefono,
            grupo_etnico=dto.grupo_etnico,
            profesional_id=dto.profesional_id,
            motivo_consulta=dto.motivo_consulta,
            remite=dto.remite,
            eps=dto.eps,
            orden_medica_no=dto.orden_medica_no,
            discapacidad=dto.discapacidad,
            codigo_rips=dto.codigo_rips,
            cups=dto.cups,
            finalidad_consulta=dto.finalidad_consulta,
            numero_sesiones=dto.numero_sesiones,
            donante=dto.donante,
        )

        saved = self._repo.save(paciente)
        # PII: NO loguear nombre_completo (Ley 1581). Sólo el ID es seguro.
        logger.info("Paciente registrado: id=%s", saved.id)
        return _to_response(saved)


# ─────────────────────────────────────────────────────────────
# 2. ACTUALIZAR PACIENTE
# ─────────────────────────────────────────────────────────────

class UpdatePatientUseCase:
    def __init__(self, repo: PatientRepository):
        self._repo = repo

    def execute(self, patient_id: str, dto: PatientUpdateDTO) -> PatientResponseDTO:
        paciente = self._repo.find_by_id(patient_id)

        # Aplicar solo los campos enviados (partial update)
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(paciente, field, value)

        saved = self._repo.save(paciente)
        return _to_response(saved)


# ─────────────────────────────────────────────────────────────
# 3. OBTENER PACIENTE
# ─────────────────────────────────────────────────────────────

class GetPatientUseCase:
    def __init__(self, repo: PatientRepository):
        self._repo = repo

    def by_id(self, patient_id: str) -> PatientResponseDTO:
        paciente = self._repo.find_by_id(patient_id)
        return _to_response(paciente)

    def by_document(self, numero_documento: str) -> list[PatientResponseDTO]:
        pacientes = self._repo.find_by_document(numero_documento)
        return [_to_response(p) for p in pacientes]


# ─────────────────────────────────────────────────────────────
# 4. BUSCAR PACIENTES
# ─────────────────────────────────────────────────────────────

class SearchPatientsUseCase:
    def __init__(self, repo: PatientRepository):
        self._repo = repo

    def execute(
        self,
        documento: str | None = None,
        nombre: str | None = None,
        limit: int = 20,
        offset: int = 0,
        profesional_id: str | None = None,
    ) -> list[PatientResponseDTO]:
        pacientes = self._repo.search(
            documento=documento, nombre=nombre, limit=limit, offset=offset,
            profesional_id=profesional_id,
        )
        return [_to_response(p) for p in pacientes]


# ─────────────────────────────────────────────────────────────
# 5. CALCULAR EDAD (UX del formulario, sin guardar)
# ─────────────────────────────────────────────────────────────

class CalculateAgeUseCase:
    """Sin dependencias — función pura envuelta en use case."""

    @staticmethod
    def execute(
        fecha_nacimiento: date,
        fecha_referencia: date | None = None,
    ) -> AgeResponseDTO:
        ref = fecha_referencia or date.today()
        age = AgeCalculator.calculate(fecha_nacimiento, ref)
        years = age.years
        poblacion = (
            "infantil" if years < 18
            else "adulto_joven" if years < 50
            else "adulto_mayor"
        )
        return AgeResponseDTO(
            years=age.years,
            months=age.months,
            days=age.days,
            total_months=age.total_months,
            decimal_years=age.decimal_years,
            display=str(age),
            poblacion=poblacion,
            birth_date=age.birth_date.isoformat(),
            reference_date=age.reference_date.isoformat(),
        )


# ─────────────────────────────────────────────────────────────
# 6. ARCHIVAR PACIENTE (soft delete)
# ─────────────────────────────────────────────────────────────

class ArchivePatientUseCase:
    def __init__(self, repo: PatientRepository):
        self._repo = repo

    def execute(self, patient_id: str) -> bool:
        # Verificar que existe
        self._repo.find_by_id(patient_id)
        return self._repo.soft_delete(patient_id)


# ─────────────────────────────────────────────────────────────
# 7. PANEL DE PACIENTES (búsqueda avanzada + estadísticas)
# ─────────────────────────────────────────────────────────────

class PatientPanelUseCase:
    """
    Búsqueda avanzada para el panel principal.
    Combina datos del paciente con conteo de evaluaciones en una
    sola consulta eficiente — evita el N+1 del enfoque ingenuo.
    """

    def __init__(self, repo: PatientRepository, db):
        self._repo = repo
        self._db = db

    def execute(
        self,
        q: str | None = None,
        sexo: str | None = None,
        poblacion: str | None = None,
        profesional_id: str | None = None,
        fecha_desde=None,
        fecha_hasta=None,
        pagina: int = 1,
        por_pagina: int = 25,
    ):

        from sqlalchemy import func

        from app.application.dtos.patient_dtos import (
            PatientPanelItemDTO,
            PatientPanelResponseDTO,
        )
        from app.infrastructure.database.orm_models import EvaluationORM

        offset = (pagina - 1) * por_pagina
        orms, total = self._repo.search_panel(
            q=q, sexo=sexo, poblacion=poblacion,
            profesional_id=profesional_id,
            fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
            limit=por_pagina, offset=offset,
        )

        # Bulk load eval counts for all patients in this page
        patient_ids = [o.id for o in orms]
        eval_counts = {}
        eval_latest = {}
        eval_protocolo = {}

        if patient_ids:
            count_rows = (
                self._db.query(
                    EvaluationORM.patient_id,
                    func.count(EvaluationORM.id).label('cnt'),
                )
                .filter(EvaluationORM.patient_id.in_(patient_ids))
                .group_by(EvaluationORM.patient_id)
                .all()
            )
            for pid, cnt in count_rows:
                eval_counts[pid] = cnt

            latest_rows = (
                self._db.query(
                    EvaluationORM.patient_id,
                    EvaluationORM.fecha,
                    EvaluationORM.protocolo,
                )
                .filter(
                    EvaluationORM.patient_id.in_(patient_ids),
                    EvaluationORM.is_latest.is_(True),
                )
                .all()
            )
            for pid, fecha, proto in latest_rows:
                # Keep only the most recent fecha per patient
                if pid not in eval_latest or (fecha and fecha > eval_latest[pid]):
                    eval_latest[pid] = fecha
                    eval_protocolo[pid] = proto

        items = []
        for orm in orms:
            from app.core.utils import AgeCalculator
            age = AgeCalculator.calculate(orm.fecha_nacimiento)
            if age.years < 18:
                pop = "infantil"
            elif age.years < 50:
                pop = "adulto_joven"
            else:
                pop = "adulto_mayor"

            nombre = " ".join(filter(None, [
                orm.primer_nombre, orm.segundo_nombre,
                orm.primer_apellido, orm.segundo_apellido,
            ]))

            items.append(PatientPanelItemDTO(
                id=orm.id,
                numero_documento=orm.numero_documento,
                tipo_documento=orm.tipo_documento or "CC",
                nombre_completo=nombre,
                fecha_nacimiento=orm.fecha_nacimiento,
                fecha_atencion=orm.fecha_atencion,
                sexo=orm.sexo,
                escolaridad=orm.escolaridad,
                ciudad=orm.ciudad,
                remite=orm.remite,
                profesional_id=orm.profesional_id,
                acompanante=orm.acompanante,
                acompanante_relacion=getattr(orm, "acompanante_relacion", None),
                acompanante_telefono=getattr(orm, "acompanante_telefono", None),
                age_display=f"{age.years}a {age.months}m",
                poblacion=pop,
                total_evaluaciones=eval_counts.get(orm.id, 0),
                ultima_evaluacion=(
                    eval_latest[orm.id].isoformat()
                    if orm.id in eval_latest and eval_latest[orm.id]
                    else None
                ),
                ultimo_protocolo=eval_protocolo.get(orm.id),
            ))

        return PatientPanelResponseDTO(
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
            pacientes=items,
        )


class PatientStatsUseCase:
    """Estadísticas rápidas para el dashboard."""

    def __init__(self, repo: PatientRepository, db):
        self._repo = repo
        self._db = db

    def execute(self, profesional_id: str | None = None):
        """
        S0.2: si `profesional_id` viene, las stats se calculan solo sobre
        los pacientes de ese profesional (admin pasa None para stats globales).
        """
        from sqlalchemy import func

        from app.application.dtos.patient_dtos import PatientStatsDTO
        from app.infrastructure.database.orm_models import EvaluationORM, PatientORM

        stats = self._repo.get_stats(profesional_id=profesional_id)

        # Total de evaluaciones (filtrado por scope)
        q_eval = self._db.query(func.count(EvaluationORM.id))
        q_sin  = self._db.query(func.count(EvaluationORM.id)).filter(
            EvaluationORM.signed_at.is_(None)
        )
        if profesional_id:
            q_eval = q_eval.join(
                PatientORM, PatientORM.id == EvaluationORM.patient_id
            ).filter(PatientORM.profesional_id == profesional_id)
            q_sin  = q_sin.join(
                PatientORM, PatientORM.id == EvaluationORM.patient_id
            ).filter(PatientORM.profesional_id == profesional_id)
        total_eval = q_eval.scalar() or 0
        sin_informe = q_sin.scalar() or 0
        stats["total_evaluaciones"] = total_eval
        stats["evaluaciones_sin_informe"] = sin_informe

        return PatientStatsDTO(**{k: v for k, v in stats.items()
                                  if k in PatientStatsDTO.model_fields})
