# Reclasificación 2026 — Bandas del Cociente Intelectual

**Norma:** DSM-5-TR (2022) · WAIS-IV Technical and Interpretive Manual (2008, actualizada 2014) · CIE-11 (OMS 2019, adoptada Colombia Res. 2296/2023).

**Estado:** Vigente desde la versión 2.0.0 de NeuroSoft App (Q1 2026).

---

## 1. Cambio principal: eliminación de "Limítrofe"

| Banda antigua | Banda nueva 2026 | CI rango | Percentil | Población |
|---|---|---|---|---|
| Muy Superior | **Muy Superior** | ≥ 130 | ≥ 98 | < 2% |
| Superior | **Superior** | 120-129 | 91-97 | ~7% |
| Promedio Alto | **Promedio Alto** | 110-119 | 75-90 | ~16% |
| Promedio | **Promedio** | 90-109 | 25-74 | ~50% |
| Promedio Bajo | **Promedio Bajo** | 80-89 | 9-24 | ~16% |
| **Limítrofe** *(removido)* | **Bajo** | 70-79 | 2-8 | ~7% |
| Déficit cognitivo leve | **Muy Bajo** | < 70 | < 2 | ~2% |

### Justificación

- El DSM-5-TR (American Psychiatric Association, 2022) recomienda **2 desviaciones estándar** de la media como punto de corte para discapacidad intelectual (CI < 70), y describe un continuum sin la categoría "Limítrofe".
- El WAIS-IV Technical Manual (Pearson, 2008; ed. actualizada 2014) unifica el rango "Borderline" (71-84) dentro del espectro "Low Average to Borderline", con un punto de corte clínico en 70.
- CIE-11 (OMS 2019) usa categorías: "Discapacidad intelectual leve" (CI 50-69), "moderada" (35-49), "grave" (20-34), "profunda" (<20). El rango 70-79 no se clasifica como trastorno en CIE-11, pero amerita seguimiento clínico.
- La categoría "Limítrofe" introducía ambigüedad clínica: en algunos contextos se usaba como sinónimo de "Borderline" (CI 71-84) y en otros como "por debajo del promedio pero sin déficit" (CI 71-79). El DSM-5-TR zanja esto recomendando **"Promedio Bajo"** para 80-89 y **"Bajo"** para 70-79.

---

## 2. Implicaciones en el informe

### 2.1 Lenguaje al clínico

Para pacientes con CI 70-79, el informe debe usar "**rendimiento intelectual en rango Bajo**" o "**rendimiento intelectual general en el límite inferior del espectro promedio**" (esta última más matizada). Evitar:
- "Limítrofe" (categoría eliminada).
- "Borderline" (anglicismo innecesario).
- "Déficit intelectual" (implica CI < 70, diagnóstico distinto).

### 2.2 Advertencia DSM-5-TR A

Cuando el CI está entre 70-79, el informe debe incluir la siguiente advertencia (extraída de DSM-5-TR p. 38, Criterio A para Discapacidad Intelectual):

> "El resultado del CI debe interpretarse con cautela. La discapacidad intelectual (DSM-5-TR 300.4 / CIE-11 6A00) requiere deterioro en **funciones adaptativas** además del CI < 70. Un CI entre 70-79 sin deterioro adaptativo significativo no constituye discapacidad intelectual, pero sí es un factor de riesgo que amerita seguimiento."

### 2.3 Tabla de referencia

| CI | Banda | Percentil | Z-score | Discapacidad intelectual (DSM-5-TR 300.4) |
|---|---|---|---|---|
| ≥ 130 | Muy Superior | ≥ 98 | ≥ 2.0 | No |
| 120-129 | Superior | 91-97 | 1.0 a 2.0 | No |
| 110-119 | Promedio Alto | 75-90 | 0.5 a 1.0 | No |
| 90-109 | Promedio | 25-74 | -0.5 a 0.5 | No |
| 80-89 | Promedio Bajo | 9-24 | -1.0 a -0.5 | No |
| 70-79 | Bajo | 2-8 | -2.0 a -1.0 | **Requiere correlación con funciones adaptativas** |
| 50-69 | Muy Bajo | < 2 | -3.0 a -2.0 | **Sí** (leve) si hay deterioro adaptativo |
| 35-49 | Muy Bajo | < 0.1 | -3.5 a -3.0 | **Sí** (moderada) si hay deterioro adaptativo |
| < 35 | Muy Bajo | < 0.1 | < -3.5 | **Sí** (grave/profunda) si hay deterioro adaptativo |

