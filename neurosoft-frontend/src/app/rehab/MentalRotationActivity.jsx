/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/MentalRotationActivity.jsx — Rotación mental
 * ───────────────────────────────────────────────────────────────────────
 * Tarea clásica de Shepard & Metzler (1971) adaptada como entrenamiento
 * cognitivo. Mide y entrena habilidad visoespacial (rotación de
 * imágenes mentales).
 *
 * Mecánica:
 *   1. En cada ensayo se presenta UN estímulo modelo (figura de
 *      referencia) y dos opciones rotadas.
 *   2. UNA opción es la misma figura rotada; la otra es su imagen
 *      espejo (no se puede rotar para igualarla).
 *   3. El paciente debe seleccionar la igualada-por-rotación.
 *   4. Se registra acierto + tiempo de reacción.
 *
 * Score:
 *   • aciertos / N
 *   • tiempo de reacción promedio
 *   • índice = aciertos × 100 / N − (RT_promedio_ms / 100)
 *
 * Props:
 *   • params      { trials, isi_ms, levels: [angles] }
 *   • onFinish(result)
 *   • onCancel()
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, _useMemo, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* Figura asimétrica simple: una "L" pintada en SVG. Puede rotarse y
 * espejarse para construir los 2 estímulos del ensayo. */
function LShape({ rotation = 0, mirror = false, size = 120, color = "#0D9488" }) {
  const transform = `rotate(${rotation}, 60, 60) ${mirror ? "scale(-1, 1) translate(-120, 0)" : ""}`;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120">
      <g transform={transform} fill={color} stroke="#1e293b" strokeWidth="1.5">
        {/* L-shape */}
        <polygon points="35,20 65,20 65,75 90,75 90,100 35,100" />
        <circle cx="50" cy="35" r="4" fill="#fbbf24" />
      </g>
    </svg>
  );
}

const DEFAULT_ANGLES = [45, 90, 135, 180];

function makeTrials(n, angles) {
  const trials = [];
  for (let i = 0; i < n; i++) {
    const angle = angles[i % angles.length];
    /* La opción correcta está rotada por `angle`; la opción incorrecta
     * es la imagen espejo rotada por un ángulo arbitrario. */
    const correctOnLeft = i % 2 === 0;
    trials.push({
      idx: i,
      angle,
      correctOnLeft,
      mirror_angle: (angle + 90) % 360,
    });
  }
  return trials;
}

