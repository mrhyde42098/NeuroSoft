"""
app/infrastructure/database/engine.py
======================================
Configuración del motor SQLAlchemy y gestión de sesiones.

Usa SQLite para máxima portabilidad y privacidad offline.
El archivo .db vive en data/neurosoft.db (configurable via settings).

Patrón Session-per-request: FastAPI crea una sesión por request y
la cierra automáticamente al final, con rollback si hay error.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Base declarativa (todas las ORM hereden de aquí)
# ─────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM."""
    pass


# ─────────────────────────────────────────────────────────────
# Motor y fábrica de sesiones
# ─────────────────────────────────────────────────────────────

def _create_engine():
    """Crea el motor SQLAlchemy con configuración optimizada para SQLite."""
    engine = create_engine(
        settings.sqlalchemy_url,
        connect_args={"check_same_thread": False},  # Necesario para FastAPI async
        echo=settings.is_development,               # SQL logging en dev
        pool_pre_ping=True,                         # Detecta conexiones muertas
    )

    # Habilitar WAL mode y foreign keys en cada nueva conexión SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    return engine


_engine = _create_engine()
SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


# ─────────────────────────────────────────────────────────────
# Ciclo de vida
# ─────────────────────────────────────────────────────────────

def init_database() -> None:
    """
    Crea todas las tablas si no existen.
    Llamar UNA VEZ en el lifespan de FastAPI.
    Idempotente: no destruye datos existentes.
    """
    # Importar modelos para que estén registrados en Base.metadata
    from app.infrastructure.database import orm_models  # noqa: F401

    settings.db_path.parent.mkdir(parents=True, exist_ok=True)

    # §rollback: snapshot pre-migracion. Si la BD ya existe y tiene datos,
    # hacemos una copia de seguridad antes de cualquier alteracion de schema.
    # Asi, si una migracion corrompe datos, el clinico puede restaurar.
    _snapshot_pre_migracion(settings.db_path)

    Base.metadata.create_all(bind=_engine)
    # Auto-upgrade ligero: sincroniza columnas nuevas en BDs existentes
    # sin obligar al operador a correr Alembic manualmente. Solo añade
    # columnas — nunca altera tipos, nunca elimina.
    _apply_additive_schema_patches()
    # FTS5: índice full-text para búsqueda rápida de pacientes
    _init_fts5_index()
    logger.info("Base de datos inicializada: %s", settings.db_path)


def _snapshot_pre_migracion(db_path):
    """
    Crea una copia de la BD antes de aplicar migraciones automaticas.

    Solo se ejecuta si el archivo ya existe (no en primer arranque).
    Mantiene maximo 10 snapshots, eliminando los mas antiguos.
    """
    import shutil
    from datetime import datetime

    if not db_path.exists():
        return

    # Solo snapshot si la BD tiene contenido real (>10 KB)
    size = db_path.stat().st_size
    if size < 10240:
        return

    snap_dir = db_path.parent / "pre_migrate"
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dest = snap_dir / f"neurosoft_pre_{ts}.db"

    try:
        snap_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(db_path, dest)
        logger.info("Snapshot pre-migracion: %s (%.1f KB)", dest.name, size / 1024)

        # Limpiar: mantener solo los 10 mas recientes
        snaps = sorted(snap_dir.glob("neurosoft_pre_*.db"), reverse=True)
        for old in snaps[10:]:
            old.unlink(missing_ok=True)
    except Exception as exc:
        logger.warning("No se pudo crear snapshot pre-migracion: %s", exc)


def _apply_additive_schema_patches() -> None:
    """
    Añade columnas nuevas a tablas existentes cuando SQLAlchemy no las crea
    (porque la tabla ya existía). Lista blanca explícita para minimizar riesgo.
    Es idempotente: si la columna ya existe, no hace nada.
    """

    patches: list[tuple[str, str, str]] = [
        # (tabla, columna, tipo_sql_sqlite)
        ("patients",          "acompanante_relacion", "VARCHAR(100)"),
        ("patients",          "acompanante_telefono", "VARCHAR(50)"),
        ("patients",          "archived_at",      "DATETIME"),
        ("patients",          "archived_by",      "VARCHAR(36)"),
        ("patients",          "archived_reason",  "TEXT"),
        ("evaluations",       "baremo_version",          "VARCHAR(30)"),
        ("evaluations",       "baremo_checksum",         "VARCHAR(64)"),
        # Campos de categoría/nota de informe inconcluso
        ("evaluations",       "informe_inconcluso_cat",  "VARCHAR(80)"),
        ("evaluations",       "informe_inconcluso_nota", "TEXT"),
        # Workflow de firma clínica (Res. 2654 MinSalud)
        ("evaluations",       "signed_at",        "DATETIME"),
        ("evaluations",       "signed_by",        "VARCHAR(36)"),
        ("evaluations",       "signed_by_label",  "VARCHAR(150)"),
        ("evaluations",       "signature_sha256", "VARCHAR(64)"),
        # Soft-delete de sesiones de evolución (Res. 1995)
        ("evolucion_terapia", "updated_at",       "DATETIME"),
        ("evolucion_terapia", "archived_at",      "DATETIME"),
        ("evolucion_terapia", "archived_by",      "VARCHAR(36)"),
        ("evolucion_terapia", "archived_reason",  "TEXT"),
        # Trazabilidad por request: X-Request-ID en cada asiento de auditoría
        ("audit_log",         "request_id",       "VARCHAR(64)"),
        # Campo de hipótesis pre-evaluativa añadido en v8 a la HC
        ("clinical_histories", "hipotesis_pre_eval", "TEXT"),
        # Foto/avatar del profesional para mostrar en perfil e informes
        ("professionals",     "foto_base64",      "TEXT"),
    ]
    # §C5-fix: validación estricta de identificadores SQL.
    # Aunque `patches` está hardcoded internamente, evitamos cualquier
    # posibilidad de inyección (futura) verificando que cada identificador
    # solo contenga caracteres seguros [A-Za-z0-9_] y tipos permitidos.
    import re as _re
    _IDENT = _re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    _ALLOWED_TYPES = {"TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC",
                       "DATETIME", "BOOLEAN"}

    with _engine.begin() as conn:
        for table, column, sql_type in patches:
            if not (_IDENT.match(table) and _IDENT.match(column)
                    and sql_type.upper() in _ALLOWED_TYPES):
                logger.error(
                    "Auto-upgrade: identificador inválido rechazado: %s.%s %s",
                    table, column, sql_type,
                )
                continue
            try:
                info = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
            except Exception as _exc:
                logger.debug("PRAGMA table_info falló (esperado si tabla no existe): %s", _exc)
            existing = {row[1] for row in info}
            if column in existing:
                continue
            try:
                conn.exec_driver_sql(
                    f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"
                )
                logger.info("Auto-upgrade: %s.%s agregada", table, column)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "Auto-upgrade: no se pudo agregar %s.%s: %s",
                    table, column, e,
                )


