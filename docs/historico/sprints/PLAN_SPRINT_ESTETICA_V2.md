# Plan Sprint Estética V2 — REVISIÓN MAYOR (2026-06-03)

**Estado:** Pendiente de aprobación
**Reemplaza:** `docs/PLAN_SPRINT_ESTETICA_UI.md` (versión subdimensionada)
**Autor:** Claude + Johan

---

## 🚨 Feedback del propietario (resumen)

| # | Área | Queja | Severidad |
|---|---|---|---|
| 1 | **PDF** | "Letras unas encima de otras, no me gusta la fuente ni la estética" | 🔴 **CRÍTICO** |
| 2 | **Casos clínicos** | "Cuando te pedí los pacientes era incluyendo pruebas, escalas, perfiles, para que los reportes salieran completos" | 🔴 **CRÍTICO** |
| 3 | **Casos — edge cases** | "Por ejemplo algún caso que haya desistido de seguir, otro que se fue de emergencia, la idea es poner a trabajar todo el flujo" | 🔴 **CRÍTICO** |
| 4 | **IA** | "Luego si tenemos que pulir mucho mucho la IA" | 🟡 **ALTO** |
| 5 | **Screening** | "Dejar las escalas en panel vertical o algo así" | 🟡 **ALTO** |
| 6 | **Estilo general** | "Muchísimos cambios del estilo que no se si ya esté en el plan" | 🟡 **ALTO** |

---

## 🔍 Diagnóstico técnico (PDF bug)

### Bug 1: Fuentes custom NO cargadas
- **Síntoma visual:** aspect ratio de Helvetica (sans) con anchos de glifo grandes → español con tildes/ñ queda apretado.
- **Causa:** `app/assets/fonts/` no existe. `theme.ensure_fonts_registered()` retorna `False` y cae a Helvetica/Times-Roman built-in.
- **Confirmado en vivo:** `using_custom_fonts() = False`

### Bug 2: Line-height insuficiente en `field_pair`
- **Ubicación:** `app/infrastructure/report_pro/helpers.py:228-249`
- **Síntoma visual:** "Psiquiátricos" se monta sobre "Médicos", "Familiares" sobre "Neurológicos", valores de un renglón sobre labels del siguiente.
- **Causa:** `return y - size * 1.5` después de dibujar. Si el valor es multilinea o los labels son largos, las filas adyacentes colisionan.
- **Causa agravante:** `wrap_text` (línea 45) usa heurística `chars_per_line = max_width / char_width` sin medir con `pdfmetrics.stringWidth` real, así que subestima/sobrestima ancho y desbalancea columnas.

### Bug 3: Anchura de columna mal calculada
- `two_column_layout(items, x, y, column_w=240, gap=16)` — pero page width = 511.27 (después de margins). 240+16+240=496 OK, pero `value_w = column_w - label_w - 4 = 240 - 90 - 4 = 146`. Si el label "Antecedentes psiquiátricos" mide > 90, **se desborda a la siguiente columna**.

### Bug 4: Sin header/footer consistente
- `kpi_card` recorta el label a 18 chars (`label[:18]`) y la interpretación a 22 — etiquetas como "Comprensión Verbal" se truncan a "Comprensión Verb".

---

## 📋 Plan V2 — 4 sprints expandidos (6-8 semanas)

### SPRINT A (1 semana): PDF PROFESIONAL — arreglar lo urgente

**Objetivo:** PDFs sin overlap, tipografía premium, layout robusto. No tocar lógica de negocio.

#### A1. Instalar fuentes TTF reales
- Descargar `Inter` y `Lora` de Google Fonts (oficial).
- Colocar en `app/assets/fonts/`:
  - `Inter-Regular.ttf`, `Inter-Bold.ttf`, `Inter-Italic.ttf`
  - `Lora-Regular.ttf`, `Lora-Bold.ttf`, `Lora-Italic.ttf`
