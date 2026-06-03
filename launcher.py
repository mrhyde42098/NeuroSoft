"""
launcher.py
===========
Punto de entrada único de NeuroSoft — abre una ventana nativa (pywebview)
que aloja el frontend React servido por el backend FastAPI local.

Funcionamiento:
  1. Ajusta sys.path para localizar `app` (backend) tanto en desarrollo
     como en el bundle de PyInstaller.
  2. Arranca uvicorn en un hilo de fondo (127.0.0.1:8765).
  3. Espera a que /health responda.
  4. Abre la ventana pywebview apuntando al servidor.
  5. Al cerrar la ventana, detiene uvicorn y termina el proceso.

Se ejecuta tanto como script suelto (`python launcher.py`) como empaquetado
por PyInstaller (doble click en NeuroSoft.exe).
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
import traceback
import urllib.request
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# FIX CRÍTICO: cuando PyInstaller corre con console=False,
# Windows no crea consola → sys.stdout / sys.stderr quedan None.
# Uvicorn (y cualquier logging) explota al llamar .isatty()
# o .write() sobre None. Redirigimos a devnull preventivamente.
# ─────────────────────────────────────────────────────────────
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

# ─────────────────────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────────────────────

HOST = "127.0.0.1"
PORT_PREFERRED = 8765   # puerto dedicado para el modo ventana
PORT_FALLBACKS = [8766, 8767, 8768, 8000]
READY_TIMEOUT = 30      # segundos máximo para que el backend esté listo
WINDOW_TITLE = "NeuroSoft"
WINDOW_W = 1400
WINDOW_H = 900


# ─────────────────────────────────────────────────────────────
# Logging temprano a %APPDATA%/NeuroSoft/startup.log
# Crucial para diagnosticar problemas cuando no hay consola.
# ─────────────────────────────────────────────────────────────

def _log_dir() -> Path:
    d = Path(os.getenv("APPDATA", Path.home())) / "NeuroSoft"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return d


_STARTUP_LOG = _log_dir() / "startup.log"


def _startup(msg: str) -> None:
    """Escribe a startup.log inmediatamente — visible para el usuario."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{ts}] {msg}\n"
    try:
        with _STARTUP_LOG.open("a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
    except Exception:
        pass
    # También a stderr por si el .exe se lanza desde consola
    try:
        sys.stderr.write(line)
        sys.stderr.flush()
    except Exception:
        pass


def _reset_startup_log() -> None:
    """Reinicia el log en cada arranque, para no acumular."""
    try:
        _STARTUP_LOG.write_text(
            f"=== NeuroSoft startup @ {datetime.now().isoformat()} ===\n"
            f"frozen={getattr(sys, 'frozen', False)}  "
            f"executable={sys.executable}  "
            f"MEIPASS={getattr(sys, '_MEIPASS', '')}\n"
            f"cwd={os.getcwd()}  argv={sys.argv}\n",
            encoding="utf-8",
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# Resolución de rutas (dev vs bundle)
# ─────────────────────────────────────────────────────────────

def _resolve_paths() -> None:
    """Inyecta el paquete `app` del backend en sys.path."""
    _startup("Paso 1: resolviendo sys.path")
    if getattr(sys, "frozen", False):
        bundle = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        _startup(f"  bundle={bundle}")
        for sub in ("", "backend", "neurosoft-backend"):
            p = bundle / sub if sub else bundle
            if (p / "app").is_dir():
                if str(p) not in sys.path:
                    sys.path.insert(0, str(p))
                _startup(f"  app/ encontrado en {p}")
                return
        raise RuntimeError(
            f"No se encontró el paquete 'app' dentro del bundle: {bundle}"
        )
    else:
        backend = Path(__file__).resolve().parent / "neurosoft-backend"
        if (backend / "app").is_dir() and str(backend) not in sys.path:
            sys.path.insert(0, str(backend))
            _startup(f"  dev mode: {backend}")


# ─────────────────────────────────────────────────────────────
# Puerto libre
# ─────────────────────────────────────────────────────────────

def _port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        try:
            s.bind((HOST, port))
            return True
        except OSError:
            return False


def pick_port() -> int:
    _startup("Paso 2: buscando puerto libre")
    for p in (PORT_PREFERRED, *PORT_FALLBACKS):
        if _port_is_free(p):
            _startup(f"  puerto elegido: {p}")
            return p
    raise RuntimeError("No hay puertos libres en 127.0.0.1")


# ─────────────────────────────────────────────────────────────
# Arranque del servidor
# ─────────────────────────────────────────────────────────────

_server = None  # referencia a uvicorn.Server para apagado limpio
_server_error: Exception | None = None


def _run_server(port: int) -> None:
    global _server, _server_error
    try:
        _startup("Paso 3a: importando uvicorn y app.main")
        import uvicorn
        from app.main import app  # noqa: F401

        _startup(f"Paso 3b: creando uvicorn.Server en :{port}")
        config = uvicorn.Config(
            app,
            host=HOST,
            port=port,
            log_level="warning",
            access_log=False,
            lifespan="on",
        )
        _server = uvicorn.Server(config)
        _startup("Paso 3c: server.run() (loop hasta should_exit)")
        _server.run()
        _startup("Paso 3d: server.run() terminó")
    except Exception as e:
        _server_error = e
        _startup(f"ERROR en servidor: {type(e).__name__}: {e}")
        _startup(traceback.format_exc())


def wait_until_ready(port: int, timeout: int = READY_TIMEOUT) -> bool:
    _startup(f"Paso 4: esperando /health en :{port} (timeout={timeout}s)")
    url = f"http://{HOST}:{port}/health"
    start = time.time()
    while time.time() - start < timeout:
        if _server_error:
            _startup(f"  servidor ya falló, abortando wait: {_server_error}")
            return False
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    elapsed = time.time() - start
                    _startup(f"  /health OK tras {elapsed:.1f}s")
                    return True
        except Exception:
            time.sleep(0.25)
    _startup("  TIMEOUT esperando /health")
    return False


# ─────────────────────────────────────────────────────────────
# Ventana pywebview
# ─────────────────────────────────────────────────────────────

def _setup_webview2_user_data_folder() -> Path:
    """
    §pywebview-fix (2026-05-18): WebView2 mantiene un perfil persistente
    (cookies, caché HTTP, IndexedDB, Service Workers) entre lanzamientos
    del .exe. Esa persistencia es la que provocaba pantalla en blanco al
    actualizar — el cache de WebView2 servía HTML viejo con hashes que ya
    no existían.

    Solución: usar un directorio dedicado para NeuroSoft, AISLADO del
    perfil de Edge del usuario, y permitir purgarlo agresivamente la
    primera vez que detectamos una versión nueva del bundle.

    Estrategia:
      - WEBVIEW2_USER_DATA_FOLDER apunta a %APPDATA%/NeuroSoft/webview2
      - Si encontramos un marcador de versión distinto al actual, borramos
        el folder antes de pasarlo a WebView2 (= caché limpia).
      - Si está intacto, lo reusamos (= preserva login, posición de
        ventana, etc. entre arranques).
    """
    import shutil

    # Versión del bundle: usamos el sha del index.html como huella estable.
    # Si cambia (= nuevo build), invalidamos la caché.
    bundle_hash = "unknown"
    try:
        bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        idx = bundle_root / "static" / "index.html"
        if idx.exists():
            import hashlib
            bundle_hash = hashlib.sha256(idx.read_bytes()).hexdigest()[:16]
    except Exception as e:
        _startup(f"  no se pudo calcular bundle_hash: {e}")

    data_dir = Path(os.getenv("APPDATA", Path.home())) / "NeuroSoft"
    webview_dir = data_dir / "webview2"
    marker_file = data_dir / ".webview2_bundle_hash"

    try:
        previous_hash = marker_file.read_text(encoding="utf-8").strip() if marker_file.exists() else ""
    except Exception:
        previous_hash = ""

    if previous_hash != bundle_hash:
        # Versión nueva del bundle → purgamos la caché de WebView2 para
        # garantizar que la próxima carga sea limpia.
        if webview_dir.exists():
            _startup(f"  bundle cambió ({previous_hash[:6]} → {bundle_hash[:6]}) — purgando caché WebView2")
            try:
                shutil.rmtree(webview_dir, ignore_errors=True)
            except Exception as e:
                _startup(f"  WARN: no se pudo borrar {webview_dir}: {e}")
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            marker_file.write_text(bundle_hash, encoding="utf-8")
        except Exception as e:
            _startup(f"  WARN: no se pudo escribir marker: {e}")
    else:
        _startup(f"  bundle hash sin cambios ({bundle_hash[:6]}) — reusando perfil WebView2")

    webview_dir.mkdir(parents=True, exist_ok=True)

    # Variable de entorno que WebView2 lee al inicializarse.
    os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(webview_dir)
    _startup(f"  WEBVIEW2_USER_DATA_FOLDER={webview_dir}")
    return webview_dir


def open_window(port: int) -> None:
    _startup("Paso 5: importando pywebview")

    # §pywebview-fix: configurar perfil aislado de WebView2 ANTES de
    # importar webview (necesario porque el flag se lee al inicializar).
    _setup_webview2_user_data_folder()

    import webview

    _startup(f"  pywebview = {webview.__file__}")
    # Cache-buster: query string único por arranque. Aunque WebView2 ahora
    # tiene perfil limpio en updates, este es un cinturón extra de seguridad.
    cache_buster = int(time.time())
    url = f"http://{HOST}:{port}/?ns={cache_buster}"

    _startup("Paso 6: webview.create_window(...)")
    window = webview.create_window(
        WINDOW_TITLE,
        url,
        width=WINDOW_W,
        height=WINDOW_H,
        min_size=(1024, 700),
        resizable=True,
        confirm_close=False,
        # x/y = None → pywebview centra la ventana en el monitor primario
    )

    def _on_closing():
        _startup("evento: ventana cerrándose → deteniendo uvicorn")
        try:
            if _server:
                _server.should_exit = True
        except Exception:
            pass

    window.events.closing += _on_closing

    _startup("Paso 7: webview.start() — bloquea hasta que la ventana se cierre")
    gui = "edgechromium" if sys.platform == "win32" else None
    try:
        # §pywebview-debug: por defecto OFF en producción. Para activar
        # DevTools (click derecho → Inspect) durante diagnóstico, fija
        # NEUROSOFT_WEBVIEW_DEBUG=1 en el entorno antes de lanzar.
        # private_mode=False permite persistir login entre sesiones; los
        # cambios de versión los gestiona _setup_webview2_user_data_folder().
        debug_mode = os.getenv("NEUROSOFT_WEBVIEW_DEBUG", "0") == "1"
        webview.start(gui=gui, debug=debug_mode, private_mode=False)
        _startup("Paso 8: webview.start() retornó — ventana cerrada")
    except Exception as e:
        _startup(f"ERROR en webview.start(): {type(e).__name__}: {e}")
        _startup(traceback.format_exc())
        raise


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main() -> int:
    _reset_startup_log()
    _startup("=== main() iniciado ===")

    try:
        _resolve_paths()

        port = pick_port()
        os.environ.setdefault("NEUROSOFT_PORT", str(port))

        _startup("Paso 3: arrancando uvicorn en thread de fondo")
        t = threading.Thread(target=_run_server, args=(port,), daemon=True)
        t.start()

        if not wait_until_ready(port):
            _startup("ABORT: backend no respondió")
            if _server_error:
                _startup(f"causa: {_server_error}")
            print("El backend no respondió a tiempo.", file=sys.stderr)
            return 2

        open_window(port)
        _startup("=== main() terminando normalmente ===")
        return 0

    except Exception:
        _startup("EXCEPCIÓN no capturada en main():")
        _startup(traceback.format_exc())
        # En caso de error en bundle sin consola, dejamos un log detallado
        try:
            (_log_dir() / "launcher_error.log").write_text(
                traceback.format_exc(), encoding="utf-8"
            )
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
