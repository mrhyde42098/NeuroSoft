/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/ReactivePanel.jsx — Captura ítem-por-ítem por subprueba
 * Renderiza ítems segun el tipo de REACTIVOS[testId] y auto-calcula PD.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { Card, _Btn, I, Label } from "../../ui/primitives.jsx";
import SectionCard from "../../ui/SectionCard.jsx";
import { TEAL, TEAL_LIGHT } from "../../ui/tokens.js";
import { REACTIVOS } from "../../data/clinical.js";
import { estadoAceptacionGlobal } from "../../data/pearsonProtected.js";
import ScoringGuide from "./ScoringGuide.jsx";
import { getItem as getProtocolItem, _getSubtest } from "../../data/protocolLoader.js";
import { CubosPattern } from "../../data/PatronesCubos.jsx";
import FCRODisplay from "../../data/FCRODisplay.jsx";
import _BlockStimulus from "./BlockStimulus.jsx";
import ItemStimulus from "./ItemStimulus.jsx";
import PresentationOverlay from "./PresentationOverlay.jsx";
import { itemMappedStimuli } from "./stimulusHelpers.js";

function resolveItemStimulus(stimuli, testId, itemN) {
  const scoped = itemMappedStimuli(stimuli, testId);
  if (!scoped.length || itemN == null) return null;
  const sid = String(itemN);
  return (
    scoped.find(
      (s) =>
        s.item_id === sid
        || s.item_id === `item_${sid}`
        || s.item_id === `i${sid}`
        || String(s.orden) === sid,
    ) || null
  );
}

