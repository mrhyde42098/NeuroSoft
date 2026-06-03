/* ═══════════════════════════════════════════════════════════════════════
 * src/ui/Skeleton.jsx — Componentes de carga esqueleto (skeleton screens)
 * ───────────────────────────────────────────────────────────────────────
 * Reemplaza spinners genéricos con placeholders animados que preservan
 * el layout esperado, reduciendo el layout shift y mejorando la UX.
 *
 * Exportaciones:
 *   • Skeleton          — barra o bloque animado base
 *   • SkeletonText      — líneas de texto (n líneas)
 *   • SkeletonCard      — tarjeta completa de paciente/item de lista
 *   • SkeletonTable     — tabla con filas de placeholder
 *   • SkeletonKpi       — card de KPI (número + label)
 *   • SkeletonPage      — pantalla completa de carga
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";

/* ─── CSS de animación (inyectado una sola vez) ──────────────── */
const ANIM_STYLE = `
  @keyframes ns-shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position:  400px 0; }
  }
  .ns-skeleton {
    background: linear-gradient(
      90deg,
      var(--ns-subtle, #f0ece4) 25%,
      var(--ns-card-b, #e5e0d6) 50%,
      var(--ns-subtle, #f0ece4) 75%
    );
    background-size: 800px 100%;
    animation: ns-shimmer 1.4s ease-in-out infinite;
    border-radius: 0.5rem;
  }
`;

let styleInjected = false;
function ensureStyle() {
  if (styleInjected || typeof document === "undefined") return;
  styleInjected = true;
  const el = document.createElement("style");
  el.textContent = ANIM_STYLE;
  document.head.appendChild(el);
}

/* ─── Skeleton base ───────────────────────────────────────────── */
export function Skeleton({ width = "100%", height = 16, className = "", style = {} }) {
  ensureStyle();
  return (
    <div
      className={`ns-skeleton ${className}`}
      style={{ width, height, ...style }}
      aria-hidden="true"
    />
  );
}

/* ─── Líneas de texto ─────────────────────────────────────────── */
export function SkeletonText({ lines = 3, className = "" }) {
  ensureStyle();
  const widths = ["100%", "85%", "72%", "90%", "60%", "80%", "95%"];
  return (
    <div className={`space-y-2 ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} width={widths[i % widths.length]} height={12} />
      ))}
    </div>
  );
}

/* ─── Card de paciente / ítem de lista ───────────────────────── */
export function SkeletonCard({ className = "" }) {
  ensureStyle();
  return (
    <div
      className={`rounded-3xl border p-5 space-y-3 ${className}`}
      style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}
      aria-hidden="true"
    >
      <div className="flex items-center gap-3">
        <Skeleton width={44} height={44} style={{ borderRadius: "50%", flexShrink: 0 }} />
        <div className="flex-1 space-y-2">
          <Skeleton width="60%" height={14} />
          <Skeleton width="40%" height={10} />
        </div>
        <Skeleton width={72} height={28} style={{ borderRadius: 99 }} />
      </div>
      <SkeletonText lines={2} />
    </div>
  );
}

/* ─── Fila de tabla ───────────────────────────────────────────── */
export function SkeletonTableRow({ cols = 5 }) {
  ensureStyle();
  const colWidths = ["40%", "20%", "15%", "15%", "10%"];
  return (
    <tr aria-hidden="true">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-6 py-4">
          <Skeleton width={colWidths[i] ?? "80%"} height={12} />
        </td>
      ))}
    </tr>
  );
}

/* ─── Tabla completa ──────────────────────────────────────────── */
export function SkeletonTable({ rows = 6, cols = 5, className = "" }) {
  ensureStyle();
  return (
    <div
      className={`rounded-3xl border overflow-hidden ${className}`}
      style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}
      aria-hidden="true"
    >
      {/* Header falso */}
      <div className="px-6 py-4 border-b flex gap-4" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} width={`${[14, 8, 10, 10, 6][i] ?? 10}%`} height={12} />
        ))}
      </div>
      <table className="w-full">
        <tbody>
          {Array.from({ length: rows }).map((_, i) => (
            <SkeletonTableRow key={i} cols={cols} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ─── KPI Card ────────────────────────────────────────────────── */
export function SkeletonKpi({ className = "" }) {
  ensureStyle();
  return (
    <div
      className={`rounded-3xl border p-6 space-y-4 ${className}`}
      style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}
      aria-hidden="true"
    >
      <div className="flex items-center justify-between">
        <Skeleton width={32} height={32} style={{ borderRadius: 8 }} />
        <Skeleton width={48} height={20} style={{ borderRadius: 99 }} />
      </div>
      <Skeleton width="50%" height={32} />
      <Skeleton width="70%" height={10} />
    </div>
  );
}

/* ─── Página completa de carga (reemplaza spinners) ──────────── */
export function SkeletonPage({ title = "", kpis = 0, table = false, cards = 0 }) {
  ensureStyle();
  return (
    <div aria-busy="true" aria-label="Cargando...">
      {/* TopBar */}
      <div className="sticky top-0 z-40 flex items-center px-8 h-20 border-b" style={{ background: "var(--ns-topbar)", borderColor: "var(--ns-card-b)" }}>
        <Skeleton width={title ? title.length * 14 : 180} height={24} />
      </div>
      <div className="p-8 space-y-6">
        {/* KPIs */}
        {kpis > 0 && (
          <div className={`grid gap-4 grid-cols-2 lg:grid-cols-${Math.min(kpis, 4)}`}>
            {Array.from({ length: kpis }).map((_, i) => (
              <SkeletonKpi key={i} />
            ))}
          </div>
        )}
        {/* Cards */}
        {cards > 0 && (
          <div className="space-y-3">
            {Array.from({ length: cards }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}
        {/* Tabla */}
        {table && <SkeletonTable />}
      </div>
    </div>
  );
}
