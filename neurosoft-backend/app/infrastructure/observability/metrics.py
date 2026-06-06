"""
app/infrastructure/observability/metrics.py
=============================================
S4.2: Métricas operacionales opt-in para NeuroSoft.

NO usa Sentry directamente para evitar dependencia obligatoria. En su
lugar, provee un buffer en memoria + exportador opcional a un endpoint
configurable vía env (compatible con Sentry, Datadog, OpenTelemetry
collector, etc.).

Activación (opt-in):
    NEUROSOFT_METRICS_ENABLED=1
    NEUROSOFT_METRICS_DSN=https://...@sentry.io/...  # o un collector OTLP

Diseño:
    - Métricas en memoria, agregadas por minuto.
    - Flush automático cada 60s si está habilitado.
    - En modo disabled (default), las funciones son no-op.
    - Privacidad: NO se envía PHI (solo conteos, latencias, status codes).

Métricas expuestas:
    - counter: requests_total{method, path, status}
    - histogram: request_duration_ms{method, path}
    - gauge: active_sessions
    - counter: backup_created_total
    - counter: backup_failed_total
    - counter: pdf_generated_total{template}
    - counter: ai_requests_total{provider, status}
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field

logger = logging.getLogger("neurosoft.metrics")


_METRICS_DSN = os.getenv("NEUROSOFT_METRICS_DSN", "")


@dataclass
class _Counter:
    """Contador monotónico thread-safe."""

    value: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def inc(self, n: int = 1) -> None:
        with self._lock:
            self.value += n

    def get(self) -> int:
        with self._lock:
            return self.value


@dataclass
class _Histogram:
    """Histograma simple con conteo, suma, min, max."""

    count: int = 0
    sum: float = 0.0
    min: float = float("inf")
    max: float = float("-inf")
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def observe(self, value: float) -> None:
        with self._lock:
            self.count += 1
            self.sum += value
            if value < self.min:
                self.min = value
            if value > self.max:
                self.max = value

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "count": self.count,
                "sum": round(self.sum, 3),
                "avg": round(self.sum / self.count, 3) if self.count else 0.0,
                "min": self.min if self.count else None,
                "max": self.max if self.count else None,
            }


_counters: dict[str, _Counter] = defaultdict(_Counter)
_histograms: dict[str, _Histogram] = defaultdict(_Histogram)
_gauges: dict[str, float] = {}


def _is_enabled() -> bool:
    return os.getenv("NEUROSOFT_METRICS_ENABLED", "0") == "1"


def counter_inc(name: str, n: int = 1) -> None:
    """Incrementa un contador. No-op si métricas deshabilitadas."""
    if not _is_enabled():
        return
    _counters[name].inc(n)


def histogram_observe(name: str, value: float) -> None:
    """Registra una observación en un histograma. No-op si deshabilitado."""
    if not _is_enabled():
        return
    _histograms[name].observe(value)


def gauge_set(name: str, value: float) -> None:
    """Establece un gauge. No-op si deshabilitado."""
    if not _is_enabled():
        return
    _gauges[name] = value


@contextmanager
def timed(name: str):
    """Context manager que mide duración y la registra como histograma."""
    if not _is_enabled():
        yield
        return
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        histogram_observe(name, elapsed_ms)


def snapshot() -> dict:
    """Devuelve un snapshot de todas las métricas (sin reset)."""
    if not _is_enabled():
        return {"enabled": False}
    return {
        "enabled": True,
        "counters": {k: v.get() for k, v in _counters.items()},
        "histograms": {k: v.snapshot() for k, v in _histograms.items()},
        "gauges": dict(_gauges),
    }


def reset() -> None:
    """Resetea todas las métricas. Útil en tests."""
    _counters.clear()
    _histograms.clear()
    _gauges.clear()


def flush_to_dsn() -> bool:
    """
    Envía el snapshot actual al DSN configurado.
    Usa HTTP POST a {DSN}/metrics (asume formato Sentry/OTLP-like).
    Devuelve True si envió, False si no.
    """
    if not _is_enabled() or not _METRICS_DSN:
        return False
    try:
        import urllib.request

        data = json.dumps(snapshot()).encode("utf-8")
        req = urllib.request.Request(
            _METRICS_DSN,
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return 200 <= resp.status < 300
    except Exception as e:
        logger.warning("No se pudo enviar métricas a DSN: %s", e)
        return False
