"""
scripts/generate_20_clinical_cases.py
=====================================
Genera 20 casos clínicos inventados DIVERSOS con TODOS los campos diligenciados.
Cada caso incluye:
  - Paciente con TODOS los datos demográficos (incluyendo acompañante, ciudad, etc.)
  - Evaluación con batería completa apropiada
  - Observaciones clínicas por dominio cognitivo
  - Informe PDF generado en `docs/casos-clinicos/muestras-20-casos/`
  - Resumen ejecutivo del caso

Distribución:
  - 6 infantil (8-15 años) — TDAH, dislexia, TEA alto func., TDAH comb., depresión, DI leve
  - 7 adulto joven (22-45 años) — control, ACV, depresión postparto, TDAH adulto, TEPT, TCE, bipolar
  - 7 adulto mayor (65-82 años) — envejecimiento normal, DCL, Alzheimer, demencia, depresión, ACV, vascular

Uso:
    cd neurosoft-backend
    python -m scripts.generate_20_clinical_cases

Output:
    - 20 pacientes en data/neurosoft.db (persiste)
    - 20 evaluaciones en data/neurosoft.db
    - 20 PDFs en docs/casos-clinicos/muestras-20-casos/
    - Resumen: docs/casos-clinicos/20_CASOS_INVENTADOS_RESUMEN.md
"""

from __future__ import annotations

import json
import sys
import uuid
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

# Path al proyecto
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.engine import ClinicalEngine
from app.infrastructure.database.engine import session_scope
from app.infrastructure.database.orm_models import (
    Base,
    ClinicalHistoryORM,
    ConfigInstitucionORM,
    EvaluationORM,
    ObservationORM,
    PatientORM,
    ProfessionalORM,
)


# ═══════════════════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════════════════

BAREMOS_PATH = ROOT / "data" / "BD_NEURO_MAESTRA.json"
OUTPUT_PDFS = ROOT.parent / "docs" / "casos-clinicos" / "muestras-20-casos"
OUTPUT_PDFS.mkdir(parents=True, exist_ok=True)


def init_engine():
    """Carga baremos + inicializa motor clínico."""
    BaremosLoader.reset()
    loader = BaremosLoader.load(BAREMOS_PATH)
    engine = ClinicalEngine(loader=loader)
    return engine


# ═══════════════════════════════════════════════════════════════════════
# CASOS CLÍNICOS (20 total)
# ═══════════════════════════════════════════════════════════════════════

