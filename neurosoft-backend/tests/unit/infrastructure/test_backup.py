"""
S4.3: Tests del módulo de backups cifrados AES-256.
"""

import gzip
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch):
    """Crea una BD temporal y configura settings para usarla."""
    db = tmp_path / "neurosoft.db"
    db.write_bytes(b"FAKE_SQLITE_V1")
    from app.core import config

    monkeypatch.setattr(config.settings, "db_path", db)
    monkeypatch.setattr(config.settings, "backup_dir", tmp_path / "backups")
    return db


def test_crear_backup_crea_archivo_cifrado(tmp_db):
    from app.infrastructure.backup import crear_backup

    ruta = crear_backup(notas="backup test")
    assert ruta.exists()
    assert ruta.suffix == ".gz"
    # El archivo debe ser gzip válido
    with gzip.open(ruta, "rb") as f:
        payload = f.read()
    obj = json.loads(payload.decode("utf-8"))
    assert "header" in obj
    assert "ciphertext" in obj
    assert obj["header"]["version"] == "NSBK1"
    assert obj["header"]["metadata"]["notas"] == "backup test"


def test_listar_backups_detecta_archivos(tmp_db):
    from app.infrastructure.backup import crear_backup, listar_backups

    crear_backup(notas="A")
    crear_backup(notas="B")
    backups = listar_backups()
    assert len(backups) == 2
    # Ambos tienen timestamps válidos
    assert all(b.timestamp is not None for b in backups)
    notas = sorted(b.notas for b in backups)
    assert notas == ["A", "B"]


def test_restaurar_backup_a_target_custom(tmp_db, tmp_path):
    from app.infrastructure.backup import crear_backup, restaurar_backup

    ruta = crear_backup(notas="X")
    target = tmp_path / "restored.db"
    restaurar_backup(ruta, target_path=target)
    assert target.exists()
    assert target.read_bytes() == tmp_db.read_bytes()


def test_restaurar_backup_a_bd_activa(tmp_db):
    from app.infrastructure.backup import crear_backup, restaurar_backup

    ruta = crear_backup(notas="principal")
    # Modificar BD
    tmp_db.write_bytes(b"BD_CORROMPIDA")
    # Restaurar
    restaurar_backup(ruta)
    # Debe volver al contenido original
    assert tmp_db.read_bytes() == b"FAKE_SQLITE_V1"
    # Y debe haber un .bak de la BD anterior
    baks = list(tmp_db.parent.glob("neurosoft.db.pre-restore-*.bak"))
    assert len(baks) == 1


def test_restaurar_backup_con_sha_incorrecto_falla(tmp_db, tmp_path):
    from app.infrastructure.backup import crear_backup

    ruta = crear_backup(notas="X")

    # Manipular el ciphertext para que el sha256 no coincida al restaurar
    with gzip.open(ruta, "rb") as f:
        payload = f.read()
    obj = json.loads(payload.decode("utf-8"))
    obj["header"]["sha256"] = "0" * 64
    nuevo = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    with gzip.open(ruta, "wb") as f:
        f.write(nuevo)

    from app.infrastructure.backup import restaurar_backup

    target = tmp_path / "restored.db"
    with pytest.raises(ValueError, match=r"SHA-256"):
        restaurar_backup(ruta, target_path=target)


def test_restaurar_backup_con_ciphertext_invalido_falla(tmp_db, tmp_path):
    from app.infrastructure.backup import crear_backup

    ruta = crear_backup(notas="X")

    with gzip.open(ruta, "rb") as f:
        payload = f.read()
    obj = json.loads(payload.decode("utf-8"))
    obj["ciphertext"] = "esto-no-es-ciphertext-valido"
    nuevo = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    with gzip.open(ruta, "wb") as f:
        f.write(nuevo)

    from app.infrastructure.backup import restaurar_backup

    target = tmp_path / "restored.db"
    with pytest.raises(ValueError, match=r"(?i)descifrar|JWT"):
        restaurar_backup(ruta, target_path=target)


def test_eliminar_backups_viejos_conserva_recientes(tmp_db):
    from app.infrastructure.backup import (
        crear_backup,
        eliminar_backups_viejos,
        listar_backups,
    )

    crear_backup(notas="hoy")
    backups_iniciales = listar_backups()
    assert len(backups_iniciales) >= 1
    # No debe eliminar el único backup
    eliminados = eliminar_backups_viejos(mantener_diarios=7, mantener_semanales=4)
    assert eliminados == 0


def test_eliminar_backups_viejos_elimina_excedente(tmp_path, monkeypatch):
    """Crea 10 backups, conserva 3 diarios y elimina el resto."""
    from app.core import config

    db = tmp_path / "neurosoft.db"
    db.write_bytes(b"X")
    backup_dir = tmp_path / "backups"
    # Limpieza defensiva (en caso de que un test anterior haya dejado archivos)
    if backup_dir.exists():
        for f in backup_dir.glob("*"):
            f.unlink()
    monkeypatch.setattr(config.settings, "db_path", db)
    monkeypatch.setattr(config.settings, "backup_dir", backup_dir)

    # Crear 10 backups
    import time

    from app.infrastructure.backup import (
        crear_backup,
        eliminar_backups_viejos,
        listar_backups,
    )

    for i in range(10):
        crear_backup(notas=f"backup {i}")
        time.sleep(0.01)  # asegurar timestamps distintos
    assert len(listar_backups()) == 10

    eliminados = eliminar_backups_viejos(
        mantener_diarios=3,
        mantener_semanales=0,
        ahora=datetime.now(UTC) + timedelta(minutes=1),
    )
    # 10 - 3 = 7
    assert eliminados == 7
    assert len(listar_backups()) == 3


def test_backup_con_bd_inexistente_falla(tmp_db, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "db_path", tmp_db.parent / "no_existe.db")
    from app.infrastructure.backup import crear_backup

    with pytest.raises(FileNotFoundError):
        crear_backup()
