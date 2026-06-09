"""
app/infrastructure/database/orm_models.py — NeuroSoft v3 COMPLETO
Todas las tablas del sistema. Ver docstring completo en el archivo fuente.
"""

from __future__ import annotations

from datetime import UTC, datetime


def _utc_now():
    """Timezone-aware UTC now — reemplaza _utc_now (deprecado 3.12)."""
    return datetime.now(UTC)


from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.infrastructure.database.engine import Base


class PatientORM(Base):
    __tablename__ = "patients"
    __table_args__ = (UniqueConstraint("numero_documento", "fecha_atencion", name="uq_patient_visit"),)
    id = Column(String(36), primary_key=True)
    numero_documento = Column(String(20), nullable=False, index=True)
    tipo_documento = Column(String(5), nullable=False, default="CC")
    primer_nombre = Column(String(50), nullable=False)
    segundo_nombre = Column(String(50))
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50))
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(1), nullable=False)
    lugar_nacimiento = Column(String(100))
    estado_civil = Column(String(30))
    telefono = Column(String(20))
    correo = Column(String(100))
    direccion = Column(String(200))
    ciudad = Column(String(100))
    localidad = Column(String(100))
    estrato = Column(Integer)
    escolaridad = Column(String(50), nullable=False)
    lateralidad = Column(String(20), default="Diestro")
    ocupacion = Column(String(50))
    acompanante = Column(String(100))
    acompanante_relacion = Column(String(100), nullable=True)
    acompanante_telefono = Column(String(50), nullable=True)
    grupo_etnico = Column(String(50))
    profesional_id = Column(String(36), ForeignKey("professionals.id"))
    fecha_atencion = Column(Date, nullable=False, index=True)
    protocolo = Column(String(200))
    motivo_consulta = Column(Text)
    remite = Column(String(200))
    eps = Column(String(100))
    regimen = Column(String(30))
    pais = Column(String(60))
    orden_medica_no = Column(String(50))
    discapacidad = Column(String(100))
    codigo_rips = Column(String(10))
    cups = Column(String(20))
    finalidad_consulta = Column(String(50))
    numero_sesiones = Column(Integer, default=1)
    donante = Column(Boolean, default=False)
    # Vía de atención: comma-separated neuropsicologia|psicoterapia|rehabilitacion|mixto
    via_atencion = Column(String(120), nullable=False, default="mixto")
    # QW-6: etiquetas configurables (JSON array de strings)
    etiquetas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    is_active = Column(Boolean, default=True, nullable=False)
    # Campos de soft-delete (Resolución 1995 / Ley 1581 exigen archivo, no
    # borrado físico, de la historia clínica y datos relacionados)
    archived_at = Column(DateTime, nullable=True, index=True)
    archived_by = Column(String(36), nullable=True)
    archived_reason = Column(Text, nullable=True)
    # IMPORTANTE: se ELIMINÓ el cascade="all, delete-orphan".
    # Si se borra un paciente por SQL crudo, las evaluaciones/HC quedan
    # huérfanas (se detecta en auditoría). Para retirar un paciente del
    # flujo clínico usar soft-delete vía PatientRepository.archive().
    clinical_history = relationship("ClinicalHistoryORM", back_populates="patient", uselist=False)
    evaluations = relationship("EvaluationORM", back_populates="patient")
    evolucion = relationship("EvolTerapiaORM", back_populates="patient")
    professional = relationship("ProfessionalORM", back_populates="patients")
    documentos = relationship("DocumentoEmitidoORM", back_populates="patient")


class ClinicalHistoryORM(Base):
    """Historia Clínica completa — FormHC (DBHC 47 campos) + FormObsClinNPS (DBObser 11 campos)."""

    __tablename__ = "clinical_histories"
    __table_args__ = (UniqueConstraint("patient_id", "fecha_atencion", name="uq_hc_visit"),)
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    numero_documento = Column(String(20), nullable=False)
    fecha_atencion = Column(Date, nullable=False)
    codigo_cie10 = Column(String(10), default="F809")
    codigo_cie11 = Column(String(15), nullable=True)
    # Pestaña 1: Desarrollo
    motivo_consulta = Column(Text, default="N/A")
    edad_materna = Column(String(10), default="N/A")
    no_gestacion = Column(String(10), default="N/A")
    riesgos = Column(String(10), default="N/A")
    cual_riesgo = Column(Text, default="N/A")
    estres_prenatal = Column(String(100), default="N/A")
    gestacion = Column(String(30), default="N/A")
    semanas = Column(String(10), default="N/A")
    tipo_parto = Column(String(50), default="N/A")
    peso_gr = Column(String(20), default="N/A")
    talla_cm = Column(String(20), default="N/A")
    condiciones_neonatales = Column(Text, default="N/A")
    incubadora = Column(String(20), default="N/A")
    sosten_cefalico = Column(String(20), default="N/A")
    sedestacion = Column(String(20), default="N/A")
    gateo = Column(String(20), default="N/A")
    marcha = Column(String(20), default="N/A")
    balbuceo = Column(String(20), default="N/A")
    primeras_palabras = Column(String(20), default="N/A")
    habla_claro = Column(String(20), default="N/A")
    control_anual = Column(String(20), default="N/A")
    control_vesical = Column(String(20), default="N/A")
    tipo_estres_prenatal = Column(String(100), default="N/A")
    ucin = Column(String(30), default="N/A")
    # Pestaña 2: Antecedentes
    patologicos_medicos = Column(Text, default="N/A")
    sensoriales_motores = Column(Text, default="N/A")
    psiquiatricos = Column(Text, default="N/A")
    farmacologicos = Column(Text, default="N/A")
    traumaticos = Column(Text, default="N/A")
    quirurgicos = Column(Text, default="N/A")
    toxicos = Column(Text, default="N/A")
    alergicos = Column(Text, default="N/A")
    terapeuticos = Column(Text, default="N/A")
    paraclinicos = Column(Text, default="N/A")
    familiares = Column(Text, default="N/A")
    # Pestaña 3: Familiar/Social/Funcional
    vive_con = Column(Text, default="N/A")
    abc = Column(Text, default="N/A")
    escolar_laboral = Column(Text, default="N/A")
    cognitivo = Column(Text, default="N/A")
    comportamiento_animo = Column(Text, default="N/A")
    patron_sueno = Column(Text, default="N/A")
    patron_alimentacion = Column(Text, default="N/A")
    # Pestaña 4: Plan de atención
    plan_atencion = Column(Text, default="N/A")
    impresion_diagnostica_hc = Column(Text, default="N/A")
    hipotesis_pre_eval = Column(Text, nullable=True, default="N/A")
    # Observaciones clínicas (FormObsClinNPS / DBObser)
    obs_clinica_general = Column(Text, default="N/A")
    obs_atencion = Column(Text, default="N/A")
    obs_memoria = Column(Text, default="N/A")
    obs_praxias_gnosias = Column(Text, default="N/A")
    obs_lenguaje = Column(Text, default="N/A")
    obs_funciones_ejecutivas = Column(Text, default="N/A")
    obs_emociones = Column(Text, default="N/A")
    obs_ci = Column(Text, default="N/A")
    obs_impresion_dx = Column(Text, default="N/A")
    obs_funcionalidad = Column(Text, default="N/A")
    obs_recomendaciones = Column(Text, default="N/A")
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    # Optimistic locking — incrementa en cada save para detectar ediciones simultáneas
    row_version = Column(Integer, default=1, nullable=False)
    patient = relationship("PatientORM", back_populates="clinical_history")


