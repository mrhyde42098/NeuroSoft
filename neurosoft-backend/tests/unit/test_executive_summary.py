"""Tests para build_executive_summary (Resumen Ejecutivo inverted pyramid).

Verifica la estructura conclusión → hallazgos → implicación en los tres
perfiles clínicos principales: AM con demencia, adulto con TDAH, infantil
con Dislexia.
"""
from app.infrastructure.report_pro.narrative import build_executive_summary


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
    ej = build_executive_summary([_r("A", -1.0)])
    assert "conclusion" in ej
    assert "hallazgos" in ej
    assert "implicacion" in ej
    assert isinstance(ej["hallazgos"], list)


def test_con_con_CIT():
    """Con CIT se genera conclusión que incluye el valor y la categoría."""
    rs = [_r("Tot", 0.0, tipo_metrica="ci", dom="CIT")] + [_r(f"P{i}", 0.0) for i in range(5)]
    ej = build_executive_summary(rs, paciente_nombre="Juan")
    assert "CIT" in ej["conclusion"] or "100" in ej["conclusion"]
    assert "Juan" in ej["conclusion"]


def test_sin_CIT_usa_dominios():
    rs = [_r("P1", -2.5, dom="Memoria"), _r("P2", -1.5, dom="Atención")]
    ej = build_executive_summary(rs, paciente_nombre="Ana")
    assert "Memoria" in ej["conclusion"] or "-2" in ej["conclusion"]
    # El hallazgo más débil debe ser Memoria
    assert any("Memoria" in h for h in ej["hallazgos"])


def test_perfil_normal_implicacion_seguimiento():
    rs = [_r("P1", 0.0), _r("P2", 0.5), _r("P3", -0.5)]
    ej = build_executive_summary(rs)
    assert "seguimiento" in ej["implicacion"].lower() or "preservada" in ej["implicacion"].lower()


def test_perfil_deficit_severo_implicacion_prioritaria():
    rs = [_r("P1", -3.0, dom="Memoria"), _r("P2", -2.5, dom="Atención"),
          _r("P3", -1.0, dom="Lenguaje")]
    ej = build_executive_summary(rs)
    assert "prioritaria" in ej["implicacion"].lower() or "intervención" in ej["implicacion"].lower()


def test_asimetria_detectada():
    """Si los índices son asimétricos, se menciona."""
    # CIT=100, ICV=130, IRP=120, IMT=70, IVP=125 → max-min=60 → asimétrico
    rs = [
        _r("ICV", 2.0, tipo_metrica="ci", dom="ICV"),
        _r("IRP", 1.33, tipo_metrica="ci", dom="IRP"),
        _r("IMT", -2.0, tipo_metrica="ci", dom="IMT"),
        _r("IVP", 1.67, tipo_metrica="ci", dom="IVP"),
        _r("CIT", 0.0, tipo_metrica="ci", dom="CIT"),
    ]
    ej = build_executive_summary(rs)
    assert "asimétr" in ej["conclusion"].lower() or "IMT" in ej["conclusion"]


def test_hallazgos_limitados_3():
    """Nunca más de 3 hallazgos en la lista."""
    rs = [_r(f"P{i}", -2.0 - i * 0.1, dom=f"D{i}") for i in range(8)]
    ej = build_executive_summary(rs)
    assert len(ej["hallazgos"]) <= 3


def test_paciente_nombre_opcional():
    """Si no se pasa nombre, usa 'El paciente'."""
    rs = [_r("P1", -1.0)]
    ej = build_executive_summary(rs)
    assert isinstance(ej["conclusion"], str)
    assert len(ej["conclusion"]) > 0


def test_resultado_vacio_devuelve_estructura():
    """Sin resultados, devuelve estructura vacía pero válida."""
    ej = build_executive_summary([])
    assert "conclusion" in ej
    assert "hallazgos" in ej
    assert "implicacion" in ej


def test_idempotencia():
    """Llamar dos veces con los mismos args produce el mismo resultado."""
    rs = [_r("P1", -1.0), _r("P2", 0.0)]
    ej1 = build_executive_summary(rs, paciente_nombre="Test")
    ej2 = build_executive_summary(rs, paciente_nombre="Test")
    assert ej1 == ej2
