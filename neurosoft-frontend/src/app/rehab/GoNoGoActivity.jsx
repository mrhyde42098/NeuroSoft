/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/GoNoGoActivity.jsx — Go/No-Go progresivo
 * ───────────────────────────────────────────────────────────────────────
 * Verde (círculo) → presionar (GO).
 * Rojo  (círculo) → no presionar (NO-GO).
 * Dificultad progresiva: aumenta velocidad y proporción de no-go.
 *
 * Bloques:
 *   Bloque 1 (nivel 1): ISI 1800ms, 20% no-go
 *   Bloque 2 (nivel 2): ISI 1200ms, 30% no-go
 *   Bloque 3 (nivel 3): ISI 800ms,  40% no-go
 *
 * Props: params { trials_per_block }, onFinish(result), onCancel()
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, useEffect, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const LEVELS = [
  { isi: 1800, noGoRatio: 0.20, label: "Nivel 1 — Básico"    },
  { isi: 1200, noGoRatio: 0.30, label: "Nivel 2 — Intermedio" },
  { isi: 800,  noGoRatio: 0.40, label: "Nivel 3 — Avanzado"  },
];
const SHOW_MS = 500;

function genBlock(n, noGoRatio) {
  return Array.from({ length: n }, () => Math.random() < noGoRatio ? "nogo" : "go");
}

