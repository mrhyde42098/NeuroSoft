/* ═══════════════════════════════════════════════════════════════════════
 * MindInEyesActivity.jsx — Cognición social: Reading the Mind in the Eyes
 * ───────────────────────────────────────────────────────────────────────
 * Versión rehab (no diagnóstica) basada en el paradigma de Baron-Cohen
 * et al. (2001). Muestra una imagen de la región ocular + 4 opciones de
 * estado mental. El paciente elige la que mejor describe lo que "siente"
 * la persona. Feedback inmediato + psicoeducación.
 *
 * Los estímulos son SVGs esquemáticos propios (no fotografías del test
 * comercial). Los estados mentales son de dominio público según la versión
 * original publicada en Journal of Child Psychology and Psychiatry.
 *
 * Props: { params, onFinish, onCancel }
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* ── Ítems: cada uno tiene un SVG de ojos + 4 opciones (1 correcta) ── */
const ITEMS = [
  {
    emotion: "preocupado",
    distract: ["aburrido", "feliz", "curioso"],
    explain: "Las cejas levantadas asimétricamente y la tensión periocular señalan preocupación.",
    eyeType: "worried",
  },
  {
    emotion: "curioso",
    distract: ["triste", "enojado", "cansado"],
    explain: "La mirada intensa con ligera apertura de párpados y cejas levantadas indica curiosidad.",
    eyeType: "curious",
  },
  {
    emotion: "desconfiado",
    distract: ["alegre", "sorprendido", "enamorado"],
    explain: "El entrecejo fruncido y los párpados entornados expresan desconfianza o escepticismo.",
    eyeType: "suspicious",
  },
  {
    emotion: "triste",
    distract: ["orgulloso", "aburrido", "ansioso"],
    explain: "Los párpados caídos y las comisuras internas de las cejas elevadas son señales de tristeza.",
    eyeType: "sad",
  },
  {
    emotion: "sorprendido",
    distract: ["cansado", "disgustado", "concentrado"],
    explain: "Los ojos muy abiertos y las cejas arqueadas hacia arriba indican sorpresa.",
    eyeType: "surprised",
  },
  {
    emotion: "concentrado",
    distract: ["celoso", "asustado", "aliviado"],
    explain: "La mirada fija y el ligero entrecejo fruncido reflejan concentración o esfuerzo mental.",
    eyeType: "focused",
  },
  {
    emotion: "aliviado",
    distract: ["frustrado", "confundido", "emocionado"],
    explain: "Los párpados relajados y la mirada suave señalan alivio o tranquilidad.",
    eyeType: "relieved",
  },
  {
    emotion: "ansioso",
    distract: ["sereno", "orgulloso", "indiferente"],
    explain: "El parpadeo frecuente y la tensión muscular alrededor del ojo revelan ansiedad.",
    eyeType: "anxious",
  },
];

