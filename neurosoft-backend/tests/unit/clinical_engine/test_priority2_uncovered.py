"""Tests para pruebas clínicas de PRIORIDAD 2.

Pruebas incluidas:
1. ViTLRes - Torre de Londres Resolución (adulto_mayor)
2. ViTLTC - Torre de Londres Total Correctas (adulto_mayor)
3. AdFCRORec - Figura Compleja Rey-Osterrieth Recobro (adulto_mayor)
4. NiWiscBusSim - Búsqueda de Símbolos WISC-IV (infantil)
5. EscKertesz - Inventario Conductual Frontal FBI (adulto_mayor)

Fuentes de referencia:
- Culley & Evans (2005) - Tower of London normative data
- Fastenau et al. (1999) - Rey-Osterrieth Complex Figure normative data
- Wechsler (2003) - WISC-IV Technical Manual
- Kertesz et al. (1997) - Frontal Behavioral Inventory
- Ostrosky-Solís et al. (2010) - Validación colombiana
"""




class TestViTLRes:
    """Torre de Londres - Resolución (adulto_mayor)."""

    def test_vitlres_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViTLRes")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_vitlres_edad_65_promedio(self, engine, ctx_adulto_mayor_65):
        """
        Torre de Londres Resolución para adulto mayor 65 años.
        PD=20 (de 30 posibles) → rendimiento promedio.
        Referencia: Culley & Evans (2005)
        """
        result = engine.score("test", {"ViTLRes": 20}, ctx_adulto_mayor_65)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViTLRes"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # PD=20 debería dar escalar alto (18)
        assert r.puntaje_escalar >= 15


class TestViTLTC:
    """Torre de Londres - Total Correctas (adulto_mayor)."""

    def test_vitltc_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViTLTC")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_vitltc_edad_65_promedio(self, engine, ctx_adulto_mayor_65):
        """
        Torre de Londres Total Correctas para adulto mayor 65 años.
        PD=7 (de 15 posibles) → rendimiento promedio-alto.
        Referencia: Culley & Evans (2005)
        Nota: PD=7 se ajusta a PD=8 por escolaridad Secundaria (+1)
        """
        result = engine.score("test", {"ViTLTC": 7}, ctx_adulto_mayor_65)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViTLTC"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # PD=7 (ajustado a 8) debería dar escalar 18
        assert r.puntaje_escalar == 18.0

    def test_vitltc_edad_65_bajo(self, engine, ctx_adulto_mayor_65):
        """
        Torre de Londres Total Correctas para adulto mayor 65 años.
        PD=5 (de 15 posibles) → rendimiento bajo.
        """
        result = engine.score("test", {"ViTLTC": 5}, ctx_adulto_mayor_65)
        r = result.resultados[0]
        assert r.fue_realizada
        # PD=5 debería dar escalar 14
        assert r.puntaje_escalar <= 15


class TestAdFCRORec:
    """Figura Compleja Rey-Osterrieth - Recobro (adulto_mayor)."""

    def test_adfcrorec_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("AdFCRORec")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_adfcrorec_edad_65_promedio(self, engine, ctx_adulto_mayor_65):
        """
        Figura Compleja Rey-Osterrieth Recobro para adulto mayor 65 años.
        PD=20 (de 36 posibles) → rendimiento promedio.
        Referencia: Fastenau et al. (1999), Meyers & Meyers (1995)
        """
        result = engine.score("test", {"AdFCRORec": 20}, ctx_adulto_mayor_65)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "AdFCRORec"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # PD=20 para 65 años debería dar escalar 12
        assert 10 <= r.puntaje_escalar <= 14

    def test_adfcrorec_edad_65_alto(self, engine, ctx_adulto_mayor_65):
        """
        Figura Compleja Rey-Osterrieth Recobro para adulto mayor 65 años.
        PD=30 (de 36 posibles) → rendimiento alto.
        """
        result = engine.score("test", {"AdFCRORec": 30}, ctx_adulto_mayor_65)
        r = result.resultados[0]
        assert r.fue_realizada
        # PD=30 debería dar escalar 15
        assert r.puntaje_escalar >= 14

    def test_adfcrorec_edad_65_bajo(self, engine, ctx_adulto_mayor_65):
        """
        Figura Compleja Rey-Osterrieth Recobro para adulto mayor 65 años.
        PD=10 (de 36 posibles) → rendimiento bajo.
        """
        result = engine.score("test", {"AdFCRORec": 10}, ctx_adulto_mayor_65)
        r = result.resultados[0]
        assert r.fue_realizada
        # PD=10 debería dar escalar 7
        assert r.puntaje_escalar <= 9


