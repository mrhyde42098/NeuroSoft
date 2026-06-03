/* ═══════════════════════════════════════════════════════════════════════
 * plantillasDocumentales.js — Plantillas documentales NeuroSoft
 * ───────────────────────────────────────────────────────────────────────
 * S2.2 del PLAN_MAESTRO: 12 plantillas documentales para uso clínico
 * cotidiano. Todas referencian la legislación colombiana vigente y
 * están redactadas en español neutro.
 *
 * Plantillas:
 *   1.  Consentimiento informado evaluación neuropsicológica
 *   2.  Consentimiento informado telepsicología
 *   3.  Asentimiento informado menores de edad
 *   4.  Informe neuropsicológico (estructura)
 *   5.  Remisión a psiquiatría
 *   6.  Remisión a neurología
 *   7.  Evolución de sesión de terapia
 *   8.  RIPS de atención
 *   9.  Recordatorio de cita
 *   10. Solicitud de historia clínica anterior
 *   11. Carta a colegio / institución educativa
 *   12. Informe pericial (medicolegal)
 *   13. Contrato de servicios profesionales
 *   14. Factura electrónica de venta (Res. 000042/2020 DIAN)
 *   15. Aviso de privacidad (Ley 1581/2012 + Decreto 1377/2013)
 *   16. Bitácora de acceso / auditoría clínica
 *   17. Consentimiento específico para uso de IA
 *
 * Las plantillas son OBJETOS con:
 *   - id: identificador único
 *   - titulo: nombre visible
 *   - categoria: 'consent' | 'informe' | 'remision' | 'evolucion' | 'rips' | 'carta' | 'factura' | 'aviso' | 'contrato'
 *   - marcoLegal: leyes/decretos que sustentan
 *   - version: número de versión semántica (MAJOR.MINOR)
 *   - fechaVigencia: fecha a partir de la cual está vigente
 *   - caducidad: meses tras los que debe revalidarse (o null)
 *   - secciones[]: array de secciones con placeholder
 *   - variables: nombres de las variables que el clínico debe llenar
 *   - audiencia: 'paciente' | 'profesional' | 'institucion' | 'mixto'
 *   - bloqueLegal: bloque fijo que se incluye al pie (Normograma Colombiano)
 *
 * Uso:
 *   import { PLANTILLAS, renderPlantilla, plantillaPorId } from './plantillasDocumentales';
 *   const html = renderPlantilla(plantillaPorId('consent_evaluacion'), {
 *     paciente_nombre: 'Juan Pérez', fecha: '2026-06-01', ...
 *   });
 *
 * Autor: NeuroSoft — 2026
 * ═══════════════════════════════════════════════════════════════════════ */

/* Bloque legal común al pie de cada documento.
 * Lista exhaustiva del marco normativo colombiano aplicable a la práctica
 * clínica psicológica y a la historia clínica. Sirve como recordatorio
 * continuo del cumplimiento. */
const BLOQUE_LEGAL_NORMOGRAMA = `— Normograma Colombiano aplicable —
Constitución Política de Colombia, arts. 15 y 20 (Habeas Data y libertad de expresión).
Ley 1090 de 2006 — Código Deontológico del Psicólogo.
Ley 1581 de 2012 — Protección de datos personales.
Ley 1616 de 2013 — Salud Mental.
Ley 1751 de 2015 — Estatutaria de la Salud.
Ley 1098 de 2006 — Código de la Infancia y la Adolescencia.
Resolución 1995 de 1999 — Manejo de la Historia Clínica.
Resolución 1441 de 2013 — Lineamientos del Plan Nacional de Salud Mental.
Resolución 2654 de 2019 — Telemedicina y telepsicología.
Resolución 2275 de 2023 — RIPS y reporte de atenciones en salud mental.
Resolución 000042 de 2020 (DIAN) — Factura electrónica.
Decreto 1377 de 2013 — Reglamentación parcial de Ley 1581/2012.
Decreto 780 de 2016 — Decreto Único Reglamentario del Sector Salud.
Decreto 1074 de 2015 — Único Reglamentario del Sector Comercio, Industria y Turismo.
Decreto 1081 de 2015 — Único del Sector de la Presidencia (publicaciones).
Decisión 486 de 2000 (CAN) — Régimen Común sobre Propiedad Intelectual.
Tratados OMPI (WIPO) — Derecho de autor.
— Fin del Normograma —`;

/* Versión de Normograma: si se actualiza, todos los documentos
 * generados deben regirse por la nueva versión. */
const NORMOGRAMA_VERSION = "2026.06";

