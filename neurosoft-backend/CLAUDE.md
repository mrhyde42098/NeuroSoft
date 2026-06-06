# CLAUDE.md — NeuroSoft Backend v3
## Contexto para auditoría con Claude Code (Opus)

---

## QUÉ ES ESTE PROYECTO

**NeuroSoft** es un sistema de evaluación neuropsicológica clínica para consultorios pequeños (2-5 psicólogos) en Colombia. Es software médico real que genera informes clínicos. Una falla silenciosa en el cálculo de un CI puede producir un diagnóstico incorrecto.

Backend: FastAPI + SQLAlchemy + SQLite. Clean Architecture real (domain / application / infrastructure / presentation).

---

## COMANDOS ESENCIALES

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr servidor
uvicorn app.main:app --reload --port 8000

# Correr TODOS los tests
pytest tests/ -v --tb=short

# Tests solo unitarios (sin BD)
pytest tests/unit/ -v --tb=short -m unit

# Tests de integración (con BD en memoria)
pytest tests/integration/ -v --tb=short -m integration

# Test con coverage
pytest tests/ --cov=app --cov-report=term-missing

# Verificar sintaxis de un archivo
python3 -m py_compile app/path/al/archivo.py

# Migraciones Alembic
alembic upgrade head        # aplicar todas las migraciones
alembic revision --autogenerate -m "descripcion"  # crear nueva
alembic history --verbose   # ver historial
```

---

## ARQUITECTURA — REGLAS CRÍTICAS

```
app/
├── domain/clinical_engine/    ← NÚCLEO. No sabe de HTTP ni BD.
│   ├── strategies.py          ← 15 estrategias de cálculo neuropsicológico
│   ├── engine.py              ← Motor principal (ClinicalEngine)
│   ├── baremos_loader.py      ← Carga BD_NEURO_MAESTRA.json en memoria
│   ├── factory.py             ← Mapea tipo_calculo → Strategy
│   └── interpretation_engine.py ← Textos clínicos por dominio
├── application/use_cases/     ← Orquesta dominio + repositorios
├── infrastructure/            ← SQLAlchemy, reportlab, auth, scheduler
└── presentation/api/v1/       ← Endpoints FastAPI (solo HTTP, CERO lógica)
```

**REGLA ABSOLUTA:** Ningún cambio en `strategies.py` o `engine.py` sin verificar que los tests pasan. Estos calculan escalares clínicos reales.

**NUNCA modificar:** `data/BD_NEURO_MAESTRA.json` (**173 pruebas**, ~114.586 claves de baremo). Es la fuente de verdad clínica. Si detectas un posible error en los datos, **PREGUNTAR PRIMERO** antes de modificar.

**Estado del proyecto:** leer `../docs/ESTADO_VIVO.md` y `../docs/PUNTO_INFLEXION_2026-06-05.md` antes de proponer features.

---

## BASE DE DATOS CLÍNICA — ESTRUCTURA

`data/BD_NEURO_MAESTRA.json` estructura:
```json
{
  "baterias": {
    "infantil":      { "NiWiscDC": { "id", "nombre", "tipo_calculo", "baremos": {...} }, ... },
    "adulto_joven":  { "AdWAISV": {...}, ... },
    "adulto_mayor":  { "ViTMTA": {...}, ... }
  }
}
```

### Formato de baremos por tipo_calculo:

| tipo_calculo | Formato clave | Formato valor | Ejemplo |
|---|---|---|---|
| `rango_puntaje` | `"{año}{bracket}{pd}"` | `escalar` (int) | `"100330": 9` |
| `wais_range` | `"{rango_edad}{pd}"` | `escalar` (int) | `"25344200": 9` |
| `desconocido` | `"{rango_am}{pd}"` | `escalar` (int) | `"50561237": 6` |
| `z_score` | `"{edad}"` | `[media, sd]` | `"10": [16.3, 5.7]` |
| `suma_a_indice` | `"{suma_escalares}"` | `CI` (int) | `"26": 93` |
| `escolaridad_pc50` | `"{edad}{esc_code}"` | `[edad, esc, pc50]` | `"28S": [28, "S", 6]` |
| `puntaje_directo_a_t` | `"{pd}"` | `T_score` (int) | `"3": 57` |
| `puntaje_doble_resultado` | `"{pd}"` | `[PE, Percentil]` | `"15": [85, 75]` |
| `clasificacion_fija` | `"{pd}"` | clasificacion (str) | `"15": "DL"` |
| `edad_sexo` | `"{banda}{sexo}"` | `[sexo, banda, media, sd]` | `"910H": ["H", 910, 9.93, 6.38]` |

---

## ESTRATEGIAS — CONTEXTO CLÍNICO

### `rango_puntaje` (65 pruebas — WISC-IV, ENI-2, K-ABC, etc.)
Busca el escalar en `baremos[key]` donde key = `{año}{bracket_meses}{pd}`.
- **bracket de meses:** 0-3m → "03", 4-7m → "47", 8-11m → "811"
- Ejemplo: niño 10a 5m, PD=30 → key = "104730"
- **ATENCIÓN:** Los escalares WISC-IV van del 1 al 19 (media=10, sd=3)

### `wais_range` (20 pruebas — WAIS-III + Neuronorma indices)
Busca en `baremos["{rango_edad}{pd}"]`.
- Rangos: 16-19, 20-24, 25-34, 35-54, 55-69, 70-00
- Ejemplo: adulto 28a, PD=42 → key = "253442"
- CI compuestos WAIS van de ~55 a ~155

### `desconocido` (33 pruebas — Neuronorma Colombia AM)
Adulto Mayor. Busca en `baremos["{rango_am}{pd}"]`.
- Rangos AM: 5056, 5759, 6062, 6365, 6668, 6971, 7274, 7577, 7880, 8190
- Ejemplo: 65a, PD=237 en ViTMTA → key = "6062237"
- **AJUSTE ESCOLARIDAD:** Se suma +N al PD antes de buscar para Analfabeta/Prim.Inc
- Valores en `BD_NEURO_MAESTRA.json` en `adulto_mayor["_ajustes_escolaridad"]`

### `z_score` (10 pruebas — NiTMTA, NiTMTB, AdTMT_AB, AdFCRO_Rey, etc.)
`Z = (PD - media) / sd`, donde `[media, sd] = baremos[str(edad)]`

### `suma_a_indice` (14 pruebas — índices WISC-IV y WAIS-III)
`CI = baremos[str(suma_escalares)]`
- WISC-IV ICV suma 3 escalares → CI (escala: 40-160)
- WISC-IV CIT suma todos los índices → CI global

### `escolaridad_pc50` (5 pruebas — AdDPros, AdDReg, AdRDI, ViDeno, ViSem)
Código escolaridad: P=Primaria, S=Secundaria, U=Universitaria
Key = `"{edad}{esc_code}"`

---

## INFORMES PDF — PLANTILLAS Y VARIANTES

NeuroSoft genera el informe clínico PDF desde el endpoint:

```
POST /api/v1/reports/pdf/{eval_id}?template=<variante>
```

Dos generadores conviven:

| Generador | Archivo | Cuándo |
|---|---|---|
| `NeuroPDFGenerator` (Estándar) | `app/infrastructure/report_service.py` | Histórico — retrocompat con builds antiguos. `template=estandar` (default). |
| `NeuroPDFGeneratorPro` + variantes | `app/infrastructure/report_pro/` | Diseño premium. Paleta TEAL/NAVY, portada dedicada, gráficos (radar, gaussiana, discrepancias), narrativa integradora. |

### Variantes disponibles

| `template` | Clase | Notas |
|---|---|---|
| `estandar` | `NeuroPDFGenerator` | Layout clásico, sin portada dedicada. |
| `pro` | `ProGenerator` | Ambulatorio adulto/escolar. Todas las secciones. |
| `pediatrico` | `PediatricGenerator` | Agrega "Historia del Desarrollo" + observación de juego/cooperación. |
| `medicolegal` | `MedicoLegalGenerator` | Agrega validez de síntomas, aculturación, alcance del informe. |
| `junta_medica` | `JuntaMedicaGenerator` | 1-2 páginas, sin portada, foco en conclusiones. |
| `inconcluso` | `InconclusoGenerator` | Sello "INCONCLUSO" + razón categórica + nota clínica. |

### Cómo agregar una nueva variante Pro

1. **Crear** `app/infrastructure/report_pro/variants/<nombre>.py`:
   ```python
   from ..base import NeuroPDFGeneratorPro
   class MiVarianteGenerator(NeuroPDFGeneratorPro):
       VARIANT_LABEL = "Mi Variante"
       VARIANT_SUBTITLE = "Informe Neuropsicológico — Mi Caso"
       USE_COVER = True       # False para variantes ejecutivas
       INCLUDE_ANNEX = True

       def _build_pages(self, c, data):
           # Sobreescribir si necesitas reordenar/agregar secciones.
           # Si no, el default produce: portada + sociodemo + motivo +
           # pruebas + antecedentes + observación + resultados + síntesis
           # + impresión + recomendaciones + anexo + firma.
           super()._build_pages(c, data)
   ```

2. **Registrar** el dispatcher en `app/infrastructure/report_pro/__init__.py`:
   ```python
   VARIANTES_DISPONIBLES = ("pro", "pediatrico", ..., "mi_variante")

   def generate_pro_pdf(report_data, template="pro"):
       ...
       if key == "mi_variante":
           from .variants.mi_variante import MiVarianteGenerator
           return MiVarianteGenerator().generate(report_data)
   ```

3. **Permitir** el valor en el endpoint `app/presentation/api/v1/reports.py`:
   ```python
   template: Literal["estandar", "pro", ..., "mi_variante"] = Query(...)
   ```

4. **Frontend** — agregar `<option value="mi_variante">Mi variante</option>` al
   `<Sel>` en `neurosoft-frontend/src/app/evaluation/EvalResultsPage.jsx`.

5. **Test** — añadir `"mi_variante"` a `ALL_TEMPLATES` en
   `tests/integration/test_reports.py`.

### Helpers reutilizables (`report_pro/`)

- **`theme.py`** — paleta `TEAL`/`NAVY`/`SLATE`/`SEMANTIC_*`, registro de
  fuentes Inter/Lora con fallback automático a Helvetica/Times-Roman, escala
  tipográfica (`TYPE.title_hero`, `TYPE.body_sm`, etc.) y `LAYOUT` (A4 + márgenes).
- **`helpers.py`** — `section_title`, `block_header`, `bullet`, `field_pair`,
  `callout`, `kpi_card`, `draw_table`, `draw_paragraph`, `two_column_layout`.
- **`charts.py`** — `draw_z_profile`, `draw_domain_radar`, `draw_normal_curve`,
  `draw_discrepancies`, `draw_ci_kpi_row` (todos dibujan en canvas directo).
- **`narrative.py`** — `build_synthesis_paragraphs`, `build_strengths_weaknesses`,
  `parse_recomendaciones` (etiquetas: `[ESCOLAR]`, `[TERAPÉUTICA]`, `(alta)`...).
- **`base.py`** — `NeuroPDFGeneratorPro` con el flujo default, paginación
  X de Y vía `_make_numbered_canvas_class`, y `_ensure_room` que salta de
  página con header automático cuando no caben N puntos.

### Fuentes Inter + Lora (opcional pero recomendado)

Para que los PDFs Pro se vean con la tipografía premium, descargar las TTFs de
[Google Fonts](https://fonts.google.com) y colocarlas en:

```
neurosoft-backend/app/assets/fonts/
  ├── Inter-Regular.ttf
  ├── Inter-Bold.ttf
  ├── Lora-Regular.ttf
  └── Lora-Bold.ttf
