"""
app/application/use_cases/clinical_history_use_cases.py
=========================================================
Casos de uso: Historia Clínica, Observaciones, Evolución Terapia,
Configuración, Documentos y Backup.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import text
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
from app.core.config import settings
from app.core.exceptions import ApplicationError, PatientNotFoundError
from app.domain.clinical_engine.interpretation_engine import InterpretationEngine
from app.domain.entities.models import ResultadoPrueba

# ─────────────────────────────────────────────────────────────────
# Helper: ORM → ResponseDTO
# ─────────────────────────────────────────────────────────────────

def _hc_to_response(orm) -> ClinicalHistoryResponseDTO:
    fields = [
        "id", "patient_id", "numero_documento", "fecha_atencion", "codigo_cie10",
        "motivo_consulta", "edad_materna", "no_gestacion", "riesgos", "cual_riesgo",
        "estres_prenatal", "gestacion", "semanas", "tipo_parto", "peso_gr", "talla_cm",
        "condiciones_neonatales", "incubadora", "sosten_cefalico", "sedestacion",
        "gateo", "marcha", "balbuceo", "primeras_palabras", "habla_claro",
        "control_anual", "control_vesical", "tipo_estres_prenatal", "ucin",
        "patologicos_medicos", "sensoriales_motores", "psiquiatricos", "farmacologicos",
        "traumaticos", "quirurgicos", "toxicos", "alergicos", "terapeuticos",
        "paraclinicos", "familiares", "vive_con", "abc", "escolar_laboral",
        "cognitivo", "comportamiento_animo", "patron_sueno", "patron_alimentacion",
        "plan_atencion", "impresion_diagnostica_hc", "hipotesis_pre_eval",
        "obs_clinica_general", "obs_atencion", "obs_memoria", "obs_praxias_gnosias",
        "obs_lenguaje", "obs_funciones_ejecutivas", "obs_emociones", "obs_ci",
        "obs_impresion_dx", "obs_funcionalidad", "obs_recomendaciones",
    ]
    return ClinicalHistoryResponseDTO(
        **{f: getattr(orm, f) for f in fields},
        row_version=getattr(orm, "row_version", 1) or 1,
    )


# ─────────────────────────────────────────────────────────────────
# 1. HISTORIA CLÍNICA
# ─────────────────────────────────────────────────────────────────

class UpsertClinicalHistoryUseCase:
    """Crea o actualiza la Historia Clínica de un paciente."""

    def __init__(self, session: Session):
        self._db = session

    def execute(self, dto: ClinicalHistoryUpsertDTO) -> ClinicalHistoryResponseDTO:
        from app.infrastructure.database.orm_models import ClinicalHistoryORM, PatientORM

        patient = self._db.query(PatientORM).filter_by(id=dto.patient_id, is_active=True).first()
        if not patient:
            raise PatientNotFoundError(dto.patient_id)

        existing = self._db.query(ClinicalHistoryORM).filter_by(
            patient_id=dto.patient_id, fecha_atencion=dto.fecha_atencion
        ).first()

        d = dto.desarrollo
        a = dto.antecedentes
        f = dto.familiar
        p = dto.plan_atencion
        o = dto.observaciones

        fields = dict(
            patient_id=dto.patient_id,
            numero_documento=patient.numero_documento,
            fecha_atencion=dto.fecha_atencion,
            codigo_cie10=dto.codigo_cie10,
            # Desarrollo
            motivo_consulta=d.motivo_consulta, edad_materna=d.edad_materna,
            no_gestacion=d.no_gestacion, riesgos=d.riesgos, cual_riesgo=d.cual_riesgo,
            estres_prenatal=d.estres_prenatal, gestacion=d.gestacion, semanas=d.semanas,
            tipo_parto=d.tipo_parto, peso_gr=d.peso_gr, talla_cm=d.talla_cm,
            condiciones_neonatales=d.condiciones_neonatales, incubadora=d.incubadora,
            sosten_cefalico=d.sosten_cefalico, sedestacion=d.sedestacion,
            gateo=d.gateo, marcha=d.marcha, balbuceo=d.balbuceo,
            primeras_palabras=d.primeras_palabras, habla_claro=d.habla_claro,
            control_anual=d.control_anual, control_vesical=d.control_vesical,
            tipo_estres_prenatal=d.tipo_estres_prenatal, ucin=d.ucin,
            # Antecedentes
            patologicos_medicos=a.patologicos_medicos, sensoriales_motores=a.sensoriales_motores,
            psiquiatricos=a.psiquiatricos, farmacologicos=a.farmacologicos,
            traumaticos=a.traumaticos, quirurgicos=a.quirurgicos, toxicos=a.toxicos,
            alergicos=a.alergicos, terapeuticos=a.terapeuticos,
            paraclinicos=a.paraclinicos, familiares=a.familiares,
            # Familiar
            vive_con=f.vive_con, abc=f.abc, escolar_laboral=f.escolar_laboral,
            cognitivo=f.cognitivo, comportamiento_animo=f.comportamiento_animo,
            patron_sueno=f.patron_sueno, patron_alimentacion=f.patron_alimentacion,
            # Plan
            plan_atencion=p.plan_atencion, impresion_diagnostica_hc=p.impresion_diagnostica_hc,
            hipotesis_pre_eval=p.hipotesis_pre_eval,
            # Observaciones
            obs_clinica_general=o.obs_clinica_general, obs_atencion=o.obs_atencion,
            obs_memoria=o.obs_memoria, obs_praxias_gnosias=o.obs_praxias_gnosias,
            obs_lenguaje=o.obs_lenguaje, obs_funciones_ejecutivas=o.obs_funciones_ejecutivas,
            obs_emociones=o.obs_emociones, obs_ci=o.obs_ci,
            obs_impresion_dx=o.obs_impresion_dx, obs_funcionalidad=o.obs_funcionalidad,
            obs_recomendaciones=o.obs_recomendaciones,
        )

        if existing:
            # ── OPTIMISTIC LOCKING ──────────────────────────────
            # Si el cliente envió row_version, verificar que coincida
            if dto.row_version is not None and dto.row_version > 0:
                current_version = getattr(existing, "row_version", 1) or 1
                if dto.row_version != current_version:
                    from app.core.exceptions import ConcurrencyError
                    raise ConcurrencyError(
                        resource="Historia Clínica",
                        client_version=dto.row_version,
                        server_version=current_version,
                    )
            # ── GUARDAR SNAPSHOT DE VERSIÓN ANTERIOR ────────────
            try:
                import json

                from app.infrastructure.database.orm_models import ClinicalHistoryVersionORM
                snapshot = {f: str(getattr(existing, f, "")) for f in fields}
                ver_snapshot = ClinicalHistoryVersionORM(
                    id=str(uuid.uuid4()),
                    hc_id=existing.id,
                    patient_id=existing.patient_id,
                    version_num=getattr(existing, "row_version", 1) or 1,
                    snapshot_json=json.dumps(snapshot, ensure_ascii=False, default=str),
                    saved_at=datetime.now(UTC),
                )
                self._db.add(ver_snapshot)
            except Exception as snap_err:
                import logging
                logging.getLogger(__name__).warning(
                    "Error guardando snapshot de HC versión %s: %s",
                    getattr(existing, "row_version", "?"), snap_err,
                )
            # ── ACTUALIZAR ──────────────────────────────────────
            for k, v in fields.items():
                setattr(existing, k, v)
            existing.updated_at = datetime.now(UTC)
            existing.row_version = (getattr(existing, "row_version", 1) or 1) + 1
            return _hc_to_response(existing)
        else:
            hc = ClinicalHistoryORM(id=str(uuid.uuid4()), row_version=1, **fields)
            self._db.add(hc)
            return _hc_to_response(hc)


class GetClinicalHistoryUseCase:
    def __init__(self, session: Session):
        self._db = session

    def by_patient(self, patient_id: str) -> ClinicalHistoryResponseDTO | None:
        from app.infrastructure.database.orm_models import ClinicalHistoryORM
        hc = self._db.query(ClinicalHistoryORM).filter_by(patient_id=patient_id).first()
        return _hc_to_response(hc) if hc else None

    def by_id(self, hc_id: str) -> ClinicalHistoryResponseDTO | None:
        from app.infrastructure.database.orm_models import ClinicalHistoryORM
        hc = self._db.query(ClinicalHistoryORM).filter_by(id=hc_id).first()
        return _hc_to_response(hc) if hc else None


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
            id=evol.id, patient_id=evol.patient_id,
            sesiones_orden=evol.sesiones_orden, numero_orden=evol.numero_orden,
            fecha_inicio=evol.fecha_inicio, fecha_sesion=evol.fecha_sesion,
            numero_sesion=evol.numero_sesion, objetivos=evol.objetivos,
            actividades=evol.actividades, plan_trabajo=evol.plan_trabajo,
        )


class GetEvolTerapiaUseCase:
    def __init__(self, session: Session):
        self._db = session

    def by_patient(self, patient_id: str) -> list[EvolTerapiaResponseDTO]:
        from app.infrastructure.database.orm_models import EvolTerapiaORM
        # Sólo sesiones activas (las archivadas se preservan para auditoría
        # pero no aparecen en el listado por defecto).
        evols = (self._db.query(EvolTerapiaORM)
                 .filter_by(patient_id=patient_id)
                 .filter(EvolTerapiaORM.archived_at.is_(None))
                 .order_by(EvolTerapiaORM.fecha_sesion.desc())
                 .all())
        return [EvolTerapiaResponseDTO(
            id=e.id, patient_id=e.patient_id, sesiones_orden=e.sesiones_orden,
            numero_orden=e.numero_orden, fecha_inicio=e.fecha_inicio,
            fecha_sesion=e.fecha_sesion, numero_sesion=e.numero_sesion,
            objetivos=e.objetivos, actividades=e.actividades, plan_trabajo=e.plan_trabajo,
        ) for e in evols]


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
                id=p.id, nombre_completo=p.nombre_completo,
                titulo=p.titulo, especialidad=p.especialidad,
                registro_profesional=p.registro_profesional,
                tiene_firma=bool(p.firma_base64),
                tiene_foto=bool(getattr(p, "foto_base64", None)),
                foto_base64=getattr(p, "foto_base64", None),
                email=p.email, activo=p.activo,
            ) for p in profs
        ]
        return ConfigCompleteResponseDTO(
            institucion=inst_dto, prefs_informe=prefs_dto, profesionales=profs_dto
        )


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
            id=prof.id, nombre_completo=prof.nombre_completo,
            titulo=prof.titulo, especialidad=prof.especialidad,
            registro_profesional=prof.registro_profesional,
            tiene_firma=bool(prof.firma_base64),
            tiene_foto=bool(foto),
            foto_base64=foto,
            email=prof.email, activo=prof.activo,
        )

    def create(self, dto: ProfessionalCreateDTO) -> ProfessionalResponseDTO:
        from app.infrastructure.database.orm_models import ProfessionalORM
        prof = ProfessionalORM(
            id=str(uuid.uuid4()),
            nombre_completo=dto.nombre_completo,
            titulo=dto.titulo, especialidad=dto.especialidad,
            registro_profesional=dto.registro_profesional,
            firma_base64=dto.firma_base64, sello_base64=dto.sello_base64,
            foto_base64=dto.foto_base64,
            email=dto.email, activo=dto.activo,
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
        """
        Copia el archivo SQLite a un directorio de backup y verifica su integridad.

        Pasos:
          1. `PRAGMA wal_checkpoint(FULL)` sobre la BD operativa para que el
             backup contenga TODOS los commits (WAL no copiado = pérdida de datos).
          2. `shutil.copy2` al destino.
          3. Abrir la copia y correr `PRAGMA integrity_check` — si no responde "ok"
             se elimina el archivo y se registra exitoso=False (no se deja un backup
             corrupto disponible para restaurar).
        """
        import sqlite3 as _sqlite3

        from app.infrastructure.database.orm_models import BackupRegistroORM, EvaluationORM, PatientORM

        db_path = settings.db_path
        if not db_path.exists():
            raise ApplicationError("Base de datos no encontrada.", code="DB_NOT_FOUND")

        # Directorio destino
        destino_base = Path(dto.destino) if dto.destino else settings.db_path.parent / "backups"
        destino_base.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_backup = f"neurosoft_backup_{timestamp}.db"
        ruta_destino = destino_base / nombre_backup

        # 1) Forzar flush del WAL hacia el archivo principal.
        #    Sin esto, un backup "copiado en caliente" perdería los commits
        #    pendientes en el journal.
        try:
            self._db.execute(text("PRAGMA wal_checkpoint(FULL)"))
        except Exception:  # noqa: BLE001
            # No bloquear la operación: si falla, el peor caso es un backup
            # ligeramente desactualizado pero el integrity_check lo detectará.
            pass

        # 2) Copia física.
        shutil.copy2(db_path, ruta_destino)

        # 3) Verificación de integridad sobre la copia.
        integrity = "unknown"
        try:
            conn = _sqlite3.connect(str(ruta_destino))
            try:
                cur = conn.execute("PRAGMA integrity_check")
                row = cur.fetchone()
                integrity = (row[0] if row else "unknown") or "unknown"
            finally:
                conn.close()
        except Exception as exc:  # noqa: BLE001
            integrity = f"error: {type(exc).__name__}"

        integrity_ok = integrity == "ok"
        tamano = ruta_destino.stat().st_size

        if not integrity_ok:
            # Backup corrupto → eliminar para que no aparezca en `list_backups`
            # y nadie pueda restaurar desde él.
            try:
                ruta_destino.unlink()
            except Exception:  # noqa: BLE001
                pass

        # Estadísticas (contadas incluso si el backup falló — info de diagnóstico)
        total_pac = self._db.query(PatientORM).filter_by(is_active=True).count()
        total_ev = self._db.query(EvaluationORM).count()

        registro = BackupRegistroORM(
            id=str(uuid.uuid4()),
            ruta_destino=str(ruta_destino) if integrity_ok else "(descartado por integrity_check)",
            tamano_bytes=tamano if integrity_ok else 0,
            total_pacientes=total_pac,
            total_evaluaciones=total_ev,
            exitoso=integrity_ok,
            notas=(dto.notas or "") + (
                "" if integrity_ok else
                f" | BACKUP DESCARTADO: integrity_check={integrity}"
            ),
            tipo="manual",
        )
        self._db.add(registro)

        return BackupResponseDTO(
            id=registro.id,
            fecha=registro.fecha.isoformat(),
            ruta_destino=nombre_backup if integrity_ok else None,
            tamano_kb=round(tamano / 1024, 1) if integrity_ok else 0.0,
            total_pacientes=total_pac,
            total_evaluaciones=total_ev,
            exitoso=integrity_ok,
            notas=dto.notas,
            integridad=integrity,
        )

    def list_backups(self) -> list[BackupResponseDTO]:
        from app.infrastructure.database.orm_models import BackupRegistroORM
        registros = self._db.query(BackupRegistroORM).order_by(
            BackupRegistroORM.fecha.desc()
        ).limit(20).all()
        return [BackupResponseDTO(
            id=r.id, fecha=r.fecha.isoformat(), ruta_destino=r.ruta_destino,
            tamano_kb=round((r.tamano_bytes or 0) / 1024, 1),
            total_pacientes=r.total_pacientes or 0,
            total_evaluaciones=r.total_evaluaciones or 0,
            exitoso=r.exitoso, notas=r.notas,
        ) for r in registros]


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

    def comprobante_asistencia(
        self, dto: ComprobanteAsistenciaDTO
    ) -> DocumentoResponseDTO:
        from app.infrastructure.database.orm_models import DocumentoEmitidoORM, PatientORM
        patient = self._db.query(PatientORM).filter_by(id=dto.patient_id, is_active=True).first()
        if not patient:
            raise PatientNotFoundError(dto.patient_id)

        doc_id = str(uuid.uuid4())
        titulo = (f"Comprobante Asistencia — "
                  f"{patient.primer_nombre} {patient.primer_apellido} "
                  f"{dto.fecha_atencion}")
        doc = DocumentoEmitidoORM(
            id=doc_id, patient_id=dto.patient_id,
            tipo_documento="comprobante_asistencia",
            titulo=titulo, formato=dto.formato,
            profesional_id=dto.profesional_id,
            contenido_json=json.dumps({
                "tipo_servicio": dto.tipo_servicio,
                "codigo_cups": dto.codigo_cups,
                "hora_inicio": dto.hora_inicio,
                "hora_fin": dto.hora_fin,
                "duracion_minutos": dto.duracion_minutos,
                "observaciones": dto.observaciones,
            }, ensure_ascii=False),
        )
        self._db.add(doc)
        return DocumentoResponseDTO(
            id=doc_id, tipo="comprobante_asistencia", titulo=titulo,
            formato=dto.formato, ruta_archivo=None,
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
            id=doc_id, patient_id=dto.patient_id,
            tipo_documento="remision", titulo=titulo, formato=dto.formato,
            profesional_id=dto.profesional_id,
            contenido_json=json.dumps({
                "remite_a": dto.remite_a,
                "motivo": dto.motivo_remision,
                "diagnostico": dto.diagnostico_presuntivo,
                "cie10": dto.codigo_cie10,
                "observaciones": dto.observaciones,
            }, ensure_ascii=False),
        )
        self._db.add(doc)
        return DocumentoResponseDTO(
            id=doc_id, tipo="remision", titulo=titulo, formato=dto.formato,
            ruta_archivo=None, fecha_emision=datetime.now(UTC).isoformat(),
            descarga_url=f"/api/v1/documents/{doc_id}/download",
        )
