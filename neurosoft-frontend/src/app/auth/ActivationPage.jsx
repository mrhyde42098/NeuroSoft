/* ═══════════════════════════════════════════════════════════════════════
 * src/app/auth/ActivationPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §BLINDAJE-N1 — Pantalla de activación de licencia.
 *
 * Se muestra antes del login. Permite:
 *  - Ingresar clave de licencia (NSFT-XXXX-XXXX-XXXX-XXXX)
 *  - Iniciar prueba gratuita de 14 días
 *
 * Si la licencia ya es válida, redirige directamente al login.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, {useEffect,useState} from "react";
import {api} from "../../api/client.js";
import {Card,I,Input,Btn,MsgBanner} from "../../ui/primitives.jsx";
import {TEAL} from "../../ui/tokens.js";

export default function ActivationPage({onActivated}) {
  const [key,setKey]=useState("");
  const [busy,setBusy]=useState(false);
  const [msg,setMsg]=useState(null);
  const [status,setStatus]=useState(null);
  const [brand,setBrand]=useState({nombre:"",subtitle:"Evaluación neuropsicológica clínica",logo_base64:null});

  /* Marca institucional (configurable en Configuración → Institución) */
  useEffect(()=>{
    let cancelled = false;
    api.get("/api/v1/config/branding").then(b=>{
      if (!cancelled && b) setBrand(b);
    }).catch(()=>{});
    return ()=>{cancelled=true;};
  },[]);

  /* Verificar si ya hay licencia valida */
  useEffect(()=>{
    let cancelled = false;
    api.get("/api/v1/license/status").then(s=>{
      if (!cancelled && s.valid) onActivated?.();
      if (!cancelled) setStatus(s);
    }).catch(()=>{if(!cancelled)setStatus(null);});
    return ()=>{cancelled=true;};
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[]);

  /* Activar con clave */
  const activate=async()=>{
    if(!key.trim()){setMsg({text:"Ingrese una clave de licencia.",type:"warn"});return}
    setBusy(true);setMsg(null);
    try{
      const r=await api.post("/api/v1/license/activate",{key:key.trim().toUpperCase()});
      setMsg({text:r.message,type:"ok"});
      setTimeout(()=>onActivated?.(),1200);
    }catch(e){
      setMsg({text:e.detail||"Error al activar la licencia.",type:"error"});
    }
    setBusy(false);
  };

  /* Iniciar prueba gratuita */
  const startTrial=async()=>{
    setBusy(true);setMsg(null);
    try{
      const r=await api.post("/api/v1/license/trial",{days:14});
      setMsg({text:r.message,type:"ok"});
      setTimeout(()=>onActivated?.(),1200);
    }catch(e){
      setMsg({text:e.detail||"Error al iniciar la prueba.",type:"error"});
    }
    setBusy(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{background:"linear-gradient(135deg,#0a1929,#0d4f4f)"}}>
      <Card className="max-w-md w-full p-8 space-y-6 text-center">
        {/* Logo */}
        <div className="flex justify-center">
          {brand.logo_base64 ? (
            <img src={brand.logo_base64} alt="" className="h-16 max-w-[200px] object-contain"/>
          ) : (
            <div className="w-16 h-16 rounded-xl flex items-center justify-center" style={{background:`${TEAL}15`}}>
              <I name="neurology" fill style={{color:TEAL,fontSize:36}}/>
            </div>
          )}
        </div>

        <div>
          <h1 className="ns-serif text-2xl font-bold">
            {brand.nombre || "Activación del sistema"}
          </h1>
          <p className="text-xs mt-1" style={{color:"var(--ns-muted)"}}>
            {brand.subtitle}
          </p>
        </div>

        {/* Estado actual */}
        {status&&!status.valid&&status.days_remaining!=null&&status.days_remaining<=3&&status.is_trial&&(
          <MsgBanner msg={{text:`Tu prueba expira en ${status.days_remaining} días. Activa una licencia para continuar.`,type:"warn"}}/>
        )}

        {/* Formulario de activación */}
        <div className="space-y-3">
          <div className="text-left">
            <label className="text-xs font-bold" style={{color:"var(--ns-muted)"}}>
              Clave de licencia
            </label>
            <Input
              value={key}
              onChange={e=>setKey(e.target.value)}
              placeholder="NSFT-XXXX-XXXX-XXXX-XXXX"
              className="ns-mono text-sm text-center tracking-wider"
              style={{letterSpacing:"2px"}}
              disabled={busy}
              onKeyDown={e=>e.key==="Enter"&&activate()}
            />
          </div>

          <Btn onClick={activate} disabled={busy||!key.trim()} className="w-full py-2.5"
            style={{background:TEAL,color:"#fff",borderColor:TEAL}}>
            <I name="vpn_key" className="text-sm"/> Activar licencia
          </Btn>

          <div className="flex items-center gap-2 py-1">
            <div className="flex-1 h-px" style={{background:"var(--ns-card-b)"}}/>
            <span className="text-[10px]" style={{color:"var(--ns-muted)"}}>o</span>
            <div className="flex-1 h-px" style={{background:"var(--ns-card-b)"}}/>
          </div>

          <Btn onClick={startTrial} disabled={busy} className="w-full py-2.5"
            style={{background:"transparent",color:"var(--ns-text)",borderColor:"var(--ns-card-b)"}}>
            <I name="play_circle" className="text-sm"/> Iniciar prueba gratuita de 14 días
          </Btn>
        </div>

        {msg&&<MsgBanner msg={msg} onDismiss={msg.type!=="ok"?()=>setMsg(null):null}/>}

        {/* Footer */}
        <div className="text-[10px] space-y-1" style={{color:"var(--ns-muted)"}}>
          <p>Herramienta de apoyo clínico. Ley 1090 de 2006.</p>
          <p>Los datos clínicos son responsabilidad del profesional tratante.</p>
        </div>
      </Card>
    </div>
  );
}
