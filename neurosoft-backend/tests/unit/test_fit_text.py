"""Tests para el helper fit_text_to_width (truncado con elipsis)."""

from app.infrastructure.report_pro.helpers import _truncate_to_width, fit_text_to_width


def test_texto_corto_no_trunca():
    s = "Hola"
    out = fit_text_to_width(s, max_width=100, font_name="Helvetica", size=10)
    assert out == "Hola"


def test_texto_largo_truncado_con_elipsis():
    s = "Escala de Depresión Geriátrica de Yesavage (GDS-15)"
    out = fit_text_to_width(s, max_width=50, font_name="Helvetica", size=10)
    assert len(out) < len(s)
    assert out.endswith("\u2026") or out.endswith("…")


def test_texto_exacto_no_trunca():
    s = "X" * 10
    out = fit_text_to_width(s, max_width=200, font_name="Helvetica", size=10)
    assert out == s


def test_max_width_menor_que_elipsis():
    s = "abcdef"
    out = fit_text_to_width(s, max_width=2, font_name="Helvetica", size=10)
    assert out == ""


def test_texto_vacio_devuelve_vacio():
    assert fit_text_to_width("", max_width=100, font_name="Helvetica", size=10) == ""


def test_glifo_a_glifo():
    """Si el texto se acorta, el resultado debe ser prefijo del original."""
    s = "ABCDEFGHIJ"
    out = fit_text_to_width(s, max_width=40, font_name="Helvetica", size=10)
    assert s.startswith(out.rstrip("\u2026").rstrip("…"))


def test_truncate_to_width_legacy():
    """El helper legacy también trunca con elipsis."""
    s = "Nombre de prueba muy largo para una celda"
    out = _truncate_to_width(s, font_name="Helvetica", size=10, max_width=40)
    assert len(out) < len(s)
    assert out.endswith("\u2026") or out.endswith("…")
