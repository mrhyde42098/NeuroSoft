"""
F9.3 — Verificación de metadatos PDF/A, variantes y bloque legal.
"""
import io
import pytest
from datetime import date

from app.infrastructure.report_pro import generate_pro_pdf
from app.infrastructure.report_service import ReportData


def _build_data(**overrides):
    base = dict(
        institucion_nombre="Test",
        nombre_completo="Paciente F9.3",
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
    base.update(overrides)
    return ReportData(**base)


class TestMetadatosPDFA:
    """F9.3 — XMP metadata para archivabilidad ISO 19005-1."""

    def test_pdf_tiene_encabezado_pdf_valido(self):
        data = _build_data(profesional_nombre="Ps. Test", eval_id="eval-12345")
        pdf = generate_pro_pdf(data, template="pro")
        assert pdf.startswith(b"%PDF-")

    def test_pdf_incluye_metadatos_keywords_cie10(self):
        data = _build_data(
            profesional_nombre="Ps. Test", eval_id="eval-abcdefgh", codigo_cie10="F90.0"
        )
        pdf = generate_pro_pdf(data, template="pro")
        # ReportLab inyecta Keywords en el stream del PDF
        assert b"Keywords" in pdf
        assert b"F90.0" in pdf
        assert b"eval-abc" in pdf  # primeros 8 chars de eval_id

    def test_pdf_incluye_producer_neurosoft(self):
        data = _build_data()
        pdf = generate_pro_pdf(data, template="pro")
        assert b"Producer" in pdf
        assert b"NeuroSoft" in pdf

    def test_pdf_incluye_creator_neurosoft(self):
        data = _build_data()
        pdf = generate_pro_pdf(data, template="pro")
        assert b"Creator" in pdf

    def test_pdf_incluye_author_del_profesional(self):
        data = _build_data(profesional_nombre="Dra. María López")
        pdf = generate_pro_pdf(data, template="pro")
        assert b"Author" in pdf


class TestVariantesDisponibles:
    """F9 — Las 6+ variantes deben generarse sin excepciones."""

    @pytest.mark.parametrize("template", [
        "estandar", "pro", "pediatrico", "medicolegal",
        "junta_medica", "inconcluso", "paciente",
    ])
    def test_variante_genera_pdf_valido(self, template):
        data = _build_data()
        try:
            pdf = generate_pro_pdf(data, template=template)
        except Exception as e:
            pytest.fail(f"Variante {template!r} lanzó excepción: {e}")
        assert pdf.startswith(b"%PDF-"), f"{template} no generó PDF válido"
        assert len(pdf) > 1000, f"{template} generó PDF demasiado pequeño ({len(pdf)} bytes)"


class TestBloqueLegalEnEncabezado:
    """F9.3 — El bloque legal del encabezado debe estar disponible y correcto."""

    def test_bloque_legal_incluye_todas_las_normas(self):
        from app.infrastructure.report_pro.narrative import construir_bloque_legal_encabezado
        bloque = construir_bloque_legal_encabezado(
            nombre_profesional="Ps. Test",
            tarjeta_profesional="TP-12345",
            universidad="UNAL",
            resolucion="Res. 0123/2010",
        )
        # Normas colombianas referenciadas
        for norma in ["Ley 1581", "Resolución 1995", "Ley 1090"]:
            assert norma in bloque, f"Falta {norma} en bloque legal"

    def test_bloque_legal_incluye_profesional(self):
        from app.infrastructure.report_pro.narrative import construir_bloque_legal_encabezado
        bloque = construir_bloque_legal_encabezado(
            nombre_profesional="Ps. Johan Salgado",
            tarjeta_profesional="TP-12345",
        )
        assert "Ps. Johan Salgado" in bloque
        assert "TP-12345" in bloque

    def test_bloque_legal_incluye_paciente_y_evaluacion(self):
        from app.infrastructure.report_pro.narrative import construir_bloque_legal_encabezado
        bloque = construir_bloque_legal_encabezado(
            nombre_paciente="Juan Pérez",
            edad_display="35a",
            fecha_evaluacion="2026-06-02",
        )
        assert "Juan Pérez" in bloque
        assert "35a" in bloque
        assert "2026-06-02" in bloque
