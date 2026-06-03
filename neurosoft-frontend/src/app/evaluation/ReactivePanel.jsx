/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/ReactivePanel.jsx — Captura ítem-por-ítem por subprueba
 * Renderiza ítems segun el tipo de REACTIVOS[testId] y auto-calcula PD.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { Card, Btn, I, Label } from "../../ui/primitives.jsx";
import { TEAL, TEAL_LIGHT } from "../../ui/tokens.js";
import { REACTIVOS } from "../../data/clinical.js";
import ScoringGuide from "./ScoringGuide.jsx";
import { getItem as getProtocolItem, getSubtest } from "../../data/protocolLoader.js";
import { CubosPattern } from "../../data/PatronesCubos.jsx";
import { FCROFigure } from "../../data/PatronFCRO.jsx";
import BlockStimulus from "./BlockStimulus.jsx";

/* ═══ Componente ReactivePanel — Renderiza ítems según tipo ═══ */
export const ReactivePanel=({testId,puntajes,setPuntajes,itemScores,setItemScores})=>{
  const cfg=REACTIVOS[testId];
  const [fcroHL,setFcroHL]=useState(-1);
  if(!cfg)return null;
  const scores=itemScores[testId]||{};
  const setS=(key,val)=>{
    const next={...scores,[key]:val};
    setItemScores(p=>({...p,[testId]:next}));
    /* Auto-calcular PD total */
    let total=0;
    if(cfg.type==="items")cfg.items.forEach(it=>{total+=(parseFloat(next[`i${it.n}`])||0)});
    /* §M2-fix: parseInt SIEMPRE con radix 10 — evita interpretación octal/hex
     * accidental si el clínico escribe "08" o "0x" en un campo PD. */
    else if(cfg.type==="scored_items")cfg.items.forEach(it=>{total+=(parseInt(next[`i${it.n}`],10)||0)});
    else if(cfg.type==="fcro")cfg.elements.forEach((_,i)=>{total+=(parseFloat(next[`e${i}`])||0)});
    else if(cfg.type==="digits"){cfg.sections.forEach(sec=>{sec.sequences.forEach((sq,i)=>{total+=(parseInt(next[`${sec.name}_${i}_a`],10)||0);total+=(parseInt(next[`${sec.name}_${i}_b`],10)||0)})});}
    else if(cfg.type==="memory_curve"){const trials=cfg.trials.filter(t=>t.type!=="recognition");const lastTrial=trials[trials.length-1];if(lastTrial)total=parseInt(next[`trial_${lastTrial.id}_total`],10)||0;else total=0;}
    else if(cfg.type==="tmt"){total=parseInt(next.tiempo,10)||0;}
    else if(cfg.type==="stroop"){total=parseInt(next.interferencia,10)||0;}
    else if(cfg.type==="caras"){total=Math.max(0,(parseInt(next.aciertos,10)||0)-(parseInt(next.errores,10)||0));}
    else if(cfg.type==="timed_count"){total=parseInt(next.correctas,10)||0;}
    else if(cfg.type==="validity_grid"){total=(cfg.items||[]).filter(it=>next[`r${it.n}`]==="1").length;}
    setPuntajes(p=>({...p,[testId]:String(total)}));
  };
  /* Banner de licencia editorial (Sprint 12) */
  const licenseBanner = cfg.requires_license && (
    <div className="p-3 mb-3 rounded-xl border-l-4 flex items-center gap-3" style={{borderColor:"#f59e0b",background:"rgba(251,191,36,0.1)"}}>
      <I name="copyright" className="text-amber-600 text-lg"/>
      <div className="flex-1">
        <p className="text-xs font-bold text-amber-700">Material editorial requerido</p>
        <p className="text-[10px] text-amber-700/80">
          Esta prueba requiere licencia y kit físico de <b>{cfg.license_publisher}</b>
          {cfg.license_authors && ` (${cfg.license_authors})`}. El sistema sólo facilita la captura digital de puntajes.
        </p>
      </div>
    </div>
  );

  /* ── Render por tipo ── */
  if(cfg.type==="items"){
    const isCubos=testId==="NiWiscDC"||testId==="AdWAISCC";
    const cubosTest=testId==="AdWAISCC"?"wais":"wisc";
    return<>{licenseBanner}<Card className="p-5 space-y-3 border-l-4 border-purple-400">
      <div className="flex items-center justify-between"><h3 className="font-bold text-sm flex items-center gap-2"><I name="grid_view" className="text-purple-600 text-lg"/>Reactivos — {cfg.label}</h3><span className="text-xs font-bold px-2 py-1 rounded-full bg-purple-100 text-purple-700">PD: {puntajes[testId]||0}</span></div>
      <div className="space-y-1.5 max-h-[28rem] overflow-y-auto pr-1">{cfg.items.map(it=>{
        const v=scores[`i${it.n}`]||"";
        return<div key={it.n} className="flex items-center gap-3 p-2 rounded-lg hover:bg-purple-50/50 transition-all">
          <span className="text-xs font-mono font-bold text-gray-400 w-6">{it.n}</span>
          {isCubos&&<div className="shrink-0 w-16 h-16 rounded border border-purple-100 bg-white overflow-hidden flex items-center justify-center" title={`Diseño ${it.n}`}><CubosPattern itemNum={it.n} test={cubosTest} size={20}/></div>}
          <div className="flex-1 min-w-0"><p className="text-sm text-gray-600 truncate">{it.desc}</p>
            <p className="text-[10px] text-gray-400">{it.cubos} cubos · {it.tiempo}s{it.bonus?" · +bonus":""} · max {it.max}</p></div>
          <input type="number" min="0" max={it.max} value={v} onChange={e=>setS(`i${it.n}`,e.target.value)} className="w-14 h-7 text-center text-xs font-bold rounded-lg border-none focus:ring-2 focus:ring-purple-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="—"/>
        </div>})}</div>
    </Card></>;
  }
  if(cfg.type==="scored_items"){
    const maxPer=cfg.scoring[cfg.scoring.length-1];
    return<Card className="p-5 space-y-3 border-l-4 border-purple-400">
      <div className="flex items-center justify-between"><h3 className="font-bold text-sm flex items-center gap-2"><I name="list_alt" className="text-purple-600 text-lg"/>Reactivos — {cfg.label}</h3><span className="text-xs font-bold px-2 py-1 rounded-full bg-purple-100 text-purple-700">PD: {puntajes[testId]||0}</span></div>
      <div className="space-y-1 max-h-72 overflow-y-auto pr-1">{cfg.items.map(it=>{
        const v=parseInt(scores[`i${it.n}`],10)||0;const label=it.pair||it.word||it.q||`Ítem ${it.n}`;
        const protoItem = getProtocolItem(testId, it.n);
        return<div key={it.n} className="space-y-1">
        <div className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-50 transition-all">
          <span className="text-xs font-mono font-bold text-gray-400 w-6">{it.n}</span>
          <p className="flex-1 text-sm text-gray-600 truncate" title={label}>{label}</p>
          <div className="flex gap-1">{cfg.scoring.map(s=><button key={s} onClick={()=>setS(`i${it.n}`,String(s))} className={`w-9 h-8 rounded-lg text-xs font-bold transition-all ${v===s?"text-white shadow":"text-gray-500 hover:bg-gray-100"}`} style={v===s?{background:TEAL}:{}}>{s}</button>)}</div>
        </div>
        {protoItem && <ScoringGuide item={protoItem} testId={testId}/>}
        </div>})}</div>
    </Card>;
  }
  if(cfg.type==="digits"){
    return<Card className="p-5 space-y-4 border-l-4 border-indigo-400">
      <div className="flex items-center justify-between"><h3 className="font-bold text-sm flex items-center gap-2"><I name="pin" className="text-indigo-600 text-lg"/>Dígitos — {cfg.label}</h3><span className="text-xs font-bold px-2 py-1 rounded-full bg-indigo-100 text-indigo-700">PD: {puntajes[testId]||0}</span></div>
      {cfg.sections.map(sec=>{
        const secTotal=sec.sequences.reduce((s,_,i)=>(s+(parseInt(scores[`${sec.name}_${i}_a`],10)||0)+(parseInt(scores[`${sec.name}_${i}_b`],10)||0)),0);
        return<div key={sec.name} className="space-y-2">
        <div className="flex items-center justify-between"><p className="text-xs font-bold text-indigo-600 uppercase tracking-wider">{sec.name}</p><span className="text-[10px] font-bold text-indigo-500">{secTotal}/{sec.sequences.length*2}</span></div>
        <div className="space-y-1 max-h-48 overflow-y-auto">{sec.sequences.map((sq,i)=>
          <div key={i} className="flex items-center gap-3 p-1.5 rounded-lg hover:bg-indigo-50/50">
            <span className="text-[10px] font-mono font-bold text-gray-400 w-4">{sq.len}</span>
            <div className="flex-1 grid grid-cols-2 gap-2">
              <div className="flex items-center gap-2"><span className="text-[10px] text-gray-500 font-mono">{sq.a}</span>
                <div className="flex gap-0.5">{[0,1].map(v=><button key={v} onClick={()=>setS(`${sec.name}_${i}_a`,String(v))} className={`w-6 h-6 rounded text-[10px] font-bold ${parseInt(scores[`${sec.name}_${i}_a`]||"0",10)===v?"text-white":"text-gray-400"}`} style={parseInt(scores[`${sec.name}_${i}_a`]||"0",10)===v?{background:v?"#22c55e":"#ef4444"}:{}}>{v?"✓":"✗"}</button>)}</div></div>
              <div className="flex items-center gap-2"><span className="text-[10px] text-gray-500 font-mono">{sq.b}</span>
                <div className="flex gap-0.5">{[0,1].map(v=><button key={v} onClick={()=>setS(`${sec.name}_${i}_b`,String(v))} className={`w-6 h-6 rounded text-[10px] font-bold ${parseInt(scores[`${sec.name}_${i}_b`]||"0",10)===v?"text-white":"text-gray-400"}`} style={parseInt(scores[`${sec.name}_${i}_b`]||"0",10)===v?{background:v?"#22c55e":"#ef4444"}:{}}>{v?"✓":"✗"}</button>)}</div></div>
            </div>
          </div>)}</div></div>})}
    </Card>;
  }
  if(cfg.type==="fcro"){
    return<Card className="p-5 space-y-3 border-l-4 border-orange-400">
      <div className="flex items-center justify-between"><h3 className="font-bold text-sm flex items-center gap-2"><I name="draw" className="text-orange-600 text-lg"/>{cfg.label}</h3><span className="text-xs font-bold px-2 py-1 rounded-full bg-orange-100 text-orange-700">PD: {puntajes[testId]||0}/36</span></div>
      <p className="text-[10px] text-gray-400">Taylor: 0 = ausente · 0.5 = deformado/mal ubicado · 1 = deformado bien ubicado o correcto mal ubicado · 2 = correcto y bien ubicado</p>
      <div className="rounded-lg border border-orange-100 bg-white p-1"><FCROFigure scores={scores} showNumbers={true} highlight={fcroHL}/></div>
      <div className="space-y-1 max-h-64 overflow-y-auto pr-1">{cfg.elements.map((el,i)=>{
        const v=parseFloat(scores[`e${i}`])||0;
        return<div key={i} onMouseEnter={()=>setFcroHL(i)} onMouseLeave={()=>setFcroHL(-1)} className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-orange-50/50">
          <span className="text-[10px] font-mono text-gray-400 w-5">{i+1}</span>
          <p className="flex-1 text-[11px] text-gray-600 truncate">{el}</p>
          <div className="flex gap-0.5">{[0,0.5,1,2].map(s=><button key={s} onClick={()=>setS(`e${i}`,String(s))} className={`w-8 h-6 rounded text-[10px] font-bold transition-all ${v===s?"text-white shadow":"text-gray-400 hover:bg-gray-100"}`} style={v===s?{background:s===2?"#22c55e":s===1?"#f59e0b":s===0.5?"#f97316":"#ef4444"}:{}}>{s}</button>)}</div>
        </div>})}</div>
    </Card>;
  }
  if(cfg.type==="memory_curve"){
    const trials=cfg.trials;
    return<Card className="p-5 space-y-4 border-l-4 border-cyan-400">
      <div className="flex items-center justify-between"><h3 className="font-bold text-sm flex items-center gap-2"><I name="neurology" className="text-cyan-600 text-lg"/>Curva de Memoria — {cfg.label}</h3><span className="text-[10px] font-bold text-cyan-700 bg-cyan-100 px-2 py-0.5 rounded-full">{cfg.words.length} palabras</span></div>
      <p className="text-[10px] text-gray-400">Marque las palabras recordadas en cada ensayo. En ensayos <strong>con clave</strong>, al pasar el cursor sobre cada palabra se muestra la clave semántica.</p>
      {/* Curva visual */}
      {(()=>{const tData=trials.filter(t=>t.type!=="recognition").map(tr=>parseInt(scores[`trial_${tr.id}_total`],10)||0);
        if(tData.some(v=>v>0)){const max=16;const w=280;const h=100;const step=w/(Math.max(tData.length-1,1));
        return<div className="rounded-xl p-3" style={{background:"#0f2a3d"}}>
          <svg width={w+40} height={h+30} className="mx-auto">
            {/* Grid */}
            {[0,4,8,12,16].map(v=><g key={v}><line x1="30" y1={h-v/max*h+5} x2={w+30} y2={h-v/max*h+5} stroke="#1e3a4d" strokeWidth="0.5"/><text x="20" y={h-v/max*h+9} fill="#64748b" fontSize="8" textAnchor="end">{v}</text></g>)}
            {/* Line */}
            <polyline fill="none" stroke={TEAL_LIGHT} strokeWidth="2" strokeLinejoin="round" points={tData.map((v,i)=>`${i*step+30},${h-v/max*h+5}`).join(" ")}/>
            {/* Dots */}
            {tData.map((v,i)=><g key={i}><circle cx={i*step+30} cy={h-v/max*h+5} r="4" fill={TEAL} stroke={TEAL_LIGHT} strokeWidth="1.5"/><text x={i*step+30} y={h+22} fill="#94a3b8" fontSize="7" textAnchor="middle">{trials.filter(t=>t.type!=="recognition")[i]?.id}</text></g>)}
          </svg>
        </div>}return null;
      })()}
      {/* Trials */}
      <div className="space-y-3 max-h-64 overflow-y-auto pr-1">{trials.map(tr=>{
        const total=parseInt(scores[`trial_${tr.id}_total`],10)||cfg.words.reduce((s,_,i)=>s+(scores[`trial_${tr.id}_w${i}`]==="1"?1:0),0);
        return<div key={tr.id} className="rounded-xl border border-gray-100 p-3 space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold" style={{color:tr.type==="free"?TEAL:tr.type==="cued"?"#7c3aed":"#f59e0b"}}><I name={tr.type==="free"?"record_voice_over":tr.type==="cued"?"help":"checklist"} className="text-xs mr-1"/>{tr.name}{tr.type==="cued"&&<span className="ml-1 text-[9px] font-normal text-purple-400">(dar clave si no recuerda)</span>}</p>
            <span className="text-xs font-mono font-bold" style={{color:TEAL}}>{total}/{cfg.words.length}</span>
          </div>
          <div className="flex flex-wrap gap-1">{cfg.words.map((w,i)=>{
            const checked=scores[`trial_${tr.id}_w${i}`]==="1";
            return<button key={i} onClick={()=>{const nv=checked?"0":"1";
              const wordKey=`trial_${tr.id}_w${i}`;const totalKey=`trial_${tr.id}_total`;
              const newTotal=cfg.words.reduce((s,_,j)=>s+((j===i?nv:(scores[`trial_${tr.id}_w${j}`]||"0"))==="1"?1:0),0);
              /* Batch update: ambas keys en una sola mutación para evitar closure estancada */
              setItemScores(prev=>{const cur=prev[testId]||{};return{...prev,[testId]:{...cur,[wordKey]:nv,[totalKey]:String(newTotal)}}});
              setPuntajes(p=>({...p,[testId]:String(newTotal)}));
            }} className={`px-2 py-1 rounded text-[10px] font-semibold transition-all ${checked?"text-white shadow-sm":"text-gray-400 hover:bg-gray-100"}`} style={checked?{background:TEAL}:{}} title={cfg.categories?.[i]?`Clave: ${cfg.categories[i]}`:""}>{w}</button>
          })}</div>
        </div>})}</div>
    </Card>;
  }
  if(cfg.type==="tmt"){
    return<Card className="p-5 space-y-3 border-l-4 border-amber-400">
      <h3 className="font-bold text-sm flex items-center gap-2"><I name="timer" className="text-amber-600 text-lg"/>{cfg.label}</h3>
      <div className="grid grid-cols-2 gap-3">
        <div><Label>Tiempo (seg)</Label><input type="number" value={scores.tiempo||""} onChange={e=>setS("tiempo",e.target.value)} className="w-full h-10 text-center text-lg font-bold rounded-xl border-none focus:ring-2 focus:ring-amber-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="seg"/></div>
        <div><Label>Errores</Label><input type="number" value={scores.errores||""} onChange={e=>setS("errores",e.target.value)} className="w-full h-10 text-center text-lg font-bold rounded-xl border-none focus:ring-2 focus:ring-red-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="0"/></div>
      </div>
      <p className="text-[10px] text-gray-400">Máximo: {cfg.maxTime}s. PD = tiempo en segundos.</p>
    </Card>;
  }
  if(cfg.type==="stroop"){
    return<Card className="p-5 space-y-3 border-l-4 border-rose-400">
      <h3 className="font-bold text-sm flex items-center gap-2"><I name="palette" className="text-rose-600 text-lg"/>{cfg.label}</h3>
      <div className="space-y-2">{cfg.conditions.map((c,i)=>
        <div key={c} className="flex items-center gap-3 p-2 rounded-lg" style={{background:i===2?"rgba(225,29,72,0.08)":"var(--ns-subtle)"}}>
          <span className="text-xs font-bold w-28" style={{color:i===2?"#e11d48":"var(--ns-muted)"}}>{c}</span>
          {/* §H12-fix: recalculamos interferencia ante CUALQUIER cambio
              de c0/c1/c2 (antes solo se recalculaba al modificar c2,
              quedando obsoleta si después se corregía c0 o c1).
              Fórmula Golden: I = c2 - (c0*c1)/(c0+c1). */}
          <input type="number" value={scores[`c${i}`]||""} onChange={e=>{setS(`c${i}`,e.target.value);const ns={...scores,[`c${i}`]:e.target.value};const c0=parseInt(ns.c0,10)||0;const c1=parseInt(ns.c1,10)||0;const c2=parseInt(ns.c2,10)||0;if(c0>0&&c1>0&&c2>0&&(c0+c1)>0){const interf=c2-((c0*c1)/(c0+c1));setS("interferencia",String(Math.round(interf)))}}} className="w-16 h-8 text-center text-sm font-bold rounded-lg border-none" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="—"/>
          <span className="text-[10px] text-gray-400">ítems</span>
        </div>
      )}</div>
      {scores.interferencia&&<div className="text-xs font-bold text-center p-2 rounded-lg" style={{background:"rgba(159,18,57,0.1)",color:"#9f1239"}}>Interferencia: {scores.interferencia}</div>}
    </Card>;
  }
  if(cfg.type==="caras"){
    return<Card className="p-5 space-y-3 border-l-4 border-sky-400">
      <h3 className="font-bold text-sm flex items-center gap-2"><I name="face" className="text-sky-600 text-lg"/>{cfg.label}</h3>
      <div className="grid grid-cols-2 gap-3">
        <div><Label>Aciertos</Label><input type="number" value={scores.aciertos||""} onChange={e=>setS("aciertos",e.target.value)} className="w-full h-10 text-center font-bold rounded-xl border-none focus:ring-2 focus:ring-sky-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="0"/></div>
        <div><Label>Errores</Label><input type="number" value={scores.errores||""} onChange={e=>setS("errores",e.target.value)} className="w-full h-10 text-center font-bold rounded-xl border-none focus:ring-2 focus:ring-red-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="0"/></div>
      </div>
      {/* §M11-fix: parseInt repetido 8 veces → extraído a variables.
          También arregla §B4: usar comparación con `>0` en lugar de
          truthy permite mostrar el panel con "0" o "0.x". */}
      {(()=>{const A=parseInt(scores.aciertos,10)||0;const E=parseInt(scores.errores,10)||0;const PD=Math.max(0,A-E);const denom=A+E;const ICI=(PD>0&&denom>0)?(PD/denom):0;return A>0&&<div className="text-xs font-bold text-center p-2 rounded-lg" style={{background:`${TEAL}15`,color:TEAL}}>PD: {PD} · ICI: {ICI.toFixed(2)}</div>})()}
    </Card>;
  }
  if(cfg.type==="timed_count"){
    return<Card className="p-5 space-y-3 border-l-4 border-emerald-400">
      <h3 className="font-bold text-sm flex items-center gap-2"><I name="speed" className="text-emerald-600 text-lg"/>{cfg.label}</h3>
      <p className="text-[10px] text-gray-400">{cfg.instruction}</p>
      <div><Label>Respuestas Correctas</Label><input type="number" value={scores.correctas||""} onChange={e=>setS("correctas",e.target.value)} className="w-full h-12 text-center text-xl font-bold rounded-xl border-none focus:ring-2 focus:ring-emerald-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="0"/></div>
    </Card>;
  }
  /* §12.5 — Rey 15-Item Test (validez de síntomas) */
  if(cfg.type==="validity_grid"){
    const recalled=(cfg.items||[]).filter(it=>scores[`r${it.n}`]==="1").length;
    const recognized=parseInt(scores.reconocimiento,10)||0;
    const cutoff=cfg.cutoff_evocacion??9;
    const low=recalled<=cutoff;
    const lowRec=recognized>0&&recognized<=cfg.cutoff_reconocimiento;
    const combined=low&&lowRec;
    /* Auto-actualizar PD con el total de evocación */
    return<Card className="p-5 space-y-4 border-l-4" style={{borderColor:"#7c3aed"}}>
      {licenseBanner}
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm flex items-center gap-2"><I name="checklist" className="text-purple-600 text-lg"/>{cfg.label}</h3>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold px-2 py-1 rounded-full ${low?"bg-red-100 text-red-700":"bg-green-100 text-green-700"}`}>{recalled}/{cfg.items.length} recordados</span>
          {low&&<span className="text-[10px] font-bold text-red-600 flex items-center gap-1"><I name="warning" className="text-sm"/>Corte ≤{cutoff}</span>}
        </div>
      </div>
      {/* Tarjeta modelo (grilla) */}
      <div className="rounded-xl p-4 border-2 border-dashed border-purple-200" style={{background:"rgba(109,40,217,0.06)"}}>
        <p className="text-[10px] font-bold text-purple-600 uppercase tracking-wider mb-3">Grilla estímulo (mostrar 10 seg.)</p>
        <div className="grid gap-2" style={{gridTemplateColumns:"repeat(3,1fr)",maxWidth:200}}>
          {(cfg.grid||[]).flat().map((cell,i)=>(
            <div key={i} className="h-10 flex items-center justify-center rounded-lg font-bold text-base border" style={{background:"var(--ns-card)",borderColor:"#c4b5fd",color:"#5b21b6"}}>{cell}</div>
          ))}
        </div>
      </div>
      {/* Ítems recordados (marcar con ✓) */}
      <div>
        <p className="text-[10px] font-bold text-purple-600 uppercase tracking-wider mb-2">Ítems recordados por el paciente</p>
        <div className="grid grid-cols-5 gap-1.5">
          {(cfg.items||[]).map(it=>{
            const chk=scores[`r${it.n}`]==="1";
            return<button key={it.n} onClick={()=>{const nv=chk?"0":"1";const ns={...scores,[`r${it.n}`]:nv};setItemScores(p=>({...p,[testId]:ns}));/* §C1-fix: paréntesis correctos — antes contaba items con cualquier valor truthy, no solo "1". */const tot=(cfg.items||[]).filter(x=>(ns[`r${x.n}`]||"0")==="1").length;setPuntajes(p=>({...p,[testId]:String(tot)}));}} className={`h-10 rounded-lg font-bold text-sm border-2 transition-all ${chk?"border-purple-500 text-white":"border-purple-100 text-purple-400 hover:border-purple-300"}`} style={{background:chk?"#7c3aed":"var(--ns-card)"}}>{it.label}</button>
          })}
        </div>
      </div>
      {/* Reconocimiento opcional */}
      <div className="flex items-center gap-4">
        <div className="flex-1"><Label>Reconocimiento (lista 30 ítems, opcional)</Label><input type="number" min={0} max={30} value={scores.reconocimiento||""} onChange={e=>{setS("reconocimiento",e.target.value)}} className="w-full h-10 text-center font-bold rounded-xl border-none focus:ring-2 focus:ring-purple-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="— / 30"/></div>
        {recognized>0&&<span className={`text-xs font-bold px-2 py-1 rounded-full shrink-0 ${lowRec?"bg-red-100 text-red-700":"bg-green-100 text-green-700"}`}>{recognized}/30 {lowRec?"⚠":"✓"}</span>}
      </div>
      {/* Interpretación */}
      {(low||combined)&&<div className={`p-3 rounded-xl border-l-4 text-xs leading-relaxed ${combined?"border-red-500":"border-amber-400"}`} style={{background:combined?"rgba(239,68,68,0.08)":"rgba(251,191,36,0.1)",color:combined?"#991b1b":"#92400e"}}>
        <p className="font-bold mb-1">{combined?"Alta sospecha de bajo esfuerzo / simulación":"Screening positivo — bajo esfuerzo posible"}</p>
        <p>{combined?"Evocación ≤9 Y reconocimiento ≤20: alta especificidad para simulación (Boone et al. 2002). Complementar con TOMM o VSVT.":"Evocación ≤"+cutoff+" (corte Rey 1964). Por sí solo tiene baja especificidad; combinar con contexto clínico y otras pruebas de validez."}</p>
      </div>}
    </Card>;
  }
  return null;
};

export default ReactivePanel;