/* ── 1. Consentimiento informado evaluación neuropsicológica ──────────── */
const PLANTILLA_CONSENT_EVALUACION = {
  id: "consent_evaluacion",
  titulo: "Consentimiento informado — Evaluación neuropsicológica",
  categoria: "consent",
  audiencia: "paciente",
  version: "2.1.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: [
    "Ley 1581/2012 (Habeas Data)",
    "Ley 1090/2006 (Código Deontológico)",
    "Resolución 1995/1999 (Historia clínica)",
  ],
  variables: [
    "paciente_nombre", "paciente_documento", "fecha", "profesional_nombre",
    "profesional_registro", "institucion_nombre", "tipo_evaluacion",
    "pruebas_a_aplicar", "duracion_estimada", "acudiente_nombre",
  ],
  secciones: [
    {
      titulo: "Información al paciente",
      cuerpo: `Yo, {{paciente_nombre}}, identificado con {{paciente_documento}},
declaro haber sido informado/a de manera clara y comprensible sobre la
evaluación neuropsicológica que se me va a realizar.`,
    },
    {
      titulo: "Objetivo de la evaluación",
      cuerpo: `El objetivo es obtener información sobre mi funcionamiento
cognitivo, emocional y conductual a través de {{tipo_evaluacion}}, con
aplicación de {{pruebas_a_aplicar}}. La duración estimada es de
{{duracion_estimada}}.`,
    },
    {
      titulo: "Procedimiento",
      cuerpo: `Se me aplicarán pruebas estandarizadas (cuestionarios,
entrevistas, tareas cognitivas) y se podrán incluir sesiones de
observación clínica. La información obtenida será registrada en mi
historia clínica conforme a la Resolución 1995 de 1999.`,
    },
    {
      titulo: "Confidencialidad y manejo de datos",
      cuerpo: `La información obtenida es confidencial y sólo será
compartida con terceros con mi autorización expresa o por requerimiento
legal. Mis datos serán tratados conforme a la Ley 1581 de 2012
(Habeas Data) y puedo ejercer mis derechos de acceso, rectificación y
supresión en cualquier momento.`,
    },
    {
      titulo: "Beneficios y riesgos",
      cuerpo: `El beneficio esperado es contar con un perfil claro de
mi funcionamiento que oriente decisiones clínicas, académicas o
laborales. Los riesgos son mínimos (fatiga, frustración ante tareas
complejas). Puedo suspender la evaluación en cualquier momento sin
consecuencia alguna.`,
    },
    {
      titulo: "Derecho a negarse",
      cuerpo: `Tengo derecho a rehusar la evaluación, a no responder
preguntas específicas o a interrumpir cualquier procedimiento si así
lo deseo.`,
    },
    {
      titulo: "Declaración y firma",
      cuerpo: `Firmo este documento libre y voluntariamente,
manifestando que he comprendido la información proporcionada y he
tenido la oportunidad de hacer preguntas.

Paciente: {{paciente_nombre}}
C.C.: {{paciente_documento}}
Fecha: {{fecha}}

Profesional: {{profesional_nombre}}
Registro: {{profesional_registro}}
Institución: {{institucion_nombre}}`,
    },
  ],
};

/* ── 2. Consentimiento telepsicología ──────────────────────────────────── */
const PLANTILLA_CONSENT_TELE = {
  id: "consent_telepsicologia",
  titulo: "Consentimiento informado — Telepsicología",
  categoria: "consent",
  audiencia: "paciente",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: [
    "Ley 1090/2006",
    "Ley 1581/2012",
    "Resolución 2654/2019 (Telemedicina)",
  ],
  variables: ["paciente_nombre", "paciente_documento", "fecha",
              "plataforma", "profesional_nombre", "profesional_registro",
              "acudiente_nombre"],
  secciones: [
    {
      titulo: "Modalidad de atención",
      cuerpo: `Autorizo la atención psicológica en modalidad de
telepsicología (videollamada) a través de {{plataforma}}, con el
profesional {{profesional_nombre}} (Registro {{profesional_registro}}).`,
    },
    {
      titulo: "Limitaciones de la modalidad",
      cuerpo: `Entiendo que la telepsicología tiene limitaciones:
conexión a internet inestable, dificultad para observar lenguaje
corporal completo, y respuesta limitada ante emergencias agudas. En
caso de crisis, debo comunicarme a las líneas de emergencia 123 o
acudir al servicio de urgencias más cercano.`,
    },
    {
      titulo: "Seguridad y privacidad",
      cuerpo: `Me comprometo a realizar la sesión desde un lugar
privado, sin terceros presentes salvo menores con su acudiente. No
grabaré la sesión sin autorización escrita. La plataforma cumple
estándares de cifrado.`,
    },
    {
      titulo: "Consentimiento expreso",
      cuerpo: `Firmo libre y voluntariamente, manifestando que
comprendo las condiciones y limitaciones de la telepsicología.

Paciente: {{paciente_nombre}}
C.C.: {{paciente_documento}}
Fecha: {{fecha}}
Acudiente (si aplica): {{acudiente_nombre}}`,
    },
  ],
};

/* ── 3. Asentimiento informado menores ────────────────────────────────── */
const PLANTILLA_ASENTIMIENTO_MENOR = {
  id: "asentimiento_menor",
  titulo: "Asentimiento informado — Menor de edad",
  categoria: "consent",
  audiencia: "mixto",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1098/2006 (Código Infancia)", "Ley 1090/2006"],
  variables: ["menor_nombre", "menor_edad", "acudiente_nombre",
              "acudiente_documento", "parentesco", "fecha",
              "profesional_nombre"],
  secciones: [
    {
      titulo: "Explicación adaptada al menor",
      cuerpo: `Hola, soy {{profesional_nombre}}, psicólogo/a. Vamos a
hacer algunas actividades como juegos, dibujos y preguntas para
conocer cómo piensas y aprendes. No hay respuestas malas. Si algo
no te gusta o quieres parar, me lo dices y paramos.`,
    },
    {
      titulo: "Autorización del acudiente",
      cuerpo: `Yo {{acudiente_nombre}}, identificado con
{{acudiente_documento}}, en calidad de {{parentesco}} del menor
{{menor_nombre}} ({{menor_edad}} años), autorizo su participación
voluntaria en la evaluación, libre de coercion.`,
    },
    {
      titulo: "Firmas",
      cuerpo: `Acudiente: {{acudiente_nombre}}
C.C.: {{acudiente_documento}}
Fecha: {{fecha}}

Menor (asentimiento verbal o firma): {{menor_nombre}}
Profesional: {{profesional_nombre}}`,
    },
  ],
};

