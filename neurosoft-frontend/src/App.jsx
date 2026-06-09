import React,{useState,useEffect,lazy,Suspense}from"react";
import{api}from"./api/client.js";
import LazyRoute,{pageLoader}from"./ui/LazyRoute.jsx";
/* §lazy: imports eager solo para los componentes críticos al primer render.
 * Las páginas grandes se cargan bajo demanda con React.lazy → reduce
 * el bundle inicial de 795 KB a ~250 KB (las rutas se traen al navegar). */
import LoginPage from"./app/auth/LoginPage.jsx";
import DashboardPage from"./app/dashboard/DashboardPage.jsx";
import SidebarLayout from"./app/layout/Sidebar.jsx";
import{SharedViewer}from"./app/compartir/PanelCompartir";
import PublicRehabViewer from"./app/rehab/PublicRehabViewer.jsx";
import {AuthProvider as ExtAuthProvider,DarkProvider as ExtDarkProvider,ToastProvider as ExtToastProvider,ConfirmProvider as ExtConfirmProvider,A11yProvider as ExtA11yProvider,useAuth as extUseAuth,useDark as extUseDark,useToast as extUseToast} from"./contexts.jsx";
import ExtErrorBoundary from"./ui/ErrorBoundary.jsx";
import{SHORTCUTS}from"./data/ui.js";
import{safeLS}from"./utils/safeLS.js";
import{SkipToMain}from"./ui/a11y.jsx";
import PearsonConsentDialog from"./ui/PearsonConsentDialog.jsx";
import{usePearsonConsent}from"./hooks/usePearsonConsent.js";

/* §lazy: chat flotante bajo demanda; rutas con React 19 use() vía LazyRoute */
const AIFloatingChat = lazy(() => import("./app/ia/PanelIA.jsx").then(m => ({ default: m.AIFloatingChat })));

/* React 19 use() — loaders cacheados para LazyRoute */
const loadEstadisticas   = pageLoader(() => import("./app/dashboard/EstadisticasPage.jsx"));
const loadRips           = pageLoader(() => import("./app/reports/RipsPage.jsx"));
const loadPatients       = pageLoader(() => import("./app/patients/PatientsPage.jsx"));
const loadRegister       = pageLoader(() => import("./app/patients/RegisterPage.jsx"));
const loadClinicalHist   = pageLoader(() => import("./app/patients/ClinicalHistoryPage.jsx"));
const loadEvalApply      = pageLoader(() => import("./app/evaluation/EvalApplyPage.jsx"));
const loadEvalResults    = pageLoader(() => import("./app/evaluation/EvalResultsPage.jsx"));
const loadHistorial      = pageLoader(() => import("./app/history/HistorialPage.jsx"));
const loadAgenda         = pageLoader(() => import("./app/agenda/AgendaPage.jsx"));
const loadInformes       = pageLoader(() => import("./app/reports/InformesPage.jsx"));
const loadCompare        = pageLoader(() => import("./app/history/ComparePage.jsx"));
const loadScreening      = pageLoader(() => import("./app/evaluation/ScreeningPage.jsx"));
const loadRehab          = pageLoader(() => import("./app/rehab/RehabPage.jsx"));
const loadTherapy        = pageLoader(() => import("./app/therapy/TherapyPage.jsx"));
const loadBiblioteca     = pageLoader(() => import("./app/aprender/BibliotecaPage.jsx"));
const loadPruebas        = pageLoader(() => import("./app/aprender/PruebasDisponiblesPage.jsx"));
const loadAprender       = pageLoader(() => import("./app/aprender/AprenderHub.jsx"));
const loadGlosario       = pageLoader(() => import("./app/aprender/GlosarioPage.jsx"));
const loadEstudiar       = pageLoader(() => import("./app/aprender/EstudiarPage.jsx"));
const loadQuiz           = pageLoader(() => import("./app/aprender/QuizPage.jsx"));
const loadArticulos      = pageLoader(() => import("./app/aprender/ArticulosPage.jsx"));
const loadSimulador      = pageLoader(() => import("./app/aprender/SimuladorPage.jsx"));
const loadReferencias    = pageLoader(() => import("./app/referencias/ReferenciasPage.jsx"));
const loadAIConfig       = pageLoader(() => import("./app/ia/PanelIA.jsx").then(m => ({ default: m.AIConfigPage })));
const loadShares         = pageLoader(() => import("./app/compartir/PanelCompartir.jsx").then(m => ({ default: m.SharesPage })));
const loadConfig         = pageLoader(() => import("./app/config/ConfigPage.jsx"));
const loadHelp           = pageLoader(() => import("./app/help/HelpPage.jsx"));
const loadProtocolos     = pageLoader(() => import("./app/aprender/ProtocolosPage.jsx"));
/* Auth/Dark/Toast/ErrorBoundary ahora viven en src/contexts.jsx y src/ui/.
 * Mantenemos los identificadores con re-asignaciones para no tocar las
 * 19 páginas que aún viven en este archivo. */
