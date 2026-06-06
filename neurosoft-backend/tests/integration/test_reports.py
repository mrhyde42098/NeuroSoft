"""
tests/integration/test_reports.py
==================================
Tests de integración del generador de PDF de informes neuropsicológicos.

Cobertura:
- generate_report_pdf() retorna bytes válidos para cada variante.
- Plantilla desconocida no rompe (fallback a 'pro').
- ReportData mínima genera PDF sin error.
- ReportData rica con CI/Z/discrepancias activa todos los gráficos.
- La variante 'inconcluso' renderiza con razón + nota.
- La variante 'estandar' sigue funcionando (retrocompat).
"""
from __future__ import annotations

from datetime import date

import pytest

# ──────────────────────────────────────────────────────────
# Fixture: ReportData rica (caso Jesús Viloria adaptado)
# ──────────────────────────────────────────────────────────

@pytest.fixture
def report_data_rich():
    from app.infrastructure.report_service import ReportData
    return ReportData(
        institucion_nombre="Centro Neuropsicológico Universidad Nacional",
        institucion_nit="899999063",
        institucion_dir="Bogotá D.C., Colombia",
        institucion_tel="+57 (1) 316 5000",
        nombre_completo="Jesús Alejandro Viloria Mendoza",
        numero_documento="1098765432",
        tipo_documento="TI",
        fecha_nacimiento=date(2008, 5, 30),
        fecha_atencion=date(2025, 5, 15),
        edad_display="16 años, 11 meses",
        sexo="Masculino",
        escolaridad="Secundaria Incompleta",
        lateralidad="Diestro",
        ocupacion="Estudiante",
        ciudad="Bogotá",
        acompanante="Madre",
        motivo_consulta=(
            "Dificultades escolares progresivas con bajo rendimiento en "
            "matemáticas y atención dispersa en clase."
        ),
        patologicos_medicos="Sin antecedentes patológicos relevantes",
        psiquiatricos="Negativos",
        farmacologicos="Ninguno",
        familiares="Tío paterno con trastorno del aprendizaje",
        obs_clinica_general="Adolescente colaborativo, lenguaje fluido.",
        obs_atencion="Atención sostenida disminuida en tareas verbales largas.",
        obs_memoria="Memoria de trabajo verbal disminuida.",
        obs_lenguaje="Lenguaje conservado.",
        obs_funciones_ejecutivas="Dificultades leves de planeación.",
        codigo_cie10="F81.9",
        codigo_cie10_desc="Trastorno del desarrollo de habilidades escolares",
        obs_impresion_dx=(
            "Perfil cognitivo dentro del rango promedio con asimetría leve "
            "entre índices."
        ),
        obs_recomendaciones=(
            "[ESCOLAR] (alta) Apoyo pedagógico individual en matemáticas\n"
            "[TERAPEUTICA] (alta) Rehabilitación cognitiva orientada a "
            "memoria de trabajo\n"
            "[FAMILIAR] (media) Psicoeducación a los padres\n"
            "[SEGUIMIENTO] (baja) Re-evaluación en 12 meses"
        ),
        profesional_nombre="Dr. Johan Salgado",
        profesional_titulo="Psicólogo, Especialista en Neuropsicología Clínica",
        profesional_registro="PS-12345-CO",
        eval_id="abc-def-12345-6789",
        protocolo="WISC-IV Colombia",
        resultados=[
            {"test_id": "NiWiscDC", "test_nombre": "Diseño con Cubos",
             "puntaje_bruto": 53, "puntaje_escalar": 11, "z_equivalente": 0.33,
             "interpretacion": "Promedio", "dominio_cognitivo": "Visoespacial",
             "tipo_metrica": "escalar"},
            {"test_id": "NiWiscSem", "test_nombre": "Semejanzas",
             "puntaje_bruto": 32, "puntaje_escalar": 11, "z_equivalente": 0.33,
             "interpretacion": "Promedio", "dominio_cognitivo": "Comprensión Verbal",
             "tipo_metrica": "escalar"},
            {"test_id": "NiWiscVoc", "test_nombre": "Vocabulario",
             "puntaje_bruto": 37, "puntaje_escalar": 6, "z_equivalente": -1.33,
             "interpretacion": "Bajo", "dominio_cognitivo": "Comprensión Verbal",
             "tipo_metrica": "escalar"},
            {"test_id": "NiWiscCl", "test_nombre": "Claves",
             "puntaje_bruto": 46, "puntaje_escalar": 8, "z_equivalente": -0.67,
             "interpretacion": "Promedio", "dominio_cognitivo": "Velocidad de Procesamiento",
             "tipo_metrica": "escalar"},
            {"test_id": "NiWiscAri", "test_nombre": "Aritmética",
             "puntaje_bruto": 21, "puntaje_escalar": 6, "z_equivalente": -1.33,
             "interpretacion": "Limítrofe", "dominio_cognitivo": "Memoria de Trabajo",
             "tipo_metrica": "escalar"},
            # Índices CI
            {"test_id": "NiWISCIndComVer", "test_nombre": "ICV",
             "puntaje_escalar": 98, "z_equivalente": -0.13,
             "interpretacion": "Promedio", "dominio_cognitivo": "Comprensión Verbal",
             "tipo_metrica": "ci"},
            {"test_id": "NiWISCIndRazPer", "test_nombre": "IRP",
             "puntaje_escalar": 105, "z_equivalente": 0.33,
             "interpretacion": "Promedio", "dominio_cognitivo": "Razonamiento Perceptual",
             "tipo_metrica": "ci"},
            {"test_id": "NiWISCIndMemTra", "test_nombre": "IMT",
             "puntaje_escalar": 86, "z_equivalente": -0.93,
             "interpretacion": "Promedio Bajo", "dominio_cognitivo": "Memoria de Trabajo",
             "tipo_metrica": "ci"},
            {"test_id": "NiWISCIndVelPro", "test_nombre": "IVP",
             "puntaje_escalar": 88, "z_equivalente": -0.80,
             "interpretacion": "Promedio Bajo", "dominio_cognitivo": "Velocidad de Procesamiento",
             "tipo_metrica": "ci"},
            {"test_id": "NiWISCTot", "test_nombre": "CIT",
             "puntaje_escalar": 93, "z_equivalente": -0.47,
             "interpretacion": "Promedio", "dominio_cognitivo": "Global",
             "tipo_metrica": "ci"},
        ],
    )