/* ── 4. Informe neuropsicológico (estructura) ─────────────────────────── */
const PLANTILLA_INFORME = {
  id: "informe_neuropsicologico",
  titulo: "Informe neuropsicológico (estructura)",
  categoria: "informe",
  audiencia: "profesional",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1090/2006", "Res. 1995/1999"],
  variables: ["paciente_nombre", "paciente_documento", "edad", "escolaridad",
              "motivo_consulta", "fecha_evaluacion", "pruebas_aplicadas",
              "observaciones_generales", "resultados", "impresion_diagnostica",
              "recomendaciones", "profesional_nombre", "profesional_registro"],
  secciones: [
    {
      titulo: "Datos de identificación",
      cuerpo: `Paciente: {{paciente_nombre}}
Documento: {{paciente_documento}}
Edad: {{edad}}
Escolaridad: {{escolaridad}}`,
    },
    {
      titulo: "Motivo de consulta",
      cuerpo: `{{motivo_consulta}}`,
    },
    {
      titulo: "Procedimiento",
      cuerpo: `Evaluación realizada el {{fecha_evaluacion}}. Se
aplicaron las siguientes pruebas: {{pruebas_aplicadas}}.

Observaciones generales: {{observaciones_generales}}`,
    },
    {
      titulo: "Resultados",
      cuerpo: `{{resultados}}`,
    },
    {
      titulo: "Impresión diagnóstica",
      cuerpo: `{{impresion_diagnostica}}

Nota: Este informe se basa en los hallazgos de la evaluación
neuropsicológica realizada y NO constituye un diagnóstico
psiquiátrico formal. Cualquier impresión diagnóstica es orientativa
y debe ser corroborada por el profesional tratante según los
criterios DSM-5-TR / CIE-10.`,
    },
    {
      titulo: "Recomendaciones",
      cuerpo: `{{recomendaciones}}`,
    },
    {
      titulo: "Firma y responsabilidad profesional",
      cuerpo: `Este informe es emitido bajo la responsabilidad
profesional del psicólogo firmante, conforme al artículo 36 de la
Ley 1090 de 2006.

Profesional: {{profesional_nombre}}
Registro: {{profesional_registro}}`,
    },
  ],
};

/* ── 5. Remisión a psiquiatría ─────────────────────────────────────────── */
const PLANTILLA_REMISION_PSIQUIATRIA = {
  id: "remision_psiquiatria",
  titulo: "Remisión a psiquiatría",
  categoria: "remision",
  audiencia: "profesional",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1616/2013"],
  variables: ["paciente_nombre", "paciente_documento", "edad", "motivo_remision",
              "hallazgos_relevantes", "tratamiento_actual", "profesional_nombre",
              "profesional_registro", "fecha"],
  secciones: [
    {
      titulo: "Datos del paciente",
      cuerpo: `Paciente: {{paciente_nombre}}
Documento: {{paciente_documento}}
Edad: {{edad}}`,
    },
    {
      titulo: "Motivo de remisión",
      cuerpo: `{{motivo_remision}}`,
    },
    {
      titulo: "Hallazgos neuropsicológicos relevantes",
      cuerpo: `{{hallazgos_relevantes}}`,
    },
    {
      titulo: "Tratamiento actual",
      cuerpo: `{{tratamiento_actual}}`,
    },
    {
      titulo: "Firma",
      cuerpo: `Profesional remitente: {{profesional_nombre}}
Registro: {{profesional_registro}}
Fecha: {{fecha}}`,
    },
  ],
};

/* ── 6. Remisión a neurología ──────────────────────────────────────────── */
const PLANTILLA_REMISION_NEUROLOGIA = {
  id: "remision_neurologia",
  titulo: "Remisión a neurología",
  categoria: "remision",
  audiencia: "profesional",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1616/2013"],
  variables: ["paciente_nombre", "paciente_documento", "edad", "motivo_remision",
              "hallazgos_neuropsicologicos", "antecedentes_relevantes",
              "profesional_nombre", "profesional_registro", "fecha"],
  secciones: [
    {
      titulo: "Datos del paciente",
      cuerpo: `Paciente: {{paciente_nombre}}
Documento: {{paciente_documento}}
Edad: {{edad}}`,
    },
    {
      titulo: "Motivo de remisión",
      cuerpo: `{{motivo_remision}}`,
    },
    {
      titulo: "Hallazgos neuropsicológicos",
      cuerpo: `{{hallazgos_neuropsicologicos}}`,
    },
    {
      titulo: "Antecedentes relevantes",
      cuerpo: `{{antecedentes_relevantes}}`,
    },
    {
      titulo: "Firma",
      cuerpo: `Profesional: {{profesional_nombre}}
Registro: {{profesional_registro}}
Fecha: {{fecha}}`,
    },
  ],
};

/* ── 7. Evolución de sesión de terapia ─────────────────────────────────── */
const PLANTILLA_EVOLUCION = {
  id: "evolucion_sesion",
  titulo: "Evolución de sesión de terapia",
  categoria: "evolucion",
  audiencia: "profesional",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1090/2006", "Res. 1995/1999"],
  variables: ["paciente_nombre", "numero_sesion", "fecha", "objetivos_sesion",
              "intervenciones", "respuesta_paciente", "tareas_asignadas",
              "plan_proxima_sesion", "profesional_nombre"],
  secciones: [
    {
      titulo: "Datos de la sesión",
      cuerpo: `Paciente: {{paciente_nombre}}
Sesión N°: {{numero_sesion}}
Fecha: {{fecha}}`,
    },
    {
      titulo: "Objetivos de la sesión",
      cuerpo: `{{objetivos_sesion}}`,
    },
    {
      titulo: "Intervenciones realizadas",
      cuerpo: `{{intervenciones}}`,
    },
    {
      titulo: "Respuesta del paciente",
      cuerpo: `{{respuesta_paciente}}`,
    },
    {
      titulo: "Tareas asignadas",
      cuerpo: `{{tareas_asignadas}}`,
    },
    {
      titulo: "Plan próxima sesión",
      cuerpo: `{{plan_proxima_sesion}}`,
    },
    {
      titulo: "Firma",
      cuerpo: `Profesional: {{profesional_nombre}}`,
    },
  ],
};

