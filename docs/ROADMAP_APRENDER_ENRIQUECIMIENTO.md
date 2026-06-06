# Roadmap — Centro de Aprendizaje (cerrado 6 jun 2026)

## Objetivo

Centro de aprendizaje clínico integrado en NeuroSoft — contenido curado offline + catálogo vivo de baremos.

## Entregado P0/P1

| Área | Entrega | Estado |
|------|---------|--------|
| Protocolos | `ProtocolosPage.jsx` + 6 protocolos en `protocolosClinicos.js` | ✅ |
| Hub | 8 módulos destacados + dashboard progreso Leitner/quizzes | ✅ |
| Quizzes | 6 cuestionarios (WISC, Neuronorma, ética, validez, WAIS, demencias) | ✅ |
| Simulador | 11 casos (3 originales + 8 nuevos por población) | ✅ |
| Artículos | Renderer markdown con tablas | ✅ |
| Biblioteca | Enlaces DOI/URL en recursos clave | ✅ |
| Manual PDF | Sección 6 Centro de Aprendizaje + beta genérico | ✅ |
| Build | `build.py` auto: shards + PDF + Inno | ✅ |

## Entregado P2 (6 jun 2026)

| Área | Entrega | Estado |
|------|---------|--------|
| Glosario | 120 términos (+20: RIPS, CIE-11, ENI-2, SVT/TOMM, ADOS-2…) | ✅ |
| Artículos | +5 editoriales (MoCA Colombia, Neuronorma, informe NPS, SVT/TOMM, Res. 1995) | ✅ |
| Rutas guiadas | `aprenderPaths.js` — 4 itinerarios + progreso localStorage | ✅ |
| Biblioteca | Favoritos y leídos (`ns_biblioteca_fav`, `ns_biblioteca_leidos`) | ✅ |
| API backend | `GET /api/v1/aprender/stats` + `/paths` + manifest JSON | ✅ |
| Tests | `tests/unit/test_aprender_api.py` | ✅ |
| Manual PDF | Conteos P2 actualizados | ✅ |

## Criterios de aceptación

- [x] Glosario ≥120 términos con fuente
- [x] 11 artículos editoriales
- [x] 4 rutas de estudio guiadas
- [x] Favoritos/leídos biblioteca
- [x] API aprender sin auth (metadata pública)
- [x] ESLint sin errores nuevos
- [x] Manual PDF actualizado
- [x] Build completo automatizado
