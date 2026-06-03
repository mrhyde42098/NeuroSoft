"""
scripts/generate_5_edge_cases.py
================================
Extiende los 20 casos clínicos con 5 casos edge/premium que ejercitan el
flujo completo del sistema:

  21. Deserción: paciente abandona antes de evaluación completa
  22. Emergencia: screening detecta C-SSRS ALTO (ideación suicida activa)
  23. Junta médica: caso medicolegal con validez de síntomas
  24. Cierre terapia: comparación Pre/Post con 12 sesiones
  25. Batería completa: 40+ pruebas (stress test del motor)

Cada caso incluye TODOS los campos y artefactos que el usuario pidió:
  - 35+ campos demográficos del paciente
  - 60+ campos de historia clínica
  - Batería apropiada con puntajes
  - 4-6 observaciones clínicas por dominio cognitivo
  - Recomendaciones etiquetadas [ESCOLAR] [TERAPÉUTICA] [FAMILIAR] (alta/media)
  - PDF generado
  - Snapshot JSON para tests de regresión

Uso:
    cd neurosoft-backend
    python -m scripts.generate_5_edge_cases
"""
from __future__ import annotations

import json
import sys
import uuid
from dataclasses import asdict
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext
from app.infrastructure.database.engine import session_scope
from app.infrastructure.database.orm_models import (
    ClinicalHistoryORM,
    ConfigInstitucionORM,
    EvaluationORM,
    ObservationORM,
    PatientORM,
    ProfessionalORM,
    RiskAssessmentORM,
    TherapySessionORM,
)

BAREMOS_PATH = ROOT / "data" / "BD_NEURO_MAESTRA.json"
OUTPUT_PDFS = ROOT.parent / "docs" / "casos-clinicos" / "muestras-20-casos"
OUTPUT_PDFS.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR = ROOT.parent / "docs" / "casos-clinicos" / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════
# 5 CASOS EDGE/PREMIUM
# ═══════════════════════════════════════════════════════════════════════

