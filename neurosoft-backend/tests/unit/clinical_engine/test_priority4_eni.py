"""Tests para pruebas clínicas de PRIORIDAD 4 - ENI (Evaluación Neuropsicológica Infantil).

Pruebas incluidas (17 subpruebas):
- NiENICDib: Cancelación de Dibujos
- NiENICLet: Cancelación de Letras
- NiENICMen: Cálculo Mental
- NiENIDNum: Dictado de Números
- NiENIDel: Deletreo
- NiENIDen: Denominación
- NiENIEOra: Escritura de Oraciones
- NiENILNum: Lectura de Números
- NiENIMLPCl: Recobro por Claves
- NiENIRHLP: Recuperación de una Historia (Largo Plazo)
- NiENIRHis: Recuerdo de una Historia
- NiENIROra: Repetición de Oraciones
- NiENISDir: Serie Directa
- NiENISIns: Seguimiento de Instrucciones
- NiENISInv: Serie Inversa
- NiENIVLS: Velocidad de Lectura en Silencio
- NiENIVLVA: Velocidad de Lectura en Voz Alta

Fuente: Ostrosky-Solís, F., et al. (2006). Evaluación Neuropsicológica Infantil (ENI).
Revista Mexicana de Psicología, 23(2), 185-199.

Nota: La ENI fue desarrollada y validada en México, pero se utiliza ampliamente
en Latinoamérica. Los baremos en BD_NEURO_MAESTRA.json fueron adaptados para
población colombiana por el equipo de NeuroSoft.
"""



class TestENICancelacion:
    """ENI - Pruebas de Cancelación (Atención)."""

    def test_nienicdib_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENICDib")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nieniclet_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENICLet")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienicmen_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENICMen")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0


class TestENILecturaEscritura:
    """ENI - Pruebas de Lectura y Escritura."""

    def test_nienidnum_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIDNum")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienidel_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIDel")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nieniden_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIDen")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienieora_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIEOra")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienilnum_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENILNum")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nieniora_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIROra")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0


class TestENIMemoria:
    """ENI - Pruebas de Memoria."""

    def test_nienimlpcl_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIMLPCl")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienirhlp_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIRHLP")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienirhis_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIRHis")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0


class TestENIFuncionesEjecutivas:
    """ENI - Pruebas de Funciones Ejecutivas."""

    def test_nienisdir_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENISDir")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienisins_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENISIns")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienisinv_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENISInv")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0


class TestENIVelocidadLectura:
    """ENI - Pruebas de Velocidad de Lectura."""

    def test_nienivls_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIVLS")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nienivlva_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiENIVLVA")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0
