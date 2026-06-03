/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/AuditoriaTab.jsx — Registro de auditoria (Res. 1995/99)
 * Filtrado por accion/entidad/dias + detalle por entidad.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { Card, I, Label, Sel } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* ══════════════ AuditoriaTab — registro de auditoría Res. 1995 ══════════════ */
export default function AuditoriaTab(){
  const[events,setEvents]=useState([]);const[summary,setSummary]=useState(null);const[ld,setLd]=useState(true);
  const[fAction,setFAction]=useState("");const[fEntity,setFEntity]=useState("");const[fDias,setFDias]=useState(30);
  const[selected,setSelected]=useState(null);const[entityEvents,setEntityEvents]=useState([]);const[loadingEntity,setLoadingEntity]=useState(false);
  const toast=useToast();
  const load=async()=>{setLd(true);try{
    const q=[];if(fAction)q.push("action="+encodeURIComponent(fAction));if(fEntity)q.push("entity_type="+encodeURIComponent(fEntity));q.push("limit=200");
    const[s,ev]=await Promise.all([
      api.get(`/api/v1/audit/summary?dias=${fDias}`).catch(()=>null),
      api.get("/api/v1/audit/?"+q.join("&")).catch(()=>[]),
    ]);
    setSummary(s);setEvents(ev||[]);
  }catch(e){toast.error(_parseError(e))}setLd(false)};
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(()=>{load()},[fAction,fEntity,fDias]);
  const verEntidad=async(ev)=>{setSelected(ev);setLoadingEntity(true);try{const d=await api.get(`/api/v1/audit/entity/${ev.entity_type}/${ev.entity_id}`);setEntityEvents(d||[])}catch{setEntityEvents([])}setLoadingEntity(false)};
  const fmtDate=s=>{if(!s)return"—";try{return new Date(s).toLocaleString("es-CO",{dateStyle:"short",timeStyle:"medium"})}catch{return s}};
  const ACCIONES=["","create","update","delete","login","login_failed","password_change","password_change_failed","backup","restore","consent_sign","consent_revoke"];
  const ENTIDADES=["","patient","clinical_history","evaluation","evolucion","consentimiento","inconcluso","auth","backup"];
  const actionColor=(a)=>({create:"#059669",update:"#0891b2",delete:"#dc2626",login:"#6366f1",login_failed:"#b91c1c",backup:"#7c3aed",restore:"#d97706"}[a]||"#6b7280");
  return<Card className="p-8 space-y-6">
    <div>
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="policy" style={{color:TEAL}}/>Registro de Auditoría</h3>
      <p className="text-xs mt-1" style={{color:"var(--ns-muted)"}}>Trazabilidad completa de acciones sobre historias clínicas y datos sensibles. Cumplimiento de la Resolución 1995 de 1999 del Ministerio de Salud.</p>
    </div>

    {/* Resumen */}
    {summary&&<div className="grid grid-cols-4 gap-3">
      <div className="p-4 rounded-xl" style={{background:"var(--ns-subtle)"}}>
        <p className="text-[10px] font-bold uppercase" style={{color:"var(--ns-muted)"}}>Total ({fDias}d)</p>
        <p className="text-2xl font-bold mt-1">{summary.total||0}</p>
      </div>
      <div className="p-4 rounded-xl" style={{background:"var(--ns-subtle)"}}>
        <p className="text-[10px] font-bold uppercase" style={{color:"var(--ns-muted)"}}>Creaciones</p>
        <p className="text-2xl font-bold mt-1" style={{color:"#059669"}}>{summary.por_accion?.create||0}</p>
      </div>
      <div className="p-4 rounded-xl" style={{background:"var(--ns-subtle)"}}>
        <p className="text-[10px] font-bold uppercase" style={{color:"var(--ns-muted)"}}>Modificaciones</p>
        <p className="text-2xl font-bold mt-1" style={{color:"#0891b2"}}>{summary.por_accion?.update||0}</p>
      </div>
      <div className="p-4 rounded-xl" style={{background:"var(--ns-subtle)"}}>
        <p className="text-[10px] font-bold uppercase" style={{color:"var(--ns-muted)"}}>Logins</p>
        <p className="text-2xl font-bold mt-1" style={{color:"#6366f1"}}>{(summary.por_accion?.login||0)+(summary.por_accion?.login_failed||0)}</p>
      </div>
    </div>}

    {/* Filtros */}
    <div className="p-4 rounded-xl grid grid-cols-3 gap-3" style={{background:"var(--ns-subtle)"}}>
      <div><Label className="text-xs">Acción</Label>
        <Sel value={fAction} onChange={e=>setFAction(e.target.value)}>{ACCIONES.map(a=><option key={a} value={a}>{a||"— Todas —"}</option>)}</Sel>
      </div>
      <div><Label className="text-xs">Entidad</Label>
        <Sel value={fEntity} onChange={e=>setFEntity(e.target.value)}>{ENTIDADES.map(a=><option key={a} value={a}>{a||"— Todas —"}</option>)}</Sel>
      </div>
      <div><Label className="text-xs">Periodo resumen (días)</Label>
        <Sel value={fDias} onChange={e=>setFDias(parseInt(e.target.value,10))}><option value={7}>7 días</option><option value={30}>30 días</option><option value={90}>90 días</option><option value={365}>1 año</option></Sel>
      </div>
    </div>

    {/* Tabla eventos */}
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-bold">Eventos ({events.length})</p>
        <button onClick={load} className="text-xs flex items-center gap-1 hover:underline" style={{color:TEAL}}><I name="refresh" className="text-sm"/>Refrescar</button>
      </div>
      {ld?<div className="flex justify-center py-8"><div className="animate-spin w-6 h-6 border-4 border-teal-200 border-t-teal-600 rounded-full"/></div>
      :events.length===0?<div className="text-center py-8" style={{color:"var(--ns-muted)"}}><I name="inventory" className="text-4xl opacity-30 mb-2"/><p className="text-sm font-bold">Sin eventos en este filtro</p></div>
      :<Card className="overflow-hidden"><table className="w-full text-sm"><thead style={{background:"var(--ns-subtle)"}}><tr>
        <th className="px-3 py-3 text-left font-bold text-xs">Fecha</th>
        <th className="px-3 py-3 text-left font-bold text-xs">Actor</th>
        <th className="px-3 py-3 text-left font-bold text-xs">Acción</th>
        <th className="px-3 py-3 text-left font-bold text-xs">Entidad</th>
        <th className="px-3 py-3 text-left font-bold text-xs">Resumen</th>
        <th className="px-3 py-3 text-left font-bold text-xs">IP</th>
        <th className="px-3 py-3 w-16"></th>
      </tr></thead>
        <tbody>{events.map((e,i)=><tr key={e.id||i} className="border-b hover:bg-gray-50" style={{borderColor:"var(--ns-card-b)"}}>
          <td className="px-3 py-2 text-[11px] font-mono" style={{color:"var(--ns-muted)"}}>{fmtDate(e.ts)}</td>
          <td className="px-3 py-2 text-xs">{e.actor_label||e.actor_id?.slice(0,8)||"—"}</td>
          <td className="px-3 py-2"><span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded" style={{background:actionColor(e.action)+"20",color:actionColor(e.action)}}>{e.action}</span></td>
          <td className="px-3 py-2 text-xs font-mono" style={{color:"var(--ns-muted)"}}>{e.entity_type}{e.entity_id?` #${e.entity_id.slice(0,8)}`:""}</td>
          <td className="px-3 py-2 text-xs max-w-xs truncate" title={e.summary}>{e.summary||"—"}</td>
          <td className="px-3 py-2 text-[10px] font-mono" style={{color:"var(--ns-muted)"}}>{e.ip||"—"}</td>
          <td className="px-3 py-2">{e.entity_id&&<button onClick={()=>verEntidad(e)} className="text-xs p-1 rounded hover:bg-teal-50" title="Ver historial" aria-label="Ver historial de auditoría de esta entidad" style={{color:TEAL}}><I name="timeline" className="text-base"/></button>}</td>
        </tr>)}</tbody></table></Card>}
    </div>

    {/* Modal historial de entidad */}
    {selected&&<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={()=>setSelected(null)}>
      <div className="bg-white dark:bg-gray-900 rounded-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col" onClick={e=>e.stopPropagation()} style={{background:"var(--ns-card)"}}>
        <div className="p-5 border-b flex items-center justify-between" style={{borderColor:"var(--ns-card-b)"}}>
          <div>
            <h3 className="text-base font-bold">Historial de <code className="text-xs">{selected.entity_type}</code></h3>
            <p className="text-xs font-mono" style={{color:"var(--ns-muted)"}}>{selected.entity_id}</p>
          </div>
          <button onClick={()=>setSelected(null)} className="p-2 rounded-lg hover:bg-gray-100" aria-label="Cerrar modal" title="Cerrar"><I name="close"/></button>
        </div>
        <div className="flex-1 overflow-auto p-5">{loadingEntity?<div className="flex justify-center py-8"><div className="animate-spin w-6 h-6 border-4 border-teal-200 border-t-teal-600 rounded-full"/></div>
        :entityEvents.length===0?<p className="text-center text-sm py-8" style={{color:"var(--ns-muted)"}}>Sin eventos previos</p>
        :<div className="space-y-3">{entityEvents.map((e,i)=><div key={i} className="p-3 rounded-xl border" style={{borderColor:"var(--ns-card-b)",background:"var(--ns-subtle)"}}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded" style={{background:actionColor(e.action)+"20",color:actionColor(e.action)}}>{e.action}</span>
            <span className="text-[10px] font-mono" style={{color:"var(--ns-muted)"}}>{fmtDate(e.ts)}</span>
          </div>
          <p className="text-xs"><b>{e.actor_label||"—"}</b>{e.ip?` · ${e.ip}`:""}</p>
          {e.summary&&<p className="text-xs mt-1" style={{color:"var(--ns-muted)"}}>{e.summary}</p>}
          {e.changes&&<details className="mt-2"><summary className="text-[10px] cursor-pointer" style={{color:TEAL}}>Ver cambios</summary><pre className="text-[10px] mt-1 p-2 rounded overflow-auto" style={{background:"var(--ns-card)",color:"var(--ns-text)",maxHeight:"200px"}}>{typeof e.changes==="string"?e.changes:JSON.stringify(e.changes,null,2)}</pre></details>}
        </div>)}</div>}</div>
      </div>
    </div>}
  </Card>
}
