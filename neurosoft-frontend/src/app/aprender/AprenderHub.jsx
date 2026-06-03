/* ═══════════════════════════════════════════════════════════════════════
 * src/app/aprender/AprenderHub.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-2 — Hub del módulo "Aprender" (Pilar 3 NeuroSoft).
 *
 * Dashboard con accesos a:
 *   • Biblioteca (recursos clínicos)
 *   • Glosario interactivo
 *   • Tarjetas spaced repetition
 *   • Quizzes auto-evaluativos
 *   • Artículos editoriales
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";
import { I, TopBar } from "../../ui/primitives.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";
import { GLOSARIO, TARJETAS_SPACED, QUIZZES, ARTICULOS } from "../../data/aprenderContent.js";
import { CASOS_SIMULADOR } from "../../data/casosSimulador.js";
import { PROTOCOLOS } from "../../data/protocolosClinicos.js";

const MODULOS = [
  {
    id: "biblioteca", page: "biblioteca",
    titulo: "Biblioteca clínica",
    descripcion: "Catálogo curado de manuales, artículos, escalas y protocolos clínicos.",
    icono: "library_books",
    color: TEAL,
  },
  {
    id: "glosario", page: "aprender_glosario",
    titulo: "Glosario neuropsicológico",
    descripcion: "Términos técnicos con definición, ejemplo y fuente.",
    icono: "translate",
    color: NAVY,
    count: () => `${GLOSARIO.length} términos`,
  },
  {
    id: "estudiar", page: "aprender_estudiar",
    titulo: "Tarjetas de estudio",
    descripcion: "Repetición espaciada (Leitner 5 cajas) para fijar conocimiento clínico.",
    icono: "psychology",
    color: "#7c3aed",
    count: () => `${TARJETAS_SPACED.length} tarjetas`,
  },
  {
    id: "quiz", page: "aprender_quiz",
    titulo: "Quizzes auto-evaluativos",
    descripcion: "Cuestionarios por tema con feedback inmediato y explicación.",
    icono: "quiz",
    color: "#f59e0b",
    count: () => `${QUIZZES.length} quizzes`,
  },
  {
    id: "articulos", page: "aprender_articulos",
    titulo: "Artículos editoriales",
    descripcion: "Lecturas cortas (5-10 min) sobre interpretación clínica y diagnóstico diferencial.",
    icono: "article",
    color: "#0891b2",
    count: () => `${ARTICULOS.length} artículos`,
  },
  {
    id: "simulador", page: "aprender_simulador",
    titulo: "Simulador de casos clínicos",
    descripcion: "Vignettes con perfiles reales del motor. Lee, interpreta, compara con respuesta experta.",
    icono: "psychology_alt",
    color: "#9333ea",
    count: () => `${CASOS_SIMULADOR.length} casos`,
  },
  {
    id: "pruebas", page: "pruebas_disponibles",
    titulo: "Pruebas disponibles",
    descripcion: "Catálogo de las 177 pruebas del motor: instrucciones, baremos, dominios.",
    icono: "biotech",
    color: "#dc2626",
  },
  {
    id: "referencias", page: "referencias",
    titulo: "Referencias bibliográficas",
    descripcion: "Catálogo curado de libros, artículos, manuales y guías con DOI/ISBN verificables.",
    icono: "menu_book",
    color: "#0891b2",
    count: () => "Catálogo APA 7ª",
  },
  {
    id: "protocolos", page: "aprender_protocolos",
    titulo: "Protocolos clínicos",
    descripcion: "Guías paso a paso para evaluación neuropsicológica e intervención terapéutica.",
    icono: "clinical_notes",
    color: "#10b981",
    count: () => `${PROTOCOLOS.length} protocolos`,
  },
];

export default function AprenderHub({ setPage }) {
  return (
    <>
      <TopBar title="Aprender" />
      <main className="p-8 max-w-6xl mx-auto space-y-6">
        {/* Hero */}
        <div className="mb-6">
          <p className="ns-eyebrow mb-1" style={{ color: TEAL }}>Pilar 3 — Aprender</p>
          <h1 className="ns-serif text-3xl font-bold mb-2">Centro de aprendizaje clínico</h1>
          <p className="text-sm max-w-2xl leading-relaxed" style={{ color: "var(--ns-muted)" }}>
            Recursos educativos curados para estudiantes y profesionales: biblioteca clínica,
            glosario interactivo, tarjetas con repetición espaciada, autoevaluación y artículos
            editoriales escritos por neuropsicólogos colombianos.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {MODULOS.map(m => (
            <button key={m.id} onClick={() => setPage?.(m.page)}
              className="text-left p-6 rounded-lg border-l-[3px] transition-all hover:shadow-md hover:-translate-y-0.5"
              style={{ background: "var(--ns-card)", borderLeftColor: m.color, borderTop: "1px solid var(--ns-card-b)", borderRight: "1px solid var(--ns-card-b)", borderBottom: "1px solid var(--ns-card-b)" }}>
              <div className="flex items-start gap-3 mb-3">
                <div className="w-12 h-12 rounded-md flex items-center justify-center shrink-0"
                  style={{ background: `${m.color}15` }}>
                  <I name={m.icono} fill style={{ color: m.color, fontSize: 24 }} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-base leading-tight">{m.titulo}</h3>
                  {m.count && (
                    <p className="text-[10px] uppercase tracking-wider mt-1" style={{ color: m.color }}>
                      {m.count()}
                    </p>
                  )}
                </div>
              </div>
              <p className="text-xs leading-relaxed" style={{ color: "var(--ns-muted)" }}>
                {m.descripcion}
              </p>
            </button>
          ))}
        </div>

        {/* Cita inspiracional */}
        <div className="rounded-lg p-5 mt-8" style={{ background: "var(--ns-subtle)" }}>
          <p className="ns-serif-italic text-sm" style={{ color: "var(--ns-text)" }}>
            "La neuropsicología clínica no es una disciplina de respuestas, sino de
            preguntas afinadas. El paciente real nunca encaja perfectamente en el
            manual — el arte está en saber dónde buscar."
          </p>
          <p className="text-xs mt-2 text-right" style={{ color: "var(--ns-muted)" }}>
            — Inspirado en Lezak, Howieson, Bigler & Tranel (2012)
          </p>
        </div>
      </main>
    </>
  );
}
