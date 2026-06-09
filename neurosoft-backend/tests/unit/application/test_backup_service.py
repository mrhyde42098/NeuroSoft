"""Tests backup_service QW-8."""

from __future__ import annotations


def test_get_schedule_config_defaults(in_memory_db, tmp_path, monkeypatch):
    from app.application.services.backup_service import get_schedule_config
    from app.core import config

    db_file = tmp_path / "neurosoft.db"
    db_file.write_bytes(b"FAKE_SQLITE_V1")
    monkeypatch.setattr(config.settings, "db_path", db_file)
    monkeypatch.setattr(config.settings, "backup_dir", tmp_path / "backups")

    cfg = get_schedule_config(in_memory_db)
    assert cfg.enabled is True
    assert cfg.frequency == "daily"
    assert cfg.mantener_total == 5


def test_run_backup_creates_encrypted_file(in_memory_db, tmp_path, monkeypatch):
    from app.application.services.backup_service import run_backup
    from app.core import config

    db_file = tmp_path / "neurosoft.db"
    db_file.write_bytes(b"FAKE_SQLITE_V1")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setattr(config.settings, "db_path", db_file)
    monkeypatch.setattr(config.settings, "backup_dir", backup_dir)

    result = run_backup(in_memory_db, notas="test", tipo="manual", mantener_total=5)
    assert result.ruta.exists()
    assert result.ruta.name.startswith("ns-backup-")
    assert result.ruta.suffix == ".gz"