/* ── Función que dibuja los ojos según el tipo ── */
function EyesSVG({ eyeType }) {
  const W = 300, H = 120;
  /* Parámetros base */
  const lx = 70, rx = 230, cy = 60, er = 28;

  const eyeParams = {
    worried:    { browL: { x1:42, y1:22, x2:98, y2:30 }, browR: { x1:202, y1:30, x2:258, y2:22 }, upper: -4 },
    curious:    { browL: { x1:42, y1:30, x2:98, y2:20 }, browR: { x1:202, y1:20, x2:258, y2:30 }, upper: 2 },
    suspicious: { browL: { x1:42, y1:30, x2:98, y2:36 }, browR: { x1:202, y1:36, x2:258, y2:30 }, upper: -8 },
    sad:        { browL: { x1:42, y1:26, x2:98, y2:34 }, browR: { x1:202, y1:34, x2:258, y2:26 }, upper: -4 },
    surprised:  { browL: { x1:42, y1:16, x2:98, y2:14 }, browR: { x1:202, y1:14, x2:258, y2:16 }, upper: 6 },
    focused:    { browL: { x1:42, y1:34, x2:98, y2:28 }, browR: { x1:202, y1:28, x2:258, y2:34 }, upper: -4 },
    relieved:   { browL: { x1:42, y1:32, x2:98, y2:34 }, browR: { x1:202, y1:34, x2:258, y2:32 }, upper: -2 },
    anxious:    { browL: { x1:42, y1:24, x2:98, y2:32 }, browR: { x1:202, y1:32, x2:258, y2:24 }, upper: -6 },
  };

  const p = eyeParams[eyeType] || eyeParams.curious;

  function Eye({ cx, side }) {
    const ry = er + p.upper;
    return (
      <g>
        {/* Esclerótica */}
        <ellipse cx={cx} cy={cy} rx={er} ry={Math.max(12, ry)} fill="#fff" stroke="#1e293b" strokeWidth="2"/>
        {/* Iris */}
        <circle cx={cx} cy={cy} r={14} fill="#1e293b"/>
        <circle cx={cx} cy={cy} r={8} fill="#3b82f6"/>
        {/* Pupila */}
        <circle cx={cx} cy={cy} r={4} fill="#0a0a0a"/>
        {/* Reflejo */}
        <circle cx={cx+6} cy={cy-5} r={2.5} fill="#fff" opacity="0.7"/>
        {/* Párpado superior */}
        <path
          d={`M${cx-er} ${cy} Q${cx} ${cy - ry - 4} ${cx+er} ${cy}`}
          fill="#fde8d0" stroke="#1e293b" strokeWidth="1.5"
        />
        {/* Ceja */}
        <line
          x1={side === "L" ? p.browL.x1 : p.browR.x1}
          y1={side === "L" ? p.browL.y1 : p.browR.y1}
          x2={side === "L" ? p.browL.x2 : p.browR.x2}
          y2={side === "L" ? p.browL.y2 : p.browR.y2}
          stroke="#1e293b" strokeWidth="4" strokeLinecap="round"
        />
      </g>
    );
  }

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ maxHeight: 130, background: "#fde8d0", borderRadius: 12 }}>
      {/* Nariz esquemática */}
      <path d={`M${W/2-8} 80 Q${W/2} 95 ${W/2+8} 80`} fill="none" stroke="#c9a87c" strokeWidth="2"/>
      <Eye cx={lx} side="L"/>
      <Eye cx={rx} side="R"/>
      <text x={W/2} y={H-6} textAnchor="middle" fontSize="8" fill="#94a3b8">
        ¿Qué estado mental expresa esta persona?
      </text>
    </svg>
  );
}

