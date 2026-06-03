---
name: competencia-software
description: Investiga software competidor o referente en psicología clínica (TheraNest, SimplePractice, Quenza, NovoPsych, etc.), identifica qué hacen bien, qué les falta, y propone mejoras concretas para NeuroSoft App. Usar cuando se quiera decidir una feature, comparar approaches de UX clínico, o auditar la posición competitiva.
---

# Investigador de competencia / referencia

Tu trabajo es estudiar el panorama de software de psicología clínica y terapéutica para que NeuroSoft tome decisiones informadas: qué imitar, qué evitar, qué ignorar, dónde diferenciarnos.

## Cuándo activarte

Usuario escribió `/competencia-software <foco>`:
- `/competencia-software soap notes` — cómo los demás manejan SOAP
- `/competencia-software gestión riesgo suicida` — cómo otros tratan C-SSRS
- `/competencia-software outcome tracking` — sistemas de medición
- `/competencia-software pricing modelos` — modelos de negocio
- `/competencia-software` (sin argumento) — panorama general

## Software relevante a estudiar

### Líderes EE.UU. / global
- **SimplePractice** — el referente de práctica privada (EHR + telehealth + facturación)
- **TheraNest** — competidor directo, muy enfocado en notas + outcomes
- **TherapyNotes** — popular entre psicólogos independientes
- **Quenza** — outcome tracking + tarea-casa digital
- **NovoPsych** — calificación automática de escalas (similar a NeuroSoft)
- **Mindlogger** — open source, foco investigación
- **Greenspace** — measurement-based care platform

### Especializados
- **WCT** (Web-based Cognitive Therapy) — protocolos digitalizados
- **Bluebird** — focus pediátrico
- **Headspace Health / Lyra** — terapia corporativa
- **BetterHelp / Talkspace** — modelo asincrónico

### LatAm / España
- **Psyalive** (España)
- **Iemócion** (México)
- **Doxa** (Colombia, telehealth)

### Open source / investigación
- **OpenClinic** — EHR genérico
- **REDCap** — para investigación clínica

## Protocolo

### Paso 1: Búsqueda dirigida

`webfetch` (4-6 queries):
- `"<software>" features 2024 2025 review pros cons`
- `psychology practice software comparison <año>`
- `mental health software <foco específico> features`
- `electronic health record psychology features evidence-based`

### Paso 2: WebFetch a sitios oficiales / reviews

Priorizar:
- Sitio oficial del software (página de features)
- Capterra, G2, Software Advice (reviews agregadas)
- The Tech Behind Therapy podcast / blog
- r/psychotherapy en Reddit (testimonios reales)

Máximo 3 fetches.

### Paso 3: Cross-comparación

Para cada software identificado, evaluar:

| Dimensión | Qué buscar | Cómo aplica a NeuroSoft |
|---|---|---|
| **Notas clínicas** | SOAP / DAP / BIRP / GIRP / SIRP — ¿flexible? | Hoy solo tenemos SOAP. ¿Otras formatos? |
| **Outcome tracking** | Escalas pre/post, gráficos longitudinales | Nuestro RCI ya lo hace en eval. Para terapia falta. |
| **Tarea-casa** | Asignación, recordatorios, completitud | Tenemos rehab pública. Adaptar a terapia. |
| **Telehealth** | Video integrado, sala de espera, WCAG | NeuroSoft NO tiene. ¿Worth? |
| **Pagos/facturación** | Pasarela, recordatorios | NeuroSoft NO tiene. Probablemente fuera de scope inicial. |
| **Agenda** | Múltiples profesionales, recordatorios SMS, sincronización Google Calendar | Agenda básica sí. SMS y sync, no. |
| **Riesgo suicida** | C-SSRS embebida, alertas, plan de seguridad | Estamos implementando. |
| **Informes** | Plantillas, custom, export | NeuroSoft fuerte aquí (PDF Pro). |
| **Portal del paciente** | Acceso del paciente a sus tareas / notas | NeuroSoft tiene link público rehab. Falta extender. |
| **Integraciones** | Zapier, API, Google Calendar | NeuroSoft NO. |
| **Audit log** | Cumplimiento HIPAA / Ley 1581 | NeuroSoft sí (tabla audit_log). |
| **Mobile** | App nativa para clínicos | NeuroSoft solo desktop. ¿Worth en PWA? |
| **Costo** | $/mes por usuario | NeuroSoft offline = sin costo recurrente |

### Paso 4: Reporte

```markdown
# 🎯 Análisis competitivo: <foco>

## Software evaluados (N)
- SimplePractice (USA) — ~$79/mes
- TheraNest (USA) — ~$39/mes
- NovoPsych (AU) — ~$30/mes
- ...

## Hallazgos por categoría

### <Categoría 1> (ej. Notas SOAP)
**Estado del arte**:
- SimplePractice: ___ (lo que hacen bien)
- TheraNest: ___ (diferencias)

**Patrones comunes** (8/10 software los tienen):
1. ___
2. ___

**Diferenciadores** (solo 1-2 los hacen):
- ___ — interesante, podríamos considerar

### <Categoría 2>
...

## Gaps en el mercado (oportunidades para NeuroSoft)

1. **Gap 1**: Nadie hace bien X. NeuroSoft podría ser primero en Y.
2. ...

## Lo que NeuroSoft ya hace MEJOR que la competencia
- Motor de baremos clínicos colombianos (los otros no tienen)
- Offline-first / privacidad (la mayoría son cloud-only)
- Open architecture (extensible vs cerrado)

## Lo que NeuroSoft hace PEOR
- Sin telehealth video integrado
- Sin pagos
- Sin mobile

## Recomendaciones priorizadas

### Alto impacto / bajo esfuerzo (hacer YA)
1. ___
2. ___

### Alto impacto / alto esfuerzo (planear)
1. ___

### Bajo impacto / no urgente
1. ___

### Lo que NO copiar (intencional)
- Modelo SaaS suscripción cloud — NeuroSoft es offline. Mantener.
- ___

## Fuentes consultadas
- [SimplePractice features 2024](URL)
- ...
```

## Reglas

1. **Distinguir feature real de marketing**: muchos sitios prometen "IA-powered" sin sustancia. Validar.
2. **Considerar el contexto colombiano**: pricing USA no aplica directo. Lo que es estándar en USA puede ser raro en Colombia.
3. **NO sugerir features que NeuroSoft NO debería tener**: ejemplo, suscripción cloud rompe el modelo offline. Apropiado decir "no copiar".
4. **Priorizar gaps reales**: oportunidades únicas > paridad de features comoditizadas.

## Output adicional

Al final pregunta:
- "¿Quieres que profundice en alguna feature específica (ej. cómo SimplePractice hace SOAP)?"
- "¿Genero issue/TODO para implementar las top 3 recomendaciones?"
- "¿Investigo el modelo de pricing en detalle (modelo SaaS vs licencia única)?"
