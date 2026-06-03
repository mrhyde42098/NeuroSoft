"""
tests/conftest.py
==================
Fixtures compartidas para toda la suite de tests.

- BD de baremos real (session-scoped, carga una sola vez)
- Engine clínico
- BD SQLite en memoria para tests de integración
- Contextos de pacientes representativos de cada población
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

# Path al proyecto
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

BAREMOS_PATH = ROOT / "data" / "BD_NEURO_MAESTRA.json"


# ─────────────────────────────────────────────────────────────
# BAREMOS + ENGINE (session-scoped — cargan una sola vez)
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def loader():
    from app.domain.clinical_engine.baremos_loader import BaremosLoader
    BaremosLoader.reset()
    if not BAREMOS_PATH.exists():
        pytest.skip("BD_NEURO_MAESTRA.json no encontrado en data/")
    return BaremosLoader.load(BAREMOS_PATH)


@pytest.fixture(scope="session")
def engine(loader):
    from app.domain.clinical_engine.engine import ClinicalEngine
    return ClinicalEngine(loader=loader)


# ─────────────────────────────────────────────────────────────
# BD EN MEMORIA para tests de integración
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def in_memory_db():
    """SQLite en memoria, esquema completo, aislado por test."""
    from sqlalchemy import create_engine as sa_engine
    from sqlalchemy.orm import sessionmaker

    from app.infrastructure.database.orm_models import Base

    engine_mem = sa_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine_mem)
    Session = sessionmaker(bind=engine_mem, autocommit=False, autoflush=True)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine_mem)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """
    S0.x: dos rate limiters in-memory persisten entre tests:
      - app.main._RL_BUCKETS (global, default 120/min)
      - app.presentation.api.v1.auth._LOGIN_ATTEMPTS (login, default 5/min)
    El de login rompe suites largas con multiples fixtures de login.
    Resetea ambos antes de cada test.
    """
    import importlib
    main_mod = importlib.import_module("app.main")
    auth_mod = importlib.import_module("app.presentation.api.v1.auth")
    with main_mod._RL_LOCK:
        main_mod._RL_BUCKETS.clear()
    auth_mod._LOGIN_ATTEMPTS.clear()
    yield


# ─────────────────────────────────────────────────────────────
# CONTEXTOS DE PACIENTE
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def ctx_infantil_10():
    """Niño 10 años exactos, Primaria Incompleta, Masculino."""
    from app.domain.clinical_engine.engine import PatientContext
    return PatientContext.from_demographics(
        birth_date=date(2016, 3, 20),
        evaluation_date=date(2026, 3, 20),
        sexo="H",
        escolaridad="Primaria Incompleta",
    )


@pytest.fixture
def ctx_infantil_7():
    """Niño 7 años 6 meses, Primaria Incompleta, Masculino."""
    from app.domain.clinical_engine.engine import PatientContext
    return PatientContext.from_demographics(
        birth_date=date(2018, 9, 20),
        evaluation_date=date(2026, 3, 20),
        sexo="H",
        escolaridad="Primaria Incompleta",
    )


@pytest.fixture
def ctx_infantil_16_11m():
    """Jesús Alejandro — 16a 11m, Secundaria Incompleta, M."""
    from app.domain.clinical_engine.engine import PatientContext
    return PatientContext.from_demographics(
        birth_date=date(2008, 5, 30),
        evaluation_date=date(2025, 5, 15),
        sexo="H",
        escolaridad="Secundaria Incompleta",
    )


@pytest.fixture
def ctx_adulto_28():
    """Adulto joven 28 años, Profesional, Masculino."""
    from app.domain.clinical_engine.engine import PatientContext
    return PatientContext.from_demographics(
        birth_date=date(1998, 1, 15),
        evaluation_date=date(2026, 3, 20),
        sexo="H",
        escolaridad="Profesional",
    )


@pytest.fixture
def ctx_adulto_mayor_80():
    """Blanca Edilma — 80a 5m, Primaria Incompleta, F."""
    from app.domain.clinical_engine.engine import PatientContext
    return PatientContext.from_demographics(
        birth_date=date(1945, 1, 1),
        evaluation_date=date(2025, 6, 3),
        sexo="M",
        escolaridad="Primaria Incompleta",
    )


@pytest.fixture
def ctx_adulto_mayor_65():
    """Adulto mayor 65 años, Analfabeta, Femenino."""
    from app.domain.clinical_engine.engine import PatientContext
    return PatientContext.from_demographics(
        birth_date=date(1961, 3, 20),
        evaluation_date=date(2026, 3, 20),
        sexo="M",
        escolaridad="Analfabeta",
    )