class ClinicalHistoryVersionORM(Base):
    """
    Histórico de cambios en la Historia Clínica.
    Cada vez que se hace upsert, la versión anterior se guarda aquí.
    """

    __tablename__ = "clinical_history_versions"
    id = Column(String(36), primary_key=True)
    hc_id = Column(String(36), ForeignKey("clinical_histories.id"), nullable=False, index=True)
    patient_id = Column(String(36), nullable=False, index=True)
    version_num = Column(Integer, nullable=False)
    snapshot_json = Column(Text, nullable=False)  # HC completa serializada en JSON
    saved_by = Column(String(100))  # username quien guardó
    saved_at = Column(DateTime, default=_utc_now, nullable=False)
    hc = relationship("ClinicalHistoryORM", foreign_keys=[hc_id])


class EvaluationORM(Base):
    """Sesión de evaluación con puntajes brutos y resultados calculados en JSON."""

    __tablename__ = "evaluations"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    protocolo = Column(String(200), index=True)
    fecha = Column(Date, nullable=False, index=True)
    # Scoring data
    puntajes_brutos_json = Column(Text)  # {test_id: pd}
    resultados_json = Column(Text)  # List[ResultadoPrueba serializado]
    # Metadata del engine
    poblacion = Column(String(30))
    edad_display = Column(String(30))
    pruebas_realizadas = Column(Integer, default=0)
    pruebas_sin_dato = Column(Integer, default=0)
    advertencias_json = Column(Text)  # List[str]
    puntos_debiles_json = Column(Text)  # List[str] (test_nombres)
    puntos_fuertes_json = Column(Text)  # List[str]
    # Trazabilidad clínica: versión del baremo con la que se calificó
    baremo_version = Column(String(30))  # ej. "BD_NEURO_MAESTRA-2025"
    baremo_checksum = Column(String(64))  # hash SHA-256 del archivo baremo
    informe_inconcluso_cat = Column(String(80), nullable=True)
    informe_inconcluso_nota = Column(Text, nullable=True)
    # Control de versiones: solo el último registro de cada protocolo tiene is_latest=True
    is_latest = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    # ── Workflow de firma clínica (Res. 2654/2019 MinSalud: telesalud) ─────
    # Una evaluación firmada NO debe poder re-calcularse ni editarse: es el
    # equivalente digital de la firma manuscrita al cerrar la historia clínica.
    # Mientras `signed_at is None`, la evaluación está en "borrador" y el
    # clínico puede recalcular. Tras firmar, queda bloqueada.
    signed_at = Column(DateTime, nullable=True, index=True)
    signed_by = Column(String(36), nullable=True)  # user_id del clínico
    signed_by_label = Column(String(150), nullable=True)  # nombre_completo en el momento de firmar
    signature_sha256 = Column(String(64), nullable=True)  # hash del payload firmado (integridad)
    patient = relationship("PatientORM", back_populates="evaluations")


class EvolTerapiaORM(Base):
    """Evolución Terapia NPs (FormObsClinNPS2 / DBETN)."""

    __tablename__ = "evolucion_terapia"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    numero_documento = Column(String(20))
    sesiones_orden = Column(String(10))
    numero_orden = Column(String(50))
    fecha_inicio = Column(Date)
    fecha_sesion = Column(Date, nullable=False)
    numero_sesion = Column(String(10), default="N/A")
    objetivos = Column(Text, default="N/A")
    actividades = Column(Text, default="N/A")
    plan_trabajo = Column(Text, default="N/A")
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    # Soft-delete (Res. 1995 / Ley 1581 — la historia clínica no se borra
    # físicamente; se archiva con trazabilidad del responsable).
    archived_at = Column(DateTime, nullable=True, index=True)
    archived_by = Column(String(36), nullable=True)
    archived_reason = Column(Text, nullable=True)
    patient = relationship("PatientORM", back_populates="evolucion")


