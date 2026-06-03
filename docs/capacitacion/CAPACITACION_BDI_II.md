# Material de Capacitación BDI-II (AdBeck) — NeuroSoft App v2.0.0

> **Paso 4 de 5** del plan de validación post-migración F7.2.
> Para clínicos usuarios del sistema. Cubre los cambios en las bandas de clasificación del BDI-II aplicados el 2026-06-03.

## ¿Qué cambió?

**Antes (pre-2026-06-03):**
El sistema tenía 6 claves heredadas del Excel VBA original (Cell IDs `16190..16195`) que en ciertos puntajes producían clasificaciones incorrectas. El motor tenía un fallback hardcoded que compensaba parcialmente, pero el bug estaba en la fuente de datos.

**Después (post-F7.2):**
El sistema usa las **4 bandas oficiales del manual Beck Steer Brown 1996**:

| Puntaje | Clasificación | Severidad | Implicación clínica |
|---|---|---|---|
| **0-13** | Depresión **mínima** | Sin criterios clínicos | Sin tratamiento específico. Seguimiento rutinario. |
| **14-19** | Depresión **leve** | Síntomas sutiles | Considerar psicoterapia. Vigilancia activa. |
| **20-28** | Depresión **moderada** | Síntomas clínicamente significativos | **Tratamiento activo**: psicoterapia + considerar farmacoterapia. |
| **29-63** | Depresión **severa** | Síntomas severos con compromiso funcional | **Tratamiento intensivo**: farmacología + psicoterapia + seguimiento estrecho. |

## Punto de corte clínico

**≥14 puntos** indica presencia de un episodio depresivo clínicamente significativo. Por debajo de este puntaje NO se considera un cuadro depresivo (aunque puede haber síntomas aislados).

## Cómo verificar en el sistema

### En la aplicación:

1. Abra la evaluación del paciente.
2. Vaya a `EvalResultsPage`.
3. Busque la sección "AdBeck" o "BDI-II".
4. Verifique que la clasificación mostrada coincida con las 4 bandas oficiales.

### En el PDF generado:

El informe PDF muestra el resultado del BDI-II en la sección de "Pruebas Aplicadas → Escalas de Tamizaje" (si la prueba fue parte del protocolo) o como observación clínica (si fue autoaplicada).

## Validación con casos reales

**Caso 5 (Isabella Cardona, 16a, Femenino):**
- PD = 22 → Clasificación: **Depresión moderada**
- Banderas clínicas: tristeza persistente, anhedonia, aislamiento, pérdida de peso
- Plan: psicoterapia + evaluación farmacológica

**Caso 9 (María Salazar, 25a, Femenino, postparto):**
- PD = 22 → Clasificación: **Depresión moderada**
- Contexto: F53.0 (depresión postparto) según CIE-10
- Plan: psicoterapia + interconsulta psiquiatría

**Caso 13 (Carolina Ramírez, 45a, Femenino, TAB):**
- PD = 28 → Clasificación: **Depresión moderada** (límite)
- Banderas: TAB tipo II en episodio depresivo
- Plan: ajuste farmacológico (litemio + lamotrigina)

**Caso 12 (Sebastián Quintero, 22a, Masculino, post-TCE):**
- PD = 18 → Clasificación: **Depresión leve**
- Banderas: ajuste emocional post-trauma
- Plan: psicoterapia de apoyo, seguimiento estrecho

## Diferencias con clasificaciones previas

| PD | Antes (incorrecto) | Ahora (correcto) | Diferencia |
|---|---|---|---|
| 14 | A veces "Mínima" | **Leve** | Cambio a severidad mayor |
| 19 | A veces "Mínima" | **Leve** (límite) | Cambio a severidad mayor |
| 20 | A veces "Mínima" o "Leve" | **Moderada** | Cambio a severidad mayor |
| 28 | A veces "Leve" | **Moderada** (límite) | Cambio a severidad mayor |
| 29 | A veces "Leve" o "Moderada" | **Severa** | Cambio a severidad mayor |

## Implicaciones clínicas

1. **Mayor sensibilidad diagnóstica:** Un paciente con PD=14 ahora se clasifica como "Leve" en vez de "Mínima", lo cual puede disparar alertas clínicas y recomendaciones de tratamiento activo.

2. **Criterios de severidad más estrictos:** Un paciente con PD=20 ahora se clasifica como "Moderada", activando recomendaciones de farmacoterapia.

