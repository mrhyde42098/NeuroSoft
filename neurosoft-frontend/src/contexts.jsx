/* ═══════════════════════════════════════════════════════════════════════
 * src/contexts.jsx — Providers globales y hooks asociados
 * ───────────────────────────────────────────────────────────────────────
 *   • AuthProvider  / useAuth   — sesión con JWT en localStorage
 *   • DarkProvider  / useDark   — modo oscuro persistido
 *   • ToastProvider / useToast  — toasts de éxito/error/warn/info
 *
 * Estos hooks se usan desde TODA la app. Vivían inline en App.jsx;
 * extraerlos permite que cada feature page los importe sin depender
 * del archivo monolítico App.jsx.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, {
  createContext, useCallback, useContext, useEffect, useState,
} from "react";
import { api } from "./api/client.js";
import { safeLS } from "./utils/safeLS.js";

/* ═══════════════════════════════════════════════════════════════
 * AUTH
 * ═══════════════════════════════════════════════════════════════ */
const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  /* §H1-fix: borrar SOLO claves de sesión; preservar preferencias UI
   * (ns_dark, ns_a11y_*) y datos clínicos en curso (ns_codif_t_*).
   * §M5-fix: usamos safeLS — modo privado o cuota llena no rompen el login. */
  const _clearSession = () => {
    ["ns_token", "ns_user"].forEach((k) => safeLS.remove(k));
  };

  useEffect(() => {
    const t = safeLS.get("ns_token");
    const s = safeLS.get("ns_user");
    if (t && s) {
      try { setUser(JSON.parse(s)); }
      catch { _clearSession(); }
    }
    setReady(true);
  }, []);

  const login = async (u, p) => {
    const d = await api.post("/api/v1/auth/login", { username: u, password: p });
    safeLS.set("ns_token", d.access_token);
    safeLS.setJSON("ns_user", d);
    setUser(d);
  };
  const logout = () => { _clearSession(); setUser(null); };

  if (!ready) return null;
  return <AuthCtx.Provider value={{ user, login, logout }}>{children}</AuthCtx.Provider>;
}
export const useAuth = () => useContext(AuthCtx);


/* ═══════════════════════════════════════════════════════════════
 * DARK MODE
 * ═══════════════════════════════════════════════════════════════ */
const DarkCtx = createContext({ dark: false, toggle: () => {} });

