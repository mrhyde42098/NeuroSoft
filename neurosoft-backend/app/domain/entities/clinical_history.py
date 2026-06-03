"""
app/domain/entities/clinical_history.py
=========================================
Entidad: Historia Clínica Neuropsicológica.

Mapea exactamente los 47 campos de la hoja DBHC del sistema VBA original,
organizados en 4 pestañas según la interfaz:
  - Pestaña 1: Desarrollo (riesgos pre/peri/postnatales)
  - Pestaña 2: Antecedentes Médicos
  - Pestaña 3: Familiar/Social/Funcional
  - Pestaña 4: Plan de Atención + Impresión Diagnóstica

Fuente: Análisis de ingeniería inversa de MISISTEMAV1.xlsm / TODO_EL_CODIGO.txt
        + Formato_Diligenciamiento_de_Historia_Clínica.pdf (NeuroSoft)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime


@dataclass
class HistoriaClinica:
    """
    Historia Clínica Neuropsicológica completa.

    Contiene toda la información clínica del paciente organizada
    en 4 pestañas temáticas, más los campos de observación clínica
    por dominio cognitivo (DBObser en el VBA).
    """

    # ── Identificación ────────────────────────────────────────────────
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""                        # FK → Paciente
    numero_documento: str = ""
    fecha_atencion: date | None = None
    codigo_cie10: str = "F809"

    # ═══════════════════════════════════════════════════════════════
    # PESTAÑA 1: DESARROLLO
    # Campos col 4-25 de DBHC (VBA: EMaterna, NoGestacion, ...)
    # ═══════════════════════════════════════════════════════════════

    motivo_consulta: str = "N/A"

    # Datos gestacionales
    edad_materna: str = "N/A"               # EMaterna — años
    no_gestacion: str = "N/A"              # NoGestacion — número de gestación
    riesgos: str = "N/A"                   # Riesgos — Si/No
    cual_riesgo: str = "N/A"               # Cual — descripción del riesgo
    estres_prenatal: str = "N/A"           # EstresP — tipo de estrés
    tipo_estres_prenatal: str = "N/A"      # TEPrenatal (col 46)
    ucin: str = "N/A"                      # UCIN (col 47) — Si/No/Días

    # Parto y nacimiento
    gestacion: str = "Término"             # Gestacion — Término/Pretérmino
    semanas: str = "N/A"                   # Semanas — semanas de gestación
    tipo_parto: str = "N/A"               # TParto — Vaginal/Cesárea/etc.
    peso: str = "N/A"                      # Peso — en gramos
    talla: str = "N/A"                     # Talla — en cm
    condiciones_neonatales: str = "N/A"    # CNeonatales — cianosis, hipoxia, etc.
    incubadora: str = "N/A"               # Incubadora — Si/No/días

    # Hitos de desarrollo motor (en meses)
    sostén_cefalico: str = "N/A"          # SosCefalico
    sedestacion: str = "N/A"              # Sedestacion
    gateo: str = "N/A"                    # Gateo
    marcha: str = "N/A"                   # Marcha

    # Hitos de desarrollo del lenguaje (en meses)
    balbuceo: str = "N/A"                 # Balbuceo
    primeras_palabras: str = "N/A"        # Palabras (1ras 10 palabras)
    habla_claro: str = "N/A"             # HablaClaro

    # Control de esfínteres
    control_anual: str = "N/A"           # Anal (esfínter anal)
    control_vesical: str = "N/A"         # Vesical

    # ═══════════════════════════════════════════════════════════════
    # PESTAÑA 2: ANTECEDENTES MÉDICOS
    # Campos col 26-36 de DBHC
    # ═══════════════════════════════════════════════════════════════

    patologicos_medicos: str = "N/A"      # Patologicos — enfermedades médicas
    sensoriales_motores: str = "N/A"      # Sensoriales — visión, audición, motor
    psiquiatricos: str = "N/A"            # Psiquiatricos — diagnósticos psiq.
    farmacologicos: str = "N/A"           # Farmacologicos — medicamentos actuales
    traumaticos: str = "N/A"              # Traumaticos — TCE, fracturas
    quirurgicos: str = "N/A"              # Quirurgicos — cirugías y anestesias
    toxicos: str = "N/A"                  # Toxicos — SPA, exposición química
    alergicos: str = "N/A"               # Alergicos — alergias atópicas
    terapeuticos: str = "N/A"            # Terapeuticos — PIR, terapias previas
    paraclinicos: str = "N/A"            # Paraclinicos — imágenes, EEG, genética
    familiares: str = "N/A"              # Familiares — antecedentes familiares

    # ═══════════════════════════════════════════════════════════════
    # PESTAÑA 3: FAMILIAR / SOCIAL / FUNCIONAL
    # Campos col 37-43 de DBHC
    # ═══════════════════════════════════════════════════════════════

    vive_con: str = "N/A"                # Vive — con quién vive, red de apoyo
    abc: str = "N/A"                     # ABC — ABVD, AIVD, AAVD
    escolar_laboral: str = "N/A"         # Escolar — rendimiento académico/laboral
    cognitivo: str = "N/A"              # Cognitivo — funciones cognitivas narrativas
    comportamiento_animo: str = "N/A"    # CompAnimo — comportamiento y estado de ánimo
    patron_sueno: str = "N/A"           # Sueno — patrón de sueño descriptivo
    patron_alimentacion: str = "N/A"     # Alimentacion — patrón alimentario

    # ═══════════════════════════════════════════════════════════════
    # PESTAÑA 4: PLAN DE ATENCIÓN
    # Campos col 44-45 de DBHC
    # ═══════════════════════════════════════════════════════════════

    plan_atencion: str = "N/A"           # PAtencion — plan terapéutico
    impresion_diagnostica_hc: str = "N/A"  # ImpDx — impresión inicial en HC
    hipotesis_pre_eval: str = "N/A"      # HipDx — hipótesis diagnóstica al cierre HC

    # ═══════════════════════════════════════════════════════════════
    # OBSERVACIONES CLÍNICAS POR DOMINIO
    # Campos col 4-12 de DBObser (formulario FormObsClinNPS en VBA)
    # Estos son los textos interpretativos escritos por el clínico
    # DESPUÉS de aplicar las pruebas.
    # ═══════════════════════════════════════════════════════════════

    obs_clinica_general: str = "N/A"     # ObsClinica — apariencia/conducta durante evaluación
    obs_atencion: str = "N/A"           # Atencion — interpretación de atención
    obs_memoria: str = "N/A"            # Memoria — interpretación de memoria
    obs_praxias_gnosias: str = "N/A"    # PGnosias — interpretación praxias/gnosias
    obs_lenguaje: str = "N/A"           # Lenguaje — interpretación de lenguaje
    obs_funciones_ejecutivas: str = "N/A"  # FEjecutivas — interpretación FE
    obs_emociones: str = "N/A"          # Emociones — esfera emocional/conductual
    obs_ci: str = "N/A"                 # CI — interpretación CI/funcionamiento intelectual
    obs_impresion_dx: str = "N/A"       # IDx — impresión diagnóstica neuropsicológica
    obs_funcionalidad: str = "N/A"      # Funcionalidad — AVD y autonomía
    obs_recomendaciones: str = "N/A"    # Recomendaciones terapéuticas

    # ── Auditoría ─────────────────────────────────────────────────
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # ── Helpers ───────────────────────────────────────────────────

    @property
    def tiene_riesgos_perinatales(self) -> bool:
        return self.riesgos.upper() in ("SI", "SÍ", "S", "YES")

    @property
    def tiene_ucin(self) -> bool:
        return self.ucin.upper() not in ("N/A", "NO", "-", "")

    def get_tab_desarrollo(self) -> dict:
        """Devuelve todos los campos de la pestaña Desarrollo."""
        return {
            "motivo_consulta": self.motivo_consulta,
            "edad_materna": self.edad_materna,
            "no_gestacion": self.no_gestacion,
            "riesgos": self.riesgos,
            "cual_riesgo": self.cual_riesgo,
            "estres_prenatal": self.estres_prenatal,
            "tipo_estres_prenatal": self.tipo_estres_prenatal,
            "ucin": self.ucin,
            "gestacion": self.gestacion,
            "semanas": self.semanas,
            "tipo_parto": self.tipo_parto,
            "peso": self.peso,
            "talla": self.talla,
            "condiciones_neonatales": self.condiciones_neonatales,
            "incubadora": self.incubadora,
            "sosten_cefalico": self.sostén_cefalico,
            "sedestacion": self.sedestacion,
            "gateo": self.gateo,
            "marcha": self.marcha,
            "balbuceo": self.balbuceo,
            "primeras_palabras": self.primeras_palabras,
            "habla_claro": self.habla_claro,
            "control_anual": self.control_anual,
            "control_vesical": self.control_vesical,
        }

    def get_tab_antecedentes(self) -> dict:
        return {
            "patologicos_medicos": self.patologicos_medicos,
            "sensoriales_motores": self.sensoriales_motores,
            "psiquiatricos": self.psiquiatricos,
            "farmacologicos": self.farmacologicos,
            "traumaticos": self.traumaticos,
            "quirurgicos": self.quirurgicos,
            "toxicos": self.toxicos,
            "alergicos": self.alergicos,
            "terapeuticos": self.terapeuticos,
            "paraclinicos": self.paraclinicos,
            "familiares": self.familiares,
        }

    def get_tab_familiar(self) -> dict:
        return {
            "vive_con": self.vive_con,
            "abc": self.abc,
            "escolar_laboral": self.escolar_laboral,
            "cognitivo": self.cognitivo,
            "comportamiento_animo": self.comportamiento_animo,
            "patron_sueno": self.patron_sueno,
            "patron_alimentacion": self.patron_alimentacion,
        }

    def get_observaciones(self) -> dict:
        return {
            "obs_clinica_general": self.obs_clinica_general,
            "obs_atencion": self.obs_atencion,
            "obs_memoria": self.obs_memoria,
            "obs_praxias_gnosias": self.obs_praxias_gnosias,
            "obs_lenguaje": self.obs_lenguaje,
            "obs_funciones_ejecutivas": self.obs_funciones_ejecutivas,
            "obs_emociones": self.obs_emociones,
            "obs_ci": self.obs_ci,
            "obs_impresion_dx": self.obs_impresion_dx,
            "obs_funcionalidad": self.obs_funcionalidad,
            "obs_recomendaciones": self.obs_recomendaciones,
        }


# ──────────────────────────────────────────────────────────────────
# ENTIDAD: EVOLUCIÓN TERAPÉUTICA
# Corresponde al formulario FormObsClinNPS2 / hoja DBETN en VBA
# ──────────────────────────────────────────────────────────────────

@dataclass
class EvolicionTerapia:
    """
    Registro de una sesión de seguimiento/rehabilitación.
    Hoja DBETN en el VBA: cols 5=Objetivos, 6=Actividades, 7=Ptrabajo, 8=Fecha
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    numero_documento: str = ""
    sesiones_orden: str = ""            # Número total de sesiones de la orden
    numero_orden: str = ""             # Número de la orden médica
    fecha_inicio: date | None = None
    fecha_sesion: date | None = None
    numero_sesion: str = "N/A"

    objetivos: str = "N/A"             # Objetivos de la sesión
    actividades: str = "N/A"           # Actividades realizadas
    plan_trabajo: str = "N/A"          # Plan para próxima sesión

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