class TestNiWiscBusSim:
    """Búsqueda de Símbolos WISC-IV (infantil)."""

    def test_niwisbussim_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWiscBusSim")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_niwisbussim_edad_10_promedio(self, engine, ctx_infantil_10):
        """
        Búsqueda de Símbolos WISC-IV para niño 10 años.
        PD=20 → rendimiento promedio-bajo.
        Referencia: Wechsler (2003), Adaptación colombiana (2014)
        """
        result = engine.score("test", {"NiWiscBusSim": 20}, ctx_infantil_10)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "NiWiscBusSim"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # PD=20 para 10 años debería dar escalar 9
        assert r.puntaje_escalar == 9.0

    def test_niwisbussim_edad_10_alto(self, engine, ctx_infantil_10):
        """
        Búsqueda de Símbolos WISC-IV para niño 10 años.
        PD=40 → rendimiento alto.
        """
        result = engine.score("test", {"NiWiscBusSim": 40}, ctx_infantil_10)
        r = result.resultados[0]
        assert r.fue_realizada
        # PD=40 debería dar escalar 18
        assert r.puntaje_escalar >= 16

    def test_niwisbussim_edad_10_bajo(self, engine, ctx_infantil_10):
        """
        Búsqueda de Símbolos WISC-IV para niño 10 años.
        PD=10 → rendimiento bajo.
        """
        result = engine.score("test", {"NiWiscBusSim": 10}, ctx_infantil_10)
        r = result.resultados[0]
        assert r.fue_realizada
        # PD=10 debería dar escalar 8
        assert r.puntaje_escalar <= 10


class TestEscKertesz:
    """Inventario Conductual Frontal FBI (adulto_mayor)."""

    def test_esckertesz_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("EscKertesz")
        assert prueba is not None
        assert prueba.tipo_calculo == "clasificacion_fija"
        assert len(prueba.baremos) > 0

    def test_esckertesz_normal(self, engine, ctx_adulto_mayor_65):
        """
        FBI/Kertesz para adulto mayor 65 años.
        PD=5 → clasificación Normal (N).
        Referencia: Kertesz et al. (1997), Ostrosky-Solís et al. (2010)
        """
        result = engine.score("test", {"EscKertesz": 5}, ctx_adulto_mayor_65)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "EscKertesz"
        assert r.fue_realizada
        # PD=5 debería dar clasificación N (Normal)
        assert r.metadata['clasificacion_codigo'] == "N"
        assert r.interpretacion == "Normal"

    def test_esckertesz_deterioro_leve(self, engine, ctx_adulto_mayor_65):
        """
        FBI/Kertesz para adulto mayor 65 años.
        PD=15 → clasificación Deterioro Leve (DL).
        """
        result = engine.score("test", {"EscKertesz": 15}, ctx_adulto_mayor_65)
        r = result.resultados[0]
        assert r.fue_realizada
        # PD=15 debería dar clasificación DL (Deterioro Leve)
        assert r.metadata['clasificacion_codigo'] == "DL"
        assert r.interpretacion == "Deficit Leve"

    def test_esckertesz_deterioro_ejecutivo(self, engine, ctx_adulto_mayor_65):
        """
        FBI/Kertesz para adulto mayor 65 años.
        PD=30 → clasificación Deterioro Ejecutivo (DE).
        """
        result = engine.score("test", {"EscKertesz": 30}, ctx_adulto_mayor_65)
        r = result.resultados[0]
        assert r.fue_realizada
        # PD=30 debería dar clasificación DE (Deterioro Ejecutivo)
        assert r.metadata['clasificacion_codigo'] == "DE"
        assert r.interpretacion == "Deficit Extremo"