```

Si los archivos no están presentes, los generadores caen automáticamente a
**Helvetica + Times-Roman** (built-in en ReportLab) — el PDF sigue funcionando.

### Tests críticos

```bash
pytest tests/integration/test_reports.py -v
```

Cubre las 6 variantes, fallback de plantilla desconocida, datos mínimos,
retrocompat de la variante estándar, narrativa y parsing de recomendaciones.

### PDFs de muestra

Para regenerar las muestras en `docs/samples/MUESTRA_INFORME_*.pdf`, ejecutar el
script de smoke test inline (ver el header de `tests/integration/test_reports.py`
para un ReportData de referencia con caso clínico real anonimizado).

---

## CASOS CLÍNICOS VERIFICADOS (GROUND TRUTH)

Estos resultados están verificados contra informes clínicos reales impresos. Son la fuente de verdad para tests:

### Caso 1: Andrés Felipe Romero Castaño (caso de referencia infantil)
- **Datos:** 16a 11m, Masculino, Secundaria Incompleta
- **Fecha nacimiento:** 2008-05-30 | **Fecha evaluación:** 2025-05-15
- **Contexto:** caso anonimizado de referencia — valores verificados contra
  informe clínico real para validar el motor de scoring WISC-IV.

| Test | PD | Escalar esperado | Interpretación |
|---|---|---|---|
| NiWiscDC | 53 | 11 | Bajo |
| NiWiscSem | 32 | 11 | Bajo |
| NiWiscVoc | 37 | 6 | Bajo |
| NiWiscLN | 25 | 16 | Bajo |
| NiWiscCl | 46 | 4 | Bajo |
| NiWiscAri | 21 | 6 | Bajo |
| NiWISCIndComVer (suma=26) | 26 | CI=93 | Promedio |
| NiWISCIndRazPer (suma=29) | 29 | CI=98 | Promedio |
| NiWISCIndMemTra (suma=15) | 15 | CI=86 | Promedio |
| NiWISCIndVelPro (suma=13) | 13 | CI=80 | Promedio |
| NiWISCTot (suma=83) | 83 | CI=87 | Promedio |

### Caso 2: María Elena Cardona Restrepo (caso de referencia AM)
- **Datos:** 80a 5m, Femenino, Primaria Incompleta
- **Fecha nacimiento:** 1945-01-01 | **Fecha evaluación:** 2025-06-03
- **Ajuste escolaridad:** +2 al PD en pruebas Neuronorma que lo requieren
- **Contexto:** caso anonimizado de referencia — valores verificados contra
  informe real para validar Neuronorma Colombia AM con ajuste por escolaridad.

| Test | PD | Escalar esperado |
|---|---|---|
| ViRDD | 4 | 13 |
| ViRDInv | 2 | 11 |
| ViTMTA | 239 | 6 |
| ViStP | 8 | 3 |
| ViGroberRLT | 3 | 3 |
| ViGroberML_Tot | 2 | 6 |
| ViGroberMC_Tot | 7 | 4 |
| ViAni | 8 | 8 |
| ViYesavage | 2 | 2 |

---

## ESTADO ACTUAL DE TESTS

### Tests existentes (pytest tests/)
- `tests/unit/clinical_engine/test_engine.py` — tests básicos (legacy)
- `tests/unit/clinical_engine/test_engine_full.py` — tests completos verificados (**27 tests, todos pasan**)
- `tests/integration/test_repositories.py` — tests de repositorios con BD en memoria
- `tests/conftest.py` — fixtures compartidas

### Cobertura actual
- **Tested:** 33 de 168 pruebas (20%) — **hace falta expandir**
- **Estrategias sin test directo:** `ajuste`, `baremo_pe`, `comparativo`, `z_score_multiple`
- **Pruebas Adulto Mayor no testeadas:** todas las `desconocido` excepto ViTMTA/ViRDD/ViStP/ViGrober
- **Pruebas Adulto Joven no testeadas:** la mayoría del WAIS-III

---

## BUG ENCONTRADO Y CORREGIDO (v7)

`PuntajeDoblResultadoStrategy` fallaba con `AttributeError: 'list' object has no attribute 'get'` para NiGadsIS/NiGadsPRC/NiGadsPatCog/NiGadsHP/NiGADSCTAs porque sus baremos son listas `[PE, Percentil]` no dicts `{"PE": x}`. **Corregido en v7.** Los tests verifican que funciona.

---

## PRIORIDADES PARA LA AUDITORÍA

### PRIORIDAD 1 — Tests faltantes (impacto directo en seguridad clínica)

Expandir `tests/unit/clinical_engine/test_engine_full.py` con:

1. **Todas las estrategias `wais_range`** que faltan:
   - AdWAISA, AdWAISC, AdWAISCC, AdWAISFI, AdWAISHI, AdWAISI, AdWAISL, AdWAISRO
   - AdSemWais, AdSDWais, AdMatr, AdDDir
   - Al menos un test por cada una con PD representativo

2. **Índices compuestos WAIS-III** (`suma_a_indice`):
   - AdWAISICV, AdWAISICP, AdWAISIMT, AdWAISIVP, AdWASIEVer, AdWAISEMan

3. **Estrategia `desconocido` AM** — tests para todas las pruebas Neuronorma sin cubrir:
   - ViStC, ViStPC, ViP, ViWCat, ViTLMExc, ViTLLat, ViTLEje, ViSimDig, ViTBDA
   - Para cada una: edad 65a + escolaridad promedio, verificar que devuelve escalar válido

4. **`z_score`** — AdTMT_AB, AdFCRO_Rey (z-score con parámetros por edad)

5. **`escolaridad_pc50`** — AdDReg, AdRDI, ViSem con distintas escolaridades

6. **`puntaje_doble_resultado`** — NiGadsHP, NiGadsPatCog, NiGADSCTAs (todos fijos tras el bug)

7. **Tests negativos importantes:**
   - PD fuera del rango del baremo → `_not_found`
   - Paciente menor de 50 años con prueba ViTMTA → `sin_norma` en metadata

### PRIORIDAD 2 — Verificación de baremos Colombia

**ANTES de cualquier cambio, consultar al usuario.** El proceso es:

1. Para cada prueba de Neuronorma Colombia AM, buscar si existen publicaciones de referencia:
   - Ostrosky-Solís F. et al. (2010) — Neuronorma Colombia
   - Arango-Lasprilla J.C. et al. — versiones colombianas de pruebas
   - INECO, CANO, GRNC — grupos de neuropsicología Colombia

2. Para WISC-IV Colombia: verificar que las tablas son de la edición colombiana (2014)
   - El baremo chileno y argentino son DISTINTOS al colombiano

3. **Para cada discrepancia encontrada:**
   - Documentar: prueba, valor actual en BD, valor de referencia, fuente
   - NO modificar — crear issue/comentario y consultar al usuario

4. Pruebas prioritarias para verificar:
   - NiWiscDC PD=53, edad 16a 11m → escalar 11 (verificado contra informe real)
   - NiWISCTot suma=83 → CI=87 (verificado)
   - ViTMTA PD=239, 80a, PrimInc → escalar 6 (verificado)

### PRIORIDAD 3 — Código

1. **`app/domain/clinical_engine/strategies.py`** — revisar todas las estrategias por:
   - Manejo de edge cases (PD=0, PD muy alto, edad extrema)
   - Consistencia entre `tipo_metrica` y los valores retornados
   - DesconocidoStrategy: asegurarse que `sin_norma` se propaga correctamente

2. **`app/infrastructure/report_service.py`** — revisar:
   - Manejo de páginas cuando el contenido es muy largo
   - Que la gráfica Z no se desborde con muchas pruebas
   - Encoding de caracteres especiales (ñ, acentos) en el PDF

3. **`app/application/use_cases/clinical_history_use_cases.py`** — verificar:
   - Que el optimistic locking (`row_version`) se aplica correctamente
   - Que el snapshot se guarda antes del update, no después

4. **`app/infrastructure/repositories/evaluation_repo.py`** — verificar:
   - Que `is_latest` se maneja correctamente en todos los casos
   - Que el JSON serializado/deserializado no pierde precisión numérica

5. **`app/presentation/api/v1/patients.py`** — verificar:
   - Que el filtro de `poblacion` en `search_panel` calcula la edad correctamente
   - Que `PatientPanelUseCase` no hace N+1 queries

### PRIORIDAD 4 — Seguridad y producción

1. Verificar que el middleware de auth no bloquea `/docs`, `/redoc`, `/openapi.json`
2. Verificar que `ConcurrencyError` retorna status 409 (no 422)
3. Verificar que las rutas de backup no exponen rutas del filesystem en el response
4. Revisar que `hash_password` usa bcrypt (no MD5/SHA1)
5. Verificar que el JWT secret nunca aparece en logs

---

## PROTOCOLO DE CAMBIOS

1. **Leer el archivo afectado completo** antes de modificar
2. **Correr tests relacionados** antes y después del cambio
3. **Para cambios en `strategies.py` o `baremos_loader.py`:** correr los 27 tests del engine
4. **Para cambios en datos clínicos:** NO modificar — consultar primero
5. **Commits atómicos** — un cambio lógico por commit
6. **Mensaje de commit:** `fix:`, `feat:`, `test:`, `refactor:`, `docs:`

---

## ARQUITECTURA DETALLADA DEL MOTOR

```python
# Flujo de cálculo (engine.py):
# 1. PatientContext.from_demographics() → calcula edad, población
# 2. ClinicalEngine.score(puntajes, ctx) →
#    para cada (test_id, pd) en puntajes:
#      a. loader.get_prueba(test_id) → Prueba (baremos, tipo_calculo)
#      b. loader.get_ajuste_escolaridad(test_id, escolaridad) → int
#      c. pd_ajustado = pd + ajuste (solo para Neuronorma AM)
#      d. factory.get(tipo_calculo) → IScoringStrategy
#      e. strategy.calculate(prueba, pd_ajustado, age.years, age.months, sexo, escolaridad)
#      f. ScoringOutput → ResultadoPrueba
# 3. EngineResult: resultados[], puntos_debiles, puntos_fuertes, advertencias
```

---

## DEPENDENCIAS Y VERSIONES CRÍTICAS

```
fastapi==0.115.0
sqlalchemy==2.0.31
pydantic==2.7.0
reportlab==4.2.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
APScheduler>=3.10.0
alembic>=1.13.0
pytest==8.2.0
httpx==0.27.0  # Para tests de endpoints
```

---

## NOTAS IMPORTANTES

- `9999` = prueba no realizada (convención del sistema VBA original)
- `N/A` = campo de HC vacío (no mostrar en UI)
- `_ajustes_escolaridad` en BD: solo aplica a pruebas Neuronorma AM con escolaridad < Secundaria
- `poblacion` se calcula en tiempo real desde la edad, no se guarda (excepto en evaluaciones guardadas)
- El scheduler (APScheduler) es **opcional** — si no está instalado, el sistema funciona igual
- Alembic migrations están en `alembic/versions/` — `001` es el punto inicial, `002` agrega todas las columnas nuevas desde v4+

---

## CAMBIOS RECIENTES (mayo 2026 — sprint quick wins + mejoras)

### Auditoría Excel vs Motor
- Comparación sistemática de `BD_NEURO_MAESTRA.json` contra el Excel original `SistemaHC_Prac Johan_Sebastian_Salgado.xlsm`: **97/102 tests con match perfecto (95%)**.
- 10 tests Grober legacy (formato `50P/50S/50U` incompatible con `tipo_calculo=desconocido`) **eliminados** del JSON.
- 1 bug corregido en BD: `AdFCRO_Rey` edad 45 (valores desplazados).
- Backup defensivo: `data/BD_NEURO_MAESTRA.backup-pre-auditoria-excel.json`.
- Reporte completo: `docs/casos-clinicos/AUDITORIA_EXCEL_VS_MOTOR.md`.
- `_meta.cambios[]` en el JSON registra fecha + razón.

### ORMs nuevos
| ORM | Tabla | Para qué |
|---|---|---|
| `ConfigSmtpORM` | `config_smtp` | Singleton config SMTP, password cifrada con Fernet derivado del JWT_SECRET (§QW-2). |
| `ConfigEmailTemplateORM` | `config_email_templates` | Override de plantillas email por tipo (§QW-3). |
| `CompanionORM` | `companions` | Acompañantes del paciente como entidad (madre/padre/cuidador), autorizaciones, principal (§M-7). |
| `RiskAssessmentORM` | `risk_assessments` | Evaluación C-SSRS con nivel + plan de seguridad + factores (§M-3). |

### Endpoints nuevos
| Método | Ruta | Para qué |
|---|---|---|
| `GET/PUT` | `/api/v1/config/smtp` | Config SMTP desde UI (sin exponer password). |
| `POST` | `/api/v1/config/smtp/test` | Envío de email de prueba. |
| `GET/PUT/DELETE` | `/api/v1/config/email-templates[/{tipo}]` | Plantillas editables. |
| `GET/POST/PUT/DELETE` | `/api/v1/companions[?patient_id=...]` | CRUD acompañantes. |
| `POST` | `/api/v1/therapy/risk-assessments` | Registrar C-SSRS. |
| `GET` | `/api/v1/clinical-history/{patient_id}/pdf` | PDF de HC sola, sin evaluación (§QW-4). |
| `POST` | `/api/v1/reports/{eval_id}/send-email` | Envío de informe por correo. |

### Servicios nuevos
- `infrastructure/crypto.py` — Fernet encrypt/decrypt para campos sensibles.
- `infrastructure/hc_pdf_service.py` — generador PDF de HC sola (§QW-4).
- `infrastructure/email_service.py` — `get_effective_smtp_config(db)` con override BD > env (§QW-2).
- `infrastructure/scheduler_service.py` — nuevo job `_task_recordatorio_email_manana` 18:00 (§QW-7).

### Mejoras en endpoints existentes
- `GET /api/v1/reports/preview/{eval_id}` ahora devuelve `secciones[]`, `completitud_pct`, `bloqueos[]`, `puede_descargar`, `advertencias_completitud[]`, `dominios_evaluados/con_obs/sin_obs` (§M-5).