- Bundlear las TTFs en el .exe (PyInstaller `--add-data`).
- Verificar `using_custom_fonts() == True` en build de producción.

#### A2. Reescribir `helpers.py` con `pdfmetrics.stringWidth` real
```python
def measure_text(text: str, font_name: str, size: float) -> float:
    """Ancho REAL en puntos usando ReportLab."""
    return pdfmetrics.stringWidth(text, font(font_name), size)

def wrap_text_exact(text, max_w, font_name, size) -> list[str]:
    """Word-wrap exacto midiendo con pdfmetrics."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if measure_text(candidate, font_name, size) <= max_w:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
```

#### A3. Reescribir `field_pair` con line-height dinámico
```python
def field_pair(c, label, value, x, y, *, label_w=110, value_w=200, size=TYPE.body_sm):
    # Mide label exacto
    actual_label_w = measure_text(f"{label}:", FONT_SANS_BOLD, size) + 4
    actual_label_w = max(actual_label_w, label_w)  # respeta mínimo
    
    # Wrap value con ancho exacto
    lines = wrap_text_exact(str(val), value_w, FONT_SANS, size)
    line_h = size * 1.55  # más espacio
    
    draw_text(c, f"{label}:", x, y, font_name=FONT_SANS_BOLD, ...)
    y -= size + 2  # baseline label
    for i, line in enumerate(lines):
        draw_text(c, line, x, y - i * line_h, ...)
    return y - len(lines) * line_h - 4  # padding
```

#### A4. Reescribir `two_column_layout` con grid vertical estricto
- Renderizar campo-por-campo, midiendo altura real de cada bloque.
- Las dos columnas se balancean al final, no a la mitad.
- Padding mínimo 8pt entre filas.

#### A5. Aumentar `kpi_card` sin truncar
- `w` mínimo 140pt (era 110).
- Quitar `label[:18]`, calcular truncado solo si excede `w - 16`.

#### A6. Header/footer con paginación "X de Y"
- Ya existe `_make_numbered_canvas_class`, verificar que aplica a TODAS las variantes.

#### A7. Auditoría visual — generar 20 PDFs
- Re-ejecutar script de 20 casos.
- Comparar visualmente cada uno.
- Iterar hasta que **0 overlap**, **0 truncado**, **toda sección con espacio**.

#### A8. Tests visuales automatizados (Playwright PDF)
- Renderizar PDF → convertir a PNG (`pdf2image`) → pixelmatch contra baseline.
- Threshold: 0.5% pixels diff.
- Cubre: portada, sección resultados, sección recomendaciones, anexo.

**Entregables A:**
- ✅ TTFs Inter + Lora cargadas en todos los builds
- ✅ `helpers.py` reescrito con medición exacta
- ✅ 0 overlap, 0 truncado, header/footer consistente
- ✅ 20 PDFs regenerados y verificados
- ✅ 5+ tests visuales Playwright

**Estimación:** 4-5 días.

---

### SPRINT B (1-2 semanas): CASOS CLÍNICOS REALES + FLUJO END-TO-END

**Objetivo:** 20+ casos que ejerciten el flujo completo (HC → Evaluación → Informe → Recomendaciones → Edge cases). Sirven como:
- Tests de regresión clínica
- Demos para beta testers
- Validación del workflow completo backend→frontend

#### B1. Modelo de caso completo
**Nuevo schema:** `neurosoft-backend/scripts/case_factory/case.py`
```python
@dataclass
class CasoClinico:
    id: str
    paciente: dict  # 35+ campos como ya existen
    historia_clinica: dict  # HC completa
    motivo_consulta: str
    bateria: list[str]  # pruebas a aplicar
    puntajes: dict[str, int]  # PD por prueba
    observaciones: list[dict]  # 4-6 obs por dominio
    hipotesis_dx: list[str]  # CIE-10 tentativos
    recomendaciones: list[dict]  # con etiquetas [ESCOLAR][TERAPÉUTICA][FAMILIAR]
    resultado_esperado: dict  # para validación
    notas_internas: str  # para el clínico, no aparece en PDF
```