export default function MindInEyesActivity({ params = {}, onFinish, onCancel }) {
  const nItems    = Math.min(params.n_items ?? 8, ITEMS.length);
  const items     = ITEMS.slice(0, nItems);
  const [idx,     setIdx]     = useState(0);
  const [chosen,  setChosen]  = useState(null);
  const [results, setResults] = useState([]);
  const [started, setStarted] = useState(false);
  const [done,    setDone]    = useState(false);

  const item = items[idx];
  /* Mezcla opciones determinística (por índice) */
  const options = [item.emotion, ...item.distract].sort((a, b) =>
    (a.charCodeAt(0) * (idx+1)) % 7 - (b.charCodeAt(0) * (idx+1)) % 7
  );

  function answer(opt) {
    if (chosen !== null) return;
    setChosen(opt);
  }

  function next() {
    const correct = chosen === item.emotion;
    const newResults = [...results, { item: idx + 1, correct, chosen, expected: item.emotion }];
    setResults(newResults);
    if (idx + 1 >= nItems) {
      setDone(true);
    } else {
      setIdx(i => i + 1);
      setChosen(null);
    }
  }

  if (!started) {
    return (
      <Card className="p-8 max-w-lg mx-auto space-y-5 text-center">
        <I name="visibility" style={{ color: TEAL, fontSize: 48 }}/>
        <h2 className="text-xl font-extrabold">Reading the Mind in the Eyes</h2>
        <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
          Verá la región de los ojos de diferentes personas. Elija la palabra que mejor
          describe el <strong>estado mental o emocional</strong> de la persona.
          No hay tiempo límite — tome el tiempo que necesite.
        </p>
        <p className="text-xs px-4" style={{ color: "var(--ns-muted)" }}>
          Basado en el paradigma de Baron-Cohen et al. (2001).
          Los dibujos son esquemáticos y no reproducen el material diagnóstico comercial.
        </p>
        <Btn onClick={() => setStarted(true)}>Comenzar</Btn>
        <button onClick={onCancel} className="block mx-auto text-xs mt-2" style={{ color: "var(--ns-muted)" }}>Cancelar</button>
      </Card>
    );
  }

  if (done) {
    const correct = results.filter(r => r.correct).length;
    const pct = Math.round((correct / nItems) * 100);
    return (
      <Card className="p-8 max-w-lg mx-auto space-y-5">
        <div className="text-center">
          <I name="face" fill style={{ color: TEAL, fontSize: 48 }}/>
          <h2 className="text-xl font-extrabold mt-2">Resultados</h2>
          <p className="text-5xl font-extrabold mt-2" style={{ color: pct >= 75 ? "#10b981" : pct >= 50 ? "#f59e0b" : "#dc2626" }}>
            {correct}/{nItems}
          </p>
          <p className="text-sm mt-1" style={{ color: "var(--ns-muted)" }}>{pct}% de aciertos</p>
        </div>
        {/* Revisión item a item */}
        <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
          {results.map((r, i) => (
            <div key={i} className={`flex items-center gap-3 p-3 rounded-xl text-xs ${r.correct ? "bg-green-50" : "bg-red-50"}`}>
              <I name={r.correct ? "check_circle" : "cancel"} fill className={r.correct ? "text-green-600" : "text-red-500"}/>
              <span className="flex-1">Ítem {r.item}: elegiste <strong>{r.chosen}</strong></span>
              {!r.correct && <span style={{ color: "#dc2626" }}>esperado: <strong>{r.expected}</strong></span>}
            </div>
          ))}
        </div>
        {pct < 75 && (
          <p className="text-xs p-3 rounded-xl" style={{ background: "#fef3c7", color: "#92400e" }}>
            <I name="lightbulb" className="text-sm mr-1"/>
            Consejo: practique observar las cejas y los párpados — son las principales señales de los estados mentales.
          </p>
        )}
        <Btn onClick={() => onFinish({ correct, total: nItems, pct_aciertos: pct })}>
          Guardar resultados
        </Btn>
      </Card>
    );
  }

  return (
    <Card className="p-6 max-w-lg mx-auto space-y-5">
      {/* Progreso */}
      <div className="flex items-center justify-between">
        <p className="text-sm font-extrabold">Ítem {idx + 1} / {nItems}</p>
        <div className="flex gap-1">
          {items.map((_, i) => (
            <div key={i} className="w-3 h-3 rounded-full" style={{
              background: i < idx ? TEAL : i === idx ? "#0D9488" : "var(--ns-card-b)"
            }}/>
          ))}
        </div>
      </div>

      {/* Imagen de ojos */}
      <EyesSVG eyeType={item.eyeType}/>

      {/* Opciones */}
      <div className="grid grid-cols-2 gap-3">
        {options.map((opt) => {
          const isChosen   = chosen === opt;
          const isCorrect  = chosen !== null && opt === item.emotion;
          const isWrong    = isChosen && opt !== item.emotion;
          let bg = "var(--ns-card)", border = "var(--ns-card-b)", color = "var(--ns-text)";
          if (isCorrect) { bg = "#ecfdf5"; border = "#10b981"; color = "#064e3b"; }
          if (isWrong)   { bg = "#fef2f2"; border = "#dc2626"; color = "#7f1d1d"; }
          if (chosen === null && isChosen) { bg = `${TEAL}18`; border = TEAL; }
          return (
            <button key={opt} onClick={() => answer(opt)} disabled={chosen !== null}
              className="p-3 rounded-xl text-sm font-bold border-2 transition-all disabled:cursor-default"
              style={{ background: bg, borderColor: border, color }}>
              {opt.charAt(0).toUpperCase() + opt.slice(1)}
              {isCorrect && <I name="check_circle" fill className="ml-2 text-green-600"/>}
              {isWrong   && <I name="cancel" fill className="ml-2 text-red-500"/>}
            </button>
          );
        })}
      </div>

      {/* Explicación tras responder */}
      {chosen !== null && (
        <div className="p-3 rounded-xl text-xs" style={{ background: "#eff6ff", color: "#1e40af" }}>
          <I name="info" className="text-sm mr-1"/>
          <strong>Clave:</strong> {item.explain}
        </div>
      )}

      {chosen !== null && (
        <Btn onClick={next} className="w-full">
          {idx + 1 < nItems ? "Siguiente" : "Ver resultados"}
        </Btn>
      )}
    </Card>
  );
}
