---
name: mejorar-informe-pdf
description: Plan estructurado para rediseñar el informe clínico PDF que genera NeuroSoft. El actual es genérico; queremos uno de calidad profesional con narrativa coherente, gráficos clínicos serios y diseño limpio. Usar cuando Johan pida trabajar en el informe PDF o cuando se quiera ofrecer una variante de plantilla nueva.
---

# Rediseño del informe clínico PDF

El informe PDF actual de NeuroSoft (generado por `neurosoft-backend/app/infrastructure/report_service.py`, ~1064 líneas) es funcional pero genérico. Hay que llevarlo a calidad profesional.

## Archivos clave

| Archivo | Rol |
|---|---|
| `neurosoft-backend/app/infrastructure/report_service.py` | Generador principal (ReportLab canvas API) |
| `neurosoft-backend/app/infrastructure/report_docx_service.py` | Variante DOCX (paralelo) |
| `neurosoft-frontend/src/data/ui.js` | `REPORT_TEMPLATES` — plantillas por tipo (clinico, pediátrico, inconcluso, retest, junta médica) |
| `neurosoft-backend/app/application/use_cases/reports_use_cases.py` | Use case que construye `ReportData` |
| `neurosoft-backend/app/presentation/api/v1/reports.py` | Endpoint que sirve el PDF |

## Estructura actual (NO romper)

`NeuroPDFGenerator.generate()` produce ~3-4 páginas:
1. Header institucional con logo
2. Datos sociodemográficos del paciente
3. Antecedentes (médicos, sensoriomotores, psiquiátricos, farmacológicos, traumáticos, quirúrgicos, tóxicos, alérgicos, terapéuticos, paraclínicos)
4. Funcionalidad / AVDs
5. Observación clínica (8 dominios)
6. **Resultados**: índices CI + gráfica Z horizontal + tabla de puntajes
7. Impresión diagnóstica (DSM-5/CIE-10)
8. Recomendaciones
9. Firma del profesional + footer

## Brechas identificadas (qué falta para que sea "el mejor")

### 🎨 Diseño visual
- **Tipografía**: usa Helvetica por defecto. Falta jerarquía clara (no hay diferencia visual marcada entre H1/H2/H3).
- **Paleta de colores**: tonos azules genéricos. NeuroSoft tiene una identidad (TEAL `#0D9488`, NAVY `#1E293B`) que el PDF NO refleja.
- **Espaciado**: bloques muy juntos, sin respiración visual.
- **No hay portada dedicada** — el header de institución comparte página con datos del paciente.
- **No hay tabla de contenidos** en informes largos.

### 📊 Gráficos clínicos
- La gráfica Z horizontal es básica (barras planas con franjas de color).
- **Faltan**:
  - Radar/spider chart de dominios cognitivos (lo más esperado en informes neuropsicológicos)
  - Distribución normativa con la curva gaussiana superpuesta al perfil del paciente
  - Gráfico de discrepancias entre índices (WISC: ICV vs IRP vs IMT vs IVP)
  - Indicadores visuales claros de fortalezas/debilidades

### 📝 Narrativa clínica
- **Texto telegráfico** — los dominios se llenan con plantillas auto-generadas que no fluyen como informe real.
- Falta una sección **"Síntesis clínica"** integradora (≠ impresión diagnóstica).
- No hay **comparativa Pre-Post** integrada al informe (existe RCI en la app, pero no aparece en el PDF de una sola evaluación).
- Las recomendaciones son lista plana; deberían estar **agrupadas por área** (escolar, ocupacional, terapéutica, médica) y por **prioridad**.

### 🏛️ Estándar profesional faltante
- Sin **encabezado/pie de página por sección** (estándar en informes médicos colombianos).
- Sin **numeración de página** en formato "Página X de Y" (Resolución 1995 lo pide).
- Sin **bloque de "Pruebas aplicadas"** al inicio (lista limpia con duración estimada).
- Sin **anexo de definiciones operativas** (qué significa "Z = -1.5", "RCI > 1.96").
- Sin **disclaimer profesional** estándar (validez del informe, alcance, limitaciones).

### 🇨🇴 Localización Colombia
- Falta cita de **Ley 1581 de 2012** y **Resolución 1995 de 1999** en el pie del informe.
- Falta espacio para **registro CIE-10** (algunos prestadores lo piden literal en el PDF, no solo en metadata).
- No diferencia entre **informe ambulatorio** vs **informe medicolegal** (este último requiere más detalle de validez de síntomas).