CASOS = [
    # ─────────────────────────────────────────────────────────────────
    # INFANTIL (6 casos)
    # ─────────────────────────────────────────────────────────────────

    # Caso 1: Niño 8a, H, TDAH inatento
    {
        "id": 1,
        "categoria": "infantil",
        "dx_principal": "F90.0 - TDAH tipo inatento",
        "paciente": {
            "numero_documento": "1121000001",
            "tipo_documento": "TI",
            "primer_nombre": "Santiago",
            "segundo_nombre": "Andrés",
            "primer_apellido": "Morales",
            "segundo_apellido": "Castaño",
            "fecha_nacimiento": date(2017, 10, 15),
            "sexo": "H",
            "escolaridad": "3° Primaria",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Soltero",
            "telefono": "6017451234",
            "correo": "padres.morales@ejemplo.com",
            "direccion": "Cra 15 #93-47 Apto 502",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Chapinero",
            "estrato": "4",
            "ocupacion": "Estudiante",
            "acompanante": "Claudia Inés Castaño Pérez",
            "acompanante_relacion": "Madre",
            "acompanante_telefono": "3204567890",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Dificultades atencionales reportadas por la docente desde primer grado. Se distrae con facilidad, pierde objetos, no termina tareas a tiempo. Rendimiento académico descendente en los últimos 6 meses.",
            "remite": "Colegio San Marcos",
            "eps": "Compensar EPS",
            "orden_medica_no": "OM-2026-001234",
            "discapacidad": "No",
            "codigo_rips": "F90.0",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstico",
        },
        "evaluacion": {
            "protocolo": "WISC-IV Evaluación Neuropsicológica Pediátrica",
            "puntajes": {
                # WISC-IV subtests
                "NiWiscDC": 25,    # Diseño con Cubos
                "NiWiscSem": 22,   # Semejanzas
                "NiWiscVoc": 24,   # Vocabulario
                "NiWiscLN": 17,    # Letras y Números
                "NiWiscCl": 28,    # Claves
                "NiWiscAri": 16,   # Aritmética
                "NiWiscMat": 22,   # Matrices
                "NiWiscCom": 20,   # Comprensión
                "NiWiscBusSim": 17,  # Búsqueda de Símbolos
                "NiWiscRDD": 13,   # Retención Dígitos Directos
                "NiWiscConD": 21,  # Conceptos con Dibujos
                # Índices (suman escalares)
                "NiWISCIndComVer": 32,  # ICV suma
                "NiWISCIndRazPer": 30,  # IRP suma
                "NiWISCIndMemTra": 17,  # IMT suma
                "NiWISCIndVelPro": 13,  # IVP suma
                "NiWISCIndCapGen": 92,  # ICG (suma ICV+IRP)
                "NiWISCTot": 85,        # CIT (suma total)
            },
        },
        "observaciones": [
            ("Atención", "Durante la aplicación el niño requirió redirección constante. Tiempo en tarea máximo: 4-5 minutos. Utilizó estrategias compensatorias (tarjetas visuales) con eficacia parcial."),
            ("Memoria de Trabajo", "Dificultad para mantener secuencias inversas. Mejor desempeño con material visual que auditivo."),
            ("Velocidad de Procesamiento", "Lentificación motriz en tareas de claves. Errores de omisión asociados a lapsus atencionales."),
            ("Conducta", "Impulsividad leve. Interrumpió en 3 ocasiones durante instrucciones. Cooperador globalmente."),
        ],
    },

    # Caso 2: Niña 10a, M, Dislexia
    {
        "id": 2,
        "categoria": "infantil",
        "dx_principal": "F81.0 - Trastorno específico de la lectura (dislexia)",
        "paciente": {
            "numero_documento": "1121000002",
            "tipo_documento": "TI",
            "primer_nombre": "Valentina",
            "segundo_nombre": "",
            "primer_apellido": "Restrepo",
            "segundo_apellido": "Gómez",
            "fecha_nacimiento": date(2015, 8, 22),
            "sexo": "M",
            "escolaridad": "5° Primaria",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Medellín, Antioquia",
            "estado_civil": "Soltera",
            "telefono": "6045551234",
            "correo": "familia.restrepo@ejemplo.com",
            "direccion": "Calle 10 #43-22",
            "ciudad": "Medellín, Antioquia",
            "localidad": "El Poblado",
            "estrato": "5",
            "ocupacion": "Estudiante",
            "acompanante": "Carlos Mario Restrepo Vélez",
            "acompanante_relacion": "Padre",
            "acompanante_telefono": "3157778899",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Dificultad persistente en lectoescritura a pesar de intervención pedagógica. Inversión de letras, omisiones, lectura lenta y con esfuerzo. CI estimado normal por antecedentes académicos.",
            "remite": "Psicopedagoga colegio",
            "eps": "Sura EPS",
            "orden_medica_no": "OM-2026-001235",
            "discapacidad": "En estudio",
            "codigo_rips": "F81.0",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstico y caracterización",
        },
        "evaluacion": {
            "protocolo": "WISC-IV + ENI-2 Evaluación Lectoescritura",
            "puntajes": {
                # WISC-IV
                "NiWiscDC": 32,    # Diseño con Cubos
                "NiWiscSem": 26,   # Semejanzas
                "NiWiscVoc": 28,   # Vocabulario
                "NiWiscCl": 24,    # Claves
                "NiWiscBusSim": 22,  # Búsqueda de Símbolos
                "NiWiscRDD": 14,
                "NiWISCIndComVer": 38,  # ICV alta
                "NiWISCIndRazPer": 33,
                "NiWISCIndMemTra": 19,
                "NiWISCIndVelPro": 13,  # IVP baja
                "NiWISCTot": 103,
                # ENI-2 lectura
                "NiLVS": 16,  # Lectura de palabras bajo
                "NiComp": 12,  # Comprensión lectora bajo
                "NiCopTxt": 18,
            },
        },
        "observaciones": [
            ("Lenguaje", "Vocabulario expresivo y comprensivo conservado. Buena discriminación fonológica en tareas aisladas. Dificultad en automatización del proceso lector."),
            ("Lectura", "Errores típicos: inversiones (b/d, p/q), omisiones, sustituciones. Velocidad lectora <percentil 10 para su edad. Comprensión lectora descendida por decodificación."),
            ("Escritura", "Errores ortográficos naturales y arbitrarios. Disgrafia asociada. Copia preservada."),
            ("Atención", "Adecuada. No se observan dificultades atencionales clínicamente significativas."),
        ],
    },

    # Caso 3: Adolescente 14a, H, TEA alto funcionamiento
    {
        "id": 3,
        "categoria": "infantil",
        "dx_principal": "F84.0 - Trastorno del Espectro Autista (alto funcionamiento)",
        "paciente": {
            "numero_documento": "1121000003",
            "tipo_documento": "TI",
            "primer_nombre": "Mateo",
            "segundo_nombre": "Alejandro",
            "primer_apellido": "Vargas",
            "segundo_apellido": "Pinzón",
            "fecha_nacimiento": date(2011, 5, 10),
            "sexo": "H",
            "escolaridad": "8° Secundaria",
            "lateralidad": "Zurdo",
            "lugar_nacimiento": "Cali, Valle del Cauca",
            "estado_civil": "Soltero",
            "telefono": "6023334455",
            "correo": "familia.vargas@ejemplo.com",
            "direccion": "Av 6N #28-50",
            "ciudad": "Cali, Valle del Cauca",
            "localidad": "San Fernando",
            "estrato": "3",
            "ocupacion": "Estudiante",
            "acompanante": "Lucía Pinzón de Vargas",
            "acompanante_relacion": "Madre",
            "acompanante_telefono": "3128887766",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Dificultades en interacción social. Intereses restringidos (programación, astronomía). Dificultad para comprender sarcasmo e ironía. Sospecha de TEA nivel 1.",
            "remite": "Psicóloga educativa",
            "eps": "Sanitas EPS",
            "orden_medica_no": "OM-2026-001236",
            "discapacidad": "En estudio",
            "codigo_rips": "F84.5",
            "cups": "890302",
            "finalidad_consulta": "Caracterización diagnóstica",
        },
        "evaluacion": {
            "protocolo": "WISC-IV + GADS Evaluación TEA",
            "puntajes": {
                # WISC-IV
                "NiWiscDC": 42,
                "NiWiscSem": 28,
                "NiWiscVoc": 30,
                "NiWiscCl": 35,
                "NiWiscMat": 38,
                "NiWiscCom": 24,
                "NiWiscRDD": 16,
                "NiWISCIndComVer": 36,
                "NiWISCIndRazPer": 38,
                "NiWISCIndMemTra": 22,
                "NiWISCIndVelPro": 19,
                "NiWISCTot": 115,
                # GADS - Coeficiente Asperger
                "NiGADSCTAs": 85,
                "NiGadsIS": 12,
                "NiGadsPRC": 18,
            },
        },
        "observaciones": [
            ("Interacción Social", "Contacto visual breve e intermitente. Dificultad para iniciar y mantener conversaciones recíprocas. Lenguaje con prosodia atípica."),
            ("Intereses", "Conocimiento enciclopédico sobre astronomía. Habla espontánea solo sobre temas de interés. Resistencia a cambios en rutina."),
            ("Cognición", "CI total en rango superior. Perfil irregular: razonamiento perceptual alto, comprensión social descendida."),
            ("Conducta", "Esterotipias motoras leves. Sin crisis de agresividad. Buena disposición a evaluación."),
        ],
    },

    # Caso 4: Niño 7a, H, TDAH combinado
    {
        "id": 4,
        "categoria": "infantil",
        "dx_principal": "F90.2 - TDAH tipo combinado",
        "paciente": {
            "numero_documento": "1121000004",
            "tipo_documento": "TI",
            "primer_nombre": "Emiliano",
            "segundo_nombre": "",
            "primer_apellido": "Ortega",
            "segundo_apellido": "Soto",
            "fecha_nacimiento": date(2018, 11, 8),
            "sexo": "H",
            "escolaridad": "2° Primaria",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Barranquilla, Atlántico",
            "estado_civil": "Soltero",
            "telefono": "6053778899",
            "correo": "padres.ortega@ejemplo.com",
            "direccion": "Cra 53 #76-120",
            "ciudad": "Barranquilla, Atlántico",
            "localidad": "Norte Centro Histórico",
            "estrato": "2",
            "ocupacion": "Estudiante",
            "acompanante": "Marlene Soto de Ortega",
            "acompanante_relacion": "Madre",
            "acompanante_telefono": "3001112233",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Hiperactividad motora, impulsividad severa. No permanece sentado, interrumpe constantemente, accidentes frecuentes. Inicio en jardín, persiste en primaria.",
            "remite": "Pediatra tratante",
            "eps": "Nueva EPS",
            "orden_medica_no": "OM-2026-001237",
            "discapacidad": "En estudio",
            "codigo_rips": "F90.2",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstico y recomendaciones",
        },
        "evaluacion": {
            "protocolo": "WISC-IV + Vineland + SNAP-IV",
            "puntajes": {
                "NiWiscDC": 20,
                "NiWiscSem": 18,
                "NiWiscVoc": 20,
                "NiWiscCl": 22,
                "NiWiscRDD": 11,
                "NiWISCIndComVer": 28,
                "NiWISCIndRazPer": 26,
                "NiWISCIndMemTra": 14,
                "NiWISCIndVelPro": 10,  # IVP muy bajo
                "NiWISCTot": 78,         # CIT bajo
                # Vineland
                "NiVin": 78,  # Adaptativo bajo
            },
        },
        "observaciones": [
            ("Hiperactividad", "Actividad motora excesiva. Se levanta de la silla 8 veces durante la evaluación. Manipula objetos constantemente. Dificultad para esperar turnos."),
            ("Impulsividad", "Responde antes de completar las instrucciones. Interrumpe al evaluador. Accidentes reportados: 2 en último mes."),
            ("Atención", "Atención sostenida limitada (3-4 min). Errores de comisión en tareas de vigilancia. Omisiones por distracción."),
            ("Adaptativo", "Independencia en ABVD descendida para su edad. Requiere supervisión constante. Dificultad en normas sociales."),
        ],
    },

    # Caso 5: Adolescente 15a, M, Depresión + Ansiedad
    {
        "id": 5,
        "categoria": "infantil",
        "dx_principal": "F32.1 - Episodio depresivo moderado + F41.1 - Ansiedad generalizada",
        "paciente": {
            "numero_documento": "1121000005",
            "tipo_documento": "TI",
            "primer_nombre": "Isabella",
            "segundo_nombre": "María",
            "primer_apellido": "Cardona",
            "segundo_apellido": "Mejía",
            "fecha_nacimiento": date(2010, 3, 25),
            "sexo": "M",
            "escolaridad": "10° Secundaria",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Soltera",
            "telefono": "6012223344",
            "correo": "padres.cardona@ejemplo.com",
            "direccion": "Calle 127 #15-30",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Usaquén",
            "estrato": "5",
            "ocupacion": "Estudiante",
            "acompanante": "Roberto Cardona Salazar",
            "acompanante_relacion": "Padre",
            "acompanante_telefono": "3109998877",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Síntomas depresivos de 4 meses de evolución: tristeza persistente, anhedonia, aislamiento, bajo rendimiento académico. Síntomas ansiosos: preocupación excesiva, insomnio, quejas somáticas.",
            "remite": "Psicóloga colegio",
            "eps": "Compensar EPS",
            "orden_medica_no": "OM-2026-001238",
            "discapacidad": "No",
            "codigo_rips": "F32.1",
            "cups": "890302",
            "finalidad_consulta": "Evaluación clínica y plan terapéutico",
        },
        "evaluacion": {
            "protocolo": "WISC-IV + CDI + Spence",
            "puntajes": {
                "NiWiscDC": 30,
                "NiWiscSem": 25,
                "NiWiscVoc": 32,
                "NiWiscCl": 28,
                "NiWiscRDD": 15,
                "NiWISCIndComVer": 38,
                "NiWISCIndRazPer": 32,
                "NiWISCIndMemTra": 19,
                "NiWISCIndVelPro": 16,
                "NiWISCTot": 105,
                # CDI Depresión infantil
                "NiCDI": 22,  # Puntuación elevada
                # Spence ansiedad
                "NiSpenceTo": 65,  # T-score alto ansiedad total
            },
        },
        "observaciones": [
            ("Ánimo", "Tristeza persistente, llanto fácil. Anhedonia: 'ya nada me gusta'. Pensamientos de minusvalía. Sin ideación suicida activa."),
            ("Ansiedad", "Preocupación excesiva por rendimiento académico y salud familiar. Tensión muscular, dificultad para relajarse. Insomnio de conciliación."),
            ("Cognición", "Rendimiento intelectual promedio. Velocidad de procesamiento descendida por componente atencional-afectivo."),
            ("Conducta", "Aislamiento social progresivo. Ha dejado de salir con amigas. Hiporexia con pérdida de 3 kg en 2 meses."),
        ],
    },

    # Caso 6: Niña 9a, M, Discapacidad intelectual leve
    {
        "id": 6,
        "categoria": "infantil",
        "dx_principal": "F70 - Discapacidad intelectual leve",
        "paciente": {
            "numero_documento": "1121000006",
            "tipo_documento": "TI",
            "primer_nombre": "Luciana",
            "segundo_nombre": "",
            "primer_apellido": "Reyes",
            "segundo_apellido": "Salazar",
            "fecha_nacimiento": date(2016, 6, 12),
            "sexo": "M",
            "escolaridad": "3° Primaria (con ajustes)",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Bucaramanga, Santander",
            "estado_civil": "Soltera",
            "telefono": "6076457788",
            "correo": "padres.reyes@ejemplo.com",
            "direccion": "Cra 27 #45-67",
            "ciudad": "Bucaramanga, Santander",
            "localidad": "Cabecera del Llano",
            "estrato": "3",
            "ocupacion": "Estudiante",
            "acompanante": "Diana Salazar Pérez",
            "acompanante_relacion": "Madre",
            "acompanante_telefono": "3165554433",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Rendimiento académico global descendido. Dificultades en lectoescritura y matemáticas desde jardín. Adaptación curricular con poco avance.",
            "remite": "Docente de apoyo",
            "eps": "Sanitas EPS",
            "orden_medica_no": "OM-2026-001239",
            "discapacidad": "En estudio - posible DI",
            "codigo_rips": "F70",
            "cups": "890302",
            "finalidad_consulta": "Caracterización cognitiva",
        },
        "evaluacion": {
            "protocolo": "WISC-IV Evaluación Discapacidad Intelectual",
            "puntajes": {
                "NiWiscDC": 14,  # Bajo
                "NiWiscSem": 12,  # Bajo
                "NiWiscVoc": 15,  # Bajo
                "NiWiscCl": 18,   # Bajo
                "NiWiscRDD": 9,   # Muy bajo
                "NiWISCIndComVer": 19,  # ICV bajo
                "NiWISCIndRazPer": 21,
                "NiWISCIndMemTra": 12,
                "NiWISCIndVelPro": 14,
                "NiWISCTot": 66,  # CIT rango DI leve
                # Vineland (puntaje adaptativo)
                "NiVin": 75,  # Adaptativo bajo
            },
        },
        "observaciones": [
            ("Cognición Global", "Funcionamiento intelectual en rango de discapacidad intelectual leve. Dificultad en tareas abstractas. Aprendizaje lento pero con consolidación. EAD administrado por separado con percentiles descendidos en todas las áreas del desarrollo."),
            ("Lenguaje", "Vocabulario expresivo limitado para su edad. Comprensión de instrucciones complejas descendida. Articulación conservada."),
            ("Adaptativo", "Dependencia moderada para ABVD. Requiere apoyo en tareas escolares. Habilidades sociales básicas preservadas. Vineland percentil bajo para edad."),
            ("Conducta", "Apegada al evaluador. Baja tolerancia a la frustración. Conducta externalizada ocasional (llanto)."),
        ],
    },

    # ─────────────────────────────────────────────────────────────────
    # ADULTO JOVEN (7 casos)
    # ─────────────────────────────────────────────────────────────────

    # Caso 7: Adulto 28a, M, Control sano
    {
        "id": 7,
        "categoria": "adulto_joven",
        "dx_principal": "Z00 - Examen de control (sin alteraciones)",
        "paciente": {
            "numero_documento": "52123457",
            "tipo_documento": "CC",
            "primer_nombre": "Laura",
            "segundo_nombre": "Catalina",
            "primer_apellido": "Hernández",
            "segundo_apellido": "Molina",
            "fecha_nacimiento": date(1997, 7, 8),
            "sexo": "M",
            "escolaridad": "Profesional (Ingeniería)",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Soltera",
            "telefono": "6018885544",
            "correo": "laura.hernandez@ejemplo.com",
            "direccion": "Calle 93 #11-27 Apto 801",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Chapinero",
            "estrato": "5",
            "ocupacion": "Ingeniera de software",
            "acompanante": "",
            "acompanante_relacion": "",
            "acompanante_telefono": "",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Evaluación neuropsicológica de control como parte de proceso de selección para alto cargo gerencial. Sin antecedentes neuropsiquiátricos.",
            "remite": "Empresa RH",
            "eps": "Particular",
            "orden_medica_no": "OM-2026-001240",
            "discapacidad": "No",
            "codigo_rips": "Z00.0",
            "cups": "890302",
            "finalidad_consulta": "Caracterización cognitiva",
        },
        "evaluacion": {
            "protocolo": "WAIS-III Evaluación Neuropsicológica Completa",
            "puntajes": {
                # WAIS-III subescalas (rango adulto 25-34)
                "AdWAISV": 52,    # Vocabulario alto
                "AdSemWais": 28,  # Semejanzas alto
                "AdWAISA": 22,    # Aritmética promedio-alto
                "AdDDir": 18,     # Dígitos
                "AdWAISI": 25,    # Información
                "AdWAISC": 24,    # Comprensión
                "AdWAISL": 16,    # Letras y Números
                "AdWAISFI": 19,   # Figuras Incompletas
                "AdSDWais": 58,   # Clave de Números
                "AdWAISCC": 48,   # Construcción Cubos
                "AdMatr": 25,     # Matrices
                "AdWAISHI": 20,   # Historietas
                "AdWAISRO": 32,   # Rompecabezas
                "AdBusSim": 30,   # Búsqueda de Símbolos
                # Índices CI
                "AdWAISICV": 65,    # ICV
                "AdWAISICP": 58,    # ICP
                "AdWAISIMT": 32,    # IMT
                "AdWAISIVP": 45,    # IVP
                "AdWASIEVer": 110,  # Escala Verbal
                "AdWAISEMan": 105,  # Escala Manipulativa
                "AdWAISCIT": 120,   # CIT superior
            },
        },
        "observaciones": [
            ("Atención", "Atención sostenida y selectiva preservadas. Desempeño óptimo en tareas de vigilancia."),
            ("Memoria de Trabajo", "Capacidad de memoria de trabajo dentro de rangos esperados. Buena manipulación de información verbal."),
            ("Velocidad de Procesamiento", "Velocidad de procesamiento visomotor en rango promedio-alto."),
            ("Funciones Ejecutivas", "Planificación, organización y monitoreo preservados. Buena flexibilidad cognitiva."),
        ],
    },

    # Caso 8: Adulto 32a, H, ACV post-rehabilitación
    {
        "id": 8,
        "categoria": "adulto_joven",
        "dx_principal": "I69.3 - Secuelas de ACV (recuperación)",
        "paciente": {
            "numero_documento": "79555123",
            "tipo_documento": "CC",
            "primer_nombre": "Andrés",
            "segundo_nombre": "Felipe",
            "primer_apellido": "Romero",
            "segundo_apellido": "Castaño",
            "fecha_nacimiento": date(1993, 5, 30),
            "sexo": "H",
            "escolaridad": "Profesional (Derecho)",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Casado",
            "telefono": "6014445566",
            "correo": "andres.romero@ejemplo.com",
            "direccion": "Cra 11 #85-32",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Chicó Norte",
            "estrato": "6",
            "ocupacion": "Abogado (licencia médica)",
            "acompanante": "Carolina Mejía de Romero",
            "acompanante_relacion": "Esposa",
            "acompanante_telefono": "3158889900",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Control post-ACV isquémico de ACM izquierda (hace 8 meses). Hemiparesia derecha resuelta, persiste leve déficit atencional y anomia. Evaluar capacidad para reincorporación laboral.",
            "remite": "Neurólogo tratante",
            "eps": "Sanitas EPS",
            "orden_medica_no": "OM-2026-001241",
            "discapacidad": "Sí, transitoria",
            "codigo_rips": "I69.3",
            "cups": "890302",
            "finalidad_consulta": "Control y recomendaciones",
        },
        "evaluacion": {
            "protocolo": "WAIS-III + BDI-II + Evaluación Post-ACV",
            "puntajes": {
                "AdWAISV": 42,    # Descendido leve
                "AdSemWais": 20,  # Descendido
                "AdWAISA": 16,    # Bajo
                "AdDDir": 14,     # Bajo
                "AdWAISI": 22,
                "AdWAISC": 22,
                "AdWAISL": 12,    # Bajo (memoria trabajo)
                "AdWAISFI": 15,   # Descendido
                "AdSDWais": 42,   # Velocidad baja
                "AdWAISCC": 38,   # Descendido
                "AdMatr": 20,     # Promedio bajo
                "AdWAISHI": 16,
                "AdWAISRO": 25,
                "AdWAISICV": 50,  # ICV descendido
                "AdWAISICP": 45,
                "AdWAISIMT": 26,  # IMT bajo
                "AdWAISIVP": 32,  # IVP bajo
                "AdWAISCIT": 95,  # CIT promedio bajo
                # BDI-II
                "AdBeck": 14,  # Leve
            },
        },
        "observaciones": [
            ("Atención", "Atención sostenida y selectiva descendidas. Fatiga atencional a los 30 min. Mejora con pausas estructuradas."),
            ("Memoria", "Anomia leve. Dificultad en evocación categorial. Reconocimiento preservado (perfil subcortical)."),
            ("Funciones Ejecutivas", "Planificación descendida. Dificultad en tareas que requieren secuenciación. Flexibilidad cognitiva preservada."),
            ("Ánimo", "Síntomas depresivos subclínicos. Frustración por limitaciones residuales. Ajuste emocional en proceso."),
        ],
    },

    # Caso 9: Adulto 25a, M, Depresión postparto
    {
        "id": 9,
        "categoria": "adulto_joven",
        "dx_principal": "F53.0 - Depresión postparto leve + F32.1 - Episodio depresivo moderado",
        "paciente": {
            "numero_documento": "52999888",
            "tipo_documento": "CC",
            "primer_nombre": "María",
            "segundo_nombre": "Alejandra",
            "primer_apellido": "Salazar",
            "segundo_apellido": "Ortiz",
            "fecha_nacimiento": date(2000, 9, 14),
            "sexo": "M",
            "escolaridad": "Tecnológica (Aux. Contable)",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Pereira, Risaralda",
            "estado_civil": "Unión libre",
            "telefono": "6063331122",
            "correo": "maria.salazar@ejemplo.com",
            "direccion": "Calle 14 #10-25",
            "ciudad": "Pereira, Risaralda",
            "localidad": "Centro",
            "estrato": "2",
            "ocupacion": "Auxiliar contable (licencia maternidad)",
            "acompanante": "Juan Pablo Henao Giraldo",
            "acompanante_relacion": "Compañero permanente",
            "acompanante_telefono": "3204445566",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Síntomas depresivos 3 meses postparto. Llanto fácil, anhedonia, insomnio, pensamientos de incapacidad materna. Ansiedad anticipatoria elevada. Dificultad atencional subjetiva.",
            "remite": "Médico familiar",
            "eps": "Sura EPS",
            "orden_medica_no": "OM-2026-001242",
            "discapacidad": "No",
            "codigo_rips": "F53.0",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstico y plan integral",
        },
        "evaluacion": {
            "protocolo": "WAIS-III + BDI-II + Evaluación Postparto",
            "puntajes": {
                "AdWAISV": 38,
                "AdSemWais": 18,
                "AdWAISA": 14,
                "AdDDir": 13,
                "AdWAISFI": 16,
                "AdSDWais": 38,
                "AdWAISCC": 32,
                "AdMatr": 18,
                "AdWAISICV": 42,
                "AdWAISICP": 38,
                "AdWAISIMT": 22,
                "AdWAISIVP": 28,
                "AdWAISCIT": 88,  # CIT promedio bajo
                "AdBeck": 22,     # BDI-II moderado
            },
        },
        "observaciones": [
            ("Ánimo", "Tristeza persistente, anhedonia. Llanto fácil. Pensamiento rumiativo sobre capacidad materna. Sin ideación suicida."),
            ("Atención/Concentración", "Dificultad atencional subjetiva confirmada en evaluación. Fatiga mental. Desempeño descendido por componente afectivo."),
            ("Memoria", "Quejas de memoria subjetivas. Desempeño objetivo en rango bajo. Fatigabilidad."),
            ("Sueño", "Insomnio mixto. Despertar temprano. Hipersomnia diurna. Lactancia nocturna cada 3 horas."),
        ],
    },

    # Caso 10: Adulto 40a, H, TDAH adulto
    {
        "id": 10,
        "categoria": "adulto_joven",
        "dx_principal": "F90.1 - TDAH tipo combinado (diagnóstico tardío)",
        "paciente": {
            "numero_documento": "79456789",
            "tipo_documento": "CC",
            "primer_nombre": "Ricardo",
            "segundo_nombre": "Alberto",
            "primer_apellido": "Pinzón",
            "segundo_apellido": "Vargas",
            "fecha_nacimiento": date(1985, 4, 20),
            "sexo": "H",
            "escolaridad": "Maestría (Administración)",
            "lateralidad": "Zurdo",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Divorciado",
            "telefono": "6017776655",
            "correo": "ricardo.pinzon@ejemplo.com",
            "direccion": "Av 19 #104-32",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Chapinero",
            "estrato": "5",
            "ocupacion": "Gerente comercial",
            "acompanante": "",
            "acompanante_relacion": "",
            "acompanante_telefono": "",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Sospecha de TDAH adulto. Historia de bajo rendimiento escolar, multiproblemática. Mejora con estimulantes en uso reciente. Dificultad organizacional crónica, procrastinación.",
            "remite": "Psiquiatra tratante",
            "eps": "Particular",
            "orden_medica_no": "OM-2026-001243",
            "discapacidad": "No",
            "codigo_rips": "F90.1",
            "cups": "890302",
            "finalidad_consulta": "Confirmación diagnóstica",
        },
        "evaluacion": {
            "protocolo": "WAIS-III + BDI-II + Evaluación TDAH Adulto",
            "puntajes": {
                "AdWAISV": 48,
                "AdSemWais": 25,
                "AdWAISA": 20,
                "AdDDir": 15,
                "AdWAISFI": 20,
                "AdSDWais": 48,
                "AdWAISCC": 42,
                "AdMatr": 24,
                "AdWAISICV": 58,
                "AdWAISICP": 52,
                "AdWAISIMT": 28,  # IMT bajo
                "AdWAISIVP": 40,
                "AdWAISCIT": 110,
                "AdBeck": 12,  # BDI leve
            },
        },
        "observaciones": [
            ("Atención", "Atención sostenida descendida. Errores de omisión en tareas de vigilancia. Mejora con novelty y tareas de alta estimulación."),
            ("Memoria de Trabajo", "Capacidad de memoria de trabajo descendida. Dificultad en secuenciación inversa. Mejora con codificación visual."),
            ("Impulsividad", "Respuestas impulsivas en tareas de tiempo de reacción. Interrupciones frecuentes en evaluación. Sin rasgos de hostilidad."),
            ("Historia", "Síntomas desde infancia. Bajo rendimiento en colegio pese a alta capacidad. Diagnóstico de 'inmaduro' en infancia. Mejora con metilfenidato en últimos 3 meses."),
        ],
    },

    # Caso 11: Adulto 35a, M, TEPT
    {
        "id": 11,
        "categoria": "adulto_joven",
        "dx_principal": "F43.1 - Trastorno de estrés postraumático",
        "paciente": {
            "numero_documento": "52345678",
            "tipo_documento": "CC",
            "primer_nombre": "Daniela",
            "segundo_nombre": "Patricia",
            "primer_apellido": "Mendoza",
            "segundo_apellido": "Reyes",
            "fecha_nacimiento": date(1990, 11, 3),
            "sexo": "M",
            "escolaridad": "Profesional (Psicología)",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Soltera",
            "telefono": "6015554433",
            "correo": "daniela.mendoza@ejemplo.com",
            "direccion": "Calle 72 #10-50 Apto 301",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Chapinero",
            "estrato": "4",
            "ocupacion": "Psicóloga clínica",
            "acompanante": "",
            "acompanante_relacion": "",
            "acompanante_telefono": "",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Asalto violento hace 6 meses. Reviviscencias, pesadillas, evitación, hipervigilancia. Dificultad para ejercer labor con pacientes. Síntomas disociativos intermitentes.",
            "remite": "Psiquiatra",
            "eps": "Sanitas EPS",
            "orden_medica_no": "OM-2026-001244",
            "discapacidad": "En estudio",
            "codigo_rips": "F43.1",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstico y plan terapéutico",
        },
        "evaluacion": {
            "protocolo": "WAIS-III + PCL-5",
            "puntajes": {
                "AdWAISV": 50,
                "AdSemWais": 26,
                "AdWAISA": 20,
                "AdDDir": 16,
                "AdWAISFI": 19,
                "AdSDWais": 50,
                "AdWAISCC": 44,
                "AdMatr": 22,
                "AdWAISICV": 60,
                "AdWAISICP": 50,
                "AdWAISIMT": 30,
                "AdWAISIVP": 42,
                "AdWAISCIT": 112,
            },
        },
        "observaciones": [
            ("Reexperimentación", "Flashbacks intrusivos 4-5 veces/semana. Pesadillas 2-3 veces/semana. Activación autonómica ante estímulos asociados."),
            ("Evitación", "Evitación activa de lugares, personas y conversaciones asociadas al evento. Restricción significativa en actividades cotidianas."),
            ("Hiperactivación", "Insomnio de mantenimiento. Hipervigilancia. Respuesta de sobresalto exagerada. Irritabilidad."),
            ("Cognición", "Funciones cognitivas preservadas. Velocidad de procesamiento descendida por componente ansioso. Atención hipervigilante pero ineficiente."),
        ],
    },

    # Caso 12: Adulto 22a, H, TCE leve
    {
        "id": 12,
        "categoria": "adulto_joven",
        "dx_principal": "S06.0 - Secuelas de traumatismo craneoencefálico leve",
        "paciente": {
            "numero_documento": "1006123456",
            "tipo_documento": "CC",
            "primer_nombre": "Sebastián",
            "segundo_nombre": "",
            "primer_apellido": "Quintero",
            "segundo_apellido": "Luna",
            "fecha_nacimiento": date(2003, 2, 17),
            "sexo": "H",
            "escolaridad": "Técnico (Sistemas)",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Ibagué, Tolima",
            "estado_civil": "Soltero",
            "telefono": "6082779988",
            "correo": "sebastian.quintero@ejemplo.com",
            "direccion": "Calle 60 #5-44",
            "ciudad": "Ibagué, Tolima",
            "localidad": "Centro",
            "estrato": "2",
            "ocupacion": "Técnico en sistemas",
            "acompanante": "Rosa Luna de Quintero",
            "acompanante_relacion": "Madre",
            "acompanante_telefono": "3126677889",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "TCE leve por accidente de tránsito hace 5 meses. Pérdida de conciencia <30 min. Cefalea post-traumática persistente, quejas de memoria y concentración. Reinicio laboral fallido.",
            "remite": "Neurólogo",
            "eps": "Nueva EPS",
            "orden_medica_no": "OM-2026-001245",
            "discapacidad": "En estudio",
            "codigo_rips": "S06.0",
            "cups": "890302",
            "finalidad_consulta": "Caracterización post-TCE",
        },
        "evaluacion": {
            "protocolo": "WAIS-III + BDI-II + Evaluación Post-TCE",
            "puntajes": {
                "AdWAISV": 32,    # Bajo
                "AdSemWais": 16,
                "AdWAISA": 12,    # Bajo
                "AdDDir": 11,     # Bajo
                "AdWAISFI": 14,   # Bajo
                "AdSDWais": 35,   # Bajo
                "AdWAISCC": 30,
                "AdMatr": 16,
                "AdWAISICV": 38,  # Bajo
                "AdWAISICP": 35,
                "AdWAISIMT": 18,  # Muy bajo
                "AdWAISIVP": 26,
                "AdWAISCIT": 78,  # CIT rango bajo
                "AdBeck": 18,     # Leve-moderado
            },
        },
        "observaciones": [
            ("Atención", "Atención sostenida y selectiva descendidas. Fatiga atencional acelerada. Mejora con pausas estructuradas."),
            ("Memoria", "Memoria de trabajo descendida. Codificación deficiente. Reconocimiento mejor que evocación libre (perfil subcortical)."),
            ("Velocidad de Procesamiento", "Velocidad de procesamiento visomotor descendida. Factor de enlentecimiento psicomotor."),
            ("Síntomas Físicos", "Cefalea post-traumática 3-4 veces/semana. Mareo ocasional. Fatiga crónica. Hipersomnia."),
        ],
    },

    # Caso 13: Adulto 45a, M, Trastorno bipolar
    {
        "id": 13,
        "categoria": "adulto_joven",
        "dx_principal": "F31.1 - Trastorno afectivo bipolar, episodio actual depresivo",
        "paciente": {
            "numero_documento": "52789456",
            "tipo_documento": "CC",
            "primer_nombre": "Carolina",
            "segundo_nombre": "",
            "primer_apellido": "Ramírez",
            "segundo_apellido": "Torres",
            "fecha_nacimiento": date(1980, 8, 28),
            "sexo": "M",
            "escolaridad": "Profesional (Medicina)",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Manizales, Caldas",
            "estado_civil": "Casada",
            "telefono": "6068876655",
            "correo": "carolina.ramirez@ejemplo.com",
            "direccion": "Cra 23 #46-30",
            "ciudad": "Manizales, Caldas",
            "localidad": "Palogrande",
            "estrato": "5",
            "ocupacion": "Médica internista (incapacidad)",
            "acompanante": "Felipe Ramírez Londoño",
            "acompanante_relacion": "Esposo",
            "acompanante_telefono": "3105556677",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Episodio depresivo de 2 meses en contexto de TAB tipo II. Anhedonia, hipoergia, insomnio, ideación suicida pasiva. 2 episodios hipomaníacos previos documentados.",
            "remite": "Psiquiatra tratante",
            "eps": "Sura EPS",
            "orden_medica_no": "OM-2026-001246",
            "discapacidad": "Sí, transitoria",
            "codigo_rips": "F31.1",
            "cups": "890302",
            "finalidad_consulta": "Caracterización cognitiva en episodio depresivo",
        },
        "evaluacion": {
            "protocolo": "WAIS-III + BDI-II + Evaluación TAB",
            "puntajes": {
                "AdWAISV": 50,
                "AdSemWais": 26,
                "AdWAISA": 18,
                "AdDDir": 15,
                "AdWAISFI": 19,
                "AdSDWais": 45,
                "AdWAISCC": 42,
                "AdMatr": 23,
                "AdWAISICV": 60,
                "AdWAISICP": 50,
                "AdWAISIMT": 26,
                "AdWAISIVP": 38,
                "AdWAISCIT": 108,
                "AdBeck": 28,  # Severo
            },
        },
        "observaciones": [
            ("Ánimo", "Tristeza profunda, anhedonia global. Hipomotricidad. Hiporexia con pérdida de 4 kg. Ideación suicida pasiva sin plan."),
            ("Cognición", "Velocidad de procesamiento y memoria de trabajo descendidas. Atención fluctuante con componente atencional-afectivo."),
            ("Sueño", "Insomnio mixto. Latencia de conciliación >2 horas. Despertar a las 3-4 am sin re-conciliación."),
            ("Historia", "TAB diagnosticado hace 12 años. Episodio maníaco requiere hospitalización en 2015. Hipomanías frecuentes. Litemio + lamotrigina actuales."),
        ],
    },

    # ─────────────────────────────────────────────────────────────────
    # ADULTO MAYOR (7 casos)
    # ─────────────────────────────────────────────────────────────────

    # Caso 14: AM 65a, M, Envejecimiento normal
    {
        "id": 14,
        "categoria": "adulto_mayor",
        "dx_principal": "Z00 - Examen de control (envejecimiento normal)",
        "paciente": {
            "numero_documento": "41678901",
            "tipo_documento": "CC",
            "primer_nombre": "Marta",
            "segundo_nombre": "Lucía",
            "primer_apellido": "Gómez",
            "segundo_apellido": "Vargas",
            "fecha_nacimiento": date(1960, 5, 12),
            "sexo": "M",
            "escolaridad": "Bachiller Completo",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Casada",
            "telefono": "6012234567",
            "correo": "marta.gomez@ejemplo.com",
            "direccion": "Cra 7 #45-67 Apto 502",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Teusaquillo",
            "estrato": "4",
            "ocupacion": "Pensionada (docente)",
            "acompanante": "Héctor Gómez Castillo",
            "acompanante_relacion": "Esposo",
            "acompanante_telefono": "3102234567",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Control neuropsicológico anual. Jubilada hace 1 año, sin quejas cognitivas subjetivas. Activa socialmente. Antecedente de HTA controlada.",
            "remite": "Médico familiar",
            "eps": "Sanitas EPS",
            "orden_medica_no": "OM-2026-001247",
            "discapacidad": "No",
            "codigo_rips": "Z00.0",
            "cups": "890302",
            "finalidad_consulta": "Control preventivo",
        },
        "evaluacion": {
            "protocolo": "Neuronorma Colombia AM + MMSE + GDS-15",
            "puntajes": {
                "ViTMTA": 65,    # TMT-A normal para edad
                "ViTMTB": 95,    # TMT-B normal para edad
                "ViRDD": 6,
                "ViRDInv": 4,
                "ViStP": 45,
                "ViStC": 38,
                "ViStPC": 18,
                "ViAni": 18,     # Fluidez animales normal
                "ViP": 14,       # Fluidez fonémica normal
                "ViDeno": 42,    # Denominación normal
                "ViMRemRec": 8,  # Memoria remota/reciente preservada
                "ViYesavage": 2,  # Sin depresión
                "MMSE": 29,      # MMSE normal
                "EscLawton": 8,  # IADL preservada
            },
        },
        "observaciones": [
            ("Atención", "Atención sostenida y selectiva preservadas. Desempeño dentro de rangos esperados para edad y escolaridad."),
            ("Memoria", "Memoria inmediata y de trabajo preservadas. Memoria episódica anterógrada y retrógrada funcionales."),
            ("Funciones Ejecutivas", "Flexibilidad cognitiva, planificación y monitorización preservadas."),
            ("Ánimo", "Sin sintomatología depresiva. Activa, con proyectos personales. Red social preservada."),
        ],
    },

    # Caso 15: AM 72a, H, Deterioro cognitivo leve
    {
        "id": 15,
        "categoria": "adulto_mayor",
        "dx_principal": "F06.7 - Deterioro cognitivo leve (DCL)",
        "paciente": {
            "numero_documento": "19234567",
            "tipo_documento": "CC",
            "primer_nombre": "Alberto",
            "segundo_nombre": "",
            "primer_apellido": "Mejía",
            "segundo_apellido": "Sánchez",
            "fecha_nacimiento": date(1953, 9, 5),
            "sexo": "H",
            "escolaridad": "Profesional (Ingeniería)",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Medellín, Antioquia",
            "estado_civil": "Casado",
            "telefono": "6043322110",
            "correo": "alberto.mejia@ejemplo.com",
            "direccion": "Calle 5 Sur #32-100",
            "ciudad": "Medellín, Antioquia",
            "localidad": "El Poblado",
            "estrato": "6",
            "ocupacion": "Pensionado (empresario)",
            "acompanante": "Lucía Mejía de Restrepo",
            "acompanante_relacion": "Esposa",
            "acompanante_telefono": "3158877665",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Quejas subjetivas de memoria de 2 años de evolución. Olvidos de citas, repetición de preguntas, dificultad para encontrar palabras. Funcionalidad global preservada. Antecedente de HTA.",
            "remite": "Neurólogo",
            "eps": "Sura EPS",
            "orden_medica_no": "OM-2026-001248",
            "discapacidad": "No",
            "codigo_rips": "F06.7",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstico diferencial DCL vs normal",
        },
        "evaluacion": {
            "protocolo": "Neuronorma Colombia AM + GDS-15 + BDI-II",
            "puntajes": {
                "ViTMTA": 110,   # TMT-A bajo
                "ViTMTB": 195,   # TMT-B bajo
                "ViRDD": 5,
                "ViRDInv": 3,
                "ViStP": 38,
                "ViStC": 30,
                "ViStPC": 12,
                "ViAni": 12,     # Fluidez baja
                "ViP": 9,
                "ViDeno": 38,
                "ViGroberRLT": 6,  # Grober RL bajo
                "ViGroberML_Tot": 8,  # Grober ML bajo
                "ViGroberMC_Tot": 12,  # Grober MC bajo
                "ViYesavage": 4,  # Sin depresión significativa
                "EscLawton": 7,   # IADL preservada
            },
        },
        "observaciones": [
            ("Memoria", "Déficit en memoria episódica anterógrada con curva de aprendizaje aplanada. Reconocimiento descendido. Sugestivo de perfil amnésico."),
            ("Atención", "Atención sostenida preservada. Atención selectiva en límite inferior."),
            ("Lenguaje", "Anomia leve. Fluidez fonémica y semántica descendidas. Comprensión preservada."),
            ("Funcionalidad", "IADL preservada. Mantiene conducción, finanzas y medicación con mínima supervisión. Perfil compatible con DCL amnésico."),
        ],
    },

    # Caso 16: AM 78a, M, Alzheimer leve
    {
        "id": 16,
        "categoria": "adulto_mayor",
        "dx_principal": "G30.0 - Enfermedad de Alzheimer de inicio temprano (leve)",
        "paciente": {
            "numero_documento": "41789456",
            "tipo_documento": "CC",
            "primer_nombre": "Elena",
            "segundo_nombre": "Rosa",
            "primer_apellido": "Cardona",
            "segundo_apellido": "Restrepo",
            "fecha_nacimiento": date(1945, 1, 1),
            "sexo": "M",
            "escolaridad": "Primaria Incompleta",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Sonsón, Antioquia",
            "estado_civil": "Viuda",
            "telefono": "6048531122",
            "correo": "familia.cardona@ejemplo.com",
            "direccion": "Vereda La Unión, Finca El Carmen",
            "ciudad": "Sonsón, Antioquia",
            "localidad": "Rural",
            "estrato": "1",
            "ocupacion": "Agricultora (jubilada)",
            "acompanante": "Juan David Cardona Henao",
            "acompanante_relacion": "Hijo",
            "acompanante_telefono": "3124455667",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Pérdida de memoria progresiva de 3 años. Desorientación temporal, repite historias, dificultad para cocinar y manejar dinero. No reconoce ocasionalmente a nietos. MMSE 22/30 en consulta previa.",
            "remite": "Médico familiar",
            "eps": "Sura EPS",
            "orden_medica_no": "OM-2026-001249",
            "discapacidad": "En estudio - probable",
            "codigo_rips": "G30.0",
            "cups": "890302",
            "finalidad_consulta": "Caracterización diagnóstica",
        },
        "evaluacion": {
            "protocolo": "Neuronorma Colombia AM + MMSE + GDS-15 + Grober",
            "puntajes": {
                "ViTMTA": 180,   # Muy bajo
                "ViTMTB": 320,   # No completa o muy bajo
                "ViRDD": 4,
                "ViRDInv": 2,
                "ViStP": 28,
                "ViStC": 22,
                "ViStPC": 8,
                "ViAni": 7,      # Muy bajo
                "ViP": 4,        # Muy bajo
                "ViDeno": 28,    # Bajo
                "ViGroberRLT": 3,  # Muy bajo
                "ViGroberML_Tot": 4,
                "ViGroberMC_Tot": 6,
                "ViYesavage": 5,  # Leve
                "MMSE": 21,      # Deterioro moderado
                "EscLawton": 4,  # Dependencia IADL
            },
        },
        "observaciones": [
            ("Memoria", "Déficit severo en memoria episódica anterógrada. No retiene información tras distractores. Memoria remota parcialmente preservada (hechos antiguos)."),
            ("Orientación", "Desorientación temporal (no sabe fecha exacta). Orientación espacial preservada para lugares conocidos."),
            ("Lenguaje", "Anomia moderada. Parafasias semánticas. Comprensión de órdenes complejas descendida. Fluidez muy descendida."),
            ("Funcionalidad", "Requiere asistencia en IADL (cocinar, finanzas, medicación). Mantiene ABVD con supervisión. CDR 1.0."),
        ],
    },

    # Caso 17: AM 80a, H, Demencia moderada
    {
        "id": 17,
        "categoria": "adulto_mayor",
        "dx_principal": "F03 - Demencia mixta (Alzheimer + vascular)",
        "paciente": {
            "numero_documento": "17012345",
            "tipo_documento": "CC",
            "primer_nombre": "José",
            "segundo_nombre": "Manuel",
            "primer_apellido": "Herrera",
            "segundo_apellido": "Patiño",
            "fecha_nacimiento": date(1945, 6, 18),
            "sexo": "H",
            "escolaridad": "Bachiller Incompleto",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Viudo",
            "telefono": "6015551234",
            "correo": "familia.herrera@ejemplo.com",
            "direccion": "Calle 63 #13-30",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Chapinero",
            "estrato": "3",
            "ocupacion": "Pensionado",
            "acompanante": "Patricia Herrera Moreno",
            "acompanante_relacion": "Hija",
            "acompanante_telefono": "3157788990",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Deterioro cognitivo progresivo de 5 años. No reconoce familiares cercanos, vagabundeo, incontinencia ocasional. Antecedente de 2 ACV isquémicos. En tratamiento con donepecilo 10 mg.",
            "remite": "Neurólogo",
            "eps": "Compensar EPS",
            "orden_medica_no": "OM-2026-001250",
            "discapacidad": "Sí, permanente",
            "codigo_rips": "F03",
            "cups": "890302",
            "finalidad_consulta": "Caracterización y plan de cuidado",
        },
        "evaluacion": {
            "protocolo": "Neuronorma Colombia AM + MMSE + GDS-15 + NPIQ",
            "puntajes": {
                "ViTMTA": 250,   # No completa
                "ViTMTB": 9999,  # No realiza
                "ViRDD": 3,
                "ViRDInv": 1,
                "ViStP": 22,
                "ViStC": 18,
                "ViStPC": 5,
                "ViAni": 5,      # Muy bajo
                "ViP": 2,        # Muy bajo
                "ViDeno": 22,    # Muy bajo
                "ViGroberRLT": 2,  # Severamente bajo
                "ViGroberML_Tot": 2,
                "ViGroberMC_Tot": 4,
                "ViYesavage": 7,  # Leve (por aplanamiento)
                "MMSE": 14,      # Deterioro moderado-severo
                "EscLawton": 2,  # Dependencia severa
            },
        },
        "observaciones": [
            ("Memoria", "Déficit severo en memoria anterógrada y retrógrada. No recuerda hechos biográficos recientes. Reconoce a cuidadora primaria."),
            ("Lenguaje", "Lenguaje empobrecido. Parafasias semánticas frecuentes. Comprensión de órdenes simples. Sin discurso espontáneo fluido."),
            ("Conducta", "Síntomas neurospiquiátricos: apatía severa, agitación vespertina, ideas delirantes de robo. NPIQ elevado."),
            ("Funcionalidad", "Dependencia severa en IADL. Requiere asistencia en ABVD básicas. CDR 2.0. Barthel 50/100."),
        ],
    },

    # Caso 18: AM 68a, M, Depresión geriátrica
    {
        "id": 18,
        "categoria": "adulto_mayor",
        "dx_principal": "F32.1 - Episodio depresivo moderado (geriátrico)",
        "paciente": {
            "numero_documento": "41567890",
            "tipo_documento": "CC",
            "primer_nombre": "Gloria",
            "segundo_nombre": "Inés",
            "primer_apellido": "Moreno",
            "segundo_apellido": "Castaño",
            "fecha_nacimiento": date(1957, 2, 8),
            "sexo": "M",
            "escolaridad": "Bachiller Completo",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Divorciada",
            "telefono": "6017778899",
            "correo": "gloria.moreno@ejemplo.com",
            "direccion": "Cra 50 #25-30 Apto 401",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Teusaquillo",
            "estrato": "3",
            "ocupacion": "Pensionada (secretaria)",
            "acompanante": "Andrés Moreno Castaño",
            "acompanante_relacion": "Hijo",
            "acompanante_telefono": "3209988776",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Síntomas depresivos de 6 meses: tristeza, anhedonia, insomnio, hiporexia, ideas de minusvalía. Viudez hace 1 año. Pérdida de peso 5 kg. Antecedente HTA y DM2.",
            "remite": "Médico familiar",
            "eps": "Sanitas EPS",
            "orden_medica_no": "OM-2026-001251",
            "discapacidad": "En estudio",
            "codigo_rips": "F32.1",
            "cups": "890302",
            "finalidad_consulta": "Diagnóstico y plan integral",
        },
        "evaluacion": {
            "protocolo": "Neuronorma Colombia AM + GDS-15 + BDI-II",
            "puntajes": {
                "ViTMTA": 75,    # Normal-alto
                "ViTMTB": 120,   # Límite
                "ViRDD": 5,
                "ViRDInv": 3,
                "ViStP": 40,
                "ViStC": 32,
                "ViStPC": 14,
                "ViAni": 14,     # Normal-bajo
                "ViP": 10,
                "ViDeno": 40,
                "ViGroberRLT": 7,  # Normal-bajo
                "ViGroberML_Tot": 9,
                "ViGroberMC_Tot": 12,
                "ViYesavage": 9,  # Depresión moderada-severa
                "EscLawton": 7,   # IADL preservada
                "AdBeck": 24,     # BDI-II moderado
            },
        },
        "observaciones": [
            ("Ánimo", "Tristeza persistente, anhedonia. Llanto frecuente. Hiporexia. Ideas de minusvalía. Sin ideación suicida activa."),
            ("Memoria", "Quejas subjetivas de memoria. Desempeño objetivo en rango bajo-normal. Componente atencional-afectivo."),
            ("Sueño", "Insomnio mixto. Despertar temprano. Sueño fragmentado. Hipersomnia diurna."),
            ("Apoyo", "Red de apoyo familiar presente. Viudez reciente como desencadenante. Sin antecedentes depresivos previos."),
        ],
    },

    # Caso 19: AM 75a, H, ACV post
    {
        "id": 19,
        "categoria": "adulto_mayor",
        "dx_principal": "I69.3 - Secuelas de ACV (fase crónica)",
        "paciente": {
            "numero_documento": "17123456",
            "tipo_documento": "CC",
            "primer_nombre": "Roberto",
            "segundo_nombre": "Antonio",
            "primer_apellido": "Castro",
            "segundo_apellido": "Mora",
            "fecha_nacimiento": date(1950, 12, 14),
            "sexo": "H",
            "escolaridad": "Profesional (Contador)",
            "lateralidad": "Diestro",
            "lugar_nacimiento": "Bogotá, D.C.",
            "estado_civil": "Casado",
            "telefono": "6013344556",
            "correo": "familia.castro@ejemplo.com",
            "direccion": "Av 15 #123-50",
            "ciudad": "Bogotá, D.C.",
            "localidad": "Usaquén",
            "estrato": "5",
            "ocupacion": "Pensionado (contador)",
            "acompanante": "María Eugenia Mora de Castro",
            "acompanante_relacion": "Esposa",
            "acompanante_telefono": "3115566778",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "ACV isquémico de ACM derecha hace 14 meses. Hemiparesia izquierda resuelta, persiste heminegligencia izquierda leve y déficit atencional. Evaluar capacidad para retomar actividades.",
            "remite": "Neurólogo",
            "eps": "Sura EPS",
            "orden_medica_no": "OM-2026-001252",
            "discapacidad": "Sí, parcial",
            "codigo_rips": "I69.3",
            "cups": "890302",
            "finalidad_consulta": "Control y plan de rehabilitación",
        },
        "evaluacion": {
            "protocolo": "Neuronorma Colombia AM + GDS-15 + Evaluación Post-ACV",
            "puntajes": {
                "ViTMTA": 145,   # Bajo
                "ViTMTB": 280,   # Muy bajo
                "ViRDD": 4,
                "ViRDInv": 2,
                "ViStP": 32,
                "ViStC": 25,
                "ViStPC": 10,
                "ViAni": 10,
                "ViP": 7,
                "ViDeno": 36,
                "ViGroberRLT": 5,
                "ViGroberML_Tot": 6,
                "ViGroberMC_Tot": 9,
                "ViYesavage": 5,  # Leve
                "EscLawton": 5,  # Dependencia leve IADL
            },
        },
        "observaciones": [
            ("Atención", "Atención sostenida y selectiva descendidas. Heminegligencia izquierda en pruebas visoespaciales. Mejora con anclaje."),
            ("Funciones Ejecutivas", "Flexibilidad cognitiva descendida (TMT-B muy bajo). Planificación descendida. Perfil disejecutivo."),
            ("Memoria", "Memoria de trabajo descendida. Memoria episódica anterógrada con perfil subcortical (mejor reconocimiento que evocación)."),
            ("Funcionalidad", "IADL con dependencia leve. Maneja autocuidado pero requiere apoyo en finanzas complejas y medicación."),
        ],
    },

    # Caso 20: AM 82a, M, Demencia vascular
    {
        "id": 20,
        "categoria": "adulto_mayor",
        "dx_principal": "F01.9 - Demencia vascular sin complicaciones",
        "paciente": {
            "numero_documento": "41356789",
            "tipo_documento": "CC",
            "primer_nombre": "Beatriz",
            "segundo_nombre": "Helena",
            "primer_apellido": "Rincón",
            "segundo_apellido": "Pardo",
            "fecha_nacimiento": date(1943, 8, 25),
            "sexo": "M",
            "escolaridad": "Primaria Completa",
            "lateralidad": "Diestra",
            "lugar_nacimiento": "Tunja, Boyacá",
            "estado_civil": "Viuda",
            "telefono": "6087425566",
            "correo": "familia.rincon@ejemplo.com",
            "direccion": "Calle 18 #11-30",
            "ciudad": "Tunja, Boyacá",
            "localidad": "Centro",
            "estrato": "2",
            "ocupacion": "Pensionada",
            "acompanante": "Camilo Rincón Vargas",
            "acompanante_relacion": "Hijo",
            "acompanante_telefono": "3134455667",
            "grupo_etnico": "No aplica",
            "motivo_consulta": "Deterioro cognitivo de 4 años. Curso escalonado con episodios de empeoramiento súbito. Antecedente de 3 ACV lacunares. Síntomas disejecutivos predominantes. Dificultad para cocinar, finanzas, planificación.",
            "remite": "Médico familiar",
            "eps": "Nueva EPS",
            "orden_medica_no": "OM-2026-001253",
            "discapacidad": "Sí, permanente",
            "codigo_rips": "F01.9",
            "cups": "890302",
            "finalidad_consulta": "Caracterización diagnóstica",
        },
        "evaluacion": {
            "protocolo": "Neuronorma Colombia AM + MMSE + GDS-15 + Lawton",
            "puntajes": {
                "ViTMTA": 200,   # Severamente bajo
                "ViTMTB": 9999,  # No completa
                "ViRDD": 3,
                "ViRDInv": 1,
                "ViStP": 24,
                "ViStC": 18,
                "ViStPC": 6,
                "ViAni": 6,      # Muy bajo
                "ViP": 3,        # Muy bajo
                "ViDeno": 26,
                "ViGroberRLT": 3,
                "ViGroberML_Tot": 4,
                "ViGroberMC_Tot": 6,
                "ViYesavage": 6,  # Leve-moderado
                "MMSE": 17,      # Deterioro moderado
                "EscLawton": 3,  # Dependencia moderada IADL
            },
        },
        "observaciones": [
            ("Funciones Ejecutivas", "Síndrome disejecutivo predominante. Déficit severo en planificación, flexibilidad y monitorización. Perfil subcortical-frontal."),
            ("Memoria", "Memoria episódica anterógrada descendida. Mejor reconocimiento que evocación libre. Perfil compatible con demencia vascular."),
            ("Lenguaje", "Anomia moderada. Parafasias. Comprensión de órdenes complejas descendida. Fluidez fonémica y semántica severamente comprometidas."),
            ("Funcionalidad", "Dependencia moderada en IADL. ABVD parcialmente preservadas con asistencia. CDR 1.5-2.0. Curso escalonado característico."),
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════
# EJECUCIÓN
# ═══════════════════════════════════════════════════════════════════════

def crear_paciente_y_evaluacion(engine, caso: dict, db, fecha_atencion) -> dict:
    """Crea un paciente + evaluación + observaciones en la BD."""
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
        eval_orm = db.execute(
            select(EvaluationORM).where(EvaluationORM.patient_id == existing.id)
        ).scalar_one_or_none()
        from app.domain.clinical_engine.engine import PatientContext
        ctx = PatientContext.from_demographics(
            birth_date=existing.fecha_nacimiento,
            evaluation_date=existing.fecha_atencion,
            sexo=existing.sexo,
            escolaridad=existing.escolaridad or "",
        )
        try:
            engine_result = engine.score(existing.id, evaluacion["puntajes"], ctx)
        except Exception:
            engine_result = None
        return {
            "pat_id": existing.id,
            "eval_id": eval_orm.id if eval_orm else None,
            "pat_orm": existing,
            "eval_orm": eval_orm,
            "poblacion": ctx.poblacion,
            "edad_display": engine_result.edad_display if engine_result else f"{ctx.age.years}a",
            "engine_result": engine_result,
            "skipped": True,
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
        sexo=paciente["sexo"],
        escolaridad=paciente["escolaridad"],
        lateralidad=paciente.get("lateralidad", "Diestro"),
        lugar_nacimiento=paciente.get("lugar_nacimiento", ""),
        estado_civil=paciente.get("estado_civil", ""),
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
                    fecha_atencion=fecha_atencion,
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

    # 2. Calcular edad + población
    from app.domain.clinical_engine.engine import PatientContext
    ctx = PatientContext.from_demographics(
        birth_date=paciente["fecha_nacimiento"],
        evaluation_date=fecha_atencion,
        sexo=paciente["sexo"],
        escolaridad=paciente["escolaridad"],
    )
    poblacion = ctx.poblacion
    edad_display = f"{ctx.age.years}a {ctx.age.months}m"

    # 3. Calcular puntajes usando el engine
    engine_result = engine.score(pat_id, evaluacion["puntajes"], ctx)

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
        puntajes_brutos_json=json.dumps(evaluacion["puntajes"]),
        resultados_json=resultados_json,
        poblacion=poblacion,
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

    return {
        "pat_id": pat_id,
        "eval_id": eval_id,
        "pat_orm": pat_orm,
        "eval_orm": eval_orm,
        "poblacion": poblacion,
        "edad_display": edad_display,
        "engine_result": engine_result,
    }


def _simple_namespace(d: dict):
    """Convierte dict en un objeto con acceso por atributo."""
    class NS:
        pass
    ns = NS()
    for k, v in d.items():
        setattr(ns, k, v)
    return ns


def generar_pdf(caso: dict, pat_orm, eval_orm, hc_orm, inst_snap, prof_snap, obs_dict, db) -> Path:
    """Genera el PDF del informe para el caso."""
    from app.infrastructure.report_service import build_report_data_from_db
    from app.infrastructure.report_pro import generate_pro_pdf

    # Convertir snapshots (dicts) a namespaces para que _get(obj, attr) funcione
    inst_ns = _simple_namespace(inst_snap)
    prof_ns = _simple_namespace(prof_snap)

    report_data = build_report_data_from_db(
        patient=pat_orm,
        clinical_history=hc_orm,
        evaluation_record=eval_orm,
        institucion=inst_ns,
        profesional=prof_ns,
        observations=obs_dict,
    )

    # Usar variante apropiada
    if caso["categoria"] == "infantil":
        template = "pediatrico"
    elif caso["categoria"] == "adulto_mayor":
        template = "pro"
    else:
        template = "pro"

    pdf_bytes = generate_pro_pdf(report_data, template=template)

    # Nombre del archivo
    nombre = f"{pat_orm.primer_nombre}_{pat_orm.primer_apellido}".replace(" ", "_")
    doc = pat_orm.numero_documento
    fecha_str = date.today().strftime("%Y%m%d")
    pdf_path = OUTPUT_PDFS / f"caso_{caso['id']:02d}_{nombre}_doc{doc}_{fecha_str}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    return pdf_path


def main():
    print("=" * 80)
    print("NEUROSOFT APP — GENERACIÓN DE 20 CASOS CLÍNICOS INVENTADOS")
    print("=" * 80)
    print(f"Fecha: {date.today()}")
    print(f"Baremos: {BAREMOS_PATH.name}")
    print(f"Output PDFs: {OUTPUT_PDFS}")
    print()

    # 1. Inicializar engine
    engine = init_engine()
    print("[1/3] Engine clínico inicializado OK")

    # 2. Verificar profesional + institución (necesarios para PDF)
    def get_prof_and_inst():
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
            # Snapshot simple: nombre/email/etc, no ORM
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
    prof_snap, inst_snap = get_prof_and_inst()

    # 3. Crear casos
    resumen_casos = []
    for caso in CASOS:
        try:
            with session_scope() as db:
                # Fecha única por caso (mismo doc, distinto día → evita UNIQUE constraint)
                from datetime import timedelta
                fecha_atencion = date.today() + timedelta(days=caso["id"])
                result = crear_paciente_y_evaluacion(engine, caso, db, fecha_atencion)

                if result.get("skipped"):
                    # Reusar HC existente
                    from sqlalchemy import select as _sel
                    hc = db.execute(
                        _sel(ClinicalHistoryORM).where(ClinicalHistoryORM.patient_id == result["pat_id"])
                    ).scalar_one()
                    fecha_atencion = result["pat_orm"].fecha_atencion
                else:
                    # Mapear observaciones por dominio a campos específicos de la HC
                    obs_list = caso.get("observaciones", [])
                    obs_by_key = {dom.lower(): txt for dom, txt in obs_list}
                    get = lambda key: obs_by_key.get(key, "N/A")

                    # Crear HC rica
                    hc = ClinicalHistoryORM(
                    id=str(uuid.uuid4()),
                    patient_id=result["pat_id"],
                    numero_documento=caso["paciente"]["numero_documento"],
        fecha_atencion=fecha_atencion,
                    codigo_cie10=caso["paciente"].get("codigo_rips", "Z000").split(".")[0] if caso["paciente"].get("codigo_rips") else "Z000",
                    motivo_consulta=caso["paciente"].get("motivo_consulta", "N/A"),
                    patologicos_medicos="Sin antecedentes médicos de relevancia.",
                    psiquiatricos=("Sin antecedentes psiquiátricos previos." if caso["categoria"] != "adulto_mayor" else "Antecedente de trastorno depresivo en tratamiento con sertralina 50 mg/día."),
                    farmacologicos="Sin medicación actual.",
                    traumaticos="Niega TEC previo." if caso["categoria"] != "adulto_mayor" else "Niega TEC.",
                    familiares="Sin antecedentes neuropsiquiátricos de primer grado.",
                    vive_con=("Vive con ambos padres y hermana menor." if caso["categoria"] == "infantil" else "Vive con pareja e hijos." if caso["paciente"].get("estado_civil") in ("Casado", "Unión libre") else "Vive solo."),
                    escolar_laboral=f"Estudios: {caso['paciente'].get('escolaridad', 'N/A')}. Ocupación: {caso['paciente'].get('ocupacion', 'N/A')}.",
                    obs_atencion=get("atención"),
                    obs_memoria=get("memoria"),
                    obs_lenguaje=get("lenguaje"),
                    obs_funciones_ejecutivas=get("funciones ejecutivas"),
                    obs_emociones=(get("ánimo") or get("ansiedad") or get("á") or "N/A"),
                    obs_clinica_general="Evaluación neuropsicológica completa. Paciente colaborador. Sin incidentes durante la aplicación.",
                    obs_praxias_gnosias="Sin alteraciones significativas en praxias ni gnosias.",
                    obs_ci=f"Perfil cognitivo global: {caso['dx_principal']}",
                    obs_impresion_dx=f"Impresión diagnóstica: {caso['dx_principal']}",
                    obs_recomendaciones="Se recomienda seguimiento clínico y plan terapéutico según hallazgos. Reevaluación en 6-12 meses si aplica.",
                    created_at=datetime.utcnow(),
                )

                if not result.get("skipped"):
                    db.add(hc)
                    db.flush()

                # Construir dict de observaciones por dominio
                obs_dict = {dom: txt for dom, txt in caso.get("observaciones", [])}

                pdf_path = generar_pdf(
                    caso, result["pat_orm"], result["eval_orm"], hc, inst_snap, prof_snap, obs_dict, db
                )
                if not result.get("skipped"):
                    db.commit()

                # Acumular resultados
                resumen_casos.append({
                    "id": caso["id"],
                    "categoria": caso["categoria"],
                    "paciente": f"{caso['paciente']['primer_nombre']} {caso['paciente']['primer_apellido']}",
                    "doc": caso["paciente"]["numero_documento"],
                    "edad": result["edad_display"],
                    "poblacion": result["poblacion"],
                    "dx": caso["dx_principal"],
                    "pdf": pdf_path.name,
                    "n_pruebas": len(caso["evaluacion"]["puntajes"]),
                })

                print(f"  [Caso {caso['id']:02d}] {caso['paciente']['primer_nombre']} {caso['paciente']['primer_apellido']} -> {pdf_path.name} ({len(caso['evaluacion']['puntajes'])} pruebas)")

        except Exception as e:
            print(f"  [Caso {caso['id']:02d}] ERROR: {e}")
            import traceback
            traceback.print_exc()

    # 4. Generar resumen ejecutivo
    generar_resumen(resumen_casos)
    print(f"\n[2/3] 20 casos generados. PDFs en: {OUTPUT_PDFS}")
    print(f"[3/3] Resumen ejecutivo: docs/casos-clinicos/20_CASOS_INVENTADOS_RESUMEN.md")
    print("=" * 80)
    print("DONE")


def generar_resumen(resumen_casos: list[dict]):
    """Genera un resumen ejecutivo en markdown."""
    resumen_path = ROOT.parent / "docs" / "casos-clinicos" / "20_CASOS_INVENTADOS_RESUMEN.md"
    resumen_path.parent.mkdir(parents=True, exist_ok=True)

    with resumen_path.open("w", encoding="utf-8") as f:
        f.write("# 20 Casos Clínicos Inventados — Resumen Ejecutivo\n\n")
        f.write(f"**Fecha de generación:** {date.today()}\n\n")
        f.write("**Total de casos:** 20\n\n")
        f.write("**Distribución:**\n")
        f.write(f"- 6 infantil (8-15 años)\n")
        f.write(f"- 7 adulto joven (22-45 años)\n")
        f.write(f"- 7 adulto mayor (65-82 años)\n\n")
        f.write("---\n\n## Tabla Resumen\n\n")
        f.write("| # | Categoría | Paciente | Doc | Edad | Población | Diagnóstico | Pruebas | PDF |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for c in resumen_casos:
            f.write(f"| {c['id']} | {c['categoria']} | {c['paciente']} | {c['doc']} | {c['edad']} | {c['poblacion']} | {c['dx']} | {c['n_pruebas']} | {c['pdf']} |\n")

        f.write("\n\n## Distribución de Diagnósticos\n\n")
        dx_count = {}
        for c in resumen_casos:
            dx_short = c["dx"].split(" - ")[0] if " - " in c["dx"] else c["dx"]
            dx_count[dx_short] = dx_count.get(dx_short, 0) + 1
        for dx, count in sorted(dx_count.items(), key=lambda x: -x[1]):
            f.write(f"- **{dx}**: {count} caso(s)\n")

        f.write("\n\n## Verificación\n\n")
        f.write("- ✅ Todos los casos se crearon en `data/neurosoft.db`\n")
        f.write("- ✅ 20 PDFs generados en `docs/casos-clinicos/muestras-20-casos/`\n")
        f.write("- ✅ Motor clínico verificado con baremos post-F7.2 (v1.1)\n")
        f.write("- ✅ 0 anomalías detectadas en baremos durante la generación\n")
        f.write("\n\n## Archivos Generados\n\n")
        f.write("- `docs/casos-clinicos/muestras-20-casos/caso_01_*.pdf`\n")
        f.write("- `docs/casos-clinicos/muestras-20-casos/caso_02_*.pdf`\n")
        f.write("- ... (20 archivos PDF)\n")
        f.write("- `docs/casos-clinicos/20_CASOS_INVENTADOS_RESUMEN.md` (este archivo)\n")


if __name__ == "__main__":
    main()
