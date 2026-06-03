# Plan Maestro Global — NeuroSoft App

**Versión:** 1.0 (2026-06-01)
**Autor:** Claude (asistente clínico + arquitecto)
**Estado:** Borrador consolidado, pendiente aprobación
**Scope:** 312 hallazgos auditoría + 9 gaps manuales WAIS/WISC + cumplimiento legal colombiano + distribución comercial

---

## 0. Contexto

NeuroSoft App es un sistema de evaluación neuropsicológica clínica para profesionales colombianos, distribuido como aplicación desktop (PyInstaller + Inno Setup) con frontend React/Vite y backend FastAPI/SQLite.

Esta auditoría consolidó:
- **6 explore agents** (motor clínico, seguridad, reportes, API, frontend, contenido) → **312 hallazgos**
- **4 explore agents** sobre 33 PDFs de manuales clínicos consultados (ya extraídos a `docs/manuales-ocr/`)
- **OCR propio** de manuales WISC-IV y WAIS-III del usuario (Editorial El Manual Moderno 2005/2003) → `docs/manuales-ocr/EXTRACCION_WISC-IV_WAIS-III.md` (37 KB)
- **Análisis del Excel original** `MISISTEMAV1.xlsm` (5.7 MB, 19 hojas)
- **Comparación** con `BD_NEURO_MAESTRA.json` (174 tests, 7 sub-tests baterías)
- **Revisión de** `docs/audits/`, `docs/legal/`, `docs/planning/` existentes

Documentos ya disponibles (NO reescribir):
- `docs/legal/HABEAS_DATA.md` — cumplimiento Ley 1581/2012
- `docs/legal/GUIA_REGISTRO_INVIMA_SaMD.md` — registro INVIMA
- `docs/audits/AUDITORIA_EXCEL_VS_MOTOR.md` — auditoría baremos
- `docs/audits/AUDITORIA_55_TESTS_SOLO_MOTOR.md` — tests solo motor
- `docs/planning/CLINICAL_ROADMAP.md` — hoja de ruta clínica
- `docs/manuales-ocr/EXTRACCION_WISC-IV_WAIS-III.md` — extracción baremos WISC/WAIS

---

## 1. Resumen ejecutivo — Los 12 frentes

| # | Frente | Severidad | Norma/justificación | # hallazgos |
|---|---|---|---|---|
| 1 | Reclasificación 5-6 bandas sin "Limítrofe" | 🔴 Crítico | CIE-11, DSM-5-TR, CONFIL 2012 | 4 |
| 2 | Bugs críticos del motor clínico | 🔴 Crítico | Validez clínica | 22 |
| 3 | Saneo CIE-10/CIE-11 (punto oficial) | 🔴 Crítico | Res. 3374/2000, Res. 2275/2023, CIE-11 | 7 |
| 4 | Copyright scrub (manuales clínicos Pearson) | 🟠 Alto | Ley 23/1982, Tratados OMPI | 15 |
| 5 | Cumplimiento documental Colombia | 🟠 Alto | Ley 1090/2006, Ley 1581, Res. 1995, 2275, 3100 | 28 |
| 6 | Integración protocolos orden clínico | 🟠 Alto | Práctica clínica estándar 2024 | 5 |
| 7 | Migración baremos faltantes (manuales + Excel) | 🟠 Alto | Arango-Lasprilla 2017, Wechsler 2003/2008 | 18 |
| 8 | Corrección catálogo escalas (GADS, SCARED, etc.) | 🟠 Alto | Birmaher 1997, Gilliam 2001, Petersen 2011 | 14 |
| 9 | Informe PDF rediseñado + 7 principios | 🟡 Medio | Práctica clínica estándar, CONFIL | 9 |
| 10 | Seguridad y kill-switches | 🔴 Crítico | HIPAA, ISO 27001, OWASP | 13 |
| 11 | Accesibilidad + dark mode + UX | 🟡 Medio | WCAG 2.1, design system | 22 |
| 12 | CI/CD, regresión clínica, docs | 🟡 Medio | Buenas prácticas, ISO 25010 | 14 |

**Total integrado:** 171 hallazgos únicos (hay solapamiento entre frentes, p.ej. el SCARED-41 entra en 2, 8 y 11).

---

## FRENTE 1 — Reclasificación 5-6 bandas sin "Limítrofe"

### 1.1 Estado actual
- **`neurosoft-frontend/src/data/IndicesCI.jsx:53-62`** — `classifyIQ()` con 7 bandas hardcoded: ≥130 "Muy Superior", ≥120 "Superior", ≥110 "Normal-Alto", ≥90 "Normal", ≥80 "Normal-Bajo", ≥70 "Borderline", <70 "Déficit".
- **`neurosoft-frontend/src/data/IndicesCI.jsx:38`** — Composición WAIS-III incluye subtest inválido (`"AdBusSim + ViBusSim"` literal string).
- **`neurosoft-frontend/src/data/IndicesCI.jsx:74-78`** — SEM hardcoded a 5 (real: ICV≈5.6, IRP≈6.6, IMT≈7.2, IVP≈7.7 según WISC-IV/WAIS-III).

### 1.2 Gap detectado
- La categoría "Borderline" (70-79) replica el constructo **"Funcionamiento Intelectual Límite"** (Borderline Intellectual Functioning - BIF) eliminado por DSM-5 (2013) y DSM-5-TR (2022), y por CIE-11 (vigente Colombia Res. 2275/2023).
- CIE-11 solamente reconoce **4 niveles de Discapacidad Intelectual** (6A00.0 Leve, 6A00.1 Moderada, 6A00.2 Grave, 6A00.3 Profunda), basados en **funcionamiento adaptativo**, NO en CI aislado.
- CONFIL 2012 (Colombia) solo menciona FIL si CI 71-85 **+ impacto funcional documentado** (no como banda independiente automática).

### 1.3 Acción concreta
1. Refactorizar `classifyIQ()` a 5-6 bandas contextualmente ajustadas (Decisión usuario pendiente — opciones: a/b/c/d):
   - **Opción A (recomendada, defensible DSM-5-TR + CIE-11 + CONFIL 2012):**
     - ≥130 Muy Superior · 120-129 Superior · 110-119 Promedio Alto · 90-109 Promedio · 80-89 Promedio Bajo · 70-79 Bajo · <70 Muy Bajo
     - **Anotación clínica automática** para CI 70-79: "Hallazgo compatible con Discapacidad Intelectual Leve (DSM-5-TR 6A00.0/CIE-11 317/F70 CIE-10) SOLO si se documenta compromiso del funcionamiento adaptativo en al menos 2 áreas (criterio A DSM-5-TR 300.45). En su defecto, clasificar como 'Funcionamiento Intelectual en Rango Bajo-Borderline' (CONFIL 2012) y complementar con evaluación adaptativa (Vineland, ABAS)."
   - **Opción B (5 bandas estrictas, alineado con la instrucción de la jefa):**
     - ≥120 Superior · 90-119 Promedio · 80-89 Bajo Promedio · 70-79 Discapacidad Intelectual Leve (condicional) · <70 Discapacidad Intelectual Moderada o mayor
2. Corregir composición IVP WAIS-III (línea 38) a `["AdSDWais", "AdBusSim"]`.
3. Reemplazar SEM=5 hardcoded por lookup por índice (Tabla 4.2 WAIS-III pág 27 manual; WISC-IV Tabla A.2 según edad).
4. Aplicar la misma reclasificación a WISC-V si se llega a migrar, y replicar a TODOS los frentes (escalares, índices, percentiles).

### 1.4 Criterio de cierre
- [ ] Test unitario `test_indices_ci.py` con 10+ casos cubriendo cada banda
- [ ] Test integración `test_e2e_reclasificacion.py` valida reporte PDF muestra
- [ ] Validación con clínico (`[PROFESIONAL_CONFIGURADO]`) sobre 3 casos reales anonimizados
- [ ] Documentado en `docs/clasificacion/RECLASIFICACION_2026.md` con citas a DSM-5-TR p.37, CIE-11 6A00, CONFIL 2012 p.18

### 1.5 Norma/justificación
- DSM-5-TR (2022) — Sección II "Trastornos del Neurodesarrollo", Discapacidad Intelectual criterios A-E
- CIE-11 (vigente Colombia Res. 2275/2023) — Sección 6A00 Discapacidad Intelectual
- CONFIL 2012 (Federación Colombiana de Psicología) — Lineamientos Funcionamiento Intelectual Límite
- Neuronorma Colombia 2ª ed. (Arango-Lasprilla & Rivera 2017) — cap. 2

### 1.6 Orden de ejecución
- **Sprint 1 (Semana 1)** — refactor + tests; ventana de aprobación del clínico 3-5 días

---

## FRENTE 2 — Bugs críticos del motor clínico

### 2.1 Motor de cálculo (`neurosoft-backend/app/domain/clinical_engine/`)

| # | Severidad | Hallazgo | Archivo:línea | Acción |
|---|---|---|---|---|
| 2.1.1 | 🔴 | TMT-B **sí** se calcula correctamente para infantil/joven; pero `ViTMTB` en adulto mayor tiene `tipo_calculo: "desconocido"` (mapea a `DesconocidoStrategy`, retorna escalar=18) | `neurosoft-backend/data/BD_NEURO_MAESTRA.json:76660` (ViTMTB) | Cambiar `tipo_calculo` a `z_score`; verificar con `OrTMTA`/`OrTMTB` |
| 2.1.2 | 🔴 | `ViTLRes` (Torre de Londres Recobro) baremo corrupto: rango 50560–505617 retorna escalar=18 fijo | `BD_NEURO_MAESTRA.json:116261-116284` | Cambiar `tipo_calculo: "desconocido" → "rango_puntaje"`; poblar baremo desde Neuronorma AM (Arango-Lasprilla 2017 cap. 8) o Manual Culbertson |
| 2.1.3 | 🔴 | `ComparativoStrategy` (CVLT) usa fórmula inventada `z = (pd/max_lista - 0.5)/0.15` sin referencia bibliográfica | `strategies.py:641` | Cambiar a z estandarizado por tabla T del manual CVLT-II (Delis 2000); o consultar Sutcliffe 2020 revisión crítica |
| 2.1.4 | 🟠 | `wisc_discrepancy.py` usa umbral constante 23 puntos para todos los pares y todas las edades; el manual WISC-IV Cuadro B-1 da umbrales variables 7-15 pts | `wisc_discrepancy.py:23-25` | Reemplazar por lookup por edad y par (ver §2.1.6) |
| 2.1.5 | 🟠 | Sentinel `9999` se filtra al backend desde frontend | `neurosoft-frontend/src/app/eval/EvalApplyPage.jsx:233` | Validar `pd` en el front con `Number.isFinite()` antes de enviar; rechazar 9999 server-side en `clinical_results.py:POST` |
| 2.1.6 | 🟠 | WISC-IV discrepancias por edad y par (Cuadro B-1): tabla completa extraída en §3 del informe de extracción; **no implementada** | `wisc_discrepancy.py:1-100` | Crear `wisc_discrepancy_tables.py` con lookup por edad; reemplazar umbral constante |

