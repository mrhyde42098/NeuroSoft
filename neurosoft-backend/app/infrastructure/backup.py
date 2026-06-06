"""
app/infrastructure/backup.py
============================
S4.3: Backups cifrados AES-128 (Fernet) de la base de datos SQLite.

Diseño:
  - Crea una copia comprimida (gzip) de la BD SQLite.
  - Cifra con Fernet (AES-128-CBC + HMAC-SHA256) derivado del JWT_SECRET.
  - Guarda en `data/backups/ns-backup-YYYYMMDD-HHMMSS.enc.gz`.
  - Rotación: conserva los últimos 7 diarios + 4 semanales.
  - Verificación: cada backup lleva un header con SHA-256 del plaintext
    antes de cifrar — al restaurar, se valida la integridad.

IMPORTANTE: si el JWT_SECRET cambia, los backups antiguos NO se pueden
descifrar. Guardar el JWT_SECRET en lugar seguro (env var o .env fuera
del backup) es responsabilidad del operador.

Uso:
    from app.infrastructure.backup import crear_backup, restaurar_backup,
        listar_backups, eliminar_backups_viejos
    ruta = crear_backup(notas="Antes de migración 007")
    backups = listar_backups()
    restaurar_backup(ruta, target_path=Path("data/neurosoft_restored.db"))
"""

from __future__ import annotations

import gzip
import hashlib
import json
import logging
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger("neurosoft.backup")


HEADER_VERSION = "NSBK1"  # marca para distinguir de backups antiguos


@dataclass
class BackupMetadata:
    ruta: Path
    timestamp: datetime
    tamano_bytes: int
    sha256_plaintext: str
    notas: str | None

    def to_dict(self) -> dict:
        return {
            "ruta": str(self.ruta),
            "timestamp": self.timestamp.isoformat(),
            "tamano_bytes": self.tamano_bytes,
            "sha256_plaintext": self.sha256_plaintext,
            "notas": self.notas,
        }


def _ruta_bd() -> Path:
    """Ruta a la BD SQLite activa."""
    return Path(settings.db_path)


def _directorio_backups() -> Path:
    d = Path(settings.backup_dir or "./data/backups")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _nombre_backup(ts: datetime | None = None) -> str:
    ts = ts or datetime.now(UTC)
    return f"ns-backup-{ts.strftime('%Y%m%d-%H%M%S-%f')}.enc.gz"


