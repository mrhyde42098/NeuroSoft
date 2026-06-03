/* ═══════════════════════════════════════════════════════════════════════
 * src/data/ui.js — Constantes UI (extraidas de App.jsx)
 * ─────────────────────────────────────────────────────────────────────── */

/* §B5-fix: "?" antes requería Shift+/ (depende del layout — en teclado
 * español varios mapeos lo cambian). Reemplazado por "h" (Help) que es
 * universal en todos los teclados latinoamericanos y europeos. */
export const SHORTCUTS=[{key:"1",desc:"Inicio",page:"dashboard"},{key:"2",desc:"Pacientes",page:"patients"},{key:"3",desc:"Agenda",page:"agenda"},{key:"4",desc:"Evaluación",page:"evaluation"},{key:"5",desc:"Screening",page:"screening"},{key:"6",desc:"Historial",page:"history"},{key:"7",desc:"Informes",page:"reports"},{key:"8",desc:"Rehabilitación",page:"rehab"},{key:"9",desc:"Configuración",page:"config"},{key:"d",desc:"Modo oscuro",action:"dark"},{key:"h",desc:"Mostrar atajos",action:"shortcuts"}];

export const DISCREPANCY_PAIRS=[{a:"ICV",b:"IRP",name:"ICV–IRP",critical15:11,critical05:15},{a:"ICV",b:"IMT",name:"ICV–IMT",critical15:12,critical05:16},{a:"ICV",b:"IVP",name:"ICV–IVP",critical15:15,critical05:19},{a:"IRP",b:"IMT",name:"IRP–IMT",critical15:13,critical05:17},{a:"IRP",b:"IVP",name:"IRP–IVP",critical15:15,critical05:19},{a:"IMT",b:"IVP",name:"IMT–IVP",critical15:16,critical05:20}];

export const CONSENT_LABELS={habeas_data:{titulo:"Autorización de Tratamiento de Datos Personales",desc:"Ley 1581/2012 — Habeas Data"},evaluacion:{titulo:"Consentimiento Informado de Evaluación Neuropsicológica",desc:"Aplicación de pruebas cognitivas"},tratamiento:{titulo:"Consentimiento para Intervención Terapéutica",desc:"Tratamiento de rehabilitación"},telepsicologia:{titulo:"Consentimiento de Telepsicología",desc:"Atención remota/telepresencial"}};

export const REPORT_TEMPLATES={
  clinico:{nombre:"Clínico Estándar",descripcion:"Formato estándar con todas las secciones",secciones:["portada","datos_paciente","motivo_consulta","antecedentes","observacion_clinica","pruebas","resultados","grafica_z","tabla_puntajes","observaciones","conclusion","firmas"]},
  ejecutivo:{nombre:"Ejecutivo Breve",descripcion:"Resumen ejecutivo de 2-3 páginas",secciones:["portada","datos_paciente","sintesis_cognitiva","conclusion","recomendaciones","firmas"]},
  escolar:{nombre:"Informe Escolar",descripcion:"Dirigido a instituciones educativas",secciones:["portada","datos_paciente","motivo_consulta","hallazgos_academicos","recomendaciones_escolares","firmas"]},
  geriatrico:{nombre:"Geriátrico",descripcion:"Enfocado en adulto mayor con énfasis en tamizaje",secciones:["portada","datos_paciente","antecedentes","screening_mmse","perfil_cognitivo","impresion_diagnostica","recomendaciones","firmas"]},
  /* §11.3 — Nuevas plantillas */
  inconcluso:{nombre:"Informe Inconcluso",descripcion:"Para evaluaciones que no pudieron completarse — incluye categoría de razón y nota clínica",secciones:["portada","datos_paciente","motivo_consulta","antecedentes","resultados_parciales","razon_inconcluso","nota_inconcluso","recomendaciones","firmas"],nota:"Secciones razon_inconcluso y nota_inconcluso se mapean a los campos informe_inconcluso_cat / informe_inconcluso_nota guardados en la evaluación."},
  retest:{nombre:"Re-test / Control de evolución",descripcion:"Comparativo entre dos evaluaciones con índice de cambio confiable (RCI de Jacobson-Truax)",secciones:["portada","datos_paciente","contexto_retest","tabla_comparativa_puntajes","grafica_rci","interpretacion_cambio","conclusion","firmas"],nota:"Requiere seleccionar evaluación basal y evaluación de seguimiento. RCI = (PE2 - PE1) / SEM·√2."},
  pediatrico_bilingue:{nombre:"Pediátrico Bilingüe (ES/EN)",descripcion:"Para familias en contexto bilingüe: secciones clínicas en español con resumen ejecutivo en inglés",secciones:["portada","datos_paciente","motivo_consulta","antecedentes","observacion_clinica","resultados","grafica_z","observaciones","conclusion","executive_summary_en","recomendaciones","firmas"],nota:"La sección executive_summary_en se completa manualmente o se marca como pendiente de traducción."},
  junta_medica:{nombre:"Junta Médica / Interconsulta",descripcion:"Estructura formal para presentación en junta interdisciplinaria o interconsulta especializada",secciones:["encabezado_junta","datos_paciente","motivo_interconsulta","resumen_antecedentes","hallazgos_neuropsicologicos","impresion_diagnostica","hipotesis_diagnosticas","preguntas_a_junta","recomendaciones","firmas"]},
};
