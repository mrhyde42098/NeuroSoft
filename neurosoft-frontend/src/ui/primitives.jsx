/* ═══════════════════════════════════════════════════════════════════════
 * src/ui/primitives.jsx — Componentes UI atómicos compartidos
 * ───────────────────────────────────────────────────────────────────────
 * Estos componentes son visuales puros: NO conocen API, contextos ni
 * páginas concretas. Son los "lego" del sistema de diseño.
 *
 *   • I            — Icono Material Symbols (con fill opcional)
 *   • BrainLogo    — logo SVG de marca
 *   • Card         — superficie con borde + sombra
 *   • Label        — etiqueta uppercase tracking
 *   • Input/Sel/Txta — inputs estilizados
 *   • Btn          — botón con variantes (primary, secondary, outline, danger)
 *   • TopBar       — header sticky de cada página
 *   • MsgBanner    — banner de éxito/error/info
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";
import { TEAL, TEAL_LIGHT, NAVY } from "./tokens.js";

/* ─── Icono Material Symbols ─────────────────────────────── */
export const I = ({ name, fill, className = "", style }) => (
  <span
    className={`material-symbols-outlined ${className}`}
    style={{
      ...(fill ? { fontVariationSettings: "'FILL' 1" } : {}),
      ...style,
    }}
  >
    {name}
  </span>
);

/* ─── Logo SVG de marca (cerebro estilizado) ─────────────── */
export const BrainLogo = ({ size = 40, className = "" }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 64 64"
    className={className}
    aria-label="NeuroSoft"
  >
    <defs>
      <linearGradient id="bl-g" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor={TEAL} />
        <stop offset="100%" stopColor={TEAL_LIGHT} />
      </linearGradient>
    </defs>
    <rect width="64" height="64" rx="14" fill={NAVY} />
    <path
      d="M32 12c-8 0-15 5.5-15 14 0 4 1.5 7 4 9.5 1.5 1.5 2 3.5 2 5.5v3c0 2 1.5 3 3 3h12c1.5 0 3-1 3-3v-3c0-2 .5-4 2-5.5 2.5-2.5 4-5.5 4-9.5 0-8.5-7-14-15-14z"
      fill="none"
      stroke="url(#bl-g)"
      strokeWidth="2.5"
      strokeLinecap="round"
    />
    <circle cx="32" cy="22" r="2" fill={TEAL_LIGHT} />
    <path
      d="M32 22v6M32 28l-5 4M32 28l5 4M26 20l6 2M38 20l-6 2"
      stroke={TEAL}
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <rect x="25" y="48" width="14" height="2" rx="1" fill={`${TEAL}80`} />
    <rect x="27" y="52" width="10" height="2" rx="1" fill={`${TEAL}60`} />
  </svg>
);

/* ─── Superficies / inputs ───────────────────────────────── */
export const Card = ({ children, className = "", style, ...p }) => (
  <div
    className={`rounded-3xl border shadow-[0_20px_50px_-20px_rgba(0,0,0,0.04)] ${className}`}
    style={{
      background: "var(--ns-card)",
      borderColor: "var(--ns-card-b)",
      color: "var(--ns-text)",
      ...style,
    }}
    {...p}
  >
    {children}
  </div>
);

export const Label = ({ children, className = "" }) => (
  <label
    className={`block text-[10px] font-extrabold uppercase tracking-[0.2em] mb-2 ${className}`}
    style={{ color: "var(--ns-muted)" }}
  >
    {children}
  </label>
);

export const Input = ({ className = "", style, ...p }) => (
  <input
    className={`w-full px-4 py-3.5 rounded-xl border-2 border-transparent focus:border-teal-500/20 focus:ring-0 transition-all text-sm ${className}`}
    style={{ background: "var(--ns-input)", color: "var(--ns-text)", ...style }}
    {...p}
  />
);

export const Sel = ({ children, className = "", style, ...p }) => (
  <select
    className={`w-full px-4 py-3.5 rounded-xl border-2 border-transparent focus:border-teal-500/20 focus:ring-0 transition-all text-sm ${className}`}
    style={{ background: "var(--ns-input)", color: "var(--ns-text)", ...style }}
    {...p}
  >
    {children}
  </select>
);

