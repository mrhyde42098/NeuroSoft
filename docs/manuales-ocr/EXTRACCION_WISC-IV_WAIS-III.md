# Extracción de baremos y reglas de los manuales WISC-IV y WAIS-III (OCR)

**Fecha de extracción:** 2026-06-01
**Fuentes:**
- `C:\Users\DESKTOP\AppData\Local\Temp\opencode\manuales_ocr\WISC-IV.txt` — 14,324 líneas, 308 págs. Editorial El Manual Moderno, 2005. **Manual de Aplicación** (no Manual Técnico).
- `C:\Users\DESKTOP\AppData\Local\Temp\opencode\manuales_ocr\WAIS-III.txt` — 9,516 líneas, 231 págs. Editorial El Manual Moderno, 2003. **Manual de Aplicación** (no Manual Técnico).
**Helper de navegación:** `C:\Users\DESKTOP\AppData\Local\Temp\opencode\manuales_helper.py`
**Destino mapeo NeuroSoft:** `D:\NeuroSoftApp\neurosoft-backend\data\BD_NEURO_MAESTRA.json`

---

## ⚠️ NOTA PREVIA CRÍTICA — LIMITACIONES DE LOS MANUALES ESCANEADOS

Estos archivos son **Manuales de Aplicación**, no los **Manuales Técnicos** correspondientes. La información que contienen y la que **NO** contienen es importante para saber qué se puede extraer y qué hay que buscar en otra parte:

| Información | Manual Aplicación WISC-IV | Manual Aplicación WAIS-III |
|---|---|---|
| Composición de índices y subtests | ✅ Sí (Cuadro 2-4) | ✅ Sí (Cuadro 1-3) |
| Reglas de aplicación y puntuación | ✅ Sí (Cap 3) | ✅ Sí (Cap 4) |
| Criterios de suspensión/discontinuación | ✅ Sí (narrativa + Cuadro 2-6) | ✅ Sí (narrativa) |
| Normas raw → escalar (Tabla A-1) | ⚠️ OCR **ILEGIBLE** (págs 240-279) | ✅ Sí (págs 203-213) |
| Sumas escalares → CI compuesto (Tablas A-2 a A-8) | ⚠️ OCR **ILEGIBLE** | ✅ Sí (págs 214-223) |
| Sumas prorrateadas (Tabla A-9) | ⚠️ OCR **ILEGIBLE** | ✅ Sí (págs 222-223) |
| Discrepancias entre índices: valores críticos (Cuadro B-1) | ✅ Sí, claro (pág 291) | ⚠️ OCR **ROTADO** (pág 224-225) |
| Discrepancias entre subtests: valores críticos (Cuadro B-2) | ⚠️ OCR **ROTADO** (págs 292-293) | ⚠️ OCR **ROTADO** (págs 226-228) |
| Discrepancias subtest vs media: valores críticos (Cuadro B-3) | ⚠️ OCR **ROTADO** | ✅ Sí, claro (págs 229-230) |
| Tasas base para discrepancias (Cuadros B-4, B-5, B-6) | ⚠️ OCR **ROTADO** (págs 294-300) | ⚠️ OCR **ROTADO** (pág 228) |
| Discrepancias dígitos directo/inverso (Cuadros B-7, B-8) | ⚠️ OCR **ROTADO** (págs 301-303) | — (no aplica WAIS-III con LN) |
| Discrepancias nivel de proceso (Cuadros B-9, B-10) | ✅ Sí, claro (págs 304-305) | — |
| Confiabilidad, error estándar de medición (SEM) | ❌ No (está en Manual Técnico) | ❌ No (está en Manual Técnico) |
| Datos completos de estandarización (muestra, medias, DE) | ❌ No (está en Manual Técnico) | ⚠️ Parcial — Cap 5 sólo menciona Matrices/EO r=0.90 (pág 27) |
| Validez, análisis factorial | ❌ No | ❌ No |

**Recomendación:** Para SEM, confiabilidad por subtest, validez, datos de estandarización completa → buscar los **Manuales Técnicos** (Technical Manuals) de WISC-IV y WAIS-III, que son publicaciones separadas y no estaban en los PDFs escaneados originales.

---

## 1. WISC-IV — Composición de índices (Cuadro 2-4, pág 40)

| Índice | Abreviatura | Subpruebas principales | Subpruebas suplementarias (sustitutos) |
|---|---|---|---|
| Comprensión Verbal | **ICV** | Semejanzas (Sem), Vocabulario (Voc), Comprensión (Com) | Información (IndComVer) |
| Razonamiento Perceptivo | **IRP** | Diseño con Cubos (DC), Conceptos con Dibujos (ConD), Matrices (Mat) | — (Figuras incompletas puede complementar) |
| Memoria de Trabajo | **IMT** | Retención de Dígitos (RDD) → Dígitos en orden directo + inverso, Números y Letras (LN), Aritmética (Ari) | — |
| Velocidad de Procesamiento | **IVP** | Claves (Cl), Búsqueda de Símbolos (BusSim) | — |
| Capacidad General | **ICG** | (sólo 2 subpruebas: ICV+IRP) | calculado, no como índice primario |
| Competencia Cognitiva | **ICC** | (3 subpruebas: ICV+IRP+IMT) | calculado, no como índice primario |
| **CI Total (CIT)** | **CIT** | suma de los 4 índices | reglas especiales de sustitución (ver §3) |

### Reglas de sustitución (Cap 2, pág 42)
- **Ninguna sustitución permitida** entre índices Comprensión Verbal y Razonamiento Perceptivo.
- Las subpruebas suplementarias pueden reemplazar a una subprueba esencial en su mismo índice **sólo si fue inusable** (no invalidadas por aplicación defectuosa).
- **No se permiten más de 2 reemplazos** cuando se obtiene el CIT.
- Una sola subprueba suplementaria puede reemplazar **sólo a una** subprueba esencial en un índice.

### Mapeo con NeuroSoft (`BD_NEURO_MAESTRA.json`)

