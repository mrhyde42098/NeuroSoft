# Infraestructura de build y distribución

**Última revisión:** 5 jun 2026

Mapa de carpetas y scripts de empaquetado que suelen confundirse en la raíz del monorepo.

---

## Raíz — scripts `.py` (no mover)

| Archivo | Función | ¿Mover? |
|---|---|---|
| `launcher.py` | Entry point PyInstaller / pywebview desktop | **No** — referenciado en `neurosoft.spec` |
| `build.py` | Orquesta npm build + PyInstaller + opcional Ollama | **No** |
| `admin_license_app.py` / `build_license_admin.py` | Panel GUI licencias → `dist/NeuroSoft-LicenseAdmin.exe` | **No** — solo titular |
| `generate_license.py` | Legacy CLI/GUI licencias | Reemplazado por `admin_license_app.py` |

Mover estos archivos rompe rutas relativas del spec y del instalador.

---

## `installer/` — Inno Setup

| Archivo | Estado |
|---|---|
| `NeuroSoft.iss` | **Activo** — genera `dist/NeuroSoft-Setup.exe` |
| `NeuroSoftInstaller.iss` | Legacy (usado por `archive/legacy/build_installer.py`) |

El setup empaqueta:
- `dist/NeuroSoft.exe` (~47 MB)
- `vendor/ollama/OllamaSetup.exe` (~1.3 GB) **como archivo separado**, no dentro del .exe
- Manual PDF, assets frontend embebidos en el exe

Reglas críticas: ver `CLAUDE.md` § Pipeline de build.

---

## `vendor/ollama/`

| Contenido | Propósito |
|---|---|
| `OllamaSetup.exe` | Instalador de Ollama para IA local opcional |

- **Gitignored** (~1.3 GB)
- En instalación va a `{app}\vendor\ollama\`
- **Nunca** bundlear dentro de `NeuroSoft.exe` (corrompe el setup)

---

## `build/` y `dist/`

| Carpeta | Contenido | Git |
|---|---|---|
| `build/` | Cache PyInstaller intermedio | Ignorado |
| `dist/` | `NeuroSoft.exe`, `NeuroSoft-Setup.exe`, manuales | Ignorado |

Regenerar con `/build-beta-tester` o pipeline manual en `CLAUDE.md`.

---

## `mcp-servers/baremos/`

**Opcional.** Servidor MCP para Claude Code — consulta baremos sin arrancar la SPA.

| Pieza | Ubicación |
|---|---|
| Servidor | `mcp-servers/baremos/server.py` |
| Config | `.mcp.json` (raíz) |
| Venv propio | `mcp-servers/baremos/venv/` — separado del backend (conflicto starlette) |

No forma parte del `.exe` de producción. Ver `mcp-servers/baremos/README.md`.

---

## `Capacitaciones Clínicas/protocolos/`

Fuente clínica autoritativa para WISC-IV y WAIS-III (textos de reactivos). Espejo parcial en `neurosoft-frontend/src/data/protocols/`. Ver `docs/REACTIVOS_WISC_WAIS_PLAN.md`.

---

## `archive/`

| Subcarpeta | Contenido |
|---|---|
| `legacy/` | `MISISTEMAV1.xlsm`, `build_installer.py` obsoleto |
| `scripts-oneoff/` | Scripts de limpieza puntual |

---

## Flujo release recomendado

```
1. pytest + npm run lint
2. /actualizar-estado-vivo (si cerraste sprint)
3. /build-beta-tester
4. E2E manual checklist (PUNTO_INFLEXION)
5. Enviar dist/NeuroSoft-Setup.exe al beta tester
```
