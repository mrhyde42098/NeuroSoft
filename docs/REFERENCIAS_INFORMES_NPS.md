# Referencias y estándar visual — Informes NPS NeuroSoft

**Actualizado:** 5 jun 2026 · Estándar **IN&S + Pro sin bugs**

## Corpus de referencia

| Archivo | Descripción |
|---------|-------------|
| [`referencias-informes/IN&S_WISC_guia.pdf`](referencias-informes/IN&S_WISC_guia.pdf) | Gold standard Johan — informe WISC infantil IN&S (5 págs) |
| `referencias-informes/` | Agregar aquí PDFs adicionales (adulto, medicolegal) |

### Anatomía IN&S (extraída del PDF guía)

1. **Header repetido** — Orden No, Fecha atención, F. entrega, título informe
2. **Sociodemografía** — rejilla compacta (nombre, edad, escolaridad, remite, etc.)
3. **Antecedentes** — prosa densa (médicos, desarrollo, familiar)
4. **Observación clínica** — dominios en prosa **antes** de resultados
5. **Resultados** — tabla PD/PB + curva Z con leyenda
6. **Síntesis / I.Dx** — integración índices WISC + comparación previa
7. **Recomendaciones** — intervenciones específicas por proceso
8. **Legal** — disclaimer pericial colombiano (CPC, CIE-10, no pericial)

## Estándar NeuroSoft implementado

Híbrido **IN&S (layout clínico)** + **Pro (gráficas premium)**:

| Regla | Detalle |
|-------|---------|
| Orden secciones | Antecedentes → **Observación** → Resultados → Resumen ejecutivo → Síntesis |
| Gráficas | KPI, discrepancias, perfil Z, campana, radar, tabla |
| Paginación | Máx. **2 bloques gráficos por página** (`CHART_MODULES`) |
| Default | `template=pro` en API, InformesPage, emails |
| Header | Orden + fecha atención en cada página (no solo portada) |
| Legacy | `estandar` = generador histórico, solo selector "Clásico (legado)" |

### Archivos de implementación

- [`neurosoft-backend/app/infrastructure/report_pro/base.py`](../neurosoft-backend/app/infrastructure/report_pro/base.py)
- [`neurosoft-backend/app/infrastructure/report_pro/charts.py`](../neurosoft-backend/app/infrastructure/report_pro/charts.py)
- Skill: [`.claude/skills/redisenar-informes/SKILL.md`](../.claude/skills/redisenar-informes/SKILL.md)

## Muestras mínimas (8 PDF)

Regenerar con:

```bash
cd neurosoft-backend
python ../docs/casos-clinicos/regenerar_muestras_minimas.py
```

Salida: `docs/samples/informes-audit/{variante}_{slug}.pdf`

| Variante | Caso ficticio |
|----------|---------------|
| pro | caso_06 David López |
| estandar | caso_06 (legacy) |
| pediatrico | caso_01 Santiago |
| medicolegal | caso_10 Ricardo |
| junta_medica | caso_16 Carlos |
| inconcluso | caso_07 Sofía |
| paciente | caso_01 Santiago |
| therapy_closure | Ana Vega (terapia) |

Los PDF masivos en `docs/casos-clinicos/muestras-20-casos/` **no se conservan** — solo estas 8 muestras.

## Checklist anti-bug (aceptación visual)

- [ ] V1 Sin superposición texto/gráfico
- [ ] V2 Sin cortes mid-gráfico (salto de página limpio)
- [ ] V3 Jerarquía tipográfica clara
- [ ] V4 Máx. 2 bloques gráficos por página en resultados
- [ ] V5 Footer "Página X de Y" + normograma
- [ ] V6 Tabla puntajes legible (wrap en nombres largos)
- [ ] V7 Misma plantilla default en InformesPage y EvalResultsPage

## Modelos de IA

| Tarea | Modelo | Notas |
|-------|--------|-------|
| **Código/layout PDF** | Composer 2.5 u Opus 4.8 | Obligatorio — ver skill |
| Borrador observación | Flash / 4o-mini | UI borrador |
| Narrativa integradora final | Sonnet / GPT-4o | No Haiku para informe final |
| Layout PDF | **Nunca IA** | Solo ReportLab |

## Prompt maestro

```
Eres el agente de rediseño de informes NeuroSoft. OBLIGATORIO: modelo Composer 2.5 u Opus 4.8.

1. Lee docs/REFERENCIAS_INFORMES_NPS.md y todos los PDF en docs/referencias-informes/
2. Ejecuta el skill /redisenar-informes
3. El estándar es IN&S (layout clínico colombiano) + gráficas Pro (Z, campana, radar, KPI, discrepancias) SIN superposiciones
4. Observación clínica ANTES de resultados. Máximo 2 gráficos por página.
5. Unifica default a template=pro en API, InformesPage y emails
6. No uses Haiku/Flash/llama3.1:8b para editar report_pro/
7. Borra PDFs viejos en docs/casos-clinicos/muestras-20-casos/; regenera SOLO 8 muestras mínimas en docs/samples/informes-audit/
8. Verifica con pytest tests/integration/test_reports.py
9. El resultado de TU implementación es el estándar permanente
```

## Marco legal Colombia (pie de informe)

- Ley 1090/2006 · Ley 1581/2012 · Resolución 1995/1999
- Normograma versión `2026.06` (sincronizado frontend/backend)
