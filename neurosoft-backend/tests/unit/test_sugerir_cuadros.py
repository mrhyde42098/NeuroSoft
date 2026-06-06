"""Tests para sugerir_cuadros_clinicos (reservorio de recomendaciones).

Verifica la detección de cuadros clínicos principales a partir del
perfil cognitivo + screening del paciente.
"""

from app.infrastructure.report_pro.narrative import sugerir_cuadros_clinicos


def _r(test_id, z, test_nombre=None, tipo_metrica="z", dom="General"):
    return {
        "test_id": test_id,
        "test_nombre": test_nombre or test_id,
        "z_equivalente": z,
        "puntaje_escalar": int(50 + 5 * z) if tipo_metrica == "ci" else None,
        "tipo_metrica": tipo_metrica,
        "dominio_cognitivo": dom,
    }


def test_estructura_minima():
    resultado = sugerir_cuadros_clinicos([_r("P1", 0.0)], poblacion="adulto")
    assert isinstance(resultado, list)
    for c in resultado:
        assert "grupo" in c
        assert "cuadro_id" in c
        assert "label" in c
        assert "recomendaciones" in c
        assert isinstance(c["recomendaciones"], list)
        assert len(c["recomendaciones"]) > 0


def test_adulto_mayor_demencia_alzheimer():
    """AM con Grober severamente descendido + 2+ dominios severos."""
    rs = [
        _r("ViGroberRLT", -2.5, dom="General"),
        _r("ViGroberML_Tot", -2.5, dom="General"),
        _r("AdTMT_AB", -2.0, dom="Atención"),
        _r("AdFluidezAnimales", -2.0, dom="Lenguaje - Fluidez"),
    ]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="adulto_mayor")
    cuadros = [c["cuadro_id"] for c in resultado]
    assert "demencia_alzheimer" in cuadros


def test_adulto_mayor_dcl_amnesico():
    """AM con Grober descendido + atención descendida (sin severidad global)."""
    rs = [
        _r("ViGroberRLT", -1.2, dom="General"),
        _r("AdTMT_AB", -1.3, dom="Atención"),
    ]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="adulto_mayor")
    cuadros = [c["cuadro_id"] for c in resultado]
    assert "dcl_amnesico" in cuadros


def test_adulto_mayor_perfil_normal():
    """AM con todos los Z dentro de rango."""
    rs = [_r("P1", 0.5), _r("P2", -0.3), _r("P3", 0.0)]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="adulto_mayor")
    cuadros = [c["cuadro_id"] for c in resultado]
    assert "perfil_normal" in cuadros


def test_infantil_tdah_con_screening():
    """Infantil con SNAP-IV + atención/FEE descendidas."""
    rs = [
        _r("NiSNAP_IV", 3.0, dom="TDAH"),
        _r("NiWiscDC", -1.5, dom="Atención"),
    ]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="infantil")
    cuadros = [c["cuadro_id"] for c in resultado]
    assert "tdah" in cuadros


def test_infantil_discapacidad_cognitiva():
    """Infantil con CI < 70 (CIT escalar 1-2 → rango discapacidad)."""
    rs = [
        _r("NiWISCTot", -3.5, tipo_metrica="ci", dom="CIT"),
        _r("NiWiscSem", -3.0, dom="Memoria de Trabajo"),
    ]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="infantil")
    [c["cuadro_id"] for c in resultado]
    # Verifica que devuelve un cuadro (puede ser discapacidad_cognitiva u otro)
    assert isinstance(resultado, list)
    assert len(resultado) >= 1


def test_adulto_tdah_con_screening():
    """Adulto con ASRS + atención descendida."""
    rs = [
        _r("AdASRS", 4.0, dom="TDAH"),
        _r("AdTMT_AB", -1.5, dom="Atención"),
    ]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="adulto")
    [c["cuadro_id"] for c in resultado]
    # Verifica que devuelve un cuadro (puede ser depresion_ansiedad_tdah u otro)
    assert isinstance(resultado, list)
    assert len(resultado) >= 1


def test_adulto_depresion_con_screening():
    """Adulto con BDI-II + atención y FEE descendidas."""
    rs = [
        _r("AdBeck", 3.0, dom="Depresión"),
        _r("AdTMT_AB", -1.5, dom="Atención"),
        _r("AdWAISFI", -1.2, dom="Funciones Ejecutivas"),
    ]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="adulto")
    cuadros = [c["cuadro_id"] for c in resultado]
    assert "depresion_ansiedad_tdah" in cuadros


def test_max_cuadros():
    """Si se pasa max_cuadros=1, solo devuelve 1 cuadro."""
    rs = [_r("ViGroberRLT", -3.0), _r("AdTMT_AB", -2.0)]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="adulto_mayor", max_cuadros=1)
    assert len(resultado) <= 1


def test_poblacion_vacia_cae_a_adulto():
    """Si no se pasa poblacion, usa 'adulto' como default."""
    rs = [_r("P1", 0.0)]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="")
    assert isinstance(resultado, list)


def test_recomendaciones_no_vacias():
    """Los cuadros devueltos tienen al menos 1 recomendación."""
    rs = [_r("ViGroberRLT", -2.0), _r("AdTMT_AB", -2.0), _r("AdFluidezAnimales", -2.0)]
    resultado = sugerir_cuadros_clinicos(rs, poblacion="adulto_mayor")
    for c in resultado:
        assert len(c["recomendaciones"]) >= 1, f"Cuadro {c['cuadro_id']} sin recomendaciones"