3. **Punto de corte ≥14:** Es el umbral estándar internacional para episodio depresivo mayor. Un paciente por debajo de este puntaje no cumple criterios DSM-5 para episodio depresivo.

4. **Documentación en informe:** El sistema automáticamente incluye la banda de clasificación en el informe PDF, lo cual facilita la comunicación con el equipo tratante.

## Cómo aplicar en la consulta

### Pregunta inicial (screening):
> "¿Ha tenido en las últimas 2 semanas alguno de estos síntomas: tristeza persistente, pérdida de interés, cambios de sueño o apetito, fatiga, dificultad de concentración, pensamientos de minusvalía?"

Si **≥2 síntomas + PD≥14** → Depresión clínicamente significativa → Iniciar protocolo de tratamiento.

### Si PD = 14-19 (Leve):
- **Primera línea:** Psicoterapia (TCC, TIP, activación conductual).
- **Seguimiento:** Cada 2-4 semanas.
- **Reevaluación BDI-II:** A las 4-6 semanas.

### Si PD = 20-28 (Moderada):
- **Tratamiento activo:** Psicoterapia + considerar ISRS (sertralina, escitalopram, fluoxetina).
- **Seguimiento:** Cada 1-2 semanas al inicio, luego cada 2-4 semanas.
- **Reevaluación BDI-II:** A las 4-6 semanas.

### Si PD = 29-63 (Severa):
- **Tratamiento intensivo:** Farmacología + psicoterapia + interconsulta psiquiatría.
- **Seguimiento:** Semanal al inicio.
- **Evaluación de riesgo suicida:** Obligatoria (C-SSRS).
- **Reevaluación BDI-II:** A las 2-4 semanas.

## Advertencias importantes

⚠️ **El BDI-II NO es diagnóstico:** Es un instrumento de tamizaje y seguimiento. El diagnóstico de episodio depresivo mayor requiere:
- 5+ síntomas DSM-5 durante ≥2 semanas
- Compromiso funcional significativo
- Exclusión de sustancias y causa médica
- Evaluación clínica por profesional competente

⚠️ **En adultos mayores:** Considerar ajuste por escolaridad. Pacientes con Primaria-Incompleta pueden sub-reportar síntomas.

⚠️ **En adolescentes (Caso 5):** El BDI-II está validado para ≥13 años. Para menores, usar CDI.

## Referencias bibliográficas

1. Beck, A. T., Steer, R. A., & Brown, G. K. (1996). *Manual for the Beck Depression Inventory-II*. San Antonio, TX: Psychological Corporation.
2. Beck, A. T., Steer, R. A., & Carbin, M. G. (1988). *Differential power of self-report questionnaires in predicting clinical judgments of depression*. Journal of Clinical Psychology, 44(5), 735-739.
3. American Psychiatric Association. (2022). *Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision (DSM-5-TR)*. Washington, DC: APA.
4. Instituto Colombiano de Neuropsicología. (2017). *Adaptación colombiana del BDI-II en población clínica y no clínica*. (Documento interno de validación).
5. World Health Organization. (2019). *International Statistical Classification of Diseases and Related Health Problems, 11th Revision (ICD-11)*. Geneva: WHO.

## Recursos adicionales en NeuroSoft

- **Auto-interpretación IA** (opcional): El sistema puede sugerir la clasificación del BDI-II y la impresión diagnóstica DSM-5/CIE-10 si el clínico lo activa en la pestaña de IA.
- **Plantillas de informe:** Hay 7 variantes de informe PDF (`estandar`, `pro`, `pediatrico`, `medicolegal`, `junta_medica`, `inconcluso`, `paciente`) que incluyen el BDI-II cuando aplica.
- **C-SSRS (riesgo suicida):** El sistema incluye el Columbia Suicide Severity Rating Scale como instrumento complementario para pacientes con PD≥20.
- **Seguimiento longitudinal:** Permite comparar BDI-II pre-post con RCI (Reliable Change Index de Jacobson & Truax 1991).

## Contacto de soporte

Para preguntas sobre la implementación del BDI-II en NeuroSoft App, contacte a:
- **Desarrollador:** Johan Sebastián Salgado Sarmiento
- **Email:** jssalgadosa@unal.edu.co

---

**Versión del documento:** 1.0 · 2026-06-03
**Aplica para:** NeuroSoft App v2.0.0+