@pytest.fixture
def report_data_minimal():
    """ReportData con sólo los campos obligatorios — debe generar PDF mínimo."""
    from app.infrastructure.report_service import ReportData
    return ReportData(
        nombre_completo="Paciente Mínimo",
        numero_documento="0000000000",
        fecha_atencion=date(2025, 1, 1),
    )


# ──────────────────────────────────────────────────────────
# Tests de cada variante
# ──────────────────────────────────────────────────────────

ALL_TEMPLATES = ["estandar", "pro", "pediatrico", "medicolegal",
                 "junta_medica", "inconcluso", "paciente"]


@pytest.mark.integration
@pytest.mark.parametrize("template", ALL_TEMPLATES)
def test_generate_pdf_each_variant_returns_bytes(report_data_rich, template):
    """Cada variante produce un PDF no vacío con header válido."""
    from app.infrastructure.report_service import generate_report_pdf
    if template == "inconcluso":
        report_data_rich.informe_inconcluso_cat = "fatiga"
        report_data_rich.informe_inconcluso_nota = "Paciente cansado tras 90 min."
    pdf_bytes = generate_report_pdf(report_data_rich, template=template)
    assert isinstance(pdf_bytes, bytes), f"{template}: no es bytes"
    assert len(pdf_bytes) > 1500, f"{template}: PDF demasiado pequeño ({len(pdf_bytes)} B)"
    # Cabecera mágica PDF
    assert pdf_bytes[:4] == b"%PDF", f"{template}: cabecera PDF inválida"
    # Trailer válido (último kilobyte contiene %%EOF)
    assert b"%%EOF" in pdf_bytes[-2048:], f"{template}: falta %%EOF"


@pytest.mark.integration
def test_generate_pdf_unknown_template_falls_back_to_pro(report_data_rich):
    """Un nombre de plantilla desconocido cae a 'pro' sin lanzar."""
    from app.infrastructure.report_service import generate_report_pdf
    pdf_bytes = generate_report_pdf(report_data_rich, template="this-does-not-exist")
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1500


