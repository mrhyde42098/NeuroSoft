---
name: redisenar-informes
description: Implementa y mantiene el estándar visual de informes PDF NeuroSoft (IN&S + gráficas Pro sin bugs). OBLIGATORIO Composer 2.5 u Opus 4.8 para editar report_pro/. Usar cuando Johan pida rediseño PDF, bugs de superposición, plantillas o calidad del informe NPS.
---

# Rediseñar informes NeuroSoft

## Gate de modelo (OBLIGATORIO)

```yaml
minimum: ["composer-2.5", "claude-opus-4-8-thinking-high"]
forbidden_for_code: ["haiku", "flash", "gpt-4o-mini", "llama3.1:8b"]
routing:
  layout_charts_refactor: "claude-opus-4-8-thinking-high"
  ui_wiring_tests_docs: "composer-2.5"
```

Si la sesión usa un modelo inferior, **detener** y pedir a Johan cambiar a Composer u Opus antes de editar `report_pro/`.

La IA **no dibuja layout PDF** — solo ReportLab en código. La IA en `ai.py` asiste narrativa, no diseño.

## Lectura obligatoria (orden)

1. [`docs/REFERENCIAS_INFORMES_NPS.md`](../../docs/REFERENCIAS_INFORMES_NPS.md)
2. PDFs en [`docs/referencias-informes/`](../../docs/referencias-informes/)
3. [`neurosoft-backend/app/infrastructure/report_pro/base.py`](../../neurosoft-backend/app/infrastructure/report_pro/base.py)

## Estándar visual (IN&S + Pro)

- Header repetido: orden, fechas, paciente (estilo IN&S)
- Observación clínica **antes** de resultados cuantitativos
- Gráficas premium: KPI, discrepancias, perfil Z, campana, radar, tabla
- **Máximo 2 bloques gráficos por página** (`CHART_MODULES` + `MAX_CHART_BLOCKS_PER_PAGE`)
- Default permanente: `template=pro` en API, InformesPage, emails

## Archivos clave

| Archivo | Rol |
|---------|-----|
| `report_pro/base.py` | Layout, `CHART_MODULES`, paginación |
| `report_pro/charts.py` | Gráficos clínicos |
| `report_pro/variants/*.py` | Variantes especializadas |
| `report_service.py` | `generate_report_pdf`, default `pro` |
| `presentation/api/v1/reports.py` | Endpoint PDF |
| `presentation/api/v1/emails.py` | Adjunto PDF con `pro` |
| `InformesPage.jsx` | Selector plantilla + default pro |

## Workflow de implementación

### 1. Referencias
- Leer PDFs en `docs/referencias-informes/`
- Actualizar spec en `REFERENCIAS_INFORMES_NPS.md` si cambia el estándar

### 2. Código
- Variantes heredan `NeuroPDFGeneratorPro` con `CHART_MODULES` propio si aplica
- Cada módulo gráfico declara altura mínima; `_ensure_room` antes de dibujar
- No apilar 6 gráficos sin salto de página

### 3. Verificación

```bash
cd neurosoft-backend
pytest tests/integration/test_reports.py tests/integration/test_pdf_metadata.py -v
python ../docs/casos-clinicos/regenerar_muestras_minimas.py
```

Salida: **8 PDF** en `docs/samples/informes-audit/` (1 caso × 1 variante).

### 4. Limpieza
- Borrar PDF viejos en `docs/casos-clinicos/muestras-20-casos/` antes de regenerar
- No commitear PDF de casos ficticios masivos — solo las 8 muestras mínimas

## Matriz mínima de muestras

| Variante | Caso |
|----------|------|
| `pro` | caso_06 David López |
| `estandar` | caso_06 (legacy) |
| `pediatrico` | caso_01 Santiago |
| `medicolegal` | caso_10 Ricardo Pinzón |
| `junta_medica` | caso_16 Carlos Hernández |
| `inconcluso` | caso_07 Sofía |
| `paciente` | caso_01 Santiago |
| `therapy_closure` | fixture sintético |

## Tests críticos

```bash
pytest tests/integration/test_reports.py -v
```

Cualquier rediseño debe pasar antes de mergear.

## IA narrativa (secundario)

Presets en `ai.py` — narrativa final con Sonnet/4o, no Haiku. Ver tabla en `REFERENCIAS_INFORMES_NPS.md`.