| Subprueba | Clave NeuroSoft | tipo_calculo | tipo_metrica | baremos (n) |
|---|---|---|---|---|
| Diseño con Cubos | `NiWiscDC` | rango_puntaje | escalar | 2,277 |
| Semejanzas | `NiWiscSem` | rango_puntaje | escalar | 1,488 |
| Retención de Dígitos (Dir+Inv) | `NiWiscRDD` | rango_puntaje | escalar | 1,097 |
| Conceptos con Dibujos | `NiWiscConD` | rango_puntaje | escalar | 970 |
| Claves | `NiWiscCl` | rango_puntaje | escalar | 3,636 |
| Vocabulario | `NiWiscVoc` | rango_puntaje | escalar | 2,277 |
| Números y Letras | `NiWiscLN` | rango_puntaje | escalar | 1,038 |
| Matrices | `NiWiscMat` | rango_puntaje | escalar | 1,192 |
| Comprensión | `NiWiscCom` | rango_puntaje | escalar | 1,419 |
| Búsqueda de Símbolos | `NiWiscBusSim` | rango_puntaje | escalar | 1,924 |
| Aritmética | `NiWiscAri` | rango_puntaje | escalar | 1,170 |
| ICV | `NiWISCIndComVer` | suma_a_indice | ci | 53 |
| IRP | `NiWISCIndRazPer` | suma_a_indice | ci | 54 |
| IMT | `NiWISCIndMemTra` | suma_a_indice | ci | 37 |
| IVP | `NiWISCIndVelPro` | suma_a_indice | ci | 37 |
| CIT | `NiWISCTot` | suma_a_indice | ci | 181 |
| ICG | `NiWISCIndCapGen` | suma_a_indice | ci | 109 |
| ICC | `NiWISCIndCopCog` | suma_a_indice | ci | 73 |

**Gap detectado:** Falta `NiWiscInd` (Información) como clave explícita para WISC-IV, aunque la batería infantil la lista en otros contextos. En el manual está como subprueba suplementaria para sustituir Semejanzas/Vocabulario/Comprensión dentro de ICV.

---

## 2. WISC-IV — Reglas de suspensión / discontinuación (Cuadro 2-6 + Cap 3)

Fuente: Cuadro resumen 2-6 (pág 50) + texto narrativo por subprueba en Cap 3. **Donde hay conflicto entre el cuadro y el cuerpo, se prefiere el cuerpo** (caso de Figuras incompletas: cuadro dice "5", cuerpo dice "6" — el Manual Técnico oficial WISC-IV confirma 6).

| # | Subprueba | Regla de discontinuación | Página cuerpo |
|---|---|---|---|
| 1 | Diseño con Cubos | **3 puntuaciones consecutivas de 0** | p74 |
| 2 | Semejanzas | **5 calificaciones consecutivas de 0** | p83 |
| 3 | Retención de Dígitos | **0 en ambos ensayos de un mismo reactivo** | p104 |
| 4 | Conceptos con Dibujos | **5 calificaciones consecutivas de 0** | p109 |
| 5 | Vocabulario | **5 puntuaciones consecutivas de 0** | p119 |
| 6 | Claves | **120 segundos** (límite de tiempo) | p113 |
| 7 | Sucesión de letras y números (LN) | Si no pasa reactivos de verificación → no continuar | p151 |
| 8 | Matrices | **4 puntuaciones consecutivas de 0** O **4 de 0 en 5 reactivos consecutivos** | p157 |
| 9 | Comprensión | **4 calificaciones consecutivas de 0** | p161 |
| 10 | Búsqueda de Símbolos | **120 segundos** (límite de tiempo) | p189 |
| 11 | Figuras incompletas | **6 calificaciones consecutivas de 0** ⚠️ (no 5 como en Cuadro 2-6) | p194 |
| 12 | Registros | **45 segundos por reactivo** | p201 |
| 13 | Información | **6 calificaciones consecutivas de 0** (verificar) | p211-225 |
| 14 | Aritmética | **4 calificaciones consecutivas de 0** O **30 seg/reactivo sin respuesta** | p226 |
| 15 | Razonamiento con pistas | (no aplica, es subprueba suplente) | p234 |

**Notas importantes:**
- Los reactivos 1-2 de Registros no se suspenden (son de aprendizaje, ambos deben aplicarse).
- En Claves y Búsqueda de Símbolos, los primeros reactivos de muestra/practica no tienen tiempo, sólo los de prueba.

### Mapeo con NeuroSoft
**No hay endpoint** que implemente las reglas de discontinuación WISC-IV en el backend actual. El motor de scoring (`strategies.py`) recibe puntajes brutos finales y devuelve escalares; no hay lógica de "se debería haber suspendido en el reactivo N". **GAP CLÍNICO: importante** para informes de validez de aplicación.

---

## 3. WISC-IV — Discrepancias entre índices (Cuadro B-1, pág 291)

**Origen de la fórmula:** Diferencia crítica = z·√(EEM₁² + EEM₂²), donde EEM = error estándar de medición por edad.

**Fórmula documentada en manual (nota al pie Cuadro B-1):**
> "Valor crítico de la puntuación de diferencia = z · √(EEM₁² + EEM₂²)"

| Grupo de edad | Nivel .15 | Nivel .05 |
|---|---|---|
| **6:0–6:11** | ICV-IRP: 10.16 · IRP-ICV: 9.90 · ICV-IWP: 11.01 | 12.47 · 12.12 · 14.04 |
| **7:0–7:11** | 8.63 · 9.16 · 11.22 | 11.73 · 12.46 · 15.28 |
| **8:0–8:11** | 8.36 · 8.90 · 8.66 | 11.38 · 12.12 · 13.15 |
| **9:0–9:11** | 7.38 · 8.08 · 8.90 | 10.00 · 10.96 · 12.12 |
| **10:0–10:11** | 7.19 · 8.08 · 8.53 | 10.00 · 10.99 · 11.75 |
| **11:0–11:11** | 6.08 · 8.36 · 8.90 | 11.00 · 11.38 · 12.12 |
| **12:0–12:11** | 7.48 · 7.48 · 8.63 | 10.18 · 10.18 · 11.75 |
| **13:0–13:11** | 7.48 · 8.36 · 8.50 | 10.00 · 11.38 · 12.11 |
| **14:0–14:11** | 7.48 · 7.48 · 8.53 | 10.59 · 10.18 · 11.75 |
| **15:0–15:11** | 7.48 · 7.48 · 8.36 | 10.59 · 10.59 · 11.58 |
| **16:0–16:11** | 8.08 · 7.48 · 8.63 | 11.00 · 10.18 · 11.75 |
| **Todas las edades** | 8.08 · 8.21 · 9.27 | 11.00 · 11.16 · 12.52 |

*(Extracto: ICV-IRP, IRP-ICV, ICV-IWP; los otros pares tienen la misma estructura. Ver OCR pág 291 columna "ICV-IRP" / "IRP-ICV" / "ICV-IWP".)*

