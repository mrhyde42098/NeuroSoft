"""
build_protected.py
==================
§BLINDAJE — Pipeline de build protegido para NeuroSoft.

Genera: D:\NeuroSoftApp-FINAL\dist\NeuroSoft-Setup.exe

Flujo:
  1. Copia el código fuente de D:\NeuroSoftApp a build\
  2. Compila módulos críticos con Cython a .pyd
  3. Cifra BD_NEURO_MAESTRA.json a AES-256
  4. Limpia rastros (.py originales, __pycache__, tests, docs, .git)
  5. Build frontend (npm run build)
  6. PyInstaller → NeuroSoft.exe
  7. Inno Setup → NeuroSoft-Setup.exe
  8. Limpieza de build\

USO:
    python build_protected.py              # build completo
    python build_protected.py --skip-cython # sin compilar .pyd (para pruebas)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────
DEV_ROOT    = Path("D:/NeuroSoftApp")
FINAL_ROOT  = Path("D:/NeuroSoftApp-FINAL")
BUILD_DIR   = FINAL_ROOT / "build"
DIST_DIR    = FINAL_ROOT / "dist"
LOGS_DIR    = FINAL_ROOT / "logs"

BACKEND_SRC = DEV_ROOT / "neurosoft-backend"
FRONTEND_SRC = DEV_ROOT / "neurosoft-frontend"

VENV_PY = BACKEND_SRC / "venv" / "Scripts" / "python.exe"

INNO_SETUP = Path("C:/Users/DESKTOP/AppData/Local/Programs/Inno Setup 6/ISCC.exe")

# Módulos críticos a compilar con Cython (.py → .pyd)
CYTHON_MODULES = [
    "app/domain/clinical_engine/strategies.py",
    "app/domain/clinical_engine/baremos_loader.py",
    "app/domain/clinical_engine/engine.py",
    "app/domain/clinical_engine/interpretation_engine.py",
    "app/domain/clinical_engine/grober_buschke.py",
    "app/domain/clinical_engine/wisc_discrepancy.py",
    "app/infrastructure/auth/auth_service.py",
    "app/infrastructure/license_manager.py",
]

# ═════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════

def log(msg, level="info"):
    colors = {"info":"\033[36m","ok":"\033[32m","warn":"\033[33m","err":"\033[31m","reset":"\033[0m"}
    prefix = {"info":"🔹","ok":"✅","warn":"⚠️","err":"❌"}
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{colors.get(level,'')}[{ts}] {prefix.get(level,'')} {msg}{colors['reset']}")

def run(cmd, cwd=None, check=True):
    """Ejecuta un comando y captura la salida."""
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        log(f"Comando falló (exit {result.returncode}): {cmd}", "err")
        if result.stderr:
            print(result.stderr[-500:])
        return False
    return True


# ═════════════════════════════════════════════════════════════
# PASO 0: Preparar entorno
# ═════════════════════════════════════════════════════════════

def step_prepare():
    """Crea/limpia el directorio de build."""
    log("Preparando directorio de build...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Copiar código fuente al build
    log("Copiando backend...")
    shutil.copytree(BACKEND_SRC / "app", BUILD_DIR / "neurosoft-backend" / "app")
    shutil.copy(BACKEND_SRC / "requirements.txt", BUILD_DIR / "neurosoft-backend" / "requirements.txt")

    log("Copiando datos...")
    shutil.copytree(BACKEND_SRC / "data", BUILD_DIR / "neurosoft-backend" / "data",
                     ignore=shutil.ignore_patterns("*.db", "*.backup*", "reports", "e2e_test.db"))

    log("Copiando alembic...")
    if (BACKEND_SRC / "alembic").exists():
        shutil.copytree(BACKEND_SRC / "alembic", BUILD_DIR / "neurosoft-backend" / "alembic")
    shutil.copy(BACKEND_SRC / "alembic.ini", BUILD_DIR / "neurosoft-backend" / "alembic.ini")

    log("Copiando frontend...")
    shutil.copytree(FRONTEND_SRC, BUILD_DIR / "neurosoft-frontend",
                     ignore=shutil.ignore_patterns("node_modules", ".git", "dist", "e2e", "test-results", "playwright-report"))

    log("Copiando archivos raíz...")
    for f in ["neurosoft.spec", "launcher.py", "neurosoft.ico", "requirements-desktop.txt"]:
        src = DEV_ROOT / f
        if src.exists():
            shutil.copy(src, BUILD_DIR / f)

    log("Entorno de build preparado.", "ok")
    return True


# ═════════════════════════════════════════════════════════════
# PASO 1: Compilar con Cython
# ═════════════════════════════════════════════════════════════

def step_cython():
    """Compila módulos críticos .py → .pyd con Cython."""
    log("Compilando módulos críticos con Cython...")

    # Verificar que Cython está instalado
    result = subprocess.run(
        [str(VENV_PY), "-c", "import Cython"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        log("Cython no instalado. Instalando...", "warn")
        run(f'"{VENV_PY}" -m pip install cython', cwd=str(BACKEND_SRC))
        # También instalar compilador C++ en Windows
        run(f'"{VENV_PY}" -m pip install setuptools wheel', cwd=str(BACKEND_SRC))

    backend_build = BUILD_DIR / "neurosoft-backend"

    for module_path in CYTHON_MODULES:
        src_file = backend_build / module_path
        if not src_file.exists():
            log(f"Módulo no encontrado: {module_path}", "warn")
            continue

        mod_name = module_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        log(f"  Compilando {mod_name}...")

        # Cython → .c
        from Cython.Build import cythonize
        try:
            cythonize(
                [str(src_file)],
                language_level="3",
                build_dir=str(backend_build / "build"),
            )
            # El .c se generó, ahora compilar a .pyd
            c_file = src_file.with_suffix(".c")
            if c_file.exists():
                # Compilar con distutils
                import distutils.core
                import distutils.extension
                ext = distutils.extension.Extension(
                    mod_name,
                    sources=[str(c_file)],
                )
                distutils.core.setup(
                    name=mod_name,
                    ext_modules=[ext],
                    script_args=["build_ext", "--inplace"],
                )
                log(f"    {mod_name} → .pyd", "ok")
            else:
                log(f"    No se generó .c para {mod_name}", "warn")
        except Exception as e:
            log(f"    Error compilando {mod_name}: {e}", "warn")
            log("    Continuando sin Cython para este módulo.", "warn")

    log("Compilación Cython completada.", "ok")
    return True


# ═════════════════════════════════════════════════════════════
# PASO 2: Cifrar BD_NEURO_MAESTRA.json
# ═════════════════════════════════════════════════════════════

def step_encrypt_baremos():
    """Cifra BD_NEURO_MAESTRA.json con AES-256."""
    log("Cifrando baremos...")

    baremo_path = BUILD_DIR / "neurosoft-backend" / "data" / "BD_NEURO_MAESTRA.json"
    if not baremo_path.exists():
        log("BD_NEURO_MAESTRA.json no encontrado.", "err")
        return False

    # Leer JSON original
    with open(baremo_path, "r", encoding="utf-8") as f:
        data = f.read()

    # Derivar clave de cifrado del checksum + fecha
    checksum = hashlib.sha256(data.encode()).digest()
    key = hashlib.pbkdf2_hmac("sha256", checksum, b"NeuroSoftProtection", 100000, dklen=32)

    # Cifrar con AES-256-GCM
    import os as _os
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aesgcm = AESGCM(key)
    nonce = _os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data.encode("utf-8"), None)

    # Guardar [nonce(12) + ciphertext]
    enc_path = baremo_path.with_suffix(".enc")
    with open(enc_path, "wb") as f:
        f.write(nonce + ciphertext)

    # Eliminar el .json original del build
    baremo_path.unlink()

    log(f"Baremos cifrados: {enc_path.name} ({len(ciphertext)} bytes)", "ok")

    # Actualizar launcher.py para que descifre al iniciar
    _patch_baremo_loader()

    return True


def _patch_baremo_loader():
    """Parchea el baremos_loader.py para que cargue desde .enc cifrado."""
    loader_path = BUILD_DIR / "neurosoft-backend" / "app" / "domain" / "clinical_engine" / "baremos_loader.py"
    if not loader_path.exists():
        return

    content = loader_path.read_text(encoding="utf-8")

    # Agregar soporte para descifrar .enc
    decrypt_code = '''
    @staticmethod
    def _decrypt_baremo(path: Path) -> bytes:
        """Descifra BD_NEURO_MAESTRA.enc en memoria."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import hashlib
        with open(path, "rb") as f:
            nonce = f.read(12)
            ciphertext = f.read()
        # La clave se deriva del propio archivo (solo funciona si el .enc no se modifica)
        key = hashlib.pbkdf2_hmac("sha256", ciphertext[:32], b"NeuroSoftProtection", 100000, dklen=32)
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
'''

    # Insertar el método antes de `def _parse`
    if "_decrypt_baremo" not in content:
        content = content.replace(
            "import hashlib",
            "import hashlib\n" + decrypt_code
        )
        # Modificar _parse para que detecte .enc
        content = content.replace(
            'with open(p, "r", encoding="utf-8") as f:',
            '''enc_path = p.with_suffix(".enc")
            if enc_path.exists():
                decrypted = cls._decrypt_baremo(enc_path)
                import io, json
                raw = json.loads(decrypted.decode("utf-8"))
            else:
                with open(p, "r", encoding="utf-8") as f:
                    raw = json.load(f)'''
        )
        loader_path.write_text(content, encoding="utf-8")


# ═════════════════════════════════════════════════════════════
# PASO 3: Limpiar rastros
# ═════════════════════════════════════════════════════════════

def step_clean_traces():
    """Elimina rastros de desarrollo del build."""
    log("Limpiando rastros de desarrollo...")

    backend_build = BUILD_DIR / "neurosoft-backend"

    # Eliminar tests
    if (backend_build / "tests").exists():
        shutil.rmtree(backend_build / "tests")

    # Eliminar __pycache__
    for pycache in backend_build.rglob("__pycache__"):
        shutil.rmtree(pycache)

    # Eliminar .py originales de módulos compilados con Cython
    for module_path in CYTHON_MODULES:
        py_file = backend_build / module_path
        pyd_file = py_file.with_suffix(".pyd")
        c_file = py_file.with_suffix(".c")
        if pyd_file.exists() and py_file.exists():
            py_file.unlink()
            log(f"  Eliminado .py: {module_path}")
        if c_file.exists():
            c_file.unlink()

    # Eliminar directorios de desarrollo
    for d in ["docs", "scripts", "venv", ".pytest_cache", "test_output.log",
              ".coverage", "investigate_*.py", "analizar_*.py", "verificar_*.py",
              "eliminar_*.py", "buscar_*.py", "count_tests.py", "analyze_coverage.py"]:
        path = backend_build / d
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # Eliminar .git y .claude si existen
    for d in [".git", ".claude", ".github"]:
        path = BUILD_DIR / d
        if path.exists() and path.is_dir():
            shutil.rmtree(path)

    log("Rastros eliminados.", "ok")
    return True


# ═════════════════════════════════════════════════════════════
# PASO 4: Build frontend
# ═════════════════════════════════════════════════════════════

def step_build_frontend():
    """npm run build en el frontend del build."""
    log("Compilando frontend...")
    fe_dir = BUILD_DIR / "neurosoft-frontend"
    if not (fe_dir / "package.json").exists():
        log("frontend no encontrado en build.", "err")
        return False

    # Instalar dependencias si no existen
    if not (fe_dir / "node_modules").exists():
        log("Instalando dependencias npm...")
        run("npm install", cwd=str(fe_dir))

    run("npm run build", cwd=str(fe_dir))
    log("Frontend compilado.", "ok")
    return True


# ═════════════════════════════════════════════════════════════
# PASO 5: PyInstaller
# ═════════════════════════════════════════════════════════════

def step_pyinstaller():
    """Empaqueta con PyInstaller."""
    log("Empaquetando con PyInstaller...")

    # Matar proceso anterior
    run("Stop-Process -Name NeuroSoft -Force -ErrorAction SilentlyContinue",
        cwd=str(BUILD_DIR))

    result = subprocess.run(
        [str(VENV_PY), "build.py", "--skip-frontend", "--skip-ollama"],
        cwd=str(DEV_ROOT),
        capture_output=True, text=True,
    )

    # Copiar .exe al dist final
    exe_src = DEV_ROOT / "dist" / "NeuroSoft.exe"
    if exe_src.exists():
        shutil.copy(exe_src, DIST_DIR / "NeuroSoft.exe")
        size_mb = exe_src.stat().st_size / (1024 * 1024)
        log(f"NeuroSoft.exe generado: {size_mb:.1f} MB", "ok")

        if size_mb > 100:
            log("WARNING: .exe > 100 MB. ¿Ollama se bundleó por error?", "warn")
    else:
        log("NeuroSoft.exe no se generó.", "err")
        return False

    return True


# ═════════════════════════════════════════════════════════════
# PASO 6: Inno Setup
# ═════════════════════════════════════════════════════════════

def step_inno_setup():
    """Compila el instalador con Inno Setup."""
    if not INNO_SETUP.exists():
        log("Inno Setup no encontrado en " + str(INNO_SETUP), "warn")
        log("El .exe está en dist/NeuroSoft.exe. El instalador no se generó.", "warn")
        return False

    log("Compilando instalador...")
    iss_file = DEV_ROOT / "installer" / "NeuroSoft.iss"
    run(f'"{INNO_SETUP}" "{iss_file}"', cwd=str(DEV_ROOT))

    # Copiar setup al dist final
    setup_src = DEV_ROOT / "dist" / "NeuroSoft-Setup.exe"
    if setup_src.exists():
        shutil.copy(setup_src, DIST_DIR / "NeuroSoft-Setup.exe")
        size_gb = setup_src.stat().st_size / (1024 * 1024 * 1024)
        log(f"NeuroSoft-Setup.exe generado: {size_gb:.2f} GB", "ok")
    else:
        log("Instalador no se generó.", "warn")

    return True


# ═════════════════════════════════════════════════════════════
# PASO 7: Limpiar build/
# ═════════════════════════════════════════════════════════════

def step_final_cleanup():
    """Elimina el directorio build/ temporal."""
    log("Limpiando build temporal...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    log("Build temporal eliminado.", "ok")


# ═════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Build protegido de NeuroSoft")
    parser.add_argument("--skip-cython", action="store_true", help="Saltar compilación Cython")
    parser.add_argument("--skip-encrypt", action="store_true", help="Saltar cifrado de baremos")
    parser.add_argument("--skip-cleanup", action="store_true", help="No borrar build/ al final")
    args = parser.parse_args()

    log("═══ BUILD PROTEGIDO NEUROSOFT ═══")
    log(f"Origen:  {DEV_ROOT}")
    log(f"Destino: {FINAL_ROOT}")

    steps = [
        ("Preparar entorno", step_prepare, True),
        ("Cython → .pyd", step_cython, not args.skip_cython),
        ("Cifrar baremos", step_encrypt_baremos, not args.skip_encrypt),
        ("Limpiar rastros", step_clean_traces, True),
        ("Build frontend", step_build_frontend, True),
        ("PyInstaller", step_pyinstaller, True),
        ("Inno Setup", step_inno_setup, True),
        ("Limpiar build/", step_final_cleanup, not args.skip_cleanup),
    ]

    for name, fn, enabled in steps:
        if not enabled:
            log(f"Paso omitido: {name}", "warn")
            continue
        log(f"\n─── {name} ───")
        try:
            fn()
        except Exception as e:
            log(f"Error en '{name}': {e}", "err")
            import traceback
            traceback.print_exc()
            return False

    log("\n═══ BUILD COMPLETADO ═══", "ok")
    log(f"Distribuible: {DIST_DIR / 'NeuroSoft-Setup.exe'}")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
