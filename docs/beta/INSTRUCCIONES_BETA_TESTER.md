# NeuroSoft v2026-05 — Guía para Beta Testing

¡Hola! 👋 Bienvenido a **NeuroSoft**, un sistema integral de evaluación neuropsicológica clínica. Esta guía te ayudará a explorar las nuevas funcionalidades y reportar feedback.

---

## 🚀 Instalación

1. **Descarga** el archivo `NeuroSoft.exe` que te han proporcionado
2. **Doble-click** para ejecutar (primera ejecución descargará datos)
3. Espera a que se abra la aplicación en tu navegador (http://localhost:3000)
4. Los datos se guardan en: `%APPDATA%/NeuroSoft/` (Windows)

---

## 📋 Qué Tesar (Testing Checklist)

### ✅ Nuevos Instrumentos de Screening

**1. FAB (Frontal Assessment Battery)**
- **Dónde:** Módulo Screening → Cognitivos → FAB
- **Qué testar:**
  - Renderiza las 6 subtareas (Conceptualización, Fluidez, Secuencia Luria, Interferencia, Go/No-Go, Autonomía)
  - Cada subtarea es 0-3
  - Total máx = 18
  - Corte ≤12 sugiere disfunción frontal
- **Caso de uso:** Paciente con sospecha de demencia frontotemporal o daño frontal

**2. IES-R (Impact of Event Scale Revised)**
- **Dónde:** Módulo Screening → Trauma / PTSD → IES-R
- **Qué testar:**
  - 22 ítems, escala 0-4
  - **3 subescalas visibles:**
    - Intrusión (8 ítems) — cutoff 12
    - Evitación (8 ítems) — cutoff 8
    - Hiperactivación (6 ítems) — cutoff 9
  - Panel inferior muestra puntajes de cada subescala
  - Total ≥33 = PTSD probable
- **Caso de uso:** Paciente con antecedente de trauma (accidente, violencia, etc.)
- **Red flag:** Si Intrusión o Hiperactivación muy altos → banner de alerta

**3. PCL-5 (PTSD Checklist for DSM-5)**
- **Dónde:** Módulo Screening → Trauma / PTSD → PCL-5
- **Qué testar:**
  - 20 ítems, escala 0-4
  - Corresponde 1:1 con criterios DSM-5 (Intrusión, Evitación, Cognición Negativa, Hiperactivación)
  - Total ≥31 = PTSD probable
  - Severity:
    - 0-19: Sin indicadores significativos
    - 20-31: Leve
    - 32-49: Moderado
    - 50-80: Severo
- **Caso de uso:** Validación diagnóstica complementaria a IES-R

---

### ✅ Subescalas en Screening (STAI Mejorado)

**Instrumento de prueba:** STAI (Inventario de Ansiedad Estado-Rasgo)
- **Qué testar:**
  - **Estado (E):** Primeros 20 ítems — "¿Cómo se siente ahora mismo?"
  - **Rasgo (R):** Ítems 21-40 — "¿Cómo se siente en general?"
  - Panel inferior muestra:
    - Puntaje Estado (máx 60)
    - Puntaje Rasgo (máx 60)
    - Puntaje Total (máx 120) — ANTES era erróneamente 80
  - Cada subescala tiene su propio cutoff (≥19/60)
- **Verificar:**
  - ¿Se ven los headers "Estado (E)" y "Rasgo (R)"?
  - ¿El panel de subescalas aparece abajo?
  - ¿Los cutoffs individuales se marcan correctamente?

---

### ✅ Panel de Interpretación Clínica Automatizada

**Dónde:** Resultados de Evaluación → Panel "Interpretación Clínica Asistida"

**Qué testar** (llena una evaluación completa WISC o WAIS y mira este panel):

1. **Detección de "Islas de Habilidad"**
   - ¿Muestra el rango, media, y desviación estándar intraindividual?
   - ¿Marca si es "Perfil Heterogéneo" o "Homogéneo"?
   - ¿Lista fortalezas y debilidades?
   - **Caso:** Paciente con IVP muy bajo pero ICV alto → debería marcar TCL/CDHS

2. **Patrones Detectados (6 tipos)**
   - [ ] **TDAH**: Ejecutivo (IMT+IVP)/2 < 90 AND Cristalizado (ICV+IRP)/2 ≥ 90 AND brecha ≥ 15
   - [ ] **TCL/CDHS**: IVP < 85 AND diferencia ≥ 20 AND ICV ≥ 90
   - [ ] **TEA**: Perfil heterogéneo + ICV bajo vs IRP alto
   - [ ] **DEA**: Discrepancia verbal-perceptual sin DI
   - [ ] **DCL**: Edad ≥55 + múltiples índices < 85
   - [ ] **Normal**: Promedio ≥95, CIT ≥90, homogéneo
   - **Verificar:** ¿Aparecen las alertas correctamente?

3. **Índices Compuestos**
   - Tabla con: CIT, ICV, IRP, IMT, IVP
   - **NEW:** Si hay ICG o ICC → panel separado con tooltips
   - **Verificar:** ¿Los colores reflejan la interpretación (verde=bueno, rojo=bajo)?

4. **Texto Clínico Borrador**
   - Botón "Texto borrador para observaciones clínicas" (expandible)
   - Genera párrafos profesionales basados en el perfil
   - Copiar botón funcional
   - **Verificar:** ¿El texto es coherente con los índices mostrados?

---

## 🎯 Casos de Uso de Prueba Recomendados

### Caso 1: TDAH Probable (Ejecutivo Bajo)
- WAIS: ICV=95, IRP=98, IMT=78, IVP=82, CIT=88
- **Esperar:** Panel marca "TDAH / Déficit atencional-ejecutivo — brecha 15-18 pts"
- **Acción recomendada:** SNAP-IV, ASRS

### Caso 2: Tempo Cognitivo Lento
- WAIS: ICV=98, IRP=100, IMT=95, IVP=68, CIT=88
- **Esperar:** Panel marca "TCL / CDHS — IVP muy bajo, otros índices preservados"
- **Acción:** Descartar ansiedad, trastorno del sueño

### Caso 3: DCL (Adulto Mayor 62 años)
- WAIS-III: ICV=82, IRP=80, IMT=78, IVP=75
- **Esperar:** Panel marca "DCL multi-dominio" + "Aplicar GDS-15, FAQ, Barthel"
- **Seguimiento:** Repetir en 6-12 meses

### Caso 4: FAB Baja
- Resultados: 8/18 (por debajo del cutoff ≤12)
- **Esperar:** Panel marca "Posible disfunción frontal — derivar a neurología"
- **Validar con:** Conglomerado de síntomas conductuales

---

## 🐛 Qué Reportar

Por favor, documenta:

### Bugs
- **Si algo no aparece:** "Panel Interpretación Clínica no aparece" + screenshot
- **Si los números son incorrectos:** "STAI total muestra 95 cuando debería ser 105"
- **Si hay error en consola:** Copia el mensaje de error exacto

### Usabilidad
- ¿Es fácil encontrar los nuevos instrumentos?
- ¿Entienden los clínicos qué significan los patrones detectados?
- ¿Falta algo en el panel de interpretación?

### Interpretación Clínica
- ¿El panel sugiere patrones que NO tienen sentido para tu caso?
- ¿Falta algún patrón importante que deberías ver?
- ¿Es accionable el texto generado automáticamente?

---

## 📧 Cómo Reportar

**Envía tus hallazgos a:** [Tu email aquí]

**Formato:**
```
TIPO: Bug / Usabilidad / Interpretación clínica
INSTRUMENTO/PANEL: Nombre
DESCRIPCIÓN: Qué sucede
CÓMO REPRODUCIR: Pasos para verlo de nuevo
IMPACTO: Minor / Major / Critical
SCREENSHOT/LOG: Si aplica
```

---

## 📚 Documentación Complementaria

- **Validación STAI:** Spielberger et al. 1970; Martens et al. 1990
- **IES-R:** Weiss & Marmar 1997; Bovin et al. 2016 (validación Colombia)
- **PCL-5:** Weathers et al. 2013 (VA/DoD)
- **FAB:** Dubois et al. 2000; Arango-Lasprilla et al. 2015 (normas Colombia)

---

## 🎁 Bonificaciones si Encuentras

- **Patrón no detectado correctamente:** Ideas para mejora
- **Instrumento que falta:** Sugerir qué agregar
- **Workflow mejorable:** Cómo haría el flujo más fluido

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo probar con datos de pacientes reales?**
R: Sí, pero asegúrate de anonimizar completamente (sin nombres, cédulas, etc.)

**P: ¿Qué pasa si un patrón detectado ≠ diagnóstico clínico?**
R: Es normal. El panel es **GUÍA, no diagnóstico**. El clínico siempre valida. Reporta si la sugerencia NO tiene sentido.

**P: ¿Cuál es el propósito de ICG vs ICC?**
R: **ICG** (Capacidad General) = alternativa cuando IVP es discrepante (más estable)
**ICC** (Competencia Cognitiva) = refleja atención/ejecutivas. Ambos complementan el CIT.

**P: ¿Por qué STAI ahora maxScore=120?**
R: Era un bug — 40 ítems × 3 (máx por ítem) = 120, no 80. Ahora es correcto clínicamente.

---

**Muchas gracias por ser beta tester. Tu feedback es invaluable para mejorar NeuroSoft.** 🙏

---

*Guía versión: 2026-05-12*
*NeuroSoft v2026-05*
