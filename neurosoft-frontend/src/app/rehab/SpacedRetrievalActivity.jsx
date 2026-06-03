/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/SpacedRetrievalActivity.jsx — Spaced Retrieval Training
 * ───────────────────────────────────────────────────────────────────────
 * Técnica de Bourgeois (1990) y Cherry et al. — gold standard para
 * rehabilitación de memoria en demencia leve y TCL amnésico.
 *
 * Mecánica:
 *   1. El clínico ingresa un par TARGET (estímulo → respuesta).
 *      Ej: "¿Cuál es el nombre de su nieto?" → "Manuel"
 *   2. Se presenta y el paciente repite (codificación inicial).
 *   3. Se hace la pregunta tras un intervalo creciente:
 *      30s → 1m → 2m → 4m → 8m → 16m
 *   4. Si el paciente responde correctamente, se duplica el intervalo
 *      (errorless: si falla, se le da la respuesta y se reinicia
 *       el intervalo previo correcto, NO el inicial).
 *   5. La sesión termina cuando se alcanza el intervalo máximo o se
 *      acumulan 3 fallos no consecutivos.
 *
 * Para tarea-casa: el paciente practica la pregunta sólo, pero ESTE
 * componente está diseñado para uso en consulta o supervisado por
 * cuidador (la "respuesta correcta" se valida manualmente).
 *
 * Props:
 *   • params       { target_question, target_answer, max_interval_min }
 *   • onFinish(result)  → { successful_intervals, max_interval_reached, total_trials, fails }
 *   • onCancel()
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState } from "react";
import { Btn, Card, I, Input } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { useToast } from "../../contexts.jsx";

/* Intervalos en segundos (escalado clásico de Bourgeois) */
const DEFAULT_INTERVALS = [30, 60, 120, 240, 480, 960];

const formatInterval = (sec) => {
  if (sec < 60) return `${sec} s`;
  return `${Math.floor(sec / 60)} min`;
};