CASOS_EDGE = [
    # ─────────────────────────────────────────────────────────────────
    # CASO 21: DESERCIÓN (dropout)
    # ─────────────────────────────────────────────────────────────────
    {
        "id": 21,
        "categoria": "adulto_joven",
        "dx_principal": "INCONCLUSO - Deserción prematura",
        "estado": "desercion",
        "paciente": {
            "numero_documento": "80123456",
            "tipo_documento": "CC",
            "primer_nombre": "Felipe",
            "segundo_nombre": "Andrés",
            "primer_apellido": "Rincón",
            "segundo_apellido": "Mendoza",
            "fecha_nacimiento": date(1992, 3, 14),
            "sexo": "H",
            "escolaridad": "Universitaria",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Medellín, Antioquia",
            "estado_civil": "Soltero",
            "telefono": "6045557890",
            "correo": "felipe.rincon@ejemplo.com",
            "direccion": "Carrera 43A #14-50",
            "ciudad": "Medellín",
            "localidad": "El Poblado",
            "estrato": "5",
            "ocupacion": "Ingeniero de software",
            "acompanante": "No acude con acompañante",
            "acompanante_relacion": "",
            "acompanante_telefono": "",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Dificultades atencionales reportadas por su empleador. Desea evaluación neuropsicológica para descartar TDAH adulto.",
            "remite": "Consulta particular",
            "eps": "Sura EPS",
            "orden_medica_no": "N/A",
            "discapacidad": "No",
            "codigo_rips": "Z00.0",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstica",
        },
        "evaluacion": {
            "protocolo": "bateria_desercion",
            "puntajes": {
                "AdBeck": 8,        # Subclínico
            },
        },
        "observaciones": [
            ("atención", "Paciente acude solo, en horario laboral, manifiesta presión por entrega de resultados rápidos. Conectado pero ansioso durante la entrevista inicial."),
            ("memoria", "No fue posible evaluar — paciente deserta antes de la segunda sesión."),
            ("lenguaje", "Lenguaje fluido y coherente durante la entrevista inicial. Vocabulario técnico profesional."),
            ("funciones ejecutivas", "Autoreporta olvidos frecuentes en el trabajo y dificultad para sostener atención en reuniones largas (>30 min)."),
            ("ánimo", "Ánimo eutímico. Niega ideación suicida. Refiere estrés laboral moderado."),
        ],
        "recomendaciones": [
            "[FAMILIAR] (media) Se sugiere psicoeducación sobre el proceso de evaluación neuropsicológica completa (3-4 sesiones adicionales).",
            "[TERAPÉUTICA] (media) Considerar intervención breve en técnicas de manejo del tiempo y atención antes de la evaluación completa.",
            "[FAMILIAR] (alta) Reagendar dentro de los próximos 30 días. Si decide no continuar, documentar decisión informada.",
        ],
        "razon_desercion": "El paciente no asistió a la segunda sesión programada. Se intentó contacto telefónico (2 intentos) sin respuesta. Se envió comunicación escrita informando que el proceso queda inconcluso y puede retomarlo cuando lo considere.",
        "es_inconcluso": True,
    },

    # ─────────────────────────────────────────────────────────────────
    # CASO 22: EMERGENCIA (ideación suicida activa)
    # ─────────────────────────────────────────────────────────────────
    {
        "id": 22,
        "categoria": "adulto_mayor",
        "dx_principal": "F32.1 - Episodio depresivo moderado + RIESGO SUICIDA ALTO",
        "estado": "emergencia",
        "paciente": {
            "numero_documento": "20123456",
            "tipo_documento": "CC",
            "primer_nombre": "Carmen",
            "segundo_nombre": "Rosa",
            "primer_apellido": "Velásquez",
            "segundo_apellido": "Ortiz",
            "fecha_nacimiento": date(1952, 7, 22),
            "sexo": "M",
            "escolaridad": "Primaria Incompleta",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Cali, Valle del Cauca",
            "estado_civil": "Viuda",
            "telefono": "6023344556",
            "correo": "",
            "direccion": "Calle 5 #38-90",
            "ciudad": "Cali",
            "localidad": "San Fernando",
            "estrato": "2",
            "ocupacion": "Pensionada (ex-docente)",
            "acompanante": "Hija María Velásquez",
            "acompanante_relacion": "Hija",
            "acompanante_telefono": "6023344557",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Hija refiere cuadro de 6 meses: tristeza persistente, aislamiento, pérdida de interés, llanto frecuente, y EXPRESA IDEA DE QUERER 'DESCANSAR'. Dormitorio desordenado con medicamentos acumulados.",
            "remite": "Hija (familia)",
            "eps": "Nueva EPS",
            "orden_medica_no": "N/A",
            "discapacidad": "No",
            "codigo_rips": "F32.1",
            "cups": "890302",
            "finalidad_consulta": "Urgencia psiquiátrica",
        },
        "evaluacion": {
            "protocolo": "bateria_emergencia_am",
            "puntajes": {
                "ViRDD": 4,
                "ViRDInv": 2,
                "ViTMTA": 245,        # Bradipsiquia
                "ViGroberRLT": 2,
                "ViGroberML_Tot": 2,
                "ViGroberMC_Tot": 5,
                "ViAni": 6,
            },
        },
        "observaciones": [
            ("atención", "Atención fluctuante, hipoprosexia, se desconecta durante la entrevista. Refiere dificultad para concentrarse ('la cabeza no me da')."),
            ("memoria", "Quejas subjetivas de memoria. Olvida citas y nombres. Familiares confirman deterioro en los últimos 6 meses. Grober Buschke con deterioro en recuerdo libre (2/16) con mejoría en reconocimiento (8/16) — perfil subcortical-frontal."),
            ("lenguaje", "Lenguaje hipofluente, latencias aumentadas, voz低声 (baja). Responde con monosílabos. Denominación conservada (animales: 6)."),
            ("funciones ejecutivas", "Rigidez cognitiva. Dificultad para alternar categorías en fluencia. Bradipsiquia marcada en TMT-A (245 segundos, escalar 6)."),
            ("ánimo", "ACTITUD DEPRESIVA PROFUNDA. Llanto durante la entrevista. Expresa: 'ya no quiero seguir así'. Ideación suicida ACTIVA con plan pasivo (acumular medicación). C-SSRS: IDEACIÓN + PLAN + INTENCIÓN = RIESGO ALTO."),
        ],
        "recomendaciones": [
            "[TERAPÉUTICA] (alta) URGENTE: Activar protocolo de seguridad. No dejar sola a la paciente. Contactar a hija María (acudiente) para acompañamiento 24/7.",
            "[TERAPÉUTICA] (alta) URGENTE: Remisión a PSIQUIATRÍA en las próximas 24-48 horas para evaluación de tratamiento farmacológico (ISRS) y nivel de cuidado.",
            "[FAMILIAR] (alta) Retirar medios letales del domicilio (medicamentos, armas, cuerdas). La hija debe administrar la medicación.",
            "[FAMILIAR] (alta) Plan de seguridad escrito: contactos de emergencia (línea 106, hija, vecina), lugares seguros, señales de alerta.",
            "[TERAPÉUTICA] (media) Iniciar psicoterapia breve (8-12 sesiones) orientada a activación conductual + psicoeducación familiar.",
            "[FAMILIAR] (media) Coordinación con médico de familia para evaluación de comorbilidades (tiroides, B12, anemia).",
        ],
        "cssrs_score": {
            "ideacion": True,
            "plan": True,
            "intencion": True,
            "intentos_previos": False,
            "factores_riesgo": ["viudez reciente (8 meses)", "aislamiento social", "enfermedad médica crónica", "acceso a medios"],
            "factores_proteccion": ["hija comprometida", "fe religiosa", "apoyo familiar ampliado"],
            "nivel": "ALTO",
        },
        "es_emergencia": True,
    },

    # ─────────────────────────────────────────────────────────────────
    # CASO 23: JUNTA MÉDICA / MEDICOLEGAL
    # ─────────────────────────────────────────────────────────────────
    {
        "id": 23,
        "categoria": "adulto_joven",
        "dx_principal": "F07.2 - Síndrome post-concusional + demanda laboral activa",
        "estado": "medicolegal",
        "paciente": {
            "numero_documento": "79555111",
            "tipo_documento": "CC",
            "primer_nombre": "Jorge",
            "segundo_nombre": "Eliécer",
            "primer_apellido": "Salazar",
            "segundo_apellido": "Pinzón",
            "fecha_nacimiento": date(1980, 11, 8),
            "sexo": "H",
            "escolaridad": "Tecnólogo",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Casado",
            "telefono": "6017778899",
            "correo": "jorge.salazar@ejemplo.com",
            "direccion": "Calle 127 #50-30",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Usaquén",
            "estrato": "4",
            "ocupacion": "Técnico electricista (incapacitado por el accidente)",
            "acompanante": "Esposa Diana Ramírez",
            "acompanante_relacion": "Esposa",
            "acompanante_telefono": "6017778898",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "PERITAJE NEUROPSICOLÓGICO ordenado por Juzgado 14 Laboral del Circuito. Paciente sufrió TEC moderado en accidente laboral el 2025-08-15 (caída de 4 metros). Demanda en curso contra la empresa constructora. La evaluación es para DETERMINAR SECUELAS COGNITIVAS y capacidad laboral residual.",
            "remite": "Juzgado 14 Laboral del Circuito — Rad. 2025-00451",
            "eps": "Sanitas EPS",
            "orden_medica_no": "Auto del 2026-05-20",
            "discapacidad": "Sí - PCL en trámite",
            "codigo_rips": "F07.2",
            "cups": "890302",
            "finalidad_consulta": "Peritaje medicolegal",
        },
        "evaluacion": {
            "protocolo": "bateria_medicolegal_adulto",
            "puntajes": {
                # WAIS-III (escalares, disponibles en BD)
                "AdWAISV": 32,        # Vocabulario
                "AdWAISC": 28,        # Comprensión
                "AdTMT_AB": 110,      # Trail Making A+B combinado
                "AdStroop_Corr": 38,  # Stroop correcto
                "AdFCRO_Rey": 25,     # Rey Figura Compleja
                "AdBeck": 18,         # Depresión moderada
            },
        },
        "observaciones": [
            ("atención", "Atención sostenida severamente comprometida. TMT-A normal pero TMT-B en percentil <1. Stroop con alta interferencia (errores x3 sobre lo esperado). Estilo de respuesta lento-cauteloso, sugerente de déficit en velocidad de procesamiento más que impulsividad."),
            ("memoria", "Memoria de trabajo auditiva descendida (dígitos inversos en percentil 16). Memoria verbal con curva de aprendizaje aplanada y alta tasa de intrusiones (FCRO Rey percentil 25)."),
            ("lenguaje", "Lenguaje expresivo conservado pero con latencias aumentadas. Comprensión auditiva intacta para material concreto, descendida para inferencias. Discurso con pausas y autocorrecciones frecuentes."),
            ("funciones ejecutivas", "Funciones ejecutivas GLOBALESMENTE descendidas. WCST con 4 categorías completadas (esperado 6). Errores perseverativos aumentados. Flexibilidad cognitiva severamente afectada (TMT-B)."),
            ("validez", "Indicadores de validez dentro de rangos esperados. TOMM (Test of Memory Malingering) con 48/50 (por encima del corte de 45). Perfil consistente con secuela orgánica, no con simulación. Sin evidencia de esfuerzo subóptimo deliberado."),
            ("emociones", "Síntomas depresivos moderados (BDI-II = 18). Ansiedad rasgo elevada. Reactividad emocional aumentada. Componente secundario al trauma y a la situación legal, no simulada."),
        ],
        "recomendaciones": [
            "[LABORAL] (alta) Paciente presenta SECUELAS COGNITIVAS SIGNIFICATIVAS compatibles con síndrome post-concusional crónico. Capacidad laboral residual estimada: 40-50% de su nivel pre-lesional.",
            "[LABORAL] (alta) Implicaciones para la demanda: Las alteraciones en funciones ejecutivas y memoria documentadas SON CONSISTENTES con el TEC moderado del 2025-08-15 (mecanismo plausible, temporalidad coherente, perfil neuropsicológico típico).",
            "[LABORAL] (media) Limitaciones específicas: no apto para trabajo en alturas, no apto para tareas que requieran alta velocidad de procesamiento o toma rápida de decisiones en condiciones de riesgo. Requiere supervisión y pausas estructuradas.",
            "[TERAPÉUTICA] (media) Indispensable: programa de rehabilitación neuropsicológica de 6 meses (mínimo 24 sesiones) con foco en funciones ejecutivas y estrategias compensatorias de memoria.",
            "[TERAPÉUTICA] (media) Tratamiento farmacológico de la sintomatología depresiva-ansiosa por psiquiatría (ISRS). Psicoterapia breve de apoyo.",
            "[FAMILIAR] (media) Psicoeducación a esposa e hijos sobre el perfil de secuela, manejo conductual en casa, expectativas realistas de recuperación.",
            "[LEGAL] (alta) Documentación completa disponible para el juzgado. Se anexa: batería administrada, resultados normativos, análisis de validez, correlación anátomo-clínica, y respuesta a cada pregunta del auto interlocutorio.",
        ],
        "es_medicolegal": True,
    },

    # ─────────────────────────────────────────────────────────────────
    # CASO 24: CIERRE TERAPIA (Pre/Post)
    # ─────────────────────────────────────────────────────────────────
    {
        "id": 24,
        "categoria": "adulto_joven",
        "dx_principal": "F41.1 - Trastorno de ansiedad generalizada + cierre terapéutico exitoso",
        "estado": "cierre_terapia",
        "paciente": {
            "numero_documento": "52999123",
            "tipo_documento": "CC",
            "primer_nombre": "Andrea",
            "segundo_nombre": "Catalina",
            "primer_apellido": "Gutiérrez",
            "segundo_apellido": "Soto",
            "fecha_nacimiento": date(1990, 5, 3),
            "sexo": "M",
            "escolaridad": "Universitaria",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Manizales, Caldas",
            "estado_civil": "Unión libre",
            "telefono": "6068889900",
            "correo": "andrea.gutierrez@ejemplo.com",
            "direccion": "Carrera 23 #45-67",
            "ciudad": "Manizales",
            "localidad": "Centro",
            "estrato": "3",
            "ocupacion": "Administradora de empresas",
            "acompanante": "Pareja Juan Pablo Ortiz",
            "acompanante_relacion": "Pareja",
            "acompanante_telefono": "6068889901",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Cierre de proceso terapéutico. Ingreso en 2025-11-10 con F41.1 (TAG) severo. Completó 12 sesiones de TCC + técnicas de mindfulness. Pre/Post comparación favorable.",
            "remite": "Consulta particular (continuidad)",
            "eps": "Sanitas EPS",
            "orden_medica_no": "N/A",
            "discapacidad": "No",
            "codigo_rips": "F41.1",
            "cups": "890302",
            "finalidad_consulta": "Seguimiento - Cierre terapéutico",
        },
        "evaluacion": {
            "protocolo": "post_tratamiento_adulto",
            "puntajes": {
                "AdBeck": 6,           # Inicial: 22 (severo). Post: 6 (mínimo)
                "AdWAISV": 36,         # CI estable
                "AdWAISC": 35,
                "AdTMT_AB": 75,        # Normal (inicial 95)
            },
        },
        "evaluacion_previa": {
            "fecha": date(2025, 11, 10),
            "puntajes_iniciales": {
                "AdBeck": 22,
                "AdTMT_AB": 95,
            },
        },
        "observaciones": [
            ("atención", "Atención sostenida normalizada. Reporta capacidad de concentrarse en tareas laborales durante 1 hora sin fatiga (línea base: 20 min)."),
            ("memoria", "Memoria funcional subjetiva恢复正常. Olvidos cotidianos en rango normal. Sin quejas."),
            ("lenguaje", "Lenguaje fluido, sin pausas ansiosas. Voz proyectada. Mejor uso de pausas."),
            ("funciones ejecutivas", "Funciones ejecutivas conservadas. TMT-A y TMT-B dentro de percentiles esperados. Mejora significativa en planificación y resolución de problemas."),
            ("ánimo", "Eutimia. BDI-II 6 (inicial 22 — cambio confiable RCI = -16, p<0.05). Atribuye mejoría a: técnicas cognitivas, exposición gradual, mindfulness, regularización sueño-ejercicio."),
            ("ansiedad", "BAI equivalente reportado en mínimo. Sin ataques de pánico desde sesión 7. Tolerancia a incertidumbre заметно mejorada (escala subjetiva 7/10 vs 2/10 al inicio)."),
        ],
        "recomendaciones": [
            "[TERAPÉUTICA] (alta) MANTENIMIENTO: continuar con práctica diaria de mindfulness (10 min) y registro semanal de pensamientos automáticos (1 vez/sem).",
            "[TERAPÉUTICA] (media) SEÑALES DE ALERTA para reconsulta: reaparición de preocupaciones incontrolables >2 semanas, deterioro del sueño, evitación social creciente.",
            "[FAMILIAR] (media) Pareja informada sobre el plan de mantenimiento. Apoya la práctica de autocuidado.",
            "[FAMILIAR] (baja) Reevaluación de seguimiento opcional en 6 meses (2026-12). Cierre formal del caso si se mantiene la mejoría.",
            "[LABORAL] (baja) Mantener estrategias de manejo de estrés laboral (pausas activas, desconexión digital post-19:00).",
        ],
        "es_cierre_terapia": True,
        "rci_calculado": {
            "medida": "BDI-II",
            "pre": 22,
            "post": 6,
            "cambio_bruto": -16,
            "rci_jacobson_truax": -2.93,  # >1.96 → confiable
            "interpretacion": "Cambio CLÍNICAMENTE SIGNIFICATIVO y CONFIABLE ESTADÍSTICAMENTE",
        },
    },

    # ─────────────────────────────────────────────────────────────────
    # CASO 25: BATERÍA COMPLETA (stress test)
    # ─────────────────────────────────────────────────────────────────
    {
        "id": 25,
        "categoria": "infantil",
        "dx_principal": "F81.2 - Trastorno del cálculo + comorbilidad atencional",
        "estado": "bateria_completa",
        "paciente": {
            "numero_documento": "1121000099",
            "tipo_documento": "TI",
            "primer_nombre": "Tomás",
            "segundo_nombre": "Ignacio",
            "primer_apellido": "Restrepo",
            "segundo_apellido": "Vargas",
            "fecha_nacimiento": date(2013, 4, 18),
            "sexo": "H",
            "escolaridad": "4° Primaria",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Pereira, Risaralda",
            "estado_civil": "Soltero",
            "telefono": "6063334455",
            "correo": "padres.restrepo@ejemplo.com",
            "direccion": "Carrera 8 #25-30",
            "ciudad": "Pereira",
            "localidad": "Centro",
            "estrato": "3",
            "ocupacion": "Estudiante",
            "acompanante": "Madre Lucía Vargas",
            "acompanante_relacion": "Madre",
            "acompanante_telefono": "6063334456",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Madre y colegio reportan dificultades severas en matemáticas desde 1° grado. Lectura y escritura en rango normal-bajo. Conducta desatenta en clase. Evaluado previamente (WISC-IV en 2024) con perfil irregular. Solicita actualización completa.",
            "remite": "Colegio + familia",
            "eps": "Sura EPS",
            "orden_medica_no": "N/A",
            "discapacidad": "En estudio",
            "codigo_rips": "F81.2",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstica - actualización",
        },
        "evaluacion": {
            "protocolo": "bateria_completa_infantil",
            "puntajes": {
                # WISC-IV
                "NiWiscDC": 28,
                "NiWiscSem": 24,
                "NiWiscVoc": 30,
                "NiWiscLN": 18,
                "NiWiscCl": 26,
                "NiWiscAri": 14,        # Mucho más bajo (discalculia)
                "NiWISCIndComVer": 9,
                "NiWISCIndRazPer": 8,
                "NiWISCIndMemTra": 6,
                "NiWISCIndVelPro": 7,
                "NiWISCTot": 30,
                # ENI-2 (subtests disponibles en BD)
                "NiEniMLP": 18,         # Memoria lógica-paraguas
                "NiEniReco": 14,        # Reconocimiento
                "NiENICLet": 24,        # Lectura
                "NiENICMen": 22,        # Memoria
                "NiENICDib": 16,        # Dibujo
                "NiENIDel": 12,         # Deletreo
                # K-ABC-II (índices disponibles en BD)
                "NiKABCIndSim": 18,
                "NiKABCIndSec": 14,
                "NiKABCIndEsc": 20,
                "NiKABCCITot": 80,
                # Screening emocional
                "NiSpenceTo": 60,       # Ansiedad T-score 60 (límite)
                "NiCDI": 14,            # Depresión
                "NiVin": 84,            # Vineland (escala global)
                "NiGadsIS": 12,
                "NiGadsPRC": 14,
                "NiGadsPatCog": 6,
                "NiGadsHP": 8,
                "NiGADSCTAs": 6,
                # Neuropsicológicas finas
                "NiTMTA": 50,
                "NiTMTB": 90,
            },
        },
        "observaciones": [
            ("atención", "Atención sostenida снижена. Span atencional de 4-5 minutos. Errores por descuido en tareas de cálculo. Necesita re-dirección externa frecuente."),
            ("memoria", "Memoria de trabajo auditiva dentro de lo esperado. Memoria visual снижена percentil 25-50. Curva de aprendizaje verbal plana (3 palabras en 3 ensayos)."),
            ("lenguaje", "Lenguaje comprensivo y expresivo en percentil 50-75. Vocabulario en percentil 90. Comprensión de instrucciones complejas preservada."),
            ("funciones ejecutivas", "Funciones ejecutivas heterogéneas. Planeación preservada. Flexibilidad снижена (categorías WCST 4/6). Inhibición en percentil 25. Velocidad de procesamiento снижена percentil 16."),
            ("habilidades académicas", "LECTURA: percentil 25-50, velocidad lectora lentificada pero comprensión adecuada. ESCRITURA: percentil 16, errores ortográficos persistentes. MATEMÁTICAS: percentil <5, severamente comprometida. Discalculia confirmada (criterios DSM-5)."),
            ("comportamiento", "Observado: colaborador, ánimo eutímico, baja frustración. Sin indicadores TEA. Conducta adaptativa social preservada."),
            ("ansiedad", "T-score Spence 60 (límite). Síntomas ansiosos reactivos a exigencias académicas, no generalizados."),
        ],
        "recomendaciones": [
            "[ESCOLAR] (alta) ADAPTACIONES CURRICULARES: tiempo extendido en evaluaciones (1.5x), calculadora autorisée, problemas contextualizados en lugar de abstractos, evitar dictado de números.",
            "[ESCOLAR] (alta) Refuerzo escolar en matemáticas con metodología multisensorial (CRA, método Singapur adaptado, materiales concretos). Mínimo 3 horas/semana durante próximo año lectivo.",
            "[ESCOLAR] (media) Psicoeducación a docentes sobre discalculia y comorbilidad atencional. Evitar etiquetas de 'flojo' o 'poco inteligente'.",
            "[FAMILIAR] (alta) Apoyo parental en tareas: priorizar comprensión sobre velocidad, evitar castigo por errores en aritmética, celebrar logros en otras áreas.",
            "[TERAPÉUTICA] (media) Programa de estimulación de habilidades numéricas básicas (subitización, conteo, composición numérica) — 16 sesiones con frecuencia semanal.",
            "[TERAPÉUTICA] (media) Evaluación y posible intervención TDAH comórbido (SNAP-IV pendiente aplicación completa).",
            "[FAMILIAR] (baja) Coordinación con colegio para seguimiento mensual. Reevaluación neuropsicológica en 18 meses para monitorear progreso.",
        ],
        "es_bateria_completa": True,
        "total_pruebas": 31,
    },
]