/* ── 8. RIPS de atención ──────────────────────────────────────────────── */
const PLANTILLA_RIPS = {
  id: "rips_atencion",
  titulo: "RIPS de atención (resumen)",
  categoria: "rips",
  audiencia: "institucion",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Resolución 3374/2000", "Resolución 1531/2023"],
  variables: ["paciente_nombre", "paciente_documento", "tipo_documento",
              "fecha_atencion", "codigo_rips", "cups", "finalidad_consulta",
              "diagnostico_principal", "profesional_nombre"],
  secciones: [
    {
      titulo: "Datos del paciente",
      cuerpo: `Nombre: {{paciente_nombre}}
Documento: {{tipo_documento}} {{paciente_documento}}`,
    },
    {
      titulo: "Datos de la atención",
      cuerpo: `Fecha: {{fecha_atencion}}
Código RIPS: {{codigo_rips}}
CUPS: {{cups}}
Finalidad: {{finalidad_consulta}}
Diagnóstico principal: {{diagnostico_principal}}`,
    },
    {
      titulo: "Profesional",
      cuerpo: `{{profesional_nombre}}`,
    },
  ],
};

/* ── 9. Recordatorio de cita ───────────────────────────────────────────── */
const PLANTILLA_RECORDATORIO = {
  id: "recordatorio_cita",
  titulo: "Recordatorio de cita",
  categoria: "carta",
  audiencia: "paciente",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1581/2012"],
  variables: ["paciente_nombre", "fecha_cita", "hora_cita", "lugar",
              "profesional_nombre", "institucion_nombre", "contacto_telefono"],
  secciones: [
    {
      titulo: "Recordatorio",
      cuerpo: `Estimado/a {{paciente_nombre}},

Le recordamos su cita programada para el día {{fecha_cita}} a las
{{hora_cita}}, en {{lugar}}, con {{profesional_nombre}}.

En caso de no poder asistir, le solicitamos cancelar con al menos
24 horas de anticipación llamando al {{contacto_telefono}}.

{{institucion_nombre}}`,
    },
  ],
};

/* ── 10. Solicitud historia clínica anterior ──────────────────────────── */
const PLANTILLA_SOLICITUD_HC = {
  id: "solicitud_hc_anterior",
  titulo: "Solicitud de historia clínica anterior",
  categoria: "carta",
  audiencia: "institucion",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1581/2012", "Res. 1995/1999"],
  variables: ["paciente_nombre", "paciente_documento", "institucion_destino",
              "profesional_destino", "motivo_solicitud", "profesional_solicitante",
              "profesional_registro", "fecha"],
  secciones: [
    {
      titulo: "Cuerpo de la solicitud",
      cuerpo: `{{institucion_destino}}
{{profesional_destino}}

Asunto: Solicitud de historia clínica

Por medio de la presente, yo {{profesional_solicitante}}, con registro
{{profesional_registro}}, solicito copia de la historia clínica del
paciente {{paciente_nombre}} (C.C. {{paciente_documento}}) con el fin
de:

{{motivo_solicitud}}

El paciente ha sido informado y autoriza la entrega de esta
información conforme a la Ley 1581 de 2012.

Cordialmente,
{{profesional_solicitante}}
Fecha: {{fecha}}`,
    },
  ],
};

/* ── 11. Carta a institución educativa ────────────────────────────────── */
const PLANTILLA_CARTA_COLEGIO = {
  id: "carta_colegio",
  titulo: "Carta a institución educativa",
  categoria: "carta",
  audiencia: "institucion",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1090/2006", "Ley 1581/2012"],
  variables: ["colegio_nombre", "docente_nombre", "paciente_nombre",
              "paciente_edad", "grado", "hallazgos_resumidos",
              "recomendaciones_escolares", "profesional_nombre",
              "profesional_registro", "fecha"],
  secciones: [
    {
      titulo: "Cuerpo de la carta",
      cuerpo: `{{colegio_nombre}}
Atn: {{docente_nombre}}

Asunto: Información sobre el proceso neuropsicológico del estudiante {{paciente_nombre}}

Estimados docentes,

El estudiante {{paciente_nombre}} ({{paciente_edad}} años, {{grado}})
ha sido valorado neuropsicológicamente. Comparto a continuación
hallazgos y recomendaciones generales para el contexto escolar:

Hallazgos resumidos:
{{hallazgos_resumidos}}

Recomendaciones escolares:
{{recomendaciones_escolares}}

Quedo atento a una reunión de articulación si se requiere.
{{profesional_nombre}}
Registro: {{profesional_registro}}
Fecha: {{fecha}}

Nota: Este documento se emite con autorización escrita del
acudiente del menor.`,
    },
  ],
};