export default function MentalRotationActivity({
  params = {},
  onFinish,
  onCancel,
}) {
  const N = params.trials ?? 12;
  const angles = params.levels || DEFAULT_ANGLES;

  const trialsRef = useRef(makeTrials(N, angles));
  const [phase, setPhase] = useState("intro");
  const [idx, setIdx] = useState(0);
  const [hits, setHits] = useState(0);
  const [rts, setRts] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const startedAt = useRef(0);

  useEffect(() => {
    if (phase === "running") startedAt.current = Date.now();
  }, [phase, idx]);

  const start = () => { setIdx(0); setHits(0); setRts([]); setPhase("running"); };

  const respond = (chooseLeft) => {
    if (phase !== "running") return;
    const trial = trialsRef.current[idx];
    const ok = (chooseLeft && trial.correctOnLeft) || (!chooseLeft && !trial.correctOnLeft);
    const rt = Date.now() - startedAt.current;
    setRts((r) => [...r, rt]);
    setFeedback(ok ? "ok" : "miss");
    if (ok) setHits((h) => h + 1);
    setTimeout(() => {
      setFeedback(null);
      const next = idx + 1;
      if (next >= N) finalize();
      else setIdx(next);
    }, 600);
  };

  const finalize = () => {
    setPhase("done");
    if (onFinish) {
      const meanRt = rts.length ? Math.round(rts.reduce((s, x) => s + x, 0) / rts.length) : 0;
      const score = Math.max(0, Math.round((hits * 100) / N - meanRt / 100));
      onFinish({
        accuracy: hits,
        total_trials: N,
        mean_rt_ms: meanRt,
        score,
      });
    }
  };

  if (phase === "intro") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-5">
        <div className="w-20 h-20 mx-auto rounded-2xl flex items-center justify-center"
             style={{ background: `${TEAL}15`, color: TEAL }}>
          <I name="screen_rotation" className="text-4xl" />
        </div>
        <h2 className="text-2xl font-bold">Rotación Mental</h2>
        <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
          Entrenamiento de habilidad visoespacial (Shepard &amp; Metzler 1971).
          Verá una figura modelo y dos opciones; elija la que sea la MISMA
          figura rotada (no su imagen espejo).
        </p>
        <div className="flex justify-center gap-6 my-3">
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase mb-1" style={{ color: "var(--ns-muted)" }}>Modelo</p>
            <LShape rotation={0} size={100} />
          </div>
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase mb-1" style={{ color: "var(--ns-muted)" }}>Rotada (igual)</p>
            <LShape rotation={90} size={100} />
          </div>
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase mb-1 text-red-600">Espejo (NO igual)</p>
            <LShape rotation={0} mirror size={100} color="#dc2626" />
          </div>
        </div>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          Tendrá {N} ensayos. Conteste tan rápido como pueda manteniendo precisión.
        </p>
        <div className="flex gap-3 justify-center">
          <Btn v="outline" onClick={onCancel}>Cancelar</Btn>
          <Btn onClick={start}><I name="play_arrow" />Iniciar</Btn>
        </div>
      </Card>
    );
  }

  if (phase === "done") {
    const meanRt = rts.length ? Math.round(rts.reduce((s, x) => s + x, 0) / rts.length) : 0;
    return (
      <Card className="p-8 max-w-xl mx-auto text-center space-y-4">
        <I name="check_circle" fill className="text-5xl" style={{ color: TEAL }} />
        <h3 className="text-2xl font-bold">Sesión completada</h3>
        <div className="grid grid-cols-3 gap-4 my-4">
          <div>
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{hits}/{N}</p>
            <p className="text-xs font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Aciertos</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{Math.round((hits / N) * 100)}%</p>
            <p className="text-xs font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Precisión</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{(meanRt / 1000).toFixed(1)}s</p>
            <p className="text-xs font-bold uppercase" style={{ color: "var(--ns-muted)" }}>RT promedio</p>
          </div>
        </div>
      </Card>
    );
  }

  /* phase === "running" */
  const trial = trialsRef.current[idx];
  return (
    <Card className="p-6 max-w-3xl mx-auto space-y-4">
      <div className="flex justify-between text-xs" style={{ color: "var(--ns-muted)" }}>
        <span>Ensayo {idx + 1} de {N}</span>
        <span>Aciertos: {hits}</span>
      </div>
      <div className="flex justify-center mb-2">
        <div className="text-center">
          <p className="text-[10px] font-bold uppercase mb-1" style={{ color: "var(--ns-muted)" }}>Modelo</p>
          <LShape rotation={0} size={140} />
        </div>
      </div>
      <p className="text-center text-sm font-bold mb-2">¿Cuál es la MISMA figura rotada?</p>
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => respond(true)}
          disabled={feedback !== null}
          className={`p-4 rounded-2xl border-2 transition-all hover:scale-105 ${feedback === "ok" && trial.correctOnLeft ? "bg-emerald-50 border-emerald-500" : feedback === "miss" && !trial.correctOnLeft ? "bg-red-50 border-red-500" : ""}`}
          style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}
        >
          <LShape rotation={trial.correctOnLeft ? trial.angle : trial.mirror_angle}
                  mirror={!trial.correctOnLeft} size={140} />
        </button>
        <button
          onClick={() => respond(false)}
          disabled={feedback !== null}
          className={`p-4 rounded-2xl border-2 transition-all hover:scale-105 ${feedback === "ok" && !trial.correctOnLeft ? "bg-emerald-50 border-emerald-500" : feedback === "miss" && trial.correctOnLeft ? "bg-red-50 border-red-500" : ""}`}
          style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}
        >
          <LShape rotation={!trial.correctOnLeft ? trial.angle : trial.mirror_angle}
                  mirror={trial.correctOnLeft} size={140} />
        </button>
      </div>
      <div className="flex justify-end">
        <Btn v="outline" onClick={onCancel} className="text-xs">Detener</Btn>
      </div>
    </Card>
  );
}
