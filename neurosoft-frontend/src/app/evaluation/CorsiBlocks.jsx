/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/CorsiBlocks.jsx — Cubos de Corsi (memoria de trabajo visual)
 * ───────────────────────────────────────────────────────────────────────
 * Implementación digital del Corsi Block-Tapping Test (Corsi 1972).
 * Mide span de memoria de trabajo visoespacial.
 *
 * Mecánica clásica:
 *   1. 9 cubos en posiciones irregulares (layout estándar Corsi).
 *   2. El examinador inicia "Mostrar secuencia": los cubos se iluminan
 *      uno a uno (1s ON, 0.5s OFF).
 *   3. El paciente reproduce la secuencia clicando los cubos en el mismo
 *      orden (forward) o en orden inverso (backward).
 *   4. Longitud inicial = 2. Si reproduce correctamente, sube a 3, 4, …
 *      hasta que falle dos ensayos consecutivos a la misma longitud.
 *   5. Score = longitud máxima reproducida correctamente (Corsi span).
 *
 * Modos:
 *   • forward  — reproduce mismo orden (Corsi clásico)
 *   • backward — reproduce orden inverso (variante MT visual)
 *
 * Baremos esperables (Neuronorma Colombia adultos 50-90):
 *   span 5±1 = promedio · ≤3 = bajo · ≥7 = superior
 *
 * Props:
 *   • params      { mode: "forward"|"backward", maxLen: 9 }
 *   • onFinish    (result) → { span, mode, totalTrials, sequence_max }
 *   • onCancel    abandono manual
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, _useMemo, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* Posiciones canónicas Corsi (coordenadas % del lienzo, 9 cubos).
 * Layout reconocido en literatura: 9 bloques distribuidos asimétricamente
 * sobre un tablero rectangular. */
const CORSI_POSITIONS = [
  { id: 0, x: 12, y: 18 },
  { id: 1, x: 78, y: 12 },
  { id: 2, x: 38, y: 22 },
  { id: 3, x: 58, y: 38 },
  { id: 4, x: 22, y: 50 },
  { id: 5, x: 82, y: 52 },
  { id: 6, x: 42, y: 70 },
  { id: 7, x: 14, y: 82 },
  { id: 8, x: 72, y: 80 },
];

/* Genera una secuencia aleatoria sin repeticiones consecutivas. */
function makeSequence(len) {
  const seq = [];
  while (seq.length < len) {
    const next = Math.floor(Math.random() * CORSI_POSITIONS.length);
    if (seq.length === 0 || seq[seq.length - 1] !== next) seq.push(next);
  }
  return seq;
}

