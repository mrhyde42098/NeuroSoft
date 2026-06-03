/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/EkmanRecognitionActivity.jsx — Reconocimiento de
 * expresiones faciales (Ekman 6 básicas)
 * ───────────────────────────────────────────────────────────────────────
 * Entrenamiento de cognición social. Se presenta una cara esquemática
 * con una emoción y el paciente elige la etiqueta correcta entre 6
 * opciones (Alegría, Tristeza, Ira, Miedo, Sorpresa, Asco).
 *
 * Útil para:
 *   - TEA (cognición social)
 *   - TCE frontal (déficit emocional)
 *   - Esquizofrenia
 *
 * Score:
 *   • aciertos / N
 *   • RT promedio
 *
 * Props:
 *   • params      { trials }
 *   • onFinish(result)
 *   • onCancel()
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const EMOTIONS = [
  { id: "alegria",   label: "Alegría",  color: "#10b981" },
  { id: "tristeza",  label: "Tristeza", color: "#3b82f6" },
  { id: "ira",       label: "Ira",      color: "#dc2626" },
  { id: "miedo",     label: "Miedo",    color: "#f59e0b" },
  { id: "sorpresa",  label: "Sorpresa", color: "#8b5cf6" },
  { id: "asco",      label: "Asco",     color: "#84cc16" },
];

function EkmanFace({ emotion, size = 160 }) {
  const cx = size / 2, cy = size / 2;
  const r = size * 0.32;
  const target = EMOTIONS.find((e) => e.id === emotion) || EMOTIONS[0];
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={cx} cy={cy} r={r} fill="#fde68a" stroke={target.color} strokeWidth="3" />
      {/* Eyes */}
      {emotion === "sorpresa" ? (
        <>
          <circle cx={cx - r * 0.4} cy={cy - r * 0.25} r={r * 0.18} fill="#1e293b" />
          <circle cx={cx + r * 0.4} cy={cy - r * 0.25} r={r * 0.18} fill="#1e293b" />
        </>
      ) : emotion === "ira" ? (
        <>
          <line x1={cx - r * 0.6} y1={cy - r * 0.4} x2={cx - r * 0.2} y2={cy - r * 0.2} stroke="#1e293b" strokeWidth="3" />
          <line x1={cx + r * 0.6} y1={cy - r * 0.4} x2={cx + r * 0.2} y2={cy - r * 0.2} stroke="#1e293b" strokeWidth="3" />
        </>
      ) : (
        <>
          <circle cx={cx - r * 0.4} cy={cy - r * 0.25} r={r * 0.08} fill="#1e293b" />
          <circle cx={cx + r * 0.4} cy={cy - r * 0.25} r={r * 0.08} fill="#1e293b" />
        </>
      )}
      {/* Mouth */}
      {emotion === "alegria" && (
        <path d={`M${cx - r * 0.45} ${cy + r * 0.25} Q${cx} ${cy + r * 0.7} ${cx + r * 0.45} ${cy + r * 0.25}`}
              stroke="#1e293b" strokeWidth="3" fill="none" />
      )}
      {emotion === "tristeza" && (
        <path d={`M${cx - r * 0.45} ${cy + r * 0.55} Q${cx} ${cy + r * 0.1} ${cx + r * 0.45} ${cy + r * 0.55}`}
              stroke="#1e293b" strokeWidth="3" fill="none" />
      )}
      {emotion === "ira" && (
        <line x1={cx - r * 0.45} y1={cy + r * 0.45} x2={cx + r * 0.45} y2={cy + r * 0.45}
              stroke="#1e293b" strokeWidth="3" />
      )}
      {emotion === "miedo" && (
        <ellipse cx={cx} cy={cy + r * 0.4} rx={r * 0.25} ry={r * 0.18} fill="#1e293b" />
      )}
      {emotion === "sorpresa" && (
        <circle cx={cx} cy={cy + r * 0.4} r={r * 0.18} fill="#1e293b" />
      )}
      {emotion === "asco" && (
        <path d={`M${cx - r * 0.35} ${cy + r * 0.55} Q${cx} ${cy + r * 0.25} ${cx + r * 0.35} ${cy + r * 0.55}`}
              stroke="#1e293b" strokeWidth="3" fill="none" />
      )}
    </svg>
  );
}

