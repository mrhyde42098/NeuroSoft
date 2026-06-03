# 🚀 Roadmap de expansión — NeuroSoft App

> **Visión a 2-3 años**: NeuroSoft pasa de ser solo evaluación neuropsicológica a una plataforma integral de psicología clínica con módulo educativo para profesionales y estudiantes.

---

## 🎯 Tres pilares del producto

```
                     NeuroSoft App
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   📊 EVALUACIÓN     🛋 SESIONES        🎓 APRENDER
   neuropsicológica   psicología         (estudiantes
   (HOY)              clínica            + profesionales)
                      (NUEVO)            (NUEVO)
```

Cada pilar comparte:
- **Paciente / cliente / usuario** (entidad común)
- **Profesional** (mismo perfil, distintas funciones)
- **Agenda** (citas para cualquier modalidad)
- **Historia clínica** (compartida)
- **Asistente IA** (configurado globalmente)
- **Configuración** (institución, plantillas, preferencias)

---

# 🛋 MÓDULO 1: Sesiones de Psicología Clínica

## Justificación

Hoy NeuroSoft sirve a neuropsicólogos que **evalúan** (1-3 sesiones, generan informe, terminan). Pero muchos psicólogos clínicos también hacen **psicoterapia** (proceso de meses, sesiones recurrentes, notas SOAP, planes de tratamiento, seguimiento de objetivos).

La extensión natural es habilitar el mismo software para psicología clínica general (CBT, sistémica, humanística, psicoanalítica, etc.) sin perder la rigurosidad neuropsicológica.

## 🎨 Modelo de datos propuesto

```python
# Nueva entidad: TerapiaSesion
class TerapiaSesion:
    id: UUID
    patient_id: FK
    profesional_id: FK
    fecha: datetime
    duracion_min: int  # default 50
    modalidad: enum("presencial", "telepsicologia", "telefonica")
    enfoque_terapeutico: enum("cbt", "tcc", "sistemica", "psicoanalitica", "humanistica", "emdr", "act", "mindfulness", "logoterapia", "gestalt", "otro")
    nota_soap_subjetivo: text  # S - lo que el paciente reporta
    nota_soap_objetivo: text   # O - lo que el clínico observa
    nota_soap_analisis: text   # A - interpretación clínica
    nota_soap_plan: text       # P - próximos pasos
    objetivos_trabajados: JSON list[FK ObjetivoTerapeutico]
    tareas_asignadas: JSON list  # "Practicar mindfulness 10 min/día"
    medicacion_actual: text  # cambios reportados
    riesgo_suicida: enum("ninguno", "ideacion_pasiva", "ideacion_activa", "plan", "intento_reciente")
    alianza_terapeutica: int  # 1-5 escala self-rated
    estado_emocional_inicio: int  # 0-10
    estado_emocional_fin: int  # 0-10
    grabacion_audio_url: Optional[str]  # si paciente consintió
    locked_at: Optional[datetime]  # firma terapéutica
    created_at: datetime

# Nueva entidad: PlanTerapeutico
class PlanTerapeutico:
    id: UUID
    patient_id: FK
    profesional_id: FK
    diagnostico_principal: str  # CIE-10
    diagnostico_secundario: Optional[str]
    objetivos_terapeuticos: JSON list[Objetivo]  # SMART goals
    enfoque_principal: str
    duracion_estimada_sesiones: int
    fecha_inicio: date
    fecha_revision: date
    fecha_cierre: Optional[date]
    motivo_cierre: Optional[str]  # "alta", "abandono", "derivacion"
    estado: enum("activo", "pausado", "cerrado")

# Nueva entidad: ObjetivoTerapeutico
class ObjetivoTerapeutico:
    id: UUID
    plan_id: FK
    descripcion: str  # "Reducir frecuencia de ataques de pánico de 4/semana a 1/semana"
    fecha_inicio: date
    fecha_meta: date
    estado: enum("activo", "cumplido", "modificado", "abandonado")
    criterios_medibles: text  # cómo se sabe si se cumple
    progreso_pct: int  # 0-100
```

## 📋 Sprints sugeridos (8 sprints, ~3 meses)

