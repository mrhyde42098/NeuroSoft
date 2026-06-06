"""Tests para pruebas clínicas de PRIORIDAD 4 - Fluidez Verbal y Figura Rey-Osterrieth.

PRUEBAS DE FLUIDEZ VERBAL:
- NiFA: Fluidez Verbal Animales (infantil)
- NiFM: Fluidez Verbal Fonémica (infantil)
- FluidAnim: Fluidez Verbal Animales (adulto mayor)
- FluidP: Fluidez Verbal Fonémica P (adulto mayor)

Fuentes:
- Infantil: Ostrosky-Solís, F., et al. (2006). Neuropsi Atención y Memoria.
- Adulto Mayor: Ostrosky-Solís, F., et al. (2007). Neuropsi Atención y Memoria 6-85 años.
  Revista Mexicana de Psicología, 24(1), 5-23.

Nota: Los baremos de fluidez verbal fueron adaptados para población colombiana
considerando diferencias léxicas regionales.

FIGURA COMPLEJA REY-OSTERRIETH (FCRO):
- NiFCROCop: FCRO Copia (infantil)
- NiFCRORec: FCRO Memoria (infantil)
- AdFCRORec: FCRO Exactitud Recobro (adulto mayor)

Fuentes:
- Rey, A. (1941). L'examen psychologique dans les cas d'encéphalopathie traumatique.
  Archives de Psychologie, 28, 286-340.
- Ostrosky-Solís, F., et al. (1999). Neuropsi: Evaluación Neuropsicológica Breve.
- Baremos colombianos adaptados por el equipo de NeuroSoft.
"""


class TestFluidezVerbal:
    """Pruebas de Fluidez Verbal (semántica y fonémica)."""

    def test_nifa_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiFA")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
        assert len(prueba.baremos) > 0

    def test_nifm_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiFM")
        assert prueba is not None
        assert prueba.tipo_calculo == "rango_puntaje"
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


class TestFiguraReyOsterrieth:
    """Figura Compleja Rey-Osterrieth (FCRO)."""

    def test_nifcro_cop_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiFCROCop")
        assert prueba is not None
        assert prueba.tipo_calculo == "z_score"
        assert len(prueba.baremos) > 0

    def test_nifcro_rec_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiFCRORec")
        assert prueba is not None
        assert prueba.tipo_calculo == "z_score"
        assert len(prueba.baremos) > 0

    def test_adfcrorec_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("AdFCRORec")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0
