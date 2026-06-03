/* ═══════════════════════════════════════════════════════════════════════
 * src/app/help/HelpPage.jsx — Guía rápida in-app de NeuroSoft
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { Card, I, TopBar } from "../../ui/primitives.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";
import { CHANGELOG } from "../../data/changelog.js";
import {
  CAPITULOS_NEURONORMA, NEURONORMA_COLOMBIA_REF, REGLAS_AJUSTE,
} from "../../data/neuronormaColombia.js";

/* ─── Contenido de la guía ────────────────────────────────────────── */
const SECCIONES = [
  {
    id: "flujo",
    icon: "route",
    titulo: "Flujo clínico típico",
    color: TEAL,
    pasos: [
      { n: 1, titulo: "Registrar paciente",    desc: "Pacientes → Registrar. Ingresa datos de identificación y demográficos. El sistema calcula automáticamente la población (infantil / adulto joven / adulto mayor) según la fecha de nacimiento.", icon: "person_add" },
      { n: 2, titulo: "Historia Clínica",      desc: "Pacientes → Historia Clínica. Documenta motivo de consulta, antecedentes, hipótesis diagnóstica y código CIE-10 (el selector sugiere códigos por población).", icon: "clinical_notes" },
      { n: 3, titulo: "Consentimiento",        desc: "En Historia Clínica hay un botón 'Consentimiento Informado'. Genera el documento PDF para que el paciente firme antes de iniciar la evaluación.", icon: "draw" },
      { n: 4, titulo: "Aplicar evaluación",    desc: "Evaluación → Aplicar. Selecciona protocolo (WISC-IV, WAIS-III, Neuronorma…), ingresa PD ítem por ítem o el total, y completa observaciones conductuales.", icon: "psychology" },
      { n: 5, titulo: "Ver resultados",        desc: "Al guardar, el motor de baremos calcula automáticamente puntajes escalares, Z, percentiles e interpretación. Revisa la curva Z, el radar de dominios y las alertas.", icon: "analytics" },
      { n: 6, titulo: "Redactar informe",      desc: "En la misma pantalla de resultados, completa las secciones narrativas. Usa 'Auto-generar' para borradores basados en los puntajes, o 'IA' para mejorar el texto.", icon: "edit_note" },
      { n: 7, titulo: "Descargar informe",     desc: "Informes → selecciona paciente y evaluación → Descargar PDF, DOCX o XLSX. El PDF incluye firma digital del profesional si está configurada.", icon: "download" },
      { n: 8, titulo: "Comparativa Pre–Post",  desc: "Historial → Pre–Post. Selecciona dos evaluaciones del mismo paciente para ver el cambio en Z, el Índice de Cambio Confiable (RCI) y el radar evolutivo.", icon: "compare_arrows" },
    ],
  },
  {
    id: "protocolos",
    icon: "quiz",
    titulo: "Protocolos y poblaciones",
    color: "#6366f1",
    items: [
      { titulo: "WISC-IV (infantil · 6-16 años)",    desc: "15 subtests. Índices: CIT, ICV, IRP, IMT, IVP. Baremos nacionales disponibles. Inicia por edad: 6-7 años desde ítem 1; 8-10 desde ítem 3; 11-13 desde ítem 5; 14-16 desde ítem 7." },
      { titulo: "WAIS-III (adultos · 16-89 años)",   desc: "11 subtests principales. Índices: CIT, CV, OP, MT. Adultos ≥75 siempre inician en ítem 1. Regla de reversal: 2 puntos perfectos consecutivos." },
      { titulo: "Neuronorma Colombia (AM · 50+)",    desc: "15 pruebas cognitivas adaptadas para adulto mayor. Ajuste por edad, escolaridad y sexo. Los puntajes escalares van de 1-19 (no CI). El motor corrige automáticamente." },
      { titulo: "Screening (tamizaje rápido)",        desc: "MMSE, MoCA, ACE-III, MOCA-BASIC, BAI, BDI-II, GDS-15, BARTHEL, LAWTON, TRAIL MAKING. Accede desde Evaluación → Screening." },
    ],
  },
  {
    id: "rci",
    icon: "science",
    titulo: "Índice de Cambio Confiable (RCI)",
    color: "#059669",
    content: `El RCI (Jacobson & Truax, 1991) determina si el cambio entre dos evaluaciones supera el error de medición del test. La fórmula es:

RCI = (Post − Pre) / SE_diff

Donde SE_diff = √2 × SEM, y SEM = SD × √(1 − r_xx).

Interpretación:
• |RCI| ≥ 1.96 → Cambio significativo (p<.05): muy improbable que sea por azar.
• |RCI| 1.64–1.96 → Cambio sugestivo (p<.10): tendencia a monitorizar.
• |RCI| < 1.64 → Dentro del error de medición: estabilidad estadística.

NeuroSoft usa r=0.85 y Z-score como métrica base (conservador). Consulte las tablas de confiabilidad del manual para valores específicos de cada prueba.`,
  },
  {
    id: "ia",
    icon: "smart_toy",
    titulo: "Asistente IA",
    color: "#8b5cf6",
    items: [
      { titulo: "Configuración",       desc: "Herramientas → Asistente IA. Conecta Ollama (local) o configura una clave de API externa. El modelo recomendado para clínica es Llama-3 8B o Mistral 7B." },
      { titulo: "Mejorar texto",       desc: "En la pantalla de resultados, selecciona cualquier sección de observaciones y pulsa el botón IA. El asistente mejora la redacción manteniendo el contenido clínico." },
      { titulo: "Chat flotante",       desc: "El botón IA en la esquina inferior derecha abre un chat contextual. Puedes preguntar sobre interpretación de puntajes, escribir borradores o generar recomendaciones." },
      { titulo: "Privacidad",          desc: "Cuando Ollama está activo (local), los datos no salen del equipo. En modo API externa, solo se envía el texto del campo seleccionado, nunca datos de identificación del paciente." },
    ],
  },
  {
    id: "shortcuts",
    icon: "keyboard",
    titulo: "Atajos de teclado",
    color: "#d97706",
    shortcuts: [
      { key: "Alt+P", desc: "Ir a Pacientes" },
      { key: "Alt+E", desc: "Ir a Evaluación" },
      { key: "Alt+R", desc: "Ir a Rehabilitación" },
      { key: "Alt+H", desc: "Toggle alto contraste" },
      { key: "Alt++", desc: "Aumentar fuente" },
      { key: "Alt+-", desc: "Reducir fuente" },
      { key: "Alt+D", desc: "Toggle modo oscuro" },
    ],
  },
  {
    id: "privacidad",
    icon: "privacy_tip",
    titulo: "Privacidad y datos",
    color: "#ef4444",
    items: [
      { titulo: "Almacenamiento",   desc: "Todos los datos se guardan en el equipo de la institución (SQLite local). NeuroSoft no transmite datos clínicos a servidores externos." },
      { titulo: "Backups",          desc: "Configura respaldos automáticos en Configuración → Respaldo. Se recomienda copiar el archivo .db a un disco externo o red segura al menos semanalmente." },
      { titulo: "Derechos ARCO",    desc: "Los pacientes pueden solicitar acceso, rectificación o eliminación de sus datos directamente al profesional tratante (Ley 1581 de 2012)." },
      { titulo: "Consentimiento",   desc: "Obtén el consentimiento informado firmado antes de iniciar cualquier evaluación. El módulo genera el documento en PDF listo para imprimir o firmar digitalmente." },
    ],
  },
  /* §neuronorma: sección nueva dedicada a las normas colombianas
   * (Arango-Lasprilla & Rivera, 2017). Componente custom. */
  {
    id: "neuronorma",
    icon: "public",
    titulo: "Neuronorma Colombia",
    color: "#fb923c",
    custom: "neuronorma",
  },
];