### 2.2 Reglas de suspensión — ausencia confirmada

| # | Severidad | Hallazgo | Acción |
|---|---|---|---|
| 2.2.1 | 🟠 | No existe lógica que aplique criterios de discontinuación WISC-IV (15 subtests) ni WAIS-III (14 subtests). Solo hay metadata informativa en `test_guide.py:69-310` no consumida por el motor. | Crear `suspension_rules.py` con motor de evaluación; endpoint nuevo `GET /api/v1/clinical/suspension-check/{paciente_id}` que devuelva "Debería haber suspendido en reactivo N" para auditoría |
| 2.2.2 | 🟠 | Reglas extraídas del manual (ver `EXTRACCION_WISC-IV_WAIS-III.md` §2 y §8): WISC-IV Cubos=3 consecutivas 0, WAIS-III Claves=120s, etc. | Implementar y exponer en `clinical_history.py:236,259` |

### 2.3 Composición de índices

| # | Severidad | Hallazgo | Archivo:línea | Acción |
|---|---|---|---|---|
| 2.3.1 | 🔴 | WAIS-III IVP compuesto usa literal inválido `"AdBusSim + ViBusSim"` (string con espacio y `+`) | `IndicesCI.jsx:38` | Cambiar a `["AdSDWais", "AdBusSim"]` |
| 2.3.2 | 🟠 | AdWAISC (Comprensión) incluida en IVP; debe estar en ICV según Wechsler 1997 Tabla 5.1 (escala verbal) | (mismo archivo, lógica de cálculo) | Reasignar a ICV |
| 2.3.3 | 🟠 | Subprueba WISC-IV `NiWiscInd` (Información) suplementaria no listada en `baterias/infantil` aunque aparece referenciada en otros endpoints | `BD_NEURO_MAESTRA.json` sección infantil | Agregar clave y baremos |

### 2.4 Criterio de cierre motor
- [ ] 280 tests motor pasando
- [ ] 15 fixtures ground truth pasando (test_casos_ground_truth.py)
- [ ] Nuevos tests: `test_vitmtb_fix.py`, `test_vitlres_fix.py`, `test_wisc_discrepancy_age_aware.py`, `test_suspension_rules.py`
- [ ] Smoke-test: 5 casos manuales con 3 clínicas distintas

### 2.5 Norma
- Wechsler D. (2003). *WISC-IV Technical and Interpretive Manual*. San Antonio: Psychological Corporation.
- Wechsler D. (1997). *WAIS-III Administration and Scoring Manual*. San Antonio: Psychological Corporation.
- Sattler JM, Dumont R. (2004). *Assessment of Children: WISC-IV and WPPSI-III Supplement*. Jerome Sattler Publishing.
- Jacobson NS, Truax P. (1991). Clinical significance: a statistical approach. *Journal of Consulting and Clinical Psychology*, 59(1), 12-19.

### 2.6 Orden de ejecución
- **Sprint 0** (días 1-3): bugs que rompen el cálculo (2.1.1, 2.1.2, 2.1.3, 2.3.1)
- **Sprint 1** (semana 2): discrepancias por edad, sentinel 9999, suspensión

---

## FRENTE 3 — Saneo CIE-10 / CIE-11 (códigos con punto oficial)

### 3.1 Estado actual
**Archivo:** `neurosoft-frontend/src/data/datosClinicos.js`

| Línea | Bug | CIE-10 real | CIE-11 equivalente | Diagnóstico |
|---|---|---|---|---|
| 736 | `F840: "Trastorno del espectro autista"` | **F84.0** (autismo infantil) NO corresponde a TEA moderno | 6A02 (TEA sin DIS) | Bug: F840 también etiqueta como TEA. F84.5 = Síndrome de Asperger (DEPRECADO DSM-5/CIE-11) |
| 739 | `F988: "TDAH predominio inatento"` | **F98.8** = "Trastorno del desarrollo emocional" — NO TDAH | — | **Bug crítico:** F98.8 mal mapeado a TDAH |
| 769 | `F438C: "TEPT complejo"` | **F43.1** = TEPT simple (sin ".C"); F43.8 = Otras reacciones a estrés; F43.0 = estrés agudo. **F438C no existe en CIE-10** | 6B41 (TEPT) | Código inventado; reemplazar |
| 794-795 | `F988: "TDAH predominio inatento"` + `F840: "TEA"` | Mismo bug replicado en `CIE_POR_POBLACION.infantil` | — | Refactor obligatorio |
| 811 | `F988: "TDAH predominio inatento (adulto)"` | Mismo bug | — | Refactor obligatorio |
| 823 | `F840: "TEA"` | Mismo bug | — | Refactor |

### 3.2 Acción concreta
1. **Mapeo canónico** (códigos con punto oficial):

   | Diagnóstico | CIE-10 (Colombia Res. 3374/2000/Res. 2275/2023) | CIE-11 (Resolución 2275/2023) | DSM-5-TR |
   |---|---|---|---|
   | TDAH predominio inatento | **F90.0** | 6A04.0 | 314.00 |
   | TDAH predominio hiperactivo-impulsivo | **F90.1** | 6A04.1 | 314.01 |
   | TDAH combinado | **F90.2** | 6A04.2 | 314.01 |
   | TDAH otro tipo especificado | **F90.8** | 6A04.Y | 314.01 |
   | TEA sin DIS | **F84.0** (recomendado) / F84.5 (Asperger DEPRECADO) | **6A02** | 299.00 |
   | Dislexia | **F81.0** | 6A03.0 | 315.00 |
   | Discalculia | **F81.2** | 6A03.2 | 315.1 |
   | Trastorno de la comunicación | **F80.9** | 6A01.Y | 307.9 |
   | Discapacidad Intelectual Leve | **F70** | 6A00.0 | 317 |
   | Discapacidad Intelectual Moderada | **F71** | 6A00.1 | 318.0 |
   | Discapacidad Intelectual Grave | **F72** | 6A00.2 | 318.1 |
   | Discapacidad Intelectual Profunda | **F73** | 6A00.3 | 318.2 |
   | TEPT | **F43.1** | 6B41 | 309.81 |
   | Trastorno depresivo mayor | **F32.0** (leve), **F32.1** (mod), **F32.2** (sev) | 6A71 | 296.xx |
   | Distimia / Trastorno depresivo persistente | **F34.1** | 6A72 | 300.4 |
   | Trastorno de ansiedad generalizada | **F41.1** | 6B02 | 300.02 |
   | Trastorno de pánico | **F41.0** | 6B01 | 300.01 |
   | Fobia social | **F40.1** | 6B04 | 300.23 |
   | TOC | **F42** | 6B20 | 300.3 |
   | Trastorno de conducta | **F91** | 6C90 | 312.xx |
   | Trastorno oposicionista desafiante | **F91.3** | 6C90 | 313.81 |
   | Disocial | **F91.2** | 6C91 | 312.xx |
   | Anorexia | **F50.0** | 6B80 | 307.1 |
   | Bulimia | **F50.2** | 6B81 | 307.51 |
   | Consumo perjudicial alcohol | **F10.1** | 6C40.1 | 305.00 |
   | Dependencia alcohol | **F10.2** | 6C40.2 | 303.90 |
   | Esquizofrenia | **F20** | 6A20 | 295.90 |

2. **Refactor `datosClinicos.js`:** crear tabla `CIE10_CATALOG_OFICIAL` con códigos exactos, luego `CIE10_POR_POBLACION` como vista derivada.
3. **Backend** `app/core/catalogs/cie10.py`: nueva constante + endpoint `GET /api/v1/catalogs/cie11` para autocompletar.
4. **Reportes PDF:** función helper `format_cie(code)` que formatee con punto (F32.1, no F321) según Res. 3374/2000.
5. **RIPS** (Res. 2275/2023): la causa externa usa subcategorías CIE-10 con punto + dígitos; el sistema debe permitir capturar hasta 4 caracteres (e.g., F32.11, F43.10, F90.0).

### 3.3 Criterio de cierre
- [ ] Tabla `CIE10_CATALOG_OFICIAL` con 80+ diagnósticos prevalentes en neuropsicología colombiana
- [ ] Cross-check manual de 30 códigos con CIE-10 impreso MinSalud 2023
- [ ] Test `test_cie10_formato.py` valida punto en todos los códigos
- [ ] Ningún código con más de 3 caracteres sin punto
- [ ] Eliminación total de F988, F438C, F88X (inexistentes)

### 3.4 Norma
- **Resolución 3374 de 2000** (MinSalud) — adopta CIE-10 para Colombia (obligatorio RIPS)
- **Resolución 2275 de 2023** (MinSalud) — actualiza estructura RIPS, permite CIE-10 y CIE-11
- **CIE-10** (5ª edición, OMS 2015) y **CIE-11** (vigente OMS 2019, en Colombia desde Res. 2275/2023)
- **DSM-5-TR** (APA 2022)

### 3.5 Orden de ejecución
- **Sprint 1** (semana 2-3) — refactor catálogo + tests

---

## FRENTE 4 — Copyright scrub (manuales clínicos)

### 4.1 Estado actual