export default function CorsiBlocks({
  params = {},
  onFinish,
  onCancel,
}) {
  const mode = params.mode ?? "forward"; // forward | backward
  const maxLen = params.maxLen ?? 9;

  const [phase, setPhase] = useState("intro");
    /* intro · presenting · responding · feedback · done */
  const [seqLen, setSeqLen] = useState(2);
  const [sequence, setSequence] = useState([]);
  const [highlightId, setHighlightId] = useState(null);
  const [response, setResponse] = useState([]);
  const [trialsAtLen, setTrialsAtLen] = useState(0); // 0..2 ensayos por longitud
  const [failsAtLen, setFailsAtLen] = useState(0);
  const [span, setSpan] = useState(0);             // mejor longitud lograda
  const [history, setHistory] = useState([]);      // {len, ok, response, expected}
  const [feedbackOk, setFeedbackOk] = useState(null);
  const presentingRef = useRef(false);

  /* Comparar respuesta del paciente con secuencia esperada */
  const expectedFor = (seq) => mode === "backward" ? [...seq].reverse() : seq;

  /* Reproducir la secuencia visualmente */
  const playSequence = async (seq) => {
    presentingRef.current = true;
    setPhase("presenting");
    for (let i = 0; i < seq.length; i++) {
      setHighlightId(seq[i]);
      await new Promise((r) => setTimeout(r, 900));
      setHighlightId(null);
      await new Promise((r) => setTimeout(r, 350));
      if (!presentingRef.current) return; // cancelado
    }
    presentingRef.current = false;
    setPhase("responding");
  };

  const startTrial = (len) => {
    const seq = makeSequence(len);
    setSequence(seq);
    setResponse([]);
    playSequence(seq);
  };

  /* Iniciar test */
  const begin = () => {
    setSeqLen(2);
    setTrialsAtLen(0);
    setFailsAtLen(0);
    setSpan(0);
    setHistory([]);
    startTrial(2);
  };

  const onCubeClick = (id) => {
    if (phase !== "responding") return;
    const next = [...response, id];
    setResponse(next);
    if (next.length === sequence.length) {
      /* Evaluar */
      const expected = expectedFor(sequence);
      const ok = next.every((v, i) => v === expected[i]);
      setFeedbackOk(ok);
      setHistory((h) => [...h, { len: sequence.length, ok, response: next, expected }]);
      setPhase("feedback");
    }
  };

  /* Avanzar tras feedback automáticamente o por click */
  const continueAfterFeedback = () => {
    const ok = feedbackOk;
    setFeedbackOk(null);
    let nextLen = seqLen;
    let nextTrials = trialsAtLen + 1;
    let nextFails = failsAtLen + (ok ? 0 : 1);
    if (ok) {
      setSpan((s) => Math.max(s, sequence.length));
      /* sube de nivel inmediatamente al primer acierto */
      nextLen = Math.min(seqLen + 1, maxLen);
      nextTrials = 0;
      nextFails = 0;
    } else if (nextFails >= 2) {
      /* dos fallos consecutivos a la misma longitud → terminar */
      finalize();
      return;
    }
    if (nextLen > maxLen) {
      finalize();
      return;
    }
    setSeqLen(nextLen);
    setTrialsAtLen(nextTrials);
    setFailsAtLen(nextFails);
    startTrial(nextLen);
  };

  const finalize = () => {
    presentingRef.current = false;
    setPhase("done");
    if (onFinish) {
      onFinish({
        span,
        mode,
        totalTrials: history.length,
        sequence_max: maxLen,
        history,
      });
    }
  };

  /* Auto-avance del feedback tras 1.2s */
  useEffect(() => {
    if (phase !== "feedback") return;
    const t = setTimeout(continueAfterFeedback, 1200);
    return () => clearTimeout(t);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase]);

  /* Cancelar limpio */
  useEffect(() => () => { presentingRef.current = false; }, []);

  /* ─── Render ─────────────────────────────────────────────── */
  if (phase === "intro") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-5">
        <div className="w-20 h-20 mx-auto rounded-2xl flex items-center justify-center"
             style={{ background: `${TEAL}15`, color: TEAL }}>
          <I name="grid_view" className="text-4xl" />
        </div>
        <h2 className="text-2xl font-bold">Cubos de Corsi — {mode === "backward" ? "Inverso" : "Directo"}</h2>
        <p className="text-sm leading-relaxed" style={{ color: "var(--ns-muted)" }}>
          Observe atentamente la secuencia de cubos que se iluminan. Cuando termine,
          {" "}haga clic en los cubos en {mode === "backward" ? "ORDEN INVERSO" : "EL MISMO ORDEN"} en que se mostraron.
        </p>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          La secuencia comenzará con 2 cubos e irá aumentando hasta que falle dos veces seguidas.
        </p>
        <div className="flex gap-3 justify-center pt-2">
          <Btn v="outline" onClick={onCancel}>Cancelar</Btn>
          <Btn onClick={begin}><I name="play_arrow" />Iniciar</Btn>
        </div>
      </Card>
    );
  }

  if (phase === "done") {
    const best = span;
    const interp =
      best <= 3 ? { label: "Bajo", color: "#dc2626" }
      : best <= 4 ? { label: "Limítrofe", color: "#f59e0b" }
      : best <= 6 ? { label: "Promedio", color: TEAL }
      : { label: "Superior", color: "#0d9488" };
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <I name="check_circle" fill className="text-5xl" style={{ color: interp.color }} />
        <h2 className="text-2xl font-bold">Sesión completada</h2>
        <div className="flex justify-center gap-8 py-3">
          <div>
            <p className="text-5xl font-extrabold" style={{ color: interp.color }}>{best}</p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1">Span Corsi</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold mt-2" style={{ color: interp.color }}>{interp.label}</p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1">Interpretación</p>
          </div>
        </div>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          Modo: <b>{mode === "backward" ? "Inverso" : "Directo"}</b> ·
          Total ensayos: <b>{history.length}</b>
        </p>
      </Card>
    );
  }

  /* presenting | responding | feedback */
  return (
    <Card className="p-8 max-w-3xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full"
              style={{ background: `${TEAL}15`, color: TEAL }}>
          Longitud: {seqLen} · Span actual: {span}
        </span>
        <span className="text-xs" style={{ color: "var(--ns-muted)" }}>
          {phase === "presenting" && "Observe la secuencia…"}
          {phase === "responding" && (
            mode === "backward"
              ? `Reproduzca en ORDEN INVERSO (${response.length}/${sequence.length})`
              : `Reproduzca en EL MISMO ORDEN (${response.length}/${sequence.length})`
          )}
          {phase === "feedback" && (feedbackOk ? "✓ Correcto" : "✗ Incorrecto")}
        </span>
      </div>

      {/* Tablero Corsi */}
      <div className="relative w-full rounded-2xl overflow-hidden" style={{ background: "var(--ns-subtle)", aspectRatio: "16 / 10" }}>
        {CORSI_POSITIONS.map((c) => {
          const isLit = highlightId === c.id;
          const isResponded = response.includes(c.id);
          const isFeedback = phase === "feedback";
          let bg = "var(--ns-card)";
          if (isLit) bg = "#fbbf24";
          else if (isFeedback && feedbackOk === true && isResponded) bg = "#10b981";
          else if (isFeedback && feedbackOk === false && isResponded) bg = "#ef4444";
          else if (isResponded) bg = TEAL;
          return (
            <button key={c.id}
              onClick={() => onCubeClick(c.id)}
              disabled={phase !== "responding"}
              className="absolute rounded-xl transition-all duration-150 active:scale-95 shadow-md"
              style={{
                left: `${c.x}%`,
                top: `${c.y}%`,
                width: "13%",
                aspectRatio: "1",
                background: bg,
                border: `2px solid ${isLit ? "#f59e0b" : "rgba(0,0,0,0.08)"}`,
                cursor: phase === "responding" ? "pointer" : "default",
                transform: isLit ? "scale(1.08)" : "scale(1)",
              }}
              aria-label={`Cubo ${c.id + 1}`}
            />
          );
        })}
      </div>

      <div className="flex justify-end">
        <Btn v="outline" onClick={onCancel} disabled={phase === "presenting"}>
          Detener
        </Btn>
      </div>
    </Card>
  );
}
