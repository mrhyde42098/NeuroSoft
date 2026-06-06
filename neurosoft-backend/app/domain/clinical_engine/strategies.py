"""
app/domain/clinical_engine/strategies.py
=========================================
Las 15 estrategias de calificación del Motor NeuroSoft.

Strategy Pattern: cada clase encapsula UN algoritmo de calificación.
Todas implementan la misma interfaz `IScoringStrategy.calculate()`.

Mapa de cobertura (173 pruebas en BD_NEURO_MAESTRA.json, 114,586 claves):

  Subtests principales
    RangoPuntajeStrategy        → ~65 pruebas (WISC-IV, KABC, ENI-2, EAD)
    DesconocidoStrategy         → ~33 pruebas (Neuronorma Colombia AM)
    WaisRangeStrategy           → ~21 pruebas (WAIS-III subescalas)
    SumaAIndiceStrategy         → ~14 pruebas (WISC-IV y WAIS-III índices)
    ZScoreStrategy              →  ~7 pruebas (FCRO, TMT, CARAS)
    PuntajeDirectoATStrategy    →  ~6 pruebas (Spence, GADS)
    PuntajeDoblResultadoStrategy →  ~5 pruebas (GADS subescalas)
    EscolaridadPC50Strategy     →  ~5 pruebas (Dígitos, Claves adulto joven)
    PuntajeDirectoStrategy      →  ~2 pruebas (Vineland)
    ClasificacionFijaStrategy   →  ~6 pruebas (Beck BDI-II, Yesavage, MMSE,
                                                Lawton, GoNoGo, Refranes)
    EdadSexoStrategy            →  ~3 pruebas (CDI, GADS-CTAs)
    ZScoreMultipleStrategy      →  ~1 prueba  (CARAS-R)
    AjusteStroopStrategy        →  ~1 prueba  (Stroop corrección)
    ComparativoStrategy         →  ~1 prueba  (CVLT memoria)
    BaremoPEStrategy            →  ~1 prueba  (Torre de Londres)

Los conteos exactos se actualizan automáticamente con `baremos_loader._meta`;
los valores listados arriba son aproximados y reflejan el estado al cierre
de la auditoría v5 (mayo 2026). Para el inventario autoritativo ver
`baremos_loader.list_strategies_coverage()` o el header del JSON maestro.

§v5-auditoría (2026-06-05): el conteo histórico de 168 pruebas quedó
obsoleto tras la eliminación de los 10 tests Grober legacy en la
auditoría Excel→motor. La BD_NEURO_MAESTRA actual tiene 173 pruebas
con 114,586 claves de baremo (header del JSON también actualizado).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.utils import BaremoKeyBuilder, ClinicalInterpreter, EscolaridadMapper
from app.domain.entities.models import PruebaDefinicion, ResultadoPrueba

logger = logging.getLogger(__name__)

_NO_DATA = 9999.0  # Sentinel del VBA: "prueba no realizada"


# ============================================================
# RESULTADO INTERMEDIO (interno al motor)
# ============================================================


@dataclass
class ScoringOutput:
    """Salida interna de una strategy antes de convertirse en ResultadoPrueba."""

    test_id: str
    test_nombre: str
    tipo_metrica: str
    puntaje_bruto: float | None
    puntaje_escalar: float | None
    llave_usada: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    # Override opcional: si la strategy provee una interpretacion explicita
    # (p.ej. clasificacion_fija con codigos N/DL/DE/DS desde baremo JSON),
    # se usa en lugar del calculo via ClinicalInterpreter. Esto evita que
    # Yesavage PD=9 (Depresion Moderada) aparezca como "Promedio" por error.
    interpretacion_override: str | None = None

    @property
    def interpretacion(self) -> str:
        if self.interpretacion_override is not None:
            return self.interpretacion_override
        return ClinicalInterpreter.interpret(self.puntaje_escalar, self.tipo_metrica)

    @property
    def z_equivalente(self) -> float | None:
        return ClinicalInterpreter.to_z_equivalent(self.puntaje_escalar, self.tipo_metrica)

    def to_resultado(self, dominio_cognitivo: str) -> ResultadoPrueba:
        return ResultadoPrueba(
            test_id=self.test_id,
            test_nombre=self.test_nombre,
            puntaje_bruto=self.puntaje_bruto,
            puntaje_escalar=self.puntaje_escalar,
            tipo_metrica=self.tipo_metrica,
            interpretacion=self.interpretacion,
            z_equivalente=self.z_equivalente,
            dominio_cognitivo=dominio_cognitivo,
            llave_baremo_usada=self.llave_usada,
            metadata=self.metadata,
        )


def _sin_dato(prueba: PruebaDefinicion) -> ScoringOutput:
    return ScoringOutput(
        test_id=prueba.id,
        test_nombre=prueba.nombre,
        tipo_metrica=prueba.tipo_metrica,
        puntaje_bruto=None,
        puntaje_escalar=None,
    )


def _not_found(prueba: PruebaDefinicion, pd: float, llave: str) -> ScoringOutput:
    """
    Construye un ScoringOutput cuando el PD ofrecido no tiene entrada en el
    baremo (fuera de rango, llave de edad inexistente, etc).

    Marca `out_of_baremo=True` en `metadata` para que el engine pueda
    propagar una advertencia visible al profesional: un PD ingresado que
    no se puede calificar NO debe desaparecer silenciosamente — la GUI
    debe mostrarlo como advertencia explícita (ver hallazgo CLIN-1 del
    informe de auditoría).
    """
    logger.warning("Llave '%s' no en baremo de '%s' (PD=%s)", llave, prueba.id, pd)
    return ScoringOutput(
        test_id=prueba.id,
        test_nombre=prueba.nombre,
        tipo_metrica=prueba.tipo_metrica,
        puntaje_bruto=pd,
        puntaje_escalar=None,
        llave_usada=llave,
        metadata={
            "error": f"PD={pd} fuera del rango del baremo",
            "out_of_baremo": True,
            "pd_offered": pd,
            "llave_intentada": llave,
        },
    )


# ============================================================
# INTERFAZ BASE
# ============================================================


class IScoringStrategy(ABC):
    """
    Contrato que todas las strategies deben cumplir.

    Recibe una PruebaDefinicion + contexto del paciente y produce
    un ScoringOutput con el puntaje estandarizado.
    """

    @abstractmethod
    def calculate(
        self,
        prueba: PruebaDefinicion,
        puntaje_bruto: float,
        years: int,
        months: int,
        sexo: str = "H",
        escolaridad: str = "Profesional",
    ) -> ScoringOutput:
        """
        Args:
            prueba:        Definición de la prueba con sus baremos.
            puntaje_bruto: PD ingresado por el clínico (9999 = no realizada).
            years:         Años completos del paciente.
            months:        Meses adicionales (0-11).
            sexo:          "H" | "M" (para CDI y similares).
            escolaridad:   Nivel educativo (para escolaridad_pc50).
        """
        ...


# ============================================================
# STRATEGY 1: RANGO PUNTAJE (65 pruebas)
# WISC-IV subtests, KABC-II, ENI-2, EAD, Spence totales, etc.
# Llave: {año}{bracket_mes}{pd} o {año}{pd} o {total_meses}{pd}
# ============================================================


class RangoPuntajeStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        pd_int = int(pd)
        hit = BaremoKeyBuilder.find_in_baremo(prueba.baremos, years, months, pd_int)
        if hit:
            llave, valor = hit
            # Baremo puede ser escalar (int) o lista [P, C, PC] (Stroop)
            score = float(valor[0]) if isinstance(valor, (list, tuple)) else float(valor)
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica=prueba.tipo_metrica,
                puntaje_bruto=float(pd_int),
                puntaje_escalar=score,
                llave_usada=llave,
            )
        return _not_found(prueba, pd_int, f"<edad>{pd_int}")


# ============================================================
# STRATEGY 2: WAIS RANGE (19 pruebas)
# WAIS-III subescalas adulto joven. Llave: {rango_wais}{pd}
# Rangos: 1619 | 2024 | 2534 | 3554 | 5569 | 7000
# ============================================================


class WaisRangeStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        pd_int = int(pd)
        llave = BaremoKeyBuilder.wais_key(years, pd_int)
        if llave and llave in prueba.baremos:
            raw = prueba.baremos[llave]
            # Value may be a scalar or a list [edad, pd, score]
            score = float(raw[2]) if isinstance(raw, (list, tuple)) and len(raw) >= 3 else float(raw)
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica=prueba.tipo_metrica,
                puntaje_bruto=float(pd_int),
                puntaje_escalar=score,
                llave_usada=llave,
            )
        # Fallback: buscar con candidatos generales (incluye rango AM)
        hit = BaremoKeyBuilder.find_in_baremo(prueba.baremos, years, months, pd_int)
        if hit:
            k, v = hit
            score = float(v[2]) if isinstance(v, (list, tuple)) and len(v) >= 3 else float(v)
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica=prueba.tipo_metrica,
                puntaje_bruto=float(pd_int),
                puntaje_escalar=score,
                llave_usada=k,
            )
        return _not_found(prueba, pd_int, llave or "N/A")


# ============================================================
# STRATEGY 3: DESCONOCIDO (23 pruebas)
# Adulto mayor con rango etario. Valor: [rango, pd, score]
# Score = valor[2]
# ============================================================


class DesconocidoStrategy(IScoringStrategy):
    # Tests that use decade+escolaridad key instead of AM range key
    _DECADE_ESC_TESTS = {"ViMRemRec"}

    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        pd_int = int(pd)

        # ── Special case: tests keyed by decade+escolaridad (ViMRemRec) ──
        if prueba.id in self._DECADE_ESC_TESTS:
            k = BaremoKeyBuilder.mrem_key(years, escolaridad)
            if k and k in prueba.baremos:
                raw = prueba.baremos[k]
                # raw = [remota_pc50, reciente_pc50]
                score = float(raw[0]) if isinstance(raw, (list, tuple)) else float(raw)
                return ScoringOutput(
                    test_id=prueba.id,
                    test_nombre=prueba.nombre,
                    tipo_metrica=prueba.tipo_metrica,
                    puntaje_bruto=float(pd_int),
                    puntaje_escalar=score,
                    llave_usada=k,
                    metadata={
                        "remota": raw[0] if isinstance(raw, (list, tuple)) else raw,
                        "reciente": raw[1] if isinstance(raw, (list, tuple)) and len(raw) > 1 else None,
                    },
                )
            return _not_found(prueba, pd_int, k or "sin_clave_mrem")

        # Check if patient's age is within the baremo's covered range.
        # If not, return sin_norma instead of a wrong fallback value.
        in_range = BaremoKeyBuilder.patient_in_am_baremo_range(prueba.baremos, years)
        if not in_range:
            max_age = BaremoKeyBuilder.max_age_covered_by_am_baremo(prueba.baremos)
            logger.warning(
                "Test '%s': paciente %da fuera del rango del baremo (máx %da) — sin norma", prueba.id, years, max_age
            )
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica=prueba.tipo_metrica,
                puntaje_bruto=float(pd_int),
                puntaje_escalar=None,
                llave_usada=None,
                metadata={
                    "sin_norma": True,
                    "razon": f"Baremo cubre hasta {max_age} años; paciente tiene {years} años",
                },
            )

        # Use find_in_baremo which tries all candidates including 5056 fallback
        hit = BaremoKeyBuilder.find_in_baremo(prueba.baremos, years, months, pd_int)
        if hit:
            llave, raw = hit
            score = float(raw[2]) if isinstance(raw, list) and len(raw) >= 3 else float(raw)
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica=prueba.tipo_metrica,
                puntaje_bruto=float(pd_int),
                puntaje_escalar=score,
                llave_usada=llave,
                metadata={"raw_value": raw},
            )
        return _not_found(prueba, pd_int, f"<edad>{pd_int}")


# ============================================================
# STRATEGY 4: Z-SCORE (7 pruebas)
# baremo[str(años)] = [media, sigma] → Z = (pd - μ) / σ
# ============================================================


class ZScoreStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        llave = str(years)
        params = prueba.baremos.get(llave)
        if params is None or not isinstance(params, list) or len(params) < 2:
            return _not_found(prueba, pd, llave)
        mu, sigma = float(params[0]), float(params[1])
        # §H9-fix: si sigma=0 el Z-score es indefinido matemáticamente.
        # Antes se retornaba 0.0 (= "rendimiento promedio") lo cual era
        # un FALSO POSITIVO clínico. Ahora marcamos sin_norma para
        # que el clínico sepa que el baremo está corrupto.
        if sigma == 0:
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica="z_score",
                puntaje_bruto=float(pd),
                puntaje_escalar=None,
                llave_usada=llave,
                metadata={
                    "mu": mu,
                    "sigma": sigma,
                    "sin_norma": True,
                    "motivo": "sigma=0 en baremo (división indefinida)",
                },
            )
        z = round((pd - mu) / sigma, 2)
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica="z_score",
            puntaje_bruto=float(pd),
            puntaje_escalar=z,
            llave_usada=llave,
            metadata={"mu": mu, "sigma": sigma},
        )


# ============================================================
# STRATEGY 5: Z-SCORE MULTIPLE (1 prueba: CARAS-R)
# baremo[str(años)] = [mu1, s1, mu2, s2, ...] → Z del primer par
# ============================================================


class ZScoreMultipleStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        llave = str(years)
        params = prueba.baremos.get(llave)
        if params is None or len(params) < 2:
            return _not_found(prueba, pd, llave)
        mu, sigma = float(params[0]), float(params[1])
        if sigma == 0:
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica="z_score",
                puntaje_bruto=float(pd),
                puntaje_escalar=None,
                llave_usada=llave,
                metadata={
                    "mu": mu,
                    "sigma": sigma,
                    "sin_norma": True,
                    "motivo": "sigma=0 en baremo (division indefinida)",
                },
            )
        z = round((pd - mu) / sigma, 2)
        pares = {}
        labels = ["total", "errores", "corregido"]
        for i in range(0, min(len(params), 6), 2):
            lbl = labels[i // 2] if i // 2 < len(labels) else f"sub{i // 2}"
            if len(params) > i + 1:
                pares[lbl] = {"mu": params[i], "sigma": params[i + 1]}
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica="z_score",
            puntaje_bruto=float(pd),
            puntaje_escalar=z,
            llave_usada=llave,
            metadata={"pares_z": pares},
        )


# ============================================================
# STRATEGY 6: PUNTAJE DIRECTO A T (6 pruebas)
# baremo[str(pd)] = T_score  (sin necesitar edad)
# ============================================================


class PuntajeDirectoATStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        llave = str(int(pd))
        valor = prueba.baremos.get(llave)
        if valor is None:
            return _not_found(prueba, pd, llave)
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica=prueba.tipo_metrica,
            puntaje_bruto=float(int(pd)),
            puntaje_escalar=float(valor),
            llave_usada=llave,
        )


# ============================================================
# STRATEGY 7: PUNTAJE DOBLE RESULTADO (5 pruebas: GADS)
# baremo[str(pd)] = {"PE": t_score, "Percentil": pc}
# ============================================================


class PuntajeDoblResultadoStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        llave = str(int(pd))
        valor = prueba.baremos.get(llave)
        if valor is None:
            return _not_found(prueba, pd, llave)
        # Baremo puede ser:
        #   • lista [PE, Percentil]          (NiGadsIS / PRC / PatCog / HP)
        #   • dict {"PE": x, "Percentil": y} (algunos GADS)
        #   • dict {"CTAS": x, "Percentil": y}  (NiGADSCTAs) ← §N3-fix mayo 2026
        #   • dict {"T": x, "Percentil": y}     (variantes futuras)
        if isinstance(valor, (list, tuple)):
            pe = float(valor[0]) if valor else 0.0
            percentil = valor[1] if len(valor) > 1 else pe
        else:
            # §N3-fix: buscar primero por claves conocidas; si no, primer numérico
            # que NO sea "Percentil". Antes solo buscaba "PE" → devolvía 0 para
            # NiGADSCTAs (que usa clave "CTAS").
            for candidate_key in ("PE", "CTAS", "T", "T_score", "Score"):
                if candidate_key in valor:
                    pe = float(valor[candidate_key])
                    break
            else:
                # Último recurso: tomar el primer valor numérico que no sea Percentil
                numeric_vals = [float(v) for k, v in valor.items() if k != "Percentil" and isinstance(v, (int, float))]
                if not numeric_vals:
                    return _not_found(prueba, pd, llave)
                pe = numeric_vals[0]
            percentil = valor.get("Percentil")
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica=prueba.tipo_metrica,
            puntaje_bruto=float(int(pd)),
            puntaje_escalar=pe,
            llave_usada=llave,
            metadata={"percentil": percentil},
        )


# ============================================================
# STRATEGY 8: SUMA A ÍNDICE (14 pruebas: WISC-IV índices CI)
# baremo[str(suma_escalares)] = CI_compuesto
# ============================================================


class SumaAIndiceStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        llave = str(int(pd))
        valor = prueba.baremos.get(llave)
        if valor is None:
            return _not_found(prueba, pd, llave)
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica="ci",
            puntaje_bruto=float(int(pd)),
            puntaje_escalar=float(valor),
            llave_usada=llave,
        )


# ============================================================
# STRATEGY 9: ESCOLARIDAD PC50 (4 pruebas: Dígitos adulto joven)
# baremo["{años}{cod_esc}"] = [edad, cod, pc50]
# ============================================================


class EscolaridadPC50Strategy(IScoringStrategy):
    # Tests Vi (Neuronorma Colombia AM) usan P/S/U, no B/S/T/U/P
    _NEURONORMA_AM_TESTS = {"ViDeno", "ViSem", "AdDPros", "AdDReg"}

    def calculate(self, prueba, pd, years=0, months=0, escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)

        # Elegir convención de escolaridad según el instrumento
        if prueba.id in self._NEURONORMA_AM_TESTS:
            cod = EscolaridadMapper.to_neuronorma_am(escolaridad)
        else:
            cod = EscolaridadMapper.to_code(escolaridad)

        llave = BaremoKeyBuilder.escolaridad_key(years, cod)
        params = prueba.baremos.get(llave)
        if params is None:
            return _not_found(prueba, pd, llave)
        pc50 = float(params[2]) if isinstance(params, list) and len(params) >= 3 else float(params)
        diff = float(pd) - pc50
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica=prueba.tipo_metrica,
            puntaje_bruto=float(pd),
            puntaje_escalar=float(pd),
            llave_usada=llave,
            metadata={"pc50": pc50, "diferencia_vs_norma": round(diff, 2)},
        )


# ============================================================
# STRATEGY 10: PUNTAJE DIRECTO (2 pruebas: Vineland)
# baremo[str(pd)] = [coeficiente]
# ============================================================


class PuntajeDirectoStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        llave = str(int(pd))
        valor = prueba.baremos.get(llave)
        if valor is None:
            return _not_found(prueba, pd, llave)
        pe = float(valor[0]) if isinstance(valor, list) else float(valor)
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica=prueba.tipo_metrica,
            puntaje_bruto=float(int(pd)),
            puntaje_escalar=pe,
            llave_usada=llave,
        )


# ============================================================
# STRATEGY 11: EDAD-SEXO (1 prueba: CDI depresión infantil)
# baremo["{rango_edad}{sexo}"] = [sexo, rango, media, sigma]
# Rangos CDI: 78 (7-8a), 910 (9-10a), 1115 (11-15a)
# ============================================================


class EdadSexoStrategy(IScoringStrategy):
    _CDI_RANGES = [(7, 8, "78"), (9, 10, "910"), (11, 15, "1115")]

    def calculate(self, prueba, pd, years=0, months=0, sexo="H", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        rango = next((c for mn, mx, c in self._CDI_RANGES if mn <= years <= mx), None)
        if rango is None:
            return _not_found(prueba, pd, f"edad_{years}_sin_rango")
        llave = f"{rango}{sexo}"
        params = prueba.baremos.get(llave)
        if params is None or not isinstance(params, list) or len(params) < 4:
            return _not_found(prueba, pd, llave)
        mu, sigma = float(params[2]), float(params[3])
        if sigma == 0:
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica="z_score",
                puntaje_bruto=float(pd),
                puntaje_escalar=None,
                llave_usada=llave,
                metadata={
                    "mu": mu,
                    "sigma": sigma,
                    "sin_norma": True,
                    "motivo": "sigma=0 en baremo (division indefinida)",
                },
            )
        z = round((float(pd) - mu) / sigma, 2)
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica="z_score",
            puntaje_bruto=float(pd),
            puntaje_escalar=z,
            llave_usada=llave,
            metadata={"mu": mu, "sigma": sigma, "sexo": sexo},
        )


# ============================================================
# STRATEGY 12: CLASIFICACIÓN FIJA (12 pruebas)
# Escalas clinicas con rangos categoricos en lugar de escalares.
#
# Comportamiento:
#   1. Si el baremo del JSON tiene baremo[str(pd)] con un codigo
#      categorico (N / DL / DE / DS), se usa esa clasificacion.
#      Aplica a: Yesavage GDS-15, MMSE, EscLawton, EscKertesz,
#      EscQueja, GoNoGoICO, InstrConflICO, InstrConfiICO, RefranesICO.
#   2. Si el baremo NO tiene esa entrada (Beck BDI-II), se usan los
#      rangos clinicos hardcoded de Beck (estandar internacional).
#
# Esto corrige el bug clinicamente peligroso anterior donde Yesavage
# PD=9 (Depresion Moderada) aparecia como "Promedio" por usar rangos
# Beck para TODAS las escalas.
# ============================================================


class ClasificacionFijaStrategy(IScoringStrategy):
    # Mapa de codigos categoricos del baremo JSON -> interpretacion clinica
    # N  = Normal           (sin alteracion)
    # DL = Deficit Leve     (alteracion ligera, vigilancia)
    # DE = Deficit Extremo  (alteracion marcada, intervencion)
    # DS = Deficit Severo   (alteracion grave, manejo prioritario)
    _CODIGO_A_INTERPRETACION = {
        "N": "Normal",
        "DL": "Deficit Leve",
        "DE": "Deficit Extremo",
        "DS": "Deficit Severo",
    }
    # Mapa de codigos -> nivel ClinicalInterpreter (Promedio/Limitrofe/Bajo)
    # para que el frontend pueda colorear consistentemente.
    _CODIGO_A_NIVEL = {
        "N": "Promedio",
        "DL": "Limítrofe",
        "DE": "Bajo",
        "DS": "Bajo",
    }

    # Fallback Beck BDI-II (estandar internacional 0-63 -> 4 niveles)
    _BECK_RANGES = [
        (0, 13, "Mínima"),
        (14, 19, "Leve"),
        (20, 28, "Moderada"),
        (29, 63, "Severa"),
    ]
    _BECK_A_NIVEL = {
        "Mínima": "Promedio",
        "Leve": "Limítrofe",
        "Moderada": "Bajo",
        "Severa": "Bajo",
    }

    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        pd_int = int(pd)

        # Intento 1: lookup directo en baremo JSON con codigo categorico
        valor_baremo = prueba.baremos.get(str(pd_int))
        if isinstance(valor_baremo, str) and valor_baremo in self._CODIGO_A_INTERPRETACION:
            codigo = valor_baremo
            interp_clinica = self._CODIGO_A_INTERPRETACION[codigo]
            nivel = self._CODIGO_A_NIVEL[codigo]
            return ScoringOutput(
                test_id=prueba.id,
                test_nombre=prueba.nombre,
                tipo_metrica=prueba.tipo_metrica,
                puntaje_bruto=float(pd_int),
                puntaje_escalar=float(pd_int),
                llave_usada=str(pd_int),
                metadata={
                    "clasificacion_codigo": codigo,
                    "clasificacion_clinica": interp_clinica,
                    "nivel_interpretacion": nivel,
                },
                # Override: la interpretacion mostrada al clinico es la
                # categoria clinica especifica (no "Bajo" generico).
                interpretacion_override=interp_clinica,
            )

        # Intento 2: fallback Beck (cuando baremo no tiene codigo categorico)
        cls_beck = next(
            (lbl for mn, mx, lbl in self._BECK_RANGES if mn <= pd_int <= mx),
            "Sin clasificación",
        )
        nivel_beck = self._BECK_A_NIVEL.get(cls_beck, "Promedio")
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica=prueba.tipo_metrica,
            puntaje_bruto=float(pd_int),
            puntaje_escalar=float(pd_int),
            llave_usada="rango_beck",
            metadata={
                "clasificacion_beck": cls_beck,
                "nivel_interpretacion": nivel_beck,
            },
            interpretacion_override=cls_beck if cls_beck != "Sin clasificación" else None,
        )


# ============================================================
# STRATEGY 13: AJUSTE STROOP (1 prueba)
# baremo[str(pd)] = [score_P, score_C, score_PC]
# ============================================================


class AjusteStroopStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        llave = str(int(pd))
        valor = prueba.baremos.get(llave)
        if valor is None:
            return _not_found(prueba, pd, llave)
        if isinstance(valor, list) and len(valor) >= 3:
            sp, sc, spc = float(valor[0]), float(valor[1]), float(valor[2])
        else:
            sp, sc, spc = float(valor), None, None
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica=prueba.tipo_metrica,
            puntaje_bruto=float(int(pd)),
            puntaje_escalar=sp,
            llave_usada=llave,
            metadata={"stroop_P": sp, "stroop_C": sc, "stroop_PC": spc},
        )


# ============================================================
# STRATEGY 14: COMPARATIVO (1 prueba: CVLT)
# baremo con claves semánticas (E1, E2, MCP, MLP...) → máximos
# ============================================================


class ComparativoStrategy(IScoringStrategy):
    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        max_lista = sum(
            float(prueba.baremos.get(f"E{i}", [0])[0])
            for i in range(1, 6)
            if isinstance(prueba.baremos.get(f"E{i}", [0]), list)
        )
        if max_lista <= 0:
            return _not_found(prueba, pd, "total_lista")
        z = round(((float(pd) / max_lista) - 0.5) / 0.15, 2)
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica=prueba.tipo_metrica,
            puntaje_bruto=float(pd),
            puntaje_escalar=z,
            llave_usada="total_lista",
            metadata={"max_esperado": max_lista},
        )


# ============================================================
# STRATEGY 15: BAREMO PE (1 prueba: Torre de Londres)
# baremo[str(pd)] = [pe_col1, pd2, pe_col2, pd3, pe_col3, ...]
# ============================================================


class BaremoPEStrategy(IScoringStrategy):
    _COLS = ["total_correctos_pe", "mov_pd", "mov_pe", "lat_pd", "lat_pe", "eje_pd", "eje_pe", "res_pd", "res_pe"]

    def calculate(self, prueba, pd, years=0, months=0, sexo="H", escolaridad="Profesional", **_) -> ScoringOutput:
        if pd == _NO_DATA or pd is None:
            return _sin_dato(prueba)
        llave = str(int(pd))
        valor = prueba.baremos.get(llave)
        if valor is None or not isinstance(valor, list) or len(valor) == 0:
            return _not_found(prueba, pd, llave)
        pe = float(valor[0])
        meta = {col: valor[i] for i, col in enumerate(self._COLS) if i < len(valor)}
        return ScoringOutput(
            test_id=prueba.id,
            test_nombre=prueba.nombre,
            tipo_metrica=prueba.tipo_metrica,
            puntaje_bruto=float(int(pd)),
            puntaje_escalar=pe,
            llave_usada=llave,
            metadata=meta,
        )
