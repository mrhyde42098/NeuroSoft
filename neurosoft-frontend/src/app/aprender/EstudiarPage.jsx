/* ═══════════════════════════════════════════════════════════════════════
 * src/app/aprender/EstudiarPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-2 — Tarjetas de estudio (spaced repetition simple).
 *
 * Algoritmo: Leitner box system básico (5 cajas).
 *   - Caja 1: revisar diariamente
 *   - Caja 2: cada 2 días
 *   - Caja 3: cada 4 días
 *   - Caja 4: cada 7 días
 *   - Caja 5: cada 15 días
 *
 * Acertar promueve a caja siguiente; fallar regresa a caja 1.
 * Progreso persistido en localStorage por cardId.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState, useMemo } from "react";
import { useConfirm } from "../../contexts.jsx";
import { Btn, Card, I, Sel, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { TARJETAS_SPACED, TEMAS_TARJETAS } from "../../data/aprenderContent.js";

const LS_KEY = "ns_aprender_leitner";
const BOX_INTERVALS = { 1: 1, 2: 2, 3: 4, 4: 7, 5: 15 }; // días

function loadProgress() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || "{}"); }
  catch { return {}; }
}
function saveProgress(p) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(p)); } catch {}
}

function diffDays(a, b) {
  return Math.floor((b - a) / (1000 * 60 * 60 * 24));
}

function isDue(progress, cardId, now = Date.now()) {
  const p = progress[cardId];
  if (!p) return true; // nueva
  const interval = BOX_INTERVALS[p.box] || 1;
  return diffDays(p.lastSeen, now) >= interval;
}

export default function EstudiarPage() {
  const [progress, setProgress] = useState(loadProgress);
  const [tema, setTema] = useState("");
  const [dificultad, setDificultad] = useState("");
  const [reveal, setReveal] = useState(false);
  const [idx, setIdx] = useState(0);
  const confirm = useConfirm();

  useEffect(() => { saveProgress(progress); }, [progress]);

  const pool = useMemo(() => TARJETAS_SPACED.filter(t =>
    (!tema || t.tema === tema) && (!dificultad || t.dificultad === dificultad)
  ), [tema, dificultad]);

  const dueCards = useMemo(
    () => pool.filter(c => isDue(progress, c.id)),
    [pool, progress]
  );

  const current = dueCards[idx];

  const responder = (acerto) => {
    if (!current) return;
    const p = progress[current.id] || { box: 1, lastSeen: 0, totalSeen: 0, totalCorrect: 0 };
    const newBox = acerto ? Math.min(5, p.box + 1) : 1;
    setProgress(prev => ({
      ...prev,
      [current.id]: {
        box: newBox,
        lastSeen: Date.now(),
        totalSeen: p.totalSeen + 1,
        totalCorrect: p.totalCorrect + (acerto ? 1 : 0),
      },
    }));
    setReveal(false);
    setIdx(i => i + 1);
  };

  const reset = async () => {
    if (!(await confirm("¿Reiniciar progreso de todas las tarjetas?"))) return;
    setProgress({});
    setIdx(0);
    setReveal(false);
  };

  /* Estadísticas globales */
  const stats = useMemo(() => {
    const total = TARJETAS_SPACED.length;
    const dominadas = Object.values(progress).filter(p => p.box >= 4).length;
    const vistas = Object.keys(progress).length;
    return { total, dominadas, vistas };
  }, [progress]);

  return (
    <>
      <TopBar title="Estudiar — Tarjetas espaciadas" />
      <main className="p-8 max-w-7xl mx-auto space-y-5">
        <div className="flex items-center gap-3 mb-2">
          <I name="psychology" style={{ color: TEAL, fontSize: 28 }} />
          <div className="flex-1">
            <h2 className="ns-serif text-xl font-bold">Tarjetas con repetición espaciada</h2>
            <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
              {stats.vistas}/{stats.total} vistas · {stats.dominadas} bien aprendidas (nivel 4+) ·
              repaso en 5 niveles
            </p>
          </div>
          <Btn variant="ghost" onClick={reset} className="text-xs">
            <I name="restart_alt" className="mr-1" />Reiniciar
          </Btn>
        </div>

        <Card className="p-4 flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[150px]">
            <label className="ns-eyebrow block mb-1">Tema</label>
            <Sel value={tema} onChange={e => { setTema(e.target.value); setIdx(0); }}>
              <option value="">Todos</option>
              {TEMAS_TARJETAS.map(t => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
            </Sel>
          </div>
          <div className="flex-1 min-w-[150px]">
            <label className="ns-eyebrow block mb-1">Dificultad</label>
            <Sel value={dificultad} onChange={e => { setDificultad(e.target.value); setIdx(0); }}>
              <option value="">Todas</option>
              <option value="facil">Fácil</option>
              <option value="media">Media</option>
              <option value="dificil">Difícil</option>
            </Sel>
          </div>
          <div className="text-xs px-3 py-2 rounded" style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
            <strong style={{ color: TEAL }}>{dueCards.length}</strong> tarjeta(s) lista(s) para revisar
          </div>
        </Card>

        {!current && dueCards.length === 0 && (
          <Card className="p-12 text-center">
            <I name="celebration" className="text-5xl mb-3" style={{ color: TEAL }} />
            <h3 className="font-bold ns-serif text-lg mb-1">¡No hay tarjetas pendientes!</h3>
            <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
              Vuelve mañana para las tarjetas que tocan según tu calendario de repaso.
            </p>
          </Card>
        )}

        {current && (
          <Card className="p-8 min-h-[400px] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded font-bold"
                  style={{ background: `${TEAL}15`, color: TEAL }}>
                  {current.tema?.replace(/_/g, " ")}
                </span>
                <span className="text-[10px] uppercase tracking-wider"
                  style={{ color: current.dificultad === "facil" ? "#10b981" : current.dificultad === "media" ? "#f59e0b" : "#dc2626" }}>
                  {current.dificultad}
                </span>
              </div>
              <span className="ns-mono text-xs" style={{ color: "var(--ns-muted)" }}>
                {idx + 1} / {dueCards.length}
              </span>
            </div>

            {/* Anverso */}
            <div className="flex-1 flex items-center justify-center px-4 text-center">
              <p className="ns-serif text-xl leading-relaxed" style={{ color: "var(--ns-text)" }}>
                {current.anverso}
              </p>
            </div>

            {/* Reverso (oculto hasta clic) */}
            {reveal && (
              <div className="mt-6 p-5 rounded-lg border-l-[3px]" style={{ borderColor: TEAL, background: "var(--ns-subtle)" }}>
                <p className="ns-eyebrow mb-2" style={{ color: TEAL }}>Respuesta</p>
                <p className="text-sm leading-relaxed" style={{ color: "var(--ns-text)" }}>{current.reverso}</p>
                {current.fuente && (
                  <p className="text-[10px] ns-serif-italic mt-3 pt-3 border-t" style={{ color: "var(--ns-muted)", borderColor: "var(--ns-card-b)" }}>
                    Fuente: {current.fuente}
                  </p>
                )}
              </div>
            )}

            {/* Controles */}
            <div className="mt-6 flex justify-center gap-3">
              {!reveal ? (
                <Btn onClick={() => setReveal(true)} style={{ background: TEAL, color: "white", borderColor: TEAL, padding: "12px 32px" }}>
                  <I name="visibility" className="mr-1.5" />Mostrar respuesta
                </Btn>
              ) : (
                <>
                  <Btn onClick={() => responder(false)} style={{ borderColor: "#dc2626", color: "#dc2626" }}>
                    <I name="close" className="mr-1" />Fallé
                  </Btn>
                  <Btn onClick={() => responder(true)} style={{ background: TEAL, color: "white", borderColor: TEAL }}>
                    <I name="check" className="mr-1" />Acerté
                  </Btn>
                </>
              )}
            </div>

            {progress[current.id] && (
              <p className="text-[10px] text-center mt-4" style={{ color: "var(--ns-muted)" }}>
                Nivel de repaso: <strong>{progress[current.id].box}/5</strong>
                {" · "}
                Aciertos: {progress[current.id].totalCorrect}/{progress[current.id].totalSeen}
              </p>
            )}
          </Card>
        )}
      </main>
    </>
  );
}
