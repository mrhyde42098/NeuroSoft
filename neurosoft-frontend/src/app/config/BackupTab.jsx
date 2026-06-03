/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/BackupTab.jsx — Respaldo y restauracion de la base de datos
 * Descarga, creacion, listado y restore con snapshot de seguridad previo.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, API, _parseError } from "../../api/client.js";
import { useToast, useConfirm } from "../../contexts.jsx";
import {
  Btn, Card, I, Input, MsgBanner,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* ══════════════ BackupTab — respaldo y restauración ══════════════ */
export default function BackupTab(){
  const[list,setList]=useState([]);const[ld,setLd]=useState(true);const[saving,setSaving]=useState(false);const[msg,setMsg]=useState("");
  const[notas,setNotas]=useState("");const[restoreFile,setRestoreFile]=useState(null);const[confirmRestore,setConfirmRestore]=useState(false);
  const toast=useToast();const confirm=useConfirm();
  const load=async()=>{setLd(true);try{const d=await api.get("/api/v1/backup/list");setList(d||[])}catch{setList([])}setLd(false)};
  useEffect(()=>{load()},[]);
  const doDownload=async()=>{try{const token=localStorage.getItem("ns_token")||"";const r=await fetch(API+"/api/v1/backup/download",{headers:{Authorization:"Bearer "+token}});if(!r.ok)throw new Error("HTTP "+r.status);const blob=await r.blob();const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=`neurosoft_backup_${new Date().toISOString().slice(0,19).replace(/[:T]/g,"")}.db`;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);toast.success("Backup descargado")}catch(e){toast.error("Error al descargar: "+(e.message||e))}};
  const doCreate=async()=>{setSaving(true);setMsg("");try{const q=notas?"?notas="+encodeURIComponent(notas):"";await api.post("/api/v1/backup/"+q,{});toast.success("Backup creado en el servidor");setNotas("");load()}catch(e){toast.error(_parseError(e))}setSaving(false)};
  const doDelete=async(nombre)=>{if(!(await confirm({title:"Eliminar backup",message:`El archivo "${nombre}" se borrará permanentemente.\nEsta acción no se puede deshacer.`,confirmText:"Eliminar",dangerous:true})))return;try{await api.del("/api/v1/backup/"+encodeURIComponent(nombre));toast.success("Backup eliminado");load()}catch(e){toast.error(_parseError(e))}};
  const handleRestoreFile=(f)=>{if(!f)return;if(!f.name.endsWith(".db")){toast.error("Solo archivos .db");return}if(f.size<1024){toast.error("Archivo demasiado pequeño");return}setRestoreFile(f);setConfirmRestore(false)};
  const doRestore=async()=>{if(!restoreFile||!confirmRestore)return;setSaving(true);setMsg("");try{const fd=new FormData();fd.append("archivo",restoreFile);const token=localStorage.getItem("ns_token")||"";const r=await fetch(API+"/api/v1/backup/restore",{method:"POST",headers:{Authorization:"Bearer "+token},body:fd});if(!r.ok){const j=await r.json().catch(()=>({detail:"HTTP "+r.status}));throw new Error(j.detail||"HTTP "+r.status)}const j=await r.json();toast.success("BD restaurada. Reinicie para aplicar cambios.");setMsg(`Restaurado: ${j.bytes_restaurados} bytes. Snapshot previo: ${j.safety_snapshot}`);setRestoreFile(null);setConfirmRestore(false);load()}catch(e){toast.error("Error al restaurar: "+(e.message||e))}setSaving(false)};
  const fmtKB=kb=>kb==null?"—":kb<1024?`${kb.toFixed(1)} KB`:`${(kb/1024).toFixed(1)} MB`;
  const fmtDate=s=>{if(!s)return"—";try{return new Date(s).toLocaleString("es-CO",{dateStyle:"short",timeStyle:"short"})}catch{return s}};
  return<Card className="p-8 space-y-6">
    <div>
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="cloud_download" style={{color:TEAL}}/>Respaldo de la Base de Datos</h3>
      <p className="text-xs mt-1" style={{color:"var(--ns-muted)"}}>Gestione copias de seguridad locales. Los respaldos automáticos se ejecutan a diario a las 02:00 y se conservan 30 días (más los del domingo indefinidamente).</p>
    </div>
    <MsgBanner msg={msg==="ok"?"ok":msg} onDismiss={msg&&msg!=="ok"?()=>setMsg(""):null}/>

    {/* Descargar + Crear manual */}
    <div className="grid grid-cols-2 gap-4">
      <div className="p-5 rounded-xl" style={{background:"var(--ns-subtle)"}}>
        <p className="text-sm font-bold mb-2 flex items-center gap-2"><I name="download" style={{color:TEAL}}/>Descargar BD actual</p>
        <p className="text-xs mb-3" style={{color:"var(--ns-muted)"}}>Descarga el archivo SQLite completo a su equipo. Guárdelo en un lugar seguro.</p>
        <Btn onClick={doDownload}><I name="download" className="text-sm"/>Descargar .db</Btn>
      </div>
      <div className="p-5 rounded-xl" style={{background:"var(--ns-subtle)"}}>
        <p className="text-sm font-bold mb-2 flex items-center gap-2"><I name="save" style={{color:TEAL}}/>Crear backup en servidor</p>
        <p className="text-xs mb-2" style={{color:"var(--ns-muted)"}}>Guarda una copia en la carpeta <code className="text-[10px]">data/backups/</code>.</p>
        <Input value={notas} onChange={e=>setNotas(e.target.value)} placeholder="Notas (opcional)" className="mb-2 text-xs"/>
        <Btn onClick={doCreate} disabled={saving}><I name="save" className="text-sm"/>{saving?"Guardando...":"Crear backup"}</Btn>
      </div>
    </div>

    {/* Restaurar */}
    <div className="p-5 rounded-xl border-2" style={{borderColor:"#fca5a5",background:"#fef2f2"}}>
      <p className="text-sm font-bold mb-2 flex items-center gap-2" style={{color:"#b91c1c"}}><I name="restore" className="text-red-600"/>Restaurar desde archivo .db</p>
      <p className="text-xs mb-3" style={{color:"#991b1b"}}>⚠️ Irreversible. Antes de restaurar se creará un snapshot de seguridad <code className="text-[10px]">pre_restore_[timestamp].db</code>. Tras restaurar, reinicie el servicio.</p>
      <div className="flex items-center gap-3 mb-3">
        <input type="file" accept=".db" onChange={e=>handleRestoreFile(e.target.files[0])} className="text-xs"/>
        {restoreFile&&<span className="text-xs font-mono" style={{color:"var(--ns-muted)"}}>{restoreFile.name} ({(restoreFile.size/1024).toFixed(1)} KB)</span>}
      </div>
      {restoreFile&&<label className="flex items-center gap-2 cursor-pointer mb-3"><input type="checkbox" checked={confirmRestore} onChange={e=>setConfirmRestore(e.target.checked)} className="w-4 h-4"/><span className="text-xs font-bold" style={{color:"#991b1b"}}>Entiendo que los datos actuales serán reemplazados</span></label>}
      <Btn onClick={doRestore} disabled={!restoreFile||!confirmRestore||saving} style={{background:"#dc2626"}}><I name="restore" className="text-sm"/>{saving?"Restaurando...":"Restaurar BD"}</Btn>
    </div>

    {/* Historial */}
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-bold">Historial de backups ({list.length})</p>
        <button onClick={load} className="text-xs flex items-center gap-1 hover:underline" style={{color:TEAL}}><I name="refresh" className="text-sm"/>Refrescar</button>
      </div>
      {ld?<div className="flex justify-center py-8"><div className="animate-spin w-6 h-6 border-4 border-teal-200 border-t-teal-600 rounded-full"/></div>
      :list.length===0?<div className="text-center py-8" style={{color:"var(--ns-muted)"}}><I name="folder_off" className="text-4xl opacity-30 mb-2"/><p className="text-sm font-bold">Sin backups guardados</p></div>
      :<Card className="overflow-hidden"><table className="w-full text-sm"><thead style={{background:"var(--ns-subtle)"}}><tr><th className="px-4 py-3 text-left font-bold text-xs">Archivo</th><th className="px-4 py-3 text-left font-bold text-xs">Fecha</th><th className="px-4 py-3 text-left font-bold text-xs">Tamaño</th><th className="px-4 py-3 text-left font-bold text-xs">Notas</th><th className="px-4 py-3 w-16"></th></tr></thead>
        <tbody>{list.map((b,i)=><tr key={i} className="border-b" style={{borderColor:"var(--ns-card-b)"}}>
          <td className="px-4 py-3 font-mono text-[11px]">{b.nombre||b.archivo||b.ruta_destino?.split(/[\\/]/).pop()||"—"}</td>
          <td className="px-4 py-3 text-xs" style={{color:"var(--ns-muted)"}}>{fmtDate(b.fecha||b.creado_en||b.fecha_creacion)}</td>
          <td className="px-4 py-3 text-xs" style={{color:"var(--ns-muted)"}}>{fmtKB(b.tamano_kb||b.size_kb)}</td>
          <td className="px-4 py-3 text-xs" style={{color:"var(--ns-muted)"}}>{b.notas||"—"}</td>
          <td className="px-4 py-3"><button onClick={()=>doDelete(b.nombre||b.archivo)} className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500" title="Eliminar" aria-label="Eliminar este respaldo"><I name="delete" className="text-lg"/></button></td>
        </tr>)}</tbody></table></Card>}
    </div>
  </Card>
}
