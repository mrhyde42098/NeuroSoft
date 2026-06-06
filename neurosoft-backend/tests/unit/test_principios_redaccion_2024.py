"""
F9.2/F9.3 — Tests del validador de principios de redacción 2024
y del constructor del bloque legal del encabezado.
"""

from app.infrastructure.report_pro.narrative import (
    CLAUSULAS_INFORME_PROFESIONAL,
    PRINCIPIOS_REDACCION_2024,
    construir_bloque_legal_encabezado,
    validar_principios_redaccion_2024,
)


class TestValidarPrincipiosRedaccion2024:
    def test_siete_principios_definidos(self):
        assert len(PRINCIPIOS_REDACCION_2024) == 7
        ids = {p["id"] for p in PRINCIPIOS_REDACCION_2024}
        assert ids == {"R1", "R2", "R3", "R4", "R5", "R6", "R7"}

    def test_infantil_con_conserva_dispara_r2(self):
        texto = (
            "El paciente conserva un CI Total de 87. Se observa alteración "
            "en funciones atencionales documentada con la prueba WCST. "
            "Se aplicaron baremos de Neuronorma Colombia por edad."
        )
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="infantil")
        r2 = resultado["principios"]["R2"]
        assert r2["estado"] == "revisar"
        assert "conserva" in r2["detalle"].lower()

    def test_infantil_sin_conserva_r2_ok(self):
        texto = (
            "El paciente rinde acorde a lo esperado para su edad y escolaridad. "
            "Presenta dificultad en la capacidad atencional documentada con la "
            "prueba WCST. Se aplicaron baremos de Neuronorma Colombia."
        )
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="infantil")
        r2 = resultado["principios"]["R2"]
        assert r2["estado"] == "ok"

    def test_adulto_con_déficit_sin_DIS_dispara_r3(self):
        texto = (
            "El paciente presenta déficit atencional. Tiene alteración en la "
            "función ejecutiva. Se aplicaron baremos de WAIS-III por edad."
        )
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="adulto_joven")
        r3 = resultado["principios"]["R3"]
        assert r3["estado"] == "revisar"

    def test_adulto_con_DIS_en_mayoria_r3_ok(self):
        texto = (
            "El paciente presenta DIS-atencional, DIS-mnésica, alteración "
            "ejecutiva. La función DIS-ejecutiva se afectó significativamente. "
            "Se aplicaron baremos de WAIS-III por edad."
        )
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="adulto_joven")
        r3 = resultado["principios"]["R3"]
        assert r3["estado"] == "ok"

    def test_infantil_r3_no_aplica(self):
        texto = "El paciente tiene déficit atencional."
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="infantil")
        r3 = resultado["principios"]["R3"]
        assert r3["estado"] == "no_aplica"

    def test_menciona_prueba_sin_funcion_dispara_r5(self):
        texto = (
            "El paciente obtuvo 30 errores en WCST. El puntaje en TMT-B fue "
            "de 45 segundos. Se aplicaron baremos de WAIS-III."
        )
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="adulto_joven")
        r5 = resultado["principios"]["R5"]
        assert r5["estado"] == "revisar"
        assert "funci" in r5["detalle"].lower()

    def test_menciona_prueba_con_funcion_r5_ok(self):
        texto = (
            "El paciente presenta dificultades en la capacidad de "
            "flexibilidad cognitiva, documentadas con la prueba WCST. "
            "La función ejecutiva se afectó en el dominio de set-shifting."
        )
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="adulto_joven")
        r5 = resultado["principios"]["R5"]
        assert r5["estado"] == "ok"

    def test_sin_mencion_baremos_r6_revisar(self):
        texto = "El paciente presenta déficit atencional con Z=-1.5."
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="adulto_joven")
        r6 = resultado["principios"]["R6"]
        assert r6["estado"] == "revisar"

    def test_con_mencion_baremos_r6_ok(self):
        texto = (
            "Se aplicaron baremos de Neuronorma Colombia (Arango-Lasprilla & "
            "Rivera, 2017) para población adulta. El paciente presenta "
            "déficit atencional."
        )
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="adulto_joven")
        r6 = resultado["principios"]["R6"]
        assert r6["estado"] == "ok"

    def test_mentiona_baremos_explicito_override_inferencia(self):
        texto = "El paciente presenta déficit atencional."
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="adulto_joven", menciona_baremos=True)
        r6 = resultado["principios"]["R6"]
        assert r6["estado"] == "ok"

    def test_narrativa_completa_cumple_todos_los_principios(self):
        texto = (
            "El paciente rinde acorde a lo esperado para su edad y escolaridad. "
            "En el dominio de atención se observa DIS-atencional, con "
            "dificultades en la capacidad atencional sostenida documentadas "
            "con la prueba WCST. La función DIS-ejecutiva se afectó "
            "significativamente. Se aplicaron baremos de Neuronorma Colombia "
            "(Arango-Lasprilla & Rivera, 2017) por edad."
        )
        resultado = validar_principios_redaccion_2024(texto, poblacion_objetivo="adulto_mayor")
        assert resultado["cumple"] is True
        assert resultado["alertas"] == []
        for pid in ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
            assert pid in resultado["principios"]

    def test_principios_no_auditables_se_marcan_como_tales(self):
        resultado = validar_principios_redaccion_2024("Texto cualquiera.", poblacion_objetivo="adulto_joven")
        r1 = resultado["principios"]["R1"]
        r4 = resultado["principios"]["R4"]
        r7 = resultado["principios"]["R7"]
        assert r1["auditable_auto"] is False
        assert r4["auditable_auto"] is False
        assert r7["auditable_auto"] is False

    def test_resumen_incluye_los_7_principios(self):
        resultado = validar_principios_redaccion_2024("Texto.", poblacion_objetivo="adulto_joven")
        for pid in ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
            assert pid in resultado["resumen"]

    def test_texto_vacio_no_falla(self):
        resultado = validar_principios_redaccion_2024("", poblacion_objetivo="adulto_joven")
        assert "principios" in resultado
        assert "alertas" in resultado
        assert "resumen" in resultado


