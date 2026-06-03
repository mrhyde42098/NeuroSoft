/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/SetShiftingActivity.jsx — Set-shifting / WCST simple
 * ───────────────────────────────────────────────────────────────────────
 * Versión simplificada de WCST para rehabilitación.
 * El paciente clasifica cartas por COLOR, FORMA o NÚMERO.
 * La regla cambia silenciosamente cada `trials_per_rule` ensayos correctos.
 * Se registran: perseveraciones, errores no-perseverativos, cambios completados.
 *
 * Props: params { total_trials, trials_per_rule }
 *        onFinish(result), onCancel()
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, _useMemo, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const COLORS  = ["rojo","azul","amarillo","verde"];
const SHAPES  = ["círculo","triángulo","estrella","cruz"];
const NUMBERS = [1, 2, 3, 4];
const RULES   = ["color","forma","numero"];

function makeCard() {
  return {
    color:   COLORS[Math.floor(Math.random() * COLORS.length)],
    shape:   SHAPES[Math.floor(Math.random() * SHAPES.length)],
    number:  NUMBERS[Math.floor(Math.random() * NUMBERS.length)],
  };
}

const SHAPE_ICONS = { círculo:"circle", triángulo:"change_history", estrella:"star", cruz:"close" };
const COLOR_HEX   = { rojo:"#ef4444", azul:"#3b82f6", amarillo:"#f59e0b", verde:"#22c55e" };
const _PILES = 4; // 4 pile targets, one per color/shape/number value

/* Devuelve los 4 "target cards" fijos (los pies de las pilas) */
const TARGETS = [
  { color:"rojo",    shape:"círculo",   number:1 },
  { color:"azul",    shape:"triángulo", number:2 },
  { color:"amarillo",shape:"estrella",  number:3 },
  { color:"verde",   shape:"cruz",      number:4 },
];

function matchesByRule(card, target, rule) {
  if (rule === "color")  return card.color  === target.color;
  if (rule === "forma")  return card.shape  === target.shape;
  if (rule === "numero") return card.number === target.number;
  return false;
}

function CardDisplay({ card, size = "md", onClick }) {
  const sz = size === "sm" ? 56 : 80;
  return (
    <button onClick={onClick}
      className="rounded-xl border-2 flex flex-col items-center justify-center gap-1 hover:scale-105 active:scale-95 transition-all"
      style={{ width:sz, height:sz, borderColor: COLOR_HEX[card.color], background: "white", cursor: onClick ? "pointer" : "default" }}>
      {Array.from({ length: card.number }).map((_, i) => (
        <span key={i} className="material-symbols-outlined" style={{ color: COLOR_HEX[card.color], fontSize: size === "sm" ? 12 : 18 }}>
          {SHAPE_ICONS[card.shape]}
        </span>
      ))}
    </button>
  );
}