**A. Itéms verbatim Pearson** (13 tests) — **decisión usuario: mantener + disclaimer + checkbox de certificación**:
- `neurosoft-frontend/src/data/clinical.js:86` — `AdWAISCC` (Cubos WAIS-III) `items` array
- `clinical.js:143` — `NiWiscVoc` (Vocabulario WISC-IV) `items` array
- `clinical.js:244` — `AdWAISV` (Vocabulario WAIS-III) usa placeholders `"Ítem ${i+1}"` (no verbatim, OK)
- Y otros: BNT (`Denom48`), Stroop (`StroopAM/AJ`), FCRO, Torre de Londres, etc.
- **Total: ~13 tests con reactivos palabra-por-palabra del manual Pearson**

**B. Atribuciones a terceros (10 ocurrencias en código)** — **decisión usuario: borrar todas, sin atribución a ningún tercero**:
- `neurosoft-frontend/src/data/protocolLoader.js:7` — comentario "Los JSONs provienen de fuentes clínicas estándar 2024"
- `neurosoft-frontend/src/data/wisc_iv_protocolo.json:7` — `"institucion": ""` (placeholder, configurable)
- `neurosoft-frontend/src/data/protocols/protocolos_casos_especiales.json:4` — igual
- `neurosoft-frontend/src/data/protocols/protocolos_memoria_verbal.json:4` — igual
- `neurosoft-frontend/src/data/protocols/protocolo_adulto_joven.json:7` — igual
- `neurosoft-frontend/src/data/protocols/protocolo_adulto_mayor.json:7` — igual
- `neurosoft-frontend/src/data/protocols/protocolo_ninos_complementario.json:7` — igual
- `neurosoft-frontend/src/data/protocols/wais_iii_protocolo.json:7` — igual
- `neurosoft-frontend/src/data/protocols/wisc_iv_protocolo.json:7` — igual (duplicado de `data/wisc_iv_protocolo.json`)
- `neurosoft-backend/data/protocols/wisc_iv_protocolo.json:7` — igual

### 4.2 Acción concreta

**A. Capa protegida Pearson** (mantener verbatim):
1. **Backend**: nuevo módulo `app/domain/copyright/protected_content.py` con decorator `@requires_license_certification(test_id)` que:
   - Lee `clinico.certificaciones[]` (nuevo campo en UserORM)
   - Verifica checkbox activo en BD para ese test
   - Audita cada acceso en `ai_logs` (similar a trazabilidad IA)
2. **Frontend**: `ProtectedTestGate.jsx` modal que:
   - Muestra disclaimer "Confirmo que poseo licencia vigente del test [NOMBRE_TEST] de [EDITORIAL]"
   - Checkbox obligatorio
   - Registro persistente con timestamp + IP
3. **Login inicial**: pantalla única de "Certificaciones del profesional" donde declara qué manuales tiene licenciados (WISC-IV, WAIS-III, WISC-V, BDI-II, etc.). Esto evita pedirlo cada vez.
4. **PDF del informe**: pie de página "Evaluación calculada con material bajo licencia del clínico. La reproducción de reactivos verbatim está prohibida por derechos de autor."

**B. Scrub total de atribuciones a terceros**:
1. Cambiar `"institucion": "<valor_anterior_con_atribución_a_tercero>"` → `"institucion": ""` (vacío, configurable) en los 9 JSON
2. Eliminar línea 7 del comentario en `protocolLoader.js:7`
3. Cambiar cabecera `_meta.autor` de cualquier atribución a tercero → "NeuroSoft App"
4. Conservar el **contenido** (orden de aplicación, criterios de suspensión, materiales, stop rules, poblaciones) — eso es conocimiento clínico no protegible. Solo se borra atribución.
5. Crear `docs/creditos/PROTOCOLOS_FUENTES.md` (interno, no distribuible) listando las fuentes originales con fines de auditoría legal.

**C. Verificación final**:
- `grep` por atribuciones a terceros en archivos distribuidos debe retornar **0** matches.
- Revisión manual del instalador `.iss` y archivos `.txt` de metadata.

### 4.3 Criterio de cierre
- [ ] 0 atribuciones a terceros en código distribuible
- [ ] Modal de certificación implementado y testeado
- [ ] Audit log de accesos a contenido protegido
- [ ] PDF disclaimer pie de página
- [ ] Verificación legal externa (abogado propiedad intelectual) — Sprint 3

### 4.4 Norma
- **Ley 23 de 1982** (Colombia) — Derechos de autor
- **Ley 44 de 1993** — Modificaciones a Ley 23
- **Decisión 486 de 2000** (CAN) — Régimen Común sobre Propiedad Industrial
- **Tratados OMPI** (WIPO) — derechos de autor en software
- **Editorial El Manual Moderno / Pearson** — licenciamiento

### 4.5 Orden de ejecución
- **Sprint 1** (semana 2): capa protegida Pearson + scrub atribuciones a terceros
- **Sprint 3**: revisión legal externa

---

## FRENTE 5 — Cumplimiento documental Colombia

### 5.1 Documentos a producir/actualizar

> Los siguientes documentos ya tienen borradores parciales en `docs/legal/HABEAS_DATA.md` y `docs/legal/GUIA_REGISTRO_INVIMA_SaMD.md`. Aquí se detallan y completan.

| # | Documento | Normativa | Estado actual | Acción |
|---|---|---|---|---|
| 5.1 | **Consentimiento informado para evaluación neuropsicológica** | Ley 23/1981, Res. 8430/1993, Ley 1581/2012, Ley 1090/2006 art. 36 | No existe plantilla en código | Crear plantilla HTML/PDF en `app/infrastructure/templates/consentimiento_evaluacion.html` (3 versiones: adulto, menor con acudiente, asentimiento informado 6-12 años) |
| 5.1.2 | **Autorización de tratamiento de datos (Ley 1581)** | Ley 1581/2012, Decreto 1377/2013 | Parcial en `HABEAS_DATA.md` | Generar plantilla `autorizacion_datos.html` con cláusulas obligatorias (responsable, finalidades, derechos, canal PQRS) |
| 5.1.3 | **Asentimiento informado menor 6-12 años** | Convención Derechos del Niño, Ley 1090/2006 | No existe | Plantilla con lenguaje adaptado a edad |
| 5.1.4 | **Contrato de servicios profesionales** | Código Civil, Estatuto Tributario | No existe | Plantilla con cláusulas: objeto, honorarios, duración, confidencialidad, retención HC 20 años |
| 5.1.5 | **Historia clínica estructurada** | Res. 1995/1999 | Implementada parcialmente | Validar 100% campos obligatorios Res. 1995/1999 art. 9 (anamnesis, antecedentes, examen mental, etc.) |
| 5.1.6 | **Informe neuropsicológico con cláusulas obligatorias** | Ley 1090/2006 art. 36 (Código Deontológico) | PDF actual carece de: firma con tarjeta profesional, número de registro, fecha, lugar, "objetivo del informe", "limitaciones", "uso previsto" | Agregar bloque legal al inicio y al final del PDF |
| 5.1.7 | **RIPS para facturación** | Res. 2275/2023 | No implementado | Implementar exportación RIPS JSON/XML para EPS, con campos: CUPS (prueba), diagnóstico CIE-10, fecha, profesional, valor |
| 5.1.8 | **Factura electrónica** | Res. 000042/2020 DIAN | No implementado | Integración con proveedor de facturación electrónica (e.g., Alegra, Siigo) o generación manual de PDF + código QR DIAN |
| 5.1.9 | **Aviso de privacidad y política de tratamiento** | Ley 1581/2012 art. 17, Decreto 1377/2013 | Parcial | Generar como página estática `/aviso-de-privacidad` |
| 5.1.10 | **Registro Nacional de Bases de Datos (RNBD)** | Decreto 1074/2015 arts. 2.2.2.25.x | Documentado en `HABEAS_DATA.md` pero no implementado en app | Crear módulo `app/infrastructure/rnbd/` con export JSON compatible con SIC |
| 5.1.11 | **Bitácora de acceso (audit log)** | Res. 1995/1999 art. 16, Ley 1581 | Implementado pero con bug PHI (ver Frente 10) | Refactorizar a redacción sin PII/PHI |
| 5.1.12 | **Plan de contingencia / backup** | Ley 1581/2012 art. 17 literales g, h | Implementado local | Documentar procedimiento escrito + cifrado AES-256 backups |

### 5.2 Política de retención (Res. 1995/1999 art. 28)
- HC adultos: **mínimo 15 años** desde última atención
- HC menores de 18: **mínimo 22 años** (algunos autores 25)
- Consentimientos informados: **mismo plazo que HC**
- Logs de acceso: **mínimo 5 años** (Ley 1581/2012)

### 5.3 Acciones transversales de cumplimiento
- Verificar que el **datosClinicos.js** no usa códigos viejos CIE-10 sin punto
- Validar que el **informe PDF** lleva firma del profesional con **tarjeta profesional colombiana** (Ley 1090 art. 5) y **fecha de expedición del título**
- Verificar **caducidad de consentimiento** (revalidación anual o por nueva evaluación)
- **Consentimiento específico para IA** (los 6 prompts del AIAsistente): declarar al paciente que parte de la narrativa usa IA generativa
- **Procedimiento de notificación de incidentes de seguridad** (Ley 1581 art. 17 literal h): 15 días hábiles a SIC + afectados

### 5.4 Criterio de cierre
- [ ] 8 plantillas documentales nuevas
- [ ] Cada plantilla firmada con escudo Normograma Colombiano
- [ ] Cada plantilla con numeración de versión y fecha
- [ ] Test E2E: simular 3 pacientes con diferentes poblaciones (adulto, menor, tercera edad) y verificar que se generan todos los consentimientos
- [ ] Validación con abogado (Sprint 3)

### 5.5 Norma
- Ley 1090 de 2006 — Código Deontológico del Psicólogo colombiano (arts. 2, 5, 36)
- Ley 1581 de 2012 — Protección de datos personales
- Decreto 1377 de 2013 — Reglamentación Ley 1581
- Ley 1616 de 2013 — Salud Mental Colombia
- Resolución 1995 de 1999 — Historia clínica
- Resolución 8430 de 1993 — Investigación en salud
- Resolución 3374 de 2000 — CIE-10 Colombia
- Resolución 2275 de 2023 — RIPS actualizados
- Resolución 3100 de 2019 — Estándares de habilitación
- Resolución 000042 de 2020 — Factura electrónica DIAN
- Decreto 1074 de 2015 — Régimen único sector comercio

