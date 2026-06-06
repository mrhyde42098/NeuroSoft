"""
S4.2: Tests del módulo de métricas (opt-in).
"""

import pytest

from app.infrastructure.observability import metrics


@pytest.fixture(autouse=True)
def reset_metrics():
    metrics.reset()
    yield
    metrics.reset()


def test_metrics_disabled_por_default():
    """Sin env var, todas las funciones son no-op."""
    assert metrics._is_enabled() is False
    metrics.counter_inc("test_x")
    metrics.histogram_observe("test_y", 10.0)
    metrics.gauge_set("test_z", 1.0)
    snap = metrics.snapshot()
    assert snap == {"enabled": False}


def test_metrics_habilitado_con_env(monkeypatch):
    monkeypatch.setenv("NEUROSOFT_METRICS_ENABLED", "1")
    # Reimport para que tome el env (módulo es global, pero `_is_enabled`
    # se evalúa en cada call, así que basta con el env)
    assert metrics._is_enabled() is True
    metrics.counter_inc("requests_total")
    metrics.counter_inc("requests_total", n=3)
    snap = metrics.snapshot()
    assert snap["enabled"] is True
    assert snap["counters"]["requests_total"] == 4


def test_histograma_snapshot_correcto(monkeypatch):
    monkeypatch.setenv("NEUROSOFT_METRICS_ENABLED", "1")
    metrics.histogram_observe("latency_ms", 10.0)
    metrics.histogram_observe("latency_ms", 20.0)
    metrics.histogram_observe("latency_ms", 30.0)
    snap = metrics.snapshot()
    h = snap["histograms"]["latency_ms"]
    assert h["count"] == 3
    assert h["sum"] == 60.0
    assert h["avg"] == 20.0
    assert h["min"] == 10.0
    assert h["max"] == 30.0


def test_gauge_set_sobrescribe(monkeypatch):
    monkeypatch.setenv("NEUROSOFT_METRICS_ENABLED", "1")
    metrics.gauge_set("active", 5.0)
    metrics.gauge_set("active", 7.0)
    assert metrics.snapshot()["gauges"]["active"] == 7.0


def test_timed_context_manager(monkeypatch):
    monkeypatch.setenv("NEUROSOFT_METRICS_ENABLED", "1")
    with metrics.timed("op_x"):
        sum(range(1000))
    snap = metrics.snapshot()
    assert snap["histograms"]["op_x"]["count"] == 1
    assert snap["histograms"]["op_x"]["sum"] > 0


def test_flush_sin_dsn_no_envia(monkeypatch):
    monkeypatch.setenv("NEUROSOFT_METRICS_ENABLED", "1")
    monkeypatch.setenv("NEUROSOFT_METRICS_DSN", "")
    assert metrics.flush_to_dsn() is False


def test_reset_limpia_estado(monkeypatch):
    monkeypatch.setenv("NEUROSOFT_METRICS_ENABLED", "1")
    metrics.counter_inc("c1")
    metrics.histogram_observe("h1", 1.0)
    metrics.gauge_set("g1", 1.0)
    metrics.reset()
    snap = metrics.snapshot()
    assert snap["counters"] == {}
    assert snap["histograms"] == {}
    assert snap["gauges"] == {}


def test_counter_thread_safe(monkeypatch):
    """Múltiples hilos incrementando el mismo counter."""
    import threading

    monkeypatch.setenv("NEUROSOFT_METRICS_ENABLED", "1")
    n = 100
    barrier = threading.Barrier(10)

    def worker():
        barrier.wait()
        for _ in range(n):
            metrics.counter_inc("shared")

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert metrics.snapshot()["counters"]["shared"] == 10 * n
