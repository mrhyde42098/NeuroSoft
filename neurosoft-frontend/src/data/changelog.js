/* ═══════════════════════════════════════════════════════════════════════
 * src/data/changelog.js
 * ───────────────────────────────────────────────────────────────────────
 * Registro de cambios de NeuroSoft App.
 *
 * Cada entrada tiene:
 *   version   — número de versión (semántico: mayor.menor.parche)
 *   fecha     — ISO date de publicación
 *   titulo    — resumen de 1 línea
 *   cambios   — array de strings (cada uno es un bullet)
 *   icono     — material symbol name para la tarjeta
 *   color     — color del acento (hex)
 *
 * CUANDO AGREGUES UNA NUEVA VERSIÓN:
 *   1. Agrega la entrada al principio del array
 *   2. Actualiza `api_version` en `neurosoft-backend/app/core/config.py`
 *   3. Build normal — la app detecta el cambio localmente al arrancar
 * ═══════════════════════════════════════════════════════════════════════ */

export const CHANGELOG = [
  {
    version: "2.0.1",
    fecha: "2026-06-07",
    titulo: "Alineación API y agenda mensual",
    icono: "sync",
    color: "#0D9488",
    cambios: [
      "Sesiones de terapia: al editar se guardan modalidad y duración (antes se perdían al guardar).",
      "Backup manual: las notas del formulario se envían correctamente al servidor.",
      "Agenda: la vista mensual carga todas las citas del mes (no solo la semana en curso).",
      "Agenda: las citas nuevas quedan asignadas al profesional autenticado.",
    ],
  },
  {
    version: "2.0.0",
    fecha: "2026-05-31",
    titulo: "Estabilidad clínica y calidad de producción",
    icono: "verified",
    color: "#0D9488",
    cambios: [
      "Motor de baremos: 175 pruebas neuropsicológicas con 98% de cobertura en tests automáticos (725 tests).",
      "Corrección de bug crítico en ZScoreMultipleStrategy: sigma=0 ya no produce falso positivo clínico.",
      "Auditoría completa de código: 210 archivos revisados, 2 bugs críticos corregidos, 5 bugs altos resueltos.",
      "Protección de localStorage: migración a safeLS en 14 archivos. La app ya no crashea en modo privado del navegador.",
      "Snapshots pre-migración: copia automática de la BD antes de cualquier cambio de schema. Máximo 10 retenidos.",
      "Error tracking: el ErrorBoundary ahora envía crash reports al backend para diagnóstico remoto.",
      "Código preparado para firma digital (NEUROSOFT_CODE_SIGN_IDENTITY). Elimina advertencia de Windows Defender.",
      "Limpieza de 31 archivos huérfanos: scripts de investigación, logs temporales, cachés de build.",
      "Interfaz mejorada en Evaluación: nombres de tests legibles (no códigos), textos más grandes, sin duplicados.",
      "Nuevo endpoint GET /health con BD, baremos, espacio en disco, uptime y métricas.",
      "Benchmark del motor: 29,267 evaluaciones por segundo. 1000 pacientes en 160ms.",
    ],
  },
  {
    version: "1.9.0",
    fecha: "2026-05-21",
    titulo: "Módulo Aprender, Simulador y tests GADS/CDI",
    icono: "school",
    color: "#7c3aed",
    cambios: [
      "Módulo Aprender (Pilar 3 educativo): Glosario 150 términos, tarjetas de repaso espaciado (5 niveles), Quiz, Artículos, Biblioteca.",
      "Simulador de casos clínicos con 3 vignettes reales (TDAH, Alzheimer, Depresión postparto) y perfiles del motor.",
      "11 tests nuevos para GADS-CTAs y NiCDI. Bug corregido: PuntajeDoblResultadoStrategy ahora busca claves CTAS/T/PE.",
      "Glosario tooltips en EvalResultsPage e InformesPage (ICV, IRP, IMT, IVP, CIT, ICG).",
      "15 fixtures ground truth con verificación automática de 134 escalares clínicos.",
      "Enriquecimiento de 13 enfoques terapéuticos (DBT, MBCT, TF-CBT, IPT, Esquemas, Gottman, EFT, etc.).",
      "Telepsicología básica: link Jitsi por sesión, botón copiar, aviso Ley 1090.",
    ],
  },
  {
    version: "1.8.0",
    fecha: "2026-05-15",
    titulo: "Sprint Quick Wins — informes, terapia, acompañantes",
    icono: "description",
    color: "#2563eb",
    cambios: [
      "Informes: botones Imprimir, Guardar como, Enviar correo + modal email completo.",
      "Indicador de completitud por sección + bloqueos visibles en InformesPage.",
      "Config SMTP UI en ConfigPage (pestaña Comunicaciones). Password cifrada con Fernet.",
      "6 plantillas de email editables (informe, remisión, evolución, RIPS, recordatorio, otro).",
      "PDF de Historia Clínica sola (sin evaluación). Botón 'Imprimir HC' en ClinicalHistoryPage.",
      "APScheduler: recordatorios automáticos de citas a las 18:00.",
      "Módulo académico de terapias: EnfoqueDetalle con 7 tabs para CBT, ACT, EMDR.",
      "C-SSRS riesgo suicida: form completo + cálculo automático + plan de seguridad + banner persistente.",
      "Orden clínico de evaluación: banner con siguiente prueba recomendada + timer de recobro (≥20 min).",
      "Acompañantes como entidad: CompanionORM + CRUD + autorizaciones (escalas proxy, recordatorios).",
      "Bandeja de escalas sugeridas: 14 reglas data-driven (MC + edad + población → SNAP-IV, PHQ-9, etc.).",
      "Auditoría Excel vs Motor: 97/102 tests con match 100%. 10 Grober legacy eliminados.",
    ],
  },
  {
    version: "1.7.0",
    fecha: "2026-05-01",
    titulo: "Motor clínico, migraciones y seguridad",
    icono: "psychology",
    color: "#0891b2",
    cambios: [
      "Motor de calificación clínica con 15 estrategias de scoring neuropsicológico.",
      "Carga de BD_NEURO_MAESTRA.json (168 pruebas, 112,643 claves de baremo) en memoria.",
      "Soporte para baremos colombianos Neuronorma (Arango-Lasprilla & Rivera, 2017).",
      "Ajuste de escolaridad para Adulto Mayor (Analfabeta/Prim.Inc → +N al PD).",
      "WISC-IV Colombia: cálculo de CI compuestos (ICV, IRP, IMT, IVP, CIT) + ICG + ICC.",
      "6 migraciones Alembic: schema inicial → row_version → archive → acompañantes → therapy_tasks → ai_logs.",
      "JWT con verify_exp explícito. Rate limiting por IP. Security headers (X-Content-Type, HSTS, etc.).",
      "Audit log listeners sobre Session ORM (trazabilidad Resolución 1995).",
      "PII redactor en logs. Token blacklist para logout real.",
      "6 variantes de informe PDF: estándar, pro, pediátrico, medicolegal, junta médica, inconcluso.",
      "15 actividades de rehabilitación cognitiva (Stroop, N-Back, CPT, Go/No-Go, Torre de Londres, etc.).",
    ],
  },
];

/** Obtiene la entrada más reciente del changelog. */
export const latestVersion = () => CHANGELOG[0];

/** Busca una entrada por número de versión. */
export const getVersion = (v) => CHANGELOG.find((c) => c.version === v) || null;
