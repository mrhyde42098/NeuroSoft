/* ═══════════════════════════════════════════════════════════════════════
 * src/app/auth/LoginPage.jsx — Pantalla de inicio de sesión
 * ───────────────────────────────────────────────────────────────────────
 * Layout split: panel izquierdo con NeuroCanvas + branding y panel
 * derecho con el formulario de login (usuario/contraseña + JWT).
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState } from "react";
import { useAuth } from "../../contexts.jsx";
import { I, BrainLogo } from "../../ui/primitives.jsx";
import NeuroCanvas, { sfx } from "../../ui/NeuroCanvas.jsx";
import { TEAL, TEAL_LIGHT, NAVY, CREAM } from "../../ui/tokens.js";
import PrivacyPolicyModal from "../legal/PrivacyPolicyModal.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [show, setShow] = useState(false);
  const [err, setErr] = useState("");
  const [ld, setLd] = useState(false);
  const [ready, setReady] = useState(false);
  const [success, setSuccess] = useState(false);
  const [privOpen, setPrivOpen] = useState(false);
  const mouseRef = useRef({ x: -999, y: -999 });

  /* §B6-fix: usar requestAnimationFrame en lugar de setTimeout(100ms)
   * para sincronizar con el primer paint. Sin delay arbitrario. */
  useEffect(() => {
    const id = requestAnimationFrame(() => setReady(true));
    return () => cancelAnimationFrame(id);
  }, []);

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    mouseRef.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

  const go = async (e) => {
    e.preventDefault();
    setErr("");
    setLd(true);
    sfx.click();
    try {
      await login(u, p);
      /* La animación de éxito sólo debe dispararse cuando el backend
       * confirma las credenciales. Antes se ejecutaba antes del await,
       * mostrando "Bienvenido" durante un instante incluso si la
       * autenticación fallaba. */
      sfx.success();
      setSuccess(true);
    } catch (ex) {
      sfx.error();
      setErr(
        ex.status === 401 ? "Credenciales incorrectas." :
        ex.status === 429 ? "Demasiados intentos." :
        "Error de conexión.",
      );
      setSuccess(false);
    }
    setLd(false);
  };

  return (
    <div className="min-h-screen flex relative overflow-hidden" style={{ background: NAVY }}>
      {/* Panel izquierdo — canvas neuronal */}
      <div
        className="hidden lg:flex lg:w-[55%] relative items-center justify-center"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => { mouseRef.current = { x: -999, y: -999 }; }}
      >
        <NeuroCanvas mouseRef={mouseRef} />
        <div className={`relative z-10 flex flex-col items-center text-center px-12 transition-all duration-1000 ${ready ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
          <div style={{ animation: "float 6s ease-in-out infinite" }}>
            <div className="relative">
              <div className="absolute inset-0 rounded-3xl blur-2xl"
                style={{ background: `radial-gradient(circle,${TEAL}40,transparent 70%)` }} />
              <BrainLogo size={110} />
            </div>
          </div>
          <h1 className="text-6xl font-extrabold mt-8 text-white tracking-tight"
            style={{ textShadow: "0 0 40px rgba(13,148,136,0.3)" }}>
            Neuro<span style={{ color: TEAL_LIGHT }}>Soft</span>
          </h1>
          <p className="text-lg mt-4 font-medium tracking-wide" style={{ color: "#94a3b8" }}>
            Sistema de Gestión Neuropsicológica
          </p>
          <div className="flex gap-4 mt-10">
            {[
              { i: "psychology",  l: "Evaluaciones",  d: "Protocolos WISC-IV, WAIS-III" },
              { i: "fitness_center", l: "Rehabilitación", d: "Estimulación cognitiva" },
              { i: "description", l: "Informes PDF",   d: "Generación automática" },
            ].map((f) => (
              <div key={f.l} onMouseEnter={sfx.hover}
                className="group flex flex-col items-center gap-2 px-5 py-4 rounded-2xl cursor-default transition-all duration-300 hover:scale-105 hover:-translate-y-1"
                style={{
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  backdropFilter: "blur(8px)",
                }}>
                <I name={f.i} fill className="text-2xl transition-all group-hover:scale-110"
                  style={{ color: TEAL_LIGHT }} />
                <span className="text-xs font-bold" style={{ color: "#e2e8f0" }}>{f.l}</span>
                <span className="text-[9px] font-medium" style={{ color: "#64748b" }}>{f.d}</span>
              </div>
            ))}
          </div>
          <div className="mt-12 px-4 py-2 rounded-full"
            style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)" }}>
            <span className="text-[10px] font-bold tracking-widest uppercase" style={{ color: "#475569" }}>
              Evaluación + Rehabilitación
            </span>
          </div>
        </div>
      </div>

      {/* Panel derecho — formulario de login */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 relative" style={{ background: CREAM }}>
        <div className="absolute top-0 right-0 w-96 h-96 rounded-full opacity-30"
          style={{ background: `radial-gradient(circle,${TEAL}08,transparent 70%)`, transform: "translate(30%,-30%)" }} />
        <div className="absolute bottom-0 left-0 w-64 h-64 rounded-full opacity-20"
          style={{ background: `radial-gradient(circle,${TEAL}06,transparent 70%)`, transform: "translate(-30%,30%)" }} />
        <main className={`w-full max-w-md relative z-10 transition-all duration-700 delay-300 ${ready ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}`}>
          <div className="flex items-center gap-3 mb-10 lg:hidden">
            <BrainLogo size={48} />
            <h1 className="text-3xl font-extrabold" style={{ color: NAVY }}>
              Neuro<span style={{ color: TEAL }}>Soft</span>
            </h1>
          </div>
          <header className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-1.5 h-8 rounded-full"
                style={{ background: `linear-gradient(to bottom,${TEAL},${TEAL_LIGHT})` }} />
              <h2 className="text-3xl font-bold" style={{ color: NAVY }}>Bienvenido de nuevo</h2>
            </div>
            <p className="font-medium ml-5" style={{ color: "#64748b" }}>
              Acceda a su entorno clínico seguro.
            </p>
          </header>
          <form className="space-y-6" onSubmit={go}>
            {err && (
              <div className="flex items-center gap-3 px-5 py-4 rounded-2xl text-sm font-semibold animate-[fadeIn_0.3s_ease-out]"
                style={{ background: "#ffdad6", color: "#93000a" }}>
                <I name="error" className="text-lg" />{err}
              </div>
            )}
            {success && (
              <div className="flex items-center gap-3 px-5 py-4 rounded-2xl text-sm font-semibold animate-[fadeIn_0.3s_ease-out]"
                style={{ background: `${TEAL}15`, color: TEAL }}>
                <I name="check_circle" fill className="text-lg" />Acceso verificado. Cargando...
              </div>
            )}
            <div className="space-y-2">
              <label className="block text-[10px] font-extrabold uppercase tracking-[0.2em] ml-1"
                style={{ color: "#434655" }}>ID Profesional</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none transition-all"
                  style={{ color: "#94a3b8" }}>
                  <I name="badge" />
                </div>
                <input
                  value={u}
                  onChange={(e) => { setU(e.target.value); sfx.type(); }}
                  className="block w-full pl-14 pr-5 py-5 rounded-2xl border-2 focus:ring-0 transition-all duration-300"
                  style={{ background: "#e4e2de30", borderColor: "transparent", boxShadow: "none" }}
                  onFocus={(e) => {
                    e.target.style.borderColor = `${TEAL}50`;
                    e.target.style.boxShadow = `0 0 0 4px ${TEAL}10`;
                    sfx.hover();
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = "transparent";
                    e.target.style.boxShadow = "none";
                  }}
                  placeholder="usuario"
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="block text-[10px] font-extrabold uppercase tracking-[0.2em] ml-1"
                style={{ color: "#434655" }}>Clave de Seguridad</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none"
                  style={{ color: "#94a3b8" }}>
                  <I name="lock" />
                </div>
                <input
                  value={p}
                  onChange={(e) => { setP(e.target.value); sfx.type(); }}
                  type={show ? "text" : "password"}
                  className="block w-full pl-14 pr-14 py-5 rounded-2xl border-2 focus:ring-0 transition-all duration-300"
                  style={{ background: "#e4e2de30", borderColor: "transparent" }}
                  onFocus={(e) => {
                    e.target.style.borderColor = `${TEAL}50`;
                    e.target.style.boxShadow = `0 0 0 4px ${TEAL}10`;
                    sfx.hover();
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = "transparent";
                    e.target.style.boxShadow = "none";
                  }}
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => { setShow(!show); sfx.click(); }}
                  className="absolute inset-y-0 right-0 pr-5 flex items-center hover:text-gray-700 transition-colors"
                  style={{ color: "#94a3b8" }}
                >
                  <I name={show ? "visibility_off" : "visibility"} />
                </button>
              </div>
            </div>
            <button
              disabled={ld}
              type="submit"
              onMouseEnter={sfx.hover}
              className={`w-full py-5 text-white font-bold rounded-2xl shadow-xl active:scale-[0.97] disabled:opacity-60 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl group relative overflow-hidden ${ld ? "" : "cursor-pointer"}`}
              style={{
                background: `linear-gradient(135deg,${NAVY},${TEAL})`,
                boxShadow: `0 12px 30px -6px ${TEAL}40`,
              }}
            >
              <span className="relative z-10 flex items-center justify-center gap-2">
                {ld ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Verificando...
                  </>
                ) : success ? (
                  <><I name="check" fill />Bienvenido</>
                ) : "Iniciar Sesión →"}
              </span>
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{ background: `linear-gradient(135deg,${TEAL},${NAVY})` }} />
            </button>
          </form>
          <div className="flex items-center justify-center gap-2 mt-8">
            <div className="w-8 h-px" style={{ background: "#cbd5e1" }} />
            <p className="text-[10px] font-bold tracking-widest uppercase" style={{ color: "#94a3b8" }}>
              NeuroSoft App
            </p>
            <div className="w-8 h-px" style={{ background: "#cbd5e1" }} />
          </div>
          {/* Aviso de privacidad — Ley 1581 de 2012 */}
          <div className="mt-6 text-center space-y-1.5">
            <p className="text-[10px] leading-relaxed" style={{ color: "#94a3b8" }}>
              Al iniciar sesión, el profesional confirma que cuenta con el consentimiento informado
              del titular para el tratamiento de sus datos de salud.
            </p>
            <button
              type="button"
              onClick={() => setPrivOpen(true)}
              className="text-[10px] font-semibold underline underline-offset-2 transition-colors hover:opacity-80"
              style={{ color: TEAL }}
            >
              <I name="policy" className="text-xs mr-0.5" />
              Política de Privacidad · Ley 1581 de 2012
            </button>
          </div>
        </main>
      </div>
      <PrivacyPolicyModal open={privOpen} onClose={() => setPrivOpen(false)} />
    </div>
  );
}
