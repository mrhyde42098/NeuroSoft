# Auditoría integral consolidada A+B · NeuroSoft V2 · 5 jun 2026

**Fuentes:** Auditoría A (pasada 1) + Auditoría B (Composer pasada 2) + cruce `AUDIT_2026-06-06_FULL.md`  
**Baseline:** 1016 pytest · ESLint 0 warnings · build `.exe` 47.3 MB

## Veredicto consolidado

NeuroSoft V2 está **listo para beta cerrada** con P0 de cumplimiento (cifrado OS + audit append-only + Dashboard batch). Gap principal vs software forense: **SVT administrada completa** (TOMM ítem a ítem con estímulos).

## Backlog unificado (implementación jun-2026)

| P | Acción | Estado post-sprint |
|---|---|---|
| P0 | Política cifrado OS + backup | `docs/SEGURIDAD_DATOS_CLINICOS.md` |
| P0 | Trigger SQLite append-only `audit_log` | `engine.py` |
| P0 | Dashboard usa `/notifications/adherence/summary` | `DashboardPage.jsx` |
| P0 | `PRAGMA busy_timeout=5000` | `engine.py` |
| P1 | Validación Pydantic bounds PD | `score_bounds.py` + `scoring_dtos.py` |
| P1 | Ollama sanitiza PHI siempre | `ai.py` |
| P1 | ValidezPanel → observaciones | wiring EvalApply + Screening |
| P2 | Dark-mode HC/ScoreInput | parcial |
| P2 | FastAPI pin + orjson baremos | `requirements.txt` + `baremos_loader.py` |
| P3 | TOMM/Rey en ReactivePanel | ya existían; mejoras UI |
| P3 | SDMT en protocolo adulto mayor | ya en protocolo |
| UX | Cronómetro en guía clínica + pin posición | `FloatingTimer.jsx` |
| UX | Reactivos texto grande + ocultar todo | `ReactivePanel.jsx` |
| UX | FCRO overlay calificación | `ReactivePanel.jsx` + `FCRODisplay.jsx` |
| UX | Preview enfoques terapia ampliada | `TherapyPage.jsx` |
| NEXT | Enriquecer Centro Aprender | `docs/ROADMAP_APRENDER_ENRIQUECIMIENTO.md` |

## Notas de discrepancia A vs B (preservadas)

- **RIPS solo CIE-10:** correcto por norma vigente; no es bug.
- **SQLCipher vs BitLocker:** P0 documental; SQLCipher P1 si portabilidad `.db`.
- **Rate limit localhost:** útil si se expone puerto en LAN.