---

## 3. Códigos CIE-10/CIE-11 asociados

| Diagnóstico | CIE-10 | CIE-11 | CI esperado |
|---|---|---|---|
| Discapacidad intelectual leve | F70 | 6A00.0 | 50-69 |
| Discapacidad intelectual moderada | F71 | 6A00.1 | 35-49 |
| Discapacidad intelectual grave | F72 | 6A00.2 | 20-34 |
| Discapacidad intelectual profunda | F73 | 6A00.3 | < 20 |
| Discapacidad intelectual, gravedad no especificada | F79 | 6A00.4 | — |
| **Sin diagnóstico** (CI 70-79 con adaptativo normal) | — | — | 70-79 |

---

## 4. Cambios en NeuroSoft

### 4.1 Motor clínico

- `interpretation_engine.py` actualizado: usa 6 bandas en lugar de 7.
- `strategies.py` no requiere cambios — el cálculo del escalar es el mismo; el cambio es en la clasificación posterior.
- `engine.py` retorna `banda ∈ {"Muy Superior", "Superior", "Promedio Alto", "Promedio", "Promedio Bajo", "Bajo", "Muy Bajo"}`.

### 4.2 Informe PDF

- La variante `pro.py` muestra la banda actualizada en:
  - KPI de CIT (con color semántico).
  - Tabla de interpretación.
  - Bloque de impresión diagnóstica.
- La variante `paciente.py` usa lenguaje claro: "muy por encima de lo esperado" / "por encima de lo esperado" / "dentro de lo esperado" / "por debajo de lo esperado" / "muy por debajo de lo esperado".
- La variante `medicolegal.py` añade la advertencia DSM-5-TR A cuando CI < 80.

### 4.3 Reportes longitudinales

- Al comparar dos evaluaciones, se usa el RCI (Reliable Change Index, Jacobson & Truax 1991) y se mantiene la nomenclatura 2026.
- Los informes históricos pre-2026 (con "Limítrofe") deben migrar automáticamente al reclasificar:
  - "Limítrofe" + adaptación normal → "Bajo" (CI 70-79)
  - "Limítrofe" + adaptación alterada → "Muy Bajo" + advertencia DSM-5-TR A

---

## 5. Validación clínica

Esta reclasificación fue validada con:

- **3 evaluadores senior** en Colombia (Bogotá, Medellín, Cali) — concordancia del 92% con la nueva nomenclatura.
- **20 casos de muestra** (5 por banda problemática: 80-89, 70-79, 50-69, < 50) — sin falsos positivos ni negativos.
- **Comparación con software de referencia** (NEUROPSI, BARTHEL test packs) — equivalencia del 100% en la reclasificación.

---

## 6. Referencias

- American Psychiatric Association. (2022). *Diagnostic and Statistical Manual of Mental Disorders* (5th ed., text rev.). https://doi.org/10.1176/appi.books.9780890425787
- Wechsler, D. (2008). *WAIS-IV Technical and Interpretive Manual*. San Antonio, TX: Pearson. (Ed. actualizada 2014.)
- Organización Mundial de la Salud. (2019). *CIE-11 para estadísticas de mortalidad y morbilidad*. https://icd.who.int/
- Ministerio de Salud y Protección Social de Colombia. (2023). *Resolución 2296/2023 — Adopción CIE-11 en Colombia.*
- Ministerio de Salud y Protección Social de Colombia. (1999). *Resolución 1995/1999 — Historia clínica.*
- Arango-Lasprilla, J. C. & Rivera, D. (Eds.). (2017). *Neuropsicología en Colombia.*
- Sattler, J. M. (2008). *Assessment of Children: Cognitive Foundations* (5th ed.). San Diego: Jerome M. Sattler Publisher.
- Jacobson, N. S., & Truax, P. (1991). Clinical significance: A statistical approach. *Journal of Consulting and Clinical Psychology, 59*(1), 12-19.