class ProfessionalORM(Base):
    """Profesionales evaluadores. Administrado desde Configuración."""

    __tablename__ = "professionals"
    id = Column(String(36), primary_key=True)
    nombre_completo = Column(String(150), nullable=False)
    titulo = Column(String(200))
    especialidad = Column(String(200))
    registro_profesional = Column(String(50))
    firma_base64 = Column(Text)
    sello_base64 = Column(Text)
    foto_base64 = Column(Text)  # avatar / foto profesional (base64 PNG/JPEG)
    email = Column(String(100))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utc_now)
    patients = relationship("PatientORM", back_populates="professional")
    documentos = relationship("DocumentoEmitidoORM", back_populates="profesional")


class ConfigInstitucionORM(Base):
    """Datos de la institución. Singleton id='1'."""

    __tablename__ = "config_institucion"
    id = Column(String(10), primary_key=True, default="1")
    nombre = Column(String(200), default="")
    nit = Column(String(30), default="")
    direccion = Column(String(300), default="")
    telefono = Column(String(50), default="")
    email = Column(String(100), default="")
    sitio_web = Column(String(200), default="")
    logo_base64 = Column(Text)
    ciudad = Column(String(100), default="Bogotá")
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class ConfigPrefsInformeORM(Base):
    """Preferencias visuales del informe. Singleton id='1'."""

    __tablename__ = "config_prefs_informe"
    id = Column(String(10), primary_key=True, default="1")
    fuente_cuerpo = Column(String(50), default="Calibri")
    fuente_titulos = Column(String(50), default="Calibri")
    tamano_fuente_cuerpo = Column(Integer, default=11)
    tamano_fuente_titulos = Column(Integer, default=13)
    color_primario = Column(String(10), default="#1a568c")
    color_secundario = Column(String(10), default="#2ec4b6")
    incluir_logo = Column(Boolean, default=True)
    incluir_firma = Column(Boolean, default=True)
    incluir_grafica_z = Column(Boolean, default=True)
    incluir_tabla_puntajes = Column(Boolean, default=True)
    formato_fecha = Column(String(20), default="DD/MM/YYYY")
    pie_pagina = Column(String(500), default="")
    nota_pie_informe = Column(
        Text,
        default=(
            "El diagnóstico aquí presentado se realiza a partir del perfil neuropsicológico "
            "analizado en la evaluación y es válido con la información presentada y reportada "
            "durante la consulta. El diagnóstico final se dará en el contexto de un análisis "
            "multidisciplinar, en particular, por parte del médico tratante. Lo anterior en "
            "acato del artículo 233 y 237 del Código de Procedimiento Civil Colombiano."
        ),
    )
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class CompanionORM(Base):
    """
    §M-7 Acompañante del paciente (madre/padre/cuidador/etc.) como entidad.

    Antes se metía como texto libre en HC. Ahora es entidad con FK al
    paciente para: contacto directo, autorización para responder escalas
    proxy (CDI-padres, SNAP-IV, GADS, etc.), trazabilidad legal.
    """

    __tablename__ = "companions"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    nombre_completo = Column(String(200), nullable=False)
    relacion = Column(String(50))  # madre|padre|hermano|conyuge|hijo|cuidador|tutor|otro
    documento = Column(String(30))
    telefono = Column(String(50))
    email = Column(String(100))
    autoriza_escalas = Column(Boolean, default=False)  # ¿puede responder escalas proxy?
    autoriza_contacto = Column(Boolean, default=True)  # ¿se le puede contactar por recordatorios?
    es_principal = Column(Boolean, default=False)  # acompañante "principal" de este paciente
    notas = Column(Text)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    patient = relationship("PatientORM", foreign_keys=[patient_id])


class ConfigSmtpORM(Base):
    """
    §QW-2 Configuración SMTP editable desde UI. Singleton id='1'.

    La contraseña se almacena cifrada con Fernet (clave derivada del JWT_SECRET).
    Si la fila NO existe, el sistema usa las variables de entorno NEUROSOFT_SMTP_*.
    Si existe, los valores de la fila TIENEN PRECEDENCIA sobre el env (override en runtime).
    """

    __tablename__ = "config_smtp"
    id = Column(String(10), primary_key=True, default="1")
    host = Column(String(120), default="")
    port = Column(Integer, default=587)
    user = Column(String(120), default="")
    password_enc = Column(Text)  # Fernet encrypted; NULL si no se guardó
    from_addr = Column(String(120), default="")
    from_name = Column(String(120), default="NeuroSoft")
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    timeout_s = Column(Integer, default=30)
    activo = Column(Boolean, default=True)
    ultima_prueba = Column(DateTime)  # cuándo se probó la última vez
    ultima_prueba_ok = Column(Boolean)  # resultado de la última prueba
    ultima_prueba_msg = Column(String(500))
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class ConfigEmailTemplateORM(Base):
    """
    §QW-3 Plantillas de correo editables por el clínico (override sobre DEFAULT_TEMPLATES).

    Una plantilla por tipo (informe | remision | evolucion | rips | otro).
    Si no hay fila para un tipo, se usa DEFAULT_TEMPLATES del email_service.
    Variables disponibles: {patient_nombre}, {patient_doc}, {fecha}, {profesional}, {institucion}.
    """

    __tablename__ = "config_email_templates"
    id = Column(String(10), primary_key=True)
    tipo = Column(String(30), nullable=False, unique=True, index=True)
    subject = Column(String(400), default="")
    body = Column(Text, default="")
    activo = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class DocumentoEmitidoORM(Base):
    """Registro de documentos generados: informes, comprobantes, recetarios, RIPS."""

    __tablename__ = "documentos_emitidos"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    tipo_documento = Column(String(50), nullable=False)
    # Tipos: informe_nps | comprobante_asistencia | comprobante_pruebas | remision | rips | certificado
    titulo = Column(String(200))
    formato = Column(String(10), default="pdf")
    ruta_archivo = Column(String(500))
    profesional_id = Column(String(36), ForeignKey("professionals.id"))
    fecha_emision = Column(DateTime, default=_utc_now, nullable=False)
    contenido_json = Column(Text)
    patient = relationship("PatientORM", back_populates="documentos")
    profesional = relationship("ProfessionalORM", back_populates="documentos")