export default function SetShiftingActivity({ params = {}, onFinish, onCancel }) {
  const totalTrials    = params.total_trials    ?? 48;
  const trialsPerRule  = params.trials_per_rule ?? 10;

  const [phase, setPhase]   = useState("intro");
  const [trial, setTrial]   = useState(0);
  const [card, setCard]     = useState(() => makeCard());
  const [ruleIdx, setRuleIdx] = useState(0);
  const [consec, setConsec] = useState(0);
  const [stats, setStats]   = useState({ correct:0, errors:0, persev:0, rules_done:0 });
  const [feedback, setFeedback] = useState(null);
  const prevRule            = useRef(null);

  const rule = RULES[ruleIdx];

  const checkAnswer = useCallback((pileIdx) => {
    if (feedback) return;
    const correct = matchesByRule(card, TARGETS[pileIdx], rule);
    const newConsec = correct ? consec + 1 : 0;

    /* Perseveración: responde según la regla ANTERIOR cuando ya cambió */
    const isPersev = !correct && prevRule.current !== null &&
      matchesByRule(card, TARGETS[pileIdx], RULES[prevRule.current]);

    setStats(s => ({
      ...s,
      correct: s.correct + (correct ? 1 : 0),
      errors:  s.errors  + (correct ? 0 : 1),
      persev:  s.persev  + (isPersev ? 1 : 0),
    }));
    setFeedback(correct ? "correct" : (isPersev ? "persev" : "error"));

    setTimeout(() => {
      setFeedback(null);
      if (trial + 1 >= totalTrials) {
        setPhase("done");
        onFinish?.({ ...stats, correct: stats.correct + (correct?1:0), errors: stats.errors+(correct?0:1), persev: stats.persev+(isPersev?1:0) });
        return;
      }
      /* Cambiar regla si alcanzó el criterio */
      let nextRuleIdx = ruleIdx;
      if (newConsec >= trialsPerRule) {
        prevRule.current = ruleIdx;
        nextRuleIdx = (ruleIdx + 1) % RULES.length;
        setRuleIdx(nextRuleIdx);
        setStats(s => ({ ...s, rules_done: s.rules_done + 1 }));
        setConsec(0);
      } else {
        setConsec(newConsec);
      }
      setTrial(t => t + 1);
      setCard(makeCard());
    }, 700);
  }, [card, rule, ruleIdx, consec, trial, feedback, stats, totalTrials, trialsPerRule, onFinish]);

  if (phase === "intro") return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="text-center">
        <I name="view_carousel" className="text-5xl mb-3" style={{color:TEAL}}/>
        <h2 className="text-xl font-extrabold">Clasificación flexible de cartas</h2>
        <p className="text-sm mt-2" style={{color:"var(--ns-muted)"}}>
          Clasifica cada carta arrastrándola a la pila que corresponda.
          La regla de clasificación cambia sin aviso — presta atención al feedback.
        </p>
      </div>
      <div className="flex gap-3 justify-center">
        <Btn v="outline" onClick={onCancel}>Cancelar</Btn>
        <Btn onClick={() => setPhase("running")}>Comenzar</Btn>
      </div>
    </Card>
  );

  if (phase === "done") return (
    <Card className="p-8 space-y-5 max-w-lg mx-auto">
      <div className="text-center"><I name="task_alt" fill className="text-5xl text-teal-500 mb-2"/><h2 className="text-lg font-extrabold">Actividad completada</h2></div>
      <div className="grid grid-cols-2 gap-3">
        {[["Correctas", stats.correct, "text-green-600"],
          ["Errores", stats.errors, "text-red-600"],
          ["Perseveraciones", stats.persev, "text-amber-600"],
          ["Reglas completadas", stats.rules_done, ""]
        ].map(([l,v,cls])=>(
          <div key={l} className="p-4 rounded-xl text-center" style={{background:"var(--ns-subtle)"}}>
            <p className="text-xs text-gray-400 uppercase">{l}</p>
            <p className={`font-extrabold text-2xl ${cls}`}>{v}</p>
          </div>
        ))}
      </div>
      <Btn onClick={() => onFinish?.(stats)}>Guardar resultados</Btn>
    </Card>
  );

  return (
    <Card className="p-6 space-y-5 max-w-xl mx-auto">
      {/* Barra de progreso + feedback */}
      <div className="flex items-center justify-between text-xs" style={{color:"var(--ns-muted)"}}>
        <span>Ensayo {trial+1}/{totalTrials}</span>
        <span>✓ {stats.correct} · ✗ {stats.errors}</span>
      </div>
      {/* §H3-fix: guard div/0 si totalTrials aún no se calculó. */}
      <div className="w-full h-1.5 bg-gray-200 rounded-full"><div className="h-full rounded-full" style={{width:`${totalTrials>0?(trial/totalTrials)*100:0}%`,background:TEAL}}/></div>
      {feedback && (
        <div className={`p-3 rounded-xl text-center font-bold text-sm ${feedback==="correct"?"bg-green-100 text-green-700":feedback==="persev"?"bg-amber-100 text-amber-700":"bg-red-100 text-red-700"}`}>
          {feedback==="correct"?"✓ Correcto":feedback==="persev"?"↩ Perseveración — intenta otra regla":"✗ Incorrecto"}
        </div>
      )}
      {/* Cartas target (pilas) */}
      <div>
        <p className="text-[10px] font-bold text-gray-400 uppercase mb-2">Elige la pila correcta:</p>
        <div className="flex justify-around">
          {TARGETS.map((t, i) => (
            <CardDisplay key={i} card={t} size="sm" onClick={() => checkAnswer(i)} />
          ))}
        </div>
      </div>
      {/* Carta actual */}
      <div className="flex items-center justify-center py-4">
        <div>
          <p className="text-[10px] font-bold text-gray-400 uppercase mb-2 text-center">Clasifica esta carta:</p>
          <CardDisplay card={card} size="md" />
        </div>
      </div>
    </Card>
  );
}