export function DarkProvider({ children }) {
  const [dark, setDark] = useState(() => safeLS.get("ns_dark") === "1");
  const toggle = () => setDark(d => {
    const nv = !d;
    safeLS.set("ns_dark", nv ? "1" : "0");
    if (nv) document.documentElement.classList.add("dark-mode");
    else document.documentElement.classList.remove("dark-mode");
    return nv;
  });
  useEffect(() => {
    if (dark) document.documentElement.classList.add("dark-mode");
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return <DarkCtx.Provider value={{ dark, toggle }}>{children}</DarkCtx.Provider>;
}
export const useDark = () => useContext(DarkCtx);


/* ═══════════════════════════════════════════════════════════════
 * TOASTS
 * ═══════════════════════════════════════════════════════════════ */
const ToastCtx = createContext({ push: () => {} });

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  /* §M10-fix: limitar máximo a 5 toasts simultáneos. Si llegan más,
   * descartamos los más antiguos para no saturar la pantalla en
   * loops accidentales. */
  const MAX_TOASTS = 5;
  const push = useCallback((msg, opts = {}) => {
    const id = Date.now() + Math.random();
    const t = { id, msg: String(msg || ""), type: opts.type || "info", dur: opts.dur ?? 4000 };
    setToasts(ts => {
      const next = [...ts, t];
      return next.length > MAX_TOASTS ? next.slice(next.length - MAX_TOASTS) : next;
    });
    if (t.dur > 0) setTimeout(() => setToasts(ts => ts.filter(x => x.id !== id)), t.dur);
    return id;
  }, []);
  const dismiss = useCallback(id => setToasts(ts => ts.filter(x => x.id !== id)), []);
  const apiToast = {
    push,
    success: (m, o) => push(m, { ...o, type: "success" }),
    error:   (m, o) => push(m, { ...o, type: "error", dur: 6000 }),
    warn:    (m, o) => push(m, { ...o, type: "warn" }),
    info:    (m, o) => push(m, { ...o, type: "info" }),
  };
  const COLORS = {
    success: { bg: "#ecfdf5", br: "#10b981", tx: "#065f46", ic: "check_circle" },
    error:   { bg: "#fef2f2", br: "#dc2626", tx: "#991b1b", ic: "error" },
    warn:    { bg: "#fffbeb", br: "#d97706", tx: "#92400e", ic: "warning" },
    info:    { bg: "#eff6ff", br: "#3b82f6", tx: "#1e3a8a", ic: "info" },
  };
  return (
    <ToastCtx.Provider value={apiToast}>
      {children}
      <div style={{
        position: "fixed", top: 20, right: 20, zIndex: 9999,
        display: "flex", flexDirection: "column", gap: 8,
        maxWidth: 420, pointerEvents: "none",
      }}>
        {toasts.map(t => {
          const c = COLORS[t.type] || COLORS.info;
          return (
            <div key={t.id} style={{
              background: c.bg, borderLeft: `4px solid ${c.br}`, color: c.tx,
              padding: "12px 16px", borderRadius: 12,
              boxShadow: "0 10px 30px -10px rgba(0,0,0,0.15)",
              display: "flex", alignItems: "flex-start", gap: 10,
              fontSize: 13, fontWeight: 600, pointerEvents: "auto",
              animation: "nsToastIn 220ms ease-out",
            }}>
              <span className="material-symbols-outlined" style={{
                fontSize: 20, color: c.br,
                fontVariationSettings: "'FILL' 1", flexShrink: 0,
              }}>{c.ic}</span>
              <span style={{ flex: 1, lineHeight: 1.4 }}>{t.msg}</span>
              <button onClick={() => dismiss(t.id)} style={{
                background: "transparent", border: "none", color: c.tx,
                opacity: 0.6, cursor: "pointer", fontSize: 16, padding: 0, lineHeight: 1,
              }} aria-label="Cerrar">×</button>
            </div>
          );
        })}
      </div>
      <style>{`@keyframes nsToastIn{from{opacity:0;transform:translateX(40px)}to{opacity:1;transform:translateX(0)}}`}</style>
    </ToastCtx.Provider>
  );
}
export const useToast = () => useContext(ToastCtx);


/* ═══════════════════════════════════════════════════════════════
 * CONFIRM (§M3/M4-fix)
 * Modal de confirmación que reemplaza window.confirm() — éste era
 * bloqueante, feo en dark mode y rompía la coherencia visual.
 *
 * Uso:
 *   const confirm = useConfirm();
 *   if (await confirm({ title, message, dangerous: true })) { ... }
 * ═══════════════════════════════════════════════════════════════ */
const ConfirmCtx = createContext(null);

export function ConfirmProvider({ children }) {
  const [state, setState] = useState(null);

  const confirm = useCallback((opts) => {
    return new Promise((resolve) => {
      setState({
        title: opts?.title || "Confirmar acción",
        message: opts?.message || "¿Deseas continuar?",
        confirmText: opts?.confirmText || "Confirmar",
        cancelText: opts?.cancelText || "Cancelar",
        dangerous: !!opts?.dangerous,
        resolve,
      });
    });
  }, []);

  const close = (value) => {
    if (state?.resolve) state.resolve(value);
    setState(null);
  };

  useEffect(() => {
    if (!state) return;
    const onKey = (e) => {
      if (e.key === "Escape") close(false);
      else if (e.key === "Enter") close(true);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

  return (
    <ConfirmCtx.Provider value={confirm}>
      {children}
      {state && (
        <div
          onClick={() => close(false)}
          style={{
            position: "fixed", inset: 0, zIndex: 9998,
            background: "rgba(15,23,42,0.55)",
            backdropFilter: "blur(2px)",
            display: "flex", alignItems: "center", justifyContent: "center",
            padding: 16,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            role="dialog" aria-modal="true"
            style={{
              background: "var(--ns-card, #fff)",
              color: "var(--ns-text, #1E293B)",
              borderRadius: 12,
              padding: "20px 24px",
              maxWidth: 460, width: "100%",
              boxShadow: "0 24px 60px -12px rgba(15,23,42,0.35)",
              border: "1px solid var(--ns-card-b, #E5E7EB)",
              animation: "nsConfirmIn 180ms ease-out",
            }}
          >
            <div style={{
              display: "flex", alignItems: "center", gap: 10, marginBottom: 8,
            }}>
              <span
                className="material-symbols-outlined"
                style={{
                  fontSize: 22,
                  color: state.dangerous ? "#dc2626" : "#0D9488",
                  fontVariationSettings: "'FILL' 1",
                }}
              >{state.dangerous ? "warning" : "help"}</span>
              <h3 style={{
                margin: 0, fontFamily: "'Lora', Georgia, serif",
                fontSize: 18, fontWeight: 700,
              }}>{state.title}</h3>
            </div>
            <p style={{
              fontSize: 13, lineHeight: 1.55, margin: "8px 0 16px",
              color: "var(--ns-muted, #475569)", whiteSpace: "pre-wrap",
            }}>{state.message}</p>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
              <button
                onClick={() => close(false)}
                style={{
                  fontSize: 13, fontWeight: 600,
                  padding: "8px 14px", borderRadius: 6,
                  background: "transparent",
                  color: "var(--ns-text, #1E293B)",
                  border: "1px solid var(--ns-card-b, #E5E7EB)",
                  cursor: "pointer",
                  fontFamily: "inherit",
                }}
              >{state.cancelText}</button>
              <button
                onClick={() => close(true)}
                style={{
                  fontSize: 13, fontWeight: 600,
                  padding: "8px 14px", borderRadius: 6,
                  background: state.dangerous ? "#dc2626" : "#0D9488",
                  color: "#fff",
                  border: "none",
                  cursor: "pointer",
                  fontFamily: "inherit",
                }}
                autoFocus
              >{state.confirmText}</button>
            </div>
          </div>
          <style>{`@keyframes nsConfirmIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}`}</style>
        </div>
      )}
    </ConfirmCtx.Provider>
  );
}

/**
 * Hook que devuelve una función `confirm(opts) => Promise<boolean>`.
 * Si por algún motivo no hay provider (tests sueltos), cae a window.confirm
 * para no romper.
 */
export const useConfirm = () => {
  const ctx = useContext(ConfirmCtx);
  return ctx || ((opts) =>
    Promise.resolve(window.confirm(opts?.message || "¿Continuar?"))
  );
};


/* ═══════════════════════════════════════════════════════════════
 * ACCESSIBILITY (§12.8)
 * ═══════════════════════════════════════════════════════════════ */
const A11yCtx = createContext({ highContrast: false, fontScale: "md", setHighContrast: () => {}, setFontScale: () => {} });

const FONT_CLASSES = ["ns-font-md", "ns-font-lg", "ns-font-xl"];

function applyFontScale(scale) {
  FONT_CLASSES.forEach(c => document.documentElement.classList.remove(c));
  document.documentElement.classList.add(`ns-font-${scale}`);
}

export function A11yProvider({ children }) {
  const [highContrast, _setHC] = useState(() => safeLS.get("ns_a11y_hc") === "1");
  const [fontScale, _setFS] = useState(() => safeLS.get("ns_a11y_fs") || "md");

  const setHighContrast = (v) => {
    _setHC(v);
    safeLS.set("ns_a11y_hc", v ? "1" : "0");
    if (v) document.documentElement.classList.add("high-contrast");
    else document.documentElement.classList.remove("high-contrast");
  };
  const setFontScale = (v) => {
    _setFS(v);
    safeLS.set("ns_a11y_fs", v);
    applyFontScale(v);
  };

  useEffect(() => {
    if (highContrast) document.documentElement.classList.add("high-contrast");
    applyFontScale(fontScale);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const SCALES = ["md", "lg", "xl"];
    const handleKey = (e) => {
      if (!e.altKey) return;
      /* §H13-fix: ignorar atajos cuando el foco está en un campo
       * editable. Antes, escribir "+" en una observación clínica
       * disparaba aumento de fuente. */
      const tag = (e.target?.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select"
          || e.target?.isContentEditable) return;
      if (e.key === "h" || e.key === "H") {
        setHighContrast(!document.documentElement.classList.contains("high-contrast"));
      } else if (e.key === "+" || e.key === "=") {
        const cur = SCALES.indexOf(safeLS.get("ns_a11y_fs") || "md");
        if (cur < SCALES.length - 1) setFontScale(SCALES[cur + 1]);
      } else if (e.key === "-") {
        const cur = SCALES.indexOf(safeLS.get("ns_a11y_fs") || "md");
        if (cur > 0) setFontScale(SCALES[cur - 1]);
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  return (
    <A11yCtx.Provider value={{ highContrast, fontScale, setHighContrast, setFontScale }}>
      {children}
    </A11yCtx.Provider>
  );
}
export const useA11y = () => useContext(A11yCtx);
