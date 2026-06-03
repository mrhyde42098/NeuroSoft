"""Tests para pruebas clínicas de PRIORIDAD 4 - Otras pruebas infantiles.

Pruebas incluidas:
- NiComp: Comprensión lectora en voz alta
- NiCopTxt: % de palabras con error en la copia
- NiDR: Dígitos en regresión
- NiIntObj: Integración de objetos
- NiLVS: Comprensión lectora silenciosa
- NiPrec: Palabras con error en lectura en voz alta
- NiRDD: Dígitos en progresión
- NiRecEmo: Reconocimiento de expresiones
- NiVin: Vineland (Adaptación Social)

Fuentes:
- NiComp, NiCopTxt, NiPrec: Ostrosky-Solís, F., et al. (2006). ENI.
- NiDR, NiRDD: Wechsler, D. (2003). WISC-IV. Adaptación colombiana.
- NiIntObj: Korkman, M., et al. (1998). NEPSY.
- NiLVS: Ostrosky-Solís, F., et al. (2006). ENI.
- NiRecEmo: Adaptación de Reading the Mind in the Eyes Test (Baron-Cohen, 2001).
- NiVin: Sparrow, S. S., et al. (1984). Vineland Adaptive Behavior Scales.
"""



class TestOtrasPruebasInfantiles:
    """Otras pruebas infantiles de PRIORIDAD 4."""

    def test_nicomp_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiComp")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nicoptxt_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiCopTxt")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nidr_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiDR")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niintobj_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiIntObj")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nilvs_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiLVS")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niprec_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiPrec")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nirdd_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiRDD")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nirecemo_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiRecEmo")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nivin_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiVin")
        assert prueba is not None
        assert prueba.tipo_calculo == "puntaje"
        assert len(prueba.baremos) > 0
