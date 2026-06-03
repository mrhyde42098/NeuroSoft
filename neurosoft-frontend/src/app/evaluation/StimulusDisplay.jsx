/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/StimulusDisplay.jsx — Mostrador de estímulos por test
 * Renderiza estímulos cargados (imagen/lista/audio) o, si no hay, el SVG nativo.
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";
import { I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { NativeStimuli } from "../../data/stimuli.jsx";
import { esVerbatim, estadoProteccion, registrarAccesoItem } from "../../data/pearsonProtected.js";
import { SelloProtegidoBadge } from "../../ui/SelloProtegidoBadge.jsx";
import ApoyoClinicoPanel from "../../ui/ApoyoClinicoPanel.jsx";
import { useEffect, useRef } from "react";

/* ═══ SVG originales para pruebas visuales comunes ═══
 * Dibujos propios creados para NeuroSoft. NO son reproducciones de los
 * reactivos editoriales; son ayudas visuales para ubicar al evaluador.
 */

export default function StimulusDisplay({testId,stimuli,itemIndex=null}){
  const custom=stimuli||[];
  const Native=NativeStimuli[testId];
  const accessLoggedRef=useRef(false);
  const verbatim=esVerbatim(testId);
  const prot=estadoProteccion(testId);

  /* §S5.1x: log de acceso (dedupe intra-render) */
  useEffect(()=>{
    if(!verbatim||!prot.aceptado)return;
    if(accessLoggedRef.current)return;
    accessLoggedRef.current=true;
    registrarAccesoItem(testId,itemIndex).catch(()=>{/* best effort */});
  },[verbatim,prot.aceptado,testId,itemIndex]);

  if(custom.length===0&&!Native)return null;
  return<div className="w-full max-w-xl mx-auto mb-3">
    <div className="rounded-xl p-3 relative" style={{background:"var(--ns-subtle)",border:"1px solid var(--ns-card-b)"}}>
      {verbatim&&prot.aceptado&&<SelloProtegidoBadge testId={testId} mode="corner"/>}
      <p className="text-[10px] font-extrabold uppercase tracking-wider mb-2" style={{color:"var(--ns-muted)"}}>
        <I name="image" className="text-[10px] mr-1"/>
        {custom.length>0?`Estímulos (${custom.length})`:"Referencia visual"}
      </p>
      {custom.length>0?<div className="flex gap-2 overflow-x-auto pb-1">{custom.map(s=><div key={s.id} className="shrink-0">
        {s.tipo==="imagen"&&s.contenido_base64?<img src={s.contenido_base64} alt={s.nombre} className="h-40 rounded-lg border bg-white"/>
        :<div className="h-40 w-40 flex flex-col items-center justify-center rounded-lg border bg-white p-2"><I name={s.tipo==="lista_palabras"?"format_list_numbered":s.tipo==="audio"?"volume_up":"description"} className="text-3xl" style={{color:TEAL}}/><p className="text-[10px] font-bold mt-1 text-center">{s.nombre}</p></div>}
        <p className="text-[9px] text-center mt-1 truncate w-40" style={{color:"var(--ns-muted)"}}>{s.nombre}</p>
      </div>)}</div>
      :Native?<div className="h-48 flex items-center justify-center bg-white rounded-lg border"><Native/></div>:null}
      {verbatim&&<div className="mt-2"><ApoyoClinicoPanel testId={testId} variant="compact"/></div>}
    </div>
  </div>;
}