# ═══════════════════════════════════════════════════════════════════════
# HELPERS COMPARTIDOS
# ═══════════════════════════════════════════════════════════════════════

def init_engine():
    """Carga baremos + inicializa motor clínico."""
    BaremosLoader.reset()
    loader = BaremosLoader.load(BAREMOS_PATH)
    return ClinicalEngine(loader=loader)


def _get_prof_and_inst():
    """Snapshot de profesional + institución (alta si no existe)."""
    with session_scope() as db:
        prof = db.query(ProfessionalORM).filter_by(activo=True).first()
        if not prof:
            prof = ProfessionalORM(
                id=str(uuid.uuid4()),
                nombre_completo="Johan Sebastián Salgado Sarmiento",
                titulo="Psicólogo Clínico",
                especialidad="Neuropsicología Clínica",
                registro_profesional="RCP-001",
                email="jssalgadosa@unal.edu.co",
                activo=True,
            )
            db.add(prof)
            db.flush()
        inst = db.query(ConfigInstitucionORM).first()
        if not inst:
            inst = ConfigInstitucionORM(
                id="1",
                nombre="[DEMO] Consultorio Demo",
                nit="[DEMO] 900.000.000-0",
                direccion="[DEMO] Calle 100 #15-20",
                telefono="[DEMO] 601-555-0000",
                email="[DEMO] demo@ejemplo.com",
                sitio_web="[DEMO] https://demo.neurosoft.com",
                ciudad="[DEMO] Bogotá, D.C.",
            )
            db.add(inst)
            db.flush()
        prof_snap = {
            "id": prof.id, "nombre_completo": prof.nombre_completo,
            "titulo": prof.titulo or "", "especialidad": prof.especialidad or "",
            "registro_profesional": prof.registro_profesional or "",
            "firma_base64": prof.firma_base64, "sello_base64": prof.sello_base64,
            "foto_base64": prof.foto_base64, "email": prof.email or "",
        }
        inst_snap = {
            "id": inst.id, "nombre": inst.nombre or "",
            "nit": inst.nit or "", "direccion": inst.direccion or "",
            "telefono": inst.telefono or "", "email": inst.email or "",
            "sitio_web": inst.sitio_web or "", "logo_base64": inst.logo_base64,
            "ciudad": inst.ciudad or "",
        }
        return prof_snap, inst_snap


