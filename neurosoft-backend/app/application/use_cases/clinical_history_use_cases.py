"""
app/application/use_cases/clinical_history_use_cases.py
=========================================================
Casos de uso: Historia Clínica, Observaciones, Evolución Terapia,
Configuración, Documentos y Backup.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

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
from app.core.exceptions import ApplicationError, PatientNotFoundError
from app.domain.clinical_engine.interpretation_engine import InterpretationEngine
from app.domain.entities.models import ResultadoPrueba
from app.infrastructure.repositories.clinical_history_repo import ClinicalHistoryRepository, hc_to_response

_hc_to_response = hc_to_response


# ─────────────────────────────────────────────────────────────────
# 1. HISTORIA CLÍNICA
# ─────────────────────────────────────────────────────────────────


class UpsertClinicalHistoryUseCase:
    """Crea o actualiza la Historia Clínica de un paciente."""

    def __init__(self, session: Session):
        self._repo = ClinicalHistoryRepository(session)

    def execute(self, dto: ClinicalHistoryUpsertDTO) -> ClinicalHistoryResponseDTO:
        return self._repo.upsert(dto)


class GetClinicalHistoryUseCase:
    def __init__(self, session: Session):
        self._repo = ClinicalHistoryRepository(session)

    def by_patient(self, patient_id: str) -> ClinicalHistoryResponseDTO | None:
        return self._repo.get_by_patient(patient_id)

    def by_id(self, hc_id: str) -> ClinicalHistoryResponseDTO | None:
        return self._repo.get_by_id(hc_id)


# ─────────────────────────────────────────────────────────────────
# 2. INTERPRETACIÓN ASISTIDA
# ─────────────────────────────────────────────────────────────────


class GetInterpretationSuggestionsUseCase:
    """
    A partir de los resultados de una evaluación,
    genera sugerencias de texto por dominio cognitivo.
    """

    def __init__(self, session: Session):
        self._db = session
        self._engine = InterpretationEngine()

    def execute(self, evaluation_id: str) -> dict:
        import json

        from app.infrastructure.database.orm_models import EvaluationORM

        ev = self._db.query(EvaluationORM).filter_by(id=evaluation_id).first()
        if not ev or not ev.resultados_json:
            return {"profiles": [], "z_chart": [], "ci_summary": None}

        raw = json.loads(ev.resultados_json)
        resultados = [ResultadoPrueba(**r) for r in raw if r.get("fue_realizada")]

        profiles = self._engine.build_profiles(resultados)
        z_chart = self._engine.build_z_chart_data(resultados)
        ci_summary = self._engine.get_ci_summary(resultados)

        return {
            "profiles": [
                {
                    "dominio": p.dominio,
                    "icono": p.icono,
                    "nivel": p.nivel_general,
                    "color": p.color,
                    "z_promedio": p.z_promedio,
                    "sugerencia_texto": p.sugerencia_texto,
                    "puntos_fuertes": p.puntos_fuertes,
                    "puntos_debiles": p.puntos_debiles,
                    "n_pruebas": len(p.pruebas),
                }
                for p in profiles
            ],
            "z_chart": z_chart,
            "ci_summary": ci_summary,
        }


# ─────────────────────────────────────────────────────────────────
# 3. EVOLUCIÓN TERAPIA
# ─────────────────────────────────────────────────────────────────


class CreateEvolTerapiaUseCase:
    def __init__(self, session: Session):
        self._db = session

    def execute(self, dto: EvolTerapiaCreateDTO) -> EvolTerapiaResponseDTO:
        from app.infrastructure.database.orm_models import EvolTerapiaORM, PatientORM

        patient = self._db.query(PatientORM).filter_by(id=dto.patient_id, is_active=True).first()
        if not patient:
            raise PatientNotFoundError(dto.patient_id)
        evol = EvolTerapiaORM(
            id=str(uuid.uuid4()),
            patient_id=dto.patient_id,
            numero_documento=patient.numero_documento,
            sesiones_orden=dto.sesiones_orden,
            numero_orden=dto.numero_orden,
            fecha_inicio=dto.fecha_inicio,
            fecha_sesion=dto.fecha_sesion,
            numero_sesion=dto.numero_sesion,
            objetivos=dto.objetivos,
            actividades=dto.actividades,
            plan_trabajo=dto.plan_trabajo,
        )
        self._db.add(evol)
        return EvolTerapiaResponseDTO(
            id=evol.id,
            patient_id=evol.patient_id,
            sesiones_orden=evol.sesiones_orden,
            numero_orden=evol.numero_orden,
            fecha_inicio=evol.fecha_inicio,
            fecha_sesion=evol.fecha_sesion,
            numero_sesion=evol.numero_sesion,
            objetivos=evol.objetivos,
            actividades=evol.actividades,
            plan_trabajo=evol.plan_trabajo,
        )


class GetEvolTerapiaUseCase:
    def __init__(self, session: Session):
        self._db = session

    def by_patient(self, patient_id: str) -> list[EvolTerapiaResponseDTO]:
        from app.infrastructure.database.orm_models import EvolTerapiaORM

        # Sólo sesiones activas (las archivadas se preservan para auditoría
        # pero no aparecen en el listado por defecto).
        evols = (
            self._db.query(EvolTerapiaORM)
            .filter_by(patient_id=patient_id)
            .filter(EvolTerapiaORM.archived_at.is_(None))
            .order_by(EvolTerapiaORM.fecha_sesion.desc())
            .all()
        )
        return [
            EvolTerapiaResponseDTO(
                id=e.id,
                patient_id=e.patient_id,
                sesiones_orden=e.sesiones_orden,
                numero_orden=e.numero_orden,
                fecha_inicio=e.fecha_inicio,
                fecha_sesion=e.fecha_sesion,
                numero_sesion=e.numero_sesion,
                objetivos=e.objetivos,
                actividades=e.actividades,
                plan_trabajo=e.plan_trabajo,
            )
            for e in evols
        ]


# ─────────────────────────────────────────────────────────────────
# 4. CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────


class GetConfigUseCase:
    def __init__(self, session: Session):
        self._db = session

    def execute(self) -> ConfigCompleteResponseDTO:
        from app.infrastructure.database.orm_models import ConfigInstitucionORM, ConfigPrefsInformeORM, ProfessionalORM

        inst = self._db.query(ConfigInstitucionORM).filter_by(id="1").first()
        prefs = self._db.query(ConfigPrefsInformeORM).filter_by(id="1").first()
        profs = self._db.query(ProfessionalORM).filter_by(activo=True).all()

        inst_dto = ConfigInstitucionDTO(
            nombre=inst.nombre if inst else "",
            nit=inst.nit if inst else "",
            direccion=inst.direccion if inst else "",
            telefono=inst.telefono if inst else "",
            email=inst.email if inst else "",
            sitio_web=inst.sitio_web if inst else "",
            logo_base64=inst.logo_base64 if inst else None,
            ciudad=inst.ciudad if inst else "Bogotá",
        )
        prefs_dto = ConfigPrefsInformeDTO(
            fuente_cuerpo=prefs.fuente_cuerpo if prefs else "Calibri",
            fuente_titulos=prefs.fuente_titulos if prefs else "Calibri",
            tamano_fuente_cuerpo=prefs.tamano_fuente_cuerpo if prefs else 11,
            tamano_fuente_titulos=prefs.tamano_fuente_titulos if prefs else 13,
            color_primario=prefs.color_primario if prefs else "#1a568c",
            color_secundario=prefs.color_secundario if prefs else "#2ec4b6",
            incluir_logo=prefs.incluir_logo if prefs else True,
            incluir_firma=prefs.incluir_firma if prefs else True,
            incluir_grafica_z=prefs.incluir_grafica_z if prefs else True,
            incluir_tabla_puntajes=prefs.incluir_tabla_puntajes if prefs else True,
        )
        profs_dto = [
            ProfessionalResponseDTO(
                id=p.id,
                nombre_completo=p.nombre_completo,
                titulo=p.titulo,
                especialidad=p.especialidad,
                registro_profesional=p.registro_profesional,
                tiene_firma=bool(p.firma_base64),
                tiene_foto=bool(getattr(p, "foto_base64", None)),
                foto_base64=getattr(p, "foto_base64", None),
                email=p.email,
                activo=p.activo,
            )
            for p in profs
        ]
        return ConfigCompleteResponseDTO(institucion=inst_dto, prefs_informe=prefs_dto, profesionales=profs_dto)


class UpdateConfigInstitucionUseCase:
    def __init__(self, session: Session):
        self._db = session

    def execute(self, dto: ConfigInstitucionDTO) -> ConfigInstitucionDTO:
        from app.infrastructure.database.orm_models import ConfigInstitucionORM

        inst = self._db.query(ConfigInstitucionORM).filter_by(id="1").first()
        if not inst:
            inst = ConfigInstitucionORM(id="1")
            self._db.add(inst)
        inst.nombre = dto.nombre
        inst.nit = dto.nit
        inst.direccion = dto.direccion
        inst.telefono = dto.telefono
        inst.email = dto.email
        inst.sitio_web = dto.sitio_web
        inst.logo_base64 = dto.logo_base64
        inst.ciudad = dto.ciudad
        inst.updated_at = datetime.now(UTC)
        return dto


class UpdateConfigPrefsUseCase:
    def __init__(self, session: Session):
        self._db = session

    def execute(self, dto: ConfigPrefsInformeDTO) -> ConfigPrefsInformeDTO:
        from app.infrastructure.database.orm_models import ConfigPrefsInformeORM

        prefs = self._db.query(ConfigPrefsInformeORM).filter_by(id="1").first()
        if not prefs:
            prefs = ConfigPrefsInformeORM(id="1")
            self._db.add(prefs)
        for field, value in dto.model_dump(exclude_none=True).items():
            setattr(prefs, field, value)
        prefs.updated_at = datetime.now(UTC)
        return dto


class ManageProfessionalUseCase:
    def __init__(self, session: Session):
        self._db = session

    def _to_resp(self, prof) -> ProfessionalResponseDTO:
        """Helper único para serializar profesional a DTO incluyendo foto."""
        foto = getattr(prof, "foto_base64", None)
        return ProfessionalResponseDTO(
            id=prof.id,
            nombre_completo=prof.nombre_completo,
            titulo=prof.titulo,
            especialidad=prof.especialidad,
            registro_profesional=prof.registro_profesional,
            tiene_firma=bool(prof.firma_base64),
            tiene_foto=bool(foto),
            foto_base64=foto,
            email=prof.email,
            activo=prof.activo,
        )

    def create(self, dto: ProfessionalCreateDTO) -> ProfessionalResponseDTO:
        from app.infrastructure.database.orm_models import ProfessionalORM

        prof = ProfessionalORM(
            id=str(uuid.uuid4()),
            nombre_completo=dto.nombre_completo,
            titulo=dto.titulo,
            especialidad=dto.especialidad,
            registro_profesional=dto.registro_profesional,
            firma_base64=dto.firma_base64,
            sello_base64=dto.sello_base64,
            foto_base64=dto.foto_base64,
            email=dto.email,
            activo=dto.activo,
        )
        self._db.add(prof)
        return self._to_resp(prof)

    def update(self, prof_id: str, dto: ProfessionalCreateDTO) -> ProfessionalResponseDTO:
        from app.infrastructure.database.orm_models import ProfessionalORM

        prof = self._db.query(ProfessionalORM).filter_by(id=prof_id).first()
        if not prof:
            raise ApplicationError(f"Profesional {prof_id} no encontrado.", code="PROF_NOT_FOUND")
        for field, value in dto.model_dump(exclude_none=True).items():
            setattr(prof, field, value)
        return self._to_resp(prof)

    def deactivate(self, prof_id: str) -> bool:
        from app.infrastructure.database.orm_models import ProfessionalORM

        prof = self._db.query(ProfessionalORM).filter_by(id=prof_id, activo=True).first()
        if not prof:
            return False
        prof.activo = False
        return True

    def list_all(self, include_inactive: bool = False) -> list[ProfessionalResponseDTO]:
        from app.infrastructure.database.orm_models import ProfessionalORM

        q = self._db.query(ProfessionalORM)
        if not include_inactive:
            q = q.filter_by(activo=True)
        profs = q.order_by(ProfessionalORM.nombre_completo).all()
        return [self._to_resp(p) for p in profs]


# ─────────────────────────────────────────────────────────────────
# 5. BACKUP
# ─────────────────────────────────────────────────────────────────


class BackupUseCase:
    def __init__(self, session: Session):
        self._db = session

    def create_backup(self, dto: BackupRequestDTO) -> BackupResponseDTO:
        """Backup cifrado unificado (QW-8) vía backup_service."""
        from app.application.services.backup_service import run_backup, to_response_dto

        result = run_backup(
            self._db,
            notas=dto.notas or "Backup manual",
            tipo="manual",
            external_path=dto.destino,
        )
        return to_response_dto(result.registro)

    def list_backups(self) -> list[BackupResponseDTO]:
        from app.application.services.backup_service import list_unified_backups

        return list_unified_backups(self._db)


# ─────────────────────────────────────────────────────────────────
# 6. DOCUMENTOS (comprobantes, remisiones, RIPS)
# ─────────────────────────────────────────────────────────────────


class GenerateDocumentUseCase:
    """
    Genera comprobantes, remisiones y RIPS.
    Por ahora devuelve metadatos; la generación real de PDF
    se implementa en el report_service.
    """

    def __init__(self, session: Session):
        self._db = session

    def comprobante_asistencia(self, dto: ComprobanteAsistenciaDTO) -> DocumentoResponseDTO:
        from app.infrastructure.database.orm_models import DocumentoEmitidoORM, PatientORM

        patient = self._db.query(PatientORM).filter_by(id=dto.patient_id, is_active=True).first()
        if not patient:
            raise PatientNotFoundError(dto.patient_id)

        doc_id = str(uuid.uuid4())
        titulo = f"Comprobante Asistencia — {patient.primer_nombre} {patient.primer_apellido} {dto.fecha_atencion}"
        doc = DocumentoEmitidoORM(
            id=doc_id,
            patient_id=dto.patient_id,
            tipo_documento="comprobante_asistencia",
            titulo=titulo,
            formato=dto.formato,
            profesional_id=dto.profesional_id,
            contenido_json=json.dumps(
                {
                    "tipo_servicio": dto.tipo_servicio,
                    "codigo_cups": dto.codigo_cups,
                    "hora_inicio": dto.hora_inicio,
                    "hora_fin": dto.hora_fin,
                    "duracion_minutos": dto.duracion_minutos,
                    "observaciones": dto.observaciones,
                },
                ensure_ascii=False,
            ),
        )
        self._db.add(doc)
        return DocumentoResponseDTO(
            id=doc_id,
            tipo="comprobante_asistencia",
            titulo=titulo,
            formato=dto.formato,
            ruta_archivo=None,
            fecha_emision=datetime.now(UTC).isoformat(),
            descarga_url=f"/api/v1/documents/{doc_id}/download",
        )

    def remision(self, dto: RemisionDTO) -> DocumentoResponseDTO:
        from app.infrastructure.database.orm_models import DocumentoEmitidoORM, PatientORM

        patient = self._db.query(PatientORM).filter_by(id=dto.patient_id, is_active=True).first()
        if not patient:
            raise PatientNotFoundError(dto.patient_id)

        doc_id = str(uuid.uuid4())
        titulo = f"Remisión a {dto.remite_a} — {patient.primer_apellido} {dto.fecha}"
        doc = DocumentoEmitidoORM(
            id=doc_id,
            patient_id=dto.patient_id,
            tipo_documento="remision",
            titulo=titulo,
            formato=dto.formato,
            profesional_id=dto.profesional_id,
            contenido_json=json.dumps(
                {
                    "remite_a": dto.remite_a,
                    "motivo": dto.motivo_remision,
                    "diagnostico": dto.diagnostico_presuntivo,
                    "cie10": dto.codigo_cie10,
                    "observaciones": dto.observaciones,
                },
                ensure_ascii=False,
            ),
        )
        self._db.add(doc)
        return DocumentoResponseDTO(
            id=doc_id,
            tipo="remision",
            titulo=titulo,
            formato=dto.formato,
            ruta_archivo=None,
            fecha_emision=datetime.now(UTC).isoformat(),
            descarga_url=f"/api/v1/documents/{doc_id}/download",
        )