/* ── 12. Informe pericial / medicolegal ────────────────────────────────── */
const PLANTILLA_PERICIAL = {
  id: "informe_pericial",
  titulo: "Informe pericial neuropsicológico (medicolegal)",
  categoria: "informe",
  audiencia: "mixto",
  version: "1.2.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  bloqueLegal: BLOQUE_LEGAL_NORMOGRAMA,
  marcoLegal: ["Ley 1090/2006", "Ley 906/2004 (C.P.P.)",
               "Res. 1995/1999", "Ley 1581/2012"],
  variables: ["caso_referencia", "autoridad_solicitante", "paciente_nombre",
              "paciente_documento", "edad", "escolaridad", "fecha_solicitud",
              "fecha_evaluacion", "preguntas_por_resolver", "metodologia",
              "resultados", "conclusiones", "alcance_informe",
              "profesional_nombre", "profesional_registro", "profesional_tarjeta"],
  secciones: [
    {
      titulo: "Identificación del dictamen",
      cuerpo: `Caso: {{caso_referencia}}
Autoridad solicitante: {{autoridad_solicitante}}
Fecha de solicitud: {{fecha_solicitud}}
Fecha de evaluación: {{fecha_evaluacion}}`,
    },
    {
      titulo: "Identificación del evaluado",
      cuerpo: `Paciente: {{paciente_nombre}}
Documento: {{paciente_documento}}
Edad: {{edad}}
Escolaridad: {{escolaridad}}`,
    },
    {
      titulo: "Preguntas por resolver",
      cuerpo: `{{preguntas_por_resolver}}`,
    },
    {
      titulo: "Metodología",
      cuerpo: `{{metodologia}}

Se siguieron los protocolos clínicos de aplicación y calificación
según manuales actualizados al 2024. Se aplicaron técnicas de
control de validez de síntomas.`,
    },
    {
      titulo: "Resultados",
      cuerpo: `{{resultados}}`,
    },
    {
      titulo: "Conclusiones",
      cuerpo: `{{conclusiones}}`,
    },
    {
      titulo: "Alcance y limitaciones del informe",
      cuerpo: `{{alcance_informe}}

El presente dictamen se emite bajo los principios de independencia
profesional, objetividad y rigor técnico, conforme al artículo 36
de la Ley 1090 de 2006.`,
    },
    {
      titulo: "Firma del perito",
      cuerpo: `Perito: {{profesional_nombre}}
Registro: {{profesional_registro}}
Tarjeta profesional: {{profesional_tarjeta}}

Declaro bajo juramento que la información contenida en este
informe es veraz y corresponde a mi leal saber y entender.`,
    },
  ],
};

/* ── 13. Contrato de servicios profesionales ───────────────────────────── */
const PLANTILLA_CONTRATO = {
  id: "contrato_servicios",
  titulo: "Contrato de servicios profesionales de psicología",
  categoria: "contrato",
  audiencia: "paciente",
  version: "1.0.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  marcoLegal: [
    "Código Civil Colombiano (arts. 1602-1617)",
    "Código de Comercio",
    "Ley 1090/2006 (Código Deontológico)",
    "Ley 1581/2012",
    "Estatuto Tributario (art. 437, 476 y ss.)",
  ],
  variables: [
    "contratante_nombre", "contratante_documento", "contratante_direccion",
    "contratante_telefono", "profesional_nombre", "profesional_documento",
    "profesional_tarjeta", "profesional_registro", "profesional_direccion",
    "objeto_contrato", "modalidad", "numero_sesiones", "valor_sesion",
    "valor_total", "periodicidad_pago", "lugar_atencion", "fecha_inicio",
    "fecha_terminacion", "ciudad", "fecha_firma",
  ],
  secciones: [
    {
      titulo: "Identificación de las partes",
      cuerpo: `EL/LA CONTRATANTE: {{contratante_nombre}}, identificado/a con
{{contratante_documento}}, con domicilio en {{contratante_direccion}},
teléfono {{contratante_telefono}}, en adelante "EL/LA CONTRATANTE".

EL/LA PROFESIONAL: {{profesional_nombre}}, identificado/a con
{{profesional_documento}}, Tarjeta Profesional N° {{profesional_tarjeta}},
Registro de salud {{profesional_registro}}, con domicilio profesional en
{{profesional_direccion}}, en adelante "EL/LA PROFESIONAL".`,
    },
    {
      titulo: "Objeto del contrato",
      cuerpo: `EL/LA PROFESIONAL se obliga a prestar a EL/LA CONTRATANTE
servicios profesionales de psicología consistentes en: {{objeto_contrato}},
en modalidad {{modalidad}}, con un total de {{numero_sesiones}} sesiones.`,
    },
    {
      titulo: "Valor y forma de pago",
      cuerpo: `El valor de cada sesión es de {{valor_sesion}}, para un
total de {{valor_total}}. La periodicidad de pago es
{{periodicidad_pago}}.`,
    },
    {
      titulo: "Lugar y fecha de inicio",
      cuerpo: `Las sesiones se realizarán en {{lugar_atencion}}, en la
ciudad de {{ciudad}}, iniciando el {{fecha_inicio}} y finalizando el
{{fecha_terminacion}} (prorrogable por mutuo acuerdo).`,
    },
    {
      titulo: "Confidencialidad y datos personales",
      cuerpo: `Toda la información derivada de la atención es
estrictamente confidencial y se manejará conforme a la Ley 1090 de 2006
y la Ley 1581 de 2012. La historia clínica se conservará por un mínimo
de quince (15) años conforme a la Resolución 1995 de 1999.`,
    },
    {
      titulo: "Derechos y deberes",
      cuerpo: `EL/LA CONTRATANTE puede desistir del servicio en cualquier
momento, sin penalidad, dando aviso con al menos 24 horas de
anticipación. En caso de fuerza mayor o caso fortuito, las partes
podrán renegociar fechas sin penalidad.`,
    },
    {
      titulo: "Solución de controversias",
      cuerpo: `Las controversias derivadas de este contrato se resolverán
en primera instancia por arreglo directo. En caso de persistir, se
acudirá a los mecanismos alternativos de solución de conflictos o a la
jurisdicción ordinaria en {{ciudad}}.`,
    },
    {
      titulo: "Firmas",
      cuerpo: `En señal de conformidad, firman en {{ciudad}}, el día
{{fecha_firma}}:

EL/LA CONTRATANTE: ________________________
C.C.: {{contratante_documento}}

EL/LA PROFESIONAL: ________________________
C.C.: {{profesional_documento}}
T.P.: {{profesional_tarjeta}}`,
    },
  ],
};

