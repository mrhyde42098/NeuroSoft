"""
F6.2 — Tests del validador de los 7 principios narrativos.
"""
import pytest

from app.infrastructure.report_pro.narrative import (
    PRINCIPIOS_NARRATIVOS,
    validar_principios_narrativa,
)


class TestValidarPrincipiosNarrativa:
    def test_narrativa_completa_cumple_todos_los_principios(self):
        texto = (
            "El paciente obtuvo un CI Total de 87 (rango Promedio Bajo), "
            "lo cual sugiere un rendimiento intelectual general dentro de los "
            "límites esperados. Se aplicaron baremos de Neuronorma Colombia "
            "(Arango-Lasprilla & Rivera, 2017), válidos para población adulta "
            "colombiana. El perfil es consistente con un TDAH de predominio "
            "inatento (DSM-5-TR 314.00 / CIE-10 F90.0), pendiente de "
            "confirmación clínica. Es importante señalar que el rendimiento "
            "del paciente pudo estar influenciado por la fatiga reportada."
        )
        recomendaciones = (
            "[TERAPÉUTICA] Iniciar terapia de rehabilitación cognitiva con "
            "frecuencia bisemanal (lunes y jueves), 12 sesiones, evaluación "
            "de progreso a la sesión 6."
        )
        resultado = validar_principios_narrativa(
            texto, recomendaciones=recomendaciones, poblacion_objetivo="adulto_mayor"
        )
        assert resultado["cumple"] is True
        assert resultado["alertas"] == []
        assert all(
            p["estado"] in ("ok", "no_aplica")
            for p in resultado["principios"].values()
        )

    def test_lenguaje_definitivo_dispara_p4(self):
        texto = (
            "El paciente tiene un trastorno de déficit atencional. Presenta "
            "un déficit atencional severo según las pruebas aplicadas. El CI "
            "de 87 indica retraso."
        )
        resultado = validar_principios_narrativa(texto)
        p4 = resultado["principios"]["P4"]
        assert p4["estado"] == "revisar"
        assert "lenguaje definitivo" in p4["detalle"].lower()

    def test_recomendaciones_vagas_disparan_p6(self):
        texto = (
            "El CI Total de 87 sugiere un rendimiento promedio bajo. "
            "El perfil es consistente con dificultades atencionales."
        )
        resultado = validar_principios_narrativa(
            texto, recomendaciones="Se recomienda seguimiento."
        )
        p6 = resultado["principios"]["P6"]
        assert p6["estado"] == "revisar"

    def test_ausencia_limitaciones_dispara_p5(self):
        texto = (
            "El CI Total de 87 sugiere un rendimiento promedio bajo. "
            "El perfil es consistente con dificultades atencionales."
        )
        resultado = validar_principios_narrativa(texto)
        p5 = resultado["principios"]["P5"]
        assert p5["estado"] == "revisar"

    def test_poblacion_infantil_exige_mencion_baremos_colombianos(self):
        texto = (
            "El paciente obtuvo un CI Total de 87, lo cual sugiere un "
            "rendimiento promedio bajo. El perfil es consistente con "
            "dificultades atencionales. La fatiga pudo haber influido."
        )
        resultado = validar_principios_narrativa(texto, poblacion_objetivo="infantil")
        p3 = resultado["principios"]["P3"]
        assert p3["estado"] == "revisar"
        assert "Neuronorma" in p3["detalle"] or "Arango" in p3["detalle"]

    def test_poblacion_adulto_joven_p3_no_aplica(self):
        texto = "El CI Total de 87 sugiere rendimiento promedio bajo."
        resultado = validar_principios_narrativa(texto, poblacion_objetivo="adulto_joven")
        p3 = resultado["principios"]["P3"]
        assert p3["estado"] == "no_aplica"

    def test_narrativa_muy_corta_dispara_p1(self):
        texto = "Breve."
        resultado = validar_principios_narrativa(texto)
        p1 = resultado["principios"]["P1"]
        assert p1["estado"] == "revisar"

    def test_sin_puntuaciones_p2_no_aplica(self):
        texto = "El paciente asistió puntualmente a las sesiones."
        resultado = validar_principios_narrativa(texto)
        p2 = resultado["principios"]["P2"]
        assert p2["estado"] == "no_aplica"

    def test_principios_narrativos_tienen_7_elementos(self):
        """F6.2 — El catálogo debe ser estable: exactamente 7 principios."""
        assert len(PRINCIPIOS_NARRATIVOS) == 7
        ids = {p["id"] for p in PRINCIPIOS_NARRATIVOS}
        assert ids == {"P1", "P2", "P3", "P4", "P5", "P6", "P7"}

    def test_resumen_incluye_los_7_principios(self):
        resultado = validar_principios_narrativa("Texto cualquiera.")
        for pid in ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]:
            assert pid in resultado["resumen"]

    def test_alertas_vacias_si_cumple(self):
        texto = (
            "El CI Total de 87 sugiere un rendimiento promedio bajo. "
            "Se aplicaron baremos de Neuronorma Colombia (Arango-Lasprilla). "
            "El perfil es consistente con TDAH (F90.0). Es importante señalar "
            "que la fatiga y la medicación pudieron haber influido en el "
            "rendimiento del paciente durante la evaluación."
        )
        recomendaciones = (
            "Iniciar terapia bisemanal con 12 sesiones, evaluación a la "
            "sesión 6 con ajuste de plan."
        )
        resultado = validar_principios_narrativa(
            texto, recomendaciones=recomendaciones, poblacion_objetivo="adulto_mayor"
        )
        assert resultado["cumple"] is True
        assert resultado["alertas"] == []

    def test_texto_vacio_no_falla(self):
        """F6.2 — debe tolerar entradas vacías sin lanzar excepciones."""
        resultado = validar_principios_narrativa("")
        assert "principios" in resultado
        assert "alertas" in resultado
        assert "resumen" in resultado
