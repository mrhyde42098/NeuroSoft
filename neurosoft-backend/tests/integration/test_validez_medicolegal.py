"""
Integración — sección de validez dinámica en informe médico-legal (caso TCE).
"""

import io
from datetime import date

from app.infrastructure.report_pro import generate_pro_pdf
from app.infrastructure.report_service import ReportData


def _extract_text(pdf_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader
    r = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(p.extract_text() for p in r.pages)


def _tce_data(**overrides):
    base = dict(
        institucion_nombre="Test Pericial",
        nombre_completo="Carlos TCE Peritaje",
        tipo_documento="CC",
        numero_documento="998877",
        fecha_nacimiento=date(1985, 6, 15),
        edad_display="40a",
        sexo="M",
        escolaridad="Universitaria",
        motivo_consulta="Peritaje neuropsicológico post-TCE",
        resultados=[
            {
                "test_id": "REY15",
                "test_nombre": "Rey 15-Item",
                "puntaje_bruto": 6,
                "dominio_cognitivo": "Validez de síntomas",
            },
            {
                "test_id": "TOMM",
                "test_nombre": "TOMM Trial 2",
                "puntaje_bruto": 41,
                "metadata": {"trial": 2},
                "dominio_cognitivo": "Validez de síntomas",
            },
            {
                "test_id": "AdWAISV",
                "test_nombre": "Vocabulario",
                "puntaje_bruto": 30,
                "puntaje_escalar": 8,
                "z_equivalente": -1.2,
                "interpretacion": "Promedio Bajo",
                "clasificacion": "Promedio Bajo",
                "tipo_metrica": "escalar",
                "dominio_cognitivo": "Lenguaje",
            },
        ],
        obs_impresion_dx="Secuela neuropsicológica compatible con TCE leve.",
    )
    base.update(overrides)
    return ReportData(**base)


class TestValidezMedicolegalPDF:
    def test_medicolegal_reporta_rey_y_tomm_dinamicamente(self):
        pdf = generate_pro_pdf(_tce_data(), template="medicolegal")
        text = _extract_text(pdf)
        assert "Rey 15-Item: 6/15" in text
        assert "TOMM" in text and "41/50" in text
        assert "No se incluyeron pruebas formales de validez" not in text

    def test_medicolegal_alerta_reserva_si_falla_validez(self):
        pdf = generate_pro_pdf(_tce_data(), template="medicolegal")
        text = _extract_text(pdf)
        assert "interpretarse con reserva" in text.lower() or "RESERVA" in text.upper()

    def test_medicolegal_sin_validez_mantiene_advertencia(self):
        data = _tce_data(
            resultados=[
                {
                    "test_id": "AdWAISV",
                    "puntaje_bruto": 30,
                    "puntaje_escalar": 10,
                    "interpretacion": "Promedio",
                    "clasificacion": "Promedio",
                    "tipo_metrica": "escalar",
                }
            ]
        )
        pdf = generate_pro_pdf(data, template="medicolegal")
        text = _extract_text(pdf)
        assert "No se incluyeron pruebas formales de validez" in text