class ConfigBackupScheduleORM(Base):
    """Configuración QW-8 — backup programado (fila única id=default)."""

    __tablename__ = "config_backup_schedule"
    id = Column(String(36), primary_key=True, default="default")
    enabled = Column(Boolean, default=True, nullable=False)
    frequency = Column(String(20), default="daily", nullable=False)
    hour = Column(Integer, default=2, nullable=False)
    minute = Column(Integer, default=0, nullable=False)
    mantener_total = Column(Integer, default=5, nullable=False)
    external_path = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class BackupRegistroORM(Base):
    """Historial de backups."""

    __tablename__ = "backup_registros"
    id = Column(String(36), primary_key=True)
    fecha = Column(DateTime, default=_utc_now, nullable=False)
    ruta_destino = Column(String(500))
    tamano_bytes = Column(Integer, default=0)
    total_pacientes = Column(Integer, default=0)
    total_evaluaciones = Column(Integer, default=0)
    exitoso = Column(Boolean, default=True)
    notas = Column(Text)
    tipo = Column(String(20), default="manual")


class UserORM(Base):
    """
    Usuario del sistema — para autenticación multi-profesional.
    Roles: admin | profesional | viewer
    """

    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    role = Column(String(20), nullable=False, default="profesional")
    # Vinculación opcional con tabla professionals
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    professional = relationship("ProfessionalORM", foreign_keys=[profesional_id])


class AppointmentORM(Base):
    """
    Agenda de citas del consultorio.
    Una cita puede estar: programada | confirmada | atendida | cancelada | no_asistio
    """

    __tablename__ = "appointments"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True)
    fecha = Column(Date, nullable=False, index=True)
    hora_inicio = Column(String(5), nullable=False)  # "HH:MM"
    hora_fin = Column(String(5))  # "HH:MM"
    tipo_cita = Column(String(50), default="evaluacion")
    # tipos: evaluacion | devolucion | terapia | seguimiento | otro
    motivo = Column(Text)
    estado = Column(String(20), default="programada", index=True)
    # estados: programada | confirmada | atendida | cancelada | no_asistio
    notas_internas = Column(Text)  # Notas del profesional (no visibles al paciente)
    recordatorio_env = Column(Boolean, default=False)  # ¿Se envió recordatorio?
    eps = Column(String(100))
    regimen = Column(String(40))
    autorizacion_no = Column(String(50))
    cups = Column(String(20))
    modalidad = Column(String(30))
    discapacidad = Column(String(100))
    contacto_telefono = Column(String(20))
    contacto_correo = Column(String(100))
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    # Relaciones
    patient = relationship("PatientORM", foreign_keys=[patient_id])
    profesional = relationship("ProfessionalORM", foreign_keys=[profesional_id])


class ObservationORM(Base):
    """
    Observaciones clínicas por dominio cognitivo.
    Un registro por (patient_id, evaluation_id, dominio).
    """

    __tablename__ = "observations"
    __table_args__ = (UniqueConstraint("patient_id", "evaluation_id", "dominio", name="uq_obs_domain"),)
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=True, index=True)
    dominio = Column(String(60), nullable=False)
    texto = Column(Text, nullable=False)
    created_at = Column(String(50), nullable=False)
    updated_at = Column(String(50), nullable=False)
    # Relaciones
    patient = relationship("PatientORM", foreign_keys=[patient_id])


class EstimuloORM(Base):
    """
    Imágenes / recursos gráficos asociados a una prueba o ítem específico.

    test_id: identificador de la prueba (e.g. "NiWiscDC", "NiFigHum").
    item_id: opcional, ítem dentro de la prueba.
    tipo: "imagen" | "lista_palabras" | "audio" | "otro".
    contenido_base64: el recurso serializado (data URL).
    """

    __tablename__ = "estimulos"
    id = Column(String(36), primary_key=True)
    test_id = Column(String(80), nullable=False, index=True)
    item_id = Column(String(40), nullable=True, index=True)
    nombre = Column(String(120), nullable=False)
    tipo = Column(String(20), default="imagen")
    mime_type = Column(String(60))
    contenido_base64 = Column(Text)  # data URL o base64 crudo
    descripcion = Column(Text)
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class InformeInconclusoORM(Base):
    """
    Registro de evaluaciones que quedan inconclusas por distintos motivos.
    Permite hacer seguimiento y cerrar el caso más adelante.

    motivo_id: identificador del catálogo (bateria_mas_segunda_orden,
        evaluacion_incompleta, evaluacion_reciente, cancelado_paciente).
    estado: 'abierto' | 'resuelto' | 'cerrado'.
    """

    __tablename__ = "informes_inconclusos"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=True, index=True)
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True)
    motivo_id = Column(String(60), nullable=False)
    motivo_titulo = Column(String(200))
    descripcion = Column(Text)
    accion_sugerida = Column(Text)
    plazo_dias = Column(Integer, default=15)
    fecha_creacion = Column(Date, nullable=False)
    fecha_limite = Column(Date)
    estado = Column(String(20), default="abierto", index=True)
    resuelto_en = Column(Date)
    notas_resolucion = Column(Text)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    # Relaciones
    patient = relationship("PatientORM", foreign_keys=[patient_id])


