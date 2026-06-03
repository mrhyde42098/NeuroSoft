# NeuroSoft App — Roadmap consolidado 2026

> Hoja de ruta práctica de mejoras pendientes, ordenadas por impacto/esfuerzo.
> Versión: 2026-05-20 (post-auditoría baremos Excel).

---

## 🟢 Quick wins — implementables en horas/días, gran impacto

### QW-1. Selector de carpeta + envío por email + impresión de informes
**Estado:** EN IMPLEMENTACIÓN (este sprint).
**Por qué:** el clínico hoy depende de la carpeta default del visor de PDF; no puede mandar al correo del paciente directamente.

**Cambios:**
- Backend `app/presentation/api/v1/reports.py`: endpoint `POST /api/v1/reports/email` con destinatario, asunto, mensaje + adjunto PDF.
- Backend `app/presentation/api/v1/config.py`: nueva entrada `default_reports_folder` en preferencias.
- Frontend `InformesPage.jsx`: 3 botones nuevos sobre el overlay PDF:
  - 🖨️ Imprimir (window.print del iframe)
  - 📧 Enviar por correo (modal con campos)
  - 💾 Guardar en… (selector de carpeta vía `pywebview.api.choose_folder()`)
- Frontend `config/FormatosTab.jsx`: campo "Carpeta default para informes".

### QW-2. Configuración SMTP de la institución
**Por qué:** sin esto no funciona QW-1.
- Pantalla en `ConfigPage.jsx` → tab "Comunicaciones" con host, puerto, usuario, contraseña, TLS/SSL.
- Endpoint `GET/PUT /api/v1/config/smtp`.
- Botón "Probar configuración" (envía email de prueba).
- Cifrar contraseña en reposo.

### QW-3. Plantillas de email del informe
- 3 plantillas precargadas: "Envío informe al paciente", "Envío informe a EPS/IPS", "Envío informe a médico tratante".
- Variables: `{paciente}`, `{fecha}`, `{diagnostico}`, `{profesional}`.
- Editor en `ConfigPage` → tab "Plantillas".

### QW-4. Acción "Imprimir HC completa"
- Botón en `PatientHCPage` que genera PDF de la historia clínica completa (sin necesidad de tener evaluación) usando ReportLab.
- Útil para EPS que piden HC, no informe NPS.

### QW-5. Acción "Compartir con código PIN"
- Hoy hay PanelCompartir. Agregar opción "Acceso protegido por PIN de 6 dígitos" para envíos sensibles.
- El paciente recibe el link + un PIN aparte (SMS/WhatsApp).

### QW-6. Etiquetas/categorías de pacientes
- En `PatientsPage`: chips de colores configurables ("EPS Sanitas", "Particular", "Convenio universidad", etc.).
- Filtro por etiqueta en el panel.

### QW-7. Recordatorios automáticos de citas
- APScheduler ya está en backend. Job diario que envía email/SMS a pacientes con cita al día siguiente.
- Plantilla configurable.

### QW-8. Backup automático configurable
- Hoy `BackupTab` existe. Agregar:
  - Frecuencia (diaria/semanal/mensual)
  - Carpeta destino (USB, OneDrive, Dropbox local sync, Google Drive sync)
  - Notificación email si falla.

---

## 🟡 Mejoras de medio plazo — sprints de 1-2 semanas

### M-1. Módulo académico de terapias enriquecido (★ priorizado por el usuario)
**Estado:** EN IMPLEMENTACIÓN.
Hoy `enfoquesTerapeuticos.js` tiene 1 línea por enfoque. Expandir a un mini-LMS:

- **Click en una terapia** → modal/panel `EnfoqueDetalle.jsx` con tabs:
  1. **Resumen** — lo actual + descripción extendida
  2. **Cómo se aplica** — paso a paso ampliado por fase
  3. **Técnicas** — cada técnica con explicación + ejemplo clínico
  4. **Videos** — embebidos YouTube (de profesores reconocidos: Aaron Beck, Steven Hayes, etc.)
  5. **Bibliografía** — libros, papers DOIs, capítulos
  6. **Casos prácticos** — vignettes clínicas
  7. **Recursos** — PDFs descargables, plantillas, registros

- Enriquecer `enfoquesTerapeuticos.js` con campos nuevos:
  ```js
  descripcion_extendida: "Texto largo...",
  videos: [{ titulo, url_youtube, autor, duracion }],
  manuales: [{ titulo, editorial, anio, isbn }],
  casos: [{ titulo, vignette, hipotesis, plan }],
  recursos_pdf: [{ titulo, url }],
  ```

