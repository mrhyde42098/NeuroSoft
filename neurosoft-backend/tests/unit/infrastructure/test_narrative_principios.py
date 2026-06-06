"""
S2.5: Tests para los 7 principios narrativos y cláusulas legales colombianas.

Los principios narrativos son una guía editorial para la redacción de
informes clínicos. No son auto-aplicables, pero su API debe ser estable.
"""

from app.infrastructure.report_pro.narrative import (
    CLAUSULAS_LEGALES,
    PRINCIPIOS_NARRATIVOS,
    aplicar_principios_en_narrativa,
    clausula_legal,
)


def test_principios_narrativos_siete():
    assert len(PRINCIPIOS_NARRATIVOS) == 7


def test_principios_tienen_estructura_completa():
    for p in PRINCIPIOS_NARRATIVOS:
        assert "id" in p
        assert "titulo" in p
        assert "descripcion" in p
        assert "ejemplo" in p
        assert p["id"].startswith("P")
        assert p["titulo"]


def test_principios_ids_unicos():
    ids = [p["id"] for p in PRINCIPIOS_NARRATIVOS]
    assert len(ids) == len(set(ids))


def test_clausulas_legales_existen():
    assert "ley_1090_2006" in CLAUSULAS_LEGALES
    assert "res_1995_1999" in CLAUSULAS_LEGALES
    assert "habeas_data" in CLAUSULAS_LEGALES
    assert "ia_clausula" in CLAUSULAS_LEGALES
    assert "responsabilidad" in CLAUSULAS_LEGALES


def test_clausula_ley_1090_deontologico():
    txt = clausula_legal("ley_1090_2006")
    assert "Ley 1090" in txt
    assert "responsabilidad profesional" in txt.lower() or "deontol" in txt.lower()


def test_clausula_res_1995_hc():
    txt = clausula_legal("res_1995_1999")
    assert "1995" in txt
    assert "historia cl" in txt.lower() or "confidencial" in txt.lower()


def test_clausula_habeas_data_1581():
    txt = clausula_legal("habeas_data")
    assert "1581" in txt


def test_clausula_ia_mencion_responsabilidad_profesional():
    txt = clausula_legal("ia_clausula")
    assert "1090" in txt
    assert "profesional" in txt.lower()


def test_clausula_responsabilidad_no_sustituye():
    txt = clausula_legal("responsabilidad")
    assert "NO sustituye" in txt or "no sustituye" in txt.lower()


def test_clausula_inexistente_devuelve_vacio():
    assert clausula_legal("nope") == ""


def test_aplicar_principios_no_altera_texto():
    original = "El paciente tiene TDAH de predominio inatento."
    out = aplicar_principios_en_narrativa(original)
    assert out == original


def test_aplicar_principios_acepta_vacio():
    assert aplicar_principios_en_narrativa("") == ""
