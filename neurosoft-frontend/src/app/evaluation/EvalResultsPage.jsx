/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/EvalResultsPage.jsx — Resultados + redaccion de informe
 * Calculo de scoring + alertas + observaciones + impresion diagnostica
 * (DSM-5 / CIE-10) + descarga PDF/DOCX/XLSX.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError, exportCSV } from "../../api/client.js";
import { useToast, useConfirm } from "../../contexts.jsx";
import {
  RECOMMENDATIONS_LIB, DIAGNOSTIC_ALGORITHMS, DSM5_DIAGNOSES,
  INCONCLUSO_REASONS, evaluarAlgoritmo,
} from "../../data/datosClinicos.js";
import {
  Btn, Card, I, Input, Label, Sel, TopBar, Txta,
} from "../../ui/primitives.jsx";
import { TEAL, TEAL_LIGHT } from "../../ui/tokens.js";
import { IQPanel } from "../../data/IndicesCI.jsx";
import GlossaryTerm from "../../ui/GlossaryTerm.jsx"; // §P4
import { improveWithAI } from "../ia/PanelIA.jsx";
import AIAsistente from "../ia/AIAsistente.jsx";
import { ShareButton, SecondOpinionButton } from "../compartir/PanelCompartir.jsx";
import { OBS_TEMPLATES } from "../../data/clinical.js";
import { DISCREPANCY_PAIRS } from "../../data/ui.js";
import DomainAnalysis from "./DomainAnalysis.jsx";
import { useReservorio } from "../../hooks/useReservorio.js";
import ClinicalInterpretationPanel from "./ClinicalInterpretationPanel.jsx";
import ClinicalDisclaimer from "./ClinicalDisclaimer.jsx";
import { validatePediatricObservations, isChildAge } from "../../utils/pediatricValidator.js";
import { analyzeWiscDiscrepancy, computeICG_ICC, interpretCI, buildDiscrepancyReportText } from "../../utils/wiscDiscrepancy.js";
import { safeLS } from "../../utils/safeLS.js";

/* Helper local: color por interpretacion clinica.
 * Soporta tanto los niveles WISC/WAIS (Bajo/Limítrofe/Promedio/Superior)
 * como las categorias de escalas clinicas (Yesavage GDS-15, MMSE, Lawton,
 * Beck BDI-II): Normal/Deficit Leve/Deficit Extremo/Deficit Severo/etc. */
const lc=i=>({
  // Estandar WISC/WAIS
  "Bajo":"#ba1a1a", "Limítrofe":"#943700", "Promedio":"#006a6a", "Superior":"#0D9488",
  // Escalas clinicas (codigos N/DL/DE/DS del baremo)
  "Normal":"#006a6a", "Deficit Leve":"#943700", "Deficit Extremo":"#ba1a1a", "Deficit Severo":"#7c1212",
  // Fallback Beck BDI-II
  "Mínima":"#006a6a", "Leve":"#943700", "Moderada":"#ba1a1a", "Severa":"#7c1212",
}[i]||"#434655");

