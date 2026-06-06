"""
app/application/dtos/clinical_history_dtos.py
===============================================
DTOs para Historia Clínica, Evolución Terapia, Configuración y Documentos.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.core.validators import OptionalUUIDStr, UUIDStr

# ═══════════════════════════════════════════════════════════════
# HISTORIA CLÍNICA — REQUEST DTOs
# ═══════════════════════════════════════════════════════════════


class HCDesarrolloDTO(BaseModel):
    """Pestaña 1: Desarrollo (riesgos perinatales e hitos)."""

    motivo_consulta: str = "N/A"
    edad_materna: str = "N/A"
    no_gestacion: str = "N/A"
    riesgos: str = "N/A"
    cual_riesgo: str = "N/A"
    estres_prenatal: str = "N/A"
    gestacion: str = "N/A"
    semanas: str = "N/A"
    tipo_parto: str = "N/A"
    peso_gr: str = "N/A"
    talla_cm: str = "N/A"
    condiciones_neonatales: str = "N/A"
    incubadora: str = "N/A"
    sosten_cefalico: str = "N/A"
    sedestacion: str = "N/A"
    gateo: str = "N/A"
    marcha: str = "N/A"
    balbuceo: str = "N/A"
    primeras_palabras: str = "N/A"
    habla_claro: str = "N/A"
    control_anual: str = "N/A"
    control_vesical: str = "N/A"
    tipo_estres_prenatal: str = "N/A"
    ucin: str = "N/A"


class HCAntecedentesDTO(BaseModel):
    """Pestaña 2: Antecedentes Médicos."""

    patologicos_medicos: str = "N/A"
    sensoriales_motores: str = "N/A"
    psiquiatricos: str = "N/A"
    farmacologicos: str = "N/A"
    traumaticos: str = "N/A"
    quirurgicos: str = "N/A"
    toxicos: str = "N/A"
    alergicos: str = "N/A"
    terapeuticos: str = "N/A"
    paraclinicos: str = "N/A"
    familiares: str = "N/A"


class HCFamiliarDTO(BaseModel):
    """Pestaña 3: Familiar/Social/Funcional."""

    vive_con: str = "N/A"
    abc: str = "N/A"
    escolar_laboral: str = "N/A"
    cognitivo: str = "N/A"
    comportamiento_animo: str = "N/A"
    patron_sueno: str = "N/A"
    patron_alimentacion: str = "N/A"


class HCPlanAtencionDTO(BaseModel):
    """Pestaña 4: Plan de Atención."""

    plan_atencion: str = "N/A"
    impresion_diagnostica_hc: str = "N/A"
    hipotesis_pre_eval: str = "N/A"


class HCObservacionesDTO(BaseModel):
    """Observaciones Clínicas por dominio (FormObsClinNPS)."""

    obs_clinica_general: str = "N/A"
    obs_atencion: str = "N/A"
    obs_memoria: str = "N/A"
    obs_praxias_gnosias: str = "N/A"
    obs_lenguaje: str = "N/A"
    obs_funciones_ejecutivas: str = "N/A"
    obs_emociones: str = "N/A"
    obs_ci: str = "N/A"
    obs_impresion_dx: str = "N/A"
    obs_funcionalidad: str = "N/A"
    obs_recomendaciones: str = "N/A"


class ClinicalHistoryUpsertDTO(BaseModel):
    """
    DTO completo para crear o actualizar la Historia Clínica.
    Agrupa las 4 pestañas del FormHC + las observaciones del FormObsClinNPS.
    """

    patient_id: UUIDStr
    fecha_atencion: date
    codigo_cie10: str = "F809"
    codigo_cie11: str | None = None
    # Optimistic locking: el cliente envía la versión que tiene.
    # Si no coincide con la BD, se lanza ConcurrencyError (409).
    # En un CREATE (nueva HC) enviar None o 0.
    row_version: int | None = None
    desarrollo: HCDesarrolloDTO = Field(default_factory=HCDesarrolloDTO)
    antecedentes: HCAntecedentesDTO = Field(default_factory=HCAntecedentesDTO)
    familiar: HCFamiliarDTO = Field(default_factory=HCFamiliarDTO)
    plan_atencion: HCPlanAtencionDTO = Field(default_factory=HCPlanAtencionDTO)
    observaciones: HCObservacionesDTO = Field(default_factory=HCObservacionesDTO)

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "uuid-del-paciente",
                "fecha_atencion": "2026-03-20",
                "codigo_cie10": "F809",
                "desarrollo": {"motivo_consulta": "Remitido por neurología..."},
                "antecedentes": {"patologicos_medicos": "IRA frecuentes..."},
                "familiar": {"vive_con": "Mamá, papá, hermana..."},
                "plan_atencion": {"plan_atencion": "Se recomienda PIR..."},
                "observaciones": {"obs_atencion": "Se mantiene..."},
            }
        }
    }


class ClinicalHistoryResponseDTO(BaseModel):
    """Respuesta de la Historia Clínica completa."""

    id: str
    patient_id: str
    numero_documento: str
    fecha_atencion: date
    codigo_cie10: str
    codigo_cie11: str | None = None
    row_version: int = 1  # Para optimistic locking — el cliente lo reenvía en el siguiente save
    # Los 4 tabs aplanados para facilitar el frontend
    motivo_consulta: str
    edad_materna: str
    no_gestacion: str
    riesgos: str
    cual_riesgo: str
    estres_prenatal: str
    gestacion: str
    semanas: str
    tipo_parto: str
    peso_gr: str
    talla_cm: str
    condiciones_neonatales: str
    incubadora: str
    sosten_cefalico: str
    sedestacion: str
    gateo: str
    marcha: str
    balbuceo: str
    primeras_palabras: str
    habla_claro: str
    control_anual: str
    control_vesical: str
    tipo_estres_prenatal: str
    ucin: str
    patologicos_medicos: str
    sensoriales_motores: str
    psiquiatricos: str
    farmacologicos: str
    traumaticos: str
    quirurgicos: str
    toxicos: str
    alergicos: str
    terapeuticos: str
    paraclinicos: str
    familiares: str
    vive_con: str
    abc: str
    escolar_laboral: str
    cognitivo: str
    comportamiento_animo: str
    patron_sueno: str
    patron_alimentacion: str
    plan_atencion: str
    impresion_diagnostica_hc: str
    hipotesis_pre_eval: str | None = "N/A"
    obs_clinica_general: str
    obs_atencion: str
    obs_memoria: str
    obs_praxias_gnosias: str
    obs_lenguaje: str
    obs_funciones_ejecutivas: str
    obs_emociones: str
    obs_ci: str
    obs_impresion_dx: str
    obs_funcionalidad: str
    obs_recomendaciones: str


# ═══════════════════════════════════════════════════════════════
# EVOLUCIÓN TERAPIA
# ═══════════════════════════════════════════════════════════════


class EvolTerapiaCreateDTO(BaseModel):
    """Crear o actualizar una sesión de evolución."""

    patient_id: UUIDStr
    sesiones_orden: str | None = None
    numero_orden: str | None = None
    fecha_inicio: date | None = None
    fecha_sesion: date = Field(default_factory=date.today)
    numero_sesion: str = "N/A"
    objetivos: str = "N/A"
    actividades: str = "N/A"
    plan_trabajo: str = "N/A"


class EvolTerapiaResponseDTO(BaseModel):
    id: str
    patient_id: str
    sesiones_orden: str | None
    numero_orden: str | None
    fecha_inicio: date | None
    fecha_sesion: date
    numero_sesion: str
    objetivos: str
    actividades: str
    plan_trabajo: str


class EvolTerapiaUpdateDTO(BaseModel):
    """
    Campos editables de una sesión de evolución.
    Todos opcionales → sólo se tocan los que vengan en el request.
    Ley 1581: sólo exponemos las columnas clínicas esperadas; el resto
    (id, patient_id, archived_*, created_at) se ignora si viene en el body.
    """

    model_config = {"extra": "forbid"}

    fecha_sesion: date | None = None
    numero_sesion: str | None = Field(default=None, max_length=10)
    objetivos: str | None = Field(default=None, max_length=10000)
    actividades: str | None = Field(default=None, max_length=10000)
    plan_trabajo: str | None = Field(default=None, max_length=10000)


class EvolTerapiaArchiveDTO(BaseModel):
    """Payload para archivar una sesión (soft-delete, Res. 1995)."""

    model_config = {"extra": "forbid"}
    reason: str = Field(..., min_length=3, max_length=500, description="Motivo del archivo — queda en auditoría.")


class SignatureUploadDTO(BaseModel):
    """
    Subida de firma digital del profesional.
    SVG se rechaza para prevenir XSS almacenado.
    """

    model_config = {"extra": "forbid"}
    firma_base64: str = Field(
        ...,
        min_length=10,
        description="Data URL o base64 puro. PNG/JPEG/GIF únicamente.",
    )


# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════


class ProfessionalCreateDTO(BaseModel):
    """Crear o actualizar un profesional evaluador."""

    nombre_completo: str = Field(..., min_length=3)
    titulo: str | None = None
    especialidad: str | None = None
    registro_profesional: str | None = None
    firma_base64: str | None = None  # "data:image/png;base64,..."
    sello_base64: str | None = None
    foto_base64: str | None = None  # avatar/foto del profesional
    email: str | None = None
    activo: bool = True


class ProfessionalResponseDTO(BaseModel):
    id: str
    nombre_completo: str
    titulo: str | None
    especialidad: str | None
    registro_profesional: str | None
    tiene_firma: bool
    tiene_foto: bool = False
    foto_base64: str | None = None  # devolvemos para mostrar avatar en UI
    email: str | None
    activo: bool


class ConfigInstitucionDTO(BaseModel):
    """Datos de la institución para el informe."""

    nombre: str = ""
    nit: str = ""
    direccion: str = ""
    telefono: str = ""
    email: str = ""
    sitio_web: str = ""
    logo_base64: str | None = None
    ciudad: str = "Bogotá"


class ConfigPrefsInformeDTO(BaseModel):
    """Preferencias visuales del informe."""

    fuente_cuerpo: str = "Calibri"
    fuente_titulos: str = "Calibri"
    tamano_fuente_cuerpo: int = Field(default=11, ge=8, le=16)
    tamano_fuente_titulos: int = Field(default=13, ge=10, le=20)
    color_primario: str = "#1a568c"
    color_secundario: str = "#2ec4b6"
    incluir_logo: bool = True
    incluir_firma: bool = True
    incluir_grafica_z: bool = True
    incluir_tabla_puntajes: bool = True
    nota_pie_informe: str | None = None


class ConfigCompleteResponseDTO(BaseModel):
    """Toda la configuración del sistema en un solo response."""

    institucion: ConfigInstitucionDTO
    prefs_informe: ConfigPrefsInformeDTO
    profesionales: list[ProfessionalResponseDTO]


# ═══════════════════════════════════════════════════════════════
# DOCUMENTOS — Comprobantes, Recetario, RIPS
# ═══════════════════════════════════════════════════════════════


class ComprobanteAsistenciaDTO(BaseModel):
    """
    Comprobante de asistencia a la cita.
    VBA: CompAtencion form.
    """

    patient_id: UUIDStr
    profesional_id: OptionalUUIDStr = None
    fecha_atencion: date = Field(default_factory=date.today)
    hora_inicio: str | None = None  # "09:00"
    hora_fin: str | None = None  # "11:00"
    duracion_minutos: int | None = None
    tipo_servicio: str = "Evaluación Neuropsicológica"
    codigo_cups: str = "890208"
    observaciones: str | None = None
    formato: str = "pdf"  # pdf | docx


class ComprobantePruebasDTO(BaseModel):
    """
    Comprobante de pruebas aplicadas.
    Lista las pruebas del protocolo aplicadas en la sesión.
    """

    patient_id: UUIDStr
    evaluation_id: OptionalUUIDStr = None
    profesional_id: OptionalUUIDStr = None
    fecha: date = Field(default_factory=date.today)
    protocolo: str | None = None
    pruebas_aplicadas: list[str] = Field(default_factory=list)  # nombres de pruebas
    formato: str = "pdf"


class RemisionDTO(BaseModel):
    """
    Formulario de remisión/interconsulta.
    VBA: FormRemision.
    """

    patient_id: UUIDStr
    profesional_id: OptionalUUIDStr = None
    fecha: date = Field(default_factory=date.today)
    remite_a: str = ""  # "Neurología | Psiquiatría | Fonoaudiología"
    motivo_remision: str = ""
    diagnostico_presuntivo: str = ""
    codigo_cie10: str = ""
    observaciones: str | None = None
    formato: str = "pdf"


class RIPSRequestDTO(BaseModel):
    """Generación del reporte RIPS."""

    patient_id: UUIDStr
    fecha_inicio: date
    fecha_fin: date
    profesional_id: OptionalUUIDStr = None
    formato: str = "pdf"


class DocumentoResponseDTO(BaseModel):
    """Respuesta tras generar un documento."""

    id: str
    tipo: str
    titulo: str
    formato: str
    ruta_archivo: str | None
    fecha_emision: str
    descarga_url: str | None = None  # Endpoint para descargar el archivo


# ═══════════════════════════════════════════════════════════════
# BACKUP
# ═══════════════════════════════════════════════════════════════


class BackupRequestDTO(BaseModel):
    """Solicitud de backup manual."""

    destino: str | None = None  # Ruta destino (vacío = ruta por defecto)
    incluir_archivos_generados: bool = True
    notas: str | None = None


class BackupRestoreDTO(BaseModel):
    """Restaurar desde un backup."""

    ruta_backup: str
    confirmar: bool = Field(..., description="Debe ser True para proceder")


class BackupResponseDTO(BaseModel):
    id: str
    fecha: str
    ruta_destino: str | None
    tamano_kb: float
    total_pacientes: int
    total_evaluaciones: int
    exitoso: bool
    notas: str | None
    # Resultado de `PRAGMA integrity_check` sobre la copia ("ok" o mensaje
    # de corrupción). Backups que no pasan el check se marcan exitoso=False
    # y se eliminan físicamente para evitar restaurar datos corruptos.
    integridad: str | None = None