### 5.6 Orden de ejecución
- **Sprint 2** (semanas 3-4): plantillas + integraciones; revisión legal Sprint 3

---

## FRENTE 6 — Integración protocolos de orden clínico (práctica clínica estándar 2024)

### 6.1 Estado actual
- **Protocolos** en `neurosoft-frontend/src/data/protocols/` (7 JSONs):
  - `protocolo_adulto_joven.json` (joven 18-49)
  - `protocolo_adulto_mayor.json` (mayor 50-99)
  - `protocolo_ninos_complementario.json` (niños 6-16)
  - `protocolos_memoria_verbal.json` (queja memoria)
  - `protocolos_casos_especiales.json` (afasias, analfabetismo, baja visión, motricidad)
  - `wais_iii_protocolo.json` (protocolo específico WAIS-III)
  - `wisc_iv_protocolo.json` (protocolo específico WISC-IV)
- Cada protocolo tiene `_meta.institucion: "<valor_anterior_con_atribución_a_tercero>"` → **a scrubbar a string vacío configurable** (ver Frente 4).
- 7 principios de redacción del informe **basados en práctica clínica estándar 2024** en `docs/manuales-ocr/EXTRACCION_WISC-IV_WAIS-III.md` §11.

### 6.2 Gap detectado
- Los protocolos ya están integrados (loader en `protocolLoader.js`), pero **no se aplican automáticamente** al iniciar una evaluación. El clínico debe seleccionarlos manualmente.
- Falta **orden canónico** que combine batería de screening + protocolo principal + baterías complementarias (algoritmo de práctica clínica estándar).
- Falta **versión extendida** para queja de memoria (screening + Grober + recuerdo selectivo).

### 6.3 Acción concreta
1. **Refactor `protocolLoader.js`** para que al crear una nueva evaluación:
   - Sugiera el protocolo según la edad y motivo de consulta
   - Aplique el orden de aplicación automáticamente en la cola de pruebas
2. **Implementar 7 principios de redacción clínica** en el generador de informe (`narrative.py`):
   - Bottom-up: de dominios a funciones, no de pruebas a dominios
   - No usar "conserva" en niños (usar "rinde acorde a lo esperado para su edad")
   - Prefijo DIS- en adultos para nombrar déficits (ej. "DIS-atencional" no "déficit atencional")
   - No repetir información del paciente en cada sección
   - No hablar de la PRUEBA sino de la FUNCIÓN evaluada
   - Considerar desarrollo (no comparar 6 años con 16)
   - Usar algoritmos diagnósticos como árbol (basado en práctica clínica estándar pediátrica)
3. **Generar protocolo sugerido** en `EvalStartPage` con preview del orden de aplicación y tiempo estimado total.
4. **Tiempos estimados** documentados (de práctica clínica estándar 2024):
   - Adulto joven completo: ~3h 30min en 2 sesiones
   - Adulto mayor completo: ~2h 30min en 2 sesiones (con pausas)
   - Niños 6-16: ~1h 45min en 1-2 sesiones
   - Queja memoria: ~1h 15min

### 6.4 Criterio de cierre
- [ ] 7 principios reflejados en el generador de informe (test E2E sobre 3 informes)
- [ ] Sugerencia automática de protocolo según edad + motivo consulta
- [ ] Tiempo estimado visible en el flujo de aplicación
- [ ] Validación con clínico (`[PROFESIONAL_CONFIGURADO]`) y opcionalmente con 1-2 usuarios externos

### 6.5 Norma
- Práctica clínica estándar 2024 (estructura y orden de aplicación, no protegible por copyright)
- Neuronorma Colombia 2017 (cap. 4 — baterías)
- No es copyright: el orden de aplicación es práctica clínica estándar

### 6.6 Orden de ejecución
- **Sprint 2** (semana 4): refactor protocoloLoader + 7 principios narrativa

---

## FRENTE 7 — Migración baremos faltantes (manuales + Excel)

### 7.1 Inventario de baremos en el sistema actual

**Total:** 174 tests en `BD_NEURO_MAESTRA.json`:
- 92 infantil (0-16 años)
- 30 adulto_joven (18-49)
- 52 adulto_mayor (50+)

**Tipos de cálculo:** `rango_puntaje`, `z_score`, `escolaridad_pc50`, `clasificacion_fija`, `comparativo`, `ajuste`, `suma_a_indice`, `wais_range`, `desconocido`.

### 7.2 Gaps por prueba (de la extracción WAIS/WISC + comparación con Excel)

| # | Prueba | Sistema actual | Fuente para completar | Acción |
|---|---|---|---|---|
| 7.2.1 | WISC-IV **normas raw→escalar por edad** (Cuadros A-1 a A-9) | ✅ Implementado (970-3,636 entradas) | OCR destruido págs 240-279 — **NO reusar OCR** | Confirmar valores contra el PDF original del usuario; si no, comprar Manual Técnico WISC-IV (Pearson) |
| 7.2.2 | WISC-IV **discrepancias por edad/par** (Cuadro B-1) | ❌ Umbral constante 23 pts | Tabla completa extraída del OCR pág 291 — `[verificar decimales]` | Refactor `wisc_discrepancy.py` con lookup por edad y par (datos en `EXTRACCION_WISC-IV_WAIS-III.md` §3) |
| 7.2.3 | WISC-IV discrepancias B-2 a B-8 | ❌ No implementado | OCR rotado págs 292-303 | Re-OCR con rotación 90° o extraer del PDF con herramienta visual |
| 7.2.4 | WISC-IV discrepancias B-9, B-10 (proceso) | ❌ No implementado | OCR limpio págs 304-305 (ya extraído en §4 del informe) | Implementar como nueva función `wisc_proceso_discrepancy()` |
| 7.2.5 | WAIS-III raw→escalar (Tabla A-1) | ✅ Implementado (132-804 entradas) | Manual OCR limpio pág 203-213 | **Auditar exhaustivamente** los valores poblados vs Tabla A-1 (adulto joven vs mayor vs tercera edad) |
| 7.2.6 | WAIS-III sumas→CI (Tablas A-2 a A-8) | ✅ Implementado (37-199 entradas) | Manual OCR limpio pág 214-223 (ya extraído) | Auditar gaps; `AdWASIEVer` 109 vs esperado ~150, `AdWAISEMan` 91 vs ~140 |
| 7.2.7 | WAIS-III discrepancias B-1, B-2 | ❌ No implementado | OCR rotado pág 224-228 | Re-OCR con rotación |
| 7.2.8 | WAIS-III discrepancias B-3 (subprueba-vs-media) | ❌ No implementado | OCR limpio pág 229-230 (ya extraído en §11) | Implementar `wais_subtest_vs_mean_discrepancy()` |
| 7.2.9 | WAIS-III **discrepancias nivel proceso** (B-4, B-5, B-6) | ❌ No implementado | OCR rotado | Re-OCR |
| 7.2.10 | Yesavage GDS-15 (depresión anciano) | ✅ `EscYesavage` (baremos en `screening.js:300+`) | (decisión usuario: "eso ya lo tengo") | Verificar baremos contra Sheikh 1986 (versión original 15 ítems) y Martínez de la Iglesia 2002 (validación española) |
| 7.2.11 | MoCA (Montreal Cognitive Assessment) | ✅ `MoCA` (screening.js) | Nasreddine 2005 original | Verificar baremos para Colombia —Hernández-Niño 2018 (Bucaramanga, n=493) publicó puntos de corte ajustados por escolaridad |
| 7.2.12 | MMSE Folstein | ✅ `MMSE` (screening.js) | Folstein 1975 | Verificar puntos de corte Colombia: Rosselli 2000 (Bucaramanga) ≥24 normal, ≥18 demencia, y por escolaridad (analfabeta ≥17) |
| 7.2.13 | BDI-II Beck | ✅ `EscBeck` (screening.js) | Beck 1996 | Verificar puntos de corte: 0-13 mínimo, 14-19 leve, 20-28 moderado, 29-63 grave |
| 7.2.14 | Escala Lawton IADL | ✅ `EscLawton` (screening.js) | Lawton Brody 1969 | 8 ítems AIVD; mujer 0-8, hombre 0-5; pérdida ≥2 = frágil |
| 7.2.15 | Escala Kertesz (Afasia) | ✅ `EscKertesz` (screening.js) | Kertesz 1982 (WAB) | Verificar puntos de corte: 0-25 muy severa, 26-50 severa, 51-75 moderada, ≥76 leve/recuperada |
| 7.2.16 | GDS-15 / GDS-5 (versión corta) | (parcial) | Sheikh 1986 / Hoyl 1999 | Validar disponibilidad GDS-5 (truncada) |
| 7.2.17 | INECO Frontal Screening (IFS) | ⚠️ `EscQueja` (probable) | Torralva 2009 | IFS max 30, ≥25 normal; subítems: programación, interferencia, control inhibitorio |
| 7.2.18 | **SNAP-IV (TDAH)** | ⚠️ `screening.js` parcial | Swanson 1992 | 18 ítems: 9 inatención + 9 hiperactividad/impulsividad; baremos por edad y sexo |
| 7.2.19 | **PHQ-9** | ⚠️ parcial | Kroenke 2001 | 9 ítems; puntos de corte: 5, 10, 15, 20 |
| 7.2.20 | **PCL-5 (TEPT)** | ⚠️ parcial | Weathers 2013 | 20 ítems DSM-5; corte ≥33 probable TEPT |
| 7.2.21 | **GAD-7 (ansiedad)** | ⚠️ parcial | Spitzer 2006 | 7 ítems; corte ≥10 ansiedad moderada |
| 7.2.22 | **WMS-III lógico / recuerdo** | ❌ `ViMRemRec` no poblado | Wechsler 1997 WMS-III | Pendiente baremos Neuronorma AM |
| 7.2.23 | **Torre de Londres (TOL)** | ❌ `ViTLRes` corrupto | Culbertson 2004 manual | Pendiente baremos (ver §7.2.24) |
| 7.2.24 | **TOL — Normas colombianas** | ❌ | Rosas 2003 / Arango-Lasprilla 2017 | Validar baremos colombianos |
| 7.2.25 | **CVLT-II** (no CVLT original) | ❌ No en sistema | Delis 2000 | Evaluar si se agrega (licenciamiento) |
| 7.2.26 | **Stroop** | ✅ Implementado | Golden 1978 versión | Auditar baremos (probablemente colombianos están en BD ya) |
| 7.2.27 | **FCR (Figuras de Rey)** | ✅ `NiFCROCop`, `NiFCRORec` | Rey 1941 / Osterrieth 1944 / Meyers 1995 | Auditar baremos: Meyers & Meyers 1995 sistema scoring |
| 7.2.28 | **TMT A y B (adulto mayor y joven)** | ✅ `AdTMTA`, `AdTMTB` | Reitan 1958 / Tombaugh 2004 | Auditar baremos por edad/sexo/escolaridad |
| 7.2.29 | **SDMT oral** | ✅ `SDMT` | Smith 1982 | Auditar baremos |
| 7.2.30 | **Fluidez fonológica / semántica** | ✅ `FluidP`, `FluidAnim`, `FluidM` | Benton 1967 / Spreen-Strauss | Auditar; baremos colombianos disponibles (Arango-Lasprilla 2017 cap. 6) |
| 7.2.31 | **WISC-IV Información (subprueba suprimida)** | ❌ No en `baterias/infantil` | Manual WISC-IV | Agregar como `NiWiscInd` |
| 7.2.32 | **Subpruebas proceso WISC-IV** (DCsub, RDsub, RA, RE) | ❌ | Manual WISC-IV cap. 5 | Pendiente decisión si se agregan |
| 7.2.33 | **WAIS-III Dígitos directo vs inverso** (separados) | ❌ `AdDDir` vs `AdDInv` faltan como claves | Manual WAIS-III | Agregar como subpruebas independientes |
| 7.2.34 | **WAIS-III Búsqueda de Símbolos** | ❌ Falta clave explícita `AdBusSim` | Manual WAIS-III | Agregar |
| 7.2.35 | **WAIS-III Matrices** | ❌ Falta clave explícita `AdMatr` | Manual WAIS-III | Agregar |
| 7.2.36 | **WAIS-III Historietas (Ordenamiento Dibujos)** | ✅ `AdWAISHI` | — | OK |

