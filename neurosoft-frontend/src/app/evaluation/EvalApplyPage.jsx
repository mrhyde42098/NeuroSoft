/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/EvalApplyPage.jsx — Aplicacion de evaluacion neuropsicologica
 * Selector de protocolo + cronometro + reactivos + guia clinica lateral.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState } from "react";
import { api } from "../../api/client.js";
import { useToast, useConfirm } from "../../contexts.jsx";
import { protocoloPorEdad } from "../../data/datosClinicos.js";
import { Btn, Card, I, Sel, TopBar, Txta } from "../../ui/primitives.jsx";
import { safeLS } from "../../utils/safeLS.js";
import { TEAL } from "../../ui/tokens.js";
import {
 CONDUCTAS, GUIA_HC, GUIA_INFORME, INSTRUCCIONES, REACTIVOS,
 HITO_LABELS, formatRetentionRemaining, getRetentionStatus,
 getRetentionStorageKey, getSuggestedClinicalTest, isClinicalTestDone,
 prepareClinicalProtocolTests,
} from "../../data/clinical.js";
import ReactivePanel from "./ReactivePanel.jsx";
import ScoreInput from "./ScoreInput.jsx";
import StimulusDisplay from "./StimulusDisplay.jsx";
import OrdenClinicoBanner from "./OrdenClinicoBanner.jsx"; // §M-6
import GuideFormatter from "./GuideFormatter.jsx";
import { ADAPTATIONS, SATTLER_FORMS, estimateCITFromShortForm } from "../../utils/sattlerShortForms.js";
import { getNeuronormaInfo, NEURONORMA_COLOMBIA_REF } from "../../data/neuronormaColombia.js";
import { getSubtest } from "../../data/protocolLoader.js";

/* §autosave: clave del borrador local. Una clave por paciente+protocolo. */
const DRAFT_KEY = (patientId, proto) => `ns_eval_draft_${patientId || "sin_paciente"}_${proto}`;
const DRAFT_TTL_MS = 7 * 24 * 60 * 60 * 1000; // 7 días — luego expira