/* ─── Componente ────────────────────────────────────────────────────── */
export default function HelpPage({ section = null }) {
  const [activeId, setActiveId] = useState(section === "changelog" ? "cambios" : "flujo");

  /* Seccion: Registro de cambios */
  const SECCION_CAMBIOS = {
    id: "cambios", icon: "new_releases", titulo: "Registro de cambios", color: "#0D9488",
  };

  const allSections = [...SECCIONES, SECCION_CAMBIOS];
  const active = allSections.find(s => s.id === activeId) || allSections[0];

  return (
    <>
      <TopBar title="Ayuda y Guía de Uso">
        <span className="text-xs" style={{ color: "var(--ns-muted)" }}>NeuroSoft App</span>
      </TopBar>
      <main className="p-8">
        <div className="flex gap-6">
          {/* Menú lateral */}
          <div className="w-56 shrink-0 space-y-1 sticky top-24 self-start">
            {allSections.map(sec => (
              <button
                key={sec.id}
                onClick={() => setActiveId(sec.id)}
                className={`w-full text-left px-4 py-3 rounded-2xl text-sm font-medium flex items-center gap-3 transition-all ${
                  activeId === sec.id ? "text-white font-bold shadow-lg" : "hover:bg-gray-100"
                }`}
                style={activeId === sec.id
                  ? { background: sec.color, boxShadow: `0 6px 20px -4px ${sec.color}50` }
                  : { color: "var(--ns-muted)" }}
              >
                <I name={sec.icon} fill={activeId === sec.id} className="text-base shrink-0" />
                {sec.titulo}
              </button>
            ))}
          </div>

          {/* Contenido */}
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-2xl flex items-center justify-center"
                style={{ background: `${active.color}20` }}>
                <I name={active.icon} fill className="text-xl" style={{ color: active.color }} />
              </div>
              <h2 className="text-2xl font-bold" style={{ color: "var(--ns-text)" }}>{active.titulo}</h2>
            </div>

            {/* Registro de cambios */}
            {activeId === "cambios" && (
              <div className="space-y-4">
                <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
                  Historial completo de versiones publicadas de NeuroSoft App.
                  Cada versión incluye las novedades y mejoras incorporadas.
                </p>
                {CHANGELOG.map((entry) => (
                  <Card key={entry.version} className="p-5 border-l-4" style={{ borderColor: entry.color }}>
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${entry.color}20` }}>
                        <I name={entry.icono} fill className="text-lg" style={{ color: entry.color }} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-extrabold" style={{ color: "var(--ns-text)" }}>v{entry.version}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded-full font-bold"
                            style={{ background: `${entry.color}20`, color: entry.color }}>
                            {new Date(entry.fecha).toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" })}
                          </span>
                        </div>
                        <p className="text-xs mt-0.5" style={{ color: "var(--ns-muted)" }}>{entry.titulo}</p>
                      </div>
                    </div>
                    <ul className="space-y-1.5">
                      {entry.cambios.map((c, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm" style={{ color: "var(--ns-text)" }}>
                          <span className="mt-1.5 shrink-0 w-1 h-1 rounded-full" style={{ background: entry.color }} />
                          <span>{c}</span>
                        </li>
                      ))}
                    </ul>
                  </Card>
                ))}
                <Card className="p-4 border-dashed text-center" style={{ background: "var(--ns-subtle)" }}>
                  <I name="update" className="text-2xl mb-1" style={{ color: "var(--ns-muted)" }} />
                  <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
                    Al instalar una nueva versión, NeuroSoft App detecta automáticamente el cambio y muestra las novedades.
                  </p>
                </Card>
              </div>
            )}

            {/* Flujo clínico — pasos */}
            {active.pasos && (
              <div className="space-y-3">
                {active.pasos.map(paso => (
                  <Card key={paso.n} className="p-5 flex items-start gap-4">
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 text-white font-extrabold text-sm"
                      style={{ background: TEAL }}>
                      {paso.n}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <I name={paso.icon} fill className="text-base" style={{ color: TEAL }} />
                        <p className="font-bold text-sm">{paso.titulo}</p>
                      </div>
                      <p className="text-xs leading-relaxed" style={{ color: "var(--ns-muted)" }}>{paso.desc}</p>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Items genéricos (protocolos, IA, privacidad) */}
            {active.items && (
              <div className="space-y-3">
                {active.items.map((item, i) => (
                  <Card key={i} className="p-5">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full shrink-0" style={{ background: active.color }} />
                      <p className="font-bold text-sm">{item.titulo}</p>
                    </div>
                    <p className="text-xs leading-relaxed pl-4" style={{ color: "var(--ns-muted)" }}>{item.desc}</p>
                  </Card>
                ))}
              </div>
            )}

            {/* Contenido de texto libre (RCI) */}
            {active.content && (
              <Card className="p-6">
                <pre className="text-xs leading-relaxed whitespace-pre-wrap font-sans"
                  style={{ color: "var(--ns-muted)" }}>
                  {active.content}
                </pre>
              </Card>
            )}

            {/* §neuronorma: sección custom Neuronorma Colombia */}
            {active.custom === "neuronorma" && (
              <div className="space-y-4">
                {/* Cita bibliográfica */}
                <Card className="p-5" style={{ background: "linear-gradient(135deg,#fff7ed,#fed7aa)" }}>
                  <div className="flex items-start gap-3">
                    <div className="text-4xl">🇨🇴</div>
                    <div>
                      <p className="font-bold text-sm" style={{ color: "#7c2d12" }}>
                        Datos normativos colombianos
                      </p>
                      <p className="text-xs mt-1 leading-relaxed" style={{ color: "#9a3412" }}>
                        {NEURONORMA_COLOMBIA_REF.cita}
                      </p>
                      <p className="text-[10px] mt-2 italic" style={{ color: "#9a3412" }}>
                        Cita corta: <strong>{NEURONORMA_COLOMBIA_REF.citaCorta}</strong>
                      </p>
                    </div>
                  </div>
                </Card>

                {/* Variables de ajuste obligatorias */}
                <Card className="p-5 border-l-4" style={{ borderColor: "#fb923c" }}>
                  <p className="text-xs font-extrabold uppercase tracking-wider mb-3" style={{ color: "#7c2d12" }}>
                    {REGLAS_AJUSTE.titulo}
                  </p>
                  <ul className="space-y-2">
                    {REGLAS_AJUSTE.bullets.map((b, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs leading-relaxed" style={{ color: "var(--ns-text)" }}>
                        <span className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ background: "#fb923c" }} />
                        {b}
                      </li>
                    ))}
                  </ul>
                </Card>

                {/* 10 pruebas con normas colombianas */}
                <div>
                  <p className="text-xs font-extrabold uppercase tracking-wider mb-3" style={{ color: "var(--ns-muted)" }}>
                    10 pruebas con baremos colombianos
                  </p>
                  <div className="space-y-2">
                    {CAPITULOS_NEURONORMA.map(c => (
                      <Card key={c.n} className="p-4 flex items-start gap-3">
                        <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 text-white font-extrabold text-sm" style={{ background: "linear-gradient(135deg,#fb923c,#f97316)" }}>
                          {c.n}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-bold text-sm" style={{ color: "var(--ns-text)" }}>{c.titulo}</p>
                          <p className="text-[11px] mt-0.5" style={{ color: "var(--ns-muted)" }}>
                            <strong>Puntuaciones:</strong> {c.pruebas.join(" · ")}
                          </p>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>

                {/* Cómo identificar pruebas con norma colombiana */}
                <Card className="p-5" style={{ background: "var(--ns-subtle)" }}>
                  <p className="text-xs font-extrabold uppercase tracking-wider mb-2" style={{ color: "var(--ns-muted)" }}>
                    Cómo identificarlas en NeuroSoft
                  </p>
                  <p className="text-xs leading-relaxed" style={{ color: "var(--ns-text)" }}>
                    Cuando aplicas una prueba con normas colombianas disponibles,
                    aparece el badge <span className="px-2 py-0.5 rounded-full text-[10px] font-bold mx-1" style={{ background: "linear-gradient(135deg,#fde047,#fb923c)", color: "#7c2d12" }}>🇨🇴 Norma Colombia</span>
                    junto al título de la prueba. Pasa el cursor sobre él para ver el capítulo de referencia.
                  </p>
                </Card>
              </div>
            )}

            {/* Atajos de teclado */}
            {active.shortcuts && (
              <Card className="p-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {active.shortcuts.map(sc => (
                    <div key={sc.key} className="flex items-center justify-between py-3 px-4 rounded-xl"
                      style={{ background: "var(--ns-subtle)" }}>
                      <span className="text-sm" style={{ color: "var(--ns-muted)" }}>{sc.desc}</span>
                      <kbd className="px-3 py-1 rounded-lg text-xs font-bold font-mono"
                        style={{ background: "var(--ns-card)", border: "1px solid var(--ns-card-b)", color: "var(--ns-text)" }}>
                        {sc.key}
                      </kbd>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Pie de guía */}
            <div className="mt-6 p-4 rounded-2xl text-center text-[10px] leading-relaxed"
              style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
              <I name="info" className="text-xs mr-1" />
              NeuroSoft es una herramienta de <strong>apoyo clínico</strong>. Los resultados deben interpretarse
              siempre en el contexto de la evaluación completa y el juicio profesional del neuropsicólogo.
              <br />
              Contacto:{" "}
              <a href="mailto:soporte@neurosoft.co" className="underline" style={{ color: TEAL }}>
                soporte@neurosoft.co
              </a>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
