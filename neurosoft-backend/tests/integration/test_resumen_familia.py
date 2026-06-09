"""
Sprint D — Verificación de la sección "Resumen para la Familia" en PDF.
Previene regresión: la sección plain-language debe estar presente en
las variantes pro, pediatric y medicolegal, y ausente en junta_medica.
"""

import io
from datetime import date

from app.infrastructure.report_pro import generate_pro_pdf
from app.infrastructure.report_service import ReportData


def _build_data(**overrides):
    base = dict(
        institucion_nombre="Test",
        nombre_completo="Paciente Sprint D",
        tipo_documento="CC",
        numero_documento="123",
        fecha_nacimiento=date(1990, 1, 1),
        edad_display="36a",
        sexo="M",
        escolaridad="Universitaria",
        motivo_consulta="Control",
        resultados=[
            {
                "test_id": "AdWAISV",
                "nombre": "Vocabulario WAIS",
                "puntaje_bruto": 35,
                "puntaje_escalar": 11,
                "clasificacion": "Promedio",
                "tipo_metrica": "escalar",
                "dominio_cognitivo": "Lenguaje",
            },
            {
                "test_id": "AdWAISC",
                "nombre": "Cubos WAIS",
                "puntaje_bruto": 40,
                "puntaje_escalar": 9,
                "clasificacion": "Promedio",
                "tipo_metrica": "escalar",
                "dominio_cognitivo": "Visoconstruccion",
            },
        ],
        obs_recomendaciones="[ESCOLAR] Coordinar con colegio\n[TERAPÉUTICA] Terapia cognitivo-conductual",
    )
    base.update(overrides)
    return ReportData(**base)


def _extract_text(pdf_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader
    r = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(p.extract_text() for p in r.pages)


class TestResumenFamilia:
    """Sprint D — Sección plain-language para padres/cuidadores."""

    def test_variante_pro_incluye_resumen_familia(self):
        data = _build_data()
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        assert "RESUMEN PARA LA FAMILIA" in text.upper() or "FAMILIA" in text.upper()
        assert "SALUDO" in text.upper() or "SALUDO" in text

    def test_variante_pediatric_incluye_resumen_familia(self):
        data = _build_data(edad_display="10a", escolaridad="Primaria")
        pdf = generate_pro_pdf(data, template="pediatrico")
        text = _extract_text(pdf)
        assert "FAMILIA" in text.upper()

    def test_variante_medicolegal_incluye_resumen_familia(self):
        data = _build_data()
        pdf = generate_pro_pdf(data, template="medicolegal")
        text = _extract_text(pdf)
        assert "FAMILIA" in text.upper()

    def test_variante_junta_medica_NO_incluye_resumen_familia(self):
        """Junta Médica es ejecutiva, sin sección de familia."""
        data = _build_data()
        pdf = generate_pro_pdf(data, template="junta_medica")
        text = _extract_text(pdf)
        # Junta médica es 1-2 páginas y NO incluye la sección familiar
        assert "RESUMEN PARA LA FAMILIA" not in text.upper()

    def test_resumen_incluye_fortalezas(self):
        data = _build_data()
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        assert "FORTALEZAS" in text.upper()

    def test_resumen_incluye_preguntas_frecuentes(self):
        data = _build_data()
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        assert "PREGUNTAS" in text.upper()

    def test_pdf_no_falla_sin_resultados(self):
        """Si no hay resultados, el PDF debe generarse sin errores."""
        data = _build_data(resultados=[])
        pdf = generate_pro_pdf(data, template="pro")
        assert pdf.startswith(b"%PDF-")

    def test_pdf_no_falla_sin_recomendaciones(self):
        """Si no hay recomendaciones, debe omitir bloque sin error."""
        data = _build_data(obs_recomendaciones="")
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        assert pdf.startswith(b"%PDF-")
        # La sección sigue presente pero sin recomendaciones
        assert "FAMILIA" in text.upper()

    def test_pro_resumen_familia_antes_de_resultados_cuantitativos(self):
        """Resumen familiar debe preceder a la tabla técnica de puntajes."""
        data = _build_data()
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        idx_familia = text.upper().find("RESUMEN PARA LA FAMILIA")
        idx_resultados = text.upper().find("RESULTADOS")
        assert idx_familia >= 0 and idx_resultados >= 0
        assert idx_familia < idx_resultados

    def test_pro_incluye_sintesis_integradora(self):
        data = _build_data(
            resultados=[
                {
                    "test_id": "AdWAISCIT",
                    "test_nombre": "CIT",
                    "puntaje_escalar": 87,
                    "z_equivalente": -0.87,
                    "interpretacion": "Promedio Bajo",
                    "clasificacion": "Promedio Bajo",
                    "tipo_metrica": "ci",
                    "dominio_cognitivo": "Inteligencia",
                },
                {
                    "test_id": "AdWAISV",
                    "test_nombre": "Vocabulario",
                    "puntaje_escalar": 11,
                    "z_equivalente": 0.0,
                    "interpretacion": "Promedio",
                    "clasificacion": "Promedio",
                    "tipo_metrica": "escalar",
                    "dominio_cognitivo": "Lenguaje",
                },
            ]
        )
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        assert "SÍNTESIS" in text.upper() or "SINTESIS" in text.upper()

    def test_pro_tabla_incluye_que_significa(self):
        data = _build_data()
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        assert "QUÉ SIGNIFICA" in text.upper() or "QUE SIGNIFICA" in text.upper()

    def test_pediatrico_voz_cuidador(self):
        data = _build_data(edad_display="10a", escolaridad="Primaria")
        pdf = generate_pro_pdf(data, template="pediatrico")
        text = _extract_text(pdf)
        assert "SU HIJO" in text.upper() or "CUIDADOR" in text.upper()

    def test_recomendaciones_familia_numeradas(self):
        data = _build_data(obs_recomendaciones="[ESCOLAR] Solicitar acompañamiento pedagógico en matemáticas")
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        assert "1." in text
        assert "matemáticas" in text.lower() or "MATEM" in text.upper()

    def test_impresion_incluye_puente_lenguaje_claro(self):
        data = _build_data(
            codigo_cie10="F90.0",
            codigo_cie10_desc="Trastorno de déficit de atención con hiperactividad",
        )
        pdf = generate_pro_pdf(data, template="pro")
        text = _extract_text(pdf)
        assert "PALABRAS SENCILLAS" in text.upper() or "En palabras sencillas" in text