export default function EvalApplyPage({setPage,nav,evalCtx,setEvalCtx}){
 /* §M3-fix: toast + confirm modal (reemplazan alert/window.confirm). */
 const toast=useToast();const confirm=useConfirm();
 const[patients,setPatients]=useState([]);const[patId,setPatId]=useState(evalCtx?.patientId||safeLS.get("ns_sel_patient")||"");
 const[tests,setTests]=useState([]);const[cur,setCur]=useState(0);const[puntajes,setPuntajes]=useState(evalCtx?.puntajes||{});const[obs,setObs]=useState(evalCtx?.obs||{});
 /* §autosave: estado del borrador (timestamp de último guardado, si hubo restore). */
 const[draftSavedAt,setDraftSavedAt]=useState(null);
 const[draftRestoredFrom,setDraftRestoredFrom]=useState(null);/* ISO date string si se restauró un draft */
 const[timer,setTimer]=useState(0);const[timerOn,setTimerOn]=useState(false);const[retentionTick,setRetentionTick]=useState(Date.now());const ref=useRef(null);
 const[mode,setMode]=useState("apply");const[guiaOpen,setGuiaOpen]=useState(false);const[guiaTab,setGuiaTab]=useState("conductas");
 const[proto,setProto]=useState("wisc_iv");
 const[adaptacion,setAdaptacion]=useState("estandar");
 const[itemScores,setItemScores]=useState({});/* Reactive item-level scores */
 const[conductas_checked,setConducChecked]=useState({});/* §4.2: conductas seleccionadas por test_id */
 const protos={wisc_iv:{nombre:"WISC-IV",tests:[{test_id:"NiWiscDC",nombre:"Diseño con Cubos",dominio:"Razonamiento Perceptual",has_timer:true,tiempo_max:120},{test_id:"NiWiscSem",nombre:"Semejanzas",dominio:"Comprensión Verbal"},{test_id:"NiWiscRDD",nombre:"Retención de Dígitos",dominio:"Memoria de Trabajo"},{test_id:"NiWiscConD",nombre:"Conceptos con Dibujos",dominio:"Razonamiento Perceptual"},{test_id:"NiWiscCl",nombre:"Claves",dominio:"Velocidad de Proceso",has_timer:true,tiempo_max:120},{test_id:"NiWiscVoc",nombre:"Vocabulario",dominio:"Comprensión Verbal"},{test_id:"NiWiscLN",nombre:"Letras y Números",dominio:"Memoria de Trabajo"},{test_id:"NiWiscMat",nombre:"Matrices",dominio:"Razonamiento Perceptual"},{test_id:"NiWiscCom",nombre:"Comprensión",dominio:"Comprensión Verbal"},{test_id:"NiWiscBusSim",nombre:"Búsqueda de Símbolos",dominio:"Velocidad de Proceso",has_timer:true,tiempo_max:120},{test_id:"NiWisFigInc",nombre:"Figuras Incompletas",dominio:"Razonamiento Perceptual",has_timer:true,tiempo_max:20,es_suplementaria:true},{test_id:"NiWiscAri",nombre:"Aritmética",dominio:"Memoria de Trabajo",has_timer:true,tiempo_max:30,es_suplementaria:true},{test_id:"NiWisInf",nombre:"Información",dominio:"Comprensión Verbal",es_suplementaria:true},{test_id:"NiWisPalCon",nombre:"Palabras en Contexto",dominio:"Comprensión Verbal",es_suplementaria:true},{test_id:"NiWisReg",nombre:"Registros",dominio:"Velocidad de Proceso",has_timer:true,tiempo_max:45,es_suplementaria:true},{test_id:"REY15",nombre:"Rey 15-Item Test (Validez)",dominio:"Validez de síntomas",es_suplementaria:true}]},wais_iii:{nombre:"WAIS-III",tests:[{test_id:"AdWAISFI",nombre:"Figuras Incompletas",dominio:"Organización Perceptual",has_timer:true,tiempo_max:20},{test_id:"AdWAISV",nombre:"Vocabulario",dominio:"Comprensión Verbal"},{test_id:"AdSDWais",nombre:"Clave de Números",dominio:"Velocidad de Procesamiento",has_timer:true,tiempo_max:120},{test_id:"AdSemWais",nombre:"Semejanzas",dominio:"Comprensión Verbal"},{test_id:"AdWAISCC",nombre:"Cubos",dominio:"Organización Perceptual",has_timer:true,tiempo_max:120},{test_id:"AdWAISA",nombre:"Aritmética",dominio:"Memoria de Trabajo",has_timer:true,tiempo_max:60},{test_id:"AdMatr",nombre:"Matrices",dominio:"Organización Perceptual"},{test_id:"AdDDir",nombre:"Dígitos",dominio:"Memoria de Trabajo"},{test_id:"AdWAISI",nombre:"Información",dominio:"Comprensión Verbal"},{test_id:"AdWAISC",nombre:"Comprensión",dominio:"Comprensión Verbal"},{test_id:"AdBusSim + ViBusSim",nombre:"Búsqueda de Símbolos",dominio:"Velocidad de Procesamiento",has_timer:true,tiempo_max:120},{test_id:"AdWAISL",nombre:"Letras y Números",dominio:"Memoria de Trabajo"},{test_id:"REY15",nombre:"Rey 15-Item Test (Validez)",dominio:"Validez de síntomas",es_suplementaria:true}]},ninos_comp:{nombre:"Niños Complementario",tests:[{test_id:"NiEniE1 + NiEniE2 + NiEniE3 + NiEniE4 = NiEniLT",nombre:"Curva Memoria ENI-2",dominio:"Memoria Verbal"},{test_id:"NiFCROCop",nombre:"FCRO Copia",dominio:"Praxias"},{test_id:"NiIntObj",nombre:"Integración de Objetos",dominio:"Praxias/Gnosias"},{test_id:"NiRecEmo",nombre:"Expresiones Faciales",dominio:"Praxias/Gnosias"},{test_id:"NiFigHum",nombre:"Figura Humana",dominio:"Praxias/Gnosias"},{test_id:"NiRDD",nombre:"Dígitos directos ENI-2",dominio:"Atención"},{test_id:"NiTMTA",nombre:"TMT-A",dominio:"Atención",has_timer:true,tiempo_max:180},{test_id:"NiTMTB",nombre:"TMT-B",dominio:"Atención",has_timer:true,tiempo_max:300},{test_id:"NiTestPC_R",nombre:"CARAS-R",dominio:"Atención",has_timer:true,tiempo_max:180},{test_id:"NiENICDib",nombre:"Cancelación Dibujos",dominio:"Atención"},{test_id:"NiFCRORec",nombre:"FCRO Recobro",dominio:"Memoria Visual"},{test_id:"NiENIDen",nombre:"Denominación",dominio:"Lenguaje"},{test_id:"NiFA",nombre:"Fluidez Animales",dominio:"Lenguaje"},{test_id:"NiPrec",nombre:"Lectura en Voz Alta",dominio:"Lectura"},{test_id:"NiLVS",nombre:"Lectura Silenciosa",dominio:"Lectura"},{test_id:"NiCopTxt",nombre:"Copia de Texto",dominio:"Escritura"},{test_id:"NiRecEscrita",nombre:"Recuperación Escrita",dominio:"Escritura"},{test_id:"NiCalcEscrito",nombre:"Cálculo Escrito",dominio:"Matemáticas"},{test_id:"NiENICMen",nombre:"Cálculo Mental",dominio:"Matemáticas"},{test_id:"NiSt_Edades",nombre:"Stroop",dominio:"Función Ejecutiva"},{test_id:"NiENISInv",nombre:"Serie Inversa/Dígitos Inversos",dominio:"Función Ejecutiva"},{test_id:"NiFM",nombre:"Fluidez M",dominio:"Función Ejecutiva"}]},adulto_mayor:{nombre:"Adulto Mayor",tests:[{test_id:"EscKertesz",nombre:"Kertesz/FBI",dominio:"Escalas"},{test_id:"EscQueja",nombre:"Queja Subjetiva Memoria",dominio:"Escalas"},{test_id:"EscYesavage",nombre:"Yesavage",dominio:"Escalas"},{test_id:"EscLawton",nombre:"Lawton",dominio:"Escalas"},{test_id:"MMSE",nombre:"MMSE Orientación",dominio:"Orientación"},{test_id:"GBTotal",nombre:"Grober & Buschke",dominio:"Memoria Verbal"},{test_id:"NiFCROCop",nombre:"FCRO Copia",dominio:"Praxias"},{test_id:"AdTMTA",nombre:"TMT-A",dominio:"Atención",has_timer:true,tiempo_max:300},{test_id:"AdTMTB",nombre:"TMT-B",dominio:"Atención",has_timer:true,tiempo_max:300},{test_id:"SDMT",nombre:"SDMT",dominio:"Atención",has_timer:true,tiempo_max:90},{test_id:"AdDDir",nombre:"Dígitos WAIS-III",dominio:"Atención"},{test_id:"InstrConflICO",nombre:"Instrucciones Conflictivas",dominio:"Atención"},{test_id:"AdFCRORec",nombre:"FCRO Recobro",dominio:"Memoria Visual"},{test_id:"FluidP",nombre:"Fluidez P",dominio:"Lenguaje"},{test_id:"FluidAnim",nombre:"Fluidez Animales",dominio:"Lenguaje"},{test_id:"Denom48",nombre:"Denominación 48 ítems",dominio:"Lenguaje"},{test_id:"AdSemWais",nombre:"Semejanzas",dominio:"Función Ejecutiva"},{test_id:"RefranesICO",nombre:"Refranes INECO",dominio:"Función Ejecutiva"},{test_id:"StroopAM",nombre:"Stroop",dominio:"Función Ejecutiva"},{test_id:"GoNoGoICO",nombre:"Go No Go INECO",dominio:"Función Ejecutiva"}]},adulto_joven:{nombre:"Adulto Joven Batería",tests:[{test_id:"EscSTAI",nombre:"STAI",dominio:"Escalas"},{test_id:"AdBeck",nombre:"Beck",dominio:"Escalas"},{test_id:"EscASRS",nombre:"ASRS",dominio:"Escalas"},{test_id:"AdCVLT",nombre:"CVLT",dominio:"Memoria Verbal"},{test_id:"NiFCROCop",nombre:"FCRO Copia",dominio:"Praxias"},{test_id:"AdTMTA",nombre:"TMT-A",dominio:"Atención",has_timer:true,tiempo_max:300},{test_id:"AdTMTB",nombre:"TMT-B",dominio:"Atención",has_timer:true,tiempo_max:300},{test_id:"AdSDWais",nombre:"Claves WAIS-III",dominio:"Atención",has_timer:true,tiempo_max:120},{test_id:"AdDDir",nombre:"Dígitos WAIS-III",dominio:"Atención"},{test_id:"AdFCRO_Rey",nombre:"FCRO Recobro",dominio:"Memoria Visual"},{test_id:"FluidM",nombre:"Fluidez M",dominio:"Lenguaje"},{test_id:"FluidAnim",nombre:"Fluidez Animales",dominio:"Lenguaje"},{test_id:"BNT",nombre:"BNT",dominio:"Lenguaje"},{test_id:"AdSemWais",nombre:"Semejanzas WAIS-III",dominio:"Función Ejecutiva"},{test_id:"AdStroop_Corr",nombre:"Stroop",dominio:"Función Ejecutiva"},{test_id:"AdMatr",nombre:"Matrices",dominio:"Función Ejecutiva"}]}};
 const retentionScope=`${evalCtx?.evaluationId||evalCtx?.id||patId||"sin_paciente"}_${proto}`;
 /* §H5-fix: validar que el timestamp sea un entero plausible (epoch ms
  * desde 2020 hasta dentro de 1h en el futuro). Si storage está
  * corrupto, ignoramos el valor en lugar de propagar NaN. */
 const readRetentionTimes=()=>{if(typeof localStorage==="undefined")return{};const MIN_TS=1577836800000;/* 2020-01-01 */const MAX_TS=Date.now()+3600000;return tests.reduce((acc,x)=>{if(x.hito==="codificacion"){const raw=safeLS.get(getRetentionStorageKey(retentionScope,x.test_id));const ts=Number(raw);if(Number.isFinite(ts)&&ts>=MIN_TS&&ts<=MAX_TS)acc[x.test_id]=ts}return acc},{})};
 const[protoSug,setProtoSug]=useState(null);/* sugerencia por edad */
 const[estimulos,setEstimulos]=useState([]);/* estímulos de la prueba actual */
  useEffect(()=>{api.get("/api/v1/patients/panel").then(d=>setPatients(d.pacientes||d||[])).catch(()=>toast.error("Error cargando pacientes"))},[]);
 /* Auto-sugerir protocolo según edad del paciente seleccionado */
 useEffect(()=>{
 if(!patId||!patients.length){setProtoSug(null);return}
 const pat=patients.find(p=>p.id===patId);if(!pat||!pat.fecha_nacimiento){setProtoSug(null);return}
 const edad=Math.floor((Date.now()-new Date(pat.fecha_nacimiento).getTime())/(365.25*24*3600*1000));
 const sug=protocoloPorEdad(edad);
 if(!sug){setProtoSug(null);return}
 /* Mapear grupo etario → protocolo más cercano */
 const map={preescolar:"ninos_comp",infantil:"wisc_iv",adolescente:"wisc_iv",adulto_joven:"wais_iii",adulto_mayor:"adulto_mayor"};
 setProtoSug({edad,grupo:sug.key,nombre:sug.nombre,protocoloId:map[sug.key]||"wisc_iv",core:sug.core,tiempo_min:sug.tiempo_min,tiempo_max:sug.tiempo_max})
 },[patId,patients]);
 useEffect(()=>{
 /* Filtrar pruebas según adaptación (excluye las no aplicables) */
 const adapt=ADAPTATIONS[adaptacion]||ADAPTATIONS.estandar;
 const filtered=protos[proto].tests.filter(t=>!(adapt.excludes||[]).includes(t.test_id));
 setTests(prepareClinicalProtocolTests(filtered));
 setCur(0);setPuntajes({});setObs({});
 setDraftRestoredFrom(null);/* reset al cambiar protocolo */
 },[proto,adaptacion]);

 /* §autosave-1: restaurar borrador al seleccionar paciente o cambiar protocolo.
  * Si existe un draft válido para esta combinación (patId + proto), lo carga.
  * El draft expira a los 7 días para no contaminar evaluaciones futuras. */
 useEffect(()=>{
  if(!patId)return;
  try{
   const raw=localStorage.getItem(DRAFT_KEY(patId,proto));
   if(!raw)return;
   const d=JSON.parse(raw);
   const now=Date.now();
   if(!d.ts||(now-d.ts)>DRAFT_TTL_MS){
    localStorage.removeItem(DRAFT_KEY(patId,proto));
    return;
   }
   /* Solo restaurar si el draft tiene datos reales (al menos 1 PD o 1 obs). */
   const hasData=(d.puntajes&&Object.keys(d.puntajes).some(k=>d.puntajes[k]!==""&&d.puntajes[k]!=null))
              ||(d.obs&&Object.keys(d.obs).some(k=>d.obs[k]?.trim()));
   if(!hasData)return;
   /* Aplicar el borrador. */
   if(d.puntajes)setPuntajes(d.puntajes);
   if(d.obs)setObs(d.obs);
   if(typeof d.cur==="number")setCur(d.cur);
   if(d.conductas_checked)setConducChecked(d.conductas_checked);
   if(d.itemScores)setItemScores(d.itemScores);
   if(d.adaptacion&&d.adaptacion!==adaptacion)setAdaptacion(d.adaptacion);
   setDraftRestoredFrom(new Date(d.ts).toLocaleString("es-CO",{dateStyle:"short",timeStyle:"short"}));
  }catch(e){
   console.warn("[autosave] No se pudo restaurar borrador:",e);
  }
 /* Solo al montar / cambiar paciente o protocolo — NO en cada cambio de puntajes. */
 // eslint-disable-next-line react-hooks/exhaustive-deps
 },[patId,proto]);

 /* §autosave-2: persistir borrador cada 30 segundos si hay cambios sin finalizar. */
 useEffect(()=>{
  if(!patId)return;
  const save=()=>{
   try{
    const hasData=Object.keys(puntajes).some(k=>puntajes[k]!==""&&puntajes[k]!=null)
               ||Object.keys(obs).some(k=>obs[k]?.trim());
    if(!hasData)return;
    const draft={ts:Date.now(),patId,proto,adaptacion,cur,puntajes,obs,conductas_checked,itemScores};
    localStorage.setItem(DRAFT_KEY(patId,proto),JSON.stringify(draft));
    setDraftSavedAt(draft.ts);
   }catch(e){
    /* localStorage puede estar lleno o deshabilitado — no es bloqueante. */
    console.warn("[autosave] No se pudo guardar borrador:",e);
   }
  };
  /* Guardado debounced: 1 segundo después del último cambio + cada 30 segundos. */
  const debounce=setTimeout(save,1000);
  const interval=setInterval(save,30000);
  return()=>{clearTimeout(debounce);clearInterval(interval)};
 },[patId,proto,adaptacion,cur,puntajes,obs,conductas_checked,itemScores]);

 /* §autosave-3: protección "cambios sin guardar" al cerrar / recargar la pestaña.
  * El navegador muestra el diálogo nativo "¿Salir? Es posible que los cambios no se guarden". */
 useEffect(()=>{
  const hasUnsaved=Object.keys(puntajes).some(k=>puntajes[k]!==""&&puntajes[k]!=null)
                ||Object.keys(obs).some(k=>obs[k]?.trim());
  if(!hasUnsaved)return;
  const handler=(e)=>{e.preventDefault();e.returnValue="";return""};
  window.addEventListener("beforeunload",handler);
  return()=>window.removeEventListener("beforeunload",handler);
 },[puntajes,obs]);
 /* Cargar estímulos de la prueba actual */
 useEffect(()=>{const curTest=tests[cur];if(!curTest){setEstimulos([]);return}const tid=curTest.test_id.split(" ")[0].trim();api.get(`/api/v1/estimulos/por_test/${encodeURIComponent(tid)}`).then(d=>setEstimulos(d||[])).catch(()=>setEstimulos([]))},[cur,tests]);
 useEffect(()=>{if(timerOn)ref.current=setInterval(()=>setTimer(t=>t+1),1000);else clearInterval(ref.current);return()=>clearInterval(ref.current)},[timerOn]);
 /* §clock-beep: sonar UNA vez al cumplirse exactamente el tiempo máximo.
  * Usa WebAudio API (no requiere ningún archivo de audio bundled). */
 useEffect(()=>{const curT=tests[cur];if(!curT?.tiempo_max)return;if(timer!==curT.tiempo_max)return;try{const Ctx=window.AudioContext||window.webkitAudioContext;if(!Ctx)return;const ctx=new Ctx();const osc=ctx.createOscillator();const gain=ctx.createGain();osc.frequency.value=880;osc.type="sine";gain.gain.setValueAtTime(0.0001,ctx.currentTime);gain.gain.exponentialRampToValueAtTime(0.18,ctx.currentTime+0.02);gain.gain.exponentialRampToValueAtTime(0.0001,ctx.currentTime+0.45);osc.connect(gain);gain.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+0.5)}catch(e){/* ignore audio errors */}},[timer,cur,tests]);
 /* §clock-space: Espacio inicia/pausa el cronómetro cuando NO se está
  * editando un input/textarea (no robar foco al clínico que escribe PD). */
 useEffect(()=>{const handler=(e)=>{if(e.code!=="Space")return;const tag=(e.target?.tagName||"").toLowerCase();if(tag==="input"||tag==="textarea"||tag==="select")return;const curT=tests[cur];if(!curT?.has_timer)return;e.preventDefault();setTimerOn(o=>!o)};window.addEventListener("keydown",handler);return()=>window.removeEventListener("keydown",handler)},[cur,tests]);
 useEffect(()=>{const id=setInterval(()=>setRetentionTick(Date.now()),1000);return()=>clearInterval(id)},[]);
 /* §M6-fix: NO borrar el timestamp cuando un PD pasa de tener valor a
  * vacío. Si el clínico corrige por error y borra el PD, antes se
  * reiniciaba el intervalo de recobro diferido (invalidación silente
  * clínica). Solo establecemos el timestamp; nunca lo eliminamos
  * desde aquí (solo el reset explícito del clínico debería). */
 useEffect(()=>{if(typeof localStorage==="undefined")return;tests.forEach(x=>{if(x.hito!=="codificacion")return;const key=getRetentionStorageKey(retentionScope,x.test_id);if(isClinicalTestDone(x,puntajes)){if(!localStorage.getItem(key))localStorage.setItem(key,String(Date.now()))}});setRetentionTick(Date.now())},[puntajes,tests,retentionScope]);
 const fmt=s=>`${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`;
 const t=tests[cur];const done=Object.keys(puntajes).filter(k=>puntajes[k]!=="");
 const dc=d=>({"Comprensión Verbal":"#0D9488","Razonamiento Perceptual":"#006a6a","Memoria de Trabajo":"#943700","Velocidad de Proceso":"#7d2d00","Organización Perceptual":"#006a6a","Velocidad de Procesamiento":"#7d2d00","Memoria Verbal":"#006a6a","Praxias":"#943700","Praxias/Gnosias":"#943700","Atención":"#7d2d00","Memoria Visual":"#006a6a","Lenguaje":"#0D9488","Lectura":"#0D9488","Escritura":"#0D9488","Matemáticas":"#943700","Función Ejecutiva":"#534AB7","Escalas":"#888780","Orientación":"#888780"}[d]||"#0D9488");
 const cond=t?CONDUCTAS[t.test_id]||[]:[];
 const retentionTimes=readRetentionTimes();
 /* §clinical-next — pasamos `cur` para que el helper EXCLUYA la prueba
  * actual de las sugerencias. Sin esto, si la prueba en pantalla aún
  * no tiene PD, se sugiere ella misma y "Ir a esta" no hace nada. */
 const suggested=getSuggestedClinicalTest(tests,puntajes,retentionTimes,retentionTick,cur);
 const currentRetention=getRetentionStatus(t,tests,retentionTimes,retentionTick);
 /* Solo mostrar el banner naranja cuando la codificación YA fue iniciada
 * pero aún no transcurre el intervalo mínimo. Si la codificación nunca
 * se ha aplicado (missingCodificacion), no es un "recobro en espera"
 * sino simplemente que aún no se hizo la codificación → la sugerencia
 * de "Siguiente prueba" ya guía al clínico hacia la codificación. */
 const waitingRecobro=tests.map((x,i)=>({test:x,index:i,status:getRetentionStatus(x,tests,retentionTimes,retentionTick)})).find(({test,status})=>test.hito==="recobro"&&!isClinicalTestDone(test,puntajes)&&status.isBlocked&&!status.missingCodificacion);
 /* fillerSuggestion: prueba "rellena-tiempo" mientras esperamos el
  * intervalo del recobro. EXCLUIMOS la actual (cur) para no sugerir
  * la misma en la que ya estamos. */
 const fillerSuggestion=waitingRecobro?tests.find((x,i)=>i!==cur&&x.test_id!==waitingRecobro.test.test_id&&x.hito!=="recobro"&&!isClinicalTestDone(x,puntajes)):null;
 const goToTest=i=>{setCur(i);setTimer(0);setTimerOn(false)};
 /* §4.2 — checkbox de conducta: ahora con detalle observado opcional.
  * §conductas-rework (2026-05-18): antes los bullets se copiaban literal
  * y eran genéricos — el clínico se quejaba (con razón) de que no
  * aportaban valor. Ahora cada conducta marcada puede llevar un detalle
  * libre que el clínico escribe (lo observado en este paciente). El
  * bloque generado incluye el detalle si existe, o solo el bullet si no.
  *
  * Formato interno:
  *   conductas_checked[tid] = [ { idx, detail } ]  (orden de marcado preservado)
  * Drafts viejos con [int, int, int] se migran transparentemente. */
 const _normalizeConducta=(arr)=>(arr||[]).map(x=>typeof x==="number"?{idx:x,detail:""}:x);
 const _recompileObs=(tid,items,condList)=>{
  const lines=items.map(it=>{
   const base=condList[it.idx]||"";
   const d=(it.detail||"").trim();
   return d?`• ${base.split(":")[0]}: ${d}`:`• ${base}`;
  });
  const block=lines.length>0?`[Conductas observadas]\n${lines.join("\n")}`:"";
  setObs(o=>{
   const old=o[tid]||"";
   if(!old||old.startsWith("[Conductas observadas]"))return{...o,[tid]:block};
   if(!old.includes("[Conductas observadas]"))return{...o,[tid]:old+(block?"\n\n"+block:"")};
   const before=old.substring(0,old.indexOf("[Conductas observadas]")).trimEnd();
   return{...o,[tid]:before+(block?"\n\n"+block:"")};
  });
 };
 const handleConducCheck=(tid,idx,chk,condList)=>{
  setConducChecked(prev=>{
   const current=_normalizeConducta(prev[tid]);
   let next;
   if(chk){
    if(current.some(x=>x.idx===idx))next=current;
    else next=[...current,{idx,detail:""}];
   }else{
    next=current.filter(x=>x.idx!==idx);
   }
   _recompileObs(tid,next,condList);
   return{...prev,[tid]:next};
  });
 };
 const handleConducDetail=(tid,idx,detail,condList)=>{
  setConducChecked(prev=>{
   const current=_normalizeConducta(prev[tid]);
   const next=current.map(x=>x.idx===idx?{...x,detail}:x);
   _recompileObs(tid,next,condList);
   return{...prev,[tid]:next};
  });
 };
 const isConducChecked=(tid,idx)=>_normalizeConducta(conductas_checked[tid]).some(x=>x.idx===idx);
 const getConducDetail=(tid,idx)=>{
  const item=_normalizeConducta(conductas_checked[tid]).find(x=>x.idx===idx);
  return item?.detail||"";
 };
 const getConducCount=(tid)=>_normalizeConducta(conductas_checked[tid]).length;
 const handleFinalizar=()=>{
  if(!patId){toast.warn("Seleccione un paciente antes de finalizar");return}
  const pd={};tests.forEach(x=>{const v=puntajes[x.test_id];pd[x.test_id]=v!=null&&v!==""?parseFloat(v):9999});
  /* §autosave-clean: borrador completado → eliminar del localStorage. */
  try{localStorage.removeItem(DRAFT_KEY(patId,proto))}catch{}
  nav("eval_results",{patientId:patId,puntajes:pd,obs,proto,protoNombre:protos[proto].nombre});
 };
 /* §autosave-discard: limpiar el borrador manualmente desde el banner. */
 const discardDraft=async()=>{
  if(!(await confirm({
    title:"Descartar borrador",
    message:"Se perderán todos los puntajes y observaciones no guardados.\nEsta acción no se puede deshacer.",
    confirmText:"Descartar",
    dangerous:true,
  })))return;
  try{localStorage.removeItem(DRAFT_KEY(patId,proto))}catch{}
  setPuntajes({});setObs({});setCur(0);setConducChecked({});setItemScores({});
  setDraftRestoredFrom(null);setDraftSavedAt(null);
 };
 if(!t)return<><TopBar title="Evaluación"/><main className="p-8 flex items-center justify-center h-96"><div className="animate-spin w-8 h-8 border-4 border-teal-200 border-t-teal-600 rounded-full"/></main></>;
 return(<><TopBar title="Evaluación Neuropsicológica">
 {/* Solo controles esenciales en el TopBar para evitar desbordes
 * cuando el sidebar está expandido. El selector de modo y la barra
 * de progreso bajan a un sub-header dedicado. */}
 <Sel value={patId} onChange={e=>setPatId(e.target.value)} className="text-xs w-44 sm:w-52">{!patId&&<option value="">— Paciente —</option>}{patients.map(p=><option key={p.id} value={p.id}>{p.nombre_completo||`${p.primer_nombre} ${p.primer_apellido}`}</option>)}</Sel>
 <Sel value={proto} onChange={e=>{setProto(e.target.value)}} className="text-xs w-28 sm:w-32">{Object.entries(protos).map(([k,v])=><option key={k} value={k}>{v.nombre}</option>)}</Sel>
 <Sel value={adaptacion} onChange={e=>setAdaptacion(e.target.value)} className="text-xs w-32 sm:w-40" title="Adaptación para casos especiales (Protocolos Alternos )">{Object.entries(ADAPTATIONS).map(([k,v])=><option key={k} value={k}>{v.label}</option>)}</Sel>
 <Btn v="danger" className="text-xs whitespace-nowrap" onClick={handleFinalizar}>Finalizar</Btn>
 </TopBar>
 {/* Sub-header: modo de aplicación + progreso */}
 <div className="px-6 sm:px-8 py-3 border-b flex flex-wrap items-center gap-4" style={{background:"var(--ns-card)",borderColor:"var(--ns-card-b)"}}>
 <div className="flex rounded-full overflow-hidden border shrink-0" style={{borderColor:"#d4d2ce"}}>
 <button onClick={()=>setMode("apply")} className={`px-4 py-1.5 text-xs font-bold transition-all whitespace-nowrap ${mode==="apply"?"bg-teal-600 text-white":"bg-transparent text-gray-500"}`}><I name="touch_app" className="text-sm mr-1"/>Aplicación</button>
 <button onClick={()=>setMode("table")} className={`px-4 py-1.5 text-xs font-bold transition-all whitespace-nowrap ${mode==="table"?"bg-teal-600 text-white":"bg-transparent text-gray-500"}`}><I name="table_chart" className="text-sm mr-1"/>Registro</button>
 </div>
 <div className="flex items-center gap-3 flex-1 min-w-[200px]">
  <span className="text-xs font-bold text-gray-400 whitespace-nowrap">Progreso: {done.length}/{tests.length}</span>
  <div className="flex-1 max-w-xs h-1.5 bg-gray-200 rounded-full overflow-hidden">
  <div className="h-full bg-teal-600 rounded-full transition-all" style={{width:`${tests.length?(done.length/tests.length)*100:0}%`}}/>
  </div>
  </div>
 {suggested&&<div data-testid="clinical-next" className="flex items-center gap-2 rounded-2xl px-3 py-2 border min-w-[260px] max-w-full" style={{borderColor:suggested.status.isBlocked?"#fed7aa":"#ccfbf1",background:suggested.status.isBlocked?"#fff7ed":"#f0fdfa"}}>
 <I name={suggested.status.isBlocked?"hourglass_top":"near_me"} className={`text-base ${suggested.status.isBlocked?"text-orange-500":"text-teal-600"}`}/>
 <div className="min-w-0">
  <p className="text-[10px] font-extrabold uppercase tracking-wider text-gray-400">Siguiente prueba sugerida</p>
  <p data-testid="clinical-next-name" className="text-sm font-bold truncate" style={{color:suggested.status.isBlocked?"#c2410c":TEAL}}>{suggested.test.nombre}</p>
 </div>
 {suggested.test.hito&&<span className="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-white/80 text-gray-500 shrink-0">{HITO_LABELS[suggested.test.hito]||suggested.test.hito}</span>}
 <button data-testid="clinical-next-go" disabled={suggested.status.isBlocked} title={suggested.status.isBlocked?"Recobro pendiente: intervalo mínimo aún no cumplido":"Ir a esta prueba"} onClick={()=>goToTest(suggested.index)} className={`ml-auto px-3 py-1.5 rounded-full text-[10px] font-bold shrink-0 ${suggested.status.isBlocked?"bg-gray-200 text-gray-400 cursor-not-allowed":"bg-teal-600 text-white hover:bg-teal-700"}`}>Ir a esta</button>
 </div>}
 </div>
 {/* §autosave: banner de borrador restaurado o indicador "guardado". */}
 {(draftRestoredFrom||draftSavedAt)&&(
   <div className="px-6 sm:px-8 py-2 border-b flex items-center gap-3 text-xs"
        style={{background:draftRestoredFrom?"rgba(13,148,136,0.08)":"var(--ns-subtle)",borderColor:"var(--ns-card-b)",color:"var(--ns-muted)"}}>
     {draftRestoredFrom?(
       <>
         <I name="restore" className="text-base" style={{color:TEAL}}/>
         <span><strong style={{color:TEAL}}>Borrador restaurado</strong> · guardado el {draftRestoredFrom}. Continúa donde lo dejaste o descártalo para empezar de cero.</span>
         <button onClick={discardDraft} className="ml-auto px-3 py-1 rounded-lg font-bold hover:bg-red-50 text-red-600 transition-all" aria-label="Descartar borrador">Descartar borrador</button>
       </>
     ):(
       <>
         <I name="cloud_done" className="text-base" style={{color:"#10b981"}}/>
         <span>Guardado automático activo · último guardado hace {Math.max(0,Math.floor((Date.now()-draftSavedAt)/1000))}s.</span>
       </>
     )}
   </div>
 )}
 {/* ─── Banner de adaptación activa (Protocolos Alternos ) ─── */}
 {adaptacion!=="estandar"&&(()=>{const adapt=ADAPTATIONS[adaptacion];const fc=adapt.forma_corta?SATTLER_FORMS[adapt.forma_corta]:null;
 /* Si hay forma corta y todos sus subtests tienen PE, calculamos CIT estimado */
 let citEstimado=null;
 if(fc){
 const escalares=fc.subtests.map(s=>parseFloat(puntajes[s.id])).filter(Number.isFinite);
 if(escalares.length===fc.subtests.length){
 const sum=escalares.reduce((a,b)=>a+b,0);
 citEstimado=estimateCITFromShortForm(sum,adapt.forma_corta);
 }
 }
 return(<div className="px-6 pt-4"><Card className="p-4 border-l-4 flex flex-wrap items-start gap-3" style={{borderColor:"#7c3aed",background:"rgba(124,58,237,0.06)"}}>{/* §dark-mode-fix */}
 <I name="accessibility_new" className="text-xl text-purple-600 mt-0.5"/>
 <div className="flex-1 min-w-[280px]">
 <p className="text-sm font-bold text-purple-700">Adaptación activa: {adapt.label}</p>
 <p className="text-xs text-purple-700/80 mt-1">{adapt.description}</p>
 {fc&&<p className="text-[10px] mt-2" style={{color:"var(--ns-muted)"}}>
 <b>{fc.name}</b> ({fc.abbr}) — Subtests: {fc.subtests.map(s=>s.label).join(", ")}.
 Citar Sattler (2010) en el informe.
 </p>}
 {(adapt.excludes||[]).length>0&&<p className="text-[10px] mt-1" style={{color:"var(--ns-muted)"}}>{adapt.excludes.length} prueba(s) excluida(s) automáticamente del protocolo.</p>}
 </div>
 {citEstimado!=null&&<div className="text-center px-4">
 <p className="text-[10px] font-extrabold uppercase tracking-wider text-purple-600">CIT estimado (Sattler)</p>
 <p className="text-3xl font-extrabold text-purple-700">{citEstimado}</p>
 <p className="text-[10px] text-purple-600">{fc.abbr}</p>
 </div>}
 </Card></div>);})()}
 {/* ─── Sugerencia de protocolo por edad ─── */}
 {protoSug&&protoSug.protocoloId!==proto&&<div className="px-6 pt-4"><Card className="p-4 border-l-4 flex items-center justify-between" style={{borderColor:TEAL,background:`${TEAL}10`}}>
 <div className="flex items-start gap-3"><I name="auto_awesome" fill style={{color:TEAL}} className="text-xl mt-0.5"/>
 <div><p className="text-sm font-bold" style={{color:TEAL}}>Sugerencia automática según edad ({protoSug.edad} años → {protoSug.nombre})</p>
 <p className="text-xs mt-0.5" style={{color:"var(--ns-muted)"}}>Protocolo recomendado: <strong>{protos[protoSug.protocoloId]?.nombre||protoSug.protocoloId}</strong> · Tiempo estimado {protoSug.tiempo_min}-{protoSug.tiempo_max} min · Core: {protoSug.core.slice(0,4).join(" · ")}{protoSug.core.length>4?"…":""}</p>
 </div>
 </div>
 <div className="flex gap-2">
 <button onClick={()=>setProtoSug(null)} className="px-3 py-1.5 rounded-full text-xs font-bold text-gray-500 hover:bg-white">Descartar</button>
 <Btn onClick={()=>setProto(protoSug.protocoloId)} className="text-xs">Aplicar sugerencia</Btn>
 </div>
 </Card></div>}
 {waitingRecobro&&<div className="px-6 pt-4"><Card className="p-4 border-l-4 flex flex-wrap items-center gap-3" style={{borderColor:"#f97316",background:"rgba(249,115,22,0.08)"}}>
 <I name="timer" className="text-orange-500 text-xl"/>
 <div className="flex-1 min-w-[240px]">
 <p className="text-sm font-bold text-orange-700">{waitingRecobro.status.missingCodificacion?`Complete primero ${waitingRecobro.status.codificacion?.nombre||"la codificacion"}`:`Faltan ${formatRetentionRemaining(waitingRecobro.status.remainingMs)} para aplicar ${waitingRecobro.test.nombre}`}</p>
 <p className="text-xs text-orange-700/80">Hasta entonces, se sugiere completar {fillerSuggestion?.nombre||"otra prueba de atencion o funcion ejecutiva"}.</p>
 </div>
 {fillerSuggestion&&<button onClick={()=>goToTest(tests.findIndex(x=>x.test_id===fillerSuggestion.test_id))} className="px-3 py-1.5 rounded-full text-xs font-bold bg-white text-orange-700 hover:bg-orange-50">Ir a sugerida</button>}
 </Card></div>}
 <main className="p-6"><div className="flex flex-col xl:flex-row gap-6 max-w-screen-2xl mx-auto">
 {/* === MODO APLICACIÓN === */}
 {mode==="apply"&&<><div className="flex-1 min-w-0 space-y-4">
 {/* El banner por prueba actual sólo aplica si la codificación ya
 * fue iniciada (interval timer activo). Si nunca se hizo, mostrar
 * un mensaje suave informativo en vez del banner alarmista. */}
 {currentRetention.isBlocked&&!currentRetention.missingCodificacion&&<Card className="p-4 border-l-4 flex flex-wrap items-center gap-3" style={{borderColor:"#f97316",background:"rgba(249,115,22,0.08)"}}>
 <I name="hourglass_top" className="text-orange-500 text-xl"/>
 <div className="flex-1 min-w-[220px]">
 <p className="text-sm font-bold text-orange-700">Recobro en espera: faltan {formatRetentionRemaining(currentRetention.remainingMs)}</p>
 <p className="text-xs text-orange-700/80">El intervalo mínimo protege la validez del recobro diferido.</p>
 </div>
 <button disabled title="Recobro pendiententervalo mínimo" className="px-3 py-1.5 rounded-full text-xs font-bold bg-gray-200 text-gray-400 cursor-not-allowed">Aplicar recobro</button>
 </Card>}
 {currentRetention.isBlocked&&currentRetention.missingCodificacion&&<Card className="p-3 flex flex-wrap items-center gap-3" style={{background:"var(--ns-subtle)"}}>
 <I name="info" className="text-base" style={{color:TEAL}}/>
 <p className="text-xs flex-1" style={{color:"var(--ns-muted)"}}>Esta es una prueba de recobro. Aplique primero <b>{currentRetention.codificacion?.nombre||"la codificación"}</b> para iniciar el intervalo de retención.</p>
 </Card>}
 {/* ── Header: nombre prueba + cronómetro inline + PD ── */}
  <Card className="p-5">
  <div className="flex items-start gap-4">
  <div className="flex-1 min-w-0">
  <div className="flex items-center gap-2 mb-1 flex-wrap">
    <span className="text-xs font-extrabold uppercase tracking-widest px-3 py-1 rounded-full" style={{background:`${dc(t.dominio)}15`,color:dc(t.dominio)}}>{t.dominio}</span>
    {t.es_suplementaria&&<span className="text-xs font-bold uppercase tracking-widest px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">Suplementaria</span>}
    {(()=>{const nn=getNeuronormaInfo(t.test_id);return nn?(
      <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full flex items-center gap-1" style={{background:"linear-gradient(135deg,#fde047,#fb923c)",color:"#7c2d12"}}
        title={`Norma colombiana disponible (${NEURONORMA_COLOMBIA_REF.citaCorta}, cap. ${nn.capitulo}). Ajuste: edad + escolaridad.`}>
        Norma Colombia
      </span>
    ):null})()}
  </div>
  <h1 className="text-2xl font-extrabold tracking-tight mb-1">{t.nombre}</h1>
  {t.has_timer&&<span className="text-xs" style={{color:"var(--ns-muted)"}}>Tiempo maximo: {t.tiempo_max||"—"}s · {t.hito?HITO_LABELS[t.hito]||t.hito:""}</span>}
  {t.has_timer&&(()=>{const st=getSubtest(t.test_id);if(!st?.items)return null;const times=[...new Set(st.items.map(i=>i.tiempo_seg).filter(Boolean))];return times.length?<span className="text-xs mt-0.5 font-semibold" style={{color:"#d97706"}}>Por item: {times.map(t=>t+"s").join(" · ")}</span>:null})()}
  </div>
  {/* Cronometro responsive: escala con el ancho disponible */}
  <div className="shrink-0" style={{minWidth:100,minHeight:t.has_timer?100:0}}>
  {t.has_timer&&(()=>{
    const max=t.tiempo_max||300;
    const pct=Math.min(timer/max,1);
    const remaining=Math.max(0,max-timer);
    const over=timer>max;
    const warning=!over&&pct>=0.85;
    const ringColor=over?"#ef4444":warning?"#f59e0b":"#2dd4bf";
    const size=120;
    const R=52;
    const C=2*Math.PI*R;
    const circleSize={width:`clamp(100px,12vw,${size}px)`,height:`clamp(100px,12vw,${size}px)`};
    return(<div className={`flex items-center gap-3 xl:gap-5 px-4 xl:px-6 py-4 rounded-2xl shrink-0 ${over?"ns-pulse-red":""}`}
      style={{background:over?"linear-gradient(135deg,#7f1d1d,#1e293b)":"linear-gradient(135deg,#0f2a3d,#1e293b)",boxShadow:over?"0 0 60px -12px #ef4444":"0 8px 24px -8px rgba(13,148,136,0.4)"}}>
      <div className="relative flex items-center justify-center shrink-0" style={circleSize}>
        <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 120 120">
          <defs>
            <linearGradient id="ns-clk-grad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor={ringColor}/>
              <stop offset="100%" stopColor={ringColor} stopOpacity="0.5"/>
            </linearGradient>
          </defs>
          <circle cx="60" cy="60" r={R} fill="transparent" stroke="#1e3a4d" strokeWidth="7"/>
          <circle cx="60" cy="60" r={R} fill="transparent"
            stroke="url(#ns-clk-grad)" strokeWidth="7"
            strokeDasharray={`${pct*C} ${C}`}
            strokeLinecap="round"
            style={{transition:"stroke-dasharray 0.4s ease-out, stroke 0.3s"}}/>
        </svg>
        <div className="flex flex-col items-center pointer-events-none">
          <span className="text-xl xl:text-2xl font-mono font-extrabold text-white tabular-nums leading-none">{fmt(timer)}</span>
          {t.tiempo_max&&<span className="text-[10px] mt-1 font-mono" style={{color:over?"#fca5a5":"#94a3b8"}}>
            {over?"+"+fmt(timer-max):fmt(remaining)}
          </span>}
        </div>
      </div>
      <div className="flex flex-col items-stretch gap-2">
        <div className="flex gap-1.5 xl:gap-2">
          <button onClick={()=>setTimerOn(true)} disabled={timerOn} className="w-9 h-9 xl:w-11 xl:h-11 rounded-xl bg-teal-600 text-white flex items-center justify-center active:scale-90 hover:bg-teal-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg shadow-teal-900/30" title="Iniciar (Espacio)" aria-label="Iniciar cronometro"><I name="play_arrow" fill className="text-lg xl:text-xl"/></button>
          <button onClick={()=>setTimerOn(false)} disabled={!timerOn} className="w-9 h-9 xl:w-11 xl:h-11 rounded-xl bg-amber-500 text-white flex items-center justify-center active:scale-90 hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg shadow-amber-900/30" title="Pausa" aria-label="Pausar cronometro"><I name="pause" fill className="text-lg xl:text-xl"/></button>
          <button onClick={()=>{setTimerOn(false);setTimer(0)}} className="w-9 h-9 xl:w-11 xl:h-11 rounded-xl bg-slate-600 text-white flex items-center justify-center active:scale-90 hover:bg-slate-500 transition-all" title="Reiniciar" aria-label="Reiniciar cronometro a cero"><I name="restart_alt" className="text-lg xl:text-xl"/></button>
        </div>
        <span className={`text-[9px] xl:text-[10px] font-bold uppercase tracking-widest text-center px-1.5 xl:px-2 py-1 rounded-lg ${over?"bg-red-500/20 text-red-200":warning?"bg-amber-500/20 text-amber-200":timerOn?"bg-teal-500/20 text-teal-200":"bg-slate-500/20 text-slate-300"}`}>
          {over?"TIEMPO EXCEDIDO":warning?"Casi se acaba":timerOn?"Grabando":"En pausa"}
        </span>
      </div>
    </div>);
  })()}
  </div>
  {/* PD compacto con validacion visual */}
  <div className="flex items-center gap-2 shrink-0">
  <span className="text-xs font-bold uppercase tracking-wider text-gray-400">PD</span>
  <ScoreInput
    testId={t.test_id}
    value={puntajes[t.test_id]||""}
    onChange={e=>setPuntajes(p=>({...p,[t.test_id]:e.target.value}))}
  />
  </div>
 </div>
 </Card>

 {/* §M-6 ── Banner de orden clínico + timer de recobro ── */}
 <OrdenClinicoBanner testIdActual={t.test_id.split(" ")[0].trim()} completados={retentionTimes} />

 {/* ── Estímulos de la prueba ── */}
 {estimulos.length>0&&<Card className="p-5"><StimulusDisplay testId={t.test_id.split(" ")[0].trim()} stimuli={estimulos}/></Card>}

 {/* ── REACTIVOS — ahora en el área principal ── */}
 {REACTIVOS[t.test_id]&&<ReactivePanel testId={t.test_id} puntajes={puntajes} setPuntajes={setPuntajes} itemScores={itemScores} setItemScores={setItemScores}/>}

 {/* ── Instrucciones de administración (colapsable) ── */}
 {INSTRUCCIONES[t.test_id]&&<Card className="p-5 space-y-3 border-l-4 border-teal-400">
 <details open={!REACTIVOS[t.test_id]}>
 <summary className="flex items-center gap-2 cursor-pointer select-none"><I name="menu_book" className="text-teal-600 text-lg"/><h3 className="font-bold text-sm text-teal-800">Administración y Tips</h3></summary>
 <div className="space-y-2.5 mt-3">
  <div><p className="text-[10px] font-extrabold text-gray-500 uppercase tracking-wider mb-1"><I name="inventory_2" className="text-[10px] mr-0.5"/>Materiales</p><p className="text-xs text-gray-700 leading-snug">{INSTRUCCIONES[t.test_id].mat}</p></div>
  <div><p className="text-[10px] font-extrabold text-teal-600 uppercase tracking-wider mb-1"><I name="play_circle" className="text-[10px] mr-0.5"/>Instrucción</p><p className="text-xs text-gray-700 leading-snug">{INSTRUCCIONES[t.test_id].inst}</p></div>
  <div><p className="text-[10px] font-extrabold text-red-600 uppercase tracking-wider mb-1"><I name="block" className="text-[10px] mr-0.5"/>Discontinuación</p><p className="text-xs text-gray-700 leading-snug">{INSTRUCCIONES[t.test_id].disc}</p></div>
  <div><p className="text-[10px] font-extrabold text-teal-600 uppercase tracking-wider mb-1"><I name="lightbulb" className="text-[10px] mr-0.5"/>Tips Clínicos</p><p className="text-xs text-gray-700 leading-snug">{INSTRUCCIONES[t.test_id].tip}</p></div>
  <div className="pt-2 border-t border-gray-100"><p className="text-[10px] font-extrabold text-purple-600 uppercase tracking-wider mb-1"><I name="calculate" className="text-[10px] mr-0.5"/>Calificación</p><p className="text-xs text-gray-700 font-semibold">{INSTRUCCIONES[t.test_id].puntaje}</p></div>
 </div>
 </details>
 </Card>}

 {/* Footer navegación */}
 <Card className="p-4">
 <div className="flex items-center justify-between">
  <button onClick={()=>{setCur(c=>Math.max(0,c-1));setTimer(0);setTimerOn(false)}} className="flex items-center gap-2 text-gray-400 hover:text-teal-600 font-bold text-base"><I name="chevron_left"/>Anterior</button>
  <span className="text-sm font-bold px-4 py-1.5 rounded-full" style={{background:"var(--ns-subtle)"}}>Prueba {cur+1} de {tests.length}</span>
  {cur<tests.length-1?<button onClick={()=>{setCur(c=>c+1);setTimer(0);setTimerOn(false)}} className="flex items-center gap-2 text-teal-600 font-bold text-base hover:translate-x-1 transition-all">Siguiente<I name="chevron_right"/></button>:<Btn onClick={handleFinalizar}>Ver Resultados</Btn>}
 </div>
 </Card>
 </div>
 {/* ── SIDEBAR DERECHO: Observaciones + Conductas + Navegador ── */}
 <div className="w-full xl:w-[26rem] xl:shrink-0 space-y-4 xl:sticky xl:top-4 xl:max-h-[calc(100vh-100px)] overflow-y-auto pr-1">
 {/* Observaciones clínicas — rediseñado para mejor UX */}
 <Card className="p-5 space-y-3">
 <div className="flex items-center justify-between">
   <h3 className="font-bold text-sm flex items-center gap-2"><I name="edit_note" fill style={{color:TEAL}}/>Observaciones</h3>
   <span className="text-[9px] font-extrabold uppercase tracking-widest px-2 py-0.5 rounded-full" style={{background:`${TEAL}15`,color:TEAL}}>Clínico</span>
 </div>
 <Txta value={obs[t.test_id]||""} onChange={e=>setObs(o=>({...o,[t.test_id]:e.target.value}))} placeholder="Actitud, colaboración, estrategias, conducta durante la prueba…" className="min-h-[120px] text-sm"/>
 {/* ─── Conductas a Observar — REDISEÑADO ─────────────────────
    * Antes era un checklist plano poco visible. Ahora muestra:
    * • header con contador visual y leyenda explicativa
    * • estado vacío informativo
    * • check cards con animación al marcar
    * • botón "Limpiar" si hay marcadas
    * • info de que se auto-añade al campo Observaciones */}
 {cond.length>0?(
   <div className="pt-3 border-t" style={{borderColor:"var(--ns-card-b)"}}>
     <div className="flex items-center gap-2 mb-2">
       <I name="checklist" fill className="text-sm" style={{color:"#d97706"}}/>
       <p className="text-[10px] font-extrabold uppercase tracking-wider flex-1" style={{color:"#92400e"}}>Conductas a observar</p>
       {getConducCount(t.test_id)>0&&(
         <button onClick={()=>{setConducChecked(p=>({...p,[t.test_id]:[]}));setObs(o=>{const old=o[t.test_id]||"";if(!old.includes("[Conductas observadas]"))return o;return{...o,[t.test_id]:old.substring(0,old.indexOf("[Conductas observadas]")).trimEnd()}})}}
           className="text-[9px] font-bold px-2 py-0.5 rounded-full hover:bg-amber-50 transition-all" style={{color:"#92400e"}}
           title="Desmarcar todas">
           <I name="close" className="text-[10px] mr-0.5"/>Limpiar
         </button>
       )}
       <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full" style={{background:getConducCount(t.test_id)>0?"#fef3c7":"var(--ns-subtle)",color:getConducCount(t.test_id)>0?"#92400e":"var(--ns-muted)"}}>
         {getConducCount(t.test_id)}/{cond.length}
       </span>
     </div>
     <p className="text-[10px] mb-2 italic leading-snug" style={{color:"var(--ns-muted)"}}>
       <b>Cómo usar:</b> marca la conducta cuando la observes y opcionalmente escribe el <i>detalle específico</i> que viste en este paciente. Ej. "se rinde antes del ítem 3", "rota la cabeza al rotar el cubo", "tiembla la mano al firmar". Eso es lo que va al informe — no el texto genérico.
     </p>
     <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
       {cond.map((c,i)=>{
         const chk=isConducChecked(t.test_id,i);
         const det=getConducDetail(t.test_id,i);
         return(<div key={i}
           className={`p-2 rounded-lg transition-all ${chk?"":""}`}
           style={chk?{background:"rgba(251,191,36,0.12)",borderLeft:"3px solid #d97706"}:{}}>
           <label className="flex items-start gap-2 cursor-pointer">
             <input type="checkbox" checked={chk}
               onChange={e=>handleConducCheck(t.test_id,i,e.target.checked,cond)}
               className="mt-0.5 shrink-0 w-3.5 h-3.5 accent-amber-500"/>
             <span className={`text-[11px] leading-snug select-none transition-colors ${chk?"font-semibold":""}`}
               style={chk?{color:"#92400e"}:{color:"var(--ns-muted)"}}>
               {c}
             </span>
           </label>
           {chk&&(
             <div className="mt-1.5 ml-5">
               <input
                 type="text"
                 value={det}
                 onChange={e=>handleConducDetail(t.test_id,i,e.target.value,cond)}
                 placeholder="¿Qué observaste específicamente? (opcional pero recomendado)"
                 className="w-full px-2 py-1 rounded text-[11px] border"
                 style={{background:"var(--ns-input)",borderColor:"#d97706",color:"var(--ns-text)"}}
               />
             </div>
           )}
         </div>);
       })}
     </div>
   </div>
 ):(
   <div className="pt-3 border-t flex items-center gap-2 text-[10px]" style={{borderColor:"var(--ns-card-b)",color:"var(--ns-muted)"}}>
     <I name="info" className="text-sm opacity-60"/>
     <span>Esta prueba no tiene lista de conductas predefinidas. Redacta libremente en el campo superior.</span>
   </div>
 )}
 </Card>
 {/* Navegador de pruebas */}
 <Card className="overflow-hidden flex flex-col" style={{maxHeight:"380px"}}><div className="p-4 border-b border-gray-100"><h3 className="font-bold text-sm flex items-center gap-2"><I name="list_alt" style={{color:TEAL}}/>Navegador</h3></div>
  <div className="flex-1 overflow-y-auto p-1.5 space-y-0.5">{tests.map((x,i)=>{const dn=puntajes[x.test_id]!=null&&puntajes[x.test_id]!=="";const ic=i===cur;return<button key={x.test_id} onClick={()=>{setCur(i);setTimer(0);setTimerOn(false)}} className={`flex items-center gap-3 p-2.5 rounded-xl w-full text-left transition-all ${ic?"bg-teal-50 border-l-4 border-teal-600":""} hover:bg-gray-50`}><I name={dn?"check_circle":ic?"radio_button_checked":"circle"} fill={dn||ic} className={`text-base ${dn?"text-teal-600":ic?"text-teal-600":"text-gray-300"}`}/><div className="flex-1 min-w-0"><p className={`text-sm font-bold truncate ${ic?"text-teal-600":"text-gray-700"}`}>{x.nombre}</p><p className="text-xs text-gray-400 uppercase truncate">{x.dominio}</p></div>{dn&&<span className="text-xs font-bold text-teal-600 bg-teal-50 px-1.5 py-0.5 rounded shrink-0">PD:{puntajes[x.test_id]}</span>}</button>})}</div>
 </Card>
 </div></>}
 {/* === MODO REGISTRO (TABLA) === */}
 {mode==="table"&&<div className="flex-1"><Card className="overflow-hidden"><table className="w-full text-sm"><thead style={{background:"#f5f3ef"}}><tr><th className="px-4 py-3 text-left font-bold w-8">#</th><th className="px-4 py-3 text-left font-bold">Prueba</th><th className="px-4 py-3 text-left font-bold w-48">Dominio</th><th className="px-4 py-3 text-center font-bold w-24">PD</th><th className="px-4 py-3 text-left font-bold">Observaciones</th><th className="px-2 py-3 w-10"></th></tr></thead>
 <tbody>{tests.map((x,i)=>{const dn=puntajes[x.test_id]!=null&&puntajes[x.test_id]!=="";return<tr key={x.test_id} className={`border-b border-gray-50 ${i===cur?"bg-teal-50/50":""} ${x.es_suplementaria?"opacity-70":""}`} onClick={()=>setCur(i)}>
 <td className="px-4 py-2.5 text-xs text-gray-400 font-mono">{i+1}</td>
 <td className="px-4 py-2.5"><div className="flex items-center gap-2"><I name={dn?"check_circle":"circle"} className={`text-base ${dn?"text-teal-600":"text-gray-300"}`}/><span className="font-bold text-xs">{x.nombre}</span>{x.es_suplementaria&&<span className="text-[9px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-bold">SUP</span>}</div></td>
 <td className="px-4 py-2.5"><span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded" style={{background:`${dc(x.dominio)}10`,color:dc(x.dominio)}}>{x.dominio}</span></td>
 <td className="px-4 py-2.5 text-center"><input type="number" min={0} value={puntajes[x.test_id]||""} onChange={e=>setPuntajes(p=>({...p,[x.test_id]:e.target.value}))} className="w-16 h-8 text-center text-sm font-bold rounded-lg border-none focus:ring-2 focus:ring-teal-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="—"/></td>{/* §dark-mode-fix */}
 <td className="px-4 py-2.5"><input value={obs[x.test_id]||""} onChange={e=>setObs(o=>({...o,[x.test_id]:e.target.value}))} className="w-full h-8 text-xs rounded-lg border-none px-2 focus:ring-2 focus:ring-teal-500/30" style={{background:"var(--ns-input)",color:"var(--ns-text)"}} placeholder="Observaciones..."/></td>
 <td className="px-2 py-2.5">{x.has_timer&&<I name="timer" className="text-gray-300 text-sm"/>}</td>
 </tr>})}</tbody></table></Card></div>}
 {/* === GUÍA CLÍNICA LATERAL === */}
 <div className={`xl:shrink-0 transition-all duration-300 ${guiaOpen?"w-full xl:w-80":"w-10"}`}>
 <button onClick={()=>setGuiaOpen(!guiaOpen)} className="w-10 h-10 rounded-full flex items-center justify-center shadow-md mb-3" style={{background:TEAL}} aria-label={guiaOpen?"Cerrar guía clínica":"Abrir guía clínica"} title={guiaOpen?"Cerrar guía":"Abrir guía"}><I name={guiaOpen?"chevron_right":"menu_book"} className="text-white text-lg"/></button>
 {guiaOpen&&<Card className="p-5 space-y-4 overflow-y-auto" style={{maxHeight:"calc(100vh - 180px)"}}>
 <h3 className="font-bold text-sm flex items-center gap-2"><I name="menu_book" style={{color:TEAL}}/>Guía Clínica</h3>
 <div className="flex gap-1">{[["conductas","Conductas"],["informe","Informe"],["hc","HC"]].map(([k,l])=><button key={k} onClick={()=>setGuiaTab(k)} className={`px-3 py-1.5 rounded-full text-[10px] font-bold transition-all ${guiaTab===k?"bg-teal-600 text-white":"bg-gray-100 text-gray-500"}`}>{l}</button>)}</div>
  {guiaTab==="conductas"&&<div className="space-y-4">
    {/* Ficha Neuronorma si aplica */}
    {(()=>{const nn=getNeuronormaInfo(t.test_id);return nn?(
      <div className="p-3 rounded-xl border-l-3" style={{borderColor:"#fb923c",background:"rgba(251,191,36,0.08)"}}>
        <p className="text-[10px] font-extrabold uppercase tracking-wider" style={{color:"#7c2d12"}}>Norma Colombia · cap. {nn.capitulo}</p>
        <p className="text-[11px] mt-1" style={{color:"#9a3412"}}>Ajuste: {nn.ajuste.join(" + ")} · Salida: {nn.tipoPuntuacion==="ambos"?"percentil + T":nn.tipoPuntuacion.replace("_"," ")}</p>
      </div>
    ):null})()}
    <GuideFormatter instructions={INSTRUCCIONES[t.test_id]}/>
  </div>}
 {guiaTab==="informe"&&<div className="space-y-4">{Object.entries(GUIA_INFORME).map(([k,v])=><div key={k}><p className="text-[10px] font-bold text-teal-600 uppercase tracking-wider mb-1">{k.replace(/_/g," ")}</p><p className="text-xs text-gray-600 leading-relaxed">{v}</p></div>)}</div>}
 {guiaTab==="hc"&&<div className="space-y-4">{Object.entries(GUIA_HC).map(([k,v])=><div key={k}><p className="text-[10px] font-bold text-teal-600 uppercase tracking-wider mb-1">{k.replace(/_/g," ")}</p><p className="text-xs text-gray-600 leading-relaxed">{v}</p></div>)}</div>}
 </Card>}
 </div>
 </div></main></>);
}