class TestConstruirBloqueLegalEncabezado:
    def test_incluye_todas_las_secciones_obligatorias(self):
        bloque = construir_bloque_legal_encabezado(
            nombre_profesional="Ps. Johan Salgado",
            tarjeta_profesional="TP-12345",
            universidad="Universidad Nacional",
            resolucion="Res. 1234/2010",
            nombre_paciente="Paciente X",
            edad_display="35a",
            fecha_evaluacion="2026-06-02",
            objetivo="Evaluar queja de memoria",
            lugar="Bogotá, D.C.",
        )
        assert "INFORME NEUROPSICOLÓGICO CONFIDENCIAL" in bloque
        assert "Ps. Johan Salgado" in bloque
        assert "TP-12345" in bloque
        assert "Universidad Nacional" in bloque
        assert "Res. 1234/2010" in bloque
        assert "Paciente X" in bloque
        assert "35a" in bloque
        assert "2026-06-02" in bloque
        assert "Evaluar queja de memoria" in bloque
        assert "Uso previsto" in bloque
        assert "Limitaciones" in bloque
        assert "Bogotá, D.C." in bloque

    def test_uso_previsto_default_cuando_no_se_pasa(self):
        bloque = construir_bloque_legal_encabezado()
        assert CLAUSULAS_INFORME_PROFESIONAL["uso_previsto_default"] in bloque

    def test_uso_previsto_custom_reemplaza_default(self):
        bloque = construir_bloque_legal_encabezado(uso_previsto="Pericial")
        assert "Uso previsto: Pericial" in bloque
        assert CLAUSULAS_INFORME_PROFESIONAL["uso_previsto_default"] not in bloque

    def test_limitaciones_default_cuando_no_se_pasa(self):
        bloque = construir_bloque_legal_encabezado()
        assert CLAUSULAS_INFORME_PROFESIONAL["limitaciones_default"] in bloque

    def test_limitaciones_custom_reemplaza_default(self):
        bloque = construir_bloque_legal_encabezado(limitaciones="Solo sesión remota.")
        assert "Limitaciones: Solo sesión remota." in bloque
        assert CLAUSULAS_INFORME_PROFESIONAL["limitaciones_default"] not in bloque

    def test_campos_vacios_se_rellenan_con_guion(self):
        bloque = construir_bloque_legal_encabezado()
        assert "Nombre: —" in bloque
        assert "Tarjeta Profesional: —" in bloque
        assert "Universidad: —" in bloque
        assert "Resolución: —" in bloque

    def test_incluye_clausula_confidencialidad_y_responsabilidad(self):
        bloque = construir_bloque_legal_encabezado()
        assert "Ley 1581" in bloque
        assert "Resolución 1995" in bloque
        assert "Ley 1090" in bloque
        assert "responsabilidad profesional" in bloque
