"""
app/domain/clinical_engine/baremos_loader.py
=============================================
Singleton para la carga y acceso a BD_NEURO_MAESTRA.json.

El JSON se carga UNA SOLA VEZ al iniciar la aplicación y se mantiene
en memoria durante toda la vida del proceso. Lecturas en microsegundos.

Patrón Singleton implementado con clase de estado de clase (no metaclass).
Thread-safe para el contexto de FastAPI (asyncio single-thread).
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from app.core.exceptions import BaremoDatabaseNotLoadedError, BaremoNotFoundError
from app.domain.entities.models import PruebaDefinicion

logger = logging.getLogger(__name__)


class BaremosLoader:
    """
    Repositorio en memoria de datos normativos.

    Responsabilidades:
        1. Cargar BD_NEURO_MAESTRA.json en el startup.
        2. Construir un índice plano {test_id → PruebaDefinicion} en O(1).
        3. Exponer la tabla de ajustes de escolaridad para adulto mayor.
        4. Exponer el nodo _meta con reglas de corte clínico.

    Uso:
        # En el lifespan de FastAPI:
        BaremosLoader.load(path)

        # En cualquier servicio:
        loader = BaremosLoader.instance()
        prueba = loader.get_prueba("NiWiscDC")
    """

    _instance: BaremosLoader | None = None
    _loaded: bool = False

    def __init__(self):
        self._meta: dict[str, Any] = {}
        self._index: dict[str, PruebaDefinicion] = {}
        self._poblacion_index: dict[str, str] = {}
        self._ajustes_escolaridad: dict[str, dict[str, int]] = {}
        # Trazabilidad clínica: versión y checksum del archivo cargado
        self._baremo_version: str = "unknown"
        self._baremo_checksum: str = ""
        self._baremo_path: Path | None = None

    # ──────────────────────────────────────────────────────────
    # Ciclo de vida del Singleton
    # ──────────────────────────────────────────────────────────

    @classmethod
    def load(cls, path: str | Path) -> BaremosLoader:
        """
        Carga el JSON y retorna la instancia Singleton.
        Llamar UNA SOLA VEZ en el lifespan de FastAPI.

        Raises:
            BaremoDatabaseNotLoadedError: Si el archivo no existe.
        """
        p = Path(path)
        if not p.exists():
            raise BaremoDatabaseNotLoadedError(str(p))

        instance = cls()
        instance._parse(p)

        cls._instance = instance
        cls._loaded = True

        logger.info(
            "BaremosLoader: %d pruebas cargadas desde %s",
            len(instance._index), p.name,
        )
        return instance

    @classmethod
    def instance(cls) -> BaremosLoader:
        """
        Retorna la instancia Singleton.

        Raises:
            BaremoDatabaseNotLoadedError: Si load() no fue llamado.
        """
        if not cls._loaded or cls._instance is None:
            raise BaremoDatabaseNotLoadedError("(no cargado)")
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reinicia el Singleton. Útil para tests."""
        cls._instance = None
        cls._loaded = False

    # ──────────────────────────────────────────────────────────
    # Parsing interno
    # ──────────────────────────────────────────────────────────

    def _parse(self, path: Path) -> None:
        raw_bytes = path.read_bytes()
        raw = json.loads(raw_bytes.decode("utf-8"))

        self._meta = raw.get("_meta", {})
        baterias = raw.get("baterias", {})

        # Versionado / checksum (clínicamente crítico: si se re-baremiza,
        # los informes generados con baremos antiguos deben poder re-ejecutarse
        # o marcarse explícitamente).
        self._baremo_path = path
        self._baremo_checksum = hashlib.sha256(raw_bytes).hexdigest()
        self._baremo_version = str(
            self._meta.get("version")
            or self._meta.get("revision")
            or f"{path.stem}-{self._baremo_checksum[:8]}"
        )

        for poblacion, tests in baterias.items():
            for test_id, test_data in tests.items():
                if test_id == "_ajustes_escolaridad":
                    # Normalizar: {nivel_escolaridad: {test_id: ajuste}}
                    self._ajustes_escolaridad = test_data
                    continue

                prueba = PruebaDefinicion(
                    id=test_id,
                    nombre=test_data.get("nombre", test_id),
                    tipo_calculo=test_data.get("tipo_calculo", "rango_puntaje"),
                    tipo_metrica=test_data.get("tipo_metrica", "escalar"),
                    poblacion=poblacion,
                    baremos=test_data.get("baremos", {}),
                )
                self._index[test_id] = prueba
                self._poblacion_index[test_id] = poblacion

    # ──────────────────────────────────────────────────────────
    # Acceso público
    # ──────────────────────────────────────────────────────────

    def get_prueba(self, test_id: str) -> PruebaDefinicion:
        """
        Retorna la definición de una prueba.
        Raises BaremoNotFoundError si no existe.
        """
        prueba = self._index.get(test_id)
        if prueba is None:
            raise BaremoNotFoundError(test_id)
        return prueba

    def get_prueba_optional(self, test_id: str) -> PruebaDefinicion | None:
        """Retorna None si no existe (no lanza excepción)."""
        return self._index.get(test_id)

    def get_pruebas_por_poblacion(self, poblacion: str) -> dict[str, PruebaDefinicion]:
        return {
            tid: p for tid, p in self._index.items()
            if self._poblacion_index.get(tid) == poblacion
        }

    def get_poblacion_de_prueba(self, test_id: str) -> str | None:
        return self._poblacion_index.get(test_id)

    # ── Versión del baremo cargado ────────────────────────────
    @property
    def baremo_version(self) -> str:
        """Cadena mostrada en informes y almacenada en EvaluationORM.baremo_version."""
        return self._baremo_version

    @property
    def baremo_checksum(self) -> str:
        """SHA-256 del archivo para auditoría."""
        return self._baremo_checksum

    def get_ajuste_escolaridad(self, test_id: str, nivel_escolaridad: str) -> int:
        """
        Retorna el ajuste de puntaje bruto para adulto mayor según escolaridad.
        Retorna 0 si no hay ajuste para esa combinación.
        """
        return self._ajustes_escolaridad.get(nivel_escolaridad, {}).get(test_id, 0)

    def get_meta(self) -> dict[str, Any]:
        return self._meta

    def exists(self, test_id: str) -> bool:
        return test_id in self._index

    @property
    def total_pruebas(self) -> int:
        return len(self._index)

    @property
    def all_test_ids(self) -> list[str]:
        return list(self._index.keys())
