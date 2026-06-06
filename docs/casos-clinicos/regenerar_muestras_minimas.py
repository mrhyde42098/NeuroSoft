"""
regenerar_muestras_minimas.py
=============================
Genera exactamente 8 PDF de muestra (1 caso ficticio × 1 variante) para QA visual
post-rediseño del informe NeuroSoft.

Uso:
    cd D:\\NeuroSoftApp\\neurosoft-backend
    python ..\\docs\\casos-clinicos\\regenerar_muestras_minimas.py

Salida:
    docs/samples/informes-audit/{variante}_{slug}.pdf
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[2] / "neurosoft-backend"
sys.path.insert(0, str(BACKEND))

from app.infrastructure.report_pro import generate_pro_pdf  # noqa: E402
from app.infrastructure.report_service import NeuroPDFGenerator, ReportData  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "samples" / "informes-audit"
OUT.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────
# Motor clínico real: calcula escalares/Z/CI/interpretación con BD_NEURO_MAESTRA
# (igual que cuando el clínico ingresa puntajes brutos en la app y da "generar")
# ─────────────────────────────────────────────────────────────────────────
def _wisc_resultados_motor(birth: date, eval_date: date, sexo: str,
                           escolaridad: str, subtest_pd: dict[str, int]) -> list[dict]:
    """Corre el ClinicalEngine sobre puntajes brutos WISC-IV reales.

    1) Califica los subtests (bruto → escalar).
    2) Suma los escalares por índice y califica los índices (suma → CI).
    Devuelve la lista de resultados como dicts (formato que consume el informe).
    """
    from dataclasses import asdict
    from app.domain.clinical_engine.baremos_loader import BaremosLoader
    from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext

    # Cargar baremos una sola vez
    try:
        BaremosLoader.instance()
    except Exception:
        BaremosLoader.load(BACKEND / "data" / "BD_NEURO_MAESTRA.json")

    eng = ClinicalEngine()
    ctx = PatientContext.from_demographics(birth, eval_date, sexo, escolaridad)

    # Paso 1: subtests
    res_sub = eng.score("caso-completo", subtest_pd, ctx, "WISC-IV Colombia")
    escalares = {r.test_id: r.puntaje_escalar for r in res_sub.resultados}

    # Paso 2: índices WISC-IV (suma de escalares de sus subtests)
    INDICES = {
        "NiWISCIndComVer": ("NiWiscSem", "NiWiscVoc", "NiWiscCom"),
        "NiWISCIndRazPer": ("NiWiscDC", "NiWiscConD", "NiWiscMat"),
        "NiWISCIndMemTra": ("NiWiscRDD", "NiWiscLN"),
        "NiWISCIndVelPro": ("NiWiscCl", "NiWiscBusSim"),
        "NiWISCTot": ("NiWiscSem", "NiWiscVoc", "NiWiscCom", "NiWiscDC",
                      "NiWiscConD", "NiWiscMat", "NiWiscRDD", "NiWiscLN",
                      "NiWiscCl", "NiWiscBusSim"),
    }
    sumas: dict[str, int] = {}
    for idx_id, comps in INDICES.items():
        vals = [escalares.get(t) for t in comps]
        if all(v is not None for v in vals):
            sumas[idx_id] = int(sum(vals))
    res_idx = eng.score("caso-completo", sumas, ctx, "WISC-IV Colombia")

    out: list[dict] = []
    for r in list(res_sub.resultados) + list(res_idx.resultados):
        d = asdict(r)
        d.pop("metadata", None)
        out.append(d)
    return out


def _row(test_id, nombre, pd, esc, z, inter, dominio, tipo="escalar"):
    return {
        "test_id": test_id,
        "test_nombre": nombre,
        "puntaje_bruto": pd,
        "puntaje_escalar": esc,
        "z_equivalente": z,
        "interpretacion": inter,
        "dominio_cognitivo": dominio,
        "tipo_metrica": tipo,
    }


def _wisc_jesus_like():
    """caso_06 David López — perfil WISC referencia."""
    return ReportData(
        nombre_completo="David López Referencia",
        numero_documento="1121000006",
        tipo_documento="TI",
        fecha_nacimiento=date(2009, 1, 15),
        fecha_atencion=date(2025, 5, 15),
        edad_display="16a 11m",
        sexo="M",
        escolaridad="Secundaria",
        poblacion="infantil",
        motivo_consulta="Evaluación cognitiva integral.",
        orden_no="264497073",
        protocolo="WISC-IV Colombia",
        obs_atencion="Atención sostenida disminuida en tareas verbales.",
        obs_lenguaje="Vocabulario limitado para la edad.",
        obs_funciones_ejecutivas="Dificultades en memoria de trabajo verbal.",
        resultados=[
            _row("NiWiscDC", "Diseño con Cubos", 53, 11, 0.33, "Promedio", "Visoespacial"),
            _row("NiWiscSem", "Semejanzas", 32, 11, 0.33, "Promedio", "Comprensión Verbal"),
            _row("NiWiscVoc", "Vocabulario", 37, 6, -1.33, "Bajo", "Comprensión Verbal"),
            _row("NiWiscCl", "Claves", 46, 8, -0.67, "Promedio", "Velocidad de Procesamiento"),
            _row("NiWiscAri", "Aritmética", 21, 6, -1.33, "Limítrofe", "Memoria de Trabajo"),
            _row("NiWISCIndComVer", "ICV", None, 98, -0.13, "Promedio", "Comprensión Verbal", "ci"),
            _row("NiWISCIndRazPer", "IRP", None, 105, 0.33, "Promedio", "Razonamiento Perceptual", "ci"),
            _row("NiWISCIndMemTra", "IMT", None, 86, -0.93, "Promedio Bajo", "Memoria de Trabajo", "ci"),
            _row("NiWISCIndVelPro", "IVP", None, 88, -0.80, "Promedio Bajo", "Velocidad de Procesamiento", "ci"),
            _row("NiWISCTot", "CIT", None, 93, -0.47, "Promedio", "Global", "ci"),
        ],
    )


def _caso_completo_wisc():
    """Caso ficticio 100% diligenciado (WISC-IV Colombia).

    Sirve para ver cómo se consigna VERBATIM en el informe completo cada campo
    que el profesional escribe: todos los antecedentes, historia psicosocial,
    observación, análisis por dominio, impresión diagnóstica y recomendaciones.
    Población infantil — protocolo WISC-IV (el que sí está disponible).
    """
    return ReportData(
        # ── Institución ──
        institucion_nombre="Centro de Neuropsicología Clínica",
        institucion_nit="901.234.567-8",
        institucion_dir="Calle 100 #15-20, Cons. 504, Bogotá",
        institucion_tel="(601) 743 2100",
        # ── Sociodemográfico ──
        nombre_completo="Isabella Restrepo Gómez",
        numero_documento="1012345678",
        tipo_documento="TI",
        fecha_nacimiento=date(2017, 3, 8),
        fecha_atencion=date(2026, 5, 20),
        edad_display="9a 2m",
        sexo="Femenino",
        escolaridad="Primaria — 3° grado",
        lateralidad="Diestra",
        ocupacion="Estudiante",
        ciudad="Bogotá D.C.",
        acompanante="Madre (Catalina Gómez, 38 años)",
        remite="Dra. Liliana Díaz — Psiquiatría Infantil",
        orden_no="264497091",
        eps="Sura EPS",
        poblacion="infantil",
        # ── Motivo de consulta (enriquecido) ──
        motivo_consulta=(
            "Niña de 9 años remitida por psiquiatría infantil para evaluación "
            "neuropsicológica con el fin de precisar el perfil cognitivo y apoyar "
            "la definición diagnóstica ante sospecha de TDAH presentación "
            "combinada y dificultades de aprendizaje en lectoescritura. La madre "
            "refiere: «se distrae con todo, no termina las tareas y la profesora "
            "dice que va atrasada en lectura». Se solicita caracterización de "
            "atención, memoria de trabajo y funciones ejecutivas para orientar el "
            "plan de intervención y los apoyos escolares."
        ),
        # ── Antecedentes médicos ──
        patologicos_medicos=(
            "Embarazo deseado, controlado. Parto a término (39 semanas) por "
            "cesárea. Sin hospitalizaciones relevantes. Desarrollo motor dentro "
            "de lo esperado (marcha a los 13 meses)."
        ),
        alergicos="Rinitis alérgica estacional. Sin alergias medicamentosas conocidas.",
        sensoriales_motores=(
            "Agudeza visual y auditiva normales (tamizajes escolares 2025). "
            "Coordinación motora gruesa adecuada; refiere torpeza en motricidad fina."
        ),
        toxicos="No reporta exposición a tóxicos.",
        psiquiatricos=(
            "Sin antecedentes psiquiátricos personales previos. Primera consulta "
            "de salud mental a los 8 años por inquietud motora."
        ),
        terapeuticos="Actualmente en terapia de lenguaje (fonoaudiología) desde marzo 2026.",
        farmacologicos="No recibe psicofármacos al momento de la evaluación.",
        quirurgicos="Adenoidectomía a los 5 años, sin complicaciones.",
        traumaticos="Niega traumatismos craneoencefálicos.",
        familiares=(
            "Padre con antecedente de dificultades de aprendizaje en la infancia. "
            "Tío materno en tratamiento por TDAH. Madre con trastorno de ansiedad."
        ),
        paraclinicos="Hemograma y perfil tiroideo (abr-2026) dentro de límites normales.",
        # ── Historia familiar / social / funcional ──
        vive_con=(
            "Vive con ambos padres y un hermano menor (5 años). Núcleo familiar "
            "funcional; la madre es la cuidadora principal."
        ),
        abc=(
            "Independiente para alimentación, higiene y vestido. Requiere "
            "supervisión para organizar materiales escolares y cumplir rutinas."
        ),
        escolar_laboral=(
            "Cursa 3° de primaria en colegio bilingüe. Rendimiento aceptable en "
            "matemáticas, descendido en lectura y escritura. La docente reporta "
            "que se levanta del puesto y no termina las actividades en clase."
        ),
        patron_sueno=(
            "Duerme ~9 horas. Dificultad para conciliar el sueño los días de "
            "colegio; sueño reparador los fines de semana."
        ),
        patron_alimentacion="Selectiva con verduras; apetito conservado. IMC en percentil normal.",
        comportamiento_animo=(
            "Niña afectuosa y sociable. Tolera mal la frustración ante tareas "
            "difíciles; episodios de llanto cuando no logra terminar a tiempo."
        ),
        # ── Observación clínica conductual ──
        obs_clinica_general=(
            "Escolar que ingresa alerta, orientada en persona y espacio, con "
            "adecuada presentación. Establece contacto visual y rapport con "
            "facilidad. Durante la sesión se observa inquietud motora (mueve "
            "pies y manos, se levanta en dos ocasiones), latencias de respuesta "
            "variables y necesidad de redirección verbal frecuente. Colaboradora, "
            "se beneficia del refuerzo positivo. Lenguaje espontáneo fluido, "
            "articulación con leve dislalia residual."
        ),
        # ── Análisis por dominio (verbatim) ──
        obs_atencion=(
            "Atención sostenida disminuida: comete omisiones en tareas largas y "
            "su rendimiento decae con el tiempo en el puesto. La atención "
            "selectiva mejora con consignas cortas y apoyo visual. Memoria de "
            "trabajo limítrofe (IMT=77), lo que repercute en el seguimiento de "
            "instrucciones de varios pasos."
        ),
        obs_memoria=(
            "Memoria de reconocimiento conservada. La memoria de trabajo es el "
            "componente más afectado del perfil (IMT=77, limítrofe), con descenso "
            "marcado en Retención de Dígitos."
        ),
        obs_praxias_gnosias=(
            "Praxias constructivas adecuadas (Diseño con Cubos PE=11). Gnosias "
            "visuales conservadas. Razonamiento perceptual en rango promedio "
            "(IRP=100). Leve torpeza en grafomotricidad."
        ),
        obs_lenguaje=(
            "Vocabulario expresivo por debajo de lo esperado para la edad "
            "(Vocabulario PE=4, bajo), con comprensión preservada. El índice de "
            "comprensión verbal (ICV=87) queda en promedio bajo. Persiste dislalia "
            "leve en abordaje fonoaudiológico."
        ),
        obs_funciones_ejecutivas=(
            "Dificultades en autorregulación, planificación y memoria de trabajo. "
            "Requiere apoyo externo para inhibir respuestas impulsivas y "
            "organizar la tarea. Se beneficia de la segmentación de actividades."
        ),
        obs_emociones=(
            "Ansiedad anticipatoria ante tareas evaluativas y baja tolerancia a "
            "la frustración. Sin indicadores de sintomatología depresiva."
        ),
        obs_ci=(
            "CI Total = 88 (promedio bajo), con perfil heterogéneo: IRP=100 (más "
            "alto) frente a IMT=77 (más bajo). La puntuación global no captura la "
            "variabilidad intraindividual, por lo que conviene interpretar por "
            "índices más que por el CIT."
        ),
        obs_funcionalidad=(
            "Funcionalidad preservada para la vida diaria; el impacto se concentra "
            "en el desempeño escolar (lectura, completar tareas, organización)."
        ),
        # ── Impresión diagnóstica ──
        codigo_cie10="F90.0",
        codigo_cie10_desc="Trastorno de la actividad y de la atención (TDAH presentación combinada)",
        obs_impresion_dx=(
            "Perfil neuropsicológico compatible con Trastorno por Déficit de "
            "Atención e Hiperactividad (TDAH), presentación combinada (CIE-10 "
            "F90.0), con afectación de la atención sostenida, la memoria de "
            "trabajo y las funciones ejecutivas, en el contexto de un "
            "funcionamiento intelectual promedio bajo (CIT=88). Coexisten una "
            "dificultad específica del lenguaje expresivo y rasgos de ansiedad "
            "anticipatoria. Se recomienda integrar estos hallazgos con la "
            "valoración psiquiátrica para la confirmación diagnóstica y la "
            "definición del manejo farmacológico, si procede."
        ),
        # ── Recomendaciones (agrupadas, verbatim del clínico) ──
        obs_recomendaciones=(
            "[MÉDICA] (alta) Continuar seguimiento por psiquiatría infantil para "
            "definir manejo farmacológico del TDAH según evolución.\n"
            "[ESCOLAR] (alta) Implementar apoyos en el aula: ubicación cercana al "
            "docente, instrucciones cortas y fraccionadas, tiempo adicional en "
            "evaluaciones y verificación de la agenda de tareas.\n"
            "[ESCOLAR] (media) Plan de apoyo en lectoescritura con refuerzo "
            "individualizado y material multisensorial.\n"
            "[TERAPÉUTICA] (alta) Iniciar entrenamiento en funciones ejecutivas "
            "y autorregulación (técnicas de organización, autoinstrucciones).\n"
            "[TERAPÉUTICA] (media) Continuar fonoaudiología enfocada en lenguaje "
            "expresivo y dislalia residual.\n"
            "[FAMILIAR] (media) Psicoeducación a padres sobre TDAH y pautas de "
            "manejo conductual en casa (rutinas, refuerzo positivo, economía de "
            "fichas).\n"
            "[SEGUIMIENTO] (baja) Reevaluación neuropsicológica en 12 meses para "
            "monitorear respuesta a la intervención."
        ),
        protocolo="WISC-IV Colombia",
        # ── Profesional ──
        profesional_nombre="Ps. Mariana Castro Ruiz",
        profesional_titulo="Psicóloga · Magíster en Neuropsicología Clínica",
        profesional_registro="C.C. 1.020.456.789 — T.P. 198765",
        eval_id="EV-2026-000091",
        # Puntajes BRUTOS ingresados por el clínico — el motor real (baremos
        # WISC-IV Colombia) calcula escalar/Z/CI/interpretación.
        resultados=_wisc_resultados_motor(
            birth=date(2017, 3, 8),
            eval_date=date(2026, 5, 20),
            sexo="F",
            escolaridad="Primaria",
            subtest_pd={
                "NiWiscDC": 30, "NiWiscSem": 18, "NiWiscVoc": 14, "NiWiscCom": 16,
                "NiWiscConD": 14, "NiWiscMat": 20, "NiWiscRDD": 9, "NiWiscLN": 12,
                "NiWiscCl": 38, "NiWiscBusSim": 18,
            },
        ),
    )


def _infantil_santiago():
    return ReportData(
        nombre_completo="Santiago Morales",
        numero_documento="1121000001",
        edad_display="10a 0m",
        sexo="M",
        escolaridad="Primaria",
        poblacion="infantil",
        motivo_consulta="Control de aprendizaje.",
        obs_clinica_general="Niño colaborador, contacto visual adecuado.",
        resultados=[
            _row("NiWiscDC", "Diseño con Cubos", 35, 10, 0.0, "Promedio", "Visoespacial"),
            _row("NiWiscSem", "Semejanzas", 22, 11, 0.33, "Promedio", "Comprensión Verbal"),
            _row("NiWiscVoc", "Vocabulario", 25, 9, -0.33, "Promedio", "Comprensión Verbal"),
            _row("NiWiscRDD", "Retención de Dígitos", 12, 10, 0.0, "Promedio", "Memoria de Trabajo"),
        ],
    )


def _adulto_ricardo():
    return ReportData(
        nombre_completo="Ricardo Pinzón",
        numero_documento="79456789",
        edad_display="41a 1m",
        sexo="M",
        escolaridad="Universitaria",
        poblacion="adulto_joven",
        motivo_consulta="Sospecha de TDAH de inicio tardío.",
        obs_atencion="Distractibilidad en tareas sostenidas.",
        resultados=[
            _row("AdWAISV", "Vocabulario", 48, 12, 0.33, "Promedio", "Comprensión Verbal"),
            _row("AdWAISA", "Aritmética", 14, 11, 0.0, "Promedio", "Memoria de Trabajo"),
            _row("AdDDir", "Dígitos Directos", 11, 12, 0.33, "Promedio", "Memoria de Trabajo"),
            _row("AdTMTA", "TMT-A", 35, 9, -0.33, "Promedio", "Atención"),
        ],
    )


def _am_carlos():
    return ReportData(
        nombre_completo="Carlos Hernández",
        numero_documento="52100007",
        edad_display="80a 5m",
        sexo="M",
        escolaridad="Primaria",
        poblacion="adulto_mayor",
        motivo_consulta="Referencia AM verificada.",
        resultados=[
            _row("ViRDD", "Dígitos Directos", 4, 13, 0.33, "Promedio", "Memoria"),
            _row("ViTMTA", "TMT-A", 239, 6, -1.33, "Limítrofe", "Atención"),
            _row("ViStP", "Stroop Palabra", 8, 3, -2.0, "Bajo", "Ejecutivas"),
            _row("ViGroberRLT", "Grober RLT", 3, 3, -2.0, "Bajo", "Memoria"),
            _row("ViYesavage", "Yesavage", 2, 2, 0.0, "Normal", "Ánimo"),
        ],
    )


def _parcial_sofia():
    return ReportData(
        nombre_completo="Sofía Ramírez",
        numero_documento="1121000007",
        edad_display="9a 4m",
        sexo="F",
        poblacion="infantil",
        motivo_consulta="Evaluación inconclusa por fatiga.",
        informe_inconcluso_cat="fatiga",
        informe_inconcluso_nota="La paciente solicitó pausa tras dos subtests.",
        resultados=[
            _row("NiWiscDC", "Diseño con Cubos", 33, 10, 0.0, "Promedio", "Visoespacial"),
            _row("NiWiscSem", "Semejanzas", 19, 8, -0.67, "Promedio", "Comprensión Verbal"),
        ],
    )


def _therapy_fixture():
    data = ReportData(
        nombre_completo="Ana Lucía Vega",
        numero_documento="52999001",
        edad_display="34a",
        sexo="F",
        motivo_consulta="Ansiedad generalizada.",
        obs_recomendaciones="Seguimiento ambulatorio en 3 meses.",
    )
    data.therapy_plan = {
        "enfoque": "cbt",
        "diagnostico": "F41.1",
        "fecha_inicio": "2025-01-10",
        "fecha_fin": "2026-05-01",
    }
    data.therapy_objectives = [
        {"descripcion": "Reducir evitación situacional", "progreso_pct": 80, "estado": "cumplido"},
        {"descripcion": "Reestructurar pensamientos catastróficos", "progreso_pct": 70, "estado": "parcial"},
    ]
    data.therapy_sessions_count = 18
    data.therapy_motivo_cierre = "alta"
    data.therapy_nota_cierre = (
        "Paciente muestra disminución significativa de síntomas ansiosos "
        "y mayor participación en actividades cotidianas."
    )
    return data


MATRIZ = [
    ("pro", "caso_completo_isabella", _caso_completo_wisc, "pro"),
    ("estandar", "caso_06_david_lopez", _wisc_jesus_like, "estandar"),
    ("pediatrico", "caso_01_santiago", _infantil_santiago, "pediatrico"),
    ("medicolegal", "caso_10_ricardo", _adulto_ricardo, "medicolegal"),
    ("junta_medica", "caso_16_carlos", _am_carlos, "junta_medica"),
    ("inconcluso", "caso_07_sofia", _parcial_sofia, "inconcluso"),
    ("paciente", "caso_01_santiago", _infantil_santiago, "paciente"),
    ("therapy_closure", "terapia_ana_vega", _therapy_fixture, "therapy_closure"),
]


def main() -> int:
    for variant, slug, builder, template in MATRIZ:
        data = builder()
        try:
            if template == "estandar":
                pdf = NeuroPDFGenerator().generate(data)
            else:
                pdf = generate_pro_pdf(data, template=template)
        except Exception as exc:
            print(f"FAIL {variant}: {exc}")
            return 1
        out = OUT / f"{variant}_{slug}.pdf"
        out.write_bytes(pdf)
        print(f"OK  {out.name} ({len(pdf)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