/* ═══ Componente ReactivePanel — Renderiza ítems según tipo ═══ */
export const ReactivePanel=({testId,puntajes,setPuntajes,itemScores,setItemScores,estimulos=[],textScale="normal"})=>{
  const cfg=REACTIVOS[testId];
  const lg=textScale==="large"||["scored_items","verbal_pistas","memory_curve","validity_grid"].includes(cfg?.type);
  const txtMain=lg?"text-[17px] leading-snug":"text-[15px]";
  const txtSub=lg?"text-sm":"text-[11px]";
  const txtWord=lg?"text-sm px-3 py-1.5 font-semibold":"text-[10px] px-2 py-1 font-semibold";
  const [fcroHL,setFcroHL]=useState(-1);
  const [overlayItem,setOverlayItem]=useState(null);
  const [showAnswers,setShowAnswers]=useState(false);
  const [trialsCollapsed,setTrialsCollapsed]=useState({});
  const perTestStim=itemMappedStimuli(estimulos,testId);
  const openOverlay=(itemN)=>{
    const st=resolveItemStimulus(estimulos,testId,itemN);
    if(st)setOverlayItem({ stimulus: st, itemN });
  };
  const itemList=Array.isArray(cfg?.items)?cfg.items:[];
  const overlayIdx=overlayItem?itemList.findIndex((it)=>it.n===overlayItem.itemN):-1;
  if(!cfg)return null;
  const items=Array.isArray(cfg.items)?cfg.items:[];
  const elements=Array.isArray(cfg.elements)?cfg.elements:[];
  const scores=itemScores[testId]||{};
  const setS=(key,val)=>{
    const next={...scores,[key]:val};
    setItemScores(p=>({...p,[testId]:next}));
    /* Auto-calcular PD total */
    let total=0;
    if(cfg.type==="items")items.forEach(it=>{total+=(parseFloat(next[`i${it.n}`])||0)});
    /* §M2-fix: parseInt SIEMPRE con radix 10 — evita interpretación octal/hex
     * accidental si el clínico escribe "08" o "0x" en un campo PD. */
    else if(cfg.type==="scored_items")items.forEach(it=>{total+=(parseInt(next[`i${it.n}`],10)||0)});
    else if(cfg.type==="fcro")elements.forEach((_,i)=>{total+=(parseFloat(next[`e${i}`])||0)});
    else if(cfg.type==="digits"){cfg.sections.forEach(sec=>{sec.sequences.forEach((sq,i)=>{total+=(parseInt(next[`${sec.name}_${i}_a`],10)||0);total+=(parseInt(next[`${sec.name}_${i}_b`],10)||0)})});}
    else if(cfg.type==="memory_curve"){const trials=cfg.trials.filter(t=>t.type!=="recognition");const lastTrial=trials[trials.length-1];if(lastTrial)total=parseInt(next[`trial_${lastTrial.id}_total`],10)||0;else total=0;}
    else if(cfg.type==="tmt"){total=parseInt(next.tiempo,10)||0;}
    else if(cfg.type==="stroop"){total=parseInt(next.interferencia,10)||0;}
    else if(cfg.type==="caras"){total=Math.max(0,(parseInt(next.aciertos,10)||0)-(parseInt(next.errores,10)||0));}
    else if(cfg.type==="timed_count"){total=parseInt(next.correctas,10)||0;}
    else if(cfg.type==="validity_grid"){total=(cfg.items||[]).filter(it=>next[`r${it.n}`]==="1").length;}
    else if(cfg.type==="ln_sequences"){items.forEach(it=>{(it.trials||[]).forEach((_,ti)=>{total+=(parseInt(next[`i${it.n}_t${ti}`],10)||0)})})}
    else if(cfg.type==="visual_cuadernillo"){items.forEach(it=>{total+=(parseInt(next[`i${it.n}`],10)||0)})}
    else if(cfg.type==="verbal_pistas"){items.forEach(it=>{total+=(parseInt(next[`i${it.n}`],10)||0)})}
    setPuntajes(p=>({...p,[testId]:String(total)}));
  };
  const pearsonOk=estadoAceptacionGlobal().aceptado;
  /* Banner de licencia editorial (Sprint 12) */
  const licenseBanner = cfg.requires_license && (
    <div className="p-3 mb-3 rounded-xl flex items-center gap-3" style={{borderColor:"#f59e0b",background:"rgba(251,191,36,0.1)"}}>
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
    return<>{licenseBanner}<Card className="p-5 space-y-3 ">
      <div className="flex items-center justify-between"><h3 className="font-bold text-sm flex items-center gap-2"><I name="grid_view" className="text-purple-600 text-lg"/>Reactivos — {cfg.label}</h3><span className="text-xs font-bold px-2 py-1 rounded-full bg-purple-100 text-purple-700">PD: {puntajes[testId]||0}</span></div>
      <div className="space-y-2 max-h-[32rem] overflow-y-auto pr-1">{items.map(it=>{
        const v=scores[`i${it.n}`]||"";
        const itemStim=resolveItemStimulus(estimulos,testId,it.n);
        return<div key={it.n} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-purple-50/50 transition-all">
          <span className="text-sm font-mono font-bold text-gray-400 w-6">{it.n}</span>
          {isCubos&&<div className="shrink-0 w-20 h-20 rounded border border-purple-100 bg-white overflow-hidden flex items-center justify-center" title={`Diseño ${it.n}`}><CubosPattern itemNum={it.n} test={cubosTest} size={24}/></div>}
          {!isCubos&&itemStim&&<ItemStimulus stimulus={itemStim} compact onExpand={()=>openOverlay(it.n)}/>}
          <div className="flex-1 min-w-0"><p className="text-[15px] text-gray-600 truncate">{it.desc}</p>
            <p className="text-[11px] text-gray-400">{it.cubos} cubos · {it.tiempo}s{it.bonus?" · +bonus":""} · max {it.max}</p></div>
          <input type="number" min="0" max={it.max} value={v} onChange={e=>setS(`i${it.n}`,e.target.value)} className="w-16 h-10 text-center text-base font-bold rounded-lg border-none focus:ring-2 focus:ring-purple-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="—"/>
        </div>})}</div>
    </Card></>;
  }
  if(cfg.type==="scored_items"){
    // §v5-hotfix: scoring global con fallback a [0,1] (binario) si no
    // está definido, para que ningún test rompa el panel.
    const scoringArr = Array.isArray(cfg.scoring) ? cfg.scoring : [0, 1];
    const _maxPer = scoringArr[scoringArr.length - 1];
    const hasAnswerKey = items.some(it=>it.ans||it.respuesta);
    return<Card className="p-5 space-y-3 ">
      <div className="flex items-center justify-between gap-2"><h3 className="font-bold text-sm flex items-center gap-2"><I name="list_alt" className="text-purple-600 text-lg"/>Reactivos — {cfg.label}</h3>
        <div className="flex items-center gap-2">
          {hasAnswerKey&&<button type="button" onClick={()=>setShowAnswers(s=>!s)} className={`text-[10px] font-bold px-2.5 py-1 rounded-full transition-all flex items-center gap-1 ${showAnswers?"bg-purple-600 text-white":"bg-purple-100 text-purple-700 hover:bg-purple-200"}`} title="Mostrar u ocultar la respuesta correcta del manual"><I name={showAnswers?"visibility":"visibility_off"} className="text-xs"/>{showAnswers?"Ocultar resp.":"Ver resp."}</button>}
          <span className="text-xs font-bold px-2 py-1 rounded-full bg-purple-100 text-purple-700">PD: {puntajes[testId]||0}</span>
        </div>
      </div>
      <div className="space-y-1.5 max-h-[32rem] overflow-y-auto pr-1">{items.map(it=>{
        const v=parseInt(scores[`i${it.n}`],10)||0;const label=it.pair||it.word||it.q||`Ítem ${it.n}`;
        const protoItem = getProtocolItem(testId, it.n);
        // Si el test define un máximo por ítem, respetarlo (ej. WISC-IV Sem 1-2 = max 1)
        const itemMax = (cfg.maxPerItem && cfg.maxPerItem[it.n] !== undefined)
          ? cfg.maxPerItem[it.n] : _maxPer;
        const itemScoring = scoringArr.filter(s => s <= itemMax);
        const itemStim=resolveItemStimulus(estimulos,testId,it.n);
        return<div key={it.n} className="space-y-1">
        <div className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 transition-all">
          <span className="text-sm font-mono font-bold text-gray-400 w-6">{it.n}</span>
          {itemStim?<ItemStimulus stimulus={itemStim} compact onExpand={()=>openOverlay(it.n)}/>:perTestStim.length>0&&<span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 shrink-0" title="Suba estímulo con item_id en Configuración">sin lámina</span>}
          <div className="flex-1 min-w-0">
            <p className={`${txtMain} text-gray-600 truncate`} title={label}>{label}</p>
            {showAnswers&&(it.ans||it.respuesta)&&<p className={`${txtSub} font-semibold mt-0.5 flex items-center gap-1`} style={{color:TEAL}}><I name="key" className="text-[12px]"/>{it.ans||it.respuesta}</p>}
          </div>
          <div className="flex gap-1">{itemScoring.map(s=><button key={s} onClick={()=>setS(`i${it.n}`,String(s))} className={`w-11 h-10 rounded-lg text-sm font-bold transition-all ${v===s?"text-white shadow":"text-gray-500 hover:bg-gray-100"}`} style={v===s?{background:TEAL}:{}}>{s}</button>)}</div>
        </div>
        {protoItem && <ScoringGuide item={protoItem} testId={testId}/>}
        </div>})}</div>
      {overlayItem&&<PresentationOverlay open stimulus={overlayItem.stimulus} label={`${cfg.label} — ítem ${overlayItem.itemN}`} onClose={()=>setOverlayItem(null)} hasPrev={overlayIdx>0} hasNext={overlayIdx>=0&&overlayIdx<itemList.length-1} onPrev={()=>{const prev=itemList[overlayIdx-1];if(prev)openOverlay(prev.n)}} onNext={()=>{const next=itemList[overlayIdx+1];if(next)openOverlay(next.n)}}/>}
    </Card>;
  }
  if(cfg.type==="digits"){
    return<Card className="p-5 space-y-4 ">
      <div className="flex items-center justify-between"><h3 className="font-bold text-sm flex items-center gap-2"><I name="pin" className="text-indigo-600 text-lg"/>Dígitos — {cfg.label}</h3><span className="text-xs font-bold px-2 py-1 rounded-full bg-indigo-100 text-indigo-700">PD: {puntajes[testId]||0}</span></div>
      {cfg.sections.map(sec=>{
        const secTotal=sec.sequences.reduce((s,_,i)=>(s+(parseInt(scores[`${sec.name}_${i}_a`],10)||0)+(parseInt(scores[`${sec.name}_${i}_b`],10)||0)),0);
        return<div key={sec.name} className="space-y-2">
        <div className="flex items-center justify-between"><p className="text-xs font-bold text-indigo-600 uppercase tracking-wider">{sec.name}</p><span className="text-[10px] font-bold text-indigo-500">{secTotal}/{sec.sequences.length*2}</span></div>
        <div className="space-y-1.5 max-h-[26rem] overflow-y-auto">{sec.sequences.map((sq,i)=>
          <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-indigo-50/50">
            <span className="text-xs font-mono font-bold text-gray-400 w-5">{sq.len}</span>
            <div className="flex-1 grid grid-cols-2 gap-3">
              <div className="flex items-center justify-between gap-2"><span className="text-base text-gray-600 font-mono font-bold tracking-wider">{sq.a}</span>
                <div className="flex gap-1">{[0,1].map(v=><button key={v} onClick={()=>setS(`${sec.name}_${i}_a`,String(v))} className={`w-9 h-9 rounded-lg text-sm font-bold ${parseInt(scores[`${sec.name}_${i}_a`]||"0",10)===v?"text-white shadow":"text-gray-400 hover:bg-gray-100"}`} style={parseInt(scores[`${sec.name}_${i}_a`]||"0",10)===v?{background:v?"#22c55e":"#ef4444"}:{}}>{v?"✓":"✗"}</button>)}</div></div>
              <div className="flex items-center justify-between gap-2"><span className="text-base text-gray-600 font-mono font-bold tracking-wider">{sq.b}</span>
                <div className="flex gap-1">{[0,1].map(v=><button key={v} onClick={()=>setS(`${sec.name}_${i}_b`,String(v))} className={`w-9 h-9 rounded-lg text-sm font-bold ${parseInt(scores[`${sec.name}_${i}_b`]||"0",10)===v?"text-white shadow":"text-gray-400 hover:bg-gray-100"}`} style={parseInt(scores[`${sec.name}_${i}_b`]||"0",10)===v?{background:v?"#22c55e":"#ef4444"}:{}}>{v?"✓":"✗"}</button>)}</div></div>
            </div>
          </div>)}</div></div>})}
    </Card>;
  }
  if(cfg.type==="fcro"){
    const fcroClean=showAnswers;/* reutilizamos el toggle: "original sin marcas" */
    return<Card className="p-5 space-y-3 ">
      <div className="flex items-center justify-between gap-2"><h3 className="font-bold text-sm flex items-center gap-2"><I name="draw" className="text-orange-600 text-lg"/>{cfg.label}</h3>
        <div className="flex items-center gap-2">
          <button type="button" onClick={()=>setShowAnswers(s=>!s)} className={`text-[10px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1 transition-all ${fcroClean?"bg-orange-600 text-white":"bg-orange-100 text-orange-700 hover:bg-orange-200"}`} title="Alternar entre lámina numerada (calificación) y original sin marcas"><I name={fcroClean?"label_off":"tag"} className="text-xs"/>{fcroClean?"Original":"Numerada"}</button>
          <button type="button" onClick={()=>setOverlayItem({fcro:true})} className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-orange-100 text-orange-700 hover:bg-orange-200 flex items-center gap-1" title="Ampliar lámina a pantalla completa"><I name="zoom_in" className="text-xs"/>Ampliar</button>
          <span className="text-xs font-bold px-2 py-1 rounded-full bg-orange-100 text-orange-700">PD: {puntajes[testId]||0}/36</span>
        </div>
      </div>
      <p className="text-[10px]" style={{color:"var(--ns-muted)"}}>Taylor · Lámina con 18 elementos. Marque 0 / 0.5 / 1 / 2 según copia o recobro del paciente. Use <b>Numerada</b> para guiar la calificación o <b>Original</b> para comparar sin marcas; <b>Ampliar</b> abre la lámina en grande.</p>
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_minmax(240px,38%)] gap-4 items-start">
        <div className="rounded-xl border-2 border-orange-200 bg-white p-4 flex items-center justify-center min-h-[300px] shadow-sm cursor-zoom-in" onClick={()=>setOverlayItem({fcro:true})} title="Clic para ampliar">
          <div className="w-full max-w-[560px]">
            <FCRODisplay scores={scores} highlight={fcroHL} showNumbers={!fcroClean} scoringMode={!fcroClean}/>
            {fcroHL>=0&&<p className="text-center text-[10px] font-bold mt-2 text-orange-700">Elemento {fcroHL+1}: {elements[fcroHL]}</p>}
          </div>
        </div>
        <div className="space-y-1 max-h-[min(420px,55vh)] overflow-y-auto pr-1 rounded-lg border border-orange-100 bg-orange-50/30 p-2">
          {elements.map((el,i)=>{
        const v=parseFloat(scores[`e${i}`])||0;
        const active=fcroHL===i;
        return<div key={i} onMouseEnter={()=>setFcroHL(i)} onMouseLeave={()=>setFcroHL(-1)} className={`flex items-center gap-2 p-2 rounded-lg transition-all ${active?"bg-white ring-2 ring-orange-400 shadow-sm":"hover:bg-white/80"}`}>
          <span className={`text-sm font-mono font-bold w-6 shrink-0 ${active?"text-orange-700":"text-gray-400"}`}>{i+1}</span>
          <p className="flex-1 text-xs leading-snug truncate" style={{color:"var(--ns-text)"}} title={el}>{el}</p>
          <div className="flex gap-0.5 shrink-0">{[0,0.5,1,2].map(s=><button key={s} type="button" onClick={()=>setS(`e${i}`,String(s))} className={`w-9 h-9 rounded-md text-xs font-bold transition-all ${v===s?"text-white shadow":"text-gray-500 hover:bg-gray-100"}`} style={v===s?{background:s===2?"#22c55e":s===1?"#f59e0b":s===0.5?"#f97316":"#ef4444"}:{}}>{s}</button>)}</div>
        </div>})}
        </div>
      </div>
      {overlayItem?.fcro&&<div className="fixed inset-0 z-[80] flex flex-col bg-black/92 p-4" onClick={()=>setOverlayItem(null)}>
        <div className="flex items-center justify-between mb-3 shrink-0">
          <p className="text-white font-bold text-sm flex items-center gap-2"><I name="draw"/>{cfg.label} — calificación ampliada</p>
          <div className="flex items-center gap-2" onClick={e=>e.stopPropagation()}>
            <button type="button" onClick={()=>setShowAnswers(s=>!s)} className="px-3 py-1.5 rounded-full text-xs font-bold bg-white/15 text-white hover:bg-white/25 flex items-center gap-1"><I name={fcroClean?"tag":"label_off"} className="text-sm"/>{fcroClean?"Capa numerada":"Solo original"}</button>
            <button type="button" onClick={()=>setOverlayItem(null)} className="px-3 py-1.5 rounded-full text-xs font-bold bg-white/15 text-white hover:bg-white/25 flex items-center gap-1"><I name="close" className="text-sm"/>Cerrar</button>
          </div>
        </div>
        <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-4" onClick={e=>e.stopPropagation()}>
          <div className="bg-white rounded-xl p-4 overflow-auto flex items-center justify-center relative min-h-[50vh]">
            <div className="relative w-full max-w-4xl">
              <img src="/assets/fcro/fcro-lamina.png" alt="FCRO original" className="w-full h-auto object-contain"/>
              {!fcroClean&&(
                <img src="/assets/fcro/fcro-lamina-numerada.png" alt="FCRO numerada" className="absolute inset-0 w-full h-full object-contain pointer-events-none" style={{opacity:0.72,mixBlendMode:"multiply"}}/>
              )}
            </div>
          </div>
          <div className="bg-white/95 rounded-xl p-3 overflow-y-auto max-h-full space-y-1">
            <p className="text-xs font-bold text-orange-700 mb-2 sticky top-0 bg-white/95 py-1">Calificar elementos (0 · 0.5 · 1 · 2)</p>
            {elements.map((el,i)=>{
              const v=parseFloat(scores[`e${i}`])||0;
              const active=fcroHL===i;
              return<div key={i} onMouseEnter={()=>setFcroHL(i)} onMouseLeave={()=>setFcroHL(-1)} className={`flex items-center gap-2 p-2 rounded-lg ${active?"ring-2 ring-orange-400 bg-orange-50":""}`}>
                <span className="text-sm font-mono font-bold w-6 text-orange-700">{i+1}</span>
                <p className="flex-1 text-xs truncate" title={el}>{el}</p>
                <div className="flex gap-0.5 shrink-0">{[0,0.5,1,2].map(s=><button key={s} type="button" onClick={()=>setS(`e${i}`,String(s))} className={`w-9 h-9 rounded-md text-xs font-bold ${v===s?"text-white shadow":"text-gray-500 hover:bg-gray-100"}`} style={v===s?{background:s===2?"#22c55e":s===1?"#f59e0b":s===0.5?"#f97316":"#ef4444"}:{}}>{s}</button>)}</div>
              </div>})}
          </div>
        </div>
      </div>}
    </Card>;
  }
  if(cfg.type==="memory_curve"){
    const trials=cfg.trials;
    const allCollapsed=trials.length>0&&trials.every(tr=>trialsCollapsed[tr.id]);
    const toggleAll=()=>{
      if(allCollapsed)setTrialsCollapsed({});
      else setTrialsCollapsed(Object.fromEntries(trials.map(tr=>[tr.id,true])));
    };
    return<Card className="p-5 space-y-4 ">
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <h3 className="font-bold text-sm flex items-center gap-2"><I name="neurology" className="text-cyan-600 text-lg"/>Curva de Memoria — {cfg.label}</h3>
        <div className="flex items-center gap-2">
          <button type="button" onClick={toggleAll} className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-cyan-100 text-cyan-800 hover:bg-cyan-200 flex items-center gap-1">
            <I name={allCollapsed?"unfold_more":"unfold_less"} className="text-xs"/>
            {allCollapsed?"Mostrar todo":"Ocultar todo"}
          </button>
          <span className="text-[10px] font-bold text-cyan-700 bg-cyan-100 px-2 py-0.5 rounded-full">{cfg.words.length} palabras</span>
        </div>
      </div>
      <p className={`${txtSub} text-gray-500`}>Marque las palabras recordadas en cada ensayo. En ensayos <strong>con clave</strong>, al pasar el cursor sobre cada palabra se muestra la clave semántica.</p>
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
      <div className="space-y-3 max-h-[min(520px,65vh)] overflow-y-auto pr-1">{trials.map(tr=>{
        const total=parseInt(scores[`trial_${tr.id}_total`],10)||cfg.words.reduce((s,_,i)=>s+(scores[`trial_${tr.id}_w${i}`]==="1"?1:0),0);
        const collapsed=trialsCollapsed[tr.id];
        return<div key={tr.id} className="rounded-xl border border-gray-100 p-3 space-y-2">
          <div className="flex items-center justify-between cursor-pointer" onClick={()=>setTrialsCollapsed(p=>({...p,[tr.id]:!p[tr.id]}))}>
            <p className={`${txtSub} font-bold flex items-center gap-1`} style={{color:tr.type==="free"?TEAL:tr.type==="cued"?"#7c3aed":"#f59e0b"}}>
              <I name={collapsed?"chevron_right":"expand_more"} className="text-sm"/>
              <I name={tr.type==="free"?"record_voice_over":tr.type==="cued"?"help":"checklist"} className="text-xs mr-1"/>{tr.name}{tr.type==="cued"&&<span className="ml-1 text-[9px] font-normal text-purple-400">(dar clave si no recuerda)</span>}
            </p>
            <span className={`${txtSub} font-mono font-bold`} style={{color:TEAL}}>{total}/{cfg.words.length}</span>
          </div>
          {!collapsed&&<div className="flex flex-wrap gap-1.5">{cfg.words.map((w,i)=>{
            const checked=scores[`trial_${tr.id}_w${i}`]==="1";
            return<button key={i} onClick={()=>{const nv=checked?"0":"1";
              const wordKey=`trial_${tr.id}_w${i}`;const totalKey=`trial_${tr.id}_total`;
              const newTotal=cfg.words.reduce((s,_,j)=>s+((j===i?nv:(scores[`trial_${tr.id}_w${j}`]||"0"))==="1"?1:0),0);
              /* Batch update: ambas keys en una sola mutación para evitar closure estancada */
              setItemScores(prev=>{const cur=prev[testId]||{};return{...prev,[testId]:{...cur,[wordKey]:nv,[totalKey]:String(newTotal)}}});
              setPuntajes(p=>({...p,[testId]:String(newTotal)}));
            }} className={`${txtWord} rounded transition-all ${checked?"text-white shadow-sm":"text-gray-500 hover:bg-gray-100"}`} style={checked?{background:TEAL}:{}} title={cfg.categories?.[i]?`Clave: ${cfg.categories[i]}`:""}>{w}</button>
          })}</div>}
        </div>})}</div>
      {/* ── Interpretación automática de la curva (heurística determinista
       *    a partir de los totales por ensayo) + casilla "incluir en informe".
       *    No llama a ningún servicio externo; es orientativa para el clínico. ── */}
      {(()=>{
        const freeTrials=trials.filter(t=>t.type==="free");
        const cuedTrials=trials.filter(t=>t.type==="cued");
        const val=(tr)=>parseInt(scores[`trial_${tr.id}_total`],10)||0;
        const firstFree=freeTrials.length?val(freeTrials[0]):0;
        const lastFree=freeTrials.length?val(freeTrials[freeTrials.length-1]):0;
        const maxCued=cuedTrials.reduce((m,tr)=>Math.max(m,val(tr)),0);
        const maxFree=freeTrials.reduce((m,tr)=>Math.max(m,val(tr)),0);
        const max=cfg.words.length;
        const anyData=freeTrials.concat(cuedTrials).some(tr=>val(tr)>0);
        if(!anyData)return null;
        const cueBenefit=maxCued-maxFree;
        let patron,detalle,color;
        if(maxCued>=max-2){patron="Beneficio de claves conservado";detalle="El recuerdo facilitado por claves alcanza casi el total: la codificación/almacenamiento están preservados y el fallo (si lo hay) es de recuperación — patrón compatible con perfil subcortical/disejecutivo más que amnésico.";color="#0d9488";}
        else if(maxCued<max*0.6){patron="Déficit de almacenamiento";detalle="Incluso con claves semánticas el recuerdo permanece bajo: sugiere compromiso de codificación/almacenamiento (perfil amnésico de tipo hipocampal). Correlacionar con recobro diferido y reconocimiento.";color="#dc2626";}
        else{patron="Patrón mixto / a precisar";detalle="El beneficio de claves es parcial. Valore aprendizaje a lo largo de los ensayos, intrusiones y recobro diferido antes de concluir.";color="#d97706";}
        const aprendizaje=lastFree-firstFree;
        return<div className="rounded-xl p-3 space-y-2" style={{background:`${color}10`,border:`1px solid ${color}40`}}>
          <div className="flex items-center gap-2">
            <I name="auto_awesome" className="text-sm" style={{color}}/>
            <p className="text-xs font-extrabold" style={{color}}>Interpretación automática de la curva</p>
          </div>
          <p className="text-xs font-bold" style={{color}}>{patron}</p>
          <p className="text-[11px] leading-relaxed" style={{color:"var(--ns-text)"}}>{detalle}</p>
          <div className="flex flex-wrap gap-2 text-[10px]" style={{color:"var(--ns-muted)"}}>
            <span className="px-2 py-0.5 rounded-full" style={{background:"var(--ns-subtle)"}}>Libre máx: {maxFree}/{max}</span>
            <span className="px-2 py-0.5 rounded-full" style={{background:"var(--ns-subtle)"}}>Con clave máx: {maxCued}/{max}</span>
            <span className="px-2 py-0.5 rounded-full" style={{background:"var(--ns-subtle)"}}>Beneficio de clave: +{Math.max(0,cueBenefit)}</span>
            <span className="px-2 py-0.5 rounded-full" style={{background:"var(--ns-subtle)"}}>Aprendizaje (1º→últ. libre): {aprendizaje>=0?"+":""}{aprendizaje}</span>
          </div>
          <label className="flex items-center gap-2 cursor-pointer pt-1.5 mt-1 border-t" style={{borderColor:"var(--ns-card-b)"}}>
            <input type="checkbox" checked={scores.incluir_en_informe==="1"} onChange={e=>setS("incluir_en_informe",e.target.checked?"1":"0")} className="w-4 h-4 accent-teal-600"/>
            <span className="text-[11px] font-semibold" style={{color:"var(--ns-text)"}}>Incluir la curva de memoria en el informe</span>
          </label>
          <p className="text-[9px]" style={{color:"var(--ns-muted)"}}>Orientativo. La interpretación clínica final es del profesional; no se exporta al informe salvo que marque la casilla.</p>
        </div>;
      })()}
    </Card>;
  }
  if(cfg.type==="tmt"){
    return<Card className="p-5 space-y-3 ">
      <h3 className="font-bold text-sm flex items-center gap-2"><I name="timer" className="text-amber-600 text-lg"/>{cfg.label}</h3>
      <div className="grid grid-cols-2 gap-3">
        <div><Label>Tiempo (seg)</Label><input type="number" value={scores.tiempo||""} onChange={e=>setS("tiempo",e.target.value)} className="w-full h-10 text-center text-lg font-bold rounded-xl border-none focus:ring-2 focus:ring-amber-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="seg"/></div>
        <div><Label>Errores</Label><input type="number" value={scores.errores||""} onChange={e=>setS("errores",e.target.value)} className="w-full h-10 text-center text-lg font-bold rounded-xl border-none focus:ring-2 focus:ring-red-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="0"/></div>
      </div>
      <p className="text-[10px] text-gray-400">Máximo: {cfg.maxTime}s. PD = tiempo en segundos.</p>
    </Card>;
  }
  if(cfg.type==="stroop"){
    const c0=parseInt(scores.c0,10)||0;const c1=parseInt(scores.c1,10)||0;const c2=parseInt(scores.c2,10)||0;
    const interf=scores.interferencia||(c0>0&&c1>0&&c2>0?String(Math.round(c2-((c0*c1)/(c0+c1)))):"");
    const condColors=["#64748b","#0ea5e9","#e11d48"];
    return<Card className="p-5 space-y-3 ">
      <h3 className="font-bold text-sm flex items-center gap-2"><I name="palette" className="text-rose-600 text-lg"/>{cfg.label}</h3>
      <p className={`${txtSub}`} style={{color:"var(--ns-muted)"}}>Registre ítems completados por condición. Interferencia = Palabra-Color − (Palabra×Color)/(Palabra+Color).</p>
      <div className="space-y-2">{cfg.conditions.map((c,i)=>
        <div key={c} className="flex items-center gap-3 p-3 rounded-xl" style={{background:i===2?"rgba(225,29,72,0.08)":"var(--ns-subtle)",borderLeft:`4px solid ${condColors[i]}`}}>
          <span className={`${txtSub} font-bold w-32 shrink-0`} style={{color:condColors[i]}}>{c}</span>
          <input type="number" min={0} value={scores[`c${i}`]||""} onChange={e=>{setS(`c${i}`,e.target.value);const ns={...scores,[`c${i}`]:e.target.value};const a=parseInt(ns.c0,10)||0;const b=parseInt(ns.c1,10)||0;const d=parseInt(ns.c2,10)||0;if(a>0&&b>0&&d>0&&(a+b)>0){const iv=d-((a*b)/(a+b));setS("interferencia",String(Math.round(iv)))}}} className="w-20 h-11 text-center text-lg font-bold rounded-xl border-none" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="—"/>
          <span className={`${txtSub}`} style={{color:"var(--ns-muted)"}}>ítems</span>
        </div>
      )}</div>
      {interf!==""&&<div className="text-sm font-bold text-center p-3 rounded-xl" style={{background:"rgba(159,18,57,0.1)",color:"#9f1239"}}>Interferencia: {interf} · PD registrado en campo superior</div>}
    </Card>;
  }
  if(cfg.type==="caras"){
    return<Card className="p-5 space-y-3 ">
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
    return<Card className="p-5 space-y-3 ">
      <h3 className="font-bold text-sm flex items-center gap-2"><I name="speed" className="text-emerald-600 text-lg"/>{cfg.label}</h3>
      <p className="text-[10px] text-gray-400">{cfg.instruction}</p>
      <div><Label>Respuestas Correctas</Label><input type="number" value={scores.correctas||""} onChange={e=>setS("correctas",e.target.value)} className="w-full h-12 text-center text-xl font-bold rounded-xl border-none focus:ring-2 focus:ring-emerald-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="0"/></div>
    </Card>;
  }
  /* ── Letras y Números (ensayos_secuencias del protocolo) ── */
  if(cfg.type==="ln_sequences"){
    const maxTrials=cfg.maxTrials||3;
    return<Card className="p-5 space-y-3">
      {licenseBanner}
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm flex items-center gap-2"><I name="sort_by_alpha" className="text-indigo-600 text-lg"/>Reactivos — {cfg.label}</h3>
        <span className="text-xs font-bold px-2 py-1 rounded-full bg-indigo-100 text-indigo-700">PD: {puntajes[testId]||0}</span>
      </div>
      <p className="text-[10px]" style={{color:"var(--ns-muted)"}}>Dictar cada secuencia (campo <b>est</b>). Respuesta esperada: números ascendente + letras A-Z (<b>cor</b>). Hasta {maxTrials} intentos por ítem.</p>
      <div className="space-y-3 max-h-[32rem] overflow-y-auto pr-1">{items.map(it=>(
        <div key={it.n} className="rounded-xl border p-3" style={{borderColor:"var(--ns-card-b)"}}>
          <p className="text-xs font-bold mb-2" style={{color:TEAL}}>Ítem {it.n}</p>
          {(it.trials||[]).slice(0,maxTrials).map((tr,ti)=>(
            <div key={ti} className="flex flex-wrap items-center gap-2 mb-2 p-2 rounded-lg" style={{background:"var(--ns-subtle)"}}>
              <span className="text-[10px] font-mono font-bold w-16">Intento {ti+1}</span>
              <span className="text-xs font-mono" title="Secuencia a dictar">{tr.est}</span>
              <I name="arrow_forward" className="text-sm opacity-40"/>
              <span className="text-xs font-mono text-teal-700" title={pearsonOk?"Respuesta modelo":"Requiere licencia Pearson"}>{pearsonOk?tr.cor:"•••"}</span>
              <div className="ml-auto flex gap-1">{[0,1].map(v=><button key={v} type="button" onClick={()=>setS(`i${it.n}_t${ti}`,String(v))} className={`w-8 h-7 rounded text-xs font-bold ${parseInt(scores[`i${it.n}_t${ti}`]||"0",10)===v?"text-white":"text-gray-500"}`} style={parseInt(scores[`i${it.n}_t${ti}`]||"0",10)===v?{background:v?"#22c55e":"#ef4444"}:{}}>{v?"✓":"✗"}</button>)}</div>
            </div>
          ))}
        </div>
      ))}</div>
    </Card>;
  }
  /* ── Matrices / Conceptos — láminas integradas + captura de puntaje ── */
  if(cfg.type==="visual_cuadernillo"){
    const hasIntegrated=perTestStim.length>0;
    return<Card className="p-5 space-y-3">
      {licenseBanner}
      <div className="p-3 rounded-xl flex items-start gap-3" style={{background:"rgba(13,148,136,0.08)",border:"1px solid rgba(13,148,136,0.2)"}}>
        <I name={hasIntegrated?"image":"menu_book"} className="text-teal-600 text-xl shrink-0"/>
        <div>
          <p className="text-xs font-bold" style={{color:TEAL}}>{hasIntegrated?"Láminas integradas en NeuroSoft":"Material visual — protocolo licenciado"}</p>
          <p className="text-[10px] mt-1" style={{color:"var(--ns-muted)"}}>
            {cfg.manualRef||"Cuaderno de estímulos"}.
            {hasIntegrated
              ? " Toque la miniatura para ver la lámina en pantalla completa y marque 0/1 por ítem."
              : " Las láminas de esta subprueba se cargan desde Config → Estímulos o su kit Pearson/Manual Moderno."}
          </p>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm flex items-center gap-2"><I name="grid_view" className="text-purple-600 text-lg"/>Reactivos — {cfg.label}</h3>
        <span className="text-xs font-bold px-2 py-1 rounded-full bg-purple-100 text-purple-700">PD: {puntajes[testId]||0}</span>
      </div>
      <div className="space-y-1 max-h-72 overflow-y-auto pr-1">{items.map(it=>{
        const v=parseInt(scores[`i${it.n}`],10)||0;
        const itemStim=resolveItemStimulus(estimulos,testId,it.n);
        return<div key={it.n} className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-50 transition-all">
          <span className="text-xs font-mono font-bold text-gray-400 w-8">{it.lamina??it.n}</span>
          {itemStim?<ItemStimulus stimulus={itemStim} compact onExpand={()=>openOverlay(it.n)}/>:null}
          <p className="flex-1 text-xs truncate" style={{color:"var(--ns-muted)"}}>
            Lámina {it.lamina??it.n}{cfg.opciones?` · ${cfg.opciones} opciones`:" · agrupar por categoría"}
            {pearsonOk&&it.clave!=null&&<span className="ml-2 font-mono text-[10px] text-amber-700">clave {it.clave}</span>}
          </p>
          <div className="flex gap-1">{[0,1].map(s=><button key={s} type="button" onClick={()=>setS(`i${it.n}`,String(s))} className={`w-9 h-8 rounded-lg text-xs font-bold ${v===s?"text-white shadow":""}`} style={v===s?{background:s?TEAL:"#ef4444"}:{color:"var(--ns-muted)"}}>{s}</button>)}</div>
        </div>})}</div>
      {overlayItem&&<PresentationOverlay open stimulus={overlayItem.stimulus} label={`${cfg.label} — lámina ${overlayItem.itemN}`} onClose={()=>setOverlayItem(null)} hasPrev={overlayIdx>0} hasNext={overlayIdx>=0&&overlayIdx<itemList.length-1} onPrev={()=>{const prev=itemList[overlayIdx-1];if(prev)openOverlay(prev.n)}} onNext={()=>{const next=itemList[overlayIdx+1];if(next)openOverlay(next.n)}}/>}
    </Card>;
  }
  /* ── Palabras en contexto (pistas progresivas) ── */
  if(cfg.type==="verbal_pistas"){
    return<Card className="p-5 space-y-3">
      {licenseBanner}
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm flex items-center gap-2"><I name="tips_and_updates" className="text-purple-600 text-lg"/>Reactivos — {cfg.label}</h3>
        <span className="text-xs font-bold px-2 py-1 rounded-full bg-purple-100 text-purple-700">PD: {puntajes[testId]||0}</span>
      </div>
      <div className="space-y-2 max-h-72 overflow-y-auto pr-1">{items.map(it=>{
        const v=parseInt(scores[`i${it.n}`],10)||0;
        return<div key={it.n} className="p-2 rounded-lg border" style={{borderColor:"var(--ns-card-b)"}}>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-gray-400 w-6">{it.n}</span>
            <div className="flex-1 min-w-0">
              {(it.pistas||[]).map((p,pi)=><p key={pi} className="text-[11px] leading-snug" style={{color:"var(--ns-text)"}}>Pista {pi+1}: {p}</p>)}
              {pearsonOk&&it.respuesta&&<p className="text-[10px] mt-1 font-bold text-amber-700">Modelo: {it.respuesta}</p>}
            </div>
            <div className="flex gap-1">{[0,1].map(s=><button key={s} type="button" onClick={()=>setS(`i${it.n}`,String(s))} className={`w-9 h-8 rounded-lg text-xs font-bold ${v===s?"text-white":""}`} style={v===s?{background:s?TEAL:"#ef4444"}:{color:"var(--ns-muted)"}}>{s}</button>)}</div>
          </div>
        </div>})}</div>
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
    return<SectionCard title={cfg.label} icon="checklist" eyebrow="Validez de síntomas" headerRight={
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold px-2 py-1 rounded-full ${low?"bg-red-100 text-red-700":"bg-green-100 text-green-700"}`}>{recalled}/{cfg.items.length} recordados</span>
          {low&&<span className="text-[10px] font-bold text-red-600 flex items-center gap-1"><I name="warning" className="text-sm"/>Corte ≤{cutoff}</span>}
        </div>
      }>
      {licenseBanner}
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
      {(low||combined)&&<div className={`p-3 rounded-xl text-xs leading-relaxed ${combined?"border-red-500":""}`} style={{background:combined?"rgba(239,68,68,0.08)":"rgba(251,191,36,0.1)",color:combined?"#991b1b":"#92400e"}}>
        <p className="font-bold mb-1">{combined?"Alta sospecha de bajo esfuerzo / simulación":"Screening positivo — bajo esfuerzo posible"}</p>
        <p>{combined?"Evocación ≤9 Y reconocimiento ≤20: alta especificidad para simulación (Boone et al. 2002). Complementar con TOMM o VSVT.":"Evocación ≤"+cutoff+" (corte Rey 1964). Por sí solo tiene baja especificidad; combinar con contexto clínico y otras pruebas de validez."}</p>
      </div>}
    </SectionCard>;
  }
  return null;
};

export default ReactivePanel;
