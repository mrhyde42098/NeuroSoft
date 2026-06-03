/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/NBackActivity.jsx — Test N-back visuoespacial
 * ───────────────────────────────────────────────────────────────────────
 * Mide memoria de trabajo y mantenimiento on-line.
 *
 * Mecánica:
 *   1. Aparece un cuadro iluminado en una grilla 3×3 durante isi_ms.
 *   2. El paciente debe presionar el botón MATCH cuando la posición
 *      actual coincida con la que apareció N pasos atrás.
 *   3. Al final: aciertos (hits), falsos positivos, omisiones, score.
 *
 * Props:
 *   • params       { n, trials, isi_ms }
 *   • onFinish(result), onCancel()
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const POSITIONS = 9; // grilla 3x3

const generateSequence = (trials, n) => {
  /* Sembramos `targetRatio` ≈ 30% de coincidencias */
  const targetRatio = 0.3;
  const seq = [];
  for (let i = 0; i < trials; i++) {
    if (i >= n && Math.random() < targetRatio) {
      seq.push(seq[i - n]); // garantizar match
    } else {
      seq.push(Math.floor(Math.random() * POSITIONS));
    }
  }
  return seq;
};

export default function NBackActivity({ params = {}, onFinish, onCancel }) {
  const n = params.n ?? 1;
  const trials = params.trials ?? 20;
  const isiMs = params.isi_ms ?? 2000;

  const sequenceRef = useRef(generateSequence(trials, n));
  const [phase, setPhase] = useState("intro"); // intro | running | done
  const [idx, setIdx] = useState(-1);
  const [hits, setHits] = useState(0); // aciertos
  const [fps, setFps] = useState(0); // falsos positivos
  const [omis, setOmis] = useState(0); // omisiones
  const [responded, setResponded] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const timerRef = useRef(null);

  /* Avance automático cada isi_ms */
  useEffect(() => {
    if (phase !== "running") return;
    if (idx >= sequenceRef.current.length - 1) {
      finish();
      return;
    }
    timerRef.current = setTimeout(() => {
      // antes de avanzar, evaluar omisión si era target
      if (idx >= n) {
        const wasMatch = sequenceRef.current[idx] === sequenceRef.current[idx - n];
        if (wasMatch && !responded) setOmis((o) => o + 1);
      }
      setResponded(false);
      setFeedback(null);
      setIdx((i) => i + 1);
    }, isiMs);
    return () => clearTimeout(timerRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, idx]);

  const handleMatch = () => {
    if (responded || idx < n) return;
    const wasMatch = sequenceRef.current[idx] === sequenceRef.current[idx - n];
    if (wasMatch) {
      setHits((h) => h + 1);
      setFeedback("ok");
    } else {
      setFps((f) => f + 1);
      setFeedback("err");
    }
    setResponded(true);
  };

  const finish = () => {
    clearTimeout(timerRef.current);
    const total = sequenceRef.current.length;
    const totalTargets = sequenceRef.current.filter(
      (v, i) => i >= n && v === sequenceRef.current[i - n]
    ).length;
    const accuracy = totalTargets ? Math.round((hits / totalTargets) * 100) : 0;
    /* Score combina hits y penaliza falsos positivos: score = hits − 0.5×fps,
     * normalizado a 0..100 */
    const rawScore = hits - 0.5 * fps;
    const maxScore = totalTargets;
    const score = maxScore
      ? Math.max(0, Math.round((rawScore / maxScore) * 100))
      : 0;
    const result = {
      score,
      aciertos: hits,
      errores: fps,
      omisiones: omis,
      target_count: totalTargets,
      total_trials: total,
      accuracy_pct: accuracy,
      params: { n, trials, isi_ms: isiMs },
    };
    setPhase("done");
    if (onFinish) onFinish(result);
  };

  /* ─── INTRO ─────────────────────────────────────────────── */
  if (phase === "intro") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
          style={{ background: `${TEAL}15`, color: TEAL }}
        >
          <I name="grid_view" className="text-4xl" />
        </div>
        <h3 className="text-2xl font-extrabold mb-3">N-back · Memoria de trabajo</h3>
        <p className="text-sm leading-relaxed mb-6" style={{ color: "var(--ns-muted)" }}>
          Verás cuadros iluminados en una grilla 3×3, uno tras otro.
          Presiona <strong>MATCH</strong> cuando la posición actual coincida con
          la posición que apareció hace <strong>{n} paso(s) atrás</strong>.
        </p>
        <div className="rounded-xl p-4 mb-8" style={{ background: "var(--ns-subtle)" }}>
          <div className="flex items-center justify-center gap-3 text-xs" style={{ color: "var(--ns-muted)" }}>
            <I name="speed" />
            <span>Velocidad: {isiMs / 1000} s por estímulo</span>
            <span>•</span>
            <I name="timer" />
            <span>{trials} ensayos</span>
          </div>
        </div>
        <div className="flex justify-center gap-3">
          {onCancel && (
            <Btn v="outline" onClick={onCancel}>
              Cancelar
            </Btn>
          )}
          <Btn onClick={() => setPhase("running") || setIdx(0)}>
            <I name="play_arrow" />
            Comenzar
          </Btn>
        </div>
      </Card>
    );
  }

  /* ─── DONE ──────────────────────────────────────────────── */
  if (phase === "done") {
    const totalTargets = sequenceRef.current.filter(
      (v, i) => i >= n && v === sequenceRef.current[i - n]
    ).length;
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
          style={{ background: "#10b98115", color: "#10b981" }}
        >
          <I name="check_circle" fill className="text-4xl" />
        </div>
        <h3 className="text-2xl font-extrabold mb-2">¡Sesión completada!</h3>
        <div className="grid grid-cols-3 gap-4 mt-8">
          <Card className="p-5">
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{hits}</p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Aciertos / {totalTargets}
            </p>
          </Card>
          <Card className="p-5">
            <p className="text-3xl font-extrabold text-red-500">{fps}</p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Falsos positivos
            </p>
          </Card>
          <Card className="p-5">
            <p className="text-3xl font-extrabold text-orange-500">{omis}</p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Omisiones
            </p>
          </Card>
        </div>
      </Card>
    );
  }

  /* ─── RUNNING ───────────────────────────────────────────── */
  const cur = sequenceRef.current[idx];
  /* §H3-fix: guard div/0 cuando aún no se inicializó la secuencia. */
  const progress = sequenceRef.current.length > 0
    ? (idx / sequenceRef.current.length) * 100 : 0;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
            Ensayo {idx + 1} de {sequenceRef.current.length} · n={n}
          </span>
          <span className="text-xs font-bold" style={{ color: TEAL }}>
            ✓ {hits} · ✗ {fps}
          </span>
        </div>
        <div className="h-2 rounded-full" style={{ background: "var(--ns-subtle)" }}>
          <div
            className="h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%`, background: TEAL }}
          />
        </div>
      </div>

      {/* Grilla 3x3 */}
      <Card
        className="p-8 mb-6"
        style={{
          borderColor: feedback === "ok" ? "#10b981" : feedback === "err" ? "#dc2626" : undefined,
          borderWidth: feedback ? 3 : undefined,
          transition: "border-color 200ms",
        }}
      >
        <div className="grid grid-cols-3 gap-3 max-w-xs mx-auto">
          {Array.from({ length: POSITIONS }).map((_, i) => (
            <div
              key={i}
              className="aspect-square rounded-2xl transition-all"
              style={{
                background: i === cur ? TEAL : "var(--ns-subtle)",
                boxShadow: i === cur ? "0 8px 20px -4px rgba(13,148,136,0.4)" : "none",
                transform: i === cur ? "scale(1.05)" : "scale(1)",
              }}
            />
          ))}
        </div>
      </Card>

      <div className="text-center">
        <button
          onClick={handleMatch}
          disabled={responded || idx < n}
          className="px-12 py-5 rounded-full text-white font-extrabold text-lg shadow-xl transition-all active:scale-95 hover:-translate-y-0.5 disabled:opacity-40 disabled:cursor-not-allowed"
          style={{ background: TEAL, boxShadow: "0 12px 30px -6px rgba(13,148,136,0.4)" }}
        >
          <I name="check_circle" fill className="mr-2" />
          MATCH
        </button>
        <p className="text-xs mt-4" style={{ color: "var(--ns-muted)" }}>
          {idx < n
            ? `Esperando ${n - idx} estímulo(s) más antes de poder responder...`
            : "Si la posición actual coincide con hace " + n + " paso(s), presiona MATCH"}
        </p>
      </div>
    </div>
  );
}
