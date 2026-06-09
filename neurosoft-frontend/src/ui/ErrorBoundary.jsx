/* ═══════════════════════════════════════════════════════════════════════
 * src/ui/ErrorBoundary.jsx — Fallback global ante errores no capturados
 * ───────────────────────────────────────────────────────────────────────
 * Captura cualquier excepción que escape del árbol React y muestra una
 * pantalla amigable con opciones: reintentar, recargar app o copiar el
 * registro de errores (almacenado en localStorage).
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(p) {
    super(p);
    this.state = { error: null, info: null };
  }
  static getDerivedStateFromError(error) { return { error }; }
  componentDidCatch(error, info) {
    this.setState({ info });
    try { console.error("NeuroSoft ErrorBoundary:", error, info); } catch {}
    try {
      const log = JSON.parse(localStorage.getItem("ns_error_log") || "[]");
      log.unshift({
        ts: new Date().toISOString(),
        msg: String(error?.message || error),
        stack: (error?.stack || "").slice(0, 2000),
        route: location.pathname,
      });
      localStorage.setItem("ns_error_log", JSON.stringify(log.slice(0, 20)));
    } catch {}

    /* Enviar crash report al backend para diagnostico remoto.
     * Fire-and-forget: no bloqueamos el render ni reintentamos.
     * Si falla (offline, backend caido), el error igual queda en localStorage. */
    try {
      const token = localStorage.getItem("ns_token") || "";
      fetch("/api/v1/errors", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          error_message: String(error?.message || error).slice(0, 500),
          error_stack: (error?.stack || "").slice(0, 2000),
          route: location.pathname.slice(0, 200),
          component_stack: (info?.componentStack || "").slice(0, 1000),
          user_agent: navigator.userAgent.slice(0, 200),
        }),
      }).catch(() => {});
    } catch {}  /* no-op si fetch no esta disponible o hay error de red */
  }
  reset = () => this.setState({ error: null, info: null });
  render() {
    if (!this.state.error) return this.props.children;
    const msg = String(this.state.error?.message || this.state.error);
    return (
      <div style={{
        minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Manrope',sans-serif", background: "#fef2f2", padding: "24px",
      }}>
        <div style={{
          maxWidth: 640, background: "#fff", borderRadius: 24,
          boxShadow: "0 20px 60px -20px rgba(220,38,38,0.25)",
          padding: 40, border: "1px solid #fecaca",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
            <span className="material-symbols-outlined" style={{
              fontSize: 40, color: "#dc2626", fontVariationSettings: "'FILL' 1",
            }}>error</span>
            <h2 style={{ fontWeight: 800, fontSize: 22, color: "#991b1b", margin: 0 }}>
              {this.props.feature
                ? `Error en ${this.props.feature}`
                : "Se produjo un error inesperado"}
            </h2>
          </div>
          <p style={{ color: "#7f1d1d", fontSize: 14, marginBottom: 16 }}>
            NeuroSoft detectó un fallo en esta pantalla. Tus datos no se han perdido —
            están guardados en la base local.
          </p>
          <pre style={{
            background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 12,
            padding: 12, fontSize: 11, color: "#991b1b",
            overflow: "auto", maxHeight: 140, whiteSpace: "pre-wrap",
          }}>{msg}</pre>
          <div style={{ display: "flex", gap: 12, marginTop: 24, flexWrap: "wrap" }}>
            <button onClick={this.reset} style={{
              padding: "10px 20px", background: "#0d9488", color: "#fff", border: "none",
              borderRadius: 999, fontWeight: 700, cursor: "pointer",
            }}>Volver a intentar</button>
            <button onClick={() => location.reload()} style={{
              padding: "10px 20px", background: "#fff", color: "#475569",
              border: "2px solid #cbd5e1", borderRadius: 999, fontWeight: 700, cursor: "pointer",
            }}>Recargar aplicación</button>
            <button onClick={(e) => {
              try {
                const log = localStorage.getItem("ns_error_log") || "[]";
                navigator.clipboard?.writeText(log);
                /* §B2-fix: en lugar de alert() bloqueante, mostramos un
                 * feedback inline temporal en el propio botón. */
                const btn = e.currentTarget;
                const prev = btn.textContent;
                btn.textContent = "✓ Registro copiado";
                setTimeout(() => { btn.textContent = prev; }, 1800);
              } catch {}
            }} style={{
              padding: "10px 20px", background: "#fff", color: "#475569",
              border: "2px solid #cbd5e1", borderRadius: 999, fontWeight: 700, cursor: "pointer",
            }}>Copiar registro</button>
          </div>
        </div>
      </div>
    );
  }
}