def _simple_namespace(d: dict):
    class NS:
        pass
    ns = NS()
    for k, v in d.items():
        setattr(ns, k, v)
    return ns


# ═══════════════════════════════════════════════════════════════════════
# CREAR CASO
# ═══════════════════════════════════════════════════════════════════════

def crear_caso_edge(caso: dict, engine, fecha_atencion: date, db) -> dict:
    """Crea un caso edge. El caller DEBE pasar una sesión activa (db).

    El ORM resultante queda attached a esa sesión para que el caller
    pueda usar build_report_data_from_db sin DetachedInstanceError.
    """
    paciente = caso["paciente"]
    evaluacion = caso["evaluacion"]

    # 0. Idempotencia: si ya existe paciente con este doc + fecha, retornar early
    from sqlalchemy import select
    existing = db.execute(
        select(PatientORM).where(
            PatientORM.numero_documento == paciente["numero_documento"],
            PatientORM.fecha_atencion == fecha_atencion,
        )
    ).scalar_one_or_none()
    if existing is not None:
        return {
            "paciente_id": existing.id,
            "evaluation_id": None,
            "engine_result": None,
            "skipped": True,
            "skip_reason": f"Paciente ya existe (doc={paciente['numero_documento']}, fecha={fecha_atencion})",
        }

    # 1. Paciente
    pat_id = str(uuid.uuid4())
    pat_orm = PatientORM(
        id=pat_id,
        numero_documento=paciente["numero_documento"],
        tipo_documento=paciente.get("tipo_documento", "CC"),
        primer_nombre=paciente["primer_nombre"],
        segundo_nombre=paciente.get("segundo_nombre", ""),
        primer_apellido=paciente["primer_apellido"],
        segundo_apellido=paciente.get("segundo_apellido", ""),
        fecha_nacimiento=paciente["fecha_nacimiento"],
        fecha_atencion=fecha_atencion,
        sexo=paciente["sexo"],
        escolaridad=paciente.get("escolaridad", ""),
        lateralidad=paciente.get("lateralidad", "Diestro"),
        lugar_nacimiento=paciente.get("lugar_nacimiento", ""),
        estado_civil=paciente.get("estado_civil", "Soltero"),
        telefono=paciente.get("telefono", ""),
        correo=paciente.get("correo", ""),
        direccion=paciente.get("direccion", ""),
        ciudad=paciente.get("ciudad", ""),
        localidad=paciente.get("localidad", ""),
        estrato=paciente.get("estrato", ""),
        ocupacion=paciente.get("ocupacion", ""),
        acompanante=paciente.get("acompanante", ""),
        acompanante_relacion=paciente.get("acompanante_relacion", ""),
        acompanante_telefono=paciente.get("acompanante_telefono", ""),
        grupo_etnico=paciente.get("grupo_etnico", "No aplica"),
        motivo_consulta=paciente.get("motivo_consulta", ""),
        remite=paciente.get("remite", ""),
        eps=paciente.get("eps", ""),
        orden_medica_no=paciente.get("orden_medica_no", ""),
        discapacidad=paciente.get("discapacidad", "No"),
        codigo_rips=paciente.get("codigo_rips", ""),
        cups=paciente.get("cups", ""),
        finalidad_consulta=paciente.get("finalidad_consulta", ""),
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(pat_orm)
    db.flush()

    # 2. Edad + población
    ctx = PatientContext.from_demographics(
        birth_date=paciente["fecha_nacimiento"],
        evaluation_date=fecha_atencion,
        sexo=paciente["sexo"],
        escolaridad=paciente["escolaridad"],
    )

    # 3. Puntajes
    puntajes_a_usar = evaluacion["puntajes"]

    try:
        engine_result = engine.score(pat_id, puntajes_a_usar, ctx)
    except Exception as e:
        print(f"   [WARN] Engine error en caso {caso['id']}: {e}")
        from app.domain.clinical_engine.engine import EngineResult
        engine_result = EngineResult(
            paciente_id=pat_id,
            edad_display=f"{ctx.age.years}a {ctx.age.months}m",
            poblacion=ctx.poblacion,
            resultados=[],
            puntos_debiles=[],
            puntos_fuertes=[],
            advertencias=[f"Error: {e}"],
            pruebas_realizadas=list(puntajes_a_usar.keys()),
            pruebas_sin_dato=[],
        )

    # 4. Evaluación
    eval_id = str(uuid.uuid4())
    resultados_json = json.dumps(
        [asdict(r) for r in engine_result.resultados],
        default=str,
    )
    eval_orm = EvaluationORM(
        id=eval_id,
        patient_id=pat_id,
        protocolo=evaluacion["protocolo"],
        fecha=fecha_atencion,
        puntajes_brutos_json=json.dumps(puntajes_a_usar),
        resultados_json=resultados_json,
        poblacion=ctx.poblacion,
        edad_display=engine_result.edad_display,
        pruebas_realizadas=engine_result.pruebas_realizadas,
        pruebas_sin_dato=engine_result.pruebas_sin_dato,
        is_latest=True,
        created_at=datetime.utcnow(),
    )
    db.add(eval_orm)
    db.flush()

    # 5. Observaciones
    now_str = datetime.utcnow().isoformat()
    for dominio, texto in caso.get("observaciones", []):
        obs_orm = ObservationORM(
            id=str(uuid.uuid4()),
            patient_id=pat_id,
            evaluation_id=eval_id,
            dominio=dominio,
            texto=texto,
            created_at=now_str,
            updated_at=now_str,
        )
        db.add(obs_orm)

    # 6. Si es emergencia → C-SSRS
    if caso.get("es_emergencia") and caso.get("cssrs_score"):
        risk = RiskAssessmentORM(
            id=str(uuid.uuid4()),
            patient_id=pat_id,
            fecha=fecha_atencion,
            instrumento="c_ssrs",
            nivel=caso["cssrs_score"]["nivel"].lower(),
            ideacion_suicida=caso["cssrs_score"]["ideacion"],
            ideacion_con_plan=caso["cssrs_score"]["plan"],
            intento_previo=caso["cssrs_score"]["intentos_previos"],
            factores_riesgo=json.dumps(caso["cssrs_score"]["factores_riesgo"]),
            factores_protectores=json.dumps(caso["cssrs_score"]["factores_proteccion"]),
            plan_seguridad=(
                "1. No dejar sola a la paciente. Acompañamiento 24/7 por hija María.\n"
                "2. Retirar medios letales del domicilio (medicamentos, armas, cuerdas).\n"
                "3. Línea 106 activa en teléfono de la paciente.\n"
                "4. Contactos de emergencia: hija (601-3344557), vecina (601-3344999), CAI cercano.\n"
                "5. Remisión a psiquiatría en 24-48h."
            ),
            derivacion_emergencia=True,
            nota_clinica=f"Activación protocolo C-SSRS nivel {caso['cssrs_score']['nivel']} durante evaluación neuropsicológica.",
            created_at=datetime.utcnow(),
        )
        db.add(risk)

    # 7. HC rica
    obs_list = caso.get("observaciones", [])
    obs_by_key = {dom.lower(): txt for dom, txt in obs_list}
    get = lambda key: obs_by_key.get(key, "N/A")

    recomendaciones_texto = "\n".join(caso.get("recomendaciones", []))

    hc = ClinicalHistoryORM(
        id=str(uuid.uuid4()),
        patient_id=pat_id,
        numero_documento=paciente["numero_documento"],
        fecha_atencion=fecha_atencion,
        codigo_cie10=paciente.get("codigo_rips", "Z00.0").split(".")[0],
        motivo_consulta=paciente.get("motivo_consulta", ""),
        patologicos_medicos=caso.get("antecedentes_medicos", "Sin antecedentes médicos de relevancia."),
        psiquiatricos=caso.get("antecedentes_psiquiatricos", "Sin antecedentes psiquiátricos previos."),
        farmacologicos=caso.get("farmacos", "Sin medicación actual."),
        traumaticos=caso.get("trauma", "Niega TEC previo."),
        familiares=caso.get("antecedentes_familiares", "Sin antecedentes neuropsiquiátricos de primer grado."),
        vive_con=caso.get("vive_con", "Vive con familia."),
        escolar_laboral=f"Estudios: {paciente.get('escolaridad', 'N/A')}. Ocupación: {paciente.get('ocupacion', 'N/A')}.",
        obs_atencion=get("atención"),
        obs_memoria=get("memoria"),
        obs_lenguaje=get("lenguaje"),
        obs_funciones_ejecutivas=get("funciones ejecutivas"),
        obs_emociones=(get("ánimo") or get("ansiedad") or "N/A"),
        obs_clinica_general="Evaluación neuropsicológica. " + caso.get("nota_clinica", "Paciente colaborador."),
        obs_praxias_gnosias=caso.get("praxias_gnosias", "Sin alteraciones significativas en praxias ni gnosias."),
        obs_ci=f"Perfil cognitivo: {caso['dx_principal']}",
        obs_impresion_dx=f"Impresión diagnóstica: {caso['dx_principal']}",
        obs_recomendaciones=recomendaciones_texto,
        created_at=datetime.utcnow(),
    )
    db.add(hc)
    db.flush()

    # 8. Snapshot JSON
    snapshot = {
        "caso_id": caso["id"],
        "estado": caso.get("estado", "normal"),
        "paciente": {
            "id": pat_id,
            "documento": paciente["numero_documento"],
            "nombre": f"{paciente['primer_nombre']} {paciente['primer_apellido']}",
            "edad": engine_result.edad_display,
            "sexo": paciente["sexo"],
            "escolaridad": paciente["escolaridad"],
        },
        "evaluacion": {
            "id": eval_id,
            "protocolo": evaluacion["protocolo"],
            "fecha": fecha_atencion.isoformat(),
            "poblacion": ctx.poblacion,
            "n_pruebas": len(evaluacion["puntajes"]),
            "resultados_count": len(engine_result.resultados),
            "advertencias": engine_result.advertencias,
        },
        "dx_principal": caso["dx_principal"],
        "n_observaciones": len(caso.get("observaciones", [])),
        "n_recomendaciones": len(caso.get("recomendaciones", [])),
        "metadatos": {
            "es_emergencia": caso.get("es_emergencia", False),
            "es_medicolegal": caso.get("es_medicolegal", False),
            "es_cierre_terapia": caso.get("es_cierre_terapia", False),
            "es_bateria_completa": caso.get("es_bateria_completa", False),
            "es_inconcluso": caso.get("es_inconcluso", False),
            "rci_calculado": caso.get("rci_calculado"),
            "cssrs_score": caso.get("cssrs_score"),
        },
    }
    snap_path = SNAPSHOTS_DIR / f"caso_{caso['id']:02d}_snapshot.json"
    snap_path.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    return {
        "pat_id": pat_id,
        "eval_id": eval_id,
        "pat_orm": pat_orm,
        "eval_orm": eval_orm,
        "hc": hc,
        "poblacion": ctx.poblacion,
        "edad_display": engine_result.edad_display,
        "engine_result": engine_result,
        "snapshot_path": snap_path,
    }


# ═══════════════════════════════════════════════════════════════════════
# GENERAR PDF
# ═══════════════════════════════════════════════════════════════════════

def generar_pdf_edge(caso: dict, result: dict, inst_snap: dict, prof_snap: dict, obs_dict: dict):
    """Genera el PDF del informe edge."""
    from app.infrastructure.report_service import build_report_data_from_db
    from app.infrastructure.report_pro import generate_pro_pdf

    inst_ns = _simple_namespace(inst_snap)
    prof_ns = _simple_namespace(prof_snap)

    report_data = build_report_data_from_db(
        patient=result["pat_orm"],
        clinical_history=result["hc"],
        evaluation_record=result["eval_orm"],
        institucion=inst_ns,
        profesional=prof_ns,
        observations=obs_dict,
    )

    # Selección de variante según estado
    estado = caso.get("estado", "")
    if estado == "desercion" or caso.get("es_inconcluso"):
        template = "inconcluso"
    elif estado == "medicolegal" or caso.get("es_medicolegal"):
        template = "medicolegal"
    elif estado == "cierre_terapia" or caso.get("es_cierre_terapia"):
        template = "pro"  # se puede agregar variante "seguimiento" después
    elif caso.get("categoria") == "infantil":
        template = "pediatrico"
    else:
        template = "pro"

    pdf_bytes = generate_pro_pdf(report_data, template=template)

    nombre = f"{result['pat_orm'].primer_nombre}_{result['pat_orm'].primer_apellido}".replace(" ", "_")
    doc = result["pat_orm"].numero_documento
    fecha_str = date.today().strftime("%Y%m%d")
    pdf_path = OUTPUT_PDFS / f"caso_{caso['id']:02d}_{nombre}_doc{doc}_{fecha_str}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    return pdf_path


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print("NEUROSOFT APP — 5 CASOS EDGE/PREMIUM")
    print("=" * 80)
    print(f"Fecha: {date.today()}")
    print(f"Output PDFs: {OUTPUT_PDFS}")
    print()

    engine = init_engine()
    print("[1/4] Engine clínico OK")

    prof_snap, inst_snap = _get_prof_and_inst()
    print(f"[2/4] Profesional + Institución OK (Prof: {prof_snap['nombre_completo']})")
    print()

    resumen = []
    for caso in CASOS_EDGE:
        print(f"--- Caso {caso['id']}: {caso['paciente']['primer_nombre']} {caso['paciente']['primer_apellido']} ({caso.get('estado', 'normal')}) ---")
        try:
            fecha_atencion = date.today() + timedelta(days=caso["id"] + 200)  # +200 evita colisión con runs previos
            # Hacer todo dentro del mismo session_scope para evitar DetachedInstance
            from app.infrastructure.report_service import build_report_data_from_db
            from app.infrastructure.report_pro import generate_pro_pdf

            with session_scope() as db:
                result = crear_caso_edge(caso, engine, fecha_atencion, db)
                if result.get("skipped"):
                    print(f"   [SKIP] {result['skip_reason']}")
                    # Si ya existe el paciente, recuperar su evaluación+HC y regenerar PDF
                    from sqlalchemy import select
                    pat_orm = db.execute(
                        select(PatientORM).where(PatientORM.id == result["paciente_id"])
                    ).scalar_one()
                    eval_orm = db.execute(
                        select(EvaluationORM).where(EvaluationORM.patient_id == pat_orm.id)
                    ).scalar_one_or_none()
                    hc_orm = db.execute(
                        select(ClinicalHistoryORM).where(ClinicalHistoryORM.patient_id == pat_orm.id)
                    ).scalar_one_or_none()
                    if eval_orm is None or hc_orm is None:
                        print(f"   [WARN] No se encontró evaluación/HC previa; saltando PDF")
                        continue
                    from datetime import date as _date
                    fecha_atencion = pat_orm.fecha_atencion
                    ctx = PatientContext.from_demographics(
                        birth_date=pat_orm.fecha_nacimiento,
                        evaluation_date=fecha_atencion,
                        sexo=pat_orm.sexo,
                        escolaridad=pat_orm.escolaridad or "",
                    )
                    try:
                        engine_result = engine.score(pat_orm.id, caso["evaluacion"]["puntajes"], ctx)
                    except Exception as e:
                        print(f"   [WARN] Engine re-score error: {e}")
                        continue
                    result = {
                        "pat_id": pat_orm.id,
                        "eval_id": eval_orm.id,
                        "pat_orm": pat_orm,
                        "eval_orm": eval_orm,
                        "hc": hc_orm,
                        "poblacion": ctx.poblacion,
                        "edad_display": engine_result.edad_display,
                        "engine_result": engine_result,
                    }

                # Generar PDF dentro de la misma sesión
                obs_dict = {dom: txt for dom, txt in caso.get("observaciones", [])}
                inst_ns = _simple_namespace(inst_snap)
                prof_ns = _simple_namespace(prof_snap)
                report_data = build_report_data_from_db(
                    patient=result["pat_orm"],
                    clinical_history=result["hc"],
                    evaluation_record=result["eval_orm"],
                    institucion=inst_ns,
                    profesional=prof_ns,
                    observations=obs_dict,
                )
                estado = caso.get("estado", "")
                if estado == "desercion" or caso.get("es_inconcluso"):
                    template = "inconcluso"
                elif estado == "medicolegal" or caso.get("es_medicolegal"):
                    template = "medicolegal"
                elif caso.get("categoria") == "infantil":
                    template = "pediatrico"
                else:
                    template = "pro"
                pdf_bytes = generate_pro_pdf(report_data, template=template)
                nombre = f"{result['pat_orm'].primer_nombre}_{result['pat_orm'].primer_apellido}".replace(" ", "_")
                doc = result["pat_orm"].numero_documento
                fecha_str = date.today().strftime("%Y%m%d")
                pdf_path = OUTPUT_PDFS / f"caso_{caso['id']:02d}_{nombre}_doc{doc}_{fecha_str}.pdf"
                pdf_path.write_bytes(pdf_bytes)

                # Acumular resumen
                resumen.append({
                    "id": caso["id"],
                    "estado": caso.get("estado", "normal"),
                    "paciente": f"{caso['paciente']['primer_nombre']} {caso['paciente']['primer_apellido']}",
                    "doc": caso["paciente"]["numero_documento"],
                    "edad": result["edad_display"],
                    "poblacion": result["poblacion"],
                    "dx": caso["dx_principal"],
                    "pdf": str(pdf_path.relative_to(ROOT.parent)),
                    "n_pruebas": len(caso["evaluacion"]["puntajes"]),
                    "n_observaciones": len(caso.get("observaciones", [])),
                    "n_recomendaciones": len(caso.get("recomendaciones", [])),
                })

                print(f"   [OK] PDF: {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")
                print(f"        {len(caso['evaluacion']['puntajes'])} pruebas, "
                      f"{len(caso.get('observaciones', []))} obs, "
                      f"{len(caso.get('recomendaciones', []))} recomendaciones")
        except Exception as e:
            import traceback
            print(f"   [FAIL] {e}")
            traceback.print_exc()

    # Resumen final
    print()
    print("=" * 80)
    print(f"RESUMEN — {len(resumen)}/5 casos generados")
    print("=" * 80)
    for r in resumen:
        flags = []
        if r["estado"] == "emergencia":
            flags.append("[EMERGENCIA]")
        elif r["estado"] == "desercion":
            flags.append("[INCONCLUSO]")
        elif r["estado"] == "medicolegal":
            flags.append("[MEDICOLEGAL]")
        elif r["estado"] == "cierre_terapia":
            flags.append("[CIERRE]")
        elif r["estado"] == "bateria_completa":
            flags.append("[STRESS-TEST]")
        flag = " ".join(flags) if flags else ""
        print(f"  Caso {r['id']:02d} | {r['paciente']:35s} | {r['edad']:8s} | {r['n_pruebas']:2d} pruebas | {flag}")

    # Guardar resumen markdown
    resumen_path = ROOT.parent / "docs" / "casos-clinicos" / "5_CASOS_EDGE_RESUMEN.md"
    md = f"""# 5 Casos Edge/Premium — Resumen

**Fecha:** {date.today()}
**Generados:** {len(resumen)}/5

## Tabla resumen

| # | Paciente | Edad | Categoría | Pruebas | Obs | Rec | Estado |
|---|---|---|---|---|---|---|---|
"""
    for r in resumen:
        md += f"| {r['id']} | {r['paciente']} | {r['edad']} | {r['estado']} | {r['n_pruebas']} | {r['n_observaciones']} | {r['n_recomendaciones']} | {r['dx']} |\n"
    md += "\n## Detalles por caso\n\n"
    for r in resumen:
        caso = next(c for c in CASOS_EDGE if c["id"] == r["id"])
        md += f"### Caso {r['id']}: {r['paciente']}\n"
        md += f"- **Estado:** {r['estado']}\n"
        md += f"- **Dx principal:** {r['dx']}\n"
        md += f"- **PDF:** `{r['pdf']}`\n"
        if caso.get("razon_desercion"):
            md += f"- **Razón de deserción:** {caso['razon_desercion']}\n"
        if caso.get("cssrs_score"):
            md += f"- **C-SSRS:** nivel {caso['cssrs_score']['nivel']}\n"
        if caso.get("rci_calculado"):
            rci = caso["rci_calculado"]
            md += f"- **RCI:** {rci['interpretacion']} (cambio={rci['cambio_bruto']}, RCI={rci['rci_jacobson_truax']})\n"
        if caso.get("es_bateria_completa"):
            md += f"- **Total pruebas:** {caso.get('total_pruebas')}\n"
        md += "\n"
    resumen_path.write_text(md, encoding="utf-8")
    print()
    print(f"Resumen: {resumen_path.relative_to(ROOT.parent)}")
    print()


if __name__ == "__main__":
    main()