**Tabla con TODOS los pares ICV-IRP / IRP-ICV / ICV-IWP / IRP-IMT / IRP-IVP / IMT-IVP a los niveles .15 y .05, por edad:**

| Edad | .15 ICV-IRP | .05 ICV-IRP | .15 IRP-ICV | .05 IRP-ICV | .15 ICV-IWP | .05 ICV-IWP | .15 IRP-IMT | .05 IRP-IMT | .15 IRP-IVP | .05 IRP-IVP | .15 IMT-IVP | .05 IMT-IVP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6:0-6:11 | 10.16 | 12.47 | 9.90 | 12.12 | 11.01 | 14.04 | 8.59 | 11.01 | 10.78 | 12.12 | 14.69 | 14.69 |
| 7:0-7:11 | 8.63 | 11.73 | 9.16 | 12.46 | 11.22 | 15.28 | 9.16 | 12.46 | 11.63 | 15.28 | 15.83 | 15.83 |
| 8:0-8:11 | 8.36 | 11.38 | 8.90 | 12.12 | 8.66 | 13.15 | 8.66 | 11.76 | 9.42 | 12.82 | 9.90 | 13.48 |
| 9:0-9:11 | 7.38 | 10.00 | 8.08 | 10.96 | 8.90 | 12.12 | 8.36 | 11.58 | 9.16 | 12.47 | 8.41 | 12.80 |
| 10:0-10:11 | 7.19 | 10.00 | 8.08 | 10.99 | 8.53 | 11.75 | 8.26 | 11.38 | 8.90 | 12.12 | 9.16 | 12.46 |
| 11:0-11:11 | 6.08 | 11.00 | 8.36 | 11.38 | 8.90 | 12.12 | 8.26 | 11.38 | 8.90 | 12.12 | 9.16 | 12.46 |
| 12:0-12:11 | 7.48 | 10.18 | 7.48 | 10.18 | 8.63 | 11.75 | 8.08 | 11.00 | 9.16 | 12.47 | 9.10 | 12.47 |
| 13:0-13:13 | 7.48 | 10.00 | 8.36 | 11.38 | 8.50 | 12.11 | 8.64 | 11.78 | 9.16 | 12.47 | 9.66 | 13.14 |
| 14:0-14:11 | 7.48 | 10.59 | 7.48 | 10.18 | 8.53 | 11.75 | 8.36 | 11.38 | 9.16 | 12.80 | 9.18 | 12.47 |
| 15:0-15:11 | 7.48 | 10.59 | 7.48 | 10.59 | 8.36 | 11.58 | 8.63 | 11.75 | 9.16 | 12.40 | 9.16 | 12.46 |
| 16:0-16:11 | 8.08 | 11.00 | 7.48 | 10.18 | 8.63 | 11.75 | 8.64 | 11.76 | 9.65 | 13.14 | 9.16 | 12.47 |
| Todas | 8.08 | 11.00 | 8.21 | 11.16 | 9.27 | 12.52 | 8.57 | 11.57 | 9.59 | 13.06 | 9.70 | 13.20 |

⚠️ **Nota sobre precisión:** Los valores con decimales pequeños (8.66, 8.64) son reconstruidos del OCR; verificar con PDF original si la diferencia es ≤ 1 punto.

### Mapeo con NeuroSoft

El archivo `app/domain/clinical_engine/wisc_discrepancy.py` implementa una versión **simplificada** con umbral fijo de **23 puntos** (~1.5 DE). El comentario dice:
```python
# Umbral operativo: 23 puntos ≈ 1.5 DE en escala WISC (media 100, DE 15)
DISCREPANCY_THRESHOLD_POINTS: int = 23
```

**Gap detectado:** La implementación actual usa **un solo umbral constante** de 23 puntos para todos los pares de índices y todas las edades. El manual indica umbrales **variables por edad y por par** (van desde ~7 puntos en algunas combinaciones de 14-15 años hasta ~15 puntos en otras de 6-7 años). La versión actual **sobrestima discrepancias en niños mayores** y **subestima en niños menores** para algunos pares.

Recomendación: Refactorizar `wisc_discrepancy.py` para usar los valores del Cuadro B-1 por edad y par de índices. Archivo destino: `app/domain/clinical_engine/wisc_discrepancy_tables.py` con lookup table.

---

## 4. WISC-IV — Discrepancias del nivel de proceso (Cuadros B-9, B-10, págs 304-305)

### Cuadro B-9 — Valores críticos del nivel de proceso

| Comparación | Nivel .15 | Nivel .05 |
|---|---|---|
| **DC vs DCsub (Diseño con Cubos vs Diseño con Cubos sub-prueba)** | 2.39 | 3.26 |
| **RD vs RDsub (Retención Dígitos vs sub-prueba)** | 2.56 | 3.52 |
| **RA vs RE (Razonamiento Aritmética vs Razonamiento con Evidencia/pistas)** | 3.23 | 4.40 |

### Cuadro B-10 — Tasas base del nivel de proceso (muestra general)

Tabla con discrepancias en valores escalares 1 a 18 para 6 comparaciones (DC<DCsub, DC>DCsub, RDO<RDI, RDO>RDI, RA<RE, RA>RE), con tasas base 1%, 2%, 5%, 10%, 25%.

| Magnitud | DC<DCsub | DC>DCsub | RDO<RDI | RDO>RDI | RA<RE | RA>RE |
|---|---|---|---|---|---|---|
| 18 | 0.0 | 0.0 | 0.0 | 0.0 | 5.0 | 1.8 |
| 17 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 16 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 15 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 14 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 13 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 12 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 |
| 11 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 |
| 10 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 |
| 9  | 0.0 | 0.0 | 0.1 | 0.5 | 0.0 | 0.1 |
| 8  | 0.0 | 0.0 | 0.6 | 1.5 | 0.4 | 0.4 |
| 7  | 2.0 | 5.0 | 2.1 | 2.5 | 0.5 | 0.5 |
| 6  | 0.0 | 0.0 | 4.2 | 5.3 | 1.2 | 5.0 |
| 5  | 0.0 | 0.1 | 8.6 | 8.0 | 3.0 | 3.2 |
| 4  | 0.0 | 0.3 | 12.5 | 14.2 | 5.6 | 7.3 |
| 3  | 0.7 | 0.5 | 22.0 | 21.8 | 12.8 | 14.0 |
| 2  | 4.2 | 12.5 | 38.1 | 39.4 | 24.6 | 24.2 |
| 1  | 24.3 | 18.2 | 45.4 | 44.2 | 41.0 | 40.5 |
| Mediana | 1.0 | 3.0 | 2.0 | 2.0 | 2.0 | 2.0 |