### 7.3 Origen de datos para los baremos faltantes

| Fuente | Formato | Costo | Disponibilidad |
|---|---|---|---|
| **Neuronorma Colombia 2ª ed.** (Arango-Lasprilla & Rivera 2017) | Calculadora online + regresiones | Comprar libro (~$60 USD) | Alta |
| **MANUAL DE APLICACIÓN WISC-IV / WAIS-III** (Editorial El Manual Moderno) | Tablas PDF | **Ya tienes el libro físico** | ✅ |
| **MANUAL TÉCNICO WISC-IV / WAIS-III** | Tablas extendidas | Comprar a Pearson | Media |
| **MISISTEMAV1.xlsm** del usuario | Excel | **Ya tienes** | ✅ (5.7 MB) |
| **Papers colombianos** (Hernández-Niño 2018, Rosselli 2000, etc.) | Artículos PubMed | Gratis | Alta |

### 7.4 Plan de migración
1. **Corto plazo (Sprint 1-2):** completar las 18 pruebas marcadas ✅ con auditoría exhaustiva
2. **Mediano plazo (Sprint 2-3):** agregar las 9 pruebas marcadas ❌ usando como base el manual técnico + el Excel del usuario
3. **Largo plazo (Sprint 3+):** comprar Manual Técnico WISC-IV / WAIS-III y Manuales Técnicos de subpruebas si se requiere máxima precisión

### 7.5 Criterio de cierre
- [ ] 174 → 195+ pruebas en `BD_NEURO_MAESTRA.json`
- [ ] Cada baremo con metadata: `fuente` (ej. "WISC-IV Manual 2003 p.291"), `poblacion` (ej. "Colombia 6:0-16:11"), `año_publicacion`, `n_muestra`
- [ ] Cada nuevo baremo con test unitario que verifique 3 valores conocidos (gold standard)
- [ ] Backup `BD_NEURO_MAESTRA.backup-pre-auditoria-final.json` antes de cualquier cambio

### 7.6 Norma
- Arango-Lasprilla JC, Rivera D (Eds.). (2017). *Neuropsicología en Colombia: Datos normativos, estado actual y retos a futuro*. Universidad de San Buenaventura.
- Strauss E, Sherman EMS, Spreen O. (2006). *A Compendium of Neuropsychological Tests*. 3rd ed. Oxford.
- Wechsler D. (2003, 2008). *WAIS-III / WISC-IV Technical and Interpretive Manual*. Psychological Corporation.
- Nasreddine ZS et al. (2005). The Montreal Cognitive Assessment (MoCA). *J Am Geriatr Soc*, 53(4), 695-699.
- Rosselli D et al. (2000). MMSE en Bucaramanga. *Acta Neurol Colomb*.

### 7.7 Orden de ejecución
- **Sprint 1-2**: completar pruebas marcadas ✅ (auditoría) y agregar las ❌ más críticas (Yesavage, MoCA, MMSE confirmadas)
- **Sprint 3**: completar el resto; considerar compra de Manuales Técnicos

---

## FRENTE 8 — Corrección catálogo escalas y baremos screening

### 8.1 Hallazgos verificados

| # | Prueba | Bug | Archivo:línea | Acción |
|---|---|---|---|---|
| 8.1.1 | **GADS** (renombrar) | "GADS" sugiere Generalized Anxiety Disorder Scale. **El manual es "Gilliam Asperger's Disorder Scale"** (James E. Gilliam 2001, ISBN 978-970-729-365-6) | `neurosoft-frontend/src/data/screening.js` (claves GADS*) | Renombrar a `GADS_GilliamAsperger` o `ESCALAGilliam`; usar para TEA, no ansiedad |
| 8.1.2 | **GAD-7 vs Gilliam** | Si el clínico busca ansiedad generalizada, el sistema no ofrece GAD-7 (Spitzer 2006) | `screening.js` | Agregar GAD-7 (7 ítems, 4 opciones Likert, corte ≥10) |
| 8.1.3 | **SCARED-41** | Índices de subescalas incorrectos: Fobia Social items_idx `[2,8,14,21,28,23,24,40]` incluye `23,24,40` que en matriz original son de otra subescala | `neurosoft-frontend/src/data/screening.js:783-789` | Reconstruir índices desde Birmaher 1997 original |
| 8.1.4 | **SCARED-5** (versión corta) | ¿Existe? | (mismo archivo) | Validar con Birmaher 1999; si no, omitir |
| 8.1.5 | **C-SSRS (riesgo suicida)** | ✅ Implementado en `TherapyPage` (M-3 sprint mayo 2026) | `neurosoft-frontend/src/app/therapy/TherapyPage.jsx` | Verificar algoritmo 1-5 con C-SSRS 2014 |
| 8.1.6 | **SDMT** | Consolidación con `OrSD/OrTMTA/OrTMTB` (z-scores Neuronorma AM) | `BD_NEURO_MAESTRA.json` | Verificar que no hay duplicación conceptual |
| 8.1.7 | **TMT-A y TMT-B** en adulto mayor | `ViTMTA`/`ViTMTB` mapeados a `desconocido` (ver §2.1.1) | `BD_NEURO_MAESTRA.json` | Cambiar a `z_score` |
| 8.1.8 | **Stroop** | ¿Falta `AdStroopP`/`AdStroopC`? | `BD_NEURO_MAESTRA.json` | Auditar |
| 8.1.9 | **INECO Frontal Screening (IFS)** | ¿Implementado? | `screening.js` | Verificar; si no, agregar |
| 8.1.10 | **FrSBe (Frontal Systems Behavior Scale)** | ¿Implementado? | (varios) | Validar |
| 8.1.11 | **BRIEF-A / BRIEF-2 (conducta)** | ❌ No implementado | (varios) | Pendiente decisión |
| 8.1.12 | **SCL-90-R (síntomas generales)** | ❌ No implementado | (varios) | Licencia Derogatis; evaluar |
| 8.1.13 | **Conners 3 (TDAH)** | ❌ No implementado | (varios) | Licencia MHS; evaluar |
| 8.1.14 | **WURS (Wender Utah, TDAH adulto)** | ❌ No implementado | (varios) | Ward 1993; dominio público |

### 8.2 Acción concreta
1. **Refactor `screening.js`** para separar por constructo (no por nombre): `SCALES_DEPRESSION`, `SCALES_ANXIETY`, `SCALES_TDAH`, `SCALES_TEA`, `SCALES_TCL`, `SCALES_FUNCIONAMIENTO_ADAPTATIVO`, `SCALES_MEMORIA`, `SCALES_FUNCIONES_EJECUTIVAS`
2. **Renombrar GADS** consistentemente
3. **Validar SCARED** con Birmaher 1997
4. **Crear test de regresión** que valide 3+ baremos por escala
5. **Crear UI wizard** que pregunte motivo de consulta y sugiera batería (ya hay M-8 screeningSugerencias.js con 14 reglas, auditar)

### 8.3 Criterio de cierre
- [ ] Catálogo refactorizado
- [ ] GADS renombrado consistentemente
- [ ] SCARED corregido
- [ ] 5 tests de regresión por cada escala

### 8.4 Norma
- Birmaher B et al. (1997). The Screen for Child Anxiety Related Emotional Disorders (SCARED). *J Am Acad Child Adolesc Psychiatry*, 36(4), 545-553.
- Gilliam JE. (2001). *Gilliam Asperger's Disorder Scale (GADS)*. PRO-ED.
- Spitzer RL et al. (2006). A brief measure for assessing generalized anxiety disorder: the GAD-7. *Arch Intern Med*, 166(10), 1092-1097.
- Posner K et al. (2011). The Columbia–Suicide Severity Rating Scale (C-SSRS). *Am J Psychiatry*.

### 8.5 Orden de ejecución
- **Sprint 2** (semana 3): refactor screening.js + corrección bugs

---

## FRENTE 9 — Informe PDF rediseñado + 7 principios de redacción

