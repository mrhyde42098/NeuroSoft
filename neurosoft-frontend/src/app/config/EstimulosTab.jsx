/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/EstimulosTab.jsx — Gestion de estimulos por subprueba
 * Subida individual + carga masiva con drag-drop y soporte ZIP.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { useToast, useConfirm } from "../../contexts.jsx";
import {
  Btn, Card, I, Input, Label, MsgBanner, Sel, Txta,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* ══════════════ EstimulosTab — gestión de estímulos y reactivos ══════════════ */
export default function EstimulosTab(){
  const toast=useToast();const confirm=useConfirm();
  const[items,setItems]=useState([]);const[ld,setLd]=useState(true);
  const[testId,setTestId]=useState("");const[itemId,setItemId]=useState("");
  const[nombre,setNombre]=useState("");const[tipo,setTipo]=useState("imagen");
  const[desc,setDesc]=useState("");const[file,setFile]=useState(null);const[fileB64,setFileB64]=useState("");
  const[saving,setSaving]=useState(false);const[msg,setMsg]=useState("");
  const[filterTest,setFilterTest]=useState("");
  /* Bulk upload (drag-drop multiselección + ZIP) */
  const[bulkQueue,setBulkQueue]=useState([]);/* [{name, size, b64, mime}] */
  const[bulkDrag,setBulkDrag]=useState(false);const[bulkTest,setBulkTest]=useState("");const[bulkTipo,setBulkTipo]=useState("imagen");const[bulkBusy,setBulkBusy]=useState(false);
  const testOptions=["NiWiscDC","NiWiscMat","NiFigHum","NiFCROCop","NiTMTA","NiTMTB","NiIntObj","NiRecEmo","GBTotal","CVLTTotal","SDMT","FluidP","FluidAnim","Denom48","BNT","StroopAM","StroopAJ","MMSE"];
  const load=async()=>{setLd(true);try{const d=await api.get(`/api/v1/estimulos/${filterTest?`?test_id=${filterTest}`:""}`);setItems(d||[])}catch{setItems([])}setLd(false)};
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(()=>{load()},[filterTest]);
  const handleFile=(f)=>{if(!f)return;if(f.size>5*1024*1024){setMsg("Archivo muy grande (máx 5MB)");return}setFile(f);const r=new FileReader();r.onload=e=>setFileB64(e.target.result);r.readAsDataURL(f)};
  const subir=async()=>{if(!testId||!nombre||!fileB64){setMsg("Faltan datos: test, nombre y archivo");return}setSaving(true);setMsg("");try{await api.post("/api/v1/estimulos/",{test_id:testId,item_id:itemId||null,nombre,tipo,mime_type:file?.type||"image/png",contenido_base64:fileB64,descripcion:desc||null,orden:items.filter(i=>i.test_id===testId).length});setMsg("ok");setNombre("");setItemId("");setDesc("");setFile(null);setFileB64("");load()}catch(e){setMsg(_parseError(e))}setSaving(false)};
  const eliminar=async(id)=>{if(!(await confirm({title:"Eliminar estímulo",message:"El estímulo se borrará permanentemente.",confirmText:"Eliminar",dangerous:true})))return;try{await api.del(`/api/v1/estimulos/${id}`);load()}catch(e){toast.error("Error: "+_parseError(e))}};
  /* Bulk helpers */
  const readAsDataURL=(f)=>new Promise((res,rej)=>{const r=new FileReader();r.onload=e=>res(e.target.result);r.onerror=rej;r.readAsDataURL(f)});
  const addFilesToQueue=async(fileList)=>{
    const out=[];
    for(const f of fileList){
      if(f.size>5*1024*1024){out.push({name:f.name,size:f.size,error:"archivo >5MB"});continue}
      const isZip=/\.zip$/i.test(f.name)||f.type==="application/zip"||f.type==="application/x-zip-compressed";
      if(isZip){
        try{
          const JSZip=(await import("jszip")).default;
          const zip=await JSZip.loadAsync(f);
          const entries=Object.values(zip.files).filter(z=>!z.dir);
          for(const z of entries){
            if(!/\.(png|jpe?g|gif|webp|bmp|svg|mp3|wav|ogg|txt|pdf)$/i.test(z.name))continue;
            const blob=await z.async("blob");
            if(blob.size>5*1024*1024){out.push({name:z.name,size:blob.size,error:"archivo >5MB"});continue}
            const b64=await readAsDataURL(new File([blob],z.name));
            out.push({name:z.name.replace(/^.*\//,""),size:blob.size,b64,mime:blob.type||"application/octet-stream"});
          }
        }catch(e){out.push({name:f.name,size:f.size,error:"ZIP inválido: "+(e?.message||e)});}
      }else{
        const b64=await readAsDataURL(f);
        out.push({name:f.name,size:f.size,b64,mime:f.type||"application/octet-stream"});
      }
    }
    setBulkQueue(q=>[...q,...out]);
  };
  const onDropBulk=async(e)=>{e.preventDefault();setBulkDrag(false);const fl=Array.from(e.dataTransfer.files||[]);if(fl.length)await addFilesToQueue(fl);};
  const subirBulk=async()=>{
    if(!bulkTest){setMsg("Elija el test_id para la carga masiva");return}
    const payload=bulkQueue.filter(q=>!q.error&&q.b64).map((q,i)=>({
      test_id:bulkTest,item_id:null,nombre:q.name.replace(/\.[^.]+$/,""),
      tipo:bulkTipo,mime_type:q.mime||"image/png",contenido_base64:q.b64,descripcion:null,orden:i,
    }));
    if(payload.length===0){setMsg("No hay archivos válidos para subir");return}
    setBulkBusy(true);setMsg("");
    try{
      const r=await api.post("/api/v1/estimulos/bulk",payload);
      setMsg(`Subidos: ${r.creados} · Fallidos: ${r.fallidos}`);
      setBulkQueue([]);load();
    }catch(e){setMsg(_parseError(e));}
    setBulkBusy(false);
  };
  return<Card className="p-8 space-y-6">
    <div>
      <h3 className="text-lg font-bold flex items-center gap-2"><I name="image" style={{color:TEAL}}/>Estímulos y Reactivos</h3>
      <p className="text-xs mt-1" style={{color:"var(--ns-muted)"}}>Suba imágenes de sus reactivos (cubos, figuras, tarjetas) o listas de palabras para que aparezcan en la pantalla de aplicación de cada prueba.</p>
    </div>
    <MsgBanner msg={msg==="ok"?"ok":msg} onDismiss={msg&&msg!=="ok"?()=>setMsg(""):null}/>

    {/* Formulario de carga */}
    <div className="p-5 rounded-xl" style={{background:"var(--ns-subtle)"}}>
      <p className="text-sm font-bold mb-3">Subir nuevo estímulo</p>
      <div className="grid grid-cols-2 gap-3">
        <div><Label className="text-xs">Prueba (test_id)</Label>
          <Sel value={testId} onChange={e=>setTestId(e.target.value)}><option value="">— Elegir —</option>{testOptions.map(t=><option key={t} value={t}>{t}</option>)}</Sel>
        </div>
        <div><Label className="text-xs">Ítem (opcional)</Label><Input value={itemId} onChange={e=>setItemId(e.target.value)} placeholder="p.ej. item_3"/></div>
        <div><Label className="text-xs">Nombre</Label><Input value={nombre} onChange={e=>setNombre(e.target.value)} placeholder="p.ej. Tarjeta modelo 1"/></div>
        <div><Label className="text-xs">Tipo</Label>
          <Sel value={tipo} onChange={e=>setTipo(e.target.value)}><option value="imagen">Imagen</option><option value="lista_palabras">Lista de palabras</option><option value="audio">Audio</option><option value="otro">Otro</option></Sel>
        </div>
        <div className="col-span-2"><Label className="text-xs">Descripción (opcional)</Label><Txta value={desc} onChange={e=>setDesc(e.target.value)} placeholder="Notas sobre el estímulo..." className="min-h-[60px] text-xs"/></div>
        <div className="col-span-2"><Label className="text-xs">Archivo (máx 5MB)</Label>
          <input type="file" accept="image/*,.txt,.pdf,audio/*" onChange={e=>handleFile(e.target.files[0])} className="text-xs"/>
          {fileB64&&fileB64.startsWith("data:image")&&<img src={fileB64} alt="preview" className="mt-2 max-h-32 rounded border"/>}
        </div>
      </div>
      <div className="flex justify-end mt-4"><Btn onClick={subir} disabled={saving}><I name="upload" className="text-sm"/>{saving?"Subiendo...":"Subir estímulo"}</Btn></div>
    </div>

    {/* ─── BULK UPLOAD drag-drop + ZIP (Fase E.3) ─── */}
    <div className="p-5 rounded-xl border-2 border-dashed" style={{borderColor:bulkDrag?TEAL:"var(--ns-card-b)",background:bulkDrag?TEAL+"0a":"var(--ns-subtle)"}}
         onDragOver={e=>{e.preventDefault();setBulkDrag(true)}} onDragLeave={()=>setBulkDrag(false)} onDrop={onDropBulk}>
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <p className="text-sm font-bold flex items-center gap-2"><I name="cloud_upload" style={{color:TEAL}}/>Carga masiva (arrastrar varios archivos o un ZIP)</p>
        <div className="flex items-center gap-2">
          <Sel value={bulkTest} onChange={e=>setBulkTest(e.target.value)} className="text-xs w-44"><option value="">— test_id destino —</option>{testOptions.map(t=><option key={t} value={t}>{t}</option>)}</Sel>
          <Sel value={bulkTipo} onChange={e=>setBulkTipo(e.target.value)} className="text-xs w-36"><option value="imagen">Imagen</option><option value="lista_palabras">Palabras</option><option value="audio">Audio</option><option value="otro">Otro</option></Sel>
        </div>
      </div>
      <p className="text-[11px] mb-3 text-center" style={{color:"var(--ns-muted)"}}>
        Arrastre aquí varios archivos (imágenes/audio/txt) <strong>o un .zip</strong> · {bulkQueue.length} archivo{bulkQueue.length===1?"":"s"} en cola
      </p>
      <div className="flex items-center justify-center gap-2 flex-wrap">
        <input id="bulkfile" type="file" multiple accept="image/*,audio/*,.txt,.zip" className="hidden" onChange={e=>{if(e.target.files?.length)addFilesToQueue(Array.from(e.target.files));e.target.value=""}}/>
        <label htmlFor="bulkfile" className="text-xs font-bold px-3 py-1.5 rounded-full cursor-pointer" style={{background:TEAL+"15",color:TEAL}}><I name="folder_open" className="text-sm"/> Seleccionar archivos</label>
        {bulkQueue.length>0&&<button onClick={()=>setBulkQueue([])} className="text-xs font-bold px-3 py-1.5 rounded-full" style={{color:"var(--ns-muted)",background:"var(--ns-subtle)"}}>Vaciar cola</button>}
        <Btn onClick={subirBulk} disabled={bulkBusy||bulkQueue.length===0||!bulkTest} className="text-xs"><I name="upload" className="text-sm"/>{bulkBusy?"Subiendo...":`Subir ${bulkQueue.filter(q=>!q.error).length}`}</Btn>
      </div>
      {bulkQueue.length>0&&<div className="mt-3 max-h-40 overflow-y-auto rounded-lg" style={{background:"var(--ns-card)"}}>
        <table className="w-full text-[10px]"><tbody>
          {bulkQueue.map((q,i)=><tr key={i} className="border-b" style={{borderColor:"var(--ns-card-b)"}}>
            <td className="px-3 py-1.5 font-mono">{q.name}</td>
            <td className="px-3 py-1.5 text-right" style={{color:"var(--ns-muted)"}}>{(q.size/1024).toFixed(1)} KB</td>
            <td className="px-3 py-1.5">{q.error?<span className="text-red-600 font-bold">{q.error}</span>:<span style={{color:TEAL}}>✓</span>}</td>
            <td className="px-3 py-1.5"><button onClick={()=>setBulkQueue(qq=>qq.filter((_,j)=>j!==i))} className="text-red-400 hover:text-red-600" aria-label="Quitar de la cola de carga" title="Quitar"><I name="close" className="text-xs"/></button></td>
          </tr>)}
        </tbody></table>
      </div>}
    </div>

    {/* Filtro + listado */}
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-bold">Estímulos cargados ({items.length})</p>
        <Sel value={filterTest} onChange={e=>setFilterTest(e.target.value)} className="text-xs w-48"><option value="">— Todos los tests —</option>{testOptions.map(t=><option key={t} value={t}>{t}</option>)}</Sel>
      </div>
      {ld?<div className="flex justify-center py-8"><div className="animate-spin w-6 h-6 border-4 border-teal-200 border-t-teal-600 rounded-full"/></div>
      :items.length===0?<div className="text-center py-8" style={{color:"var(--ns-muted)"}}><I name="image" className="text-4xl opacity-30 mb-2"/><p className="text-sm font-bold">Sin estímulos cargados</p></div>
      :<div className="grid grid-cols-3 gap-3">{items.map(i=><Card key={i.id} className="p-3">
        <div className="flex items-start justify-between mb-2"><div className="flex-1 min-w-0">
          <p className="text-xs font-bold truncate">{i.nombre}</p>
          <p className="text-[10px] font-mono" style={{color:"var(--ns-muted)"}}>{i.test_id}{i.item_id?" · "+i.item_id:""}</p>
        </div><button onClick={()=>eliminar(i.id)} className="text-red-500 hover:bg-red-50 rounded p-1" aria-label="Eliminar este estímulo" title="Eliminar"><I name="delete" className="text-sm"/></button></div>
        <span className="text-[9px] font-bold uppercase px-2 py-0.5 rounded" style={{background:TEAL+"15",color:TEAL}}>{i.tipo}</span>
        {i.descripcion&&<p className="text-[10px] mt-2 leading-snug" style={{color:"var(--ns-muted)"}}>{i.descripcion}</p>}
      </Card>)}</div>}
    </div>
  </Card>
}