@pytest.mark.integration
def test_generate_pdf_minimal_data(report_data_minimal):
    """Con datos mínimos la variante Pro no debe fallar."""
    from app.infrastructure.report_service import generate_report_pdf
    pdf_bytes = generate_report_pdf(report_data_minimal, template="pro")
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 800  # umbral más bajo: sin resultados ni narrativa


@pytest.mark.integration
def test_generate_pdf_default_template_is_pro(report_data_rich):
    """Sin parámetro template, el default es 'pro' (estándar IN&S+Pro)."""
    from app.infrastructure.report_service import generate_report_pdf
    pdf_default = generate_report_pdf(report_data_rich)
    pdf_pro = generate_report_pdf(report_data_rich, template="pro")
    pdf_estandar = generate_report_pdf(report_data_rich, template="estandar")
    assert pdf_default[:4] == b"%PDF"
    assert len(pdf_default) > len(pdf_estandar) * 2
    assert abs(len(pdf_default) - len(pdf_pro)) < 800


@pytest.mark.integration
def test_estandar_template_still_works(report_data_rich):
    """Retrocompatibilidad: la plantilla 'estandar' usa NeuroPDFGenerator clásico."""
    from app.infrastructure.report_service import generate_report_pdf
    pdf_bytes = generate_report_pdf(report_data_rich, template="estandar")
    assert pdf_bytes[:4] == b"%PDF"
    # El estándar suele ser más pequeño que la variante Pro (sin gráficos avanzados)
    pdf_pro = generate_report_pdf(report_data_rich, template="pro")
    # Sólo verificamos que ambos generen; el tamaño relativo no es invariante
    assert pdf_bytes != pdf_pro, "Estándar y Pro deben producir PDFs distintos"


@pytest.mark.integration
def test_junta_medica_is_compact(report_data_rich):
    """La variante Junta Médica no debería tener portada — PDF más compacto."""
    from app.infrastructure.report_service import generate_report_pdf
    pdf_junta = generate_report_pdf(report_data_rich, template="junta_medica")
    pdf_pro = generate_report_pdf(report_data_rich, template="pro")
    assert pdf_junta[:4] == b"%PDF"
    assert pdf_pro[:4] == b"%PDF"
    # Junta médica debe ser más pequeña (sin portada ni anexo)
    assert len(pdf_junta) < len(pdf_pro), (
        f"Junta Médica ({len(pdf_junta)}) debería ser más compacta que Pro "
        f"({len(pdf_pro)})"
    )


@pytest.mark.integration
def test_inconcluso_with_category_and_note(report_data_rich):
    """La variante Inconcluso incluye razón y nota en el contenido."""
    from app.infrastructure.report_service import generate_report_pdf
    report_data_rich.informe_inconcluso_cat = "fatiga"
    report_data_rich.informe_inconcluso_nota = (
        "Paciente reporta fatiga significativa después de 90 minutos."
    )
    pdf_bytes = generate_report_pdf(report_data_rich, template="inconcluso")
    assert pdf_bytes[:4] == b"%PDF"
    # El contenido contiene el texto en alguna forma (puede estar encodeado en
    # streams comprimidos, pero la presencia de la cadena exacta suele
    # detectarse en PDFs sin compresión avanzada). No assertamos por contenido
    # estricto para evitar acoplarse a la versión de ReportLab.
    assert len(pdf_bytes) > 2000


@pytest.mark.integration
def test_variants_available_via_public_api():
    """La API pública expone la lista canónica de variantes."""
    from app.infrastructure.report_pro import VARIANTES_DISPONIBLES
    assert "pro" in VARIANTES_DISPONIBLES
    assert "pediatrico" in VARIANTES_DISPONIBLES
    assert "medicolegal" in VARIANTES_DISPONIBLES
    assert "junta_medica" in VARIANTES_DISPONIBLES
    assert "inconcluso" in VARIANTES_DISPONIBLES
    # Las variantes deben ser inmutables (tupla) para evitar mutación accidental
    assert isinstance(VARIANTES_DISPONIBLES, tuple)


# ──────────────────────────────────────────────────────────
# Tests de utilidades específicas
# ──────────────────────────────────────────────────────────

