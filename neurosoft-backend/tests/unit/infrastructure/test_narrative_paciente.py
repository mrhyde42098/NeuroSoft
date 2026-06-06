"""
S3.2: Tests de los helpers para versión paciente del informe.
"""

from app.infrastructure.report_pro.narrative import (
    MAPEO_LENGUAJE_CLARO,
    banda_a_lenguaje_claro,
    generar_resumen_paciente,
    traducir_termino,
)


def test_mapeo_lenguaje_claro_tiene_terminos_clave():
    assert "CI Total" in MAPEO_LENGUAJE_CLARO
    assert "Memoria de Trabajo" in MAPEO_LENGUAJE_CLARO
    assert "TDAH" in MAPEO_LENGUAJE_CLARO
    assert "Superior" in MAPEO_LENGUAJE_CLARO
    assert "Bajo" in MAPEO_LENGUAJE_CLARO


def test_traducir_termino_exacto():
    assert "tu rendimiento intelectual general" in traducir_termino("CI Total")
    mt = traducir_termino("Memoria de Trabajo")
    assert ("memoria activa" in mt) or ("mantener información" in mt)


def test_traducir_termino_case_insensitive():
    """El input case-insensitive debe matchear al menos una clave del mapeo."""
    r = traducir_termino("memoria de TRABAJO")
    # Acepta cualquiera de las dos traducciones registradas
    assert ("memoria activa" in r) or ("mantener información" in r)


def test_traducir_termino_desconocido_devuelve_original():
    assert traducir_termino("FooBar123") == "FooBar123"
    assert traducir_termino("") == ""


def test_banda_a_lenguaje_claro():
    assert "muy por encima del promedio" in banda_a_lenguaje_claro("Superior")
    assert "dentro del rango esperado" in banda_a_lenguaje_claro("Promedio")
    assert "muy por debajo del promedio" in banda_a_lenguaje_claro("Muy Bajo")
    assert banda_a_lenguaje_claro("—") == "dentro del rango esperado"
    assert banda_a_lenguaje_claro("") == "dentro del rango esperado"


def test_generar_resumen_paciente_estructura():
    resumen = generar_resumen_paciente([], paciente_nombre="Juan Pérez")
    assert "saludo" in resumen
    assert "que_hicimos" in resumen
    assert "que_encontramos" in resumen
    assert "fortalezas" in resumen
    assert "areas_apoyo" in resumen
    assert "que_recomendamos" in resumen
    assert "preguntas_frecuentes" in resumen
    assert isinstance(resumen["preguntas_frecuentes"], list)
    assert len(resumen["preguntas_frecuentes"]) >= 2


def test_generar_resumen_paciente_saludo_personalizado():
    resumen = generar_resumen_paciente([], paciente_nombre="María López")
    assert "María" in resumen["saludo"]


def test_generar_resumen_paciente_detecta_fortalezas():
    resultados = [
        {"nombre": "Memoria de Trabajo", "clasificacion": "Promedio"},
        {"nombre": "Atención Sostenida", "clasificacion": "Superior"},
    ]
    resumen = generar_resumen_paciente(resultados, paciente_nombre="Juan")
    assert len(resumen["fortalezas"]) >= 1
    assert len(resumen["areas_apoyo"]) == 0


def test_generar_resumen_paciente_detecta_areas_apoyo():
    resultados = [
        {"nombre": "Atención Sostenida", "clasificacion": "Bajo"},
        {"nombre": "Memoria de Trabajo", "clasificacion": "Promedio"},
    ]
    resumen = generar_resumen_paciente(resultados, paciente_nombre="Ana")
    assert len(resumen["areas_apoyo"]) >= 1
    assert "concentrarte" in resumen["areas_apoyo"][0].lower() or "apoyo" in resumen["areas_apoyo"][0].lower()


def test_generar_resumen_paciente_sin_resultados_devuelve_texto_generico():
    resumen = generar_resumen_paciente([], paciente_nombre="Test")
    assert "psic" in resumen["que_encontramos"].lower()


def test_generar_resumen_paciente_recomendaciones_escolares():
    resumen = generar_resumen_paciente([], paciente_nombre="X", recomendaciones=["Reforzar lectura en colegio"])
    assert (
        "colegio" in resumen["que_recomendamos"].lower()
        or "escuela" in resumen["que_recomendamos"].lower()
        or "academia" in resumen["que_recomendamos"].lower()
    )


def test_generar_resumen_paciente_recomendaciones_terapeuticas():
    resumen = generar_resumen_paciente([], paciente_nombre="X", recomendaciones=["Iniciar terapia cognitiva"])
    assert "terapia" in resumen["que_recomendamos"].lower() or "sesiones" in resumen["que_recomendamos"].lower()


def test_generar_resumen_paciente_recomendaciones_genericas():
    resumen = generar_resumen_paciente([], paciente_nombre="X", recomendaciones=["Otra cosa rara xyz"])
    assert "Recomendación" in resumen["que_recomendamos"] or "psicólogo" in resumen["que_recomendamos"].lower()


def test_generar_resumen_paciente_faq_con_preguntas_y_respuestas():
    resumen = generar_resumen_paciente([], paciente_nombre="Test")
    for pregunta, respuesta in resumen["preguntas_frecuentes"]:
        assert pregunta
        assert respuesta
        assert pregunta.endswith("?")