export const Txta = ({ className = "", style, ...p }) => (
  <textarea
    className={`w-full px-4 py-4 rounded-xl border-2 border-transparent focus:border-teal-500/20 focus:ring-0 transition-all text-sm min-h-[100px] ${className}`}
    style={{ background: "var(--ns-input)", color: "var(--ns-text)", ...style }}
    {...p}
  />
);

/* ─── Botón ──────────────────────────────────────────────── */
export const Btn = ({ v = "primary", children, className = "", ...p }) => {
  const s = {
    primary: "text-white shadow-xl hover:-translate-y-0.5",
    secondary: "bg-teal-600 text-white shadow-lg",
    outline: "border-2 border-gray-300 text-gray-600 hover:bg-gray-50",
    danger: "border-2 border-red-400 text-red-500 hover:bg-red-50",
  };
  return (
    <button
      className={`px-6 py-3 rounded-full font-bold text-sm transition-all active:scale-95 flex items-center justify-center gap-2 ${s[v]} ${className}`}
      style={
        v === "primary"
          ? { background: TEAL, boxShadow: "0 8px 20px -4px rgba(13,148,136,0.3)" }
          : {}
      }
      {...p}
    >
      {children}
    </button>
  );
};

/* ─── Header sticky por página ─────────────────────────────
 * El título usa `truncate` y `min-w-0` para no empujar a los controles;
 * los controles llevan `flex-wrap` + `justify-end` para que en pantallas
 * estrechas se acomoden en lugar de cortarse. La altura mínima es
 * `min-h-20` (no fija) por si los children deciden envolverse. */
export const TopBar = ({ title, children }) => (
  <header
    className="sticky top-0 z-40 flex items-center justify-between gap-4 px-6 sm:px-8 min-h-20 py-3 border-b"
    style={{
      background: "var(--ns-topbar)",
      backdropFilter: "blur(12px)",
      borderColor: "var(--ns-card-b)",
    }}
  >
    <h2
      className="text-xl sm:text-2xl font-bold truncate min-w-0 flex-shrink"
      style={{ color: "var(--ns-text)" }}
      title={typeof title === "string" ? title : undefined}
    >
      {title}
    </h2>
    <div className="flex items-center justify-end gap-3 flex-wrap">{children}</div>
  </header>
);

/* ─── Banner de mensaje (success/error/warn) ─────────────── */
export const MsgBanner = ({ msg, onDismiss }) => {
  if (!msg) return null;
  const isOk = msg === "ok" || msg === "Cambios guardados";
  return (
    <div
      className="flex items-center gap-3 px-5 py-4 rounded-2xl text-sm font-semibold animate-[fadeIn_0.3s_ease-out]"
      style={{
        background: isOk ? "#ecfdf5" : "#fef2f2",
        color: isOk ? "#065f46" : "#991b1b",
        borderLeft: `4px solid ${isOk ? "#10b981" : "#dc2626"}`,
      }}
    >
      <I name={isOk ? "check_circle" : "error"} fill className="text-lg" />
      <span className="flex-1">{isOk ? "Cambios guardados correctamente" : msg}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="opacity-60 hover:opacity-100 transition-opacity"
          aria-label="Cerrar"
        >
          <I name="close" className="text-base" />
        </button>
      )}
    </div>
  );
};

/* ─── Estado vacío estandarizado ─────────────────────────── */
export const EmptyState = ({
  icon = "inbox",
  title,
  description,
  cta,
  className = "",
}) => (
  <div className={`flex flex-col items-center justify-center py-16 px-6 text-center ${className}`} style={{ color: "var(--ns-muted)" }}>
    <div
      className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
      style={{ background: "var(--ns-subtle)", color: TEAL }}
    >
      <I name={icon} className="text-3xl" />
    </div>
    {title && <p className="font-bold text-base mb-1" style={{ color: "var(--ns-text)" }}>{title}</p>}
    {description && <p className="text-xs max-w-md">{description}</p>}
    {cta && <div className="mt-5">{cta}</div>}
  </div>
);

/* ─── Skeleton de carga ──────────────────────────────────── */
export const Skeleton = ({ className = "" }) => (
  <div
    className={`rounded-xl animate-pulse ${className}`}
    style={{ background: "var(--ns-subtle)" }}
  />
);

/* ─── Spinner pequeño ────────────────────────────────────── */
export const Spinner = ({ size = 8 }) => (
  <div
    className={`animate-spin border-4 border-teal-200 border-t-teal-600 rounded-full`}
    style={{ width: `${size * 4}px`, height: `${size * 4}px` }}
  />
);