/* ── 14. Factura electrónica de venta (Res. 000042/2020 DIAN) ─────────── */
const PLANTILLA_FACTURA = {
  id: "factura_electronica",
  titulo: "Factura electrónica de venta — Servicios de psicología",
  categoria: "factura",
  audiencia: "institucion",
  version: "1.0.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: null,
  tarjetaProfesionalRequerida: true,
  marcoLegal: [
    "Resolución DIAN 000042 de 2020",
    "Estatuto Tributario (art. 615, 616-1, 617)",
    "Decreto 1625 de 2016 (Unico Tributario)",
    "Ley 2277 de 2022 (Reforma Tributaria)",
  ],
  variables: [
    "numero_factura", "prefijo", "fecha_emision", "fecha_vencimiento",
    "vendedor_nombre", "vendedor_nit", "vendedor_direccion", "vendedor_telefono",
    "comprador_nombre", "comprador_nit", "comprador_direccion",
    "comprador_telefono", "descripcion_servicio", "cantidad", "valor_unitario",
    "valor_total", "valor_iva", "valor_retefuente", "valor_a_pagar",
    "forma_pago", "medio_pago", "cufe", "fecha_validacion_dian",
  ],
  secciones: [
    {
      titulo: "Encabezado factura",
      cuerpo: `FACTURA ELECTRÓNICA DE VENTA N° {{prefijo}}-{{numero_factura}}
Fecha de emisión: {{fecha_emision}}
Fecha de vencimiento: {{fecha_vencimiento}}

VENDEDOR: {{vendedor_nombre}}
NIT: {{vendedor_nit}}
Dirección: {{vendedor_direccion}}
Teléfono: {{vendedor_telefono}}

COMPRADOR: {{comprador_nombre}}
NIT/CC: {{comprador_nit}}
Dirección: {{comprador_direccion}}
Teléfono: {{comprador_telefono}}`,
    },
    {
      titulo: "Detalle del servicio",
      cuerpo: `Descripción: {{descripcion_servicio}}
Cantidad: {{cantidad}}
Valor unitario: {{valor_unitario}}
Valor total: {{valor_total}}`,
    },
    {
      titulo: "Impuestos y retenciones",
      cuerpo: `IVA: {{valor_iva}}
Retención en la fuente: {{valor_retefuente}}
TOTAL A PAGAR: {{valor_a_pagar}}

Forma de pago: {{forma_pago}}
Medio de pago: {{medio_pago}}`,
    },
    {
      titulo: "Validación DIAN",
      cuerpo: `CUFE (Código Único de Facturación Electrónica): {{cufe}}
Fecha y hora de validación: {{fecha_validacion_dian}}

Esta factura electrónica ha sido validada por la DIAN y cumple con
todos los requisitos del artículo 617 del Estatuto Tributario y la
Resolución 000042 de 2020.`,
    },
  ],
};

/* ── 15. Aviso de privacidad (Ley 1581/2012 + Decreto 1377/2013) ─────── */
const PLANTILLA_AVISO_PRIVACIDAD = {
  id: "aviso_privacidad",
  titulo: "Aviso de privacidad — Tratamiento de datos personales",
  categoria: "aviso",
  audiencia: "paciente",
  version: "1.0.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: null,
  tarjetaProfesionalRequerida: true,
  marcoLegal: [
    "Ley 1581/2012",
    "Decreto 1377/2013",
    "Decreto 1074/2015",
    "Circular Externa SIC 02 de 2015",
  ],
  variables: [
    "responsable_nombre", "responsable_nit", "responsable_direccion",
    "responsable_telefono", "responsable_correo", "finalidad_tratamiento",
    "datos_recolectados", "tratamiento_autorizado", "transferencia_internacional",
    "derechos_titular", "canal_consultas", "fecha_vigencia",
  ],
  secciones: [
    {
      titulo: "Identificación del responsable",
      cuerpo: `RESPONSABLE DEL TRATAMIENTO:
{{responsable_nombre}}
NIT: {{responsable_nit}}
Dirección: {{responsable_direccion}}
Teléfono: {{responsable_telefono}}
Correo: {{responsable_correo}}`,
    },
    {
      titulo: "Finalidad del tratamiento",
      cuerpo: `Los datos personales recolectados serán tratados para la
siguiente finalidad: {{finalidad_tratamiento}}.`,
    },
    {
      titulo: "Datos recolectados",
      cuerpo: `{{datos_recolectados}}`,
    },
    {
      titulo: "Tratamiento autorizado",
      cuerpo: `Con la firma de la autorización previa, expresa e
informada, el titular autoriza el siguiente tratamiento:
{{tratamiento_autorizado}}.

Transferencia internacional: {{transferencia_internacional}}`,
    },
    {
      titulo: "Derechos del titular",
      cuerpo: `Conforme al artículo 8 de la Ley 1581 de 2012, el titular
de los datos personales tiene los siguientes derechos:
{{derechos_titular}}

Para ejercer estos derechos, el titular puede contactarse a través
del siguiente canal: {{canal_consultas}}.`,
    },
    {
      titulo: "Vigencia",
      cuerpo: `El presente aviso de privacidad entra en vigencia a
partir del {{fecha_vigencia}} y se mantiene publicado de forma
permanente en el portal de la organización.`,
    },
  ],
};

