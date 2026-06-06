# Auditoría Integral NeuroSoft — Reporte Final
**Sprint V1-V5 · Junio 2026**

**Autor de cambios:** Johan Sebastián Salgado Sarmiento (software propietario)
**Auditor técnico:** NeuroSoft quality pipeline (3 subagentes)
**Estado:** ✅ 5/5 sprints completados
**Verificación:** 1010/1010 tests backend + ESLint limpio + 17 PDFs regenerados + rebuild completo

---

## Resumen ejecutivo

Auditoría sistemática del código clínico (frontend + backend) y los PDFs generados por la app contra los 10 protocolos fuente en PDF. Se identificaron, priorizaron y corrigieron **23 hallazgos** agrupados en 5 sprints (V1-V5), preservando 100% de los baremos (BD_NEURO_MAESTRA.json sin tocar valores), 100% de los tests pasando y 0 nuevas regresiones.

### Tabla de hallazgos V1-V5

| # | Severidad | Hallazgo | Sprint | Estado |
|---|---|---|---|---|
| 1 | ALTO | PDF: doble `_header()` en `draw_z_profile` dibujaba bandas semánticas 2 veces | V1 | ✅ Fix |
| 2 | ALTO | PDF: doble título "Discrepancias" (en chart_title + section_subtitle) | V1 | ✅ Fix |
| 3 | ALTO | PDF: overlap curva normal vs perfil Z en misma página | V1 | ✅ Fix |
| 4 | ALTO | PDF: valores Z se superponían con labels largos | V1 | ✅ Fix |
| 5 | ALTO | PDF: "Áreas para apoyar" strikethrough raro en `two_column_blocks` | V1 | ✅ Fix |
| 6 | MEDIO | PDF: demasiadas subsecciones (KPI + Discrepancias + Perfil Z + Semáforo + Curva + Radar + Tabla = 7 bloques) | V1 | ✅ Agrupado a 4 |
| 7 | ALTO | FCRO: elemento 3 era X completa; debe ser una sola diagonal ↘ | V2 | ✅ Fix |
| 8 | ALTO | FCRO: elemento 8 eran 4 líneas horizontales; deben ser verticales (persianas) | V2 | ✅ Fix |
| 9 | ALTO | FCRO: elemento 18 era una línea vertical; debe ser un cuadrado 20×20 | V2 | ✅ Fix |
| 10 | ALTO | Cubos: 14 patrones recreados "geográficamente análogos, no idénticos" sin disclaimer clínico-legal | V2 | ✅ Disclaimer |
| 11 | ALTO | WISC-IV Semejanzas: scoring 0-1-2 uniforme; ítems 1-2 deben ser 0-1 | V4 | ✅ Fix |
| 12 | ALTO | WISC-IV Semejanzas: 6+ ítems inventados mezclados con oficiales | V4 | ✅ Reemplazados |
| 13 | ALTO | WISC-IV Vocabulario: "Rivalidad" duplicado (n:14 y n:26) | V4 | ✅ Fix |
| 14 | MEDIO | WISC-IV Vocabulario: faltaban 4 ilustrados (Coche, Flor, Tren, Cubeta) | V4 | ✅ Agregados |
| 15 | ALTO | WISC-IV Comprensión: 21 preguntas inventadas; deben ser 18 oficiales | V4 | ✅ Reescrito |
| 16 | ALTO | NiWiscLN (Letras y Números) y NiWisReg (Registro) en INSTRUCCIONES pero NO en REACTIVOS | V4 | ✅ Agregados |
| 17 | ALTO | WAIS-III Semejanzas: scoring 0-1-2 uniforme; ítems 1-5 deben ser 0-1 | V4 | ✅ Fix |
| 18 | MEDIO | WAIS-III Semejanzas: 19 pares sin textos, sólo "Par N" | V4 | ✅ Reemplazados con pares oficiales |
| 19 | ALTO | BNT (Boston Naming Test) sin `requires_license: true` (requiere PAR Inc.) | V4 | ✅ Agregado |
| 20 | MEDIO | Key `"AdBusSim + ViBusSim"` con `+` y espacios (frágil) | V4 | ✅ Refactor a 2 tests |
| 21 | ALTO | Motor: sin validación edad vs `test_id` (riesgo clínico de baremo inapropiado) | V5 | ✅ Warning no-bloqueante |
| 22 | MEDIO | 7 JSONs de protocolos en `Capacitaciones Clínicas\protocolos\` con `institucion: "IN&S SAS"` | V5 | ✅ Sanitizado a "" |
| 23 | BAJO | Docstring `strategies.py` con conteos desactualizados (168 pruebas; real 173) | V5 | ✅ Actualizado |

---

## V1 — Bugs visuales PDF

### Cambios
- **`neurosoft-backend/app/infrastructure/report_pro/charts.py`** — reescrito completo (~700 líneas)
  - `draw_z_profile`: una sola llamada a `_header()` (antes 2×)
  - Bandas semánticas dibujadas una vez por bloque (antes duplicadas)
  - Marcador prominente (círculo 2.4pt) en barras Z
  - `chart_title()` único sin section_title duplicado
  - Leyenda compacta al pie
  - `fit_text_to_width` en labels de pruebas largas
  - `draw_normal_curve`: banda verde -1 a +1 sombreada con `setFillAlpha`
  - Ticks verticales coloreados por paciente sobre la curva
  - `draw_bell_curve_with_ci` (nueva): campana centrada en CIT + bandas IC 90/95% translúcidas
  - `draw_discrepancies`: barras desde 0, líneas críticas p<.05 (sólida) y p<.15 (punteada)
  - Etiquetas `p<.05 / p<.15 / n.s.` con color semántico
  - `draw_domain_radar`: 7 anillos concéntricos Z=-3..+3, zona normal verde
  - Polígono paciente teal con `setFillAlpha(0.18)`, vértices coloreados por Z
  - `draw_ci_kpi_row` (nueva): tarjetas KPI grandes
  - `draw_domain_traffic_light` (nueva): semáforo ● + Z̄ + banda
- **`neurosoft-backend/app/infrastructure/report_pro/base.py`** — `_section_resultados` reescrita
  - KPI row + Discrepancias en mismo bloque
  - Perfil Z (con `chart_title` interno, sin `section_subtitle` redundante)
  - Curva normal con CIT
  - Radar
  - Tabla detallada
  - Eliminados `section_subtitle` duplicados
- **`neurosoft-backend/app/infrastructure/report_pro/helpers.py`** — `two_column_blocks` corregido para pasar `x` específico a cada `block_header` (antes ambos titles colisionaban en `L.margin`, causando strikethrough falso)

### Verificación
- 33/33 tests de `test_reports.py` + `test_pdf_metadata.py` pasan
- 7/7 variantes PDF (`estandar / pro / pediatrico / medicolegal / junta_medica / inconcluso / paciente`) generan PDFs válidos

---

## V2 — Estímulos visuales fidelidad

### Cambios
- **`neurosoft-frontend/src/data/PatronFCRO.jsx`** — geometría Rey-Osterrieth corregida
  - Elemento 3: era la X completa → ahora una sola diagonal ↘
  - Elemento 8: eran 4 líneas horizontales → ahora 4 líneas verticales (persianas)
  - Elemento 18: era una línea vertical → ahora un cuadrado 20×20 adosado al vértice inf-izq
  - Comentario histórico `§fcro-fix-3-elementos (2026-06-05)` documenta los 3 fixes
- **`neurosoft-frontend/src/data/PatronesCubos.jsx`** — disclaimer prominente
  - Header del archivo: "⚠️ AVISO IMPORTANTE — Estos 14 diseños son recreaciones ESQUEMÁTICAS (no idénticas) de los patrones con copyright activo (WISC-IV y WAIS-III, Pearson Education)"
  - `CubosPattern` muestra banner ámbar "Esquemático — use el kit oficial para aplicación clínica"
  - `CubosPoster` muestra bloque de advertencia al inicio

### Verificación
- ESLint pasa limpio (0 warnings)
- Build frontend OK (8.94s)

---

## V3 — Gráficas rediseñadas

Todas las mejoras de V3 están en el rewrite de `charts.py` descrito en V1. Resumen visual de las nuevas funciones:

| Función | Mejora clave |
|---|---|
| `draw_z_profile` | Bandas semánticas únicas, marcadores prominentes, leyenda compacta |
| `draw_normal_curve` | Banda verde -1 a +1 sombreada, ticks coloreados por paciente |
| `draw_bell_curve_with_ci` | Campana centrada en CIT + IC 90/95% translúcidas |
| `draw_discrepancies` | Barras desde 0, líneas p<.05 (sólida) y p<.15 (punteada) |
| `draw_domain_radar` | 7 anillos Z=-3..+3, polígono translúcido, vértices coloreados |
| `draw_ci_kpi_row` | Tarjetas KPI grandes (CIT, ICV, IRP, IMT, IVP) |
| `draw_domain_traffic_light` | Semáforo ● con Z̄ y banda |

---

## V4 — Reactivos fidelidad clínica

### Cambios en `neurosoft-frontend/src/data/clinical.js`

| Test | Cambio |
|---|---|
| `NiWiscSem` (Semejanzas WISC-IV) | Scoring por ítem: 1-2 = [0,1]; 3-23 = [0,1,2]. 23 pares en orden de aplicación WISC-IV |
| `NiWiscVoc` (Vocabulario WISC-IV) | 4 ilustrados (Coche, Flor, Tren, Cubeta) + 28 verbales. "Rivalidad" duplicado eliminado |
| `NiWiscCom` (Comprensión WISC-IV) | 18 preguntas oficiales reescritas (no las 21 inventadas) con categoría por pregunta |
| `NiWiscLN` (Letras y Números) | **NUEVO** — 10 niveles × 3 trials, maxTime 90s. Estructura 3-L+1-N escalonada |
| `NiWisReg` (Registro de Símbolos) | **NUEVO** — 5 series cronometradas 45s |
| `AdSemWais` (Semejanzas WAIS-III) | Scoring por ítem: 1-5 = [0,1]; 6-19 = [0,1,2]. 19 pares oficiales |
| `BNT` (Boston Naming Test) | `requires_license: true` + `license_publisher: "Pro-Ed / Lippincott Williams & Wilkins"` + `license_authors: "Kaplan, Goodglass, Weintraub (2001)"` |
| `"AdBusSim + ViBusSim"` | Refactor a 2 tests separados: `AdBusSim` y `ViBusSim` (sin `+` frágil) |

### Verificación
- ESLint pasa limpio
- 7 índices WISC-IV/ICV/IRP/IMT/IVP ya están en motor — los 2 nuevos subtests solo agregan captura, no baremos nuevos

---

## V5 — Backend hardening

### Cambios
- **`neurosoft-backend/app/domain/clinical_engine/engine.py`**
  - Nuevo módulo: `_EDAD_RANGO_POR_PREFIJO` con (Ni: 4-17, Ad: 16-64, Vi: 50-100) y `_ESCALAS_SIN_RANGO_ETARIO` (escalas autoadministradas)
  - Función helper `_rango_edad_esperado_para_test(test_id)`
  - Validación no-bloqueante en `_score_single`: si edad del paciente está fuera del rango del prefijo del test_id, emite warning en `output.metadata` y en `advertencias` del ResultadoPrueba
  - El warning aparece en el PDF para que el clínico verifique baremo apropiado
- **`neurosoft-backend/app/domain/clinical_engine/strategies.py`**
  - Docstring actualizado: 173 pruebas (no 168), 114,586 claves de baremo
  - Conteo de pruebas por estrategia con `~` para reflejar aproximación real
  - Banner `§v5-auditoría (2026-06-05)` documenta la obsolescencia del conteo anterior
- **JSONs de protocolos sincronizados** (7 archivos en `Capacitaciones Clínicas\protocolos\` y `neurosoft-frontend\src\data\protocols\`)
  - `"institucion": "IN&S SAS"` → `"institucion": ""` en los 7 archivos
  - Eliminado `"autores_protocolo": [...]` con cualquier mención a IN&S
  - PDFs fuente no editados (corromperían el binario); documentado en este informe

### Verificación
- 1010/1010 tests pasan (`pytest tests/ -q`)
- 1 test ajustado: `pd_ajuste` → `pd_ajustado` (typo mío, restaurado)
- 33/33 tests PDF pasan
- ESLint pasa limpio
- Frontend rebuild OK (8.94s)
- PyInstaller OK: `dist\NeuroSoft.exe` 47.05 MB (cumple regla <100 MB, sin bundlear Ollama)
- Inno Setup OK: `dist\NeuroSoft-Setup.exe` 1376.78 MB (≈1.4 GB, correcto)
- 17 PDFs de muestra regenerados con todos los fixes V1-V5

---

## Estado de baremos (BD_NEURO_MAESTRA.json)

**NO se modificó `data/BD_NEURO_MAESTRA.json`**, salvo las 3 ediciones realizadas en rondas previas (auditoría Excel→motor, ya documentadas en `docs/casos-clinicos/AUDITORIA_EXCEL_VS_MOTOR.md`):

- 10 tests Grober legacy eliminados (formato `50P/50S/50U` incompatible)
- 1 bug `AdFCRO_Rey` edad 45 corregido
- Backup en `data/BD_NEURO_MAESTRA.backup-pre-auditoria-excel.json`

Los cambios V1-V5 son puramente de:
- **Presentación** (PDF, gráficos, estímulos visuales)
- **Frontend** (REACTIVOS, INSTRUCCIONES, keys de tests)
- **Validación** (warning edad, no cambio de baremo)
- **Documentación** (sincronización JSONs, docstring)

---

## Hallazgos NO resueltos en este sprint (recomendados para próximos)

1. **Cubos WISC-IV / WAIS-III — copyright activo**
   - Aunque agregamos disclaimer, los 14 patrones son recreaciones geométricas, no idénticos.
   - **Recomendación:** adquirir el kit oficial Pearson para clínica real; en la app mantener solo los esquemáticos como referencia visual.
2. **30+ placeholders `Ítem N` en MMSE, Matrices, Conceptos, Información, Aritmética, etc.**
   - Muchos tests no tienen reactivos capturados en `clinical.js` (sólo número de ítem sin texto).
   - **Recomendación:** usar el PDF de estímulos extraído en `C:\Users\DESKTOP\AppData\Local\Temp\opencode\pdf_text\` para reescribir `Ítem N` con contenido real.
3. **Typos nombres en BD_NEURO**
   - `AdWAISC` "COMRENSI_N" (con N mayúscula) → debería ser "COMPRENSIóN"
   - `AdWAISICP` "ORGNIZACI_N" → debería ser "ORGANIZACIÓN"
   - **Recomendación:** corregir en próxima sprint, con re-validación de los 17 casos ground truth.

---

## Comandos de verificación

```bash
# Backend
cd D:\NeuroSoftApp\neurosoft-backend
python -m pytest tests/ -q                    # → 1010 passed
python -m pytest tests/integration/test_reports.py -v   # → 33 passed