### S1: Modelo de datos y migración
- Crear ORMs `terapia_sesion`, `plan_terapeutico`, `objetivo_terapeutico`
- Agregar `tipo_atencion` a tabla `agenda_citas`: `"evaluacion" | "terapia"`
- Migración SQLite vía `patches` (engine.py)
- 0 datos perdidos del módulo de evaluación

### S2: Notas SOAP — UI principal
- Página `SesionTerapeuticaPage.jsx` con 4 textareas SOAP
- Cronómetro de duración (similar al de evaluación pero pasivo, opcional)
- Selector de objetivos trabajados (de los activos del plan)
- Botón "Cerrar sesión + firmar" (lock irreversible)
- Mejoras IA: botón "mejorar redacción" en cada SOAP

### S3: Plan terapéutico
- Página `PlanTerapeuticoPage.jsx` (creación, edición, cierre)
- Diagnóstico principal + comorbilidad (selector CIE-10 ya existe)
- Lista de objetivos terapéuticos SMART con progreso visual
- Indicador de "próxima revisión" en dashboard

### S4: Riesgo suicida — Sistema crítico
- Escala C-SSRS (Columbia Suicide Severity Rating Scale) embebida
- Alerta visual cuando se marca riesgo medio/alto
- Banner persistente en HC del paciente: "⚠ Riesgo activo desde DD/MM"
- Protocolo emergente: lista de contactos crisis (configurable por institución)
- Auditoría inmutable de cambios en nivel de riesgo

### S5: Telepsicología
- Modalidad "telepsicologia" en sesión
- Integración con link Jitsi/Whereby (sin grabar — privacidad)
- Consentimiento informado específico de telepsicología (formato ya existe en `consentimientos`)
- Verificación de identidad antes de iniciar (opcional)

### S6: Tareas terapéuticas para el paciente
- Reutilizar el sistema de "tarea-casa" de rehabilitación
- Adaptación a contexto clínico: diario de pensamientos, registro de emociones, ejercicios CBT
- El paciente entra al link público y completa
- Notificación al terapeuta cuando hay nueva entrada (igual que rehab notifications)

### S7: Informes de cierre / alta
- Informe distinto al neuropsicológico:
  - Motivo de consulta + evolución
  - Diagnóstico DSM-5/CIE-10
  - Objetivos cumplidos vs pendientes
  - Recomendaciones de seguimiento
  - Plantilla "Informe de alta", "Informe de derivación"

### S8: Visualización del proceso
- Gráfico de evolución del estado emocional sesión a sesión (línea 0-10)
- Gráfico de cumplimiento de objetivos (barras por objetivo, % cumplido)
- Dashboard "pacientes activos en terapia" vs "pacientes en evaluación"

## ⚠ Reglas críticas a definir antes de empezar

1. **¿Las notas SOAP se cifran en reposo?** Sí — son más sensibles que datos neuropsicológicos.
2. **¿El paciente tiene acceso a sus notas?** Por Ley 1581 Colombia, **sí puede solicitarlas** (derecho ARCO). Implementar export a PDF anonimizado.
3. **¿Hay diferencia de permisos entre psicólogos clínicos y neuropsicólogos?** Probablemente NO. Mismo rol `profesional`, distintas pantallas usadas.
4. **¿Cómo migrar evaluaciones existentes que también tuvieron terapia?** Backfill: agregar evento "Inicio de proceso terapéutico" en HC.

---

# 🎓 MÓDULO 2: Aprender / Repasar (Educativo)

## Justificación

Hay una oportunidad enorme: NeuroSoft ya tiene **datos clínicos rigurosos** (REACTIVOS, CONDUCTAS, GUIA_HC, INSTRUCCIONES, GUIA_INFORME, 168 pruebas con sus estímulos, casos clínicos verificados). Eso es material **educativo de primera mano** que estudiantes de psicología pagan por aprender en cursos.

Ofrecer este módulo:
- A estudiantes de pregrado/posgrado: ejercicios de práctica clínica, simulaciones de aplicación de pruebas
- A profesionales: repaso continuo (spaced repetition de criterios clínicos, casos para diagnóstico diferencial)

## 🧩 Componentes propuestos

### 1. Biblioteca clínica searchable
**Pantalla**: `BibliotecaPage.jsx`

