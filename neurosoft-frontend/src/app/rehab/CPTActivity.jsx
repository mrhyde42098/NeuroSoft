/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/CPTActivity.jsx — Continuous Performance Task (CPT)
 * ───────────────────────────────────────────────────────────────────────
 * Tarea de atención sostenida: letras aparecen a ritmo fijo; el paciente
 * presiona la tecla/botón SÓLO cuando aparece la letra objetivo (X).
 *
 * Métricas: hits, omisiones, falsos positivos, tiempo de reacción (TR).
 * Dificultad adaptable por velocidad (isi_ms) y proporción de blancos.
 *
 * Props: params { trials, isi_ms, target, target_ratio }
 *        onFinish(result), onCancel()
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, useEffect, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const LETTERS = "ACDEFGHIJKLMNOPQRSTUVWZ".split("");

function genSeq(trials, target, targetRatio) {
  const seq = [];
  for (let i = 0; i < trials; i++) {
    if (Math.random() < targetRatio) seq.push(target);
    else {
      let l;
      do { l = LETTERS[Math.floor(Math.random() * LETTERS.length)]; } while (l === target);
      seq.push(l);
    }
  }
  return seq;
}

export default function CPTActivity({ params = {}, onFinish, onCancel }) {
  const trials     = params.trials       ?? 30;
  const isiMs      = params.isi_ms       ?? 1500;
  const target     = params.target       ?? "X";
  const targetRatio= params.target_ratio ?? 0.25;
  const showMs     = Math.min(800, isiMs - 200);

  const seqRef     = useRef(genSeq(trials, target, targetRatio));
  const [phase, setPhase]     = useState("intro");
  const [idx, setIdx]         = useState(-1);
  const [show, setShow]       = useState(false);
  const [result, setResult]   = useState({ hits:0, omis:0, fps:0, trs:[] });
  const tStart                = useRef(null);
  const respondedRef          = useRef(false);
  const timerRef              = useRef(null);

  const finish = useCallback((r) => {
    setPhase("done");
    onFinish?.({ ...r, total_targets: seqRef.current.filter(x => x === target).length });
  }, [onFinish, target]);

  useEffect(() => {
    if (phase !== "running") return;
    if (idx >= seqRef.current.length) { finish(result); return; }
    respondedRef.current = false;
    setShow(true);
    tStart.current = Date.now();

    timerRef.current = setTimeout(() => {
      setShow(false);
      const isTarget = seqRef.current[idx] === target;
      if (isTarget && !respondedRef.current) {
        setResult(r => ({ ...r, omis: r.omis + 1 }));
      }
      timerRef.current = setTimeout(() => setIdx(i => i + 1), isiMs - showMs);
    }, showMs);

    return () => clearTimeout(timerRef.current);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idx, phase]);

  const respond = () => {
    if (phase !== "running" || !show) return;
    const rt = Date.now() - tStart.current;
    const isTarget = seqRef.current[idx] === target;
    if (isTarget) {
      respondedRef.current = true;
      setResult(r => ({ ...r, hits: r.hits + 1, trs: [...r.trs, rt] }));
    } else {
      setResult(r => ({ ...r, fps: r.fps + 1 }));
    }
  };

  useEffect(() => {
    /* §A2-fix: filtrar Space si el foco está en un input — protege
     * la métrica clínica contra disparos accidentales desde modales. */
    const onKey = (e) => {
      if (e.code !== "Space") return;
      const tgt = e.target;
      const tag = (tgt?.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select") return;
      if (tgt?.isContentEditable) return;
      if (document.activeElement?.tagName === "TEXTAREA") return;
      respond();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, show, idx]);

  const start = () => { setIdx(0); setPhase("running"); };
  const avgTR = result.trs.length ? Math.round(result.trs.reduce((a,b)=>a+b,0)/result.trs.length) : "—";
  const totalT = seqRef.current.filter(x => x === target).length;
  const accuracy = totalT > 0 ? Math.round((result.hits / totalT) * 100) : 0;

  if (phase === "intro") return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="text-center">
        <I name="ads_click" className="text-5xl mb-3" style={{color:TEAL}}/>
        <h2 className="text-xl font-extrabold">CPT — Atención Sostenida</h2>
        <p className="text-sm mt-2" style={{color:"var(--ns-muted)"}}>
          Aparecerán letras, una a la vez. Presione el botón (o Espacio) <b>solo cuando aparezca la letra {target}</b>.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="p-3 rounded-xl text-center" style={{background:"var(--ns-subtle)"}}>
          <p className="text-xs text-gray-400 uppercase">Estímulos</p>
          <p className="font-bold text-lg">{trials}</p>
        </div>
        <div className="p-3 rounded-xl text-center" style={{background:"var(--ns-subtle)"}}>
          <p className="text-xs text-gray-400 uppercase">Velocidad</p>
          <p className="font-bold text-lg">{(isiMs/1000).toFixed(1)}s</p>
        </div>
      </div>
      <div className="flex gap-3 justify-center">
        <Btn v="outline" onClick={onCancel}>Cancelar</Btn>
        <Btn onClick={start}>Comenzar</Btn>
      </div>
    </Card>
  );

  if (phase === "running") return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="flex items-center justify-between text-xs" style={{color:"var(--ns-muted)"}}>
        <span>Progreso: {idx+1}/{trials}</span>
        <div className="flex gap-3">
          <span className="text-green-600 font-bold">✓ {result.hits}</span>
          <span className="text-red-600 font-bold">✗ {result.fps}</span>
        </div>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full bg-teal-500 transition-all" style={{width:`${((idx+1)/trials)*100}%`}}/>
      </div>
      <div className="flex items-center justify-center" style={{minHeight:180}}>
        <div className={`w-40 h-40 rounded-3xl flex items-center justify-center text-7xl font-extrabold transition-all duration-150 ${show ? "shadow-2xl scale-100" : "scale-90 opacity-0"}`}
          style={{background:show?(seqRef.current[idx]===target?"#ecfdf5":"var(--ns-subtle)"):"transparent",
                  color:show?(seqRef.current[idx]===target?TEAL:"var(--ns-text)"):"transparent",
                  border:show?`4px solid ${seqRef.current[idx]===target?"#10b981":"var(--ns-card-b)"}`:undefined}}>
          {show ? seqRef.current[idx] : ""}
        </div>
      </div>
      <button onClick={respond} onTouchStart={respond}
        className="w-full h-20 rounded-2xl text-white text-xl font-extrabold active:scale-95 transition-all select-none"
        style={{background:TEAL,boxShadow:"0 8px 20px -6px rgba(13,148,136,0.5)"}}>
        ¡ES {target}! &nbsp; (Espacio)
      </button>
    </Card>
  );

  return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="text-center">
        <I name="task_alt" fill className="text-5xl mb-2 text-teal-500"/>
        <h2 className="text-lg font-extrabold">Tarea completada</h2>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {[["Precisión", `${accuracy}%`, accuracy>=80?"text-green-600":"text-red-600"],
          ["TR medio",`${avgTR}ms`,""],
          ["Omisiones",result.omis,"text-amber-600"],
          ["Falsos Pos.",result.fps,"text-red-600"]
        ].map(([l,v,cls])=>(
          <div key={l} className="p-4 rounded-xl text-center" style={{background:"var(--ns-subtle)"}}>
            <p className="text-xs text-gray-400 uppercase">{l}</p>
            <p className={`font-extrabold text-2xl ${cls}`}>{v}</p>
          </div>
        ))}
      </div>
      <Btn onClick={() => onFinish?.({ hits:result.hits, omis:result.omis, fps:result.fps, avg_tr:avgTR, accuracy, total_targets:totalT })}>
        Guardar resultados
      </Btn>
    </Card>
  );
}