export default function EvalResultsPage({setPage,nav,evalCtx,setEvalCtx}){
  /* §B3-fix: usamos toast en lugar de alert() — antes había 9 alert()
   * bloqueantes que rompían el modo oscuro y eran feos.
   * §M3-fix: confirm modal reemplaza window.confirm. */
  const toast=useToast();const confirm=useConfirm();
  const[loading,setLoading]=useState(true);const[error,setError]=useState(null);
  /* Animación de barras Z — se activa 200ms después de recibir resultados */
  const[zAnimated,setZAnimated]=useState(false);
  const[res,setRes]=useState(null);const[evalId,setEvalId]=useState(null);
  const[savingObs,setSavingObs]=useState(false);const[obsSaved,setObsSaved]=useState(false);
  const[genPdf,setGenPdf]=useState(false);const[genDocx,setGenDocx]=useState(false);const[genXlsx,setGenXlsx]=useState(false);
  /* Selector de plantilla PDF — el backend acepta: estandar, pro, pediatrico,
   * medicolegal, junta_medica, inconcluso. Default "pro" porque es la
   * plantilla profesional con portada, paleta TEAL/NAVY, radar, gaussiana
   * y narrativa integradora. "estandar" se conserva para retrocompat. La
   * elección NO se persiste; cada
   * descarga puede usar una plantilla distinta. */
  const[pdfTemplate,setPdfTemplate]=useState("pro");
  /* Impresión diagnóstica: selector + respuestas a criterios */
  const[dxAlg,setDxAlg]=useState("");const[dxRes,setDxRes]=useState({});
  /* DSM-5 / CIE-10 picker — impresión final estructurada (Fase F.1) */
  const[dsmPicks,setDsmPicks]=useState([]);const[dsmQ,setDsmQ]=useState("");
  /* Recomendaciones sugeridas (panel aparte) */
  const[recCuadro,setRecCuadro]=useState("");
  /* Marcar informe como inconcluso */
  const[showIncForm,setShowIncForm]=useState(false);
  const[incMotivo,setIncMotivo]=useState(INCONCLUSO_REASONS[0].id);
  const[incDesc,setIncDesc]=useState("");
  const[incSaving,setIncSaving]=useState(false);
  const[incMsg,setIncMsg]=useState("");
  const obsDoms=[["apariencia_conducta","Observación Clínica"],["atencion_concentracion","Atención y Concentración"],["memoria","Memoria"],["lenguaje","Lenguaje"],["funciones_ejecutivas","Funciones Ejecutivas"],["habilidades_visoespaciales","Habilidades Visoespaciales"],["impresion_diagnostica","Impresión Diagnóstica"],["recomendaciones","Recomendaciones"]];
  const[obsT,setObsT]=useState(()=>{const o={};obsDoms.forEach(([k])=>o[k]="");return o});
  /* §autosave-results: clave del borrador de informe en localStorage.
   * Una clave por paciente+evaluación: si se cierra el informe a medio
   * redactar, al volver se restauran las observaciones. */
  const obsDraftKey=()=>`ns_report_obs_${evalCtx?.patientId||"sin_paciente"}_${evalId||evalCtx?.proto||"sin_eval"}`;
  const[_obsDraftSavedAt,setObsDraftSavedAt]=useState(null);
  /* Pre-fill observaciones desde notas por prueba */
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(()=>{if(!evalCtx?.obs)return;const perTest=evalCtx.obs;const byDom={};Object.entries(perTest).forEach(([tid,txt])=>{if(!txt)return;byDom[tid]=txt});if(Object.keys(byDom).length>0){const pre="Observaciones por prueba:\n"+Object.entries(byDom).map(([tid,txt])=>`• ${tid}: ${txt}`).join("\n");setObsT(o=>({...o,apariencia_conducta:pre}))}},[]);

  /* §autosave-results-1: restaurar borrador de informe al cargar la página.
   * Solo aplica si ya tenemos evalId (después de scoring). */
  useEffect(()=>{
    if(!evalId)return;
    try{
      const raw=localStorage.getItem(obsDraftKey());
      if(!raw)return;
      const d=JSON.parse(raw);
      const TTL=7*24*60*60*1000;
      if(!d.ts||(Date.now()-d.ts)>TTL){safeLS.remove(obsDraftKey());return}
      if(d.obsT&&Object.values(d.obsT).some(v=>v?.trim())){
        setObsT(prev=>({...prev,...d.obsT}));
      }
    }catch(e){console.warn("[autosave-results] restore:",e)}
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[evalId]);

  /* §autosave-results-2: persistir borrador del informe cada 30s + debounce 1s. */
  useEffect(()=>{
    if(!evalId)return;
    const save=()=>{
      try{
        const hasData=Object.values(obsT).some(v=>v?.trim());
        if(!hasData)return;
        localStorage.setItem(obsDraftKey(),JSON.stringify({ts:Date.now(),obsT}));
        setObsDraftSavedAt(Date.now());
      }catch(e){console.warn("[autosave-results] save:",e)}
    };
    const debounce=setTimeout(save,1000);
    const interval=setInterval(save,30000);
    return()=>{clearTimeout(debounce);clearInterval(interval)};
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[obsT,evalId]);

  /* §autosave-results-3: beforeunload — protección al cerrar tab con cambios. */
  useEffect(()=>{
    const hasUnsaved=Object.values(obsT).some(v=>v?.trim())&&!obsSaved;
    if(!hasUnsaved)return;
    const handler=(e)=>{e.preventDefault();e.returnValue="";return""};
    window.addEventListener("beforeunload",handler);
    return()=>window.removeEventListener("beforeunload",handler);
  },[obsT,obsSaved]);
  /* Llamar al motor de scoring */
  useEffect(()=>{if(!evalCtx?.patientId||!evalCtx?.puntajes){setError("No hay datos de evaluación. Vuelva a la pantalla de aplicación.");setLoading(false);return}
    const run=async()=>{try{const body={patient_id:evalCtx.patientId,protocolo:evalCtx.protoNombre||"WISC-IV",puntajes:evalCtx.puntajes};const d=await api.post("/api/v1/scores/",body);setRes(d);setEvalId(d.evaluation_id||null);if(setEvalCtx)setEvalCtx(c=>({...c,scoringResult:d}))}catch(e){setError(_parseError(e))}setLoading(false)};
    // eslint-disable-next-line react-hooks/exhaustive-deps
    run()},[]);
  /* Activar animación Z 200ms después de tener resultados */
  useEffect(()=>{if(res){const t=setTimeout(()=>setZAnimated(true),200);return()=>clearTimeout(t)}},[res]);
  /* Extraer índices del resultado */
  const indices=(res?.resultados||[]).filter(r=>r.test_id&&(r.test_id.includes("Ind")||r.test_id.includes("Tot")||r.tipo_metrica==="ci"||r.tipo_metrica==="indice")).map(r=>{const abr=r.test_nombre.match(/^(\w+)/)?.[1]||r.test_id;return{n:abr.length>5?r.test_nombre.split("—")[0]?.trim()||abr:abr,v:r.puntaje_escalar,i:r.interpretacion}});
  /* Subtests (no-índices) con z */
  const subtests=(res?.resultados||[]).filter(r=>r.z_equivalente!=null&&!r.test_id.includes("Ind")&&!r.test_id.includes("Tot")&&r.tipo_metrica!=="ci"&&r.tipo_metrica!=="indice");
  const zp=z=>Math.max(0,Math.min(100,((z+3)/6)*100));
  /* Alertas clínicas — detectar puntajes en rango "Bajo" */
  const alertas=(res?.resultados||[]).filter(r=>r.interpretacion==="Bajo"||r.interpretacion==="Limítrofe");
  /* Calculadora de discrepancias entre índices */
  /* §M2-fix: si dos índices comparten 3 primeras mayúsculas, conservamos
   * el primero (no sobreescribimos). Esto previene colisiones futuras
   * con protocolos que usen prefijos comunes (ej. "ICV1", "ICV2"). */
  const indicesMap={};indices.forEach(i=>{const k=i.n.replace(/[^A-Z]/g,"").slice(0,3);if(!(k in indicesMap))indicesMap[k]=Math.round(i.v||0)});
  /* §M3-fix: usar `!= null` en lugar de truthy. Antes un índice con
   * valor 0 (improbable pero válido) se excluía silenciosamente. */
  const discrepancias=DISCREPANCY_PAIRS.filter(p=>indicesMap[p.a]!=null&&indicesMap[p.b]!=null).map(p=>{const diff=indicesMap[p.a]-indicesMap[p.b];const abs=Math.abs(diff);const sig=abs>=p.critical05?"0.05":abs>=p.critical15?"0.15":"ns";return{...p,diff,abs,sig,higher:diff>0?p.a:p.b,va:indicesMap[p.a],vb:indicesMap[p.b]}});
  /* Análisis de discrepancia mayor (≥23 puntos) — regla del sistema V.1
   * 2024 — invalida el CIT y obliga a reportar ICG/ICC. */
  const wiscAnalysis=analyzeWiscDiscrepancy(indicesMap);
  const igcEstimate=computeICG_ICC(indicesMap);
  const wiscReportText=wiscAnalysis?.isMajor?buildDiscrepancyReportText(wiscAnalysis,igcEstimate):"";
  /* CSV Export */
  const exportResults=()=>{const rows=(res?.resultados||[]).map(r=>({prueba:r.test_nombre,dominio:r.dominio_cognitivo||"",PD:r.puntaje_bruto,PE:r.puntaje_escalar,Z:r.z_equivalente,interpretacion:r.interpretacion}));exportCSV(rows,`Eval_${res?.patient_info?.nombre||"resultado"}_${Date.now()}.csv`)};
  /* Generador de observaciones IA — crea borradores a partir de resultados */
  const generarObservacion=(dominio)=>{const templates=OBS_TEMPLATES[dominio]||[];if(templates.length===0)return"";const relevantes=subtests.filter(r=>{if(dominio==="atencion_concentracion")return(r.dominio_cognitivo||"").toLowerCase().includes("atenci")||(r.test_nombre||"").toLowerCase().match(/claves|símbolos|tmt|stroop/);if(dominio==="memoria")return(r.dominio_cognitivo||"").toLowerCase().includes("memoria")||(r.test_nombre||"").toLowerCase().match(/grober|cvlt|fcro|dígitos/);if(dominio==="lenguaje")return(r.dominio_cognitivo||"").toLowerCase().includes("lengu")||(r.test_nombre||"").toLowerCase().match(/vocab|semej|comp|fluid/);if(dominio==="funciones_ejecutivas")return(r.dominio_cognitivo||"").toLowerCase().includes("ejec")||(r.test_nombre||"").toLowerCase().match(/matrices|wisconsin|trail/);if(dominio==="habilidades_visoespaciales")return(r.test_nombre||"").toLowerCase().match(/cubos|rey|fcro|matrices/);return true});const bajos=relevantes.filter(r=>r.interpretacion==="Bajo"||r.interpretacion==="Limítrofe");const altos=relevantes.filter(r=>r.interpretacion==="Superior");let texto=templates[0]+"\n\n";if(bajos.length>0)texto+=`Se identifican puntajes por debajo del promedio en: ${bajos.map(r=>r.test_nombre).join(", ")}.\n`;if(altos.length>0)texto+=`Se destaca desempeño superior en: ${altos.map(r=>r.test_nombre).join(", ")}.\n`;if(dominio==="atencion_concentracion"&&templates[1])texto+="\n"+templates[1];return texto.trim()};
  const autocompletarTodo=()=>{const nuevo={...obsT};obsDoms.forEach(([k])=>{if(!nuevo[k])nuevo[k]=generarObservacion(k)});setObsT(nuevo)};
  /* Guardar observaciones */
  /* Warnings de redacción pediátrica (regla del sistema: nunca "conserva"
   * en niños; usar DIS- en lugar de A-; hablar de la función no de la
   * prueba). Se calculan reactivamente y se muestran como banner antes
   * de guardar — no bloquean, sólo advierten. */
  const isPed = isChildAge(res?.patient_info?.fecha_nacimiento) || isChildAge(res?.edad_display);
  const pedWarnings = isPed ? validatePediatricObservations(obsT) : {};
  const pedWarningCount = Object.values(pedWarnings).reduce((s,a)=>s+a.length,0);

  /* Poblacion del paciente (infantil | adulto | adulto_mayor) — se usa
   * para filtrar los cuadros del backend via /api/v1/reservorio/cuadros.
   * Single source of truth = backend (app/domain/data/reservorio_recomendaciones.json). */
  const _edadNum = res?.patient_info?.edad_anios ?? evalCtx?.edad ?? null;
  const _poblacion = isPed
    ? "infantil"
    : (_edadNum != null && _edadNum >= 50 ? "adulto_mayor" : "adulto");
  const { cuadros: cuadrosResv, loading: resvLoading, source: resvSource } = useReservorio(_poblacion);
  /* Lookup rápido: id → cuadro (backend o local fallback) */
  const cuadroById = React.useMemo(() => {
    const m = {};
    for (const c of cuadrosResv) m[c.id] = c;
    return m;
  }, [cuadrosResv]);
  const saveObs=async()=>{if(!evalCtx?.patientId)return;
    /* Si hay warnings pediátricos, pedir confirmación al clínico (modal editorial). */
    if(pedWarningCount>0){
      const lines=Object.entries(pedWarnings).flatMap(([dom,ws])=>ws.map(w=>`• [${dom}] "${w.term}" — ${w.suggestion}`));
      const ok=await confirm({
        title:`Advertencias pediátricas (${pedWarningCount})`,
        message:`Se detectaron términos no recomendados para pacientes pediátricos:\n\n${lines.slice(0,8).join("\n")}\n\n¿Guardar de todos modos?`,
        confirmText:"Guardar igual",
        cancelText:"Revisar",
      });
      if(!ok){setSavingObs(false);return}
    }
    setSavingObs(true);try{const promises=obsDoms.filter(([k])=>obsT[k]&&obsT[k].trim()).map(([k])=>api.post("/api/v1/observations/",{patient_id:evalCtx.patientId,evaluation_id:evalId,dominio:k,texto:obsT[k].trim()}));await Promise.all(promises);setObsSaved(true);setTimeout(()=>setObsSaved(false),3000);/* §autosave-results-clean: guardado en backend → borrador local ya no es necesario */safeLS.remove(obsDraftKey())}catch(e){toast.error("Error guardando observaciones: "+(e.detail||e.message||"Error"))}setSavingObs(false)};
  /* Corrector IA (Fase G.2) — llama al backend AI para mejorar un dominio concreto */
  const[aiBusy,setAiBusy]=useState("");
  const mejorarDominioIA=async(k,mode="style")=>{const t=obsT[k]||"";if(t.trim().length<20){toast.warn("El texto es muy corto para corregir. Mínimo 20 caracteres.");return}setAiBusy(k+":"+mode);try{const r=await improveWithAI(t,mode);if(r?.improved){setObsT(o=>({...o,[k]:r.improved}));toast.success("Texto mejorado con IA.")}else toast.warn("La IA no devolvió respuesta. Configure un proveedor en 'Asistente IA'.")}catch(e){toast.error("Error IA: "+(e.message||e))}setAiBusy("")};
  /* Generar PDF — usa la plantilla seleccionada en `pdfTemplate` */
  const downloadPdf=async()=>{if(!evalId){toast.warn("Primero se debe calificar la evaluación");return}setGenPdf(true);try{const blob=await api.blob(`/api/v1/reports/pdf/${evalId}?template=${encodeURIComponent(pdfTemplate)}`);const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=`InformeNPS_${pdfTemplate}_${evalId.slice(0,8)}.pdf`;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);toast.success("PDF descargado.")}catch(e){toast.error("Error generando PDF: "+e.message)}setGenPdf(false)};
  /* Generar DOCX */
  const downloadDocx=async()=>{if(!evalId){toast.warn("Primero se debe calificar la evaluación");return}setGenDocx(true);try{const blob=await api.blob(`/api/v1/reports/docx/${evalId}`);const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=`InformeNPS_${evalId.slice(0,8)}.docx`;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);toast.success("DOCX descargado.")}catch(e){toast.error("Error generando DOCX: "+e.message)}setGenDocx(false)};
  /* Generar XLSX */
  const downloadXlsx=async()=>{if(!evalId){toast.warn("Primero se debe calificar la evaluación");return}setGenXlsx(true);try{const blob=await api.blob(`/api/v1/reports/xlsx/${evalId}`);const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=`Puntajes_${evalId.slice(0,8)}.xlsx`;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);toast.success("XLSX descargado.")}catch(e){toast.error("Error generando XLSX: "+e.message)}setGenXlsx(false)};
  /* Marcar como inconcluso */
  const marcarInconcluso=async()=>{if(!evalCtx?.patientId){toast.warn("Falta el paciente");return}setIncSaving(true);setIncMsg("");try{const m=INCONCLUSO_REASONS.find(r=>r.id===incMotivo);await api.post("/api/v1/inconclusos/",{patient_id:evalCtx.patientId,evaluation_id:evalId,motivo_id:incMotivo,motivo_titulo:m?.titulo||incMotivo,descripcion:incDesc||m?.descripcion||"",accion_sugerida:m?.accion||"",plazo_dias:m?.plazo_dias||15});setIncMsg("ok");setShowIncForm(false);setIncDesc("")}catch(e){setIncMsg(_parseError(e))}setIncSaving(false)};
  if(loading)return<><TopBar title="Resultados"/><main className="p-8 flex flex-col items-center justify-center h-96 gap-4" style={{background:"var(--ns-bg)"}}>
    <div className="animate-spin w-10 h-10 border-4 rounded-full" style={{borderColor:`${TEAL}33`,borderTopColor:TEAL}}/>
    <p className="ns-eyebrow" style={{color:TEAL}}>Procesando</p>
    <p className="ns-serif text-lg italic" style={{color:"var(--ns-muted)"}}>Calificando evaluación con el motor de baremos…</p>
  </main></>;
  if(error)return<><TopBar title="Resultados"/><main className="p-8 max-w-2xl mx-auto"><Card className="p-8 text-center space-y-4"><I name="error" className="text-5xl text-red-400"/><p className="font-bold text-lg text-red-700">Error en la calificación</p><p className="text-gray-600">{error}</p><Btn onClick={()=>nav("eval_apply")}>← Volver a Evaluación</Btn></Card></main></>;

  /* Completitud: bloquear descarga si faltan secciones criticas */
  const puedeDescargarPDF = !!(evalId && res?.resultados?.length > 0 && evalCtx?.patientId);
  const razonBloqueoPDF = !evalId ? "Evaluacion no guardada. Guarda los resultados primero."
    : !res?.resultados?.length ? "Sin resultados calificados."
    : !evalCtx?.patientId ? "Sin paciente asignado."
    : null;

  return(<><TopBar title="Resultados y Observaciones">
    <div className="flex items-center gap-3">
      <span className="text-xs ns-serif-italic" style={{color:"var(--ns-muted)"}}>{res?.edad_display}</span>
      <span className="text-[10px] font-semibold uppercase tracking-wider px-2.5 py-1 rounded-sm border" style={{borderColor:TEAL,color:TEAL,background:`${TEAL}10`}}>{res?.protocolo}</span>
      <span className="text-xs ns-mono" style={{color:"var(--ns-muted)"}}>{res?.pruebas_realizadas}/{res?.total_pruebas} pruebas</span>
      {evalId&&<span className="text-[10px] ns-mono px-2 py-0.5 rounded-sm" style={{color:TEAL,background:`${TEAL}10`}}>ID: {evalId.slice(0,8)}</span>}
    </div></TopBar>
    <main className="p-6"><div className="grid grid-cols-12 gap-6">
      <div className="col-span-12 lg:col-span-7 space-y-5">
        {/* ─── ALERTAS CLÍNICAS ─── */}
        {alertas.length>0&&<Card className="p-5 border-l-4 border-red-500" style={{background:"rgba(239,68,68,0.08)"}}>
          <div className="flex items-start gap-3"><I name="warning" fill className="text-red-500 text-2xl mt-0.5 shrink-0"/>
            <div className="flex-1"><h4 className="text-sm font-extrabold text-red-700 mb-2">⚠ Alertas Clínicas ({alertas.length})</h4>
              <p className="text-xs text-red-600 mb-2">Se detectaron puntajes en rango clínicamente significativo. Revisar y considerar intervención.</p>
              <div className="flex flex-wrap gap-1.5">{alertas.slice(0,6).map((r,i)=><span key={i} className="text-[10px] font-bold px-2 py-1 rounded-full" style={{background:lc(r.interpretacion)+"20",color:lc(r.interpretacion)}}>{r.test_nombre}: {r.interpretacion}</span>)}{alertas.length>6&&<span className="text-[10px] font-bold px-2 py-1 rounded-full bg-red-100 text-red-700">+{alertas.length-6} más</span>}</div>
            </div></div>
        </Card>}
        {/* Advertencias */}
        {res?.advertencias?.length>0&&<Card className="p-4 space-y-1" style={{background:"rgba(245,158,11,0.08)",borderLeft:"3px solid #f59e0b"}}>{res.advertencias.map((w,i)=><p key={i} className="text-xs flex items-center gap-2" style={{color:"#92400e"}}><I name="warning" className="text-sm" style={{color:"#f59e0b"}}/>{w}</p>)}</Card>}
        {/* Índices compuestos */}
        {indices.length>0&&<div className={`grid gap-3 ${indices.length<=5?"grid-cols-5":"grid-cols-"+Math.min(indices.length,6)}`}>{indices.map(c=>{
          const esPrincipal=c.n.includes("CIT")||c.n.includes("Total");
          return(
            <div key={c.n} className="p-4 rounded-md border" style={{background:"var(--ns-card)",borderColor:esPrincipal?lc(c.i):"var(--ns-card-b)",borderLeftWidth:3,borderLeftColor:lc(c.i)}}>
              <p className="ns-eyebrow truncate">{c.n}</p>
              <p className="ns-serif text-3xl font-bold tabular-nums leading-none mt-2" style={{color:lc(c.i)}}>{c.v!=null?Math.round(c.v):"—"}</p>
              <div className="mt-2 h-1 w-full rounded-full overflow-hidden" style={{background:"var(--ns-subtle)"}}>
                <div className="h-full rounded-full" style={{width:`${(c.v||0)/1.5}%`,background:lc(c.i)}}/>
              </div>
              <p className="text-[10px] ns-serif-italic mt-1.5" style={{color:lc(c.i)}}>{c.i}</p>
            </div>
          );
        })}</div>}
        {/* ─── CÁLCULO DE CI (WISC-IV / WAIS-III) ─── */}
        {(evalCtx?.protoId==="wisc_iv"||evalCtx?.protoId==="wais_iii"||(res?.protocolo||"").includes("WISC")||(res?.protocolo||"").includes("WAIS"))&&
          <Card className="p-6">
            <IQPanel
              protocol={(res?.protocolo||evalCtx?.protoNombre||"").includes("WAIS")?"wais_iii":"wisc_iv"}
              subtestLabels={Object.fromEntries((res?.resultados||[]).map(r=>[r.test_id,r.test_nombre]))}
            />
          </Card>}
        {/* ─── DISCREPANCIA MAYOR ≥23 puntos (regla del sistema) ─── */}
        {wiscAnalysis?.isMajor&&<Card className="p-5 border-l-4" style={{borderColor:"#dc2626",background:"rgba(239,68,68,0.07)"}}>
          <div className="flex items-start gap-3">
            <I name="warning" fill className="text-2xl text-red-600 mt-0.5 shrink-0"/>
            <div className="flex-1">
              <h4 className="text-sm font-extrabold text-red-700 mb-1">Discrepancia mayor entre índices (≥{wiscAnalysis.threshold} puntos)</h4>
              <p className="text-xs text-red-700 leading-relaxed mb-3">
                Rango de {wiscAnalysis.range} puntos entre <b>{wiscAnalysis.highest.name}={wiscAnalysis.highest.value}</b> y <b>{wiscAnalysis.lowest.name}={wiscAnalysis.lowest.value}</b>.
                El CIT pierde su valor como resumen unitario. Se reportan los índices alternativos:
              </p>
              <div className="grid grid-cols-2 gap-3 mt-3">
                {igcEstimate?.ICG!=null&&(()=>{const interp=interpretCI(igcEstimate.ICG);return(
                  <div className="p-3 rounded-xl border-2" style={{borderColor:interp?.color||"var(--ns-card-b)",background:"var(--ns-card)"}}>
                    <p className="text-[10px] font-extrabold uppercase tracking-wider" style={{color:"var(--ns-muted)"}}><GlossaryTerm term="ICG">ICG</GlossaryTerm> estimado</p>
                    <p className="text-3xl font-extrabold" style={{color:interp?.color}}>{igcEstimate.ICG}</p>
                    <p className="text-[10px] font-bold" style={{color:interp?.color}}>{interp?.label}</p>
                    <p className="text-[9px] mt-1" style={{color:"var(--ns-muted)"}}>Capacidad General (<GlossaryTerm term="ICV">ICV</GlossaryTerm>+<GlossaryTerm term="IRP">IRP</GlossaryTerm>)</p>
                  </div>);})()}
                {igcEstimate?.ICC!=null&&(()=>{const interp=interpretCI(igcEstimate.ICC);return(
                  <div className="p-3 rounded-xl border-2" style={{borderColor:interp?.color||"var(--ns-card-b)",background:"var(--ns-card)"}}>
                    <p className="text-[10px] font-extrabold uppercase tracking-wider" style={{color:"var(--ns-muted)"}}>ICC estimado</p>
                    <p className="text-3xl font-extrabold" style={{color:interp?.color}}>{igcEstimate.ICC}</p>
                    <p className="text-[10px] font-bold" style={{color:interp?.color}}>{interp?.label}</p>
                    <p className="text-[9px] mt-1" style={{color:"var(--ns-muted)"}}>Competencia Cognitiva (<GlossaryTerm term="IMT">IMT</GlossaryTerm>+<GlossaryTerm term="IVP">IVP</GlossaryTerm>)</p>
                  </div>);})()}
              </div>
              <details className="mt-3">
                <summary className="text-[10px] font-bold cursor-pointer text-red-700">Texto sugerido para el informe ▾</summary>
                <p className="text-[11px] text-red-700/80 leading-relaxed mt-2 italic">{wiscReportText}</p>
                <p className="text-[9px] text-gray-500 mt-2">ICG/ICC son <b>estimaciones</b> calculadas como promedio aritmético. Para el valor oficial consultar tablas Flanagan &amp; Kaufman (2009).</p>
                <button onClick={()=>{navigator.clipboard?.writeText(wiscReportText);toast.success("Texto copiado al portapapeles")}} className="text-[10px] font-bold px-3 py-1 rounded-full bg-red-600 text-white hover:bg-red-500 mt-2">Copiar texto</button>
              </details>
            </div>
          </div>
        </Card>}
        {/* ─── CALCULADORA DE DISCREPANCIAS ─── */}
        {discrepancias.length>0&&<Card className="p-6"><h3 className="text-sm font-extrabold mb-4 flex items-center gap-2"><I name="compare_arrows" style={{color:TEAL}}/>Análisis de Discrepancias entre Índices</h3>
          <div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr className="text-left" style={{color:"var(--ns-muted)"}}><th className="pb-2 font-bold">Par</th><th className="pb-2 font-bold text-center">Valor A</th><th className="pb-2 font-bold text-center">Valor B</th><th className="pb-2 font-bold text-center">Diferencia</th><th className="pb-2 font-bold">Significancia</th></tr></thead>
            <tbody>{discrepancias.map((d,i)=><tr key={i} className="border-t" style={{borderColor:"var(--ns-card-b)"}}>
              <td className="py-2 font-bold">{d.name}</td><td className="py-2 text-center">{d.va}</td><td className="py-2 text-center">{d.vb}</td>
              <td className="py-2 text-center font-bold" style={{color:d.sig==="0.05"?"#dc2626":d.sig==="0.15"?"#f59e0b":"var(--ns-muted)"}}>{d.diff>0?"+":""}{d.diff}</td>
              <td className="py-2"><span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{background:d.sig==="0.05"?"rgba(220,38,38,0.1)":d.sig==="0.15"?"rgba(245,158,11,0.1)":"var(--ns-subtle)",color:d.sig==="0.05"?"#dc2626":d.sig==="0.15"?"#d97706":"var(--ns-muted)"}}>{d.sig==="0.05"?"p<.05 significativo":d.sig==="0.15"?"p<.15 tendencia":"No significativo"}</span>{d.sig!=="ns"&&<span className="text-[10px] ml-2" style={{color:"var(--ns-muted)"}}>→ {d.higher} superior</span>}</td>
            </tr>)}</tbody></table></div>
          <p className="text-[10px] mt-3" style={{color:"var(--ns-muted)"}}>Los valores críticos corresponden a WISC-IV (Flanagan & Kaufman). Diferencias significativas (p&lt;.05) indican discrepancia clínicamente relevante entre dominios.</p>
        </Card>}
        {/* Perfil Z con CURVA NORMATIVA superpuesta */}
        {subtests.length>0&&<Card className="p-6"><div className="flex justify-between items-center mb-4"><h3 className="text-sm font-extrabold">Perfil Z — Curva Normativa Superpuesta</h3><div className="flex gap-3 text-[10px] font-bold">{[{l:"Bajo",c:"#ba1a1a"},{l:"Limítrofe",c:"#943700"},{l:"Promedio",c:"#006a6a"},{l:"Superior",c:"#0D9488"}].map(x=><span key={x.l} className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{background:x.c}}/>{x.l}</span>)}</div></div>
          {/* Curva normativa visual (distribución gaussiana) */}
          <div className="relative mb-3 p-3 rounded-xl" style={{background:"var(--ns-subtle)"}}>
            <svg viewBox="0 0 600 80" className="w-full h-16">
              <path d="M 0 75 Q 100 75 150 60 T 250 35 T 300 5 T 350 35 T 450 60 T 600 75" fill="none" stroke={TEAL} strokeWidth="1.5" strokeOpacity="0.4"/>
              <path d="M 0 75 Q 100 75 150 60 T 250 35 T 300 5 T 350 35 T 450 60 T 600 75 L 600 75 L 0 75 Z" fill={TEAL} fillOpacity="0.08"/>
              {[-3,-2,-1,0,1,2,3].map(z=>{const x=((z+3)/6)*600;return<g key={z}><line x1={x} y1="5" x2={x} y2="75" stroke="var(--ns-card-b)" strokeWidth="0.5" strokeDasharray="2 3"/><text x={x} y="78" textAnchor="middle" fontSize="9" fill="var(--ns-muted)">{z}</text></g>})}
              {/* Marcadores de subtests */}
              {subtests.map((r,i)=>{const x=((r.z_equivalente+3)/6)*600;const y=75-Math.exp(-(r.z_equivalente*r.z_equivalente)/2)*70;return<circle key={i} cx={x} cy={y} r="3" fill={lc(r.interpretacion)} stroke="#fff" strokeWidth="1"/>})}
            </svg>
            <p className="text-[9px] text-center mt-1" style={{color:"var(--ns-muted)"}}>Distribución normal teórica con posición de cada subtest del paciente</p>
          </div>
          <div className="flex justify-between text-[10px] font-bold mb-2 px-2" style={{color:"var(--ns-muted)"}}>{[-3,-2,-1,0,1,2,3].map(x=><span key={x}>{x}</span>)}</div>
          <div className="space-y-2">{subtests.map(r=><div key={r.test_id} className="flex items-center gap-2"><span className="w-28 text-[11px] font-bold truncate text-right">{r.test_nombre}</span><div className="flex-1 h-2.5 rounded-full relative overflow-hidden" style={{background:"var(--ns-subtle)"}}><div className="absolute top-0 bottom-0 opacity-8" style={{left:"33.3%",width:"33.4%",background:"#0D9488"}}/><div className="absolute top-0 bottom-0 rounded-full" style={{left:`${Math.min(zp(0),zp(r.z_equivalente))}%`,width:zAnimated?`${Math.max(Math.abs(zp(r.z_equivalente)-zp(0)),2)}%`:"0%",background:lc(r.interpretacion),transition:"width 0.7s cubic-bezier(0.34,1.56,0.64,1)"}}/></div><span className="w-8 text-[10px] font-bold text-right" style={{color:lc(r.interpretacion)}}>{r.z_equivalente>0?"+":""}{r.z_equivalente.toFixed(1)}</span></div>)}</div>
        </Card>}
        {/* Fortalezas / Debilidades */}
        {(res?.puntos_fuertes?.length>0||res?.puntos_debiles?.length>0)&&<div className="grid grid-cols-2 gap-4">
          {res.puntos_fuertes?.length>0&&
            <div className="p-5 rounded-md border" style={{background:"var(--ns-card)",borderColor:"var(--ns-card-b)",borderLeftWidth:3,borderLeftColor:"#0D9488"}}>
              <p className="ns-eyebrow" style={{color:"#0D9488"}}>Fortalezas</p>
              <h4 className="ns-serif text-base font-bold mt-1 mb-3" style={{color:"var(--ns-text)"}}>Patrón conservado</h4>
              {res.puntos_fuertes.map((f,i)=><p key={i} className="text-xs leading-relaxed mb-1.5" style={{color:"var(--ns-text)"}}>· {f}</p>)}
            </div>}
          {res.puntos_debiles?.length>0&&
            <div className="p-5 rounded-md border" style={{background:"var(--ns-card)",borderColor:"var(--ns-card-b)",borderLeftWidth:3,borderLeftColor:"#dc2626"}}>
              <p className="ns-eyebrow" style={{color:"#dc2626"}}>Debilidades</p>
              <h4 className="ns-serif text-base font-bold mt-1 mb-3" style={{color:"var(--ns-text)"}}>Patrón comprometido</h4>
              {res.puntos_debiles.map((f,i)=><p key={i} className="text-xs leading-relaxed mb-1.5" style={{color:"var(--ns-text)"}}>· {f}</p>)}
            </div>}
        </div>}
        {/* ─── INTERPRETACIÓN CLÍNICA ASISTIDA ─── */}
        <ClinicalInterpretationPanel resultados={res?.resultados||[]} edad={res?.patient_info?.edad_anios??evalCtx?.edad??null}/>
        {/* ─── ANÁLISIS POR DOMINIOS COGNITIVOS (Fase F.2) ─── */}
        <DomainAnalysis subtests={subtests}/>
        {/* Tabla de resultados */}
        <Card className="overflow-hidden"><table className="w-full text-sm"><thead style={{background:"var(--ns-subtle)"}}><tr><th className="px-4 py-3 text-left font-bold">Prueba</th><th className="px-3 py-3 text-center font-bold">PD</th><th className="px-3 py-3 text-center font-bold">PE</th><th className="px-3 py-3 text-center font-bold">Z</th><th className="px-3 py-3 text-left font-bold">Nivel</th><th className="px-4 py-3 text-left font-bold">Dominio</th></tr></thead>
          <tbody>{(res?.resultados||[]).filter(r=>r.puntaje_bruto!==9999).map((r,i)=><tr key={r.test_id} className={`border-b border-gray-50 ${i%2?"bg-gray-50/30":""}`}><td className="px-4 py-2.5 font-bold text-xs">{r.test_nombre}</td><td className="px-3 py-2.5 text-center text-xs">{r.puntaje_bruto!=null?r.puntaje_bruto:"—"}</td><td className="px-3 py-2.5 text-center font-extrabold text-xs" style={{color:lc(r.interpretacion)}}>{r.puntaje_escalar!=null?Math.round(r.puntaje_escalar):"—"}</td><td className="px-3 py-2.5 text-center text-xs font-mono" style={{color:lc(r.interpretacion)}}>{r.z_equivalente!=null?(r.z_equivalente>0?"+":"")+r.z_equivalente.toFixed(1):"—"}</td><td className="px-3 py-2.5"><span className="px-2 py-0.5 text-[10px] font-bold rounded" style={{background:`${lc(r.interpretacion)}15`,color:lc(r.interpretacion)}}>{r.interpretacion}</span></td><td className="px-4 py-2.5 text-gray-400 italic text-[10px]">{r.dominio_cognitivo}</td></tr>)}</tbody></table>
        </Card>
        {/* ─── IMPRESIÓN DIAGNÓSTICA SUGERIDA (algoritmos ponderados) ─── */}
        <Card className="p-6"><div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-extrabold flex items-center gap-2"><I name="psychology" style={{color:TEAL}}/>Impresión Diagnóstica — Algoritmo Asistido</h3>
          <Sel value={dxAlg} onChange={e=>{setDxAlg(e.target.value);setDxRes({})}} className="text-xs w-64"><option value="">— Elegir cuadro a evaluar —</option>{Object.entries(DIAGNOSTIC_ALGORITHMS).map(([k,a])=><option key={k} value={k}>{a.nombre}</option>)}</Sel>
        </div>
        {!dxAlg?<p className="text-xs" style={{color:"var(--ns-muted)"}}>Seleccione un cuadro clínico para aplicar criterios DSM-5/CIE-10 y obtener nivel de sospecha ponderado.</p>
        :(()=>{const alg=DIAGNOSTIC_ALGORITHMS[dxAlg];const evalRes=evaluarAlgoritmo(dxAlg,dxRes);const colorN=evalRes.nivel==="alta"?"#dc2626":evalRes.nivel==="media"?"#d97706":"#059669";return<div className="space-y-4">
          <p className="text-[10px]" style={{color:"var(--ns-muted)"}}>Marco: <strong>{alg.marco}</strong> · Marque los criterios que se cumplen en el caso actual.</p>
          <div className="space-y-2">{alg.criterios.map(c=>{const checked=!!dxRes[c.id];return<label key={c.id} className="flex items-start gap-3 p-3 rounded-xl cursor-pointer hover:bg-teal-50/40 transition-all" style={{background:checked?`${TEAL}10`:"var(--ns-subtle)"}}>
            <input type="checkbox" checked={checked} onChange={e=>setDxRes(r=>({...r,[c.id]:e.target.checked}))} className="mt-0.5"/>
            <div className="flex-1"><p className="text-xs font-semibold">{c.pregunta}</p></div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0" style={{background:TEAL+"20",color:TEAL}}>peso {c.peso}</span>
          </label>})}</div>
          <div className="p-4 rounded-xl border-l-4" style={{background:`${colorN}10`,borderColor:colorN}}>
            <div className="flex items-center justify-between mb-2"><p className="text-sm font-extrabold" style={{color:colorN}}>Sospecha {evalRes.nivel.toUpperCase()} · Score {Math.round(evalRes.ratio*100)}%</p>
              <button onClick={()=>{const txt=`${alg.nombre}: ${evalRes.interpretacion}\n\nCriterios cumplidos:\n${evalRes.criterios_cumplidos.map(c=>"• "+c).join("\n")||"(ninguno)"}\n\nCriterios por confirmar:\n${evalRes.criterios_faltantes.map(c=>"• "+c).join("\n")||"(ninguno)"}`;setObsT(o=>({...o,impresion_diagnostica:(o.impresion_diagnostica?o.impresion_diagnostica+"\n\n":"")+txt}))}} className="text-[10px] font-bold px-3 py-1 rounded-full" style={{background:TEAL,color:"#fff"}}>→ A observaciones</button>
            </div>
            <p className="text-xs leading-relaxed" style={{color:"var(--ns-fg)"}}>{evalRes.interpretacion}</p>
          </div>
        </div>})()}
        </Card>
        {/* ─── DSM-5 / CIE-10 PICKER — Impresión final estructurada (Fase F.1) ─── */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4 gap-3 flex-wrap">
            <h3 className="text-sm font-extrabold flex items-center gap-2"><I name="medical_information" style={{color:TEAL}}/>Códigos DSM-5 / CIE-10 — Impresión final</h3>
            <Input value={dsmQ} onChange={e=>setDsmQ(e.target.value)} placeholder="Buscar código o diagnóstico…" className="text-xs w-64"/>
          </div>
          <p className="text-[10px] mb-3" style={{color:"var(--ns-muted)"}}>Seleccione uno o más códigos para la impresión diagnóstica final. Los seleccionados se insertan en "Impresión Diagnóstica" con formato estructurado.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5 max-h-72 overflow-y-auto pr-1">
            {Object.entries(DSM5_DIAGNOSES).filter(([k,d])=>{const q=dsmQ.trim().toLowerCase();if(!q)return true;return k.toLowerCase().includes(q)||d.nombre.toLowerCase().includes(q)||(d.dsm5||"").toLowerCase().includes(q);}).map(([code,d])=>{const checked=dsmPicks.includes(code);return<label key={code} className="flex items-start gap-2 p-2 rounded-lg cursor-pointer hover:bg-teal-50/40 transition-all" style={{background:checked?`${TEAL}15`:"var(--ns-subtle)"}}>
              <input type="checkbox" checked={checked} onChange={e=>setDsmPicks(p=>e.target.checked?[...p,code]:p.filter(x=>x!==code))} className="mt-0.5"/>
              <div className="flex-1 min-w-0">
                <p className="text-[11px] font-bold truncate"><span className="font-mono" style={{color:TEAL}}>{code}</span> · {d.nombre}</p>
                <p className="text-[9px] truncate" style={{color:"var(--ns-muted)"}}>{d.dsm5}{d.ci_rango?` · CI ${d.ci_rango}`:""}</p>
              </div>
            </label>})}
          </div>
          <div className="flex items-center justify-between mt-3 pt-3 border-t">
            <p className="text-[10px]" style={{color:"var(--ns-muted)"}}>{dsmPicks.length} seleccionado{dsmPicks.length===1?"":"s"}</p>
            <div className="flex gap-2">
              <button onClick={()=>setDsmPicks([])} className="text-[10px] font-bold px-3 py-1 rounded-full" style={{color:"var(--ns-muted)",background:"var(--ns-subtle)"}}>Limpiar</button>
              <button disabled={dsmPicks.length===0} onClick={()=>{const txt="Impresión diagnóstica final (DSM-5 / CIE-10):\n"+dsmPicks.map(c=>{const d=DSM5_DIAGNOSES[c];return`• ${c} — ${d.nombre}${d.dsm5?` [${d.dsm5}]`:""}`}).join("\n");setObsT(o=>({...o,impresion_diagnostica:(o.impresion_diagnostica?o.impresion_diagnostica+"\n\n":"")+txt}))}} className="text-[10px] font-bold px-3 py-1 rounded-full disabled:opacity-40" style={{background:TEAL,color:"#fff"}}>→ A impresión diagnóstica</button>
            </div>
          </div>
        </Card>
        {/* ─── RECOMENDACIONES POR CUADRO ─── */}
        <Card className="p-6"><div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-extrabold flex items-center gap-2"><I name="lightbulb" style={{color:TEAL}}/>Biblioteca de Recomendaciones</h3>
          <div className="flex items-center gap-2">
            <span className="text-[9px] px-2 py-0.5 rounded-full" style={{background: resvSource === "backend" ? TEAL : "var(--ns-subtle)", color: resvSource === "backend" ? "#fff" : "var(--ns-muted)"}} title={resvSource === "backend" ? "Sincronizado con backend" : "Usando copia local (offline)"}>
              {resvLoading ? "Cargando..." : (resvSource === "backend" ? "v.backend" : "v.local")}
            </span>
            <Sel value={recCuadro} onChange={e=>setRecCuadro(e.target.value)} className="text-xs w-64" disabled={resvLoading}><option value="">— Elegir cuadro —</option>
              {cuadrosResv.map(c=><option key={c.id} value={c.id}>{c.nombre}</option>)}
            </Sel>
          </div>
        </div>
        {!recCuadro?<p className="text-xs" style={{color:"var(--ns-muted)"}}>Seleccione un cuadro para ver recomendaciones listas para incorporar al informe.</p>
        :(()=>{const cuadro=cuadroById[recCuadro] || RECOMMENDATIONS_LIB[recCuadro]; if(!cuadro) return null; return<div className="space-y-3">
          <p className="text-[10px]" style={{color:"var(--ns-muted)"}}>{cuadro.cie ? <><span>CIE-10: <strong>{cuadro.cie}</strong></span></> : null}{cuadro.grupo_label ? <span className="ml-1">— {cuadro.grupo_label}</span> : null}</p>
          {Object.entries(cuadro.categorias).map(([cat,recs])=><div key={cat} className="rounded-xl p-3" style={{background:"var(--ns-subtle)"}}>
            <div className="flex items-center justify-between mb-2">
              <p className="text-[11px] font-extrabold uppercase tracking-wider" style={{color:TEAL}}>{cat.replace(/_/g," ")}</p>
              <button onClick={()=>{const block=recs.map(r=>"• "+r).join("\n");setObsT(o=>({...o,recomendaciones:(o.recomendaciones?o.recomendaciones+"\n\n":"")+`[${cuadro.nombre} · ${cat.replace(/_/g," ")}]\n${block}`}))}} className="text-[9px] font-bold px-2 py-0.5 rounded-full" style={{background:TEAL,color:"#fff"}}>Insertar todas</button>
            </div>
            <ul className="space-y-1.5">{recs.map((r,i)=><li key={i} className="flex items-start gap-2 group">
              <span className="text-teal-500 mt-0.5 shrink-0">•</span>
              <span className="text-xs leading-snug flex-1">{r}</span>
              <button onClick={()=>setObsT(o=>({...o,recomendaciones:(o.recomendaciones?o.recomendaciones+"\n":"")+"• "+r}))} className="opacity-0 group-hover:opacity-100 text-[9px] font-bold px-1.5 py-0.5 rounded transition-all shrink-0" style={{color:TEAL,background:"var(--ns-card)"}} title="Insertar esta recomendación">+</button>
            </li>)}</ul>
          </div>)}
        </div>})()}
        </Card>
      </div>
      {/* Panel lateral: Observaciones */}
      <div className="col-span-12 lg:col-span-5"><div className="sticky top-24 space-y-3">
        <div className="flex items-center justify-between px-1">
          <h3 className="text-base font-bold flex items-center gap-2">Observaciones por Dominio{obsSaved&&<span className="text-xs text-teal-600 font-normal ml-2 animate-pulse">Guardadas</span>}</h3>
          <button onClick={autocompletarTodo} className="text-[10px] font-bold px-3 py-1.5 rounded-full flex items-center gap-1.5 hover:scale-105 transition-all" style={{background:`linear-gradient(135deg,${TEAL},${TEAL_LIGHT})`,color:"#fff"}} title="Generar borradores automáticos"><I name="auto_awesome" className="text-xs"/>Auto-generar</button>
        </div>

        {/* §ai-asistente (2026-05-18): asistente IA con 6 prompts especializados.
          * Contexto pasado: edad, escolaridad, puntajes, observaciones, dominios bajos.
          * Permite generar hipótesis dx, narrativa integradora, recomendaciones,
          * explicar discrepancias o adaptar a lenguaje pediátrico. */}
        {res && (
          <AIAsistente
            context={{
              edad: res?.edad_display || "",
              escolaridad: res?.patient_info?.escolaridad || "",
              motivo: res?.patient_info?.motivo_consulta || "",
              puntajes: (res?.resultados || []).map(r =>
                `${r.test_nombre}: z=${r.z_equivalente?.toFixed(2) ?? "—"} (${r.interpretacion})`
              ).join("\n"),
              dominios: indices.map(c => `${c.n}: ${c.v} (${c.i})`).join("\n"),
              dominios_bajos: (res?.puntos_debiles || []).join("\n"),
              fortalezas: (res?.puntos_fuertes || []).join("\n"),
              observaciones: Object.entries(obsT).filter(([, v]) => v?.trim()).map(([k, v]) => `[${k}] ${v}`).join("\n\n"),
              texto: Object.values(obsT).filter(v => v?.trim()).join("\n\n"),
            }}
          />
        )}

        <div className="space-y-2 max-h-[calc(100vh-220px)] overflow-y-auto pr-1">{obsDoms.map(([k,l])=><Card key={k} className="p-4">
          <div className="flex items-center justify-between mb-1"><Label className="text-xs">{l}</Label>
            <div className="flex gap-1">
              <button onClick={()=>setObsT(o=>({...o,[k]:generarObservacion(k)}))} className="text-[9px] font-bold px-2 py-0.5 rounded hover:bg-teal-50" style={{color:TEAL}} title="Generar plantilla para este dominio"><I name="auto_fix_high" className="text-xs"/>Plantilla</button>
              <button onClick={()=>mejorarDominioIA(k,"style")} disabled={aiBusy===k+":style"||!obsT[k]} className="text-[9px] font-bold px-2 py-0.5 rounded hover:bg-teal-50 disabled:opacity-40" style={{color:TEAL}} title="Corregir estilo/gramática con IA">{aiBusy===k+":style"?"…":<><I name="auto_awesome" className="text-xs"/>Estilo</>}</button>
              <button onClick={()=>mejorarDominioIA(k,"clinical_review")} disabled={aiBusy===k+":clinical_review"||!obsT[k]} className="text-[9px] font-bold px-2 py-0.5 rounded hover:bg-amber-50 disabled:opacity-40" style={{color:"#B45309"}} title="Revisión clínica con IA">{aiBusy===k+":clinical_review"?"…":<><I name="medical_services" className="text-xs"/>Revisar</>}</button>
              {OBS_TEMPLATES[k]&&<select onChange={e=>{if(e.target.value)setObsT(o=>({...o,[k]:(o[k]||"")+(o[k]?"\n\n":"")+e.target.value}));e.target.value=""}} className="text-[9px] font-bold px-1.5 py-0.5 rounded hover:bg-gray-50 cursor-pointer" style={{color:"var(--ns-muted)",background:"var(--ns-subtle)"}} title="Insertar plantilla"><option value="">⊕ Plantilla</option>{OBS_TEMPLATES[k].map((t,i)=><option key={i} value={t}>{t.slice(0,50)}...</option>)}</select>}
            </div>
          </div>
          <Txta value={obsT[k]} onChange={e=>setObsT(o=>({...o,[k]:e.target.value}))} placeholder={`${l}...`} className="min-h-[70px] text-xs"/>
        </Card>)}</div>
        <div className="flex flex-wrap gap-2 pt-3">
          <Btn v="outline" onClick={()=>nav("eval_apply",{puntajes:evalCtx.puntajes,obs:evalCtx.obs})} className="text-xs">← Puntajes</Btn>
          <Btn v="outline" onClick={exportResults} className="text-xs"><I name="download" className="text-sm"/>CSV</Btn>
          <Btn v="secondary" className="flex-1 text-xs" onClick={saveObs} disabled={savingObs}>{savingObs?"Guardando...":"Guardar"}</Btn>
          <Sel value={pdfTemplate} onChange={e=>setPdfTemplate(e.target.value)} className="text-xs" title="Plantilla del informe PDF" style={{maxWidth:"200px"}}>
            <option value="pro">★ Profesional (recomendada)</option>
            <option value="pediatrico">Pediátrica</option>
            <option value="medicolegal">Medicolegal</option>
            <option value="junta_medica">Junta Médica (corta)</option>
            <option value="inconcluso">Inconclusa</option>
            <option value="therapy_closure">Cierre terapéutico</option>
            <option value="estandar">Estándar (legado)</option>
          </Sel>
          <Btn className="flex-1 text-xs" onClick={downloadPdf} disabled={genPdf||!puedeDescargarPDF} title={razonBloqueoPDF||`Descargar PDF (plantilla: ${pdfTemplate})`}>{genPdf?"Generando...":"PDF"}</Btn>
          <Btn v="outline" className="text-xs" onClick={downloadDocx} disabled={genDocx||!evalId} title="Informe editable en Word"><I name="description" className="text-sm"/>{genDocx?"...":"DOCX"}</Btn>
          <Btn v="outline" className="text-xs" onClick={downloadXlsx} disabled={genXlsx||!evalId} title="Matriz de puntajes en Excel"><I name="grid_on" className="text-sm"/>{genXlsx?"...":"XLSX"}</Btn>
          {evalId&&<ShareButton evaluationId={evalId}/>}
          {evalId&&<SecondOpinionButton evaluationId={evalId}/>}
          {evalId&&<Btn v="outline" onClick={async()=>{try{const sug=await api.get(`/api/v1/rehab/suggest/${evalId}`);if(!sug.dominios_sugeridos.length){toast.info("No se detectaron dominios bajos en esta evaluación.");return}localStorage.setItem("ns_rehab_suggestion",JSON.stringify({...sug,from_eval:evalId}));setPage("rehab")}catch(e){toast.error("Error: "+_parseError(e))}}} className="text-xs"><I name="fitness_center" className="text-sm"/>Iniciar Rehabilitación</Btn>}
        </div>
        {/* ─── Marcar como Informe Inconcluso ─── */}
        <div className="pt-3 border-t" style={{borderColor:"var(--ns-card-b)"}}>
          {incMsg==="ok"&&<p className="text-xs mb-2 p-2 rounded" style={{background:"#dcfce7",color:"#166534"}}><I name="check_circle" className="text-xs"/> Informe marcado como inconcluso. Aparecerá en el seguimiento del paciente.</p>}
          {incMsg&&incMsg!=="ok"&&<p className="text-xs mb-2 p-2 rounded bg-red-50 text-red-700">{incMsg}</p>}
          {!showIncForm?<button onClick={()=>setShowIncForm(true)} className="w-full text-[11px] font-bold py-2 rounded-lg border border-dashed flex items-center justify-center gap-1.5" style={{borderColor:"#d97706",color:"#d97706",background:"rgba(217,119,6,0.05)"}}><I name="flag" className="text-sm"/>Marcar este informe como inconcluso</button>
          :<Card className="p-4 space-y-3" style={{background:"rgba(217,119,6,0.06)",borderLeft:"3px solid #d97706"}}>
            <div className="flex items-center justify-between"><p className="text-xs font-extrabold" style={{color:"#b45309"}}>Motivo del informe inconcluso</p>
              <button onClick={()=>{setShowIncForm(false);setIncMsg("")}} className="text-xs text-gray-400 hover:text-gray-700" aria-label="Cancelar marcar como inconcluso" title="Cancelar"><I name="close" className="text-sm"/></button></div>
            <Sel value={incMotivo} onChange={e=>setIncMotivo(e.target.value)} className="text-xs">{INCONCLUSO_REASONS.map(m=><option key={m.id} value={m.id}>{m.titulo}</option>)}</Sel>
            <p className="text-[10px] leading-snug" style={{color:"var(--ns-muted)"}}><strong>Acción sugerida:</strong> {INCONCLUSO_REASONS.find(m=>m.id===incMotivo)?.accion} <span className="ml-1 font-bold">(plazo {INCONCLUSO_REASONS.find(m=>m.id===incMotivo)?.plazo_dias} días)</span></p>
            <Txta value={incDesc} onChange={e=>setIncDesc(e.target.value)} placeholder="Notas adicionales (opcional)..." className="text-xs min-h-[60px]"/>
            <Btn v="danger" className="w-full text-xs" onClick={marcarInconcluso} disabled={incSaving}>{incSaving?"Guardando...":"Confirmar y marcar"}</Btn>
          </Card>}
        </div>
      </div></div>
    <ClinicalDisclaimer modo="footer" className="px-6 py-2"/>
    </div></main></>);
}