class ConsentimientoORM(Base):
    """
    Registros de consentimientos firmados por el paciente.
    Soporta Habeas Data (Ley 1581/2012) y consentimiento informado
    de evaluación neuropsicológica.

    tipo: 'habeas_data' | 'evaluacion' | 'tratamiento' | 'telepsicologia'.
    version_texto: versión del texto aceptado, para trazabilidad
        cuando el texto cambie en el tiempo.
    aceptado: booleano explícito (True cuando el paciente firma).
    firma_base64: imagen PNG de la firma dibujada o escaneada.
    """

    __tablename__ = "consentimientos"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True)
    tipo = Column(String(40), nullable=False, index=True)
    version_texto = Column(String(20), default="1.0")
    texto_completo = Column(Text)
    aceptado = Column(Boolean, default=False, nullable=False)
    firma_base64 = Column(Text)
    nombre_firmante = Column(String(200))
    relacion_firmante = Column(String(60))
    documento_firmante = Column(String(30))
    ip_registro = Column(String(45))
    dispositivo = Column(String(200))
    fecha_firma = Column(DateTime, default=_utc_now, nullable=False, index=True)
    fecha_revocado = Column(DateTime)
    motivo_revocado = Column(Text)
    modo_firma = Column(String(20), default="digital", nullable=False)  # digital | fisico
    adjunto_path = Column(String(500))  # ruta local cifrada del escaneado firmado
    requiere_adjunto = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    patient = relationship("PatientORM", foreign_keys=[patient_id])


class AuditLogORM(Base):
    """
    Bitácora de auditoría — Resolución 1995 de 1999.
    Registra toda creación/modificación/eliminación sobre datos clínicos
    para garantizar trazabilidad no repudiable.

    entity_type: nombre lógico ('patient','evaluation','clinical_history',
        'evolucion','consentimiento','auth','backup'...).
    action: 'create'|'update'|'delete'|'login'|'logout'|'export'|
        'backup'|'restore'|'view_sensitive'.
    changes: snapshot JSON del diff (campos modificados).
    """

    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=_utc_now, nullable=False, index=True)
    actor_id = Column(String(36), index=True)
    actor_label = Column(String(120))
    action = Column(String(40), nullable=False, index=True)
    entity_type = Column(String(40), nullable=False, index=True)
    entity_id = Column(String(36), index=True)
    summary = Column(String(300))
    changes = Column(Text)
    ip = Column(String(45))
    user_agent = Column(String(400))
    # Trazabilidad por request: correlaciona este asiento con los logs
    # del proceso (X-Request-ID) y otros asientos del mismo request.
    request_id = Column(String(64), index=True)


class AIConfigORM(Base):
    """
    Configuración de proveedor de IA por usuario.

    provider: 'gemini' | 'claude' | 'openai' | 'ollama' | 'auto'
    - 'auto' = intenta nube (si hay API key) → cae en Ollama local
    - 'ollama' = siempre local (127.0.0.1:11434)
    - el resto usa su API key correspondiente

    api_key: se guarda tal cual (el bundle es local, NO se sube a la nube).
             Idealmente se cifraría con Windows DPAPI — pendiente.
    model:   nombre específico del modelo (ej. gemini-1.5-flash,
             claude-3-5-sonnet-20241022, llama3.1:8b).
    ollama_url: URL de Ollama local (por defecto http://127.0.0.1:11434).
    """

    __tablename__ = "ai_config"
    user_id = Column(String(36), primary_key=True)
    provider = Column(String(20), default="auto", nullable=False)
    api_key = Column(Text)  # opcional si provider=ollama
    model = Column(String(80))
    ollama_url = Column(String(200), default="http://127.0.0.1:11434")
    # Endpoint OpenAI-compatible para proveedores en línea como MedGemma
    # (OpenRouter, Hugging Face TGI, Vertex proxy, etc.). Vacío = OpenAI oficial.
    openai_base_url = Column(String(300))
    temperature = Column(Integer, default=70)  # /100 → 0.70
    max_tokens = Column(Integer, default=1024)
    enable_cloud = Column(Boolean, default=True)  # si False → forzar Ollama
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class SharedReportORM(Base):
    """
    Link público con token para compartir informes (telemedicina).

    token: identificador opaco (uuid sin guiones) que sustituye la URL
           al paciente / remitente; nunca se expone el eval_id real.
    expires_at: fecha/hora de expiración; vencido → 410 Gone.
    revoked: desactivación manual por el clínico.
    viewed_count: cuántas veces fue abierto (para auditoría).
    password_hash: opcional — si se pone, el viewer pide contraseña.
    scope: qué mostrar ('summary' | 'full' | 'iq_only').
    """

    __tablename__ = "shared_reports"
    id = Column(String(36), primary_key=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    evaluation_id = Column(String(36), nullable=False, index=True)
    patient_id = Column(String(36), nullable=False, index=True)
    created_by = Column(String(36), nullable=False)
    scope = Column(String(20), default="summary")
    password_hash = Column(String(200))  # bcrypt, opcional
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, default=False, index=True)
    viewed_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime)
    created_at = Column(DateTime, default=_utc_now, nullable=False)


class RehabActivityCatalogORM(Base):
    """
    Catálogo de actividades de rehabilitación cognitiva disponibles.
    Cada actividad tiene un slug único, un dominio cognitivo objetivo
    y parámetros por defecto que el clínico puede sobre-escribir al
    asignarla.

    provider:
      - 'internal'   → ejecuta en el frontend de NeuroSoft
      - 'ecognitiva' → enlace externo (iframe o ventana nueva)
      - 'manual'     → solo registro administrativo (papel y lápiz)
    """

    __tablename__ = "rehab_activity_catalog"
    id = Column(String(36), primary_key=True)
    slug = Column(String(60), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    dominio = Column(String(60), nullable=False, index=True)
    # dominios: atencion | memoria | funciones_ejecutivas | lenguaje |
    #           visoespacial | velocidad_procesamiento | memoria_trabajo
    dificultad_default = Column(Integer, default=1)  # 1=fácil, 5=difícil
    duracion_min = Column(Integer, default=10)
    descripcion = Column(Text)
    instrucciones = Column(Text)
    parametros_json = Column(Text)  # JSON: parámetros por defecto
    provider = Column(String(20), default="internal", nullable=False)
    external_url = Column(String(500))  # solo si provider != 'internal'
    activo = Column(Boolean, default=True, nullable=False, index=True)
    orden = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utc_now, nullable=False)