/* ── 16. Bitácora de acceso / auditoría clínica ──────────────────────── */
const PLANTILLA_BITACORA_AUDITORIA = {
  id: "bitacora_auditoria",
  titulo: "Bitácora de auditoría clínica — Acceso a historia clínica",
  categoria: "informe",
  audiencia: "profesional",
  version: "1.0.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: null,
  tarjetaProfesionalRequerida: false,
  marcoLegal: [
    "Resolución 1995/1999 (art. 13, 14)",
    "Ley 1581/2012",
    "Ley 1090/2006",
  ],
  variables: [
    "paciente_nombre", "paciente_documento", "periodo_inicio", "periodo_fin",
    "total_accesos", "accesos_lectura", "accesos_escritura",
    "accesos_denegados", "responsable_nombre", "responsable_registro",
    "fecha_emision", "observaciones",
  ],
  secciones: [
    {
      titulo: "Información del paciente y periodo",
      cuerpo: `Paciente: {{paciente_nombre}}
Documento: {{paciente_documento}}
Periodo reportado: del {{periodo_inicio}} al {{periodo_fin}}`,
    },
    {
      titulo: "Resumen de accesos",
      cuerpo: `Total de accesos registrados: {{total_accesos}}
Accesos de lectura: {{accesos_lectura}}
Accesos de escritura: {{accesos_escritura}}
Accesos denegados: {{accesos_denegados}}`,
    },
    {
      titulo: "Observaciones",
      cuerpo: `{{observaciones}}`,
    },
    {
      titulo: "Emisión responsable",
      cuerpo: `La presente bitácora se emite conforme al artículo 14 de
la Resolución 1995 de 1999 y la Ley 1581 de 2012, y refleja el
registro de auditoría del sistema.

Responsable: {{responsable_nombre}}
Registro: {{responsable_registro}}
Fecha de emisión: {{fecha_emision}}

Esta bitácora es generada automáticamente por el sistema de
información. Cualquier inconsistencia debe ser reportada al
responsable del tratamiento.`,
    },
  ],
};

/* ── 17. Consentimiento específico para uso de IA ─────────────────────── */
const PLANTILLA_CONSENT_IA = {
  id: "consent_ia",
  titulo: "Consentimiento informado — Asistencia de IA en evaluación",
  categoria: "consent",
  audiencia: "paciente",
  version: "1.0.0",
  fechaVigencia: "2026-01-15",
  caducidadMeses: 12,
  tarjetaProfesionalRequerida: true,
  marcoLegal: [
    "Ley 1581/2012",
    "Ley 1090/2006 (art. 2 y 36)",
    "Resolución 1995/1999",
  ],
  variables: [
    "paciente_nombre", "paciente_documento", "fecha", "profesional_nombre",
    "profesional_registro", "proveedor_ia", "tipo_aporte", "limites_ia",
    "supervision_humana", "revocacion",
  ],
  secciones: [
    {
      titulo: "Información sobre la asistencia de IA",
      cuerpo: `Yo, {{paciente_nombre}}, identificado/a con
{{paciente_documento}}, declaro haber sido informado/a de que la
evaluación neuropsicológica se realiza con asistencia de inteligencia
artificial, específicamente: {{proveedor_ia}}.`,
    },
    {
      titulo: "Tipo de aporte y alcances",
      cuerpo: `La asistencia de IA se limita a: {{tipo_apporte}}.
La IA NO reemplaza el criterio clínico profesional; es una
herramienta de apoyo.

{{limites_ia}}`,
    },
    {
      titulo: "Supervisión humana",
      cuerpo: `Toda sugerencia de la IA es revisada y firmada por el
profesional tratante ({{profesional_nombre}}, Registro
{{profesional_registro}}). La responsabilidad clínica final es
exclusiva del profesional, conforme al artículo 36 de la Ley 1090 de
2006.

{{supervision_humana}}`,
    },
    {
      titulo: "Protección de datos y anonimización",
      cuerpo: `Los datos enviados a la IA son previamente anonimizados:
se eliminan nombres, documentos, fechas de nacimiento, contactos y
cualquier dato que permita identificar al paciente. El proveedor de
IA recibe únicamente texto clínico despersonalizado.`,
    },
    {
      titulo: "Revocación del consentimiento",
      cuerpo: `{{revocacion}}

Fecha: {{fecha}}`,
    },
    {
      titulo: "Firmas",
      cuerpo: `Paciente: {{paciente_nombre}}
C.C.: {{paciente_documento}}
Fecha: {{fecha}}

Profesional: {{profesional_nombre}}
Registro: {{profesional_registro}}`,
    },
  ],
};

/* ───────────────────────────────────────────────────────────────────────
 * EXPORT
 * ─────────────────────────────────────────────────────────────────────── */