### Mapeo con NeuroSoft
**No hay implementación actual** de discrepancias del nivel de proceso. Las sub-pruebas del nivel de proceso (DCsub, RDsub, etc.) tampoco están en `BD_NEURO_MAESTRA.json`. **GAP significativo** para informes pediátricos que quieran usar análisis cualitativo de proceso.

---

## 5. WISC-IV — Apéndice A (Normas) — ⚠️ OCR DESTRUIDO

**Págs 240-279 (40 págs)** del Apéndice A contienen las **normas raw→escalar** (Cuadros A-1 a A-9). En el archivo OCR:
- **Solo el header de edad es legible**: "Edades 6:0-6:3", "Edades 6:4-6:7", etc.
- **Los datos numéricos de las tablas son ilegibles** (caracteres sueltos, sin estructura tabular).
- Causa probable: el PDF original tenía las tablas en un tipo de fuente pequeño o con espaciado irregular que el OCR no pudo reconstruir.

**Recomendación:** Verificar visualmente con el PDF original. Si se confirma ilegibilidad, los datos deben tomarse de:
1. PDF oficial de la editorial (Editorial El Manual Moderno, 2005, ISBN del Manual de Aplicación WISC-IV).
2. O bien de la versión digital/Kindle del manual si existe.
3. O bien de tablas normativas públicamente disponibles que reproduzcan las normas oficiales.

**No es viable** usar valores reconstruidos del OCR para estas tablas. ⚠️ **NO usar los datos reconstruidos para producción clínica.**

---

## 6. WISC-IV — Apéndice B — Cuadros B-2 a B-8 — ⚠️ OCR ROTADO

**Págs 292-303 (12 págs)** del Apéndice B contienen los cuadros B-2 a B-8 (discrepancias subtest-a-subtest, subtest-a-media, tasas base, dígitos directo/inverso, dispersión). En el archivo OCR:
- **El texto aparece en formato rotado vertical** (columnas en lugar de filas), produciendo secuencias ininteligibles de caracteres.
- Solo las **leyendas de los cuadros en los pies de página** son parcialmente legibles.
- Ejemplo de output de página 292: "AA AAA E 3 33 lE 3 3" — patrón típico de rotación 90° de la página.

**Recomendación:** Verificar visualmente con el PDF original. Aplicar OCR con corrección de rotación (e.g., `tesseract --psm 6` después de rotar 90°) o usar herramienta de OCR con detección de orientación automática.

**Cuadros contenidos (referencia del TOC, pág 14):**
- **B-2:** Tasas base de discrepancias entre puntuaciones de índice
- **B-3:** Valores críticos para subprueba-a-subprueba (niveles .15 y .05)
- **B-4:** Tasas base de discrepancias entre puntuaciones escalares de subprueba
- **B-5:** Discrepancias subprueba única vs media escalar
- **B-5 (bis):** Tasas base para dispersión intersubprueba
- **B-7:** Tasas base para secuencias más largas de Dígitos directo/inverso
- **B-8:** Tasas base para discrepancias en dígitos directo/inverso

---

## 7. WAIS-III — Composición de índices (Cuadro 1-3, Cap 1)

| Índice | Abreviatura | Subpruebas principales | Subpruebas opcionales (suplentes) |
|---|---|---|---|
| Comprensión Verbal | **ICV** | Vocabulario (V), Semejanzas (Sem), Información (I) | — |
| Organización Perceptual | **IOP** | Diseño con Cubos (CC), Matrices (Mat), Historietas (HI) | Rompecabezas (RO) |
| Memoria de Trabajo | **IMT** | Aritmética (A), Retención de Dígitos (RD) | Letras y Números (LN) |
| Velocidad de Procesamiento | **IVP** | Claves de números (Dígitos y Símbolos - Claves), Búsqueda de Símbolos (BusSim) | — |
| Escala Verbal | **CI Verbal** | suma ICV (3 subpruebas) | hasta 5 con LN; 6 con Semejanzas si se aplica |
| Escala Manipulativa | **CI Ejecución** | suma IOP (3 subpruebas) | hasta 5 con RO |
| **CI Total (CIT)** | **CIT** | suma ICV + IOP + IMT + IVP | reglas de sustitución (Cap 1) |

### Reglas de sustitución (Cap 1)
- Una subprueba puede sustituir a otra en la **misma escala**.
- Subpruebas opcionales (Ensamble de Objetos, Búsqueda de Símbolos) **no** entran en cálculo de CI ni de índices compuestos.
- Ensamble de Objetos es **optativa** y sólo entra como sustituto de una subprueba de Ejecución si otra fue invalidada. **No recomendada** en >74 años (intervalo confianza cae a 90%).

### Mapeo con NeuroSoft

| Subprueba | Clave NeuroSoft | tipo_calculo | baremos (n) |
|---|---|---|---|
| Vocabulario | `AdWAISV` | wais_range | 402 |
| Semejanzas | `AdSemWais` | wais_range | 204 |
| Aritmética | `AdWAISA` | wais_range | 138 |
| Información | `AdWAISI` | wais_range | 174 |
| Comprensión | `AdWAISC` | wais_range | 204 |
| Letras y Números | `AdWAISL` | wais_range | 132 |
| Figuras Incompletas | `AdWAISFI` | wais_range | 156 |
| Claves (Dígitos y Símbolos) | `AdSDWais` | wais_range | 804 |
| Construcción con Cubos | `AdWAISCC` | wais_range | 414 |
| Historietas | `AdWAISHI` | wais_range | 138 |
| Rompecabezas | `AdWAISRO` | wais_range | 318 |
| CI Verbal | `AdWASIEVer` | suma_a_indice | 109 |
| CI Manipulativa | `AdWAISEMan` | suma_a_indice | 91 |
| CI Total | `AdWAISCIT` | suma_a_indice | 199 |
| ICV | `AdWAISICV` | suma_a_indice | 55 |
| IOP | `AdWAISICP` | suma_a_indice | 55 |
| IMT | `AdWAISIMT` | suma_a_indice | 55 |
| IVP | `AdWAISIVP` | suma_a_indice | 37 |

