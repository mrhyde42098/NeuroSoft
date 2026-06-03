"""Tests para pruebas clínicas de PRIORIDAD 4 - Pruebas restantes.

Pruebas incluidas:
- GoNoGoICO: Go/No-Go (Inhibición de Conducta)
- InstrConflICO: Instrucciones Conflictivas
- NiEniMLP: ENI Memoria a Largo Plazo
- NiEniReco: ENI Reconocimiento
- OrDNpsi: Orden Neuropsicológica
- OrSD: Orden Simples-Dobles
- OrTMTA: Orden Trail Making Test A
- OrTMTB: Orden Trail Making Test B
- RefranesICO: Refranes (Inventario de Conducta Oral)

Pruebas combinadas (no se prueban individualmente):
- AdBusSim + ViBusSim: Búsqueda de Símbolos (combinada adulto joven/mayor)
- NiEniE1 + NiEniE2 + NiEniE3 + NiEniE4 = NiEniLT: ENI Lectura Total (suma de 4 subpruebas)

Fuentes:
- GoNoGoICO, InstrConflICO, RefranesICO: Adaptaciones de pruebas de funciones ejecutivas.
- NiEniMLP, NiEniReco: Ostrosky-Solís, F., et al. (2006). ENI.
- OrDNpsi, OrSD, OrTMTA, OrTMTB: Protocolos de ordenamiento neuropsicológico.
"""


class TestPruebasRestantes:
    """Pruebas restantes de PRIORIDAD 4."""

    def test_gonogoico_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("GoNoGoICO")
        assert prueba is not None
        assert len(prueba.baremos) > 0

    def test_instrconflico_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("InstrConflICO")
        assert prueba is not None
        assert len(prueba.baremos) > 0

    def test_nienimlp_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiEniMLP")
        assert prueba is not None
        assert len(prueba.baremos) > 0

    def test_nienireco_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiEniReco")
        assert prueba is not None
        assert len(prueba.baremos) > 0

    def test_ordnpsi_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("OrDNpsi")
        assert prueba is not None
        assert len(prueba.baremos) > 0

    def test_orsd_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("OrSD")
        assert prueba is not None
        assert len(prueba.baremos) > 0

    def test_ortmta_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("OrTMTA")
        assert prueba is not None
        assert len(prueba.baremos) > 0

    def test_ortmtb_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("OrTMTB")
        assert prueba is not None
        assert len(prueba.baremos) > 0

    def test_refranesico_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("RefranesICO")
        assert prueba is not None
        assert len(prueba.baremos) > 0