#### B2. 25 casos cubriendo flujos completos
**Distribución:**
- 6 infantil (8-15a) — TDAH, dislexia, TEA, depresión, DI, alto funcionamiento
- 8 adulto joven (18-45a) — control, ACV, postparto, TDAH adulto, TEPT, TCE, bipolar, ansiedad
- 7 adulto mayor (60+a) — normal, DCL, Alzheimer, demencia mixta, depresión geri, ACV, vascular
- **2 edge cases** especiales:
  - **Caso 21 — Deserción:** Paciente adulto joven, primeraconsulta + screening, abandona antes de evaluación completa. HC parcial + 1 observación + cierre "INCONCLUSO" + alerta en UI.
  - **Caso 22 — Emergencia:** Paciente adulto mayor, evaluación en curso, ideación suicida activa detectada → C-SSRS ALTO + plan de seguridad activado + remisión a psiquiatría + informe pausado.
- **2 casos premium**:
  - **Caso 23 — Junta médica:** Paciente con accidente laboral, demanda en curso, informe `medicolegal` con validez de síntomas y alcance.
  - **Caso 24 — Cierre terapia:** Paciente adulto con 12 sesiones, pre-post comparación + narrativa de progreso + plan de mantenimiento.
- **1 caso stress test:**
  - **Caso 25 — Batería completa:** TODAS las pruebas del catálogo (40+), para validar que el motor no se rompe con batería máxima.

#### B3. Validación de cada caso
- Antes de generar PDF, ejecutar el motor y comparar `resultado_esperado` con `engine.score()`.
- Si difiere, **rechazar el caso** y revisar baremos.
- Solo se aceptan casos que pasan el motor con valores esperados.

#### B4. Cada caso tiene TODOS los entregables
- Paciente en BD (35+ campos)
- HC completa (60+ campos)
- Evaluación con batería + puntajes + resultados del motor
- 4-6 observaciones clínicas (cualitativas por dominio)
- Recomendaciones etiquetadas
- PDF generado (variante apropiada: `pro`/`pediatrico`/`medicolegal`/`junta_medica`/`inconcluso`)
- PDF de HC sola
- Plan terapéutico (si aplica)
- Snapshot JSON (para tests de regresión)

#### B5. Tests E2E de los 25 casos
- `tests/integration/test_e2e_casos_reales.py`
- Para cada caso: ejecutar el flujo backend completo, generar PDF, verificar que el archivo > 0 bytes y se abre.
- Si el caso es "deserción", verificar que el endpoint retorna 409 al intentar generar informe.
- Si el caso es "emergencia", verificar que la alerta C-SSRS aparece en `GET /api/v1/patients/{id}`.

**Entregables B:**
- ✅ 25 casos clínicos completos (vs 20 incompletos)
- ✅ Modelo `CasoClinico` reutilizable
- ✅ 25 PDFs + 25 HCs + 25 snapshots JSON
- ✅ Tests E2E automatizados
- ✅ Cobertura de edge cases (deserción, emergencia)
- ✅ Documento `docs/casos-clinicos/25_CASOS_FLUJO_COMPLETO.md`

**Estimación:** 5-7 días.

---

### SPRINT C (1-2 semanas): IA POLISH + SCREENING VERTICAL + UX

**Objetivo:** Pulir la integración de IA, reorganizar screening, mejorar UX general.

#### C1. IA — re-arquitectura de prompts
- **Estado actual:** 6 prompts especializados en `ai_prompts.py` con sanitización PHI.
- **Mejoras:**
  - Validar que el output de IA se integre LIMPIAMENTE en el informe (no como bloque pegado).
  - Agregar 4 prompts nuevos:
    - `preguntas_padres` — guidance para entrevista con padres
    - `recomendaciones_escolares` — adaptaciones curriculares
    - `plan_seguimiento` — cronograma de re-evaluación
    - `carta_remision` — borrador de remisión a especialista
  - Mejorar parsing de tags `[ESCOLAR]`, `[TERAPÉUTICA]`, `[FAMILIAR]`, `(alta/media/baja)`.
  - Logging mejorado en `ai_logs` — capturar latencia, tokens, prompt version, score de calidad (0-1).
  - Feedback loop — clínico marca "útil/no útil" en UI → entrenar corpus futuro.

