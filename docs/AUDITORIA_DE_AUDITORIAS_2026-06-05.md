# Auditoría de auditorías — NeuroSoft App
**5 de junio de 2026**

Revisión sistemática de roadmaps, audits, sprints y carpetas tras trabajo disperso en múltiples chats/sitios.

---

## Resumen ejecutivo

| Acción | Cantidad |
|---|---|
| Archivos movidos desde raíz | 5 audits + 1 xlsm + 1 script build |
| Carpetas nuevas | `docs/historico/`, `archive/` |
| Documentos maestros creados | `INDICE_MAESTRO`, `ESTADO_VIVO`, `CARPETAS_RAIZ` |
| `CLAUDE.md` actualizado | Sí (jun 2026) |
| Skill nueva | `/organizar-repo` |
| Borrados | **0** (solo archivado) |

---

## Hallazgo principal

Había **duplicación de verdad**: roadmaps en `planning/` decían "EN IMPLEMENTACIÓN" para features ya terminadas (QW-1–7, M-1–8, N1–P5). Las IAs nuevas releían roadmaps viejos y proponían trabajo ya hecho.

**Solución:** `docs/ESTADO_VIVO.md` como única fuente de estado. Los roadmaps quedan como archivo histórico.

---

## Inventario de auditorías

| Archivo | Fecha | Ubicación actual | ¿Superseded? |
|---|---|---|---|
| AUDIT_2026-06-05 | 5 jun | `historico/audits/` | **Vigente** (más completo) |
| AUDIT_2026-06-03 | 3 jun | `historico/audits/` | Parcialmente |
| AUDIT_2026-06-01 | 1 jun | `historico/audits/` | Parcialmente |
| AUDIT_2026-05-31 | 31 may | `historico/audits/` | Sí |
| AUDIT_2026-05-26 | 26 may | `historico/audits/` | Sí |
| AUDITORIA_PDFs | jun | `docs/` | Vigente V1–V5 |
| audits/* 2025-05 | may 25 | `docs/audits/` | Histórico |

**Regla:** para trabajo nuevo, leer solo `AUDIT_2026-06-05` + `PUNTO_INFLEXION`.

---

## Roadmaps — verificación contra código

### Completados (marcados en ESTADO_VIVO)

- QW-1 a QW-4, QW-7 ✅
- M-1 a M-8 ✅ (mayo 2026 sprint)
- N1, N3, P2–P5 ✅
- V0–V6 sprints ✅
- GitHub Actions CI ✅ (existía; CLAUDE.md decía "faltar")

### Parciales

- QW-5 (share password, no PIN SMS)
- QW-8 (backup manual, sin schedule)
- N2 / glosario InformesPage
- Placeholders REACTIVOS (~16 bloques `requires_protocol_text`)

### Pendientes reales

- QW-6 etiquetas pacientes
- Dark mode evaluation flow
- HL7/FHIR, RIPS, multi-tenant (largo plazo)

---

## Carpetas raíz — propósito verificado

| Carpeta | Veredicto |
|---|---|
| `neurosoft-backend` / `frontend` | ✅ Activas |
| `docs` | ✅ Reorganizada |
| `.claude` | ✅ 14 skills + 1 agente |
| `mcp-servers` | ⚙️ Opcional (baremos MCP) |
| `Capacitaciones Clínicas` | ✅ Protocolos fuente |
| `session_logs` | Vacía, gitignored — OK |
| `data/` (raíz) | ⚠️ Solo `last_update.json` prueba OTA — huérfano |
| `scripts/` (raíz) | Vacía tras archivar |
| `__pycache__` | Ignorar (gitignore) |
| `.benchmarks` | Cache pytest |

---

## Archivos movidos (jun 2026)

```
RAÍZ → docs/historico/audits/
  AUDIT_2026-05-26.md
  AUDIT_2026-05-31.md
  AUDIT_2026-06-01.md
  AUDIT_2026-06-03.md
  AUDIT_2026-06-05.md

docs/ → docs/historico/sprints/
  PLAN_SPRINT_ESTETICA_UI.md
  PLAN_SPRINT_ESTETICA_V2.md

docs/historic-prompts/ → docs/historico/prompts/
  (3 archivos PROMPT_*.md)

RAÍZ → archive/legacy/
  MISISTEMAV1.xlsm
  build_installer.py

scripts/ → archive/scripts-oneoff/
  fix_frontend_warnings.py
  fix_frontend_warnings_v2.py
```

---

## Skills y agentes — estado

| Recurso | Estado | Acción |
|---|---|---|
| 14 skills en `.claude/skills/` | ✅ Completas | Ninguna duplicada |
| `clinical-engine-reviewer` | ✅ | Mantener |
| **`organizar-repo`** | 🆕 Creada | Para futuras limpiezas |
| `exportar-sesion` | ✅ | Usar al cerrar chat |

**No crear** skills duplicadas de audit/build/investigar — ya existen (ver CLAUDE.md).

---

## CLAUDE.md — cambios aplicados

1. Sección **"Punto de entrada IA"** con orden de lectura.
2. Tests: 27 → **1011**.
3. Sprint V0–V6 documentado.
4. "Podría faltar" reemplazado por puntero a `ESTADO_VIVO.md`.
5. Comando `/organizar-repo` añadido.

**Actualizado también:** `neurosoft-backend/CLAUDE.md` (173 pruebas + puntero a `ESTADO_VIVO.md`).

---

## Para la próxima IA

```
1. Lee docs/PUNTO_INFLEXION_2026-06-05.md
2. Lee docs/ESTADO_VIVO.md
3. NO re-implementes QW/M/N/P sin verificar estado
4. NO pongas AUDIT_*.md en la raíz — usar docs/historico/audits/
5. Al cerrar sprint: actualizar ESTADO_VIVO.md
```

---

## Recomendaciones Johan (opcionales)

1. **Commit** esta reorganización con mensaje tipo: `docs: reorganizar auditorías y crear ESTADO_VIVO`
2. **Revisar** `neurosoft-backend/docs/` — 3 RESUMEN_*.md duplican info de mayo
3. **Mover** `data/last_update.json` raíz → `archive/` si no es producción
4. ~~**Eliminar** carpeta vacía `docs/historic-prompts/`~~ ✅ Hecho (jun 2026)
5. **Trimestral:** correr `/organizar-repo` antes de releases

---

*Fin auditoría de auditorías · NeuroSoft App*
