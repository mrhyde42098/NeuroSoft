/* Hub del módulo Aprender — tabs internos + acceso a sub-módulos */
import React, { useState } from "react";
import { I, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { GLOSARIO, TARJETAS_SPACED, QUIZZES, ARTICULOS } from "../../data/aprenderContent.js";
import { CASOS_SIMULADOR } from "../../data/casosSimulador.js";
import { PROTOCOLOS } from "../../data/protocolosClinicos.js";

const TABS = [
  { id: "inicio", label: "Inicio", icon: "home" },
  { id: "biblioteca", label: "Biblioteca", page: "biblioteca", icon: "library_books" },
  { id: "glosario", label: "Glosario", page: "aprender_glosario", icon: "translate", count: GLOSARIO.length },
  { id: "estudiar", label: "Tarjetas", page: "aprender_estudiar", icon: "psychology", count: TARJETAS_SPACED.length },
  { id: "quiz", label: "Quizzes", page: "aprender_quiz", icon: "quiz", count: QUIZZES.length },
  { id: "articulos", label: "Artículos", page: "aprender_articulos", icon: "article", count: ARTICULOS.length },
  { id: "simulador", label: "Simulador", page: "aprender_simulador", icon: "psychology_alt", count: CASOS_SIMULADOR.length },
  { id: "referencias", label: "Referencias", page: "referencias", icon: "menu_book" },
  { id: "protocolos", label: "Protocolos", page: "help", icon: "clinical_notes", count: PROTOCOLOS.length },
];

const MODULOS_DESTACADOS = [
  { id: "biblioteca", page: "biblioteca", titulo: "Biblioteca clínica", descripcion: "Manuales, artículos, escalas y protocolos curados.", icono: "library_books", color: TEAL },
  { id: "glosario", page: "aprender_glosario", titulo: "Glosario neuropsicológico", descripcion: `${GLOSARIO.length} términos con definición y fuente.`, icono: "translate", color: "#1E293B" },
  { id: "estudiar", page: "aprender_estudiar", titulo: "Tarjetas de estudio", descripcion: "Repetición espaciada Leitner 5 cajas.", icono: "psychology", color: "#7c3aed" },
  { id: "simulador", page: "aprender_simulador", titulo: "Simulador de casos", descripcion: `${CASOS_SIMULADOR.length} casos con perfiles del motor.`, icono: "psychology_alt", color: "#9333ea" },
];

export default function AprenderHub({ setPage }) {
  const [tab, setTab] = useState("inicio");

  const go = (page) => {
    if (page && setPage) setPage(page);
  };

  return (
    <>
      <TopBar title="Aprender" />
      <main className="p-8 max-w-6xl mx-auto space-y-6">
        <div className="mb-2">
          <p className="ns-eyebrow mb-1" style={{ color: TEAL }}>Pilar 3 — Aprender</p>
          <h1 className="ns-serif text-3xl font-bold mb-2">Centro de aprendizaje clínico</h1>
          <p className="text-sm max-w-2xl leading-relaxed" style={{ color: "var(--ns-muted)" }}>
            Recursos educativos para estudiantes y profesionales. Use las pestañas para navegar entre módulos.
          </p>
        </div>

        <nav className="flex flex-wrap gap-1.5 pb-2 border-b" style={{ borderColor: "var(--ns-card-b)" }} aria-label="Módulos Aprender">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => {
                setTab(t.id);
                if (t.page) go(t.page);
              }}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold transition-all"
              style={
                tab === t.id
                  ? { background: TEAL, color: "#fff" }
                  : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }
              }
            >
              <I name={t.icon} className="text-sm" />
              {t.label}
              {t.count != null && <span className="opacity-70">({t.count})</span>}
            </button>
          ))}
        </nav>

        {tab === "inicio" && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-2 gap-4">
            {MODULOS_DESTACADOS.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => go(m.page)}
                className="text-left p-6 rounded-xl border transition-all hover:shadow-md"
                style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}
              >
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 rounded-md flex items-center justify-center shrink-0" style={{ background: `${m.color}15` }}>
                    <I name={m.icono} fill style={{ color: m.color, fontSize: 24 }} />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm mb-1">{m.titulo}</h3>
                    <p className="text-xs" style={{ color: "var(--ns-muted)" }}>{m.descripcion}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}

        <blockquote className="rounded-xl p-5 mt-4" style={{ background: "var(--ns-subtle)", borderLeft: `3px solid ${TEAL}` }}>
          <p className="ns-serif italic text-sm leading-relaxed" style={{ color: "var(--ns-text)" }}>
            La neuropsicología clínica no es una disciplina de respuestas, sino de preguntas afinadas.
          </p>
          <footer className="text-[10px] mt-2" style={{ color: "var(--ns-muted)" }}>Lezak, Howieson, Bigler & Tranel (2012)</footer>
        </blockquote>
      </main>
    </>
  );
}
