/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/ConfigPage.jsx — Pagina de configuracion del sistema
 * 8 tabs agrupadas: institucion, profesionales, informe, plantillas,
 * firmas, estimulos, respaldo, auditoria.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import {
  Btn, Card, I, Input, Label, MsgBanner, Sel, TopBar,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { useA11y, useAuth, useToast } from "../../contexts.jsx";
import { REPORT_TEMPLATES } from "../../data/ui.js";
import SignatureCanvas from "../evaluation/SignatureCanvas.jsx";
import AvatarUploader from "../../ui/AvatarUploader.jsx";
import EstimulosTab from "./EstimulosTab.jsx";
import BackupTab from "./BackupTab.jsx";
import AuditoriaTab from "./AuditoriaTab.jsx";
import FormatosTab from "./FormatosTab.jsx";
import AdminKpisTab from "./AdminKpisTab.jsx";
import PrivacyPolicyModal from "../legal/PrivacyPolicyModal.jsx";
import ComunicacionesTab from "./ComunicacionesTab.jsx"; // §QW-2/3
import UpdateTab from "./UpdateTab.jsx"; // §update-system

/* ══════════════ CONFIGURACIÓN ══════════════ */

export default function ConfigPage({setPage}){
  const toast = useToast();
  const{highContrast,fontScale,setHighContrast,setFontScale}=useA11y();
  const{user}=useAuth();
  const isAdmin=user?.role==="admin";
  const[privOpen,setPrivOpen]=useState(false);
  const[tab,setTab]=useState(0);
  const[inst,setInst]=useState({nombre:"",nit:"",direccion:"",telefono:"",email:"",sitio_web:"",logo_base64:null,ciudad:"Bogotá"});
  const[profs,setProfs]=useState([]);const[pf,setPf]=useState({nombre_completo:"",registro_profesional:"",titulo:"",especialidad:"",email:"",firma_base64:"",foto_base64:""});
  const[prefs,setPrefs]=useState({fuente_cuerpo:"Calibri",fuente_titulos:"Calibri",tamano_fuente_cuerpo:11,tamano_fuente_titulos:13,color_primario:"#0D9488",color_secundario:"#2ec4b6",incluir_logo:true,incluir_firma:true,incluir_grafica_z:true,incluir_tabla_puntajes:true,nota_pie_informe:"",plantilla_activa:"clinico"});
  const[editingProf,setEditingProf]=useState(null);const[firmaDraw,setFirmaDraw]=useState("");
  const[msg,setMsg]=useState("");const[ld,setLd]=useState(true);const[saving,setSaving]=useState(false);
  useEffect(()=>{Promise.all([
    api.get("/api/v1/config/").catch(e=>({_err:e.detail||"No se pudo cargar configuración"})),
    api.get("/api/v1/config/profesionales").catch(()=>[])
  ]).then(([cfg,ps])=>{
    if(cfg&&cfg._err){setMsg(cfg._err);setLd(false);return}
    if(cfg&&cfg.institucion)setInst(cfg.institucion);
    if(cfg&&cfg.prefs_informe)setPrefs(p=>({...p,...cfg.prefs_informe}));
    if(cfg&&cfg.profesionales&&(!ps||ps.length===0))setProfs(cfg.profesionales);
    else setProfs(ps||[]);
    setLd(false)
  })},[]);
  const saveInst=async()=>{setSaving(true);setMsg("");try{await api.put("/api/v1/config/institucion",inst);setMsg("ok")}catch(e){setMsg(_parseError(e))}setSaving(false)};
  const savePrefs=async()=>{setSaving(true);setMsg("");try{await api.put("/api/v1/config/prefs-informe",prefs);setMsg("ok")}catch(e){setMsg(_parseError(e))}setSaving(false)};
  const addProf=async()=>{if(!pf.nombre_completo)return;setSaving(true);try{const body={...pf};["firma_base64","foto_base64","titulo","especialidad","registro_profesional","email"].forEach(k=>{if(!body[k])delete body[k]});const d=await api.post("/api/v1/config/profesionales",body);setProfs(p=>[...p,d]);setPf({nombre_completo:"",registro_profesional:"",titulo:"",especialidad:"",email:"",firma_base64:"",foto_base64:""});setMsg("ok")}catch(e){setMsg(_parseError(e))}setSaving(false)};
  /* §foto: actualizar la foto de un profesional ya existente. */
  const updateProfFoto=async(prof,foto_base64)=>{try{const d=await api.put(`/api/v1/config/profesionales/${prof.id}`,{nombre_completo:prof.nombre_completo,titulo:prof.titulo,especialidad:prof.especialidad,registro_profesional:prof.registro_profesional,email:prof.email,activo:prof.activo,foto_base64});setProfs(ps=>ps.map(x=>x.id===prof.id?{...x,foto_base64:d.foto_base64,tiene_foto:d.tiene_foto}:x));setMsg("ok")}catch(e){setMsg(_parseError(e))}};
  const delProf=async(id)=>{try{await api.del(`/api/v1/config/profesionales/${id}`);setProfs(p=>p.filter(x=>x.id!==id))}catch{toast.error("Error al eliminar profesional")}};
  const si=(k,v)=>setInst(o=>({...o,[k]:v}));
  const sp=(k,v)=>setPrefs(o=>({...o,[k]:v}));
  const sf=(k,v)=>setPf(o=>({...o,[k]:v}));
  if(!isAdmin)return<><TopBar title="Configuracion"><span className="text-xs text-gray-400">Perfil sin permisos administrativos</span></TopBar>
  <main className="p-8 max-w-3xl mx-auto space-y-6">
    <Card className="p-8 space-y-6">
      <div>
        <h3 className="text-lg font-bold flex items-center gap-2"><I name="lock" style={{color:TEAL}}/>Modo profesional / beta tester</h3>
        <p className="text-xs mt-2" style={{color:"var(--ns-muted)"}}>Este usuario puede probar los flujos clinicos, pero no puede cambiar institucion, profesionales, backups, auditoria ni KPIs administrativos.</p>
      </div>
      <div className="space-y-3">
        <p className="text-sm font-bold" style={{color:"var(--ns-text)"}}>Modo alto contraste</p>
        <label className="flex items-center gap-3 cursor-pointer w-fit">
          <div onClick={()=>setHighContrast(!highContrast)} className={`relative w-12 h-6 rounded-full transition-colors ${highContrast?"bg-teal-600":"bg-gray-300"}`}>
            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${highContrast?"translate-x-6":""}`}/>
          </div>
          <span className="text-sm font-medium">{highContrast?"Activado":"Desactivado"}</span>
        </label>
      </div>
      <div className="space-y-3">
        <p className="text-sm font-bold" style={{color:"var(--ns-text)"}}>Tamano de texto de la interfaz</p>
        <div className="flex gap-3 flex-wrap">
          {[["md","Normal"],["lg","Grande"],["xl","Muy grande"]].map(([k,label])=>(
            <button key={k} onClick={()=>setFontScale(k)}
              className={`px-5 py-3 rounded-2xl text-sm font-bold border-2 transition-all ${fontScale===k?"text-white border-teal-500":"border-transparent hover:border-teal-300"}`}
              style={fontScale===k?{background:TEAL}:{background:"var(--ns-subtle)",color:"var(--ns-muted)"}}>
              {label}
            </button>
          ))}
        </div>
      </div>
    </Card>
  </main></>;
  if(ld)return<><TopBar title="Configuración"/><main className="p-8 flex items-center justify-center h-96"><div className="animate-spin w-8 h-8 border-4 border-teal-200 border-t-teal-600 rounded-full"/></main></>;
  return(<><TopBar title="Configuración del Sistema"><span className="text-xs text-gray-400">Datos institucionales y preferencias</span></TopBar>
  <main className="p-8 max-w-5xl mx-auto space-y-6">
    <MsgBanner msg={msg==="ok"?"ok":msg} onDismiss={msg&&msg!=="ok"?()=>setMsg(""):null}/>
    {/* Navegación por secciones temáticas */}
    <div className="rounded-xl border overflow-hidden" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}>
      {[
        {
          title: "Mi consultorio",
          icon: "business",
          desc: "Datos de la institución, profesionales y configuración del informe",
          items: [{i:0,ic:"business",l:"Institución"},{i:1,ic:"badge",l:"Profesionales"},{i:2,ic:"article",l:"Informe PDF"},{i:3,ic:"dashboard_customize",l:"Plantillas"},{i:4,ic:"draw",l:"Firmas"}],
        },
        {
          title: "Datos clínicos",
          icon: "science",
          desc: "Materiales y estímulos para las evaluaciones",
          items: [{i:5,ic:"image",l:"Estímulos"}],
        },
        {
          title: "Sistema",
          icon: "settings",
          desc: "Respaldo, auditoría, comunicaciones y accesibilidad",
          items: [{i:6,ic:"cloud_download",l:"Respaldo"},{i:7,ic:"policy",l:"Auditoría"},{i:8,ic:"description",l:"Formatos"},{i:9,ic:"dashboard",l:"KPIs"},{i:10,ic:"accessibility_new",l:"Accesibilidad"},{i:11,ic:"privacy_tip",l:"Privacidad"},{i:12,ic:"mail",l:"Comunicaciones"},{i:13,ic:"system_update",l:"Actualizar"}],
        },
      ].map((group, gi) => (
        <div key={group.title} className={gi > 0 ? "border-t" : ""} style={{ borderColor: "var(--ns-card-b)" }}>
          <div className="px-5 py-3 flex items-center gap-2" style={{ background: "var(--ns-subtle)" }}>
            <I name={group.icon} className="text-sm" style={{ color: TEAL }} />
            <span className="text-[11px] font-extrabold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>{group.title}</span>
            <span className="text-[10px] ml-2" style={{ color: "var(--ns-muted)" }}>— {group.desc}</span>
          </div>
          <div className="flex flex-wrap gap-1.5 px-5 py-3">
            {group.items.map(({i, ic, l}) => (
              <button key={i} onClick={() => { setTab(i); setMsg(""); }}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${tab === i ? "text-white shadow-md" : "hover:shadow-sm"}`}
                style={tab === i
                  ? { background: TEAL, boxShadow: `0 4px 12px -4px ${TEAL}60` }
                  : { background: "var(--ns-subtle)", color: "var(--ns-muted)", border: "1px solid var(--ns-card-b)" }}>
                <I name={ic} className="text-sm" />{l}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
    {tab===0&&<Card className="p-8 space-y-6">
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="business" style={{color:TEAL}}/>Datos de la Institución</h3>
      <div className="grid grid-cols-2 gap-4">
        <div><Label>Nombre de la Institución</Label><Input value={inst.nombre||""} onChange={e=>si("nombre",e.target.value)} placeholder="Nombre de su institución"/></div>
        <div><Label>NIT</Label><Input value={inst.nit||""} onChange={e=>si("nit",e.target.value)} placeholder="Ej: 901.192.434-4"/></div>
        <div><Label>Dirección</Label><Input value={inst.direccion||""} onChange={e=>si("direccion",e.target.value)} placeholder="Ej: Cl 90 # 19-41 Of 305"/></div>
        <div><Label>Teléfono</Label><Input value={inst.telefono||""} onChange={e=>si("telefono",e.target.value)} placeholder="Ej: 6018418995"/></div>
        <div><Label>Email</Label><Input value={inst.email||""} onChange={e=>si("email",e.target.value)} placeholder="Ej: coordinacion@institucion.com"/></div>
        <div><Label>Ciudad</Label><Input value={inst.ciudad||""} onChange={e=>si("ciudad",e.target.value)} placeholder="Ej: Bogotá"/></div>
        <div className="col-span-2"><Label>Sitio Web</Label><Input value={inst.sitio_web||""} onChange={e=>si("sitio_web",e.target.value)} placeholder="Ej: www.institucion.com"/></div>
      </div>
      <div className="flex justify-end"><Btn onClick={saveInst} disabled={saving}>{saving?"Guardando...":"Guardar Institución"}</Btn></div>
    </Card>}
    {tab===1&&<div className="space-y-4">
      <Card className="p-6">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2"><I name="person_add" className="text-teal-600"/>Agregar Profesional</h3>
        <div className="flex gap-6">
          {/* §foto: Avatar uploader a la izquierda del formulario */}
          <div className="shrink-0">
            <AvatarUploader
              value={pf.foto_base64}
              onChange={v=>sf("foto_base64",v)}
              name={pf.nombre_completo}
              size={104}
            />
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 flex-1">
            <div><Label>Nombre Completo *</Label><Input value={pf.nombre_completo} onChange={e=>sf("nombre_completo",e.target.value)} placeholder="Nombre completo del profesional"/></div>
            <div><Label>Registro Profesional</Label><Input value={pf.registro_profesional} onChange={e=>sf("registro_profesional",e.target.value)} placeholder="TP-12345"/></div>
            <div><Label>Título</Label><Input value={pf.titulo} onChange={e=>sf("titulo",e.target.value)} placeholder="Neuropsicóloga"/></div>
            <div><Label>Especialidad</Label><Input value={pf.especialidad} onChange={e=>sf("especialidad",e.target.value)} placeholder="NPs Infantil"/></div>
            <div className="col-span-2"><Label>Email</Label><Input value={pf.email} onChange={e=>sf("email",e.target.value)} placeholder="correo@email.com"/></div>
          </div>
        </div>
        <div className="flex justify-end mt-4"><Btn onClick={addProf} disabled={saving||!pf.nombre_completo}>{saving?"Guardando...":"Agregar"}</Btn></div>
      </Card>
      {/* §foto: listado de profesionales con avatar editable in-line */}
      <Card className="overflow-hidden">
        {profs.length===0?<div className="p-8 text-center" style={{color:"var(--ns-muted)"}}>
          <I name="group" className="text-4xl mb-2"/><p className="font-bold">Sin profesionales registrados</p>
        </div>:(
          <div className="divide-y" style={{borderColor:"var(--ns-card-b)"}}>
            {profs.map(p=>(
              <div key={p.id} className="p-4 flex items-center gap-4 hover:bg-gray-50/30 transition-all">
                <AvatarUploader
                  value={p.foto_base64||""}
                  onChange={v=>updateProfFoto(p,v)}
                  name={p.nombre_completo}
                  size={64}
                />
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-sm truncate" style={{color:"var(--ns-text)"}}>{p.nombre_completo}</p>
                  <p className="text-xs truncate" style={{color:"var(--ns-muted)"}}>
                    {p.titulo||"—"} {p.especialidad?`· ${p.especialidad}`:""}
                  </p>
                  <div className="flex items-center gap-3 mt-1">
                    {p.registro_profesional&&<span className="text-[10px] font-mono px-2 py-0.5 rounded" style={{background:"var(--ns-subtle)",color:"var(--ns-muted)"}}>{p.registro_profesional}</span>}
                    {p.tiene_firma&&<span className="text-[10px] font-bold flex items-center gap-1" style={{color:TEAL}}><I name="draw" className="text-[10px]"/>Firma</span>}
                    {p.tiene_foto&&<span className="text-[10px] font-bold flex items-center gap-1" style={{color:TEAL}}><I name="photo_camera" className="text-[10px]"/>Foto</span>}
                  </div>
                </div>
                <button onClick={()=>delProf(p.id)}
                  className="p-2 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 shrink-0"
                  title="Desactivar profesional">
                  <I name="delete" className="text-lg"/>
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>}
    {tab===2&&<Card className="p-8 space-y-6">
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="article" className="text-orange-600"/>Preferencias del Informe PDF</h3>
      <div className="grid grid-cols-2 gap-4">
        <div><Label>Fuente Cuerpo</Label><Input value={prefs.fuente_cuerpo||""} onChange={e=>sp("fuente_cuerpo",e.target.value)} placeholder="Calibri"/></div>
        <div><Label>Fuente Títulos</Label><Input value={prefs.fuente_titulos||""} onChange={e=>sp("fuente_titulos",e.target.value)} placeholder="Calibri"/></div>
        <div><Label>Tamaño Fuente Cuerpo</Label><Input type="number" value={prefs.tamano_fuente_cuerpo||11} onChange={e=>sp("tamano_fuente_cuerpo",parseInt(e.target.value,10)||11)} min={8} max={16}/></div>
        <div><Label>Tamaño Fuente Títulos</Label><Input type="number" value={prefs.tamano_fuente_titulos||13} onChange={e=>sp("tamano_fuente_titulos",parseInt(e.target.value,10)||13)} min={10} max={20}/></div>
        <div><Label>Color Primario</Label><Input type="color" value={prefs.color_primario||"#0D9488"} onChange={e=>sp("color_primario",e.target.value)}/></div>
        <div><Label>Color Secundario</Label><Input type="color" value={prefs.color_secundario||"#2ec4b6"} onChange={e=>sp("color_secundario",e.target.value)}/></div>
        <div className="col-span-2"><Label>Nota Pie de Informe</Label><Input value={prefs.nota_pie_informe||""} onChange={e=>sp("nota_pie_informe",e.target.value)} placeholder="Texto para el pie del informe"/></div>
      </div>
      <div className="flex gap-6 flex-wrap">
        <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={prefs.incluir_logo} onChange={e=>sp("incluir_logo",e.target.checked)} className="w-4 h-4 rounded"/><span className="text-sm font-medium">Incluir logo</span></label>
        <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={prefs.incluir_firma} onChange={e=>sp("incluir_firma",e.target.checked)} className="w-4 h-4 rounded"/><span className="text-sm font-medium">Incluir firma profesional</span></label>
        <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={prefs.incluir_grafica_z} onChange={e=>sp("incluir_grafica_z",e.target.checked)} className="w-4 h-4 rounded"/><span className="text-sm font-medium">Incluir gráfica Z</span></label>
        <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={prefs.incluir_tabla_puntajes} onChange={e=>sp("incluir_tabla_puntajes",e.target.checked)} className="w-4 h-4 rounded"/><span className="text-sm font-medium">Incluir tabla de puntajes</span></label>
      </div>
      <div className="flex justify-end"><Btn onClick={savePrefs} disabled={saving}>{saving?"Guardando...":"Guardar Preferencias"}</Btn></div>
    </Card>}
    {tab===3&&<Card className="p-8 space-y-5">
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="dashboard_customize" style={{color:TEAL}}/>Plantillas de Informe</h3>
      <p className="text-xs" style={{color:"var(--ns-muted)"}}>Seleccione el formato de informe predeterminado. Cada plantilla define qué secciones se incluyen y en qué orden.</p>
      <div className="grid grid-cols-2 gap-4">{Object.entries(REPORT_TEMPLATES).map(([k,tpl])=><button key={k} onClick={()=>sp("plantilla_activa",k)} className={`p-5 rounded-2xl text-left border-2 transition-all ${prefs.plantilla_activa===k?"border-teal-500 shadow-lg":"hover:border-teal-300"}`} style={{borderColor:prefs.plantilla_activa===k?TEAL:"var(--ns-card-b)",background:prefs.plantilla_activa===k?`${TEAL}08`:"var(--ns-card)"}}>
        <div className="flex items-center justify-between mb-2"><h4 className="font-bold text-sm">{tpl.nombre}</h4>{prefs.plantilla_activa===k&&<I name="check_circle" fill className="text-teal-600"/>}</div>
        <p className="text-xs mb-3" style={{color:"var(--ns-muted)"}}>{tpl.descripcion}</p>
        <div className="flex flex-wrap gap-1">{tpl.secciones.map(s=><span key={s} className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{background:"var(--ns-subtle)",color:"var(--ns-muted)"}}>{s.replace(/_/g," ")}</span>)}</div>
      </button>)}</div>
      <div className="flex justify-end"><Btn onClick={savePrefs} disabled={saving}>{saving?"Guardando...":"Guardar Plantilla"}</Btn></div>
    </Card>}
    {tab===4&&<Card className="p-8 space-y-6">
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="draw" style={{color:TEAL}}/>Firma Digital de Profesionales</h3>
      <p className="text-xs" style={{color:"var(--ns-muted)"}}>Capture la firma digital de cada profesional dibujándola directamente en el panel. La firma se guardará en formato PNG y se integrará automáticamente en los informes PDF.</p>
      {profs.length===0?<div className="text-center py-12" style={{color:"var(--ns-muted)"}}><I name="group_off" className="text-4xl mb-3 opacity-30"/><p className="text-sm font-bold">Sin profesionales registrados</p><p className="text-xs mt-1">Vaya a la pestaña "Profesionales" para agregar uno primero</p></div>
      :<div className="space-y-4">{profs.map(p=>{const isEditing=editingProf===p.id;return<div key={p.id} className="rounded-2xl p-5 border" style={{borderColor:"var(--ns-card-b)",background:"var(--ns-subtle)"}}>
        <div className="flex items-center justify-between mb-3"><div><h4 className="font-bold text-sm">{p.nombre_completo}</h4><p className="text-xs" style={{color:"var(--ns-muted)"}}>{p.titulo||"—"} · {p.registro_profesional||"—"}</p></div>
          {p.firma_base64&&!isEditing&&<img src={p.firma_base64} alt="firma" className="h-12 rounded bg-white p-1"/>}
          {!isEditing?<Btn v="outline" onClick={()=>{setEditingProf(p.id);setFirmaDraw(p.firma_base64||"")}} className="text-xs"><I name="edit" className="text-sm"/>{p.firma_base64?"Cambiar":"Agregar"} Firma</Btn>
          :<div className="flex gap-2"><Btn v="outline" onClick={()=>{setEditingProf(null);setFirmaDraw("")}} className="text-xs">Cancelar</Btn><Btn onClick={async()=>{try{await api.post(`/api/v1/advanced/config/profesionales/${p.id}/firma`,{firma_base64:firmaDraw});setProfs(ps=>ps.map(x=>x.id===p.id?{...x,firma_base64:firmaDraw,tiene_firma:true}:x));setEditingProf(null);setFirmaDraw("");setMsg("ok")}catch(e){setMsg(_parseError(e))}}} className="text-xs">Guardar Firma</Btn></div>}
        </div>
        {isEditing&&<SignatureCanvas value={firmaDraw} onChange={setFirmaDraw}/>}
      </div>})}</div>}
    </Card>}
    {tab===5&&<EstimulosTab/>}
    {tab===6&&<BackupTab/>}
    {tab===7&&<AuditoriaTab/>}
    {tab===8&&<FormatosTab/>}
    {tab===9&&<AdminKpisTab/>}
{tab===12&&<ComunicacionesTab/>}
    {tab===13&&<UpdateTab/>}
    {tab===11&&<Card className="p-8 space-y-6">
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="privacy_tip" fill style={{color:TEAL}}/>Privacidad y Protección de Datos</h3>
      <div className="p-5 rounded-2xl border-l-4 text-sm leading-relaxed" style={{background:`${TEAL}08`,borderColor:TEAL,color:"var(--ns-text)"}}>
        <p className="font-bold mb-1 flex items-center gap-2"><I name="gavel" className="text-base" style={{color:TEAL}}/>Marco legal aplicable</p>
        <p className="text-xs" style={{color:"var(--ns-muted)"}}>NeuroSoft cumple con la Ley 1581 de 2012 (Protección de Datos Personales), el Decreto 1377 de 2013, la Resolución 1995 de 1999 (Historia Clínica Electrónica) y la Resolución 2654 de 2019 (Telesalud). El prestador de servicios es responsable del tratamiento adecuado de los datos de sus pacientes.</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {[
          {icon:"lock",title:"Almacenamiento local",desc:"Todos los datos clínicos se almacenan únicamente en el equipo de la institución. NeuroSoft no transmite datos a servidores externos."},
          {icon:"person_check",title:"Derechos ARCO",desc:"Los pacientes tienen derecho a Acceder, Rectificar, Cancelar y Oponerse al tratamiento de sus datos. Gestionar a través del módulo de pacientes."},
          {icon:"description",title:"Historia clínica",desc:"La conservación mínima es de 20 años para adultos. Los documentos generados deben custodiarse conforme a la Resolución 1995 de 1999."},
          {icon:"security",title:"Datos sensibles",desc:"Los datos de salud son datos sensibles (Art. 5, Ley 1581). Su tratamiento requiere consentimiento explícito. Use el módulo de consentimiento informado."},
        ].map(item=>(
          <div key={item.title} className="p-5 rounded-2xl border space-y-2" style={{borderColor:"var(--ns-card-b)",background:"var(--ns-subtle)"}}>
            <div className="flex items-center gap-2">
              <I name={item.icon} fill className="text-base" style={{color:TEAL}}/>
              <p className="text-sm font-bold">{item.title}</p>
            </div>
            <p className="text-xs leading-relaxed" style={{color:"var(--ns-muted)"}}>{item.desc}</p>
          </div>
        ))}
      </div>
      <div className="flex flex-col sm:flex-row gap-3">
        <button onClick={()=>setPrivOpen(true)} className="flex-1 flex items-center justify-center gap-2 py-4 rounded-2xl border-2 font-bold text-sm transition-all hover:-translate-y-0.5" style={{borderColor:TEAL,color:TEAL,background:`${TEAL}08`}}>
          <I name="policy" fill className="text-lg"/>Ver Política de Privacidad Completa
        </button>
        <a href="https://www.sic.gov.co/bases-de-datos" target="_blank" rel="noopener noreferrer" className="flex-1 flex items-center justify-center gap-2 py-4 rounded-2xl border-2 font-bold text-sm transition-all hover:-translate-y-0.5" style={{borderColor:"var(--ns-card-b)",color:"var(--ns-muted)",background:"var(--ns-subtle)"}}>
          <I name="open_in_new" className="text-lg"/>Registro SIC (Base de datos)
        </a>
      </div>
      <div className="p-4 rounded-2xl text-[10px] leading-relaxed text-center" style={{background:"var(--ns-subtle)",color:"var(--ns-muted)"}}>
        <I name="info" className="text-xs mr-1"/>
        El registro de la base de datos ante la Superintendencia de Industria y Comercio (SIC) es obligatorio para los responsables del tratamiento. Consulte el portal SIC para completar este trámite administrativo.
      </div>
      <PrivacyPolicyModal open={privOpen} onClose={()=>setPrivOpen(false)}/>
    </Card>}
    {tab===10&&<Card className="p-8 space-y-8">
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="accessibility_new" style={{color:TEAL}}/>Accesibilidad</h3>
      {/* Alto contraste */}
      <div className="space-y-3">
        <p className="text-sm font-bold" style={{color:"var(--ns-text)"}}>Modo alto contraste</p>
        <p className="text-xs" style={{color:"var(--ns-muted)"}}>Aumenta el contraste de colores y bordes para facilitar la lectura en ambientes con poca luz o para usuarios con baja visión.</p>
        <label className="flex items-center gap-3 cursor-pointer w-fit">
          <div onClick={()=>setHighContrast(!highContrast)} className={`relative w-12 h-6 rounded-full transition-colors ${highContrast?"bg-teal-600":"bg-gray-300"}`}>
            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${highContrast?"translate-x-6":""}`}/>
          </div>
          <span className="text-sm font-medium">{highContrast?"Activado":"Desactivado"}</span>
        </label>
      </div>
      {/* Escala de fuente */}
      <div className="space-y-3">
        <p className="text-sm font-bold" style={{color:"var(--ns-text)"}}>Tamaño de texto de la interfaz</p>
        <p className="text-xs" style={{color:"var(--ns-muted)"}}>Ajusta el tamaño base del texto en toda la aplicación. El tamaño de los PDF no se ve afectado.</p>
        <div className="flex gap-3">
          {[["md","Normal (16px)"],["lg","Grande (18px)"],["xl","Muy grande (20px)"]].map(([k,label])=>(
            <button key={k} onClick={()=>setFontScale(k)}
              className={`px-5 py-3 rounded-2xl text-sm font-bold border-2 transition-all ${fontScale===k?"text-white border-teal-500":"border-transparent hover:border-teal-300"}`}
              style={fontScale===k?{background:TEAL}:{background:"var(--ns-subtle)",color:"var(--ns-muted)"}}>
              {label}
            </button>
          ))}
        </div>
      </div>
      {/* Atajos de teclado para accesibilidad */}
      <div className="space-y-3 p-4 rounded-2xl" style={{background:"var(--ns-subtle)"}}>
        <p className="text-xs font-bold uppercase tracking-wider" style={{color:"var(--ns-muted)"}}>Atajos de teclado activos</p>
        <div className="grid grid-cols-2 gap-2 text-xs" style={{color:"var(--ns-muted)"}}>
          <span><kbd className="px-1.5 py-0.5 rounded text-xs font-mono" style={{background:"var(--ns-card)",border:"1px solid var(--ns-card-b)"}}>Alt+H</kbd> Toggle alto contraste</span>
          <span><kbd className="px-1.5 py-0.5 rounded text-xs font-mono" style={{background:"var(--ns-card)",border:"1px solid var(--ns-card-b)"}}>Alt++</kbd> Aumentar fuente</span>
          <span><kbd className="px-1.5 py-0.5 rounded text-xs font-mono" style={{background:"var(--ns-card)",border:"1px solid var(--ns-card-b)"}}>Alt+-</kbd> Reducir fuente</span>
        </div>
      </div>
    </Card>}
  </main></>);
}