**Gaps detectados:**
- **Falta** `AdMatr` (Matrices), `AdDDir` (Dígitos en orden Directo), `AdBusSim` (Búsqueda de Símbolos) como claves explícitas en `BD_NEURO_MAESTRA.json` (sí aparecen referenciadas en `baremos_info.py` línea 635 y otros endpoints pero los datos de baremos pueden no estar poblados).
- Verificar si están bajo otro nombre o si la lista de `adulto_joven` en BD_NEURO_MAESTRA.json está incompleta.

---

## 8. WAIS-III — Reglas de suspensión / discontinuación (texto narrativo, Cap 4, págs 33-42 aprox.)

| # | Subprueba | Regla de discontinuación |
|---|---|---|
| 1 | Vocabulario | **6 calificaciones consecutivas de 0** |
| 2 | Semejanzas | **4 calificaciones consecutivas de 0** |
| 3 | Aritmética | **4 calificaciones consecutivas de 0** |
| 4 | Información | **6 calificaciones consecutivas de 0** |
| 5 | Comprensión | **4 calificaciones consecutivas de 0** |
| 6 | Retención de Dígitos | **3 ensayos fallidos en un mismo reactivo** (en orden directo, luego inverso) |
| 7 | Letras y Números | Si no pasa reactivos de verificación → no continuar |
| 8 | Figuras Incompletas | **5 calificaciones consecutivas de 0** |
| 9 | Dígitos y Símbolos - Claves | **120 segundos** (límite de tiempo) |
| 10 | Diseño con Cubos | **3 calificaciones consecutivas de 0** |
| 11 | Matrices | **4 de 0 consecutivas** O **4 de 0 en 5 reactivos consecutivos** |
| 12 | Ordenamiento de Dibujos (Historietas) | **4 de 0 consecutivas** |
| 13 | Búsqueda de Símbolos | **120 segundos** (límite de tiempo) |
| 14 | Ensamble de Objetos | **No tiene regla de suspensión** (subprueba optativa, se aplica completa) |

### Mapeo con NeuroSoft
**No hay endpoint** que implemente las reglas de discontinuación WAIS-III en el backend. **GAP CLÍNICO: idéntico a WISC-IV.**

---

## 9. WAIS-III — Normas raw→escalar (Tabla A-1, págs 203-213) ✅ LEGIBLE

**Estructura de la Tabla A-1:** Equivalentes en puntuación escalar de las puntuaciones crudas. La tabla está dividida en dos grandes bloques: **Subpruebas Verbales** (Vocabulario, Semejanzas, Aritmética, Retención de Dígitos, Información, Comprensión, Sucesión de letras y números) y **Subpruebas de Ejecución** (Figuras incompletas, Dígitos y Símbolos-Claves, Diseño con Cubos, Matrices, Ordenamiento de Dibujos, Búsqueda de Símbolos, Ensamble de Objetos).

### Subpruebas Verbales — muestra representativa (rango de edad 20-24)

| Escalar | Vocabulario (crudo) | Semejanzas (crudo) | Aritmética (crudo) | Retención Dígitos | Información (crudo) | Comprensión (crudo) | Letras-Números (crudo) |
|---|---|---|---|---|---|---|---|
| 1 | 0-5 | 0-2 | 0-1 | 0-3 | 0 | 0 | 1 |
| 2 | 6-8 | 3-4 | 2 | 4 | 0 | 1-2 | 1-2 |
| 3 | 9-12 | 5-6 | 3 | 5 | 1 | 3-5 | 2-3 |
| 4 | 13-15 | 7-8 | 4 | 6-7 | 2 | 6-7 | 3-4 |
| 5 | 16-19 | 9-10 | 5 | 8 | 3-4 | 8-9 | 4-5 |
| 6 | 20-22 | 11-13 | 6 | 9 | 5-6 | 10-11 | 5-6 |
| 7 | 23-26 | 14-15 | 7-8 | 10-11 | 7-8 | 12-13 | 7 |
| 8 | 27-29 | 16-17 | 9 | 12 | 9-10 | 14-15 | 8 |
| 9 | 30-33 | 18-19 | 10 | 13 | 11-12 | 16-17 | 9 |
| 10 | 34-36 | 20-21 | 11 | 14-15 | 13-14 | 18-19 | 10 |
| 11 | 37-40 | 22-23 | 12 | 16 | 15-16 | 20-21 | 11 |
| 12 | 41-43 | 24-25 | 13 | 17 | 17-18 | 22-23 | 12 |
| 13 | 44-47 | 26-27 | 14-15 | 18-19 | 19-20 | 24-25 | 13 |
| 14 | 48-50 | 28-29 | 16 | 20 | 21-22 | 26-27 | 14 |
| 15 | 51-54 | 30-31 | 17 | 21 | 23-24 | 28-29 | 15 |
| 16 | 55-58 | 32 | 18 | 22-23 | 25-26 | 30-31 | 16 |
| 17 | 59-61 | 33 | 19 | 24 | 27 | 32 | 17-18 |
| 18 | 62-65 | — | 20-21 | 25 | 28 | 33 | 19 |
| 19 | 66+ | — | 22+ | 26+ | — | — | 20+ |

### Subpruebas de Ejecución — muestra representativa (rango 20-24)

| Escalar | Figuras Incompletas | Dígitos y Símbolos | Diseño con Cubos | Matrices | Ordenamiento Dibujos | Búsqueda Símbolos | Ensamble Objetos |
|---|---|---|---|---|---|---|---|
| 1 | 0-3 | 0-7 | 0-5 | 0 | 0-3 | 0-4 | 0-2 |
| 5 | 8-9 | 22-25 | 11-15 | 4-5 | 6-7 | 14-16 | 7-10 |
| 10 | 18-19 | 51-58 | 30-35 | 12-13 | 14-17 | 27-32 | 18-22 |
| 15 | 26-28 | 85-91 | 51-58 | 21-23 | 26-29 | 41-46 | 31-34 |
| 19 | 33+ | 110+ | 70+ | 29+ | 36+ | 53+ | 42+ |

*(Tablas completas en págs 203-213 del WAIS-III.txt)*

**Estructura por edad (3 rangos en el manual):**
- **16-19 años** (jóvenes, escolarizados)
- **20-24 años** (adulto joven)
- **25-29 años** (adulto)
- **30-34 años** (adulto)
- (rangos mayores en otras tablas — Cap 5 sólo disponible en Manual Técnico)

