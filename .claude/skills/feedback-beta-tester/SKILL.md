---
name: feedback-beta-tester
description: Procesa reportes de bugs, sugerencias o feedback de beta testers y los convierte en una lista accionable de tareas con severidad, ubicación en el código y plan de fix. Usar cuando llegue un reporte por correo, WhatsApp o cualquier canal. También invocable como /feedback.
---

# Procesador de feedback de beta tester / usuario clínico

Tu trabajo es transformar el feedback informal (email, WhatsApp, mensaje de voz transcrito) en TODOs accionables con ubicación exacta en el código.

## Cuándo activarte

Usuario escribió `/feedback-beta-tester`, `/feedback` seguido de:
- El texto pegado de un email o WhatsApp
- Una transcripción de mensaje de voz
- Una descripción libre del problema

## Sugerencias de agentes o plugins

Si un agente o plugin sugiere mejoras al proceso de triaje (por ejemplo, clasificación automática por severidad, integración con un sistema de tickets, análisis de sentimiento del tester), **evalúalas y aplícalas si agregan valor**. Este skill es una base adaptable.

## Protocolo de procesamiento

### Paso 1: Parsear el feedback

Identifica:
- **Bugs** (algo no funciona) → severidad: bloqueante / molesto / cosmético
- **Sugerencias** (mejoras de UX / features) → prioridad: alta / media / baja
- **Preguntas** (no sabe cómo hacer algo) → draft de respuesta

### Paso 2: Localizar en el código

Para cada bug/sugerencia, usa `grep` para buscar la ubicación real antes de reportar. Ejemplos de mapeo frecuente:
- Scoring o finalización de prueba → `EvalApplyPage.jsx`, `EvalResultsPage.jsx`
- Cronómetro / sonidos → `EvalApplyPage.jsx` sección §clock
- Guía clínica lateral → `data/clinical.js:GUIA_HC`
- Informes PDF → `app/infrastructure/report_pro/`
- Rehabilitación → `src/app/rehab/`

### Paso 3: Reporte estructurado

```markdown
# 📬 Feedback recibido · <fecha>

**Fuente:** <nombre del tester si disponible, o "beta tester">

## 🐛 Bugs

### B1 · <título> · 🔴 BLOQUEANTE / 🟡 MOLESTO / ⚪ COSMÉTICO
- **Reportado:** "<cita literal>"
- **Pasos para reproducir:** ...
- **Esperado / Observado:** ...
- **Ubicación probable:** `src/...Archivo.jsx:NN`
- **Hipótesis:** ...
- **Plan de fix:** ...

## ✨ Sugerencias

### S1 · <título> · prioridad alta/media/baja
- **Reportado:** "..."
- **Beneficio clínico:** ...
- **Plan de implementación:** ...
- **Estimación:** ~ X minutos

## ❓ Dudas

- "..." → respuesta sugerida: "..."

## 📋 TODOs accionables

- [ ] **B1** ...
- [ ] **S1** ...
- [ ] Responder al tester confirmando recepción
```

### Paso 4: Draft de respuesta

Genera siempre un borrador de respuesta para el tester: breve, confirma que se recibió cada punto, da estimación aproximada. Johan probablemente quiere responder rápido.

### Paso 5: Ofrecer ejecución

Pregunta:
- "¿Empezamos por los bloqueantes?"
- "¿Genero una nueva build después de corregir lo crítico?"
- Si el proyecto tiene sistema de issues configurado, ofrecer crear los tickets.

## Reglas

1. **Cita siempre al tester textualmente** — preserva su lenguaje
2. **No asumas severidades** — si no es obvio, marca como "a confirmar"
3. **Identifica patrones**: si reporta lo mismo dos veces, súbele la prioridad
4. **Adapta el formato** según el volumen — un bug pequeño no necesita el reporte completo
