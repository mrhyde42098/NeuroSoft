"""
app/domain/clinical_engine/baremos_loader.py
=============================================
Singleton para la carga y acceso a BD_NEURO_MAESTRA.json.

El JSON se carga UNA SOLA VEZ al iniciar la aplicación y se mantiene
en memoria durante toda la vida del proceso. Lecturas en microsegundos.

Patrón Singleton implementado con clase de estado de clase (no metaclass).
Thread-safe para el contexto de FastAPI (asyncio single-thread).

OVERRIDES (F7.2)
----------------
Algunos tests tienen baremos heredados del Excel VBA original que no
son clasificaciones clínicas válidas (ej. AdBeck — keys `16190..16195`
son Cell IDs del Excel, no bandas depresivas). En lugar de modificar
el JSON (regla: el BD es intocable), este loader consulta
`app.domain.clinical_engine.overrides` ANTES de devolver un
`PruebaDefinicion`. Si hay override, se inyecta el baremo correcto.
El checksum del BD se preserva para trazabilidad clínica.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from app.core.exceptions import BaremoDatabaseNotLoadedError, BaremoNotFoundError
from app.domain.entities.models import PruebaDefinicion
from app.domain.clinical_engine import overrides as baremos_overrides

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
        self._stubs: dict[str, tuple[str, dict[str, Any] | None]] = {}  # test_id → (poblacion, raw|None)
        self._poblacion_index: dict[str, str] = {}
        self._ajustes_escolaridad: dict[str, dict[str, int]] = {}
        self._shard_dir: Path | None = None
        self._poblacion_cache: dict[str, dict[str, Any]] = {}
        # Trazabilidad clínica: versión y checksum del archivo cargado
        self._baremo_version: str = "unknown"
        self._baremo_checksum: str = ""
        self._baremo_path: Path | None = None
        # F7.2 — registro de overrides aplicados
        self._overrides_aplicados: set[str] = set()

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
        shards_dir = p.parent / "baremos_shards"
        if (shards_dir / "manifest.json").exists():
            instance._parse_sharded(shards_dir, p)
        else:
            instance._parse(p)

        cls._instance = instance
        cls._loaded = True

        logger.info(
            "BaremosLoader: %d pruebas indexadas (lazy) desde %s",
            len(instance._stubs), p.name,
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
        try:
            import orjson
            raw = orjson.loads(raw_bytes)
        except ImportError:
            try:
                raw = json.loads(raw_bytes.decode("utf-8"))
            except json.JSONDecodeError as exc:
                logger.exception("BD_NEURO_MAESTRA.json inválido en %s", path)
                raise BaremoDatabaseNotLoadedError(
                    f"JSON de baremos corrupto o ilegible: {exc}"
                ) from exc

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

                self._stubs[test_id] = (poblacion, test_data)
                self._poblacion_index[test_id] = poblacion

        if self._overrides_aplicados:
            logger.info(
                "BaremosLoader: overrides F7.2 se aplican al materializar cada prueba",
            )

    def _parse_sharded(self, shards_dir: Path, master_path: Path) -> None:
        """Carga índice ligero desde shards; datos de prueba bajo demanda por población."""
        manifest_path = shards_dir / "manifest.json"
        meta_path = shards_dir / "_meta.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self._meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.exception("Shards de baremos inválidos en %s", shards_dir)
            raise BaremoDatabaseNotLoadedError(
                f"Shards de baremos corruptos o ilegibles: {exc}"
            ) from exc

        self._shard_dir = shards_dir
        self._baremo_path = master_path if master_path.exists() else shards_dir
        self._baremo_checksum = str(manifest.get("checksum_master", ""))
        self._baremo_version = str(
            manifest.get("version")
            or self._meta.get("version")
            or self._meta.get("revision")
            or f"{shards_dir.name}-{self._baremo_checksum[:8]}"
        )
        self._ajustes_escolaridad = manifest.get("_ajustes_escolaridad", {})

        for poblacion, info in manifest.get("poblaciones", {}).items():
            for test_id in info.get("test_ids", []):
                self._stubs[test_id] = (poblacion, None)
                self._poblacion_index[test_id] = poblacion

        logger.info(
            "BaremosLoader: modo shards (%d pruebas indexadas, %d poblaciones)",
            len(self._stubs),
            len(manifest.get("poblaciones", {})),
        )

    def _load_poblacion_shard(self, poblacion: str) -> dict[str, Any]:
        if self._shard_dir is None:
            raise BaremoDatabaseNotLoadedError("(shards no configurados)")
        cached = self._poblacion_cache.get(poblacion)
        if cached is not None:
            return cached
        shard_file = self._shard_dir / f"{poblacion}.json"
        if not shard_file.exists():
            raise BaremoDatabaseNotLoadedError(f"Shard ausente: {shard_file.name}")
        raw_bytes = shard_file.read_bytes()
        try:
            import orjson
            loaded = orjson.loads(raw_bytes)
        except ImportError:
            loaded = json.loads(raw_bytes.decode("utf-8"))
        self._poblacion_cache[poblacion] = loaded
        return loaded

    def _resolve_stub_data(self, test_id: str, poblacion: str, test_data: dict[str, Any] | None) -> dict[str, Any]:
        if test_data is not None:
            return test_data
        poblacion_data = self._load_poblacion_shard(poblacion)
        resolved = poblacion_data.get(test_id)
        if resolved is None:
            raise BaremoNotFoundError(test_id)
        self._stubs[test_id] = (poblacion, resolved)
        return resolved

    def _materialize(self, test_id: str) -> PruebaDefinicion:
        """Construye PruebaDefinicion bajo demanda (lazy load por prueba)."""
        cached = self._index.get(test_id)
        if cached is not None:
            return cached
        stub = self._stubs.get(test_id)
        if stub is None:
            raise BaremoNotFoundError(test_id)
        poblacion, test_data = stub
        test_data = self._resolve_stub_data(test_id, poblacion, test_data)
        baremos_originales = test_data.get("baremos", {})
        baremos = baremos_originales
        if baremos_overrides.has_override(test_id):
            baremos_override = baremos_overrides.get_override(test_id)
            if baremos_override is not None:
                baremos = baremos_override
                self._overrides_aplicados.add(test_id)
        prueba = PruebaDefinicion(
            id=test_id,
            nombre=test_data.get("nombre", test_id),
            tipo_calculo=test_data.get("tipo_calculo", "rango_puntaje"),
            tipo_metrica=test_data.get("tipo_metrica", "escalar"),
            poblacion=poblacion,
            baremos=baremos,
        )
        self._index[test_id] = prueba
        return prueba

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
            return self._materialize(test_id)
        return prueba

    def get_prueba_optional(self, test_id: str) -> PruebaDefinicion | None:
        """Retorna None si no existe (no lanza excepción)."""
        if test_id not in self._stubs and test_id not in self._index:
            return None
        try:
            return self.get_prueba(test_id)
        except BaremoNotFoundError:
            return None

    def get_pruebas_por_poblacion(self, poblacion: str) -> dict[str, PruebaDefinicion]:
        return {
            tid: self._materialize(tid)
            for tid, pop in self._poblacion_index.items()
            if pop == poblacion
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
        return test_id in self._stubs or test_id in self._index

    @property
    def total_pruebas(self) -> int:
        return len(self._stubs)

    @property
    def all_test_ids(self) -> list[str]:
        return list(self._stubs.keys())

    # ── F7.2 introspection de overrides ────────────────────────
    def baremo_en_revision(self, test_id: str) -> bool:
        """
        Retorna True si el baremo del test está siendo corregido por un
        override Python (F7.2). Útil para que UI / informes / tests
        reporten que la clasificación actual proviene de un override
        validado contra literatura, no del dato crudo en el JSON.
        """
        return test_id in self._overrides_aplicados

    @property
    def overrides_aplicados(self) -> list[str]:
        """Lista de test_ids con override activo. Para diagnóstico / logs."""
        return sorted(self._overrides_aplicados)

    def get_pd_sanity_range(self, test_id: str) -> dict[str, Any]:
        """
        Rango heurístico min/max de PD brutos para validación en UI.

        No sustituye las reglas del motor; sirve como sanity check rápido.
        """
        prueba = self.get_prueba(test_id)
        baremos = prueba.baremos or {}
        pds: set[int] = set()
        for key in baremos:
            sk = str(key).strip()
            if not sk or sk.startswith("_"):
                continue
            if sk.isdigit():
                if len(sk) <= 3:
                    pds.add(int(sk))
                else:
                    for suffix_len in (3, 2, 1):
                        try:
                            suffix = int(sk[-suffix_len:])
                            if 0 <= suffix <= 200:
                                pds.add(suffix)
                        except ValueError:
                            continue
        if not pds:
            return {
                "test_id": test_id,
                "pd_min": None,
                "pd_max": None,
                "n_keys": len(baremos),
                "heuristic": True,
            }
        return {
            "test_id": test_id,
            "pd_min": min(pds),
            "pd_max": max(pds),
            "n_keys": len(baremos),
            "heuristic": True,
        }