### 9.1 Estado actual
- **6 variantes de informe PDF** en `neurosoft-backend/app/infrastructure/report_pro/variants/`:
  - `pro.py` (ambulatoria adulto/escolar)
  - `pediatric.py` (pediátrica)
  - `medicolegal.py` (médico-legal)
  - `junta_medica.py` (1-2 págs)
  - `inconcluso.py` (evaluación inconclusa)
  - `therapy_closure.py` (cierre terapia)
- **Base + helpers:** `base.py`, `charts.py`, `helpers.py`, `narrative.py`, `theme.py`
- **Template dispatcher:** `__init__.py:generate_pro_pdf(template=...)`
- **Color theme:** TEAL/NAVY (`theme.py`)
- **Issue crítico:** informes actuales no aplican los 7 principios de redacción clínica (basados en práctica clínica estándar 2024).

### 9.2 Los 7 principios de redacción (extraídos)

1. **Bottom-up**: ir de dominios a funciones (ej. "atención" → "atención sostenida", "selectiva", "alternante") NO de pruebas a dominios
2. **No usar "conserva" en niños** (usar "rinde acorde a lo esperado para su edad" o "dentro de rangos esperados para su grupo normativo")
3. **Prefijo DIS- en adultos** para déficits (ej. "DIS-atencional", "DIS-mnésico") — en niños no aplica
4. **No repetir información del paciente** entre secciones (cada mención aporta algo nuevo)
5. **Hablar de la FUNCIÓN no de la PRUEBA**: "el paciente presenta dificultades en funciones ejecutivas" no "obtuvo puntaje bajo en WCST"
6. **Considerar desarrollo** (no comparar 6 años con 16; usar baremos por edad)
7. **Usar algoritmos diagnósticos** como árbol (basado en práctica clínica estándar pediátrica): TDAH + IRP-bajo + IMT-bajo = screening positivo; no diagnosticar sin criterios DSM-5-TR

### 9.3 Acción concreta
1. **Refactor `narrative.py`** para que el generador de narrativa integradora aplique los 7 principios automáticamente
2. **Nuevas cláusulas legales obligatorias** en el PDF (ver Frente 5):
   - Encabezado: "INFORME NEUROPSICOLÓGICO CONFIDENCIAL" + número de informe
   - "Profesional responsable": Nombre + Tarjeta Profesional + Universidad + Resolución
   - "Paciente": nombre, edad, fecha de evaluación
   - "Objetivo del informe": derivado del motivo de consulta
   - "Uso previsto": clínico / pericial / junta (si es el caso)
   - "Limitaciones": explicitadas (ej. "evaluación aplicada en una sola sesión")
   - "Fecha y lugar"
   - "Firma y sello"
3. **Gráficos profesionales** (ya hay `charts.py` con z-profile, radar, gaussiana, discrepancias): revisar
4. **Tablas de perfil** (escalares, índices, percentiles, IC, Gc, puntos fuertes/débiles)
5. **Versión "corta para junta médica"** (1-2 pp) ya existe pero auditar calidad
6. **Versión "para paciente"** (sin jerga técnica, lenguaje accesible) — **NUEVA**
7. **Generar PDF/A** (archivo archivable de largo plazo, Res. 1995/1999)

### 9.4 Criterio de cierre
- [ ] 7 principios validados en las 6 variantes
- [ ] Cláusulas legales en todas las variantes
- [ ] Versión "para paciente" nueva
- [ ] PDF/A en lugar de PDF estándar
- [ ] 3 informes muestra revisados con clínico

### 9.5 Norma
- Ley 1090/2006 art. 36 — Deberes del psicólogo
- Resolución 1995/1999 art. 17 — Informar
- APA Publications Manual 7th ed. — Estilo de informe
- CONFIL 2012 — Lineamientos éticos
- ISO 19005-1:2005 — Formato PDF/A

### 9.6 Orden de ejecución
- **Sprint 2** (semana 4): refactor narrativa + 7 principios
- **Sprint 3** (semana 5): versión paciente + PDF/A

---

## FRENTE 10 — Seguridad y kill-switches (SPRINT 0)

### 10.1 Estado actual — vulnerabilidades verificadas

| # | Severidad | Hallazgo | Archivo:línea | Exploit |
|---|---|---|---|---|
| 10.1.1 | 🔴 Crítico | **Endpoint `/system/update` sin `require_admin`** — cualquier usuario autenticado puede subir un `.nsupdate` arbitrario y ejecutar código en el servidor | `neurosoft-backend/app/presentation/api/v1/update.py:27-28` | `curl -X POST /api/v1/system/update -H "Authorization: Bearer $TOKEN" -F "file=@evil.nsupdate"` |
| 10.1.2 | 🔴 Crítico | **IDOR en `patients.py`** — los handlers `/:patient_id` y `/:patient_id/export` solo reciben `patient_id: str` y delegan a UC sin verificar ownership | `neurosoft-backend/app/presentation/api/v1/patients.py:178,190,205,222` | `GET /api/v1/patients/<otro_paciente_id>` retorna datos completos sin auth cross-tenant |
| 10.1.3 | 🔴 Crítico | **Audit log filtra PHI** en `changes` — se serializa con `json.dumps(changes, default=str)[:20000]` todos los campos del ORM (HC, motivo, antecedentes, documentos) | `neurosoft-backend/app/infrastructure/audit/listeners.py:118` | Filtrar auditoría retorna historia clínica completa |
| 10.1.4 | 🔴 Crítico | **Kill switch `NEUROSOFT_DISABLE_AUTH=1`** desactiva autenticación si `settings.env != "production"`, pero `settings.env` puede no estar seteado en builds antiguos | `neurosoft-backend/app/main.py:377` | Variable de entorno accidental desactiva auth |
| 10.1.5 | 🔴 Crítico | **Reset silencioso admin password** — `NEUROSOFT_RESET_ADMIN_PASSWORD=1` sobreescribe el hash en cada arranque | `neurosoft-backend/app/infrastructure/auth/auth_service.py:301` | Si la env var queda en `.env` post-troubleshooting, admin se sobreescribe |
| 10.1.6 | 🟠 Alto | **Endpoint WISC forma corta** `wisc_forma_corta_cit` carga JSON de `app/domain/data/` | `neurosoft-backend/app/presentation/api/v1/clinical_extras.py:119-127` | Confirmar que el JSON existe y validar entrada (✓ verificado: `wisc_iv_forma_corta_cit.json` existe) |
| 10.1.7 | 🟠 Alto | **Carga `baterias_alternas.json` y `reservorio_recomendaciones.json`** sin validación de path traversal | `clinical_extras.py:160-162, 337-339` | Confirmar paths; auditar si user input entra al filename |
| 10.1.8 | 🟠 Alto | **JWT verify_exp** — confirmar que está explícito (sí verificado) | `auth_service.py` | Sin `verify_exp` explícito, tokens podrían ser eternos |
| 10.1.9 | 🟠 Alto | **Rate limiting in-memory** — no distribuido; reinicio del server borra contadores | `core/` (varios) | IP atacante puede reintentar |
| 10.1.10 | 🟠 Alto | **PII redactor en logs** — parcial | `core/logging_redactor.py` | Auditar expresiones regex |
| 10.1.11 | 🟠 Alto | **Token blacklist** implementado pero no se aplica consistentemente | `auth_service.py` | Logout real vs solo client-side |
| 10.1.12 | 🟡 Medio | **Secret management** — variables en `.env` (no vault); se commitea accidentalmente | `app/core/config.py` | Documentar uso de `.env.example` |
| 10.1.13 | 🟡 Medio | **Sin CSP headers** | `main.py` middleware | XSS en frontend potencialmente ejecutable |

### 10.2 Acción concreta Sprint 0 (días 1-3)

1. **Día 1 mañana** — Cerrar 10.1.1:
   - Agregar `Depends(require_admin)` al endpoint `/system/update`
   - Log obligatorio con user_id de quien subió el .nsupdate
   - Verificar que la firma del .nsupdate sea válida (HMAC-SHA256 con clave en config)
2. **Día 1 tarde** — Cerrar 10.1.2:
   - Implementar `verify_ownership(patient_id, current_user)` helper
   - Aplicar a TODOS los handlers de `patients.py`
   - Test E2E con dos usuarios: usuario A no debe ver pacientes de usuario B
3. **Día 2 mañana** — Cerrar 10.1.3:
   - Refactorizar `audit/listeners.py:_diff()` para whitelist de campos auditables
   - Hash SHA-256 de campos sensibles (HC, documentos) en lugar del valor
   - Mantener trazabilidad sin PII
4. **Día 2 tarde** — Cerrar 10.1.4 y 10.1.5:
   - Eliminar `NEUROSOFT_DISABLE_AUTH` del código (force disable auth solo en development con flag de log explícito)
   - Eliminar `NEUROSOFT_RESET_ADMIN_PASSWORD` (cambiar a flow normal con endpoint de admin autenticado)
   - Ambos removidos de `.env.example` con comentario "# no usar — dejado para auditoría"
5. **Día 3** — Cerrar 10.1.6-10.1.13:
   - Path traversal protection en carga de JSON (`resolve()` + check está en `/app/domain/data/`)
   - CSP header estricto en `main.py`
   - Verificar verify_exp, blacklist de tokens, rate limit
   - Documentar secrets management

### 10.3 Criterio de cierre
- [ ] 5 kill-switches eliminados
- [ ] Test E2E multi-tenant pasa (2 usuarios, 3 pacientes, asserts cross-tenant)
- [ ] Audit log con redacción PHI verificado (test que sube un paciente, hace cambios, lee audit, valida que no hay PII)
- [ ] Penetración test interno con OWASP ZAP (al menos 5 vulnerabilidades más identificadas y resueltas)
- [ ] Documento de seguridad `docs/seguridad/MODELO_AMENAZAS.md` (STRIDE aplicado a la app)

### 10.4 Norma
- OWASP Top 10 2021
- CWE (Common Weakness Enumeration)
- ISO 27001 (controles de acceso, log de auditoría)
- HIPAA Security Rule (modelo de referencia internacional para software de salud)
- Ley 1581/2012 art. 17 literales f, h (medidas de seguridad, notificación de incidentes)
- Resolución 1995/1999 art. 16 (trazabilidad de acceso a HC)

