/* ═══════════════════════════════════════════════════════════════════════
 * src/app/aprender/QuizPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-2 — Quizzes auto-evaluativos por tema.
 *
 * Cada quiz: 10 preguntas opción múltiple. Feedback inmediato con
 * explicación + fuente. Puntaje final con historial en localStorage.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState, useMemo } from "react";
import { Btn, Card, I, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { QUIZZES } from "../../data/aprenderContent.js";

const LS_KEY = "ns_aprender_quiz_history";

function loadHistory() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || "{}"); }
  catch { return {}; }
}
function saveHistory(h) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(h)); } catch {}
}

export default function QuizPage() {
  const [quizSel, setQuizSel] = useState(null);
  const [respuestas, setRespuestas] = useState({}); // idx -> opcionElegida
  const [reveladas, setReveladas] = useState({});   // idx -> true (mostrar feedback)
  const [terminado, setTerminado] = useState(false);
  const [history, setHistory] = useState(loadHistory);

  const empezar = (q) => {
    setQuizSel(q);
    setRespuestas({});
    setReveladas({});
    setTerminado(false);
  };

  const responder = (qIdx, opcion) => {
    if (reveladas[qIdx]) return; // ya contestado
    setRespuestas(r => ({ ...r, [qIdx]: opcion }));
    setReveladas(r => ({ ...r, [qIdx]: true }));
  };

  const terminar = () => {
    setTerminado(true);
    const correctas = quizSel.preguntas.filter((p, i) => respuestas[i] === p.correcta).length;
    const total = quizSel.preguntas.length;
    const pct = Math.round(100 * correctas / total);
    const h = { ...history, [quizSel.id]: { ts: Date.now(), correctas, total, pct } };
    setHistory(h);
    saveHistory(h);
  };

  const cerrar = () => {
    setQuizSel(null);
    setRespuestas({});
    setReveladas({});
    setTerminado(false);
  };

  const score = useMemo(() => {
    if (!quizSel) return null;
    return quizSel.preguntas.filter((p, i) => respuestas[i] === p.correcta).length;
  }, [quizSel, respuestas]);

  /* Vista LISTA de quizzes */
  if (!quizSel) {
    return (
      <>
        <TopBar title="Quizzes — Autoevaluación clínica" />
        <main className="p-8 max-w-5xl mx-auto space-y-5">
          <div className="flex items-center gap-3 mb-2">
            <I name="quiz" style={{ color: TEAL, fontSize: 28 }} />
            <div>
              <h2 className="ns-serif text-xl font-bold">Quizzes por tema</h2>
              <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
                {QUIZZES.length} quizzes disponibles · feedback inmediato con fuente bibliográfica
              </p>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            {QUIZZES.map(q => {
              const hist = history[q.id];
              return (
                <button key={q.id} onClick={() => empezar(q)}
                  className="text-left p-5 rounded border transition-all hover:shadow-md"
                  style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold ns-serif text-lg leading-tight">{q.titulo}</h3>
                      <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
                        {q.preguntas.length} preguntas
                      </p>
                    </div>
                    <I name="play_circle" fill style={{ color: TEAL, fontSize: 24 }} />
                  </div>
                  <p className="text-sm mb-3" style={{ color: "var(--ns-text)" }}>
                    {q.descripcion}
                  </p>
                  {hist && (
                    <div className="text-xs flex items-center gap-2 pt-2 border-t"
                      style={{ borderColor: "var(--ns-card-b)" }}>
                      <I name="history" className="text-sm" style={{ color: TEAL }} />
                      <span style={{ color: "var(--ns-muted)" }}>Último intento:</span>
                      <strong style={{
                        color: hist.pct >= 80 ? "#10b981" : hist.pct >= 60 ? "#f59e0b" : "#dc2626",
                      }}>
                        {hist.correctas}/{hist.total} ({hist.pct}%)
                      </strong>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </main>
      </>
    );
  }

  /* Vista RESULTADO final */
  if (terminado) {
    const pct = Math.round(100 * score / quizSel.preguntas.length);
    const color = pct >= 80 ? "#10b981" : pct >= 60 ? "#f59e0b" : "#dc2626";
    return (
      <>
        <TopBar title={quizSel.titulo} />
        <main className="p-8 max-w-3xl mx-auto">
          <Card className="p-8 text-center">
            <I name={pct >= 80 ? "emoji_events" : "psychology"} fill className="text-6xl mb-4" style={{ color }} />
            <h2 className="ns-serif text-3xl font-bold mb-2">{score} / {quizSel.preguntas.length}</h2>
            <p className="text-xl font-bold mb-2" style={{ color }}>{pct}%</p>
            <p className="text-sm mb-6" style={{ color: "var(--ns-muted)" }}>
              {pct >= 80 ? "Excelente dominio del tema." : pct >= 60 ? "Buena base, repasa los puntos perdidos." : "Repasa el material y vuelve a intentar."}
            </p>
            <div className="flex justify-center gap-3">
              <Btn variant="ghost" onClick={cerrar}>
                <I name="arrow_back" className="mr-1" />Volver
              </Btn>
              <Btn onClick={() => empezar(quizSel)} style={{ background: TEAL, color: "white", borderColor: TEAL }}>
                <I name="refresh" className="mr-1" />Reintentar
              </Btn>
            </div>
          </Card>
        </main>
      </>
    );
  }

  /* Vista PREGUNTAS */
  return (
    <>
      <TopBar title={quizSel.titulo} />
      <main className="p-8 max-w-3xl mx-auto space-y-4">
        <div className="flex items-center justify-between mb-2">
          <p className="ns-eyebrow" style={{ color: TEAL }}>{quizSel.titulo}</p>
          <span className="text-xs ns-mono" style={{ color: "var(--ns-muted)" }}>
            {Object.keys(reveladas).length} / {quizSel.preguntas.length} respondidas
          </span>
        </div>

        {quizSel.preguntas.map((p, i) => {
          const elegida = respuestas[i];
          const revelada = reveladas[i];
          const correcta = elegida === p.correcta;
          return (
            <Card key={i} className="p-5">
              <p className="font-bold mb-3">
                <span className="ns-mono text-xs mr-2" style={{ color: TEAL }}>P{i + 1}</span>
                {p.enunciado}
              </p>
              <div className="space-y-2">
                {p.opciones.map((opt, oi) => {
                  let bg = "var(--ns-card)", border = "var(--ns-card-b)", color = "var(--ns-text)";
                  if (revelada) {
                    if (oi === p.correcta) { bg = "rgba(16,185,129,0.10)"; border = "#10b981"; }
                    else if (oi === elegida) { bg = "rgba(220,38,38,0.10)"; border = "#dc2626"; }
                  } else if (oi === elegida) {
                    bg = `${TEAL}15`; border = TEAL;
                  }
                  return (
                    <button key={oi} onClick={() => responder(i, oi)}
                      disabled={revelada}
                      className="w-full text-left p-3 rounded border-2 transition-all flex items-center gap-3"
                      style={{ background: bg, borderColor: border, color, cursor: revelada ? "default" : "pointer" }}>
                      <span className="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0"
                        style={{ background: revelada && oi === p.correcta ? "#10b981" : revelada && oi === elegida ? "#dc2626" : "var(--ns-subtle)",
                                 color: revelada && (oi === p.correcta || oi === elegida) ? "white" : "var(--ns-muted)" }}>
                        {revelada && oi === p.correcta ? "✓" : revelada && oi === elegida ? "✗" : String.fromCharCode(65 + oi)}
                      </span>
                      <span className="text-sm flex-1">{opt}</span>
                    </button>
                  );
                })}
              </div>
              {revelada && (
                <div className="mt-3 p-3 rounded text-sm"
                  style={{ background: correcta ? "rgba(16,185,129,0.06)" : "rgba(220,38,38,0.06)" }}>
                  <p className="font-bold mb-1" style={{ color: correcta ? "#047857" : "#dc2626" }}>
                    {correcta ? "✓ Correcto" : "✗ Incorrecto"}
                  </p>
                  <p style={{ color: "var(--ns-text)" }}>{p.explicacion}</p>
                  {p.fuente && (
                    <p className="text-[10px] ns-serif-italic mt-2" style={{ color: "var(--ns-muted)" }}>
                      Fuente: {p.fuente}
                    </p>
                  )}
                </div>
              )}
            </Card>
          );
        })}

        <div className="flex justify-end gap-2 pt-4">
          <Btn variant="ghost" onClick={cerrar}>Cancelar</Btn>
          <Btn onClick={terminar}
            disabled={Object.keys(reveladas).length < quizSel.preguntas.length}
            style={{ background: TEAL, color: "white", borderColor: TEAL }}>
            <I name="check_circle" className="mr-1" />Ver resultado
          </Btn>
        </div>
      </main>
    </>
  );
}
