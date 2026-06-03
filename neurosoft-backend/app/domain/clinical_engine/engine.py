"""
app/domain/clinical_engine/engine.py
=====================================
Orquestador del Motor de Calificación Clínica.

El Engine es el cerebro del sistema. Recibe un diccionario de
{test_id: puntaje_bruto} y produce una lista de ResultadoPrueba
aplicando la strategy correcta para cada prueba, con ajuste de
escolaridad para adulto mayor.

Responsabilidades:
    1. Determinar la población clínica del paciente.
    2. Aplicar ajuste de escolaridad (Adulto Mayor).
    3. Seleccionar la strategy via Factory.
    4. Ejecutar el cálculo y capturar errores.
    5. Retornar ResultadoPrueba con dominio cognitivo asignado.

NO SABE de FastAPI, SQLAlchemy ni de DTOs de presentación.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from app.core.utils import AgeCalculator, CronologicalAge
from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.factory import ScoringStrategyFactory
from app.domain.entities.models import ResultadoPrueba

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Mapa de dominios cognitivos
# (test_id → nombre del dominio para la tabla e informe)
# ─────────────────────────────────────────────────────────────
_COGNITIVE_DOMAINS: dict[str, str] = {
    # WISC-IV
    "NiWiscDC": "Razonamiento Perceptual", "NiWiscSem": "Comprensión Verbal",
    "NiWiscVoc": "Comprensión Verbal", "NiWiscCom": "Comprensión Verbal",
    "NiWiscLN": "Memoria de Trabajo", "NiWiscAri": "Memoria de Trabajo",
    "NiWiscMat": "Razonamiento Perceptual", "NiWiscConD": "Razonamiento Perceptual",
    "NiWiscCl": "Velocidad de Proceso", "NiWiscBusSim": "Velocidad de Proceso",
    "NiWisFigInc": "Razonamiento Perceptual", "NiWisInf": "Comprensión Verbal",
    "NiWiscRDD": "Memoria de Trabajo", "NiWisPalCon": "Comprensión Verbal",
    "NiWisReg": "Comprensión Verbal",
    # WISC-IV Índices
    "NiWISCTot": "Inteligencia General", "NiWISCIndCapGen": "Inteligencia General",
    "NiWISCIndCopCog": "Inteligencia General", "NiWISCIndComVer": "Índice CI",
    "NiWISCIndRazPer": "Índice CI", "NiWISCIndMemTra": "Índice CI",
    "NiWISCIndVelPro": "Índice CI",
    # KABC-II
    "NiKabcVMag": "Razonamiento Perceptual", "NiKabcRC": "Memoria",
    "NiKabcMMa": "Funciones Ejecutivas", "NiKabcCG": "Razonamiento Perceptual",
    "NiKabcRN": "Memoria de Trabajo", "NiKabcTria": "Razonamiento Perceptual",
    "NiKabcOPa": "Memoria", "NiKabcSFot": "Memoria",
    "NiKabcMEsp": "Memoria", "NiKabcMAna": "Razonamiento Perceptual",
    # ENI-2
    "NiENIRHis": "Memoria", "NiENIRHLP": "Memoria",
    "NiEniMLP": "Memoria Verbal", "NiENIMLPCl": "Memoria Verbal",
    "NiEniReco": "Memoria Verbal", "NiENIDen": "Lenguaje",
    "NiENIROra": "Lenguaje", "NiENIDel": "Lenguaje",
    "NiENILNum": "Lenguaje", "NiENIDNum": "Lenguaje",
    "NiENISDir": "Memoria de Trabajo", "NiENISInv": "Funciones Ejecutivas",
    "NiENICDib": "Atención", "NiENICLet": "Atención",
    "NiENIEOra": "Lenguaje", "NiENISIns": "Lenguaje",
    "NiENIVLS": "Lenguaje", "NiENIVLVA": "Lenguaje",
    "NiENIRHis": "Memoria",
    # Atención
    "NiTMTA": "Atención", "NiTMTB": "Funciones Ejecutivas",
    "NiSt_Edades": "Atención", "NiSt_Puntajes": "Atención",
    "NiTestPC": "Atención", "NiTestPC_R": "Atención",
    "NiDR": "Funciones Ejecutivas", "NiRDD": "Funciones Ejecutivas",
    "NiIntObj": "Funciones Ejecutivas",
    # Memoria visuoespacial
    "NiFCROCop": "Memoria Visuoespacial", "NiFCRORec": "Memoria Visuoespacial",
    # Lectura
    "NiComp": "Lenguaje", "NiLVS": "Lenguaje",
    "NiPrec": "Lenguaje", "NiCopTxt": "Lenguaje",
    # FCRO Adulto
    "AdFCRO_Rey": "Memoria Visuoespacial",
    # Lenguaje
    "NiFA": "Lenguaje - Fluidez", "NiFM": "Lenguaje - Fluidez",
    "NiRecEmo": "Habilidades Socioemocionales",
    # EAD
    "NiEADMG": "Desarrollo Motor", "NiEADMF": "Desarrollo Motor",
    "NiEADAL": "Desarrollo Lenguaje", "NiEADPS": "Desarrollo Social",
    "NiEADTot": "Desarrollo Global",
    # Socioemocional
    "NiCDI": "Socioemocional - Depresión", "NiVin": "Funcionamiento Adaptativo",
    "NiSpenceOCD": "Socioemocional - Ansiedad", "NiSpenceGA": "Socioemocional - Ansiedad",
    "NiSpenceSA": "Socioemocional - Ansiedad", "NiSpenceSepAx": "Socioemocional - Ansiedad",
    "NiSpencePIF": "Socioemocional - Ansiedad", "NiSpenceTo": "Socioemocional - Ansiedad",
    "NiGadsIS": "Socioemocional - TEA", "NiGadsHP": "Socioemocional - TEA",
    "NiGadsPRC": "Socioemocional - TEA", "NiGadsPatCog": "Socioemocional - TEA",
    "NiGADSCTAs": "Socioemocional - TEA",
    # WAIS-III
    "AdWAISCIT": "Inteligencia General", "AdWAISEMan": "Inteligencia General",
    "AdWASIEVer": "Índice CI", "AdWAISICV": "Índice CI",
    "AdWAISICP": "Índice CI", "AdWAISIMT": "Índice CI", "AdWAISIVP": "Índice CI",
    "AdWAISV": "Comprensión Verbal", "AdWAISI": "Comprensión Verbal",
    "AdWAISC": "Comprensión Verbal", "AdWAISA": "Comprensión Verbal",
    "AdWAISCC": "Organización Perceptual", "AdSDWais": "Velocidad de Proceso",
    "AdMatr": "Organización Perceptual", "AdWAISFI": "Organización Perceptual",
    "AdWAISHI": "Organización Perceptual", "AdWAISRO": "Organización Perceptual",
    "AdWAISL": "Memoria de Trabajo", "AdSemWais": "Comprensión Verbal",
    "AdDDir": "Atención", "AdDPros": "Atención", "AdDReg": "Atención",
    "AdBusSim": "Velocidad de Proceso", "AdBusSim + ViBusSim": "Velocidad de Proceso",
    "AdFCRO_Rey": "Memoria Visuoespacial",
    # Adulto: Memoria y FE
    "AdCVLT": "Memoria Verbal", "AdTMT_AB": "Atención / Funciones Ejecutivas",
    "AdStroop_Corr": "Atención", "AdTL_Torre": "Funciones Ejecutivas",
    "AdBeck": "Socioemocional - Depresión",
    # Adulto mayor
    "ViTMTA": "Atención", "ViTMTB": "Funciones Ejecutivas",
    "ViRDD": "Memoria de Trabajo", "ViRDInv": "Memoria de Trabajo",
    "ViStP": "Atención", "ViStC": "Atención", "ViStPC": "Atención",
    "ViAni": "Lenguaje - Fluidez", "ViSem": "Lenguaje",
    "ViWCat": "Funciones Ejecutivas", "ViWCor": "Funciones Ejecutivas",
    "ViWEPer": "Funciones Ejecutivas", "ViWEAte": "Atención",
    "ViTLTC": "Funciones Ejecutivas", "ViTLMExc": "Funciones Ejecutivas",
    "ViTLLat": "Funciones Ejecutivas", "ViTLEje": "Funciones Ejecutivas",
    "ViTLRes": "Funciones Ejecutivas", "ViGrober_Main": "Memoria Verbal",
    "ViMRemRec": "Memoria", "ViP": "Lenguaje",
    "ViDeno": "Lenguaje", "ViYesavage": "Socioemocional - Depresión",
}

# Tests de tamizaje / escalas / observación directa que no tienen baremos
# en BD_NEURO_MAESTRA.json. El motor los omite sin advertencia porque su
# puntuación se maneja client-side (ScreeningPage.jsx, datos directos).
_NON_BAREMO_TESTS: set[str] = {
    "EscSTAI", "EscASRS", "BNT", "FluidM", "NiCalcEscrito",
    "NiFigHum", "NiRecEscrita", "REY15",
}

def _get_domain(test_id: str) -> str:
    return _COGNITIVE_DOMAINS.get(test_id, "General")


# ─────────────────────────────────────────────────────────────
# CONTEXTO DEL PACIENTE (lo que el Engine necesita)
# ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PatientContext:
    """
    Snapshot demográfico del paciente para el motor.
    Inmutable: garantiza que el motor no muta datos del paciente.
    """
    age: CronologicalAge
    sexo: str
    escolaridad: str
    poblacion: str              # infantil | adulto_joven | adulto_mayor

    @classmethod
    def from_demographics(
        cls,
        birth_date: date,
        evaluation_date: date,
        sexo: str,
        escolaridad: str,
    ) -> PatientContext:
        age = AgeCalculator.calculate(birth_date, evaluation_date)
        return cls(
            age=age,
            sexo=sexo,
            escolaridad=escolaridad,
            poblacion=cls._determine_poblacion(age.years),
        )

    @staticmethod
    def _determine_poblacion(years: int) -> str:
        if years < 18:  return "infantil"
        if years < 50:  return "adulto_joven"
        return "adulto_mayor"


# ─────────────────────────────────────────────────────────────
# RESULTADO DEL MOTOR
# ─────────────────────────────────────────────────────────────

@dataclass
class EngineResult:
    """
    Resultado completo de una sesión de calificación.
    Contiene todos los ResultadoPrueba + metadatos del proceso.
    """
    paciente_id: str
    protocolo: str | None
    poblacion: str
    edad_display: str
    resultados: list[ResultadoPrueba] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    @property
    def pruebas_realizadas(self) -> int:
        return sum(1 for r in self.resultados if r.fue_realizada)

    @property
    def pruebas_sin_dato(self) -> int:
        return sum(1 for r in self.resultados if not r.fue_realizada)

    @property
    def total_pruebas(self) -> int:
        return len(self.resultados)

    @property
    def puntos_debiles(self) -> list[ResultadoPrueba]:
        return [r for r in self.resultados if r.es_punto_debil]

    @property
    def puntos_fuertes(self) -> list[ResultadoPrueba]:
        return [r for r in self.resultados if r.es_punto_fuerte]


# ─────────────────────────────────────────────────────────────
# MOTOR PRINCIPAL
# ─────────────────────────────────────────────────────────────

class ClinicalEngine:
    """
    Motor de calificación neuropsicológica.

    Orquesta el proceso completo:
        puntajes_brutos → ajuste_escolaridad → strategy → ResultadoPrueba

    Inyección de dependencias:
        loader:  BaremosLoader singleton con los baremos en memoria.
        factory: ScoringStrategyFactory (stateless, se puede mockear en tests).
    """

    def __init__(
        self,
        loader: BaremosLoader | None = None,
        factory: ScoringStrategyFactory | None = None,
    ):
        self._loader = loader or BaremosLoader.instance()
        self._factory = factory or ScoringStrategyFactory

    def score(
        self,
        paciente_id: str,
        puntajes: dict[str, Any],
        patient_context: PatientContext,
        protocolo: str | None = None,
    ) -> EngineResult:
        """
        Califica todos los puntajes del request.

        Args:
            paciente_id:     UUID del paciente (solo para el resultado).
            puntajes:        {test_id: puntaje_bruto}. Usar 9999 = no realizado.
            patient_context: Contexto demográfico del paciente.
            protocolo:       Nombre del protocolo clínico (metadata).

        Returns:
            EngineResult con todos los ResultadoPrueba.
        """
        resultado = EngineResult(
            paciente_id=paciente_id,
            protocolo=protocolo,
            poblacion=patient_context.poblacion,
            edad_display=patient_context.age.display,
        )

        for test_id, pd_raw in puntajes.items():
            r, warn = self._score_single(test_id, pd_raw, patient_context)
            if r is not None:
                resultado.resultados.append(r)
            if warn:
                resultado.advertencias.append(warn)

        logger.info(
            "Engine: %d pruebas calificadas para paciente %s (%d advertencias)",
            resultado.pruebas_realizadas, paciente_id, len(resultado.advertencias),
        )
        return resultado

    def score_single(
        self,
        test_id: str,
        pd: Any,
        patient_context: PatientContext,
    ) -> ResultadoPrueba | None:
        """Califica una sola prueba. Útil para el endpoint /preview."""
        resultado, _ = self._score_single(test_id, pd, patient_context)
        return resultado

    # ─── Internal ───────────────────────────────────────────

    def _score_single(
        self,
        test_id: str,
        pd_raw: Any,
        ctx: PatientContext,
    ) -> tuple[ResultadoPrueba | None, str | None]:
        """
        Califica una prueba y retorna (ResultadoPrueba, advertencia_opcional).
        """
        # 1. Validar que el test existe
        prueba = self._loader.get_prueba_optional(test_id)
        if prueba is None:
            if test_id in _NON_BAREMO_TESTS:
                logger.debug("Test '%s' omitido (screening/escala sin baremo).", test_id)
                return None, None
            warn = f"Test '{test_id}' no encontrado en BD_NEURO_MAESTRA.json."
            logger.warning(warn)
            return None, warn

        # 2. Normalizar PD
        try:
            pd = float(pd_raw) if pd_raw is not None else 9999.0
        except (ValueError, TypeError):
            warn = f"PD inválido para '{test_id}': {pd_raw!r}."
            return None, warn

        # 2b. Rechazar PD negativos (clínicamente inválidos)
        if pd < 0:
            warn = f"PD negativo para '{test_id}': {pd}. Los puntajes brutos no pueden ser negativos."
            logger.warning(warn)
            return None, warn

        # 3. Ajuste de escolaridad (Adulto Mayor)
        pd_ajustado = pd
        warn = None
        if ctx.poblacion == "adulto_mayor" and pd != 9999.0:
            ajuste = self._loader.get_ajuste_escolaridad(test_id, ctx.escolaridad)
            if ajuste != 0:
                pd_ajustado = pd + ajuste
                logger.debug("Ajuste escolaridad %s para %s: PD %s+%s=%s",
                             ctx.escolaridad, test_id, pd, ajuste, pd_ajustado)

        # 4. Seleccionar y ejecutar strategy
        try:
            strategy = self._factory.get(prueba.tipo_calculo)
            output = strategy.calculate(
                prueba,
                pd_ajustado,
                ctx.age.years,
                ctx.age.months,
                sexo=ctx.sexo,
                escolaridad=ctx.escolaridad,
            )
        except Exception as exc:
            warn = f"Error al calificar '{test_id}': {exc}"
            logger.exception(warn)
            return None, warn

        # 5. Agregar ajuste al metadata si hubo
        if pd_ajustado != pd:
            output.metadata["pd_original"] = pd
            output.metadata["pd_ajustado"] = pd_ajustado

        # 6. Detectar PD fuera del rango del baremo (hallazgo CLIN-1).
        # Cuando la strategy no pudo ubicar el PD en la tabla, el helper
        # `_not_found` marca out_of_baremo=True. Antes se devolvía
        # silenciosamente un resultado con escalar=None — ahora
        # propagamos una advertencia visible al profesional.
        if output.metadata.get("out_of_baremo"):
            warn = (
                f"'{prueba.nombre}' (PD={pd}): fuera del rango del baremo "
                f"para esta edad/llave — no se calificó."
            )

        # 6b. Fix: BD_NEURO_MAESTRA.json marca erroneamente `tipo_metrica="ci"`
        # para pruebas de Adulto Mayor (Neuronorma Colombia) cuyos valores
        # son ESCALARES 1-19, no CIs de 70-130.  Sin este override, un
        # escalar=13 en ViRDD aparecería como "Bajo" en lugar de "Superior".
        #
        # RESTRICCION IMPORTANTE: Solo aplica a estrategias `desconocido` y
        # `wais_range` (Neuronorma Colombia). Las escalas `clasificacion_fija`
        # (Yesavage GDS-15, MMSE, Lawton, GoNoGo, etc.) tienen puntajes
        # directos — NO son escalares 1-19 — y no deben recibir este override.
        # Ejemplo incorrecto sin restricción: Yesavage PD=9 (Depresión Moderada)
        # quedaría como "Promedio" en lugar de marcar deterioro.
        _NEURONORMA_CALCULO_TYPES = {"desconocido", "wais_range"}
        if (
            output.puntaje_escalar is not None
            and prueba.tipo_metrica == "ci"
            and ctx.poblacion == "adulto_mayor"
            and prueba.tipo_calculo in _NEURONORMA_CALCULO_TYPES
            and 1 <= output.puntaje_escalar <= 19
        ):
            output.tipo_metrica = "escalar"

        resultado = output.to_resultado(dominio_cognitivo=_get_domain(test_id))
        return resultado, warn