## Plan propuesto (sesión completa)

### Fase 1 — Análisis y diseño (30%)
1. Hablar con Johan sobre prioridades (¿más diseño, más narrativa, más rigor clínico?)
2. Buscar 2-3 ejemplos de informes neuropsicológicos referencia (Univ. Nacional, Univ. Javeriana, Hospital Militar) que sirvan de inspiración
3. Bocetar la nueva estructura (mockup textual)

### Fase 2 — Implementación de plantilla "Premium" (50%)
4. Crear nueva clase `NeuroPDFGeneratorPro` (no romper `NeuroPDFGenerator` actual — mantener compatibilidad)
5. Implementar portada dedicada con logo + datos paciente + ID evaluación
6. Implementar nueva tipografía (registrar fuentes serif para títulos, sans para cuerpo)
7. Implementar paleta TEAL/NAVY con bandas decorativas
8. Implementar nuevo header/footer (con numeración "X de Y", cita legal, ID evaluación)

### Fase 3 — Gráficos clínicos serios (30%)
9. **Radar/spider** de dominios cognitivos (usar reportlab.graphics.charts.spider)
10. **Curva gaussiana** con perfil Z superpuesto
11. **Gráfico de discrepancias** entre índices con líneas críticas (p<.05, p<.15)
12. Mantener la gráfica Z horizontal actual pero pulir colores y espacios

### Fase 4 — Narrativa clínica (20%)
13. Nueva sección **"Síntesis clínica integradora"** que cite resultados específicos (ej. "El paciente obtuvo CIT=87, dentro del rango promedio (PE 16-84). Sin embargo, destaca una asimetría entre ICV=98 e IMT=86 (diferencia de 12 puntos, p<.15)…").
14. Recomendaciones agrupadas por **área** y **prioridad** (Alta/Media/Baja).
15. Bloque de **"Pruebas aplicadas"** al inicio (tabla limpia con duración).
16. **Anexo de definiciones operativas** al final.

### Fase 5 — Variantes especializadas (10%)
17. Variante **medicolegal**: incluir validez de síntomas (Rey 15, TOMM), discusión de aculturación, escolaridad.
18. Variante **pediátrica**: incluir lenguaje observacional infantil, escala de cooperación, observaciones de juego.
19. Variante **junta médica**: 2 páginas máximo, sin antecedentes detallados, foco en conclusiones.

## Selectores en la UI

Después de implementar, agregar en `EvalResultsPage` un selector de plantilla:
- "Estándar" (la actual, para retrocompat)
- "Profesional Pro" (la nueva)
- "Medicolegal"
- "Pediátrica"
- "Junta médica"

## Tests críticos a no romper

```bash
pytest tests/integration/test_reports.py -v
```
El test verifica que el PDF se genera sin errores con datos completos. **Cualquier rediseño debe pasar este test antes de mergear.**

## Inspiración técnica

Bibliotecas ReportLab útiles:
- `reportlab.graphics.charts.spider.SpiderChart` — radar
- `reportlab.graphics.charts.linecharts.HorizontalLineChart` — curva
- `reportlab.graphics.charts.barcharts.HorizontalBarChart` — alternativas a la Z actual
- `reportlab.platypus.Table` con `TableStyle` rica — para tablas con celdas coloreadas

Fuentes a registrar (opcionales):
- Inter o Source Sans Pro (cuerpo)
- Manrope o Lora (títulos)
- Vía `pdfmetrics.registerFont(TTFont(...))`

## Output esperado

Al cabo de la sesión:
- Nueva variante "Pro" del informe lista, seleccionable desde la UI
- Test de integración pasando
- PDF de muestra en `docs/samples/MUESTRA_INFORME_PRO.pdf` para revisión visual de Johan
- Documentación en `neurosoft-backend/CLAUDE.md` de cómo agregar nuevas variantes

## Decisiones a confirmar con Johan al inicio

1. ¿Mantener `NeuroPDFGenerator` como "Estándar" o lo reemplazamos?
2. ¿Cuántas variantes implementar en esta sesión? (sugiero "Pro" + "Pediátrica" mínimo)
3. ¿Quiere registrar fuentes externas (Inter, Manrope) o usar Helvetica? (Helvetica bundleado, Inter más bonito pero requiere distribuir TTF)
4. ¿Algún informe real que quiera replicar como referencia?
