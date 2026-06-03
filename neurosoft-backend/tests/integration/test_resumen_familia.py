"""
Sprint D — Verificación de la sección "Resumen para la Familia" en PDF.
Previene regresión: la sección plain-language debe estar presente en
las variantes pro, pediatric y medicolegal, y ausente en junta_medica.
"""
import io
import pytest
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
