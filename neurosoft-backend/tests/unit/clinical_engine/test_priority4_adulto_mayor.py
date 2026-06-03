"""Tests para pruebas clínicas de PRIORIDAD 4 - Adulto Mayor (pruebas restantes).

Pruebas incluidas:
- Denom48: Denominación 48 items - Adulto Mayor
- EscQueja: Escala de Queja Subjetiva de Memoria
- EscYesavage: Escala de Depresión Geriátrica Yesavage (GDS-15)
- GBTotal: Grober & Buschke - Recuerdo Libre Total
- SDMT: SDMT - Símbolo-Dígito (norma AM)
- ViGroberMC_Dif: Grober MC - Retención Diferida Claves
- ViMRemRec: Memoria de Trabajo - Recuerdo
- ViTMTB: Trail Making Test B (Adulto Mayor)

Fuentes:
- Denom48: Deloche, G., et al. (1997). DO 80. Adaptación colombiana.
- EscQueja: Adaptación de Memory Complaints Questionnaire.
- EscYesavage: Yesavage, J. A., et al. (1982). Geriatric Depression Scale.
  Validación colombiana: Campo-Arias, A., et al. (2006).
- GBTotal: Grober, E., & Buschke, H. (1987). Genuine memory deficits in dementia.
  Developmental Neuropsychology, 3(1), 13-36.
- SDMT: Smith, A. (1982). Symbol Digit Modalities Test.
  Baremos colombianos: Ostrosky-Solís, F., et al. (2007).
- ViGroberMC_Dif: Grober, E., & Buschke, H. (1987).
- ViMRemRec: Adaptación de pruebas de memoria de trabajo.
- ViTMTB: Reitan, R. M. (1958). Trail Making Test.
  Baremos colombianos: Ostrosky-Solís, F., et al. (2007).
"""



class TestAdultoMayorRestantes:
    """Pruebas de adulto mayor de PRIORIDAD 4."""

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

    def test_vigrobermc_dif_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViGroberMC_Dif")
        assert prueba is not None
        assert prueba.tipo_calculo == "wais_range"
        assert len(prueba.baremos) > 0

    def test_vimremrec_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViMRemRec")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_vitmtb_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViTMTB")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0
