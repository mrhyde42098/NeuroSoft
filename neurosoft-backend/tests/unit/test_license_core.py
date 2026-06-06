"""Tests unitarios para tools/license_core.py (generación e inventario offline)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import license_core as lc  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_admin_dir(tmp_path, monkeypatch):
    admin = tmp_path / "LicenseAdmin"
    admin.mkdir()
    monkeypatch.setattr(lc, "_admin_dir", lambda: admin)
    yield admin


def test_generate_and_decode_key_roundtrip():
    key = lc.generate_key("beta", "Ana Test", "ana@test.com", "123", 0, "Clínica X")
    assert key.startswith("NSFT-")
    info = lc.decode_key(key)
    assert info["type"] == "beta"
    assert info["watermark"] is True
    assert info["expires_at"] is None


def test_inventory_register_and_stats():
    key = lc.generate_key("trial", "Trial User", "t@t.com", days=14)
    lc.inventory_register({"key": key, "type": "trial", "name": "Trial User", "email": "t@t.com", "days": 14})
    st = lc.inventory_stats()
    assert st["total"] >= 1
    assert st["available"] >= 1
    assert st["by_type_detail"]["trial"]["available"] >= 1


def test_check_quota_blocks_when_limit_reached():
    settings = {"quotas": {"beta": 1}}
    lc.inventory_register({"key": "NSFT-0001", "type": "beta", "name": "x", "email": "x@y.z"}, status="available")
    ok, msg = lc.check_quota("beta", count=1, settings=settings)
    assert ok is False
    assert "Cuota" in msg


def test_export_inventory_csv(tmp_path):
    key = lc.generate_key("beta", "Export", "exp@test.com")
    lc.inventory_register({"key": key, "type": "beta", "name": "Export", "email": "exp@test.com", "batch": "T1"})
    csv_path = tmp_path / "out.csv"
    n = lc.export_inventory_csv(csv_path)
    assert n >= 1
    text = csv_path.read_text(encoding="utf-8-sig")
    assert "NSFT-" in text


def test_import_csv_skips_duplicates(tmp_path):
    key = lc.generate_key("beta", "Dup", "d@test.com")
    lc.inventory_register({"key": key, "type": "beta", "name": "Dup", "email": "d@test.com"})
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(
        "key,type,name,email,status\n"
        f"{key},beta,Dup,d@test.com,available\n"
        "NSFT-FAKE-FAKE-FAKE-FAKE,beta,New,n@t.com,available\n",
        encoding="utf-8-sig",
    )
    new_n, total = lc.import_csv_inventory(csv_path)
    assert total == 2
    assert new_n == 1
