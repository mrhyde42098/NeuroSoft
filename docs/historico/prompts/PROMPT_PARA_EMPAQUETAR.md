# NeuroSoft — Prompt para Empaquetar .exe

## 🎯 Tarea Única

**Empaquetar NeuroSoft.exe** usando PyInstaller.

## 📂 Ubicación del Proyecto

```
D:\NeuroSoftApp\
├── neurosoft-frontend/    (React/Vite SPA — LISTO)
├── neurosoft-backend/     (FastAPI — LISTO)
├── build.py               (Script PyInstaller)
└── dist/                  (Salida esperada)
```

## 🚀 Instrucción

Ejecuta **una sola vez**:

```bash
cd D:\NeuroSoftApp
python build.py --skip-ollama
```

**Tiempo esperado:** ~60-90 segundos

**Resultado esperado:** `D:\NeuroSoftApp\dist\NeuroSoft.exe` (39-40 MB)

## ✅ Validación Post-Build

1. El archivo `D:\NeuroSoftApp\dist\NeuroSoft.exe` debe existir y ser > 39 MB
2. No debe haber errores en la salida de PyInstaller
3. El .exe no necesita ser ejecutado — solo asegúrate de que se generó

## 📦 Archivos Necesarios para Enviar a Beta Tester

Una vez que `NeuroSoft.exe` esté en `dist/`:

1. **NeuroSoft.exe** — Aplicación compilada
2. **INSTRUCCIONES_BETA_TESTER.md** — Guía para beta testing
3. **README.md** — Información general del proyecto

Comprimir estos 3 archivos en un .zip y enviar.

## 📝 Nota

- Frontend y backend ya están listos (compilados/validados)
- No hagas cambios de código
- Solo empaqueta
- Si falla, revisa que Node.js y Python 3.11+ estén en PATH

---

**¡Eso es todo!** 🎉

