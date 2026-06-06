"""Tests para pruebas clínicas de PRIORIDAD 3.

Pruebas incluidas:
1. WISC-IV complementarias (6 pruebas)
2. K-ABC índices y subpruebas (15 pruebas)
3. Stroop variantes (3 pruebas)
4. Otras escalas (10 pruebas)

Nota: Estos tests verifican que los baremos existen y que el motor puede
procesar las pruebas sin errores. Los valores específicos no se verifican
debido a la variabilidad de los rangos de PD válidos.
"""


class TestWISCIVComplementarias:
    """WISC-IV subpruebas complementarias (infantil)."""

    def test_niwiscond_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWiscConD")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niwiscond_edad_10(self, engine, ctx_infantil_10):
        """Conceptos con Dibujos WISC-IV para niño 10 años."""
        result = engine.score("test", {"NiWiscConD": 20}, ctx_infantil_10)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "NiWiscConD"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None

    def test_niwiscmat_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWiscMat")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niwiscmat_edad_10(self, engine, ctx_infantil_10):
        """Matrices WISC-IV para niño 10 años."""
        result = engine.score("test", {"NiWiscMat": 20}, ctx_infantil_10)
        r = result.resultados[0]
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # PD=20 para 10 años debería dar escalar 10
        assert r.puntaje_escalar == 10.0

    def test_niwisfiginc_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWisFigInc")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niwisfiginc_edad_10(self, engine, ctx_infantil_10):
        """Figuras Incompletas WISC-IV para niño 10 años."""
        result = engine.score("test", {"NiWisFigInc": 20}, ctx_infantil_10)
        r = result.resultados[0]
        assert r.fue_realizada
        assert r.puntaje_escalar is not None

    def test_niwisinf_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWisInf")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niwisinf_edad_10(self, engine, ctx_infantil_10):
        """Información WISC-IV para niño 10 años."""
        result = engine.score("test", {"NiWisInf": 20}, ctx_infantil_10)
        r = result.resultados[0]
        assert r.fue_realizada
        assert r.puntaje_escalar is not None

    def test_niwispalcon_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWisPalCon")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niwispalcon_edad_10(self, engine, ctx_infantil_10):
        """Palabras con Contexto WISC-IV para niño 10 años."""
        result = engine.score("test", {"NiWisPalCon": 20}, ctx_infantil_10)
        r = result.resultados[0]
        assert r.fue_realizada
        assert r.puntaje_escalar is not None

    def test_niwisreg_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWisReg")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niwisreg_edad_10(self, engine, ctx_infantil_10):
        """Registros WISC-IV para niño 10 años."""
        result = engine.score("test", {"NiWisReg": 40}, ctx_infantil_10)
        r = result.resultados[0]
        assert r.fue_realizada
        assert r.puntaje_escalar is not None


class TestKABCIndices:
    """K-ABC índices compuestos (infantil)."""

    def test_nikabccitot_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKABCCITot")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcindesc_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKABCIndEsc")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcindsec_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKABCIndSec")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcindsim_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKABCIndSim")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0


class TestKABCSubpruebas:
    """K-ABC subpruebas (infantil)."""

    def test_nikabccg_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcCG")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcmana_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcMAna")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcmesp_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcMEsp")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcmma_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcMMa")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcopa_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcOPa")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcrc_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcRC")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcrn_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcRN")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcsfot_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcSFot")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabctria_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcTria")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nikabcvmag_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiKabcVMag")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0


class TestStroopVariantes:
    """Stroop variantes (adulto_mayor e infantil)."""

    def test_stroopam_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("StroopAM")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_stroopam_edad_65(self, engine, ctx_adulto_mayor_65):
        """Stroop Adulto Mayor para 65 años."""
        result = engine.score("test", {"StroopAM": 30}, ctx_adulto_mayor_65)
        r = result.resultados[0]
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # PD=30 debería dar escalar 10
        assert r.puntaje_escalar == 10.0

    def test_nist_edades_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiSt_Edades")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nist_puntajes_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiSt_Puntajes")
        assert prueba is not None
        assert prueba.tipo_calculo == "puntaje"
        assert len(prueba.baremos) > 0


class TestOtrasEscalas:
    """Otras escalas (adulto_mayor)."""

    def test_denom48_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("Denom48")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_escqueja_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("EscQueja")
        assert prueba is not None
        assert prueba.tipo_calculo == "clasificacion_fija"
        assert len(prueba.baremos) > 0

    def test_escyesavage_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("EscYesavage")
        assert prueba is not None
        assert prueba.tipo_calculo == "clasificacion_fija"
        assert len(prueba.baremos) > 0

    def test_fluidanim_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("FluidAnim")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_fluidp_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("FluidP")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_gbtotal_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("GBTotal")
        assert prueba is not None
        assert prueba.tipo_calculo == "wais_range"
        assert len(prueba.baremos) > 0

    def test_sdmt_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("SDMT")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_vimremrec_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViMRemRec")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_vigroberrt_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViGroberRT")
        assert prueba is not None
        assert prueba.tipo_calculo == "wais_range"
        assert len(prueba.baremos) > 0

    def test_vifcro_tiempo_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViFCRO_Tiempo")
        assert prueba is not None
        assert prueba.tipo_calculo == "wais_range"
        assert len(prueba.baremos) > 0