const AuthProvider = ExtAuthProvider;
const DarkProvider = ExtDarkProvider;
const ToastProvider = ExtToastProvider;
const A11yProvider = ExtA11yProvider;
const useAuth = extUseAuth;
const useDark = extUseDark;
const useToast = extUseToast;
const ErrorBoundary = ExtErrorBoundary;


/* ── Keyboard Shortcuts ── */

/* ── Observation Templates ── */

/* ── Screening Forms Data ── */
/* SCREENING_FORMS extraído a src/data/screening.js */

/* ── Discrepancy significance table (WISC-IV) ── */

/* ── Shared ── */
const I=({name,fill,className="",style})=><span className={`material-symbols-outlined ${className}`} style={{...(fill?{fontVariationSettings:"'FILL' 1"}:{}),...style}}>{name}</span>;
const TEAL="#0D9488";const TEAL_LIGHT="#67E8F9";const NAVY="#1E293B";
/* SVG Brain Logo — coherent brand mark */
const BrainLogo=({size=40,className=""})=>(
<svg viewBox="0 0 64 64" width={size} height={size} className={className} xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="bl" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stopColor={TEAL}/><stop offset="100%" stopColor={TEAL_LIGHT}/></linearGradient></defs>
  <rect width="64" height="64" rx="14" fill={NAVY}/>
  <path d="M32 12c-8 0-15 5.5-15 14 0 4 1.5 7 4 9.5 1.5 1.5 2 3.5 2 5.5v3c0 2 1.5 3 3 3h12c1.5 0 3-1 3-3v-3c0-2 .5-4 2-5.5 2.5-2.5 4-5.5 4-9.5 0-8.5-7-14-15-14z" fill="none" stroke="url(#bl)" strokeWidth="2.5" strokeLinecap="round"/>
  <circle cx="32" cy="22" r="2" fill={TEAL_LIGHT}/>
  <path d="M32 22v6M32 28l-5 4M32 28l5 4M26 20l6 2M38 20l-6 2" stroke={TEAL} strokeWidth="1.5" strokeLinecap="round"/>
  <rect x="25" y="48" width="14" height="2" rx="1" fill={`${TEAL}80`}/>
  <rect x="27" y="52" width="10" height="2" rx="1" fill={`${TEAL}60`}/>
</svg>);
/* §dead-code-fix (2026-05-18): componentes locales Card/Label/Input/Sel/Txta/Btn/MsgBanner/TOPBar/lc
 * eliminados. La app usa los de primitives.jsx y colores.js importados via contexts. */
/* §audit-meta-2026-05: mantener solo lo esencial en este archivo. */

/* Sidebar — implementación extraída a src/app/layout/Sidebar.jsx.
 * Aquí solo dejamos el wrapper que inyecta los hooks/contextos y los
 * tokens de marca. Mantiene el contrato `<Sidebar page={…} setPage={…}/>`
 * para que AppShell no requiera cambios. */
function Sidebar({page,setPage}){
  const{logout,user}=useAuth();
  const{dark,toggle}=useDark();
  return <SidebarLayout page={page} setPage={setPage}
    user={user} logout={logout} dark={dark} toggle={toggle}
    shortcuts={SHORTCUTS}
    BrainLogo={BrainLogo} I={I} TEAL={TEAL} NAVY={NAVY}/>;
}

