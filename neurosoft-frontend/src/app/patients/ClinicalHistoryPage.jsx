/* ═══════════════════════════════════════════════════════════════════════
 * src/app/patients/ClinicalHistoryPage.jsx — Historia clínica neuropsicológica
 * Formulario en 4 pasos: Desarrollo, Antecedentes, Familiar/Social, Plan.
 * Integra el modal de consentimientos por paciente.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import {
  Btn, Card, I, Input, Label, MsgBanner, Sel, TopBar, Txta,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import ConsentModal from "./ConsentModal.jsx";
import CompanionsSection from "./CompanionsSection.jsx"; // §M-7
import { CIE_POR_POBLACION } from "../../data/datosClinicos.js";
import { useToast } from "../../contexts.jsx";
import { safeLS } from "../../utils/safeLS.js";
import SectionCard from "../../ui/SectionCard.jsx";

/* ══════════════ CLINICAL HISTORY ══════════════ */

/* Codifica los 3 sub-campos del MC en un único string con marcadores
 * (compatibilidad backend que sólo guarda `motivo_consulta` plano).
 * Formato:
 *    [Remitente] ...texto...\n
 *    [Subjetivo] ...texto...\n
 *    [Enfermedad actual] ...texto...
 * Si todos están vacíos, devuelve "" (no genera marcadores). */
function encodeMC({rem, sub, act}) {
  const parts = [];
  if (rem && rem.trim()) parts.push(`[Remitente] ${rem.trim()}`);
  if (sub && sub.trim()) parts.push(`[Subjetivo] ${sub.trim()}`);
  if (act && act.trim()) parts.push(`[Enfermedad actual] ${act.trim()}`);
  return parts.join("\n\n");
}

/* Decodifica el `motivo_consulta` plano. Si tiene marcadores, separa en
 * los 3 sub-campos. Si no (HC antigua), todo el texto va a `rem` para
 * que el clínico lo redistribuya manualmente. */
function decodeMC(raw) {
  const out = {rem: "", sub: "", act: ""};
  if (!raw) return out;
  const hasMarkers = /\[Remitente\]|\[Subjetivo\]|\[Enfermedad actual\]/.test(raw);
  if (!hasMarkers) { out.rem = raw; return out; }
  const re = /\[(Remitente|Subjetivo|Enfermedad actual)\]\s*([\s\S]*?)(?=\[(?:Remitente|Subjetivo|Enfermedad actual)\]|$)/g;
  let m;
  while ((m = re.exec(raw)) !== null) {
    const txt = (m[2] || "").trim();
    if (m[1] === "Remitente") out.rem = txt;
    else if (m[1] === "Subjetivo") out.sub = txt;
    else if (m[1] === "Enfermedad actual") out.act = txt;
  }
  return out;
}

/* §1.4 Marcador de completitud por sección */
function completitudsHC(f) {
  const checks = {
    "Desarrollo": [f.mc_remitente||f.mc_subjetivo, f.tipo_parto, f.sosten_cefalico||f.marcha].filter(Boolean).length,
    "Antecedentes": [f.patologicos_medicos, f.farmacologicos, f.familiares].filter(v=>v&&v!=="N/A"&&v!=="").length,
    "Fam/Social": [f.vive_con, f.abc, f.cognitivo].filter(v=>v&&v!=="N/A"&&v!=="").length,
    "Plan": [f.plan_atencion, f.impresion_diagnostica_hc||f.hipotesis_pre_eval].filter(v=>v&&v!=="N/A"&&v!=="").length,
  };
  const total = Object.keys(checks).length;
  const done = Object.values(checks).filter(v=>v>0).length;
  return {checks, done, total};
}