#### C2. IA — UI mejorada
- En `EvalResultsPage`, sección "IA Assistant" en panel colapsable a la derecha.
- Dropdown de 10 prompts con descripción (1 línea).
- Streaming de respuesta (mostrar mientras se genera, no esperar).
- "Copiar al portapapeles" + "Insertar en informe" + "Descartar".
- Indicador visual de "IA usada en este informe" en cabecera.

#### C3. Screening — layout vertical (panel)
**Estado actual:** `ScreeningPage.jsx` con escalas en grid horizontal.
**Cambio:** Cada escala en su propia fila con:
- Título + descripción corta
- Botón "Aplicar"
- Resultado compacto (1 línea)
- Botón "Ver detalle" → modal con baremos

```
┌────────────────────────────────────────────────────────┐
│ 📋 BDI-II — Inventario de Depresión Beck               │
│    Autoaplicado · 21 ítems · 5 min                     │
│                                            [ Aplicar ] │
│    Resultado: 18/63 (Depresión moderada)               │
│                                            [ Detalle ] │
├────────────────────────────────────────────────────────┤
│ 📋 PHQ-9 — Cuestionario de Salud del Paciente          │
│    ...                                                  │
└────────────────────────────────────────────────────────┘
```

**Archivo:** Refactor `ScreeningPage.jsx`. Componente nuevo `ScreeningScaleRow.jsx`.

#### C4. Screening — wizard mejorado
- Ya existe `ScreeningWizard.jsx`. Mejorar UX:
  - Barra de progreso visual (no solo texto "Paso 3 de 7").
  - Skip inteligente — si una escala no aplica por edad/población, ofrecer skip con razón.
  - Auto-guardado en cada paso.

#### C5. UX general — pulir
- `DashboardPage`: widgets con loading skeleton.
- `PatientsPage`: tabla con filtros guardados, ordenamiento por columnas.
- `EvalResultsPage`: tabs (Resultados / Observaciones / Recomendaciones / IA) con persistencia.
- `InformesPage`: preview embebido del PDF antes de descargar.
- `ConfigPage`: tabs con iconos + mejor jerarquía.

#### C6. Empty states
- Cuando no hay pacientes: ilustración + CTA "Crear primer paciente".
- Cuando no hay evaluaciones: ilustración + CTA "Iniciar evaluación".
- Cuando no hay informes: ilustración + CTA "Generar informe".

#### C7. Feedback visual
- Toast en cada acción (success, error, warning, info).
- Confirmaciones destructivas con `useConfirm` (ya existe) para TODAS las acciones de eliminación.
- Progress bar en operaciones largas (generar PDF, backup).

**Entregables C:**
- ✅ 4 prompts nuevos en `ai_prompts.py`
- ✅ UI de IA mejorada (streaming, insertar, copiar)
- ✅ Screening vertical (componente nuevo)
- ✅ Wizard de screening con skip inteligente
- ✅ Empty states para todas las páginas principales
- ✅ Toast system centralizado
- ✅ +30 tests frontend (Playwright)

**Estimación:** 6-8 días.

---

### SPRINT D (1 semana): REPORTES — REDISEÑO COMPLETO

**Objetivo:** Llevar el PDF a calidad de "consultorio premium internacional".