### 10.5 Orden de ejecución
- **Sprint 0 (crítico, días 1-3):** 5 hallazgos críticos
- **Sprint 1 (semana 2):** 8 hallazgos altos y medios

---

## FRENTE 11 — Accesibilidad + dark mode + UX

### 11.1 Hallazgos

| # | Severidad | Hallazgo | Acción |
|---|---|---|---|
| 11.1.1 | 🟡 | **Skill `dark-mode-fix` ya existe** pero no se ha aplicado sistemáticamente | Ejecutar skill sobre las 22 páginas principales |
| 11.1.2 | 🟡 | 6 variantes de informe PDF (TEAL/NAVY) sin tema oscuro | Tema oscuro para informe |
| 11.1.3 | 🟡 | Falta **A11y** (accesibilidad WCAG 2.1) en formularios | Contraste mínimo 4.5:1, foco visible, navegación por teclado |
| 11.1.4 | 🟡 | **PWA / offline strategy** ya documentada (Service Worker deshabilitado en pywebview) | Documentar arquitectura en `docs/arquitectura/PWA_OFFLINE.md` |
| 11.1.5 | 🟡 | **Tooltip glossary** (P-4) implementado en `EvalResultsPage` pero falta extender a `InformesPage` | Extender |
| 11.1.6 | 🟡 | **ConfirmProvider** ya reemplaza `window.confirm()` | Auditar que no haya window.confirm/alert nativos |
| 11.1.7 | 🟡 | `safeLS helper` para localStorage | Auditar uso en las 22 páginas |

### 11.2 Acción concreta
- Aplicar skill `dark-mode-fix` en los componentes principales
- Test A11y con axe-core (extension Chrome) sobre las 22 páginas
- Documentar PWA/offline architecture

### 11.3 Criterio de cierre
- [ ] 0 colores hardcoded
- [ ] Contraste WCAG AA en todas las páginas
- [ ] Navegación por teclado funcional
- [ ] axe-core sin issues críticos

### 11.4 Orden de ejecución
- **Sprint 2-3** (paralelo a otros frentes)

---

## FRENTE 12 — CI/CD, regresión clínica, docs, observabilidad

### 12.1 Estado actual

**Tests existentes (verificados):**
- **280 tests** del motor clínico en `neurosoft-backend/tests/unit/clinical_engine/` (15 archivos)
- **3 funciones** de test integración con **15 fixtures** ground truth
- **280+ tests** totales backend
- **Frontend:** Playwright E2E `smoke.spec.js` (no auditado en este plan, ver skill `audit-completo`)

**Documentación existente (NO reescribir):**
- `docs/legal/HABEAS_DATA.md` (7.8 KB) — Ley 1581
- `docs/legal/GUIA_REGISTRO_INVIMA_SaMD.md` (14 KB) — INVIMA SaMD
- `docs/audits/AUDITORIA_EXCEL_VS_MOTOR.md` — baremos vs Excel
- `docs/audits/AUDITORIA_55_TESTS_SOLO_MOTOR.md` — 55 tests
- `docs/planning/CLINICAL_ROADMAP.md` — roadmap clínico
- `docs/manuales-ocr/EXTRACCION_WISC-IV_WAIS-III.md` — WISC/WAIS

### 12.2 Acción concreta
1. **GitHub Actions / CI pipeline**:
   - Backend: `pytest -v` (gate)
   - Backend: `python -m py_compile` (gate)
   - Frontend: `npm run lint --max-warnings 0` (gate)
   - Frontend: `npm run build` (gate)
   - Playwright E2E
2. **Regresión clínica**: 15 fixtures + snapshot nuevos por cada cambio de baremo
3. **Documentación**:
   - `docs/arquitectura/MAPA_MODULOS.md` — diagrama de capas
   - `docs/arquitectura/FLUJO_DATOS.md` — DFD nivel 1
   - `docs/seguridad/MODELO_AMENAZAS.md` — STRIDE
   - `docs/clasificacion/RECLASIFICACION_2026.md` — reclasificación CI
   - `docs/NOTAS_DESARROLLO.md` (interno) — entradas genéricas sobre decisiones de diseño sin atribución a terceros
4. **Observabilidad**:
   - Sentry para tracking de errores
   - Logging estructurado JSON
   - Métricas Prometheus básicas (request count, latency, error rate)
5. **Backup automático** cifrado AES-256 con rotación 7/30/365 días
6. **Plan de recuperación ante desastre (DRP)** documentado

### 12.3 Criterio de cierre
- [ ] CI pipeline verde en cada PR
- [ ] 280+ tests backend + smoke E2E + 15 ground truth
- [ ] Documentación arquitectura completa
- [ ] Backups automáticos verificados
- [ ] DRP documentado y probado (simulacro trimestral)

### 12.4 Norma
- ISO/IEC 25010 (calidad de software)
- ISO/IEC 12207 (procesos de ciclo de vida)
- ISO 14721 (OAIS — referencia para backups)
- Ley 1581/2012 art. 17 literal h (medidas de seguridad y planes de contingencia)
- Resolución 1995/1999 (conservación HC)

### 12.5 Orden de ejecución
- **Sprint 3-4** (paralelo)

---

## 13. Plan de sprints consolidado

### Sprint 0 — Seguridad Crítica (días 1-3)
- Frente 10: 5 hallazgos críticos (kill-switches, IDOR, audit log PHI, update.py)
- **Entregable:** release bloqueado si Sprint 0 no completa

### Sprint 1 — Motor clínico + CIE-10 (semana 1-2)
- Frente 2: TMT-B, ViTLRes, ComparativoStrategy, sentinel 9999 (4 críticos)
- Frente 2: wisc_discrepancy.py refactor con Cuadro B-1 por edad
- Frente 2: suspensión WISC-IV/WAIS-III
- Frente 3: catálogo CIE-10/CIE-11 con punto oficial
- Frente 7: auditoría exhaustiva de las 18 pruebas marcadas ✅
- **Entregable:** 8 nuevos tests pasan, regresión ground truth intacta

### Sprint 2 — Documental + Scrub (semana 3-4)
- Frente 4: scrub atribuciones a terceros (10 ocurrencias) + capa protegida Pearson
- Frente 5: 12 plantillas documentales (consentimientos, contratos, HC, informe, RIPS, factura, aviso privacidad, RNBD)
- Frente 6: protocoloLoader refactor + 7 principios narrativa
- Frente 8: refactor screening.js + corrección GADS/SCARED
- Frente 9: refactor narrative.py con 7 principios + cláusulas legales
- **Entregable:** release beta con scrub completo, plantillas legales, screening corregido

### Sprint 3 — UX + Legal final (semana 5-6)
- Frente 1: reclasificación 5-6 bandas (validado con clínico)
- Frente 9: versión paciente + PDF/A
- Frente 11: dark mode + A11y
- Frente 12: CI/CD pipeline + docs arquitectura
- Revisión legal externa (abogado propiedad intelectual)
- **Entregable:** release candidato

### Sprint 4 — Pulido + Distribución (semana 7-8)
- Frente 7: completar baremos restantes (35+ pruebas adicionales)
- Frente 12: observabilidad (Sentry, métricas), backups automatizados, DRP
- Beta tester feedback (M-3 adelante)
- **Entregable:** release de producción

---

## 14. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Manual Técnico WISC-IV no disponible (faltan SEM, RCI, validez) | Alta | Medio | Documentar limitación en informe; usar aproximación desde Manual Aplicación; consultar papers secundarios |
| OCR destruido en Apéndice A WISC-IV no recuperable | Media | Bajo | Usar Manual Aplicación + Excel del usuario como cross-check |
| Cambios regulatorios MinSalud no anticipados | Baja | Alto | Monitoreo bimestral de normograma; suscripción a alertas SIC |
| Beta tester reporta bug clínico crítico post-release | Media | Crítico | 15 ground truth + 280 tests minimizan; plan de hotfix <24h |
| Clasificación DSM-5-TR/CIE-11 cambia | Baja | Alto | Diseño modular permite actualizar tabla sin tocar lógica |
| Tercero cualquiera reclama atribución | Baja | Bajo | Scrub completo + docs internos sin atribución; sin contenido protegido |
| Pearson reclama copyright | Baja | Crítico | Capa protegida con checkbox + certificación + audit log; disclaimers explícitos |

---

## 15. Resumen de entregables por sprint

| Sprint | Duración | Entregable | Bloqueo de release |
|---|---|---|---|
| 0 | 3 días | 5 hallazgos críticos de seguridad cerrados | Sí |
| 1 | 2 semanas | Motor clínico + CIE-10 + baremos validados | Sí |
| 2 | 2 semanas | Scrub + cumplimiento documental + screening corregido | Sí |
| 3 | 2 semanas | Reclasificación + UX + CI/CD | Sí |
| 4 | 2 semanas | Baremos completos + observabilidad + beta feedback | No (release candidato) |

**Total: 9-10 semanas para release de producción listo para distribución comercial en Colombia.**

---

## 16. Referencias normativas colombianas consolidadas

| Norma | Tema | URL oficial |
|---|---|---|
| Ley 1090/2006 | Código Deontológico del Psicólogo | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6625 |
| Ley 1581/2012 | Habeas Data | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981 |
| Decreto 1377/2013 | Reglamentación Ley 1581 | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=53646 |
| Decreto 1074/2015 | Decreto único sector comercio (RNBD) | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=77862 |
| Ley 1616/2013 | Salud Mental | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=52411 |
| Ley 23/1981 | Ética médica | https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=14314 |
| Ley 23/1982 | Derechos de autor | https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=3431 |
| Ley 44/1993 | Modificaciones a Ley 23 | https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=3427 |
| Resolución 1995/1999 | Historia clínica | https://www.minsalud.gov.co/Normatividad_Nuevo/RESOLUCI%C3%93N%201995%20DE%201999.pdf |
| Resolución 8430/1993 | Investigación en salud | https://www.minsalud.gov.co/sites/rid/Lists/BibliotecaDigital/RIDE/DE/DIJ/RESOLUCION-8430-1993.PDF |
| Resolución 3374/2000 | CIE-10 Colombia | https://www.minsalud.gov.co/Normatividad_Nuevo/RESOLUCI%C3%93N%203374%20DE%202000.pdf |
| Resolución 2275/2023 | RIPS actualizados | https://www.minsalud.gov.co/Normatividad_Nuevo/Resoluci%C3%B3n%20No.%202275%20de%202023.pdf |
| Resolución 3100/2019 | Habilitación | https://www.minsalud.gov.co/Normatividad_Nuevo/Resoluci%C3%B3n%20No.%203100%20de%202019.pdf |
| Resolución 000042/2020 | Factura electrónica DIAN | https://www.dian.gov.co/ |

