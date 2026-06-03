/* ═══════════════════════════════════════════════════════════════════════
 * src/app/patients/ConsentModal.jsx — Modal de consentimientos informados
 * Carga pendientes (Habeas Data, Evaluación, Tratamiento, Telepsicología),
 * permite firmar con SignatureCanvas y registra la versión del texto + IP.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { Btn, I, Input, Label, Sel } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { CONSENT_LABELS } from "../../data/ui.js";
import SignatureCanvas from "../evaluation/SignatureCanvas.jsx";

export default function ConsentModal({patientId,patientName,onClose,onAllSigned}){
  const[pendientes,setPendientes]=useState([]);const[ld,setLd]=useState(true);
  const[firmados,setFirmados]=useState([]);const[currentIdx,setCurrentIdx]=useState(0);
  const[textoActual,setTextoActual]=useState(null);const[firma,setFirma]=useState("");
  const[nombreFirmante,setNombreFirmante]=useState("");const[relacion,setRelacion]=useState("titular");
  const[docFirmante,setDocFirmante]=useState("");const[aceptado,setAceptado]=useState(false);
  const[saving,setSaving]=useState(false);const toast=useToast();
  const load=async()=>{setLd(true);try{
    const[p,f]=await Promise.all([
      api.get(`/api/v1/consentimientos/pendientes/${patientId}`).catch(()=>[]),
      api.get(`/api/v1/consentimientos/?patient_id=${patientId}`).catch(()=>[]),
    ]);
    setPendientes(p||[]);setFirmados(f||[]);
    if(p&&p.length>0){const t=await api.get(`/api/v1/consentimientos/textos/${p[0]}`).catch(()=>null);setTextoActual(t)}
  }catch(e){toast.error(_parseError(e))}setLd(false)};
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(()=>{load()},[patientId]);
  const cargarTipo=async(tipo)=>{const t=await api.get(`/api/v1/consentimientos/textos/${tipo}`).catch(()=>null);setTextoActual(t);setFirma("");setNombreFirmante("");setDocFirmante("");setAceptado(false);setRelacion("titular")};
  const firmar=async()=>{if(!firma||!nombreFirmante||!docFirmante||!aceptado){toast.error("Complete nombre, documento, firma y marque la casilla");return}setSaving(true);try{
    await api.post("/api/v1/consentimientos/",{patient_id:patientId,tipo:pendientes[currentIdx],version_texto:textoActual.version,texto_completo:textoActual.texto,aceptado:true,firma_base64:firma,nombre_firmante:nombreFirmante,relacion_firmante:relacion,documento_firmante:docFirmante});
    toast.success("Consentimiento firmado");
    const nuevosPend=pendientes.filter((_,i)=>i!==currentIdx);
    setPendientes(nuevosPend);
    if(nuevosPend.length===0){onAllSigned&&onAllSigned();onClose()}
    else{setCurrentIdx(0);await cargarTipo(nuevosPend[0])}
  }catch(e){toast.error(_parseError(e))}setSaving(false)};
  const revocar=async(id)=>{const motivo=prompt("Motivo de la revocación:");if(!motivo)return;try{await api.patch(`/api/v1/consentimientos/${id}/revocar`,{motivo});toast.success("Consentimiento revocado");load()}catch(e){toast.error(_parseError(e))}};
  return<div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
    <div className="rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col" onClick={e=>e.stopPropagation()} style={{background:"var(--ns-card)"}}>
      <div className="p-5 border-b flex items-center justify-between" style={{borderColor:"var(--ns-card-b)"}}>
        <div>
          <h3 className="text-lg font-bold flex items-center gap-2"><I name="verified_user" style={{color:TEAL}}/>Consentimientos informados</h3>
          <p className="text-xs" style={{color:"var(--ns-muted)"}}>Paciente: <b>{patientName}</b></p>
        </div>
        <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100" aria-label="Cerrar modal de consentimientos" title="Cerrar"><I name="close"/></button>
      </div>
      <div className="flex-1 overflow-auto p-6">{ld?<div className="flex justify-center py-12"><div className="animate-spin w-8 h-8 border-4 border-teal-200 border-t-teal-600 rounded-full"/></div>
      :<div className="space-y-6">
        {/* Pendientes */}
        {pendientes.length>0&&textoActual&&<div className="p-5 rounded-xl border-2" style={{borderColor:TEAL,background:TEAL+"08"}}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-[10px] font-bold uppercase" style={{color:TEAL}}>{pendientes.length} pendiente{pendientes.length===1?"":"s"}</p>
              <h4 className="font-bold">{CONSENT_LABELS[pendientes[currentIdx]]?.titulo||pendientes[currentIdx]}</h4>
              <p className="text-xs" style={{color:"var(--ns-muted)"}}>{CONSENT_LABELS[pendientes[currentIdx]]?.desc}</p>
            </div>
            {pendientes.length>1&&<div className="flex gap-1">{pendientes.map((t,i)=><button key={t} onClick={()=>{setCurrentIdx(i);cargarTipo(t)}} className={`text-[10px] px-2 py-1 rounded ${i===currentIdx?"font-bold":""}`} style={i===currentIdx?{background:TEAL,color:"white"}:{background:"var(--ns-subtle)"}}>{i+1}</button>)}</div>}
          </div>
          <div className="p-4 rounded-lg max-h-64 overflow-auto text-xs leading-relaxed whitespace-pre-wrap" style={{background:"var(--ns-card)",border:"1px solid var(--ns-card-b)"}}>{textoActual.texto}</div>
          <p className="text-[10px] mt-2" style={{color:"var(--ns-muted)"}}>Versión {textoActual.version}</p>

          <div className="grid grid-cols-2 gap-3 mt-4">
            <div><Label className="text-xs">Nombre del firmante *</Label><Input value={nombreFirmante} onChange={e=>setNombreFirmante(e.target.value)} placeholder="Nombre completo de quien firma"/></div>
            <div><Label className="text-xs">Documento *</Label><Input value={docFirmante} onChange={e=>setDocFirmante(e.target.value)} placeholder="CC / TI / CE"/></div>
            <div><Label className="text-xs">Relación con el paciente</Label>
              <Sel value={relacion} onChange={e=>setRelacion(e.target.value)}><option value="titular">Titular (paciente mayor de edad)</option><option value="padre">Padre</option><option value="madre">Madre</option><option value="tutor_legal">Tutor legal</option><option value="representante">Representante legal</option><option value="otro">Otro familiar</option></Sel>
            </div>
            <div></div>
            <div className="col-span-2">
              <Label className="text-xs">Firma manuscrita *</Label>
              <SignatureCanvas value={firma} onChange={setFirma}/>
            </div>
            <label className="col-span-2 flex items-start gap-2 cursor-pointer"><input type="checkbox" checked={aceptado} onChange={e=>setAceptado(e.target.checked)} className="w-4 h-4 mt-0.5"/><span className="text-xs">He leído y entiendo el contenido de este consentimiento. Acepto voluntariamente lo aquí descrito y autorizo el tratamiento de los datos según la Ley 1581 de 2012.</span></label>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Btn v="outline" onClick={onClose}>Más tarde</Btn>
            <Btn onClick={firmar} disabled={saving||!firma||!nombreFirmante||!docFirmante||!aceptado}><I name="draw" className="text-sm"/>{saving?"Guardando...":"Firmar consentimiento"}</Btn>
          </div>
        </div>}

        {/* Firmados */}
        <div>
          <p className="text-sm font-bold mb-3 flex items-center gap-2"><I name="task_alt" style={{color:"#059669"}}/>Consentimientos firmados ({firmados.filter(f=>!f.fecha_revocado).length})</p>
          {firmados.length===0?<p className="text-xs text-center py-6" style={{color:"var(--ns-muted)"}}>Sin consentimientos previos</p>
          :<div className="space-y-2">{firmados.map(f=>{const revocado=!!f.fecha_revocado;return<div key={f.id} className="p-3 rounded-lg border flex items-center justify-between" style={{borderColor:"var(--ns-card-b)",background:revocado?"#fef2f2":"var(--ns-subtle)",opacity:revocado?0.6:1}}>
            <div className="flex-1">
              <p className="text-xs font-bold">{CONSENT_LABELS[f.tipo]?.titulo||f.tipo} <span className="font-normal text-[10px]" style={{color:"var(--ns-muted)"}}>v{f.version_texto}</span></p>
              <p className="text-[10px]" style={{color:"var(--ns-muted)"}}>{f.nombre_firmante} ({f.relacion_firmante}) · {f.documento_firmante}</p>
              <p className="text-[10px]" style={{color:"var(--ns-muted)"}}>Firmado: {f.fecha_firma?new Date(f.fecha_firma).toLocaleDateString("es-CO"):"—"}{f.ip_registro?" · IP "+f.ip_registro:""}</p>
              {revocado&&<p className="text-[10px] text-red-600 font-bold mt-1">REVOCADO el {new Date(f.fecha_revocado).toLocaleDateString("es-CO")}{f.motivo_revocado?" — "+f.motivo_revocado:""}</p>}
            </div>
            {!revocado&&<button onClick={()=>revocar(f.id)} className="text-xs p-1.5 rounded hover:bg-red-50 text-gray-400 hover:text-red-600" title="Revocar" aria-label="Revocar este consentimiento"><I name="block" className="text-base"/></button>}
          </div>})}</div>}
        </div>
      </div>}</div>
    </div>
  </div>;
}