#### D1. Nuevo layout del PDF
- **Portada rediseñada:** logo configurable (de `ConfigInstitucion`), nombre del paciente, foto opcional, fecha, nombre del profesional, QR (futuro portal paciente).
- **Tipografía:** Inter (sans) para UI/tablas, Lora (serif) para títulos/narrativa. Ver Sprint A.
- **Colores:** Paleta NeuroSoft (teal/navy) configurable.
- **Espaciado:** 1.5x line-height, padding generoso, sin overlap.
- **Header:** Banda teal superior con logo + nombre clínica.
- **Footer:** Número de página + código de verificación + cita "Ley 1090/2006".

#### D2. Gráficos premium
- **Radar/Spider chart** del perfil cognitivo multi-dominio.
- **Heatmap** baremo vs paciente (por edad/sexo).
- **Barras agrupadas** Pre/Post intervención.
- **Curva normal** con posición del paciente marcada.
- **Gráfico de discrepancias** (ICV vs IRP, etc.) con asteriscos significativos.

#### D3. Variantes mejoradas
- **`pro`** (estándar) — adulto ambulatorio, 6-10 páginas.
- **`pediatrico`** — infantil, agrega "Historia del Desarrollo".
- **`medicolegal`** — peritaje, validez + alcance + disclaimer reforzado.
- **`junta_medica`** — 1-2 páginas, conclusiones + recomendaciones.
- **`inconcluso`** — sello + razón + nota clínica (ya existe).
- **`familiar`** — NUEVO. Lenguaje accesible para padres/cuidadores.
- **`seguimiento`** — NUEVO. Solo Pre/Post comparativo.

#### D4. Narrativa mejorada
- 3 audiencias: técnico (psicólogo), paciente, familiar.
- Conectores enriquecidos (no "Sin embargo" repetido 10 veces).
- Bloques opcionales según completitud de la evaluación.

#### D5. Tema visual configurable
- Logo, color primario, tipografía (default Inter/Lora) desde `ConfigInstitucion`.
- Marca de agua opcional (texto diagonal o logo) — desactivado por defecto.

**Entregables D:**
- ✅ Layout PDF rediseñado (no overlap, premium)
- ✅ 5 gráficos nuevos (radar, heatmap, barras, curva, discrepancias)
- ✅ 7 variantes de informe operativas
- ✅ Narrativa 3 audiencias
- ✅ Tema configurable por institución
- ✅ 25 PDFs regenerados con nuevo diseño

**Estimación:** 5-6 días.

---

## 📅 Cronograma propuesto

| Semana | Sprint | Foco | Esfuerzo |
|---|---|---|---|
| **1** | **A** | PDF profesional (TTFs + medición exacta + 0 overlap) | 4-5 días |
| **2-3** | **B** | 25 casos completos + edge cases + tests E2E | 5-7 días |
| **3-4** | **C** | IA polish + screening vertical + UX general | 6-8 días |
| **5-6** | **D** | Rediseño PDF completo + gráficos + variantes | 5-6 días |

**Total:** 20-26 días (~5 semanas). El plan anterior era 3 semanas subdimensionadas.

---

## 🎯 Criterios de éxito

| Métrica | Meta |
|---|---|
| **PDF — overlap** | 0 en 25 PDFs verificados |
| **PDF — truncado** | 0 (etiquetas, valores, interpretaciones) |
| **PDF — fuente** | Inter + Lora cargadas en build |
| **Casos completos** | 25/25 con HC + batería + obs + recomendaciones |
| **Edge cases** | 2 (deserción, emergencia) automatizados |
| **IA — prompts** | 10 totales, todos con sanitización PHI |
| **Screening — vertical** | 1 fila por escala, sin grid horizontal |
| **Tests** | 0 regresión + 50+ nuevos |
| **A11y** | WCAG 2.1 AA mantenido |
| **Bundle size** | < 500KB gzipped frontend |

---

## ⚠️ Riesgos nuevos identificados

1. **TTFs en .exe:** PyInstaller debe bundlearlas correctamente. Si se olvidan, fallback a Helvetica = bug regresivo.
   - **Mitigación:** Smoke test post-build que verifica `using_custom_fonts() == True`.

