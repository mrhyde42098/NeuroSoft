# Informe de cierre — NeuroSoft App
**Fecha:** 6 de junio de 2026 (noche) 
**Alcance:** Consolidación post-PLAN_MAESTRO, OSS GitHub, Codex OSS, HC clínica, build beta.

---

## Resumen ejecutivo

NeuroSoft queda **empaquetado para beta** con instalador regenerado, **1016 tests pytest en verde**, frontend lint+build OK, y repositorio público preparado para mantenimiento OSS. Se corrigió el flujo de HC (4 pasos, screening aparte), se retiró material de capacitación del repo, y se envió solicitud **Codex para Open Source**.

---

## Entregables de build (verificados 6 jun 2026)

| Artefacto | Tamaño | Ruta |
|-----------|--------|------|
| Frontend `dist/` | ~2.1 MB (gzip ~57 KB main) | `neurosoft-frontend/dist/` |
| `NeuroSoft.exe` | **47.3 MB** | `dist/NeuroSoft.exe` |
| `NeuroSoft-Setup.exe` | ~1.34 GB | `dist/NeuroSoft-Setup.exe` |

Pipeline: `npm run build` → `py_compile` → `python build.py --skip-frontend --skip-ollama` → Inno Setup.

---

## Cambios clínicos / UX cerrados en esta sesión

| Tema | Qué se hizo |
|------|-------------|
| **HC 4 pasos** | Revertido wizard de 7 pasos; MMSE/escalas van en Screening, no en HC |
| **Informe Pro** | Restaurada sección «Resumen para la Familia» en variante `pro` (8 tests integración OK) |
| **GitHub OSS** | README badges, CONTRIBUTING, issue templates, script `abrir-todo-codex-oss.ps1` |
| **Material de capacitación** | Eliminado del repo + `.gitignore`; permanece solo en local |
| **Codex OSS** | Formulario enviado (org configurado, maintainer principal) |

---

## Métricas de calidad

| Métrica | Valor |
|---------|-------|
| pytest | **1016 passed** |
| ESLint | 0 warnings |
| Baremos | 173 pruebas, ~114k claves |
| Issues GitHub abiertos | 2 (roadmap público) |

---

## Pendiente real (no bloquea envío a beta testers)

| Prioridad | Item |
|-----------|------|
| P0 | Sprint REACTIVOS WISC/WAIS visuales (`docs/REACTIVOS_WISC_WAIS_PLAN.md`) |
| P0 | E2E manual: paciente → WISC → PDF Pro |
| P1 | QW-6 etiquetas pacientes, QW-8 backup programado |
| P1 | CI GitHub en verde (badges; requiere push con cambios backend/frontend) |
| P2 | OTP SMS consentimiento, RIPS XML, FHIR |

---

## Distribución beta

1. Enviar `dist/NeuroSoft-Setup.exe` (o solo `.exe` si no necesitan Ollama embebido).
2. Primera ejecución: cambiar contraseña admin.
3. Configurar SMTP en Ajustes → Comunicaciones para consentimiento por email.

---

## Repositorio

- **URL:** https://github.com/mrhyde42098/NeuroSoft 
- **Licencia:** Apache 2.0 
- **Maintainer:** @mrhyde42098
