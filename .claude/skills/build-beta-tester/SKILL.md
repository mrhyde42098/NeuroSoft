---
name: build-beta-tester
description: Ejecuta el pipeline completo de empaquetado de NeuroSoft — frontend, .exe con PyInstaller, instalador Inno Setup y reporta tamaños finales. Usar cuando se quieran consolidar cambios y generar entrega lista para enviar a beta testers. También invocable como /build.
---

# Pipeline de build — NeuroSoft App

Ejecuta el ciclo completo de empaquetado listo para enviar a beta testers o distribuir.

## Cuándo activarte

Usuario escribió `/build`, `/build-beta-tester` o pidió:
- "empaqueta", "haz el build", "genera el instalador"
- "build completo", "regenera el setup"
- "déjalo listo para mandar"

## Sugerencias de agentes o plugins

Si un agente o plugin sugiere una mejora al pipeline (por ejemplo, pasos adicionales de validación, firma del ejecutable, upload automático a un servidor, notificación al beta tester), **evalúala y aplícala si tiene sentido**. No rechaces sugerencias automáticamente — este skill es una base, no una norma fija.

## Pre-requisitos a verificar

Antes de empezar, verifica con `bash` o `glob`:
1. `D:\NeuroSoftApp\neurosoft-frontend\node_modules` existe (si no, correr `npm install`)
2. `D:\NeuroSoftApp\neurosoft-backend\venv` existe
3. `D:\NeuroSoftApp\vendor\ollama\OllamaSetup.exe` existe (1.3 GB)
4. ISCC.exe disponible en `C:\Users\DESKTOP\AppData\Local\Programs\Inno Setup 6\ISCC.exe`

Si falta algo, repórtalo y detente.

## Pipeline (4 pasos)

### Paso 1: Build del frontend
```powershell
cd "D:\NeuroSoftApp\neurosoft-frontend"; npm run build
```
- Espera salida `✓ built in N s`
- Reporta tamaño del bundle principal

### Paso 2: Verificar sintaxis backend (rápido)
```powershell
cd "D:\NeuroSoftApp\neurosoft-backend"; python -m py_compile app/main.py
```
Si falla, ABORTA — no tiene sentido seguir si el backend no compila.

### Paso 3: Matar proceso anterior + build .exe
```powershell
Stop-Process -Name "NeuroSoft" -Force -ErrorAction SilentlyContinue
cd "D:\NeuroSoftApp"; python build.py --skip-frontend --skip-ollama
```

Usar `--skip-frontend` porque ya lo hicimos en el paso 1.
Usar `--skip-ollama` porque `OllamaSetup.exe` se distribuye **separado** dentro del instalador Inno Setup (NO bundleado dentro del .exe).

Verificar que `NeuroSoft.exe` pesa ~40-60 MB (NO 1.4 GB — eso sería corrupción por bundlear Ollama).

### Paso 4: Compilar instalador Inno Setup
```powershell
& "C:\Users\DESKTOP\AppData\Local\Programs\Inno Setup 6\ISCC.exe" "D:\NeuroSoftApp\installer\NeuroSoft.iss"
```
Espera mensaje "Successful compile". Confirma que `D:\NeuroSoftApp\dist\NeuroSoft-Setup.exe` se generó.

## Reporte final

```
✅ Build pipeline completo

| Artefacto                    | Tamaño  | Ubicación                                        |
|-----------------------------|---------|--------------------------------------------------|
| Frontend bundle             | XXX KB  | neurosoft-frontend/dist/                         |
| NeuroSoft.exe               | XX MB   | dist/NeuroSoft.exe                               |
| OllamaSetup.exe (separado)  | 1.3 GB  | vendor/ollama/                                   |
| NeuroSoft-Setup.exe (final) | 1.4 GB  | dist/NeuroSoft-Setup.exe ← listo para distribuir |

Tiempo total: ~XX segundos
```

## Verificaciones post-build (críticas)

1. `NeuroSoft.exe` debe ser **<100 MB** (si es >1 GB, Ollama se bundleó por error)
2. `NeuroSoft-Setup.exe` debe ser **~1.4 GB**
3. Manual PDF en `dist/` si fue generado previamente

Si algo falla, lista el error específico y detén el pipeline. No intentes continuar con errores.

## Variantes

- `/build rápido` — solo frontend + .exe, sin instalador (para iteración rápida)
- `/build completo` — todo + regenera PDF (`python docs/scripts/generate_manual_pdf.py`)
- `/build debug` — agrega `--clean` al build.py

## Errores comunes

- **"NeuroSoft.exe está en uso"** → ejecuta `Stop-Process -Name "NeuroSoft" -Force -ErrorAction SilentlyContinue` primero
- **"npm run build falla"** → verifica errores de import en frontend
- **"py_compile falla"** → revisa cambios recientes en backend
- **"ISCC.exe no encontrado"** → confirma ruta `C:\Users\DESKTOP\AppData\Local\Programs\Inno Setup 6\ISCC.exe`