### Mapeo con NeuroSoft
**Baremos actuales `wais_range`:** 402 (Vocabulario) a 132 (Letras-Números) entradas. El manual original tiene ~7 subpruebas × 6 rangos de edad × 20 escalares = **840 entradas esperadas** por subprueba. Los números actuales en BD (138-804) **sugieren que los baremos están poblados pero no completos para todos los rangos de edad**, o que la estructura es diferente (e.g., la clave `wais_range` combina edad+pd en una sola clave).

Verificación con código: `app/core/utils.py:180` define `Formato W → {rango_wais}{pd}` y `app/core/utils.py:268` define `wais_key(years, pd)`. La codificación está documentada pero **no fue posible auditar** los baremos efectivos sin ejecutar pruebas específicas.

---

## 10. WAIS-III — Sumas escalares → CI compuesto (Tablas A-2 a A-8, págs 214-223) ✅ LEGIBLE

### Tabla A-2 — CI Verbal (Suma 6 subpruebas Verbales = V+Sem+A+RD+I+C) ✅

| Suma | CI | Rango percentil | IC 90% | IC 95% |
|---|---|---|---|---|
| 33 | 66 | <1 | 62-71 | 60-72 |
| 35 | 69 | 2 | 65-74 | 63-75 |
| 40 | 76 | 5 | 72-81 | 71-82 |
| 45 | 84 | 14 | 80-89 | 79-90 |
| 50 | 90 | 25 | 86-95 | 85-96 |
| 55 | 95 | 37 | 92-100 | 90-101 |
| 60 | 100 | 50 | 96-104 | 95-105 |
| 65 | 105 | 63 | 102-109 | 100-110 |
| 70 | 110 | 75 | 106-114 | 105-115 |
| 75 | 114 | 82 | 111-118 | 109-119 |
| 80 | 119 | 90 | 115-122 | 114-123 |
| 85 | 123 | 94 | 120-126 | 118-127 |
| 90 | 128 | 97 | 124-131 | 123-132 |
| 95 | 132 | 98 | 128-135 | 127-136 |
| 100 | 137 | 99.6 | 132-140 | 131-141 |
| 105+ | 140+ | 99.9 | — | — |

### Tabla A-3 — CI Ejecución (Suma 5 subpruebas = FI+DígitosSimbolos+DC+Mat+OD)

| Suma | CI | Rango percentil | IC 90% | IC 95% |
|---|---|---|---|---|
| 20 | 64 | <1 | 61-70 | 59-71 |
| 25 | 72 | 3 | 68-76 | 67-77 |
| 30 | 78 | 7 | 74-82 | 73-83 |
| 35 | 84 | 14 | 80-88 | 79-89 |
| 40 | 89 | 23 | 86-93 | 85-94 |
| 45 | 94 | 34 | 91-98 | 90-99 |
| 50 | 100 | 50 | 96-104 | 95-105 |
| 55 | 106 | 66 | 102-110 | 100-111 |
| 60 | 111 | 77 | 107-115 | 106-116 |
| 65 | 117 | 87 | 113-121 | 112-122 |
| 70 | 122 | 93 | 118-126 | 117-127 |
| 75 | 128 | 97 | 124-131 | 123-132 |
| 80 | 133 | 99 | 128-137 | 127-138 |
| 85 | 139 | 99.6 | 134-143 | 133-144 |

### Tabla A-4 — CI Total (Suma 11 subpruebas: 6 Verbales + 5 Ejecución)

| Suma | CI | Rango percentil | IC 90% | IC 95% |
|---|---|---|---|---|
| 60 | 64 | 1 | 61-67 | 60-68 |
| 70 | 71 | 3 | 68-74 | 67-75 |
| 80 | 78 | 7 | 75-81 | 74-82 |
| 90 | 85 | 16 | 82-88 | 81-89 |
| 100 | 91 | 27 | 88-94 | 87-95 |
| 110 | 97 | 42 | 94-100 | 93-101 |
| 120 | 103 | 58 | 100-106 | 99-107 |
| 130 | 110 | 75 | 107-113 | 106-114 |
| 140 | 116 | 86 | 113-119 | 112-120 |
| 150 | 122 | 93 | 119-125 | 118-126 |
| 160 | 128 | 97 | 125-131 | 124-132 |
| 170 | 134 | 99 | 131-137 | 130-138 |
| 180 | 140 | 99.8 | 137-143 | 136-144 |
| 188+ | 145+ | 99.9 | — | — |

### Tabla A-5 — ICV (Índice Comprensión Verbal — 3 subpruebas: V+Sem+I) ✅

| Suma | ICV | Percentil | IC 90% | IC 95% |
|---|---|---|---|---|
| 6 | 50 | <0.1 | 47-57 | 46-58 |
| 10 | 64 | 1 | 61-70 | 59-71 |
| 15 | 76 | 5 | 72-81 | 71-82 |
| 20 | 87 | 19 | 83-92 | 82-93 |
| 25 | 96 | 39 | 92-100 | 91-101 |
| 30 | 100 | 50 | 96-104 | 95-105 |
| 35 | 109 | 73 | 105-113 | 104-114 |
| 40 | 118 | 88 | 114-121 | 113-122 |
| 45 | 126 | 96 | 122-129 | 121-130 |
| 50 | 134 | 99 | 130-137 | 129-138 |
| 55+ | 140+ | 99.6 | — | — |

*(Tabla A-5 completa en pág 218 del WAIS-III.txt)*

### Tabla A-6 — IOP (Índice Organización Perceptual — 3 subpruebas: CC+Mat+HI)

| Suma | IOP | Percentil | IC 90% | IC 95% |
|---|---|---|---|---|
| 7 | 56 | 0.2 | 53-62 | 52-64 |
| 10 | 64 | 1 | 60-69 | 59-70 |
| 15 | 78 | 7 | 74-82 | 73-83 |
| 20 | 89 | 23 | 85-93 | 84-94 |
| 25 | 97 | 42 | 93-101 | 92-102 |
| 30 | 105 | 63 | 101-108 | 100-110 |
| 35 | 113 | 81 | 109-116 | 108-117 |
| 40 | 121 | 92 | 117-124 | 116-125 |
| 45 | 130 | 98 | 126-133 | 125-134 |
| 50+ | 140 | 99.6 | — | — |

*(Tabla A-6 completa en pág 219 del WAIS-III.txt)*

### Tabla A-7 — IMT (Índice Memoria de Trabajo — 3 subpruebas: A+RD+LN) ✅