export default function ClinicalHistoryPage({setPage}){
  const toast = useToast();
  const[patId,setPatId]=useState(()=>safeLS.get("ns_sel_patient")||"");const[loading,setLoading]=useState(false);
  const[patients,setPatients]=useState([]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(()=>{api.get("/api/v1/patients/panel").then(d=>setPatients(d.pacientes||d||[])).catch(()=>toast.error("Error cargando pacientes"));return()=>localStorage.removeItem("ns_sel_patient")},[]);
  const[tab,setTab]=useState(0);const tabs=["Desarrollo","Antecedentes","Familiar / Social","Plan de Atención"];
  const dflt={patient_id:"",numero_documento:"",fecha_atencion:new Date().toISOString().split("T")[0],codigo_cie10:"F809",codigo_cie11:"",row_version:null,motivo_consulta:"",mc_remitente:"",mc_subjetivo:"",enfermedad_actual:"",/* §1.1 acompañante */acompanante_nombre:"",acompanante_relacion:"",acompanante_telefono:"",/* §1.2 hipótesis */hipotesis_pre_eval:"",edad_materna:"",no_gestacion:"",riesgos:"No",cual_riesgo:"",estres_prenatal:"No",tipo_estres_prenatal:"",gestacion:"A Término",semanas:"",tipo_parto:"Natural",peso_gr:"",talla_cm:"",condiciones_neonatales:"",incubadora:"No",ucin:"No",sosten_cefalico:"",sedestacion:"",gateo:"",marcha:"",balbuceo:"",primeras_palabras:"",habla_claro:"",control_anual:"",control_vesical:"",patologicos_medicos:"",sensoriales_motores:"",psiquiatricos:"",farmacologicos:"",traumaticos:"",quirurgicos:"",toxicos:"",alergicos:"",terapeuticos:"",paraclinicos:"",familiares:"",vive_con:"",abc:"",escolar_laboral:"",cognitivo:"",comportamiento_animo:"",patron_sueno:"",patron_alimentacion:"",plan_atencion:"",impresion_diagnostica_hc:""};
  const[f,sF]=useState({...dflt});const set=(k,val)=>sF(o=>({...o,[k]:val}));
  const[msg,setMsg]=useState("");const[saving,setSaving]=useState(false);
  const[cie,setCie]=useState([]);const[cieQ,setCieQ]=useState("");const[cieOpen,setCieOpen]=useState(false);
  const[cie11Label,setCie11Label]=useState("");
  useEffect(()=>{
    const c10=(f.codigo_cie10||"").trim();
    if(!c10||c10.length<3){setCie11Label("");set("codigo_cie11","");return}
    api.get(`/api/v1/cie11/map?codigo10=${encodeURIComponent(c10)}`)
      .then((m)=>{set("codigo_cie11",m.cie11||"");setCie11Label(m.nombre11?`${m.cie11} — ${m.nombre11}`:m.cie11||"")})
      .catch(()=>{setCie11Label("");set("codigo_cie11","")});
  },[f.codigo_cie10]);
  const[showConsent,setShowConsent]=useState(false);const[pendCount,setPendCount]=useState(0);
  const checkConsents=async(pid)=>{if(!pid){setPendCount(0);return}try{const p=await api.get(`/api/v1/consentimientos/pendientes/${pid}`);const pend=Array.isArray(p)?p:(p?.pendientes||[]);setPendCount(pend.length);if(pend.length>0)setShowConsent(true)}catch{setPendCount(0)}};
  const loadHC=async(pid)=>{if(!pid)return;setLoading(true);try{const[d,patData]=await Promise.all([api.get(`/api/v1/clinical-history/${pid}`).catch(()=>null),api.get(`/api/v1/patients/panel`).then(r=>(r.pacientes||r||[]).find(p=>p.id===pid)).catch(()=>null)]);if(d){const merged={...dflt};Object.keys(d).forEach(k=>{if(k in merged&&d[k]!==null)merged[k]=d[k]});const dec=decodeMC(merged.motivo_consulta||"");merged.mc_remitente=dec.rem;merged.mc_subjetivo=dec.sub;merged.enfermedad_actual=dec.act;if(patData){merged.acompanante_nombre=patData.acompanante||"";merged.acompanante_relacion=patData.acompanante_relacion||"";merged.acompanante_telefono=patData.acompanante_telefono||""}sF(merged)}}catch{}setLoading(false);checkConsents(pid)};
  const searchCie=async(q)=>{
    setCieQ(q);
    if(q.length<2){setCie([]);return}
    /* Filtro local inmediato por población del paciente */
    const pat=patients.find(p=>p.id===f.patient_id);
    const ageYrs=pat?.age_display?parseInt(pat.age_display,10):null;
    const pob=ageYrs===null?null:ageYrs<18?"infantil":ageYrs<50?"adulto_joven":"adulto_mayor";
    const sugs=pob?(CIE_POR_POBLACION[pob]||[]):[];
    const q2=q.toLowerCase();
    const local=sugs.filter(c=>c.codigo.toLowerCase().includes(q2)||c.nombre.toLowerCase().includes(q2));
    if(local.length>0)setCie(local);
    /* Complementar con API si existe */
    try{const d=await api.get(`/api/v1/cie10/?buscar=${q}`);if(d?.length)setCie(d.map(c=>({...c,nombre:c.descripcion||c.nombre})))}catch{toast.error("Error buscando CIE-10")}
    if(!local.length)setCie([]);
  };
  const saveHC=async()=>{if(!f.patient_id){setMsg("Seleccione un paciente primero");return}setSaving(true);setMsg("");try{const mcEncoded=encodeMC({rem:f.mc_remitente,sub:f.mc_subjetivo,act:f.enfermedad_actual})||f.motivo_consulta||"N/A";const body={patient_id:f.patient_id,fecha_atencion:f.fecha_atencion,codigo_cie10:f.codigo_cie10,codigo_cie11:f.codigo_cie11||null,row_version:f.row_version||null,desarrollo:{motivo_consulta:mcEncoded,edad_materna:f.edad_materna||"N/A",no_gestacion:f.no_gestacion||"N/A",riesgos:f.riesgos||"N/A",cual_riesgo:f.cual_riesgo||"N/A",estres_prenatal:f.estres_prenatal||"N/A",tipo_estres_prenatal:f.tipo_estres_prenatal||"N/A",gestacion:f.gestacion||"N/A",semanas:f.semanas||"N/A",tipo_parto:f.tipo_parto||"N/A",peso_gr:f.peso_gr||"N/A",talla_cm:f.talla_cm||"N/A",condiciones_neonatales:f.condiciones_neonatales||"N/A",incubadora:f.incubadora||"N/A",ucin:f.ucin||"N/A",sosten_cefalico:f.sosten_cefalico||"N/A",sedestacion:f.sedestacion||"N/A",gateo:f.gateo||"N/A",marcha:f.marcha||"N/A",balbuceo:f.balbuceo||"N/A",primeras_palabras:f.primeras_palabras||"N/A",habla_claro:f.habla_claro||"N/A",control_anual:f.control_anual||"N/A",control_vesical:f.control_vesical||"N/A"},antecedentes:{patologicos_medicos:f.patologicos_medicos||"N/A",sensoriales_motores:f.sensoriales_motores||"N/A",psiquiatricos:f.psiquiatricos||"N/A",farmacologicos:f.farmacologicos||"N/A",traumaticos:f.traumaticos||"N/A",quirurgicos:f.quirurgicos||"N/A",toxicos:f.toxicos||"N/A",alergicos:f.alergicos||"N/A",terapeuticos:f.terapeuticos||"N/A",paraclinicos:f.paraclinicos||"N/A",familiares:f.familiares||"N/A"},familiar:{vive_con:f.vive_con||"N/A",abc:f.abc||"N/A",escolar_laboral:f.escolar_laboral||"N/A",cognitivo:f.cognitivo||"N/A",comportamiento_animo:f.comportamiento_animo||"N/A",patron_sueno:f.patron_sueno||"N/A",patron_alimentacion:f.patron_alimentacion||"N/A"},plan_atencion:{plan_atencion:f.plan_atencion||"N/A",impresion_diagnostica_hc:f.impresion_diagnostica_hc||"N/A",hipotesis_pre_eval:f.hipotesis_pre_eval||"N/A"}};const resp=await api.post("/api/v1/clinical-history/",body);if(resp&&resp.row_version)set("row_version",resp.row_version);/* Persistir datos del acompañante en el registro del paciente */if(f.acompanante_nombre||f.acompanante_relacion||f.acompanante_telefono){try{await api.patch(`/api/v1/patients/${f.patient_id}`,{acompanante:f.acompanante_nombre,acompanante_relacion:f.acompanante_relacion,acompanante_telefono:f.acompanante_telefono})}catch{/* no bloquear si falla */}}setMsg("ok");setTimeout(()=>setMsg(""),3000)}catch(e){setMsg(_parseError(e))}setSaving(false)};
  const FG=({children,title,icon})=><div className="space-y-4"><h4 className="text-sm font-bold uppercase tracking-wider flex items-center gap-2" style={{color:"var(--ns-muted)"}}>{icon&&<I name={icon} className="text-base"/>}{title}</h4><div className="grid grid-cols-4 gap-4">{children}</div></div>;
  const devMotor=[["sosten_cefalico","Sostén Cefálico"],["sedestacion","Sedestación"],["gateo","Gateo"],["marcha","Marcha"]];
  const devLeng=[["balbuceo","Balbuceo"],["primeras_palabras","Primeras Palabras"],["habla_claro","Habla Claro"]];
  const devEsf=[["control_anual","Control Anal"],["control_vesical","Control Vesical"]];
  const antec=[["patologicos_medicos","Patológicos / Médicos"],["sensoriales_motores","Sensoriales / Motores"],["psiquiatricos","Psiquiátricos"],["farmacologicos","Farmacológicos"],["traumaticos","Traumáticos"],["quirurgicos","Quirúrgicos"],["toxicos","Tóxicos"],["alergicos","Alérgicos"],["terapeuticos","Terapéuticos"],["paraclinicos","Paraclínicos"],["familiares","Familiares"]];
  const famSoc=[["vive_con","¿Con quién vive?"],["abc","Actividades Básicas Cotidianas"],["escolar_laboral","Escolar / Laboral"],["cognitivo","Cognitivo"],["comportamiento_animo","Comportamiento y Ánimo"],["patron_sueno","Patrón de Sueño"],["patron_alimentacion","Patrón de Alimentación"]];
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(()=>{if(patId){set("patient_id",patId);loadHC(patId)}},[]);
  const patSel=patients.find(p=>p.id===f.patient_id);
  const patNombre=patSel?(patSel.nombre_completo||`${patSel.primer_nombre||""} ${patSel.primer_apellido||""}`.trim()):"";
  /* Población clínica derivada de la edad ya registrada del paciente */
  const patAgeYrs=patSel?.age_display?parseInt(patSel.age_display,10):null;
  const patPoblacion=patAgeYrs===null?null:patAgeYrs<18?"infantil":patAgeYrs<50?"adulto_joven":"adulto_mayor";
  const cieSugeridos=patPoblacion?(CIE_POR_POBLACION[patPoblacion]||[]):[];
  return(<><TopBar title="Historia Clínica"><div className="flex items-center gap-3"><Sel value={f.patient_id} onChange={e=>{const v=e.target.value;set("patient_id",v);setPatId(v);loadHC(v)}} className="text-xs w-72"><option value="">-- Seleccionar Paciente --</option>{patients.map(p=><option key={p.id} value={p.id}>{p.nombre_completo||`${p.primer_nombre} ${p.primer_apellido}`} - {p.numero_documento}</option>)}</Sel>{loading&&<div className="animate-spin w-5 h-5 border-2 border-teal-200 border-t-teal-600 rounded-full"/>}{f.patient_id&&<button onClick={()=>setShowConsent(true)} className="relative flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold transition-opacity hover:opacity-90" style={{color:pendCount>0?"#b45309":TEAL,background:pendCount>0?"#fef3c7":"var(--ns-subtle)"}} title="Consentimientos informados"><I name={pendCount>0?"error":"verified_user"} className="text-base"/>{pendCount>0?`${pendCount} pendiente${pendCount===1?"":"s"}`:"Consentimientos"}</button>}{/* §QW-4: Imprimir HC PDF */}{f.patient_id&&<button onClick={async()=>{try{const blob=await api.blob(`/api/v1/clinical-history/${f.patient_id}/pdf`);const u=URL.createObjectURL(blob);window.open(u,"_blank");setTimeout(()=>URL.revokeObjectURL(u),60000)}catch(e){setMsg(_parseError(e))}}} className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-teal-50" style={{color:TEAL,background:"var(--ns-subtle)"}} title="Generar PDF de la Historia Clínica completa para imprimir o adjuntar"><I name="print" className="text-base"/>Imprimir HC</button>}</div></TopBar>
  <main className="p-8 max-w-7xl mx-auto space-y-6">
    <MsgBanner msg={msg==="ok"?"ok":msg} onDismiss={msg&&msg!=="ok"?()=>setMsg(""):null}/>
    {/* §M-7: Sección de acompañantes (entidad separada del MC) */}
    {f.patient_id && <CompanionsSection patientId={f.patient_id} />}
    {f.patient_id&&<Card className="p-6 space-y-4">
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-3">
          <Label>Código CIE-10{patPoblacion&&<span className="ml-2 text-[10px] font-normal opacity-60">— {cieSugeridos.length} sugeridos para {patPoblacion.replace("_"," ")}</span>}</Label>
          <div className="relative">
            <Input
              value={cieQ||f.codigo_cie10}
              onChange={e=>searchCie(e.target.value)}
              onFocus={()=>setCieOpen(true)}
              onBlur={()=>setTimeout(()=>setCieOpen(false),200)}
              placeholder={cieSugeridos.length>0?"Haz clic o escribe para filtrar por población...":"Buscar código CIE-10..."}
            />
            {/* ── Dropdown inicial (por población): se muestra al hacer foco sin haber escrito ── */}
            {cieOpen&&!cieQ&&cieSugeridos.length>0&&(
              <div className="absolute z-20 top-full left-0 right-0 border rounded-xl shadow-xl max-h-64 overflow-y-auto mt-1" style={{background:"var(--ns-card)",borderColor:"var(--ns-card-b)"}}>
                <div className="sticky top-0 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wide border-b flex items-center gap-1.5" style={{background:"var(--ns-subtle)",color:TEAL}}>
                  <I name="filter_list" className="text-sm"/>
                  Frecuentes · {patPoblacion.replace("_"," ")} ({cieSugeridos.length})
                </div>
                {cieSugeridos.map(c=>(
                  <button key={c.codigo} onClick={()=>{set("codigo_cie10",c.codigo);setCieQ(c.codigo+" — "+c.nombre);setCie([]);setCieOpen(false)}} className="w-full text-left px-4 py-2 text-xs border-b last:border-0 flex items-baseline gap-2 transition-opacity hover:opacity-80" style={{borderColor:"var(--ns-card-b)"}}>
                    <span className="font-bold text-teal-600 shrink-0">{c.codigo}</span>
                    <span className="flex-1">{c.nombre}</span>
                    <span className="text-[9px] opacity-40 shrink-0">{c.dsm5}</span>
                  </button>
                ))}
              </div>
            )}
            {/* ── Dropdown de búsqueda: resultados filtrados al escribir ── */}
            {cie.length>0&&(
              <div className="absolute z-20 top-full left-0 right-0 border rounded-xl shadow-xl max-h-48 overflow-y-auto mt-1" style={{background:"var(--ns-card)",borderColor:"var(--ns-card-b)"}}>
                {cie.slice(0,10).map(c=>(
                  <button key={c.codigo} onClick={()=>{set("codigo_cie10",c.codigo);setCieQ(c.codigo+" — "+(c.nombre||c.descripcion));setCie([]);setCieOpen(false)}} className="w-full text-left px-4 py-2 text-xs hover:bg-teal-50 border-b last:border-0 flex items-baseline gap-2">
                    <span className="font-bold text-teal-600 shrink-0">{c.codigo}</span>
                    <span className="flex-1">{c.nombre||c.descripcion}</span>
                    {c.dsm5&&<span className="text-[9px] opacity-40 shrink-0">{c.dsm5}</span>}
                  </button>
                ))}
              </div>
            )}
          </div>
          {cie11Label&&(
            <div className="col-span-3 mt-1">
              <p className="text-[10px] font-bold uppercase tracking-wide" style={{color:"var(--ns-muted)"}}>CIE-11 (transición)</p>
              <p className="text-xs font-mono px-2 py-1 rounded" style={{background:"var(--ns-subtle)",color:TEAL}}>{cie11Label}</p>
            </div>
          )}
          {patSel?.via_atencion&&(
            <div className="col-span-3 mt-1">
              <p className="text-[10px] font-bold uppercase tracking-wide" style={{color:"var(--ns-muted)"}}>Vía de atención</p>
              <p className="text-xs capitalize">{patSel.via_atencion.replace("_"," ")}</p>
            </div>
          )}
        </div>
        <div className="col-span-2"><Label>No. Documento</Label><Input value={f.numero_documento} onChange={e=>set("numero_documento",e.target.value)}/></div>
        <div className="col-span-2"><Label>Fecha Atención</Label><Input type="date" value={f.fecha_atencion} onChange={e=>set("fecha_atencion",e.target.value)}/></div>
      </div>
      {/* §1.1 Acompañante como entidad separada */}
      <div className="pt-2 border-t" style={{borderColor:"var(--ns-card-b)"}}>
        <p className="text-xs font-bold uppercase tracking-wider mb-3 flex items-center gap-1.5" style={{color:TEAL}}><I name="group" className="text-base"/>Datos del acompañante</p>
        <div className="grid grid-cols-3 gap-4">
          <div><Label>Nombre del acompañante</Label><Input value={f.acompanante_nombre} onChange={e=>set("acompanante_nombre",e.target.value)} placeholder="Nombre completo"/></div>
          <div><Label>Relación / Parentesco</Label><Sel value={f.acompanante_relacion} onChange={e=>set("acompanante_relacion",e.target.value)}>
            <option value="">-- Seleccione --</option>
            <option>Madre</option><option>Padre</option><option>Ambos padres</option>
            <option>Cónyuge/Pareja</option><option>Hijo/a</option><option>Hermano/a</option>
            <option>Abuelo/a</option><option>Tío/a</option><option>Cuidador formal</option>
            <option>Otro familiar</option><option>Amigo/a</option><option>Acude solo</option>
          </Sel></div>
          <div><Label>Teléfono de contacto</Label><Input value={f.acompanante_telefono} onChange={e=>set("acompanante_telefono",e.target.value)} placeholder="Ej: 310 000 0000"/></div>
        </div>
      </div>
    </Card>}
    {/* Stepper visual numerado: muestra progreso del formulario y permite navegar */}
    {/* §1.4 Marcador de completitud */}
    {f.patient_id&&(()=>{const{done:doneN,total}=completitudsHC(f);return<div className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs" style={{background:doneN===total?"#d1fae5":"#fef3c7",color:doneN===total?"#065f46":"#92400e"}}><I name={doneN===total?"check_circle":"pending"} className="text-base" fill={doneN===total}/><span className="font-bold">{doneN}/{total} secciones con datos</span><span className="opacity-70">— {doneN<total?"Completar antes de finalizar el informe":"Lista para generar informe"}</span></div>})()}
    <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2">{tabs.map((t,i)=>{const ICONS=["child_care","medical_services","family_restroom","assignment"];const done=i<tab;const active=i===tab;return<React.Fragment key={t}>
      <button onClick={()=>setTab(i)} className="flex items-center gap-3 transition-all flex-shrink-0" style={{opacity:active||done?1:0.5}}>
        <div className="w-10 h-10 rounded-full flex items-center justify-center font-extrabold text-sm transition-all" style={active?{background:TEAL,color:"#fff",boxShadow:"0 8px 20px -4px rgba(13,148,136,0.5)",transform:"scale(1.1)"}:done?{background:"#10b981",color:"#fff"}:{background:"var(--ns-subtle)",color:"var(--ns-muted)"}}>
          {done?<I name="check" fill className="text-base"/>:<I name={ICONS[i]} className="text-lg"/>}
        </div>
        <div className="text-left">
          <p className="text-[9px] font-extrabold uppercase tracking-widest" style={{color:active?TEAL:"var(--ns-muted)"}}>Paso {i+1}</p>
          <p className="text-xs font-bold" style={{color:active?"var(--ns-text)":"var(--ns-muted)"}}>{t}</p>
        </div>
      </button>
      {i<tabs.length-1&&<div className="flex-1 h-0.5 rounded-full mx-1" style={{background:i<tab?"#10b981":"var(--ns-subtle)"}}/>}
    </React.Fragment>})}</div>
    {tab===0&&<div className="space-y-6">
      <Card className="p-8 space-y-4">
        <h3 className="text-lg font-bold flex items-center gap-2"><I name="record_voice_over" style={{color:TEAL}}/>Motivo de consulta y curso</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><Label>MC del remitente</Label><Txta value={f.mc_remitente} onChange={e=>set("mc_remitente",e.target.value)} placeholder="Orden médica / sospecha remitente" className="min-h-[80px]"/></div>
          <div><Label>Queja subjetiva (paciente o familiar)</Label><Txta value={f.mc_subjetivo} onChange={e=>set("mc_subjetivo",e.target.value)} placeholder="En palabras del consultante" className="min-h-[80px]"/></div>
          <div className="md:col-span-2"><Label>Enfermedad actual (inicio, curso, factores)</Label><Txta value={f.enfermedad_actual} onChange={e=>set("enfermedad_actual",e.target.value)} placeholder="Cronología y evolución del cuadro" className="min-h-[100px]"/></div>
        </div>
        <div className="flex flex-wrap gap-2">
          {["Memoria","Atención","Lenguaje","Conducta","Ánimo"].map(q=><button key={q} type="button" onClick={()=>set("mc_subjetivo",f.mc_subjetivo?`${f.mc_subjetivo}; ${q.toLowerCase()}`:q.toLowerCase())} className="text-[10px] px-2 py-1 rounded-full border" style={{borderColor:TEAL,color:TEAL}}>+ {q}</button>)}
        </div>
      </Card>
      <Card className="p-8"><FG title="Periodo Perinatal" icon="pregnant_woman"><div><Label>Edad Materna</Label><Input value={f.edad_materna} onChange={e=>set("edad_materna",e.target.value)} placeholder="N/A"/></div><div><Label>No. Gestación</Label><Input value={f.no_gestacion} onChange={e=>set("no_gestacion",e.target.value)} placeholder="Ej: 1"/></div><div><Label>Riesgos</Label><Sel value={f.riesgos} onChange={e=>set("riesgos",e.target.value)}><option>No</option><option>Sí</option></Sel></div>{f.riesgos==="Sí"&&<div><Label>¿Cuál riesgo?</Label><Input value={f.cual_riesgo} onChange={e=>set("cual_riesgo",e.target.value)}/></div>}<div><Label>Estrés Prenatal</Label><Sel value={f.estres_prenatal} onChange={e=>set("estres_prenatal",e.target.value)}><option>No</option><option>Sí</option></Sel></div>{f.estres_prenatal==="Sí"&&<div><Label>Tipo Estrés</Label><Input value={f.tipo_estres_prenatal} onChange={e=>set("tipo_estres_prenatal",e.target.value)}/></div>}<div><Label>Gestación</Label><Sel value={f.gestacion} onChange={e=>set("gestacion",e.target.value)}><option>A Término</option><option>Pretérmino</option><option>Postérmino</option></Sel></div><div><Label>Semanas</Label><Input value={f.semanas} onChange={e=>set("semanas",e.target.value)} placeholder="Ej: 38"/></div></FG></Card>
      <Card className="p-8"><FG title="Parto y Neonatal" icon="crib"><div><Label>Tipo de Parto</Label><Sel value={f.tipo_parto} onChange={e=>set("tipo_parto",e.target.value)}><option>Natural</option><option>Cesárea</option><option>Inducido</option><option>Fórceps</option></Sel></div><div><Label>Peso (gr)</Label><Input value={f.peso_gr} onChange={e=>set("peso_gr",e.target.value)} placeholder="Ej: 3200"/></div><div><Label>Talla (cm)</Label><Input value={f.talla_cm} onChange={e=>set("talla_cm",e.target.value)} placeholder="Ej: 50"/></div><div><Label>Incubadora</Label><Sel value={f.incubadora} onChange={e=>set("incubadora",e.target.value)}><option>No</option><option>Sí</option></Sel></div><div><Label>UCIN</Label><Sel value={f.ucin} onChange={e=>set("ucin",e.target.value)}><option>No</option><option>Sí</option></Sel></div><div className="col-span-3"><Label>Condiciones Neonatales</Label><Txta value={f.condiciones_neonatales} onChange={e=>set("condiciones_neonatales",e.target.value)} placeholder="Ictericia, cianosis, Apgar..."/></div></FG></Card>
      <Card className="p-8 space-y-6">
        <FG title="Desarrollo Motor" icon="directions_walk">{devMotor.map(([k,l])=><div key={k}><Label>{l}</Label><Input value={f[k]} onChange={e=>set(k,e.target.value)} placeholder="Edad (meses)"/></div>)}</FG>
        <FG title="Desarrollo del Lenguaje" icon="record_voice_over">{devLeng.map(([k,l])=><div key={k}><Label>{l}</Label><Input value={f[k]} onChange={e=>set(k,e.target.value)} placeholder="Edad (meses)"/></div>)}<div/></FG>
        <FG title="Control de Esfínteres" icon="wc">{devEsf.map(([k,l])=><div key={k}><Label>{l}</Label><Input value={f[k]} onChange={e=>set(k,e.target.value)} placeholder="Edad (meses)"/></div>)}<div/><div/></FG>
      </Card>
    </div>}
    {tab===1&&<Card className="p-8"><h3 className="text-lg font-bold mb-4 flex items-center gap-2"><I name="medical_services" className="text-red-500"/>Antecedentes médicos</h3><div className="grid grid-cols-2 gap-x-6 gap-y-4">{antec.map(([k,l])=><div key={k}><Label>{l}</Label><Txta value={f[k]} onChange={e=>set(k,e.target.value)} placeholder="N/A" className="min-h-[60px]"/></div>)}</div></Card>}
    {tab===2&&<Card className="p-8"><h3 className="text-lg font-bold mb-6 flex items-center gap-2"><I name="family_restroom" className="text-purple-600"/>Familiar / Social / Funcional</h3><div className="grid grid-cols-2 gap-x-6 gap-y-4">{famSoc.map(([k,l])=><div key={k}><Label>{l}</Label><Txta value={f[k]} onChange={e=>set(k,e.target.value)} placeholder="N/A" className="min-h-[70px]"/></div>)}</div></Card>}
    {tab===3&&<Card className="p-8 space-y-6"><h3 className="text-lg font-bold mb-2 flex items-center gap-2"><I name="assignment" className="text-green-600"/>Plan de Atención</h3>
      <SectionCard title="Screening y tamización (módulo aparte)" icon="fact_check" eyebrow="Flujo clínico" subtitle="MMSE, escalas breves y tamización emocional se aplican y registran en Evaluación → Screening, usualmente antes o en paralelo a esta HC — no como paso del formulario.">
        <div className="flex flex-wrap items-center gap-3">
          <Btn v="outline" onClick={()=>{safeLS.set("ns_sel_patient",f.patient_id);setPage("screening")}}><I name="open_in_new" className="text-sm"/>Ir a Screening del paciente</Btn>
          <p className="text-xs" style={{color:"var(--ns-muted)"}}>Los resultados quedan vinculados al expediente y alimentan el informe NPS.</p>
        </div>
      </SectionCard>
      <SectionCard title="Hipótesis diagnóstica" icon="psychology" eyebrow="Plan clínico" subtitle="Integra anamnesis, screening previo (MMSE/escalas) y observación clínica. Orienta el protocolo de evaluación cognitiva.">
        <Txta value={f.hipotesis_pre_eval} onChange={e=>set("hipotesis_pre_eval",e.target.value)} placeholder="Ej: DCL probable con queja subjetiva + MMSE 24/30. Orientar protocolo adulto mayor con énfasis en memoria y FE." className="min-h-[80px]"/>
      </SectionCard>
      <div><Label>Plan de Atención</Label><Txta value={f.plan_atencion} onChange={e=>set("plan_atencion",e.target.value)} placeholder="Objetivos, actividades, frecuencia..." className="min-h-[150px]"/></div>
      <div><Label>Impresión Diagnóstica</Label><Txta value={f.impresion_diagnostica_hc} onChange={e=>set("impresion_diagnostica_hc",e.target.value)} placeholder="Diagnóstico diferencial, hipótesis clínica..." className="min-h-[150px]"/></div>
    </Card>}
    <div className="flex justify-between items-center"><div className="flex gap-2">{tab>0&&<Btn v="outline" onClick={()=>setTab(t=>t-1)}><I name="chevron_left" className="text-sm"/>Anterior</Btn>}{tab<3&&<Btn v="outline" onClick={()=>setTab(t=>t+1)}>Siguiente<I name="chevron_right" className="text-sm"/></Btn>}</div><div className="flex gap-4"><Btn v="outline" onClick={()=>setPage("patients")}>Cancelar</Btn><Btn onClick={saveHC} disabled={saving}>{saving?"Guardando...":"Guardar Historia Clínica"}</Btn></div></div>
  </main>
  {showConsent&&f.patient_id&&<ConsentModal patientId={f.patient_id} patientName={patNombre} patientEmail={patSel?.correo||""} onClose={()=>{setShowConsent(false);checkConsents(f.patient_id)}} onAllSigned={()=>setPendCount(0)}/>}
  </>);
}