class RehabPlanORM(Base):
    """
    Plan individualizado de rehabilitación neuropsicológica.

    Tras una evaluación, el clínico genera un plan que define:
      - Dominios a intervenir
      - Frecuencia (sesiones/semana)
      - Objetivos terapéuticos
      - Actividades asignadas

    Como cualquier documento clínico, soporta firma digital
    (mismo patrón que EvaluationORM): tras firmar, hash SHA-256 del
    payload se guarda y el plan queda inmutable.
    """

    __tablename__ = "rehab_plans"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    evaluation_id = Column(String(36), nullable=True, index=True)
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin_estimada = Column(Date, nullable=True)
    frecuencia_semanal = Column(Integer, default=2)
    objetivos = Column(Text)  # texto libre del clínico
    dominios_json = Column(Text)  # List[str] dominios objetivo
    actividades_json = Column(Text)  # List[{slug, dificultad, parametros}]
    notas = Column(Text)
    estado = Column(String(20), default="activo", nullable=False, index=True)
    # estados: borrador | activo | pausado | finalizado | archivado
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    # ── Workflow de firma ─────────────────────────────────
    signed_at = Column(DateTime, nullable=True, index=True)
    signed_by = Column(String(36), nullable=True)
    signed_by_label = Column(String(150), nullable=True)
    signature_sha256 = Column(String(64), nullable=True)
    # Soft-delete
    archived_at = Column(DateTime, nullable=True, index=True)
    archived_by = Column(String(36), nullable=True)