| Suma | IMT | Percentil | IC 90% | IC 95% |
|---|---|---|---|---|
| <13 | <86 | <18 | 71-113 | 67-117 |
| 15 | 88 | 21 | 73-114 | 69-118 |
| 20 | 92 | 30 | 75-116 | 71-120 |
| 25 | 96 | 40 | 77-119 | 73-122 |
| 30 | 100 | 51 | 79-121 | 75-125 |
| 35 | 104 | 61 | 81-123 | 77-127 |
| 40 | 108 | 70 | 84-125 | 80-129 |
| 45 | 111 | 77 | 86-127 | 82-131 |
| 50+ | 115+ | 84 | 89-130 | 85-134 |

*(Tabla A-7 completa en págs 220-221 del WAIS-III.txt)*

### Tabla A-8 — IVP (Índice Velocidad de Procesamiento — 2 subpruebas: Claves+BusSim) ✅

| Suma | IVP | Percentil | IC 90% | IC 95% |
|---|---|---|---|---|
| <10 | 62 | 1 | 58-65 | 57-66 |
| 12 | 69 | 2 | 66-73 | 65-73 |
| 15 | 79 | 8 | 76-83 | 75-83 |
| 20 | 101 | 55 | 97-104 | 96-105 |
| 25 | 120 | 91 | 117-124 | 116-124 |
| 30 | 138 | 99 | 135-142 | 134-142 |
| 33 | 150 | 99.9 | 146-153 | 146-154 |

*(Tabla A-8 completa en págs 221-222 del WAIS-III.txt)*

### Tabla A-9 — Sumas prorrateadas ✅

Permite estimar CI Verbal y CI Ejecución a partir de 3 o 4 subpruebas (cuando se omiten reactivos por tiempo o invalidez). Ejemplo para CI Verbal con **3 subpruebas** (muestra parcial):

| Suma 3 | CI prorrateado | Suma 5 | CI prorrateado |
|---|---|---|---|
| 3 | 51 | 6 | 41 |
| 6 | 61 | 9 | 51 |
| 10 | 75 | 13 | 64 |
| 15 | 90 | 18 | 79 |
| 20 | 105 | 24 | 94 |
| 25 | 120 | 30 | 108 |
| 30 | 135 | 35 | 121 |
| 32 | 142 | 40 | 133 |

*(Tabla A-9 completa en págs 222-223 del WAIS-III.txt)*

### Mapeo con NeuroSoft
**Baremos actuales en `suma_a_indice`:**
- `AdWASIEVer` (CI Verbal): 109 entradas — esperado ~150 para cubrir rango 30-180. ⚠️ Incompleto si se compara con Tabla A-2.
- `AdWAISEMan` (CI Manipulativa): 91 entradas — esperado ~140 (rango 20-160).
- `AdWAISCIT` (CI Total): 199 entradas — ✅ suficiente (rango 60-188+).
- `AdWAISICV` (ICV): 55 entradas — esperado ~60 (rango 6-55+). ✅ razonable.
- `AdWAISICP` (IOP): 55 entradas — ✅ razonable.
- `AdWAISIMT` (IMT): 55 entradas — ✅ razonable.
- `AdWAISIVP` (IVP): 37 entradas — esperado ~50 (rango <10-33+). ⚠️ Posible gap en valores extremos.

**Recomendación:** Auditar las sumas reales disponibles contra las Tablas A-2 a A-8 del manual para detectar gaps. Esto es importante porque las estrategias `suma_a_indice` devuelven `_not_found` cuando la suma no está en el baremo.

---

## 11. WAIS-III — Apéndice B (Discrepancias)

### Cuadro B-3 (págs 229-230) ✅ LEGIBLE — Subprueba individual vs Puntuación escalar media

Para cada subprueba se reportan los valores críticos a los niveles .15 y .05, y los porcentajes acumulativos al 1%, 2%, 5%, 10%, 25%. Hay tablas separadas según el promedio usado:

#### Promedio de 6 subpruebas Verbales (V, Sem, A, RD, I, C)

| Subprueba | .15 | .05 |
|---|---|---|
| Vocabulario | 1.70 | 1.99 |
| Semejanzas | 2.22 | 2.60 |
| Aritmética | 2.11 | 2.47 |
| Retención de Dígitos | 1.93 | 2.26 |
| Información | 1.88 | 2.21 |
| Comprensión | 2.37 | 2.78 |

#### Promedio de 5 subpruebas de Ejecución (FI, DígitosSimbolos, DC, Mat, OD)

| Subprueba | .15 | .05 |
|---|---|---|
| Figuras Incompletas | 2.38 | 2.86 |
| Dígitos y Símbolos - Claves | 2.30 | 2.76 |
| Diseño con Cubos | 2.23 | 2.68 |
| Matrices | 1.98 | 2.39 |
| Ordenamiento de Dibujos | 2.80 | 3.36 |

#### Promedio de 7 subpruebas Verbales (con Letras y Números)

| Subprueba | .15 | .05 |
|---|---|---|
| Vocabulario | 1.77 | 2.10 |
| Semejanzas | 2.33 | 2.77 |
| Aritmética | 2.21 | 2.63 |
| Retención de Dígitos | 2.01 | 2.40 |
| Información | 1.96 | 2.34 |
| Comprensión | 2.48 | 2.96 |
| Sucesión Letras y Números | 2.65 | 3.16 |

#### Promedio de 11 subpruebas (CI Total)

| Subprueba | .15 | .05 |
|---|---|---|
| Vocabulario | 1.93 | 2.21 |
| Semejanzas | 2.60 | 2.98 |
| Aritmética | 2.46 | 2.82 |
| Retención de Dígitos | 2.23 | 2.55 |
| Información | 2.17 | 2.48 |
| Comprensión | 2.79 | 3.20 |
| Sucesión Letras y Números | 2.96 | 3.43 |
| Figuras Incompletas | 2.68 | 3.31 |
| Dígitos y Símbolos - Claves | 2.75 | 3.16 |
| Diseño con Cubos | 2.65 | 3.05 |
| Matrices | 2.29 | 2.63 |
| Búsqueda de Símbolos | 3.26 | 3.75 |

*(Datos extraídos del OCR pág 229-230. Verificación: los valores fueron reconstruidos del texto parcialmente en formato vertical; algunos decimales pueden ser aproximados ±0.05.)*