- Implementación en 3 enfoques piloto: **CBT**, **ACT**, **EMDR**.

### M-2. Módulo "Aprender / Estudiar" (académico general)
Del `ROADMAP_EXPANSION.md` §MÓDULO 2:
- Biblioteca clínica searchable (Cmd+K).
- Glosario interactivo con tooltips embebidos en toda la app.
- Tarjetas spaced repetition (Anki-style).
- Quiz engine con cuestionarios por tema.
- Artículos clínicos cortos.

### M-3. Riesgo suicida — Sistema crítico
Del `ROADMAP_EXPANSION.md` §S4:
- Escala C-SSRS embebida.
- Banner persistente en HC del paciente.
- Lista de contactos crisis configurable por institución.
- Auditoría inmutable de cambios en nivel.

### M-4. Telepsicología
- Modalidad "telepsicologia" en sesión (ya existe enum).
- Botón "Generar link Jitsi/Whereby/Meet" en cada sesión.
- Consentimiento informado específico de telepsicología.
- Verificación de identidad (DOC + selfie opcional).

### M-5. Marcador de completitud por sección del informe
Del `CLINICAL_ROADMAP.md` §1.4:
- En cada paso del wizard de informe: indicador "HC ✓, evaluación ✓, observaciones por dominio ⚠ 3/8".
- Bloquear envío si secciones críticas vacías.
- "Modo informe inconcluso" con razón categórica.

### M-6. Orden clínico de aplicación en evaluación
Del `CLINICAL_ROADMAP.md` §2:
- El `ReactivePanel` actual sigue orden del manual editorial; el clínico real aplica por interferencia.
- Botón "Siguiente clínicamente" que respeta protocolo + bloquea recobro antes de 20 min.
- Indicador de "tiempo de retención" para Grober/HVLT.

### M-7. Acompañante como entidad
Del `CLINICAL_ROADMAP.md` §1.1:
- Hoy se mete texto libre. Crear tabla `acompanantes` con FK a paciente.
- Relación (madre/padre/cuidador/etc.), teléfono, email, autorización para escalas.

### M-8. Bandeja de escalas sugeridas según MC
Del `CLINICAL_ROADMAP.md` §1.2:
- Si MC = "déficit atención" + edad <16 → sugerir SNAP-IV + SCARED.
- Si MC = "deterioro cognitivo" + edad >55 → sugerir Yesavage + Lawton + Zarit.
- Reglas en `data/datosClinicos.js` (`DIAGNOSTIC_ALGORITHMS` ya tiene base).

---

## 🔵 Largo plazo — meses

### L-1. Refactor del Sidebar (4 grupos → 5 con "Aprender")
Del `ROADMAP_EXPANSION.md` §Cambios técnicos.

### L-2. Sistema de notificaciones in-app
- Hoy todo va a toasts efímeros.
- Nueva tabla `notifications` con bell-icon en el sidebar.
- Tipos: nueva sesión paciente, tarea-casa completada, riesgo activo, backup falló, etc.

### L-3. Multi-profesional / Multi-institución
- Hoy 1 usuario admin. Agregar:
  - Rol `psicologo`, `recepcion`, `coordinador`, `admin`.
  - Permisos granulares.
  - Filtros "mis pacientes" vs "todos".

### L-4. Sincronización en la nube opcional
- Modo offline-first (actual) + sync con servidor central cuando hay internet.
- Útil para clínicas pequeñas con 2-3 consultorios.

### L-5. App móvil para paciente (PWA)
- Tareas terapéuticas, registro de pensamientos diarios, recordatorios de cita, sesión por telepsicología.
- Acceso por código del paciente (sin contraseña, link mágico email/SMS).

### L-6. Marketplace de plantillas comunidad
- Profesionales suben plantillas de informe, escalas custom, casos clínicos.
- Calificación + descargas + reputación.
- Curado por equipo NeuroSoft.

### L-7. Integraciones EPS Colombia
- Generación automática de RIPS (Registro Individual de Prestación de Servicios) en XML.
- Integración con Pisis-EPS de Sanitas/Sura/etc. para envío directo.
- Hoy `RIPS` está en `D:\Archivo\...` pero no en el motor.

### L-8. Certificación ISO 27001 + cumplimiento Ley 1581 Colombia
- Cifrado en reposo de campos sensibles.
- Logs inmutables (ya parcialmente con audit_listeners).
- Política de retención automática.
- Export ARCO (Acceso, Rectificación, Cancelación, Oposición) automatizado.

---

## 🎓 Detalle expandido — Módulo académico de terapias (M-1)

