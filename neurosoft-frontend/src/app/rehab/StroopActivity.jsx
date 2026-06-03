/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/StroopActivity.jsx — Test de Stroop interactivo
 * ───────────────────────────────────────────────────────────────────────
 * Mide control inhibitorio y resistencia a la interferencia.
 *
 * Mecánica:
 *   1. Aparece una palabra (ROJO/AZUL/VERDE/AMARILLO) en algún color de
 *      tinta, congruente o incongruente con el significado.
 *   2. El paciente debe elegir el COLOR DE LA TINTA, no la palabra.
 *   3. Se mide tiempo de reacción y aciertos/errores.
 *   4. Al final, score = aciertos×100/trials, RT promedio en ms.
 *
 * Props:
 *   • params       { trials, isi_ms, congruency_ratio }
 *   • onFinish(result)   se llama con el resultado al terminar
 *   • onCancel()         abandono manual
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useMemo, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const COLOR_LABELS = {
  ROJO: "#dc2626",
  AZUL: "#2563eb",
  VERDE: "#10b981",
  AMARILLO: "#d97706",
};
const COLOR_NAMES = Object.keys(COLOR_LABELS);

const generateTrials = (n, congruencyRatio) => {
  const trials = [];
  for (let i = 0; i < n; i++) {
    const word = COLOR_NAMES[Math.floor(Math.random() * COLOR_NAMES.length)];
    const congruent = Math.random() < congruencyRatio;
    let ink;
    if (congruent) {
      ink = word;
    } else {
      const others = COLOR_NAMES.filter((c) => c !== word);
      ink = others[Math.floor(Math.random() * others.length)];
    }
    trials.push({ word, ink, congruent });
  }
  return trials;
};

