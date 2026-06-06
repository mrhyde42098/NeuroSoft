/* Hub del módulo Aprender — tabs internos + acceso a sub-módulos */
import React, { useMemo, useState } from "react";
import { I, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { GLOSARIO, TARJETAS_SPACED, QUIZZES, ARTICULOS } from "../../data/aprenderContent.js";
import { CASOS_SIMULADOR } from "../../data/casosSimulador.js";
import { PROTOCOLOS } from "../../data/protocolosClinicos.js";
import { APRENDER_PATHS, readPathProgress, markPathStep } from "../../data/aprenderPaths.js";
import { safeLS } from "../../utils/safeLS.js";

const TABS = [
  { id: "inicio", label: "Inicio", icon: "home" },
  { id: "biblioteca", label: "Biblioteca", page: "biblioteca", icon: "library_books" },
  { id: "glosario", label: "Glosario", page: "aprender_glosario", icon: "translate", count: GLOSARIO.length },
  { id: "estudiar", label: "Tarjetas", page: "aprender_estudiar", icon: "psychology", count: TARJETAS_SPACED.length },
  { id: "quiz", label: "Quizzes", page: "aprender_quiz", icon: "quiz", count: QUIZZES.length },
  { id: "articulos", label: "Artículos", page: "aprender_articulos", icon: "article", count: ARTICULOS.length },
  { id: "simulador", label: "Simulador", page: "aprender_simulador", icon: "psychology_alt", count: CASOS_SIMULADOR.length },
  { id: "protocolos", label: "Protocolos", page: "aprender_protocolos", icon: "clinical_notes", count: PROTOCOLOS.length },
  { id: "pruebas", label: "Pruebas", page: "pruebas_disponibles", icon: "rule" },
  { id: "referencias", label: "Referencias", page: "referencias", icon: "menu_book" },
];

const MODULOS_DESTACADOS = [
  { id: "biblioteca", page: "biblioteca", titulo: "Biblioteca clínica", descripcion: "Manuales, artículos, escalas y protocolos seleccionados.", icono: "library_books", color: TEAL },
  { id: "glosario", page: "aprender_glosario", titulo: "Glosario neuropsicológico", descripcion: `${GLOSARIO.length} términos con definición y fuente.`, icono: "translate", color: "#1E293B" },
  { id: "estudiar", page: "aprender_estudiar", titulo: "Tarjetas de estudio", descripcion: "Repetición espaciada Leitner 5 cajas.", icono: "psychology", color: "#7c3aed" },
  { id: "quiz", page: "aprender_quiz", titulo: "Quizzes clínicos", descripcion: `${QUIZZES.length} cuestionarios con retroalimentación inmediata.`, icono: "quiz", color: "#059669" },
  { id: "articulos", page: "aprender_articulos", titulo: "Artículos editoriales", descripcion: `${ARTICULOS.length} lecturas cortas sobre interpretación clínica.`, icono: "article", color: "#0369A1" },
  { id: "simulador", page: "aprender_simulador", titulo: "Simulador de casos", descripcion: `${CASOS_SIMULADOR.length} casos con perfiles del motor.`, icono: "psychology_alt", color: "#9333ea" },
  { id: "protocolos", page: "aprender_protocolos", titulo: "Protocolos paso a paso", descripcion: `${PROTOCOLOS.length} guías de evaluación e intervención.`, icono: "clinical_notes", color: "#B45309" },
  { id: "pruebas", page: "pruebas_disponibles", titulo: "Pruebas disponibles", descripcion: "Catálogo vivo de baremos en NeuroSoft.", icono: "rule", color: "#0F766E" },
];

function readProgress() {
  try {
    const leitner = JSON.parse(safeLS.get("ns_aprender_leitner") || "{}");
    const quizHist = JSON.parse(safeLS.get("ns_aprender_quiz_history") || "[]");
    const tarjetasRepasadas = Object.values(leitner).reduce((n, box) => n + (Array.isArray(box) ? box.length : 0), 0);
    const quizzesHechos = Array.isArray(quizHist) ? quizHist.length : 0;
    return { tarjetasRepasadas, quizzesHechos };
  } catch {
    return { tarjetasRepasadas: 0, quizzesHechos: 0 };
  }
}

export default function AprenderHub({ setPage }) {
  const [tab, setTab] = useState("inicio");
  const [pathProgress, setPathProgress] = useState(() => readPathProgress());
  const progress = useMemo(() => readProgress(), [tab, pathProgress]);

  const go = (page) => {
    if (page && setPage) setPage(page);
  };

  const iniciarPaso = (pathId, paso) => {
    markPathStep(pathId, paso.orden);
    setPathProgress(readPathProgress());
    if (paso.page) go(paso.page);
  };

  return (
    <>
      <TopBar title="Aprender" />
      <main className="p-8 max-w-7xl mx-auto space-y-6">
        <div className="mb-2">
          <p className="ns-eyebrow mb-1" style={{ color: TEAL }}>Pilar 3 — Aprender</p>
          <h1 className="ns-serif text-3xl font-bold mb-2">Centro de aprendizaje clínico</h1>
          <p className="text-sm max-w-2xl leading-relaxed" style={{ color: "var(--ns-muted)" }}>
            Recursos educativos para estudiantes y profesionales. Glosario, tarjetas, quizzes, simulador y protocolos integrados con el motor clínico de NeuroSoft.
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
          <>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="p-4 rounded-xl border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                <p className="text-[10px] font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Glosario</p>
                <p className="text-2xl font-extrabold" style={{ color: TEAL }}>{GLOSARIO.length}</p>
                <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>términos curados</p>
              </div>
              <div className="p-4 rounded-xl border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                <p className="text-[10px] font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Tarjetas repasadas</p>
                <p className="text-2xl font-extrabold" style={{ color: TEAL }}>{progress.tarjetasRepasadas}</p>
                <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>de {TARJETAS_SPACED.length} en Leitner</p>
              </div>
              <div className="p-4 rounded-xl border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                <p className="text-[10px] font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Quizzes completados</p>
                <p className="text-2xl font-extrabold" style={{ color: TEAL }}>{progress.quizzesHechos}</p>
                <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>{QUIZZES.length} disponibles</p>
              </div>
              <div className="p-4 rounded-xl border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                <p className="text-[10px] font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Simulador</p>
                <p className="text-2xl font-extrabold" style={{ color: TEAL }}>{CASOS_SIMULADOR.length}</p>
                <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>casos clínicos</p>
              </div>
            </div>

            <div>
              <p className="ns-eyebrow mb-3" style={{ color: TEAL }}>Rutas de estudio guiadas</p>
              <div className="grid sm:grid-cols-2 gap-4">
                {APRENDER_PATHS.map((ruta) => {
                  const prog = pathProgress[ruta.id] || { completed: [], lastStep: 0 };
                  const pct = Math.round((prog.completed.length / ruta.pasos.length) * 100);
                  return (
                    <div
                      key={ruta.id}
                      className="p-5 rounded-xl border"
                      style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                          <h3 className="font-bold text-sm">{ruta.titulo}</h3>
                          <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>{ruta.descripcion}</p>
                        </div>
                        <span className="text-[10px] font-bold shrink-0 px-2 py-1 rounded" style={{ background: "var(--ns-subtle)", color: TEAL }}>
                          {pct}%
                        </span>
                      </div>
                      <p className="text-[10px] mb-3" style={{ color: "var(--ns-muted)" }}>
                        {ruta.duracion_estimada} · {ruta.pasos.length} pasos
                      </p>
                      <ol className="space-y-1.5">
                        {ruta.pasos.map((paso) => {
                          const done = prog.completed.includes(paso.orden);
                          return (
                            <li key={paso.orden}>
                              <button
                                type="button"
                                onClick={() => iniciarPaso(ruta.id, paso)}
                                className="w-full text-left flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all hover:bg-[var(--ns-subtle)]"
                                style={{ color: done ? TEAL : "var(--ns-text)" }}
                              >
                                <I name={done ? "check_circle" : "radio_button_unchecked"} className="text-sm shrink-0" style={{ color: done ? TEAL : "var(--ns-muted)" }} />
                                <span className={done ? "line-through opacity-70" : ""}>{paso.titulo}</span>
                              </button>
                            </li>
                          );
                        })}
                      </ol>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-4">
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
          </>
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