### Vision
Hoy `TherapyPage` muestra una lista de 18 enfoques con info básica. La idea es que **cuando el clínico hace click en un enfoque** se abra un panel con todo lo que necesita para **aprender ese enfoque** o **refrescar su práctica**.

### Estructura del panel `EnfoqueDetalle.jsx`

```
┌─ Header con nombre + sigla + nivel de evidencia ────────┐
│ [Tab Resumen] [Cómo se aplica] [Técnicas] [Videos]      │
│ [Bibliografía] [Casos prácticos] [Recursos]             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  TAB RESUMEN                                             │
│  • Descripción extendida (200-300 palabras)              │
│  • Para qué condiciones funciona (con d/g effect size)   │
│  • Para qué NO funciona                                  │
│  • Duración típica + estructura                          │
│                                                          │
│  TAB CÓMO SE APLICA                                      │
│  • Fase 1 — Evaluación inicial (qué preguntar, qué      │
│    escalas aplicar, cómo formular el caso)              │
│  • Fase 2 — Psicoeducación (qué explicar al paciente)   │
│  • Fase 3 — Intervención activa (técnicas centrales)    │
│  • Fase 4 — Mantenimiento (prevención de recaídas)      │
│  • Fase 5 — Cierre (criterios de alta)                  │
│                                                          │
│  TAB TÉCNICAS                                            │
│  • Cada técnica: nombre, descripción, cuándo usar,      │
│    ejemplo de diálogo, ejercicio para casa              │
│  • Plantillas descargables (registros, hojas paciente)  │
│                                                          │
│  TAB VIDEOS                                              │
│  • YouTube embebidos de profesores reconocidos          │
│  • Aaron Beck — CBT fundamentals                        │
│  • Steven Hayes — ACT en español                        │
│  • Curado por NeuroSoft + comunidad                     │
│                                                          │
│  TAB BIBLIOGRAFÍA                                        │
│  • Libros fundacionales con ISBN                        │
│  • Manuales prácticos                                   │
│  • Papers seminales (DOI clickeable)                    │
│  • Guías clínicas (NICE, APA, Cochrane)                 │
│                                                          │
│  TAB CASOS PRÁCTICOS                                     │
│  • 2-3 vignettes clínicas anonimizadas                  │
│  • Para cada uno: MC, hipótesis, plan terapéutico       │
│    aplicado, evolución, criterios de alta usados        │
│                                                          │
│  TAB RECURSOS                                            │
│  • PDFs de registros (Tabla 3 columnas Beck, etc.)      │
│  • Worksheets para paciente                              │
│  • Audios de ejercicios (mindfulness, defusión ACT)     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Modelo de datos enriquecido

```js
// enfoquesTerapeuticos.js — campos nuevos opcionales
{
  id: "cbt", nombre, sigla, evidencia, indicaciones, ...,  // los actuales
  descripcion_extendida: "Texto largo de 200-300 palabras...",
  efecto_tamano: { depresion: 0.61, ansiedad: 0.73, ... },  // de meta-análisis
  fases_aplicacion: [
    {
      fase: 1, nombre: "Evaluación inicial",
      objetivos: ["Establecer alianza", "Formular caso"],
      tareas_clinico: ["Aplicar PHQ-9, GAD-7", "Mapa de problemas"],
      tareas_paciente: ["Registro inicial pensamientos 7 días"],
      duracion_sesiones: "1-2",
    },
    ...
  ],
  tecnicas_detalladas: [
    {
      id: "registro_pensamientos",
      nombre: "Registro de pensamientos automáticos",
      descripcion: "Identificar y desafiar pensamientos...",
      cuando_usar: "Cuando el paciente reporta sufrimiento sin causa clara",
      ejemplo_dialogo: "Cliente: 'Siempre fracaso'. T: '¿Qué pasó hoy que disparó ese pensamiento?'...",
      ejercicio_casa: "Registrar 3 pensamientos automáticos al día por 1 semana",
      plantilla_pdf: "/recursos/cbt/registro_pensamientos.pdf",
    },
    ...
  ],
  videos: [
    {
      titulo: "Aaron Beck — What is Cognitive Therapy?",
      url_youtube: "https://www.youtube.com/embed/abc123",
      autor: "Beck Institute",
      duracion: "12:34",
      idioma: "en",
    },
    ...
  ],
  bibliografia: [
    {
      tipo: "libro", titulo: "Cognitive Behavior Therapy: Basics and Beyond",
      autor: "Beck, J. S.", anio: 2021, edicion: 3, isbn: "978-1462544196",
    },
    {
      tipo: "paper", titulo: "The efficacy of cognitive behavioral therapy: a review of meta-analyses",
      autores: "Hofmann et al.", anio: 2012, doi: "10.1007/s10608-012-9476-1",
    },
    ...
  ],
  casos_practicos: [
    {
      titulo: "Mujer 28a — Trastorno de ansiedad generalizada",
      motivo_consulta: "Preocupación excesiva, insomnio, tensión muscular...",
      hipotesis: "TAG (CIE-10: F41.1). Vulnerabilidad cognitiva + estilo de afrontamiento evitativo.",
      plan_aplicado: ["10 sesiones CBT-TAG (Borkovec adaptado)", "Mindfulness 5/sem", "..."],
      evolucion: "Reducción GAD-7 de 17 a 6 al cierre",
      reflexion: "La clave fue trabajar primero el control de la preocupación antes que las creencias...",
    },
  ],
  recursos_descargables: [
    { titulo: "Registro de pensamientos automáticos (3 columnas)", url: "/recursos/cbt/registro_3col.pdf", tipo: "plantilla" },
    { titulo: "Hoja de psicoeducación: ¿qué es la CBT?", url: "/recursos/cbt/psicoeducacion.pdf", tipo: "paciente" },
    { titulo: "Audio: relajación muscular progresiva", url: "/recursos/cbt/relajacion_muscular.mp3", tipo: "audio" },
  ],
}
```

### Cómo se llena el contenido educativo

- **Enfoques top 5** (CBT, ACT, EMDR, Sistémica, Humanística): contenido completo en este sprint.
- **Resto de enfoques** (13 más): contenido extendido en sprints siguientes vía `/investigar-terapia`.
- **Vídeos**: solo embebidos de canales serios (Beck Institute, ACBS, EMDRIA, etc.) con permiso público de YouTube.
- **PDFs descargables**: hosted en `/app/assets/recursos_terapia/` (incluidos en el .exe vía PyInstaller).
- **Casos prácticos**: anonimizados, basados en casos reales del clínico.

---

## 🟣 Otros pendientes detectados

### Auditoría baremos (cerrada en este sprint)
- ✅ 97/102 baremos coinciden 100% con Excel original
- ✅ 1 bug corregido (AdFCRO_Rey edad 45)
- ✅ 10 tests Grober legacy eliminados
- ⏳ Auditar las 55 pruebas "solo motor" (escalas modernas) contra sus fuentes (MMSE, Yesavage, Beck, Lawton, Kertesz, INECO).

### Snapshots de los 15 casos clínicos como tests de regresión
- Usar `/snapshot-paciente` para cada caso de `CASOS_GROUND_TRUTH.md`.
- Generar 15 fixtures JSON en `tests/fixtures/casos_ground_truth/`.
- Tests `tests/integration/test_casos_ground_truth.py` que iteren los 15 y verifiquen los escalares esperados.

### CI/CD en GitHub Actions
- Hoy el proyecto vive en máquina local. Crear workflow:
  - Push → corre tests Python + lint frontend + Playwright e2e
  - Tag → build .exe + .iso + sube release

### Documentación pública (landing + tutoriales)
- Hoy README es técnico. Crear:
  - Landing simple (Netlify/Vercel) con qué es NeuroSoft.
  - Tutoriales en video corto (5 min cada uno) para cada feature.
  - Blog del clínico autor (artículos clínicos).

---

## Plan de ejecución sugerido (próximos 6 sprints)

| Sprint | Foco | Entregable |
|---|---|---|
| **1 (ESTE)** | Quick wins informes + módulo académico CBT/ACT/EMDR | Carpeta+email+imprimir + EnfoqueDetalle.jsx con 3 enfoques |
| 2 | Configuración SMTP + plantillas email | Tab Comunicaciones funcional |
| 3 | Riesgo suicida C-SSRS + banner persistente | Sistema crítico activo |
| 4 | Marcador completitud informe + bandeja escalas sugeridas | UX guiado |
| 5 | Orden clínico evaluación + acompañante entidad | Refinamiento flujo HC |
| 6 | Auditar 55 pruebas "solo motor" + snapshots ground truth en CI | Cobertura cerrada |

---

## Reglas de implementación

1. **Cada feature nuevo requiere test**: unitario (backend) o e2e (frontend) o ambos.
2. **Cada cambio en motor requiere correr los 302 tests** antes de commit.
3. **NUNCA tocar `BD_NEURO_MAESTRA.json`** sin auditar contra Excel + fuente clínica.
4. **`build-mayra` antes de cada release** beta.
5. **`checkpoint` antes de refactor grande**.