Indexa todo lo que ya existe:
- **Pruebas** (168 con sus instrucciones, materiales, calificación) → para repasar "¿cómo se aplica WISC-IV?"
- **Escalas** (BAI, HADS, GDS, etc.) → "¿qué mide cada uno?"
- **Patrones clínicos** (de `DSM5_DIAGNOSES`, `RECOMMENDATIONS_LIB`) → "criterios DSM-5 de TDAH"
- **Glosario neuropsicológico** (nuevo): ICV, ICG, RCI, FBI, percentil, T-score, etc.
- **Algoritmos diagnósticos** (de `DIAGNOSTIC_ALGORITHMS`) → "decisión TDAH vs ansiedad"

Búsqueda global con `Cmd+K` (similar a Linear / Notion).

### 2. Sistema de tarjetas (spaced repetition)
**Pantalla**: `EstudiarPage.jsx`

Tarjetas tipo Anki integradas. Por ejemplo:
- **Anverso**: "¿Cuál es el punto de corte clínico del MMSE en deterioro cognitivo leve?"
- **Reverso**: "MMSE < 24 = deterioro probable; entre 24-26 = sospechoso (Folstein 1975, ajuste por escolaridad obligatorio)"

Curva de olvido FSRS (algoritmo moderno post-SM2):
- Acertaste fácil → revisión en 4 días
- Acertaste con esfuerzo → en 1 día
- No supiste → mañana

Cada profesional construye SU mazo o usa el oficial de NeuroSoft.

### 3. Simulador de casos
**Pantalla**: `SimuladorPage.jsx`

Caso clínico ficticio (basado en casos verificados anonimizados):
> "Paciente femenino, 8 años, viene a consulta por bajo rendimiento académico. Padre reporta dificultades atencionales..."

El estudiante:
1. Toma decisiones (¿qué baterías aplicar?)
2. Recibe resultados ficticios (PD generados con baremos reales)
3. Interpreta (escribe impresión diagnóstica)
4. Compara con la respuesta "experto" (Johan u otro neuropsicólogo experimentado)

Gamificación opcional: puntaje, ranking, certificado de finalización.

### 4. Quizzes auto-evaluativos
**Pantalla**: `QuizPage.jsx`

Cuestionarios cortos (10 preguntas) por tema:
- Quiz "DSM-5 Trastornos del Neurodesarrollo"
- Quiz "Interpretación de WISC-IV"
- Quiz "Neuronorma Colombia AM"
- Quiz "Validez de síntomas (Rey 15, TOMM)"

Resultados se registran. Si el profesional aprueba 80% en todos los quizzes de un módulo, badge "Experto certificado en X" (puramente reputacional, no acreditación formal).

### 5. Glosario interactivo
**Componente reutilizable**: `<GlossaryTerm>`

Cualquier término técnico en cualquier parte de la app puede tener un tooltip con definición. Ejemplo: hover sobre "ICV" en EvalResultsPage → muestra "Índice de Comprensión Verbal: medida del razonamiento verbal y conocimiento adquirido. Suma escalar de Semejanzas, Vocabulario y Comprensión (WISC-IV)."

Implementación: componente `<GlossaryTerm term="ICV">ICV</GlossaryTerm>` que envuelve cualquier texto.

### 6. Contenido educativo (artículos cortos)
**Pantalla**: `AprenderPage.jsx`

Artículos de 5-10 min de lectura sobre temas clínicos:
- "Cómo interpretar una discrepancia ICV-IRP en WISC-IV"
- "Diferencial entre TDAH presentación inatenta y ansiedad infantil"
- "Aplicación del Stroop en pacientes con baja escolaridad"
- "Comprensión del RCI y cuándo NO usarlo"

Cada artículo escrito por Johan o profesionales invitados. Hace que NeuroSoft sea también **referencia clínica viva**.

## 📋 Sprints (6 sprints, ~2 meses)

| Sprint | Entregable |
|---|---|
| E1 | Biblioteca clínica searchable (indexa lo que ya existe) |
| E2 | Glosario interactivo + tooltips embebidos en la app |
| E3 | Spaced repetition + 200 tarjetas oficiales iniciales |
| E4 | Quiz engine + 10 quizzes oficiales |
| E5 | Simulador de casos clínicos (3-5 casos iniciales) |
| E6 | Plataforma de artículos (markdown rendering + tracking de progreso) |

## 💎 Modelos de monetización (futuro lejano, no parte de este roadmap técnico)

