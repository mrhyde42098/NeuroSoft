import React,{useState,useEffect,lazy,Suspense}from"react";
import{api}from"./api/client.js";
/* §lazy: imports eager solo para los componentes críticos al primer render.
 * Las páginas grandes se cargan bajo demanda con React.lazy → reduce
 * el bundle inicial de 795 KB a ~250 KB (las rutas se traen al navegar). */
import LoginPage from"./app/auth/LoginPage.jsx";
import DashboardPage from"./app/dashboard/DashboardPage.jsx";
import SidebarLayout from"./app/layout/Sidebar.jsx";
import {AIFloatingChat} from"./app/ia/PanelIA";
import{SharedViewer}from"./app/compartir/PanelCompartir";
import PublicRehabViewer from"./app/rehab/PublicRehabViewer.jsx";
import {AuthProvider as ExtAuthProvider,DarkProvider as ExtDarkProvider,ToastProvider as ExtToastProvider,ConfirmProvider as ExtConfirmProvider,A11yProvider as ExtA11yProvider,useAuth as extUseAuth,useDark as extUseDark,useToast as extUseToast} from"./contexts.jsx";
import ExtErrorBoundary from"./ui/ErrorBoundary.jsx";
import{SHORTCUTS}from"./data/ui.js";
import{safeLS}from"./utils/safeLS.js";
import{SkipToMain}from"./ui/a11y.jsx";
import PearsonConsentDialog from"./ui/PearsonConsentDialog.jsx";
import{usePearsonConsent}from"./hooks/usePearsonConsent.js";

/* §lazy: páginas cargadas bajo demanda. Cada una se descarga al primer setPage(). */
const AIConfigPage     = lazy(() => import("./app/ia/PanelIA").then(m => ({default: m.AIConfigPage})));
const SharesPage       = lazy(() => import("./app/compartir/PanelCompartir").then(m => ({default: m.SharesPage})));
const RehabPage        = lazy(() => import("./app/rehab/RehabPage.jsx"));
const PatientsPage     = lazy(() => import("./app/patients/PatientsPage.jsx"));
const RegisterPage     = lazy(() => import("./app/patients/RegisterPage.jsx"));
const AgendaPage       = lazy(() => import("./app/agenda/AgendaPage.jsx"));
const InformesPage     = lazy(() => import("./app/reports/InformesPage.jsx"));
const HistorialPage    = lazy(() => import("./app/history/HistorialPage.jsx"));
const ScreeningPage    = lazy(() => import("./app/evaluation/ScreeningPage.jsx"));
const ComparePage      = lazy(() => import("./app/history/ComparePage.jsx"));
const ConfigPage       = lazy(() => import("./app/config/ConfigPage.jsx"));
const HelpPage         = lazy(() => import("./app/help/HelpPage.jsx"));
const EvalApplyPage    = lazy(() => import("./app/evaluation/EvalApplyPage.jsx"));
const EvalResultsPage  = lazy(() => import("./app/evaluation/EvalResultsPage.jsx"));
const ClinicalHistoryPage = lazy(() => import("./app/patients/ClinicalHistoryPage.jsx"));
const TherapyPage         = lazy(() => import("./app/therapy/TherapyPage.jsx"));
const BibliotecaPage      = lazy(() => import("./app/aprender/BibliotecaPage.jsx"));
const PruebasDisponiblesPage = lazy(() => import("./app/aprender/PruebasDisponiblesPage.jsx"));
/* §M-2 Módulo Aprender — pilar 3 educativo */
const AprenderHub         = lazy(() => import("./app/aprender/AprenderHub.jsx"));
const GlosarioPage        = lazy(() => import("./app/aprender/GlosarioPage.jsx"));
const EstudiarPage        = lazy(() => import("./app/aprender/EstudiarPage.jsx"));
const QuizPage            = lazy(() => import("./app/aprender/QuizPage.jsx"));
const ArticulosPage       = lazy(() => import("./app/aprender/ArticulosPage.jsx"));
const SimuladorPage       = lazy(() => import("./app/aprender/SimuladorPage.jsx"));
const ReferenciasPage    = lazy(() => import("./app/referencias/ReferenciasPage.jsx"));  // §F2
const EstadisticasPage   = lazy(() => import("./app/dashboard/EstadisticasPage.jsx"));
const RipsPage           = lazy(() => import("./app/reports/RipsPage.jsx"));
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
  const[page,setPage]=useState("dashboard");
  const[pageKey,setPageKey]=useState(0);
  const[evalCtx,setEvalCtx]=useState({patientId:null,puntajes:{},obs:{},proto:"wisc_iv",protoNombre:"WISC-IV",scoringResult:null});
  const{toggle}=useDark();
  const toast=useToast();
  const pearson=usePearsonConsent();
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
  const pages={dashboard:<DashboardPage setPage={setPageNav}/>,estadisticas:<EstadisticasPage setPage={setPageNav}/>,rips:<RipsPage setPage={setPageNav}/>,patients:<PatientsPage setPage={setPageNav} nav={nav} setEvalCtx={setEvalCtx}/>,register:<RegisterPage setPage={setPageNav}/>,clinical_history:<ClinicalHistoryPage setPage={setPageNav}/>,evaluation:<EvalApplyPage setPage={setPageNav} nav={nav} evalCtx={evalCtx} setEvalCtx={setEvalCtx}/>,eval_apply:<EvalApplyPage setPage={setPageNav} nav={nav} evalCtx={evalCtx} setEvalCtx={setEvalCtx}/>,eval_results:<EvalResultsPage setPage={setPageNav} nav={nav} evalCtx={evalCtx} setEvalCtx={setEvalCtx}/>,history:<HistorialPage setPage={setPageNav}/>,agenda:<AgendaPage setPage={setPageNav}/>,reports:<InformesPage setPage={setPageNav}/>,compare:<ComparePage setPage={setPageNav}/>,screening:<ScreeningPage setPage={setPageNav}/>,rehab:<RehabPage/>,therapy:<TherapyPage setPage={setPageNav}/>,biblioteca:<BibliotecaPage/>,pruebas:<PruebasDisponiblesPage/>,pruebas_disponibles:<PruebasDisponiblesPage/>,aprender:<AprenderHub setPage={setPageNav}/>,aprender_glosario:<GlosarioPage/>,aprender_estudiar:<EstudiarPage/>,aprender_quiz:<QuizPage/>,aprender_articulos:<ArticulosPage/>,aprender_simulador:<SimuladorPage/>,referencias:<ReferenciasPage/>,ai:<AIConfigPage/>,shares:<SharesPage/>,config:<ConfigPage setPage={setPageNav}/>,help:<HelpPage/>,help_changelog:<HelpPage section="changelog"/>};
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
      <AIFloatingChat/>
      <PearsonConsentDialog
        open={!pearson.aceptado}
        mode="firstInstall"
        user={null}
        onClose={(acepto)=>{if(acepto)pearson.refresh()}}
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