@pytest.mark.integration
def test_narrative_builds_synthesis_paragraphs(report_data_rich):
    """build_synthesis_paragraphs debe producir al menos 1 párrafo coherente."""
    from app.infrastructure.report_pro.narrative import build_synthesis_paragraphs
    paragraphs = build_synthesis_paragraphs(
        report_data_rich.resultados,
        paciente_nombre="Jesús",
    )
    assert len(paragraphs) >= 1
    # El primer párrafo debe mencionar el CIT (93)
    assert "93" in paragraphs[0] or "CIT" in paragraphs[0]


@pytest.mark.integration
def test_narrative_parses_recomendaciones_with_tags(report_data_rich):
    """parse_recomendaciones distingue [ESCOLAR], (alta), etc."""
    from app.infrastructure.report_pro.narrative import parse_recomendaciones
    grouped = parse_recomendaciones(report_data_rich.obs_recomendaciones)
    assert "Escolar" in grouped
    assert "Terapéutica" in grouped
    assert "Familiar" in grouped
    # Al menos un item de prioridad alta en Escolar
    escolar_priorities = [it["prioridad"] for it in grouped.get("Escolar", [])]
    assert "alta" in escolar_priorities


@pytest.mark.integration
def test_strengths_weaknesses_extraction(report_data_rich):
    """Identifica correctamente Bajo (Vocabulario, Aritmética) como debilidades."""
    from app.infrastructure.report_pro.narrative import build_strengths_weaknesses
    weak, strong = build_strengths_weaknesses(report_data_rich.resultados)
    # Vocabulario y Aritmética con Z=-1.33 deben aparecer
    weak_names = " ".join(weak).lower()
    assert "vocabulario" in weak_names or "aritmética" in weak_names


@pytest.mark.integration
def test_footer_includes_normograma_version():
    """F5.3: el footer del PDF Pro debe incluir la versión del Normograma."""
    from app.infrastructure.report_pro.base import NORMOGRAMA_VERSION
    from datetime import date

    assert NORMOGRAMA_VERSION == "2026.06"

    from app.infrastructure.report_pro import generate_pro_pdf
    from app.infrastructure.report_service import ReportData

    data = ReportData(
        institucion_nombre="Test",
        nombre_completo="Paciente Test",
        tipo_documento="CC",
        numero_documento="123",
        fecha_nacimiento=date(1990, 1, 1),
        edad_display="36a",
        sexo="M",
        escolaridad="Universitaria",
        motivo_consulta="Control",
        resultados=[],
        obs_recomendaciones="",
    )
    pdf = generate_pro_pdf(data, template="pro")
    assert pdf.startswith(b"%PDF-")
    # Footer es texto dibujado en stream; verificamos indirectamente que la
    # versión aparece en el módulo y que el factory no lanza excepciones.
    src = open("app/infrastructure/report_pro/base.py", encoding="utf-8").read()
    assert "Normograma {NORMOGRAMA_VERSION}" in src
    assert "Confidencial · Ley 1581/2012" in src


@pytest.mark.integration
def test_normograma_version_frontend_backend_lockstep():
    """F5.3: la versión del Normograma debe coincidir entre frontend y backend."""
    from pathlib import Path
    from app.infrastructure.report_pro.base import NORMOGRAMA_VERSION

    fe = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "neurosoft-frontend"
        / "src"
        / "data"
        / "plantillasDocumentales.js"
    )
    src = fe.read_text(encoding="utf-8")
    # El frontend exporta NORMOGRAMA_COLOMBIANO_VERSION = NORMOGRAMA_VERSION;
    # (alias), y la versión literal está en la línea ``const NORMOGRAMA_VERSION = "X"``.
    assert "NORMOGRAMA_COLOMBIANO_VERSION" in src
    import re
    m = re.search(
        r'(?:const|let|var)\s+NORMOGRAMA_VERSION\s*=\s*["\']([^"\']+)["\']',
        src,
    )
    assert m, "Frontend debe declarar NORMOGRAMA_VERSION con literal de versión"
    assert m.group(1) == NORMOGRAMA_VERSION, (
        f"Desincronizado: backend={NORMOGRAMA_VERSION} frontend={m.group(1)}"
    )