# Frontend
cd D:\NeuroSoftApp\neurosoft-frontend
npx eslint src --max-warnings 0               # → sin output (limpio)
npm run build                                  # → built in ~9s

# Validación clínica
cd D:\NeuroSoftApp\neurosoft-backend
venv\Scripts\python ..\docs\casos-clinicos\validar_casos.py
venv\Scripts\python ..\docs\casos-clinicos\regenerar_samples_v5.py

# Build desktop
cd D:\NeuroSoftApp
python build.py --skip-frontend --skip-ollama # → NeuroSoft.exe 47 MB
& "C:\Users\DESKTOP\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer\NeuroSoft.iss
                                              # → NeuroSoft-Setup.exe 1.4 GB
```

---

## Archivos modificados (resumen)

### Backend
- `neurosoft-backend/app/domain/clinical_engine/engine.py` — validación edad + banner §v5-auditoria
- `neurosoft-backend/app/domain/clinical_engine/strategies.py` — docstring actualizado
- `neurosoft-backend/app/infrastructure/report_pro/charts.py` — **reescrito completo** (V1+V3)
- `neurosoft-backend/app/infrastructure/report_pro/base.py` — `_section_resultados` reescrita
- `neurosoft-backend/app/infrastructure/report_pro/helpers.py` — `two_column_blocks` fix strikethrough
- `neurosoft-backend/app/presentation/api/v1/reservorio.py` — IN&S → institucional (V0)

### Frontend
- `neurosoft-frontend/src/data/clinical.js` — REACTIVOS reescritos (V4)
- `neurosoft-frontend/src/data/PatronFCRO.jsx` — geometría corregida (V2)
- `neurosoft-frontend/src/data/PatronesCubos.jsx` — disclaimer prominente (V2)
- `neurosoft-frontend/src/data/protocols/*.json` — sincronizados y sanitizados (V5)

### Datos
- `Capacitaciones Clínicas\protocolos\*.json` — sanitizados de "IN&S SAS" a ""
- `docs/casos-clinicos/regenerar_samples_v5.py` — **nuevo**, regenera 17 muestras
- `docs/casos-clinicos/muestras-20-casos/*.pdf` — 17 PDFs regenerados

### Documentación
- `docs/ARQUITECTURA.md` — IN&S → institucional
- `docs/seguridad/MODELO_AMENAZAS.md` — IN&S → institucional
- `docs/AUDITORIA_PDFs.md` — **este informe** (nuevo)

### Builds
- `dist\NeuroSoft.exe` — 47.05 MB (rebuilt)
- `dist\NeuroSoft-Setup.exe` — 1376.78 MB (rebuilt)

---

**Conclusión:** 23/23 hallazgos del sprint V1-V5 corregidos. 1010/1010 tests pasan. Build desktop completo. PDFs de muestra regenerados. No hay regresiones. Baremo maestro preservado.
