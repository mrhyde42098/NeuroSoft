"""Tests para pruebas clínicas de PRIORIDAD 4 - EAD (Escala Abreviada de Desarrollo).

Pruebas incluidas (5 subescalas):
- NiEADAL: Audición y Lenguaje
- NiEADMF: Motricidad Fina
- NiEADMG: Motricidad Gruesa
- NiEADPS: Personal Social
- NiEADTot: EAD Total

Fuente: Ministerio de la Protección Social de Colombia (2008).
Escala Abreviada de Desarrollo (EAD-3). Bogotá: Ministerio de la Protección Social.

Nota: La EAD-3 es una escala desarrollada específicamente para población colombiana
por el Ministerio de la Protección Social. Es utilizada en el seguimiento del
desarrollo infantil en programas de crecimiento y desarrollo en Colombia.
"""


class TestEADDesarrolloInfantil:
    """Escala Abreviada de Desarrollo (EAD-3) - Colombia."""

    def test_nieadal_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiEADAL")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nieadmf_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiEADMF")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nieadmg_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiEADMG")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nieadps_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiEADPS")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nieadtot_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiEADTot")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0