def _cifrar_y_empaquetar(plaintext: bytes, metadata: dict) -> bytes:
    """Cifra plaintext con Fernet y antepone header con metadata + sha256."""
    from app.infrastructure.crypto import encrypt

    # sha256 para verificación de integridad al restaurar
    sha = hashlib.sha256(plaintext).hexdigest()
    header = {
        "version": HEADER_VERSION,
        "sha256": sha,
        "metadata": metadata,
    }
    cipher_b = encrypt(plaintext.decode("latin-1"))
    payload = json.dumps(
        {
            "header": header,
            "ciphertext": cipher_b,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    return payload


def _descifrar_y_verificar(payload: bytes) -> tuple[bytes, dict]:
    """Descifra payload y verifica sha256. Lanza ValueError si falla."""
    from app.infrastructure.crypto import decrypt

    obj = json.loads(payload.decode("utf-8"))
    header = obj.get("header") or {}
    cipher_b = obj.get("ciphertext") or ""
    sha_esperado = header.get("sha256")
    if not sha_esperado:
        raise ValueError("Header de backup inválido: sin sha256")
    plain = decrypt(cipher_b)
    if plain is None:
        raise ValueError("No se pudo descifrar el backup (¿cambió JWT_SECRET?)")
    plain_b = plain.encode("latin-1")
    sha_actual = hashlib.sha256(plain_b).hexdigest()
    if sha_actual != sha_esperado:
        raise ValueError(
            f"SHA-256 no coincide. Esperado: {sha_esperado[:12]}… actual: {sha_actual[:12]}… (backup corrupto)"
        )
    return plain_b, header


def crear_backup(notas: str | None = None) -> Path:
    """
    Crea un backup cifrado de la BD. Devuelve la ruta del archivo .enc.gz.
    """
    bd_path = _ruta_bd()
    if not bd_path.exists():
        raise FileNotFoundError(f"BD no encontrada: {bd_path}")
    # Copia en caliente a un temp local (SQLite permite copiar el archivo
    # si no hay transacciones activas gracias a WAL).
    ts = datetime.now(UTC)
    ts_str = ts.strftime("%Y%m%d-%H%M%S-%f")
    meta_dict = {
        "version": HEADER_VERSION,
        "timestamp": ts.isoformat(),
        "bd_path": str(bd_path),
        "tamano_original": bd_path.stat().st_size,
        "notas": notas or "",
    }
    raw = bd_path.read_bytes()
    payload = _cifrar_y_empaquetar(raw, meta_dict)
    out_name = f"ns-backup-{ts_str}.enc.gz"
    out_path = _directorio_backups() / out_name
    # Comprimir con gzip
    with gzip.open(out_path, "wb", compresslevel=6) as f:
        f.write(payload)
    logger.info("Backup creado: %s (%.1f KB)", out_path, out_path.stat().st_size / 1024)
    return out_path


def restaurar_backup(
    ruta_backup: Path | str,
    target_path: Path | str | None = None,
    verificar_sha: bool = True,
) -> Path:
    """
    Restaura un backup cifrado a la ruta indicada (default: BD activa).
    Crea un .bak de la BD actual antes de sobrescribir.
    """
    ruta = Path(ruta_backup)
    if not ruta.exists():
        raise FileNotFoundError(f"Backup no encontrado: {ruta}")
    with gzip.open(ruta, "rb") as f:
        payload = f.read()
    plain_b, header = _descifrar_y_verificar(payload)
    target = Path(target_path) if target_path else _ruta_bd()
    target.parent.mkdir(parents=True, exist_ok=True)
    # Backup defensivo de la BD actual
    if target.exists():
        backup_anterior = target.with_suffix(
            target.suffix + f".pre-restore-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.bak"
        )
        shutil.copy2(target, backup_anterior)
        logger.info("BD actual respaldada en: %s", backup_anterior)
    target.write_bytes(plain_b)
    logger.info("Backup restaurado: %s → %s (%.1f KB)", ruta, target, len(plain_b) / 1024)
    return target


def listar_backups() -> list[BackupMetadata]:
    """Lista todos los backups cifrados en el directorio configurado."""
    out: list[BackupMetadata] = []
    for p in sorted(_directorio_backups().glob("ns-backup-*.enc.gz")):
        try:
            with gzip.open(p, "rb") as f:
                payload = f.read()
            _, header = _descifrar_y_verificar(payload)
            meta = header.get("metadata") or {}
            ts_str = meta.get("timestamp") or ""
            try:
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                ts = datetime.fromtimestamp(p.stat().st_mtime, tz=UTC)
            out.append(
                BackupMetadata(
                    ruta=p,
                    timestamp=ts,
                    tamano_bytes=p.stat().st_size,
                    sha256_plaintext=header.get("sha256", ""),
                    notas=meta.get("notas"),
                )
            )
        except Exception as e:
            logger.warning("No se pudo leer backup %s: %s", p, e)
    return out


def eliminar_backups_viejos(
    mantener_diarios: int = 7,
    mantener_semanales: int = 4,
    ahora: datetime | None = None,
) -> int:
    """
    Conserva los últimos N backups diarios y los últimos M semanales
    (cualquier backup de hace más de 7 días se considera candidato a
    semanal). Devuelve el número de backups eliminados.
    """
    ahora = ahora or datetime.now(UTC)
    backups = listar_backups()
    if not backups:
        return 0
    # Ordenar por timestamp descendente
    backups.sort(key=lambda b: b.timestamp, reverse=True)
    # Diarios: los más recientes del último día
    hoy = ahora.date()
    diarios = [b for b in backups if b.timestamp.date() == hoy]
    semanales = [b for b in backups if (ahora - b.timestamp).days <= 7 and b not in diarios]
    # Conservar top N de cada categoría
    mantener_diarios_set = {id(b) for b in diarios[:mantener_diarios]}
    mantener_semanales_set = {id(b) for b in semanales[:mantener_semanales]}
    conservar = mantener_diarios_set | mantener_semanales_set
    eliminados = 0
    for b in backups:
        if id(b) not in conservar:
            try:
                b.ruta.unlink()
                eliminados += 1
                logger.info("Backup viejo eliminado: %s", b.ruta)
            except OSError as e:
                logger.warning("No se pudo eliminar %s: %s", b.ruta, e)
    return eliminados