class RehabSessionORM(Base):
    """
    Cada vez que el paciente realiza una actividad de rehabilitación
    se inserta una fila aquí. Sirve para:
      - Rastrear adherencia (¿cuántas sesiones hizo esta semana?)
      - Medir evolución (score por dominio en el tiempo)
      - Generar reportes

    modo:
      - 'en_consulta'  → paciente con clínico al lado
      - 'tarea_casa'   → paciente solo en casa (asíncrono)
      - 'telerehab'    → videollamada en vivo
    """

    __tablename__ = "rehab_sessions"
    id = Column(String(36), primary_key=True)
    plan_id = Column(String(36), ForeignKey("rehab_plans.id"), nullable=True, index=True)
    activity_id = Column(String(36), ForeignKey("rehab_activity_catalog.id"), nullable=False, index=True)
    activity_slug = Column(String(60), nullable=False, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    ts_inicio = Column(DateTime, default=_utc_now, nullable=False, index=True)
    ts_fin = Column(DateTime, nullable=True)
    duracion_seg = Column(Integer, nullable=True)
    parametros_json = Column(Text)  # parámetros con los que se ejecutó
    resultado_json = Column(Text)  # score, aciertos, errores, RT, etc.
    score = Column(Integer, nullable=True, index=True)
    aciertos = Column(Integer, nullable=True)
    errores = Column(Integer, nullable=True)
    modo = Column(String(20), default="en_consulta", nullable=False, index=True)
    origen_token = Column(String(64), nullable=True)
    notas_clinico = Column(Text)
    created_at = Column(DateTime, default=_utc_now, nullable=False)


class RehabShareLinkORM(Base):
    """
    Link público con token para que el paciente realice actividades en
    casa o desde otro dispositivo, sin necesidad de credenciales.

    Patrón análogo a SharedReportORM (telemedicina) — pero apunta a un
    plan de rehabilitación, no a un informe.
    """

    __tablename__ = "rehab_share_links"
    id = Column(String(36), primary_key=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    plan_id = Column(String(36), nullable=False, index=True)
    patient_id = Column(String(36), nullable=False, index=True)
    created_by = Column(String(36), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, default=False, index=True)
    sessions_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=_utc_now, nullable=False)


class TokenBlacklistORM(Base):
    """
    Revocación de JWTs — complemento necesario a la firma digital y al
    resto de controles de auditoría (Res. 1995/99 y Ley 1581/12).

    Un JWT no puede ser "invalidado" por su sola estructura criptográfica
    (sigue siendo válido hasta `exp`). Para que el botón *Cerrar sesión*
    sea real y para poder echar a un usuario por seguridad,
    guardamos el identificador único del token (`jti`) en esta tabla.
    El middleware de auth consulta este set en cada request.

    reason: 'logout' | 'password_change' | 'admin_revoked' | 'compromised'
    """

    __tablename__ = "token_blacklist"
    jti = Column(String(64), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    revoked_at = Column(DateTime, default=_utc_now, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    reason = Column(String(40), default="logout", nullable=False)


class EmailLogORM(Base):
    """
    Bitácora de correos enviados (informes, remisiones, evoluciones).
    Res. 1995/99 exige trazabilidad de cada entrega documental al asegurador /
    paciente / entidad remisora. Este log responde a esa exigencia y cubre la
    paridad con el sistema VBA legacy (SubEnvioOutlook).

    status: 'sent' | 'failed'
    tipo:   'informe' | 'evolucion' | 'remision' | 'rips' | 'otro'
    """

    __tablename__ = "email_logs"
    id = Column(String(36), primary_key=True)
    ts = Column(DateTime, default=_utc_now, nullable=False, index=True)
    actor_id = Column(String(36), index=True)
    actor_label = Column(String(120))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=True, index=True)
    evaluation_id = Column(String(36), nullable=True, index=True)
    documento_id = Column(String(36), nullable=True, index=True)
    tipo = Column(String(30), default="informe", nullable=False, index=True)
    recipient_to = Column(String(500), nullable=False)
    recipient_cc = Column(String(500))
    recipient_bcc = Column(String(500))
    subject = Column(String(400), nullable=False)
    body_preview = Column(Text)
    attachments_json = Column(Text)  # List[{"filename": ..., "size": N}]
    status = Column(String(20), default="sent", nullable=False, index=True)
    error_message = Column(String(500))
    smtp_host = Column(String(120))
    smtp_user = Column(String(120))


# ═══════════════════════════════════════════════════════════════════════
# MÓDULO PSICOLOGÍA CLÍNICA (sesiones terapéuticas)
# ─────────────────────────────────────────────────────────────────────────
# Nuevo en la fase de expansión: NeuroSoft ahora también soporta
# psicoterapia recurrente, no solo evaluación. Estos modelos conviven con
# los de evaluación; ambos comparten paciente, profesional y agenda.
#
# Ver: ROADMAP_EXPANSION.md → Pilar 2 (Sesiones de Psicología Clínica)
# ═══════════════════════════════════════════════════════════════════════


class TherapyPlanORM(Base):
    """
    Plan terapéutico de un paciente. Un plan agrupa varias sesiones y
    objetivos terapéuticos hacia una meta clínica (CBT, sistémica, etc.).
    Un paciente puede tener varios planes a lo largo del tiempo (uno
    activo por proceso). Se cierra al alta, abandono o derivación.
    """

    __tablename__ = "therapy_plans"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True, index=True)
    enfoque_principal = Column(
        String(40)
    )  # cbt|sistemica|psicoanalitica|humanistica|emdr|act|mindfulness|logoterapia|gestalt|otro
    diagnostico_principal = Column(String(20))  # código CIE-10
    diagnostico_secundario = Column(String(20))
    codigo_cie11 = Column(String(15), nullable=True)
    motivo_consulta = Column(Text)
    duracion_estimada_sesiones = Column(Integer)  # sesiones estimadas por el clínico
    fecha_inicio = Column(DateTime, default=_utc_now, nullable=False, index=True)
    fecha_revision = Column(DateTime)  # próxima revisión del plan
    fecha_cierre = Column(DateTime)
    motivo_cierre = Column(String(40))  # alta|abandono|derivacion|cambio_terapeuta
    nota_cierre = Column(Text)
    estado = Column(String(20), default="activo", nullable=False, index=True)
    # activo | pausado | cerrado
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class TherapyObjectiveORM(Base):
    """
    Objetivo terapéutico SMART asociado a un plan. Los objetivos se
    trabajan a lo largo de sesiones y permiten medir progreso.
    """

    __tablename__ = "therapy_objectives"
    id = Column(String(36), primary_key=True)
    plan_id = Column(String(36), ForeignKey("therapy_plans.id"), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    criterios_medibles = Column(Text)  # cómo se sabe que se cumple
    fecha_inicio = Column(DateTime, default=_utc_now, nullable=False)
    fecha_meta = Column(DateTime)
    estado = Column(String(20), default="activo", nullable=False, index=True)
    # activo | cumplido | modificado | abandonado
    progreso_pct = Column(Integer, default=0)  # 0-100
    orden = Column(Integer, default=0)  # para mostrar ordenados
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)


class TherapySessionORM(Base):
    """
    Sesión terapéutica individual. Notas SOAP (Subjective/Objective/
    Assessment/Plan), modalidad, riesgo suicida, alianza terapéutica
    auto-reportada y estado emocional inicio/fin.
    """

    __tablename__ = "therapy_sessions"
    id = Column(String(36), primary_key=True)
    plan_id = Column(String(36), ForeignKey("therapy_plans.id"), nullable=True, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True, index=True)
    fecha = Column(DateTime, default=_utc_now, nullable=False, index=True)
    duracion_min = Column(Integer, default=50)
    modalidad = Column(String(20), default="presencial", nullable=False, index=True)
    # presencial | telepsicologia | telefonica
    enfoque_sesion = Column(String(40))  # puede sobrescribir el del plan en sesiones específicas
    # ─── Notas SOAP ────────────────────────────────────────────
    soap_subjetivo = Column(Text)  # S: lo que el paciente reporta
    soap_objetivo = Column(Text)  # O: lo que el clínico observa
    soap_analisis = Column(Text)  # A: interpretación clínica
    soap_plan = Column(Text)  # P: próximos pasos
    # ─── Métricas de sesión ────────────────────────────────────
    objetivos_trabajados = Column(Text)  # JSON list[objective_id]
    tareas_asignadas = Column(Text)  # texto libre o JSON
    medicacion_actual = Column(Text)  # cambios reportados
    riesgo_suicida = Column(String(30), default="ninguno", index=True)
    # ninguno | ideacion_pasiva | ideacion_activa | plan | intento_reciente
    riesgo_observaciones = Column(Text)
    alianza_terapeutica = Column(Integer)  # 1-5, auto-reportada por el clínico
    estado_emocional_ini = Column(Integer)  # 0-10 reportado por el paciente al inicio
    estado_emocional_fin = Column(Integer)  # 0-10 al cierre
    # ─── Firma ────────────────────────────────────────────────
    locked_at = Column(DateTime)  # firma terapéutica (no editable después)
    locked_by = Column(String(36))
    signature_sha256 = Column(String(64))  # hash del contenido al firmar
    # ─── Auditoría ───────────────────────────────────────────
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    archived_at = Column(DateTime)
    archived_reason = Column(Text)


class RiskAssessmentORM(Base):
    """
    Evaluación de riesgo suicida (C-SSRS o similar). Cada evaluación se
    guarda separada para trazabilidad longitudinal del riesgo a lo largo
    del tratamiento. Crítico por implicaciones legales y clínicas.
    """

    __tablename__ = "risk_assessments"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("therapy_sessions.id"), nullable=True, index=True)
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True)
    fecha = Column(DateTime, default=_utc_now, nullable=False, index=True)
    instrumento = Column(String(30), default="c_ssrs")  # c_ssrs | sad_persons | clinical_judgment
    nivel = Column(String(20), nullable=False, index=True)
    # ninguno | leve | moderado | alto | inminente
    ideacion_suicida = Column(Boolean, default=False)
    ideacion_con_plan = Column(Boolean, default=False)
    intento_previo = Column(Boolean, default=False)
    intento_reciente_30d = Column(Boolean, default=False)
    factores_protectores = Column(Text)
    factores_riesgo = Column(Text)
    plan_seguridad = Column(Text)
    derivacion_emergencia = Column(Boolean, default=False)
    nota_clinica = Column(Text)
    created_at = Column(DateTime, default=_utc_now, nullable=False)


