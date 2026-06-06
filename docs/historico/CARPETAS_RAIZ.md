# Mapa de carpetas raíz — D:\NeuroSoftApp

Última revisión: 5 jun 2026.

| Carpeta / archivo | Función | ¿Activo? | Última mod. típica |
|---|---|---|---|
| **neurosoft-backend/** | API FastAPI, motor clínico, PDF, SQLite | ✅ Sí | Diario |
| **neurosoft-frontend/** | React SPA | ✅ Sí | Diario |
| **docs/** | Documentación, auditorías, legal | ✅ Sí | Por sprint |
| **.claude/** | Skills, agentes, hooks pre-commit | ✅ Sí | Ocasional |
| **installer/** | `NeuroSoft.iss` (Inno Setup activo) | ✅ Sí | Estable |
| **dist/** | `NeuroSoft.exe`, `NeuroSoft-Setup.exe` (gitignored) | ✅ Build | Cada release |
| **build/** | Artefactos PyInstaller (gitignored) | ✅ Build | Cada build |
| **vendor/ollama/** | `OllamaSetup.exe` ~1.3 GB (gitignored) | ✅ Instalador | Raro |
| **.github/** | CI backend + frontend | ✅ Sí | Estable |
| **Capacitaciones Clínicas/** | Protocolos JSON fuente clínica | ✅ Referencia | Raro |
| **mcp-servers/** | MCP baremos para Claude Code (venv propio) | ⚙️ Opcional dev | Estable |
| **docs/infra/** | Build, vendor, installer explicados | ✅ Referencia | Jun 2026 |
| **archive/** | Legacy (Excel VBA, scripts viejos) | 📦 Archivo | — |
| **data/** (raíz) | `last_update.json` prueba OTA — huérfano | ⚠️ Mover/ignorar | Jun 2026 |
| **scripts/** (raíz) | Vacía (scripts movidos a archive) | — | — |
| **session_logs/** | Logs sesión Claude (gitignored, vacía) | 📋 Reservada | — |
| **.benchmarks/** | pytest-benchmark cache | 🔧 Auto | — |
| **__pycache__/** (raíz) | Cache Python launcher | 🔧 Auto | Ignorar |

## Archivos raíz que deben quedarse

| Archivo | Función |
|---|---|
| `CLAUDE.md` | Contexto IA principal |
| `README.md` | Intro proyecto |
| `build.py` | Pipeline PyInstaller |
| `launcher.py` | Entry point desktop |
| `neurosoft.spec` | Spec PyInstaller |
| `neurosoft.ico` | Icono app |
| `requirements-desktop.txt` | Deps empaquetado |
| `generate_license.py` | Licencias desktop |
| `LICENSE` | Licencia software |
| `.mcp.json` | Config MCP servers |

## Movidos a archive (jun 2026)

| Antes (raíz) | Ahora |
|---|---|
| `AUDIT_2026-*.md` | `docs/historico/audits/` |
| `MISISTEMAV1.xlsm` | `archive/legacy/` (Excel VBA histórico, feb 2026) |
| `build_installer.py` | `archive/legacy/` (usar `build.py` + `NeuroSoft.iss`) |
| `scripts/fix_frontend_warnings*.py` | `archive/scripts-oneoff/` |

## Carpetas que suelen confundirse

| Carpeta | Para qué sirve | Doc |
|---|---|---|
| `vendor/ollama/` | `OllamaSetup.exe` ~1.3 GB — IA local opcional en instalador | `docs/infra/BUILD_Y_DISTRIBUCION.md` |
| `installer/` | Inno Setup activo (`NeuroSoft.iss`) | idem |
| `mcp-servers/baremos/` | Consultar baremos desde Claude Code sin arrancar SPA | `mcp-servers/baremos/README.md` |
| `Capacitaciones Clínicas/` | Protocolos JSON fuente WISC/WAIS | `docs/REACTIVOS_WISC_WAIS_PLAN.md` |
| `build.py` / `launcher.py` | Pipeline desktop — **permanecen en raíz** | idem |

## installer/ — dos .iss

| Archivo | Estado |
|---|---|
| `NeuroSoft.iss` | **Activo** — genera `NeuroSoft-Setup.exe` |
| `NeuroSoftInstaller.iss` | Legacy — usado por `build_installer.py` archivado |