def get_session() -> Generator[Session, None, None]:
    """
    Generador de sesión para usar con Depends() de FastAPI.

    Uso en endpoint:
        @router.post("/")
        def create(db: Session = Depends(get_session)):
            ...

    Garantiza:
        - La sesión se abre al entrar al endpoint.
        - Se hace commit si no hay errores.
        - Se hace rollback si hay excepción.
        - La sesión se cierra siempre (finally).
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def session_scope():
    """
    Context manager para uso fuera de FastAPI (scripts, tests).

    Uso:
        with session_scope() as db:
            repo = PatientRepository(db)
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────
# FTS5 — Full-Text Search para pacientes
# ─────────────────────────────────────────────────────────────

def _init_fts5_index() -> None:
    """
    Crea y mantiene sincronizado el índice FTS5 para búsqueda full-text
    de pacientes. Usa triggers de SQLite para mantener la sincronización
    automática en INSERT/UPDATE/DELETE.

    FTS5 es una extensión nativa de SQLite (viene incluida) que permite
    búsqueda full-text instantánea con ranking BM25.
    """
    from sqlalchemy import text

    with _engine.begin() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='patients_fts'"
        )).fetchone()

        if result:
            count = conn.execute(text("SELECT COUNT(*) FROM patients_fts")).scalar()
            if count > 0:
                return
            conn.execute(text("INSERT INTO patients_fts(patients_fts) VALUES('rebuild')"))
            logger.info("FTS5: índice repoblado (%d documentos)", count)
            return

        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS patients_fts
            USING fts5(
                id UNINDEXED,
                primer_nombre,
                segundo_nombre,
                primer_apellido,
                segundo_apellido,
                numero_documento,
                motivo_consulta,
                eps,
                ciudad,
                ocupacion,
                content='patients',
                content_rowid='rowid',
                tokenize='unicode61'
            )
        """))

        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS patients_ai AFTER INSERT ON patients BEGIN
                INSERT INTO patients_fts(rowid, id, primer_nombre, segundo_nombre,
                    primer_apellido, segundo_apellido, numero_documento,
                    motivo_consulta, eps, ciudad, ocupacion)
                VALUES (new.rowid, new.id, new.primer_nombre, new.segundo_nombre,
                    new.primer_apellido, new.segundo_apellido, new.numero_documento,
                    new.motivo_consulta, new.eps, new.ciudad, new.ocupacion);
            END
        """))

        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS patients_ad AFTER DELETE ON patients BEGIN
                INSERT INTO patients_fts(patients_fts, rowid, id, primer_nombre,
                    segundo_nombre, primer_apellido, segundo_apellido,
                    numero_documento, motivo_consulta, eps, ciudad, ocupacion)
                VALUES ('delete', old.rowid, old.id, old.primer_nombre,
                    old.segundo_nombre, old.primer_apellido, old.segundo_apellido,
                    old.numero_documento, old.motivo_consulta, old.eps,
                    old.ciudad, old.ocupacion);
            END
        """))

        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS patients_au AFTER UPDATE ON patients BEGIN
                INSERT INTO patients_fts(patients_fts, rowid, id, primer_nombre,
                    segundo_nombre, primer_apellido, segundo_apellido,
                    numero_documento, motivo_consulta, eps, ciudad, ocupacion)
                VALUES ('delete', old.rowid, old.id, old.primer_nombre,
                    old.segundo_nombre, old.primer_apellido, old.segundo_apellido,
                    old.numero_documento, old.motivo_consulta, old.eps,
                    old.ciudad, old.ocupacion);
                INSERT INTO patients_fts(rowid, id, primer_nombre, segundo_nombre,
                    primer_apellido, segundo_apellido, numero_documento,
                    motivo_consulta, eps, ciudad, ocupacion)
                VALUES (new.rowid, new.id, new.primer_nombre, new.segundo_nombre,
                    new.primer_apellido, new.segundo_apellido, new.numero_documento,
                    new.motivo_consulta, new.eps, new.ciudad, new.ocupacion);
            END
        """))

        conn.execute(text("""
            INSERT INTO patients_fts(patients_fts) VALUES('rebuild')
        """))

        count = conn.execute(text("SELECT COUNT(*) FROM patients_fts")).scalar()
        logger.info("FTS5: índice creado y poblado (%d documentos)", count)