export default function StroopActivity({
  params = {},
  onFinish,
  onCancel,
}) {
  const trials = params.trials ?? 30;
  const isiMs = params.isi_ms ?? 1500;
  const congruencyRatio = params.congruency_ratio ?? 0.5;

  const trialsRef = useRef(generateTrials(trials, congruencyRatio));
  const [phase, setPhase] = useState("intro"); // intro | running | done
  const [idx, setIdx] = useState(0);
  const [hits, setHits] = useState(0);
  const [errors, setErrors] = useState(0);
  const [rts, setRts] = useState([]);
  const [showFeedback, setShowFeedback] = useState(null); // 'ok' | 'err' | null
  const trialStartRef = useRef(0);

  const current = trialsRef.current[idx];
  const remaining = trialsRef.current.length - idx;

  /* Cuando se monta el trial activo, guardamos su timestamp inicial */
  useEffect(() => {
    if (phase === "running") {
      trialStartRef.current = performance.now();
      setShowFeedback(null);
    }
  }, [phase, idx]);

  const handleAnswer = (chosenInk) => {
    if (phase !== "running" || !current) return;
    const rt = performance.now() - trialStartRef.current;
    const correct = chosenInk === current.ink;
    setRts((rs) => [...rs, rt]);
    if (correct) {
      setHits((h) => h + 1);
      setShowFeedback("ok");
    } else {
      setErrors((e) => e + 1);
      setShowFeedback("err");
    }
    /* Pequeño delay de feedback antes del siguiente */
    setTimeout(() => {
      const nextIdx = idx + 1;
      if (nextIdx >= trialsRef.current.length) {
        finish(
          correct ? hits + 1 : hits,
          correct ? errors : errors + 1,
          [...rts, rt]
        );
      } else {
        setIdx(nextIdx);
      }
    }, Math.min(400, isiMs / 3));
  };

  const finish = (finalHits, finalErrors, finalRts) => {
    const totalTrials = trialsRef.current.length;
    const accuracy = totalTrials ? Math.round((finalHits / totalTrials) * 100) : 0;
    const rtAvg = finalRts.length
      ? Math.round(finalRts.reduce((a, b) => a + b, 0) / finalRts.length)
      : null;
    const result = {
      score: accuracy,
      aciertos: finalHits,
      errores: finalErrors,
      total_trials: totalTrials,
      rt_avg_ms: rtAvg,
      rt_min_ms: finalRts.length ? Math.round(Math.min(...finalRts)) : null,
      rt_max_ms: finalRts.length ? Math.round(Math.max(...finalRts)) : null,
      params: { trials, isi_ms: isiMs, congruency_ratio: congruencyRatio },
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
          <I name="psychology" className="text-4xl" />
        </div>
        <h3 className="text-2xl font-extrabold mb-3">Stroop — Inhibición</h3>
        <p className="text-sm leading-relaxed mb-6" style={{ color: "var(--ns-muted)" }}>
          Verás palabras escritas en distintos colores. Tu tarea es indicar el
          <strong> COLOR DE LA TINTA </strong>
          en que está escrita la palabra, NO la palabra que dice.
        </p>
        <div className="space-y-3 mb-8 text-left">
          <div className="rounded-xl p-4" style={{ background: "var(--ns-subtle)" }}>
            <p className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: TEAL }}>
              Ejemplo
            </p>
            <p className="text-3xl font-extrabold" style={{ color: COLOR_LABELS.AZUL }}>
              ROJO
            </p>
            <p className="text-xs mt-2" style={{ color: "var(--ns-muted)" }}>
              ↑ La respuesta correcta es <strong>AZUL</strong> (color de la tinta), no rojo.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs" style={{ color: "var(--ns-muted)" }}>
            <div className="flex items-center gap-2">
              <I name="speed" style={{ color: TEAL }} />
              <span>Responde tan rápido como puedas</span>
            </div>
            <div className="flex items-center gap-2">
              <I name="check_circle" style={{ color: TEAL }} />
              <span>Sin equivocarte</span>
            </div>
            <div className="flex items-center gap-2">
              <I name="timer" style={{ color: TEAL }} />
              <span>{trials} ensayos (~{Math.ceil((trials * 2) / 60)} min)</span>
            </div>
            <div className="flex items-center gap-2">
              <I name="touch_app" style={{ color: TEAL }} />
              <span>Toca el botón del color correcto</span>
            </div>
          </div>
        </div>
        <div className="flex justify-center gap-3">
          {onCancel && (
            <Btn v="outline" onClick={onCancel}>
              Cancelar
            </Btn>
          )}
          <Btn onClick={() => setPhase("running")}>
            <I name="play_arrow" />
            Comenzar
          </Btn>
        </div>
      </Card>
    );
  }

  /* ─── DONE ──────────────────────────────────────────────── */
  if (phase === "done") {
    const total = trialsRef.current.length;
    const accuracy = total ? Math.round((hits / total) * 100) : 0;
    const rtAvg = rts.length
      ? Math.round(rts.reduce((a, b) => a + b, 0) / rts.length)
      : null;
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
          style={{ background: "#10b98115", color: "#10b981" }}
        >
          <I name="check_circle" fill className="text-4xl" />
        </div>
        <h3 className="text-2xl font-extrabold mb-2">¡Sesión completada!</h3>
        <p className="text-sm mb-8" style={{ color: "var(--ns-muted)" }}>
          Tus resultados se guardaron en el expediente.
        </p>
        <div className="grid grid-cols-3 gap-4 mb-8">
          <Card className="p-5">
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>
              {accuracy}%
            </p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Aciertos
            </p>
          </Card>
          <Card className="p-5">
            <p className="text-3xl font-extrabold">{hits}/{total}</p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Correctas
            </p>
          </Card>
          <Card className="p-5">
            <p className="text-3xl font-extrabold">{rtAvg}<span className="text-base">ms</span></p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              RT promedio
            </p>
          </Card>
        </div>
      </Card>
    );
  }

  /* ─── RUNNING ───────────────────────────────────────────── */
  /* §H3-fix: guard div/0 cuando aún no se inicializó la lista. */
  const progress = trialsRef.current.length > 0
    ? (idx / trialsRef.current.length) * 100 : 0;
  return (
    <div className="max-w-2xl mx-auto">
      {/* Barra de progreso */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
            Ensayo {idx + 1} de {trialsRef.current.length}
          </span>
          <span className="text-xs font-bold" style={{ color: TEAL }}>
            {hits} correctas · {errors} errores
          </span>
        </div>
        <div className="h-2 rounded-full" style={{ background: "var(--ns-subtle)" }}>
          <div
            className="h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%`, background: TEAL }}
          />
        </div>
      </div>

      {/* Estímulo */}
      <Card
        className="p-12 text-center mb-6 min-h-[240px] flex items-center justify-center"
        style={{
          borderColor: showFeedback === "ok" ? "#10b981" : showFeedback === "err" ? "#dc2626" : undefined,
          borderWidth: showFeedback ? 3 : undefined,
          transition: "border-color 200ms",
        }}
      >
        {current && (
          <div className="text-7xl font-extrabold tracking-wider" style={{ color: COLOR_LABELS[current.ink] }}>
            {current.word}
          </div>
        )}
      </Card>

      {/* Botones de respuesta */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {COLOR_NAMES.map((c) => (
          <button
            key={c}
            onClick={() => handleAnswer(c)}
            disabled={!!showFeedback}
            className="px-6 py-5 rounded-2xl font-extrabold text-lg text-white transition-all active:scale-95 hover:-translate-y-0.5 disabled:opacity-50"
            style={{
              background: COLOR_LABELS[c],
              boxShadow: `0 8px 20px -4px ${COLOR_LABELS[c]}50`,
            }}
          >
            {c}
          </button>
        ))}
      </div>

      <p className="text-xs text-center" style={{ color: "var(--ns-muted)" }}>
        Recuerda: elige el <strong>color de la tinta</strong>, no la palabra.
      </p>
    </div>
  );
}