class TherapyTaskORM(Base):
    """
    Tarea terapéutica ("tarea-casa") asignada entre sesiones.

    Las tareas inter-sesión son uno de los componentes con mejor evidencia
    en TCC (Kazantzis et al., 2016; meta-análisis: g=0.48 sobre outcome
    clínico). El paciente las completa y el clínico revisa en sesión.

    Tipos comunes:
      - registro_pensamientos  (TCC: detección de distorsiones)
      - registro_emocional     (regulación emocional, DBT)
      - autorregistro_conducta (frecuencia/intensidad de un síntoma)
      - exposicion             (jerarquía de ansiedad)
      - activacion_conductual  (depresión)
      - habilidades_DBT        (mindfulness, tolerancia al malestar)
      - psicoeducacion         (lectura/video con preguntas)
      - libre                  (texto libre)
    """

    __tablename__ = "therapy_tasks"
    id = Column(String(36), primary_key=True)
    plan_id = Column(String(36), ForeignKey("therapy_plans.id"), nullable=True, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("therapy_sessions.id"), nullable=True, index=True)
    profesional_id = Column(String(36), ForeignKey("professionals.id"), nullable=True, index=True)
    # ─── Definición de la tarea ─────────────────────────────────
    tipo = Column(String(30), nullable=False, default="libre", index=True)
    titulo = Column(String(120), nullable=False)
    descripcion = Column(Text)  # instrucciones detalladas
    objetivo_id = Column(String(36), ForeignKey("therapy_objectives.id"), nullable=True)
    # ─── Calendario ─────────────────────────────────────────────
    fecha_asignacion = Column(DateTime, default=_utc_now, nullable=False, index=True)
    fecha_limite = Column(DateTime)
    frecuencia = Column(String(20))  # diaria | varias_semana | semanal | unica
    # ─── Estado y entrega ───────────────────────────────────────
    estado = Column(String(20), default="pendiente", nullable=False, index=True)
    # pendiente | en_progreso | completada | parcial | omitida
    completada_en = Column(DateTime)
    respuesta = Column(Text)  # texto del paciente / autorregistro
    adherencia_pct = Column(Integer)  # 0-100 cuántas instancias cumplió
    dificultad_pct = Column(Integer)  # 0-100 reportado por paciente
    utilidad_pct = Column(Integer)  # 0-100 reportado por paciente
    # ─── Revisión por el clínico ────────────────────────────────
    revisada_en = Column(DateTime)
    nota_clinico = Column(Text)
    # ─── Auditoría ──────────────────────────────────────────────
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    archived_at = Column(DateTime)


class AILogORM(Base):
    """
    Registro de cada llamada al Asistente IA — trazabilidad clínica.

    §ai-log (2026-05-18): cuando el clínico usa IA para asistir un informe
    (mejorar redacción, sugerir dx, generar recomendaciones), queda registro
    de qué prompt se usó, qué proveedor respondió, longitud in/out. NO se
    guarda el contenido completo del prompt ni la respuesta (eso sería PHI
    en algunos casos) — solo metadata útil para auditoría de Resolución 1995.

    Si en una auditoría posterior se detecta que la IA generó algo
    cuestionable en un informe, se puede rastrear cuándo se usó qué prompt.
    """

    __tablename__ = "ai_logs"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=True, index=True)
    evaluation_id = Column(String(36), nullable=True, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    # ─── Qué se invocó ──────────────────────────────────────────
    prompt_id = Column(String(60), nullable=False, index=True)
    # mejorar_observacion_clinica | sugerir_dx_dsm5 | explicar_discrepancia |
    # redactar_recomendaciones | narrativa_integradora | revisar_pediatrico |
    # improve | narrate | chat
    endpoint = Column(String(40))  # "/specialized" | "/improve" | "/narrate" | "/chat"
    # ─── Proveedor / modelo usado ───────────────────────────────
    provider = Column(String(20))  # gemini | claude | openai | ollama
    model = Column(String(60))
    # ─── Métricas (sin contenido) ───────────────────────────────
    input_length = Column(Integer)
    output_length = Column(Integer)
    duration_ms = Column(Integer)
    tokens_in = Column(Integer)
    tokens_out = Column(Integer)
    # ─── Estado ────────────────────────────────────────────────
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text)
    # Si el output se aplicó al informe (clínico aceptó la sugerencia).
    applied_to_report = Column(Boolean, default=False)
    # ─── Auditoría ──────────────────────────────────────────────
    created_at = Column(DateTime, default=_utc_now, nullable=False, index=True)


# ═════════════════════════════════════════════════════════════════
# §F2 — Referencias bibliográficas (Sistema de documentación)
# ═════════════════════════════════════════════════════════════════


class ReferenciaBibliograficaORM(Base):
    """Catálogo de referencias bibliográficas verificadas."""

    __tablename__ = "referencias_bibliograficas"

    id = Column(String(36), primary_key=True)
    tipo = Column(String(20), nullable=False)  # libro, articulo, manual, guia, ley, escala, protocolo
    autores = Column(String(300), nullable=False)
    titulo = Column(String(500), nullable=False)
    anio = Column(Integer, nullable=False)
    journal = Column(String(200))
    doi = Column(String(100))
    isbn = Column(String(30))
    url = Column(String(500))
    cita_apa = Column(String(800))
    disciplina = Column(String(30), nullable=False)  # neuropsicologia, psicologia_clinica, ambas
    categoria = Column(String(50))
    tags = Column(Text)  # JSON array de strings
    resumen = Column(Text)
    nivel_evidencia = Column(String(5))  # A, B, C, D (APA Division 12)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