- **Gratis**: app de evaluación clínica para profesionales licenciados (NeuroSoft actual)
- **Premium estudiantil** ($X/mes): acceso a simulador, quizzes, tarjetas oficiales
- **Premium institucional** ($Y/año): toda la suite + dashboards de aprendizaje para universidades

---

# 🔧 Cambios técnicos que habilitan ambas expansiones

## 1. Refactor de navegación (Sidebar)

El sidebar actual tiene 4 grupos: Clínica, Evaluación, Rehabilitación, Herramientas. Cambiar a:

```
┌─ Clínica
│   ├─ Pacientes
│   └─ Agenda
├─ Evaluación
│   ├─ Aplicar evaluación
│   ├─ Screening
│   ├─ Historial
│   ├─ Pre–Post
│   └─ Informes
├─ Sesiones [NUEVO]
│   ├─ Sesión activa
│   ├─ Planes terapéuticos
│   └─ Riesgo & alertas
├─ Rehabilitación
│   └─ Plan & Actividades
├─ Aprender [NUEVO]
│   ├─ Biblioteca
│   ├─ Estudiar (tarjetas)
│   ├─ Simulador
│   ├─ Quizzes
│   └─ Artículos
└─ Herramientas
    ├─ Asistente IA
    ├─ Telemedicina
    ├─ Configuración
    └─ Ayuda
```

## 2. Extender entidad Paciente

Agregar campos:
- `tipo_atencion`: enum("evaluacion", "terapia", "ambos")
- `plan_terapeutico_id`: FK opcional (si está en proceso)
- `frecuencia_sesiones`: enum("semanal", "quincenal", "mensual", "puntual")

## 3. Extender entidad Profesional

Agregar:
- `enfoques_terapeuticos`: list[str] — CBT, sistémica, etc.
- `acepta_evaluaciones`: bool (default True)
- `acepta_terapia`: bool (default False, opt-in)
- `acepta_estudiantes`: bool (para módulo educativo, mentoring)

## 4. Sistema de permisos extendido

Roles actuales: `admin`, `profesional`, `viewer`.
Roles propuestos:
- `admin` (sin cambios)
- `profesional` (sin cambios — acceso completo a evaluación + sesiones)
- `viewer` (sin cambios)
- `estudiante` [NUEVO]: solo módulo educativo, NO acceso a datos reales de pacientes
- `paciente` [NUEVO, futuro]: acceso a SUS propios datos (informes, tareas-casa, derecho ARCO)

## 5. Domain-driven design — bounded contexts

Reorganizar el backend en módulos por dominio:

```
neurosoft-backend/app/
├── shared/                ← entidades comunes (Paciente, Profesional, Agenda)
├── evaluation/           ← módulo evaluación (HOY)
│   ├── domain/clinical_engine/
│   ├── application/
│   └── presentation/
├── therapy/              ← módulo terapia [NUEVO]
│   ├── domain/
│   ├── application/
│   └── presentation/
└── education/            ← módulo educativo [NUEVO]
    ├── domain/
    ├── application/
    └── presentation/
```

Cada módulo tiene su propio dominio. Comparte solo `shared`.

---

# 🎯 Orden de implementación recomendado

| Fase | Duración | Objetivo |
|---|---|---|
| **0** Pre-trabajo | 2 semanas | Mejoras de UI/código del audit actual, FCRO arreglado, informe PDF Pro |
| **1** Sesiones — MVP | 1 mes | S1-S3: modelo, notas SOAP, plan terapéutico básico |
| **2** Sesiones — Avanzado | 1 mes | S4-S8: riesgo suicida, telepsi, tareas, informes, visualización |
| **3** Refactor estructural | 2-3 semanas | Bounded contexts en backend, sidebar reorganizado |
| **4** Educativo — MVP | 1 mes | E1-E3: biblioteca, glosario, tarjetas |
| **5** Educativo — Avanzado | 1 mes | E4-E6: quizzes, simulador, artículos |
| **6** Iteración beta | continua | Feedback de beta testers (3-4 profesionales) |

Total estimado: **5-6 meses** para tener ambos módulos en estado beta.

---

**Próximo paso inmediato**: terminar la auditoría actual, arreglar lo que se pueda en pre-trabajo (Fase 0), y antes de empezar Fase 1 hacer una sesión de planeación con Johan para definir prioridades específicas.