export default function GoNoGoActivity({ params = {}, onFinish, onCancel }) {
  const trialsPerBlock = params.trials_per_block ?? 20;

  const [phase, setPhase]   = useState("intro");
  const [level, setLevel]   = useState(0);
  const [block, setBlock]   = useState(() => genBlock(trialsPerBlock, LEVELS[0].noGoRatio));
  const [idx, setIdx]       = useState(0);
  const [show, setShow]     = useState(false);
  const [stim, setStim]     = useState("go");
  const [stats, setStats]   = useState({ go_hits:0, go_miss:0, nogo_correct:0, nogo_comm:0 });
  const [allStats, setAllStats] = useState([]);
  const [levelMsg, setLevelMsg] = useState("");
  const respondedRef = useRef(false);
  const timerRef     = useRef(null);

  const nextStimulus = useCallback((curBlock, curIdx) => {
    if (curIdx >= curBlock.length) return false;
    respondedRef.current = false;
    const s = curBlock[curIdx];
    setStim(s); setShow(true);
    timerRef.current = setTimeout(() => {
      setShow(false);
      if (s === "go" && !respondedRef.current)
        setStats(st => ({ ...st, go_miss: st.go_miss + 1 }));
      timerRef.current = setTimeout(() => setIdx(i => i + 1), LEVELS[level].isi - SHOW_MS);
    }, SHOW_MS);
    return true;
  }, [level]);

  useEffect(() => {
    if (phase !== "running") return;
    const lv = LEVELS[level];
    if (!nextStimulus(block, idx)) {
      /* Fin del bloque */
      clearTimeout(timerRef.current);
      setAllStats(prev => [...prev, { ...stats, level }]);
      if (level + 1 < LEVELS.length) {
        const nextLevel = level + 1;
        setLevelMsg(`Bloque completado. ${LEVELS[nextLevel].label}`);
        setPhase("between");
      } else {
        setPhase("done");
        onFinish?.({ levels: [...allStats, { ...stats, level }] });
      }
    }
  }, [idx, phase]);

  useEffect(() => () => clearTimeout(timerRef.current), []);

  const respond = useCallback(() => {
    if (phase !== "running" || !show) return;
    respondedRef.current = true;
    if (stim === "go")
      setStats(st => ({ ...st, go_hits: st.go_hits + 1 }));
    else
      setStats(st => ({ ...st, nogo_comm: st.nogo_comm + 1 }));
  }, [phase, show, stim]);

  useEffect(() => {
    /* §A2-fix: ignorar Space si el foco está en un input editable —
     * antes se disparaba respond() al escribir texto en un modal abierto
     * por encima de la actividad, contaminando las métricas clínicas. */
    const h = (e) => {
      if (e.code !== "Space") return;
      const tgt = e.target;
      const tag = (tgt?.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select") return;
      if (tgt?.isContentEditable) return;
      if (document.activeElement?.tagName === "TEXTAREA") return;
      respond();
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [respond]);

  if (phase === "intro") return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="text-center">
        <I name="traffic" className="text-5xl mb-3" style={{color:TEAL}}/>
        <h2 className="text-xl font-extrabold">Go / No-Go Progresivo</h2>
        <p className="text-sm mt-2" style={{color:"var(--ns-muted)"}}>
          Círculo <b style={{color:"#22c55e"}}>verde</b>: presione rápido (GO).<br/>
          Círculo <b style={{color:"#dc2626"}}>rojo</b>: <b>no</b> presione (NO-GO).
        </p>
        <p className="text-xs mt-2" style={{color:"var(--ns-muted)"}}>3 bloques progresivos · {trialsPerBlock} estímulos cada uno</p>
      </div>
      <div className="flex gap-3 justify-center">
        <Btn v="outline" onClick={onCancel}>Cancelar</Btn>
        <Btn onClick={() => { setPhase("running"); }}>Comenzar</Btn>
      </div>
    </Card>
  );

  if (phase === "between") return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto text-center">
      <I name="check_circle" fill className="text-5xl text-teal-500"/>
      <h2 className="text-lg font-bold">{levelMsg}</h2>
      <p className="text-sm" style={{color:"var(--ns-muted)"}}>Descanse unos segundos y continue cuando esté listo.</p>
      <Btn onClick={() => {
        const nextLv = level + 1;
        setLevel(nextLv);
        setBlock(genBlock(trialsPerBlock, LEVELS[nextLv].noGoRatio));
        setIdx(0);
        setStats({ go_hits:0, go_miss:0, nogo_correct:0, nogo_comm:0 });
        setPhase("running");
      }}>Siguiente bloque</Btn>
    </Card>
  );

  if (phase === "done") return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="text-center"><I name="task_alt" fill className="text-5xl text-teal-500 mb-2"/><h2 className="text-lg font-extrabold">Actividad completada</h2></div>
      <div className="space-y-2">{allStats.map((s,i)=>(
        <div key={i} className="p-3 rounded-xl flex justify-between text-sm" style={{background:"var(--ns-subtle)"}}>
          <span className="font-bold">{LEVELS[s.level].label}</span>
          <span className="text-green-600">GO ✓ {s.go_hits} / ✗ {s.go_miss}</span>
          <span className="text-red-600">NoGo 🚫 {s.nogo_comm}</span>
        </div>
      ))}</div>
      <Btn onClick={() => onFinish?.({ levels: allStats })}>Guardar resultados</Btn>
    </Card>
  );

  return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="flex justify-between text-xs" style={{color:"var(--ns-muted)"}}>
        <span>{LEVELS[level].label}</span>
        <span>{idx+1}/{block.length}</span>
      </div>
      {/* §H3-fix: guard div/0 cuando el bloque aún no se inicializó. */}
      <div className="w-full h-1.5 bg-gray-200 rounded-full"><div className="h-full rounded-full" style={{width:`${block.length>0?(idx/block.length)*100:0}%`,background:TEAL}}/></div>
      <div className="flex items-center justify-center" style={{minHeight:200}}>
        <div className={`rounded-full transition-all duration-150 ${show?"opacity-100 scale-100":"opacity-0 scale-75"}`}
          style={{width:160,height:160,background:show?(stim==="go"?"#22c55e":"#dc2626"):"transparent",
                  boxShadow:show?`0 16px 40px -10px ${stim==="go"?"#22c55e80":"#dc262680"}`:"none"}}/>
      </div>
      <button onClick={respond} onTouchStart={respond}
        className="w-full h-20 rounded-2xl text-white text-xl font-extrabold active:scale-95 transition-all select-none"
        style={{background:TEAL}}>
        ¡GO! (Espacio)
      </button>
    </Card>
  );
}
