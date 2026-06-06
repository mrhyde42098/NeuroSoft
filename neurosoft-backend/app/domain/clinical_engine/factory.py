"""
app/domain/clinical_engine/factory.py
======================================
Selector dinámico de strategies (Factory Pattern).

El Factory resuelve qué IScoringStrategy aplicar a partir del
`tipo_calculo` de la PruebaDefinicion, sin que el Engine necesite
saber nada de los algoritmos individuales.

Open/Closed Principle: agregar un nuevo tipo_calculo = una línea
en el diccionario _REGISTRY. El Engine no cambia.
"""

from __future__ import annotations

import logging

from app.core.exceptions import UnsupportedStrategyError
from app.domain.clinical_engine.strategies import (
    AjusteStroopStrategy,
    BaremoPEStrategy,
    ClasificacionFijaStrategy,
    ComparativoStrategy,
    DesconocidoStrategy,
    EdadSexoStrategy,
    EscolaridadPC50Strategy,
    IScoringStrategy,
    PuntajeDirectoATStrategy,
    PuntajeDirectoStrategy,
    PuntajeDoblResultadoStrategy,
    RangoPuntajeStrategy,
    SumaAIndiceStrategy,
    WaisRangeStrategy,
    ZScoreMultipleStrategy,
    ZScoreStrategy,
)

logger = logging.getLogger(__name__)


class ScoringStrategyFactory:
    """
    Fábrica de strategies de calificación.

    Instancia cada strategy UNA SOLA VEZ (flyweight) porque son
    stateless — no guardan información entre calificaciones.
    """

    # Registro: tipo_calculo → instancia de strategy (singleton por tipo)
    _REGISTRY: dict[str, IScoringStrategy] = {
        "rango_puntaje": RangoPuntajeStrategy(),
        "wais_range": WaisRangeStrategy(),
        "desconocido": DesconocidoStrategy(),
        "z_score": ZScoreStrategy(),
        "z_score_multiple": ZScoreMultipleStrategy(),
        "puntaje_directo_a_t": PuntajeDirectoATStrategy(),
        "puntaje_doble_resultado": PuntajeDoblResultadoStrategy(),
        "suma_a_indice": SumaAIndiceStrategy(),
        "escolaridad_pc50": EscolaridadPC50Strategy(),
        "puntaje": PuntajeDirectoStrategy(),
        "clasificacion_fija": ClasificacionFijaStrategy(),
        "edad_sexo": EdadSexoStrategy(),
        "ajuste": AjusteStroopStrategy(),
        "comparativo": ComparativoStrategy(),
        "baremo_pe": BaremoPEStrategy(),
    }

    # Fallback para tipos no registrados (evita que el motor explote)
    _FALLBACK: IScoringStrategy = RangoPuntajeStrategy()

    @classmethod
    def get(cls, tipo_calculo: str) -> IScoringStrategy:
        """
        Retorna la strategy para el tipo_calculo dado.

        Si el tipo no está registrado, usa RangoPuntajeStrategy como
        fallback y registra una advertencia (no lanza excepción) para
        que el motor continúe calificando las demás pruebas.
        """
        strategy = cls._REGISTRY.get(tipo_calculo)
        if strategy is None:
            logger.warning(
                "tipo_calculo='%s' no tiene strategy registrada. Usando RangoPuntajeStrategy como fallback.",
                tipo_calculo,
            )
            return cls._FALLBACK
        return strategy

    @classmethod
    def get_strict(cls, tipo_calculo: str) -> IScoringStrategy:
        """
        Versión estricta: lanza UnsupportedStrategyError si no existe.
        Usar en tests o cuando se necesita fallar explícitamente.
        """
        strategy = cls._REGISTRY.get(tipo_calculo)
        if strategy is None:
            raise UnsupportedStrategyError(tipo_calculo)
        return strategy

    @classmethod
    def registered_types(cls) -> list[str]:
        """Lista de todos los tipos_calculo registrados."""
        return list(cls._REGISTRY.keys())

    @classmethod
    def register(cls, tipo_calculo: str, strategy: IScoringStrategy) -> None:
        """
        Registra una strategy adicional en tiempo de ejecución.
        Útil para extensiones sin modificar este archivo.
        """
        cls._REGISTRY[tipo_calculo] = strategy
        logger.info("Strategy registrada para tipo_calculo='%s'", tipo_calculo)