export const PLANTILLAS = [
  PLANTILLA_CONSENT_EVALUACION,
  PLANTILLA_CONSENT_TELE,
  PLANTILLA_ASENTIMIENTO_MENOR,
  PLANTILLA_INFORME,
  PLANTILLA_REMISION_PSIQUIATRIA,
  PLANTILLA_REMISION_NEUROLOGIA,
  PLANTILLA_EVOLUCION,
  PLANTILLA_RIPS,
  PLANTILLA_RECORDATORIO,
  PLANTILLA_SOLICITUD_HC,
  PLANTILLA_CARTA_COLEGIO,
  PLANTILLA_PERICIAL,
  PLANTILLA_CONTRATO,
  PLANTILLA_FACTURA,
  PLANTILLA_AVISO_PRIVACIDAD,
  PLANTILLA_BITACORA_AUDITORIA,
  PLANTILLA_CONSENT_IA,
];

/** Devuelve la plantilla por id, o null si no existe. */
export function plantillaPorId(id) {
  return PLANTILLAS.find((p) => p.id === id) || null;
}

/** Filtra plantillas por categoría. */
export function plantillasPorCategoria(cat) {
  return PLANTILLAS.filter((p) => p.categoria === cat);
}

/** Versión del Normograma Colombiano aplicada a todos los documentos. */
export const NORMOGRAMA_COLOMBIANO_VERSION = NORMOGRAMA_VERSION;

/** Bloque legal común al pie de cada documento. */
export const BLOQUE_LEGAL = BLOQUE_LEGAL_NORMOGRAMA;

/**
 * Verifica si una plantilla está caducada según su `caducidadMeses`
 * (a partir de su `fechaVigencia`).
 * @returns {{caducada: boolean, fechaVigencia: string, fechaCaducidad: string, mesesRestantes: number | null}}
 */
export function estadoCaducidad(plantilla, fechaReferencia = new Date()) {
  if (!plantilla) return { caducada: false, fechaVigencia: null, fechaCaducidad: null, mesesRestantes: null };
  if (!plantilla.caducidadMeses) {
    return {
      caducada: false,
      fechaVigencia: plantilla.fechaVigencia,
      fechaCaducidad: null,
      mesesRestantes: null,
      sinCaducidad: true,
    };
  }
  const inicio = new Date(plantilla.fechaVigencia);
  const caduca = new Date(inicio);
  caduca.setMonth(caduca.getMonth() + plantilla.caducidadMeses);
  const diffMs = caduca.getTime() - fechaReferencia.getTime();
  const mesesRestantes = Math.round(diffMs / (1000 * 60 * 60 * 24 * 30.44));
  return {
    caducada: diffMs < 0,
    fechaVigencia: plantilla.fechaVigencia,
    fechaCaducidad: caduca.toISOString().slice(0, 10),
    mesesRestantes,
  };
}

/** Renderiza una plantilla reemplazando {{var}} por su valor. */
export function renderPlantilla(plantilla, valores = {}) {
  if (!plantilla) return "";
  let html = "";
  // Encabezado con metadata de versión
  html += `<div class="ns-plantilla-meta">`;
  html += `<p><small>Versión del documento: <strong>${plantilla.version || "1.0.0"}</strong> · `;
  html += `Vigente desde: <strong>${plantilla.fechaVigencia || "N/D"}</strong> · `;
  html += `Normograma Colombiano: <strong>${NORMOGRAMA_VERSION}</strong></small></p>`;
  if (plantilla.caducidadMeses) {
    const cad = estadoCaducidad(plantilla);
    html += `<p><small>Caducidad: ${plantilla.caducidadMeses} meses`;
    if (cad.fechaCaducidad) html += ` (fecha de caducidad: ${cad.fechaCaducidad})`;
    if (cad.mesesRestantes !== null && cad.mesesRestantes < 3) {
      html += ` — <strong style="color:#B45309">próxima a caducar (${cad.mesesRestantes} meses)</strong>`;
    }
    html += `</small></p>`;
  }
  if (plantilla.tarjetaProfesionalRequerida) {
    html += `<p><small>Tarjeta profesional del firmante requerida (Ley 1090/2006 art. 5).</small></p>`;
  }
  html += `</div>\n`;
  for (const sec of plantilla.secciones) {
    html += `<h3>${sec.titulo}</h3>\n`;
    let cuerpo = sec.cuerpo;
    for (const v of plantilla.variables) {
      const valor = valores[v] ?? `[${v}]`;
      cuerpo = cuerpo.split(`{{${v}}}`).join(valor);
    }
    cuerpo = cuerpo.replace(/\{\{[^}]+\}\}/g, "[falta completar]");
    html += `<p>${cuerpo.replace(/\n/g, "<br>")}</p>\n`;
  }
  // Bloque legal al pie
  if (plantilla.bloqueLegal) {
    html += `<footer class="ns-plantilla-bloque-legal">`;
    html += `<hr><pre style="font-size:10px;color:#475569;white-space:pre-wrap">${plantilla.bloqueLegal}</pre>`;
    html += `</footer>`;
  }
  return html;
}

/** Extrae las variables requeridas de una plantilla. */
export function variablesRequeridas(plantilla) {
  if (!plantilla) return [];
  const requeridas = new Set(plantilla.variables);
  for (const sec of plantilla.secciones) {
    const matches = sec.cuerpo.match(/\{\{[^}]+\}\}/g) || [];
    for (const m of matches) {
      const nombre = m.replace(/[{}]/g, "");
      requeridas.add(nombre);
    }
  }
  return [...requeridas];
}

/** Valida que una plantilla tenga todas sus variables llenadas. */
export function validarValores(plantilla, valores) {
  const faltantes = plantilla.variables.filter((v) => !valores[v]);
  return { completo: faltantes.length === 0, faltantes };
}