---

## 17. Documentación a producir durante implementación

| Documento | Ubicación | Norma | Sprint |
|---|---|---|---|
| PLAN_MAESTRO_GLOBAL.md (este) | `docs/PLAN_MAESTRO_GLOBAL.md` | — | 0 |
| RECLASIFICACION_2026.md | `docs/clasificacion/` | DSM-5-TR, CIE-11 | 1 |
| AUDITORIA_FINAL_BAREMOS.md | `docs/audits/` | — | 1 |
| PROTOCOLOS_FUENTES.md (interno) | `docs/creditos/` | — | 2 |
| MAPA_MODULOS.md | `docs/arquitectura/` | ISO 25010 | 2 |
| FLUJO_DATOS.md | `docs/arquitectura/` | — | 2 |
| MODELO_AMENAZAS.md | `docs/seguridad/` | STRIDE | 0 |
| DRP_PLAN_RECUPERACION.md | `docs/seguridad/` | ISO 14721 | 3 |
| 8 plantillas documentales | `app/infrastructure/templates/` | Ley 1090, 1581, Res 1995, 2275 | 2 |
| TESTING_GUIDE.md | `docs/desarrollo/` | — | 3 |

---

## 18. Próximos pasos inmediatos

1. **Aprobación de este plan** por parte del usuario
2. **Salir de plan mode**
3. **Ejecutar Sprint 0** (3 días) — seguridad crítica
4. **Smoke test E2E** post-Sprint 0
5. **Iniciar Sprint 1** (motor clínico + CIE-10)

---

**Fin del plan maestro. Documento vivo — actualizar al final de cada sprint con hallazgos nuevos y decisiones tomadas.**

---

## 19. Sistema de identidad configurable (sin atribución a terceros)

El software es de Johan Sebastián Salgado Sarmiento, sin atribución a terceros en ninguna parte del código, manuales, plantillas, informes, ni artefactos distribuidos.

Toda la información del profesional, institución y contacto se captura en el primer inicio de sesión y se persiste cifrada en BD. Valores por defecto: **vacíos** (el clínico los completa desde ConfigPage).

### 19.1 Constantes configurables (cifradas en BD)

Módulo nuevo: `neurosoft-backend/app/core/config_institucion.py`

| Campo | Tipo | Obligatorio | Uso |
|---|---|---|---|
| `nombre_completo` | str | ✅ para generar informes | Encabezado del PDF, firma, consentimientos |
| `tarjeta_profesional` | str | ✅ para generar informes | Ley 1090/2006 art. 5 — credencial del psicólogo |
| `universidad` | str | — | Pie de informes y contratos |
| `fecha_tarjeta` | str | — | Res. 0123/YYYY |
| `resolucion` | str | — | Res. que avala la tarjeta profesional |
| `institucion_nombre` | str | — | Razón social si hay consultorio; vacío si es independiente |
| `institucion_nit` | str | ✅ para RIPS/factura | NIT o identificación para RIPS y factura electrónica |
| `institucion_direccion` | str | — | Dirección física para informes y facturas |
| `institucion_telefono` | str | — | Contacto en plantillas |
| `institucion_correo` | str | — | Contacto en plantillas |
| `institucion_logo_path` | str | — | Ruta a logo (opcional) para encabezados |
| `pie_pagina_pdf` | str | — | Texto del pie de página de informes |
| `codigo_habilitacion` | str | — | Res. 3100/2019 si la institución aplica |
| `sello_digital_path` | str | — | Imagen de sello o firma para PDF |

### 19.2 Acceso desde código

**Backend (Python):**

```python
from app.core.config_institucion import get_config_institucion

config = get_config_institucion(current_user_id)

# Uso en generador de PDF (ReportLab)
pdf.drawString(x, y, config.nombre_completo or "[NOMBRE DEL PROFESIONAL]")

# Uso en plantillas Jinja2
{{ config.nombre_completo or "[NOMBRE DEL PROFESIONAL]" }}
```

**Frontend (React):**

```jsx
import { useInstitucion } from "@/contexts/InstitucionContext";

const { config } = useInstitucion();
return <p>Profesional: {config.nombre_completo || <em>[Configurar en Configuración → Identidad]</em>}</p>;
```

### 19.3 Pantalla de configuración inicial (ConfigPage → tab "Identidad profesional")

- Inputs vacíos
- Validación: `nombre_completo` + `tarjeta_profesional` obligatorios para poder generar informes o consentimientos
- Botón "Usar datos de prueba" para demos (rellena con datos ficticios claramente marcados como "[DEMO] — No usar en producción")
- Cifrado AES-256 en BD (helper `infrastructure/crypto.py` ya existe)

### 19.4 Comportamiento de placeholders en UI

| Caso | Visualización |
|---|---|
| Informe PDF, campo con valor | Muestra el valor normal |
| Informe PDF, campo vacío | Muestra `[NOMBRE DEL PROFESIONAL]` en gris cursiva |
| Consentimiento, falta llenar | Banner amarillo: "Complete su identidad profesional en Configuración antes de generar documentos" |
| RIPS / Factura, falta NIT | Bloquea generación con mensaje claro |
| Login, sin configuración | Wizard de primer inicio fuerza a completar `nombre_completo` + `tarjeta_profesional` |

### 19.5 Lugares donde aparece cada placeholder

| # | Lugar | Campo |
|---|---|---|
| 1 | Informe PDF — encabezado | `config.nombre_completo` |
| 2 | Informe PDF — pie de página | `config.pie_pagina_pdf` |
| 3 | Informe PDF — firma y sello | imagen + `config.nombre_completo` |
| 4 | Informe PDF — bloque legal | `config.nombre_completo`, `config.tarjeta_profesional` |
| 5 | Consentimiento informado | "Yo, [NOMBRE_PROFESIONAL]..." |
| 6 | Consentimiento — datos del responsable | `config.institucion_*` |
| 7 | Asentimiento informado (menores) | Versión simplificada para el niño |
| 8 | Contrato de servicios | "EL PRESTADOR..." → `config.institucion_nombre` o `config.nombre_completo` |
| 9 | RIPS | Campo "Prestador" → `config.institucion_nit` + `institucion_nombre` |
| 10 | Factura electrónica | Emisor → `config.institucion_nit` + `institucion_nombre` |
| 11 | Aviso de privacidad | "El responsable del tratamiento es..." |
| 12 | App login screen | "NeuroSoft App" (constante, no configurable) |
| 13 | Protocolos JSON `_meta.institucion` | `""` (vacío, configurable desde ConfigPage) |
| 14 | Protocolos JSON `_meta.autor` | `"NeuroSoft App"` (fijo, no editable) |
| 15 | Protocolos JSON `_meta.fuente` | Eliminar el campo o `null` |
| 16 | Emails plantillas (6 tipos) | "Cordialmente, [NOMBRE]" |
| 17 | Diplo / certificado de evaluación | "Evaluador: [NOMBRE]" |
| 18 | Configuración SMTP (mail from) | `config.institucion_correo` |
| 19 | Reporte de auditoría (admin) | `config.nombre_completo` como filtro de eventos |

### 19.6 JSONs de protocolos — campos finales

```json
{
  "_meta": {
    "id": "protocolo_adulto_joven",
    "version": "1.0",
    "autor": "NeuroSoft App",
    "institucion": "",
    "fuente": null,
    "fecha_creacion": "2026-06-01",
    "poblacion": "adulto_joven"
  }
}
```

Cuando el clínico abre un protocolo y la UI detecta `institucion === ""`, muestra:
> "Institución no configurada. Puedes asignar una en Configuración → Identidad institucional."

### 19.7 Documento de desarrollo interno

**Archivo:** `docs/NOTAS_DESARROLLO.md` (entregable Sprint 2)

**Contenido:** entradas genéricas sobre decisiones de diseño, sin atribución a terceros, formato:
- "Orden de aplicación basado en práctica clínica estándar 2024"
- "Tiempos estimados tomados de protocolos clínicos publicados"
- "Estructura de informe basada en APA Publications Manual 7th ed."
- "Criterios de suspensión ajustados a manuales de aplicación publicados en español"

**Acceso:** solo para el desarrollador (no se distribuye).

### 19.8 Criterio de cierre

- [ ] Módulo `config_institucion.py` implementado con cifrado AES-256
- [ ] Contexto React `InstitucionContext` global
- [ ] Pantalla ConfigPage → tab "Identidad profesional" funcional
- [ ] Wizard de primer inicio (fuerza completar `nombre_completo` + `tarjeta_profesional`)
- [ ] Banner amarillo en consentimientos si falta identidad
- [ ] Bloqueo de generación de RIPS/factura si falta NIT
- [ ] Test E2E: 3 escenarios (todo configurado, parcial, vacío)
- [ ] Auditoría: 0 menciones a terceros en código distribuible (verificar con `grep`)
- [ ] JSONs de protocolos con `_meta.institucion: ""` y `_meta.autor: "NeuroSoft App"`

### 19.9 Norma
- Ley 1090/2006 art. 5 (identidad profesional con tarjeta)
- Ley 1581/2012 art. 17 literales a, c (responsable identificado, datos exactos)
- Resolución 1995/1999 art. 11 (firma y sello del profesional en informes)
- Resolución 2275/2023 (prestador identificado en RIPS)
- Resolución 000042/2020 DIAN (emisor identificado en factura)

### 19.10 Orden de ejecución
- **Sprint 2** (semana 3-4): modelo de datos + UI ConfigPage + wizard primer inicio
- **Sprint 3** (semana 5-6): integración en todos los lugares (informes, consentimientos, RIPS, factura)




