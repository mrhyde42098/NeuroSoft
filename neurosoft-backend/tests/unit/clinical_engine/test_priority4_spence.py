"""Tests para pruebas clínicas de PRIORIDAD 4 - Spence (Ansiedad Infantil).

Pruebas incluidas (4 subescalas):
- NiSpenceGA: Ansiedad Generalizada
- NiSpencePIF: Temor a Lesión Física
- NiSpenceSA: Ansiedad Social
- NiSpenceSepAx: Ansiedad de Separación

Fuente: Spence, S. H. (1998). A measure of anxiety symptoms among children.
Behaviour Research and Therapy, 36(5), 545-566.

Validación latinoamericana:
- Orgilés, M., et al. (2016). Adaptación española de la Spence Children's Anxiety Scale.
- Essau, C. A., et al. (2011). Validation of the Spence Children's Anxiety Scale in
  Spanish children. Journal of Anxiety Disorders, 25(8), 1023-1030.

Nota: Aunque la validación principal es española, los baremos se han adaptado
para población colombiana considerando similitudes culturales y lingüísticas.
"""


class TestSpenceAnsiedadInfantil:
    """Spence Children's Anxiety Scale - Subescalas."""

    def test_nispencega_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiSpenceGA")
        assert prueba is not None
        assert prueba.tipo_calculo == "puntaje_directo_a_t"
        assert len(prueba.baremos) > 0

    def test_nispencepif_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiSpencePIF")
        assert prueba is not None
        assert prueba.tipo_calculo == "puntaje_directo_a_t"
        assert len(prueba.baremos) > 0

    def test_nispencesa_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiSpenceSA")
        assert prueba is not None
        assert prueba.tipo_calculo == "puntaje_directo_a_t"
        assert len(prueba.baremos) > 0

    def test_nispencesepax_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiSpenceSepAx")
        assert prueba is not None
        assert prueba.tipo_calculo == "puntaje_directo_a_t"
        assert len(prueba.baremos) > 0
