# NeuroSoft — Prompt para Nueva Sesión

## 📋 Estado del Proyecto (Mayo 2026)

Este es el prompt para continuar desarrollo en una nueva sesión o Codex. El proyecto es un **sistema integral de evaluación neuropsicológica clínica** para consultorios en Colombia (frontend React/Vite + backend FastAPI/SQLAlchemy/SQLite).

---

## 🎯 Qué se ha implementado

### Versión actual: **v2026-05 (Mayo)**

**Stack:**
- Frontend: React 18 + Vite 5.4, Tailwind CSS, Recharts
- Backend: FastAPI, SQLAlchemy 2.0, SQLite, Alembic
- Build: PyInstaller (Windows .exe 39.4 MB)

**Ubicación del repositorio:** `D:\NeuroSoftApp\`
```
├── neurosoft-frontend/    (React/Vite SPA)
├── neurosoft-backend/     (FastAPI + domain logic)
└── build.py               (PyInstaller script)
```

---

## 🔧 Cambios Recientes (Esta Sesión)

### 1. **Instrumentos de Screening Nuevos** (`screening.js`)
- **FAB** (Frontal Assessment Battery): 6 subtareas, detección de disfunción frontal
- **IES-R** (Impact of Event Scale Revised): 22 ítems, 3 subescalas (Intrusión/Evitación/Hiperactivación)
- **PCL-5** (PTSD Checklist DSM-5): 20 ítems, correspondencia 1:1 con criterios DSM-5

### 2. **Corrección STAI**
- `maxScore`: 80 → **120** (40 ítems × 3)
- Severity thresholds: 0-37 (bajo), 38-59 (moderado), 60-79 (elevado), 80-120 (muy alto)
- Subescalas: Estado (20 ítems) + Rasgo (20 ítems), cada una con cutoff=19

### 3. **ScreeningPage.jsx — Soporte de Subescalas**
- `computeResult()` calcula puntajes parciales por subescala
- `renderLikert()` muestra headers de sección (Estado/Rasgo, Part A/B)
- Panel de resumen de subescalas con alertas de cutoff individual

### 4. **ClinicalInterpretationPanel.jsx Mejorado**
- Detección de **WAIS-III**: ICP, ICG, ICC (índices alternativos)
- 3 nuevos patrones clínicos:
  - **DEA Verbal**: ICV bajo vs IRP alto → dislexia/TDL
  - **DEA Visoespacial**: IRP bajo vs ICV alto → NLD
  - **Secuela Neurológica**: TCE/ACV pattern detection
- Mejora de DCL: detecta amnésico vs multi-dominio
- Texto clínico generado por párrafos (mejor formato)
- Panel ICG/ICC separado con tooltips

### 5. **report_enrichment.py Enriquecido**
- Nueva función: `detectar_patrones_cognitivos(resultados, edad)`
- Detecta automáticamente: TDAH, TCL/CDHS, TEA, DI, Discapacidad Intelectual, Secuela neurológica
- `EnrichmentResult.patrones_cognitivos`: nuevo campo con patrones detectados
- `reports.py`: pasa `resultados_pruebas` al enrichment para detección automática

### 6. **Base de Conocimiento Clínico** (`datosClinicos.js`)

**RECOMMENDATIONS_LIB** (nuevos):
- `tept`: psicoterapia (TF-CBT/CPT/PE/EMDR), manejo familiar, escolar, evaluación de riesgo
- `long_covid_cognitivo`: pacing, umbral de fatiga, ajustes laborales, rehabilitación graduada

**DIAGNOSTIC_ALGORITHMS** (nuevos):
- `tept`: 7 criterios DSM-5 (A-G), interpretación por nivel
- `dcl`: Petersen criteria + Winblad revisado, seguimiento recomendado

**CUADROS_CLINICOS**: 14 cuadros (incluye TEPT)

**DSM5_DIAGNOSES**: 
- F431: TEPT + F438C (TEPT complejo CIE-11)
- U099: Post-COVID / Long COVID
- F068: TNC leve por condición médica

**PROTOCOL_SUGGESTIONS**:
- `adolescente.por_sospecha`: trauma → [PCL-5, IES-R, CAPS-5]
- `adulto_joven.por_sospecha`: trauma, long_covid incluidos
- `adulto_mayor.por_sospecha`: trauma, long_covid incluidos

### 7. **Selector de Screening** (ScreeningPage.jsx)
- Nuevo grupo: **"Trauma / PTSD"** con IES-R, PCL-5

---

## 📦 Build

**Comando:** `python build.py --skip-ollama`
**Resultado:** `D:\NeuroSoftApp\dist\NeuroSoft.exe` (39.4 MB)

**Tiempo de build:** ~66 segundos

---

## 🚀 Para la Próxima Sesión

### Posibles Mejoras (Roadmap):
1. **STAI — Inversión de ítems**: Los ítems marcados con `*` son inversos (puntuación = 4 - respuesta). El sistema actualmente NO invierte; necesita UI para señalar inversión manual o automatizar.

2. **SRS-2** (Social Responsiveness Scale): Útil para TEA en todos los grupos etarios

3. **AUDIT** (Alcohol Use Disorders Identification Test): Importante en evaluaciones forenses

4. **BRIEF-2**: Executive functions parent/teacher report (2-5 años)

5. **FAQ** (Functional Activities Questionnaire): Ya existe en `PROTOCOL_SUGGESTIONS` pero podría mejorarse la presentación

6. **ClinicalInterpretationPanel — Memoria**: Detectar patrones Grober-Buschke bajo (memoria episódica afectada selectivamente)

7. **Wizard de Evaluación Forense**: Paso a paso para cálculo de capacidad, validez de síntomas, etc.

8. **Rehabilitación Cognitiva — Nuevas Actividades**:
   - Entrenamiento de memoria prospectiva
   - Entrenamiento de funciones ejecutivas
   - Pacing / Fatiga management para Long COVID

### Testing Priorities:
- IES-R y PCL-5 en casos reales de trauma
- FAB en demencias vs TEC
- Patrones de ClinicalInterpretationPanel en WAIS-III (validación cross-test)
- report_enrichment con resultados reales (verificar que patrones = observación clínica)

---

## 📂 Archivos Críticos

| Archivo | Propósito | Última Actualización |
|---|---|---|
| `screening.js` | Definición de todos los instrumentos de tamizaje | ✅ Session actual |
| `datosClinicos.js` | RECOMMENDATIONS_LIB, DIAGNOSTIC_ALGORITHMS, CUADROS_CLINICOS, DSM5_DIAGNOSES, PROTOCOL_SUGGESTIONS | ✅ Session actual |
| `ScreeningPage.jsx` | Aplicación de formularios (likert_flat, binary_domains) | ✅ Session actual |
| `ClinicalInterpretationPanel.jsx` | Panel de interpretación automática de perfil cognitivo | ✅ Session actual |
| `report_enrichment.py` | Enriquecimiento de informe con patrones cognitivos | ✅ Session actual |
| `reports.py` | Endpoint `/enrichment/{eval_id}` — integra report_enrichment.py | ✅ Session actual |
| `EvalResultsPage.jsx` | Página de resultados — incluye ClinicalInterpretationPanel | Session anterior |
| `EvalApplyPage.jsx` | Administración de test + cronómetro + CONDUCTAS | Session anterior |

---

## 🔍 Verificación Pre-Sesión

Antes de empezar en nueva sesión, verificar:

```bash
# Frontend compila
cd neurosoft-frontend && npm run build

# Backend syntax OK
python -m py_compile neurosoft-backend/app/application/use_cases/report_enrichment.py
python -m py_compile neurosoft-backend/app/presentation/api/v1/reports.py

# Frontend + Backend tests
cd neurosoft-frontend && npm run test:e2e  # si existen

# Build exe
python build.py --skip-ollama
```

---

## 📞 Contacto / Notas

- **Usuario**: JSS (jssalgadosa@unal.edu.co)
- **Preferencia**: Español, sesiones largas, implementación sin confirmación previa
- **Build final**: Siempre ejecutar `python build.py --skip-ollama` al final

---

## 🎓 Próximas Mejoras Sugeridas

1. **UI para Inversión de Ítems en STAI**: Checkbox o radio automático
2. **Alertas en ClinicalInterpretationPanel**: Cuando patrón detectado ≠ diagnóstico en HC
3. **Exportación de Patrones**: Incluir patrones_cognitivos en PDF informe
4. **Protocolo por Sospecha Mejorado**: Link directo desde ClinicalInterpretationPanel → ScreeningPage
5. **Dashboard de Cambio**: Seguimiento de mejora/empeoramiento entre evaluaciones

---

**Versión de este prompt:** 2026-05-12