function makeTrials(n) {
  const trials = [];
  for (let i = 0; i < n; i++) {
    const emotion = EMOTIONS[i % EMOTIONS.length];
    trials.push({ idx: i, target: emotion.id });
  }
  /* Shuffle ligeramente */
  for (let i = trials.length - 1; i > 0; i--) {
    const j = (i * 7) % trials.length;
    [trials[i], trials[j]] = [trials[j], trials[i]];
  }
  return trials;
}

export default function EkmanRecognitionActivity({
  params = {},
  onFinish,
  onCancel,
}) {
  const N = params.trials ?? 12;
  const trialsRef = useRef(makeTrials(N));
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

  const respond = (chosen) => {
    if (phase !== "running" || feedback) return;
    const trial = trialsRef.current[idx];
    const ok = chosen === trial.target;
    const rt = Date.now() - startedAt.current;
    setRts((r) => [...r, rt]);
    setFeedback({ ok, chosen, target: trial.target });
    if (ok) setHits((h) => h + 1);
    setTimeout(() => {
      setFeedback(null);
      const next = idx + 1;
      if (next >= N) finalize();
      else setIdx(next);
    }, 900);
  };

  const finalize = () => {
    setPhase("done");
    if (onFinish) {
      const meanRt = rts.length ? Math.round(rts.reduce((s, x) => s + x, 0) / rts.length) : 0;
      onFinish({
        accuracy: hits,
        total_trials: N,
        mean_rt_ms: meanRt,
        accuracy_pct: Math.round((hits / N) * 100),
      });
    }
  };

  if (phase === "intro") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-5">
        <div className="w-20 h-20 mx-auto rounded-2xl flex items-center justify-center"
             style={{ background: `${TEAL}15`, color: TEAL }}>
          <I name="emoji_emotions" className="text-4xl" />
        </div>
        <h2 className="text-2xl font-bold">Reconocimiento de Emociones</h2>
        <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
          Entrenamiento de cognición social (Ekman 6 emociones básicas).
          Verá una cara y deberá identificar la emoción que expresa.
        </p>
        <div className="flex justify-center my-3">
          <EkmanFace emotion="alegria" size={120} />
        </div>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          {N} ensayos. Útil en rehabilitación de TEA, TCE frontal y esquizofrenia.
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

  const trial = trialsRef.current[idx];
  return (
    <Card className="p-6 max-w-3xl mx-auto space-y-4">
      <div className="flex justify-between text-xs" style={{ color: "var(--ns-muted)" }}>
        <span>Ensayo {idx + 1} de {N}</span>
        <span>Aciertos: {hits}</span>
      </div>
      <div className="flex justify-center mb-2">
        <EkmanFace emotion={trial.target} size={180} />
      </div>
      <p className="text-center text-sm font-bold mb-2">¿Qué emoción expresa esta cara?</p>
      <div className="grid grid-cols-3 gap-3">
        {EMOTIONS.map((e) => {
          const isChosen = feedback?.chosen === e.id;
          const isTarget = feedback?.target === e.id;
          let bg = "var(--ns-card)", border = "var(--ns-card-b)";
          if (feedback) {
            if (isTarget) { bg = "#dcfce7"; border = "#10b981"; }
            else if (isChosen && !feedback.ok) { bg = "#fee2e2"; border = "#dc2626"; }
          }
          return (
            <button key={e.id}
              onClick={() => respond(e.id)}
              disabled={feedback !== null}
              className="px-4 py-3 rounded-xl border-2 font-bold text-sm transition-all hover:scale-105 disabled:cursor-not-allowed"
              style={{ background: bg, borderColor: border, color: e.color }}
            >
              {e.label}
            </button>
          );
        })}
      </div>
      <div className="flex justify-end">
        <Btn v="outline" onClick={onCancel} className="text-xs">Detener</Btn>
      </div>
    </Card>
  );
}