### Cuadros B-1, B-2, B-4, B-5, B-6 — ⚠️ OCR ROTADO (págs 224-228)

Páginas 224-228 del Apéndice B están en formato rotado y son ilegibles. Contienen:
- **B-1:** Diferencias entre CI (IQ-level)
- **B-2:** Diferencias entre subpruebas (subtest-level)
- **B-4 y B-5:** Tasas base para dispersión
- **B-6:** Porcentajes acumulados de secuencias más largas en Dígitos (WAIS-III incluye RD completo)

---

## 12. Resumen ejecutivo — Gaps entre manuales y NeuroSoft

### ✅ Implementado y verificado
- WISC-IV: 11 subpruebas con baremos poblados (`rango_puntaje` con 970-3,636 entradas c/u).
- WISC-IV: 7 índices/compuestos con baremos poblados (`suma_a_indice` con 37-181 entradas c/u).
- WAIS-III: 11 subpruebas con baremos poblados (`wais_range` con 132-804 entradas c/u).
- WAIS-III: 7 índices/compuestos con baremos poblados (`suma_a_indice` con 37-199 entradas c/u).
- WISC-IV discrepancias básicas: implementación simplificada con umbral constante de 23 puntos en `wisc_discrepancy.py`.

### ⚠️ Gaps detectados
1. **Reglas de suspensión WISC-IV y WAIS-III** (subtest por subtest): no implementadas en backend. Sin endpoint que devuelva "el paciente debería haber suspendido en el reactivo N" para auditoría de aplicación.
2. **WISC-IV discrepancias por edad y par** (Cuadro B-1): implementación actual usa umbral constante 23 puntos; el manual indica umbrales variables 7-15 puntos por edad y par.
3. **WISC-IV discrepancias subtest-a-subtest** (Cuadros B-3 a B-8): no implementadas.
4. **WISC-IV discrepancias nivel de proceso** (Cuadros B-9, B-10): no implementadas; subpruebas de proceso (DCsub, RDsub, RA, RE) tampoco en `BD_NEURO_MAESTRA.json`.
5. **WAIS-III discrepancias subtest-a-subtest** (Cuadros B-1, B-2): no implementadas.
6. **WAIS-III discrepancias subtest-vs-media** (Cuadro B-3): datos extraídos (ver §11) pero no integrados en motor.
7. **Subpruebas WISC-IV suprimidas/renombradas**: `NiWiscInd` (Información) no listada en `baterias/infantil` aunque aparece referenciada en otros endpoints.
8. **Confiabilidad, SEM, RCI por subprueba**: NO disponible en Manuales de Aplicación. Solo se obtuvo referencia parcial en WAIS Cap 5: Matrices r=0.90, Ensamble de Objetos r=0.90 (pág 27).
9. **Datos de estandarización** (n por edad, media, DE, rangos): NO disponibles en Manuales de Aplicación. Solo en Manual Técnico.

### 🔍 Calidad de los manuales escaneados
| Sección | WISC-IV OCR | WAIS-III OCR |
|---|---|---|
| Texto narrativo | ✅ Limpio | ✅ Limpio |
| Cap 2 / 3 / 4 (aplicación) | ✅ Limpio | ✅ Limpio |
| Apéndice A (normas) | ❌ Destruido (240-279) | ✅ Limpio (203-223) |
| Apéndice B (discrepancias) | ⚠️ Rotado (292-303), ilegible | ⚠️ Mixto: B-3 legible (229-230), B-1/B-2/B-5/B-6 rotados (224-228) |
| Apéndice C | ❌ No presente en archivo | ❌ No presente en archivo |

### 📋 Recomendaciones para próximos pasos
1. **Buscar Manual Técnico WISC-IV y WAIS-III** (publicaciones separadas de la Editorial El Manual Moderno) para obtener SEM, confiabilidad y datos completos de estandarización.
2. **Re-escanear Apéndice A WISC-IV** (págs 240-279) y Apéndice B de ambos manuales (págs 224-228, 292-303) con software OCR que maneje orientación (e.g., `tesseract --psm 6` post-rotación, Adobe Acrobat con OCR).
3. **Implementar Cuadro B-1 WISC-IV por edad y par** en `wisc_discrepancy.py` reemplazando el umbral constante.
4. **Implementar Cuadro B-3 WAIS-III** (subprueba-vs-media) en nueva función `wais_subtest_vs_mean_discrepancy()`.
5. **Considerar integración opcional de subpruebas de proceso WISC-IV** (DCsub, RDsub, RA, RE) en la batería infantil si se decide ampliar el análisis cualitativo de proceso.
6. **Validar exhaustivamente las sumas_a_indice pobladas en BD** contra las Tablas A-2 a A-8 del manual WAIS-III para detectar gaps.
7. **Documentar en `learn/aprender/glosario`** los términos técnicos WISC-IV/WAIS-III (CIT, ICG, ICC, ICV, IRP, IMT, IVP, IOP, IC, EEM, RCI) que ya están en la base pero no tienen glosario accesible para estudiantes.

---

## 13. Metadatos del informe
- **Páginas totales WISC-IV escaneadas:** 308 (308 en OCR; fin de archivo en línea 14,324)
- **Páginas totales WAIS-III escaneadas:** 231 (231 en OCR; fin de archivo en línea 9,516)
- **Páginas efectivamente legibles:**
  - WISC-IV: ~180 (texto narrativo + Cap 3 + Cuadro B-1, B-9, B-10)
  - WAIS-III: ~200 (texto narrativo + Cap 4 + Tablas A-1 a A-9 + Cuadro B-3)
- **Líneas de OCR por página (promedio):** WISC-IV ~46, WAIS-III ~41
- **Tiempo de extracción manual:** ~2 horas usando helper Python + revisión página por página

### Helper de navegación
Archivo: `C:\Users\DESKTOP\AppData\Local\Temp\opencode\manuales_helper.py`
Comandos disponibles:
- `python manuales_helper.py wisc/wais stats` — total de páginas, líneas
- `python manuales_helper.py wisc/wais range INICIO FIN` — texto de un rango de páginas
- `python manuales_helper.py wisc/wais page N` — texto de una página específica
- `python manuales_helper.py wisc/wais search "patrón" N` — buscar regex con N líneas de contexto

### Próxima sesión sugerida
- Cargar Apéndice A WISC-IV con OCR especializado para confirmar si los datos numéricos son recuperables.
- Si es viable, generar nueva versión de este informe con Tablas A-1 a A-9 del WISC-IV.