2. **25 casos vs 1 semana:** Generar 25 casos válidos es costoso. Cada caso requiere validación de baremos.
   - **Mitigación:** Script `case_factory` reutilizable + validación automática.

3. **IA — calidad de output:** La IA puede generar texto clínico impreciso.
   - **Mitigación:** Disclaimer obligatorio + clínico debe aprobar antes de incluir en informe.

4. **Screening — backward compat:** Cambiar el layout puede romper tests existentes.
   - **Mitigación:** Mantener API del componente, cambiar solo presentación.

5. **PDF redesign — riesgo de regresión visual:** Cambiar fonts/layout puede romper PDFs antiguos.
   - **Mitigación:** Versión de plantilla en metadatos, regenerar todos los PDFs de demo.

---

## 💡 Decisiones pendientes para aprobar

1. **¿Empezar por Sprint A (PDF profesional) — Recomendado?**
   - Resuelve la queja #1 de forma visible e inmediata.
   - 1 semana.
2. **¿Sprint B (25 casos) antes de C/D?**
   - Recomendado: los nuevos diseños (Sprint D) deben probarse contra casos completos.
3. **¿Aceptar las TTFs Inter+Lora como dependencias del proyecto?**
   - Son OFL (SIL Open Font License), uso comercial libre.
4. **¿Agregar `framer-motion` (10KB) o quedarse con CSS?**
   - **Recomendación:** CSS para mantener bundle pequeño.
5. **¿`jspdf` o ReportLab para generación de PDFs?**
   - **Recomendación:** ReportLab (ya está, es la fuente de verdad clínica). NO migrar.

---

## 📂 Archivos a crear/modificar (resumen)

| Archivo | Cambio | Sprint |
|---|---|---|
| `app/assets/fonts/*.ttf` | NUEVO (6 archivos) | A |
| `app/infrastructure/report_pro/helpers.py` | REWRITE (medición exacta) | A |
| `app/infrastructure/report_pro/theme.py` | Verificar registro TTF en build | A |
| `app/infrastructure/report_pro/base.py` | Ajustar header/footer | A |
| `app/infrastructure/report_pro/narrative.py` | Pulir textos | A, D |
| `app/infrastructure/report_pro/charts.py` | Agregar radar, heatmap | D |
| `app/infrastructure/report_pro/variants/familiar.py` | NUEVO | D |
| `app/infrastructure/report_pro/variants/seguimiento.py` | NUEVO | D |
| `neurosoft-backend/scripts/case_factory/case.py` | NUEVO | B |
| `neurosoft-backend/scripts/case_factory/*.py` | 25 casos | B |
| `neurosoft-backend/tests/integration/test_e2e_casos_reales.py` | NUEVO | B |
| `app/domain/clinical_engine/ai_prompts.py` | +4 prompts | C |
| `app/infrastructure/ai_service.py` | Streaming + métricas | C |
| `neurosoft-frontend/src/app/evaluation/ScreeningPage.jsx` | Refactor vertical | C |
| `neurosoft-frontend/src/app/evaluation/ScreeningScaleRow.jsx` | NUEVO | C |
| `neurosoft-frontend/src/app/ia/AIAsistente.jsx` | Streaming + insertar | C |
| `neurosoft-frontend/src/ui/Toaster.jsx` | NUEVO | C |
| `neurosoft-frontend/src/ui/EmptyState.jsx` | NUEVO | C |
| `tests/e2e/pdf-visual/*.spec.js` | NUEVO (5+) | A, D |

---

## 🚀 Para empezar mañana

1. **Checkpoint** (ya hecho) — congelado en `a28cfeb`.
2. **Aprobar este plan** (o ajustar).
3. **Empezar Sprint A (PDF profesional)** — instalar TTFs, reescribir `helpers.py`.
4. **Regenerar 1 PDF muestra** para validación visual inmediata.
5. **Iterar** con feedback de Johan.

---

**Esperando aprobación para empezar Sprint A.**