export default function SpacedRetrievalActivity({
  params = {},
  onFinish,
  onCancel,
}) {
  const toast = useToast();
  const intervals = params.intervals || DEFAULT_INTERVALS;
  const _maxIntervalMin = params.max_interval_min || 16;

  const [phase, setPhase] = useState("setup");
    /* setup · encoding · waiting · prompting · feedback · done */
  const [question, setQuestion] = useState(params.target_question || "");
  const [answer, setAnswer] = useState(params.target_answer || "");
  const [intervalIdx, setIntervalIdx] = useState(0);
  const [secsLeft, setSecsLeft] = useState(0);
  const [history, setHistory] = useState([]);
  const [fails, setFails] = useState(0);
  const [feedbackText, setFeedbackText] = useState("");
  const tickRef = useRef(null);

  /* Cronómetro descendente */
  useEffect(() => {
    if (phase !== "waiting" || secsLeft <= 0) return;
    tickRef.current = setInterval(() => {
      setSecsLeft((s) => {
        if (s <= 1) {
          clearInterval(tickRef.current);
          setPhase("prompting");
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(tickRef.current);
  }, [phase, secsLeft]);

  const startSession = () => {
    if (!question.trim() || !answer.trim()) {
      toast.warn("Ingrese pregunta y respuesta target.");
      return;
    }
    setPhase("encoding");
  };

  const startNextInterval = () => {
    setSecsLeft(intervals[intervalIdx]);
    setPhase("waiting");
  };

  const onResponse = (ok) => {
    const cur = intervals[intervalIdx];
    setHistory((h) => [...h, { interval: cur, ok }]);
    if (ok) {
      setFeedbackText(`✓ Correcto. Intervalo de ${formatInterval(cur)} superado.`);
      const nextIdx = intervalIdx + 1;
      if (nextIdx >= intervals.length) {
        finalize(true);
        return;
      }
      setIntervalIdx(nextIdx);
      setPhase("feedback");
    } else {
      const nextFails = fails + 1;
      setFails(nextFails);
      setFeedbackText(`✗ Recuerde: la respuesta correcta es "${answer}".`);
      if (nextFails >= 3) {
        finalize(false);
        return;
      }
      /* Errorless: bajar al intervalo previo correcto */
      const lastOk = [...history].reverse().findIndex((x) => x.ok);
      if (lastOk >= 0) {
        const lastOkInterval = history[history.length - 1 - lastOk].interval;
        const newIdx = intervals.indexOf(lastOkInterval);
        setIntervalIdx(Math.max(0, newIdx));
      } else {
        setIntervalIdx(0); // volver al inicio
      }
      setPhase("feedback");
    }
  };

  const continueAfterFeedback = () => {
    setFeedbackText("");
    startNextInterval();
  };

  const finalize = (success) => {
    setPhase("done");
    if (onFinish) {
      onFinish({
        successful_intervals: history.filter((x) => x.ok).length,
        max_interval_reached_sec: success ? intervals[intervals.length - 1] : (history.filter((x) => x.ok).slice(-1)[0]?.interval || 0),
        total_trials: history.length + 1,
        fails,
        completed: success,
        target_question: question,
        target_answer: answer,
      });
    }
  };

  /* ─── Render por fase ─────────────────────────────────────── */
  if (phase === "setup") {
    return (
      <Card className="p-8 max-w-2xl mx-auto space-y-5">
        <div className="text-center">
          <div className="w-20 h-20 mx-auto rounded-2xl flex items-center justify-center mb-4"
               style={{ background: `${TEAL}15`, color: TEAL }}>
            <I name="psychology_alt" className="text-4xl" />
          </div>
          <h2 className="text-2xl font-bold">Recobro Espaciado</h2>
          <p className="text-sm mt-2" style={{ color: "var(--ns-muted)" }}>
            Técnica con mayor evidencia en rehab. de memoria para demencia leve.
          </p>
        </div>
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-[0.2em] mb-2" style={{ color: "var(--ns-muted)" }}>
            Pregunta target
          </label>
          <Input value={question} onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ej: ¿Cuál es el nombre de su nieto?" />
        </div>
        <div>
          <label className="block text-[10px] font-extrabold uppercase tracking-[0.2em] mb-2" style={{ color: "var(--ns-muted)" }}>
            Respuesta correcta
          </label>
          <Input value={answer} onChange={(e) => setAnswer(e.target.value)}
            placeholder="Ej: Manuel" />
        </div>
        <p className="text-xs italic" style={{ color: "var(--ns-muted)" }}>
          Intervalos: {intervals.map(formatInterval).join(" → ")}.
          La sesión termina al superar el intervalo máximo o tras 3 fallos.
        </p>
        <div className="flex gap-3 justify-center pt-2">
          <Btn v="outline" onClick={onCancel}>Cancelar</Btn>
          <Btn onClick={startSession}><I name="play_arrow" />Iniciar codificación</Btn>
        </div>
      </Card>
    );
  }

  if (phase === "encoding") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <I name="record_voice_over" className="text-5xl" style={{ color: TEAL }} />
        <h3 className="text-lg font-bold">Codificación inicial</h3>
        <div className="p-5 rounded-2xl" style={{ background: "var(--ns-subtle)" }}>
          <p className="text-sm font-bold mb-2">Pregunta:</p>
          <p className="text-xl">{question}</p>
          <p className="text-sm font-bold mt-4 mb-2">Respuesta:</p>
          <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{answer}</p>
        </div>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          Pida al paciente que repita la respuesta. Cuando esté listo, inicie el primer intervalo.
        </p>
        <Btn onClick={startNextInterval}><I name="timer" />Iniciar intervalo de {formatInterval(intervals[intervalIdx])}</Btn>
      </Card>
    );
  }

  if (phase === "waiting") {
    const total = intervals[intervalIdx];
    const progress = ((total - secsLeft) / total) * 100;
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-5">
        <I name="hourglass_top" className="text-5xl" style={{ color: TEAL }} />
        <h3 className="text-lg font-bold">Esperando intervalo de retención</h3>
        <p className="text-6xl font-extrabold tabular-nums" style={{ color: TEAL }}>
          {Math.floor(secsLeft / 60)}:{String(secsLeft % 60).padStart(2, "0")}
        </p>
        <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: "var(--ns-subtle)" }}>
          <div className="h-full rounded-full transition-all" style={{ width: `${progress}%`, background: TEAL }} />
        </div>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          Mantenga al paciente en una conversación neutral o tarea distractora durante este tiempo.
          Cuando termine el cronómetro, se hará la pregunta target.
        </p>
        <Btn v="outline" onClick={() => setPhase("prompting")} className="text-xs">
          Saltar espera (sólo para pruebas)
        </Btn>
      </Card>
    );
  }

  if (phase === "prompting") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <I name="quiz" className="text-5xl text-amber-500" />
        <h3 className="text-lg font-bold">Pregunte ahora</h3>
        <div className="p-5 rounded-2xl" style={{ background: "#fef3c7", color: "#92400e" }}>
          <p className="text-2xl font-bold">{question}</p>
        </div>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          ¿La respuesta del paciente fue correcta?
        </p>
        <div className="flex gap-3 justify-center">
          <Btn v="outline" onClick={() => onResponse(false)} className="text-red-600 border-red-300">
            <I name="close" />Incorrecto
          </Btn>
          <Btn onClick={() => onResponse(true)} className="bg-emerald-600">
            <I name="check" />Correcto
          </Btn>
        </div>
        <p className="text-[10px] italic" style={{ color: "var(--ns-muted)" }}>
          Respuesta esperada: <b>{answer}</b>
        </p>
      </Card>
    );
  }

  if (phase === "feedback") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <p className="text-lg font-bold">{feedbackText}</p>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          {fails > 0 ? `${fails} fallo(s) acumulado(s).` : ""}
          {" "}Intervalo siguiente: {formatInterval(intervals[intervalIdx])}.
        </p>
        <Btn onClick={continueAfterFeedback}><I name="arrow_forward" />Continuar</Btn>
      </Card>
    );
  }

  if (phase === "done") {
    const successful = history.filter((x) => x.ok).length;
    const lastOk = history.filter((x) => x.ok).slice(-1)[0]?.interval || 0;
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <I name="check_circle" fill className="text-5xl" style={{ color: TEAL }} />
        <h3 className="text-2xl font-bold">Sesión completada</h3>
        <div className="grid grid-cols-3 gap-4 my-4">
          <div>
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{successful}</p>
            <p className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>Aciertos</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{formatInterval(lastOk)}</p>
            <p className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>Máx. intervalo</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold" style={{ color: fails === 0 ? TEAL : "#dc2626" }}>{fails}</p>
            <p className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>Fallos</p>
          </div>
        </div>
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          Para mantener el aprendizaje, repita la sesión con la misma pareja en próxima consulta.
        </p>
      </Card>
    );
  }

  return null;
}
