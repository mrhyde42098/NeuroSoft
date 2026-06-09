"""
app/infrastructure/desktop_auto_update.py
==========================================
Auto-actualización silenciosa para NeuroSoft desktop (offline-first).

Fuentes de update.json (en orden de prioridad):
  1. {install_dir}/update.json          — USB o copia manual junto al .exe
  2. %APPDATA%/NeuroSoft/update.json     — descargado previamente
  3. NEUROSOFT_UPDATE_URL (HTTP GET)      — solo si hay red; timeout 5 s

Formato update.json (campos mínimos):
{
  "version": "2.1.0",
  "released": "2026-06-07",
  "channel": "stable",
  "artifacts": {
    "windows_x64_exe": {
      "filename": "NeuroSoft.exe",
      "sha256": "<hex>",
      "size_bytes": 49876543,
      "url": "https://cdn.example.com/patches/NeuroSoft-2.1.0.exe"
    },
    "frontend_nsupdate": {
      "filename": "neurosoft-v2.1.0.nsupdate",
      "sha256": "<hex>",
      "size_bytes": 640000,
      "url": "https://cdn.example.com/patches/neurosoft-v2.1.0.nsupdate"
    }
  },
  "signature": "<hmac_sha256_hex del JSON canónico sin este campo>"
}

Verificación:
  HMAC-SHA256(NEUROSOFT_UPDATE_HMAC_KEY, canonical_json_sin_signature)

Reemplazo de .exe en Windows:
  No se puede sobrescribir el proceso en ejecución. Se lanza un script
  updater que espera el cierre, renombra el binario viejo y activa el nuevo.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

UPDATE_LOG_NAME = "update.log"
UPDATE_MANIFEST_LOCAL = "update.json"
HTTP_TIMEOUT_S = 5
MAX_EXE_BYTES = 250 * 1024 * 1024  # 250 MB — parche onefile
MAX_DIR_ZIP_BYTES = 500 * 1024 * 1024  # 500 MB — onedir completo


@dataclass
class ArtifactInfo:
    filename: str
    sha256: str
    size_bytes: int
    url: str | None = None


@dataclass
class UpdateManifest:
    version: str
    released: str
    channel: str
    artifacts: dict[str, ArtifactInfo]
    signature: str
    raw: dict[str, Any] = field(repr=False, default_factory=dict)


@dataclass
class UpdateCheckResult:
    update_available: bool
    current_version: str
    latest_version: str | None = None
    manifest: UpdateManifest | None = None
    source: str | None = None
    message: str = ""


def _resolve_hmac_key() -> str:
    explicit = os.getenv("NEUROSOFT_UPDATE_HMAC_KEY", "").strip()
    if explicit:
        return explicit
    from app.infrastructure.auth.auth_service import SECRET_KEY

    return hashlib.sha256(("nsupdate-hmac::" + SECRET_KEY).encode("utf-8")).hexdigest()


def _install_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[3]


def _user_data_dir() -> Path:
    try:
        from app.core.config import settings

        return Path(settings.db_path).parent
    except Exception:
        base = Path(os.getenv("APPDATA", Path.home())) / "NeuroSoft"
        base.mkdir(parents=True, exist_ok=True)
        return base


def _update_log_path() -> Path:
    return _user_data_dir() / UPDATE_LOG_NAME


def _log_migration(event: str, **details: Any) -> None:
    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "event": event,
        **details,
    }
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    try:
        with _update_log_path().open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as exc:
        logger.debug("No se pudo escribir update.log: %s", exc)
    logger.info("update: %s %s", event, details)


def _canonical_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    payload = {k: v for k, v in manifest.items() if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def verify_manifest_signature(manifest: dict[str, Any]) -> bool:
    sig = (manifest.get("signature") or "").strip().lower()
    if not sig:
        _log_migration("signature_missing")
        return False
    expected = hmac.new(
        _resolve_hmac_key().encode("utf-8"),
        _canonical_manifest_bytes(manifest),
        hashlib.sha256,
    ).hexdigest()
    ok = hmac.compare_digest(expected, sig)
    if not ok:
        _log_migration("signature_invalid", received=sig[:12], expected=expected[:12])
    return ok


def _parse_manifest(data: dict[str, Any]) -> UpdateManifest:
    artifacts: dict[str, ArtifactInfo] = {}
    for key, val in (data.get("artifacts") or {}).items():
        if not isinstance(val, dict):
            continue
        artifacts[key] = ArtifactInfo(
            filename=str(val.get("filename", "")),
            sha256=str(val.get("sha256", "")).lower(),
            size_bytes=int(val.get("size_bytes", 0)),
            url=val.get("url"),
        )
    return UpdateManifest(
        version=str(data.get("version", "")),
        released=str(data.get("released", "")),
        channel=str(data.get("channel", "stable")),
        artifacts=artifacts,
        signature=str(data.get("signature", "")),
        raw=data,
    )


def _load_manifest_file(path: Path) -> UpdateManifest | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not verify_manifest_signature(data):
            return None
        return _parse_manifest(data)
    except Exception as exc:
        _log_migration("manifest_read_error", path=str(path), error=str(exc))
        return None


def _fetch_remote_manifest(url: str) -> UpdateManifest | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NeuroSoft-Updater/1.0"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not verify_manifest_signature(data):
            return None
        manifest = _parse_manifest(data)
        cache = _user_data_dir() / UPDATE_MANIFEST_LOCAL
        cache.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        _log_migration("remote_manifest_failed", url=url, error=str(exc))
        return None


def _version_tuple(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in v.strip().split("."):
        try:
            parts.append(int(piece))
        except ValueError:
            parts.append(0)
    return tuple(parts) if parts else (0,)


def check_for_updates(current_version: str) -> UpdateCheckResult:
    """
    Busca update.json en fuentes locales y remotas.
    Retorna si hay una versión más nueva firmada.
    """
    sources: list[tuple[str, Path | str]] = [
        ("install_dir", _install_dir() / UPDATE_MANIFEST_LOCAL),
        ("user_data", _user_data_dir() / UPDATE_MANIFEST_LOCAL),
    ]
    remote = os.getenv("NEUROSOFT_UPDATE_URL", "").strip()
    if remote:
        sources.append(("http", remote))

    best: UpdateManifest | None = None
    best_source: str | None = None

    for name, src in sources:
        manifest: UpdateManifest | None
        if isinstance(src, Path):
            if not src.exists():
                continue
            manifest = _load_manifest_file(src)
        else:
            manifest = _fetch_remote_manifest(src)
        if manifest is None or not manifest.version:
            continue
        if best is None or _version_tuple(manifest.version) > _version_tuple(best.version):
            best = manifest
            best_source = name

    if best is None:
        return UpdateCheckResult(
            update_available=False,
            current_version=current_version,
            message="Sin manifest de actualización válido",
        )

    newer = _version_tuple(best.version) > _version_tuple(current_version)
    return UpdateCheckResult(
        update_available=newer,
        current_version=current_version,
        latest_version=best.version,
        manifest=best,
        source=best_source,
        message="Actualización disponible" if newer else "Sistema al día",
    )


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download_artifact(artifact: ArtifactInfo, dest: Path) -> bool:
    if artifact.url:
        try:
            req = urllib.request.Request(artifact.url, headers={"User-Agent": "NeuroSoft-Updater/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                dest.write_bytes(resp.read())
        except Exception as exc:
            _log_migration("download_failed", url=artifact.url, error=str(exc))
            return False
    elif not dest.exists():
        for candidate in (
            _install_dir() / artifact.filename,
            _user_data_dir() / "updates" / artifact.filename,
            dest,
        ):
            if candidate.is_file() and candidate != dest:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(candidate.read_bytes())
                break
        if not dest.exists():
            _log_migration("artifact_missing_local", path=str(dest))
            return False

    if dest.stat().st_size != artifact.size_bytes:
        _log_migration(
            "size_mismatch",
            expected=artifact.size_bytes,
            actual=dest.stat().st_size,
        )
        return False

    digest = _sha256_file(dest)
    if digest.lower() != artifact.sha256.lower():
        _log_migration("sha256_mismatch", expected=artifact.sha256[:16], actual=digest[:16])
        return False
    return True


def _write_updater_dir_zip_script(
    *,
    install_dir: Path,
    zip_path: Path,
    restart: bool,
) -> Path:
    """Reemplaza el directorio de instalación onedir desde un ZIP verificado."""
    script = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".cmd",
        delete=False,
        encoding="utf-8",
        newline="\r\n",
    )
    target_exe = install_dir / "NeuroSoft.exe"
    lines = [
        "@echo off",
        "setlocal",
        f'set INSTALL="{install_dir}"',
        f'set ZIP="{zip_path}"',
        f'set EXE="{target_exe}"',
        ":wait",
        'tasklist /FI "IMAGENAME eq NeuroSoft.exe" 2>nul | find /I "NeuroSoft.exe" >nul',
        "if %ERRORLEVEL%==0 (",
        "  timeout /t 2 /nobreak >nul",
        "  goto wait",
        ")",
        f'powershell -NoProfile -Command "Expand-Archive -Path \\"{zip_path}\\" -DestinationPath \\"{install_dir}\\" -Force"',
    ]
    if restart:
        lines.append('start "" "%EXE%"')
    lines += ["endlocal", 'del /F /Q "%~f0"']
    script.write("\r\n".join(lines) + "\r\n")
    script.close()
    return Path(script.name)


def _write_updater_script(
    *,
    target_exe: Path,
    new_exe: Path,
    restart: bool,
) -> Path:
    """
    Genera un .cmd que reemplaza el .exe tras cerrar NeuroSoft.
    Patrón estándar Windows: rename viejo → move nuevo → relanzar.
    """
    old_backup = target_exe.with_suffix(".exe.old")
    script = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".cmd",
        delete=False,
        encoding="utf-8",
        newline="\r\n",
    )
    lines = [
        "@echo off",
        "setlocal",
        f'set TARGET="{target_exe}"',
        f'set NEW="{new_exe}"',
        f'set OLD="{old_backup}"',
        ":wait",
        'tasklist /FI "IMAGENAME eq NeuroSoft.exe" 2>nul | find /I "NeuroSoft.exe" >nul',
        "if %ERRORLEVEL%==0 (",
        "  timeout /t 2 /nobreak >nul",
        "  goto wait",
        ")",
        'if exist "%OLD%" del /F /Q "%OLD%"',
        'ren "%TARGET%" "NeuroSoft.exe.old"',
        'move /Y "%NEW%" "%TARGET%"',
    ]
    if restart:
        lines.append('start "" "%TARGET%"')
    lines += [
        "endlocal",
        'del /F /Q "%~f0"',
    ]
    script.write("\r\n".join(lines) + "\r\n")
    script.close()
    return Path(script.name)


def apply_binary_update(manifest: UpdateManifest, *, restart: bool = True) -> dict[str, Any]:
    """
    Descarga (si hay URL) y programa reemplazo del binario principal.
    Debe invocarse cuando el usuario confirma la actualización; el proceso
    actual debe terminar para que el script updater complete el swap.
    """
    if not verify_manifest_signature(manifest.raw):
        raise ValueError("Manifest sin firma válida")

    install = _install_dir()
    target_exe = Path(sys.executable).resolve() if getattr(sys, "frozen", False) else install / "NeuroSoft.exe"

    dir_zip = manifest.artifacts.get("windows_x64_dir_zip")
    single_exe = manifest.artifacts.get("windows_x64_exe")

    if dir_zip is not None:
        if dir_zip.size_bytes > MAX_DIR_ZIP_BYTES:
            raise ValueError(f"ZIP onedir demasiado grande ({dir_zip.size_bytes} bytes)")
        staging = _user_data_dir() / "updates" / f"NeuroSoft-v{manifest.version}-win64.zip"
        staging.parent.mkdir(parents=True, exist_ok=True)
        _log_migration(
            "binary_update_start",
            mode="onedir_zip",
            version=manifest.version,
            install=str(install),
            staging=str(staging),
        )
        if not _download_artifact(dir_zip, staging):
            raise RuntimeError("No se pudo obtener o verificar el ZIP de actualización")
        updater = _write_updater_dir_zip_script(
            install_dir=install,
            zip_path=staging,
            restart=restart,
        )
    elif single_exe is not None:
        if single_exe.size_bytes > MAX_EXE_BYTES:
            raise ValueError(f"Artefacto demasiado grande ({single_exe.size_bytes} bytes)")
        staging = _user_data_dir() / "updates" / f"NeuroSoft-{manifest.version}.exe"
        staging.parent.mkdir(parents=True, exist_ok=True)
        _log_migration(
            "binary_update_start",
            mode="onefile_exe",
            version=manifest.version,
            target=str(target_exe),
            staging=str(staging),
        )
        if not _download_artifact(single_exe, staging):
            raise RuntimeError("No se pudo obtener o verificar el binario de actualización")
        updater = _write_updater_script(target_exe=target_exe, new_exe=staging, restart=restart)
    else:
        raise ValueError("Manifest sin artifact windows_x64_dir_zip ni windows_x64_exe")

    _log_migration("updater_spawned", script=str(updater))

    # Detached: el updater sobrevive al cierre de NeuroSoft
    subprocess.Popen(
        ["cmd.exe", "/C", str(updater)],
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        close_fds=True,
    )

    pending = {
        "version": manifest.version,
        "applied_at": datetime.now(UTC).isoformat(),
        "sha256": (dir_zip or single_exe).sha256,  # type: ignore[union-attr]
        "pending_restart": True,
        "mode": "onedir_zip" if dir_zip else "onefile_exe",
    }
    (_user_data_dir() / "pending_binary_update.json").write_text(
        json.dumps(pending, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "version": manifest.version,
        "message": "Actualización programada. Cierre la aplicación para completar.",
        "updater": str(updater),
    }


def run_startup_update_check(current_version: str) -> UpdateCheckResult:
    """
    Llamar desde lifespan startup (modo frozen).
    No aplica actualizaciones automáticamente — solo detecta y registra.
    """
    if not getattr(sys, "frozen", False):
        return UpdateCheckResult(
            update_available=False,
            current_version=current_version,
            message="Modo desarrollo — sin auto-update",
        )

    result = check_for_updates(current_version)
    _log_migration(
        "startup_check",
        current=current_version,
        latest=result.latest_version,
        available=result.update_available,
        source=result.source,
    )
    return result


def finalize_pending_update() -> None:
    """
    Tras reinicio exitoso, limpia marcadores si el binario nuevo está activo.
    """
    pending_path = _user_data_dir() / "pending_binary_update.json"
    if not pending_path.exists():
        return
    try:
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
        old = _install_dir() / "NeuroSoft.exe.old"
        if old.exists():
            old.unlink(missing_ok=True)
        _log_migration("binary_update_complete", version=pending.get("version"))
        pending_path.unlink(missing_ok=True)
    except Exception as exc:
        _log_migration("finalize_error", error=str(exc))
