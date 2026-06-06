"""Tests para pruebas clínicas de PRIORIDAD 4 - Adulto Joven (pruebas restantes).

Pruebas incluidas:
- AdStroop_Corr: Stroop Corrección (Adulto Joven)

Fuentes:
- Stroop, J. R. (1935). Studies of interference in serial verbal reactions.
  Journal of Experimental Psychology, 18(6), 643-662.
- Baremos colombianos: Ostrosky-Solís, F., et al. (2007). Neuropsi Atención y Memoria.
"""


class TestAdultoJovenRestantes:
    """Pruebas de adulto joven de PRIORIDAD 4."""

    def test_adstroop_corr_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("AdStroop_Corr")
        assert prueba is not None
        assert prueba.tipo_calculo == "ajuste"
        assert len(prueba.baremos) > 0