function AppShell(){
  const{user}=useAuth();
  const[page,setPage]=useState("dashboard");
  const[pageKey,setPageKey]=useState(0);
  const[evalCtx,setEvalCtx]=useState({patientId:null,puntajes:{},obs:{},proto:"wisc_iv",protoNombre:"WISC-IV",scoringResult:null});
  const{toggle}=useDark();
  const toast=useToast();
  const pearson=usePearsonConsent();
  const[agreement,setAgreement]=useState(null);
  const[lic,setLic]=useState(null);
  useEffect(()=>{
    let cancelled=false;
    Promise.all([
      api.get("/api/v1/license/agreement-status").catch(()=>null),
      api.get("/api/v1/license/status").catch(()=>null),
    ]).then(([a,l])=>{if(!cancelled){setAgreement(a);setLic(l);}});
    return()=>{cancelled=true;};
  },[]);
  const skipAgreement=user?.role==="admin"||lic?.is_master||lic?.dev_mode;
  const showAgreement=!skipAgreement&&agreement&&!agreement.accepted;
  const nav=(p,data)=>{if(data)setEvalCtx(c=>({...c,...data}));setPage(p);setPageKey(k=>k+1)};
  /* Polling de tarea-casa: notifica al clínico cuando un paciente
   * completa una actividad desde el link público. Cada 90 s. */
  useEffect(()=>{
    const KEY="ns_last_homework_check";
    let last=parseInt(safeLS.get(KEY)||"0",10);
    if(!last){last=Date.now();safeLS.set(KEY,String(last))}
    const tick=async()=>{
      try{
        const panel=await api.get("/api/v1/patients/panel?por_pagina=50").catch(()=>null);
        /* §B9-fix: si falla la consulta, igualmente avanzar `last` para
         * no quedar atascado en una ventana vieja que genere falsos
         * "nuevos" cuando vuelva el server. */
        if(!panel||!panel.pacientes){last=Date.now();safeLS.set(KEY,String(last));return}
        const stamp=Date.now();
        const since=last;
        let nuevas=0;const detalles=[];
        await Promise.all(panel.pacientes.slice(0,15).map(async p=>{
          const sess=await api.get(`/api/v1/rehab/sessions/by-patient/${p.id}?limit=10`).catch(()=>null);
          if(!sess)return;
          for(const s of sess){
            if(s.modo!=="tarea_casa")continue;
            const t=new Date(s.ts_inicio).getTime();
            if(t>since){nuevas++;detalles.push({paciente:p.nombre_completo||"Paciente",slug:s.activity_slug,score:s.score})}
          }
        }));
        if(nuevas>0){
          /* Notificación nativa si está concedida */
          if(typeof Notification!=="undefined"&&Notification.permission==="granted"){
            try{new Notification("Tareas en casa completadas — NeuroSoft",{body:`${nuevas} actividad(es) recibida(s).`,icon:"/favicon.ico",tag:"rehab_homework",requireInteraction:false})}catch(e){/* §B7-fix: visibilidad mínima si el navegador revoca permisos a media sesión. */try{console.debug("[NeuroSoft] Notification falló:",e)}catch{}}
          }
          /* Toast in-app: siempre */
          toast.success(`${nuevas} actividad(es) de rehabilitación completada(s) por tus pacientes.`);
        }
        last=stamp;
        safeLS.set(KEY,String(stamp));
      }catch(err){/* §M4-fix: visibilidad mínima para diagnóstico. */if(typeof console!=="undefined")console.warn("[NeuroSoft] Polling tarea-casa falló:",err)}
    };
    /* Tick inicial a los 30 s para no saturar el arranque */
    const t1=setTimeout(tick,30000);
    const t2=setInterval(tick,90000);
    return()=>{clearTimeout(t1);clearInterval(t2)};
  },[toast]);
  /* Keyboard shortcuts global */
  /* §A1-fix: guard adicional contra contentEditable (editor IA / informes inline). */
  useEffect(()=>{const handler=e=>{if(!e.altKey)return;const tag=(e.target?.tagName||"").toLowerCase();if(tag==="input"||tag==="textarea"||tag==="select")return;if(e.target?.isContentEditable)return;const sc=SHORTCUTS.find(s=>s.key.toLowerCase()===e.key.toLowerCase());if(sc){e.preventDefault();if(sc.page){setPage(sc.page);setPageKey(k=>k+1);}else if(sc.action==="dark")toggle();else if(sc.action==="shortcuts"){/* show shortcuts - handled in sidebar */}}};window.addEventListener("keydown",handler);return()=>window.removeEventListener("keydown",handler)},[toggle]);
  const setPageNav=(p)=>{setPage(p);setPageKey(k=>k+1)};
  const pages={
    dashboard:<DashboardPage setPage={setPageNav}/>,
    estadisticas:<LazyRoute load={loadEstadisticas} setPage={setPageNav}/>,
    rips:<LazyRoute load={loadRips} setPage={setPageNav}/>,
    patients:<LazyRoute load={loadPatients} setPage={setPageNav} nav={nav} setEvalCtx={setEvalCtx}/>,
    register:<LazyRoute load={loadRegister} setPage={setPageNav}/>,
    clinical_history:<LazyRoute load={loadClinicalHist} setPage={setPageNav}/>,
    evaluation:<LazyRoute feature="Evaluación" load={loadEvalApply} setPage={setPageNav} nav={nav} evalCtx={evalCtx} setEvalCtx={setEvalCtx}/>,
    eval_apply:<LazyRoute feature="Evaluación" load={loadEvalApply} setPage={setPageNav} nav={nav} evalCtx={evalCtx} setEvalCtx={setEvalCtx}/>,
    eval_results:<LazyRoute feature="Resultados" load={loadEvalResults} setPage={setPageNav} nav={nav} evalCtx={evalCtx} setEvalCtx={setEvalCtx}/>,
    history:<LazyRoute load={loadHistorial} setPage={setPageNav}/>,
    agenda:<LazyRoute load={loadAgenda} setPage={setPageNav}/>,
    reports:<LazyRoute feature="Informes" load={loadInformes} setPage={setPageNav}/>,
    compare:<LazyRoute load={loadCompare} setPage={setPageNav}/>,
    screening:<LazyRoute load={loadScreening} setPage={setPageNav}/>,
    rehab:<LazyRoute feature="Rehabilitación" load={loadRehab}/>,
    therapy:<LazyRoute feature="Terapia" load={loadTherapy} setPage={setPageNav}/>,
    biblioteca:<LazyRoute load={loadBiblioteca}/>,
    pruebas:<LazyRoute load={loadPruebas}/>,
    pruebas_disponibles:<LazyRoute load={loadPruebas}/>,
    aprender:<LazyRoute load={loadAprender} setPage={setPageNav}/>,
    aprender_glosario:<LazyRoute load={loadGlosario}/>,
    aprender_estudiar:<LazyRoute load={loadEstudiar}/>,
    aprender_quiz:<LazyRoute load={loadQuiz}/>,
    aprender_articulos:<LazyRoute load={loadArticulos}/>,
    aprender_simulador:<LazyRoute load={loadSimulador}/>,
    aprender_protocolos:<LazyRoute load={loadProtocolos}/>,
    referencias:<LazyRoute load={loadReferencias}/>,
    ai:<LazyRoute feature="Inteligencia artificial" load={loadAIConfig}/>,
    shares:<LazyRoute load={loadShares}/>,
    config:<LazyRoute load={loadConfig} setPage={setPageNav}/>,
    help:<LazyRoute load={loadHelp}/>,
    help_changelog:<LazyRoute load={loadHelp} section="changelog"/>,
  };
  return(
    <div className="flex min-h-screen" style={{background:"var(--ns-bg)",color:"var(--ns-text)",fontFamily:"'Manrope',sans-serif"}}>
      <SkipToMain/>
      <Sidebar page={page} setPage={setPageNav}/>
      <main id="ns-main-content" tabIndex={-1} className="flex-1 ml-72 focus:outline-none" aria-label="Contenido principal">
        <div key={pageKey} className="ns-page-in">
          <Suspense fallback={<div className="p-8 flex items-center justify-center h-64" role="status" aria-live="polite"><div className="animate-spin w-10 h-10 border-4 border-teal-200 border-t-teal-600 rounded-full" aria-hidden="true"/></div>}>
            {pages[page]||pages.dashboard}
          </Suspense>
        </div>
      </main>
      <Suspense fallback={null}>
        <AIFloatingChat/>
      </Suspense>
      <PearsonConsentDialog
        open={showAgreement}
        mode="firstInstall"
        user={user}
        onClose={async(acepto)=>{
          if(acepto){
            try{
              await api.post("/api/v1/license/accept-agreement",{});
              pearson.aceptar(user?.id,user?.nombre_completo||user?.username);
              setAgreement(a=>({...a,accepted:true,version:agreement?.current_version}));
            }catch{pearson.refresh();}
          }
        }}
      />
    </div>
  );
}
export default function App(){return<ErrorBoundary><A11yProvider><DarkProvider><ToastProvider><ExtConfirmProvider><AuthProvider><Router/></AuthProvider></ExtConfirmProvider></ToastProvider></DarkProvider></A11yProvider></ErrorBoundary>}
function Router(){
  /* Rutas públicas (sin login):
   *   • /shared/view/{token}   → informe compartido (telemedicina)
   *   • /shared/rehab/{token}  → actividades de rehabilitación (tarea-casa)
   *
   * §hooks-fix (2026-05-18): useAuth() debe llamarse SIEMPRE antes de
   * los returns condicionales (rules-of-hooks). Antes la llamada estaba
   * después de dos `if (return)` — funcionaba por casualidad porque las
   * rutas públicas no se cambian dinámicamente, pero ESLint lo marcaba. */
  const{user}=useAuth();
  const path=typeof window!=="undefined"?window.location.pathname:"";
  const sharedMatch=path.match(/^\/shared\/view\/([A-Za-z0-9_-]+)\/?$/);
  if(sharedMatch)return<SharedViewer token={sharedMatch[1]}/>;
  const rehabMatch=path.match(/^\/shared\/rehab\/([A-Za-z0-9_-]+)\/?$/);
  if(rehabMatch)return<PublicRehabViewer token={rehabMatch[1]}/>;
  if(!user)return<LoginPage/>;return<AppShell/>
}
